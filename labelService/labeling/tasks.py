import argparse
import json
import sys
import time
from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.serialization import Deserializer, Serializer
import socket

LABEL_ACC_GOOD_TOPIC = 'good_acc_label'
LABEL_ACC_BAD_TOPIC = 'bad_acc_label'


from pymongo import MongoClient
def sendToMongoDB(msg):
    db = MongoClient("mongodb://121.130.68.170:27017/")
    mydb = db['test']
    mycol = mydb['image']
    
    key = msg.key()
    value = msg.value()
    
    mycol.insert

def main():
    
    topic = LABEL_ACC_BAD_TOPIC
    
    consumer_conf = {
        # 'bootstrap.servers' : 'localhost:9092',
        'bootstrap.servers' : '203.252.166.207:9092',
        'auto.offset.reset' : 'earliest',
        'group.id' : 'streams-wordcount'
    }
    
    consumer = Consumer(consumer_conf)
    
    running = True
    try:
        consumer.subscribe([topic])
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
                                     (topic))
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