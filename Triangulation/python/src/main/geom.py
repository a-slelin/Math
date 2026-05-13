import math
from typing import List, Dict


class Point:
    """Класс точки"""

    __slots__ = ("x", "y", "id")

    # noinspection PyShadowingBuiltins
    def __init__(self, x: float, y: float, id: int = -1):
        self.x, self.y, self.id = x, y, id

    def __repr__(self):
        return f'P{self.id}({self.x:.1f},{self.y:.1f})'

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


class Mesh:
    """Класс графа смежности"""

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
