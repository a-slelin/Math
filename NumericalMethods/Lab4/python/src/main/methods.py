import numpy as np
from const import semi_x, semi_y, ellipse, tolerance, eps, max_iterations

# Типы узлов сетки
OUTSIDE = 0     # узел снаружи области — в расчёте не участвует
ON_BOUNDARY = 1 # узел лежит прямо на границе Г — значение известно сразу: u = phi
NEAR = 2        # приграничный узел: внутри D, но хотя бы один сосед снаружи
INTERIOR = 3    # внутренний узел: все четыре соседа внутри D (или на Г)


# ---------------------------------------------------------------------------
# Шаг 1. Минимальный прямоугольник, содержащий эллипс, и сетка на нём.
#
# Эллипс x²/16 + y²/25 = 1 помещается в прямоугольник [-4, 4] x [-5, 5].
# Покрываем его сеткой с шагом h: x_k = -4 + k*h,  y_j = -5 + j*h.
# ---------------------------------------------------------------------------
def make_grid(h):
    nx = int(round(2 * semi_x / h))
    ny = int(round(2 * semi_y / h))
    x = np.linspace(-semi_x, semi_x, nx + 1)
    y = np.linspace(-semi_y, semi_y, ny + 1)
    return x, y


# Лежит ли точка в замкнутой области D + Г (внутри или на границе)
def in_domain(x, y):
    return ellipse(x, y) <= 1 + tolerance


# ---------------------------------------------------------------------------
# Шаг 2. Определяем тип каждого узла.
# Массив types[j, k] хранит тип узла с координатами (x_k, y_j).
# ---------------------------------------------------------------------------
def classify_nodes(x, y, h):
    types = np.full((len(y), len(x)), OUTSIDE)

    for j in range(len(y)):
        for k in range(len(x)):
            xk, yj = x[k], y[j]

            # Узел снаружи — пропускаем
            if not in_domain(xk, yj):
                continue

            # Узел прямо на эллипсе
            if abs(ellipse(xk, yj) - 1) <= tolerance:
                types[j, k] = ON_BOUNDARY
                continue

            # Проверяем четырёх соседей "крестом": слева, справа, снизу, сверху
            neighbours = [(xk - h, yj), (xk + h, yj), (xk, yj - h), (xk, yj + h)]
            if all(in_domain(nx_, ny_) for nx_, ny_ in neighbours):
                types[j, k] = INTERIOR
            else:
                types[j, k] = NEAR

    return types


# ---------------------------------------------------------------------------
# Шаг 3. Аппроксимация граничного условия в приграничном узле A (как в методичке).
#
# Пусть сосед A в каком-то направлении оказался снаружи. Тогда на отрезке
# между A и этим соседом лежит точка B на границе Г, на расстоянии delta < h от A.
# С другой стороны от A, на расстоянии h, лежит соседний узел C.
#
#        C ------- h ------- A --- delta --- B (на эллипсе)
#
# Линейная интерполяция между C и B даёт (формула из методички, погрешность O(h²)):
#
#     u(A) = (h * phi(B) + delta * u(C)) / (h + delta).
#
# Направление выбираем то, где delta меньше всего (там точность выше).
# Функция возвращает: delta, точку B и индексы узла C (или None, если C тоже снаружи).
# ---------------------------------------------------------------------------
def boundary_stencil(x, y, j, k, h):
    xk, yj = x[k], y[j]
    best = None

    # Направления (dx, dy): влево, вправо, вниз, вверх
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        # Нас интересуют только направления, где сосед вне области
        if in_domain(xk + dx * h, yj + dy * h):
            continue

        # Ищем точку B на эллипсе на этой линии сетки
        if dx != 0:
            # Горизонтальная линия y = yj: эллипс пересекает её при x = ±4*sqrt(1 - y²/25)
            xb = dx * semi_x * np.sqrt(max(0.0, 1 - yj ** 2 / semi_y ** 2))
            point_b = (xb, yj)
            delta = abs(xb - xk)
        else:
            # Вертикальная линия x = xk: эллипс пересекает её при y = ±5*sqrt(1 - x²/16)
            yb = dy * semi_y * np.sqrt(max(0.0, 1 - xk ** 2 / semi_x ** 2))
            point_b = (xk, yb)
            delta = abs(yb - yj)

        # Узел C — сосед с противоположной стороны (если он в области)
        jc, kc = j - dy, k - dx
        c_inside = 0 <= jc < len(y) and 0 <= kc < len(x) and in_domain(x[kc], y[jc])
        node_c = (jc, kc) if c_inside else None

        if best is None or delta < best[0]:
            best = (delta, point_b, node_c)

    return best


