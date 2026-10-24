#!/usr/bin/env python3
"""Exact two-stage support witness. Cinna Davis, substantial OpenAI assistance; Apache-2.0."""
import argparse, json
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
from fractions import Fraction as F
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
p = ROOT / 'research/coded-native-caller'

def need(ok, message):
    if not ok:
        raise ValueError(message)
for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
    if row.get('usage') == 'input':
        need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'Live source hash: ' + row['path'])
n = json.loads((p / 'NORMALIZERS.json').read_text())['ports']
a = [[F(x) for x in row] for row in json.loads((p / 'CODE.json').read_text())['A']]

def parity(x):
    return x.bit_count() & 1

def act(g, x):
    y = 0
    while x:
        b = x & -x
        y ^= g[b.bit_length() - 1]
        x ^= b
    return y

def transpose(g):
    return tuple((sum(((c >> i & 1) << j for j, c in enumerate(g))) for i in range(len(g))))

def compose(l, r):
    g, b = l
    h, c = r
    return (tuple((act(g, x) for x in h)), c ^ sum((parity(b & x) << i for i, x in enumerate(h))))

def inv(m):
    g, b = m
    h = transpose(g)
    return (h, sum((parity(b & x) << i for i, x in enumerate(h))))

def embed(rec, offset):
    cols = transpose(rec['G_rows'])
    z = rec['Z_mask']
    bits = [0] + list(range(offset, offset + 8))

    def lift(x):
        return sum(((x >> j & 1) << bits[j] for j in range(9)))
    g = [1 << i for i in range(17)]
    for j, b in enumerate(bits):
        g[b] = lift(cols[j])
    beta = sum((parity(z & x) << i for i, x in enumerate(cols)))
    return (tuple(g), lift(beta))
ks = [[embed(r, o) for r in n] for o in (1, 9)]

def expansion(m, x):
    g, b = m
    s = 1 - 2 * parity(b & x)
    t = 1 - 2 * parity(b & (x ^ 1))
    v = act(g, x)
    w = g[0]
    d = {}
    for y, c in [(v, (s, 0)), (v ^ w, (0, -t)), (v ^ 1, (0, s)), (v ^ w ^ 1, (t, 0))]:
        old = d.get(y, (0, 0))
        d[y] = (old[0] + c[0], old[1] + c[1])
    return {k: v for k, v in d.items() if v != (0, 0)}

def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])

def direct_k(record, offset, x, backwards=False):
    """Independent row-based action; does not use composed 17-axis matrices."""
    bits = [0] + list(range(offset, offset + 8))
    local = sum(((x >> bit & 1) << j for j, bit in enumerate(bits)))
    rows, z = (record['G_rows'], record['Z_mask'])
    if backwards:
        sign = 1 - 2 * parity(z & local)
        rows = transpose(rows)
    transformed = sum((parity(row & local) << j for j, row in enumerate(rows)))
    if not backwards:
        sign = 1 - 2 * parity(z & transformed)
    mask = sum((1 << bit for bit in bits))
    return (x & ~mask | sum(((transformed >> j & 1) << bit for j, bit in enumerate(bits))), sign)

