import logging
import pickle
import tkinter as tk
from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
from keras.layers import Dense
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.models import load_model

import tkSimpleDialog
from config_case import *
from data_slicer import slicer
from tbcallback_mod import TB
from tkModelConfig import ModelConfigurator
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

        self.input_tagselect_widget = TagSelectorWidget(master,
                                                        text='select input tags',
                                                        tagslist=self.model_config[ALL_TAGS],
                                                        selected_tags=self.model_config[INPUT_TAGS]
                                                        )
        self.input_tagselect_widget.grid(row=0, column=0)

        self.model_configurator_widget = ModelConfigurator(master,
                                                           self.model_config)
        self.model_configurator_widget.grid(row=0, column=1)

        self.output_tagselect_widget = TagSelectorWidget(master,
                                                         text='select output tags',
                                                         tagslist=self.model_config[ALL_TAGS],
                                                         selected_tags=self.model_config[OUTPUT_TAGS]
                                                         )
        self.output_tagselect_widget.grid(row=0, column=2)

        tk.Label(master, text="Time steps:").grid(row=2)

        self.time_steps_var = tk.IntVar()
        self.time_steps_var.set(str(self.model_config[TIME_STEPS]))
        self.e1 = tk.Spinbox(master, from_=1, to=3600, textvariable=self.time_steps_var)
        self.e1.grid(row=2, column=1)

        return self.e1  # initial focus

    def apply(self):
        model_config = self.model_config
        model_config[INPUT_TAGS] = self.input_tagselect_widget.selected_tags
        model_config[OUTPUT_TAGS] = self.output_tagselect_widget.selected_tags
        model_config[TIME_STEPS] = int(self.e1.get())
        # logging.info('Model was configured')
        # logging.debug(str(model_config))  # or something
        self.result = True
        return

    def validate(self):
        if int(self.input_tagselect_widget.count.get()) > 1 and \
                int(self.output_tagselect_widget.count.get()) > 0:
            return True
        else:
            return False


class LeakTesterTrainConfigureGUI(tkSimpleDialog.ModelTrainDialog):
    def body(self, master):
        tk.Label(master, text="These options do not apply to the model,\nbut affect its learning") \
            .grid(row=0, columnspan=2, pady=10)

        tk.Label(master, text="Batch size:").grid(row=1)

        self.batch_size = tk.IntVar()
        self.batch_size.set(str(self.model_config[BATCH_SIZE]))
        self.bs_spin_wdg = tk.Spinbox(master, from_=1, to=1000, textvariable=self.batch_size)
        self.bs_spin_wdg.grid(row=1, column=1)

        tk.Label(master, text="Epochs:").grid(row=2)

        self.epo_num = tk.IntVar()
        self.epo_num.set(str(1))
        self.epo_spin_wdg = tk.Spinbox(master, from_=1, to=100, textvariable=self.epo_num)
        self.epo_spin_wdg.grid(row=2, column=1)

        tk.Label(master, text="Validation:").grid(row=3)

        self.validation_split = tk.Scale(master, from_=0, to=1,
                                         resolution=0.05,
                                         orient=tk.HORIZONTAL,
                                         )
        self.validation_split.grid(row=3, column=1)

    def apply(self):
        self.model_config[BATCH_SIZE] = int(self.batch_size.get())
        self.model_config[EPOCH] = int(self.epo_num.get())
        self.model_config[VALIDATION_PART] = self.validation_split.get()

        self.model.train()


