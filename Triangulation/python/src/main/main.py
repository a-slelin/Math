import math
import random
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib.widgets import TextBox, Button
from typing import List, Tuple, Optional, Dict

# Настройка бэкенда
try:
    matplotlib.use("TkAgg")
except:
    pass


# ─────────────────────────────────────────────────────────────────────────────
# ГЕОМЕТРИЯ
# ─────────────────────────────────────────────────────────────────────────────

class Point:
    __slots__ = ("x", "y", "id")

    def __init__(self, x: float, y: float, id: int = -1):
        self.x, self.y, self.id = x, y, id

    def __repr__(self):
        return f"P{self.id}({self.x:.1f},{self.y:.1f})"

    def __lt__(self, other):
        if abs(self.x - other.x) > 1e-9: return self.x < other.x
        return self.y < other.y


def cross_prod(a, b, c):
    """Положительно — левый поворот (CCW)."""
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def in_circle(a, b, c, d):
    """Критерий Делоне: точка d внутри окружности abc."""
    ax, ay = a.x - d.x, a.y - d.y
    bx, by = b.x - d.x, b.y - d.y
    cx, cy = c.x - d.x, c.y - d.y
    return (ax * ax + ay * ay) * (bx * cy - by * cx) - \
        (bx * bx + by * by) * (ax * cy - ay * cx) + \
        (cx * cx + cy * cy) * (ax * by - ay * bx) > 1e-9


# ─────────────────────────────────────────────────────────────────────────────
# СТРУКТУРА ДАННЫХ (ГРАФ СМЕЖНОСТИ)
# ─────────────────────────────────────────────────────────────────────────────

class Mesh:
    def __init__(self):
        self.adj: Dict[Point, List[Point]] = {}

    def add_edge(self, u, v):
        for a, b in [(u, v), (v, u)]:
            if a not in self.adj: self.adj[a] = []
            if b not in self.adj[a]: self.adj[a].append(b)
        self.sort_around(u)
        self.sort_around(v)

    def remove_edge(self, u, v):
        if u in self.adj and v in self.adj[u]: self.adj[u].remove(v)
        if v in self.adj and u in self.adj[v]: self.adj[v].remove(u)

    def sort_around(self, p):
        if p in self.adj:
            self.adj[p].sort(key=lambda n: math.atan2(n.y - p.y, n.x - p.x))

    def next_ccw(self, p, neighbor):
        nodes = self.adj[p]
        return nodes[(nodes.index(neighbor) + 1) % len(nodes)]

    def next_cw(self, p, neighbor):
        nodes = self.adj[p]
        return nodes[(nodes.index(neighbor) - 1) % len(nodes)]


# ─────────────────────────────────────────────────────────────────────────────
# АЛГОРИТМ ВЫПУКЛОГО ПОЛОСОВОГО СЛИЯНИЯ (§3.3.2)
# ─────────────────────────────────────────────────────────────────────────────

