"""
Интерактивная визуализация триангуляции Делоне
Модифицированный иерархический алгоритм
"""

import math
import random
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle
from matplotlib.widgets import TextBox, Button
from typing import Optional, List, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Геометрия
# ─────────────────────────────────────────────────────────────────────────────

class Point:
    __slots__ = ('x', 'y', 'idx', 'is_super')

    def __init__(self, x: float, y: float, idx: int = -1, is_super: bool = False):
        self.x = x
        self.y = y
        self.idx = idx
        self.is_super = is_super

    def __repr__(self):
        return f'P{self.idx}({self.x:.2f},{self.y:.2f})'


def orient2d(ax, ay, bx, by, cx, cy) -> float:
    """
    Вычисляет знаковую площадь (удвоенную) треугольника (A,B,C).
    Результат > 0 – точки A, B, C идут против часовой стрелки.
    Результат < 0 – по часовой стрелке.
    Результат = 0 – точки коллинеарны (лежат на одной прямой).

    Геометрический смысл:
    Площадь параллелограмма, построенного на векторах AB и AC,
    со знаком, определяемым ориентацией.
    Формула: (B - A) x (C - A) (векторное произведение в 2D).
    """
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def in_circle(ax, ay, bx, by, cx, cy, dx, dy) -> float:
    """
    Определяет, лежит ли точка D внутри окружности,
    проходящей через точки A, B, C.
    Предполагается, что A, B, C заданы в порядке против часовой стрелки.
    Возвращает:
      > 0 – D строго внутри окружности
      = 0 – D лежит на окружности
      < 0 – D вне окружности

    Критерий основан на вычислении знака определителя 4x4:
    | x^2+y^2, x, y, 1 |
    | x1^2+y1^2, x1, y1, 1 |
    | x2^2+y2^2, x2, y2, 1 |
    | x3^2+y3^2, x3, y3, 1 |
    После подстановки D вместо (x,y) и A,B,C вместо (x1,y1)... знак определителя
    равен знаку выражения, вычисляемого ниже.
    """
    adx = ax - dx
    ady = ay - dy
    bdx = bx - dx
    bdy = by - dy
    cdx = cx - dx
    cdy = cy - dy
    return (adx * (bdy * (cdx * cdx + cdy * cdy) - cdy * (bdx * bdx + bdy * bdy))
            - ady * (bdx * (cdx * cdx + cdy * cdy) - cdx * (bdx * bdx + bdy * bdy))
            + (adx * adx + ady * ady) * (bdx * cdy - cdx * bdy))


def pt_in_tri(px, py, ax, ay, bx, by, cx, cy) -> bool:
    """
    Проверяет, лежит ли точка P внутри треугольника ABC.
    Используется метод «проверки одинаковости знаков ориентаций».
    Точка считается принадлежащей треугольнику, если она находится
    строго внутри или на границе (рёбрах/вершинах).
    """
    d1 = orient2d(px, py, ax, ay, bx, by)
    d2 = orient2d(px, py, bx, by, cx, cy)
    d3 = orient2d(px, py, cx, cy, ax, ay)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)


def circumcenter(ax, ay, bx, by, cx, cy):
    """
    Вычисляет центр (x,y) и радиус описанной окружности треугольника ABC.
    Возвращает ((cx, cy), radius). В случае коллинеарных точек возвращает (None, None).
    Формула выведена из решения системы:
        (x - x0)^2 + (y - y0)^2 = R^2 для трёх точек.
    Используется метод через определители, устойчивый для почти вырожденных случаев.
    """
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None, None
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def make_ccw(a: Point, b: Point, c: Point):
    """
    Принимает три объекта Point и возвращает кортеж (p, q, r) такой,
    что эти три точки идут в порядке против часовой стрелки (CCW).
    Если исходная тройка уже CCW, оставляет как есть.
    Иначе (CW) меняет местами b и c.
    """
    if orient2d(a.x, a.y, b.x, b.y, c.x, c.y) < 0:
        return a, c, b
    return a, b, c


# ─────────────────────────────────────────────────────────────────────────────
# Ядро алгоритма — Модифицированный иерархический алгоритм
# ─────────────────────────────────────────────────────────────────────────────

class FlipRecord:
    """Запись об одном перекидывании ребра на Проходе 2."""
    __slots__ = ("edge_old", "edge_new", "snap_before", "snap_after")

    def __init__(self, edge_old, edge_new, snap_before, snap_after):
        self.edge_old = edge_old  # (Point, Point)
        self.edge_new = edge_new  # (Point, Point)
        self.snap_before = snap_before  # список троек Point перед flip
        self.snap_after = snap_after  # список троек Point после flip


