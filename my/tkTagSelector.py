from tkinter import *


# http://effbot.org/tkinterbook/checkbutton.htm

class TagSelectorWidget(LabelFrame):
    # todo: add selected_tags as parametr
    def __init__(self, master=None, text='Check tags:', tagslist=['Tag №1', 'Super Tag №2'], checked=True):
        super().__init__(master, text=text)
        self.tagslist = tagslist
        self.selected_tags = []
        self.create_widgets(checked)

    def create_widgets(self, checked):
        self.vars = []
        for tag in self.tagslist:
            self.vars.append(StringVar())
            c = Checkbutton(
                self,
                text=tag,
                variable=self.vars[-1],
                onvalue=tag, offvalue="-",
                command=self.cb
            )
            c.pack(anchor='w', padx=5, pady=0)
            if checked:
                c.select()
            else:
                c.deselect()
            self.cb()


    def cb(self):
        self.selected_tags = []
        for x in self.vars:
            if x.get() == '-':
                continue
            self.selected_tags.append(x.get())