class ConvexStripMerge:
    def __init__(self, points: List[Tuple[float, float]], s: float = 0.13):
        self.pts = [Point(p[0], p[1], i) for i, p in enumerate(points)]
        self.s = s
        self.mesh = Mesh()
        self.strip_boundaries = []
        if len(self.pts) >= 3:
            self._build()

    def _build(self):
        # Шаг 1: Разбиение (стр. 54)
        self.pts.sort()
        N = len(self.pts)
        xmin, xmax = self.pts[0].x, self.pts[-1].x
        ymin, ymax = min(p.y for p in self.pts), max(p.y for p in self.pts)

        # Формула оптимального числа полос (стр. 56)
        a, b = max(1, xmax - xmin), max(1, ymax - ymin)
        m_count = max(1, int(math.sqrt(self.s * (a / b) * N)))

        strip_size = math.ceil(N / m_count)
        strips_pts = [self.pts[i:i + strip_size] for i in range(0, N, strip_size)]

        # Шаг 2 и 3а: Триангуляция и достраивание выпуклости
        sub_meshes = []
        for strip in strips_pts:
            if len(strip) < 3: continue
            sm = self._triangulate_strip_step2(strip)
            self._make_convex_step3a(sm)
            sub_meshes.append(sm)

        for i in range(len(strips_pts) - 1):
            self.strip_boundaries.append((strips_pts[i][-1].x + strips_pts[i + 1][0].x) / 2)

        # Шаг 3б: Слияние выпуклых полос
        if not sub_meshes: return
        res = sub_meshes[0]
        for i in range(1, len(sub_meshes)):
            res = self._merge_step3b(res, sub_meshes[i])
        self.mesh = res

    def _triangulate_strip_step2(self, strip: List[Point]) -> Mesh:
        """Алгоритм триангуляции полосы (стр. 54, Рис 30)."""
        m = Mesh()
        pts = sorted(strip, key=lambda p: -p.y)  # Сверху вниз

        # Первый треугольник (ABC)
        m.add_edge(pts[0], pts[1])
        m.add_edge(pts[1], pts[2])
        m.add_edge(pts[2], pts[0])

        # Добавление остальных (Рис 30, б)
        for i in range(3, len(pts)):
            p = pts[i]
            # Ищем ближайшее видимое ребро на нижней границе
            # Для полосы это обычно соединение с "нижними" точками текущего меша
            best_dist = float('inf')
            best_edge = None
            for u in m.adj:
                for v in m.adj[u]:
                    d = (p.x - (u.x + v.x) / 2) ** 2 + (p.y - (u.y + v.y) / 2) ** 2
                    if d < best_dist:
                        best_dist, best_edge = d, (u, v)
            m.add_edge(p, best_edge[0])
            m.add_edge(p, best_edge[1])
        return m

    def _make_convex_step3a(self, mesh: Mesh):
        """Достраивание выпуклости (стр. 57, Шаг 3а, Рис. 31, д)."""
        while True:
            hull = self._get_hull(mesh)
            changed = False
            for i in range(len(hull)):
                p_prev = hull[i - 1]
                p_curr = hull[i]
                p_next = hull[(i + 1) % len(hull)]
                # Если угол < 180 (впадина), достраиваем треугольник
                if cross_prod(p_prev, p_curr, p_next) > 1e-9:
                    mesh.add_edge(p_prev, p_next)
                    changed = True
                    break
            if not changed: break

    def _get_hull(self, mesh: Mesh):
        start = min(mesh.adj.keys(), key=lambda p: (p.x, p.y))
        hull = []
        curr, prev_dir = start, -math.pi / 2
        while True:
            hull.append(curr)
            best_pt, min_diff = None, 10
            for n in mesh.adj[curr]:
                diff = (math.atan2(n.y - curr.y, n.x - curr.x) - prev_dir) % (2 * math.pi)
                if diff < min_diff:
                    min_diff, best_pt = diff, n
            prev_dir = math.atan2(curr.y - best_pt.y, curr.x - best_pt.x)
            curr = best_pt
            if curr == start: break
        return hull

    def _merge_step3b(self, left_m, right_m):
        """Слияние выпуклых триангуляций (Шаг 3б)."""
        new_m = Mesh()
        new_m.adj.update(left_m.adj)
        new_m.adj.update(right_m.adj)

        # Общая нижняя касательная
        ld = max(left_m.adj.keys(), key=lambda p: p.x)
        rd = min(right_m.adj.keys(), key=lambda p: p.x)
        while True:
            moved = False
            for n in left_m.adj[ld]:
                if cross_prod(rd, ld, n) < -1e-9: ld, moved = n, True; break
            if moved: continue
            for n in right_m.adj[rd]:
                if cross_prod(ld, rd, n) > 1e-9: rd, moved = n, True; break
            if not moved: break

        # Зигзаг
        while True:
            new_m.add_edge(ld, rd)
            l_cand = self._find_zip_cand(ld, rd, new_m, True)
            r_cand = self._find_zip_cand(rd, ld, new_m, False)
            if not l_cand and not r_cand: break
            if not l_cand or (r_cand and in_circle(ld, rd, l_cand, r_cand)):
                rd = r_cand
            else:
                ld = l_cand
        return new_m

    def _find_zip_cand(self, p, other, mesh, is_left):
        side = 1 if is_left else -1
        candidates = [n for n in mesh.adj[p] if cross_prod(p, other, n) * side > 1e-9]
        if not candidates: return None

        # Выбираем лучшего по Делоне (как в "Разделяй и властвуй")
        best = candidates[0]
        for i in range(1, len(candidates)):
            if in_circle(p, other, best, candidates[i]):
                mesh.remove_edge(p, best)
                best = candidates[i]
        return best


# ─────────────────────────────────────────────────────────────────────────────
# ВИЗУАЛИЗАЦИЯ (Интерфейс)
# ─────────────────────────────────────────────────────────────────────────────

