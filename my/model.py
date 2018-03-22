import logging
import tkinter as tk

import numpy as np
from keras.layers import Dense
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.models import load_model

import tkSimpleDialog
from config_case import *
from data_reader import VerboseFunc
from data_slicer import slicer
from tbcallback_mod import TB
from tkTagSelector import TagSelectorWidget


# from keras.callbacks import TensorBoard


class CommonModelConfigureGUI(tkSimpleDialog.ModelConfigDialog):
    """"Это тестовое окно для испытания диалога конфигуратора модели.
    Не делает ничего"""

    def body(self, master):
        tk.Label(master, text="Создать диалог на основе\n этого необходимо.").grid(row=0, columnspan=2)

        tk.Label(master, text="First:").grid(row=1)
        tk.Label(master, text="Second:").grid(row=2)

        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master)

        self.e1.grid(row=1, column=1)
        self.e2.grid(row=2, column=1)
        return self.e1  # initial focus

    def apply(self):
        first = int(self.e1.get())
        second = int(self.e2.get())
        logging.info("First: %i \nSecond: %i" % (first, second))  # or something


class LeakTesterModelConfigureGUI(tkSimpleDialog.ModelConfigDialog):
    """"Диалоговое окно конфигуратора модели LeakTesterModel"""

    def body(self, master):
        self.input_tagselect_widget = TagSelectorWidget(master, text='select input tags', tagslist=self.taglist)
        self.input_tagselect_widget.grid(row=0, column=0)

        self.output_tagselect_widget = TagSelectorWidget(master, text='select output tags', tagslist=self.taglist,
                                                         checked=False)
        self.output_tagselect_widget.grid(row=0, column=1)

        tk.Label(master, text="Time steps:").grid(row=2)
        tk.Label(master, text="Batch size:").grid(row=3)

        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master)

        self.e1.grid(row=2, column=1)
        self.e2.grid(row=3, column=1)
        return self.e1  # initial focus

    def apply(self):
        model_config = self.model_config = {}
        model_config[INPUT_TAGS] = self.input_tagselect_widget.selected_tags
        model_config[OUTPUT_TAGS] = self.output_tagselect_widget.selected_tags
        model_config[TIME_STEPS] = int(self.e1.get())
        model_config[BATCH_SIZE] = int(self.e2.get())
        logging.info(str(model_config))  # or something


class CommonModel(object):

    def __init__(self):
        self.saved = False
        self.trained = False
        pass

    def train(self, *args, **kwargs):
        """Train compiled model"""
        logging.warning("Method is not defined!")
        pass

    def savemodel(self, filepath):
        """save model to file"""
        # https://keras.io/getting-started/faq/#how-can-i-save-a-keras-model
        logging.info("saving model to '%s'" % filepath)
        try:
            self.model.save(filepath)
            self.saved = True
        except AttributeError:
            logging.error('Model was not initialised properly!')
        except IOError:
            logging.error("Input-output error! File: '%s'" % filepath)

    def loadmodel(self, filepath):
        """Loadmodel from file
        returns a compiled model"""
        try:
            self.model = load_model(filepath)
            self.saved = True
        except IOError:
            logging.error("Input-output error! File: '%s'" % filepath)

    def gui_model_configure(self, parent):
        result = CommonModelConfigureGUI(parent, title="Диалог настройки модели")


