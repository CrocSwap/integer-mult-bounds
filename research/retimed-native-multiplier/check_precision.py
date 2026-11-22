"""Audit the Gaussian transport reserve against the two literal finite programs."""
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from math import gcd
import gzip
import json


def loadp(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def digest(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class Bound:
    def __init__(self, height=0, mass=Q(1)):
        self.height, self.mass = height, mass

    def __add__(self, other):
        return Bound(max(self.height, other.height), self.mass + other.mass)

    def scaled(self, re, im=0):
        re, im = Q(re), Q(im)
        val2 = lambda n: (n & -n).bit_length() - 1
        return Bound(self.height + max(val2(re.denominator), val2(im.denominator)),
                     self.mass * (abs(re) + abs(im)))


def audit_mixed(events, n):
    rows = [Bound() for _ in range(n)]
    mixed_height = graph_height = 0
    mixed_mass = graph_mass = Q(1)

    def see(*values):
        nonlocal mixed_mass, mixed_height
        for value in values:
            mixed_height = max(mixed_height, value.height)
            mixed_mass = max(mixed_mass, value.mass)
        return values[-1]

    for kind, dst, *args in events:
        if kind.startswith("HOST"):
            inputs = [rows[j] for j in args]
            graph_mass = max(graph_mass, *(v.mass for v in inputs))
            graph_height = max(graph_height, *(v.height for v in inputs))
            if kind == "HOST_A":
                x, y, u, v = args
                rows[y] = see(rows[y] + rows[x])
                rows[u] = see(rows[u] + rows[v])
            else:
                x, y = args
                one = rows[x] + rows[y]
                half = rows[x].scaled(Q(1, 2)) + rows[y].scaled(Q(1, 2))
                rows[x], rows[y] = see(one), see(half)
        elif kind == "SWAP":
            i, = args
            rows[i], rows[dst] = rows[dst], rows[i]
        elif kind in ("ADD", "SCALE"):
            operand = rows[args[0]] if kind == "ADD" else rows[dst]
            scaled = see(operand.scaled(*args[-1]))
            rows[dst] = see(rows[dst] + scaled) if kind == "ADD" else scaled
        elif kind == "QUERY":
            rows[dst] = see(rows[dst] + rows[args[0]])
        elif kind == "LAMBDA":
            half = see(rows[dst].scaled(Q(1, 2), Q(1, 2)))
            rows[dst] = see(half + half)
        else:
            assert kind in ("IDLE_ONE", "IDLE_ODD")
    return mixed_height, graph_height, mixed_mass, graph_mass


def graph_bound(graph):
    mass = {~i: Q(1) for i in range(len(graph["initial"]))}
    edges = dict(graph["forms"])
    peak = Q(1)
    terms = literal_bits = 0
    for vertex in graph["schedule"]:
        total = Q(0)
        for donor, literal in edges[vertex]:
            scalar = Q(literal)
            literal_bits = max(literal_bits, abs(scalar.numerator).bit_length(), scalar.denominator.bit_length())
            total += mass[donor] * abs(scalar)
        mass[vertex] = total
        terms += len(edges[vertex])
        peak = max(peak, total)
    return peak, terms, literal_bits


def audit():
    from upstream import HERE, install
    _, _, _, src = install()
    retained = src / "research/grade14-native-realization/retained"
    from strong_complex import load_changed
    from closed_caller import templates
    from mixed_grid import exact
    from check_strong_complex import literal_grid
    from strong_complex import GRID, WORD, ODD, DYADIC, LAYOUT

    g, layout = load_changed(HERE / "inputs")
    assert digest(g) == WORD and digest(layout) == LAYOUT
    local, terms, literal = graph_bound(g)
    signed = literal_grid(g, layout)
    assert local == Q(signed["peak"]) and signed["literal_width_with_odd"] == 87
    print("graph", terms, "edges", literal, "direct scalar bits", signed["products"], "basis products",
          signed["nontrivial"], "nontrivial separate divisions", flush=True)

    drops, masses = [], []
    for name, (events, diagonal) in templates(loadp(retained / "data/CALLER.json.gz")).items():
        receipt = exact(events, diagonal, 2025 << 9)
        assert receipt == exact(events, diagonal, receipt["minimum_grid"])
        d, b, m, n = audit_mixed(events, len(diagonal))
        drop = max(d, b+DYADIC)
        mass = max(2025*m, 2025*n*ODD*local)
        drops.append(drop)
        masses.append(mass)
        print(name, "source signed grid", receipt["minimum_grid"], "height/entrance", d, b,
              "Mell", drop, "ceil-log-mass", ((mass.numerator-1)//mass.denominator).bit_length())
    assert max(drops) == 148
    big = max(masses)
    assert 2**435 < big < 2**436
    assert GRID == ODD << DYADIC
    profiles = ((3000, 14), (13000, 14), (36000, 17))
    for h, d in profiles:
        assert 872*(4*h+1) < 1 << h
        assert 66+(6+77)*h < 92*h
        assert 96*h + 92*h + h + 100 < 191*h
        assert 700*h + 200 < (1 << (h-2))
        assert 16*(h+2) + 200 < h*h//2
    print("bound per causal raw context", max(drops), 436)
    print("all listed profiles satisfy the finite reserve and clock inequalities")


if __name__ == "__main__":
    audit()
