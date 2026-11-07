"""
Тройные точки D-кривой (вариант 17): значения ε, при которых три ветви D-кривой
проходят через одну точку границы области устойчивости.

В такой точке у P(λ) одновременно три пары чисто мнимых корней ±iω₁, ±iω₂, ±iω₃,
а все остальные корни лежат в левой полуплоскости — критический случай тройной
бифуркации Андронова–Хопфа.

Запуск:
    python triple.py                       # уточнить и проверить известные тройные точки, нарисовать картинку
    python triple.py --scan 1.0 0.18 0.005 # заново просканировать ε от 1.0 до 0.18 с шагом 0.005 (долго)
"""

import itertools
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
from colorama import init, Fore, Style
from matplotlib.colors import ListedColormap

from const import RESULTS_DIR
from equation import d_curve, characteristic, characteristic_derivative
from partition import count_unstable_roots, DELTA_ZERO_STEP

A = 1.0

# Начальные приближения (ω₁, ω₂, ω₃, ε), полученные сканированием по ε (см. --scan)
KNOWN_GUESSES = (
    (0.474, 1.443, 2.345, 0.440),
    (1.020, 1.969, 3.920, 0.260),
    (1.499, 2.480, 3.451, 0.255),
    (1.993, 2.985, 3.946, 0.240),
    (1.513, 3.525, 4.472, 0.200),
)

# Окрестность области устойчивости, в которой ищем углы при сканировании
SCAN_BOX = 2.0

# Цвета трёх ветвей на картинке (ω₁, ω₂, ω₃) и цвет области устойчивости
BRANCH_COLORS = ('#2a78d6', '#eb6834', '#1baf7a')
STABLE_FILL = '#e4e2da'


def print_col(text, color):
    print(color + text + Style.RESET_ALL)


def delimiter():
    print_col('*' * 100, Fore.YELLOW)


# Уточнение тройной точки методом Ньютона


def residual(x):
    """
    Невязка системы a(ω₁; ε) = a(ω₂; ε) = a(ω₃; ε): 4 уравнения на 4 неизвестных (ω₁, ω₂, ω₃, ε).
    a(ω; ε) = (a₁(ω), a₂(ω)) — точка D-кривой (формулы Крамера из equation.d_curve).
    """
    w1, w2, w3, eps = x
    p1, p2, p3 = (np.array(d_curve(w, eps, A)) for w in (w1, w2, w3))
    return np.concatenate((p1 - p2, p2 - p3))


def newton(x, steps=50, tol=1e-14):
    """Метод Ньютона; матрицу Якоби считаем центральными разностями."""
    x = np.array(x, dtype=float)
    for _ in range(steps):
        f = residual(x)
        if np.max(np.abs(f)) < tol:
            break
        jac = np.empty((4, 4))
        for j in range(4):
            h = 1e-7 * max(1.0, abs(x[j]))
            dx = np.zeros(4)
            dx[j] = h
            jac[:, j] = (residual(x + dx) - residual(x - dx)) / (2 * h)
        x = x - np.linalg.solve(jac, f)
    return x


# Проверки найденной точки


def count_in_halfplane(a1, a2, eps, shift, radius=200.0, n=4_000_000):
    """
    Число корней в полуплоскости Re λ > shift — по принципу аргумента: обходим границу
    полукруга {Re λ > shift, |λ - shift| < radius} и считаем, сколько раз P(λ) обернулось вокруг нуля.
    Радиус с большим запасом: корней с Re λ > shift дальше него у квазиполинома нет.
    """
    side = shift + 1j * np.linspace(radius, -radius, n)
    arc = shift + radius * np.exp(1j * np.linspace(-np.pi / 2, np.pi / 2, n))
    phase = np.unwrap(np.angle(characteristic(np.concatenate([side, arc]), a1, a2, eps, A)))
    return (phase[-1] - phase[0]) / (2 * np.pi)


def rightmost_roots(a1, a2, eps, count=8):
    """
    Самые правые корни с Im λ ≥ 0: запускаем метод Ньютона сразу из сетки начальных точек
    в прямоугольнике Re λ ∈ [-3, 0.5], Im λ ∈ [0, 30] и собираем различные сошедшиеся корни.
    """
    re, im = np.meshgrid(np.linspace(-3, 0.5, 60), np.linspace(0, 30, 400))
    z = (re + 1j * im).ravel()
    with np.errstate(all='ignore'):  # далеко слева e^(-6λ) переполняется — такие точки просто выбросим
        for _ in range(60):
            z = z - characteristic(z, a1, a2, eps, A) / characteristic_derivative(z, a1, a2, eps, A)
        good = np.isfinite(z) & (np.abs(characteristic(z, a1, a2, eps, A)) < 1e-10) & (z.imag > -1e-9)
    roots = []
    for r in sorted(z[good], key=lambda v: -v.real):  # отбрасываем повторы
        if all(abs(r - q) > 1e-7 for q in roots):
            roots.append(r)
    return roots[:count]