# ---------------------------------------------------------------------------
# Шаг 4. Решаем разностную систему итерационным методом.
#
# Во внутреннем узле уравнение Лапласа заменяем пятиточечным "крестом"
# (h1 = h2 = h, поэтому формула совсем простая):
#
#     u_(k,j) = (u_(k-1,j) + u_(k+1,j) + u_(k,j-1) + u_(k,j+1)) / 4.
#
# В приграничном узле — формула интерполяции из шага 3.
#
# Метод Зейделя: обходим узлы по очереди и сразу подставляем новое значение,
# используя уже обновлённые значения соседей. Чтобы сходилось быстрее, используем
# верхнюю релаксацию (вариант метода Зейделя):
#
#     u_new = u_old + omega * (u_Зейделя - u_old),   1 <= omega < 2.
#
# При omega = 1 получается обычный метод Зейделя. Релаксацию применяем только
# во внутренних узлах, а приграничные узлы считаем обычным Зейделем —
# иначе при omega, близком к 2, итерации перестают сходиться.
# ---------------------------------------------------------------------------
def solve_dirichlet(x, y, h, boundary_value, omega=None):
    types = classify_nodes(x, y, h)

    # Начальное приближение — нули; на границе сразу ставим известные значения
    u = np.zeros((len(y), len(x)))
    for j, k in zip(*np.nonzero(types == ON_BOUNDARY)):
        u[j, k] = boundary_value(x[k], y[j])

    # Для каждого приграничного узла заранее считаем, откуда брать значения:
    # (j, k, delta, phi(B), узел C)
    near_nodes = []
    for j, k in zip(*np.nonzero(types == NEAR)):
        delta, point_b, node_c = boundary_stencil(x, y, j, k, h)
        near_nodes.append((j, k, delta, boundary_value(*point_b), node_c))

    interior_nodes = list(zip(*np.nonzero(types == INTERIOR)))

    # Оптимальный параметр релаксации для прямоугольника с N шагами по стороне:
    #     omega = 2 / (1 + sin(π / N)).
    # Берём N по большей стороне прямоугольника — для эллипса это хорошая оценка.
    if omega is None:
        n_steps = max(len(x), len(y)) - 1
        omega = 2 / (1 + np.sin(np.pi / n_steps))

    # Здесь запоминаем, насколько менялось решение на каждой итерации
    history = []

    for iteration in range(1, max_iterations + 1):
        biggest_change = 0.0

        # Приграничные узлы: интерполяция между границей и соседом C
        for j, k, delta, phi_b, node_c in near_nodes:
            if node_c is None:
                # Совсем узкое место: соседа C нет, просто переносим значение с границы
                new_value = phi_b
            else:
                new_value = (h * phi_b + delta * u[node_c]) / (h + delta)
            # Здесь релаксацию не применяем (просто Зейдель): эти узлы не "усредняют"
            # соседей, и ускорение в них только раскачивает итерации
            change = new_value - u[j, k]
            u[j, k] = new_value
            biggest_change = max(biggest_change, abs(change))

        # Внутренние узлы: среднее четырёх соседей (пятиточечный "крест")
        for j, k in interior_nodes:
            new_value = (u[j, k - 1] + u[j, k + 1] + u[j - 1, k] + u[j + 1, k]) / 4
            change = new_value - u[j, k]
            u[j, k] += omega * change
            biggest_change = max(biggest_change, abs(change))

        history.append(biggest_change)
        if biggest_change < eps:
            break

    # Узлы снаружи области отмечаем как "нет значения" (NaN), чтобы их не рисовать
    u[types == OUTSIDE] = np.nan

    return u, types, history, omega
