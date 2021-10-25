from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from .execFile.getDataFromKafkaAndSendToKafka import producer_process

import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP
mongo_ip = IP('../ips','mongo')
kafka_ip = IP('../ips','kafka')

def connectMongo(selector):
    if selector == 'write':
        write_db = MongoClient([f'{mongo_ip}:27020',f'{mongo_ip}:27021',f'{mongo_ip}:27022'],replicaset='rs_write')
        mydb = write_db['test']
        mycol = mydb['image']
        return write_db,mycol
    elif selector == 'read':
        read_db = MongoClient([f'{mongo_ip}:27017',f'{mongo_ip}:27018',f'{mongo_ip}:27019'],replicaset='rs0')
        mydb = read_db['test']
        mycol = mydb['image']
        return read_db,mycol
    elif selector == 'test':
        write_db = MongoClient([f'{mongo_ip}:27020',f'{mongo_ip}:27021',f'{mongo_ip}:27022'],replicaset='rs_write')
        read_db = MongoClient([f'{mongo_ip}:27017',f'{mongo_ip}:27018',f'{mongo_ip}:27019'],replicaset='rs0')
        wdb = write_db['test']
        wcol = wdb['test']
        rdb = read_db['test']
        rcol = rdb['test']
        return wcol,rcol
    else:
        return -1
# Create your views here.

def image(request):
    # GET
    if request.method == 'GET':
        write_client,writedb = connectMongo('write')
        read_client,readdb = connectMongo('read')
        
        wdata = writedb.find_one({"read_count": {"$lt" : 10}})
        rdata = readdb.find_one({"_id" : wdata['_id']})
        
        responseData = {
            "image_id" : str(rdata['_id']),
            "image" : rdata['image'],
            "labels" : rdata['labels']
        }
        
        # mongodb read_count + 1
        writedb.update({"_id" : wdata['_id']}, {"$set" : {"read_count" : wdata['read_count'] + 1}})
        
        from .catalog.form import LabelingForm
        request.session['image_id'] = str(rdata['_id'])
        labeling_form = LabelingForm(rdata['labels'][0],rdata['labels'][1],rdata['labels'][2])
        
        write_client.close()
        read_client.close()
        
        return render(request,'labeling/index.html',{'form' : labeling_form})
    
    
    # POST
    if request.method == 'POST':
        
        # request.body
        ###
        # imageid
        # selected_label
        
        from .catalog.form import LabelingForm
        labeling_form = LabelingForm(request.POST)
        image_id = request.session['image_id']
        selected_label = request.POST.get('label_radio')
    
        print(image_id)
        
        write_client,writedb = connectMongo('write')
        read_client,readdb = connectMongo('read')
        
        image = writedb.find_one({"_id" : ObjectId(image_id)})
        imagefile = readdb.find_one({"_id":ObjectId(image_id)})['image']
        
        if image['write_count'] >= 9:
            # write table에서 labeling 결과 가져오기
            labeling_data = image['labels']
            
            selected_label = ""
            max_selected_count = 0
            for ld in labeling_data:
                if ld['label'] == selected_label:
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
            writedb.remove({"_id": ObjectId(image_id) })
            readdb.remove({"_id": ObjectId(image_id) })
            
            write_client.close()
            read_client.close()

            return render(request,'labeling/result.html')
        else:
            # write table의 데이터 업데이트
            new_labels = []
            for lb in image['labels']:
                if lb['label'] == selected_label:
                    lb['selected_count'] += 1
                print(lb)
                new_labels.append(lb)
            
            writedb.update({"_id" : ObjectId(image_id)}, {"$set" : {"labels" : new_labels, "write_count" : image['write_count'] + 1}})
            
            write_client.close()
            read_client.close()
            
            return render(request,'labeling/result.html')

