import numpy as np

from const import TAU_1, TAU_2


def characteristic(lam, a1, a2, eps, A):
    """Значение квазиполинома P(λ) = ε²λ² + εAλ + 1 + a₁e^(-τ₁λ) + a₂e^(-τ₂λ)."""
    return eps ** 2 * lam ** 2 + eps * A * lam + 1 + a1 * np.exp(-TAU_1 * lam) + a2 * np.exp(-TAU_2 * lam)


def characteristic_derivative(lam, a1, a2, eps, A):
    """Производная P'(λ) по λ."""
    return (2 * eps ** 2 * lam + eps * A
            - TAU_1 * a1 * np.exp(-TAU_1 * lam) - TAU_2 * a2 * np.exp(-TAU_2 * lam))


def zero_root_line(a1):
    """Граница λ = 0: P(0) = 1 + a₁ + a₂ = 0, т.е. a₂ = -1 - a₁."""
    return -1 - a1


def d_curve(omega, eps, A):
    """
    Граница λ = iω, ω > 0.

    Подставляем λ = iω в P(λ) = 0 и разделяем вещественную и мнимую части:

        a₁·cos(2ω) + a₂·cos(6ω) = ε²ω² - 1     (= R)
        a₁·sin(2ω) + a₂·sin(6ω) = εAω          (= I)

    Определитель системы: Δ(ω) = cos2ω·sin6ω - sin2ω·cos6ω = sin(4ω).
    По правилу Крамера:

        a₁(ω) = (R·sin6ω - I·cos6ω) / sin4ω,
        a₂(ω) = (I·cos2ω - R·sin2ω) / sin4ω.
    """
    R = eps ** 2 * omega ** 2 - 1
    I = eps * A * omega
    det = np.sin((TAU_2 - TAU_1) * omega)

    a1 = (R * np.sin(TAU_2 * omega) - I * np.cos(TAU_2 * omega)) / det
    a2 = (I * np.cos(TAU_1 * omega) - R * np.sin(TAU_1 * omega)) / det
    return a1, a2


def crossing_direction(omega, a1, a2, eps, A):
    """
    Направление (в плоскости (a₁, a₂)), при сдвиге в которое корень λ = iω
    уходит в правую полуплоскость.

    Из P(λ(a), a) = 0 получаем dλ = -(e^(-2iω)·da₁ + e^(-6iω)·da₂) / P'(iω),
    поэтому Re dλ = g·da, где g — вектор, который мы и возвращаем.
    """
    lam = 1j * omega
    dp = characteristic_derivative(lam, a1, a2, eps, A)
    g1 = np.real(-np.exp(-TAU_1 * lam) / dp)
    g2 = np.real(-np.exp(-TAU_2 * lam) / dp)
    return g1, g2


def guaranteed_radius(A):
    """
    Ромб гарантированной устойчивости |a₁| + |a₂| < m(A), верный сразу для всех ε > 0.

    При λ = iω положим x = εω ≥ 0. Тогда |ε²λ² + εAλ + 1| = |1 - x² + iAx| ≥ m(A),
    а |a₁e^(-2iω) + a₂e^(-6iω)| ≤ |a₁| + |a₂|. Значит, внутри ромба P(iω) ≠ 0
    ни при каком ω, ромб содержит устойчивую точку (0, 0) и, следовательно,
    целиком лежит в области устойчивости.

        m(A) = min_x |1 - x² + iAx| = A·√(1 - A²/4)  при 0 < A < √2,
        m(A) = 1                                   при A ≥ √2.

    При ε → 0 частоты ω = x/ε пробегают все фазы, и оценка становится точной
    в вершинах ромба (область устойчивости «сжимается» к нему).
    """
    if A <= 0:
        return 0.0
    return A * np.sqrt(1 - A ** 2 / 4) if A ** 2 < 2 else 1.0
