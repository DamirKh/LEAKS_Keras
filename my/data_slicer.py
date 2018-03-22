import logging

import numpy as np


def slicer(dataSource, tags):
    '''
    :type dataSource: ScadaDataFile
    :param dataSource: ScadaDataFile object
    :param tags: list
    :return: np.
    '''
    # данные переносятся из исходного массива dataSource.data
    # в новый массив, исключая ненужные теги
    # ось 0 - временнАя ось
    # ось 1 - ось данных тегов
    # форма массива, должна соответствовать исходному массиву.
    # нулевая колонка - не содержит данных. она для создания массива нужной формы
    data = np.zeros((dataSource.data.shape[0], 1), dtype=np.float64)
    for tag in dataSource.tags_list:
        if tag in tags:
            logging.debug("Found tag %s in input data" % tag)
            # срез вдоль оси данных
            tag_data = dataSource.data[..., dataSource.tags_list.index(tag)]
            data = np.c_[data, tag_data]
            pass
        else:
            logging.debug("Skip tag %s in input data" % tag)
    # удаляем нулевую колонку: она не содержит данных
    data = np.delete(data, 0, 1)
    return data
