import argparse
import json
import sys
import time
from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.serialization import Deserializer, Serializer
import socket
from pymongo import MongoClient

LABEL_ACC_GOOD_TOPIC = 'good_acc_label'
LABEL_ACC_BAD_TOPIC = 'bad_acc_label'

db = MongoClient("mongodb://121.130.68.170:27017/")
mydb = db['test']
mycol = mydb['image']

def msg_process(msg):    
    # Json 형태의 메시지를 파이썬 객체로 변환
    val = json.loads(msg.value())
    
    # selected_count 추가
    label_count = len(val['labels'])
    for i in range(label_count):
        val['labels'][i]['selected_count'] = 0
    
    # mongoDB저장용 객체
    mongoDoc = {
        'image' : val['image'],
        'labels' : val['labels'],
        'read_count' : 0,
        'write_count' : 0
    }
    docId = mycol.insert_one(mongoDoc)
    # 저장된 docuement id
    print(docId)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of the Kafka topic to stream.')
    
    args = parser.parse_args()
    
    topic = args.topic
    
    consumer_conf = {
        'bootstrap.servers' : '203.252.166.207:9092',
        'auto.offset.reset' : 'earliest',
        'group.id' : 'streams-wordcount'
    }
    
    consumer = Consumer(consumer_conf)
    
    running = True
    try:
        consumer.subscribe([args.topic])
        while running:
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
                msg_process(msg)
        
    except KeyboardInterrupt:
        pass
    
    finally:
        consumer.close()

if __name__ == "__main__":
    main()