class LeakTesterModel(CommonModel):
    '''Simple LSTM stateless model'''

    def analyze_and_train(self,
                          dataSource,
                          ):
        """
        конфигурация уже должна быть представлена в аттрибуте
        self.model_config
        Stacked LSTM for sequence classification. Not statefull!
        """
        self.dataSource = dataSource

        input_tags = self.model_config[INPUT_TAGS]
        logging.info("Used tag list for model:")
        [logging.info(tag) for tag in input_tags]

        # Do I really need next? YES!
        self.DATA_DIM = len(input_tags)
        logging.debug(VerboseFunc("First layer will get data ", self.DATA_DIM, " wide"))

        timesteps = self.model_config[TIME_STEPS]
        logging.info("Timesteps = %i" % timesteps)

        num_classes = len(self.model_config[OUTPUT_TAGS])
        logging.debug("Output classes:")
        [logging.debug(tag) for tag in self.model_config[OUTPUT_TAGS]]

        # normalize and constructing working array
        # данные переносятся из исходного массива dataSource.data
        # в новый массив, исключая ненужные теги
        # ось 0 - временнАя ось
        # ось 1 - ось данных тегов
        # форма массива, должна соответствовать исходному массиву.
        # нулевая колонка - не содержит данных. она для создания массива нужной формы
        in_data = slicer(dataSource=dataSource, tags=input_tags)
        out_data = slicer(dataSource=dataSource, tags=self.model_config[OUTPUT_TAGS])

        # normalize all data
        logging.debug('Normalising input data')
        # WARNING! DIVIDE BY ZERO!
        in_data = 1 / in_data
        out_data = 1 / out_data

        num_of_frames = in_data.shape[0] - timesteps - 1
        logging.info("Input data will split into %i frames" % num_of_frames)

        batch_size = self.model_config[BATCH_SIZE]  #

        # Делим входные данные на временнЫе наборы.
        # Ось 0 - номер набора
        # Ось 1 - в диапазоне времени [номер набора] - [номер набора + размер временного набора]
        # Ось 2 - по списку тегов
        # train data
        X = np.zeros((num_of_frames, timesteps, self.DATA_DIM), dtype=np.float64)
        Y = np.zeros((num_of_frames, num_classes), dtype=np.float64)

        for frame_ in range(num_of_frames):
            X[frame_] = in_data[frame_:frame_ + timesteps, ...]
            Y[frame_] = out_data[frame_ + timesteps]

        # # validate data
        # self.X_val = np.zeros((validation_tail, self.TIMESTEPS, self.DATA_DIM), dtype=np.float64)
        # self.Y_val = np.zeros((validation_tail, self.NUM_CLASSES), dtype=np.float64)
        #
        # for frame_ in range(self.NUM_OF_FRAMES, self.NUM_OF_FRAMES + validation_tail):
        #     self.X_val[frame_ - self.NUM_OF_FRAMES] = self.data[frame_:frame_ + self.TIMESTEPS, ...]
        #     self.Y_val[frame_ - self.NUM_OF_FRAMES] = self.data[frame_ + self.TIMESTEPS]

        logging.info('Input data prepared successfully')

        self.saved = False
        self.compile()
        self.tbCallBack = TB(log_dir=TENSOR_BOARD_LOGDIR,
                             histogram_freq=1,
                             write_graph=True,
                             write_images=False,
                             )
        self.model.fit(X, Y,
                       batch_size=batch_size,
                       epochs=5,  # todo: GUI
                       shuffle=False,
                       validation_split=0.2,  # todo: GUI
                       callbacks=[self.tbCallBack]
                       )
        self.trained = True

    def compile(self):
        # expected input data shape for this model: (batch_size, timesteps, data_dim)
        # https://keras.io/getting-started/sequential-model-guide/#getting-started-with-the-keras-sequential-model
        self.model = Sequential()
        model = self.model
        model.add(LSTM(self.DATA_DIM * 2,
                       return_sequences=True,
                       input_shape=(self.model_config[TIME_STEPS], self.DATA_DIM)
                       )
                  )
        model.add(LSTM(self.DATA_DIM * 2,
                       return_sequences=True)
                  )
        model.add(LSTM(self.DATA_DIM * 2)
                  )
        model.add(Dense(len(self.model_config[OUTPUT_TAGS]),
                        activation='softmax'
                        )
                  )
        model.compile(loss='mean_absolute_percentage_error',
                      optimizer='adagrad',
                      metrics=['accuracy']
                      )
        logging.info('Model compiled successfully')
        logging.info(model.summary(line_length=50))

    def gui_model_configure(self, parent, tag_list):
        self.model_config = LeakTesterModelConfigureGUI(parent, title=self.__doc__, taglist=tag_list).model_config
        self.saved = False
        logging.debug(str(self.model_config))
