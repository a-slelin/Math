import os

import matplotlib.pyplot as plt
import numpy as np
from const import exact, results_dir

# Для каждой схемы свой маркер, чтобы точки не сливались
MARKERS = ['o', 's', '^']


# Сохраняем картинку в папку results и показываем её на экране
def save_and_show(fig, name):
    os.makedirs(results_dir, exist_ok=True)
    fig.savefig(os.path.join(results_dir, name), dpi=150, bbox_inches='tight')
    plt.show()


# Рисуем решение в момент t0: точное (линия), три схемы (точки) и метод Фурье (пунктир)
def plot_solutions(x, t0, schemes, fourier):
    xs = np.linspace(0, 1, 500)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(xs, exact(xs, t0), 'k-', label='Точное решение')

    for (name, u), marker in zip(schemes.items(), MARKERS):
        ax.plot(x, u, marker, markersize=6, fillstyle='none', label=name)

    ax.plot(x, fourier, 'm--', label='Метод Фурье (3 члена)')

    ax.grid(True)
    ax.set_xlabel('x')
    ax.set_ylabel(f'u(x, {t0:g})')
    ax.set_title(f'Решение уравнения теплопроводности в момент t0 = {t0:g}')
    ax.legend()
    save_and_show(fig, 'solutions.png')


# Рисуем ошибки всех способов в момент t0.
# Ось y логарифмическая, потому что ошибки очень разного размера.
def plot_errors(x, t0, schemes, fourier):
    fig, ax = plt.subplots(figsize=(9, 6))

    for (name, u), marker in zip(schemes.items(), MARKERS):
        ax.semilogy(x[1:-1], np.abs(u - exact(x, t0))[1:-1], marker + '-', markersize=5,
                    fillstyle='none', label=name)

    ax.semilogy(x[1:-1], np.abs(fourier - exact(x, t0))[1:-1], 'm--', label='Метод Фурье (3 члена)')

    ax.grid(True, which='both')
    ax.set_xlabel('x')
    ax.set_ylabel('|u_прибл − u_точн|')
    ax.set_title(f'Ошибка во внутренних узлах в момент t0 = {t0:g}')
    ax.legend()
    save_and_show(fig, 'errors.png')


# Рисуем "карту тепла": как решение меняется по x и по времени t
def plot_heatmap(x, t, u):
    fig, ax = plt.subplots(figsize=(9, 6))

    picture = ax.pcolormesh(x, t, u, shading='auto', cmap='inferno')
    fig.colorbar(picture, ax=ax, label='u(x, t)')

    ax.set_xlabel('x')
    ax.set_ylabel('t')
    ax.set_title('Решение u(x, t) (схема Кранка – Никольсона)')
    save_and_show(fig, 'heatmap.png')
