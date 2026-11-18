"""Exact finite-iterate Gaussian construction checks.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The half-grid and annular construction adapt CubeJerry PR7570.
Ring, cycle and exact comparison routines adapt Ali Romman PR7699.
"""
from collections import Counter
from itertools import product
from math import gcd, isqrt, lcm
from pathlib import Path
import hashlib
import json


def need(value, message):
    if not value:
        raise ValueError(message)


def q(point):
    return point[1], -point[0]


def rotate(point, turns):
    for _ in range(turns % 4):
        point = q(point)
    return point


def color(point):
    return ((point[0] + point[1]) // 2) % 2


def norm(point):
    return (point[0] ** 2 + point[1] ** 2 + 2) // 4


def gap_le(a, b, p, denominator):
    remainder = (b - a) * denominator ** 2 - p ** 2
    return remainder <= 0 or remainder ** 2 <= 4 * a * p ** 2 * denominator ** 2


def at_most_rho(a, b):
    difference = b - a
    return difference <= 0 or (2 * difference - 1) ** 2 <= 8 * a


def threshold(r):
    return (r * r + 1) // 2, (r * r + 2 * r + 3) // 2


def gap_category(a, b, r):
    if b <= a:
        return -1
    lower, upper = threshold(r)
    if (a, b) == (lower, upper):
        return 0
    scale = 10 ** 30
    low = isqrt(upper * scale * scale) - isqrt(lower * scale * scale) - 1
    if gap_le(a, b, low, scale):
        return -1
    need(not gap_le(a, b, low + 3, scale), 'resolved exact radical comparison')
    return 1


def first_bad(m):
    need(m > 0 and m % 4 == 0, 'positive iterate divisible by four')
    r = 5
    while m % r == 0:
        r += 2
    return r


def ring(r):
    points = []
    x = y = r
    for dx, dy in [(-2, 0), (0, -2), (2, 0), (0, 2)]:
        for _ in range(r):
            points.append((x, y))
            x += dx
            y += dy
    need((x, y) == (r, r) and len(set(points)) == 4 * r, 'complete ring')
    return points


def ring_index(point):
    x, y = point
    r = max(abs(x), abs(y))
    if y == r and x > -r:
        index = (r - x) // 2
    elif x == -r and y > -r:
        index = r + (r - y) // 2
    elif y == -r and x < r:
        index = 2 * r + (x + r) // 2
    else:
        need(x == r and y < r, 'fourth ring side')
        index = 3 * r + (y + r) // 2
    return r, index


def ring_point(r, index):
    side, offset = divmod(index % (4 * r), r)
    return [(r - 2 * offset, r), (-r, r - 2 * offset),
            (-r + 2 * offset, -r), (r, -r + 2 * offset)][side]


def annulus_partner(point, r):
    b = r + 2
    for turns in range(4):
        x, y = rotate(point, turns)
        if (x, y) == (r, r):
            partner = (b, r)
        elif (x, y) == (b, r):
            partner = (r, r)
        elif y == r and -r < x < r:
            index = (x + r - 2) // 2
            partner = (x + (2 if index % 2 == 0 else -2), y)
        elif y == b and -r + 2 <= x <= b:
            index = (b - x) // 2
            partner = (x + (-2 if index % 2 == 0 else 2), y)
        else:
            continue
        return rotate(partner, -turns)
    raise ValueError('annulus coverage')


def annulus_edges(r):
    mapping = {}
    edges = [((r, r), (r + 2, r))]
    inner = [(x, r) for x in range(-r + 2, r, 2)]
    outer = [(x, r + 2) for x in range(r + 2, -r, -2)]
    for arc in [inner, outer]:
        need(len(arc) % 2 == 0, 'even arc length')
        edges.extend(zip(arc[::2], arc[1::2]))
    for a, b in edges:
        for turns in range(4):
            u, v = rotate(a, turns), rotate(b, turns)
            need(u not in mapping and v not in mapping, 'disjoint annular edges')
            mapping[u], mapping[v] = v, u
    need(set(mapping) == set(ring(r) + ring(r + 2)), 'annular coverage')
    return mapping


def local_map(point, m, inverse=False):
    cutoff = first_bad(m)
    r, index = ring_index(point)
    if r < cutoff:
        if m % 3 and r <= 3:
            return annulus_partner(point, 1)
        return ring_point(r, index + (-1 if inverse else 1))
    inner = cutoff + 4 * ((r - cutoff) // 4)
    return annulus_partner(point, inner)


def gaussian(value, m, inverse=False):
    need(m > 0 and m % 4 == 0, 'positive iterate divisible by four')
    a, b, c, d = value
    sx, sy, dx, dy = a + c, b + d, a - c, b - d
    if (sx - sy) % 2 == 0:
        ex, ey = (dy, -dx) if inverse else (-dy, dx)
    elif inverse:
        tx, ty = local_map((dx + dy, dx - dy), m, True)
        ex, ey = (tx - ty) // 2, -(tx + ty) // 2
    else:
        ux, uy = local_map((dx - dy, -dy - dx), m)
        ex, ey = (ux + uy) // 2, (ux - uy) // 2
    numerators = (sx + ex, sy + ey, sx - ex, sy - ey)
    need(all(x % 2 == 0 for x in numerators), 'Gaussian integral output')
    return tuple(x // 2 for x in numerators)


def direct_contract(value, target):
    a, b, c, d = value
    sx, sy, dx, dy = a + c, b + d, a - c, b - d
    ideal2 = (sx - dy, sy + dx, sx + dy, sy - dx)
    need((target[0] + target[2], target[1] + target[3]) == (sx, sy), 'exact sum')
    error4 = sum((2 * x - y) ** 2 for x, y in zip(target, ideal2))
    need(error4 == 4 * ((sx - sy) % 2), 'exact Gaussian error')
    return error4


def cycles(mapping):
    need(set(mapping) == set(mapping.values()), 'permutation of the whole finite domain')
    seen, lengths = set(), []
    for point in sorted(mapping):
        if point in seen:
            continue
        current, length = point, 0
        while current not in seen:
            seen.add(current)
            length += 1
            current = mapping[current]
        need(current == point, 'closed cycle')
        lengths.append(length)
    return lengths


def complete_fixture(m):
    cutoff = first_bad(m)
    outer = cutoff + 10
    points = [(x, y) for x in range(-outer, outer + 1, 2)
              for y in range(-outer, outer + 1, 2)]
    mapping = {p: local_map(p, m) for p in points}
    need(set(mapping.values()) == set(points), 'complete finite local permutation')
    oracle = {}
    singles = []
    if m % 3:
        oracle.update(annulus_edges(1))
        start = 5
    else:
        start = 1
    for r in range(start, cutoff, 2):
        arc = ring(r)
        oracle.update(zip(arc, arc[1:] + arc[:1]))
        singles.append(r)
    for r in range(cutoff, outer, 4):
        oracle.update(annulus_edges(r))
    need(mapping == oracle, 'pointwise rule equals separate arc generator')
    digest = hashlib.sha256()
    for p, out in sorted(mapping.items()):
        need(abs(p[0] - out[0]) + abs(p[1] - out[1]) == 2, 'unit neighbor')
        need(local_map(out, m, True) == p, 'explicit local inverse')
        need(local_map(q(p), m) == q(out), 'quarter-turn covariance')
        need(gap_category(min(norm(p), norm(out)), max(norm(p), norm(out)), cutoff) <= 0,
             'absolute radial bound on both colors')
        sx, sy = ((1, 0) if color(p) == 0 else (0, 1))
        dx, dy = (p[0] - p[1]) // 2, -(p[0] + p[1]) // 2
        value = ((sx + dx) // 2, (sy + dy) // 2, (sx - dx) // 2, (sy - dy) // 2)
        target = gaussian(value, m)
        direct_contract(value, target)
        need(gaussian(target, m, True) == value, 'Gaussian inverse on both colors')
        need(sum(x*x for x in value) == norm(p) and sum(x*x for x in target) == norm(out), 'coordinate norm identity')
        digest.update(f'{p}:{out};'.encode())
    g = {p: q(out) for p, out in mapping.items()}
    lengths = cycles(g)
    actual_order = lcm(*lengths)
    predicted_order = lcm(4, *(2*r//gcd(2*r, (1-r)//2) for r in singles))
    need(actual_order == predicted_order and m % actual_order == 0, 'direct cycles and iterate identity')
    a = (cutoff + 1) // 2
    attaining = [(a, 0, 1-a, 0), (0, a, 1, -a), (1-a, 0, a, 0), (1, -a, 0, a)]
    for old, new in zip(attaining, attaining[1:] + attaining[:1]):
        need(gaussian(old, m) == new, 'attaining four-cycle')
    need([sum(x*x for x in z) for z in attaining] == list(threshold(cutoff))*2, 'exact attained threshold')
    return {'iterate': m, 'cutoff': cutoff, 'central_pair': bool(m % 3), 'points': len(points),
            'cycle_lengths': dict(sorted(Counter(lengths).items())), 'map_order': actual_order,
            'map_sha256': digest.hexdigest(), 'attaining_cycle': attaining,
            'threshold_squared_norms': threshold(cutoff)}


def lower_boundaries(cutoff):
    rows = []
    for r in [cutoff - 2, cutoff]:
        count = 0
        for p in product(range(-r, r + 1, 2), repeat=2):
            if color(p):
                continue
            x, y = p
            for out in [(x-2, y), (x+2, y), (x, y-2), (x, y+2)]:
                if max(abs(out[0]), abs(out[1])) > r:
                    need(gap_category(norm(p), norm(out), cutoff) >= 0, 'every exterior edge meets lower threshold')
                    count += 1
        rows.append({'radius_doubled': r, 'exterior_edges': count})
    need(sum(x['exterior_edges'] for x in rows) == 4 * cutoff, 'independent boundary count')
    need(not at_most_rho(*threshold(cutoff)), 'strictly above unrestricted optimum')
    return rows


def compute():
    order_digest = hashlib.sha256()
    distribution = Counter()
    for m in range(4, 4097, 4):
        cutoff = first_bad(m)
        need(all(m % r == 0 for r in range(5, cutoff, 2)) and m % cutoff, 'least incompatible odd ring')
        need(m % 3 == 0 or cutoff <= 9, 'central exception has only three cutoffs')
        distribution[cutoff] += 1
        order_digest.update(f'{m}:{cutoff};'.encode())
    representatives = {}
    for candidate in range(5, 66, 2):
        minimum = 4*lcm(*range(5, candidate, 2))
        for m in [minimum, 3*minimum]:
            cutoff = first_bad(m)
            if cutoff <= 65:
                representatives.setdefault((cutoff, bool(m % 3)), m)
    fixtures = [complete_fixture(m) for _, m in sorted(representatives.items())]
    boundaries = {r: lower_boundaries(r) for r in sorted({r for r, _ in representatives})}
    gaussian_cases = 0
    for m in [4, 12, 20, 60, 140, 420, 1260, 13860]:
        cutoff = first_bad(m)
        for value in product(range(-3, 4), repeat=4):
            target = gaussian(value, m)
            direct_contract(value, target)
            need(gaussian(target, m, True) == value and gaussian(gaussian(value, m, True), m) == value,
                 'both full Gaussian inverse identities')
            need(gap_category(sum(x*x for x in value), sum(x*x for x in target), cutoff) <= 0, 'all-sum forward bound')
            phase = (-value[1], value[0], -value[3], value[2])
            need(gaussian(phase, m) == (-target[1], target[0], -target[3], target[2]), 'Gaussian phase covariance')
            gaussian_cases += 1
    need(gap_le(1, 3, 733, 1000) and not gap_le(41, 51, 733, 1000), 'central connector below the smallest exceptional threshold')
    controls = []
    for m in [4, 20, 140]:
        points = ring(3)
        bad = {p: q(points[(i+1) % len(points)]) for i, p in enumerate(points)}
        lengths = cycles(bad)
        need(any(m % length for length in lengths), 'omitted central pairing breaks iterate identity')
        controls.append({'iterate': m, 'omitted_central_pair_cycle_lengths': lengths})
    for row in fixtures:
        r, m = row['cutoff'], row['iterate']
        orders = [r, 2*r]
        need(all(m % order for order in orders), 'both isolated critical-ring maps fail')
    need(gap_category(13, 19, 7) == 1, 'unchanged fourth-power map exceeds the order-twenty budget')
    zero_sum = (1, 0, -1, 0)
    after = zero_sum
    for step in range(1, 65):
        after = gaussian(after, 4)
        need((after == zero_sum) == (step % 4 == 0), 'four divides every global iterate identity')
    return {'status': 'PASS_GAUSSIAN_FINITE_ITERATE_OPTIMUM',
            'small_iterates': 1024, 'cutoff_distribution': dict(sorted(distribution.items())),
            'iterate_cutoff_sha256': order_digest.hexdigest(), 'fixtures': fixtures,
            'lower_boundaries': boundaries, 'gaussian_input_cases': gaussian_cases,
            'controls': controls, 'total_half_grid_points': sum(r['points'] for r in fixtures)}


if __name__ == '__main__':
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    need(actual == expected, 'exact committed receipt')
    print(actual['status'])
    print('1024 iterate budgets; 23 complete grids; 41032 half-grid points')
    print('2424 lower-boundary edges; 19208 full Gaussian inputs; all controls pass')
