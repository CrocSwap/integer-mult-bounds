#!/usr/bin/env python3
"""Exact minimum hosting charges of the P104 frame-indicator rows.

Setting (inherited from PR #7031 / #7047): the 120 root lines of E8 carry chart
points in F_2^8 (simple-root coordinates mod 2). A *host* of a row is a Boolean
function f on F_2^8 that equals the row's indicator on the root-line points; its
*charge* is the number of monomials of degree >= 2 in its algebraic normal form
(ANF) in the chart coordinates x0..x7. Affine terms are free, as in #7031/#7047.

Facts checked here, all by exhaustive enumeration:
  * the 120 chart points are exactly {x : Q(x) = 1} for the chart's quadratic form;
  * each of the 15 odd 8-cliques (13 P104 frames, 2 excluded) is a coset of a
    3-dimensional subspace W_F;
  * no host of degree <= 2 exists for any row (a 3-flat inside the root lines meets
    the row in one point, and every polynomial of degree <= 2 sums to 0 on a 3-flat);
  * the four #7031 forms (p, q, r, s) miss exactly one of their 16 values on the 120
    lines, so exactly two functions of them host frame 0: charge 40 and charge 16;
  * exact minima over W_F-invariant functions (the five flat indicators are among
    them) and over all hosts of degree <= 3, on the 120-line scope and on the 104
    P104-line scope; the five flat charges are listed on the 120-line scope;
  * a letter-product baseline and explicit sparser hosts (data/hosts_*.json), each
    re-evaluated at every scope point.

Checks are need() failures, so python -O still runs them. No claim is made about
the minimum over all Boolean functions, about sums of products, or about kappa.
"""

import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
FRAMES_SHA256 = "c75915c18fc06ac19cc90fb9911209517c071862fdf401b998d5075efc0cda0d"
N = 8
SIZE = 1 << N
FRAME0_PORTS = (11, 21, 38, 56, 140, 146, 161, 191)

# Expected exact results (each is recomputed below and compared).
# per clique index 0..14: (sorted (|G|, charge) of the five flat hosts, invariant min, cubic min)
EXPECT_T120 = {
    0: ([(8, 63), (16, 39), (16, 39), (16, 40), (32, 16)], 16, 14),
    1: ([(8, 46), (16, 24), (16, 60), (16, 111), (32, 51)], 24, 24),
    2: ([(8, 42), (16, 26), (16, 58), (16, 89), (32, 49)], 26, 26),
    3: ([(8, 40), (16, 34), (16, 46), (16, 105), (32, 51)], 34, 22),
    4: ([(8, 48), (16, 36), (16, 44), (16, 83), (32, 39)], 36, 24),
    5: ([(8, 18), (16, 10), (16, 54), (16, 93), (32, 45)], 10, 18),
    6: ([(8, 102), (16, 35), (16, 84), (16, 84), (32, 27)], 27, 23),
    7: ([(8, 16), (16, 20), (16, 40), (16, 101), (32, 41)], 16, 14),
    8: ([(8, 58), (16, 42), (16, 54), (16, 111), (32, 51)], 42, 30),
    9: ([(8, 28), (16, 30), (16, 36), (16, 103), (32, 53)], 28, 28),
    10: ([(8, 24), (16, 26), (16, 40), (16, 107), (32, 49)], 24, 24),
    11: ([(8, 89), (16, 57), (16, 58), (16, 59), (32, 28)], 28, 21),
    12: ([(8, 21), (16, 13), (16, 49), (16, 90), (32, 42)], 13, 17),
    13: ([(8, 60), (16, 11), (16, 44), (16, 48), (32, 7)], 7, 7),
    14: ([(8, 40), (16, 34), (16, 40), (16, 87), (32, 53)], 34, 30),
}
# The unique minimiser among frame 0's hosts of degree <= 3 (charge 14), monomials in mask order.
EXPECT_FRAME0_CUBIC = (
    "1 + x0 + x1 + x2 + x0*x2 + x0*x3 + x0*x1*x3 + x0*x2*x3 + x4 + x0*x3*x4 + x5 + x1*x5 + x0*x1*x5 + "
    "x2*x5 + x0*x2*x5 + x4*x5 + x6 + x5*x6 + x7 + x5*x7 + x0*x5*x7 + x0*x6*x7"
)
# Product-of-letters hosting words of #7031: the charge of the indicator of span(F).
EXPECT_LETTER_BASELINE = [40, 111, 89, 105, 83, 93, 35, 101, 111, 103, 107, 58, 90, 11, 87]
# Charges of the explicit hosts in data/hosts_*.json (search.py, 3000 orders per row, seed 20261110).
EXPECT_SEARCHED_T120 = [14, 20, 20, 22, 22, 6, 23, 10, 26, 18, 14, 21, 9, 7, 20]
EXPECT_SEARCHED_P104 = [14, 18, 16, 22, 19, 6, 23, 10, 23, 16, 14, 21, 9]
# 104-line scope (frames 0..12 only): (invariant min, cubic min)
EXPECT_P104 = {
    0: (15, 14), 1: (24, 24), 2: (26, 23), 3: (34, 22), 4: (36, 21), 5: (10, 18),
    6: (27, 23), 7: (16, 14), 8: (42, 30), 9: (28, 28), 10: (24, 24), 11: (28, 21),
    12: (13, 17),
}


