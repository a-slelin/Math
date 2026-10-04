import time

import numpy as np
from const import h, phi, semi_x, semi_y
from draw import plot_grid, plot_solution_map, plot_solution_surface, plot_iterations, plot_test_convergence
from methods import make_grid, solve_dirichlet, OUTSIDE, ON_BOUNDARY, NEAR, INTERIOR


# Тестовая гармоническая функция: (x² − y²)'' по x плюс по y = 2 − 2 = 0.
# Для неё точное решение задачи Дирихле известно — это она сама.
def harmonic_test(x, y):
    return x ** 2 - y ** 2


# Главная функция: строим сетку, решаем задачу Дирихле и проверяем метод
def main():
    print('Задача Дирихле для уравнения Лапласа (вариант 10):')
    print('  u_xx + u_yy = 0   в эллипсе x²/16 + y²/25 < 1,   u|Г = |x|·|y|\n')

    # Шаг 1. Сетка на минимальном прямоугольнике [-4, 4] x [-5, 5]
    x, y = make_grid(h)
    print(f'Минимальный прямоугольник: [{-semi_x:g}, {semi_x:g}] x [{-semi_y:g}, {semi_y:g}],  h1 = h2 = {h}')
    print(f'Сетка: {len(x)} x {len(y)} узлов\n')

    # Шаги 2–4. Классификация узлов, граничные значения и итерации
    start = time.perf_counter()
    u, types, history, omega = solve_dirichlet(x, y, h, phi)
    elapsed = time.perf_counter() - start

    print('Типы узлов:')
    print(f'  внутренние (уравнение "крест"):         {np.sum(types == INTERIOR)}')
    print(f'  приграничные (интерполяция к границе):  {np.sum(types == NEAR)}')
    print(f'  лежат прямо на границе:                 {np.sum(types == ON_BOUNDARY)}')
    print(f'  снаружи (не участвуют):                 {np.sum(types == OUTSIDE)}\n')
    print(f'Метод верхней релаксации (omega = {omega:.4f}): {len(history)} итераций, {elapsed:.1f} с\n')

    # Печатаем решение в узлах с целыми координатами (весь массив слишком большой)
    print('Решение u(x, y) в узлах с целыми координатами ("·" — точка вне области):')
    whole_x = np.arange(-4, 5)
    whole_y = np.arange(5, -6, -1)
    print('  y \\ x ' + ''.join(f'{v:>8}' for v in whole_x))
    for yv in whole_y:
        j = int(round((yv + semi_y) / h))
        row = f'{yv:>6}  '
        for xv in whole_x:
            k = int(round((xv + semi_x) / h))
            row += f'{"·":>8}' if np.isnan(u[j, k]) else f'{u[j, k]:>8.3f}'
        print(row)

    # Проверка 1. Сравниваем обычный метод Зейделя и верхнюю релаксацию (на сетке h = 0.2, чтобы было быстро)
    print('\nСравнение итерационных методов на сетке h = 0.2:')
    x2, y2 = make_grid(0.2)
    _, _, history_seidel, _ = solve_dirichlet(x2, y2, 0.2, phi, omega=1.0)
    _, _, history_sor, omega2 = solve_dirichlet(x2, y2, 0.2, phi)
    print(f'  метод Зейделя (omega = 1):                {len(history_seidel)} итераций')
    print(f'  верхняя релаксация (omega = {omega2:.4f}):    {len(history_sor)} итераций')

    # Проверка 2. Тестовая задача с известным решением u = x² − y² на разных сетках
    print('\nПроверка метода на тестовой задаче u|Г = x² − y² (точное решение u = x² − y²):')
    print(f'{"h":>6} {"ошибка":>12} {"отношение":>10}')
    steps, errors = [0.4, 0.2, 0.1], []
    for step in steps:
        xt, yt = make_grid(step)
        ut, _, _, _ = solve_dirichlet(xt, yt, step, harmonic_test)
        X, Y = np.meshgrid(xt, yt)
        errors.append(np.nanmax(np.abs(ut - harmonic_test(X, Y))))
        ratio = '' if len(errors) == 1 else f'{errors[-2] / errors[-1]:>10.2f}'
        print(f'{step:>6} {errors[-1]:>12.6f} {ratio}')

    # Графики
    plot_grid(x, y, types)
    plot_solution_map(x, y, u)
    plot_solution_surface(x, y, u)
    plot_iterations({'Метод Зейделя': history_seidel, f'Верхняя релаксация, ω = {omega2:.3f}': history_sor})
    plot_test_convergence(steps, errors)


if __name__ == '__main__':
    main()
