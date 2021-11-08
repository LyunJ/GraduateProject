import os
import zipfile
import numpy as np
from tensorflow.python.eager.context import check_alive
from tqdm.auto import tqdm
from pathlib import Path

import tensorflow as tf
from keras.callbacks import EarlyStopping
from keras.preprocessing.image import ImageDataGenerator
import zipfile 
import shutil

# Tensorflow의 GPU 메모리 할당 문제를 해결해주는 코드(Tensorflow >= 2.0.0)
gpu_devices = tf.config.experimental.list_physical_devices('GPU')
for device in gpu_devices:
    tf.config.experimental.set_memory_growth(device, True)

dir = os.path.dirname(os.path.abspath(__file__))


class classificationModel():
    def __init__(self, model_dir):
        # Load Model
        self.delete_model(model_dir)
        model_name = 'model_new.zip' if os.path.isfile(Path(model_dir) / 'model_new.zip') else 'model.zip'
        with zipfile.ZipFile(Path(model_dir) / model_name) as zip:
            zip.extractall(Path(model_dir))
        self.model = tf.keras.models.load_model(model_dir)

    # Train
    def train(self, data_dir):
        data_gen = ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2,
            )
        train_gen = data_gen.flow_from_directory(
            data_dir, 
            target_size=(64, 64),
            batch_size=32,
            class_mode='categorical',
            subset='training'
            )
        valid_gen = data_gen.flow_from_directory(
            data_dir,
            target_size=(64, 64),
            batch_size=32,
            class_mode='categorical',
            subset='validation'
        )

        early_stopping = EarlyStopping(monitor='val_loss', patience=10)
        history = self.model.fit(
            train_gen,
            batch_size=32, 
            epochs=100,
            validation_data = valid_gen,
            callbacks=[early_stopping], 
            workers=0, 
            use_multiprocessing=True)

    # zip model
    def zipmodel(self, output_dir='./best'):
        tf.keras.models.save_model(self.model, Path(output_dir) / 'model')
        print('model saving complete')

        origin_dir = os.getcwd()

        with zipfile.ZipFile('./deeplearning/parameterFile/model_new.zip', 'w') as zip:
            os.chdir(Path(dir) / 'parameterFile' / 'model')
            for path, dirs, files in os.walk('./'):
                zip.write('assets')
                for file in files:
                    zip.write(os.path.join(path, file))
            zip.close()
        os.chdir(origin_dir)

    def delete_model(self, model_dir):
        if os.path.isdir(Path(model_dir) / 'assets'):
            os.rmdir(Path(model_dir) / 'assets')
        if os.path.isdir(Path(model_dir) / 'variables'):
            shutil.rmtree(Path(model_dir) / 'variables')
        delete_list = [x for x in os.listdir(model_dir) if x not in ['model', 'model.zip', 'model_new.zip']]
        for delete in delete_list:
            os.remove(Path(model_dir) / delete)