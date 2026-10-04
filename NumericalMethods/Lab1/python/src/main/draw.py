import os

import matplotlib.pyplot as plt
import numpy as np
from const import a, b, exact, results_dir


# Сохраняем картинку в папку results и показываем её на экране
def save_and_show(fig, name):
    os.makedirs(results_dir, exist_ok=True)
    fig.savefig(os.path.join(results_dir, name), dpi=150, bbox_inches='tight')
    plt.show()


# Рисуем два графика рядом:
# слева — метод последовательных приближений, справа — метод СЛАУ.
# На каждом пунктиром показано точное решение, чтобы было с чем сравнить.
def plot_solutions(grid, phi_iter, phi_slae):
    # Густая сетка, чтобы точное решение выглядело гладкой линией
    t = np.linspace(a, b, 500)

    fig, (left, right) = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    # Левый график: последовательные приближения
    left.plot(t, exact(t), 'k--', label='Точное решение')
    left.plot(grid, phi_iter, 'o', color='tab:blue', markersize=3, label='Последовательные приближения')
    left.set_title('Метод последовательных приближений')

    # Правый график: СЛАУ
    right.plot(t, exact(t), 'k--', label='Точное решение')
    right.plot(grid, phi_slae, 's', color='tab:orange', markersize=3, label='СЛАУ (трапеции)')
    right.set_title('Метод сведения к СЛАУ')

    # Общие настройки для обоих графиков
    for ax in (left, right):
        ax.grid(True)
        ax.set_xlabel('t')
        ax.legend()
    left.set_ylabel('φ(t)')

    fig.suptitle('Решение уравнения φ(t) = ∫ (5/π)·sin(5t+5s)·φ(s) ds + 1.5·sin(5t)')
    save_and_show(fig, 'solutions.png')


# Рисуем ошибки: насколько каждый численный метод отличается от точного решения
def plot_errors(grid, phi_iter, phi_slae):
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(grid, np.abs(phi_iter - exact(grid)), color='tab:blue', label='Последовательные приближения')
    ax.plot(grid, np.abs(phi_slae - exact(grid)), '--', color='tab:orange', label='СЛАУ')

    ax.grid(True)
    ax.set_xlabel('t')
    ax.set_ylabel('|φ_числ(t) − φ_точн(t)|')
    ax.set_title('Ошибка численных методов')
    ax.legend()
    save_and_show(fig, 'errors.png')


# Рисуем, как быстро сходятся последовательные приближения:
# по оси y — насколько изменилось решение на очередном шаге.
# Ось y логарифмическая, чтобы маленькие числа тоже было видно.
def plot_convergence(differences):
    fig, ax = plt.subplots(figsize=(8, 5))

    steps = range(1, len(differences) + 1)
    ax.semilogy(steps, differences, 'o-', color='tab:blue')

    ax.grid(True)
    ax.set_xlabel('Номер шага k')
    ax.set_ylabel('max |φ_k − φ_(k−1)|')
    ax.set_title('Сходимость метода последовательных приближений')
    save_and_show(fig, 'convergence.png')
