# core import
from collections import OrderedDict
# lib imports
from tkinter import *

# my modules imports
import layers_opt
from label_link import LabelLink
from layers_opt import BoolProp, SelectOneProp, IntRangeProp
from layers_opt import layer_activation_any, num_of_units_any, avail_act, avail_initializer
from tkSimpleDialog import Dialog

COLUMN0_W = 200


class ActivationConfigWidget(Frame):
    DROP = '** X **'

    def __init__(self, master, act_conf_obj):
        super().__init__(master, bd=2)
        assert isinstance(act_conf_obj, layers_opt.SelectOneProp), "Bad configuration object"
        self.ac = act_conf_obj  # Activation Config
        self.create_widgets()

    # def create_widgets(self):
    #     ac = self.ac
    #     scrollbar = Scrollbar(self)
    #     scrollbar.pack(side=RIGHT, fill=Y)
    #
    #     listbox = Listbox(self, bd=0, yscrollcommand=scrollbar.set)
    #     listbox.pack()
    #
    #     scrollbar.config(command=listbox.yview)
    #
    #     for item in ac:
    #         listbox.insert(END, item)

    def create_widgets(self):
        ac = self.ac
        variable = StringVar()

        w = OptionMenu(self, variable, *[i for i in ac])
        w.config(width=20)
        w.grid(row=0, column=1)

        b = Button(self, text='DROP', command=self.drop_config)
        b.config(width=6)
        b.grid(row=0, column=2)

        LabelLink(self, www=ac.www).grid(row=0, column=3)
        Label(self, text=ac.__doc__).grid(row=0, column=0)

        self.var = variable
        variable.trace_variable('w', self.callback)

        self.columnconfigure(0, minsize=COLUMN0_W)

    def drop_config(self):
        self.ac.drop()
        self.var.set('')

    def callback(self, *args):
        if len(self.var.get()):
            self.ac(self.var.get())


class NumOfUnitsConfigWidget(Frame):
    def __init__(self, master, intrange_conf_obj):
        super().__init__(master)
        assert isinstance(intrange_conf_obj,
                          layers_opt.IntRangeProp), 'Bad configuration object. Must be %s' % layers_opt.IntRangeProp.__name__
        self.uc = intrange_conf_obj  # num of Units Config
        self.create_widgets()

    def create_widgets(self):
        uc = self.uc
        variable = IntVar()

        sb = Spinbox(self, from_=uc.min, to=uc.max, textvariable=variable)
        sb.config(width=20)
        sb.grid(row=0, column=1)

        Label(self, text='' * 6).grid(row=0, column=2)  # placeholder
        LabelLink(self, www=uc.www).grid(row=0, column=3)
        Label(self, text=uc.__doc__).grid(row=0, column=0)

        self.var = variable
        variable.trace_variable('w', self.callback)

        self.columnconfigure(0, minsize=COLUMN0_W)

    def callback(self, *args):
        self.uc(self.var.get())


class BoolConfigWidget(Frame):
    def __init__(self, master, bool_conf_obj):
        super().__init__(master)
        assert isinstance(bool_conf_obj,
                          layers_opt.BoolProp), 'Bad configuration object. Must be %s' % layers_opt.BoolProp.__name__
        self.bc = bool_conf_obj  # boolean config
        self.create_widgets()

    def create_widgets(self):
        bc = self.bc
        variable = BooleanVar()

        c = Checkbutton(self, text=bc.__doc__, variable=variable)
        c.grid(row=0, column=1)

        Label(self, text='' * 6).grid(row=0, column=2)  # placeholder
        LabelLink(self, www=bc.www).grid(row=0, column=3)
        Label(self, text=bc.__doc__).grid(row=0, column=0)

        self.var = variable
        variable.trace_variable('w', self.callback)

        self.columnconfigure(0, minsize=COLUMN0_W)

    def callback(self, *args):
        self.bc(self.var.get())


