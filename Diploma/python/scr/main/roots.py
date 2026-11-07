"""
Математика D-разбиения для характеристического уравнения (4) нейтрального типа

    P(λ) = λ + 1 - a·λ·e^(-λT) - b·λ·e^(-λH) = 0,    T > H > 0.

Здесь собрано всё, что нужно для рисунков:
  * D-кривая (9) — граница, на которой есть корень λ = ±iω;
  * предельная кривая — граница устойчивости разностного оператора D(λ) = 1 - a·e^(-λT) - b·e^(-λH);
  * направление, в котором корень λ = iω уходит в правую полуплоскость (штриховка границы);
  * число N корней с Re λ > 0 в каждой точке сетки (a, b) — по принципу аргумента.

Все функции принимают как числа, так и массивы numpy (считают поэлементно).
Запаздывания T и H должны быть целыми: тогда D(λ) — многочлен от z = e^(-λ), и его корни
легко найти (этого достаточно для T = 5, H = 1 из работы).
"""

import numpy as np


# ----------------------------------------------------------------------------------------------------------------------
# Характеристическое уравнение и его производные
# ----------------------------------------------------------------------------------------------------------------------

# noinspection PyPep8Naming
def characteristic(lam, a, b, T, H):
    """P(λ) = λ + 1 - a·λ·e^(-λT) - b·λ·e^(-λH)."""
    return lam + 1 - a * lam * np.exp(-lam * T) - b * lam * np.exp(-lam * H)


# noinspection PyPep8Naming
def characteristic_derivative(lam, a, b, T, H):
    """P'(λ) = 1 - a·e^(-λT)·(1 - λT) - b·e^(-λH)·(1 - λH) — производная по λ."""
    return 1 - a * np.exp(-lam * T) * (1 - lam * T) - b * np.exp(-lam * H) * (1 - lam * H)


# ----------------------------------------------------------------------------------------------------------------------
# Границы D-разбиения
# ----------------------------------------------------------------------------------------------------------------------

# noinspection PyPep8Naming
def d_curve(w, T, H):
    """
    D-кривая (9): точки (a, b), при которых λ = iω — корень уравнения (4).
    Знаменатель sin(ω(T - H)) обращается в ноль при ω = πk/(T - H) — там ветви уходят на бесконечность.
    """
    det = np.sin(w * (T - H))
    a = (np.cos(w * H) / w - np.sin(w * H)) / det
    b = (np.sin(w * T) - np.cos(w * T) / w) / det
    return a, b


# noinspection PyPep8Naming
def limit_curve(w, T, H):
    """
    Предельная кривая (ω → ∞ в формуле (9), слагаемые с 1/ω пропадают):

        a(ω) = -sin(ωH) / sin(ω(T - H)),    b(ω) = sin(ωT) / sin(ω(T - H)).

    Это D-кривая разностного оператора D(λ) = 1 - a·e^(-λT) - b·e^(-λH):
    на ней D(iω) = 0. Именно к ней «прижимаются» ветви D-кривой при больших ω.
    """
    det = np.sin(w * (T - H))
    return -np.sin(w * H) / det, np.sin(w * T) / det


# noinspection PyPep8Naming
def crossing_direction(w, a, b, T, H):
    """
    Вектор g = (g_a, g_b): при малом сдвиге (da, db) от точки D-кривой корень λ = iω
    сдвигается так, что Re dλ = g_a·da + g_b·db.

    Дифференцируем тождество P(λ(a, b), a, b) = 0:
        P'(λ)·dλ - λe^(-λT)·da - λe^(-λH)·db = 0   ⇒   dλ = (λe^(-λT)·da + λe^(-λH)·db) / P'(λ).
    Значит, сдвиг вдоль g уводит пару корней ±iω в правую полуплоскость.
    """
    lam = 1j * w
    dp = characteristic_derivative(lam, a, b, T, H)
    g_a = np.real(lam * np.exp(-lam * T) / dp)
    g_b = np.real(lam * np.exp(-lam * H) / dp)
    return g_a, g_b


# ----------------------------------------------------------------------------------------------------------------------
# Разностный оператор D(z) = 1 - a·z^T - b·z^H,  z = e^(-λ)
# ----------------------------------------------------------------------------------------------------------------------

# noinspection PyPep8Naming
def difference_operator_roots(a, b, T, H):
    """
    Корни z многочлена 1 - a·z^T - b·z^H (для каждой точки (a, b) — строка из T корней).

    Делим уравнение a·z^T + b·z^H - 1 = 0 на a: z^T + (b/a)·z^H - 1/a = 0,
    и ищем корни как собственные числа сопровождающей матрицы — сразу для всех точек.
    При a = 0 многочлен вырождается в 1 - b·z^H: его корни |z| = |b|^(-1/H), недостающие корни
    считаем лежащими на бесконечности.
    """
    a, b = np.ravel(a).astype(float), np.ravel(b).astype(float)
    z = np.full((a.size, T), np.inf, dtype=complex)
    nz = np.abs(a) > 1e-14
    if nz.any():
        an, bn = a[nz], b[nz]
        coef = np.zeros((an.size, T))  # коэффициенты при z^(T-1), ..., z^0 (без старшего z^T)
        coef[:, T - 1 - H] = bn / an  # z^H
        coef[:, T - 1] = -1 / an  # z^0
        companion = np.zeros((an.size, T, T))
        companion[:, 0, :] = -coef  # первая строка — коэффициенты с обратным знаком
        companion[:, np.arange(1, T), np.arange(T - 1)] = 1  # под главной диагональю единицы
        z[nz] = np.linalg.eigvals(companion)
    zero_a = ~nz & (np.abs(b) > 1e-14)
    z[zero_a, :H] = np.abs(b[zero_a, None]) ** (-1 / H)  # для проверки |z| > 1 хватает модуля
    return z


