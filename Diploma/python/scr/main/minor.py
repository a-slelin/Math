"""
Численная проверка нормальной формы (раздел 2): колебания вблизи простой точки границы 𝔻₀.

Уравнение (1):  ẋ + x = a·ẋ(t - T) + b·ẋ(t - H) + f₂x² + f₃x³,   a = a* - ε,  b = b*,
где (a*, b*) = (a(ω), b(ω)) — точка D-кривой (9).

По теореме 4 при Re λ > 0, Re σ < 0 у уравнения есть устойчивый цикл
    x(t) ≈ √ε · 2ρ* · cos(ωt),   ρ* = √(-Re λ / Re σ).

Программа:
  1) считает a*, b*, Re λ, Re σ, ρ* и проверяет, что (a*, b*) — простая точка границы 𝔻₀;
  2) решает уравнение (1) методом Рунге–Кутты 4-го порядка для двух начальных функций:
     с амплитудой меньше и больше, чем у цикла;
  3) рисует два графика: сверху — весь отрезок времени (видно, как обе амплитуды подходят к √ε·2ρ*),
     снизу — последние периоды вместе с приближённым решением (25).

Запуск: python minor.py. Картинка сохраняется в Diploma/images/Oscillations.png.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from roots import d_curve, characteristic_derivative, difference_operator_stable, difference_operator_min

# Параметры уравнения
T = 5  # Первое запаздывание
H = 1  # Второе запаздывание

# Частота ω выбирает точку (a*, b*) = (a(ω), b(ω)) на границе 𝔻₀.
# ω = 6.6313810303 — простая точка на верхней левой границе 𝔻₀: там граница — одна ветвь D-кривой,
# за ней лежит 𝔻₂, и сдвиг a = a* - ε уводит из 𝔻₀ ровно одну пару корней ±iω.
# (На нижней правой границе, ω ≈ 3.5–3.8, из 𝔻₀ выводит сдвиг a* + ε, а не a* - ε.)
# Прежнее значение ω = 8.192419118 даёт точку (-1.0074, 0.0001) вне 𝔻₀: там разностный оператор
# неустойчив и корней с Re λ > 0 уже бесконечно много (см. проверку в check_point).
OMEGA = 6.6313810303
EPS = 0.001  # Малый параметр ε (сдвиг a = a* - ε)

# Нелинейность f(x) = f₂x² + f₃x³ (подобрана так, чтобы Re σ < 0 — цикл устойчив)
F2 = 9.0
F3 = -50.0

# Начальные функции φ(t) = k·√ε·2ρ*·cos(ωt), t ∈ [-T, 0]: k < 1 — амплитуда меньше цикла, k > 1 — больше
START_FACTORS = (0.3, 2.0)
COLORS = ('#1f77b4', '#ff7f0e')  # голубой и оранжевый

# Интегрирование
STEP = 0.01  # Шаг по времени (T/STEP и H/STEP должны быть целыми)
T_END = 20000.0  # Конец отрезка интегрирования
LAST_PERIODS = 6  # Сколько последних периодов показать на нижнем графике

IMAGES_DIR = Path(__file__).resolve().parents[3] / 'images'


# noinspection PyPep8Naming
def normal_form(omega, f2, f3):
    """Точка (a*, b*) и коэффициенты нормальной формы λ (23), σ (24) с учётом α (20) и β (19)."""
    a, b = d_curve(omega, T, H)
    i = 1j

    beta = 2 * f2  # (19)
    alpha = f2 / (1 + 2 * i * omega
                  - a * 2 * i * omega * np.exp(-2 * i * omega * T)
                  - b * 2 * i * omega * np.exp(-2 * i * omega * H))  # (20)

    # Общий знаменатель (23)–(24) — это производная P'(iω) характеристического квазиполинома
    delimiter = characteristic_derivative(i * omega, a, b, T, H)
    lam = -i * omega * np.exp(-i * omega * T) / delimiter  # (23)
    sigma = (2 * f2 * beta + 2 * f2 * alpha + 3 * f3) / delimiter  # (24)
    return a, b, lam, sigma


def check_point(a, b):
    """
    Нормальная форма применима только в простой точке границы 𝔻₀: разностный оператор
    D(λ) = 1 - a·e^(-λT) - b·e^(-λH) должен быть устойчив (иначе корней с Re λ > 0 бесконечно много).
    """
    if difference_operator_stable(a, b, T, H)[0]:
        print(f'\tПростая точка границы: min|D(iω)| = {difference_operator_min(a, b, T, H)[0]:.4f} > 0')
    else:
        print('\tВНИМАНИЕ: разностный оператор неустойчив — точка не на границе 𝔻₀, нормальная форма неприменима!')


def solve(a, b, amplitude):
    """
    Решение уравнения (1) методом Рунге–Кутты 4-го порядка на равномерной сетке с шагом STEP.

    Уравнение нейтрального типа: правая часть содержит ẋ(t - T) и ẋ(t - H). Поэтому вместе с x
    храним и производную ẋ на всей сетке. Запаздывания кратны шагу, так что ẋ(t - T) — это просто
    значение массива на nT шагов назад, а в середине шага (для k₂, k₃) берём среднее двух соседних значений.
    """
    n_t, n_h = round(T / STEP), round(H / STEP)  # запаздывания в шагах сетки
    n = round(T_END / STEP)

    t = np.arange(-n_t, n + 1) * STEP  # сетка от -T до T_END
    x = np.zeros(t.size)
    dx = np.zeros(t.size)

    # История на [-T, 0]: φ(t) = A·cos(ωt), φ'(t) = -A·ω·sin(ωt)
    x[:n_t + 1] = amplitude * np.cos(OMEGA * t[:n_t + 1])
    dx[:n_t + 1] = -amplitude * OMEGA * np.sin(OMEGA * t[:n_t + 1])

    def rhs(x_val, delayed):
        """Правая часть ẋ = -x + f₂x² + f₃x³ + [a·ẋ(t - T) + b·ẋ(t - H)] (запаздывающая часть передаётся готовой)."""
        return -x_val + F2 * x_val * x_val + F3 * x_val ** 3 + delayed

    for k in range(n_t, t.size - 1):
        # Запаздывающая часть в начале, в конце и в середине шага
        d0 = a * dx[k - n_t] + b * dx[k - n_h]
        d1 = a * dx[k + 1 - n_t] + b * dx[k + 1 - n_h]
        dm = 0.5 * (d0 + d1)

        # Классический шаг Рунге–Кутты 4-го порядка
        xk = x[k]
        k1 = rhs(xk, d0)
        k2 = rhs(xk + STEP / 2 * k1, dm)
        k3 = rhs(xk + STEP / 2 * k2, dm)
        k4 = rhs(xk + STEP * k3, d1)
        x[k + 1] = xk + STEP / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

        # Производная в новой точке — прямо из уравнения
        dx[k + 1] = rhs(x[k + 1], d1)

    return t, x


def envelope(t, x):
    """Огибающие решения: максимум и минимум x(t) на каждом отрезке длиной в период 2π/ω (t ≥ 0)."""
    width = int(np.ceil(2 * np.pi / OMEGA / STEP))  # число точек сетки на один период
    x = x[t >= 0]
    count = x.size // width
    blocks = x[:count * width].reshape(count, width)  # строка — один период
    centers = (np.arange(count) + 0.5) * width * STEP
    return centers, blocks.max(axis=1), blocks.min(axis=1)


def fitted_phase(t, x):
    """
    Фаза φ, при которой cos(ωt + φ) лучше всего совпадает с x(t) на данном отрезке (метод наименьших квадратов).
    Нужна только для наглядности: формула (25) задаёт амплитуду и частоту, а фаза у цикла любая.
    """
    c, s = np.dot(x, np.cos(OMEGA * t)), np.dot(x, np.sin(OMEGA * t))
    return np.arctan2(-s, c)


if __name__ == '__main__':
    # 1) Параметры и коэффициенты нормальной формы
    a_star, b_star, lam, sigma = normal_form(OMEGA, F2, F3)
    a = a_star - EPS
    rho = np.sqrt(-lam.real / sigma.real)  # существует при Re λ · Re σ < 0
    cycle = np.sqrt(EPS) * 2 * rho  # амплитуда цикла (25)

    print('Параметры:')
    print(f'\tω = {OMEGA:.10f}, ε = {EPS:g}')
    print(f'\ta* = {a_star:.10f}, b* = {b_star:.10f}, a = a* - ε = {a:.10f}')
    print(f'\tf₂ = {F2:g}, f₃ = {F3:g}')
    print(f'\tRe(λ) = {lam.real:.10f}')
    print(f'\tRe(σ) = {sigma.real:.10f}')
    print(f'\tρ* = {rho:.10f}, √ε·2ρ* = {cycle:.10f}')
    check_point(a_star, b_star)

    # 2) Численные решения для двух начальных функций
    solutions = []
    for factor in START_FACTORS:
        t, x = solve(a, b_star, factor * cycle)
        solutions.append((factor, t, x))
        tail = t > T_END - 200
        print(f'\tk = {factor:g}: амплитуда в конце = {np.max(np.abs(x[tail])):.6f} (теория {cycle:.6f})')

    # 3) Рисунок: сверху — весь отрезок, снизу — последние периоды
    fig, (ax_all, ax_end) = plt.subplots(2, 1, figsize=(12, 9), gridspec_kw={'height_ratios': (1, 1)})

    # Верхний график: колебания очень частые (период ≈ 1), и на отрезке длины 20000 сами кривые
    # слились бы в сплошные полосы. Поэтому рисуем огибающие — максимум и минимум x на каждом периоде.
    for (factor, t, x), color in zip(solutions, COLORS):
        t_env, upper, lower = envelope(t, x)
        ax_all.fill_between(t_env, lower, upper, color=color, alpha=0.12, lw=0)
        ax_all.plot(t_env, upper, color=color, lw=2.2, label=rf'$\varphi(t) = {factor:g}\cdot\sqrt{{\varepsilon}}\cdot 2\rho^*\cos(\omega t)$')
        ax_all.plot(t_env, lower, color=color, lw=2.2)
    for sign in (1, -1):
        ax_all.axhline(sign * cycle, color='black', ls='--', lw=1.6,
                       label=r'$\pm\sqrt{\varepsilon}\cdot 2\rho^*$ — амплитуда цикла (25)' if sign > 0 else None)
    ax_all.legend(fontsize=12, loc='upper right', framealpha=0.95)
    ax_all.set_xlim(0, T_END)
    ax_all.set_title('Огибающие решений: выход на цикл', fontsize=16)

    # Нижний график: последние периоды и приближённое решение (25) с подобранной фазой
    period = 2 * np.pi / OMEGA
    t0 = T_END - LAST_PERIODS * period
    for (factor, t, x), color in zip(solutions, COLORS):
        end = t >= t0
        ax_end.plot(t[end], x[end], color=color, lw=2.2,
                    label=rf'$\varphi(t) = {factor:g}\cdot\sqrt{{\varepsilon}}\cdot 2\rho^*\cos(\omega t)$')
    end = solutions[0][1] >= t0
    t_end, x_end = solutions[0][1][end], solutions[0][2][end]
    ax_end.plot(t_end, cycle * np.cos(OMEGA * t_end + fitted_phase(t_end, x_end)), color='black', ls='--', lw=1.8,
                label=r'$x(t) = \sqrt{\varepsilon}\cdot 2\rho^*\cos(\omega t + \varphi_0)$')
    ax_end.set_xlim(t0, T_END)
    ax_end.set_title('Последние периоды', fontsize=16)
    ax_end.legend(fontsize=13, loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False)

    # Общее оформление
    for ax in (ax_all, ax_end):
        ax.set_xlabel('$t$', fontsize=20)
        ax.set_ylabel('$x$', fontsize=20, rotation=0, labelpad=12)
        ax.tick_params(axis='both', which='major', labelsize=13)
        ax.grid(True, alpha=0.3)
        ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
        ax.ticklabel_format(axis='x', useOffset=False)  # без «+2e4» под осью t

    fig.tight_layout()
    IMAGES_DIR.mkdir(exist_ok=True)
    fig.savefig(IMAGES_DIR / 'Oscillations.png', dpi=200)
    print(f'Сохранено: {IMAGES_DIR / "Oscillations.png"}')
    plt.show()
