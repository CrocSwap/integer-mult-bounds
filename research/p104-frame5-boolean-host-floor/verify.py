#!/usr/bin/env python3
"""Exact unrestricted Boolean-host charge of P104 frame 5.

Evidence class: exhaustive finite census of a finite domain, plus direct
evaluation of one host. Not a heuristic search and not a kappa change.

Claim. On the 120 root lines, every Boolean host of P104 frame 5 has at
least 6 algebraic-normal-form monomials of degree >= 2, and one explicit
host attains 6. The selected frontier is not changed.

The charged supports of size at most 5 form a finite set of size
7509373288. They are partitioned by which of three column blocks they meet,
and every block of that partition is enumerated. Checks use need(), so
python -O still runs them.
"""

import hashlib
import json
import sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
FRAMES_SHA256 = "c75915c18fc06ac19cc90fb9911209517c071862fdf401b998d5075efc0cda0d"
LINE_MAP_SHA256 = "b37530e8e9b2b3bd5be418d5ed3060a42ceb66e60ed3789f8ee79f29dabde437"
PORTS_SHA256 = "691c7b7d212112115b1bfc76db89f90d304ec448dc8c4a0c43d9a5954317146c"
FRAME5_PORTS = (28, 49, 133, 168, 265, 292, 400, 445)
# Charged monomials of x0*x5*(x3 + x1*x3 + x3*x6 + x2*x7 + x1*x3*x7 + x4*x7).
HOST_MONOMIALS = (41, 43, 105, 165, 171, 177)
FACTOR_G = (8, 10, 72, 132, 138, 144)
DOMAIN_AT_MOST_5 = 7509373288
BASIS15_TARGETS = 4944
WEIGHT_LIMIT = 5
EDGES = ((0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7))
N = 8
SIZE = 1 << N
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
    return sum(1 for m in range(SIZE) if (anf >> m) & 1 and m.bit_count() >= 2)


def anf_bits(anf):
    return tuple(m for m in range(SIZE) if (anf >> m) & 1)


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


def monomial_name(mask):
    if mask == 0:
        return "1"
    return "*".join("x%d" % i for i in range(N) if (mask >> i) & 1)


def load_frame5():
    frame_path = ROOT / "data" / "frames.json"
    line_path = REPO / "research/p104-port-window-haemers/data/e8_line_map.json"
    ports_path = REPO / "research/p104-port-window-haemers/data/ports_p104.json"
    need(sha256_file(frame_path) == FRAMES_SHA256, "frames.json sha256 mismatch")
    need(sha256_file(line_path) == LINE_MAP_SHA256, "e8_line_map.json sha256 mismatch")
    need(sha256_file(ports_path) == PORTS_SHA256, "ports_p104.json sha256 mismatch")
    frames_doc = json.loads(frame_path.read_bytes().decode())
    line_map = json.loads(line_path.read_bytes().decode())
    ports_p104 = json.loads(ports_path.read_bytes().decode())["ports"]
    frames = frames_doc["frames"]
    excluded = frames_doc["excluded_odd_cliques"]
    need(len(frames) == 13 and len(excluded) == 2, "frame count")
    need(tuple(frames[5]) == FRAME5_PORTS, "frame 5 ports changed")
    need(len(ports_p104) == 104 and len(set(ports_p104)) == 104, "P104 ports")
    need(set(ports_p104) == {p for frame in frames for p in frame}, "frames do not partition P104")
    cliques = [tuple(c) for c in frames] + [tuple(c) for c in excluded]
    need(sorted(p for clique in cliques for p in clique) == sorted(line_map["vectors"]), "cliques do not partition the lines")
    need(set(FRAME5_PORTS) <= set(ports_p104), "frame 5 is not inside the P104 ports")

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
    frame = {points[port_position[p]] for p in FRAME5_PORTS}
    need(len(frame) == 8, "frame 5 is not eight chart points")
    return lines_t, frame


