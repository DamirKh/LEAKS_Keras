import numpy as np

# накидываем тысячу точек от -3 до 3
x = np.linspace(-3, 3, 1000).reshape(-1, 1)


# линейная функция
def f(x):
    return 2 * x + 5


f = np.vectorize(f)
line_func = f(x)


# синусоида
def f(x):
    return 2 * np.sin(x) + 5


f = np.vectorize(f)
sin_func = f(x)


# сложная функция
def f(x):
    return x * np.sin(x * 2 * np.pi) if x < 0 else -x * np.sin(x * np.pi) + np.exp(x / 2) - np.exp(0)


f = np.vectorize(f)
comp_func = f(x)
