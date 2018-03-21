import logging
import tkinter as tk

import numpy as np
from keras.layers import Dense
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.models import load_model

import tkSimpleDialog
from data_reader import VerboseFunc
from tkTagSelector import TagSelectorWidget


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
        model_config['input_tags'] = self.input_tagselect_widget.selected_tags
        model_config['output_tags'] = self.output_tagselect_widget.selected_tags
        model_config['time_steps'] = int(self.e1.get())
        model_config['batch_size'] = int(self.e2.get())
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

    def analyze(self,
                dataSource,
                input_tags,
                num_classes,
                timesteps,
                validation_tail=100):
        """

        :type input_tags: list
        :type dataSource: ScadaDataFile
        input_tags - список входных тегов. Входных тегов может быть меньше чем в наличии в источнике данных.
        Модель будет тренироваться (и анализировать) только данные в этом списке. Остальные будут проигнорированы.
        num_classes - количество выходных классов. (вообще-то нам нужен список тэгов, которые являются выходными)
        Stacked LSTM for sequence classification. Not statefull!
        """
        self.dataSource = dataSource

        assert isinstance(input_tags, type([]))
        self.input_tags = input_tags
        logging.info("Used tag list for model:")
        for tag in input_tags:
            logging.info(tag)
        self.DATA_DIM = len(self.input_tags)
        logging.debug(VerboseFunc("First layer is ", self.DATA_DIM, "neurons wide"))

        self.TIMESTEPS = timesteps
        logging.info("Timesteps = %i" % self.TIMESTEPS)

        self.NUM_CLASSES = num_classes
        logging.info("Output classes = %i" % self.NUM_CLASSES)

        # normalize and constructing working array
        # данные переносятся из исходного массива dataSource.data
        # в новый массив, исключая ненужные теги
        # ось 0 - временнАя ось
        # ось 1 - ось данных тегов
        # форма массива, должна соответствовать исходному массиву.
        # нулевая колонка - не содержит данных. она для создания массива нужной формы
        data = np.zeros((dataSource.data.shape[0], 1), dtype=np.float64)
        for tag in dataSource.tags_list:
            if tag in self.input_tags:
                logging.debug("Found tag %s in input data" % tag)
                # срез вдоль оси данных
                tag_data = dataSource.data[..., dataSource.tags_list.index(tag)]
                data = np.c_[data, tag_data]
                pass
            else:
                logging.debug("Skip tag %s in input data" % tag)
        # удаляем нулевую колонку: она не содержит данных
        data = np.delete(data, 0, 1)

        # normalize all data
        logging.debug('Normalising input data')
        # WARNING! DIVIDE BY ZERO!
        self.data = 1 / data

        self.NUM_OF_FRAMES = self.data.shape[0] - timesteps - 1 - validation_tail
        logging.info("Input data will split into %i frames" % self.NUM_OF_FRAMES)

        self.BATCH_SIZE = self.TIMESTEPS * 10  # взято от балды TODO: вынести настройку в ГИП

        # Делим входные данные на временнЫе наборы.
        # Ось 0 - номер набора
        # Ось 1 - в диапазоне времени [номер набора] - [номер набора + размер временного набора]
        # Ось 2 - по списку тегов
        # train data
        self.X = np.zeros((self.NUM_OF_FRAMES, self.TIMESTEPS, self.DATA_DIM), dtype=np.float64)
        self.Y = np.zeros((self.NUM_OF_FRAMES, self.NUM_CLASSES), dtype=np.float64)

        for frame_ in range(self.NUM_OF_FRAMES):
            # error here!
            # input_string_number =
            self.X[frame_] = self.data[frame_:frame_ + self.TIMESTEPS, ...]
            self.Y[frame_] = self.data[frame_ + self.TIMESTEPS]

        # validate data
        self.X_val = np.zeros((validation_tail, self.TIMESTEPS, self.DATA_DIM), dtype=np.float64)
        self.Y_val = np.zeros((validation_tail, self.NUM_CLASSES), dtype=np.float64)

        for frame_ in range(self.NUM_OF_FRAMES, self.NUM_OF_FRAMES + validation_tail):
            self.X_val[frame_ - self.NUM_OF_FRAMES] = self.data[frame_:frame_ + self.TIMESTEPS, ...]
            self.Y_val[frame_ - self.NUM_OF_FRAMES] = self.data[frame_ + self.TIMESTEPS]


        logging.info('Input data prepared successfully')

    def compile(self):
        # expected input data shape for this model: (batch_size, timesteps, data_dim)
        # https://keras.io/getting-started/sequential-model-guide/#getting-started-with-the-keras-sequential-model
        self.model = Sequential()
        model = self.model
        model.add(LSTM(self.DATA_DIM * 2,
                       return_sequences=True,
                       input_shape=(self.TIMESTEPS, self.DATA_DIM)
                       )
                  )
        model.add(LSTM(self.DATA_DIM * 2,
                       return_sequences=True)
                  )
        model.add(LSTM(self.DATA_DIM * 2)
                  )
        model.add(Dense(self.NUM_CLASSES,
                        activation='softmax'
                        )
                  )
        model.compile(loss='mean_absolute_percentage_error',
                      optimizer='adagrad',
                      metrics=['accuracy']
                      )
        logging.info('Model compiled successfully')
        logging.info(model.summary(line_length=50))

    def train(self):
        self.saved = False
        self.model.fit(self.X, self.Y,
                  batch_size=self.BATCH_SIZE,
                  epochs=5,
                  shuffle=False,
                  validation_data=(self.X_val, self.Y_val)
                  )
        self.trained = True

    def gui_model_configure(self, parent, tag_list):
        self.model_config = LeakTesterModelConfigureGUI(parent, title=self.__doc__, taglist=tag_list).model_config
        self.saved = False
        logging.debug(str(model_config))
