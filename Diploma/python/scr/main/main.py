import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Polygon

eps = 10 ** -3


# Построение основной кривой
# noinspection PyPep8Naming,PyShadowingNames
def get_general_line(h, T, H, W):
    # noinspection PyShadowingNames
    def a(w):
        return (np.cos(w * H) / w - np.sin(w * H)) / np.sin(w * (T - H))

    # noinspection PyShadowingNames
    def b(w):
        return (np.sin(w * T) - np.cos(w * T) / w) / np.sin(w * (T - H))

    segments, current_segment = [], []

    for i in range(1, W + 1):
        w = i * h

        if abs(np.sin(w * (T - H))) <= eps:
            segments.append(current_segment)
            current_segment = []
            continue

        current_segment.append((a(w), b(w)))

    return segments


if __name__ == '__main__':
    matplotlib.use('TkAgg')

    # Настройка отображения matplotlib
    a_limit, b_limit = -1.5, 1.5

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.grid()
    ax.set_xlabel('a', fontsize=26)
    ax.set_ylabel('b', fontsize=26, rotation=0)
    ax.set_ylim(-a_limit, a_limit)
    ax.set_xlim(-b_limit, b_limit)
    ax.tick_params(axis='both', which='major', labelsize=18)

    # Параметры
    T = 5  # Запаздывание
    H = 1  # Второе запаздывание
    W = 10 ** 6  # Количество точек
    h = 10 ** -4  # Шаг

    # Отрисовка основной кривой
    segments = get_general_line(h, T, H, W)
    for seg in segments:
        if len(seg) > 1:
            A = [p[0] for p in seg]
            B = [p[1] for p in seg]
            ax.plot(A, B, color='blue')

    legend_elements = [
        Patch(facecolor='lightgreen', edgecolor='black', label='$D_0$'),
        plt.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='red',
                      hatch='///', label='Устойчивая область')
    ]

    legend = ax.legend(handles=legend_elements, loc='upper left', fontsize=20)
    ax.add_artist(legend)

    # Вершины ромба
    verts = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    # Сплошная зелёная заливка
    romb_fill = Polygon(verts, closed=True, facecolor='lightgreen', edgecolor='none', alpha=0.7)
    ax.add_patch(romb_fill)

    # Поверх – красная штриховка и красная граница
    romb_hatch = Polygon(verts, closed=True, edgecolor='red', facecolor='none',
                         hatch='///', linewidth=2)
    ax.add_patch(romb_hatch)

    plt.show()
