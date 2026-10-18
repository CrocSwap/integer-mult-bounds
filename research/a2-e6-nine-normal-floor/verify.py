#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound exact A2+E6 P112 COPY floor; standard library, no search oracle."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ALL = (1 << 512) - 1
PAIRS = ((0, 1), (0, 2), (1, 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_check(root=ROOT):
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for item in pins['files']:
        if item['usage'] == 'input':
            actual = hashlib.sha256((root / item['path']).read_bytes()).hexdigest()
            require(actual == item['sha256'], 'source mismatch: ' + item['path'])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup():
    source_check()  # Authenticate all external executable bytes before importing them.
    predecessor = ROOT / 'research/nine-term-decoder-normal-form-seed42'
    sys.modules['e8lab'] = load('e8lab', predecessor / 'e8lab.py')
    model = load('a2_e6_predecessor', predecessor / 'verify.py')
    frame = model.build_frames()['A2 weights + E6 root basis']
    puncture = model.coordinate_frame()
    indices = [i for i in range(120) if i not in puncture]
    live = sum(1 << i for i in indices)
    base = {i: frame.base(i) for i in indices}
    return model, frame, puncture, indices, live, base


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def character_table(E):
    basis, nonzero = E.code_words()
    require(len(basis) == 9 and len(set(nonzero)) == 511, 'label code dimension')
    return basis, [0] + nonzero


def compatibility(characters, constraints):
    return {
        pair: [sum(1 << v for v in range(512)
                   if not (characters[u] & characters[v] & mask))
               for u in range(512)]
        for pair, mask in constraints.items()
    }


def span(values):
    result = {0}
    for value in values:
        if value not in result:
            result |= {value ^ old for old in tuple(result)}
    return sum(1 << value for value in result)


def census(relations):
    degrees = {}
    triple = []
    pair_exceptions = ((1, 512), (446, 256), (256, 256))
    degree_expected = ({4: 508, 2: 2, 512: 1},
                       {2: 255, 4: 254, 1: 1, 256: 1},
                       {2: 255, 4: 254, 1: 1, 256: 1})
    for pair, exception, expected in zip(PAIRS, pair_exceptions, degree_expected):
        table = relations[pair]
        require(table[0] == ALL, 'zero character must be free')
        require(all(span(members(mask)) == mask for mask in table), 'compatibility is a subspace')
        require(all(bool(table[u] >> v & 1) == bool(table[v] >> u & 1)
                    for u in range(512) for v in range(512)), 'pair symmetry')
        distribution = Counter(mask.bit_count() for mask in table[1:])
        require(distribution == expected, 'pair compatibility census')
        large = [(u, mask.bit_count()) for u, mask in enumerate(table) if u and mask.bit_count() > 4]
        require(large == [exception], 'unique large partner space')
        degrees[str(pair)] = {'sizes': dict(sorted(distribution.items())), 'exception': list(exception)}
    expected_large = ((1, 446, 256), (1, 256, 256), (446, 256, 128))
    expected_hist = ({1: 759, 2: 511, 4: 1, 256: 1},
                     {1: 759, 2: 511, 4: 1, 256: 1},
                     {1: 1396, 2: 639, 4: 1, 128: 1})
    for k in range(3):
        j, ell = [x for x in range(3) if x != k]
        left = relations[tuple(sorted((k, j)))]
        right = relations[tuple(sorted((k, ell)))]
        cross = relations[tuple(sorted((j, ell)))]
        histogram, large = Counter(), []
        for u in range(1, 512):
            for v in members(cross[u] & ~1):
                size = (left[u] & right[v]).bit_count()
                histogram[size] += 1
                if size > 4:
                    large.append((u, v, size))
        require(histogram == expected_hist[k], 'triple partner census')
        require(large == [expected_large[k]], 'unique large triple partner space')
        triple.append({'large_side': k, 'partner_sides': [j, ell],
                       'sizes': dict(sorted(histogram.items())), 'exception': list(large[0])})
    return degrees, triple


def exact_identity(E, frame, indices, rows):
    for i in indices:
        for j in indices:
            value = sum(rows[i][k] * sum(Q(a) * b for a, b in zip(E.LINES[j], frame.F[k])) / 4
                        for k in range(9))
            if value != 2 * E.G[i][j]:
                return False
    return True


def budget():
    ceiling = load('a2_e6_ceiling', ROOT / 'research/complex-local-word-ceiling/ceiling.py')
    selected = json.loads((ROOT / 'research/complex-local-word-ceiling/RESULT.json').read_text())
    local = {int(r): Q(n) for r, n in selected['selected']['local_profile_per_call'].items()}
    require(local.pop(8) == 8, 'selected centre inventory')
    require(sum(r * n for r, n in local.items()) == 5522, 'fixed noncentre mass')
    result = {}
    for cost in (65, 69):
        optimistic = dict(local)
        optimistic[9] = Q(cost, 9)
        lo, hi = ceiling.ceiling(optimistic, 73, 896, 9, cost)
        require(hi < Q(selected['ceiling']['a_relaxation_achievable']), 'optimistic screen fails even incumbent ceiling')
        result[str(cost)] = {'a_bracket': [str(lo), str(hi)],
                            'kappa_cap': str(hi / (1 + hi)),
                            'moment_at_lower': [str(x) for x in ceiling.relax(optimistic, 73, 896, 9, cost, lo)],
                            'moment_at_upper': [str(x) for x in ceiling.relax(optimistic, 73, 896, 9, cost, hi)]}
    result['model'] = {'noncentre': {str(r): int(n) for r, n in local.items()}, 'width': 73,
                       'families': 896, 'stages': 9, 'idle_rank_cap': 51, 'idle_mass': 1646,
                       'centre_rank_cap': 9, 'additional_interface_overhead': 0,
                       'coverage': '72W + C N; assumed for conditional substitution only',
                       'comparison': 'selected word ceiling, original gate is 5 percent above it'}
    return result


def run():
    model, frame, puncture, indices, live, base = setup()
    E = model.E
    require(frame.S == [0, 1, 2] and frame.z == [Q(-1)] * 3 + [Q(0)] * 6, 'fixed dependency')
    require(len(indices) == 112 and E.q_rank([list(frame.F[k]) for k in range(9)]) == 8, 'geometry ranks')
    require(E.q_rank([list(E.LINES[i]) for i in indices]) == 8, 'live root rank')
    basis, characters = character_table(E)
    require(E.label_dim(live) == 9, 'punctured label span')
    column_ranks = [E.label_dim(E.support(b, live)) for b in frame.F]
    require(column_ranks == [9, 9, 9, 8, 8, 9, 9, 9, 9], 'column support ranks')
    costs, _, _ = model.decoder_cost(base, frame.F, live)
    require(costs[3:] == [8, 8, 9, 9, 9, 9], 'six forced costs')
    constraints = {pair: sum(1 << i for i in indices if base[i][pair[0]] != base[i][pair[1]])
                   for pair in PAIRS}
    pair_ranks = [E.label_dim(constraints[pair]) for pair in PAIRS]
    require(pair_ranks == [8, 9, 9], 'initial rank-sum budget floor')
    relations = compatibility(characters, constraints)
    degrees, triples = census(relations)
    kernels = [relations[(0, 1)][1] & relations[(0, 2)][446], 1 | (1 << 1), 1 | (1 << 446)]
    require([mask.bit_count() for mask in kernels] == [256, 2, 2], 'attaining kernel dimensions')
    forced_zero = [0, 0, 0]
    for k in range(3):
        for w in members(kernels[k]):
            forced_zero[k] |= characters[w]
    rows, shifts = {}, {}
    for i in indices:
        required = {base[i][k] for k in range(3) if forced_zero[k] >> i & 1}
        require(len(required) <= 1, 'attaining shifts compatible')
        t = next(iter(required), Q(0))
        shifts[i] = t
        rows[i] = [base[i][k] - t if k < 3 else base[i][k] for k in range(9)]
    require({i: t for i, t in shifts.items() if t} == {45: Q(-4)}, 'single-port witness')
    require(exact_identity(E, frame, indices, rows), 'all-pairs decoder identity')
    per_term, supports, columns = model.decoder_cost(rows, frame.F, live)
    require(per_term == [1, 8, 8, 8, 8, 9, 9, 9, 9], 'sharp active COPY69 witness')
    require(all(supports), 'all nine terms active')
    # Semantic controls, not weakened acceptance conditions.
    bad_rows = {i: list(row) for i, row in rows.items()}
    bad_rows[45][0] += 1
    require(not exact_identity(E, frame, indices, bad_rows), 'coefficient mutation must fail')
    generic = {i: [base[i][k] - Q(1, 3) if k < 3 else base[i][k] for k in range(9)] for i in indices}
    generic_costs = model.decoder_cost(generic, frame.F, live)[0]
    require(generic_costs == [9, 9, 9, 8, 8, 9, 9, 9, 9], 'generic complex-shift support class')
    require(sum(generic_costs) == 79, 'zero-pattern selection matters')
    wrong = {pair: list(table) for pair, table in relations.items()}
    wrong[(0, 2)][1] |= 1 << 1
    try:
        census(wrong)
    except ValueError:
        pass
    else:
        raise ValueError('compatibility mutation accepted')
    return {'status': 'PASS_A2_E6_NINE_NORMAL_FLOOR', 'minimum_copy': 69,
            'variable_cost_floor': 17, 'maximum_deficiency_sum': 10, 'fixed_cost': 52,
            'puncture': puncture, 'live_root_count': len(indices),
            'normal_vectors_doubled': [[str(x) for x in v] for v in frame.F],
            'dependency': [str(x) for x in frame.z],
            'character_basis_hex': [hex(x) for x in basis],
            'column_label_ranks': column_ranks, 'pair_support_ranks': pair_ranks,
            'pair_compatibility': degrees, 'triple_compatibility': triples,
            'witness': {'nonzero_shifts': {'45': '-4'}, 'per_term_copy': per_term,
                        'row_supports_hex': [hex(x) for x in supports],
                        'column_supports_hex': [hex(x) for x in columns],
                        'identity_entries': len(indices) ** 2, 'all_terms_active': True},
            'budget': budget(),
            'controls': ['changed coefficient rejected', 'generic shift costs 79',
                         'changed compatibility rejected', 'all nine actual supports charged']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='regenerate RESULT.json explicitly')
    args = parser.parse_args()
    result = run()
    # JSON normalization makes integer histogram keys portable and explicit.
    result = json.loads(json.dumps(result))
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(result == json.loads((HERE / 'RESULT.json').read_text()), 'saved certificate mismatch')
    print('PASS_A2_E6_NINE_NORMAL_FLOOR copy=69 active=9 variable=17 fixed=52 entries=12544 controls=4')


if __name__ == '__main__':
    main()
