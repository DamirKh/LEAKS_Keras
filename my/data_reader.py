# SCADA file data reader
import os
import csv
import datetime
#from dateparser import parse
import pickle
import matplotlib.pyplot as plt

import numpy as np

StampWorld = 'Timestamp', 'DATA QUALITY'
Lang = ['ru', 'en']

mon_ru = {'янв': 1,
          'фев': 2,
          'мар': 3,
          'апр': 4,
          'май': 5,
          'июн': 6,
          'июл': 7,
          'авг': 8,
          'сен': 9,
          'окт': 10,
          'ноя': 11,
          'дек': 12
          }

def parse_date(_data_string):
    "S string"
    # data string example '02.мар.2018 23:56:44'
    _date = int(_data_string[0:2])
    _mon = mon_ru[_data_string[3:6]]
    _year = int(_data_string[7:11])
    _h, _m, _s = _data_string[12:].split(':', maxsplit=2)
    _h = int(_h)
    _m = int(_m)
    _s = int(_s)
    dt = datetime.datetime(_year, _mon, _date, _h, _m, _s)
    return dt

def parse_tag(tag_string):
    """_:type """
    # tagname found analog.P0034SB_PT0004_PV.curval
    return tag_string.split('.', maxsplit=2)[1]


def noop(*args, **kwargs):
    pass


# VerboseFunc = noop
VerboseFunc = print


class ScadaDataFile(object):
    """All methods to load data file"""

    def __init__(self):

        self.time_start = datetime.datetime(2027, 9, 27)
        self.time_stop = datetime.datetime(1973, 10, 17)
        self.time_delta = self.time_stop - self.time_start
        self.tags = set()
        self.tags_list = []
        # self._path_to_file = path_to_file


    def import_data_from_csv(self, path_to_file):
        if os.path.exists(path_to_file):
            f = open(path_to_file, newline='', encoding='windows-1251')
            csv_data_iterator = csv.reader(f, dialect='excel-tab')
            # First rollover. Find Tags and calculate time
            for row in csv_data_iterator:
                # VerboseFunc(row)
                if len(row) < 3:
                    continue  # empty string
                if (row[0], row[2]) == StampWorld:
                    # tagname found analog.P0034SB_PT0004_PV.curval
                    tag_name = parse_tag(row[1])
                    self.tags.add(tag_name)
                else:
                    dt = parse_date(row[0])
                    if dt < self.time_start:  # found ealer then start time
                        self.time_start = dt
                        # VerboseFunc("Start ", self.time_start)
                    if dt > self.time_stop:  # found later then stop time
                        self.time_stop = dt
                        # VerboseFunc("Stop  ",self.time_stop)
                    # VerboseFunc(dt)
                    pass

            for tag in self.tags:
                VerboseFunc(tag)
            print('-' * 10, 'tags total:', len(self.tags))
            print("Start from:", self.time_start)
            print("Up to:", self.time_stop)
            self.time_delta = self.time_stop - self.time_start
            print("Seconds:", self.time_delta.total_seconds())

        data_width = len(self.tags)
        data_lenth = int(self.time_delta.total_seconds()) + 1
        mesivo = np.zeros((data_lenth, data_width), dtype=np.float64)
        filled_data = np.zeros((data_lenth, data_width), dtype=np.bool)
        print("Data Size:", mesivo.size)
        tags_list = list(self.tags)
        tags_list.sort()
        # reset csv reader
        f.seek(0)
        current_tag = None

        for row in csv_data_iterator:
            if len(row) < 3: continue  # incomplete or empty string
            if (row[0], row[2]) == StampWorld:
                # tagname found
                current_tag = row[1]  # tag name as string
                assert isinstance(current_tag, type(''))
                tag_position = tags_list.index(parse_tag(current_tag))
            else:
                # data found
                if current_tag is None: continue  # all data before first tag name will be passed away
                try:
                    dt = parse_date(row[0])
                    dt -= self.time_start
                    second_from_start = int(dt.total_seconds())
                    filled_data[second_from_start, tag_position] = True
                    mesivo[second_from_start, tag_position] = float(row[1])
                except IndexError:
                    print("Start time:", self.time_start)
                    print("Stop time:", self.time_stop)
                    print("Row:", row)
                    print(dt)
                    print("seconds=", second_from_start)
                    continue

        # print(mesivo)

        # filling missing data forward
        rolling_forward_data = mesivo[0]
        for current_second in range(data_lenth):
            for current_tag in range(data_width):
                if not filled_data[current_second, current_tag]:
                    mesivo[current_second, current_tag] = rolling_forward_data[current_tag]
            rolling_forward_data = mesivo[current_second]

        # filling missing data backward
        for current_tag in range(data_width):
            for current_second in range(data_lenth):
                filled_flag = filled_data[current_second, current_tag]
                if current_second == 0 and filled_flag: break
                if filled_flag:
                    back_filling_data = mesivo[current_second, current_tag]
                    for count_back in range(current_second, -1,
                                            -1):  # возвращаемся назад и заполняем недостающие данные
                        mesivo[count_back, current_tag] = back_filling_data
                    break
                else:
                    pass

        self.data = mesivo
        self.tags_list = tags_list
        self._not_saved = True

    def save_data(self, filename):
        with open(filename + '.data', mode='wb') as f:
            np.save(f, self.data)
        with open(filename + '.meta', mode='wb') as f:
            pickler = pickle.Pickler(f)
            pickler.dump(self.tags_list)
            pickler.dump(self.tags)
            pickler.dump(self.time_start)
            pickler.dump(self.time_stop)
            pickler.dump(self.time_delta)
            # pickler.dump(self._path_to_file)

        self._not_saved = False

    def load_data(self, filename):
        with open(filename + '.data', mode='rb') as f:
            self.data = np.load(f)
        with open(filename + '.meta', mode='rb') as f:
            unpickler = pickle.Unpickler(f)
            self.tags_list = unpickler.load()
            self.tags = unpickler.load()
            self.time_start = unpickler.load()
            self.time_stop = unpickler.load()
            self.time_delta = unpickler.load()
            # self._path_to_file = unpickler.load()

    def show_me_data(self, tag_names=None, reduced=False):
        x_axe = np.arange(start=0, stop=self.time_delta.total_seconds() + 1, step=1, dtype=np.int32)
        if tag_names is None:
            tag_names = self.tags_list
        for par in range(len(tag_names)):
            i = self.tags_list.index(tag_names[par])
            if reduced:
                plt.plot(x_axe, self.reduced_data[..., i])
            else:
                plt.plot(x_axe, self.data[..., i])
        plt.show()


if __name__ == '__main__':
    data_path = '../../data'
    if os.path.exists(os.path.join(data_path, '2Dx2.meta')):
        s = ScadaDataFile()
        s.load_data(os.path.join(data_path, '2Dx2'))
    else:
        s = ScadaDataFile()
        s.import_data_from_csv(os.path.join(data_path, '2Dx2.txt'))
        s.save_data(os.path.join(data_path, '2Dx2'))
    s.show_me_data()

    print('Ok!')