# noinspection PyPep8Naming
def difference_operator_inside(a, b, T, H):
    """Сколько корней z разностного оператора лежит внутри единичного круга (|z| < 1)."""
    return np.sum(np.abs(difference_operator_roots(a, b, T, H)) < 1, axis=1)


# noinspection PyPep8Naming
def difference_operator_stable(a, b, T, H, margin=1e-9):
    """
    True, если все корни многочлена 1 - a·z^T - b·z^H лежат вне единичного круга (|z| > 1).

    Корень z₀ с |z₀| < 1 даёт целую цепочку корней уравнения (4) вблизи λ_k = -ln z₀ + 2πik,
    у которых Re λ_k → -ln|z₀| > 0. Тогда корней в правой полуплоскости бесконечно много (N = ∞).
    """
    return np.min(np.abs(difference_operator_roots(a, b, T, H)), axis=1) > 1 + margin


# noinspection PyPep8Naming
def difference_operator_min(a, b, T, H, n=4096):
    """m = min |D(iω)| = min по |z| = 1 модуля 1 - a·z^T - b·z^H (D 2π-периодична по ω, хватает одного периода)."""
    u = np.linspace(0, 2 * np.pi, n, endpoint=False)
    zt, zh = np.exp(-1j * u * T), np.exp(-1j * u * H)
    a, b = np.ravel(a), np.ravel(b)
    out = np.empty(a.size)
    chunk = max(1, 4_000_000 // n)  # чтобы матрица «точки × ω» не съела всю память
    for s in range(0, a.size, chunk):
        out[s:s + chunk] = np.min(np.abs(1 - a[s:s + chunk, None] * zt - b[s:s + chunk, None] * zh), axis=1)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Подсчёт числа корней N с Re λ > 0
# ----------------------------------------------------------------------------------------------------------------------

INFINITE = -1  # так помечаем точки, где корней с Re λ > 0 бесконечно много (N = ∞)
UNRESOLVED = -2  # точка слишком близко к предельной кривой: шаг по ω пришлось бы брать слишком мелким


# noinspection PyPep8Naming
def count_unstable_roots(a, b, T, H, m_min=2e-3, max_elements=3_000_000):
    """
    Число корней уравнения (4) с Re λ > 0 для каждой точки (a, b).

    1) Если разностный оператор D неустойчив — N = ∞ (см. difference_operator_stable).
    2) Иначе D(λ) ≠ 0 при Re λ ≥ 0, и корни P совпадают с корнями функции

           Q(λ) = P(λ) / ((λ + 1)·D(λ)) = 1 + E(λ) / ((λ + 1)·D(λ)),   E(λ) = a·e^(-λT) + b·e^(-λH).

       В правой полуплоскости |E| ≤ |a| + |b| и |D| ≥ m, поэтому Q → 1 при |λ| → ∞, и по принципу
       аргумента (контур — мнимая ось и большая полуокружность справа)

           N = -(1/π)·Δ arg Q(iω),  ω: 0 → +∞,     Q(0) = 1 / (1 - a - b) > 0.

       При ω > Ω = 2(|a| + |b|)/m имеем |Q - 1| < 1/2, т.е. Q больше не может обернуться вокруг нуля:
       считаем приращение аргумента численно на [0, Ω], а хвост добавляем как -arg Q(iΩ).

    Шаг по ω выбираем по m: вблизи нулей D аргумент Q поворачивается со скоростью до (T|a| + H|b|)/m.
    """
    a, b = np.ravel(a).astype(float), np.ravel(b).astype(float)
    roots = np.full(a.size, INFINITE, dtype=int)

    stable_d = difference_operator_stable(a, b, T, H)
    idx = np.nonzero(stable_d)[0]
    m = difference_operator_min(a[idx], b[idx], T, H)

    # Совсем близко к предельной кривой честный счёт слишком дорогой — помечаем такие точки отдельно
    roots[idx[m < m_min]] = UNRESOLVED
    idx, m = idx[m >= m_min], m[m >= m_min]

    # Группируем точки по m (в «октавы» [m₀, 2m₀)): у каждой группы общие Ω и шаг по ω
    octave = np.floor(np.log2(m)).astype(int)
    for o in np.unique(octave):
        sel = idx[octave == o]
        m0 = 2.0 ** o  # нижняя граница m в этой группе
        size = np.max(np.abs(a[sel]) + np.abs(b[sel]))
        speed = np.max(T * np.abs(a[sel]) + H * np.abs(b[sel])) + 1
        big_omega = 2 * size / m0 + 1
        step = min(0.02, 0.5 * m0 / speed)
        w = np.arange(0, big_omega + step, step)

        # Не зависящие от параметров множители считаем один раз
        lam = 1j * w
        et, eh = np.exp(-lam * T), np.exp(-lam * H)

        chunk = max(1, max_elements // w.size)
        for s in range(0, sel.size, chunk):
            part = sel[s:s + chunk]
            e = a[part, None] * et + b[part, None] * eh  # E(iω)
            q = 1 + e / ((lam + 1) * (1 - e))  # Q(iω), D = 1 - E

            # Приращение аргумента — сумма малых поворотов между соседними точками
            delta = np.angle(q[:, 1:] / q[:, :-1]).sum(axis=1)
            delta -= np.angle(q[:, -1])  # хвост: от arg Q(iΩ) до 0

            roots[part] = np.rint(-delta / np.pi).astype(int)  # N — целое, rint убирает погрешность
    return roots
