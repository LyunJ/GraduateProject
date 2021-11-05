import argparse
import json
import time
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from confluent_kafka.serialization import Deserializer, Serializer
import socket
from pymongo import MongoClient

# ip 주소 받아오기
import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP

hadoop_ip = IP('../ips','hadoop')
kafka_ip = IP('../ips','kafka')


# hadoop에 파라미터 파일 저장
from hdfs import InsecureClient
def msg_process(msg):  
    client_hdfs = InsecureClient(f'http://{hadoop_ip}:9870')
    client_hdfs.download(json.loads(msg.value())['url'],'../parameter')

def main():
    # 실행 방법 python get_parameter.py {topic}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of the Kafka topic to stream.')
    args = parser.parse_args()
    topic = args.topic
    
    # kafka consumer configuration
    consumer_conf = {
        'bootstrap.servers' : f'{kafka_ip}:9092',
        'auto.offset.reset' : 'earliest',
        'group.id' : 'streams-wordcount'
    }
    consumer = Consumer(consumer_conf)
    
    running = True
    try:
        consumer.subscribe([args.topic])
        while running:
            # 1ms 주기로 consuming
            msg = consumer.poll(1)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    sys.stderr.write('Topic unknown, creating %s topic\n' %
                                     (args.topic))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # kafka message 처리
                msg_process(msg)
        
    except KeyboardInterrupt:
        pass
    
    finally:
        consumer.close()

if __name__ == "__main__":
    main()