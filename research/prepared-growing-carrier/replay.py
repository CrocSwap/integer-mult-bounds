"""Check the frozen growing-carrier word with exact Gaussian arithmetic.

Read the saved recipes. Do not import the builder or call its lowering
procedure. Replay every phase basis column and every full word column.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


if not __debug__:
    raise SystemExit("Run this verifier without -O. Historical sources use assert.")
parser = argparse.ArgumentParser()
parser.add_argument("--word", type=Path, required=True)
parser.add_argument("--clifford", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
if args.output.exists():
    raise SystemExit("The output file exists.")
WORD, CLIFFORD = args.word, args.clifford
EXPECTED_WORD = '15d7b2143c360357a1f372926b1ff77378b48099118fa8b506d752daf7f33da5'
EXPECTED_CLIFFORD = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'
raw = WORD.read_bytes()
assert hashlib.sha256(raw).hexdigest() == EXPECTED_WORD
assert hashlib.sha256(CLIFFORD.read_bytes()).hexdigest() == EXPECTED_CLIFFORD
w = json.loads(raw)
spec = importlib.util.spec_from_file_location('growing_frame_definitions', CLIFFORD)
cx = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = cx
spec.loader.exec_module(cx)
H, N, COUNT = w['h'], 1 << w['h'], len(w['final_frames'])
assert (H, COUNT) == (6, 11)
assert w['source_ports'] == [1 << (2 * i) for i in range(3)]
assert w['target_ports'] == [sum(1 << (2 * i + ((t >> i) & 1)) for i in range(3)) for t in range(8)]


def span(vectors):
    points = {0}
    for v in vectors:
        assert 0 <= v < N
        points |= {x ^ v for x in points}
    return frozenset(points)


def dimension(vectors):
    return len(span(vectors)).bit_length() - 1


def invert(rows):
    a = [r | (1 << (H + i)) for i, r in enumerate(rows)]
    for j in range(H):
        i = next(i for i in range(j, H) if (a[i] >> j) & 1)
        a[i], a[j] = a[j], a[i]
        for i in range(H):
            if i != j and (a[i] >> j) & 1:
                a[i] ^= a[j]
    assert [r & (N - 1) for r in a] == [1 << i for i in range(H)]
    return tuple(r >> H for r in a)


def monomial(record):
    g = tuple(record['matrix_rows'])
    q = tuple(record['quadratic_rows'])
    alpha = tuple(record['linear_Z4'])
    assert len(g) == len(q) == len(alpha) == H
    assert dimension(g) == H and 0 <= record['offset'] < N
    assert all(((q[i] >> j) & 1) == ((q[j] >> i) & 1) for i in range(H) for j in range(H))
    assert all(alpha[i] % 2 == ((q[i] >> i) & 1) for i in range(H))
    assert 0 <= record['phase'] < 4
    return [('D', q, alpha), ('P', g), ('X', record['offset']), ('phase', record['phase'])]


def normalize(v, denominator):
    if not any(a or b for a, b in v):
        return ((0, 0),) * N, 0
    while denominator and all(a % 2 == b % 2 == 0 for a, b in v):
        v = tuple((a // 2, b // 2) for a, b in v)
        denominator -= 1
    return tuple(v), denominator


permutations, phases = {}, {}


def apply(circuit, state):
    v, denominator = state
    if not any(a or b for a, b in v):
        return state
    for e in circuit:
        tag = e[0]
        if tag == 'P':
            key = tuple(e[1])
            if key not in permutations:
                permutations[key] = [sum(((row & x).bit_count() % 2) << i for i, row in enumerate(key)) for x in range(N)]
            out = [(0, 0)] * N
            for x, y in enumerate(permutations[key]):
                out[y] = v[x]
            v = out
        elif tag == 'X':
            v = [v[x ^ e[1]] for x in range(N)]
        elif tag in ('D', 'phase'):
            if tag == 'phase':
                powers = [e[1] % 4] * N
            else:
                key = tuple(e[1]), tuple(e[2])
                if key not in phases:
                    phases[key] = [(sum(e[2][i] for i in range(H) if (x >> i) & 1)
                                    + 2 * sum((e[1][i] >> j) & 1 for i in range(H) for j in range(i + 1, H)
                                              if ((x >> i) & 1) and ((x >> j) & 1))) % 4 for x in range(N)]
                powers = phases[key]
            units = ((1, 0), (0, 1), (-1, 0), (0, -1))
            v = [(a * units[p][0] - b * units[p][1], a * units[p][1] + b * units[p][0])
                 for (a, b), p in zip(v, powers)]
        elif tag == 'C':
            q, sign = e[1:]
            out = []
            for x, (a, b) in enumerate(v):
                c, d = v[x ^ q]
                out.append((a - sign * b + c + sign * d, b + sign * a + d - sign * c))
            v = out
            denominator += 1
        else:
            raise AssertionError(e)
    return normalize(v, denominator)


def adjoint(circuit):
    out = []
    for e in reversed(circuit):
        if e[0] == 'P':
            out.append(('P', invert(tuple(e[1]))))
        elif e[0] == 'D':
            out.append(('D', tuple(e[1]), tuple((-x) % 4 for x in e[2])))
        elif e[0] == 'C':
            out.append(('C', e[1], -e[2]))
        elif e[0] == 'phase':
            out.append(('phase', (-e[1]) % 4))
        else:
            assert e[0] == 'X'
            out.append(tuple(e))
    return out


def plus(a, b, coefficient=Q(1)):
    assert coefficient.denominator & (coefficient.denominator - 1) == 0
    extra = coefficient.denominator.bit_length() - 1
    power = max(a[1], b[1] + extra)
    aa, bb = 1 << (power - a[1]), coefficient.numerator << (power - b[1] - extra)
    return normalize([(aa * x + bb * u, aa * y + bb * z) for (x, y), (u, z) in zip(a[0], b[0])], power)


zero = (((0, 0),) * N, 0)
basis = [(tuple((int(j == col), 0) for j in range(N)), 0) for col in range(N)]
initial = [(q,) for q in w['source_ports']] + [()] * 8
frames = {tuple(f) for f in initial + [tuple(f) for f in w['final_frames']]}
for e in w['events']:
    frames |= {tuple(e[2]), tuple(e[3])} if e[0] == 'child' else {tuple(e[-1])}
assert all(dimension(f) == len(f) for f in frames)
canonical = {f: cx.canonical_frame(H, f).circuit for f in frames}
recipes = {}
for item in w['recipes']:
    old, new, r = tuple(item['old']), tuple(item['new']), item['recipe']
    assert (old, new) not in recipes
    assert span(old) < span(new)
    assert r['rank'] == len(new) - len(old)
    serialized = monomial(r['right']) + [('C', 1 << i, 1) for i in range(r['rank'])] + monomial(r['left'])
    expected = adjoint(canonical[old]) + canonical[new]
    for state in basis:
        assert apply(serialized, state) == apply(expected, state), ('full recipe column', old, new)
    recipes[old, new] = serialized

labels = [('T', f) for f in initial]
rows = [{r: Q(1)} for r in range(COUNT)]
pending = [{t for t, q in enumerate(w['target_ports']) if not (q & u).bit_count() % 2} for u in w['source_ports']]
paid = Counter()
per_register = [0] * COUNT
read_caps = [[] for _ in w['source_ports']]
seen_reads, used = [], set()
for e in w['events']:
    if e[0] == 'child':
        _, r, old, new, charged = e
        old, new = tuple(old), tuple(new)
        assert labels[r] == ('T', old)
        assert span(old) < span(new) and charged == len(new) - len(old)
        assert (old, new) in recipes
        if r < 3:
            assert all(not (u & w['target_ports'][t]).bit_count() % 2 for u in new for t in pending[r])
        else:
            assert all(not (u & w['target_ports'][r - 3]).bit_count() % 2 for u in new)
        labels[r] = ('T', new)
        paid[charged] += 1
        per_register[r] += charged
        used.add((old, new))
    else:
        assert e[0] == 'add'
        _, t, s, num, den, f = e
        assert 3 <= t < COUNT and 0 <= s < 3
        assert labels[t] == labels[s] == ('T', tuple(f))
        assert t - 3 in pending[s]
        pending[s].remove(t - 3)
        seen_reads.append([s, t - 3])
        read_caps[s].append((t - 3, tuple(f)))
        for col, value in rows[s].items():
            rows[t][col] = rows[t].get(col, Q(0)) + Q(num, den) * value
assert not any(pending) and seen_reads == w['schedule']
assert used == set(recipes) and len(recipes) == 23
assert [f for _, f in labels] == [tuple(f) for f in w['final_frames']]
for r in range(COUNT):
    expected = {r: Q(1)}
    if r >= 3:
        expected.update({s: Q(1) for s in range(3) if (r - 3) >> s & 1})
    assert rows[r] == expected
for t, q in enumerate(w['target_ports']):
    assert span(w['final_frames'][3 + t]) == frozenset(x for x in range(N) if not (x & q).bit_count() % 2)
assert per_register == [5] * 11
assert sum(r * n for r, n in paid.items()) == 55


def replay(state, inverse=False):
    state = list(state)
    events = list(reversed(w['events'])) if inverse else w['events']
    for e in events:
        if e[0] == 'child':
            circuit = recipes[tuple(e[2]), tuple(e[3])]
            state[e[1]] = apply(adjoint(circuit) if inverse else circuit, state[e[1]])
        else:
            q = Q(e[3], e[4]) * (-1 if inverse else 1)
            state[e[1]] = plus(state[e[1]], state[e[2]], q)
    return state


for r in range(COUNT):
    for vector in basis:
        start = [zero] * COUNT
        start[r] = vector
        actual = replay(start)
        logical = [apply(adjoint(canonical[initial[s]]), start[s]) for s in range(COUNT)]
        wanted = []
        for output in range(COUNT):
            value = zero
            for col, q in rows[output].items():
                value = plus(value, logical[col], q)
            wanted.append(apply(canonical[tuple(w['final_frames'][output])], value))
        assert actual == wanted, ('full physical column', r)
        assert replay(actual, True) == start, ('inverse physical column', r)

source_bridges = []
for q in w['source_ports']:
    assert all(apply(canonical[(q,)], v) == apply([('C', q, 1)], v) for v in basis)
    source_bridges.append(True)
target_bridges = []
for t, q in enumerate(w['target_ports']):
    cap = tuple(w['final_frames'][3 + t])
    goal = cx.cgate(H, q).adjoint().then(cx.fourier(H))
    endpoint = cx.canonical_frame(H, cap)
    correction = endpoint.adjoint().then(goal)
    rank = cx.rank([x for x, z, p in correction.tab[H:]])
    equal = all(apply(canonical[cap], v) == apply(goal.circuit, v) for v in basis)
    assert not equal and rank == 0
    target_bridges.append({'q': q, 'canonical_equals_legacy_endpoint': equal, 'exit_correction_rank': rank})

last_read_cap = [caps[-1][1] for caps in read_caps]
invalid_fixed_caps = []
for source, caps in enumerate(read_caps):
    for t, cap in caps:
        if any((u & w['target_ports'][t]).bit_count() % 2 for u in last_read_cap[source]):
            invalid_fixed_caps.append({'source': source, 'target': t, 'q': w['target_ports'][t],
                                       'read_cap': cap, 'last_read_cap': last_read_cap[source]})
assert invalid_fixed_caps
charges = [sum(Q(1 << len(cap), 8) for t, cap in caps) for caps in read_caps]
assert charges == [Q(3, 2), Q(2), Q(2)]
first = w['recipes'][0]
mutant = list(recipes[tuple(first['old']), tuple(first['new'])]) + [('phase', 1)]
assert apply(mutant, basis[0]) != apply(recipes[tuple(first['old']), tuple(first['new'])], basis[0])

result = {
    'status': 'PASS_INDEPENDENT_GROWING_CAP_WORD',
    'word_sha256': EXPECTED_WORD, 'clifford_source_sha256': EXPECTED_CLIFFORD,
    'builder_imported': False, 'lower_child_called': False,
    'canonical_frame_definitions_shared': True,
    'separate_integer_gaussian_interpreter': True,
    'scalar_input_columns': COUNT,
    'recipe_basis_columns': len(recipes) * N,
    'whole_physical_basis_columns': COUNT * N,
    'inverse_round_trip_columns': COUNT * N,
    'all_moves_strict_nested_ascents': True,
    'full_common_labels_at_adds': True,
    'future_targets_compatible_before_each_source_move': True,
    'sources_unchanged_in_scalar_replay': True,
    'target_rows_exact': True,
    'literal_events': len(w['events']), 'scalar_add_reads': len(seen_reads),
    'paid_child_calls': sum(paid.values()), 'distinct_recipe_lowerings': len(recipes),
    'paid_profile': dict(sorted(paid.items())), 'paid_rank_mass': 55,
    'paid_rank_by_register': per_register, 'copies': 0,
    'source_line_bridge_equals_C_e': source_bridges,
    'target_endpoint_bridges': target_bridges,
    'target_exit_adapters_in_frozen_word': False,
    'fixed_last_cap_counterexamples': invalid_fixed_caps,
    'three_selector_analogue_charges_per_carrier': list(map(str, charges)),
    'phase_mutant_rejected': True,
    'scope': 'One finite canonical-frame decoder. No complete scalar factory, legacy exit adapter word, global owner controller, supplier or kappa gain is checked.',
}
result['checker_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
args.output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
