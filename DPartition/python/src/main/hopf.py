"""
Нормальная форма для одной пары ±iω (вариант 17).

    ε²x″ + εAx′ + x + a₁x(t−2) + a₂x(t−6) = x³ + x³(t−2) + x³(t−6).

Запуск: python hopf.py [ε] [A] [ω] [μ].
μ — сдвиг от D-кривой по единичной нормали в сторону роста Re λ.
"""

import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, TextBox

from const import A, EPS, EPS_MIN, RESULTS_DIR, TAU_1, TAU_2
from equation import characteristic, characteristic_derivative, d_curve


def other_unstable_roots(omega, a1, a2, eps, A):
    """Число корней справа после исключения пары ±iω. Ещё одна пара на оси исключает расчёт."""
    # Q(λ) = P(λ)/(λ²+ω²) аналитична и стремится к ε² на правой полуокружности.
    # На мнимой оси (ω+ν)Q(iν) = P(iν)/(ω−ν). Положительный множитель не меняет аргумент.
    # Разность P(iν)−P(iω) делим аналитически, чтобы не терять точность при ν ≈ ω.
    def value(nu):
        result = eps ** 2 * (nu + omega) - 1j * eps * A
        for tau, coeff in ((TAU_1, a1), (TAU_2, a2)):
            phase = np.exp(-0.5j * tau * (nu + omega))
            result = result + 1j * tau * coeff * phase * np.sinc(tau * (nu - omega) / (2 * np.pi))
        return result

    # За верхней границей Re P(iν) < 0 и Re Q(iν) > 0. Хвост аргумента известен.
    end = np.sqrt(1 + abs(a1) + abs(a2)) / eps + 1
    tail = -np.angle(value(end))
    # Для разделённой разности |value′| ≤ max |(d/dν)²P(iν)| / 2.
    slope = eps ** 2 + (TAU_1 ** 2 * abs(a1) + TAU_2 ** 2 * abs(a2)) / 2
    tol = 1e-10 * (1 + eps ** 2 * (end + omega) + abs(eps * A) + TAU_1 * abs(a1) + TAU_2 * abs(a2))
    left, right = np.array([0.0]), np.array([end])
    angle = tail
    while left.size:
        if left.size > 100_000:
            raise ValueError('Слишком много неразличимых интервалов для надёжной проверки спектра.')
        mid = (left + right) / 2
        radius = (right - left) * slope / 2
        # Если диск со всеми значениями на отрезке не содержит 0, поворот меньше π.
        safe = abs(value(mid)) > radius + tol
        angle += np.sum(np.angle(value(right[safe]) / value(left[safe])))
        if np.any(radius[~safe] <= tol):
            raise ValueError('Рядом с мнимой осью есть ещё один корень или спектральный зазор слишком мал.')
        lo, hi, cut = left[~safe], right[~safe], mid[~safe]
        left, right = np.concatenate((lo, cut)), np.concatenate((cut, hi))
    return int(round(-angle / np.pi))


