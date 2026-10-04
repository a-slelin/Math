import os

import matplotlib.pyplot as plt
import numpy as np
from const import semi_x, semi_y, results_dir
from methods import ON_BOUNDARY, NEAR, INTERIOR


# Сохраняем картинку в папку results и показываем её на экране
def save_and_show(fig, name):
    os.makedirs(results_dir, exist_ok=True)
    fig.savefig(os.path.join(results_dir, name), dpi=150, bbox_inches='tight')
    plt.show()


# Рисуем границу области — эллипс x²/16 + y²/25 = 1
def draw_ellipse(ax, **style):
    angle = np.linspace(0, 2 * np.pi, 400)
    ax.plot(semi_x * np.cos(angle), semi_y * np.sin(angle), **style)


# Рисуем сетку и типы узлов (как рисунок в методичке): слева вся область, справа увеличенный уголок
def plot_grid(x, y, types):
    X, Y = np.meshgrid(x, y)

    fig, (whole, zoom) = plt.subplots(1, 2, figsize=(13, 7))

    for ax in (whole, zoom):
        draw_ellipse(ax, color='k', linewidth=1.5, label='Граница Г')
        ax.plot(X[types == INTERIOR], Y[types == INTERIOR], '.', color='tab:blue', markersize=2,
                label='Внутренние узлы')
        ax.plot(X[types == NEAR], Y[types == NEAR], 'o', color='tab:red', markersize=3,
                label='Приграничные узлы')
        ax.plot(X[types == ON_BOUNDARY], Y[types == ON_BOUNDARY], 's', color='tab:green', markersize=4,
                label='Узлы на границе')
        ax.set_aspect('equal')
        ax.set_xlabel('x')
        ax.set_ylabel('y')

    whole.set_title('Сетка в эллипсе x²/16 + y²/25 = 1')
    whole.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=8)

    # Увеличенный уголок: правый верхний край эллипса, видна каждая клетка сетки
    zoom.set_xlim(2.0, 3.6)
    zoom.set_ylim(2.6, 4.2)
    zoom.set_xticks(np.arange(2.0, 3.61, 0.1), minor=True)
    zoom.set_yticks(np.arange(2.6, 4.21, 0.1), minor=True)
    zoom.grid(True, which='both', alpha=0.4)
    zoom.set_title('Увеличенный фрагмент (каждая клетка — шаг h = 0.1)')

    save_and_show(fig, 'grid.png')


# Рисуем решение цветной картой с линиями уровня
def plot_solution_map(x, y, u):
    fig, ax = plt.subplots(figsize=(7, 8))

    picture = ax.contourf(x, y, u, levels=30, cmap='viridis')
    lines = ax.contour(x, y, u, levels=12, colors='white', linewidths=0.6)
    ax.clabel(lines, fontsize=7, fmt='%.1f')
    fig.colorbar(picture, ax=ax, label='u(x, y)')
    draw_ellipse(ax, color='k', linewidth=1.5)

    ax.set_aspect('equal')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Решение задачи Дирихле: Δu = 0,  u|Г = |x|·|y|')
    save_and_show(fig, 'solution.png')


# Рисуем решение как поверхность в 3D
def plot_solution_surface(x, y, u):
    X, Y = np.meshgrid(x, y)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(projection='3d')
    ax.plot_surface(X, Y, np.ma.masked_invalid(u), cmap='viridis', linewidth=0, antialiased=True)

    # Значения на границе — чёрной линией, чтобы было видно, что поверхность к ним "прилипает"
    angle = np.linspace(0, 2 * np.pi, 400)
    bx, by = semi_x * np.cos(angle), semi_y * np.sin(angle)
    ax.plot(bx, by, np.abs(bx) * np.abs(by), 'k-', linewidth=1.5, label='u|Г = |x|·|y|')

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('u')
    ax.set_title('Поверхность решения u(x, y)')
    ax.legend()
    save_and_show(fig, 'surface.png')


# Рисуем, как быстро сходятся итерации: Зейдель против верхней релаксации
def plot_iterations(histories):
    fig, ax = plt.subplots(figsize=(9, 6))

    for name, history in histories.items():
        ax.semilogy(range(1, len(history) + 1), history, label=f'{name} ({len(history)} итераций)')

    ax.grid(True, which='both')
    ax.set_xlabel('Номер итерации')
    ax.set_ylabel('Наибольшее изменение за итерацию')
    ax.set_title('Сходимость итерационного метода (сетка h = 0.2)')
    ax.legend()
    save_and_show(fig, 'iterations.png')


# Рисуем, как уменьшается ошибка на тестовой задаче с известным решением при уменьшении h.
# Оси логарифмические: зависимость "ошибка ~ h²" выглядит прямой.
def plot_test_convergence(steps, errors):
    steps = np.array(steps)
    errors = np.array(errors)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.loglog(steps, errors, 'o-', label='Ошибка на тесте u = x² − y²')
    ax.loglog(steps, errors[0] * (steps / steps[0]) ** 2, 'k--', label='~ h² (второй порядок)')

    ax.grid(True, which='both')
    ax.set_xlabel('Шаг сетки h')
    ax.set_ylabel('max |u_прибл − u_точн|')
    ax.set_title('Проверка метода на гармонической функции')
    ax.legend()
    save_and_show(fig, 'test_convergence.png')
