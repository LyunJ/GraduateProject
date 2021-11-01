import argparse
import json
import time
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from confluent_kafka.serialization import Deserializer, Serializer
import socket
from pymongo import MongoClient, ReadPreference

import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP
mongo_ip = IP('../ips','mongo')
kafka_ip = IP('../ips','kafka')

def connectMongo(selector):
    if selector == 'write':
        write_db = MongoClient(f"mongodb://{mongo_ip}:27020,{mongo_ip}:27021,{mongo_ip}:27022/?replicaSet=rs_write")
        mydb = write_db['test']
        mycol = mydb['image']
        return mycol
    elif selector == 'read':
        read_db = MongoClient(f"mongodb://{mongo_ip}:27017,{mongo_ip}:27018,{mongo_ip}:27019/?replicaSet=rs0")
        mydb = read_db['test']
        mycol = mydb['image']
        return mycol
    else:
        return -1

def msg_process(msg):    
    # Json 형태의 메시지를 파이썬 객체로 변환
    val = json.loads(msg.value())
    
    label_set = []
    
    # selected_count 추가
    label_count = len(val['labels']) # ['A','B','C']
    for i in range(label_count):
        label_set.append(val['labels'][i]['label'])
        val['labels'][i]['selected_count'] = 0
    
    # mongoDB저장용 객체
    mongoWriteDoc = {
        'labels' : val['labels'],
        'read_count' : 0,
        'write_count' : 0
    }
    mongoReadDoc = {
        'image' : val['image'],
        'labels' : label_set
    }
    
    # mongodb 연결
    writedb = connectMongo('write')
    readdb = connectMongo('read')
    
    docResult = readdb.insert_one(mongoReadDoc)
    try:
        mongoWriteDoc['_id'] = ObjectId(docResult.inserted_id)
        print('object')
    except:
        mongoWriteDoc['_id'] = docResult.inserted_id
        print('string')
    writedb.insert_one(mongoWriteDoc)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of the Kafka topic to stream.')
    
    args = parser.parse_args()
    
    topic = args.topic
    
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