def normal_form(eps, A, omega):
    """Критическая точка, комплексные коэффициенты и спектр вне центральной пары."""
    if not EPS_MIN <= eps <= 1 or not np.isfinite(A):
        raise ValueError(f'Требуются ε в [{EPS_MIN:g}, 1] и конечное A.')
    if not np.isfinite(omega) or omega <= 0:
        raise ValueError('Частота ω должна быть положительной и конечной.')
    if abs(np.sin((TAU_2 - TAU_1) * omega)) < 1e-8:
        raise ValueError('При sin(4ω) ≈ 0 частота не задаёт регулярную точку D-кривой.')

    a1, a2 = d_curve(omega, eps, A)
    lam = 1j * omega
    if not np.isfinite(abs(a1) + abs(a2)) or not np.isfinite(omega * (TAU_2 - TAU_1)):
        raise ValueError('Масштаб параметров слишком велик для вычисления D-кривой.')
    phase = np.exp(-lam * np.array([TAU_1, TAU_2]))
    dp = characteristic_derivative(lam, a1, a2, eps, A)
    scale = 1 + abs(eps * A) + 2 * eps ** 2 * omega + TAU_1 * abs(a1) + TAU_2 * abs(a2)
    if not np.isfinite(scale) or not np.isfinite(dp):
        raise ValueError('Производную P′(iω) не удалось вычислить с конечной точностью.')
    if abs(dp) <= 1e-9 * scale:
        raise ValueError('P′(iω) близка к нулю: требуется простая критическая пара.')
    others = other_unstable_roots(omega, a1, a2, eps, A)

    # Сдвиг λ при изменении (a₁, a₂). Нормаль направляем в сторону Re λ > 0.
    derivatives = -phase / dp
    speed = np.linalg.norm(derivatives.real)
    if speed <= 1e-10 * np.linalg.norm(derivatives):
        raise ValueError('Не удалось определить поперечное направление к D-кривой.')
    normal = derivatives.real / speed
    slope = derivatives @ normal

    # Коэффициенты при z³ и z²·z̄ в сумме трёх кубов (x = z + z̄ в первом порядке).
    f30 = 1 + np.sum(phase ** 3)
    f21 = 3 * (1 + np.sum(phase))
    h30 = f30 / characteristic(3 * lam, a1, a2, eps, A)
    d21 = f21 / dp
    if abs(d21.real) <= 1e-9 * 9 / abs(dp):
        raise ValueError('Re d₂₁ численно равна нулю: тип цикла не определяется в кубическом порядке.')
    kind = 'сверхкритическая' if d21.real < 0 else 'подкритическая'
    stable = d21.real < 0 and others == 0
    return dict(a1=a1, a2=a2, dp=dp, derivatives=derivatives, normal=normal, slope=slope,
                kind=kind, stable=stable,
                f30=f30, h30=h30, f21=f21, d21=d21, others=others)


def cycle_parameters(omega, mu, data):
    """Радиус и частота цикла кубической нормальной формы в первом приближении."""
    if not np.isfinite(mu):
        raise ValueError('Сдвиг μ должен быть конечным.')
    d21, slope = data['d21'], data['slope']
    radius_sq = -slope.real * mu / d21.real
    frequency = omega + slope.imag * mu + d21.imag * radius_sq
    if not np.isfinite(radius_sq) or not np.isfinite(frequency):
        raise ValueError('Сдвиг слишком велик для расчёта в окрестности точки Хопфа.')
    if radius_sq > 0 and frequency <= 0:
        raise ValueError('Поправка к частоте слишком велика. Уменьшите |μ|.')

    return radius_sq, frequency


def plot_solution(axes, eps, A, omega, mu, data, radius_sq, frequency):
    """Ветвь амплитуд и ведущая гармоника x(t) для выбранного сдвига μ."""
    d21, slope = data['d21'], data['slope']
    branch, wave = axes
    branch.clear()
    wave.clear()
    width = max(0.01, 1.2 * abs(mu))
    offsets = np.linspace(0, -np.sign(d21.real) * width, 250)
    stable = data['stable']
    label = 'Устойчивый цикл' if stable else 'Неустойчивый цикл'
    branch.plot(offsets, 2 * np.sqrt(-slope.real * offsets / d21.real), '-' if stable else '--',
                color='#1f3b73', lw=2, label=label)
    branch.axhline(0, color='k', lw=0.6)
    branch.axvline(mu, color='#777777', ls=':', label='Выбранный сдвиг')
    branch.set(xlim=(-width, width), xlabel='Сдвиг μ по нормали к D-кривой', ylabel='Амплитуда x ≈ 2r',
               title='Ветвь малых периодических решений')
    branch.set_xticks(np.linspace(-width, width, 5))
    branch.legend()
    wave.set(xlabel='Время t', ylabel='x(t)', title='Ведущая гармоника решения')
    if radius_sq > 0:
        amplitude = 2 * np.sqrt(radius_sq)
        time = np.linspace(0, 4 * np.pi / frequency, 600)
        branch.plot(mu, amplitude, 'o', color='#1baf7a')
        wave.plot(time, amplitude * np.cos(frequency * time), color='#1f3b73')
        wave.set_title(f'Амплитуда ≈ {amplitude:.5g}, период ≈ {2 * np.pi / frequency:.5g}')
    else:
        message = 'Критическая точка: r = 0' if mu == 0 else 'С этой стороны малого цикла нет'
        wave.text(0.5, 0.5, message, transform=wave.transAxes, ha='center', va='center')
    for ax in axes:
        ax.grid(True, alpha=0.25)

    kind = data['kind']
    branch.figure.suptitle(f'Вариант 17: ε = {eps:g}, A = {A:g}, ω = {omega:g}\n'
                          f'Бифуркация Хопфа {kind}, Re d₂₁ = {d21.real:+.6g}')