class InteractiveApp:
    def __init__(self):
        self.points = [(random.uniform(10, 90), random.uniform(10, 90)) for _ in range(40)]
        self.s_val = 0.13

        self.fig = plt.figure(figsize=(12, 9), facecolor='#11111b')
        self.ax = self.fig.add_axes([0.05, 0.15, 0.75, 0.8])
        self.ax.set_facecolor('#1e1e2e')

        # Коллекции
        self._lc_edges = LineCollection([], colors='#89b4fa', lw=1, alpha=0.8)
        self._lc_strips = LineCollection([], colors='#f38ba8', lw=1.2, ls='--', alpha=0.5)
        self._sc_pts = self.ax.scatter([], [], c='#fab387', edgecolors='white', s=35, zorder=10)
        self._hi_tri = mpatches.Polygon([[0, 0]], closed=True, fc='#a6e3a133', ec='#a6e3a1', lw=2, visible=False)

        self.ax.add_collection(self._lc_edges)
        self.ax.add_collection(self._lc_strips)
        self.ax.add_patch(self._hi_tri)

        self._setup_ui()
        self._rebuild()

        self.fig.canvas.mpl_connect("button_press_event", self._on_click)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_hover)
        plt.show()

    def _setup_ui(self):
        # Исправленный TextBox без textcolor
        ax_s = self.fig.add_axes([0.15, 0.05, 0.1, 0.04])
        self.txt_s = TextBox(ax_s, "Коэф. s: ", initial=str(self.s_val), color='#313244')
        self.txt_s.label.set_color('#cdd6f4')
        self.txt_s.text_disp.set_color('white')  # Ручная установка цвета текста
        self.txt_s.on_submit(self._on_s_change)

        ax_clr = self.fig.add_axes([0.35, 0.05, 0.1, 0.04])
        self.btn_clr = Button(ax_clr, "Очистить", color='#45475a', hovercolor='#585b70')
        self.btn_clr.label.set_color('white')
        self.btn_clr.on_clicked(self._clear)

        self.info = self.fig.text(0.82, 0.8, "", color='#cdd6f4', fontfamily='monospace')

    def _on_s_change(self, val):
        try:
            self.s_val = float(val); self._rebuild()
        except:
            pass

    def _clear(self, _):
        self.points = [];
        self._rebuild()

    def _on_click(self, event):
        if event.inaxes != self.ax: return
        if event.button == 1:
            self.points.append((event.xdata, event.ydata))
        elif event.button == 3 and self.points:
            idx = min(range(len(self.points)),
                      key=lambda i: math.hypot(self.points[i][0] - event.xdata, self.points[i][1] - event.ydata))
            self.points.pop(idx)
        self._rebuild()

    def _on_hover(self, event):
        if not event.inaxes or not self.algo: return
        # Поиск треугольника под курсором для подсветки
        found = False
        px, py = event.xdata, event.ydata
        for p, neighbors in self.algo.mesh.adj.items():
            for i in range(len(neighbors)):
                n1, n2 = neighbors[i], neighbors[(i + 1) % len(neighbors)]
                if n2 in self.algo.mesh.adj[n1]:  # Проверка на грань треугольника
                    # Проверка попадания в треугольник через ориентацию
                    if cross_prod(p, n1, Point(px, py)) > 0 and \
                            cross_prod(n1, n2, Point(px, py)) > 0 and \
                            cross_prod(n2, p, Point(px, py)) > 0:
                        self._hi_tri.set_xy([(p.x, p.y), (n1.x, n1.y), (n2.x, n2.y)])
                        self._hi_tri.set_visible(True)
                        found = True;
                        break
            if found: break
        if not found: self._hi_tri.set_visible(False)
        self.fig.canvas.draw_idle()

    def _rebuild(self):
        self.algo = ConvexStripMerge(self.points, self.s_val)

        edges = []
        for p, neighbors in self.algo.mesh.adj.items():
            for n in neighbors:
                if id(p) < id(n): edges.append([(p.x, p.y), (n.x, n.y)])

        self._lc_edges.set_segments(edges)
        self._lc_strips.set_segments([[(bx, 0), (bx, 100)] for bx in self.algo.strip_boundaries])

        if self.points:
            self._sc_pts.set_offsets(self.points)
        else:
            self._sc_pts.set_offsets(matplotlib.collections.np.empty((0, 2)))

        self.info.set_text(
            f"Точек: {len(self.points)}\nПолос: {len(self.algo.strip_boundaries) + 1}\nРебер: {len(edges)}")
        self.ax.set_xlim(0, 100);
        self.ax.set_ylim(0, 100)
        self.fig.canvas.draw_idle()


if __name__ == "__main__":
    InteractiveApp()
