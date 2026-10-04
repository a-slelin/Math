import numpy as np
from const import n, m, t0, fourier_terms, exact
from draw import plot_solutions, plot_errors, plot_heatmap
from methods import SCHEMES, solve_heat, fourier_solution, get_sigma
from solvers import SOLVERS


# Главная функция: решаем задачу тремя разностными схемами и методом Фурье,
# затем сравниваем всё с точным решением
def main():
    print('Уравнение теплопроводности (вариант 13):')
    print('  u_t = u_xx + (1 - t)*e^(-x),   u(x, 0) = 0,   u(0, t) = t,   u(1, t) = t/e')
    h, tau = 1 / n, t0 / m
    print(f'  n = {n}, m = {m}, t0 = {t0:g}   ->   h = {h:g}, tau = {tau:g}\n')

    # Шаг 1. Решаем тремя разностными схемами (система на каждом слое — правой прогонкой)
    final_layers = {}
    layers = {}
    for scheme in SCHEMES:
        x, t, u = solve_heat(scheme, n, m, t0)
        final_layers[scheme] = u[-1]
        layers[scheme] = u
        print(f'{scheme:<28} sigma = {get_sigma(scheme, h, tau):.6f}')

    # Шаг 2. Метод Фурье: ряд до третьего члена
    fourier = fourier_solution(x, t0, fourier_terms)

    # Шаг 3. Таблица значений в узлах x_i при t = t0
    u_exact = exact(x, t0)
    names = ['Неявная', 'Кранк–Никольсон', 'Повыш. порядок', 'Фурье (3 чл.)']
    header = f'{"i":>3} {"x_i":>6} {"точное":>12}' + ''.join(f'{name:>17}' for name in names)
    print(f'\nРешение при t = t0 = {t0:g}:')
    print(header)
    print('-' * len(header))
    for i in range(n + 1):
        row = f'{i:>3} {x[i]:>6.2f} {u_exact[i]:>12.8f}'
        row += ''.join(f'{final_layers[s][i]:>17.8f}' for s in SCHEMES)
        row += f'{fourier[i]:>17.8f}'
        print(row)

    # Шаг 4. Максимальные ошибки
    print('\nМаксимальная ошибка |u_прибл - u_точн| при t = t0:')
    for scheme in SCHEMES:
        print(f'  {scheme:<28} {np.max(np.abs(final_layers[scheme] - u_exact)):.3e}')
    print(f'  {"Метод Фурье (3 члена)":<28} {np.max(np.abs(fourier - u_exact)):.3e}')

    # Шаг 5. Проверяем, что все четыре метода решения сеточной задачи дают одно и то же
    print('\nРасхождение методов решения сеточной задачи с правой прогонкой (схема Кранка – Никольсона):')
    base = layers['Схема Кранка – Никольсона'][-1]
    for name, solver in SOLVERS.items():
        _, _, u = solve_heat('Схема Кранка – Никольсона', n, m, t0, solver)
        print(f'  {name:<20} {np.max(np.abs(u[-1] - base)):.3e}')

    # Шаг 6. Графики
    plot_solutions(x, t0, final_layers, fourier)
    plot_errors(x, t0, final_layers, fourier)
    plot_heatmap(x, t, layers['Схема Кранка – Никольсона'])


if __name__ == '__main__':
    main()
