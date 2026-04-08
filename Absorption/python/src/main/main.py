import sys
import time

from colorama import init, Fore, Style
from simplex import read_simplex, build_A, compute_inverse, compute_alpha, compute_xi, compute_axial_ends, \
    compute_center, compute_alpha_center
from visualization import plot_1d, plot_2d, plot_3d


def printCol(text, color):
    print(color + text + Style.RESET_ALL)


def error(text):
    printCol(text, Fore.RED)


def delimiter():
    printCol("*" * 100, Fore.YELLOW)


def main():
    if len(sys.argv) != 2:
        error("Использование: python main.py <файл_с_координатами>")
        sys.exit(1)

    init()

    start = time.perf_counter()

    filename = sys.argv[1]
    try:
        n, vertices = read_simplex(filename)
    except Exception as e:
        error(f"Ошибка чтения файла: {e}")
        sys.exit(1)

    delimiter()
    printCol(f"Размерность n = {n}", Fore.BLUE)
    printCol("Вершины:", Fore.CYAN)
    for i, v in enumerate(vertices):
        printCol(f"  x{i + 1} = ({', '.join(str(int(x) if x.is_integer() else x) for x in v)})", Fore.LIGHTCYAN_EX)
    delimiter()

    printCol("Строим матрицу A", Fore.BLUE)
    A = build_A(vertices)
    printCol("A:", Fore.CYAN)
    for row in A:
        row_str = "  " + " ".join(f"{x:10.3f}" for x in row)
        printCol(row_str, Fore.LIGHTCYAN_EX)
    delimiter()

    printCol("Ищем обратную матрицу для A", Fore.BLUE)
    A_inv = compute_inverse(A)
    printCol("A⁻¹:", Fore.CYAN)
    for row in A_inv:
        row_str = "  " + " ".join(f"{x:10.3f}" for x in row)
        printCol(row_str, Fore.LIGHTCYAN_EX)
    delimiter()

    printCol("Вычисляем α(S) и ξ(S)", Fore.BLUE)
    alpha = compute_alpha(A_inv, n)
    xi = compute_xi(A_inv, n)
    printCol(f"α(S) = {alpha}", Fore.GREEN)
    printCol(f"ξ(S) = {xi}", Fore.GREEN)
    delimiter()

    printCol("Находим осевые диаметры и центр тяжести", Fore.BLUE)
    axial_ends = compute_axial_ends(A_inv, vertices)
    center = compute_center(vertices)
    alpha_center = compute_alpha_center(A_inv, vertices, alpha)
    printCol(f"Центр тяжести: {center}", Fore.CYAN)
    delimiter()

    end = time.perf_counter()
    printCol(f"🕜  Программа отработала за {end - start:.6f} с", Fore.GREEN)
    delimiter()

    if n > 3:
        printCol("❎  Не могу визуализировать для размерности n > 3.", Fore.GREEN)
        sys.exit(0)

    printCol("✅  Визуализация доступна в новом окне.", Fore.GREEN)

    if n == 1:
        plot_1d(vertices, axial_ends, alpha, xi, alpha_center)
    elif n == 2:
        plot_2d(vertices, axial_ends, alpha, xi, alpha_center)
    elif n == 3:
        plot_3d(vertices, axial_ends, alpha, xi, alpha_center)

if __name__ == "__main__":
    main()