def check_host_polynomial(lines_t, frame):
    """The six-monomial product hosts frame 5, and deleting one monomial does not."""
    expanded = poly_mul(poly_mul({1}, {1 << 5}), set(FACTOR_G))
    need(expanded == set(HOST_MONOMIALS), "x0*x5*g did not expand to the six monomials: %s" % sorted(expanded))
    for mask in FACTOR_G:
        need(mask & ((1 << 0) | (1 << 5)) == 0, "a factor of g meets x0 or x5")
    need(len(FACTOR_G) == len(set(FACTOR_G)) == 6, "g is not six distinct monomials")
    host = anf_from_masks(HOST_MONOMIALS)
    need(anf_bits(host) == HOST_MONOMIALS, "host bit order changed")
    need(charge_of(host) == 6, "the explicit host does not have charge 6")
    need(mobius(mobius(host)) == host, "the subset-sum transform is not an involution on this host")
    # Direct ANF evaluation, independent of the factored arithmetic above.
    for point in lines_t:
        got = eval_anf(host, point)
        factored = ((point >> 0) & 1) & ((point >> 5) & 1) & eval_anf(anf_from_masks(FACTOR_G), point)
        need(got == factored, "factored evaluation disagrees with the ANF at %d" % point)
        need(got == (1 if point in frame else 0), "the charge-6 host misses a root line")
    deleted = host ^ (1 << HOST_MONOMIALS[0])
    need(charge_of(deleted) == 5, "deleting one host monomial did not leave charge 5")
    need(
        any(eval_anf(deleted, point) != (1 if point in frame else 0) for point in lines_t),
        "a one-monomial deletion of the host was accepted",
    )
    return host


def build_system(lines_t, frame):
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
        equations.append((mask, 1 if x in frame else 0))
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


