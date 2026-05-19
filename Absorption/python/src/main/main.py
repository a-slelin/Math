import sys
import time

from colorama import init, Fore, Style
from simplex import read_simplex, build_A, compute_inverse, compute_alpha, compute_xi, compute_axial_ends, \
    compute_center, compute_alpha_center
from visualization import plot_1d, plot_2d, plot_3d


def print_col(text, color):
    print(color + text + Style.RESET_ALL)


def error(text):
    print_col(text, Fore.RED)


def delimiter():
    print_col('*' * 100, Fore.YELLOW)


def main():
    if len(sys.argv) != 2:
        error('Использование: python main.py <файл_с_координатами>')
        sys.exit(1)

    init()

    start = time.perf_counter()

    filename = sys.argv[1]
    try:
        n, vertices = read_simplex(filename)
    except Exception as e:
        error(f'Ошибка чтения файла: {e}')
        sys.exit(1)

    delimiter()
    print_col(f'Размерность n = {n}', Fore.BLUE)
    print_col('Вершины:', Fore.CYAN)
    for i, v in enumerate(vertices):
        print_col(f'  x{i + 1} = ({', '.join(str(int(x) if x.is_integer() else x) for x in v)})', Fore.LIGHTCYAN_EX)
    delimiter()

    print_col('Строим матрицу A', Fore.BLUE)
    # noinspection PyPep8Naming
    A = build_A(vertices)
    print_col('A:', Fore.CYAN)
    for row in A:
        row_str = '  ' + ' '.join(f'{x:10.3f}' for x in row)
        print_col(row_str, Fore.LIGHTCYAN_EX)
    delimiter()

    print_col('Ищем обратную матрицу для A', Fore.BLUE)
    # noinspection PyPep8Naming
    A_inv = compute_inverse(A)
    print_col('A⁻¹:', Fore.CYAN)
    for row in A_inv:
        row_str = '  ' + ' '.join(f'{x:10.3f}' for x in row)
        print_col(row_str, Fore.LIGHTCYAN_EX)
    delimiter()

    print_col('Вычисляем α(S) и ξ(S)', Fore.BLUE)
    alpha = compute_alpha(A_inv, n)
    xi = compute_xi(A_inv, n)
    print_col(f'α(S) = {alpha}', Fore.GREEN)
    print_col(f'ξ(S) = {xi}', Fore.GREEN)
    delimiter()

    print_col('Находим осевые диаметры и центр тяжести', Fore.BLUE)
    axial_ends = compute_axial_ends(A_inv, vertices)
    center = compute_center(vertices)
    alpha_center = compute_alpha_center(A_inv, vertices)
    print_col(f'Центр тяжести: {center}', Fore.CYAN)
    delimiter()

    end = time.perf_counter()
    print_col(f'🕜  Программа отработала за {end - start:.6f} с', Fore.GREEN)
    delimiter()

    if n > 3:
        print_col('❎  Не могу визуализировать для размерности n > 3.', Fore.GREEN)
        sys.exit(0)

    print_col('✅  Визуализация доступна в новом окне.', Fore.GREEN)

    if n == 1:
        plot_1d(vertices, axial_ends, alpha, xi, alpha_center)
    elif n == 2:
        plot_2d(vertices, axial_ends, alpha, xi, alpha_center)
    elif n == 3:
        plot_3d(vertices, axial_ends, alpha, xi, alpha_center)


if __name__ == '__main__':
    main()
