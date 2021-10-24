from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.serialization import Deserializer, Serializer
import json
# Create your views here.

import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP

mongo_ip = IP('../ips','mongo')
kafka_ip = IP('../ips','kafka')

producer_conf = {
    'bootstrap.servers' : f'{kafka_ip}:9092',
    'compression.codec' : 'gzip'
}

PARAMETER_LABEL = 'parameter'

def parameter(request):
    if request.method == 'GET':
        msg = {
            "parameter" : "hello"
        }
        key = ""
        producer = Producer(producer_conf)
        producer.produce(PARAMETER_LABEL, key=key, value = json.dumps(msg))
        producer.flush()
        return HttpResponse("Thank you")