from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from .execFile.getDataFromKafkaAndSendToKafka import producer_process


db = MongoClient("mongodb://121.130.68.170:27017/")
mydb = db['test']
mycol = mydb['image']

# Create your views here.

def image(request):
    # GET
    if request.method == 'GET':
        data = mycol.find_one({"read_count": {"$lt" : 10}})
        print(data['_id'])
        responseData = {
            "image_id" : str(data['_id']),
            "image" : data['image'],
            "labels" : data['labels']
        }
        # mongodb read_count + 1
        mycol.update({"_id" : data['_id']}, {"$set" : {"read_count" : data['read_count'] + 1}})
        return JsonResponse(responseData)
    
    
    # POST
    if request.method == 'POST':
        
        # request.body
        ###
        # imageid
        # selected_label
        
        data = json.loads(request.body)
        image = mycol.find_one({"_id" : ObjectId(data['image_id'])})
        if image['write_count'] > 10:
            # write table에서 labeling 결과 가져오기
            labeling_data = image['labels']
            
            selected_label = ""
            max_selected_count = 0
            for ld in labeling_data:
                if ld['label'] == data['selected_label']:
                    ld['selected_count'] += 1
                if ld['selected_count'] > max_selected_count:
                    selected_label = ld['label']

            # kafka 전송
            kafka_image = {
                'image' : image['image'],
                'label' : selected_label
            }
            producer_process("",kafka_image)
            
            # mongodb image 삭제
            mycol.remove({"_id": ObjectId(data['image_id']) })
            return HttpResponse("hello")
        else:
            # write table의 데이터 업데이트
            new_labels = []
            for lb in image['labels']:
                if lb['label'] == data['selected_label']:
                    lb['selected_count'] += 1
                print(lb)
                new_labels.append(lb)
            
            mycol.update({"_id" : ObjectId(data['image_id'])}, {"$set" : {"labels" : new_labels, "write_count" : image['write_count'] + 1}})
            return HttpResponse("hello")