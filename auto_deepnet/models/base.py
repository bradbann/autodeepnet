from __future__ import absolute_import, division, print_function
import sys
import os
curr_path = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.dirname(os.path.dirname(curr_path)), curr_path] + sys.path
curr_path = None
from auto_deepnet.utils import data_io_utils
import logging
import tarfile
import pandas as pd
from keras.models import load_model

logger = logging.getLogger("auto_deepnet")
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class Base(object):
    def __init__(self,
                 batch_size=512,
                 prediction_batch_size=16,
                 epochs=50,
                 dropout=0.75,
                 optimizer='adagrad',
                 loss='categorical_crossentropy',
                 metrics=['accuracy'],
                 verbose=True,
                 model_checkpoint_path='./model_checkpoint.{epoch:02d}-{val_loss:.2f}.hdf5',
                 model_path='./model.tar',
                 **kwargs):
        self.config = self._generate_config(
            batch_size=batch_size,
            prediction_batch_size=prediction_batch_size,
            epochs=epochs,
            dropout=dropout,
            optimizer=optimizer,
            loss=loss,
            metrics=metrics,
            verbose=verbose,
            model_path=model_path,
            model_checkpoint_path=model_checkpoint_path,
            **kwargs)

    def update_config(self, **kwargs):
        self.config.update(kwargs)

    def _generate_config(self, **kwargs):
        return kwargs

    def _generate_kwargs(self, *args, **kwargs):
        for arg in args:
            kwargs[arg] = kwargs.get(arg, self.config[arg])
        return kwargs

    def get_config(self):
        return self.config

    def build_model(self, **kwargs):
        pass

    def fit(self, X, Y, **kwargs):
        pass

    def predict(self, X, **kwargs):
        pass

    def save_adn_model(self, model_path=None, **kwargs):
        if not model_path:
            model_path = self.config['model_path']
        dir_name, file_name = os.path.split(model_path)
        if len(dir_name) == 0:
            dir_name = '.'
        config_path = os.path.join(dir_name, 'config.pkl')
        keras_model_path = os.path.join(dir_name, 'keras_model.h5')
        data_io_utils.save_data(config_path, self.config, data_is_pandas=False, save_format='pickle', mode='wb', overwrite=True)
        self.model.save(keras_model_path)
        with tarfile.open(model_path, mode='w:gz') as f:
            f.add(config_path, arcname='config.pkl')
            f.add(keras_model_path, arcname='keras_model.h5')
        os.remove(config_path)
        os.remove(keras_model_path)
        

    def load_adn_model(self, model_path=None, **kwargs):
        if not model_path:
            model_path = self.config['model_path']
        dir_name, _ = os.path.split(model_path)
        if len(dir_name) == 0:
            dir_name = '.'
        with tarfile.open(model_path, mode='r:gz') as f:
            f.extractall(dir_name)
        self.config = data_io_utils.load_data(os.path.join(dir_name, 'config.pkl'), load_format='pickle', mode='rb')
        self.model = load_model(os.path.join(dir_name, 'keras_model.h5'))
