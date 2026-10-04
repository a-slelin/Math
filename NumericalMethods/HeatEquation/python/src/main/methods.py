import numpy as np
from const import f, f_xx, phi, alpha1, beta1, gamma1, alpha2, beta2, gamma2
from solvers import right_sweep


# ---------------------------------------------------------------------------
# Разностные схемы.
#
# Все три схемы из методички — это частные случаи схемы с весом sigma:
#
#   (u_i^(j+1) - u_i^j) / tau = sigma * Λu_i^(j+1) + (1 - sigma) * Λu_i^j + φ_i^j,
#
# где Λu_i = (u_(i-1) - 2*u_i + u_(i+1)) / h² — разностная вторая производная.
#
#   * неявная схема:                  sigma = 1,                   φ = f(x_i, t_(j+1));
#   * схема Кранка – Никольсона:      sigma = 1/2,                 φ = (f(x_i, t_j) + f(x_i, t_(j+1))) / 2;
#   * схема повышенного порядка:      sigma = 1/2 - h²/(12*tau),   φ = f + h²/12 * f''_xx  в точке (x_i, t_j + tau/2).
# ---------------------------------------------------------------------------

# Названия схем, в том порядке, в котором будем их выводить
SCHEMES = ('Неявная схема', 'Схема Кранка – Никольсона', 'Схема повышенного порядка')


# Возвращает вес sigma для выбранной схемы
def get_sigma(scheme, h, tau):
    if scheme == 'Неявная схема':
        return 1.0
    if scheme == 'Схема Кранка – Никольсона':
        return 0.5
    if scheme == 'Схема повышенного порядка':
        return 0.5 - h ** 2 / (12 * tau)
    raise ValueError(f'Неизвестная схема: {scheme}')


# Возвращает правую часть φ_i^j для выбранной схемы на шаге от t_j к t_(j+1)
def get_phi(scheme, x, t_j, h, tau):
    if scheme == 'Неявная схема':
        return f(x, t_j + tau)
    if scheme == 'Схема Кранка – Никольсона':
        return (f(x, t_j) + f(x, t_j + tau)) / 2
    if scheme == 'Схема повышенного порядка':
        t_half = t_j + tau / 2
        return f(x, t_half) + h ** 2 / 12 * f_xx(x, t_half)
    raise ValueError(f'Неизвестная схема: {scheme}')


# Краевые условия на слое t в виде y_0 = chi1*y_1 + mu1, y_n = chi2*y_(n-1) + mu2.
# Производную на краю заменяем односторонней разностью (как в BoundaryValue):
#     alpha1*y_0 + beta1*(y_1 - y_0)/h = gamma1,
#     alpha2*y_n + beta2*(y_n - y_(n-1))/h = gamma2.
def boundary_coefficients(t, h):
    chi1 = -beta1 / (alpha1 * h - beta1)
    mu1 = gamma1(t) * h / (alpha1 * h - beta1)
    chi2 = beta2 / (alpha2 * h + beta2)
    mu2 = gamma2(t) * h / (alpha2 * h + beta2)
    return chi1, mu1, chi2, mu2