def print_solution(eps, A, omega, mu, data, radius_sq, frequency):
    """Коэффициенты нормальной формы и результат для выбранной точки в консоли."""
    d21, slope = data['d21'], data['slope']
    print(f'ε = {eps:g}, A = {A:g}, ω = {omega:g}, μ = {mu:g}')
    print(f"  (a₁*, a₂*) = ({data['a1']:.9f}, {data['a2']:.9f}), P′(iω) = {data['dp']:.8g}")
    print(f"  ∂λ/∂a₁ = {data['derivatives'][0]:.8g}, ∂λ/∂a₂ = {data['derivatives'][1]:.8g}")
    print(f"  f₃₀ = {data['f30']:.8g}, h₃₀(0) = {data['h30']:.8g}")
    print(f"  f₂₁ = {data['f21']:.8g}, d₂₁ = {d21:.8g}")
    print(f"  n = {data['normal']}, α ≈ {slope.real:.8g}·μ; других корней справа: {data['others']}")
    a1, a2 = np.array([data['a1'], data['a2']]) + mu * data['normal']
    print(f'  При выбранном μ: (a₁, a₂) = ({a1:.9f}, {a2:.9f}).')
    label = 'Устойчивый цикл' if data['stable'] else 'Неустойчивый цикл'
    print(f"  Бифуркация {data['kind']}.")
    print(f'  {label} при μ {">" if d21.real < 0 else "<"} 0.')
    if radius_sq > 0:
        print(f'  При выбранном μ: r ≈ {np.sqrt(radius_sq):.7g}, частота ≈ {frequency:.7g}, '
              f'период ≈ {2 * np.pi / frequency:.7g}.')
    else:
        print('  Положительного радиуса при выбранном μ нет.')


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('eps', type=float, nargs='?', default=EPS, help='ε из варианта 17')
    args.add_argument('A', type=float, nargs='?', default=A, help='коэффициент A')
    args.add_argument('omega', type=float, nargs='?', default=1.2, help='частота на регулярной ветви D-кривой')
    args.add_argument('mu', type=float, nargs='?', default=0.001, help='малый сдвиг по нормали')
    params = args.parse_args()

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.subplots_adjust(top=0.82, bottom=0.26, wspace=0.28)
    omega_box = TextBox(fig.add_axes([0.14, 0.115, 0.13, 0.055]), 'ω  ', initial=str(params.omega))
    mu_box = TextBox(fig.add_axes([0.36, 0.115, 0.13, 0.055]), 'μ  ', initial=str(params.mu))
    button = Button(fig.add_axes([0.58, 0.115, 0.28, 0.055]), 'Вычислить коэффициенты')
    status = fig.text(0.5, 0.045, '', ha='center', fontsize=9)

    def calculate():
        omega, mu = float(omega_box.text), float(mu_box.text)
        data = normal_form(params.eps, params.A, omega)
        radius_sq, frequency = cycle_parameters(omega, mu, data)
        plot_solution(axes, params.eps, params.A, omega, mu, data, radius_sq, frequency)
        print_solution(params.eps, params.A, omega, mu, data, radius_sq, frequency)
        RESULTS_DIR.mkdir(exist_ok=True)
        path = RESULTS_DIR / f'hopf_eps={params.eps:g}_A={params.A:g}_w={omega:g}_mu={mu:g}.png'
        status.set_text(f'Рисунок: {path.name}')
        status.set_color('#333333')
        fig.savefig(path, dpi=140)
        print(f'  Картинка сохранена в {path}')

    def recalculate(event):
        try:
            calculate()
        except ValueError as exc:
            status.set_text(f'Расчёт не выполнен: {exc}')
            status.set_color('#b51730')
        fig.canvas.draw_idle()

    try:
        calculate()
    except ValueError as exc:
        args.error(str(exc))
    button.on_clicked(recalculate)
    plt.show()


if __name__ == '__main__':
    main()