def direct_entry(k, x, y):
    """Twice the entry, by the actual four Q/inverse-Q terms and four K actions."""
    value = (0, 0)
    for toggle, incoming in ((0, (1, 1)), (1, (1, -1))):
        v, sign = (x ^ toggle, 1)
        for owner, offset, backwards in ((1, 9, False), (k, 9, True), (k, 1, False), (0, 1, True)):
            v, s = direct_k(n[owner], offset, v, backwards)
            sign *= s
        for out_toggle, outgoing in ((0, (1, -1)), (1, (1, 1))):
            if y == v ^ out_toggle:
                term = mul(incoming, outgoing)
                value = (value[0] + sign * term[0], value[1] + sign * term[1])
    need(all((v % 2 == 0 for v in value)), 'Twice-entry Gaussian integrality')
    return (value[0] // 2, value[1] // 2)

def run():
    need(len(a) == 112 and all((len(row) == 112 for row in a)), '112-owner code')
    b = [[int(2 * x) for x in row] for row in a]
    need(all((F(b[i][j], 2) == a[i][j] and b[i][j] in (-1, 0, 1) for i in range(112) for j in range(112))), 'Half-integral source code')
    need(all((sum((b[i][k] * b[k][j] for k in range(112))) + 24 * b[i][j] == 52 * (i == j) for i in range(112) for j in range(112))), 'A^2+12A=13I, including inverse diagonal')
    unsigned = 0
    for r in n:
        g, z = (r['G_rows'], r['Z_mask'])
        need(all((parity(x & y) == (i == j) for i, x in enumerate(g) for j, y in enumerate(g))), 'Orthogonal K')
        need(transpose(g)[0] == r['q'], 'Actual central port')
        for x in range(512):
            y = sum((parity(row & x) << j for j, row in enumerate(g)))
            need((y.bit_count() - x.bit_count() - 2 * parity(z & y)) % 4 == 0, 'Literal signed Gaussian phase')
            unsigned += (y.bit_count() - x.bit_count()) % 4 != 0
    need(unsigned > 0, 'Unsigned phase control')
    paths = [compose(compose(inv(ks[0][0]), ks[0][k]), compose(inv(ks[1][k]), ks[1][1])) for k in range(112)]
    chosen = paths[31]
    need(chosen[0][0] == 2048 and chosen[1] == 1038, 'Selected literal path')
    need(transpose(chosen[0])[0] == 16, 'Selected inverse central image')
    direct_checks = 0
    for k in range(112):
        for x in (0, 1, 2, 16, 17, 512, 2048, 65536):
            expected = expansion(paths[k], x)
            for y in set(expected) | {0, 1, 2048}:
                need(direct_entry(k, x, y) == expected.get(y, (0, 0)), 'Independent signed K/Q evaluator')
                direct_checks += 1
    cases = []
    for e, f in product((1, -1), repeat=2):
        weights = [(b[0][k] + 24 * (e == -1 and k == 0)) * (b[k][1] + 24 * (f == -1 and k == 1)) for k in range(112)]
        grouped = Counter()
        for k, w in enumerate(weights):
            grouped[paths[k]] += w
        isolated = [(k, w, expansion(paths[k], 0)[2048]) for k, w in enumerate(weights) if w and 2048 in expansion(paths[k], 0)]
        need(isolated == [(31, 1, (0, -1))], 'Unique marker across all paths')
        finite = []
        for width in (1, 2, 3, 4):
            count = 0
            for rest in product((0, 1, 16, 17), repeat=width - 1):
                entry = (0, 0)
                for k, w in enumerate(weights):
                    if not w:
                        continue
                    term = direct_entry(k, 0, 2048)
                    for x in rest:
                        term = mul(term, direct_entry(k, x, 0))
                    entry = (entry[0] + w * term[0], entry[1] + w * term[1])
                target = (0, -1)
                for x in rest:
                    target = mul(target, expansion(chosen, x).get(0, (0, 0)))
                need(entry == target and entry in ((1, 0), (-1, 0), (0, 1), (0, -1)), 'Literal coefficient once and tensor support')
                count += 1
            finite.append({'width': width, 'restricted_row_nonzero_entries': count})
        if e != f:
            same = Counter()
            for k, w in enumerate(weights):
                m = compose(compose(inv(ks[0][0]), ks[0][k]), compose(inv(ks[0][k]), ks[0][1]))
                same[m] += w
            need(all((w == 0 for w in same.values())), 'Same-stage inverse cancellation')
        cases.append({'left_exponent': e, 'right_exponent': f, 'collected_monomials': sum((w != 0 for w in grouped.values())), 'owner_coefficient_denominator': 4 * 13 ** ((e == -1) + (f == -1)), 'finite_tensor_checks': finite})
    need(expansion(chosen, 2) != expansion((chosen[0], 0), 2), 'Wrong selected sign control')
    identity = (tuple((1 << i for i in range(17))), 0)
    need(2048 not in expansion(identity, 0), 'Scalar-code substitution control')
    for e, f in product((1, -1), repeat=2):
        twice_marker = sum((scalar_weight * direct_entry(k, 0, 2048)[1] for k in range(112) if (scalar_weight := ((a[0][k] if e == 1 else (a[0][k] + 12 * (k == 0)) / 13) * (a[k][1] if f == 1 else (a[k][1] + 12 * (k == 1)) / 13)))))
        twice_zero = sum(((a[0][k] if e == 1 else (a[0][k] + 12 * (k == 0)) / 13) * (a[k][1] if f == 1 else (a[k][1] + 12 * (k == 1)) / 13) * direct_entry(k, 0, 0)[0] for k in range(112)))
        literal_width_two = -F(1, 16 * 13 ** ((e == -1) + (f == -1)))
        need(twice_marker * twice_zero / 4 != literal_width_two, 'Actual owner-tensorization mutant rejected')
    endpoints = json.loads((p / 'GAUGE.json').read_text())['typed_caller']['endpoint']
    actual = []
    for role, word in ((0, [[32, 1], [31, -1]]), (8, [[1, -1], [0, 1]])):
        row = endpoints[role]
        need(row['role'] == role and row['operator'] == 'Q^-1 B D' and (row['code_word_left_to_right'] == word), 'Actual terminal binding')
        actual.append({'role': role, 'word': word})
    return {'schema': 'two-stage-coded-terminal/1', 'status': 'PASS_TWO_STAGE_TERMINAL_SUPPORT_NO_KAPPA', 'dimension': 17, 'owner_block': [0, 1], 'marker_input': 0, 'marker_output': 2048, 'path_owner': 31, 'path_ports': [n[i]['q'] for i in (0, 31, 1)], 'selected_columns': list(chosen[0]), 'selected_input_phase_mask': chosen[1], 'unmarked_row_inputs': [0, 1, 16, 17], 'all_width_support_lower_bound': '4^(f-1), f>=1', 'fixed_word_add_lower_bound': 'g>=2(f-1)', 'actual_negative_roles': actual, 'cases': cases, 'independent_entry_checks': direct_checks, 'unsigned_phase_failures': unsigned, 'controls': ['same-stage inverse cancellation', 'unsigned K', 'wrong selected sign', 'scalar A substitution', 'owner tensorization'], 'scope': 'Two distinct fresh eight-axis stages, all four signs and inverse words; no paid-decoder, longer-product, supplier or kappa claim.'}
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_text()), 'Committed exact receipt')
    print(json.dumps({'status': result['status'], 'cases': len(result['cases']), 'actual_negative_roles': [0, 8], 'support': '4^(f-1)'}))