def nearest_resonances(omegas, max_order=6, count=3):
    """Целочисленные соотношения k₁ω₁ + k₂ω₂ + k₃ω₃ ≈ 0 с |k₁| + |k₂| + |k₃| ≤ max_order."""
    found = []
    for k in itertools.product(range(-max_order, max_order + 1), repeat=3):
        # каждое соотношение берём один раз (k и -k эквивалентны)
        if any(k) and sum(map(abs, k)) <= max_order and k > tuple(-v for v in k):
            found.append((abs(np.dot(k, omegas)), k))
    return sorted(found)[:count]


def transversality_matrix(a1, a2, eps, omegas):
    """
    Матрица M[k] = ∂(Re λ_k)/∂(a₁, a₂, ε) в тройной точке (λ_k = iω_k).

    Из P(λ(p), p) = 0 получаем dλ = -(∂P/∂p)·dp / P'(λ), где
    ∂P/∂a₁ = e^(-2λ), ∂P/∂a₂ = e^(-6λ), ∂P/∂ε = 2ελ² + Aλ.
    Если det M ≠ 0, то три параметра (a₁, a₂, ε) независимо управляют тремя
    действительными частями — это полная («версальная») трёхпараметрическая развёртка.
    """
    rows = []
    for w in omegas:
        lam = 1j * w
        dp = np.array([np.exp(-2 * lam), np.exp(-6 * lam), 2 * eps * lam ** 2 + A * lam])
        rows.append(np.real(-dp / characteristic_derivative(lam, a1, a2, eps, A)))
    return np.array(rows)


def sector_counts(a1, a2, eps, radius=0.003, points=720):
    """
    Число неустойчивых корней N в секторах вокруг точки: обходим маленькую окружность.
    Ветви могут пересекаться под очень малым углом, поэтому точек на окружности много —
    иначе узкий сектор проскакивает между ними.
    """
    angles = np.linspace(0, 2 * np.pi, points, endpoint=False)
    n = count_unstable_roots(eps, A, a1 + radius * np.cos(angles), a2 + radius * np.sin(angles))
    sectors = [int(v) for v, _ in itertools.groupby(n)]  # подряд идущие одинаковые значения склеиваем
    if len(sectors) > 1 and sectors[0] == sectors[-1]:  # обход замкнут: первый и последний сектор — один
        sectors.pop()
    return sectors


# Сканирование по ε: поиск углов области устойчивости


def curve_pieces(eps, samples=6000):
    """Куски ветвей D-кривой внутри квадрата |a₁|, |a₂| ≤ SCAN_BOX; точки сгущены к концам интервалов."""
    pieces = []
    omega_max = np.sqrt(1 + 2 * SCAN_BOX) / eps + 1
    for k in range(int(np.ceil(omega_max / DELTA_ZERO_STEP))):
        t = np.linspace(0, 1, samples)[1:-1]
        w = k * DELTA_ZERO_STEP + DELTA_ZERO_STEP * (1 - np.cos(np.pi * t)) / 2
        a1, a2 = d_curve(w, eps, A)
        inside = (np.abs(a1) < SCAN_BOX) & (np.abs(a2) < SCAN_BOX)
        edges = np.diff(np.concatenate(([0], inside.astype(int), [0])))
        for s, e in zip(np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0]):
            if e - s > 2:
                pieces.append((w[s:e], a1[s:e], a2[s:e]))
    return pieces


def polyline_intersections(p, q, same):
    """Все пересечения двух ломаных; для каждого — (a₁, a₂, ω на первой, ω на второй)."""
    wp, xp, yp = p
    wq, xq, yq = q
    x0, y0, dx, dy = xp[:-1, None], yp[:-1, None], np.diff(xp)[:, None], np.diff(yp)[:, None]
    u0, v0, du, dv = xq[None, :-1], yq[None, :-1], np.diff(xq)[None, :], np.diff(yq)[None, :]
    den = dx * dv - dy * du
    with np.errstate(divide='ignore', invalid='ignore'):
        s = ((u0 - x0) * dv - (v0 - y0) * du) / den  # параметр на отрезке первой ломаной
        r = ((u0 - x0) * dy - (v0 - y0) * dx) / den  # параметр на отрезке второй ломаной
    ok = (s >= 0) & (s < 1) & (r >= 0) & (r < 1) & (den != 0)
    if same:  # самопересечения одной ломаной: соседние отрезки и повторы не считаем
        i, j = np.indices(ok.shape)
        ok &= (np.abs(i - j) > 2) & (i < j)
    return [(x0[i, 0] + s[i, j] * dx[i, 0], y0[i, 0] + s[i, j] * dy[i, 0],
             wp[i] + s[i, j] * (wp[i + 1] - wp[i]), wq[j] + r[i, j] * (wq[j + 1] - wq[j]))
            for i, j in zip(*np.nonzero(ok))]


