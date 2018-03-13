import tkinter as tk
from tkinter import messagebox
import os.path
from tkinter.filedialog import askopenfilename, asksaveasfilename
import data_reader

DATA = data_reader.ScadaDataFile()
SCADA_EXPORT_FILENAMES = (("SCADA txt data files", "*.txt"),)
DATAFILE_NAMES = (("LEAK Tester data file", "*.data"), )

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.sourceDataWidget = SourceDataWidget(self)
        self.sourceDataWidget.pack(side='left', anchor='n', padx=5, pady=10)

        self.modelWidget = ModelWidget(self)
        self.modelWidget.pack(side='left', anchor='n', padx=5, pady=10)

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit.pack(side="left")

    def say_hi(self):
        print("hi there, everyone!")


class SourceDataWidget(tk.LabelFrame):
    def __init__(self, master=None):
        super().__init__(master, text='Data source')
        # importself.pack()
        self.create_widgets()
        global DATA
        assert isinstance(DATA, data_reader.ScadaDataFile)
        self.data = DATA

    def create_widgets(self):
        self.importDataButton = tk.Button(self)
        self.importDataButton["text"] = "IMPORT\ndata\n..."
        self.importDataButton["command"] = self.DoImportData
        self.importDataButton.pack(side="top", fill='both')

        self.SaveDataButton = tk.Button(self)
        self.SaveDataButton["text"] = "SAVE\nimported data\n..."
        self.SaveDataButton["command"] = self.DoSaveData
        self.SaveDataButton.pack(side="top", fill='both')

        self.LoaDataButton = tk.Button(self)
        self.LoaDataButton["text"] = "LOAD\nsaved data\n..."
        self.LoaDataButton["command"] = self.DoLoadData
        self.LoaDataButton.pack(side="top", fill='both')

        self.ShowDataButton = tk.Button(self)
        self.ShowDataButton["text"] = "Show data"
        self.ShowDataButton["command"] = self.DoShowData
        self.ShowDataButton.pack(side="top", fill='both')

    def DoSaveData(self):
        print("Lets save data!")
        filename = asksaveasfilename(title='Save data to file',
                                     filetypes = DATAFILE_NAMES)
        if filename:
            f = os.path.splitext(filename)[0]
            try:
                self.data.save_data(f)
            except FileExistsError or IOError:
                messagebox.showerror("Save data", "Failed to save file \n'%s'" % filename)
                return


    def DoImportData(self):
        print("Lets import data!")
        filename = askopenfilename(title="Import data from file:",
                                   filetypes = SCADA_EXPORT_FILENAMES)
        if filename:
            try:
                #self.settings["template"].set(filename)
                self.data.import_data_from_csv(filename)
            except FileNotFoundError or IOError:
                messagebox.showerror("Open Source File", "Failed to read file \n'%s'" % filename)
                return


    def DoLoadData(self):
        print("Lets load data!")

    def DoShowData(self):
        print("Lets load data!")
        self.data.show_me_data()


class ModelWidget(tk.LabelFrame):
    def __init__(self, master=None):
        super().__init__(master, text='Model')
        # importself.pack()
        self.create_widgets()

    def create_widgets(self):
        self.importDataButton = tk.Button(self)
        self.importDataButton["text"] = "Create model\nfrom data"
        self.importDataButton["command"] = self.DoCreateModel
        self.importDataButton.pack(side="top", fill='both')

        self.SaveDataButton = tk.Button(self)
        self.SaveDataButton["text"] = "Train model\nwith loaded data"
        self.SaveDataButton["command"] = self.DoTrainModel
        self.SaveDataButton.pack(side="top", fill='both')

        self.SaveDataButton = tk.Button(self)
        self.SaveDataButton["text"] = "Save model\nfor future use"
        self.SaveDataButton["command"] = self.DoSaveModel
        self.SaveDataButton.pack(side="top", fill='both')

        self.SaveDataButton = tk.Button(self)
        self.SaveDataButton["text"] = "Load model\n---"
        self.SaveDataButton["command"] = self.DoLoadModel
        self.SaveDataButton.pack(side="top", fill='both')

    def DoCreateModel(self):
        print("Lets create model")

    def DoTrainModel(self):
        print("Lets train model")

    def DoSaveModel(self):
        print("Lets save model")

    def DoLoadModel(self):
        print("Lets load model")


root = tk.Tk()
root.title("Leak tester")
app = Application(master=root)
app.mainloop()