class ModifiedHierarchical:
    """
    Двухпроходный алгоритм построения триангуляции Делоне (модифицированный иерархический).

    Идея:
        1) Проход 1: последовательно вставляем все точки в триангуляцию,
           не проверяя условие Делоне – только разбиваем треугольник,
           содержащий точку, на три меньших. Используется суперструктура,
           чтобы гарантировать, что все точки лежат внутри начального треугольника.
        2) Проход 2: после вставки всех точек запускаем процесс глобального
           перестроения – обходим все внутренние рёбра и, если пара смежных
           треугольников нарушает условие Делоне, выполняем флип ребра.
           Повторяем, пока все пары не станут допустимыми.
           В результате получаем триангуляцию Делоне.

    Сохраняются промежуточные состояния (снимки) для последующей визуализации.
    """

    def __init__(self, points: List[Tuple[float, float]]):
        """
        Инициализирует алгоритм переданными точками.

        Параметры:
            points (List[Tuple[float, float]]): список координат (x, y) исходных точек.

        Поля класса:
            _real_pts (List[Point]): список исходных точек (объекты Point с индексами).
            _all_pts (List[Point]): объединённый список всех точек (реальные + суперструктура).
            _super (List[Point]): три вершины супертреугольника.
            tris_pass1 (List[Tuple[Point, Point, Point]]): результат после прохода 1
                (без учёта суперструктуры, только треугольники из реальных точек).
            tris_final (List[Tuple[Point, Point, Point]]): финальная триангуляция Делоне.
            flips (List[FlipRecord]): список всех выполненных флипов с сохранением
                состояний до и после каждого флипа (для анимации/отладки).
            _p1_snapshots (List[List]): снимки после каждой вставки на проходе 1
                (полные списки треугольников, включая суперструктуру).

        Если точек меньше трёх, построение не запускается (результаты останутся пустыми).
        """
        self._real_pts: List[Point] = [
            Point(x, y, int(i)) for i, (x, y) in enumerate(points)
        ]
        self._all_pts: List[Point] = []  # real + super
        self._super: List[Point] = []

        # Результаты, заполняются после build()
        self.tris_pass1: List[Tuple[Point, Point, Point]] = []  # после П1
        self.tris_final: List[Tuple[Point, Point, Point]] = []  # после П2
        self.flips: List[FlipRecord] = []

        self._p1_snapshots: List[List] = []  # снапшот после каждой вставки

        if len(self._real_pts) >= 3:
            self._build()

    # ── Суперструктура ───────────────────────────────────────────────────────

    def _make_super(self):
        """
        Строит большой треугольник, гарантированно покрывающий все исходные точки.

        Алгоритм:
            1. Находим минимальные/максимальные координаты среди реальных точек.
            2. Вычисляем центр (cx, cy) ограничивающего прямоугольника.
            3. Вычисляем полудиагональ r = (max(ширина, высота) * 12 + 5).
            4. Создаём три вершины супертреугольника:
                - вершина сверху: (cx, cy + 3*r)
                - левая нижняя: (cx - 3*r, cy - 3*r)
                - правая нижняя: (cx + 3*r, cy - 3*r)
            5. Сохраняем эти точки в self._super.
            6. Формируем общий список self._all_pts = реальные + суперточки.
            7. Возвращаем список трёх суперточек.

        Зачем нужен супертреугольник?
            Он обеспечивает, что при вставке первой точки у нас уже есть
            треугольник, куда она попадёт. Без него первые три точки пришлось бы
            обрабатывать как особый случай. Также супертреугольник покрывает
            всю область, упрощая локализацию точек, лежащих вне текущей триангуляции.
        """
        pts = self._real_pts
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        r = max(max(xs) - min(xs), max(ys) - min(ys), 1.0) * 12 + 5
        s0 = Point(cx, cy + 3 * r, -1, is_super=True)
        s1 = Point(cx - 3 * r, cy - 3 * r, -2, is_super=True)
        s2 = Point(cx + 3 * r, cy - 3 * r, -3, is_super=True)
        self._super = [s0, s1, s2]
        self._all_pts = list(self._real_pts) + self._super
        return [s0, s1, s2]

    # ── Локализация точки (линейный обход) ──────────────────────────────────

    @staticmethod
    def _find_tri(tris: List, px: float, py: float) -> int:
        """
        Находит индекс треугольника, содержащего заданную точку.

        Параметры:
            tris (List[Tuple[Point, Point, Point]]): список треугольников (каждый – тройка точек).
            px, py (float): координаты точки.

        Возвращает:
            int: индекс треугольника в списке, в который попадает точка,
                 либо -1, если точка не находится ни в одном треугольнике.

        Примечание:
            Используется линейный перебор O(|tris|). Для демонстрационных целей
            этого достаточно, так как количество треугольников невелико.
            В промышленных реализациях применяют кэширование или деревья поиска.
        """
        for i, (a, b, c) in enumerate(tris):
            if pt_in_tri(px, py, a.x, a.y, b.x, b.y, c.x, c.y):
                return i
        return -1

    # ── Проход 1: вставка без Делоне ────────────────────────────────────────

    def _pass1(self):
        """
        Первый проход: вставка всех реальных точек в триангуляцию
        без проверки условия Делоне.

        Шаги:
            1. Создаём супертреугольник (три вершины) – начальная триангуляция.
            2. Для каждой реальной точки:
                a) Находим треугольник, содержащий эту точку (self._find_tri).
                b) Если точка не найдена (что маловероятно из-за супертреугольника),
                   берём первый треугольник (индекс 0) – fallback.
                c) Удаляем этот треугольник из списка.
                d) Добавляем три новых треугольника, соединяя точку с каждой
                   парой вершин удалённого треугольника.
                e) Сохраняем снимок (копию всего списка треугольников)
                   для последующей визуализации.
            3. После обработки всех точек удаляем треугольники,
               содержащие хотя бы одну вершину суперструктуры.
               Результат сохраняется в self.tris_pass1.

        Важно:
            На этом этапе триангуляция НЕ является триангуляцией Делоне,
            могут существовать пары треугольников, нарушающие условие пустой окружности.
        """
        s0, s1, s2 = self._make_super()
        tris: List[Tuple[Point, Point, Point]] = [(s0, s1, s2)]

        for p in self._real_pts:
            idx = self._find_tri(tris, p.x, p.y)
            if idx < 0:
                # Точка вне всех треугольников — ищем ближайший
                idx = 0
            a, b, c = tris.pop(idx)
            tris.append((p, a, b))
            tris.append((p, b, c))
            tris.append((p, c, a))
            self._p1_snapshots.append(list(tris))

        # Убрать треугольники с суперструктурными вершинами
        super_set = {id(s) for s in self._super}
        self.tris_pass1 = [
            t for t in tris
            if not any(id(v) in super_set for v in t)
        ]

    # ── Проход 2: полное перестроение ────────────────────────────────────────

    def _pass2(self):
        """
        Второй проход: итеративное исправление триангуляции до выполнения условия Делоне.

        Алгоритм (см. теорему 1 в книге Скворцова):
            Пока есть хотя бы одна пара смежных треугольников, нарушающих условие Делоне:
                1. Построить отображение "ребро → индексы треугольников, содержащих это ребро".
                2. Для каждого внутреннего ребра (принадлежащего ровно двум треугольникам):
                   a) Найти противоположные вершины c и d.
                   b) Привести треугольник abc к ориентации против часовой стрелки (CCW).
                   c) Вычислить критерий in_circle для точки d относительно описанной окружности abc.
                   d) Если d внутри окружности (val > 1e-9), выполнить флип:
                      - Удалить ребро (a,b)
                      - Добавить ребро (c,d)
                      - Заменить старые треугольники на новые: (c,a,d) и (c,d,b)
                      - Зафиксировать факт изменения и сохранить запись о флипе
                3. Если ни одного флипа не выполнено на полном обходе – триангуляция стала Делоне.

        Технические детали:
            - Работа ведётся с полным списком треугольников (включая суперструктуру),
              потому что супер-вершины участвуют в проверках на границе.
            - После всех флипов треугольники, содержащие супер-вершины, удаляются.
            - Для предотвращения зацикливания вводится ограничение max_iter.
            - Каждый флип записывается в self.flips с сохранением состояний до/после.

        Результат:
            self.tris_final – триангуляция Делоне без суперструктуры.
            self.flips – список всех выполненных флипов (для анимации).
        """
        super_set = {id(s) for s in self._super}

        # Работаем на полном списке (включая суперструктуру) до финального удаления
        _, _, _ = self._super
        # Восстановить полный список из последнего снапшота
        tris = list(self._p1_snapshots[-1]) if self._p1_snapshots else []

        changed = True
        safety = 0
        max_iter = 15 * max(1, len(tris)) ** 2

        while changed and safety < max_iter:
            changed = False
            edge_map: dict = {}
            for i, (a, b, c) in enumerate(tris):
                for ea, eb in [(a, b), (b, c), (a, c)]:
                    key = (id(ea), id(eb)) if id(ea) < id(eb) else (id(eb), id(ea))
                    edge_map.setdefault(key, []).append((i, ea, eb))

            for key, entries in edge_map.items():
                safety += 1
                if len(entries) != 2:
                    continue

                (i1, ea, eb), (i2, _, __) = entries
                t1 = tris[i1]
                t2 = tris[i2]
                a_pt = ea
                b_pt = eb
                c_pt = next(v for v in t1 if id(v) != id(ea) and id(v) != id(eb))
                d_pt = next(v for v in t2 if id(v) != id(ea) and id(v) != id(eb))

                ax, ay = a_pt.x, a_pt.y
                bx, by = b_pt.x, b_pt.y
                cx, cy = c_pt.x, c_pt.y
                dx, dy = d_pt.x, d_pt.y

                # Обеспечить CCW для треугольника ABC
                if orient2d(ax, ay, bx, by, cx, cy) < 0:
                    a_pt, b_pt = b_pt, a_pt
                    ax, ay, bx, by = bx, by, ax, ay

                val = in_circle(ax, ay, bx, by, cx, cy, dx, dy)
                if val > 1e-9:
                    snap_before = list(tris)
                    # Flip: (a,b) → (c,d)
                    new_t1 = make_ccw(c_pt, a_pt, d_pt)
                    new_t2 = make_ccw(c_pt, d_pt, b_pt)
                    tris[i1] = new_t1
                    tris[i2] = new_t2
                    snap_after = list(tris)
                    self.flips.append(FlipRecord(
                        edge_old=(a_pt, b_pt),
                        edge_new=(c_pt, d_pt),
                        snap_before=snap_before,
                        snap_after=snap_after,
                    ))
                    changed = True
                    break

        # Финальный список без суперструктуры
        self.tris_final = [
            t for t in tris
            if not any(id(v) in super_set for v in t)
        ]

    # ── Публичный метод ─────────────────────────────────────────────────────

    def _build(self):
        """
        Запускает оба прохода построения триангуляции.

        Сбрасывает предыдущие результаты, затем вызывает _pass1() и _pass2().
        Вызывается автоматически из __init__ при наличии хотя бы трёх точек.
        """
        self.tris_pass1 = []
        self.tris_final = []
        self.flips = []
        self._p1_snapshots = []
        self._pass1()
        self._pass2()

    def real_points(self) -> List[Point]:
        """Возвращает список исходных точек (объекты Point)."""
        return self._real_pts

    def n_real(self) -> int:
        """Возвращает количество исходных точек."""
        return len(self._real_pts)

    def triangles_pass1(self):
        """Возвращает список треугольников после первого прохода (без суперструктуры)."""
        return self.tris_pass1

    def triangles_final(self):
        """Возвращает финальную триангуляцию Делоне (без суперструктуры)."""
        return self.tris_final

    def n_flips(self) -> int:
        """Возвращает общее количество выполненных флипов на втором проходе."""
        return len(self.flips)


