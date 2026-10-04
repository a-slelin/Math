import numpy as np
from const import n, exact
from draw import plot_solutions, plot_errors, plot_convergence
from methods import build_grid_problem, right_sweep, METHODS


# Главная функция: строим сеточную задачу, решаем её четырьмя методами
# и сравниваем с точным решением
def main():
    print("Краевая задача (вариант 13):")
    print("  y'' + 2y' - 3y = e^x,   y(0) = 0,   y'(1) = 1,   n = 20\n")

    # Шаг 1. Строим сеточную задачу
    x, d, e, g, chi1, mu1, chi2, mu2 = build_grid_problem(n)
    print(f'Коэффициенты: d = {d[1]:.4f}, e = {e[1]:.4f}')
    print(f'Краевые условия: y_0 = {chi1 + 0:g}*y_1 + {mu1 + 0:g},   y_n = {chi2 + 0:g}*y_(n-1) + {mu2 + 0:g}\n')

    # Шаг 2. Решаем всеми четырьмя методами
    solutions = {}
    for name, method in METHODS.items():
        solutions[name] = method(d, e, g, chi1, mu1, chi2, mu2)

    # Шаг 3. Печатаем таблицу: точное и приближённое решение в узлах x_i
    # (так требует методичка при сдаче работы)
    y_exact = exact(x)
    header = f'{"i":>3} {"x_i":>6} {"точное":>12}' + ''.join(f'{name:>20}' for name in solutions)
    print(header)
    print('-' * len(header))
    for i in range(n + 1):
        row = f'{i:>3} {x[i]:>6.2f} {y_exact[i]:>12.6f}'
        row += ''.join(f'{y[i]:>20.6f}' for y in solutions.values())
        print(row)

    # Шаг 4. Ошибки методов
    print('\nМаксимальная ошибка |y_числ - y_точн|:')
    for name, y in solutions.items():
        print(f'  {name:<20} {np.max(np.abs(y - y_exact)):.6e}')

    # Все методы решают одну и ту же систему, поэтому должны совпасть между собой
    base = solutions['Правая прогонка']
    biggest = max(np.max(np.abs(y - base)) for y in solutions.values())
    print(f'\nНаибольшее расхождение между методами: {biggest:.3e}')

    # Шаг 5. Проверяем, как уменьшается ошибка с ростом n
    ns = [10, 20, 40, 80, 160, 320, 640]
    errors = []
    print('\nСходимость (правая прогонка):')
    print(f'{"n":>5} {"h":>10} {"ошибка":>14} {"ошибка/h":>10}')
    for count in ns:
        xs, d_, e_, g_, c1, m1, c2, m2 = build_grid_problem(count)
        error = np.max(np.abs(right_sweep(d_, e_, g_, c1, m1, c2, m2) - exact(xs)))
        errors.append(error)
        print(f'{count:>5} {1 / count:>10.5f} {error:>14.6e} {error * count:>10.4f}')

    # Шаг 6. Графики
    plot_solutions(x, solutions)
    plot_errors(x, solutions)
    plot_convergence(ns, np.array(errors))


if __name__ == '__main__':
    main()
