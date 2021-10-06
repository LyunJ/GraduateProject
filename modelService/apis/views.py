from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import json
from .execFile.getDataFromKafkaAndSendToKafka import producer_process
import random

def getLabelAndAccuracy(image):
    
    acc1  =random.randrange(60,100)
    acc2 = (100 - acc1)/2
    acc3 = (100 - acc1)/2
    
    return [
        {
            'label' : 'A',
            'accuracy' : acc1
        },
        {
            'label' : 'B',
            'accuracy' : acc2
        },
        {
            'label' : 'C',
            'accuracy' : acc3
        },
    ]

# Create your views here.
def labeling(request):
    if request.method == 'GET':
        print("REQUEST BODY : " , request.body)
        data = json.loads(request.body)
        image = data['image']
        labels = getLabelAndAccuracy(image)
        labeledImage = {
            'image' : image,
            'labels' : labels
        }
        producer_process("",labeledImage)
        return JsonResponse(labeledImage)