import logging

import numpy as np
from keras.layers import Dense
from keras.layers.recurrent import LSTM
from keras.models import Sequential

from data_reader import ScadaDataFile, VerboseFunc


class LeakTesterModel(object):
    def __init__(self):
        self.saved = True
        pass

    def analyze(self, dataSource,
                input_tags,
                validation,
                timesteps,
                batch_size,
                num_classes):
        """

        :type input_tags: list
        :type dataSource: ScadaDataFile
        """
        self.dataSource = dataSource

        assert isinstance(input_tags, type([]))
        self.input_tags = input_tags
        logging.info("Used tag list for model:")
        for tag in input_tags:
            logging.info(tag)
        self.DATA_DIM = len(self.input_tags)
        logging.debug(VerboseFunc("First layer is ", self.DATA_DIM, "neurons wide"))

        self.VALIDATION_PART = validation
        logging.info("Validation data is %i lenth" % self.VALIDATION_PART)

        self.TIMESTEPS = timesteps
        logging.info("Timesteps = %i" % self.TIMESTEPS)

        self.BATCH_SIZE = batch_size
        logging.info("Batch size:%i" % self.BATCH_SIZE)

        self.NUM_CLASSES = num_classes
        logging.info("Output classes = %i" % self.NUM_CLASSES)

        # normalize and constructing working array
        data = np.zeros((dataSource.data.shape[0], 1), dtype=np.float64)
        for tag in dataSource.tags_list:
            if tag in self.input_tags:
                logging.debug("Found tag %s in input data" % tag)
                tag_data = dataSource.data[..., dataSource.tags_list.index(tag)]
                data = np.c_[data, tag_data]
                pass
            else:
                logging.debug("Skip tag %s in input data" % tag)
        data = np.delete(data, 0, 1)

        # normalize all data
        logging.debug('Normalising input data')
        self.data = 1 / data

        self.NUM_OF_FRAMES = self.data.shape[0] - self.TIMESTEPS - 1 - self.VALIDATION_PART

        # train data
        self.X = np.zeros((self.BATCH_SIZE * self.NUM_OF_FRAMES, self.TIMESTEPS, self.DATA_DIM), dtype=np.float64)
        self.Y = np.zeros((self.BATCH_SIZE * self.NUM_OF_FRAMES, self.DATA_DIM), dtype=np.float64)

        for frame_ in range(self.NUM_OF_FRAMES):
            # error here!
            # input_string_number =
            self.X[frame_] = self.data[frame_:frame_ + self.TIMESTEPS, ...]
            self.Y[frame_] = self.data[frame_ + self.TIMESTEPS + 1]

        # validate data
        self.X_val = np.zeros((self.BATCH_SIZE * self.VALIDATION_PART, self.TIMESTEPS, self.DATA_DIM), dtype=np.float64)
        self.Y_val = np.zeros((self.BATCH_SIZE * self.VALIDATION_PART, self.DATA_DIM), dtype=np.float64)

        for frame_ in range(self.NUM_OF_FRAMES, self.NUM_OF_FRAMES + self.VALIDATION_PART):
            self.X_val[frame_] = data[frame_:frame_ + self.TIMESTEPS, ...]
            self.Y_val[frame_] = data[frame_ + self.TIMESTEPS + 1]


        logging.info('Input data prepared successfully')

    def compile(self):
        self.model = Sequential()
        model = self.model
        model.add(LSTM(self.DATA_DIM * 2,
                       return_sequences=True,
                       stateful=True,
                       batch_input_shape=(self.BATCH_SIZE, self.TIMESTEPS, self.DATA_DIM
                                          )
                       )
                  )
        model.add(LSTM(self.DATA_DIM * 2,
                       return_sequences=True,
                       stateful=True
                       )
                  )
        model.add(LSTM(self.DATA_DIM * 2,
                       stateful=True
                       )
                  )
        model.add(Dense(self.DATA_DIM,
                        activation='sigmoid'
                        )
                  )
        model.compile(loss='mean_absolute_percentage_error',
                      optimizer='adagrad',
                      metrics=['accuracy']
                      )
        logging.info('Model compiled successfully')

        model.fit(self.X, self.Y,
                  batch_size=self.BATCH_SIZE,
                  epochs=5,
                  shuffle=False,
                  validation_data=(self.X_val, self.Y_val)
                  )