class LSTMLayerConfigWidget(Frame):
    def __init__(self, master=None, layer_conf=None):
        super().__init__(master)
        self.layer_conf = layer_conf
        self.create_widgets()

    def create_widgets(self):
        lc = self.layer_conf  # Layer Config
        Label(self, text=lc['name'], font=("Helvetica", 20)).pack(pady=10)
        LabelLink(self, www=lc['www']).pack()

        units_config = NumOfUnitsConfigWidget(self, layers_opt.NumOfUnitsAny)
        units_config.pack(pady=10)

        activation_config = ActivationConfigWidget(self, layers_opt.LayerActivationAny)
        activation_config.pack(pady=5)

        recurrent_activation_config = ActivationConfigWidget(self, layers_opt.RecurrentActivationAny)
        recurrent_activation_config.pack(pady=5)

        use_bias_config = BoolConfigWidget(self, layers_opt.BoolProp('Use bias', ))
        use_bias_config.pack(pady=5)


class LayerConfigDialog(Dialog):
    def __init__(self, master=None, layer_conf=None):
        self.layer_conf = layer_conf
        # self.create_widgets()
        super().__init__(master, title="Layer Configuration")

    def body(self, master):
        lc = self.layer_conf  # Layer Config
        Label(self, text=lc['name'], font=("Helvetica", 20)).pack(pady=10)
        LabelLink(self, www=lc['www']).pack()

        for c in lc['layer_conf']:
            conf = lc['layer_conf'][c]
            if isinstance(conf, BoolProp):
                BoolConfigWidget(self, conf).pack()
            if isinstance(conf, SelectOneProp):
                ActivationConfigWidget(self, conf).pack()
            if isinstance(conf, IntRangeProp):
                NumOfUnitsConfigWidget(self, conf).pack()


if __name__ == '__main__':
    # layer dialog configuration example
    lstm_config_ex = dict(name='Long Short-Term Memory layer',
                          www=r'https://keras.io/layers/recurrent/#lstm',
                          layer_conf=OrderedDict([
                              ('units', num_of_units_any()),
                              ('activation', layer_activation_any()),
                              ('recurrent_activation', SelectOneProp(avail_act,
                                                                     description='Activation function to use\nfor the recurrent step ',
                                                                     www=r'https://keras.io/activations/')),
                              ('use_bias',
                               BoolProp(description='Use bias', help_='Boolean, whether the layer uses a bias vector')),
                              ('kernel_initializer', SelectOneProp(avail_initializer,
                                                                   description='Initializer for the kernel weights matrix,\nused for the linear transformation of the inputs',
                                                                   www=r'https://keras.io/initializers/')),
                              ('recurrent_initializer', SelectOneProp(avail_initializer,
                                                                      description='Initializer for the recurrent_kernel weights matrix,\nused for the linear transformation of the recurrent state',
                                                                      www=r'https://keras.io/initializers/')),
                              ('bias_initializer', SelectOneProp(avail_initializer,
                                                                 description='Initializer for the bias vector',
                                                                 www=r'https://keras.io/initializers/')),
                              ('unit_forget_bias', BoolProp(description='Forget gate',
                                                            help_='If True, add 1 to the bias of the forget gate at initialization',
                                                            www='http://www.jmlr.org/proceedings/papers/v37/jozefowicz15.pdf')),

                              ('return_sequences', BoolProp(description='Return sequences',
                                                            help_='Whether to return the last output in the output sequence, or the full sequence')),
                              ('return_state', BoolProp(description='Return state',
                                                        help_='Whether to return the last state in addition to the output')),
                              ('stateful', BoolProp(description='Stateful',
                                                    help_='If True, the last state for each sample at index i in a batch will be used as initial state for the sample of index i in the following batch')),
                          ])
                          )

    import os

    root = Tk()
    root.title(os.name)

    w = LayerConfigDialog(root, lstm_config_ex)
    #w.pack()

    # l = ActivationConfigWidget(root, layers_opt.LayerActivationAny)
    # l.pack(fill=BOTH)

    root.mainloop()
