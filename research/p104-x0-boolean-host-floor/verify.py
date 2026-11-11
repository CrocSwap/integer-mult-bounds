#!/usr/bin/env python3
"""Exact unrestricted Boolean-host charge of excluded clique X0.

Evidence class: exhaustive finite census of a finite domain, plus direct
evaluation of one host. Not a heuristic search and not a kappa change.

Claim. On the 120 root lines, every Boolean host of excluded clique X0 has
at least 7 algebraic-normal-form monomials of degree >= 2, and the indicator
of the flat a + W-perp attains 7.

The charged supports of size at most 6 form a finite set of size
304181752291. They are partitioned by which of three column blocks they meet,
and every block of that partition is enumerated. Checks use need(), so
python -O still runs them.
"""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
FRAMES_SHA256 = "c75915c18fc06ac19cc90fb9911209517c071862fdf401b998d5075efc0cda0d"
LINE_MAP_SHA256 = "b37530e8e9b2b3bd5be418d5ed3060a42ceb66e60ed3789f8ee79f29dabde437"
PORTS_SHA256 = "691c7b7d212112115b1bfc76db89f90d304ec448dc8c4a0c43d9a5954317146c"
X0_PORTS = (7, 25, 42, 52, 76, 82, 97, 127)
HOST_MONOMIALS = (0, 1, 8, 9, 32, 33, 40, 41, 64, 65, 96, 97)
DOMAIN_AT_MOST_6 = 304181752291
BASIS18_TARGETS = 31180
EDGES = ((0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7))
N = 8
SIZE = 1 << N
GE2 = sum(1 << m for m in range(SIZE) if m.bit_count() >= 2)
LOW = [sum(1 << m for m in range(SIZE) if not (m >> j) & 1) for j in range(N)]


def need(condition, message):
    if not condition:
        raise SystemExit(message)


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def comb_count(n, k):
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    value = 1
    for i in range(k):
        value = value * (n - i) // (i + 1)
    return value


def domain_size(n, limit):
    return sum(comb_count(n, k) for k in range(limit + 1))


# ------------------------------------------------------------------- geometry
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


def mobius(table):
    for j in range(N):
        table ^= (table & LOW[j]) << (1 << j)
    return table


def charge_of(anf):
    return (anf & GE2).bit_count()


def anf_bits(anf):
    masks = []
    while anf:
        bit = anf & -anf
        masks.append(bit.bit_length() - 1)
        anf ^= bit
    return tuple(masks)


def eval_anf(anf, point):
    value = 0
    rest = anf
    while rest:
        bit = rest & -rest
        mask = bit.bit_length() - 1
        if mask & ~point == 0:
            value ^= 1
        rest ^= bit
    return value


def poly_mul(left, right):
    out = set()
    for a in left:
        for b in right:
            out ^= {a | b}
    return out


def anf_from_masks(masks):
    value = 0
    for mask in masks:
        value ^= 1 << mask
    return value


def span(vectors):
    space = {0}
    for vector in vectors:
        if vector not in space:
            space |= {item ^ vector for item in space}
    return space


