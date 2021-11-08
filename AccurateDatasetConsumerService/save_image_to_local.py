import argparse
import json
import time
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from confluent_kafka.serialization import Deserializer, Serializer
import socket

import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP

hbase_ip = IP('../ips','hbase')
kafka_ip = IP('../ips','kafka')

# 이미지 저장 위치
output_basedir = './image'

label_to_str = {
    0:"+자형교차로",
    1:"T자형교차로",
    2:"Y자형교차로",
    3:"ㅏ자형교차로",
    4:"ㅓ자형교차로",
    5:"우선도로",
    6:"우합류도로",
    7:"좌합류도로",
    8:"회전교차로",
    9:"철길건널목",
    10:"우로굽은도로",
    11:"좌로굽은도로",
    12:"우좌로이중굽은도로",
    13:"좌우로이중굽은도로",
    14:"두방향통행",
    15:"오르막경사",
    16:"내리막경사",
    17:"도로폭이좁아짐",
    18:"우측차로없어짐",
    19:"좌측차로없어짐",
    20:"우측방통행",
    21:"양측방통행",
    22:"중앙분리대시작",
    23:"중앙분리대끝남",
    24:"신호기",
    25:"미끄럼도로",
    26:"강변도로",
    27:"노면고르지못함",
    28:"과속방지턱",
    29:"낙석주의",
    30:"횡단보도",
    31:"어린이보호",
    32:"자전거",
    33:"도로공사중",
    34:"비행기",
    35:"횡풍",
    36:"터널",
    37:"교량",
    38:"야생동물보호",
    39:"위험",
    40:"상습정체구간",
    41:"통행금지",
    42:"자동차통행금지",
    43:"화물자동차통행금지",
    44:"승합자동차통행금지",
    45:"이륜자동차및원동기장치자전거통행금지",
    46:"자동차,이륜자동차및원동기장치자전거통행금지",
    47:"경운기,트렉터및손수레통행금지",
    48:"자전거통행금지",
    49:"진입금지",
    50:"직진금지",
    51:"우회전금지",
    52:"좌회전금지",
    53:"유턴금지",
    54:"앞지르기금지",
    55:"주정차금지",
    56:"주차금지",
    57:"차중량제한",
    58:"차높이제한",
    59:"차폭제한",
    60:"차간거리확보",
    61:"최고속도제한",
    62:"최저속도제한",
    63:"서행",
    64:"일시정지",
    65:"양보",
    66:"보행자보행금지",
    67:"위험물적재차량통행금지",
    68:"자동차전용도로",
    69:"자전거전용도로",
    70:"자전거및보행자겸용도로",
    71:"회전교차로",
    72:"직진",
    73:"우회전",
    74:"좌회전",
    75:"직진및우회전",
    76:"직진및좌회전",
    77:"좌회전및유턴",
    78:"좌우회전",
    79:"유턴",
    80:"양측방통행",
    81:"우측면통행",
    82:"좌측면통행",
    83:"진행방향별통행구분",
    84:"우회로",
    85:"자전거및보행자통행구분",
    86:"자전거전용차로",
    87:"주차장",
    88:"자전거주차장",
    89:"보행자전용도로",
    90:"횡단보도",
    91:"노인보호구역",
    92:"어린이보호구역",
    93:"장애인보호구역",
    94:"자전거횡단도",
    95:"우측일방통행",
    96:"좌측일방통행",
    97:"정면일방통행",
    98:"비보호좌회전",
    99:"버스전용차로",
    100:"다인승차량전용차로",
    101:"통행우선",
    102:"자전거나란히통행허용"}

def findKey(value):
    key_list = list(label_to_str.keys())
    val_list = list(label_to_str.values())
    
    return key_list[val_list.index(value)]


import happybase
import base64
def getImageFromHbase(rowkey):
    conn = happybase.Connection(f'{hbase_ip}',9090,autoconnect=True)
    result = conn.table('test').row(rowkey)[b'data:1']
    return result

from PIL import Image
import io
import numpy as np
def msg_process(msg):    
    # 이미지 로컬에 저장
    label_num = findKey(json.loads(msg.value())['label'])
    
    image = getImageFromHbase(json.loads(msg.value())['image_rowkey'])
    img_bytes = base64.b64decode(image)
    img = np.frombuffer(img_bytes,dtype=np.uint8)
    img = np.reshape(img,(64,64,3))
    img = Image.fromarray(img)
    
    # 라벨별 이미지 저장 위치
    output_dir = f'{output_basedir}/{label_num}'
    
    if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
    if len(os.listdir(output_dir)) != 0:
        last_file = os.path.splitext(os.listdir(output_dir)[-1])[0]
    else:
        last_file = 0
    img.save(f'{output_dir}/{int(last_file)+1}.jpg')

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