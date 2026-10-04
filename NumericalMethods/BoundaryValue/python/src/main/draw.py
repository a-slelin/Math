import os

import matplotlib.pyplot as plt
import numpy as np
from const import a, b, exact, results_dir

# Для каждого метода свой маркер, чтобы точки разных методов не сливались
MARKERS = ['o', 's', '^', 'x']


# Сохраняем картинку в папку results и показываем её на экране
def save_and_show(fig, name):
    os.makedirs(results_dir, exist_ok=True)
    fig.savefig(os.path.join(results_dir, name), dpi=150, bbox_inches='tight')
    plt.show()


# Рисуем точное решение (линия) и решения всеми четырьмя методами (точки)
def plot_solutions(x, solutions):
    # Густая сетка, чтобы точное решение выглядело гладкой линией
    t = np.linspace(a, b, 500)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(t, exact(t), 'k-', label='Точное решение')

    for (name, y), marker in zip(solutions.items(), MARKERS):
        ax.plot(x, y, marker, markersize=6, fillstyle='none', label=name)

    ax.grid(True)
    ax.set_xlabel('x')
    ax.set_ylabel('y(x)')
    ax.set_title("y'' + 2y' − 3y = eˣ,   y(0) = 0,   y'(1) = 1,   n = 20")
    ax.legend()
    save_and_show(fig, 'solutions.png')


# Рисуем ошибку |y_числ − y_точн| в каждом узле
def plot_errors(x, solutions):
    fig, ax = plt.subplots(figsize=(9, 6))

    for (name, y), marker in zip(solutions.items(), MARKERS):
        ax.plot(x, np.abs(y - exact(x)), marker + '-', markersize=5, fillstyle='none', label=name)

    ax.grid(True)
    ax.set_xlabel('x')
    ax.set_ylabel('|y_числ(x) − y_точн(x)|')
    ax.set_title('Ошибка в узлах сетки (n = 20)')
    ax.legend()
    save_and_show(fig, 'errors.png')


# Рисуем, как уменьшается ошибка, если брать всё больше узлов.
# Оси логарифмические: тогда зависимость "ошибка ~ h" выглядит прямой линией.
def plot_convergence(ns, errors):
    h = 1 / np.array(ns)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.loglog(h, errors, 'o-', label='Максимальная ошибка')

    # Для сравнения рисуем прямую "ошибка = C * h" (порядок 1)
    ax.loglog(h, errors[0] * h / h[0], 'k--', label='~ h (первый порядок)')

    ax.grid(True, which='both')
    ax.set_xlabel('Шаг сетки h')
    ax.set_ylabel('max |y_числ − y_точн|')
    ax.set_title('Сходимость разностной схемы при уменьшении h')
    ax.legend()
    save_and_show(fig, 'convergence.png')
