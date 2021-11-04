import os
import torch
from tqdm.auto import tqdm
from PIL import Image
from pathlib import Path
import tensorflow as tf
import numpy as np
import sys
import zipfile

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir)
sys.path.insert(0, './apis/yolov5/')
dir = Path(dir)
tag = {
    0: 'traffic_sign',
    1: 'traffic_information',
    2: 'traffic_light'
}

label_to_str = {
    0:"+자형교차로",
    1:"T자형교차로",
    2:"Y자형교차로",
    3:"ㅏ자형교차로",
    4:"ㅓ자형교차로",
    5:"우선도로",
    6:"우합류도로",
    7:"좌합류도로",
    8:"회전교차로",
    9:"철길건널목",
    10:"우로굽은도로",
    11:"좌로굽은도로",
    12:"우좌로이중굽은도로",
    13:"좌우로이중굽은도로",
    14:"두방향통행",
    15:"오르막경사",
    16:"내리막경사",
    17:"도로폭이좁아짐",
    18:"우측차로없어짐",
    19:"좌측차로없어짐",
    20:"우측방통행",
    21:"양측방통행",
    22:"중앙분리대시작",
    23:"중앙분리대끝남",
    24:"신호기",
    25:"미끄럼도로",
    26:"강변도로",
    27:"노면고르지못함",
    28:"과속방지턱",
    29:"낙석주의",
    30:"횡단보도",
    31:"어린이보호",
    32:"자전거",
    33:"도로공사중",
    34:"비행기",
    35:"횡풍",
    36:"터널",
    37:"교량",
    38:"야생동물보호",
    39:"위험",
    40:"상습정체구간",
    41:"통행금지",
    42:"자동차통행금지",
    43:"화물자동차통행금지",
    44:"승합자동차통행금지",
    45:"이륜자동차및원동기장치자전거통행금지",
    46:"자동차,이륜자동차및원동기장치자전거통행금지",
    47:"경운기,트렉터및손수레통행금지",
    48:"자전거통행금지",
    49:"진입금지",
    50:"직진금지",
    51:"우회전금지",
    52:"좌회전금지",
    53:"유턴금지",
    54:"앞지르기금지",
    55:"주정차금지",
    56:"주차금지",
    57:"차중량제한",
    58:"차높이제한",
    59:"차폭제한",
    60:"차간거리확보",
    61:"최고속도제한",
    62:"최저속도제한",
    63:"서행",
    64:"일시정지",
    65:"양보",
    66:"보행자보행금지",
    67:"위험물적재차량통행금지",
    68:"자동차전용도로",
    69:"자전거전용도로",
    70:"자전거및보행자겸용도로",
    71:"회전교차로",
    72:"직진",
    73:"우회전",
    74:"좌회전",
    75:"직진및우회전",
    76:"직진및좌회전",
    77:"좌회전및유턴",
    78:"좌우회전",
    79:"유턴",
    80:"양측방통행",
    81:"우측면통행",
    82:"좌측면통행",
    83:"진행방향별통행구분",
    84:"우회로",
    85:"자전거및보행자통행구분",
    86:"자전거전용차로",
    87:"주차장",
    88:"자전거주차장",
    89:"보행자전용도로",
    90:"횡단보도",
    91:"노인보호구역",
    92:"어린이보호구역",
    93:"장애인보호구역",
    94:"자전거횡단도",
    95:"우측일방통행",
    96:"좌측일방통행",
    97:"정면일방통행",
    98:"비보호좌회전",
    99:"버스전용차로",
    100:"다인승차량전용차로",
    101:"통행우선",
    102:"자전거나란히통행허용"}

str_to_label = {v:k for k, v in label_to_str.items()}

weight_path = './apis/yolo/model0.pt'
model_dir = './apis/classification/'

class labeling():
    def __init__(self, output_dir):
        output_dir = Path(output_dir)

        # Tensorflow의 GPU 메모리 할당 문제를 해결해주는 코드(Tensorflow >= 2.0.0)
        gpu_devices = tf.config.experimental.list_physical_devices('GPU')
        for device in gpu_devices:
            tf.config.experimental.set_memory_growth(device, True)
        
        self.device = torch.device('cuda:0')

        with zipfile.ZipFile(Path(model_dir) / 'model.zip') as zip:
            zip.extractall(Path(model_dir))

        self.model0 = torch.hub.load(dir / 'yolov5', 'custom', path=weight_path, source='local').to(self.device)
        self.model1 = tf.keras.models.load_model(model_dir)
        self.output_dir = Path(output_dir)

        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)
        if not os.path.isdir(self.output_dir / 'image'):
            os.mkdir(self.output_dir / 'image')
        for label in label_to_str.keys():
            if not os.path.isdir(self.output_dir / 'image' / str(label)):
                os.mkdir(self.output_dir / 'image' / str(label))


    def predict(self, source, size=640):
        # Image Detection & Image Crop
        isvideo = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))

        if isvideo: # input이 영상 데이터일때
            from yolov5 import detect
            detect.run(
                weights = weight_path,
                source=source,
                project=self.ouptut_dir,
                name='imagedetection',
                exist_ok=True,
                save_crop=True
            )
            # 추가적으로 이미지 다시 불러와야함
            file_list = os.listdir(self.output_dir / 'imagedetection' / 'crops' / 'traffic_sign')
            classification_img = []
            for f in file_list:
                classification_img.append(Image.open(f).resize((64, 64)))
        else:
            filelist = os.listdir(source)
            img = [Image.open(f) for f in tqdm(filelist)]
            result = self.model0(img, size=size).pandas().xyxy
            classification_img = []
            for im, r in zip(img, result):
                for i in r.index:
                    classification_img = self.resize_img(im, i, classification_img)

        # Image Classification
        result = self.model1(classification_img).argmax(axis=1)
        for im, r in zip(classification_img, result):
            self.save_img(im, r)
        
    def simple_predict(self, image):
        result = self.model0(image, size=640).pandas().xyxy
        classification_img = []
        for r in result:
            for _, i in r.iterrows():
                classification_img = self.resize_img(image, i, classification_img)
        
        classification_img = np.array(classification_img)
        classification_img.reshape([-1, 64, 64, 3])
        result = self.model1(classification_img)
        return result
        
    def resize_img(self, img, result, lst):
        if result['name'] == 'traffic_sign':
            im = img.crop((int(result['xmin']), int(result['ymin']), int(result['xmax']), int(result['ymax'])))
            im = im.resize((64, 64), Image.ANTIALIAS)
            lst.append(np.asarray(im))
        return lst

    def save_img(self, img, result):
        if os.path.isfile(self.output_dir / f'{result}'):
            last_file = os.path.splitext(os.path.listdir(self.output_dir / f'{result}')[-1])[0]
        else:
            last_file = 0
        img.save(self.output_dir / f'{result}' / f'{int(last_file)+1}.jpg')
        pass

    def update_model(self):
        self.model0 = torch.hub.load(dir / 'yolov5', 'custom', path=weight_path, source='local').to(self.device)
        self.model1 = tf.keras.models.load_model(model_dir)


if __name__ == "__main__":
    label = labeling('./output')
    labeling.predict(r'C:\GProjects\data\images\train')

# Create your models here.