def load_x0():
    frame_path = ROOT / "data" / "frames.json"
    line_path = REPO / "research/p104-port-window-haemers/data/e8_line_map.json"
    ports_path = REPO / "research/p104-port-window-haemers/data/ports_p104.json"
    need(sha256_file(frame_path) == FRAMES_SHA256, "frames.json sha256 mismatch")
    need(sha256_file(line_path) == LINE_MAP_SHA256, "e8_line_map.json sha256 mismatch")
    need(sha256_file(ports_path) == PORTS_SHA256, "ports_p104.json sha256 mismatch")
    frames_doc = json.loads(frame_path.read_bytes().decode())
    line_map = json.loads(line_path.read_bytes().decode())
    ports_p104 = json.loads(ports_path.read_bytes().decode())["ports"]
    need(tuple(frames_doc["excluded_odd_cliques"][0]) == X0_PORTS, "X0 ports changed")
    need(len(frames_doc["frames"]) == 13 and len(frames_doc["excluded_odd_cliques"]) == 2, "frame count")
    need(len(ports_p104) == 104 and len(set(ports_p104)) == 104, "P104 ports")
    cliques = [tuple(c) for c in frames_doc["frames"]] + [tuple(c) for c in frames_doc["excluded_odd_cliques"]]
    need(set(ports_p104) == {p for frame in frames_doc["frames"] for p in frame}, "frames do not partition P104")
    need(sorted(p for clique in cliques for p in clique) == sorted(line_map["vectors"]), "cliques do not partition the lines")

    basis = simple_basis()
    matrix = list(zip(*basis))
    cartan = [[dot(basis[i], basis[j]) for j in range(8)] for i in range(8)]
    edges = tuple((i, j) for i in range(8) for j in range(i + 1, 8) if cartan[i][j] & 1)
    need(edges == EDGES, "E8 diagram edges changed: %s" % (edges,))
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
    need(len(set(points)) == 120, "chart points are not distinct")
    index = {}
    for position, root in enumerate(lines):
        index[root] = position
        index[negate(root)] = position
    port_position = {}
    for vector, root in zip(line_map["vectors"], line_map["roots2"]):
        port_position[vector] = index[tuple(root)]
    need(len(port_position) == 120 and len(set(port_position.values())) == 120, "line map is not bijective")

    def quad(x):
        return (x.bit_count() + sum(((x >> i) & (x >> j)) & 1 for i, j in edges)) & 1

    lines_t = set(points)
    need({x for x in range(SIZE) if quad(x)} == lines_t, "the 120 chart points are not {Q = 1}")
    x0 = {points[port_position[p]] for p in X0_PORTS}
    need(len(x0) == 8, "X0 is not eight chart points")
    return lines_t, x0, quad


def flat_and_host(lines_t, x0, quad):
    anchor = min(x0)
    direction = span(x ^ anchor for x in x0 if x != anchor)
    need(len(direction) == 8 and {anchor ^ w for w in direction} == x0, "X0 is not a 3-flat")

    def polar(x, y):
        return quad(x ^ y) ^ quad(x) ^ quad(y)

    perp = [u for u in range(SIZE) if all(polar(u, w) == 0 for w in direction)]
    need(len(perp) == 32 and all(w in perp for w in direction), "W-perp is not 5-dimensional")
    flat = {anchor ^ u for u in perp}
    need(len(flat) == 32 and flat & lines_t == x0, "a + W-perp does not host X0")
    table = 0
    for point in flat:
        table |= 1 << point
    transformed = mobius(table)
    x0_factor = {0, 1 << 0}
    x5_factor = {0, 1 << 5}
    x3x6_factor = {0, 1 << 3, 1 << 6}
    expanded = poly_mul(poly_mul(x0_factor, x5_factor), x3x6_factor)
    expanded_anf = anf_from_masks(expanded)
    need(expanded_anf == transformed, "the flat indicator is not (1+x0)(1+x5)(1+x3+x6)")
    need(anf_bits(expanded_anf) == HOST_MONOMIALS, "host monomials changed: %s" % (anf_bits(expanded_anf),))
    need(charge_of(expanded_anf) == 7, "the flat host does not have charge 7")
    for point in range(SIZE):
        value = (1 ^ (point & 1)) & (1 ^ ((point >> 5) & 1)) & (1 ^ ((point >> 3) & 1) ^ ((point >> 6) & 1))
        need(value == (1 if point in flat else 0), "factored evaluation misses the flat")
        need(eval_anf(expanded_anf, point) == value, "transform and factored form disagree")
    for point in lines_t:
        need(eval_anf(expanded_anf, point) == (1 if point in x0 else 0), "the charge-7 host misses a root line")
    # A one-monomial deletion is not a host. This is a failure control.
    deleted = expanded_anf ^ (1 << 9)
    need(any(eval_anf(deleted, point) != (1 if point in x0 else 0) for point in lines_t), "a corrupted host was accepted")
    return expanded_anf


