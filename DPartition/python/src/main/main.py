import sys
import time

import matplotlib.pyplot as plt
import numpy as np
from colorama import init, Fore, Style

from const import EPS, A, EPS_LIST, A1_LIM, A2_LIM, GRID_SIZE, RESULTS_DIR
from draw import plot_partition, plot_eps_evolution
from equation import d_curve, guaranteed_radius
from partition import (d_curve_branches, singular_lines, count_unstable_roots, stable_mask_limit,
                       omega_max, DELTA_ZERO_STEP)


def print_col(text, color):
    print(color + text + Style.RESET_ALL)


def error(text):
    print_col(text, Fore.RED)


def delimiter():
    print_col('*' * 100, Fore.YELLOW)


def read_args():
    """Необязательные аргументы: python main.py [ε] [A]."""
    try:
        eps = float(sys.argv[1]) if len(sys.argv) > 1 else EPS
        a = float(sys.argv[2]) if len(sys.argv) > 2 else A
    except ValueError:
        error('Использование: python main.py [ε] [A], где ε ∈ (0, 1]')
        sys.exit(1)

    if not 0 < eps <= 1:
        error('Параметр ε должен лежать в (0, 1] (случай ε = 0 строится на сравнительном графике)')
        sys.exit(1)
    return eps, a


def stability_mask(eps, a, a1_mesh, a2_mesh):
    """Маска устойчивости на сетке (для ε = 0 — отдельный критерий)."""
    if eps == 0:
        return stable_mask_limit(a1_mesh, a2_mesh).reshape(a1_mesh.shape)
    return count_unstable_roots(eps, a, a1_mesh, a2_mesh).reshape(a1_mesh.shape) == 0


def main():
    init()
    eps, a = read_args()
    start = time.perf_counter()

    delimiter()
    print_col('Характеристическое уравнение (вариант 17):', Fore.BLUE)
    print_col('  P(λ) = ε²λ² + εAλ + 1 + a₁·e^(-2λ) + a₂·e^(-6λ) = 0', Fore.CYAN)
    print_col(f'  ε = {eps:g}, A = {a:g};  плоскость (a₁, a₂): {A1_LIM} × {A2_LIM}', Fore.CYAN)
    delimiter()

    print_col('Граница λ = 0:', Fore.BLUE)
    print_col('  1 + a₁ + a₂ = 0', Fore.LIGHTCYAN_EX)
    print_col('Граница λ = iω (ω > 0):', Fore.BLUE)
    print_col('  a₁(ω) = ((ε²ω² - 1)·sin6ω - εAω·cos6ω) / sin4ω', Fore.LIGHTCYAN_EX)
    print_col('  a₂(ω) = (εAω·cos2ω - (ε²ω² - 1)·sin2ω) / sin4ω', Fore.LIGHTCYAN_EX)
    print_col(f'  Особые точки: sin4ω = 0, т.е. ω = kπ/4 (шаг {DELTA_ZERO_STEP:.4f})', Fore.LIGHTCYAN_EX)

    branches = d_curve_branches(eps, a, A1_LIM, A2_LIM)
    lines = singular_lines(eps, a, A1_LIM, A2_LIM)
    print_col(f'  Рассматриваем ω ∈ (0, {omega_max(eps, A1_LIM, A2_LIM):.3f}], ветвей D-кривой: {len(branches)}',
              Fore.LIGHTCYAN_EX)
    print_col(f'  Особых прямых: {len(lines)}', Fore.LIGHTCYAN_EX)

    print_col('Несколько точек D-кривой:', Fore.BLUE)
    print_col(f'  {"ω":>8} {"a₁(ω)":>12} {"a₂(ω)":>12}', Fore.CYAN)
    for w in (0.2, 0.5, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0):
        a1_w, a2_w = d_curve(np.array(w), eps, a)
        print_col(f'  {w:8.3f} {a1_w:12.4f} {a2_w:12.4f}', Fore.LIGHTCYAN_EX)
    delimiter()

    print_col('Считаем число корней в правой полуплоскости (принцип аргумента)...', Fore.BLUE)
    a1 = np.linspace(*A1_LIM, GRID_SIZE)
    a2 = np.linspace(*A2_LIM, GRID_SIZE)
    a1_mesh, a2_mesh = np.meshgrid(a1, a2)
    roots = count_unstable_roots(eps, a, a1_mesh, a2_mesh).reshape(a1_mesh.shape)

    values, counts = np.unique(roots, return_counts=True)
    cell = (a1[1] - a1[0]) * (a2[1] - a2[0])
    print_col(f'  {"N":>4} {"доля окна":>12} {"площадь":>10}', Fore.CYAN)
    for value, count in zip(values, counts):
        color = Fore.GREEN if value == 0 else Fore.LIGHTCYAN_EX
        print_col(f'  {value:4d} {count / roots.size:12.2%} {count * cell:10.3f}', color)

    stable = roots == 0
    if stable.any():
        print_col(f'  Устойчивость: a₁ ∈ [{a1_mesh[stable].min():.3f}, {a1_mesh[stable].max():.3f}], '
                  f'a₂ ∈ [{a2_mesh[stable].min():.3f}, {a2_mesh[stable].max():.3f}]', Fore.GREEN)
        print_col(f'  Точка (0, 0): N = {roots[GRID_SIZE // 2, GRID_SIZE // 2]} '
                  f'(ε²λ² + εAλ + 1 устойчив при A > 0)', Fore.GREEN)
    print_col(f'  Ромб |a₁| + |a₂| < m(A) = {guaranteed_radius(a):.4f} устойчив при любом ε > 0', Fore.GREEN)
    delimiter()

    print_col('Строим области устойчивости для ε из ' + str(EPS_LIST), Fore.BLUE)
    small = slice(None, None, 2)  # для сравнительного графика хватит более грубой сетки
    panels = []
    for e in EPS_LIST:
        mask = stability_mask(e, a, a1_mesh[small, small], a2_mesh[small, small])
        panels.append((e, mask, d_curve_branches(e, a, A1_LIM, A2_LIM), singular_lines(e, a, A1_LIM, A2_LIM)))
        print_col(f'  ε = {e:<5g}: доля области устойчивости в окне {mask.mean():7.2%}', Fore.LIGHTCYAN_EX)
    delimiter()

    RESULTS_DIR.mkdir(exist_ok=True)
    tag = f'eps={eps:g}_A={a:g}'
    plot_partition(eps, a, a1, a2, roots, branches, lines, A1_LIM, A2_LIM, RESULTS_DIR / f'partition_{tag}.png')
    plot_eps_evolution(a, a1[small], a2[small], panels, A1_LIM, A2_LIM, RESULTS_DIR / f'evolution_A={a:g}.png')

    end = time.perf_counter()
    print_col(f'🕜  Программа отработала за {end - start:.3f} с', Fore.GREEN)
    print_col(f'💾  Картинки сохранены в {RESULTS_DIR}', Fore.GREEN)
    print_col('✅  Визуализация доступна в новом окне.', Fore.GREEN)
    delimiter()

    plt.show()


if __name__ == '__main__':
    main()