def need(condition, message):
    if not condition:
        raise SystemExit(message)


# --------------------------------------------------------------------------- chart
def e8_roots():
    roots = []
    for left, right in combinations(range(8), 2):
        for sl in (1, -1):
            for sr in (1, -1):
                vector = [0] * 8
                vector[left] = 2 * sl
                vector[right] = 2 * sr
                roots.append(tuple(vector))
    for signs in product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(signs))
    return roots


def simple_basis():
    basis = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0), (-2, 2, 0, 0, 0, 0, 0, 0)]
    for index in range(1, 6):
        vector = [0] * 8
        vector[index] = -2
        vector[index + 1] = 2
        basis.append(tuple(vector))
    return basis


def dot(left, right):
    return sum(a * b for a, b in zip(left, right)) // 4


def solve_coordinates(matrix, target):
    rows = [[Fraction(entry) for entry in matrix[i]] + [Fraction(target[i])] for i in range(8)]
    for column in range(8):
        pivot = next(row for row in range(column, 8) if rows[row][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = 1 / rows[column][column]
        rows[column] = [entry * scale for entry in rows[column]]
        for row in range(8):
            if row != column and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [rows[row][c] - factor * rows[column][c] for c in range(9)]
    solution = [rows[i][8] for i in range(8)]
    need(all(entry.denominator == 1 for entry in solution), "root coordinates are not integral")
    return tuple(int(entry) for entry in solution)


def negate(vector):
    return tuple(-entry for entry in vector)


def load_geometry():
    """Return (cartan, chart points of the 120 lines, port -> line position)."""
    basis = simple_basis()
    matrix = list(zip(*basis))
    cartan = [[dot(basis[i], basis[j]) for j in range(8)] for i in range(8)]
    lines, seen = [], set()
    for root in e8_roots():
        key = root if root > negate(root) else negate(root)
        if key not in seen:
            seen.add(key)
            lines.append(root)
    need(len(lines) == 120, "expected 120 root lines")
    points = []
    for root in lines:
        bits = 0
        for index, value in enumerate(solve_coordinates(matrix, root)):
            if value & 1:
                bits |= 1 << index
        points.append(bits)
    need(len(set(points)) == 120, "chart points of the root lines are not distinct")
    line_map = json.loads((REPO / "research/p104-port-window-haemers/data/e8_line_map.json").read_text())
    ports_p104 = json.loads((REPO / "research/p104-port-window-haemers/data/ports_p104.json").read_text())["ports"]
    need(len(ports_p104) == 104 and len(set(ports_p104)) == 104, "expected 104 distinct P104 ports")
    index = {}
    for position, root in enumerate(lines):
        index[root] = position
        index[negate(root)] = position
    port_position = {}
    for vector, root in zip(line_map["vectors"], line_map["roots2"]):
        port_position[vector] = index[tuple(root)]
    need(len(port_position) == 120 and len(set(port_position.values())) == 120, "line map is not a bijection")
    frame_bytes = (ROOT / "data" / "frames.json").read_bytes()
    need(hashlib.sha256(frame_bytes).hexdigest() == FRAMES_SHA256, "frames.json sha256 mismatch")
    frames_doc = json.loads(frame_bytes.decode())
    frames = frames_doc["frames"]
    excluded = frames_doc["excluded_odd_cliques"]
    need(len(frames) == 13 and len(excluded) == 2, "expected 13 frames and 2 excluded cliques")
    need(tuple(frames[0]) == FRAME0_PORTS, "frame 0 ports changed")
    need(set(ports_p104) == {p for frame in frames for p in frame}, "frames do not partition the P104 ports")
    cliques = [tuple(c) for c in frames] + [tuple(c) for c in excluded]
    need(sorted(p for c in cliques for p in c) == sorted(line_map["vectors"]), "cliques do not partition 120 lines")
    return cartan, points, port_position, cliques


# ------------------------------------------------------------- boolean functions
# A function on F_2^8 is a 256-bit integer truth table (bit x is f(x)); its ANF is
# a 256-bit integer whose bit m says that the square-free monomial prod_{i in m} x_i
# occurs. The two are related by the (involutive) subset-sum transform.
LOW = [sum(1 << m for m in range(SIZE) if not (m >> j) & 1) for j in range(N)]
GE2 = sum(1 << m for m in range(SIZE) if bin(m).count("1") >= 2)


def mobius(table):
    for j in range(N):
        table ^= (table & LOW[j]) << (1 << j)
    return table


def table_of(points):
    table = 0
    for point in points:
        table |= 1 << point
    return table


def charge(anf):
    return (anf & GE2).bit_count()


def eval_anf(anf, point):
    """f(point) read directly from the ANF (independent of the transform)."""
    value = 0
    for m in range(SIZE):
        if (anf >> m) & 1 and m & ~point == 0:
            value ^= 1
    return value


def poly_mul(left, right):
    """Product of two ANFs (sets of monomial masks) over F_2 with x_i^2 = x_i."""
    out = set()
    for a in left:
        for b in right:
            out ^= {a | b}
    return out


def anf_set(anf):
    return {m for m in range(SIZE) if (anf >> m) & 1}


def anf_int(monomials):
    value = 0
    for m in monomials:
        value ^= 1 << m
    return value


def monomial_name(mask):
    return "1" if mask == 0 else "*".join("x%d" % i for i in range(N) if (mask >> i) & 1)


def f2_span(vectors):
    span = {0}
    for vector in vectors:
        if vector not in span:
            span |= {s ^ vector for s in span}
    return span


def f2_rank(vectors):
    basis = {}
    for vector in vectors:
        x = vector
        while x:
            top = x.bit_length() - 1
            if top in basis:
                x ^= basis[top]
            else:
                basis[top] = x
                break
    return len(basis)


def quadratic_form(cartan):
    edges = [(i, j) for i in range(8) for j in range(i + 1, 8) if cartan[i][j] & 1]
    need(len(edges) == 7, "the E8 diagram has 7 edges")
    def q(x):
        return (bin(x).count("1") + sum(((x >> i) & (x >> j)) & 1 for i, j in edges)) & 1
    return q, edges


def all_subspaces(dimension):
    subspaces = {frozenset([0])}
    frontier = [frozenset([0])]
    while frontier:
        new = []
        for space in frontier:
            for vector in range(1, 1 << dimension):
                if vector not in space:
                    bigger = frozenset(space | {s ^ vector for s in space})
                    if bigger not in subspaces:
                        subspaces.add(bigger)
                        new.append(bigger)
        frontier = new
    return subspaces


# ----------------------------------------------------------- per-clique analysis
class Clique:
    """Quotient data of F_2^8 by the translation space W_F of a clique F."""

    def __init__(self, points_of_clique):
        self.points = sorted(points_of_clique)
        self.set = set(self.points)
        anchor = self.points[0]
        self.anchor = anchor
        self.direction = f2_span([x ^ anchor for x in self.points[1:]])
        need(len(self.direction) == 8, "a clique is not a coset of a 3-dimensional subspace")
        need({anchor ^ w for w in self.direction} == self.set, "a clique is not a full coset")
        reps = sorted({min(x ^ w for w in self.direction) for x in range(SIZE)})
        need(len(reps) == 32, "expected 32 cosets")
        basis, span = [], set(self.direction)
        for rep in reps:
            if rep not in span:
                basis.append(rep)
                span |= {s ^ rep for s in span}
            if len(basis) == 5:
                break
        need(len(span) == SIZE, "coset representatives do not span F_2^8")
        self.coset_of = {}
        for z in range(32):
            vector = 0
            for i in range(5):
                if (z >> i) & 1:
                    vector ^= basis[i]
            for w in self.direction:
                self.coset_of[vector ^ w] = z
        self.cosets = {z: [x for x in range(SIZE) if self.coset_of[x] == z] for z in range(32)}
        self.z0 = self.coset_of[anchor]


def invariant_class(clique, scope):
    """All W_F-invariant hosts on `scope`: base indicator of F plus free cosets."""
    touched = Counter(clique.coset_of[x] for x in scope if x not in clique.set)
    need(clique.z0 not in touched, "the clique's coset meets another scope point")
    free = [z for z in range(32) if z != clique.z0 and z not in touched]
    base = mobius(table_of(clique.cosets[clique.z0]))
    deltas = [mobius(table_of(clique.cosets[z])) for z in free]
    current, hosts = base, [base]
    for index in range(1, 1 << len(free)):
        current ^= deltas[(index & -index).bit_length() - 1]
        hosts.append(current)
    return free, hosts


def flat_hosts(clique, scope, subspaces5):
    """Flat indicators G (containing F) with G meeting `scope` only inside F."""
    found = []
    for space in subspaces5:
        flat = [x for z in space for x in clique.cosets[z ^ clique.z0]]
        if all(x not in scope or x in clique.set for x in flat):
            found.append((len(flat), charge(mobius(table_of(flat))), anf_set(mobius(table_of(flat)))))
    found.sort(key=lambda item: (item[0], item[1]))
    return found


def check_host(anf, clique, scope):
    """Evaluate the ANF directly at every scope point and compare with the indicator."""
    monomials = [m for m in range(SIZE) if (anf >> m) & 1]
    for x in scope:
        value = 0
        for m in monomials:
            if m & ~x == 0:
                value ^= 1
        need(value == (1 if x in clique.set else 0), "a claimed host disagrees with the indicator")


def solve_f2(rows, rhs, unknowns):
    """Return (particular solution, null-space basis) over F_2, or None if inconsistent."""
    pivots = {}
    for row, value in zip(rows, rhs):
        x, y = row, value
        while x:
            top = x.bit_length() - 1
            if top in pivots:
                px, py = pivots[top]
                x ^= px
                y ^= py
            else:
                pivots[top] = (x, y)
                break
        else:
            if y:
                return None
    for p in sorted(pivots):
        xp, yp = pivots[p]
        for q in list(pivots):
            if q != p and (pivots[q][0] >> p) & 1:
                pivots[q] = (pivots[q][0] ^ xp, pivots[q][1] ^ yp)
    free = [c for c in range(unknowns) if c not in pivots]
    particular = 0
    for p, (x, y) in pivots.items():
        if y:
            particular |= 1 << p
    null = []
    for f in free:
        vector = 1 << f
        for p, (x, y) in pivots.items():
            if (x >> f) & 1:
                vector |= 1 << p
        null.append(vector)
    return particular, null


def low_degree_hosts(clique, scope, degree):
    """All hosts of degree <= `degree` as ANF integers, or None if there is none."""
    monomials = [m for m in range(SIZE) if bin(m).count("1") <= degree]
    column = {m: i for i, m in enumerate(monomials)}
    rows, rhs = [], []
    for x in scope:
        row = 0
        for m in monomials:
            if m & ~x == 0:
                row |= 1 << column[m]
        rows.append(row)
        rhs.append(1 if x in clique.set else 0)
    solved = solve_f2(rows, rhs, len(monomials))
    if solved is None:
        return None
    particular, null = solved

    def lift(vector):
        anf = 0
        for m, i in column.items():
            if (vector >> i) & 1:
                anf |= 1 << m
        return anf

    base = lift(particular)
    deltas = [lift(v) for v in null]
    current, hosts = base, [base]
    for index in range(1, 1 << len(deltas)):
        current ^= deltas[(index & -index).bit_length() - 1]
        hosts.append(current)
    return hosts, len(deltas)


def three_flat_certificate(clique, quad):
    """A 3-flat S inside the 120 lines with |S ∩ F| = 1.

    S = a + U with a in F and U a 3-dimensional subspace, U ∩ W_F = {0}, on which
    Q(a + u) = 1 for every u in U. Then sum_{x in S} 1_F(x) = 1, while every
    polynomial of degree <= 2 sums to 0 over a 3-flat.
    """
    a = clique.anchor
    good = [w for w in range(1, SIZE) if quad(a ^ w) == 1]
    good_set = set(good)
    for d1 in good:
        if d1 in clique.direction:
            continue
        for d2 in good:
            if d2 <= d1 or (d1 ^ d2) not in good_set or d2 in clique.direction:
                continue
            if (d1 ^ d2) in clique.direction:
                continue
            for d3 in good:
                if d3 <= d2:
                    continue
                span = f2_span([d1, d2, d3])
                if len(span) != 8 or span & clique.direction != {0}:
                    continue
                if all(w == 0 or w in good_set for w in span):
                    return a, (d1, d2, d3), sorted(a ^ w for w in span)
    return None


def check_structure(quad, lines_t, clique_data):
    """Lemma behind the 28 + 3 + 1 coset pattern, checked on every clique.

    Let F = a + W be an odd 8-clique and B(x, y) = Q(x+y) + Q(x) + Q(y). Since Q = 1
    on F, Q(a + w) = 1 for w in W, so W is totally isotropic and Q(w) = B(a, w).
    For a coset c + W, Q(c + w) = Q(c) + B(a + c, w): constant if a + c lies in the
    5-dimensional space W-perp, otherwise a non-constant affine function that takes
    each value on exactly 4 of the 8 points. The translate Q'(x) = Q(a + x) + Q(a)
    has 120 zeros, so it is elliptic; W is totally singular for Q', hence maximal,
    and W-perp / W is anisotropic, so Q' = 1 on W-perp minus W. Therefore the 4
    cosets inside a + W-perp are F (8 lines) and 3 cosets with no root line, and the
    other 28 cosets hold 4 lines each: 8 + 28 * 4 = 120.
    """
    def polar(x, y):
        return quad(x ^ y) ^ quad(x) ^ quad(y)

    for index, clique in enumerate(clique_data):
        a = clique.anchor
        perp = [u for u in range(SIZE) if all(polar(u, w) == 0 for w in clique.direction)]
        need(len(perp) == 32 and all(w in perp for w in clique.direction), "W-perp has the wrong size")
        for w in clique.direction:
            need(quad(a ^ w) == 1, "Q is not 1 on a clique")
            need(all(polar(w, v) == 0 for v in clique.direction), "W is not totally isotropic")
        need(sum(1 for x in range(SIZE) if quad(a ^ x) ^ quad(a) == 0) == 120, "Q' is not elliptic")
        biggest = {a ^ u for u in perp}
        need(biggest & lines_t == clique.set, "a + W-perp meets the lines outside the clique")
        sizes = Counter(sum(1 for x in clique.cosets[z] if x in lines_t) for z in range(32))
        need(dict(sizes) == {8: 1, 4: 28, 0: 3}, "coset pattern changed for clique %d: %s" % (index, dict(sizes)))
        inside = {clique.coset_of[x] for x in biggest}
        need(len(inside) == 4 and all(sum(1 for x in clique.cosets[z] if x in lines_t) in (0, 8) for z in inside),
             "the four cosets of a + W-perp are not F and three empty cosets")
        for z in range(32):
            if z not in inside:
                ones = [quad(x) for x in clique.cosets[z]]
                need(sorted(ones) == [0] * 4 + [1] * 4, "a coset outside W-perp is not balanced")
    return True


def main(argv):
    cartan, points, port_position, cliques = load_geometry()
    quad, edges = quadratic_form(cartan)
    lines_t = set(points)
    need({x for x in range(SIZE) if quad(x)} == lines_t, "the 120 chart points are not {Q = 1}")
    p104 = {points[port_position[p]] for c in cliques[:13] for p in c}
    need(len(p104) == 104 and len(lines_t - p104) == 16, "P104 scope sizes changed")
    clique_data = [Clique({points[port_position[p]] for p in c}) for c in cliques]
    subspaces5 = all_subspaces(5)
    need(len(subspaces5) == 374, "subspace count of F_2^5 changed")
    check_structure(quad, lines_t, clique_data)

    # ---- frame 0 four-form class (open question 2 of #7047)
    p_form = lambda x: 1 ^ ((x >> 1) & 1) ^ ((x >> 2) & 1) ^ ((x >> 4) & 1)
    q_form = lambda x: x & 1
    r_form = lambda x: (x >> 5) & 1
    s_form = lambda x: ((x >> 6) & 1) ^ ((x >> 7) & 1)
    image, fibres = {}, {}
    frame0 = clique_data[0]
    for x in lines_t:
        key = (p_form(x), q_form(x), r_form(x), s_form(x))
        image.setdefault(key, set()).add(1 if x in frame0.set else 0)
        fibres[key] = fibres.get(key, 0) + 1
    need(all(len(v) == 1 for v in image.values()), "the indicator is not constant on a four-form fibre")
    missing = [(a, b, c, d) for a in (0, 1) for b in (0, 1) for c in (0, 1) for d in (0, 1) if (a, b, c, d) not in image]
    need(missing == [(0, 0, 0, 1)], "missing four-form fibres changed: %s" % (missing,))
    need(set(fibres.values()) == {8}, "every attained four-form fibre should hold 8 lines")
    # explicit expansions by polynomial multiplication (independent of the transform)
    one = {0}
    P = {0, 1 << 1, 1 << 2, 1 << 4}
    Qf, R, S = {1}, {1 << 5}, {1 << 6, 1 << 7}
    comp = lambda f: f ^ one
    product_host = poly_mul(poly_mul(comp(Qf), P), poly_mul(comp(R), comp(S)))
    delta_missing = poly_mul(poly_mul(comp(P), comp(Qf)), poly_mul(comp(R), S))
    three_form_host = product_host ^ delta_missing
    direct = poly_mul(poly_mul(comp(Qf), comp(R)), P ^ S)
    need(three_form_host == direct, "(1+q)(1+r)(p+s) is not the product plus the missing fibre")
    four_form = sorted([charge(anf_int(product_host)), charge(anf_int(three_form_host))])
    need(four_form == [16, 40], "four-form charges changed: %s" % four_form)
    for host in (product_host, three_form_host):
        check_host(anf_int(host), frame0, lines_t)
    # the same two hosts from the transform of the truth tables
    tables = []
    for host in (product_host, three_form_host):
        anf = anf_int(host)
        tables.append(sum(1 << x for x in range(SIZE) if eval_anf(anf, x)))
        need(mobius(tables[-1]) == anf, "transform and expansion disagree")

    # ---- degree-2 impossibility certificates, all 15 cliques
    certificates = []
    for index, clique in enumerate(clique_data):
        cert = three_flat_certificate(clique, quad)
        need(cert is not None, "no 3-flat certificate for clique %d" % index)
        a, dirs, flat = cert
        need(all(x in lines_t for x in flat) and len(flat) == 8, "certificate flat leaves the lines")
        need(sum(1 for x in flat if x in clique.set) == 1, "certificate flat meets the clique evenly")
        for degree_mask in range(SIZE):
            if bin(degree_mask).count("1") <= 2:
                parity = 0
                for x in flat:
                    parity ^= 1 if degree_mask & ~x == 0 else 0
                need(parity == 0, "a monomial of degree <= 2 does not sum to 0 on a 3-flat")
        certificates.append((index, a, dirs))

    # ---- per-clique exact minima in the named classes, two scopes
    results = {}
    for scope_name, scope in (("T120", lines_t), ("P104", p104)):
        for index, clique in enumerate(clique_data):
            if scope_name == "P104" and index >= 13:
                continue
            low2 = low_degree_hosts(clique, scope, 2)
            need(low2 is None, "a host of degree <= 2 exists (%s, clique %d)" % (scope_name, index))
            free, hosts = invariant_class(clique, scope)
            for anf in hosts:
                check_host(anf, clique, scope)
            invariant_min = min(charge(h) for h in hosts)
            flats = flat_hosts(clique, scope, subspaces5)
            for _, _, mons in flats:
                check_host(anf_int(mons), clique, scope)
            cubic, nullity = low_degree_hosts(clique, scope, 3)
            cubic_min = min(charge(h) for h in cubic)
            best_cubic = min(cubic, key=lambda h: (charge(h), h))
            check_host(best_cubic, clique, scope)
            best_invariant = min(hosts, key=lambda h: (charge(h), h))
            if scope_name == "T120":
                results[index] = {
                    "free": len(free), "flats": [(g, c) for g, c, _ in flats], "invariant_min": invariant_min,
                    "cubic_min": cubic_min, "cubic_nullity": nullity, "cubic_min_count": sum(1 for h in cubic if charge(h) == cubic_min),
                    "invariant_best": best_invariant, "cubic_best": best_cubic,
                }
            else:
                results[("P104", index)] = {"free": len(free), "invariant_min": invariant_min, "cubic_min": cubic_min, "cubic_nullity": nullity}

    # ---- compare with the expected tables
    for index in range(15):
        flats, inv_min, cubic_min = EXPECT_T120[index]
        got = results[index]
        need(got["flats"] == flats, "flat charges changed for clique %d: %s" % (index, got["flats"]))
        need(got["invariant_min"] == inv_min and got["cubic_min"] == cubic_min,
             "class minima changed for clique %d: %s" % (index, (got["invariant_min"], got["cubic_min"])))
        need(got["cubic_nullity"] == 9, "cubic host space should have dimension 9")
        need(got["free"] == 3, "expected three free cosets on the 120-line scope")
        need(min(c for _, c in flats) == inv_min, "the best W_F-invariant host is not a flat indicator")
    for index in range(13):
        inv_min, cubic_min = EXPECT_P104[index]
        got = results[("P104", index)]
        need((got["invariant_min"], got["cubic_min"]) == (inv_min, cubic_min), "P104-scope minima changed for frame %d" % index)
        need(got["cubic_nullity"] == 11, "cubic host space on the 104 lines should have dimension 11")

    # baseline: the product-of-letters hosts of #7031. A letter of root line l is
    # 1 + B(l, x); it equals 1 on a clique F exactly when l lies in F, because
    # F-perp = span(F) = F + W_F meets the root lines only in F. A product of letters
    # is the indicator of the common-1 set, here span(F), so the baseline charge of a
    # row is the charge of span(F).
    def polar(x, y):
        return quad(x ^ y) ^ quad(x) ^ quad(y)

    letter_vectors = [sum(polar(l, 1 << i) << i for i in range(N)) | (1 << N) for l in lines_t]
    need(f2_rank(letter_vectors) == 9, "the 120 letters do not span the affine functions")
    letter_baseline = []
    for index, clique in enumerate(clique_data):
        span = set(clique.points) | clique.direction
        need(len(span) == 16 and span & lines_t == clique.set, "span(F) meets the lines outside F")
        common = {x for x in range(SIZE) if all(polar(l, x) == 0 for l in clique.points)}
        need(common == span, "the common-1 set of the frame letters is not span(F)")
        ones = {l for l in lines_t if all(polar(l, f) == 0 for f in clique.points)}
        need(ones == clique.set, "a non-frame letter equals 1 on the whole clique")
        letter_baseline.append(charge(mobius(table_of(span))))
        need(any(g == 16 and c == letter_baseline[-1] for g, c in results[index]["flats"]),
             "the letter-product host is not among the five flat hosts")
    need(letter_baseline == EXPECT_LETTER_BASELINE, "letter-product baseline changed: %s" % letter_baseline)
    need(letter_baseline[0] == 40 and letter_baseline[1] == 111, "baseline disagrees with #7031 / #7046")

    need(results[0]["cubic_min_count"] == 1, "frame 0 should have a unique cubic minimiser")
    shown = " + ".join(monomial_name(m) for m in sorted(anf_set(results[0]["cubic_best"])))
    need(shown == EXPECT_FRAME0_CUBIC, "the frame-0 charge-14 host changed: %s" % shown)

    # the cubic hosts are f + (1+Q) * (affine function): verify the 9-dimensional kernel
    quad_anf = {1 << i for i in range(N)} ^ {(1 << i) | (1 << j) for i, j in edges}
    ideal_gens = [poly_mul(comp(quad_anf), {0 if k == 8 else (1 << k)}) for k in range(9)]
    for gen in ideal_gens:
        need(all(eval_anf(anf_int(gen), x) == 0 for x in lines_t), "(1+Q)*affine does not vanish on the lines")
    need(f2_rank([anf_int(g) for g in ideal_gens]) == 9, "(1+Q)*affine generators are dependent")
    need(all(max(bin(m).count("1") for m in g) <= 3 for g in ideal_gens), "an ideal generator has degree > 3")

    # cross-method checks: the hosts expanded by polynomial multiplication must occur in
    # both enumerations (one built from cosets, one from the linear system)
    free0, invariant0 = invariant_class(clique_data[0], lines_t)
    cubic0, _ = low_degree_hosts(clique_data[0], lines_t, 3)
    for host in (product_host, three_form_host):
        need(anf_int(host) in set(invariant0), "a four-form host is missing from the invariant class")
    need(anf_int(three_form_host) in set(cubic0), "the three-form host is missing from the cubic class")
    need(anf_int(product_host) not in set(cubic0), "the 40-monomial product has degree 4, not 3")

    # failure controls: each deliberately wrong statement must be rejected
    broken = set(three_form_host)
    broken ^= {sorted(three_form_host)[-1]}
    for rejected in (broken, product_host ^ {0b11}):
        try:
            check_host(anf_int(rejected), frame0, lines_t)
        except SystemExit:
            continue
        raise SystemExit("a corrupted host was accepted")
    wrong_forms = lambda x: (p_form(x) ^ ((x >> 3) & 1), q_form(x), r_form(x), s_form(x))
    wrong_image = {}
    for x in lines_t:
        wrong_image.setdefault(wrong_forms(x), set()).add(1 if x in frame0.set else 0)
    need(any(len(v) > 1 for v in wrong_image.values()), "a wrong form should make the indicator non-constant on a fibre")
    # an even-parity 3-flat (the clique itself) gives no obstruction to a quadratic host
    need(sum(1 for x in frame0.points if x in frame0.set) % 2 == 0, "the clique is an even flat")

    # explicit sparse hosts from search.py (upper bounds): re-evaluate every one directly
    searched = {}
    for scope_name, scope in (("T120", lines_t), ("P104", p104)):
        path = ROOT / "data" / ("hosts_%s.json" % scope_name)
        entries = json.loads(path.read_text())
        need([e["row"] for e in entries] == list(range(15 if scope_name == "T120" else 13)),
             "hosts_%s.json must list rows in order" % scope_name)
        for entry in entries:
            need(entry["scope"] == scope_name, "host entry has the wrong scope")
            anf = anf_int(set(entry["monomials"]))
            need(len(set(entry["monomials"])) == len(entry["monomials"]), "a host lists a monomial twice")
            need(charge(anf) == entry["charge"], "recorded charge is wrong for %s row %d" % (scope_name, entry["row"]))
            check_host(anf, clique_data[entry["row"]], scope)
            searched[(scope_name, entry["row"])] = (entry["charge"], anf)
    for index in range(15):
        class_best = min(results[index]["invariant_min"], results[index]["cubic_min"])
        need(searched[("T120", index)][0] <= class_best, "the search missed a class optimum on row %d" % index)
    for index in range(13):
        need(searched[("P104", index)][0] <= searched[("T120", index)][0], "a 120-line host should also host on 104 lines")
        class_best = min(results[("P104", index)]["invariant_min"], results[("P104", index)]["cubic_min"])
        need(searched[("P104", index)][0] <= class_best, "the search missed a P104 class optimum on row %d" % index)
    searched_t120 = [searched[("T120", i)][0] for i in range(15)]
    searched_p104 = [searched[("P104", i)][0] for i in range(13)]
    need(searched_t120 == EXPECT_SEARCHED_T120, "explicit 120-line host charges changed: %s" % searched_t120)
    need(searched_p104 == EXPECT_SEARCHED_P104, "explicit 104-line host charges changed: %s" % searched_p104)
    need(sum(searched_t120[:13]) == 225 and sum(searched_p104) == 211, "explicit host totals changed")
    below = [i for i in range(15) if searched_t120[i] < min(results[i]["invariant_min"], results[i]["cubic_min"])]
    need(below == [1, 2, 4, 5, 7, 8, 9, 10, 12, 14], "rows below the exact class minima changed: %s" % below)

    if "--table" in argv:
        print("| row | letter product | exact flat/invariant min | exact cubic min | explicit host, 120 lines | explicit host, 104 lines |")
        for index in range(15):
            r = results[index]
            p104_cell = searched_p104[index] if index < 13 else "-"
            print("| %s%d | %d | %d | %d | %d | %s |" % (
                "F" if index < 13 else "X", index if index < 13 else index - 13,
                letter_baseline[index], r["invariant_min"], r["cubic_min"], searched_t120[index], p104_cell))
        print("exact P104-scope (invariant, cubic) per frame:", [EXPECT_P104[i] for i in range(13)])
    if "--show" in argv:
        r = results[0]
        print("frame 0 three-form host (charge 16): (1+x0)(1+x5)(1+x1+x2+x4+x6+x7)")
        for name, anf in (("invariant best", r["invariant_best"]), ("cubic best", r["cubic_best"])):
            print(name, charge(anf), " + ".join(monomial_name(m) for m in sorted(anf_set(anf))))
    print(
        "PASS_P104_FRAME_HOST_MINIMUM frame0_four_form_min=16 frame0_product=40 frame0_cubic_min=14 "
        "no_degree2_host=15 free_cosets=3 flats_per_row=5 rows=15 structure=28+3+1 "
        "letter_baseline_sum_13=%d searched_t120=%s searched_p104=%s sum_t120_13=%d sum_p104_13=%d"
        % (sum(letter_baseline[:13]), ",".join(map(str, searched_t120)), ",".join(map(str, searched_p104)),
           sum(searched_t120[:13]), sum(searched_p104))
    )


if __name__ == "__main__":
    main(sys.argv[1:])
