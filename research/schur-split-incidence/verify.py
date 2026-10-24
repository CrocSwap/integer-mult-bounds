"""Exact binary scalar-incidence checks; no GL4 or 496-split census."""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
REPS = [(0, 0, 4, 8), (0, 0, 4, 9), (0, 2, 0, 8),
        (0, 2, 2, 8), (0, 4, 4, 8), (0, 4, 4, 9), (0, 6, 0, 8)]
SREP = (0, 0, 4, 8)


def require(ok, label):
    if not ok:
        raise ValueError(label)


def dot(a, b):
    return (a & b).bit_count() % 2


def apply(matrix, vector):
    return sum(dot(row, vector) << i for i, row in enumerate(matrix))


def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in tuple(out)}
    return out


def basis(vectors):
    out = []
    for v in sorted(vectors):
        if v not in span(out):
            out.append(v)
    return out


def rank(matrix):
    return len(basis(matrix))


def compose(a, b):
    n = len(a)
    return tuple(sum(dot(row, sum(((b[k] >> j) & 1) << k for k in range(n))) << j
                     for j in range(n)) for row in a)


def residual(profile, a, b):
    n = sum(profile)
    masks = []
    offset = 0
    for r in profile:
        masks.append(((1 << r) - 1) << offset)
        offset += r
    p, q = masks[1] | masks[3], masks[2] | masks[3]
    require(dot(a, b) == dot(a & p, b) == dot(a & q, b) == 1, 'split/guard')
    hb = basis(v for v in range(1 << n) if not dot(b, v))
    coordinates = {0: 0}
    for i, v in enumerate(hb):
        coordinates.update({x ^ v: c | (1 << i) for x, c in tuple(coordinates.items())})
    matrices = []
    for mask in (p, q):
        columns = [coordinates[(v & mask) ^ ((a & mask) if dot(b, v & mask) else 0)] for v in hb]
        matrices.append(tuple(sum(((v >> i) & 1) << j for j, v in enumerate(columns)) for i in range(n - 1)))
    return tuple(matrices)


def fingerprint(s, t):
    n = len(s)
    si = {apply(s, x) for x in range(1 << n)}
    ti = {apply(t, x) for x in range(1 << n)}
    common_kernel = sum(apply(s, x) == apply(t, x) == 0 for x in range(1 << n))
    st, ts = compose(s, t), compose(t, s)
    return (s == t, len(si & ti), common_kernel, rank(st), rank(ts), rank(tuple(a ^ b for a, b in zip(st, ts))))


def conjugacy_witness(pair, target):
    # Solve S*K=K*S0 and T*K=K*T0, then find one invertible solution.
    equations = []
    for a, b in zip(pair, target):
        for i in range(4):
            for j in range(4):
                row = 0
                for k in range(4):
                    if (a[i] >> k) & 1:
                        row ^= 1 << (4 * k + j)
                    if (b[k] >> j) & 1:
                        row ^= 1 << (4 * i + k)
                equations.append(row)
    pivots = {}
    for row in equations:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    free = [i for i in range(16) if i not in pivots]
    solutions = []
    for f in free:
        x = 1 << f
        for pivot, row in sorted(pivots.items()):
            if dot(row, x):
                x ^= 1 << pivot
        solutions.append(x)
    for encoded in sorted(span(solutions)):
        k = tuple((encoded >> (4 * i)) & 15 for i in range(4))
        if rank(k) == 4:
            require(all(compose(a, k) == compose(k, b) for a, b in zip(pair, target)), 'intertwiner identity')
            return k
    raise ValueError('no invertible intertwiner')


def sector_types(r, h):
    require(type(r) is int and r >= 0 and h in (0, 1), 'sector domain')
    if r == 0:
        return [] if h else [('Z', 0, 0, 1)]
    m = (1 << r) - 1
    if h:
        return [('C', 1, 1, m * (1 << (r - 1)))]
    result = [('Z', 0, 0, 1), ('A', 1, 0, m), ('B', 0, 1, m)]
    if r > 1:
        result.append(('N', 1, 2, m * ((1 << (r - 1)) - 1)))
    return result


