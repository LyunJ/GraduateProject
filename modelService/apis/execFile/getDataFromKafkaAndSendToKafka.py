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

LABEL_ACC_GOOD_TOPIC = 'good_acc_label'
LABEL_ACC_BAD_TOPIC = 'bad_acc_label'

ACC_STANDARD = 80

# def msg_process(msg):    
#     # Print the current time and the message.
#     time_start = time.strftime("%Y-%m-%d %H:%M:%S")
#     print(time_start)
    
#     newVal = {
#         'image' : '',
#         'label' : '' 
#     }
#     key = msg.key()
#     val = msg.value()
#     newVal['image'] = str(val)
#     newVal['label'] = 'temp'            # 모델의 라벨링를 대신함

#     msgValueAddedLabel = json.dumps(newVal)
#     producer_process(key,msgValueAddedLabel)

def producer_process(key,msg):
    producer_conf = {
        'bootstrap.servers' : '203.252.166.207:9092',
        'compression.codec' : 'gzip'
    }
    try:
        producer = Producer(producer_conf)
        for lb in msg['labels']:
            if lb['accuracy'] >= ACC_STANDARD:
                print(lb['accuracy'])
                # good_acc_label message 구조로 바꿔줌
                msg['label'] = lb['label']
                msg.pop('labels')
                # kafka로 전송
                producer.produce(LABEL_ACC_GOOD_TOPIC, key=key, value = json.dumps(msg))
                producer.flush()
                return
        # bad_acc_label message 구조로 바꿔줌
        for i in range(len(msg['labels'])):
            msg['labels'][i].pop('accuracy')
        # kafka로 전송
        print(msg)
        producer.produce(LABEL_ACC_BAD_TOPIC, key=key, value = json.dumps(msg))
        producer.flush()
    except:
        print('error')
        pass

# def main():
#     parser = argparse.ArgumentParser(description=__doc__)
#     parser.add_argument('topic', type=str,
#                         help='Name of the Kafka topic to stream.')
    
#     args = parser.parse_args()
    
#     topic = args.topic
    
#     consumer_conf = {
#         'bootstrap.servers' : 'localhost:9092',
#         'auto.offset.reset' : 'earliest',
#         'group.id' : 'streams-wordcount'
#     }
    
#     consumer = Consumer(consumer_conf)
    
#     running = True
#     try:
#         consumer.subscribe([args.topic])
#         while running:
#             msg = consumer.poll(1)
#             if msg is None:
#                 continue
            
#             if msg.error():
#                 if msg.error().code() == KafkaError._PARTITION_EOF:
#                     # End of partition event
#                     sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
#                                      (msg.topic(), msg.partition(), msg.offset()))
#                 elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
#                     sys.stderr.write('Topic unknown, creating %s topic\n' %
#                                      (args.topic))
#                 elif msg.error():
#                     raise KafkaException(msg.error())
#             else:
#                 msg_process(msg)
        
#     except KeyboardInterrupt:
#         pass
    
#     finally:
#         consumer.close()

# if __name__ == "__main__":
#     main()