import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation,Dropout
from keras.layers.recurrent import LSTM
from data_reader import ScadaDataFile

dataSource = ScadaDataFile()
dataSource.load_data('../../data/dataset1')
data = 1/dataSource.data

DATA_DIM = len(dataSource.tags_list)
VALIDATION_PART = int(DATA_DIM/5)
TIMESTEPS = 100
BATCH_SIZE = 10
NUM_CLASSES = DATA_DIM  # кол-во выходных классов соответствует количеству входных датчиков

# кол-во фрэймов продолжительностью TIMESTEPS во входных данных не включая хвост валидации
NUM_OF_FRAMES = data.shape[0]-TIMESTEPS-1-VALIDATION_PART

X = np.zeros((BATCH_SIZE*NUM_OF_FRAMES, TIMESTEPS, DATA_DIM), dtype=np.float64)
Y = np.zeros((BATCH_SIZE*NUM_OF_FRAMES, DATA_DIM), dtype=np.float64)

for frame_ in range(NUM_OF_FRAMES):
    X[frame_] = data[frame_:frame_+TIMESTEPS, ...]
    Y[frame_] = data[frame_+TIMESTEPS+1]

X_val = np.zeros((BATCH_SIZE*VALIDATION_PART, TIMESTEPS, DATA_DIM), dtype=np.float64)
Y_val = np.zeros((BATCH_SIZE*VALIDATION_PART, DATA_DIM), dtype=np.float64)

for frame_ in range(NUM_OF_FRAMES, NUM_OF_FRAMES+VALIDATION_PART):
    X[frame_] = data[frame_:frame_+TIMESTEPS, ...]
    Y[frame_] = data[frame_+TIMESTEPS+1]

model = Sequential()
model.add(LSTM(DATA_DIM*2,
               return_sequences=True,
               stateful=True,
               batch_input_shape=(BATCH_SIZE, TIMESTEPS, DATA_DIM
                                  )
               )
          )
model.add(LSTM(DATA_DIM*2,
               return_sequences=True,
               stateful=True
               )
          )
model.add(LSTM(DATA_DIM*2,
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

