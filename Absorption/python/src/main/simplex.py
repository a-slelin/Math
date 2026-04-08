import numpy as np


def read_simplex(filename):
    """
    Читает файл с координатами вершин симплекса.
    Формат: первая строка содержит целое число n (размерность),
    затем n+1 строк, каждая из которых содержит n чисел (координаты вершины).
    Возвращает n и массив вершин (n+1, n).
    """
    with open(filename, 'r') as f:
        n = int(f.readline().strip())
        vertices = []
        for _ in range(n + 1):
            line = f.readline()
            if not line:
                raise ValueError("Недостаточно строк с вершинами")
            coords = list(map(float, line.split()))
            if len(coords) != n:
                raise ValueError(f"Ожидалось {n} координат, получено {len(coords)}")
            vertices.append(coords)
    return n, np.array(vertices, dtype=float)


def build_A(vertices):
    """
    Строит матрицу A размера (n+1) x (n+1):
    первые n столбцов - координаты вершин, последний столбец - единицы.
    """
    A = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
    return A


def compute_inverse(A):
    """Возвращает обратную матрицу A^{-1}."""
    return np.linalg.inv(A)


def compute_alpha(A_inv, n):
    """
    Вычисляет α(S) = 0.5 * sum_{i=1..n} sum_{j=1..n+1} |l_{ij}|
    где l_{ij} - элементы A_inv (строки i, столбцы j).
    """
    # Берём только первые n строк (соответствуют координатам)
    rows = A_inv[:n, :]
    return 0.5 * np.sum(np.abs(rows))


def compute_xi(A_inv, n):
    """
    Вычисляет ξ(S) = (n+1) * max_j M_j + 1,
    где M_j = sum_{i: l_{ij}<0} |l_{ij}| - l_{n+1,j}.
    """
    M = []
    for j in range(n + 1):
        col = A_inv[:n, j]  # коэффициенты при переменных
        free = A_inv[n, j]  # свободный член
        neg_sum = -np.sum(col[col < 0])  # сумма модулей отрицательных
        M_j = neg_sum - free
        M.append(M_j)
    return max(1.0, (n + 1) * max(M) + 1)


def compute_axial_ends(A_inv, vertices):
    """
    Для каждой координатной оси i (1..n) возвращает пару точек (концы отрезка)
    максимальной длины, параллельного этой оси.
    Использует формулы (1.13)-(1.14) из пособия.
    """
    n = vertices.shape[1]
    ends = []
    for i in range(n):
        row = A_inv[i, :]  # l_{i1} ... l_{i,n+1}
        s = np.abs(row) - row
        t = np.abs(row) + row
        sum_abs = np.sum(np.abs(row))
        if sum_abs == 0:
            raise ValueError(f"Нулевая строка {i + 1} в обратной матрице")
        alpha = s / sum_abs
        beta = t / sum_abs
        y_minus = np.sum(alpha[:, np.newaxis] * vertices, axis=0)
        y_plus = np.sum(beta[:, np.newaxis] * vertices, axis=0)
        ends.append((y_minus, y_plus))
    return ends


def compute_center(vertices):
    """Центр тяжести симплекса (среднее арифметическое вершин)."""
    return np.mean(vertices, axis=0)


def compute_alpha_center(A_inv, vertices, alpha):
    """
    Вычисляет центр гомотетии x0 для α(S) по формуле (1.44).
    A_inv - обратная матрица A^{-1} размера (n+1)x(n+1),
    vertices - массив вершин (n+1, n),
    alpha - значение α(S).
    Возвращает массив длины n.
    """
    n = vertices.shape[1]
    # суммы модулей элементов в столбцах (по первым n строкам)
    s_j = np.sum(np.abs(A_inv[:n, :]), axis=0)  # вектор длины n+1
    sum_s = np.sum(s_j)  # = 2*alpha
    denominator = sum_s - 2  # = 2*alpha - 2
    if abs(denominator) < 1e-12:
        raise ValueError("Знаменатель близок к нулю: α(S) ≈ 1?")
    numerator = np.zeros(n)
    for k in range(n):
        # Σ_j s_j * x_k^{(j)} - 1
        numerator[k] = np.sum(s_j * vertices[:, k]) - 1
    x0 = numerator / denominator
    return x0
