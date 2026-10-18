#!/usr/bin/env python3
"""Exact finite certificates supporting the unit-phase connector theorem.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
The continuum reduction is written in README.md; this is not a proof assistant.
No predecessor implementation is imported. Python 3.10+, standard library.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools as it
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
M = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
ZERO, ONE, OMEGA = (0, 0), (1, 0), (0, 1)


def require(ok, message):
    if not ok:
        raise ValueError(message)


# Exact Q(omega), omega^2 + omega + 1 = 0. No floating-point phases.
def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def mul(x, y):
    a, b = x
    c, d = y
    return (a*c - b*d, a*d + b*c - b*d)


def conj(x):
    return (x[0] - x[1], -x[1])


def norm(x):
    a, b = x
    return a*a - a*b + b*b


def source_pins():
    src = json.loads((HERE / 'SOURCES.json').read_text())
    for row in src['files']:
        if row['usage'] == 'input':
            p = ROOT / row['path']
            require(p.is_file() and not p.is_symlink(), 'missing source: ' + str(p))
            require(hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'],
                    'source drift: ' + row['path'])
    return src


def connected_without(column=None):
    vertices = {('A', i) for i in range(3)} | {('B', j) for j in range(3) if j != column}
    reached = {('A', 0)}
    while True:
        nxt = set(reached)
        for i, j in it.product(range(3), repeat=2):
            if j != column and M[i][j] and ({('A', i), ('B', j)} & reached):
                nxt.update((('A', i), ('B', j)))
        if nxt == reached:
            return reached == vertices
        reached = nxt


def source_census(symbols, matrix=M):
    """All distinct labeled permutations; record attainable requested row sets."""
    histogram = Counter()
    digest = hashlib.sha256()
    targets = [tuple(v for a in row for v in (a, 0)) for row in matrix]
    require(len(set(symbols)) == len(symbols), 'census symbols must be distinct')
    for word in it.permutations(sorted(symbols)):
        q = [0] * 6
        vertices = [tuple(q)]
        for j, a, b in word:
            q[2*j] += a
            q[2*j+1] += b
            vertices.append(tuple(q))
        require(q == [0]*6, 'source path not restored')
        differences = {tuple(v[k]-u[k] for k in range(6))
                       for u in vertices for v in vertices}
        mask = sum(1 << i for i, row in enumerate(targets) if row in differences)
        histogram[mask] += 1
        digest.update(bytes([mask]))
    return {'paths': sum(histogram.values()),
            'row_mask_histogram': {str(k): v for k, v in sorted(histogram.items())},
            'full_covers': histogram[7], 'mask_stream_sha256': digest.hexdigest()}


def inverse(word):
    return [(kind, j, conj(c) if kind == 'Z' else neg(c)) for kind, j, c in reversed(word)]


def free_run(word, rows=7, primitive=False):
    """Free noncommutative module: (incoming row, operator word) -> coefficient."""
    state = [{(r, ()): ONE} for r in range(rows)]
    for kind, index, c in word:
        if kind == 'Z':
            state[6] = {key: mul(c, value) for key, value in state[6].items()}
            continue
        if primitive:
            src, dst = index
            op = kind
        elif kind == 'B':
            src, dst, op = index, 6, 'B' + str(index)
        else:
            require(kind == 'A', 'unknown query')
            src, dst, op = 6, 3 + index, 'A' + str(index)
        require(src != dst and 0 <= src < rows and 0 <= dst < rows, 'aliased or missing port')
        for (input_row, operators), value in list(state[src].items()):
            key = (input_row, (op,) + operators)
            updated = add(state[dst].get(key, ZERO), mul(c, value))
            if updated == ZERO:
                state[dst].pop(key, None)
            else:
                state[dst][key] = updated
    return state


def expected(matrix=M, factor_names=None, rows=7):
    state = [{(r, ()): ONE} for r in range(rows)]
    for i, j in it.product(range(3), repeat=2):
        if not matrix[i][j]:
            continue
        ops = ('A'+str(i), 'B'+str(j))
        if factor_names is not None:
            ops = tuple(reversed(factor_names['A'+str(i)])) + tuple(reversed(factor_names['B'+str(j)]))
        state[3+i][(j, ops)] = (matrix[i][j], 0)
    return state


def valid(word, matrix=M, unit=True):
    return ((not unit or all(norm(c) == 1 for _, _, c in word))
            and free_run(word) == expected(matrix))


def root_gauge(word, phase):
    """Insert unit root rotations and conjugate queries; preserve the same map."""
    require(norm(phase) == 1, 'gauge must be unit')
    result, p = [], ONE
    for kind, j, c in word:
        result.append(('Z', 0, phase))
        p = mul(phase, p)
        result.append((kind, j, mul(c, p if kind == 'B' else conj(p))))
    result.append(('Z', 0, conj(p)))
    return result


def normalized(word):
    p, result = ONE, []
    for kind, j, c in word:
        require(norm(c) == 1, 'nonunit query or rotation')
        if kind == 'Z':
            p = mul(c, p)
        else:
            result.append((kind, j, mul(c, conj(p) if kind == 'B' else p)))
    require(p == ONE, 'unrestored root phase')
    return result


def product_word(names, src, dst, depth=0):
    if len(names) == 1:
        return [(names[0], (src, dst), ONE)]
    middle = len(names) // 2
    work = 7 + depth
    left = product_word(names[:middle], src, work, depth+1)
    right = product_word(names[middle:], work, dst, depth+1)
    return left + right + inverse(left) + inverse(right)


def leaves(n):
    return 1 if n == 1 else 2*leaves(n//2) + 2*leaves(n-n//2)


def orbit_words(witnesses):
    """One exact transformation for each distinct signed/permuted target."""
    targets = {}
    for rp, cp in it.product(it.permutations(range(3)), repeat=2):
        for rs, cs in it.product(it.product((-1, 1), repeat=3), repeat=2):
            matrix = tuple(tuple(rs[i]*cs[j]*M[rp[i]][cp[j]] for j in range(3)) for i in range(3))
            if matrix not in targets:
                row_inverse = {old: new for new, old in enumerate(rp)}
                col_inverse = {old: new for new, old in enumerate(cp)}
                transformed = []
                for word in witnesses.values():
                    new = []
                    for kind, j, c in word:
                        k = (col_inverse if kind == 'B' else row_inverse)[j]
                        sign = cs[k] if kind == 'B' else rs[k]
                        new.append((kind, k, mul((sign, 0), c)))
                    transformed.append(new)
                targets[matrix] = transformed
    return targets


def evidence():
    source_pins()
    signed_source = json.loads((ROOT / 'research/signed-connector-obstruction/CERTIFICATE.json').read_text())
    weighted = json.loads((ROOT / 'research/weighted-signed-connector-seed58/CERTIFICATE.json').read_text())
    require(tuple(map(tuple, signed_source['canonical']['matrix'])) == M, 'source matrix mismatch')
    require(tuple(map(tuple, weighted['matrix'])) == M, 'weighted source matrix mismatch')
    require(all(connected_without(j) for j in (None, 0, 1, 2)), 'support graph reduction fails')
    require(M == tuple(zip(*M)), 'transpose reduction requires this symmetric representative')
    require(add(add(ONE, OMEGA), (-1, -1)) == ZERO, 'unit triangle sum')
    require(all(norm(c) == 1 for c in (ONE, OMEGA, (-1, -1))), 'unit triangle norms')

    signed = source_census([(j, s, 0) for j in range(3) for s in (-1, 1)])
    require(signed['paths'] == 720 and signed['full_covers'] == 0, 'twelve-query exclusion failed')
    all_ones = ((1,1,1),)*3
    positive = ([('A',i,(-1,0)) for i in range(3)] + [('B',j,ONE) for j in range(3)]
                + [('A',i,ONE) for i in range(3)] + [('B',j,(-1,0)) for j in range(3)])
    positive_census = source_census([(j,s,0) for j in range(3) for s in (-1,1)], all_ones)
    require(len(positive)==12 and valid(positive, all_ones) and positive_census['full_covers']>0,
            'twelve-query positive control failed')
    triangles = {}
    for j, sign in it.product(range(3), (-1, 1)):
        symbols = [(k, s, 0) for k in range(3) if k != j for s in (-1, 1)]
        symbols += [(j, sign, 0), (j, 0, sign), (j, -sign, -sign)]
        census = source_census(symbols)
        require(census['paths'] == 5040 and census['full_covers'] == 0, 'thirteen-query exclusion failed')
        triangles[str(j) + ':' + str(sign)] = census

    witnesses = {name: [(kind, j, (s, 0)) for kind, j, s in w]
                 for name, w in weighted['witnesses'].items()}
    require(set(witnesses) == {'A0','A1','A2','B0','B1','B2'}, 'six attaining profiles required')
    controls = 0
    gauges = [OMEGA, (F(3, 7), F(8, 7)), (F(-5, 7), F(3, 7))]
    gauge_checks = 0
    factor_lengths = dict(zip(('B0','B1','B2','A0','A1','A2'), (5,6,7,2,3,4)))
    factor_names = {name: [name+'f'+str(i) for i in range(n)] for name, n in factor_lengths.items()}
    leaf_counts = {}
    for name, word in witnesses.items():
        require(valid(word), 'invalid attaining word: ' + name)
        counts = Counter(kind+str(j) for kind, j, _ in word)
        require(counts == Counter({k: 4 if k == name else 2 for k in witnesses}), 'wrong cost profile')
        require(free_run(word+inverse(word)) == [{(r, ()): ONE} for r in range(7)], 'root inverse failed')
        for phase in gauges:
            gauged = root_gauge(word, phase)
            require(valid(gauged) and normalized(gauged) == word, 'root normalization failed')
            require(free_run(gauged+inverse(gauged)) == [{(r, ()): ONE} for r in range(7)], 'gauged inverse failed')
            gauge_checks += 1
        for k in range(len(word)):
            require(not valid(word[:k]+word[k+1:]), 'deleted query escaped')
            changed = word[:]
            kind, j, c = changed[k]
            changed[k] = (kind, j, neg(c))
            require(not valid(changed), 'phase sign error escaped')
            controls += 2
        lowered = []
        for kind, j, c in word:
            src, dst = (j, 6) if kind == 'B' else (6, 3+j)
            child = product_word(factor_names[kind+str(j)], src, dst)
            lowered.extend(child if c == ONE else inverse(child))
        require(free_run(lowered, rows=10, primitive=True) == expected(factor_names=factor_names, rows=10),
                'noncommutative leaf endpoint/restoration failed')
        require(free_run(lowered+inverse(lowered), rows=10, primitive=True) ==
                [{(r, ()): ONE} for r in range(10)], 'leaf inverse failed')
        leaf_counts[name] = len(lowered)
        predicted = 2*sum(leaves(n) for n in factor_lengths.values()) + 2*leaves(factor_lengths[name])
        require(len(lowered) == predicted, 'unpaid leaf')

    orbit = orbit_words(witnesses)
    require(len(orbit) == 288, 'wrong signed/permuted orbit')
    for matrix, words in orbit.items():
        for word in words:
            require(valid(word, matrix), 'orbit witness failure')
    # Exact nonunit control: fuse the predecessor's two adjacent B0- calls.
    original = [(k, j, (s, 0)) for k, j, s in signed_source['canonical']['word']]
    require(original[:2] == [('B', 0, (-1, 0))]*2, 'nonunit control source changed')
    nonunit = [('B', 0, (-2, 0))] + original[2:]
    require(len(nonunit) == 13 and valid(nonunit, unit=False) and not valid(nonunit),
            'nonunit boundary control failed')
    require(not valid(root_gauge(witnesses['A0'], OMEGA)[:-1]), 'unrestored rotation escaped')
    require(free_run([('B',0,ONE)]*3)[6].get((0,('B0',))) == (3,0), 'characteristic-three leak')
    controls += 3
    # Odd restored unit-phase words are legal; no signed-parity shortcut applies.
    odd = [('B',0,ONE), ('A',0,ONE), ('B',0,OMEGA), ('A',0,(-1,0)), ('B',0,(-1,-1))]
    odd_expected = [{(r, ()): ONE} for r in range(7)]
    odd_expected[3][(0,('A0','B0'))] = (0,-1)
    require(all(norm(c)==1 for _,_,c in odd) and free_run(odd)==odd_expected
            and free_run(odd+inverse(odd))==[{(r, ()): ONE} for r in range(7)],
            'odd unit-phase positive control failed')
    controls += 1
    return {'schema_version': 1, 'status': 'PASS_COMPLEX_UNIT_PHASE_CONNECTOR',
            'assignment_seed': 39, 'matrix': [list(r) for r in M],
            'signed_census': signed, 'unit_triangle_censuses': triangles,
            'all_ones_positive_census': positive_census,
            'unit_triangle_paths': sum(x['paths'] for x in triangles.values()),
            'minimum_complete_queries': 14, 'weighted_minimum': '2*sum(c_F)+2*min(c_F)',
            'orbit_matrices': len(orbit), 'orbit_word_checks': 6*len(orbit),
            'gauged_words': gauge_checks, 'semantic_controls': controls,
            'odd_unit_phase_positive_control': 'Five queries restore the root and add -omega*A0*B0*x0 to y0.',
            'nonunit_13_query_control': [[k,j,list(c)] for k,j,c in nonunit],
            'factor_lengths': factor_lengths, 'complete_leaf_counts': dict(sorted(leaf_counts.items())),
            'cheapest_fixture_operator': min(leaf_counts, key=leaf_counts.get),
            'scope': 'Written unit-phase reduction plus exact finite checks; no physical supplier, new kappa or proof-assistant theorem.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-certificate', action='store_true', help='print regenerated evidence without comparing the committed certificate')
    args = parser.parse_args()
    result = evidence()
    if args.emit_certificate:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(json.loads((HERE / 'CERTIFICATE.json').read_text()) == result, 'certificate drift')
        print('PASS_COMPLEX_UNIT_PHASE_CONNECTOR signed_paths=720 triangle_paths=30240 '
              'minimum_queries=14 orbit_words=1728 controls=' + str(result['semantic_controls']) + ' no_new_kappa')


if __name__ == '__main__':
    main()
