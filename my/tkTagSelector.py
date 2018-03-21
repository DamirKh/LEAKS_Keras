from tkinter import *


# http://effbot.org/tkinterbook/checkbutton.htm

class TagSelectorWidget(LabelFrame):
    def __init__(self, master=None, text='Check tags:', tags_list=['Tag №1', 'Super Tag №2']):
        super().__init__(master, text=text)
        self.tags_list = tags_list
        self.create_widgets()

    def create_widgets(self):
        self.vars = []
        for tag in self.tags_list:
            self.vars.append(StringVar())
            c = Checkbutton(
                self.master, text=tag,
                variable=self.vars[-1],
                onvalue=tag, offvalue="-",
                command=self.cb
            )
            c.pack()

    def cb(self):
        for x in self.vars:
            if x.get() == '-':
                continue
            print(x)
