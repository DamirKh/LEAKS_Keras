from tkinter import *

from config_case import *

# http://effbot.org/tkinterbook/checkbutton.htm

activation_choice = [
    ('Softmax function', 'softmax'),
    ('softplus', 'softplus'),
    ('softsign', 'softsign'),
    ('relu', 'relu'),
    ('tanh', 'tanh'),
    ('sigmoid', 'sigmoid'),
    ('hard_sigmoid', 'hard_sigmoid'),
    ('linear', 'linear'),
]

loss_func_choice = [
    ('mean squared error', 'mean_squared_error'),
    ('mean absolute error', 'mean_absolute_error'),
    ('mean absolute percentage error', 'mean_absolute_percentage_error'),
    ('mean_squared_logarithmic_error', 'mean_squared_logarithmic_error'),
    ('squared_hinge', 'squared_hinge'),
    ('hinge', 'hinge'),
    ('categorical_hinge', 'categorical_hinge'),
    ('logcosh', 'logcosh'),
    ('categorical_crossentropy', 'categorical_crossentropy'),
    ('sparse_categorical_crossentropy', 'sparse_categorical_crossentropy'),
    ('binary_crossentropy', 'binary_crossentropy'),
    ('kullback_leibler_divergence', 'kullback_leibler_divergence'),
    ('poisson', 'poisson'),
    ('cosine_proximity', 'cosine_proximity'),
]

optimaiser_choice = [
    ('Stochastic gradient descent', 'sgd'),
    ('RMSProp', 'rmsprop'),
    ('Adagrad', 'adagrad'),
    ('Adadelta', 'adadelta'),
    ('Adam', 'adam'),
    ('Adamax', 'adamax'),
    ('Nesterov Adam', 'nadam'),
]


class ModelConfigurator(LabelFrame):
    # todo: add selected_tags as parametr
    def __init__(self, master=None, model_config={}):
        super().__init__(master, text="Model properties")
        self.model_config = model_config

        self.activation_var = StringVar()
        self.activation_var.set(self.model_config.get(ACTIVATION_LAST_LAYER, 'softmax'))

        self.lossfunc_var = StringVar()
        self.lossfunc_var.set(self.model_config.get(LOSS_COMPILE, 'mean_squared_error'))

        self.optimiser_var = StringVar()
        self.optimiser_var.set(self.model_config.get(OPTIMASER_COMPILE, 'sgd'))

        self.create_widgets()

    def create_widgets(self):
        Label(self, text='Last layer activation func:').pack()
        for text, mode in activation_choice:
            b = Radiobutton(self, text=text,
                            variable=self.activation_var, value=mode,
                            command=self.cb)
            b.pack(anchor=W)

        Label(self, text='Loss func:').pack()
        for text, mode in loss_func_choice:
            b = Radiobutton(self, text=text,
                            variable=self.lossfunc_var, value=mode,
                            command=self.cb)
            b.pack(anchor=W)

        Label(self, text='Optimiser:').pack()
        for text, mode in optimaiser_choice:
            b = Radiobutton(self, text=text,
                            variable=self.optimiser_var, value=mode,
                            command=self.cb)
            b.pack(anchor=W)

    def cb(self):
        self.model_config[ACTIVATION_LAST_LAYER] = self.activation_var.get()
        self.model_config[LOSS_COMPILE] = self.lossfunc_var.get()
        self.model_config[OPTIMASER_COMPILE] = self.optimiser_var.get()