class CommonModel(object):

    def __init__(self, dataSource):
        """При создании модели нужен источник данных"""
        self.saved = False
        self.trained = False
        self.model_config = None
        self.dataSource = dataSource
        pass

    def train(self, *args, **kwargs):
        """Train compiled model"""
        logging.error("Method is not defined!")
        pass

    def savemodel(self, filename):
        """save model to file"""
        # https://keras.io/getting-started/faq/#how-can-i-save-a-keras-model
        logging.info("saving model to '%s'" % filename)
        try:
            f = filename + '.h5'
            self.model.save(f)
            logging.info("Model train data file '%s' saved" % f)
            self.saved = True
        except AttributeError:
            logging.error('Model was not initialised properly!')
        with open(filename + '.h5m', mode='wb') as f:
            try:
                pickler = pickle.Pickler(f)
                pickler.dump(self.model_config)
                logging.info("Model configuration file '%s' saved" % f.name)
                logging.debug("Config:\n%s" % self.model_config)
            except AttributeError:
                logging.error('Model was not initialised properly!')

    def loadmodel(self, filename):
        """Loadmodel from file
        returns a compiled model"""
        logging.info("Loading model from '%s'" % filename)
        try:
            f = filename + '.h5'
            self.model = load_model(f)
            logging.info("Model train data file '%s' loaded" % f)
        except AttributeError:
            logging.error("Model train data '%s' loading ERROR!" % f)

        with open(filename + '.h5m', mode='rb') as f:
            try:
                unpickler = pickle.Unpickler(f)
                self.model_config = unpickler.load()
                logging.info("Model configuration file '%s' loaded" % f.name)
            except AttributeError:
                logging.error("Model configuration file '%s' loaded ERROR!" % f.name)
        self.analyze()


