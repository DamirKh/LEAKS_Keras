from tkinter import *


# http://effbot.org/tkinterbook/checkbutton.htm

class TagSelectorWidget(LabelFrame):
    # todo: add selected_tags as parametr
    def __init__(self, master=None, text='Check tags:', tagslist=['Tag №1', 'Super Tag №2'], selected_tags=[]):
        super().__init__(master, text=text)
        self.tagslist = tagslist
        self.count = IntVar()
        self.selected_tags = selected_tags
        self.create_widgets()

    def create_widgets(self):
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
            if tag in self.selected_tags:
                c.select()
            else:
                c.deselect()
        self.counter = Label(self, textvariable=self.count)
        self.counter.pack(anchor='e', padx=5, pady=5)
        self.count.set(len(self.selected_tags))


    def cb(self):
        selected_tags = []
        for x in self.vars:
            if x.get() == '-':
                continue
            selected_tags.append(x.get())
        self.selected_tags = selected_tags
        self.count.set(len(self.selected_tags))
