from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.serialization import Deserializer, Serializer
import json
# Create your views here.

producer_conf = {
    'bootstrap.servers' : '203.252.166.207:9092',
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
