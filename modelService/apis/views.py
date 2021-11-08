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

def checkRowkeyExistAndDelete(rowkey):
    conn = happybase.Connection(f'{hbase_ip}',9090,autoconnect=True)
    data = conn.table('test').row(rowkey)
    if len(data) == 0:
        return False
    else:
        conn.table('test').delete(rowkey)
        return True


import base64
import io
import copy
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
        resLabeledImages = []
        for label,i in zip(labels,images):
            img = base64.b64encode(i).decode()
            rowkey = generateRowKey(img)
            sendImageToHbase(img,rowkey)
            labeledImage={
                'image_rowkey' : rowkey,
                'labels' : label
            }
            
            labeledImages.append(labeledImage)
            resLabeledImages.append(copy.deepcopy(labeledImage))
            producer_process("",labeledImage)

            
        for li in resLabeledImages:
            max_count = 0
            sl = ""
            for l in li['labels']:
                if l['accuracy'] > max_count:
                    max_count = l['accuracy']
                    sl = l['label']
            li.pop('labels')
            li['label'] = sl
        return JsonResponse({"labeledImages":resLabeledImages})

def labelingTest(request):
    if request.method == 'GET':
        # request body에서 base64로 인코딩된 image data 가져오기
        image_body = json.loads(request.body)['image']
        image_bytes = base64.b64decode(image_body)
        image_file = io.BytesIO(image_bytes)
        image = Image.open(image_file)
        # model로부터 라벨 후보와 accuracy받아오기
        labels, images = getLabelAndAccuracy(image)
        labeledImages = []

        for l,i in zip(labels,images):
            img = base64.b64encode(i).decode()
            rowkey = generateRowKey(img)
            sendImageToHbase(img,rowkey)
            labeledImages.append({
                'image_rowkey' : rowkey,
                'labels' : l
            })
        
        result = True
        for li in labeledImages:
            result = result & checkRowkeyExistAndDelete(li['image_rowkey'])
        
        if result == True:
            return JsonResponse({"result" : "GOOD","labeledImages" : labeledImages})
        if result == False:
            return JsonResponse({"result" : "BAD"})

def modelUpdate(request):
    if request.method == 'GET':
        model.update_model()
        return HttpResponse("Model Update Complete")