# --------------------------------------------------------------- coset system
def build_system(lines_t, x0):
    """Eliminate the 9 affine monomials and return the 111 checks on 247 columns.

    Column j is the syndrome of charged monomial j. A 0-1 vector d is the
    charged part of a host if and only if the XOR of columns[i] for i in d
    equals `syndrome`. Affine coefficients are existential and are not counted.
    """
    affine = [m for m in range(SIZE) if m.bit_count() <= 1]
    charged = [m for m in range(SIZE) if m.bit_count() >= 2]
    need(len(affine) == 9 and len(charged) == 247, "monomial split")
    equations = []
    for x in sorted(lines_t):
        mask = 0
        for i, monomial in enumerate(affine):
            if monomial & ~x == 0:
                mask |= 1 << i
        for j, monomial in enumerate(charged):
            if monomial & ~x == 0:
                mask |= 1 << (9 + j)
        equations.append((mask, 1 if x in x0 else 0))
    used = [False] * len(equations)
    for col in range(9):
        pivot = next((i for i, (mask, _rhs) in enumerate(equations) if not used[i] and (mask >> col) & 1), None)
        need(pivot is not None, "affine evaluations are dependent at column %d" % col)
        used[pivot] = True
        pmask, prhs = equations[pivot]
        for i, (mask, rhs) in enumerate(equations):
            if i != pivot and (mask >> col) & 1:
                equations[i] = (mask ^ pmask, rhs ^ prhs)
    remaining = []
    for i, (mask, rhs) in enumerate(equations):
        if used[i]:
            continue
        need((mask & ((1 << 9) - 1)) == 0, "an affine bit survived elimination")
        charged_mask = mask >> 9
        if charged_mask == 0:
            need(rhs == 0, "the host equations are inconsistent")
            continue
        remaining.append((charged_mask, rhs))
    pivots = {}
    for mask, rhs in remaining:
        x, y = mask, rhs
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
            need(y == 0, "a dependent host equation is inconsistent")
    for p in sorted(pivots):
        xp, yp = pivots[p]
        for q in list(pivots):
            if q != p and (pivots[q][0] >> p) & 1:
                pivots[q] = (pivots[q][0] ^ xp, pivots[q][1] ^ yp)
    reduced = [pivots[p] for p in sorted(pivots)]
    need(len(reduced) == 111, "expected 111 independent checks, got %d" % len(reduced))
    columns = []
    for j in range(247):
        col = 0
        for r, (mask, _rhs) in enumerate(reduced):
            if (mask >> j) & 1:
                col |= 1 << r
        columns.append(col)
    syndrome = 0
    for r, (_mask, rhs) in enumerate(reduced):
        if rhs:
            syndrome |= 1 << r
    need(syndrome != 0, "the zero charged support would be a host")
    return charged, columns, syndrome


def affine_solvable(lines_t, x0, high_masks):
    """Independent solver: exist affine coefficients matching the residual?

    This gaussian elimination uses only the 9 affine columns. It does not
    reuse the 247-column syndrome matrix.
    """
    affine = [m for m in range(SIZE) if m.bit_count() <= 1]
    pivots = {}
    for x in sorted(lines_t):
        mask = 0
        for i, monomial in enumerate(affine):
            if monomial & ~x == 0:
                mask |= 1 << i
        rhs = 1 if x in x0 else 0
        for monomial in high_masks:
            if monomial & ~x == 0:
                rhs ^= 1
        xmask, yrhs = mask, rhs
        while xmask:
            top = xmask.bit_length() - 1
            if top in pivots:
                px, py = pivots[top]
                xmask ^= px
                yrhs ^= py
            else:
                pivots[top] = (xmask, yrhs)
                break
        else:
            if yrhs:
                return False
    return True


