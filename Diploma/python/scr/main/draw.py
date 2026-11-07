"""
Общие функции отрисовки для рисунков D-разбиения (main.py и regions.py).
"""

import numpy as np
from matplotlib import patheffects

from roots import crossing_direction, difference_operator_inside, count_unstable_roots

# Цвета, общие для всех рисунков
STABLE_COLOR = '#8fd18f'  # область 𝔻₀ (светло-зелёный)
STABLE_EDGE = '#2e7d32'  # контур области 𝔻₀ (тёмно-зелёный)
CURVE_COLOR = '#1f3b8c'  # D-кривая (9)
LIMIT_COLOR = '#c62828'  # предельная кривая — граница области 𝔻_∞

# Штриховка границы: расстояние между штрихами и их длина (в точках)
TICK_SPACING = 6
TICK_LENGTH = 0.55


# ----------------------------------------------------------------------------------------------------------------------
# Сетка и подсчёт корней
# ----------------------------------------------------------------------------------------------------------------------

# noinspection PyPep8Naming
def roots_on_grid(T, H, a_lim, b_lim, n):
    """
    Число корней N с Re λ > 0 в узлах сетки n × n на окне a_lim × b_lim.
    Возвращает оси сетки a, b и матрицу N (строка — значение b, столбец — значение a).
    """
    a = np.linspace(*a_lim, n)
    b = np.linspace(*b_lim, n)
    a_mesh, b_mesh = np.meshgrid(a, b)
    roots = count_unstable_roots(a_mesh, b_mesh, T, H).reshape(a_mesh.shape)
    return a, b, roots


# ----------------------------------------------------------------------------------------------------------------------
# Ветви D-кривой
# ----------------------------------------------------------------------------------------------------------------------

def pieces(mask):
    """Срезы непрерывных отрезков, где mask = True: [F, T, T, F, T] → [slice(1, 3), slice(4, 5)]."""
    edges = np.diff(np.concatenate(([0], mask.astype(int), [0])))
    starts, stops = np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0]
    return [slice(s, e) for s, e in zip(starts, stops) if e - s > 1]


# noinspection PyPep8Naming
def curve_branches(curve, T, H, w_max, step, far=20.0):
    """
    Ветви параметрической кривой curve(ω) = (a(ω), b(ω)) при ω ∈ (0, w_max].

    Знаменатель sin(ω(T - H)) обнуляется при ω_k = πk/(T - H): там кривая уходит на бесконечность,
    поэтому каждую ветвь берём на своём интервале (ω_k, ω_{k+1}) и выкидываем далёкие точки (|a| или |b| > far).
    """
    period = np.pi / (T - H)
    branches = []
    for k in range(int(np.ceil(w_max / period))):
        left, right = k * period, min((k + 1) * period, w_max)
        w = np.arange(left, right, step)[1:]  # левый конец — особая точка (или ω = 0), отбрасываем
        if w.size < 3:
            continue
        a, b = curve(w, T, H)
        near = (np.abs(a) < far) & (np.abs(b) < far)
        branches += [(w[p], a[p], b[p]) for p in pieces(near)]
    return branches


# noinspection PyPep8Naming
def d_curve_side(w, a, b, T, H):
    """
    Сторона штриховки ветви D-кривой: +1 — слева по ходу роста ω, -1 — справа.

    Штрихуем ту сторону, при переходе на которую пара корней ±iω уходит в правую полуплоскость:
    сравниваем вектор g (см. roots.crossing_direction) с левой нормалью (-b'(ω), a'(ω)) к кривой.
    Знак на ветви постоянен, поэтому берём «голосование» по всем её точкам.
    """
    ta, tb = np.gradient(a, w), np.gradient(b, w)  # касательная (a'(ω), b'(ω))
    g_a, g_b = crossing_direction(w, a, b, T, H)
    return 1 if np.sum(np.sign(-tb * g_a + ta * g_b)) >= 0 else -1


# noinspection PyPep8Naming
def limit_curve_side(a, b, T, H, shift=1e-3):
    """
    Сторона штриховки красной границы (предельная кривая и прямые z = ±1): та, где у разностного
    оператора D больше корней z внутри единичного круга — туда уходит ещё одна цепочка корней λ.
    Проверяем численно: сдвигаемся от середины линии на shift по нормали в обе стороны.
    """
    i = a.size // 2
    ta, tb = a[i + 1] - a[i - 1], b[i + 1] - b[i - 1]
    norm = np.hypot(ta, tb)
    na, nb = -tb / norm * shift, ta / norm * shift  # левая нормаль длины shift
    left, right = difference_operator_inside(np.array([a[i] + na, a[i] - na]), np.array([b[i] + nb, b[i] - nb]), T, H)
    return 1 if left > right else -1


def ticked(side):
    """Эффект «штрихи вдоль линии»: angle = 90 — штрихи слева по ходу линии, angle = -90 — справа."""
    return [patheffects.withTickedStroke(angle=90 * side, spacing=TICK_SPACING, length=TICK_LENGTH)]


# noinspection PyPep8Naming
def z_lines(T, H):
    """
    Две прямые, которые тоже входят в границу 𝔻_∞: корень z = e^(-λ) = ±1 разностного оператора.
        z = 1:   1 - a - b = 0;
        z = -1:  1 - a·(-1)^T - b·(-1)^H = 0.
    Возвращаем их как тройки (c_a, c_b, c): c_a·a + c_b·b = c.
    """
    return [(1.0, 1.0, 1.0), (float((-1) ** T), float((-1) ** H), 1.0)]


# ----------------------------------------------------------------------------------------------------------------------
# Оформление осей
# ----------------------------------------------------------------------------------------------------------------------

def setup_axes(ax, a_lim, b_lim):
    """Окно, одинаковый масштаб по осям, оси координат, подписи и сетка. Ось b направлена вверх."""
    ax.set_xlim(a_lim)
    ax.set_ylim(b_lim)
    ax.set_aspect('equal')
    ax.axhline(0, color='k', lw=0.6, alpha=0.35, zorder=1)
    ax.axvline(0, color='k', lw=0.6, alpha=0.35, zorder=1)
    ax.set_xlabel('$a$', fontsize=20)
    ax.set_ylabel('$b$', fontsize=20, rotation=0, labelpad=12)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.grid(True, alpha=0.3, zorder=0)
