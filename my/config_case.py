INPUT_TAGS = 'input tags'
OUTPUT_TAGS = 'output tags'
TIME_STEPS = 'time steps'
BATCH_SIZE = 'batch size'
TENSOR_BOARD_LOGDIR = '/dev/shm/logs'
ALL_TAGS = 'all tags'
EPOCH = 'epoch'
VALIDATION_PART = 'valid part'
ACTIVATION_LAST_LAYER = 'activation_ll'
OPTIMASER_COMPILE = 'optimizer_comp'
LOSS_COMPILE = 'loss_comp'


class DataRange(object):
    def __init__(self, minim, maxim):
        self.min = minim
        self.max = maxim


# use only UPPER case symbols!
NORMALISE_DICT = {
    'PT': DataRange(0, 8000),
    'TT': DataRange(-10, 50),
    'FT': DataRange(0, 10000),
    'other': DataRange(-10000, 100000),
}
