import logging
import os.path
import tkinter as tk
import tkinter.scrolledtext as ScrolledText
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

import data_reader
import model
from loggerwidget import WidgetLogger
from parallel_launcher import StartTensorBoardParallel

# Logging configuration
logging.basicConfig(filename='test.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# TODO https://stackoverflow.com/questions/616645/how-do-i-duplicate-sys-stdout-to-a-log-file-in-python/2216517#2216517

SCADA_EXPORT_FILENAMES = (("SCADA txt data files", "*.txt"),)
DATAFILE_NAMES = (("LEAK Tester meta file", "*.meta"),)
MODELFILE_NAMES = (("LEAK Tester model file", "*.h5"),)

DATA = data_reader.ScadaDataFile()
MODEL = model.LeakTesterModel()


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.sourceDataWidget = SourceDataWidget(self)
        self.sourceDataWidget.grid(row=0, column=0, sticky='n', padx=5, pady=10)

        self.modelWidget = ModelWidget(self)
        self.modelWidget.grid(row=0, column=1, sticky='n', padx=5, pady=10)

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit.grid(row=0, column=2, sticky='ne', padx=5, pady=10, )

        # Add text widget to display logging info
        self.st = ScrolledText.ScrolledText(self, state='disabled', height=10)
        self.st.configure(font='TkFixedFont')
        self.st.grid(row=1, column=0, columnspan=3, sticky='n', )
        # Create textLogger
        self.text_handler = WidgetLogger(self.st)
        # Add the handler to logger
        logging.getLogger().addHandler(self.text_handler)

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
        self.importDataButton["text"] = "IMPORT data"
        self.importDataButton["command"] = self.DoImportData
        self.importDataButton.pack(side="top", fill='both')

        self.SaveDataButton = tk.Button(self)
        self.SaveDataButton["text"] = "SAVE imported data"
        self.SaveDataButton["command"] = self.DoSaveData
        self.SaveDataButton.pack(side="top", fill='both')

        self.LoaDataButton = tk.Button(self)
        self.LoaDataButton["text"] = "LOAD saved data"
        self.LoaDataButton["command"] = self.DoLoadData
        self.LoaDataButton.pack(side="top", fill='both')

        self.ShowDataButton = tk.Button(self)
        self.ShowDataButton["text"] = "Show data"
        self.ShowDataButton["command"] = self.DoShowData
        self.ShowDataButton.pack(side="top", fill='both')

    def DoSaveData(self):
        logging.debug("Lets save data!")
        filename = asksaveasfilename(title='Save data to file',
                                     filetypes=DATAFILE_NAMES)
        if filename:
            f = os.path.splitext(filename)[0]
            try:
                self.data.save_data(f)
            except FileExistsError or IOError:
                logging.error("Failed to save file '%s'" % filename)
                messagebox.showerror("Save data", "Failed to save file \n'%s'" % filename)
                return

    def DoImportData(self):
        logging.debug("Lets import data!")
        filename = askopenfilename(title="Import data from file:",
                                   filetypes=SCADA_EXPORT_FILENAMES)
        if filename:
            try:
                # self.settings["template"].set(filename)
                self.data.import_data_from_csv(filename)
            except FileNotFoundError or IOError:
                logging.error("Failed to read file '%s'" % filename)
                messagebox.showerror("Open Source File", "Failed to read file \n'%s'" % filename)
                return

    def DoLoadData(self):
        logging.debug("Lets load data!")
        filename = askopenfilename(title='Load data from file', filetypes=DATAFILE_NAMES)
        if filename:
            f = os.path.splitext(filename)[0]
            try:
                self.data.load_data(f)
            except FileNotFoundError or IOError:
                logging.error("Failed to load file '%s'" % filename)
                messagebox.showerror("Load data", "Failed to load file \n'%s'" % filename)
                return

    def DoShowData(self):
        logging.debug("Lets load data!")
        self.data.show_me_data()


class ModelWidget(tk.LabelFrame):
    def __init__(self, master=None):
        super().__init__(master, text='Model')
        self.create_widgets()

    def create_widgets(self):
        self.importDataButton = tk.Button(self)
        self.importDataButton["text"] = "Configure model"
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

        self.TensorBoardButton = tk.Button(self)
        self.TensorBoardButton["text"] = "Launch TensorBoard "
        self.TensorBoardButton["command"] = self.DoLaunchTensorBoard
        self.TensorBoardButton.pack(side="top", fill='both')

    def DoCreateModel(self):
        logging.debug("Let's configure model")
        MODEL.gui_model_configure(self.master, tag_list=DATA.tags_list)

    def DoTrainModel(self):
        logging.debug("Let's train model")
        MODEL.trainGUI(self.master)
        # MODEL.analyze_and_train(DATA)

    def DoSaveModel(self):
        logging.debug("Let's save model")
        filename = asksaveasfilename(title='Save model to file',
                                     filetypes=MODELFILE_NAMES)
        if filename:
            try:
                MODEL.savemodel(filename)
            except FileExistsError or IOError:
                logging.error("Failed to save file '%s'" % filename)
                messagebox.showerror("Save model", "Failed to save file \n'%s'" % filename)
                return

    def DoLoadModel(self):
        logging.debug("Let's load model")
        filename = askopenfilename(title='Load model from file',
                                   filetypes=MODELFILE_NAMES)
        if filename:
            try:
                MODEL.loadmodel(filename)
            except FileExistsError or IOError:
                logging.error("Failed to load file '%s'" % filename)
                messagebox.showerror("Save model", "Failed to save file \n'%s'" % filename)
                return

    def DoLaunchTensorBoard(self):
        """Launch TensorBoard as parallel process"""
        logging.info("Let's launch TensorBoard!")
        self.TensorBoardProccess = StartTensorBoardParallel()
        self.TensorBoardProccess.start()


root = tk.Tk()
root.title("Leak tester")
app = Application(master=root)
app.mainloop()