class LeakTesterModel(CommonModel):
    '''Simple LSTM stateless model '''

    def analyze(self):
        """
        конфигурация уже должна быть представлена в аттрибуте
        self.model_config
        Источник данных уже должен быть в аттрибуте
        self.dataSource
        Stacked LSTM for sequence classification. Not statefull!
        """
        # метод нужно вызывать при восстановлении модели из файла .loadmodel()

        logging.info("Analyze input data...")

        input_tags = self.model_config[INPUT_TAGS]
        logging.info("Used tag list for model:")
        [logging.info(tag) for tag in input_tags]

        # Do I really need next? YES!
        # кол-во входных тегов
        self.DATA_DIM = len(input_tags)
        logging.debug("First layer will get data %i wide" % self.DATA_DIM)

        # кол-во шагов на один фрейм временнЫх данных
        timesteps = self.model_config[TIME_STEPS]
        logging.info("Timesteps = %i" % timesteps)

        # кол-во выходных тегов (общий случай: один тег LEAKAGE)
        num_classes = len(self.model_config[OUTPUT_TAGS])
        logging.debug("Output classes:")
        [logging.debug(tag) for tag in self.model_config[OUTPUT_TAGS]]

        # всю эту хрень нужно заменить объектом https://keras.io/preprocessing/sequence/#timeseriesgenerator
        # normalize and constructing working array
        # данные переносятся из исходного массива dataSource.data
        # в новый массив, исключая ненужные теги
        # ось 0 - временнАя ось
        # ось 1 - ось данных тегов
        # форма массива, должна соответствовать исходному массиву.
        # нулевая колонка - не содержит данных. она для создания массива нужной формы
        in_data = slicer(dataSource=self.dataSource, tags=input_tags)
        out_data = slicer(dataSource=self.dataSource, tags=self.model_config[OUTPUT_TAGS])

        # normalize all data
        # нормализация примитавная, нужно переделать
        # варианты:
        # https://machinelearningmastery.com/how-to-scale-data-for-long-short-term-memory-networks-in-python/
        # http://neuronus.com/theory/931-sposoby-normalizatsii-peremennykh.html
        # logging.debug('Normalising input data')
        # WARNING! DIVIDE BY ZERO!
        # in_data = 1 / in_data
        # out_data = 1 / out_data

        # кол-во фреймов во входных данных
        num_of_frames = in_data.shape[0] - timesteps - 1
        logging.info("Input data will split into %i frames" % num_of_frames)

        # Делим входные данные на временнЫе наборы.
        # этот способ жрет память как бык помои, так как многократно копирует входные данные.
        # следует использовать https://keras.io/preprocessing/sequence/#timeseriesgenerator
        # Ось 0 - номер набора
        # Ось 1 - в диапазоне времени [номер набора] - [номер набора + размер временного набора]
        # Ось 2 - по списку тегов
        # train data
        self.X = np.zeros((num_of_frames, timesteps, self.DATA_DIM), dtype=np.float64)
        self.Y = np.zeros((num_of_frames, num_classes), dtype=np.float64)

        for frame_ in range(num_of_frames):
            self.X[frame_] = in_data[frame_:frame_ + timesteps, ...]
            self.Y[frame_] = out_data[frame_ + timesteps]

        logging.info('Input data prepared successfully')

    def train(self):
        self.saved = False
        # self.compile()
        # следует добавить еще коллбэков:
        # для записи лучших результатов тренировки,
        # для остановки в случае отсутсвия положительного результата
        self.tbCallBack = TB(log_dir=TENSOR_BOARD_LOGDIR,
                             histogram_freq=1,
                             write_graph=True,
                             write_images=False,
                             )

        self.model.fit(self.X, self.Y,
                       batch_size=self.model_config[BATCH_SIZE],
                       epochs=self.model_config[EPOCH],  #
                       shuffle=False,
                       validation_split=self.model_config[VALIDATION_PART],
                       callbacks=[self.tbCallBack]
                       )
        self.trained = True

    def compile(self):
        # expected input data shape for this model: (batch_size, timesteps, data_dim)
        # https://keras.io/getting-started/sequential-model-guide/#getting-started-with-the-keras-sequential-model
        # данный метод не нужно вызывать при восстановлении модели из файла методом .loadmodel()
        self.model = Sequential()
        model = self.model
        model.add(LSTM(self.DATA_DIM * 2,
                       activation='tanh',
                       return_sequences=True,
                       input_shape=(self.model_config[TIME_STEPS], self.DATA_DIM)
                       )
                  )
        model.add(LSTM(self.DATA_DIM * 2,
                       activation='tanh',
                       return_sequences=True)
                  )
        model.add(LSTM(self.DATA_DIM * 2,
                       activation='tanh',)
                  )
        model.add(Dense(len(self.model_config[OUTPUT_TAGS]),
                        activation=self.model_config[ACTIVATION_LAST_LAYER],
                        # activation='softmax',
                        use_bias=True,
                        )
                  )
        model.compile(loss=self.model_config[LOSS_COMPILE],
                      optimizer=self.model_config[OPTIMASER_COMPILE],
                      metrics=['accuracy']
                      )
        logging.info('Model compiled successfully')
        logging.info(model.summary(line_length=50))
        self.compiled = True

    def predict(self):
        """Prediction"""
        predictions = self.model.predict(self.X, batch_size=self.model_config[BATCH_SIZE])
        [print(x[0]) for x in predictions]

    def predict_np(self):
        """Predict and save data to np"""
        predictions = self.model.predict(self.X, batch_size=self.model_config[BATCH_SIZE])
        self.predict_np = np.zeros((self.X.shape[0],))
        for i in range(self.X.shape[0]):
            self.predict_np[i] = predictions[i][0]
        x_axe = np.linspace(0, i, i + 1)
        fig, (ax0, ax1, ax3) = plt.subplots(nrows=3)
        ax0.plot(x_axe, self.predict_np)
        ax0.set_title('Prediction')
        # Tweak spacing between subplots to prevent labels from overlapping
        plt.subplots_adjust(hspace=0.5)
        plt.show()

    def gui_model_configure(self, parent, tag_list):
        if self.model_config is None:
            # модель еще не конфигурирована
            logging.debug("Generating new configuration...")
            model_config = {}
            model_config[ALL_TAGS] = tag_list
            model_config[INPUT_TAGS] = tag_list
            model_config[OUTPUT_TAGS] = []
            model_config[TIME_STEPS] = 50
            model_config[BATCH_SIZE] = 50
            self.model_config = model_config
        temporary_config = deepcopy(self.model_config)
        result = LeakTesterModelConfigureGUI(parent,
                                             title=self.__doc__,
                                             model_config=self.model_config).result
        if result:
            logging.debug("Model configured!")
            global DATA
            self.analyze()
            self.compile()
            self.saved = False
        else:
            logging.debug("Model configuring canceled.")
            self.model_config = temporary_config
        logging.debug(str(self.model_config))
