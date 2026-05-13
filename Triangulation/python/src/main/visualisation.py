import random
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib.widgets import TextBox, Button
from algorithm import *

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
