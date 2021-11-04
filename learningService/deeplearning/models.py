from django.db import models

import os
import zipfile
import numpy as np
from tensorflow.python.eager.context import check_alive
from tqdm.auto import tqdm
from pathlib import Path

import tensorflow as tf
from keras.callbacks import EarlyStopping
from keras.preprocessing.image import ImageDataGenerator

# Tensorflow의 GPU 메모리 할당 문제를 해결해주는 코드(Tensorflow >= 2.0.0)
gpu_devices = tf.config.experimental.list_physical_devices('GPU')
for device in gpu_devices:
    tf.config.experimental.set_memory_growth(device, True)

dir = os.path.dirname(os.path.abspath(__file__))


class classificationModel():
    def __init__(self, model_dir):
        # Load Model
        self.model = tf.keras.models.load_model(model_dir)

    # Train
    def train(self, data_dir):
        data_gen = ImageDataGenerator(
            rescale=1./255
            ) # 리스케일링 되었는지 모르겠음
        train_gen = data_gen.flow_from_directory(
            data_dir, 
            target_size=(64, 64),
            batch_size=32,
            class_mode='categorical'
            )

        early_stopping = EarlyStopping(monitor='val_loss', patience=10)
        history = self.model.fit(
            train_gen,
            batch_size=32, 
            epochs=100, 
            validation_split=0.2, 
            callbacks=[early_stopping], 
            workers=0, 
            use_multiprocessing=True)

    # zip model
    def zipmodel(self, output_dir='./best'):
        tf.keras.models.save_modeL(Path(output_dir) / 'model')

        os.chdir(dir)
        with zipfile.ZipFile('model.zip', 'w') as zip:
            for dirpath, dirnames, filenames in os.walk(Path(output_dir) / 'model'):
                zip.write(dirnames)
                for filename in filenames:
                    zip.write(os.path.join(dirpath,filename))
            zip.close()     