from my_lstm_config import MyLstmConfigDialog
from topWindow import topWindow


class MyTopWindow(topWindow):
    def let_lstm_config_dialog(self, event):
        MyLstmConfigDialog(self).ShowModal()
