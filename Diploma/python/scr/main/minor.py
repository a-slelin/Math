import matplotlib
import numpy as np
import matplotlib.pyplot as plt


# Функция правой части уравнения: dx/dt = -x + a*dx(t-T) + b*dx(t-H) + f2*x^2 + f3*x^3
# noinspection PyPep8Naming,PyUnusedLocal
def F(t_val, x_val, dx_T, dx_H):
    return -x_val + a * dx_T + b * dx_H + f2 * x_val ** 2 + f3 * x_val ** 3


# Линейная интерполяция для истории
def interpolate(t_target, t_array, y_array):
    idx = np.searchsorted(t_array, t_target) - 1
    if idx < 0:
        return y_array[0]
    if idx >= len(y_array) - 1:
        return y_array[-1]
    frac = (t_target - t_array[idx]) / (t_array[idx + 1] - t_array[idx])
    return y_array[idx] + frac * (y_array[idx + 1] - y_array[idx])


if __name__ == '__main__':
    matplotlib.use('TkAgg')

    plt.figure(figsize=(12, 8))

    # Параметры
    T = 5  # Первое запаздывание
    H = 1  # Второе запаздывание
    omega = 8.192419118  # Специально подобранное значение
    eps = 0.001

    a = ((np.cos(omega * H) / omega - np.sin(omega * H))
         / np.sin(omega * (T - H)))  # a < 0
    b = ((np.sin(omega * T) - np.cos(omega * T) / omega)
         / np.sin(omega * (T - H)))  # -a + |b| = 1
    print('Параметры:')
    print(f'\ta = {a:.10f}')
    print(f'\tb = {b:.10f}')

    f2 = 9.0
    f3 = -379.0

    i = 0 + 1j

    beta = 2 * f2
    alpha = f2 / (1 + 2 * i * omega
                  - a * 2 * i * omega * np.exp(-2 * i * omega * T)
                  - b * 2 * i * omega * np.exp(-2 * i * omega * H))

    e_T = np.exp(-i * omega * T)
    e_H = np.exp(-i * omega * H)
    delimiter = (1 - a * e_T
                 + a * T * i * omega * e_T
                 - b * e_H
                 + b * H * i * omega * e_H)
    real_lambda = np.real((-i * omega * e_T) / delimiter)
    real_sigma = np.real((2 * f2 * beta + 2 * f2 * alpha + 3 * f3) / delimiter)
    rho = np.sqrt(-real_lambda / real_sigma)  # real_lambda * real_sigma < 0
    print(f'\tRe(lambda) = {real_lambda:.10f}')
    print(f'\tRe(sigma) = {real_sigma:.10f}')
    # noinspection PyStringConversionWithoutDunderMethod
    print(f'\trho = {rho:.10f}')

    t_end = 1000.0
    phi = np.linspace(0, t_end, int(t_end / 0.01) + 1)

    plt.plot(
        phi,
        np.sqrt(eps) * 2 * rho * np.cos(omega * phi),
        color='black',
        linestyle='--',
        label=rf'$x(t) = -\sqrt{{\varepsilon}} \cdot 2 \cdot \rho^* \cdot \cos{{(\omega t)}} + o(\sqrt{{\varepsilon}})$',
    )

    # noinspection PyShadowingNames
    initial_conditions = [
        lambda t: np.sqrt(eps) * 2 * rho * np.cos(omega * t),
        lambda t: -np.sqrt(eps) * 2 * rho * np.cos(omega * t),
        lambda t: -0.05,
        lambda t: 0.05
    ]

    # Параметры интегрирования
    h = 0.01  # Шаг времени
    num_steps = int(t_end / h) + 1
    N_T = int(T / h)  # Число шагов запаздывания T
    N_H = int(H / h)  # Число шагов запаздывания H

    # Создание массивов времени: от -T до t_end
    t = np.arange(-T, t_end + h, h)
    total_points = len(t)

    for ic_idx, phi in enumerate(initial_conditions):
        # Инициализация массивов
        x = np.zeros(total_points)
        dx = np.zeros(total_points)

        # Заполнение истории (t < 0)
        for i in range(total_points):
            if t[i] <= 0:
                x[i] = phi(t[i])

                if ic_idx == 0:
                    dx[i] = -omega * np.sqrt(eps) * 2 * rho * np.sin(omega * t[i])
                elif ic_idx == 1:
                    dx[i] = omega * np.sqrt(eps) * 2 * rho * np.sin(omega * t[i])
                else:  # Константы
                    dx[i] = 0

        # Интегрирование методом Рунге-Кутты 4-го порядка
        for i in range(N_T, total_points - 1):
            t_i = t[i]
            x_i = x[i]

            # k1: значения в t_i - T и t_i - H
            t_T_del1 = t_i - T
            t_H_del1 = t_i - H
            dx_T1 = interpolate(t_T_del1, t[: i + 1], dx[: i + 1])
            dx_H1 = interpolate(t_H_del1, t[: i + 1], dx[: i + 1])
            k1 = h * F(t_i, x_i, dx_T1, dx_H1)

            # k2: значения в t_i + h/2
            t2 = t_i + h / 2
            x2 = x_i + k1 / 2
            t_T_del2 = t2 - T
            t_H_del2 = t2 - H
            dx_T2 = interpolate(t_T_del2, t[: i + 1], dx[: i + 1])
            dx_H2 = interpolate(t_H_del2, t[: i + 1], dx[: i + 1])
            k2 = h * F(t2, x2, dx_T2, dx_H2)

            # k3: те же запаздывающие значения, что для k2
            x3 = x_i + k2 / 2
            k3 = h * F(t2, x3, dx_T2, dx_H2)

            # k4: значения в t_i + h
            t4 = t_i + h
            x4 = x_i + k3
            t_T_del4 = t4 - T
            t_H_del4 = t4 - H
            dx_T4 = interpolate(t_T_del4, t[: i + 1], dx[: i + 1])
            dx_H4 = interpolate(t_H_del4, t[: i + 1], dx[: i + 1])
            k4 = h * F(t4, x4, dx_T4, dx_H4)

            # Обновление x[i+1]
            x[i + 1] = x_i + (k1 + 2 * k2 + 2 * k3 + k4) / 6

            # Обновление производной dx[i+1]
            t_next = t[i + 1]
            t_T_next = t_next - T
            t_H_next = t_next - H
            dx_T_next = interpolate(t_T_next, t[: i + 2], dx[: i + 2])
            dx_H_next = interpolate(t_H_next, t[: i + 2], dx[: i + 2])
            dx[i + 1] = F(t_next, x[i + 1], dx_T_next, dx_H_next)

        # Построение решения
        plt.plot(t[N_T:], x[N_T:])

    # Визуализация
    plt.xlabel('t', fontsize=26)
    plt.ylabel('x', fontsize=26, rotation=0)
    plt.tick_params(axis='both', which='major', labelsize=18)
    plt.grid(True)
    plt.legend(fontsize=20)
    plt.show()
