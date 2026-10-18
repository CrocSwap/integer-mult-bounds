"""Check a coupled P104 profile LP certificate, without an optimizer.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
The network implications are the credited written proofs in README.md.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PINS = {
    'research/p104-native-channel/inputs/LOWRANK-WITNESS.json':
        '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e',
    'research/p104-native-channel/inputs/P104-FIXTURE.json':
        '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4',
    'research/complex-local-word-ceiling/ceiling.py':
        '86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc',
}
BASE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}
FORCED = [4656, 4656, 4672, 4680, 4672, 4656, 4656]
RHS = FORCED + [208, 208]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def unique(pairs):
    result = dict(pairs)
    need(len(result) == len(pairs), 'duplicate JSON key')
    return result


def read_json(path):
    need(path.stat().st_size <= 2_000_000, 'JSON size limit')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def rational(value):
    need(type(value) is str and len(value) <= 320, 'rational encoding')
    result = Q(value)
    need(max(abs(result.numerator).bit_length(), result.denominator.bit_length()) <= 512,
         'rational size limit')
    return result


def span(basis):
    result = {0}
    need(len(basis) <= 9, 'frame dimension')
    for vector in basis:
        need(type(vector) is int and 0 < vector < 512, 'binary vector')
        result |= {v ^ vector for v in tuple(result)}
    need(len(result) == 2 ** len(basis), 'independent frame basis')
    return frozenset(result)


def geometry(witness, fixture):
    """Reconstruct finite premises, not the entire native/channel theorem."""
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    puncture = fixture['section4_explicit_P104']
    ports = sorted(roots - {tuple(v) for v in puncture['F0'] + puncture['C']})
    need(len(roots) == 120 and len(ports) == 104, 'P104 geometry')
    names = [f'{kind}{i}' for kind in 'XY' for i in range(104)]
    paths = {n: [span(witness['initial_frames'][n])] for n in names}
    paid = Counter()
    need(len(witness['program']) == 4058, 'frozen word length')
    for event in witness['program']:
        if event[0] == 'add':
            need(not event[1].startswith('X') and not event[2].startswith('Y'),
                 'source/target directions')
        if event[0] == 'transport':
            _, name, old, new, rank = event
            paid[rank] += 1
            if name in paths:
                before, after = span(old), span(new)
                need(paths[name][-1] == before < after and rank == len(new) - len(old),
                     'frozen monotone data path')
                paths[name].append(after)
    need(dict(paid) == BASE, 'whole channel paid profile')
    for name in names:
        need(paths[name][-1] == span(witness['final_frames'][name]), 'data endpoint')
    lines = [paths[f'X{s}'][0] for s in range(104)]
    hyper = [paths[f'Y{t}'][-1] for t in range(104)]
    need(len(set(lines)) == len(set(hyper)) == 104, 'distinct endpoints')
    need(all(len(v) == 2 for v in lines) and all(len(v) == 256 for v in hyper),
         'line/hyperplane dimensions')
    labels = [next(v for v in line if v) for line in lines]
    normals = []
    for h in hyper:
        dual = [n for n in range(1, 512) if all((v & n).bit_count() % 2 == 0 for v in h)]
        need(len(dual) == 1, 'unique normal')
        normals.append(dual[0])
    need(all(any(all((q & v).bit_count() % 2 for v in alphabet) for q in range(1, 512))
             for alphabet in (labels, normals)), 'two affine odd functionals')
    demands = set()
    for t, left in enumerate(ports):
        for s, right in enumerate(ports):
            gram4 = sum(a * b for a, b in zip(left, right, strict=True))
            need(gram4 % 4 == 0, 'integral Gram entry')
            if Q(t == s) - Q(gram4, 8):
                demands.add((t, s))
            need((labels[s] in hyper[t]) == (gram4 % 8 == 4), 'support/frame binding')
    need(len(demands) == 4992, 'correction support count')
    source_bypass, target_bypass, counts = [], [], []
    for k in range(1, 8):
        sb = {(t, s) for t, s in demands if any(len(v) > 2**k and v <= hyper[t]
              for v in paths[f'X{s}'])}
        tb = {(t, s) for t, s in demands if any(len(v) <= 2**k and labels[s] in v
              for v in paths[f'Y{t}'])}
        source_bypass.append(len(sb))
        target_bypass.append(len(tb))
        counts.append(len(demands - sb - tb))
    need(counts == FORCED, 'all seven forced counts')
    for s in range(104):
        forced = [t for t in range(104) if (t, s) in demands and not any(
            len(v) > 2 and v <= hyper[t] for v in paths[f'X{s}'])]
        intersection = frozenset(range(512))
        for t in forced:
            intersection &= hyper[t]
        need(intersection == lines[s], 'two-departure intersection premise')
        need(all(lines[s] not in paths[f'Y{t}'] for t in range(104)), 'no target line bypass')
    for t in range(104):
        residual = [labels[s] for s in range(104) if (t, s) in demands
                    and not any(labels[s] in v for v in paths[f'Y{t}'] if len(v) < 256)
                    and hyper[t] not in paths[f'X{s}']]
        generated = {0}
        for v in residual:
            generated |= {x ^ v for x in tuple(generated)}
        need(generated == hyper[t], 'two-arrival spanning premise')
    return {'forced': counts, 'source_bypass': source_bypass,
            'target_bypass': target_bypass, 'departure_lines': 104, 'arrival_hyperplanes': 104}


def histories():
    result = []
    for mask in range(256):
        stops = [0] + [i for i in range(1, 9) if mask & (1 << (i - 1))] + [9]
        edges = list(zip(stops[:-1], stops[1:], strict=True))
        capacities = []
        for k in range(1, 8):
            left, right = next((u, v) for u, v in edges if u <= k < v)
            capacities.append(0 if left == 0 or right == 9 else 2 ** (7 - right + left))
        result.append(([v - u for u, v in edges], capacities + [int(1 in stops), int(8 in stops)]))
    return result


def check_certificate(certificate, cost):
    need(set(certificate) == {'a_lo', 'a_hi', 'primal', 'dual', 'cost_rounding_scale'},
         'certificate fields')
    lo, hi = rational(certificate['a_lo']), rational(certificate['a_hi'])
    need(0 < lo < hi < Q(1, 100) and hi - lo <= Q(1, 10**10), 'saving bracket')
    need(type(certificate['cost_rounding_scale']) is int and
         certificate['cost_rounding_scale'] == 10**14, 'proposer rounding scale')
    x = {}
    for key, value in certificate['primal'].items():
        need(key.isdecimal() and key == str(int(key)) and 0 <= int(key) < 256, 'history index')
        x[int(key)] = rational(value)
    mu = [rational(v) for v in certificate['dual']]
    need(len(mu) == 9 and all(v >= 0 for v in mu) and all(v > 0 for v in x.values()),
         'nonnegative primal/dual')
    h = histories()
    totals = [sum(xj * h[j][1][i] for j, xj in x.items()) for i in range(9)]
    need(all(v >= b for v, b in zip(totals, RHS, strict=True)), 'primal coupled capacities')
    lifetimes = sum(x.values())
    need(9 * lifetimes <= 4344, 'nonnegative ideal idle mass')
    profile = Counter({r: Q(n) for r, n in BASE.items()})
    for j, xj in x.items():
        for r in h[j][0]:
            profile[r] += xj
    upper = cost.relax(profile, 73, 832, 9, 56, lo)[1]
    need(upper < 1, 'primal strict feasible moment')
    cc = {r: cost.child_cost(r, 73, hi) for r in range(1, 10)}
    idle = cost.child_cost(51, 73, hi)
    for jumps, column in h:
        price_lower = sum(cc[r][0] for r in jumps) - Q(9, 51) * idle[1]
        need(sum(u * v for u, v in zip(mu, column, strict=True)) <= price_lower,
             'dual history inequality')
    constant_lower = sum(n * cc[r][0] for r, n in BASE.items()) + Q(4344, 51) * idle[0]
    lower = (constant_lower + sum(u * v for u, v in zip(mu, RHS, strict=True))) / Q(832, 9)
    need(lower > 1, 'dual strict exclusion moment')
    selected = Q(67018507072324140917, 40000000000000000000000)
    selected_upper = cost.relax(profile, 73, 832, 9, 56, selected)[1]
    need(selected_upper < 1, 'selected-budget positive relaxation')
    integer = Counter(BASE)
    integer[1] += 2 * 137 + 9 * 71
    integer[7] += 137
    need(all(137 * h[129][1][i] + 71 * h[255][1][i] >= RHS[i] for i in range(9)),
         'integer relaxation capacities')
    integer_upper = cost.relax(integer, 73, 832, 9, 56, selected)[1]
    need(integer_upper < 1, 'integer selected-budget relaxation')
    def decimal_upper(q):
        return str(Q(-((-q.numerator * 10**15) // q.denominator), 10**15))
    def decimal_lower(q):
        return str(Q((q.numerator * 10**15) // q.denominator, 10**15))
    return {'a_lo': str(lo), 'a_hi': str(hi), 'histories': 256,
            'lifetimes': str(lifetimes), 'constraint_totals': [str(v) for v in totals],
            'local_profile': {str(r): str(n) for r, n in sorted(profile.items())},
            'idle_rank_mass': str(Q(4344) - 9 * lifetimes),
            'primal_moment_upper': decimal_upper(upper),
            'dual_moment_lower': decimal_lower(lower),
            'selected_relaxation_upper': decimal_upper(selected_upper),
            'integer_selected_relaxation_upper': decimal_upper(integer_upper)}


def calculate():
    for path, digest in PINS.items():
        source = ROOT / path
        need(source.stat().st_size <= 2_000_000, 'source size limit')
        need(hashlib.sha256(source.read_bytes()).hexdigest() == digest, 'source hash: ' + path)
    spec = importlib.util.spec_from_file_location('p104_pinned_cost', ROOT / 'research/complex-local-word-ceiling/ceiling.py')
    cost = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cost)
    finite = geometry(read_json(ROOT / 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'),
                      read_json(ROOT / 'research/p104-native-channel/inputs/P104-FIXTURE.json'))
    certificate = read_json(PACKAGE / 'CERTIFICATE.json')
    return {'finite_premises': finite, **check_certificate(certificate, cost)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = calculate()
    expected = read_json(PACKAGE / 'EXPECTED.json')
    need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
         'complete expected receipt')
    if args.out:
        with args.out.open('x', encoding='utf-8') as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS_P104_COUPLED_PROFILE_BUDGET histories=256 a_lo=' + result['a_lo'] + ' a_hi=' + result['a_hi'])


if __name__ == '__main__':
    main()