def affine_solvable(lines_t, frame, high_masks):
    """Independent solver: exist affine coefficients matching the residual?

    This Gaussian elimination uses only the 9 affine columns. It does not
    reuse the 247-column syndrome matrix.
    """
    affine = [m for m in range(SIZE) if m.bit_count() <= 1]
    pivots = {}
    for x in sorted(lines_t):
        mask = 0
        for i, monomial in enumerate(affine):
            if monomial & ~x == 0:
                mask |= 1 << i
        rhs = 1 if x in frame else 0
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

    `targets` maps a required block syndrome to a disjoint support already
    chosen outside this block. Every split of `weight` across one fixed
    halving of `cols` is enumerated, so the search is complete for that
    exact weight. One stored support per syndrome is enough for existence.
    """
    n = len(cols)
    if weight < 0 or weight > n or not targets:
        return None
    if weight == 0:
        extra = targets.get(0)
        return tuple(sorted(extra)) if extra is not None else None
    mid = n // 2
    if mid <= 0 or mid >= n:
        for syn, supp in iter_supported(cols, weight, offset):
            extra = targets.get(syn)
            if extra is not None:
                return tuple(sorted(extra + supp))
        return None
    left, right = cols[:mid], cols[mid:]
    for k in range(weight + 1):
        lw, rw = k, weight - k
        if comb_count(mid, lw) == 0 or comb_count(n - mid, rw) == 0:
            continue
        if comb_count(mid, lw) <= comb_count(n - mid, rw):
            small, sw, soff = left, lw, offset
            big, bw, boff = right, rw, offset + mid
        else:
            small, sw, soff = right, rw, offset + mid
            big, bw, boff = left, lw, offset
        big_map = {}
        for syn, supp in iter_supported(big, bw, boff):
            if syn not in big_map:
                big_map[syn] = supp
        for syn, supp in iter_supported(small, sw, soff):
            for target_syn, extra in targets.items():
                hit = big_map.get(syn ^ target_syn)
                if hit is not None:
                    return tuple(sorted(extra + supp + hit))
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


def shape_bucket(x, y, z):
    """Classify a sorted block-weight triple of total at most 5.

    The three tests are disjoint and, for x >= y >= z >= 0 with
    x + y + z <= 5, exactly one applies:
      1. max part at most 2;
      2. max part exactly 3 and the other two parts sum to at most 2;
      4. max part at least 4, so the other two parts sum to at most 5 - x.
    (3, 3, *) sums to at least 6 and is outside this cap.
    """
    if x <= 2:
        return 1
    if x == 3 and y + z <= 2:
        return 2
    if x >= 4 and y + z <= 5 - x:
        return 4
    return None


def assert_shape_cover():
    seen = []
    for x in range(0, WEIGHT_LIMIT + 1):
        for y in range(0, x + 1):
            for z in range(0, y + 1):
                if x + y + z <= WEIGHT_LIMIT:
                    bucket = shape_bucket(x, y, z)
                    need(bucket in (1, 2, 4), "shape %s has no bucket" % ((x, y, z),))
                    seen.append((x, y, z, bucket))
    need(len(seen) == 16, "expected 16 sorted shapes of weight at most 5, got %d" % len(seen))
    need(shape_bucket(3, 3, 0) is None, "weight 6 shape (3,3,0) was accepted")
    need(shape_bucket(4, 1, 1) is None, "weight 6 shape (4,1,1) was accepted")


def find_witness(columns, target, limit=WEIGHT_LIMIT):
    """One support of size <= 5 whose columns XOR to target, or None.

    Completeness for limit 5. Split the columns into three contiguous blocks
    whose sizes differ by at most one. For a support with sorted block
    weights x >= y >= z and x + y + z <= 5, assert_shape_cover records that
    exactly one of the following holds:

    * x <= 2. Bucket 1 enumerates every triple of supports of weight <= 2
      whose weights sum to at most 5.
    * x = 3 and y + z <= 2. Bucket 2 enumerates the weight-3 block and every
      complementary pair of weight at most 2 whose weights sum to at most 2.
    * x >= 4, so y + z <= 5 - x. Bucket 4 enumerates that exact heavy weight
      by every left/right split of one halving, against every light support
      of weight at most 5 - x.

    Keeping the minimum weight for a repeated syndrome cannot drop a legal
    solution: if a heavier support of the same syndrome fits under the cap,
    the lighter support fits as well.
    """
    need(limit == WEIGHT_LIMIT, "the completeness argument is written for weight at most 5")
    n = len(columns)
    sizes = [n // 3 + (1 if i < n % 3 else 0) for i in range(3)]
    bounds = []
    parts = []
    start = 0
    for size in sizes:
        parts.append(columns[start:start + size])
        bounds.append((start, start + size))
        start += size
    need(start == n and sorted(sizes, reverse=True)[0] - sorted(sizes)[0] <= 1, "bad partition")

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
                if wp + wq <= 2:
                    paired.append((sp ^ sq, wp + wq, pp + qq))
        dict_l = min_dict(paired)
        for syn, supp in exact3[special]:
            hit = dict_l.get(target ^ syn)
            if hit is not None and 3 + hit[0] <= limit:
                return tuple(sorted(supp + hit[1]))

    for heavy in range(3):
        lights = [j for j in range(3) if j != heavy]
        for heavy_w in (4, 5):
            slack = limit - heavy_w
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
    """Every basis target of length 15 and weight <= 5 has a unique support."""
    assert_shape_cover()
    columns = [1 << i for i in range(15)]
    checked = 0
    for weight in range(WEIGHT_LIMIT + 1):
        for comb in combinations(range(15), weight):
            target = 0
            for i in comb:
                target |= 1 << i
            found = find_witness(columns, target, WEIGHT_LIMIT)
            need(check_witness(columns, target, found, WEIGHT_LIMIT), "basis self-test rejected %s" % (comb,))
            need(tuple(found) == comb, "basis self-test returned %s for %s" % (found, comb))
            checked += 1
    need(checked == BASIS15_TARGETS, "basis self-test count %d" % checked)
    target6 = sum(1 << i for i in range(6))
    need(find_witness(columns, target6, WEIGHT_LIMIT) is None, "a weight-6 basis vector was accepted")

    # A repeated column has two legal weight-1 supports. Either is a hit.
    repeated = [1, 1, 1 << 2]
    found_rep = find_witness(repeated, 1, WEIGHT_LIMIT)
    need(found_rep in ((0,), (1,)), "repeated-column search returned %s" % (found_rep,))
    need(find_witness(repeated, 0, WEIGHT_LIMIT) == (), "the zero target missed the empty support")

    large = [1 << i for i in range(90)]
    patterns = {
        "221": (0, 1, 30, 31, 60),
        "111": (0, 30, 60),
        "320": (0, 1, 2, 30, 31),
        "311": (0, 1, 2, 30, 60),
        "300": (0, 1, 2),
        "410": (0, 1, 2, 3, 30),
        "500": (0, 1, 2, 3, 4),
        "500_last": (25, 26, 27, 28, 29),
        "221_ends": (28, 29, 58, 59, 89),
    }
    for name, comb in patterns.items():
        target = 0
        for i in comb:
            target |= 1 << i
        found = find_witness(large, target, WEIGHT_LIMIT)
        need(tuple(found) == tuple(sorted(comb)), "pattern %s returned %s" % (name, found))
    return checked


def require_no_solution(columns, syndrome):
    found = find_witness(columns, syndrome, WEIGHT_LIMIT)
    need(found is None, "a charged support of size %s meets the frame-5 syndrome: %s" % (
        None if found is None else len(found), found))


def require_found(columns, target, label):
    witness = find_witness(columns, target, WEIGHT_LIMIT)
    need(check_witness(columns, target, witness, WEIGHT_LIMIT), "planted support %s was not found" % label)


def note(message):
    print(message, file=sys.stderr, flush=True)


def main():
    need(domain_size(247, WEIGHT_LIMIT) == DOMAIN_AT_MOST_5, "domain size changed")
    need(domain_size(15, WEIGHT_LIMIT) == BASIS15_TARGETS, "basis-target count changed")
    note("self-test")
    checked = self_test_enumerator()
    lines_t, frame = load_frame5()
    host = check_host_polynomial(lines_t, frame)
    charged, columns, syndrome = build_system(lines_t, frame)
    high = [i for i, mask in enumerate(charged) if (host >> mask) & 1]
    need(high and [charged[i] for i in high] == list(HOST_MONOMIALS), "charge-6 support is not the factored host")
    need(len(high) == 6, "charge-6 support has the wrong length")
    need(syndrome_solvable(columns, syndrome, high), "the charge-6 host misses the coset syndrome")
    need(affine_solvable(lines_t, frame, [charged[i] for i in high]), "independent affine solver rejects the charge-6 host")
    rejected = high[:-1]
    need(len(rejected) == 5, "rejected support")
    need(not syndrome_solvable(columns, syndrome, rejected), "five of the host monomials already host frame 5")
    need(
        not affine_solvable(lines_t, frame, [charged[i] for i in rejected]),
        "independent solver accepts a weight-5 subset of the host",
    )
    first5 = list(range(5))
    syndrome_no = syndrome_solvable(columns, syndrome, first5)
    affine_no = affine_solvable(lines_t, frame, [charged[i] for i in first5])
    need(syndrome_no is affine_no and syndrome_no is False, "the two solvers disagree on the first five monomials")

    note("planted supports")
    require_found(columns, columns[0], "one-column")
    planted = (
        (0, 1, 83, 165, 166),
        (0, 1, 2, 83, 84),
        (0, 1, 2, 3, 4),
        (80, 81, 82, 163, 164),
    )
    for comb in planted:
        target = 0
        for index in comb:
            target ^= columns[index]
        require_found(columns, target, "columns%s" % (comb,))

    note("census partition 1")
    require_no_solution(columns, syndrome)
    order = sorted(range(247), key=lambda i: (i % 5, i))
    need(len(set(order)) == 247, "stride order is not a permutation")
    permuted = [columns[i] for i in order]
    note("census partition 2")
    require_no_solution(permuted, syndrome)
    require_found(permuted, permuted[0], "strided-one-column")
    planted5 = 0
    for index in range(5):
        planted5 ^= permuted[index]
    require_found(permuted, planted5, "strided-first-five")
    print(
        "PASS_P104_FRAME5_BOOLEAN_HOST_FLOOR minimum=6 "
        "host=x0*x5*(x3+x1*x3+x3*x6+x2*x7+x1*x3*x7+x4*x7) "
        "scope=120_root_lines frame=5 checks=111 charged_columns=247 "
        "census_domain=%d partitions=2 basis_self_test=%d kappa_claim=none"
        % (DOMAIN_AT_MOST_5, checked)
    )


if __name__ == "__main__":
    main()
