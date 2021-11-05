from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import json
from .execFile.getDataFromKafkaAndSendToKafka import producer_process
import random

# ip 주소 받아오기
import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
sys.path.append('./apis')
from ips import IP
import classification
from pathlib import Path

hbase_ip = IP('../ips','hbase')

import happybase
from PIL import Image

model = classification.labeling('./apis/yolo')

def getLabelAndAccuracyTmp(image):
    # 딥러닝 팀
    # 모델함수에 이미지를 넣었을 때 getLabelAndAccuracyTmp return의 구조로 출력될 수 있도록 코드 짜기
    # 모델 파일 경로는 docker 공유 폴더 테스트 후 나오기 때문에 일단 임의로 테스트
    # return 구조
    #     [
    #     {
    #         'label' : 'A',
    #         'accuracy' : acc1
    #     },
    #     {
    #         'label' : 'B',
    #         'accuracy' : acc2
    #     },
    #     {
    #         'label' : 'C',
    #         'accuracy' : acc3
    #     },
    #     ]
    result, images = model.simple_predict(image)
    result = [[{'label' : k, 'accuracy': v} for k, v in zip(classification.label_to_str.values(), r)] for r in result]
    result = list(map(lambda x : list(filter(lambda x: x['accuracy'] != 0,x)),result))
    return result, images

def getLabelAndAccuracy(image):
    result, images = model.simple_predict(image)
    result = [[{'label' : k, 'accuracy': v} for k, v in zip(classification.label_to_str.values(), r)] for r in result]
    result = list(map(lambda x : list(filter(lambda x: x['accuracy'] != 0,x)),result))
    return result, images

# rowkey로 구분될 image를 저장
def sendImageToHbase(image,rowkey):
    conn = happybase.Connection(f'{hbase_ip}',9090,autoconnect=True)
    conn.table('test').put(rowkey,{'data:1' : image})

# unique하고 monotonic하지 않는 rowkey 생성
# 이미지의 byte와 시간, sha256을 조합하여 생성
import time
import hashlib
def generateRowKey(image):
    t = time.time()
    time_int = int(t)
    unique_time = str(int((t - time_int) * 10000))
    
    unique_image_1 = image[:5]
    unique_image_2 = image[-5:]
    
    unique_hash = hashlib.sha256((unique_time+unique_image_2).encode()).hexdigest()
    
    result = unique_hash[:5] + unique_time + unique_image_1 + unique_image_2
    return result


import base64
import io
# /api/labeling
def labeling(request):
    if request.method == 'GET':
        # request body에서 base64로 인코딩된 image data 가져오기
        image_body = json.loads(request.body)['image']
        image_bytes = base64.b64decode(image_body)
        image_file = io.BytesIO(image_bytes)
        image = Image.open(image_file)
        # model로부터 라벨 후보와 accuracy받아오기
        labels, images = getLabelAndAccuracy(image)
        labeledImages = []
        
        for label,i in zip(labels,images):
            print(i.dtype)
            img = base64.b64encode(i).decode()
            rowkey = generateRowKey(img)
            sendImageToHbase(img,rowkey)
            labeledImage={
                'image_rowkey' : rowkey,
                'labels' : label
            }
            labeledImages.append(labeledImage)
            producer_process("",labeledImage)
        return JsonResponse({"labeledImages":labeledImages})

def labelingTest(request):
    if request.method == 'GET':
        # request body에서 base64로 인코딩된 image data 가져오기
        # image = json.loads(request.body)['image']
        
        # test용
        image = Image.open(r'C:\Users\tedle\work\project\graduate\s01000200.jpg')

        # model로부터 라벨 후보와 accuracy받아오기
        labels, images = getLabelAndAccuracyTmp(image)
        labeledImages = []
        for l,i in zip(labels,images):
            labeledImages.append({
            'image_rowkey' : base64.b64encode(i).decode(),
            'labels' : l
        })
        return JsonResponse({"labeledImages" : labeledImages})

def modelUpdate(request):
    if request.method == 'GET':
        model.update_model()
        return HttpResponse("Model Update Complete")