def stability_corners(eps, radius=0.004):
    """Углы области устойчивости = пересечения двух ветвей, рядом с которыми есть точка с N = 0."""
    pieces = curve_pieces(eps)
    found = []
    for i in range(len(pieces)):
        for j in range(i, len(pieces)):
            found += polyline_intersections(pieces[i], pieces[j], same=(i == j))
    if not found:
        return []
    pts = np.array([f[:2] for f in found])
    angles = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    ring1 = (pts[:, :1] + radius * np.cos(angles)).ravel()
    ring2 = (pts[:, 1:] + radius * np.sin(angles)).ravel()
    n = count_unstable_roots(eps, A, ring1, ring2).reshape(len(found), -1)
    return [f for f, row in zip(found, n) if row.min() == 0]


def scan(eps_from, eps_to, step, merge_distance=0.03):
    """
    Идём по ε и ищем моменты, когда два угла области устойчивости с общей частотой
    сходятся в одну точку: ребро границы вдоль этой частоты стягивается — это тройная точка.
    """
    for eps in np.arange(eps_from, eps_to - 1e-12, -step):
        cs = stability_corners(eps)
        for c, d in itertools.combinations(cs, 2):
            distance = np.hypot(c[0] - d[0], c[1] - d[1])
            if distance < merge_distance and any(abs(w - v) < 0.01 for w in c[2:] for v in d[2:]):
                freqs = ', '.join(f'{w:.3f}' for w in sorted({round(float(w), 3) for w in c[2:] + d[2:]}))
                print_col(f'  ε = {eps:.3f}: углы ({c[0]:+.3f}, {c[1]:+.3f}) и ({d[0]:+.3f}, {d[1]:+.3f}) '
                          f'на расстоянии {distance:.4f}, частоты {freqs}', Fore.LIGHTCYAN_EX)


# Картинка


