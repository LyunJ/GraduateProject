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
import sys
import time
from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.serialization import Deserializer, Serializer
import socket

# ip 가져오기
import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP
kafka_ip = IP('../ips','kafka')

# kafka topic name
LABEL_ACC_GOOD_TOPIC = 'good_acc_label'

def producer_process(key,msgValueAddedLabel):
    # producer configuration
    producer_conf = {
        'bootstrap.servers' : f'{kafka_ip}:9092',
        'compression.codec' : 'gzip'
    }

    # kafka의 good_acc_label topic에 데이터 전송
    producer = Producer(producer_conf) 
    producer.produce(LABEL_ACC_GOOD_TOPIC, key=key, value = json.dumps(msgValueAddedLabel))
    producer.flush()
