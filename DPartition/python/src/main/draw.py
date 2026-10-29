import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from equation import zero_root_line, guaranteed_radius
from partition import connected_regions, deepest_point

# Палитра: зелёный — область устойчивости (N = 0), дальше — тёплые тона по росту N
STABLE_COLOR = '#7fc97f'
UNSTABLE_COLORS = ('#fdf1d6', '#fddbaa', '#fcbf80', '#f99d5e', '#ef7548', '#dc4f3a', '#bf2f32', '#97182e')
CURVE_COLOR = '#1f3b73'
ZERO_LINE_COLOR = '#b5179e'
SINGULAR_COLOR = '#555555'
RHOMB_COLOR = '#111111'

TITLE = r'$\varepsilon^2\lambda^2 + \varepsilon A\lambda + 1 + a_1 e^{-2\lambda} + a_2 e^{-6\lambda} = 0$'


def roots_colormap(n_max):
    """Дискретная палитра для N = 0, 1, ..., n_max."""
    colors = [STABLE_COLOR] + [UNSTABLE_COLORS[min(i, len(UNSTABLE_COLORS) - 1)] for i in range(n_max)]
    return ListedColormap(colors), BoundaryNorm(np.arange(-0.5, n_max + 1.5), n_max + 1)


def draw_boundaries(ax, branches, lines, a1_lim, ticks=True):
    """D-кривые (со штриховкой), прямая λ = 0 и особые прямые."""
    for b in branches:
        effects = [patheffects.withTickedStroke(angle=90 * b['side'], spacing=7, length=0.6)] if ticks else None
        ax.plot(b['a1'], b['a2'], color=CURVE_COLOR, lw=1.6, path_effects=effects)

    # λ = 0: 1 + a₁ + a₂ = 0. При переходе в 1 + a₁ + a₂ < 0 появляется
    # положительный вещественный корень — штрихуем нижнюю сторону.
    a1 = np.array(a1_lim)
    effects = [patheffects.withTickedStroke(angle=90, spacing=7, length=0.6)] if ticks else None
    ax.plot(a1[::-1], zero_root_line(a1[::-1]), color=ZERO_LINE_COLOR, lw=1.8, path_effects=effects)

    for c1, c2, c in lines:
        ax.plot(a1, (c - c1 * a1) / c2, color=SINGULAR_COLOR, lw=1.4, ls='--')


def draw_rhomb(ax, A):
    """Ромб |a₁| + |a₂| = m(A) — гарантированная устойчивость при любом ε > 0."""
    m = guaranteed_radius(A)
    if m > 0:
        ax.plot([m, 0, -m, 0, m], [0, m, 0, -m, 0], color=RHOMB_COLOR, lw=1.2, ls=(0, (4, 3)))


def setup_axes(ax, a1_lim, a2_lim):
    ax.set_xlim(a1_lim)
    ax.set_ylim(a2_lim)
    ax.set_aspect('equal')
    ax.axhline(0, color='k', lw=0.5, alpha=0.4)
    ax.axvline(0, color='k', lw=0.5, alpha=0.4)
    ax.set_xlabel(r'$a_1$', fontsize=13)
    ax.set_ylabel(r'$a_2$', fontsize=13)
    ax.grid(True, alpha=0.25)


def label_regions(ax, roots, a1, a2, min_share=0.004):
    """Подписываем число неустойчивых корней N в каждой достаточно крупной области."""
    for value, mask in connected_regions(roots):
        if mask.sum() < min_share * roots.size:
            continue
        i, j = deepest_point(mask)
        ax.text(a1[j], a2[i], f'{value}', ha='center', va='center', fontsize=12, fontweight='bold',
                color='#1b5e20' if value == 0 else '#3b1d0f',
                bbox=dict(boxstyle='circle,pad=0.25', fc='white', ec='none', alpha=0.75))


def plot_partition(eps, A, a1, a2, roots, branches, lines, a1_lim, a2_lim, path):
    """Главный график: D-разбиение плоскости (a₁, a₂) при фиксированных ε и A."""
    fig, ax = plt.subplots(figsize=(10, 9))

    n_max = int(roots.max())
    cmap, norm = roots_colormap(n_max)
    extent = (a1[0], a1[-1], a2[0], a2[-1])
    ax.imshow(roots, origin='lower', extent=extent, cmap=cmap, norm=norm, interpolation='nearest', alpha=0.9)

    draw_boundaries(ax, branches, lines, a1_lim)
    draw_rhomb(ax, A)
    label_regions(ax, roots, a1, a2)
    setup_axes(ax, a1_lim, a2_lim)

    legend = [
        Patch(fc=STABLE_COLOR, label='Область устойчивости (N = 0)'),
        Patch(fc=UNSTABLE_COLORS[2], label='Неустойчивость (N > 0)'),
        Line2D([], [], color=CURVE_COLOR, lw=1.6, label=r'$\lambda = \pm i\omega$ (D-кривая)'),
        Line2D([], [], color=ZERO_LINE_COLOR, lw=1.8, label=r'$\lambda = 0$: $1 + a_1 + a_2 = 0$'),
        Line2D([], [], color=RHOMB_COLOR, lw=1.2, ls=(0, (4, 3)),
               label=rf'$|a_1| + |a_2| < m(A) = {guaranteed_radius(A):.3f}$ (любое ε)'),
    ]
    ax.legend(handles=legend, loc='upper right', fontsize=9.5, framealpha=0.95)
    ax.set_title(f'D-разбиение: {TITLE}\n' + rf'$\varepsilon = {eps:g},\ A = {A:g}$'
                 + '   (числа — количество корней с Re λ > 0)', fontsize=12)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    return fig


def plot_eps_evolution(A, a1, a2, panels, a1_lim, a2_lim, path):
    """
    Сравнение областей устойчивости для разных ε.
    panels — список (ε, маска устойчивости, ветви D-кривой, особые прямые).
    """
    cols = 3
    rows = int(np.ceil(len(panels) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(5.2 * cols, 5 * rows))
    extent = (a1[0], a1[-1], a2[0], a2[-1])
    stable_cmap = ListedColormap(['white', STABLE_COLOR])

    for ax, (eps, stable, branches, lines) in zip(axes.flat, panels):
        ax.imshow(stable, origin='lower', extent=extent, cmap=stable_cmap, vmin=0, vmax=1,
                  interpolation='nearest', alpha=0.9)
        draw_boundaries(ax, branches, lines, a1_lim, ticks=False)
        draw_rhomb(ax, A)
        setup_axes(ax, a1_lim, a2_lim)
        title = rf'$\varepsilon = {eps:g}$' + ('  (предельный случай)' if eps == 0 else '')
        ax.set_title(title, fontsize=13)

    for ax in axes.flat[len(panels):]:
        ax.set_visible(False)

    fig.suptitle(f'Эволюция области устойчивости по ε,  A = {A:g}\n{TITLE}', fontsize=14)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    return fig
