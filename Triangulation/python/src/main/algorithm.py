from geom import *
from typing import Tuple

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