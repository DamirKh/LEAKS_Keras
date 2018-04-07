class NotDefinedError(Exception):
    # https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors


class CommonProp(object):
    def __bool__(self):
        """True if property was configured.
        False if property was not configured"""
        return self.configured

    def drop(self):
        """Drops configured state"""
        self.configured = False


class BoolProp(CommonProp):
    def __init__(self, description='Some boolean object', www=r'https://www.google.com/', state=None):
        self.www = www
        self.__doc__ = description
        if state is None:
            self.configured = False
        else:
            self.configured = True
            self.__state = state

    def __call__(self, state=None):
        if state is not None:
            self.configured = True
            self.__state = state
            return self.__state
        else:
            if self.configured:
                return self.__state
            else:
                raise NotDefinedError


class SelectOneProp(CommonProp):
    default_choice = ['first First choice',
                      'second Second choice',
                      'last Last choice']

    def __init__(self, setofchoice=default_choice, description='Make Your choice', www=r'https://www.google.com/',
                 choice=None, ):
        self.__doc__ = description
        self.www = www
        # i=''
        self.__setofchoice = [i.split(' ', 2)[0] for i in setofchoice]
        self.__rawsetofchoice = {i.split(' ', 1)[0]: i.split(' ', 1)[-1] for i in setofchoice}
        # print(self.__rawsetofchoice)
        if choice is None:
            self.configured = False
        else:
            self.configured = True
            self.__choice = choice

    def __call__(self, choice=None):
        """If call with no choice return current choice if configured or raise NotDefinedError if not configured.
        If call with choice configure new choice"""
        if choice is not None:
            # set new choice
            self.configured = True
            if choice not in self.__setofchoice:
                self.__setofchoice.append(choice)
            self.__choice = choice
        elif not self.configured:
            # getting choice but choice is not configured yet
            raise NotDefinedError
        print(self.__choice, self.__rawsetofchoice[self.__choice])
        return self.__choice

    def __iter__(self):
        # https://stackoverflow.com/a/4020011/8124158
        return self.__setofchoice.__iter__()

    def __len__(self):
        return len(self.__setofchoice)

    def __contains__(self, item):
        return item in self.__setofchoice


class IntRangeProp(CommonProp):
    def __init__(self, rng=(0, 100), description=None, www=r'https://www.google.com/', value=None):
        self.www = www
        if description is None:
            self.__doc__ = 'Range of integers %i .. %i' % rng
        else:
            self.__doc__ = description
        if rng[0] < rng[1]:
            self.__min, self.__max = rng
        else:
            raise ValueError
        if value is None:
            self.configured = False
        else:
            self.configured = True
            self.__value = value

    @property
    def min(self):
        """Range minimum"""
        return self.__min

    @property
    def max(self):
        """Range maximum"""
        return self.__max


    def __call__(self, value=None):
        if value is not None:
            # set new value
            value = int(value)
            if self.__min <= value <= self.__max:
                self.configured = True
                self.__value = value
            else:
                raise ValueError
        elif not self.configured:
            # getting choice but choice is not configured yet
            raise NotDefinedError
        print(self.__doc__, '=', self.__value)
        return self.__value


class RealRangeProp(CommonProp):
    def __init__(self, rng=(0., 1.), description=None, www=r'https://www.google.com/', value=None):
        self.www = www
        if description is None:
            self.__doc__ = 'Range of real %i .. %i' % rng
        else:
            self.__doc__ = description
        if rng[0] < rng[1]:
            self.__min, self.__max = rng
        else:
            raise ValueError
        if value is None:
            self.configured = False
        else:
            self.configured = True
            self.__value = value

    def __call__(self, value=None):
        if value is not None:
            # set new value
            value = float(value)
            if self.__min <= value <= self.__max:
                self.configured = True
                self.__value = value
            else:
                raise ValueError
        elif not self.configured:
            # getting choice but choice is not configured yet
            raise NotDefinedError
        return self.__value


# https://keras.io/activations/
avail_act = ['softmax Softmax activation function',
             'elu See documentation',
             'selu Scaled Exponential Linear Unit.',
             'softplus See documentation',
             'softsign See documentation',
             'relu See documentation',
             'tanh See documentation',
             'sigmoid See documentation',
             'hard_sigmoid See documentation',
             'linear See documentation',
             ]

LayerActivationAny = SelectOneProp(avail_act, description='Layer activation function',
                                   www=r'https://keras.io/activations/')

NumOfUnitsAny = IntRangeProp((1, 1000), "Dimensionality of\nthe output space",
                             www=r'https://keras.io/getting-started/sequential-model-guide/#getting-started-with-the-keras-sequential-model',
                             value=3)

# LayersType ={
#     'LSTM': dict(
#         name = 'Long Short-Term Memory layer',
#         www = r'https://keras.io/layers/recurrent/#lstm',
#         arguments = dict(
#             units = None,
#             activations = Activations,
#
#             ),
#     )
# }

if __name__ == '__main__':
    b = BoolProp("Boolean property", )
    print(b)
    if b:
        print("b was configured")
        print('b %s', b())
    else:
        print('b was not configured')

    b(True)
    if b:
        print("b was configured")
        print('b =', b())
    else:
        print('b was not configured')

    b(False)
    if b:
        print("b was configured")
        print('b =', b())
    else:
        print('b was not configured')

    L = SelectOneProp(['a', 'b', 'c', 'd'], "abcd property", )
    if L:
        print('L configured (%s)' % L.__doc__)
        print(L())
    else:
        print('L NOT configured')

    L('b')
    if L:
        print('L configured (%s)' % L.__doc__)
        print(L())
    else:
        print('L NOT configured')

    L('X')
    if L:
        print('L configured (%s)' % L.__doc__)
        print(L())
    else:
        print('L NOT configured')
    [print(x) for x in L]
    print('X' in L)
    print('Y' in L)

    I = IntRangeProp()
    if I:
        print("I configured (%s)" % I.__doc__)
        print(L())
    else:
        print("I not configured")
    I(10)
    if I:
        print("I configured (%s)" % I.__doc__)
        print(I())
    else:
        print("I not configured")

    assert isinstance(I, IntRangeProp)
    assert isinstance(I, BoolProp), "Not a boolean property"
    assert isinstance(I, CommonProp), "Not a Common property"
