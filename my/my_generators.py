def generate_from_dataSource(data, start_, stop_):
    """

    :type data: ScadaDataFile
    """
    for i in range(start_, stop_):
        x = data.data[]
    for data_line in data.data:
        # create Numpy arrays of input data
        # and labels, from each line in the file
        x, y = process_line(line)
        yield (x, y)
