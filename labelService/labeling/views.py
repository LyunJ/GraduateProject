from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from .execFile.getDataFromKafkaAndSendToKafka import producer_process

def connectMongo(selector):
    if selector == 'write':
        write_db = MongoClient(['121.130.68.170:27020','121.130.68.170:27021','121.130.68.170:27022'],replicaset='rs_write')
        mydb = write_db['test']
        mycol = mydb['image']
        return mycol
    elif selector == 'read':
        read_db = MongoClient(['121.130.68.170:27017','121.130.68.170:27018','121.130.68.170:27019'],replicaset='rs0')
        mydb = read_db['test']
        mycol = mydb['image']
        return mycol
    else:
        return -1
# Create your views here.

def image(request):
    # GET
    if request.method == 'GET':
        writedb = connectMongo('write')
        readdb = connectMongo('read')
        
        wdata = writedb.find_one({"read_count": {"$lt" : 10}})
        rdata = readdb.find_one({"_id" : wdata['_id']})
        
        responseData = {
            "image_id" : str(rdata['_id']),
            "image" : rdata['image'],
            "labels" : rdata['labels']
        }
        
        # mongodb read_count + 1
        writedb.update({"_id" : wdata['_id']}, {"$set" : {"read_count" : wdata['read_count'] + 1}})
        return JsonResponse(responseData)
    
    
    # POST
    if request.method == 'POST':
        
        # request.body
        ###
        # imageid
        # selected_label
        
        data = json.loads(request.body)
        
        writedb = connectMongo('write')
        readdb = connectMongo('read')
        
        image = writedb.find_one({"_id" : ObjectId(data['image_id'])})
        imagefile = readdb.find_one({"_id":ObjectId(data['image_id'])})['image']
        
        if image['write_count'] >= 9:
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
                'image' : imagefile,
                'label' : selected_label
            }
            producer_process("",kafka_image)
            
            # mongodb image 삭제
            writedb.remove({"_id": ObjectId(data['image_id']) })
            readdb.remove({"_id": ObjectId(data['image_id']) })
            return HttpResponse("hello")
        else:
            # write table의 데이터 업데이트
            new_labels = []
            for lb in image['labels']:
                if lb['label'] == data['selected_label']:
                    lb['selected_count'] += 1
                print(lb)
                new_labels.append(lb)
            
            writedb.update({"_id" : ObjectId(data['image_id'])}, {"$set" : {"labels" : new_labels, "write_count" : image['write_count'] + 1}})
            return HttpResponse("hello")