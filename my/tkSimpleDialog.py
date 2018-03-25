from tkinter import *


# http://effbot.org/tkinterbook/tkinter-dialog-windows.htm

class Dialog(Toplevel):

    def __init__(self, parent, title=None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1  # override

    def apply(self):

        pass  # override


class ModelConfigDialog(Dialog):
    def __init__(self, parent, model_config, title=None):
        self.model_config = model_config
        super().__init__(parent, title=title)


class ModelTrainDialog(Dialog):
    def __init__(self, parent, model, datasource, title='Train dialog'):
        self.model_config = model.model_config
        self.model = model
        self.datasource = datasource
        super().__init__(parent, title=title)

    def rem_buttonbox(self):
        # Train and exit buttons

        self.status_var = StringVar()
        self.status_var.set("   Start training   ")

        box = Frame(self)

        w = Checkbutton(box,
                        textvariable=self.status_var,
                        variable=self.flag_var,
                        indicatoron=False,
                        width=len(self.status_var.get()),
                        command=self.start_stop)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Close", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        box.pack()

    def rem_start_stop(self):
        self.apply()
        if self.flag_var.get() == 1:
            #                   "   Start training   "
            self.status_var.set(" Train in progress  ")
        else:
            self.status_var.set(" Continue training  ")
