#!/usr/bin/env python3
"""Exact gauge certificates, source-bound Borel controls and a sharp literal word."""
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G, C, W = (load(n) for n in ('gauge', 'check', 'word'))
need = G.need


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    need(path.stat().st_size < 2000000, 'bounded JSON file')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def sources():
    manifest = read(HERE/'SOURCES.json')
    runtime = [row for row in manifest['files'] if row['usage'] == 'input']
    for row in runtime + manifest['retained_documents']:
        raw = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
             'source Git blob')


def serialize(matrices):
    return [[[str(x) for x in row] for row in matrix] for matrix in matrices]


def graph_controls():
    """Independent min-plus closure, not the producer's predecessor algorithm."""
    counts = {'feasible': 0, 'infeasible': 0}
    for m in (2, 3):
        positions = [(i, j) for i in range(m) for j in range(m) if m == 2 or i != j]
        for values in itertools.product((None, -1, 0, 1), repeat=len(positions)):
            a = [[Q(0)]*m for _ in range(m)]
            d = [[0 if i == j else 999 for j in range(m)] for i in range(m)]
            for (i, j), v in zip(positions, values):
                if v is not None:
                    a[i][j] = Q(2)**v
                    d[j][i] = min(d[j][i], v)
            for k in range(m):
                for i in range(m):
                    for j in range(m):
                        d[i][j] = min(d[i][j], d[i][k]+d[k][j])
            possible = all(d[i][i] >= 0 for i in range(m))
            matrices = [W.shear(a)]
            certificate = G.solve(m, matrices)
            C.check(m, matrices, certificate)
            need((certificate['kind'] == 'potential') == possible, 'min-plus oracle mismatch')
            counts['feasible' if possible else 'infeasible'] += 1
    return counts


def reduced_hd(state, m=2):
    r = len(state)
    output = [[0]*(m*r) for _ in range(m*r)]
    for i in range(r):
        for j in range(r):
            for g in state[i][j]:
                for u in range(m):
                    for v in range(m):
                        x = g[u][v+m]
                        need(x.denominator % 2, 'reduced endpoint is integral')
                        output[i*m+u][j*m+v] ^= x.numerator % 2
    return output


def full_word():
    matrices, operations = W.fixture()
    need(any(Q(x).denominator % 2 == 0 for g in matrices for row in g for x in row),
         'genuinely dyadic applied matrices')
    certificate = G.solve(2, matrices)
    need(C.check(2, matrices, certificate) == 'integral-in-paired-gauge', 'accepted gauge')
    weights = certificate['weights']
    transformed = [G.conjugate(g, weights) for g in matrices]
    for k in (0, 1):
        for version in (matrices, transformed):
            a = [row[2:] for row in version[k][:2]]
            need(W.rank(a) == 1, 'paid rational rank preserved')
    for k in (2, 3, 4):
        need(all(matrices[k][i][j] == 0 for i in range(2) for j in range(2, 4)),
             'free block-lower maps')
    original, changed = W.replay(matrices, operations), W.replay(transformed, operations)
    conjugated = [[{W.mat(G.conjugate(g, weights)) for g in entry} for entry in row]
                  for row in original]
    need(conjugated == changed, 'full formal conjugation correspondence')
    h = reduced_hd(changed)
    need(W.rank(h, 2) == 4 and W.rank([row[:4] for row in h[:4]], 2) == 4,
         'two unit data targets give sharp rank four')
    need(W.rank(transformed[4], 2) == 2, 'free map singular modulo two')
    return {'m': 2, 'data_roles': 2, 'auxiliary_roles': 1,
            'matrices': serialize(matrices), 'operations': [list(x) for x in operations],
            'certificate': certificate, 'paid_rank': 4, 'data_hd_rank_mod2': 4,
            'transformed_matrices': serialize(transformed),
            'auxiliary_contract': 'unconstrained output, complete arbitrary-input map checked'}


def boundary_controls():
    # Exact named scope controls from PR2613 verify.py, retained as source data.
    half = [W.shear([[Q(1, 2)]])]
    d, di = W.mat([[2, 0], [0, 1]]), W.mat([[Q(1, 2), 0], [0, 1]])
    commutator = [d, W.shear([[1]]), di, W.shear([[-1]])]
    product = W.identity(2)
    for g in commutator:
        product = W.multiply(product, g)
    need(product == W.shear([[1]]), 'source commutator identity')
    two_cycle = [W.shear([[0, Q(1, 2)], [0, 0]]),
                 W.shear([[0, 0], [Q(1, 2), 0]])]
    output = []
    for name, m, matrices in [('source-half-frame', 1, half),
                              ('source-commutator', 1, commutator),
                              ('incompatible-offdiagonal-pair', 2, two_cycle)]:
        cert = G.solve(m, matrices)
        need(C.check(m, matrices, cert) == 'no-paired-diagonal-gauge', 'negative cycle required')
        output.append({'name': name, 'm': m, 'matrices': serialize(matrices), 'certificate': cert})
    need(all(G.solve(2, [g])['kind'] == 'potential' for g in two_cycle), 'individual gauges insufficient')
    # Dropping the paired restriction clears the half frame but destroys the unit target.
    b, bi = W.mat([[Q(1, 2), 0], [0, 1]]), W.mat([[2, 0], [0, 1]])
    need(W.multiply(W.multiply(bi, half[0]), b) == W.shear([[1]]), 'unpaired clearing')
    target = W.multiply(W.multiply(bi, W.shear([[1]])), b)
    need(target[0][1] == 2 and W.rank([[target[0][1]]], 2) == 0, 'unpaired target loses unit rank')
    # Entrywise clearing of even denominators is not similarity and can increase paid rank.
    a = W.mat([[1, Q(1, 2)], [2, 1]])
    cleared = [[x*Q(2)**max(0, -G.valuation(x)) for x in row] for row in a]
    need(W.rank(a) == 1 and W.rank(cleared) == 2, 'entrywise clearing changes paid rank')
    even = [W.shear([[2, 0], [0, 2]])]
    need(C.check(2, even, G.solve(2, even)) == 'integral-in-paired-gauge' and
         W.rank([row[2:] for row in even[0][:2]], 2) == 0, 'integrality is not target admission')
    return output


def compute():
    sources()
    return {'status': 'PASS', 'schema_version': 1, 'full_word': full_word(),
            'negative_cases': boundary_controls(), 'graph_oracle': graph_controls(),
            'limits': 'Analytic paired-diagonal gauge only; no arbitrary-lattice, saving or native-supplier claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        need(json.dumps(result, sort_keys=True) == json.dumps(read(HERE/'RESULT.json'), sort_keys=True),
             'typed result differs')
        print('PASS paired-diagonal gauges: sharp dyadic Borel word, three negative certificates, 4352 graph controls')


if __name__ == '__main__':
    main()