def incidence(profile):
    for h in (0, 1):
        choices = [sector_types(r, h if j == 3 else 1 - h) for j, r in enumerate(profile)]
        for types in product(*choices):
            offset = a = b = 0
            weight = 1
            for r, (_, u, v, w) in zip(profile, types):
                a |= u << offset
                b |= v << offset
                offset += r
                weight *= w
            yield h, tuple(t[0] for t in types), a, b, weight


def derive_state(h, types):
    if h == 0:
        return {'Z': 0, 'A': 1, 'B': 4, 'N': 5}[types[3]]
    if types[1:3] == ('A', 'B'):
        return 3
    if types[1:3] == ('B', 'A'):
        return 6
    return 2


def gl(n):
    result = 1
    for i in range(n):
        result *= (1 << n) - (1 << i)
    return result


def main():
    sources = json.loads((ROOT / 'RETAINED.json').read_text())
    for row in sources:
        require(hashlib.sha256((ROOT / row['retained_path']).read_bytes()).hexdigest() == row['sha256'], 'retained source bytes')
    fingerprints = [fingerprint(SREP, t) for t in REPS]
    require(len(set(fingerprints)) == 7, 'seven states distinct')
    weights = [0] * 7
    seeds = []
    for h, types, a, b, w in incidence((1, 1, 1, 2)):
        state = derive_state(h, types)
        pair = residual((1, 1, 1, 2), a, b)
        require(fingerprint(*pair) == fingerprints[state], 'canonical seed state')
        conjugacy_witness(pair, (SREP, REPS[state]))
        require(all(compose(x, x) == x and rank(x) == 2 for x in pair), 'residual idempotency/rank')
        weights[state] += w
        seeds.append({'h': h, 'types': types, 'a': a, 'b': b, 'weight': w, 'state': state + 1})
    require(len(seeds) == 31, '31 canonical sector tuples')
    require(weights[:2] == [1, 3], 'first fixture')
    # The old table is calibration only: derive_state never reads it.
    calibration = json.loads((ROOT / 'retained/calibration.json').read_text())
    require(weights == calibration['split_weights'], 'published input calibration')
    require(sum(weights) == 172, 'first guard split total')

    # Independent direct splits in dimension two and three, including empty sectors.
    tiny = 0
    for n in (2, 3):
        for profile in product(range(n + 1), repeat=4):
            if sum(profile) != n:
                continue
            expected = Counter()
            for _, _, a, b, w in incidence(profile):
                expected[fingerprint(*residual(profile, a, b))] += w
            direct = Counter()
            offset = 0
            masks = []
            for r in profile:
                masks.append(((1 << r) - 1) << offset)
                offset += r
            for a in range(1, 1 << n):
                for b in range(1 << n):
                    if dot(a, b) == dot(a & (masks[1] | masks[3]), b) == dot(a & (masks[2] | masks[3]), b) == 1:
                        direct[fingerprint(*residual(profile, a, b))] += 1
            require(direct == expected, 'tiny direct split versus weighted incidence')
            tiny += 1

    z = calibration['stabilizers']
    f = calibration['depth_two_orbit_counts']
    contributions = [w * c * d for w, c, d in zip(weights, z, f)]
    require(sum(contributions) == 93564, 'credited continuation composition')
    require([weights[i] * z[i] for i in (0, 1)] == [36, 12], 'header per coordinate pair')
    controls = 0
    for wrong, correct in [(sum(weights), sum(weights) * gl(4)),
                           ([gl(4) // c for c in z], weights),
                           ([1] * 7, weights),
                           (21, weights[2]),
                           (496, sum(weights))]:
        try:
            require(wrong == correct, 'semantic mutant')
        except ValueError:
            controls += 1
        else:
            raise ValueError('semantic mutant accepted')
    require(controls == 5, 'all controls rejected')
    result = {'split_weights': weights, 'canonical_tuples': len(seeds), 'tiny_profiles': tiny,
              'semantic_rejections': controls, 'complete_header_fibre': gl(4),
              'header_per_coordinate_pair': [w * c for w, c in zip(weights, z)],
              'credited_full_guard_contributions': contributions,
              'credited_full_guard_total': sum(contributions)}
    require(result == json.loads((ROOT / 'RESULT.json').read_text()), 'result replay')
    print('PASS_SCHUR_SPLIT_INCIDENCE', json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
