import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


def plot_1d(vertices, axial_ends, alpha, xi, alpha_center):
    """1D график с S, осевым диаметром, α(S)S и ξ(S)S."""
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.grid(True)

    # Границы куба Q1 = [0,1]
    ax.axvline(0, color='k', linestyle='--', alpha=0.5)
    ax.axvline(1, color='k', linestyle='--', alpha=0.5)

    # Отрезок S
    x1, x2 = vertices.flatten()
    ax.plot([x1, x2], [0, 0], 'b-', linewidth=4, label='S')
    ax.plot(x1, 0, 'bo')
    ax.plot(x2, 0, 'bo')

    # Осевой диаметр (совпадает с S, чуть выше)
    y_minus, y_plus = axial_ends[0]
    ax.plot([y_minus[0], y_plus[0]], [0.1, 0.1], 'r-', linewidth=2, label='Осевой диаметр')

    # Гомотетичный образ α(S)S
    center = np.mean(vertices, axis=0)
    scaled_alpha = alpha_center + alpha * (vertices - alpha_center)
    xa1, xa2 = scaled_alpha.flatten()
    ax.plot([xa1, xa2], [-0.2, -0.2], 'orange', linestyle=':', linewidth=2, label='α(S)S')
    ax.plot(xa1, -0.2, 'o', color='orange')
    ax.plot(xa2, -0.2, 'o', color='orange')

    # Гомотетичный образ ξ(S)S
    scaled_xi = center + xi * (vertices - center)
    xs1, xs2 = scaled_xi.flatten()
    ax.plot([xs1, xs2], [-0.1, -0.1], 'g--', linewidth=2, label='ξ(S)S')
    ax.plot(xs1, -0.1, 'go')
    ax.plot(xs2, -0.1, 'go')

    ax.set_yticks([])
    ax.set_xlabel('x')
    ax.set_title(f'α(S) = {alpha:.6f}, ξ(S) = {xi:.6f}', fontsize=20)
    ax.legend()
    plt.show()


def plot_2d(vertices, axial_ends, alpha, xi, alpha_center):
    """2D график с Q₂, S, осевыми диаметрами, α(S)S и ξ(S)S."""
    fig, ax = plt.subplots()
    ax.grid(True)

    # Квадрат
    square = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
    ax.plot(square[:, 0], square[:, 1], 'k-', lw=1, label='Q₂')

    # Симплекс (треугольник)
    tri = np.vstack([vertices, vertices[0]])
    ax.plot(tri[:, 0], tri[:, 1], 'b-', lw=2, label='S')

    # Осевые диаметры
    for i, (ym, yp) in enumerate(axial_ends):
        ax.plot([ym[0], yp[0]], [ym[1], yp[1]], 'r-', lw=2, label='Осевые диаметры' if i == 0 else '')

    # Гомотетичный образ α(S)S
    center = np.mean(vertices, axis=0)
    scaled_alpha = alpha_center + alpha * (vertices - alpha_center)
    scaled_alpha = np.vstack([scaled_alpha, scaled_alpha[0]])
    ax.plot(scaled_alpha[:, 0], scaled_alpha[:, 1], 'orange', linestyle=':', lw=2, label=f'α(S)S')

    # Гомотетичный образ ξ(S)S
    scaled_xi = center + xi * (vertices - center)
    scaled_xi = np.vstack([scaled_xi, scaled_xi[0]])
    ax.plot(scaled_xi[:, 0], scaled_xi[:, 1], 'g--', lw=2, label='ξ(S)S')

    ax.set_aspect('equal')
    ax.set_title(f'α(S) = {alpha:.6f}, ξ(S) = {xi:.6f}', fontsize=20)
    ax.legend()
    plt.show()


def plot_3d(vertices, axial_ends, alpha, xi, alpha_center):
    """3D график с кубом Q₃, тетраэдром, осевыми диаметрами, α(S)S и ξ(S)S."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Вершины куба [0,1]^3
    cube_vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                              [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
    # Рёбра куба
    edges = [(0, 1), (1, 2), (2, 3), (3, 0),  # нижняя грань
             (4, 5), (5, 6), (6, 7), (7, 4),  # верхняя грань
             (0, 4), (1, 5), (2, 6), (3, 7)]  # вертикальные

    for e in edges:
        ax.plot3D(*zip(cube_vertices[e[0]], cube_vertices[e[1]]), color='k', linewidth=0.5,
                  label='Q₃' if e == (0, 1) else '')

    # Тетраэдр (грани)
    faces = [
        [vertices[0], vertices[1], vertices[2]],
        [vertices[0], vertices[1], vertices[3]],
        [vertices[0], vertices[2], vertices[3]],
        [vertices[1], vertices[2], vertices[3]]
    ]
    ax.add_collection3d(Poly3DCollection(faces, alpha=0.2, facecolor='cyan', linewidths=1, edgecolor='b', label='S'))

    # Осевые диаметры
    for i, (ym, yp) in enumerate(axial_ends):
        ax.plot3D(*zip(ym, yp), color='r', linewidth=2, label='Осевые диаметры' if i == 0 else '')

    # Гомотетичный образ α(S)S (контур)
    center = np.mean(vertices, axis=0)
    scaled_alpha = alpha_center + alpha * (vertices - alpha_center)
    alpha_edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    tmp = 0
    for e in alpha_edges:
        ax.plot3D(*zip(scaled_alpha[e[0]], scaled_alpha[e[1]]), color='orange', linestyle=':', linewidth=2,
                  label='α(S)S' if tmp == 0 else '')
        tmp += 1

    # Гомотетичный образ ξ(S)S (контур)
    scaled_xi = center + xi * (vertices - center)
    tmp = 0
    for e in alpha_edges:
        ax.plot3D(*zip(scaled_xi[e[0]], scaled_xi[e[1]]), color='g', linestyle='--', linewidth=2,
                  label='ξ(S)S' if tmp == 0 else '')
        tmp += 1

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'α(S) = {alpha:.6f}, ξ(S) = {xi:.6f}', fontsize=20)
    ax.legend()
    plt.show()
