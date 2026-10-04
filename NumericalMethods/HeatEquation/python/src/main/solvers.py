import numpy as np

# Методы решения трёхдиагональной системы
#
#     y_(i-1) + d_i * y_i + e_i * y_(i+1) = g_i,   i = 1, ..., n-1,
#     y_0 = chi1 * y_1 + mu1,
#     y_n = chi2 * y_(n-1) + mu2.
#
# Это те же методы, что и в лабораторной работе BoundaryValue (там они разобраны подробно).
# Массивы d, e, g имеют длину n + 1, чтобы номер в массиве совпадал с номером узла.


# Правая (прямая) прогонка: y_i = Q_i * y_(i+1) + F_i
def right_sweep(d, e, g, chi1, mu1, chi2, mu2):
    n = len(d) - 1
    Q = np.zeros(n + 1)
    F = np.zeros(n + 1)

    # Начало берём из левого краевого условия
    Q[0] = chi1
    F[0] = mu1

    # Прямой ход: слева направо
    for i in range(1, n):
        denominator = Q[i - 1] + d[i]
        Q[i] = -e[i] / denominator
        F[i] = (g[i] - F[i - 1]) / denominator

    # Последнее значение — из правого краевого условия
    y = np.zeros(n + 1)
    y[n] = (mu2 + chi2 * F[n - 1]) / (1 - Q[n - 1] * chi2)

    # Обратный ход: справа налево
    for i in range(n - 1, -1, -1):
        y[i] = Q[i] * y[i + 1] + F[i]

    return y


# Левая (обратная) прогонка: y_(i+1) = xi_(i+1) * y_i + eta_(i+1)
def left_sweep(d, e, g, chi1, mu1, chi2, mu2):
    n = len(d) - 1
    xi = np.zeros(n + 1)
    eta = np.zeros(n + 1)

    # Начало берём из правого краевого условия
    xi[n] = chi2
    eta[n] = mu2

    # Справа налево
    for i in range(n - 1, 0, -1):
        denominator = d[i] + e[i] * xi[i + 1]
        xi[i] = -1 / denominator
        eta[i] = (g[i] - e[i] * eta[i + 1]) / denominator

    # Первое значение — из левого краевого условия
    y = np.zeros(n + 1)
    y[0] = (mu1 + chi1 * eta[1]) / (1 - chi1 * xi[1])

    # Слева направо
    for i in range(0, n):
        y[i + 1] = xi[i + 1] * y[i] + eta[i + 1]

    return y


# Встречная прогонка: правая слева до узла k, левая справа до узла k+1, встреча посередине
def meeting_sweep(d, e, g, chi1, mu1, chi2, mu2, k=None):
    n = len(d) - 1
    if k is None:
        k = n // 2

    # Правая прогонка до узла k
    Q = np.zeros(n + 1)
    F = np.zeros(n + 1)
    Q[0] = chi1
    F[0] = mu1
    for i in range(1, k + 1):
        denominator = Q[i - 1] + d[i]
        Q[i] = -e[i] / denominator
        F[i] = (g[i] - F[i - 1]) / denominator

    # Левая прогонка до узла k+1
    xi = np.zeros(n + 1)
    eta = np.zeros(n + 1)
    xi[n] = chi2
    eta[n] = mu2
    for i in range(n - 1, k, -1):
        denominator = d[i] + e[i] * xi[i + 1]
        xi[i] = -1 / denominator
        eta[i] = (g[i] - e[i] * eta[i + 1]) / denominator

    # Встреча: решаем систему из двух уравнений для y_k и y_(k+1)
    y = np.zeros(n + 1)
    y[k] = (Q[k] * eta[k + 1] + F[k]) / (1 - Q[k] * xi[k + 1])
    y[k + 1] = xi[k + 1] * y[k] + eta[k + 1]

    # Расходимся в обе стороны
    for i in range(k - 1, -1, -1):
        y[i] = Q[i] * y[i + 1] + F[i]
    for i in range(k + 1, n):
        y[i + 1] = xi[i + 1] * y[i] + eta[i + 1]

    return y


# Метод стрельбы: Y = C1*U + C2*V + W, константы C1 и C2 — из краевых условий
def shooting(d, e, g, chi1, mu1, chi2, mu2):
    n = len(d) - 1

    # По двум стартовым значениям "выстреливаем" всю последовательность
    def shoot(start0, start1, rhs):
        y = np.zeros(n + 1)
        y[0] = start0
        y[1] = start1
        for i in range(1, n):
            y[i + 1] = (rhs[i] - y[i - 1] - d[i] * y[i]) / e[i]
        return y

    zero = np.zeros(n + 1)
    U = shoot(0.0, 1.0, zero)
    V = shoot(1.0, 0.0, zero)
    W = shoot(0.0, 0.0, g)

    # Подбираем C1 и C2 из краевых условий (вывод — в README.md лабораторной BoundaryValue)
    A = U[n] - chi2 * U[n - 1]
    B = V[n] - chi2 * V[n - 1]
    R = mu2 - W[n] + chi2 * W[n - 1]
    C1 = (R - mu1 * B) / (A + chi1 * B)
    C2 = chi1 * C1 + mu1

    return C1 * U + C2 * V + W


# Все четыре метода в одном словаре: "название" -> функция
SOLVERS = {
    'Правая прогонка': right_sweep,
    'Левая прогонка': left_sweep,
    'Встречная прогонка': meeting_sweep,
    'Метод стрельбы': shooting,
}
