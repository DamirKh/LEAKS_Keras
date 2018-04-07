import webbrowser
from tkinter import *


class LabelLink(Frame):
    """Label packed in Frame for http links"""

    def __init__(self, master, www=r'https://www.google.com', wwwidth=50):
        """www: r'http://google.com'"""
        super().__init__(master)
        # self.www = shorten(www, wwwidth, placeholder="..")
        self.www = www[:wwwidth] + (www[wwwidth:] and '..')
        self._www = www
        self.create_widgets()

    def create_widgets(self):
        lbl = Label(self, text=self.www, fg="blue", cursor="hand2")
        lbl.pack(side="top", fill='both')
        lbl.bind("<Button-1>", self.cb)
        pass

    def cb(self, event):
        webbrowser.open_new(self._www)


if __name__ == '__main__':
    root = Tk()
    root.title("Label link")

    w = LabelLink(root, www=r"http://www.google.com")
    w.pack()

    root.mainloop()
