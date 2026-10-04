import numpy as np
from const import a, b, lam, kernel, f, n, eps, max_iterations


# Строим сетку: делим отрезок [a, b] на n равных частей.
# Получается n + 1 точка: t_0 = a, t_1, ..., t_n = b.
def make_grid():
    return np.linspace(a, b, n + 1)


# Веса формулы трапеций.
# Интеграл ∫[a, b] g(s) ds ≈ h * (g_0 / 2 + g_1 + g_2 + ... + g_(n-1) + g_n / 2),
# где h = (b - a) / n — шаг сетки.
# То есть у крайних точек вес h / 2, а у всех внутренних — h.
def trapezoid_weights():
    h = (b - a) / n
    weights = np.full(n + 1, h)
    weights[0] = h / 2
    weights[-1] = h / 2
    return weights


# Таблица значений ядра на сетке: K_jk = K(t_j, s_k).
# Строка j — это точка t_j, столбец k — это точка s_k.
def kernel_matrix(grid):
    # meshgrid делает две таблицы: в одной везде стоят t_j, в другой — s_k
    t, s = np.meshgrid(grid, grid, indexing='ij')
    return kernel(t, s)


# Проверяем, сжимающий ли оператор A (это условие сходимости
# метода последовательных приближений).
# Возвращаем числа, которые потом печатаем и сравниваем с единицей.
def check_contraction():
    # Берём густую сетку, чтобы хорошо оценить максимум и интеграл
    fine = np.linspace(a, b, 1001)
    t, s = np.meshgrid(fine, fine, indexing='ij')
    values = kernel(t, s)

    # M = max |K(t, s)| на квадрате [a, b] x [a, b]
    M = np.max(np.abs(values))

    # B = корень из двойного интеграла от K² по квадрату.
    # Двойной интеграл считаем как "среднее значение * площадь квадрата".
    B = np.sqrt(np.mean(values ** 2) * (b - a) ** 2)

    # Условие в пространстве C[a, b]:  |λ| * M * (b - a) < 1
    c_value = abs(lam) * M * (b - a)

    # Условие в пространстве L2[a, b]: |λ| * B < 1
    l2_value = abs(lam) * B

    return M, B, c_value, l2_value


# ---------------------------------------------------------------------------
# Метод 1. Метод последовательных приближений.
#
# Идея: берём любую стартовую функцию φ_0 (у нас φ_0 = f),
# и много раз подставляем её в правую часть уравнения:
#     φ_(k+1)(t) = λ * ∫ K(t, s) φ_k(s) ds + f(t).
# Если оператор сжимающий, то функции φ_k приближаются к ответу.
# ---------------------------------------------------------------------------
def successive_approximations():
    grid = make_grid()
    K = kernel_matrix(grid)
    w = trapezoid_weights()
    f_values = f(grid)

    # Стартуем с φ_0 = f
    phi = f_values.copy()

    # Сюда будем записывать, насколько сильно менялось решение на каждом шаге
    differences = []

    for step in range(1, max_iterations + 1):
        # Считаем интеграл ∫ K(t_j, s) φ(s) ds для каждой точки t_j сразу.
        # K @ (w * phi) — это сумма по k от K_jk * w_k * φ_k.
        integral = K @ (w * phi)

        # Новое приближение
        new_phi = lam * integral + f_values

        # Насколько новое приближение отличается от старого (максимум по модулю)
        diff = np.max(np.abs(new_phi - phi))
        differences.append(diff)

        phi = new_phi

        # Если изменения стали совсем маленькими — останавливаемся
        if diff < eps:
            break

    return grid, phi, differences


# ---------------------------------------------------------------------------
# Метод 2. Сведение к системе линейных алгебраических уравнений (СЛАУ).
#
# Идея: заменяем интеграл суммой по формуле трапеций и записываем
# уравнение в каждой точке сетки t_j. Получаем n + 1 уравнение
# с n + 1 неизвестными φ_0, ..., φ_n:
#     φ_j - λ * Σ_k w_k K_jk φ_k = f_j,
# или коротко (I - Q) φ = f, где Q_jk = λ * w_k * K_jk.
# ---------------------------------------------------------------------------
def linear_system():
    grid = make_grid()
    K = kernel_matrix(grid)
    w = trapezoid_weights()
    f_values = f(grid)

    # Матрица Q: каждый столбец k умножаем на свой вес w_k
    Q = lam * K * w

    # Единичная матрица I того же размера
    I = np.eye(n + 1)

    # Решаем систему (I - Q) φ = f готовой функцией numpy
    phi = np.linalg.solve(I - Q, f_values)

    return grid, phi
