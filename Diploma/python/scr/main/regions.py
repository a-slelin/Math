"""
Подробное D-разбиение для уравнения (4):

    λ + 1 = a·λ·e^(-λT) + b·λ·e^(-λH).

В отличие от main.py здесь каждая область 𝔻_N раскрашена по числу N корней с Re λ > 0:
  * 𝔻₀ — зелёная (устойчивость);
  * 𝔻₂, 𝔻₄, ... — тёплые цвета, темнеют с ростом N;
  * 𝔻_∞ — серая со штриховкой: разностный оператор D(λ) = 1 - a·e^(-λT) - b·e^(-λH) неустойчив,
    и корней в правой полуплоскости бесконечно много.

На границах нарисованы штрихи: они смотрят в ту сторону, при переходе в которую корни уходят
в правую полуплоскость (через D-кривую — пара ±iω, N увеличивается на 2; через красную границу — N становится ∞).

Рисунок из двух частей: слева — всё окно, справа — увеличенный угол области 𝔻₀,
где видны узкие полосы 𝔻₂, 𝔻₄, ... между ветвями D-кривой.

Запуск: python regions.py. Картинка сохраняется в Diploma/images/D-regions.png (счёт — несколько минут).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from scipy import ndimage

from draw import (STABLE_COLOR, CURVE_COLOR, LIMIT_COLOR, roots_on_grid, curve_branches, d_curve_side,
                  limit_curve_side, ticked, z_lines, pieces, setup_axes)
from roots import d_curve, limit_curve, difference_operator_stable, INFINITE, UNRESOLVED

# Параметры уравнения
T = 5  # Запаздывание
H = 1  # Второе запаздывание

# Окна: всё D-разбиение и увеличенный фрагмент (верхний левый угол 𝔻₀)
FULL_A, FULL_B = (-1.5, 1.5), (-1.5, 1.5)
ZOOM_A, ZOOM_B = (-0.42, 0.02), (0.84, 1.28)

# Число узлов сетки по каждой оси (время счёта растёт как квадрат)
GRID_FULL = 301
GRID_ZOOM = 301

# D-кривая: ω ∈ (0, W_MAX] с шагом W_STEP; штрихи рисуем только на ветвях с ω ≤ W_TICKS —
# дальше ветви сливаются, и штрихи превратились бы в кашу
W_MAX = 100
W_STEP = 10 ** -4
W_TICKS = 16

# Цвета: 𝔻₂, 𝔻₄, ..., 𝔻₁₂ и далее (при N ≥ 12 цвет больше не меняется), 𝔻_∞
UNSTABLE_COLORS = ('#fde4b8', '#fcc98a', '#f9a965', '#f0834b', '#dc5c3b', '#b83a33')
INFINITE_COLOR = '#d9d9d9'

IMAGES_DIR = Path(__file__).resolve().parents[3] / 'images'


def color_index(roots):
    """
    Номер цвета для каждой точки: 0 — 𝔻₀, 1..6 — 𝔻₂..𝔻₁₂₊, 7 — 𝔻_∞.
    Точки, слишком близкие к красной границе (UNRESOLVED), красим как 𝔻_∞ — они фактически лежат на ней.
    """
    idx = np.minimum(roots // 2, len(UNSTABLE_COLORS))
    idx[(roots == INFINITE) | (roots == UNRESOLVED)] = len(UNSTABLE_COLORS) + 1
    return idx


def colormap():
    """Дискретная палитра: каждому номеру из color_index — свой цвет."""
    colors = [STABLE_COLOR, *UNSTABLE_COLORS, INFINITE_COLOR]
    return ListedColormap(colors), BoundaryNorm(np.arange(-0.5, len(colors)), len(colors))


def draw_regions(ax, a, b, roots):
    """Заливка областей по числу корней и серая штриховка 𝔻_∞."""
    cmap, norm = colormap()
    extent = (a[0], a[-1], b[0], b[-1])
    # origin='lower' — строка 0 массива внизу (b растёт вверх); extent — реальные координаты окна
    ax.imshow(color_index(roots), origin='lower', extent=extent, cmap=cmap, norm=norm,
              interpolation='nearest', zorder=1)
    # Штриховка поверх 𝔻_∞: contourf по маске «N = ∞» без заливки, только с hatch
    infinite = ((roots == INFINITE) | (roots == UNRESOLVED)).astype(float)
    ax.contourf(a, b, infinite, levels=[0.5, 1.5], colors='none', hatches=['//'], zorder=2)


def draw_line(ax, a_w, b_w, important, color, lw, alpha, effects):
    """
    Рисуем линию по кускам: там, где important = True, — ярко и со штрихами (effects),
    в остальных местах — тонко и бледно, без штрихов.
    """
    for p in pieces(important):
        ax.plot(a_w[p], b_w[p], color=color, lw=lw, alpha=alpha, path_effects=effects, zorder=5)
    for p in pieces(~important):
        ax.plot(a_w[p], b_w[p], color=color, lw=0.5, alpha=0.25, zorder=4)


def near_stable_d(a_w, b_w, shift=2e-3):
    """True в точках линии, рядом с которыми (на расстоянии shift по a или b) разностный оператор D устойчив."""
    near = np.zeros(a_w.size, dtype=bool)
    for da, db in ((shift, 0), (-shift, 0), (0, shift), (0, -shift)):
        near |= difference_operator_stable(a_w + da, b_w + db, T, H)
    return near


def draw_boundaries(ax, a_lim, b_lim):
    """
    Ветви D-кривой (со штрихами на первых ветвях), предельная кривая и прямые z = ±1 (красные, со штрихами).
    Внутри 𝔻_∞ линии рисуем бледно: там N = ∞ по обе стороны, и эти линии уже ничего не разделяют.
    """
    # D-кривая (9): переход на заштрихованную сторону добавляет пару корней ±iω
    for w, a_w, b_w in curve_branches(d_curve, T, H, W_MAX, W_STEP):
        fade = 1 / (1 + w[0] / 15)
        effects = ticked(d_curve_side(w, a_w, b_w, T, H)) if w[-1] <= W_TICKS else None
        draw_line(ax, a_w, b_w, difference_operator_stable(a_w, b_w, T, H), CURVE_COLOR,
                  0.4 + 1.1 * fade, 0.35 + 0.65 * fade, effects)

    # Предельная кривая (граница 𝔻_∞): переход на заштрихованную сторону даёт бесконечно много корней
    for w, a_w, b_w in curve_branches(limit_curve, T, H, 2 * np.pi, 10 ** -4):
        draw_line(ax, a_w, b_w, near_stable_d(a_w, b_w), LIMIT_COLOR, 1.8, 1.0,
                  ticked(limit_curve_side(a_w, b_w, T, H)))

    # Прямые z = ±1 — тоже часть границы 𝔻_∞. Проводим их через окно, сторону штрихов выбираем так же
    a_line = np.linspace(a_lim[0] - 1, a_lim[1] + 1, 4000)
    for c_a, c_b, c in z_lines(T, H):
        b_line = (c - c_a * a_line) / c_b
        draw_line(ax, a_line, b_line, near_stable_d(a_line, b_line), LIMIT_COLOR, 1.8, 1.0,
                  ticked(limit_curve_side(a_line, b_line, T, H)))


def label_regions(ax, a, b, roots, min_share):
    """
    Подписываем N в каждой достаточно крупной связной области (подпись ставим в самую «глубокую» точку —
    дальше всего от границы, там она точно не налезет на линии).
    """
    idx = color_index(roots)
    min_size = min_share * roots.size
    for value in np.unique(idx):
        components, count = ndimage.label(idx == value)  # связные куски области данного цвета
        for k in range(1, count + 1):
            mask = components == k
            if mask.sum() < min_size:
                continue
            # Расстояние до границы куска; берём точку, где оно максимально
            depth = ndimage.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
            i, j = np.unravel_index(np.argmax(depth), depth.shape)
            n = roots[i, j]
            text = r'$\infty$' if n < 0 else str(n)
            ax.text(a[j], b[i], text, ha='center', va='center', fontsize=15, fontweight='bold', zorder=6,
                    color='#1b5e20' if n == 0 else '#3b1d0f',
                    bbox=dict(boxstyle='circle,pad=0.25', fc='white', ec='none', alpha=0.8))


if __name__ == '__main__':
    # Штриховка 𝔻_∞ — тонкая и серая, чтобы не перебивать цветные области
    plt.rcParams['hatch.color'] = '#9e9e9e'
    plt.rcParams['hatch.linewidth'] = 0.6

    fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(17, 9.4))

    for ax, a_lim, b_lim, grid, min_share in ((ax_full, FULL_A, FULL_B, GRID_FULL, 0.01),
                                              (ax_zoom, ZOOM_A, ZOOM_B, GRID_ZOOM, 0.004)):
        a, b, roots = roots_on_grid(T, H, a_lim, b_lim, grid)
        draw_regions(ax, a, b, roots)
        draw_boundaries(ax, a_lim, b_lim)
        label_regions(ax, a, b, roots, min_share)
        setup_axes(ax, a_lim, b_lim)
        print(f'Окно a ∈ {a_lim}, b ∈ {b_lim}: найдены N = {sorted(set(roots[roots >= 0].tolist()))[:12]} ...')

    # Рамка увеличенного фрагмента на общем виде
    ax_full.add_patch(Rectangle((ZOOM_A[0], ZOOM_B[0]), ZOOM_A[1] - ZOOM_A[0], ZOOM_B[1] - ZOOM_B[0],
                                fill=False, ec='k', lw=1.4, ls='--', zorder=7))

    legend = [
        Patch(fc=STABLE_COLOR, label=r'$\mathbb{D}_0$'),
        *[Patch(fc=c, label=rf'$\mathbb{{D}}_{{{2 * (k + 1)}}}$') for k, c in enumerate(UNSTABLE_COLORS[:-1])],
        Patch(fc=UNSTABLE_COLORS[-1], label=rf'$\mathbb{{D}}_N,\ N \geq {2 * len(UNSTABLE_COLORS)}$'),
        Patch(fc=INFINITE_COLOR, hatch='//', label=r'$\mathbb{D}_\infty$'),
        Line2D([], [], color=CURVE_COLOR, lw=1.5, label=r'D-кривая (9): $\lambda = \pm i\omega$'),
        Line2D([], [], color=LIMIT_COLOR, lw=1.8, label=r'граница $\mathbb{D}_\infty$: $D(i\omega) = 0$'),
    ]
    fig.legend(handles=legend, loc='lower center', ncol=5, fontsize=13, frameon=False)

    fig.tight_layout(rect=(0, 0.1, 1, 1))
    IMAGES_DIR.mkdir(exist_ok=True)
    fig.savefig(IMAGES_DIR / 'D-regions.png', dpi=200)
    print(f'Сохранено: {IMAGES_DIR / "D-regions.png"}')
    plt.show()
