import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation,Dropout
from keras.layers.recurrent import LSTM
from data_reader import ScadaDataFile

np.random.seed(17)
FRAME_SIZE = 100

dataSource = ScadaDataFile()
dataSource.load_data('../../data/dataset1')

data = 1/dataSource.data
DATA_WIDTH = len(dataSource.tags_list)

NUM_OF_FRAMES = data.shape[0]-FRAME_SIZE-1

X = np.zeros((NUM_OF_FRAMES, FRAME_SIZE, DATA_WIDTH), dtype=np.float64)
Y = np.zeros((NUM_OF_FRAMES, DATA_WIDTH), dtype=np.float64)

for frame_ in range(NUM_OF_FRAMES):
    X[frame_] = data[frame_:frame_+FRAME_SIZE, ...]
    Y[frame_] = data[frame_+FRAME_SIZE+1]


model = Sequential()
model.add(Dense(100, input_shape = (FRAME_SIZE, DATA_WIDTH)))
model.add(Activation('relu'))
model.add(LSTM(57, return_sequences=True))
model.add(LSTM(DATA_WIDTH*2))
model.add(Dropout(0.5))
model.add(Dense(DATA_WIDTH))
model.add(Activation('sigmoid'))

model.compile(optimizer='rmsprop',
              loss='mse')

model.fit(X, Y, )

A = model.call(X)
print( 1/A )
pass

