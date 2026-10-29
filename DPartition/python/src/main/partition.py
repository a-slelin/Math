from collections import deque

import numpy as np

from const import TAU_1, TAU_2, OMEGA_STEP, COUNT_STEP
from equation import d_curve, crossing_direction

# Полупериод знаменателя Δ(ω) = sin(4ω): нули в точках ω = kπ/4
DELTA_ZERO_STEP = np.pi / (TAU_2 - TAU_1)


def window_radius(a1_lim, a2_lim):
    """L = max(|a₁| + |a₂|) по окну — грубая оценка величины параметров."""
    return max(abs(a1_lim[0]), abs(a1_lim[1])) + max(abs(a2_lim[0]), abs(a2_lim[1]))


def omega_max(eps, a1_lim, a2_lim):
    """
    Частота, начиная с которой D-кривая гарантированно уходит за пределы окна.

    Из системы для λ = iω: |ε²ω² - 1| ≤ |a₁| + |a₂| ≤ L, значит при
    ω > √(1 + L)/ε точек кривой в окне нет. При ε = 0 кривая периодична
    по ω с периодом π, поэтому достаточно взять ω ∈ (0, π).
    """
    if eps == 0:
        return np.pi
    return np.sqrt(1 + window_radius(a1_lim, a2_lim)) / eps + 1


def d_curve_branches(eps, A, a1_lim, a2_lim):
    """
    Разбиваем D-кривую на ветви между нулями Δ(ω) = sin4ω (там кривая уходит
    на бесконечность). Для каждой ветви возвращаем массивы ω, a₁(ω), a₂(ω)
    и сторону штриховки: +1 — слева по ходу роста ω, -1 — справа.
    """
    big = 10 * window_radius(a1_lim, a2_lim)  # всё, что дальше, обрезаем
    branches = []

    k_max = int(np.ceil(omega_max(eps, a1_lim, a2_lim) / DELTA_ZERO_STEP))
    for k in range(k_max):
        left, right = k * DELTA_ZERO_STEP, (k + 1) * DELTA_ZERO_STEP
        n = max(int((right - left) / OMEGA_STEP), 200)
        omega = np.linspace(left, right, n)[1:-1]  # концы — особые точки
        a1, a2 = d_curve(omega, eps, A)

        near = (np.abs(a1) < big) & (np.abs(a2) < big)
        if not near.any():
            continue

        # Далёкие точки выкидываем, а оставшиеся куски ветви храним по отдельности
        side = hatch_side(omega[near], a1[near], a2[near], eps, A)
        for piece in contiguous_pieces(near):
            branches.append({'omega': omega[piece], 'a1': a1[piece], 'a2': a2[piece], 'side': side})

    return branches


def contiguous_pieces(mask):
    """Индексы непрерывных отрезков, где mask = True."""
    edges = np.diff(np.concatenate(([0], mask.astype(int), [0])))
    starts, stops = np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0]
    return [slice(a, b) for a, b in zip(starts, stops) if b - a > 1]


def hatch_side(omega, a1, a2, eps, A):
    """
    Штриховка D-разбиения: штрихуем ту сторону кривой, при переходе на
    которую пара корней ±iω уходит в правую полуплоскость.

    Сравниваем направление g (см. crossing_direction) с левой нормалью
    к касательной (da₁/dω, da₂/dω). Знак постоянен на ветви, поэтому
    берём «голосование» по всем точкам ветви.
    """
    t1, t2 = np.gradient(a1, omega), np.gradient(a2, omega)
    g1, g2 = crossing_direction(omega, a1, a2, eps, A)
    dot = -t2 * g1 + t1 * g2  # скалярное произведение g и левой нормали (-t₂, t₁)
    return 1 if np.sum(np.sign(dot)) >= 0 else -1


def singular_lines(eps, A, a1_lim, a2_lim, tol=1e-9):
    """
    Особые прямые: при sin4ω = 0 система для λ = iω вырождается и может
    задавать целую прямую в плоскости (a₁, a₂). Это бывает только если:
      * ω = πm/2   и  εAω = 0          (то есть ε·A = 0);
      * ω = π/4·(2m+1) и ε²ω² = 1     (то есть 1/ε попало в эту сетку).
    Возвращаем список троек (c₁, c₂, c), задающих прямую c₁·a₁ + c₂·a₂ = c.
    Прямая λ = 0 (ω = 0) сюда не входит — она строится отдельно.
    """
    lines = []
    k_max = int(np.ceil(omega_max(eps, a1_lim, a2_lim) / DELTA_ZERO_STEP))
    for k in range(1, k_max + 1):
        w = k * DELTA_ZERO_STEP
        R, I = eps ** 2 * w ** 2 - 1, eps * A * w
        c = np.array([[np.cos(TAU_1 * w), np.cos(TAU_2 * w), R],
                      [np.sin(TAU_1 * w), np.sin(TAU_2 * w), I]])
        # Ранг вырожденной системы равен 1: подходит та строка, где есть коэффициенты
        row_r, row_i = c[0], c[1]
        if np.allclose(row_i[:2], 0, atol=tol) and abs(row_i[2]) < tol:
            line = tuple(row_r)
        elif np.allclose(row_r[:2], 0, atol=tol) and abs(row_r[2]) < tol:
            line = tuple(row_i)
        else:
            continue

        # Нормируем, чтобы одинаковые прямые совпали, и отбрасываем прямую λ = 0
        line = tuple(np.round(np.array(line) / line[0], 9).tolist())
        if line != (1.0, 1.0, -1.0) and line not in lines:
            lines.append(line)
    return lines


