"""Read-only exact certificates for a conditional P104 transport relaxation.

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable, optimizer or numerical library is imported.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from math import factorial
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
SCALE = 10**50


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def read(path):
    need(path.stat().st_size <= 2_000_000, 'bounded JSON input')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_pairs)


def authenticate():
    manifest = read(P / 'SOURCES.json')
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'live source SHA256')
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'live source Git blob')
    for row in read(P / 'PREDECESSORS.json')['files']:
        raw = (P / row['local']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'retained predecessor SHA256')
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'retained predecessor Git blob')


def space(basis):
    """512-bit characteristic function of a binary span; no echelon dependency."""
    values = [0]
    for vector in basis:
        need(type(vector) is int and 0 < vector < 512, 'frame vector')
        values += [x ^ vector for x in values]
    need(len(values) == len(set(values)), 'independent frame basis')
    return sum(1 << x for x in values)


def subset(a, b):
    return a & ~b == 0


def binary_rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            j = vector.bit_length()-1
            if j not in pivots:
                pivots[j] = vector
                break
            vector ^= pivots[j]
    return len(pivots)


def demands_from_sources():
    base = ROOT / 'research/p104-native-channel/inputs'
    word = read(base / 'LOWRANK-WITNESS.json')
    fixture = read(base / 'P104-FIXTURE.json')['section4_explicit_P104']
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *tail) for tail in product((-1, 1), repeat=7)
              if tail.count(-1) % 2 == 0]
    removed = {tuple(row) for row in fixture['F0'] + fixture['C']}
    ports = sorted(set(roots) - removed)
    need(len(roots) == 120 and len(removed) == 16 and len(ports) == 104, 'root order')
    names = [f'{kind}{j}' for kind in 'XY' for j in range(104)]
    paths = {r: [(len(word['initial_frames'][r]), space(word['initial_frames'][r]))]
             for r in names}
    need(len(word['program']) == 4058, 'frozen event count')
    for event in word['program']:
        if event[0] == 'add':
            need(not event[1].startswith('X') and not event[2].startswith('Y'),
                 'immutable sources and unread targets')
        if event[0] != 'transport' or event[1] not in paths:
            continue
        _, name, old, new, rank = event
        before, after = space(old), space(new)
        need(paths[name][-1] == (len(old), before), 'chronological entry')
        need(before != after and subset(before, after) and rank == len(new)-len(old),
             'strict original path')
        paths[name].append((len(new), after))
    for name in names:
        final = word['final_frames'][name]
        need(paths[name][-1] == (len(final), space(final)), 'original endpoint')
    labels = [word['initial_frames'][f'X{s}'][0] for s in range(104)]
    targets = [space(word['final_frames'][f'Y{t}']) for t in range(104)]
    normals = []
    for t in range(104):
        basis = word['final_frames'][f'Y{t}']
        candidates = [n for n in range(1, 512)
                      if all((n & v).bit_count() % 2 == 0 for v in basis)]
        need(len(candidates) == 1, 'unique target normal')
        normals.append(candidates[0])
    need(len(set(labels)) == len(set(normals)) == 104, 'distinct label alphabets')
    for points in (labels, normals):
        need(any(all((n & v).bit_count() % 2 for v in points) for n in range(1, 512)),
             'affine odd capacity premise')
    pairs = []
    for t, a in enumerate(ports):
        for s, b in enumerate(ports):
            dot = sum(x*y for x, y in zip(a, b))
            c = Q(t == s) - Q(dot, 8)
            if c:
                need(c in (Q(-1, 2), Q(1, 2)) and targets[t] >> labels[s] & 1,
                     'correction support in target')
                pairs.append((t, s))
    need(len(pairs) == 4992, 'nonzero correction entries')
    # PR2353's proof needs two source-dependent proper entries at each distinct
    # target hyperplane. Recheck its finite premise, not merely a free count floor.
    for t in range(104):
        late = [labels[s] for tt, s in pairs if tt == t
                and not any(d < 8 and f >> labels[s] & 1 for d, f in paths[f'Y{t}'])
                and not any(f == targets[t] for _, f in paths[f'X{s}'])]
        need(binary_rank(late) == 8, 'two proper endpoint arrivals per target')
    cuts = []
    for k in range(1, 8):
        forced = [(t, s) for t, s in pairs
                  if not any(d > k and subset(f, targets[t]) for d, f in paths[f'X{s}'])
                  and not any(d <= k and f >> labels[s] & 1 for d, f in paths[f'Y{t}'])]
        raw = json.dumps(forced, separators=(',', ':')).encode()
        cuts.append({'cut': k, 'forced': len(forced),
                     'forced_sha256': hashlib.sha256(raw).hexdigest()})
    prior = read(P / 'inputs/PR2640-EXPECTED.json')['cuts']
    need(cuts == [{k: row[k] for k in cuts[0]} for row in prior], 'all seven predecessor sets')
    return cuts


def histories():
    rows = []
    for mask in range(256):
        stops = [0] + [k for k in range(1, 9) if mask >> (k-1) & 1] + [9]
        jumps = [b-a for a, b in zip(stops, stops[1:])]
        capacities = []
        for cut in range(1, 8):
            a, b = next((a, b) for a, b in zip(stops, stops[1:]) if a <= cut < b)
            capacities.append(0 if a == 0 or b == 9 else 1 << (7-(b-a)))
        arrival = int(8 in stops and stops[stops.index(8)-1] > 0)
        rows.append({'mask': mask, 'jumps': jumps, 'capacities': capacities,
                     'endpoint_arrival': arrival})
    need(len({tuple(row['jumps']) for row in rows}) == 256, 'complete compositions')
    return rows


def ceilq(value):
    return -(-value.numerator // value.denominator)


@lru_cache(None)
def logarithm(n):
    """Positive atanh series with a geometric upper bound for its tail."""
    def unit(x):
        z = (x-1)/(x+1)
        total = sum((2*z**(2*j+1)/Q(2*j+1) for j in range(60)), Q(0))
        tail = 2*z**121 / (121*(1-z*z))
        return total, total+tail
    k = n.bit_length()-1
    lo, hi = unit(Q(n, 1 << k))
    l2, h2 = unit(Q(2))
    return lo+k*l2, hi+k*h2


@lru_cache(None)
def power(n, p):
    """Integer outward rounding, exp after division by 16, then four squares."""
    need(type(n) is int and 1 <= n <= 9 and 0 < p <= 1, 'power domain')
    if n == 1 or p == 1:
        return n*SCALE, n*SCALE
    lo, hi = logarithm(n)
    low = (lo*p*SCALE/16).__floor__()
    high = ceilq(hi*p*SCALE/16)
    need(0 <= low <= high <= SCALE//4, 'exp small argument')
    a = b = u = v = SCALE
    for j in range(1, 61):
        a = a*low//(SCALE*j)
        b = -(-b*high//(SCALE*j))
        u, v = u+a, v+b
    need(Q(SCALE, 4**61*factorial(61)) / (1-Q(1, 4*62)) < 1, 'exp tail < one unit')
    v += 1
    for _ in range(4):
        u, v = u*u//SCALE, -(-v*v//SCALE)
    return u, v


def matrix(rows, proper_arrivals=True):
    return [row['capacities'] + [row['endpoint_arrival'] if proper_arrivals else 1]
            for row in rows]


def check_certificate(cert, rows, demands, p, proper_arrivals=True):
    costs = [tuple(sum(power(r, p)[side] for r in row['jumps'])
                   for side in (0, 1)) for row in rows]
    weights = [Q(value) for value in cert['dual']]
    need(len(weights) == 8 and all(w >= 0 for w in weights), 'dual nonnegative')
    a = matrix(rows, proper_arrivals)
    for coefficients, (lower, _) in zip(a, costs):
        need(sum(c*w for c, w in zip(coefficients, weights)) <= lower,
             'dual inequality for every history')
    need(all(type(k) is str and k == str(int(k)) and type(x) is str
             for k, x in cert['primal'].items()), 'canonical primal encoding')
    counts = {int(mask): Q(value) for mask, value in cert['primal'].items()}
    need(all(0 <= m < 256 and x >= 0 for m, x in counts.items()), 'primal domain')
    b = demands + [208]
    for j, bound in enumerate(b):
        need(sum(a[m][j]*x for m, x in counts.items()) >= bound, 'primal constraint')
    count = sum(counts.values())
    need(count <= 482, 'feasible witness also respects 482 lifetime cap')
    lower = sum(w*d for w, d in zip(weights, b))/SCALE
    upper = sum(costs[m][1]*x for m, x in counts.items())/SCALE
    need(0 <= upper-lower < Q(1, 10**40), 'certified optimum enclosure')
    return {'p': str(p), 'lower': str(lower), 'upper': str(upper),
            'lifetimes': str(count), 'primal': cert['primal'], 'dual': cert['dual'],
            'active_histories': [{'mask': m, 'jumps': rows[m]['jumps'], 'count': str(x)}
                                 for m, x in sorted(counts.items()) if x]}


def compute():
    authenticate()
    cuts = demands_from_sources()
    rows = histories()
    selected = read(ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json')
    ps = [Q(1), 1-Q(selected['complex_lower']), Q(98, 99)]
    certificates = read(P / 'CERTIFICATES.json')
    need(set(certificates) == {str(p) for p in ps}, 'exact exponent set')
    result = [check_certificate(certificates[str(p)], rows,
                                [row['forced'] for row in cuts], p) for p in ps]
    weak_certs = read(P / 'COUNT-ONLY.json')
    need(set(weak_certs) == {str(p) for p in ps}, 'count-only exponent set')
    weak = [check_certificate(weak_certs[str(p)], rows,
                             [row['forced'] for row in cuts], p, False) for p in ps]
    gaps = [{'p': str(p), 'lower': str(Q(a['lower'])-Q(b['upper'])),
             'upper': str(Q(a['upper'])-Q(b['lower']))}
            for p, a, b in zip(ps, result, weak)]
    need(all(Q(g['lower']) > 1 for g in gaps[1:]), 'strict transport bound strengthening')
    # An integer feasible witness matters: fractional feasibility alone would
    # not show that these necessary constraints admit 208 whole lifetimes.
    integer_counts = {129: 137, 255: 71}
    a = matrix(rows)
    integer_constraints = [sum(a[m][j]*x for m, x in integer_counts.items())
                           for j in range(8)]
    need(integer_constraints == [4681]*7+[208], '208 integral lifetime witness')
    integer_bills = []
    for p in ps:
        lo, hi = power(7, p)
        integer_bills.append({'p': str(p), 'lower': str(Q(913*SCALE+137*lo, SCALE)),
                              'upper': str(Q(913*SCALE+137*hi, SCALE))})
    return {'scope': 'conditional fractional transport-only relaxation',
            'histories': len(rows), 'cuts': cuts, 'results': result,
            'count_only_results': weak, 'proper_arrival_strengthening': gaps,
            'endpoint_arrivals_required': 208,
            'integer_witness': {'counts': {'129': 137, '255': 71},
                                'constraints': integer_constraints,
                                'profile': {'1': 913, '7': 137},
                                'bills': integer_bills},
            'ignored_costs': ['ADDs', 'geometry and chronology coupling', 'native adapters',
                              'hosting and idle/residual', 'precision/tape', 'consumer'],
            'no_supplier_or_kappa_claim': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        need(json.dumps(result, sort_keys=True) == json.dumps(read(P/'RESULT.json'), sort_keys=True),
             'complete typed receipt')
        print('PASS_P104_CROSSING_PROFILE_SCREEN histories=256 cuts=7 exponents=3')


if __name__ == '__main__':
    main()
