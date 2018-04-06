from tkinter import *

import layers_opt
# my modules next
from label_link import LabelLink


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
        w.grid(row=0, column=1, padx=5)

        b = Button(self, text='DROP', command=self.drop_config)
        b.grid(row=0, column=2, padx=3)

        LabelLink(self, www=ac.www).grid(row=0, column=3)
        Label(self, text=ac.__doc__).grid(row=0, column=0)

        self.var = variable
        variable.trace_variable('w', self.callback)

    def drop_config(self):
        self.ac.drop()
        self.var.set('')

    def callback(self, *args):
        if len(self.var.get()):
            self.ac(self.var.get())


class LayerConfigWidget(Frame):
    def __init__(self, master=None, layer_conf=None):
        super().__init__(master)
        self.layer_conf = layer_conf
        self.create_widgets()

    def create_widgets(self):
        lc = self.layer_conf  # Layer Config
        Label(self, text=lc['name']).pack()
        LabelLink(self, www=lc['www']).pack()


if __name__ == '__main__':
    import os

    root = Tk()
    root.title(os.name)

    # w = LayerConfigWidget(root, {'name':'Long Short-Term Memory layer', 'www':r'https://keras.io/layers/recurrent/#lstm'})
    # w.pack()

    l = ActivationConfigWidget(root, layers_opt.LayerActivationAny)
    l.pack(fill=BOTH)

    root.mainloop()
