import subprocess
import threading

from config_case import TENSOR_BOARD_LOGDIR


class StartTensorBoardParallel(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        cmdline = 'tensorboard --logdir=%s' % TENSOR_BOARD_LOGDIR
        p = subprocess.Popen(cmdline.split(),
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        self.stdout, self.stderr = p.communicate()

# myclass = MyClass()
# myclass.start()
# myclass.join()
# print myclass.stdout
