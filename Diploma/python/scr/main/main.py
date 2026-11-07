"""
Рисунок D-разбиения для характеристического уравнения (4):

    λ + 1 = a·λ·e^(-λT) + b·λ·e^(-λH).

На рисунке: ветви D-кривой (9) и область 𝔻₀ (все корни в левой полуплоскости), залитая зелёным.
Область 𝔻₀ находится автоматически: в каждой точке сетки (a, b) считаем число корней N с Re λ > 0
(см. roots.count_unstable_roots) и закрашиваем точки, где N = 0.

Запуск: python main.py. Картинка сохраняется в Diploma/images/D-partition.png.
Счёт занимает около минуты: почти всё время уходит на точки вблизи границы 𝔻₀.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from draw import STABLE_COLOR, STABLE_EDGE, CURVE_COLOR, roots_on_grid, curve_branches, setup_axes
from roots import d_curve

# Параметры уравнения
T = 5  # Запаздывание
H = 1  # Второе запаздывание

# Окно на плоскости (a, b)
A_LIM = (-1.5, 1.5)
B_LIM = (-1.5, 1.5)

# Число узлов сетки по каждой оси для подсчёта корней (время счёта растёт как GRID_SIZE²)
GRID_SIZE = 301

# D-кривая: ω ∈ (0, W_MAX] с шагом W_STEP (как и раньше — 10⁶ точек)
W_MAX = 100
W_STEP = 10 ** -4

# Папка для картинок: этот файл лежит в Diploma/python/scr/main — поднимаемся на 3 уровня вверх
IMAGES_DIR = Path(__file__).resolve().parents[3] / 'images'


if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(9, 9))

    # 1) Число корней с Re λ > 0 в каждой точке сетки и заливка области 𝔻₀ = {N = 0}.
    #    contourf по маске (уровень 0.5) даёт гладкую границу заливки вместо «ступенек» из пикселей.
    #    Контур отдельно не обводим: границу 𝔻₀ и так рисуют ветви D-кривой поверх заливки.
    a, b, roots = roots_on_grid(T, H, A_LIM, B_LIM, GRID_SIZE)
    stable = (roots == 0).astype(float)
    ax.contourf(a, b, stable, levels=[0.5, 1.5], colors=[STABLE_COLOR], zorder=2)

    # 2) Ветви D-кривой (9). Чем больше ω, тем тоньше и прозрачнее линия:
    #    ветви с большими ω сгущаются, и иначе слились бы в сплошное синее пятно.
    for w, a_w, b_w in curve_branches(d_curve, T, H, W_MAX, W_STEP):
        fade = 1 / (1 + w[0] / 15)  # от 1 (первые ветви) до ≈ 0.13 (ω ≈ 100)
        ax.plot(a_w, b_w, color=CURVE_COLOR, lw=0.4 + 1.1 * fade, alpha=0.35 + 0.65 * fade, zorder=4)

    setup_axes(ax, A_LIM, B_LIM)

    # 3) Легенда (заливка и линии сами в неё не попадают — собираем вручную)
    legend = [
        Patch(facecolor=STABLE_COLOR, edgecolor=STABLE_EDGE, label=r'$\mathbb{D}_0$'),
        Line2D([], [], color=CURVE_COLOR, lw=1.5, label='D-кривая (9)'),
    ]
    ax.legend(handles=legend, loc='upper left', fontsize=16, framealpha=0.95)

    fig.tight_layout()
    IMAGES_DIR.mkdir(exist_ok=True)
    fig.savefig(IMAGES_DIR / 'D-partition.png', dpi=200)
    print(f'Сохранено: {IMAGES_DIR / "D-partition.png"}')
    print(f'Точек сетки в 𝔻₀: {int(stable.sum())} из {stable.size}')
    plt.show()