def test(request):
    if request.method == 'GET':
        writedb,readdb = connectMongo('test')
        
        wdata = writedb.find_one()
        rdata = readdb.find_one()
        
        responseData = {
            "image_id" : str(rdata['_id']),
            "image" : rdata['image'],
            "labels" : rdata['labels']
        }
        
        # mongodb read_count + 1
        writedb.update({"_id" : wdata['_id']}, {"$inc" : {"read_count" : 1}})
        
        from .catalog.form import LabelingForm
        # request.session['image_id'] = str(rdata['_id'])
        labeling_form = LabelingForm(rdata['labels'][0],rdata['labels'][1],rdata['labels'][2])
        
        
        return render(request,'labeling/index.html',{'form' : labeling_form})
    
    if request.method == 'POST':

        for key in request.session.keys():
            print("key:=>" + request.session[key])

        # from .catalog.form import LabelingForm
        # labeling_form = LabelingForm(request.POST)
        # image_id = request.session['image_id']
        # 부하 테스트에서는 세션을 만들지 않기 때문에 request.body에서 받아옴
        data = json.loads(request.body)
        image_id = data['image_id']
        selected_label = data['selected_label']
        # selected_label = request.POST.get('label_radio')
        
        writedb,readdb = connectMongo('test')
        
        image = writedb.find_one({"_id" : ObjectId(image_id)})
        imagefile = readdb.find_one({"_id":ObjectId(image_id)})['image']
        
        
        # if image['write_count'] >= 9:
        #     # write table에서 labeling 결과 가져오기
        #     labeling_data = image['labels']
            
        #     selected_label = ""
        #     max_selected_count = 0
        #     for ld in labeling_data:
        #         if ld['label'] == selected_label:
        #             ld['selected_count'] += 1
        #         if ld['selected_count'] > max_selected_count:
        #             selected_label = ld['label']

        #     # kafka 전송
        #     kafka_image = {
        #         'image' : imagefile,
        #         'label' : selected_label
        #     }
        #     producer_process("",kafka_image)
            
        #     # mongodb image 삭제
        #     writedb.remove({"_id": ObjectId(image_id) })
        #     readdb.remove({"_id": ObjectId(image_id) })
            
        #     write_client.close()
        #     read_client.close()

        #     return render(request,'labeling/result.html')
        # else:
        # write table의 데이터 업데이트
        # selected_label = 'A'
        new_labels = []
        for lb in image['labels']:
            if lb['label'] == selected_label:
                lb['selected_count'] += 1
            print(lb)
            new_labels.append(lb)
        
        # writedb.update({"_id" : ObjectId(image_id)}, {"$set" : {"labels" : new_labels, "write_count" : image['write_count'] + 1}})
        writedb.update({"_id" : ObjectId(image_id)}, {"$set" : {"labels" : new_labels}, "$inc" : {"write_count" : 1}})
        
        
        return render(request,'labeling/result.html')


# def data(request):
#     if request.method == 'GET':
#         deleteAll = request.GET.get('deleteAll',None)
#         dataNum = request.GET.get('dataNum',None)
        
#         write_client,writedb = connectMongo('write')
#         read_client,readdb = connectMongo('read')
        
#         if deleteAll == 'true':
#             writedb.drop()
#             readdb.drop()
            
#             write_client['test']['image']
#             read_client['test']['image']
        
#         if dataNum != None:
#             dataNum = int(dataNum)
            
#             readdb_list = []
#             writedb_list = []
            
#             mongoWriteDoc = {
#                 'labels' : [
#                     {
#                         'label':'A',
#                         'selected_count':0
#                     },
#                     {
#                         'label':'B',
#                         'selected_count':0
#                     },
#                     {
#                         'label':'C',
#                         'selected_count':0
#                     }
#                     ],
#                 'read_count' : 0,
#                 'write_count' : 0
#             }
#             mongoReadDoc = {
#                 'image' : 'Image',
#                 'labels' : label_set
#             }
            
#             for i in range(dataNum):
#                 if (i+1) % 100000 == 0:
#                     readdb_result = readdb.insert_many(readdb_list)
    

