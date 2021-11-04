from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.serialization import Deserializer, Serializer
import json
import requests
import torch

import base64

# ip 가져오기
import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP

hadoop_ip = IP('../ips','hadoop')
kafka_ip = IP('../ips','kafka')

producer_conf = {
    'bootstrap.servers' : f'{kafka_ip}:9092',
    'compression.codec' : 'gzip'
}

PARAMETER_LABEL = 'parameter'

# 이전 pt파일 삭제 후 새로운 pt파일 저장
from hdfs import InsecureClient
def save_to_hdfs(data):
    client_hdfs = InsecureClient(f'http://{hadoop_ip}:9870')
    client_hdfs.delete('/tmp/test_new.pt')
    client_hdfs.write('/tmp/test_new.pt',data=data)

# byte[] 타입으로 파일 읽어오기
def getParameterFile(fileName):
    file = open(f'./deeplearning/parameterFile/{fileName}','rb')
    return file.read()

# /model/parameter
def parameter(request):
    if request.method == 'GET':
        # parameter 파일 load 후 hadoop에 업로드
        data = getParameterFile('best.pt')
        save_to_hdfs(data)
        
        # hdfs url을 kafka의 parameter topic에 전송
        producer = Producer(producer_conf)
        producer.produce(PARAMETER_LABEL, key="", value = json.dumps({"url":"/tmp/test_new.pt"}))
        producer.flush()
        return HttpResponse("Thank you")

def training(request):
    if request.method == 'GET':
        return HttpResponse("training complete")

def trainingTest(request):
    if request.method == 'GET':
        # 모델 학습 개시
        # 모델 파일은 ./deeplaerning/parameterFile 경로로 저장 (이 파일의 디렉토리에 있음)
        return HttpResponse("training complete")