"""
Точка входа: D-разбиение для характеристического уравнения (вариант 17)

    P(λ) = ε²λ² + εAλ + 1 + a₁·e^(-2λ) + a₂·e^(-6λ) = 0.

Запуск: python main.py [ε] [A]

Программа по шагам:
  1) печатает уравнение и формулы границ D-разбиения;
  2) строит ветви D-кривой и особые прямые;
  3) считает число корней N с Re λ > 0 в каждой точке сетки на плоскости (a₁, a₂);
  4) строит области устойчивости для набора ε (сравнительный график);
  5) сохраняет обе картинки в папку results и показывает их в окне.
"""

import sys
import time

import matplotlib.pyplot as plt
import numpy as np
from colorama import init, Fore, Style

from const import EPS, A, EPS_MIN, EPS_LIST, A1_LIM, A2_LIM, GRID_SIZE, RESULTS_DIR
from draw import plot_partition, plot_eps_evolution
from equation import d_curve, guaranteed_radius
from partition import (d_curve_branches, singular_lines, count_unstable_roots, stable_mask_limit,
                       omega_max, DELTA_ZERO_STEP)


# Вспомогательные функции для цветного вывода в консоль


def print_col(text, color):
    print(color + text + Style.RESET_ALL)


def error(text):
    print_col(text, Fore.RED)


def delimiter():
    print_col('*' * 100, Fore.YELLOW)


def read_args():
    """
    Читаем необязательные аргументы: python main.py [ε] [A].
    Если их нет — берём значения по умолчанию из const.py.
    """
    try:
        eps = float(sys.argv[1]) if len(sys.argv) > 1 else EPS
        a = float(sys.argv[2]) if len(sys.argv) > 2 else A
    except ValueError:
        error(f'Использование: python main.py [ε] [A], где ε ∈ [{EPS_MIN:g}, 1]')
        sys.exit(1)

    # ε = 0 здесь не принимаем: для него не работает подсчёт корней по принципу аргумента
    # (уравнение становится разностным), этот случай есть только на сравнительном графике.
    # Сравнение записано так, чтобы nan тоже отсекался (с nan любое сравнение ложно).
    if not (EPS_MIN <= eps <= 1 and np.isfinite(a)):
        error(f'Параметр ε должен лежать в [{EPS_MIN:g}, 1], A — конечное число '
              '(случай ε = 0 строится на сравнительном графике)')
        sys.exit(1)
    return eps, a


def stability_mask(eps, a, a1_mesh, a2_mesh):
    """
    Маска устойчивости на сетке: True там, где все корни в левой полуплоскости.
    При ε > 0 считаем N по принципу аргумента, при ε = 0 — по критерию для многочлена.
    """
    if eps == 0:
        return stable_mask_limit(a1_mesh, a2_mesh).reshape(a1_mesh.shape)
    return count_unstable_roots(eps, a, a1_mesh, a2_mesh).reshape(a1_mesh.shape) == 0


def print_boundaries(eps, a, branches, lines):
    """Шаг 1–2: формулы границ D-разбиения и несколько точек D-кривой для контроля."""
    print_col('Граница λ = 0:', Fore.BLUE)
    print_col('  1 + a₁ + a₂ = 0', Fore.LIGHTCYAN_EX)
    print_col('Граница λ = iω (ω > 0):', Fore.BLUE)
    print_col('  a₁(ω) = ((ε²ω² - 1)·sin6ω - εAω·cos6ω) / sin4ω', Fore.LIGHTCYAN_EX)
    print_col('  a₂(ω) = (εAω·cos2ω - (ε²ω² - 1)·sin2ω) / sin4ω', Fore.LIGHTCYAN_EX)
    print_col(f'  Особые точки: sin4ω = 0, т.е. ω = kπ/4 (шаг {DELTA_ZERO_STEP:.4f})', Fore.LIGHTCYAN_EX)
    print_col(f'  Рассматриваем ω ∈ (0, {omega_max(eps, A1_LIM, A2_LIM):.3f}], ветвей D-кривой: {len(branches)}',
              Fore.LIGHTCYAN_EX)
    print_col(f'  Особых прямых: {len(lines)}', Fore.LIGHTCYAN_EX)

    # Таблица значений a₁(ω), a₂(ω) — удобно сверять с ручным счётом
    print_col('Несколько точек D-кривой:', Fore.BLUE)
    print_col(f'  {"ω":>8} {"a₁(ω)":>12} {"a₂(ω)":>12}', Fore.CYAN)
    for w in (0.2, 0.5, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0):
        a1_w, a2_w = d_curve(np.array(w), eps, a)
        print_col(f'  {w:8.3f} {a1_w:12.4f} {a2_w:12.4f}', Fore.LIGHTCYAN_EX)