def plot_triple(eps_star, point, omegas, path, eps_around=(0.452, 0.430),
                x_lim=(-0.20, 0.02), y_lim=(0.89, 0.99)):
    """Окрестность тройной точки при ε > ε*, ε = ε* и ε < ε*: три ветви и область устойчивости."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 6.2), sharey=True)
    g1, g2 = np.linspace(*x_lim, 221), np.linspace(*y_lim, 101)
    m1, m2 = np.meshgrid(g1, g2)

    for ax, eps in zip(axes, (eps_around[0], eps_star, eps_around[1])):
        # Фон: область устойчивости (N = 0) серым
        n = count_unstable_roots(eps, A, m1, m2).reshape(m1.shape)
        ax.imshow(n == 0, origin='lower', extent=(*x_lim, *y_lim), aspect='auto',
                  cmap=ListedColormap(['#ffffff', STABLE_FILL]), vmin=0, vmax=1, interpolation='nearest')

        # Три ветви D-кривой: каждая живёт на своём интервале (kπ/4, (k+1)π/4), где лежит ω_k
        for w0, color, name in zip(omegas, BRANCH_COLORS, ('ω₁', 'ω₂', 'ω₃')):
            k = int(w0 // DELTA_ZERO_STEP)
            w = np.linspace(k * DELTA_ZERO_STEP + 1e-6, (k + 1) * DELTA_ZERO_STEP - 1e-6, 200001)
            ax.plot(*d_curve(w, eps, A), color=color, lw=2, label=f'ветвь {name}: ω ≈ {w0:.3f}')

        # Подписи N в характерных точках окна
        for x, y in ((-0.15, 0.91), (-0.02, 0.98), (-0.17, 0.975), (0.0, 0.905)):
            i, j = np.argmin(np.abs(g2 - y)), np.argmin(np.abs(g1 - x))
            ax.text(x, y, f'N = {n[i, j]}', ha='center', va='center', fontsize=11, color='#333333')

        if eps == eps_star:
            ax.plot(*point, 'o', ms=9, mfc='white', mec='#222222', mew=2, zorder=5)
            ax.annotate('тройная точка\n±iω₁, ±iω₂, ±iω₃', point, xytext=(-0.17, 0.955), fontsize=11,
                        arrowprops=dict(arrowstyle='->', color='#222222'))

        ax.set_xlim(x_lim)
        ax.set_ylim(y_lim)
        ax.set_xlabel('$a_1$', fontsize=13)
        ax.grid(True, alpha=0.25)
        mark = '= ε*' if eps == eps_star else ('> ε*' if eps > eps_star else '< ε*')
        ax.set_title(f'ε = {eps:.7g}  ({mark})', fontsize=13)

    axes[0].set_ylabel('$a_2$', fontsize=13)
    axes[0].legend(loc='lower left', fontsize=10, framealpha=0.95)
    fig.suptitle('Вариант 17, A = 1: три ветви D-кривой проходят через одну точку границы устойчивости '
                 '(серым — область устойчивости N = 0)', fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    return fig


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    init()
    start = time.perf_counter()

    if len(sys.argv) == 5 and sys.argv[1] == '--scan':
        delimiter()
        print_col('Сканирование по ε: ищем сливающиеся углы области устойчивости...', Fore.BLUE)
        scan(*map(float, sys.argv[2:]))
        delimiter()
        return

    results = []
    for guess in KNOWN_GUESSES:
        w1, w2, w3, eps = newton(guess)
        a1, a2 = d_curve(w1, eps, A)
        results.append((eps, a1, a2, (w1, w2, w3)))

        delimiter()
        print_col(f'ε* = {eps:.10f},  A = {A:g}', Fore.BLUE)
        print_col(f'  (a₁, a₂) = ({a1:.10f}, {a2:.10f})', Fore.CYAN)
        print_col(f'  ω₁, ω₂, ω₃ = {w1:.10f}, {w2:.10f}, {w3:.10f}', Fore.CYAN)
        print_col(f'  невязка системы: {np.max(np.abs(residual([w1, w2, w3, eps]))):.1e}', Fore.LIGHTCYAN_EX)
        print_col('  |P(iω)|  = ' + ', '.join(f'{abs(characteristic(1j * w, a1, a2, eps, A)):.1e}'
                                             for w in (w1, w2, w3)), Fore.LIGHTCYAN_EX)
        print_col('  |P\'(iω)| = ' + ', '.join(f'{abs(characteristic_derivative(1j * w, a1, a2, eps, A)):.3f}'
                                              for w in (w1, w2, w3)) + '  (не ноль — корни простые)',
                  Fore.LIGHTCYAN_EX)
        print_col(f'  корней с Re λ > +0.01: {count_in_halfplane(a1, a2, eps, 0.01):.3f}', Fore.GREEN)
        print_col(f'  корней с Re λ > -0.01: {count_in_halfplane(a1, a2, eps, -0.01):.3f}', Fore.GREEN)
        print_col('  самые правые корни: ' + ', '.join(f'{z.real:+.4f}{z.imag:+.4f}i'
                                                       for z in rightmost_roots(a1, a2, eps)[:5]),
                  Fore.LIGHTCYAN_EX)
        print_col(f'  отношения частот: ω₂/ω₁ = {w2 / w1:.4f}, ω₃/ω₁ = {w3 / w1:.4f}, ω₃/ω₂ = {w3 / w2:.4f}',
                  Fore.LIGHTCYAN_EX)
        print_col('  ближайшие резонансы: ' + ', '.join(f'{k} → {d:.4f}' for d, k in nearest_resonances((w1, w2, w3))),
                  Fore.LIGHTCYAN_EX)
        m = transversality_matrix(a1, a2, eps, (w1, w2, w3))
        print_col(f'  трансверсальность: det ∂(Re λ₁, Re λ₂, Re λ₃)/∂(a₁, a₂, ε) = {np.linalg.det(m):+.4f}, '
                  f'число обусловленности {np.linalg.cond(m):.1f}', Fore.LIGHTCYAN_EX)
        print_col(f'  N в секторах вокруг точки (обход против часовой): {sector_counts(a1, a2, eps)}',
                  Fore.LIGHTCYAN_EX)

    # Картинка — для основной точки (наибольшее ε*)
    eps, a1, a2, omegas = results[0]
    RESULTS_DIR.mkdir(exist_ok=True)
    plot_triple(eps, (a1, a2), omegas, RESULTS_DIR / 'triple_point.png')

    delimiter()
    print_col(f'🕜  Программа отработала за {time.perf_counter() - start:.1f} с', Fore.GREEN)
    print_col(f'💾  Картинка сохранена в {RESULTS_DIR / "triple_point.png"}', Fore.GREEN)
    delimiter()
    plt.show()


if __name__ == '__main__':
    main()
