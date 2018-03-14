import logging

import numpy as np
from keras.layers import Dense
from keras.layers.recurrent import LSTM
from keras.models import Sequential

from data_reader import ScadaDataFile, VerboseFunc


class LeakTesterModel(object):
    def __init__(self):
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
        data = np.zeros((dataSource.data.shape[0],), dtype=np.float64)
        for tag in dataSource.tags_list:
            if tag in self.input_tags:
                logging.debug("Found tag %s in input data" % tag)
                data = np.concatenate((data, dataSource.data[..., dataSource.tags_list.index(tag)]), axis=1)
                pass
            else:
                logging.debug("Skip tag %s in input data" % tag)
        data = np.delete(data, 0, 1)

        # normalize all data
        self.data = 1 / dataSource.data

        self.NUM_OF_FRAMES = self.data.shape[0] - self.TIMESTEPS - 1 - self.VALIDATION_PART

        self.X = np.zeros((self.BATCH_SIZE * self.NUM_OF_FRAMES, self.TIMESTEPS, self.DATA_DIM), dtype=np.float64)
        self.Y = np.zeros((self.BATCH_SIZE * self.NUM_OF_FRAMES, self.DATA_DIM), dtype=np.float64)

        for frame_ in range(self.NUM_OF_FRAMES):
            # input_string_number =
            X[frame_] = data[frame_:frame_ + TIMESTEPS, ...]
            Y[frame_] = data[frame_ + TIMESTEPS + 1]


# dataSource = ScadaDataFile()
# dataSource.load_data('../../data/dataset1')
# data = 1/dataSource.data

# DATA_DIM = len(dataSource.tags_list)  # ok
# VALIDATION_PART = int(DATA_DIM/5)     #  ??
# TIMESTEPS = 100  #
# BATCH_SIZE = 10
# NUM_CLASSES = DATA_DIM  # кол-во выходных классов соответствует количеству входных датчиков

# кол-во фрэймов продолжительностью TIMESTEPS во входных данных не включая хвост валидации
# NUM_OF_FRAMES = data.shape[0]-TIMESTEPS-1-VALIDATION_PART

# X = np.zeros((BATCH_SIZE*NUM_OF_FRAMES, TIMESTEPS, DATA_DIM), dtype=np.float64)
# Y = np.zeros((BATCH_SIZE*NUM_OF_FRAMES, DATA_DIM), dtype=np.float64)

if False:
    for frame_ in range(NUM_OF_FRAMES):
        X[frame_] = data[frame_:frame_ + TIMESTEPS, ...]
        Y[frame_] = data[frame_ + TIMESTEPS + 1]

    X_val = np.zeros((BATCH_SIZE * VALIDATION_PART, TIMESTEPS, DATA_DIM), dtype=np.float64)
    Y_val = np.zeros((BATCH_SIZE * VALIDATION_PART, DATA_DIM), dtype=np.float64)

    for frame_ in range(NUM_OF_FRAMES, NUM_OF_FRAMES + VALIDATION_PART):
        X[frame_] = data[frame_:frame_ + TIMESTEPS, ...]
        Y[frame_] = data[frame_ + TIMESTEPS + 1]

    model = Sequential()
    model.add(LSTM(DATA_DIM * 2,
                   return_sequences=True,
                   stateful=True,
                   batch_input_shape=(BATCH_SIZE, TIMESTEPS, DATA_DIM
                                      )
                   )
              )
    model.add(LSTM(DATA_DIM * 2,
                   return_sequences=True,
                   stateful=True
                   )
              )
    model.add(LSTM(DATA_DIM * 2,
                   stateful=True
                   )
              )
    model.add(Dense(DATA_DIM,
                    activation='sigmoid'
                    )
              )
    model.compile(loss='mean_absolute_percentage_error',
                  optimizer='adagrad',
                  metrics=['accuracy']
                  )

    model.fit(X, Y,
              batch_size=BATCH_SIZE,
              epochs=5,
              shuffle=False,
              validation_data=(X_val, Y_val)
              )
