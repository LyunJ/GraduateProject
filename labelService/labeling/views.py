from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from .execFile.getDataFromKafkaAndSendToKafka import producer_process

# ip 가져오기
import os, sys
sys.path.insert(0, os.path.dirname("../ips/ips.py"))
from ips import IP
mongo_ip = IP('../ips','mongo')
hbase_ip = IP('../ips','hbase')

# mongodb 연결
def connectMongo(selector):
    if selector == 'write':
        write_db = MongoClient([f'{mongo_ip}:27020',f'{mongo_ip}:27021',f'{mongo_ip}:27022'],replicaset='rs_write')
        mydb = write_db['test']
        mycol = mydb['test_image']
        return write_db,mycol
    elif selector == 'test':
        write_db = MongoClient([f'{mongo_ip}:27020',f'{mongo_ip}:27021',f'{mongo_ip}:27022'],replicaset='rs_write')
        wdb = write_db['test']
        wcol = wdb['test']
        return write_db,wcol
    else:
        return -1


# hbase에서 rowkey로 이미지 가져오기
import happybase
def getImageFromHbase(rowkey):
    conn = happybase.Connection(f'{hbase_ip}',9090,autoconnect=True)
    result = conn.table('test').row(rowkey)[b'data:1']
    return result

# /labeling/image
import base64
import numpy as np
from PIL import Image
import io
def image(request):
    # GET
    if request.method == 'GET':
        write_client,writedb = connectMongo('write')
        
        # read_count 10 미만인 데이터만 가져오기
        wdata = writedb.find_one({"read_count": {"$lt" : 10}})
        
        # mongodb read_count + 1
        writedb.update({"_id" : wdata['_id']}, {"$inc" : {"read_count" : 1}})
        
        write_client.close()
        
        # 세션에 mongodb image_id 저장
        from .catalog.form import LabelingForm
        request.session['image_id'] = str(wdata['_id'])
        
        # django html form
        labeling_form = LabelingForm(wdata['labels'])
        
        # html img의 src에 들어갈 url
        # 이미지를 base64형태로 넣어줌
        
        image = getImageFromHbase(wdata['image_rowkey'])
        img_bytes = base64.b64decode(image)
        img = np.frombuffer(img_bytes,dtype=np.uint8)
        img = np.reshape(img,(64,64,3))
        img = Image.fromarray(img)
        buffer = io.BytesIO()
        img.save(buffer,format="JPEG")
        myimage=buffer.getvalue()
        image_src = "data:image/png;base64,"+base64.b64encode(myimage).decode('utf8')
        return render(request,'labeling/index.html',{'form' : labeling_form,'image' : image_src})
    
    
    # POST
    if request.method == 'POST':
        # session에서 image_id 가져오기
        image_id = request.session['image_id']
        
        # 선택된 label 데이터 가져오기
        selected_label = request.POST.get('label_radio')
        
        # mongoDB 연결
        write_client,writedb = connectMongo('write')
        
        # 세션에서 가져온 image_id로 mongodb에서 데이터 가져오기
        image = writedb.find_one({"_id" : ObjectId(image_id)})
        
        # write_count가 10인가?
        if image['write_count'] >= 9:
            # write table에서 labeling 결과 가져오기
            labeling_data = image['labels']
            
            # 가장 많이 선택된 라벨 구하기
            most_selected_label = ""
            max_selected_count = 0
            for ld in labeling_data:
                # 10번째 선택된 라벨 카운트 적용
                if ld['label'] == selected_label:
                    ld['selected_count'] += 1
                if ld['selected_count'] > max_selected_count:
                    most_selected_label = ld['label']

            # kafka 전송
            kafka_image = {
                'image_rowkey' : image['image_rowkey'],
                'label' : most_selected_label
            }
            producer_process("",kafka_image)
            
            # mongodb image 삭제
            writedb.remove({"_id": ObjectId(image_id) })
            write_client.close()

            return render(request,'labeling/result.html')
        else:
            # write table의 데이터 업데이트
            new_labels = []
            for lb in image['labels']:
                if lb['label'] == selected_label:
                    lb['selected_count'] += 1
                new_labels.append(lb)
            
            # mongodb write count 증가 및 선택된 라벨의 selected_count 증가
            writedb.update({"_id" : ObjectId(image_id) , "labels.label":selected_label}, {"$inc" : {"write_count" : 1, "labels.$.selected_count" : 1}})
            write_client.close()
            
            return render(request,'labeling/result.html')

def test(request):
    if request.method == 'GET':
        write_client,writedb = connectMongo('test')
        
        wdata = writedb.find_one()
        
        # mongodb read_count + 1
        writedb.update({"_id" : wdata['_id']}, {"$inc" : {"read_count" : 1}})
        write_client.close()
        
        from .catalog.form import LabelingForm
        labeling_form = LabelingForm(wdata['labels'][0],wdata['labels'][1],wdata['labels'][2])
        
         # html img의 src에 들어갈 url
        # 이미지를 base64형태로 넣어줌
        image_rowkey = getImageFromHbase(wdata['image_rowkey'])
        image_src = "data:image/png;base64,"+image_rowkey.decode('utf8')
        
        return render(request,'labeling/index.html',{'form' : labeling_form,'image' : image_src})


    if request.method == 'POST':
        for key in request.session.keys():
            print("key:=>" + request.session[key])
        # 부하 테스트에서는 세션을 만들지 않기 때문에 request.body에서 받아옴
        data = json.loads(request.body)
        image_id = data['image_id']
        selected_label = data['selected_label']

        write_client,writedb = connectMongo('test')
        
        image = writedb.find_one({"_id" : ObjectId(image_id)})

        # write table의 데이터 업데이트
        # selected_label = 'A'
        writedb.update({"_id" : ObjectId(image_id) , "labels.label":selected_label}, {"$inc" : {"write_count" : 1, "labels.$.selected_count" : 1}})
        write_client.close()
        return render(request,'labeling/result.html')