def count_unstable_roots(eps, A, a1, a2, chunk=2000):
    """
    Число корней P(λ) в правой полуплоскости Re λ > 0 (ε > 0) для каждой
    пары (a₁, a₂) — по принципу аргумента.

    P — квазиполином запаздывающего типа со старшим членом ε²λ² (n = 2),
    поэтому при движении по мнимой оси ω: 0 → +∞

        Δ arg P(iω) = π·(n/2 - N)  ⇒  N = 1 - Δ/π.

    При ω > Ω = √(1 + L)/ε имеем Re P(iω) ≤ 1 - ε²ω² + L < 0, т.е. P(iω)
    остаётся в левой полуплоскости и в пределе arg P → π. Поэтому считаем
    аргумент численно на [0, Ω], а «хвост» добавляем аналитически.
    """
    if eps <= 0:
        raise ValueError('Подсчёт по принципу аргумента требует ε > 0')

    a1, a2 = np.ravel(a1), np.ravel(a2)
    big_l = np.max(np.abs(a1) + np.abs(a2))
    big_omega = np.sqrt(1 + big_l) / eps + 1
    omega = np.arange(0, big_omega + COUNT_STEP, COUNT_STEP)

    # Части P(iω), не зависящие от параметров, считаем один раз
    lam = 1j * omega
    base = eps ** 2 * lam ** 2 + eps * A * lam + 1
    e1, e2 = np.exp(-TAU_1 * lam), np.exp(-TAU_2 * lam)

    roots = np.empty(a1.size, dtype=int)
    for s in range(0, a1.size, chunk):
        p = base + a1[s:s + chunk, None] * e1 + a2[s:s + chunk, None] * e2
        p[p == 0] = 1e-12  # точка ровно на границе: N там не определено, просто избегаем деления на 0

        # Приращение аргумента = сумма малых поворотов между соседними точками
        delta = np.angle(p[:, 1:] / p[:, :-1]).sum(axis=1)

        # Хвост: от arg P(iΩ) до ближайшего π (mod 2π)
        delta += np.angle(-1 / p[:, -1])
        roots[s:s + chunk] = np.rint(1 - delta / np.pi).astype(int)

    return roots


def stable_mask_limit(a1, a2):
    """
    Предельный случай ε = 0: P(λ) = 1 + a₁e^(-2λ) + a₂e^(-6λ).

    Замена z = e^(-2λ) даёт многочлен 1 + a₁z + a₂z³, а условие Re λ < 0
    равносильно |z| > 1. Переходя к w = 1/z, получаем: все корни
    w³ + a₁w² + a₂ = 0 должны лежать строго внутри единичного круга.
    Корни ищем как собственные числа сопровождающей матрицы (сразу для всей сетки).
    """
    a1, a2 = np.ravel(a1), np.ravel(a2)
    companion = np.zeros((a1.size, 3, 3))
    companion[:, 0, 0] = -a1
    companion[:, 0, 2] = -a2
    companion[:, 1, 0] = 1
    companion[:, 2, 1] = 1
    w = np.linalg.eigvals(companion)
    return np.max(np.abs(w), axis=1) < 1


def connected_regions(labels):
    """
    Связные компоненты (4-связность) сетки с одинаковыми значениями.
    Возвращает список (значение, маска компоненты).
    """
    rows, cols = labels.shape
    seen = np.zeros_like(labels, dtype=bool)
    regions = []

    for i in range(rows):
        for j in range(cols):
            if seen[i, j]:
                continue
            value, mask = labels[i, j], np.zeros_like(seen)
            queue = deque([(i, j)])
            seen[i, j] = True
            while queue:
                y, x = queue.popleft()
                mask[y, x] = True
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= ny < rows and 0 <= nx < cols and not seen[ny, nx] and labels[ny, nx] == value:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
            regions.append((value, mask))

    return regions


def deepest_point(mask):
    """Самая «глубокая» точка области (дольше всех переживает эрозию) — сюда ставим подпись."""
    current = mask.copy()
    while True:
        inner = current.copy()
        inner[1:, :] &= current[:-1, :]
        inner[:-1, :] &= current[1:, :]
        inner[:, 1:] &= current[:, :-1]
        inner[:, :-1] &= current[:, 1:]
        inner[[0, -1], :] = inner[:, [0, -1]] = False  # край окна считаем границей области
        if not inner.any():
            ys, xs = np.nonzero(current)
            mid = len(ys) // 2
            return ys[mid], xs[mid]
        current = inner