def syndrome_solvable(columns, syndrome, indices):
    syn = 0
    for i in indices:
        syn ^= columns[i]
    return syn == syndrome


# ------------------------------------------------------------------- census
def iter_syn(cols, weight):
    n = len(cols)
    if weight == 0:
        yield 0
        return
    if weight > n or weight < 0:
        return
    for comb in combinations(range(n), weight):
        syn = 0
        for i in comb:
            syn ^= cols[i]
        yield syn


def iter_supported(cols, weight, offset):
    n = len(cols)
    if weight == 0:
        yield 0, ()
        return
    if weight > n or weight < 0:
        return
    for comb in combinations(range(n), weight):
        syn = 0
        supp = []
        for i in comb:
            syn ^= cols[i]
            supp.append(offset + i)
        yield syn, tuple(supp)


def find_exact(cols, targets, weight, offset):
    """Return one weight-`weight` subset whose XOR lies in `targets`, or None.

    `targets` maps a required heavy-block syndrome to a disjoint support that
    has already been chosen outside this block. Every split of `weight` across
    one fixed halving of `cols` is enumerated, so the search is complete for
    that exact weight.
    """
    n = len(cols)
    if weight < 0 or weight > n:
        return None
    if weight == 0:
        extra = targets.get(0)
        return tuple(sorted(extra)) if extra is not None else None
    mid = max(1, n // 2)
    if mid >= n:
        mid = n - 1
    left, right = cols[:mid], cols[mid:]
    for k in range(weight + 1):
        lw, rw = k, weight - k
        left_count = comb_count(mid, lw)
        right_count = comb_count(n - mid, rw)
        if left_count == 0 or right_count == 0:
            continue
        if left_count <= right_count:
            small, sw, soff = left, lw, offset
            big, bw, boff = right, rw, offset + mid
        else:
            small, sw, soff = right, rw, offset + mid
            big, bw, boff = left, lw, offset
        big_set = set(iter_syn(big, bw))
        found_small = None
        need_syn = None
        extra = None
        for syn, supp in iter_supported(small, sw, soff):
            for target_syn, target_supp in targets.items():
                if syn ^ target_syn in big_set:
                    found_small = supp
                    need_syn = syn ^ target_syn
                    extra = target_supp
                    break
            if found_small is not None:
                break
        if found_small is None:
            continue
        for syn, supp in iter_supported(big, bw, boff):
            if syn == need_syn:
                return tuple(sorted(extra + found_small + supp))
        raise RuntimeError("a stored heavy syndrome was not recovered")
    return None


def enum_upto(cols, max_w, offset):
    items = [(0, 0, ())]
    n = len(cols)
    if max_w >= 1:
        for i, col in enumerate(cols):
            items.append((col, 1, (offset + i,)))
    if max_w >= 2:
        for i, j in combinations(range(n), 2):
            items.append((cols[i] ^ cols[j], 2, (offset + i, offset + j)))
    return items


def min_dict(items):
    best = {}
    for syn, weight, supp in items:
        old = best.get(syn)
        if old is None or weight < old[0]:
            best[syn] = (weight, supp)
    return best


def find_witness(columns, target, limit=6):
    """One support of size <= 6 whose columns XOR to target, or None.

    Completeness for limit 6. Split the columns into three contiguous blocks
    whose sizes differ by at most one. For a support with block weights
    x >= y >= z and x + y + z <= 6, exactly one of the following holds:

    * x <= 2. Bucket 1 enumerates every triple of supports of weight <= 2.
    * x = 3 and y <= 2. Bucket 2 enumerates the weight-3 block and every
      complementary pair of weight at most 2 whose weights sum to at most 3.
    * x = y = 3, hence z = 0. Bucket 3 enumerates the two weight-3 blocks.
    * x >= 4. Then y + z <= 2. Bucket 4 enumerates that exact heavy weight
      by every left/right split of one halving, against every light support
      of weight at most 6 - x.

    Keeping the minimum weight for a repeated syndrome cannot drop a legal
    solution: a heavier support of the same syndrome is less likely to fit
    under the weight cap, and the lighter one is legal whenever the heavier
    one is.
    """
    need(limit == 6, "the completeness argument is written for weight at most 6")
    n = len(columns)
    sizes = [n // 3 + (1 if i < n % 3 else 0) for i in range(3)]
    bounds = []
    parts = []
    start = 0
    for size in sizes:
        parts.append(columns[start:start + size])
        bounds.append((start, start + size))
        start += size
    need(start == n and all(bounds[i][1] - bounds[i][0] == sizes[i] for i in range(3)), "bad partition")
    light = [enum_upto(part, 2, bounds[i][0]) for i, part in enumerate(parts)]

    dict_c = min_dict(light[2])
    for sa, wa, pa in light[0]:
        for sb, wb, pb in light[1]:
            if wa + wb > limit:
                continue
            hit = dict_c.get(target ^ sa ^ sb)
            if hit is not None and wa + wb + hit[0] <= limit:
                return tuple(sorted(pa + pb + hit[1]))

    exact3 = [list(iter_supported(part, 3, bounds[i][0])) for i, part in enumerate(parts)]
    for special in range(3):
        others = [j for j in range(3) if j != special]
        paired = []
        for sp, wp, pp in light[others[0]]:
            for sq, wq, qq in light[others[1]]:
                if wp + wq <= 3:
                    paired.append((sp ^ sq, wp + wq, pp + qq))
        dict_l = min_dict(paired)
        for syn, supp in exact3[special]:
            hit = dict_l.get(target ^ syn)
            if hit is not None and 3 + hit[0] <= limit:
                return tuple(sorted(supp + hit[1]))

    sets3 = []
    for entries in exact3:
        table = {}
        for syn, supp in entries:
            table.setdefault(syn, supp)
        sets3.append(table)
    for i, j in ((0, 1), (0, 2), (1, 2)):
        for syn, supp in exact3[i]:
            other = sets3[j].get(target ^ syn)
            if other is not None:
                return tuple(sorted(supp + other))

    for heavy in range(3):
        lights = [j for j in range(3) if j != heavy]
        for heavy_w, slack in ((4, 2), (5, 1), (6, 0)):
            targets = {}
            for sp, wp, pp in light[lights[0]]:
                if wp > slack:
                    continue
                for sq, wq, qq in light[lights[1]]:
                    if wp + wq <= slack:
                        syn = sp ^ sq
                        old = targets.get(syn)
                        if old is None or wp + wq < old[0]:
                            targets[syn] = (wp + wq, pp + qq)
            # The heavy XOR must cancel the light XOR against the global target.
            target_map = {target ^ syn: supp for syn, (_weight, supp) in targets.items()}
            found = find_exact(parts[heavy], target_map, heavy_w, bounds[heavy][0])
            if found is not None:
                return found
    return None


def check_witness(columns, target, witness, limit):
    if witness is None or len(witness) > limit or len(set(witness)) != len(witness):
        return False
    if any(i < 0 or i >= len(columns) for i in witness):
        return False
    syn = 0
    for i in witness:
        syn ^= columns[i]
    return syn == target


def self_test_enumerator():
    """Every basis target of length 18 and weight <= 6 has a unique support."""
    columns = [1 << i for i in range(18)]
    checked = 0
    for weight in range(7):
        for comb in combinations(range(18), weight):
            target = 0
            for i in comb:
                target |= 1 << i
            found = find_witness(columns, target, 6)
            need(check_witness(columns, target, found, 6), "basis self-test rejected %s" % (comb,))
            need(tuple(found) == comb, "basis self-test returned %s for %s" % (found, comb))
            checked += 1
    need(checked == BASIS18_TARGETS, "basis self-test count %d" % checked)
    target7 = sum(1 << i for i in range(7))
    need(find_witness(columns, target7, 6) is None, "a weight-7 basis vector was accepted")

    large = [1 << i for i in range(90)]
    patterns = {
        "222": (0, 1, 30, 31, 60, 61),
        "330": (0, 1, 2, 30, 31, 32),
        "420": (0, 1, 2, 3, 30, 31),
        "411": (0, 1, 2, 3, 30, 60),
        "510": (0, 1, 2, 3, 4, 30),
        "600_first": (0, 1, 2, 3, 4, 5),
        "600_last": (24, 25, 26, 27, 28, 29),
        "321": (0, 1, 2, 30, 31, 60),
    }
    for name, comb in patterns.items():
        target = 0
        for i in comb:
            target |= 1 << i
        found = find_witness(large, target, 6)
        need(tuple(found) == tuple(sorted(comb)), "pattern %s returned %s" % (name, found))
    return checked


def require_no_solution(columns, syndrome):
    found = find_witness(columns, syndrome, 6)
    need(found is None, "a charged support of size %s meets the X0 syndrome: %s" % (
        None if found is None else len(found), found))


def require_found(columns, target, label):
    witness = find_witness(columns, target, 6)
    need(check_witness(columns, target, witness, 6), "planted support %s was not found" % label)


def main():
    need(domain_size(247, 6) == DOMAIN_AT_MOST_6, "domain size changed")
    need(domain_size(18, 6) == BASIS18_TARGETS, "basis-target count changed")
    checked = self_test_enumerator()
    lines_t, x0, quad = load_x0()
    host = flat_and_host(lines_t, x0, quad)
    charged, columns, syndrome = build_system(lines_t, x0)
    high = [i for i, mask in enumerate(charged) if (host >> mask) & 1]
    need(len(high) == 7, "charge-7 support has the wrong length")
    need(syndrome_solvable(columns, syndrome, high), "the charge-7 host misses the coset syndrome")
    need(affine_solvable(lines_t, x0, [charged[i] for i in high]), "independent affine solver rejects the charge-7 host")
    rejected = high[:-1]
    need(len(rejected) == 6, "rejected support")
    need(not syndrome_solvable(columns, syndrome, rejected), "six of the host monomials already host X0")
    need(not affine_solvable(lines_t, x0, [charged[i] for i in rejected]), "independent solver accepts a weight-6 subset of the host")
    first6 = list(range(6))
    syndrome_no = syndrome_solvable(columns, syndrome, first6)
    affine_no = affine_solvable(lines_t, x0, [charged[i] for i in first6])
    need(syndrome_no is affine_no and syndrome_no is False, "the two solvers disagree on the first six monomials")
    require_no_solution(columns, syndrome)
    # These targets are explicit column XORs, so a complete enumerator must
    # find some support of size at most 6. The one-column target is not the
    # X0 syndrome; it only checks that an empty return is not hard-coded.
    require_found(columns, columns[0], "one-column")
    planted6 = 0
    for index in range(6):
        planted6 ^= columns[index]
    require_found(columns, planted6, "first-six-columns")
    order = sorted(range(247), key=lambda i: (i % 5, i))
    need(len(set(order)) == 247, "stride order is not a permutation")
    permuted = [columns[i] for i in order]
    require_no_solution(permuted, syndrome)
    require_found(permuted, permuted[0], "strided-one-column")
    print(
        "PASS_X0_BOOLEAN_HOST_FLOOR minimum=7 achieved_by=(1+x0)(1+x5)(1+x3+x6) "
        "scope=120_root_lines clique=X0 checks=111 charged_columns=247 "
        "census_domain=%d partitions=2 basis_self_test=%d kappa_claim=none"
        % (DOMAIN_AT_MOST_6, checked)
    )


if __name__ == "__main__":
    main()
