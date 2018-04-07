from tkinter import *

import layers_opt
# my modules next
from label_link import LabelLink

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


class LayerConfigWidget(Frame):
    def __init__(self, master=None, layer_conf=None):
        super().__init__(master)
        self.layer_conf = layer_conf
        self.create_widgets()

    def create_widgets(self):
        lc = self.layer_conf  # Layer Config
        Label(self, text=lc['name']).pack()
        LabelLink(self, www=lc['www']).pack()

        units_config = NumOfUnitsConfigWidget(self, layers_opt.NumOfUnitsAny)
        units_config.pack(pady=10)

        activation_config = ActivationConfigWidget(self, layers_opt.LayerActivationAny)
        activation_config.pack(pady=5)

        recurrent_activation_config = ActivationConfigWidget(self, layers_opt.RecurrentActivationAny)
        recurrent_activation_config.pack(pady=5)

        use_bias_config = BoolConfigWidget(self, layers_opt.BoolProp('Use bias', ))
        use_bias_config.pack(pady=5)



if __name__ == '__main__':
    import os

    root = Tk()
    root.title(os.name)

    w = LayerConfigWidget(root,
                          {'name': 'Long Short-Term Memory layer', 'www': r'https://keras.io/layers/recurrent/#lstm'})
    w.pack()

    # l = ActivationConfigWidget(root, layers_opt.LayerActivationAny)
    # l.pack(fill=BOTH)

    root.mainloop()