# ─────────────────────────────────────────────────────────────────────────────
# Интерактивное приложение
# ─────────────────────────────────────────────────────────────────────────────

# noinspection PyUnresolvedReferences
class InteractiveModifiedHierarchical:
    WORLD = (0, 100, 0, 100)
    MIN_DIST = 0.8

    # Цветовая схема (Catppuccin Mocha)
    C_BG = "#1e1e2e"
    C_PANEL = "#181825"
    C_INFO = "#313244"
    C_TEXT = "#cdd6f4"
    C_SUB = "#a6adc8"
    C_MUTED = "#585b70"
    C_BORDER = "#555555"

    C_EDGE_P1 = "#fab387"  # рёбра Прохода 1 (оранжевый)
    C_EDGE_DEL = "#89b4fa"  # рёбра Делоне (синий)
    C_EDGE_FLIP = "#f9e2af"  # перекидываемое ребро (жёлтый)
    C_PT = "#f38ba8"  # точки
    C_PT_INPUT = "#a6e3a1"  # точка из поля ввода
    C_HOVER = "#a6e3a155"
    C_HOVER_EC = "#a6e3a1"
    C_CIRC = "#f9e2af"

    def __init__(self, n_initial: int = 20):
        self.raw_points: List[Tuple[float, float]] = []
        self.dt: Optional[ModifiedHierarchical] = None

        # Режим отображения: "p1" | "p2"
        self._mode: str = "p2"
        # Текущий шаг прохода 2 (индекс flip, -1 = финал)
        self._flip_step: int = -1
        self.show_circles: bool = False
        self._last_input_pt: Optional[Tuple[float, float]] = None

        # ── Фигура ──────────────────────────────────────────────────────────
        self.fig = plt.figure(figsize=(11, 9.5))
        self.fig.patch.set_facecolor(self.C_BG)
        self.fig.canvas.manager.set_window_title(
            "Модифицированный иерархический алгоритм"
        )

        # Основной холст
        self.ax = self.fig.add_axes([0.06, 0.20, 0.70, 0.76])
        self.ax.set_facecolor(self.C_BG)
        self.ax.set_xlim(*self.WORLD[:2])
        self.ax.set_ylim(*self.WORLD[2:])
        self.ax.set_aspect("equal")
        self.ax.tick_params(colors="#aaaaaa")
        for sp in self.ax.spines.values():
            sp.set_color(self.C_BORDER)

        # Заголовок
        self.title = self.fig.text(
            0.41, 0.975, "", ha="center", fontsize=12,
            fontweight="bold", color=self.C_TEXT
        )

        # Инфо-панель
        self.info_text = self.ax.text(
            101, 98, "", va="top", ha="left",
            fontsize=8.5, color=self.C_TEXT, fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.4", fc=self.C_INFO,
                      ec="#555577", alpha=0.9)
        )

        # ── Слои рисования ──────────────────────────────────────────────────
        self._lc_edges = LineCollection([], colors=self.C_EDGE_DEL,
                                        linewidths=0.9, alpha=0.85)
        self._lc_flip = LineCollection([], colors=self.C_EDGE_FLIP,
                                       linewidths=2.5, alpha=1.0, zorder=5)
        self._sc_pts = self.ax.scatter([], [], s=22, c=self.C_PT,
                                       zorder=6, edgecolors=self.C_BG,
                                       linewidths=0.5)
        self._patch_hi = mpatches.Polygon(
            [[0, 0]], closed=True,
            fc=self.C_HOVER, ec=self.C_HOVER_EC, linewidth=1.5, zorder=4
        )
        self._sc_input_pt = self.ax.scatter(
            [], [], s=90, c=self.C_PT_INPUT, zorder=8,
            marker="*", edgecolors=self.C_BG, linewidths=0.5
        )
        self._circles_art: List = []

        self.ax.add_collection(self._lc_edges)
        self.ax.add_collection(self._lc_flip)
        self.ax.add_patch(self._patch_hi)

        # ── Нижняя панель виджетов ───────────────────────────────────────────
        panel_ax = self.fig.add_axes([0.0, 0.0, 1.0, 0.18])
        panel_ax.set_facecolor(self.C_PANEL)
        panel_ax.axis("off")

        self.fig.text(0.07, 0.155, "Координаты точки:",
                      color=self.C_TEXT, fontsize=9, va="bottom")

        # Поле X
        ax_x = self.fig.add_axes([0.07, 0.09, 0.13, 0.055])
        self._tb_x = TextBox(ax_x, "X: ", initial="",
                             color=self.C_INFO, hovercolor="#45475a",
                             label_pad=0.05)
        self._tb_x.label.set_color(self.C_TEXT)
        self._tb_x.text_disp.set_color(self.C_TEXT)
        self._tb_x.text_disp.set_fontsize(10)

        # Поле Y
        ax_y = self.fig.add_axes([0.25, 0.09, 0.13, 0.055])
        self._tb_y = TextBox(ax_y, "Y: ", initial="",
                             color=self.C_INFO, hovercolor="#45475a",
                             label_pad=0.05)
        self._tb_y.label.set_color(self.C_TEXT)
        self._tb_y.text_disp.set_color(self.C_TEXT)
        self._tb_y.text_disp.set_fontsize(10)

        # Кнопка «Добавить»
        ax_add = self.fig.add_axes([0.41, 0.085, 0.10, 0.065])
        self._btn_add = Button(ax_add, "Добавить",
                               color="#45475a", hovercolor="#585b70")
        self._btn_add.label.set_color(self.C_TEXT)
        self._btn_add.label.set_fontsize(9)
        self._btn_add.on_clicked(self._on_btn_add)

        # Кнопка «Сброс полей»
        ax_clr = self.fig.add_axes([0.53, 0.085, 0.08, 0.065])
        self._btn_clr = Button(ax_clr, "Сброс\nполей",
                               color=self.C_INFO, hovercolor="#45475a")
        self._btn_clr.label.set_color(self.C_SUB)
        self._btn_clr.label.set_fontsize(8)
        self._btn_clr.on_clicked(self._on_btn_clear_fields)

        # Кнопки «Проход 1» / «Проход 2»
        ax_p1 = self.fig.add_axes([0.63, 0.085, 0.08, 0.065])
        self._btn_p1 = Button(ax_p1, "Проход 1",
                              color=self.C_INFO, hovercolor="#45475a")
        self._btn_p1.label.set_color(self.C_EDGE_P1)
        self._btn_p1.label.set_fontsize(8)
        self._btn_p1.on_clicked(lambda _: self._set_mode("p1"))

        ax_p2 = self.fig.add_axes([0.73, 0.085, 0.08, 0.065])
        self._btn_p2 = Button(ax_p2, "Проход 2",
                              color=self.C_INFO, hovercolor="#45475a")
        self._btn_p2.label.set_color(self.C_EDGE_DEL)
        self._btn_p2.label.set_fontsize(8)
        self._btn_p2.on_clicked(lambda _: self._set_mode("p2"))

        # Кнопки «‹» / «›» (шаги flip)
        ax_prev = self.fig.add_axes([0.83, 0.085, 0.05, 0.065])
        self._btn_prev = Button(ax_prev, "◀",
                                color=self.C_INFO, hovercolor="#45475a")
        self._btn_prev.label.set_color(self.C_EDGE_FLIP)
        self._btn_prev.label.set_fontsize(12)
        self._btn_prev.on_clicked(self._on_prev_flip)

        ax_next = self.fig.add_axes([0.89, 0.085, 0.05, 0.065])
        self._btn_next = Button(ax_next, "▶",
                                color=self.C_INFO, hovercolor="#45475a")
        self._btn_next.label.set_color(self.C_EDGE_FLIP)
        self._btn_next.label.set_fontsize(12)
        self._btn_next.on_clicked(self._on_next_flip)

        # Сообщение об ошибке / успехе
        self._msg = self.fig.text(
            0.07, 0.025, "", color="#f38ba8", fontsize=8.5,
            fontfamily="monospace", va="bottom"
        )

        # Подсказка
        self.fig.text(
            0.41, 0.155,
            "ЛКМ: добавить   ПКМ: удалить   R: случайные   C: очистить   "
            "H: окружности   1/2: проход   ←/→: шаг перестройки",
            color=self.C_MUTED, fontsize=8, va="bottom"
        )

        # ── События ─────────────────────────────────────────────────────────
        # noinspection PyTypeChecker
        self.fig.canvas.mpl_connect("button_press_event", self._on_click)
        # noinspection PyTypeChecker
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        # noinspection PyTypeChecker
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self._tb_x.on_submit(lambda _: self._on_btn_add(None))
        self._tb_y.on_submit(lambda _: self._on_btn_add(None))

        # ── Начальные точки ─────────────────────────────────────────────────
        random.seed(7)
        self.raw_points = [
            (random.uniform(5, 95), random.uniform(5, 95))
            for _ in range(n_initial)
        ]
        self._rebuild()
        plt.show()

    # ── Вспомогательные ─────────────────────────────────────────────────────

    def _nearest_dist(self, x, y) -> Tuple[float, object]:
        if not self.raw_points:
            return float("inf"), None
        idx = min(range(len(self.raw_points)),
                  key=lambda i: math.hypot(self.raw_points[i][0] - x,
                                           self.raw_points[i][1] - y))
        pt = self.raw_points[idx]
        return math.hypot(pt[0] - x, pt[1] - y), pt

    def _set_msg(self, text: str, ok: bool):
        self._msg.set_text(text)
        self._msg.set_color("#a6e3a1" if ok else "#f38ba8")
        self.fig.canvas.draw_idle()

    def _set_mode(self, mode: str):
        self._mode = mode
        if mode == "p2":
            self._flip_step = -1  # финальная триангуляция
        self._redraw()

    # ── Добавление точки ────────────────────────────────────────────────────

    # noinspection PyUnresolvedReferences
    def _try_add_point(self, x: float, y: float,
                       from_input: bool = False) -> bool:
        dist, near = self._nearest_dist(x, y)
        if dist < self.MIN_DIST:
            self._set_msg(
                f"✗  Слишком близко к ({near[0]:.2f}, {near[1]:.2f})"
                f" — расстояние {dist:.3f} < {self.MIN_DIST}",
                ok=False
            )
            return False
        if not (self.WORLD[0] <= x <= self.WORLD[1] and
                self.WORLD[2] <= y <= self.WORLD[3]):
            self._set_msg(
                f"✗  Точка ({x:.2f}, {y:.2f}) вне области "
                f"[{self.WORLD[0]}, {self.WORLD[1]}] × [{self.WORLD[2]}, {self.WORLD[3]}]",
                ok=False
            )
            return False
        self.raw_points.append((x, y))
        if from_input:
            self._last_input_pt = (x, y)
            self._set_msg(f"✓  Точка добавлена: ({x:.4f}, {y:.4f})", ok=True)
        else:
            self._last_input_pt = None
            self._set_msg("", ok=True)
        self._rebuild()
        return True

    # ── Парсинг полей ────────────────────────────────────────────────────────

    def _parse_fields(self) -> Optional[Tuple[float, float]]:
        raw_x = self._tb_x.text.strip().replace(",", ".")
        raw_y = self._tb_y.text.strip().replace(",", ".")
        try:
            return float(raw_x), float(raw_y)
        except ValueError:
            return None

    def _on_btn_add(self, _event):
        result = self._parse_fields()
        if result is None:
            self._set_msg(
                f"✗  Ошибка: введите числа в оба поля"
                f"  (X='{self._tb_x.text}'  Y='{self._tb_y.text}')",
                ok=False
            )
            return
        if self._try_add_point(*result, from_input=True):
            self._tb_x.set_val("")
            self._tb_y.set_val("")
        # noinspection PyUnresolvedReferences
        self.fig.canvas.get_tk_widget().focus_set()

    def _on_btn_clear_fields(self, _event):
        self._tb_x.set_val("")
        self._tb_y.set_val("")
        self._last_input_pt = None
        self._set_msg("", ok=True)
        self._update_input_marker()
        self.fig.canvas.draw_idle()

    # ── Шаги по flip-ам ─────────────────────────────────────────────────────

    def _on_prev_flip(self, _=None):
        if not self.dt or self.dt.n_flips() == 0:
            return
        self._mode = "p2"
        if self._flip_step == -1:
            self._flip_step = self.dt.n_flips() - 1
        else:
            self._flip_step = max(0, self._flip_step - 1)
        self._redraw()

    def _on_next_flip(self, _=None):
        if not self.dt or self.dt.n_flips() == 0:
            return
        self._mode = "p2"
        if self._flip_step == -1:
            return
        self._flip_step += 1
        if self._flip_step >= self.dt.n_flips():
            self._flip_step = -1
        self._redraw()

    # ── Перестройка ─────────────────────────────────────────────────────────

    def _rebuild(self):
        self._flip_step = -1
        if len(self.raw_points) >= 3:
            self.dt = ModifiedHierarchical(self.raw_points)
        else:
            self.dt = None
        self._redraw()

    # ── Перерисовка ─────────────────────────────────────────────────────────

    def _redraw(self):
        import numpy as np

        # Выбрать набор треугольников и цвет рёбер
        flip_edge = None
        if self._mode == "p1" or not self.dt:
            tris_draw = self.dt.triangles_pass1() if self.dt else []
            edge_color = self.C_EDGE_P1
        else:
            # Режим П2
            if self._flip_step == -1 or not self.dt or self.dt.n_flips() == 0:
                tris_draw = self.dt.triangles_final() if self.dt else []
            else:
                fr = self.dt.flips[self._flip_step]
                tris_draw = [t for t in fr.snap_before
                             if not any(v.is_super for v in t)]
                flip_edge = fr.edge_old
            edge_color = self.C_EDGE_DEL

        self._lc_edges.set_color(edge_color)

        # Рёбра треугольников
        segments = []
        for (a, b, c) in tris_draw:
            segments.append([(a.x, a.y), (b.x, b.y)])
            segments.append([(b.x, b.y), (c.x, c.y)])
            segments.append([(a.x, a.y), (c.x, c.y)])
        self._lc_edges.set_segments(segments)

        # Подсвеченное перекидываемое ребро
        if flip_edge:
            ea, eb = flip_edge
            self._lc_flip.set_segments([[(ea.x, ea.y), (eb.x, eb.y)]])
        else:
            self._lc_flip.set_segments([])

        # Точки
        if self.raw_points:
            xs, ys = zip(*self.raw_points)
            self._sc_pts.set_offsets(list(zip(xs, ys)))
        else:
            self._sc_pts.set_offsets(np.empty((0, 2)))
        self._update_input_marker()

        # Описанные окружности
        for art in self._circles_art:
            art.remove()
        self._circles_art.clear()
        if self.show_circles and self.dt:
            for (a, b, c) in self.dt.triangles_final():
                ctr, r = circumcenter(a.x, a.y, b.x, b.y, c.x, c.y)
                if ctr:
                    circ = Circle(ctr, r, fill=False,
                                  edgecolor=self.C_CIRC,
                                  linewidth=0.5, alpha=0.35)
                    self.ax.add_patch(circ)
                    self._circles_art.append(circ)

        # Инфо-панель
        n = len(self.raw_points)
        if self.dt:
            t1 = len(self.dt.triangles_pass1())
            t2 = len(self.dt.triangles_final())
            nf = self.dt.n_flips()
        else:
            t1 = t2 = nf = 0

        mode_str = "Проход 1 (без Делоне)" if self._mode == "p1" else "Проход 2 (Делоне)"
        if self._mode == "p2" and self._flip_step >= 0:
            step_str = f"flip {self._flip_step + 1}/{nf}"
        elif self._mode == "p2":
            step_str = "финал"
        else:
            step_str = ""

        self.info_text.set_text(
            f"Точек        : {n}\n"
            f"─────────────────────\n"
            f"П1 треуг.    : {t1}\n"
            f"П2 треуг.    : {t2}\n"
            f"Ожидаемо     : {max(0, 2 * n - 2)}\n"
            f"─────────────────────\n"
            f"Flip-ов П2   : {nf}\n"
            f"─────────────────────\n"
            f"Режим : {mode_str}\n"
            + (f"Шаг   : {step_str}\n" if step_str else "")
            + f"─────────────────────\n"
              f"[H] Окружн.  : {'вкл' if self.show_circles else 'выкл'}\n"
              f"[1/2] Проход : {'1' if self._mode == 'p1' else '2'}"
        )

        # Заголовок
        self.title.set_text(
            "Триангуляция Делоне — модифицированный иерархический алгоритм"
        )

        self.fig.canvas.draw_idle()

    def _update_input_marker(self):
        import numpy as np
        if self._last_input_pt:
            self._sc_input_pt.set_offsets([self._last_input_pt])
        else:
            self._sc_input_pt.set_offsets(np.empty((0, 2)))

    # ── Hover-подсветка треугольника ────────────────────────────────────────

    def _on_motion(self, event):
        if event.inaxes is not self.ax or not self.dt:
            self._patch_hi.set_visible(False)
            self.fig.canvas.draw_idle()
            return

        px, py = event.xdata, event.ydata

        if self._mode == "p1":
            tris = self.dt.triangles_pass1()
        elif self._flip_step >= 0:
            fr = self.dt.flips[self._flip_step]
            tris = [t for t in fr.snap_before if not any(v.is_super for v in t)]
        else:
            tris = self.dt.triangles_final()

        found = None
        for (a, b, c) in tris:
            if pt_in_tri(px, py, a.x, a.y, b.x, b.y, c.x, c.y):
                found = (a, b, c)
                break

        if found:
            a, b, c = found
            self._patch_hi.set_xy([(a.x, a.y), (b.x, b.y), (c.x, c.y)])
            self._patch_hi.set_visible(True)
        else:
            self._patch_hi.set_visible(False)
        self.fig.canvas.draw_idle()

    # ── Клики мыши ──────────────────────────────────────────────────────────

    def _on_click(self, event):
        if event.inaxes is not self.ax:
            return
        x, y = event.xdata, event.ydata
        if event.button == 1:
            self._try_add_point(x, y, from_input=False)
        elif event.button == 3:
            if not self.raw_points:
                return
            idx = min(range(len(self.raw_points)),
                      key=lambda i: math.hypot(
                          self.raw_points[i][0] - x, self.raw_points[i][1] - y))
            removed = self.raw_points.pop(idx)
            if self._last_input_pt == removed:
                self._last_input_pt = None
            self._rebuild()

    # ── Клавиатура ──────────────────────────────────────────────────────────

    def _on_key(self, event):
        key = (event.key or "").lower()
        if key == "r":
            random.seed(random.randint(0, 9999))
            n = max(10, len(self.raw_points))
            self.raw_points = [
                (random.uniform(5, 95), random.uniform(5, 95))
                for _ in range(n)
            ]
            self._last_input_pt = None
            self._set_msg("", ok=True)
            self._rebuild()
        elif key == "c":
            self.raw_points.clear()
            self._last_input_pt = None
            self._set_msg("", ok=True)
            self._rebuild()
        elif key == "h":
            self.show_circles = not self.show_circles
            self._redraw()
        elif key == "1":
            self._set_mode("p1")
        elif key == "2":
            self._set_mode("p2")
        elif key in ("left", "a"):
            self._on_prev_flip()
        elif key in ("right", "d"):
            self._on_next_flip()


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    InteractiveModifiedHierarchical(n_initial=20)