def print_roots_summary(a, a1, a2, a1_mesh, a2_mesh, roots, lines):
    """Шаг 3: сколько места в окне занимает каждое значение N и где лежит область устойчивости."""
    values, counts = np.unique(roots, return_counts=True)
    cell = (a1[1] - a1[0]) * (a2[1] - a2[0])  # площадь одной клетки сетки
    print_col(f'  {"N":>4} {"доля окна":>12} {"площадь":>10}', Fore.CYAN)
    for value, count in zip(values, counts):
        color = Fore.GREEN if value == 0 else Fore.LIGHTCYAN_EX
        print_col(f'  {value:4d} {count / roots.size:12.2%} {count * cell:10.3f}', color)

    # Прямоугольник, в который вписана область устойчивости
    stable = roots == 0
    if stable.any():
        print_col(f'  Устойчивость: a₁ ∈ [{a1_mesh[stable].min():.3f}, {a1_mesh[stable].max():.3f}], '
                  f'a₂ ∈ [{a2_mesh[stable].min():.3f}, {a2_mesh[stable].max():.3f}]', Fore.GREEN)
    else:
        print_col('  В окне нет ни одной устойчивой точки (N ≥ 1 везде)', Fore.RED)

    # Проверка в начале координат и ромб гарантированной устойчивости имеют смысл только при A > 0
    if a > 0:
        print_col(f'  Точка (0, 0): N = {roots[GRID_SIZE // 2, GRID_SIZE // 2]} '
                  f'(ε²λ² + εAλ + 1 устойчив при A > 0)', Fore.GREEN)
        print_col(f'  Ромб |a₁| + |a₂| < m(A) = {guaranteed_radius(a):.4f} устойчив при любом ε > 0', Fore.GREEN)
    else:
        print_col('  При A ≤ 0 точка (0, 0) неустойчива (A < 0) или лежит на границе (A = 0, корни ±i/ε)',
                  Fore.LIGHTCYAN_EX)

    for c1, c2, c in lines:
        print_col(f'  Особая прямая: {c1:g}·a₁ + {c2:g}·a₂ = {c:.4f}', Fore.LIGHTCYAN_EX)


def build_evolution_panels(a, a1_mesh, a2_mesh, step):
    """
    Шаг 4: данные для сравнительного графика — по одной панели на каждое ε из EPS_LIST.
    Сетку прореживаем в step раз: для сравнения форм областей хватит и грубой.
    """
    coarse = slice(None, None, step)
    panels = []
    for e in EPS_LIST:
        mask = stability_mask(e, a, a1_mesh[coarse, coarse], a2_mesh[coarse, coarse])
        panels.append((e, mask, d_curve_branches(e, a, A1_LIM, A2_LIM), singular_lines(e, a, A1_LIM, A2_LIM)))
        print_col(f'  ε = {e:<5g}: доля области устойчивости в окне {mask.mean():7.2%}', Fore.LIGHTCYAN_EX)
    return panels


def main():
    # Чтобы греческие буквы и индексы печатались и в консоли Windows, и при перенаправлении вывода в файл
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    init()
    eps, a = read_args()
    start = time.perf_counter()

    delimiter()
    print_col('Характеристическое уравнение (вариант 17):', Fore.BLUE)
    print_col('  P(λ) = ε²λ² + εAλ + 1 + a₁·e^(-2λ) + a₂·e^(-6λ) = 0', Fore.CYAN)
    print_col(f'  ε = {eps:g}, A = {a:g};  плоскость (a₁, a₂): {A1_LIM} × {A2_LIM}', Fore.CYAN)
    delimiter()

    # Шаги 1–2: границы D-разбиения
    branches = d_curve_branches(eps, a, A1_LIM, A2_LIM)
    lines = singular_lines(eps, a, A1_LIM, A2_LIM)
    print_boundaries(eps, a, branches, lines)
    delimiter()

    # Шаг 3: число неустойчивых корней в каждом узле сетки GRID_SIZE × GRID_SIZE.
    # roots[i, j] относится к точке (a1[j], a2[i]) — строки сетки идут по a₂, столбцы по a₁.
    print_col('Считаем число корней в правой полуплоскости (принцип аргумента)...', Fore.BLUE)
    a1 = np.linspace(*A1_LIM, GRID_SIZE)
    a2 = np.linspace(*A2_LIM, GRID_SIZE)
    a1_mesh, a2_mesh = np.meshgrid(a1, a2)
    roots = count_unstable_roots(eps, a, a1_mesh, a2_mesh).reshape(a1_mesh.shape)
    print_roots_summary(a, a1, a2, a1_mesh, a2_mesh, roots, lines)
    delimiter()

    # Шаг 4: как область устойчивости меняется с ε
    print_col('Строим области устойчивости для ε из ' + str(EPS_LIST), Fore.BLUE)
    step = 2
    panels = build_evolution_panels(a, a1_mesh, a2_mesh, step)
    delimiter()

    # Шаг 5: рисуем и сохраняем картинки (имя файла содержит параметры, чтобы не затирать другие запуски)
    RESULTS_DIR.mkdir(exist_ok=True)
    tag = f'eps={eps:g}_A={a:g}'
    plot_partition(eps, a, a1, a2, roots, branches, lines, A1_LIM, A2_LIM, RESULTS_DIR / f'partition_{tag}.png')
    plot_eps_evolution(a, a1[::step], a2[::step], panels, A1_LIM, A2_LIM, RESULTS_DIR / f'evolution_A={a:g}.png')

    end = time.perf_counter()
    print_col(f'🕜  Программа отработала за {end - start:.3f} с', Fore.GREEN)
    print_col(f'💾  Картинки сохранены в {RESULTS_DIR}', Fore.GREEN)
    print_col('✅  Визуализация доступна в новом окне.', Fore.GREEN)
    delimiter()

    plt.show()


if __name__ == '__main__':
    main()
