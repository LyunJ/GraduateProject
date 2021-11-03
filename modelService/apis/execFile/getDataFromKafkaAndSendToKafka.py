# from kafka import KafkaConsumer
# from json import loads
# import binascii
# import numpy as np
# import cv2

# consumer = KafkaConsumer(
#     'test',
#     bootstrap_servers=['localhost:9092'],
#     auto_offset_reset='earliest',
#     enable_auto_commit=True,
#     group_id='my-group',
#     value_deserializer=lambda v: binascii.unhexlify(v),
#     consumer_timeout_ms=1000
# )

# print('[begin] get consumer list')
# count=0
# for message in consumer:
#     img = np.frombuffer(message.value,dtype=np.uint8)
#     img = cv2.imdecode(img,cv2.IMREAD_COLOR)
#     cv2.imwrite(f'temp{count}.png',img)
#     count += 1
#     if count == 2:
#         break
# print('[end] get consumer list')

import argparse
import json
import time
from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.serialization import Deserializer, Serializer
import socket

# ip 주소 가져오기
import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP

mongo_ip = IP('../ips','mongo')
kafka_ip = IP('../ips','kafka')

# topic name
LABEL_ACC_GOOD_TOPIC = 'good_acc_label'
LABEL_ACC_BAD_TOPIC = 'bad_acc_label'

# bad/good accuracy 기준
ACC_STANDARD = 80


def producer_process(key,msg):
    # producer configuration
    producer_conf = {
        'bootstrap.servers' : f'{kafka_ip}:9092',
        'compression.codec' : 'gzip'
    }
    try:
        producer = Producer(producer_conf)
        for label in msg['labels']:
            if label['accuracy'] >= ACC_STANDARD:
                # good_acc_label message 구조로 바꿔줌
                msg['label'] = label['label']
                msg.pop('labels')
                # kafka로 전송
                producer.produce(LABEL_ACC_GOOD_TOPIC, key=key, value = json.dumps(msg))
                producer.flush()
                return
        # bad_acc_label message 구조로 바꿔줌
        for i in range(len(msg['labels'])):
            msg['labels'][i].pop('accuracy')
        # kafka로 전송
        producer.produce(LABEL_ACC_BAD_TOPIC, key=key, value = json.dumps(msg))
        producer.flush()
    except:
        print('error')
        pass