# ---------------------------------------------------------------------------
# Решаем задачу выбранной схемой, слой за слоем, от t = 0 до t = t0.
#
# На каждом шаге по времени умножаем схему на h²/sigma и переносим всё
# известное (со старого слоя j) вправо. Для нового слоя y_i = u_i^(j+1) получаем:
#
#     y_(i-1) - (2 + h²/(tau*sigma)) * y_i + y_(i+1) = g_i,
#
#     g_i = -h²/(tau*sigma) * u_i^j - (1 - sigma)/sigma * (u_(i-1)^j - 2u_i^j + u_(i+1)^j) - h²/sigma * φ_i^j.
#
# Это ровно такая же трёхдиагональная система, как в BoundaryValue,
# и решается она прогонкой (или любым другим методом из solvers.py).
#
# Возвращает узлы x, моменты времени t и таблицу u[j, i] = u(x_i, t_j).
# ---------------------------------------------------------------------------
def solve_heat(scheme, n, m, t0, solver=right_sweep):
    h = 1 / n
    tau = t0 / m
    x = np.linspace(0, 1, n + 1)
    t = np.linspace(0, t0, m + 1)

    sigma = get_sigma(scheme, h, tau)

    # Таблица решения: строка j — это слой по времени t_j
    u = np.zeros((m + 1, n + 1))

    # Нулевой слой — начальное условие
    u[0] = phi(x)

    # Коэффициенты d_i и e_i одинаковы на всех слоях
    d = np.full(n + 1, -(2 + h ** 2 / (tau * sigma)))
    e = np.ones(n + 1)

    for j in range(m):
        old = u[j]

        # Разностная вторая производная на старом слое, умноженная на h²:
        # old_i-1 - 2*old_i + old_i+1 (на краях не нужна, оставляем 0)
        second_diff = np.zeros(n + 1)
        second_diff[1:-1] = old[:-2] - 2 * old[1:-1] + old[2:]

        # Правая часть g_i
        phi_values = get_phi(scheme, x, t[j], h, tau)
        g = (-h ** 2 / (tau * sigma) * old
             - (1 - sigma) / sigma * second_diff
             - h ** 2 / sigma * phi_values)

        # Краевые условия на новом слое t_(j+1)
        chi1, mu1, chi2, mu2 = boundary_coefficients(t[j + 1], h)

        # Решаем трёхдиагональную систему и получаем новый слой
        u[j + 1] = solver(d, e, g, chi1, mu1, chi2, mu2)

    return x, t, u


# ---------------------------------------------------------------------------
# Метод Фурье (разделения переменных), ряд до третьего члена.
#
# 1. Замена u = v + w, где w(x, t) = t + (t/e - t) * x — линейная функция,
#    которая сама удовлетворяет краевым условиям. Тогда для v:
#        v_t = v_xx + G(x, t),   v(0, t) = v(1, t) = 0,   v(x, 0) = Φ(x),
#        G = f - w_t + w_xx = (1 - t)*e^(-x) - (1 + (1/e - 1)*x),
#        Φ = phi(x) - w(x, 0) = 0.
#
# 2. Собственные функции задачи y'' = λy, y(0) = y(1) = 0:
#        e_k(x) = sin(kπx),   λ_k = -(kπ)².
#
# 3. Раскладываем G по синусам: G(x, t) = Σ G_k(t) * sin(kπx),
#        G_k(t) = 2 * ∫[0,1] G(x, t) sin(kπx) dx = a_k + b_k * t
#    (интегралы считаются руками, формулы — в README.md).
#
# 4. Для каждого k решаем ОДУ  v_k' = -(kπ)² v_k + a_k + b_k t,  v_k(0) = 0.
#    Его решение: v_k(t) = c0 + c1*t - c0*e^(-(kπ)² t),
#        где c1 = b_k / (kπ)²,  c0 = (a_k - c1) / (kπ)².
#
# 5. Ответ: u(x, t) ≈ w(x, t) + Σ_(k=1..K) v_k(t) * sin(kπx).
# ---------------------------------------------------------------------------
def fourier_coefficients(k):
    kp = k * np.pi
    sign = (-1) ** k

    # Три интеграла по отрезку [0, 1]:
    #   I1 = ∫ e^(-x) sin(kπx) dx,   I2 = ∫ sin(kπx) dx,   I3 = ∫ x sin(kπx) dx
    I1 = kp * (1 - sign * np.exp(-1)) / (1 + kp ** 2)
    I2 = (1 - sign) / kp
    I3 = -sign / kp

    # G_k(t) = 2 * [(1 - t)*I1 - I2 - (1/e - 1)*I3] = a_k + b_k * t
    a_k = 2 * (I1 - I2 - (np.exp(-1) - 1) * I3)
    b_k = -2 * I1
    return a_k, b_k


def fourier_solution(x, t, terms):
    # Функция w, которая "забирает" на себя краевые условия
    w = t + (t * np.exp(-1) - t) * x

    v = np.zeros_like(x)
    for k in range(1, terms + 1):
        a_k, b_k = fourier_coefficients(k)
        mu = (k * np.pi) ** 2

        # Решение ОДУ для коэффициента v_k(t) (начальное значение v_k(0) = 0)
        c1 = b_k / mu
        c0 = (a_k - c1) / mu
        v_k = c0 + c1 * t - c0 * np.exp(-mu * t)

        v += v_k * np.sin(k * np.pi * x)

    return w + v
