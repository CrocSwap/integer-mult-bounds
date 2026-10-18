#!/usr/bin/env python3
"""Source-bound full-input witness and Clifford+T ring controls."""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
spec = importlib.util.spec_from_file_location('exact_ring', PKG / 'ring.py')
ring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ring)
need = ring.need
H = [1, 25, 3, 4, 5, 6, 8, 12]
H0 = [1, 2, 3, 4, 5, 6, 8, 12]
Z = [1, 2, 1, 1, 1, 1, 3, -2]


def read_json(path, limit=2000000):
    need(path.stat().st_size <= limit, 'bounded JSON input')
    return json.loads(path.read_text(encoding='utf-8'))


def sources():
    manifest = read_json(PKG / 'SOURCES.json')
    rows = manifest['files'] + manifest['retained_documents']
    for row in rows:
        path = ROOT / row['path']
        need(path.stat().st_size <= 4000000, 'bounded source file')
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256: ' + row['path'])
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        need(blob == row['git_blob'], 'source Git blob: ' + row['path'])
    raw = (ROOT / 'research/joint-query/certificate.json.gz').read_bytes()
    payload = gzip.decompress(raw)  # authenticated fixed source, bounded compressed size
    need(hashlib.sha256(payload).hexdigest() == manifest['packet_payload_sha256'], 'packet payload')
    packet = json.loads(payload)
    R = [[Q(row.get(str(j), '0')) for j in range(112)] for row in packet['R_rows']]
    A, T, U = (packet[k] for k in ('A_ports', 'T_ports', 'U_ports'))
    need(len(R) == 8 and len(A) == len(T) == 8 and len(U) == 96, 'packet dimensions')
    need(len(set(A + T + U)) == 112, 'port partition')
    need(all(sum(R[i][j]*R[k][j] for j in ports) == 4*int(i == k)
             for ports in (A, T) for i in range(8) for k in range(8)), 'selected sections')
    return R, A, T, U


def inverse(matrix):
    n = len(matrix)
    a = [list(row) + [Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if a[i][col]), None)
        need(pivot is not None, 'nonsingular matrix')
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [v / scale for v in a[col]]
        for i in range(n):
            if i != col:
                scale = a[i][col]
                a[i] = [x - scale*y for x, y in zip(a[i], a[col])]
    return [row[n:] for row in a]


def inverse_checks(R):
    result = {}
    for label, ports in [('original', H0), ('alternative', H)]:
        a = [[row[j] for j in ports] for row in R]
        b = inverse(a)
        for left, right in ((a, b), (b, a)):
            need(all(sum(left[i][k]*right[k][j] for k in range(8)) == int(i == j)
                     for i in range(8) for j in range(8)), 'both inverse orders')
        if label == 'original':
            need(all(ring.dyadic(v) for row in b for v in row), 'original dyadic positive control')
        else:
            need(b[0][1] == Q(1, 10), 'odd denominator boundary')
        result[label] = [[str(v) for v in row] for row in b]
    return result


def cut(R, A, T, U, z=Z):
    def query(values, ports):
        return [sum(row[j]*values[j] for j in ports) for row in R]
    def section(v, j):
        return sum(R[i][j]*v[i] for i in range(8)) / 4
    x, y = [Q(0)]*112, [Q(0)]*112
    for j, value in zip(H, z):
        x[j] = Q(value)
    q = query(x, U)
    need(q == [0, 10, 0, 0, 0, 0, 0, 0], 'exact unread witness')
    for j in A:
        x[j], y[j] = -section(q, j), section(q, j)
    f, c = query(x, range(112)), query(x, T)
    x1, y1 = x[:], y[:]
    for j in U:
        x1[j] = x[j] - section(f, j)
        y1[j] = y[j] + x1[j]
    for j in A + T:
        x1[j] = section(c if j in A else f, j)
        y1[j] = x[j] + y[j] - x1[j]
    u = y1[:]
    future = query(y1, range(112))
    for j in A:
        u[j] = section(future, j)
    a, b = query(x1, T), query(u, range(112))
    x2, y2 = x1[:], y1[:]
    for j in A:
        x2[j], y2[j] = x1[j] + y1[j] - u[j], u[j]
    for j in U:
        x2[j], y2[j] = x1[j] - y1[j], y1[j] + section(a, j)
    for j in T:
        x2[j] = section([b[k] + 12*a[k] for k in range(8)], j)
        y2[j] = u[j] - section([b[k] + 11*a[k] for k in range(8)], j)
    obs = [x1[j] for j in A + T] + [y1[j] for j in A + T]
    obs += [y2[j] for j in A] + [x2[j] for j in U] + [x1[j] for j in U if j not in H]
    need(len(obs) == 224 and all(ring.reduce(ring.scalar(v)) == (0, 0) for v in obs), 'lost modulo five')
    need(x[1] == 1, 'required original output unit')
    need([y2[j] for j in A] == [Q(5, 2), Q(-5, 2), 0, Q(5, 2), 0, 0, Q(-5, 2), 0],
         'complete retained logger witness')
    return {'input_x': list(map(str, x)), 'input_y': list(map(str, y)),
            'observation': list(map(str, obs)), 'y2_A': [str(y2[j]) for j in A],
            'required_original_x_port1': str(x[1])}


def ring_checks():
    r = ring
    need(r.mul(r.SQRT2, r.SQRT2) == r.scalar(2), 'square root relation')
    need(r.mul(r.HALFROOT, r.SQRT2) == r.ONE, 'normalization inverse')
    basis = [tuple(Q(i == j) for i in range(4)) for j in range(4)]
    need(all(r.reduce(r.mul(a, b)) == r.fmul(r.reduce(a), r.reduce(b))
             for a in basis for b in basis), 'sixteen basis products')
    need(all((a*a - 2*b*b) % 5 for a in range(5) for b in range(5) if a or b), 'F25 norm')
    need(r.reduce(r.ONE) == (1, 0) and r.reduce(r.scalar(5)) == (0, 0), 'proper ideal')
    need(r.reduce(r.I) != r.reduce(r.neg(r.I)), 'conjugation is not assumed compatible')
    need(r.fmul(r.reduce(r.ZETA), r.reduce(r.ZETA), square=3) != r.reduce(r.I), 'wrong field relation detected')
    try:
        r.reduce(r.scalar(Q(1, 5)))
    except ValueError:
        pass
    else:
        raise ValueError('odd denominator admitted')
    need(Q(1, 5) * 5 == 1, 'admitting inverse five breaks obstruction')
    return {name: list(r.reduce(value)) for name, value in
            [('zeta8', r.ZETA), ('i', r.I), ('sqrt2', r.SQRT2),
             ('inverse_sqrt2', r.HALFROOT), ('inverse_zeta8', r.neg(r.ZETA3))]}


def gate_checks(y2):
    r = ring
    gates = [('H', 0, None), ('T', 1, None), ('CNOT', 0, 2),
             ('S', 2, None), ('X', 1, None), ('Z', 0, None), ('SWAP', 0, 2)]
    for op, bit, other in gates:
        for j in range(8):
            basis = [r.ZERO]*8
            basis[j] = r.ONE
            v = r.gate(basis, op, bit, other)
            need(r.gate(v, op, bit, other, inverse=True) == basis, 'literal inverse columns')
            need(all(r.reduce(r.mul(x, r.scalar(5))) == (0, 0) for x in v), 'reduced gate coefficients')
    start = [r.scalar(Q(v)) for v in y2]
    current, prefixes = start[:], []
    for op, bit, other in gates:
        current = r.gate(current, op, bit, other)
        need(all(r.reduce(v) == (0, 0) for v in current), 'gate prefix preserves ideal')
        prefixes.append([[str(c) for c in v] for v in current])
    need(any(Q(v[1]) or Q(v[3]) for row in prefixes for v in row), 'non-Gaussian coefficients exercised')
    for op, bit, other in reversed(gates):
        current = r.gate(current, op, bit, other, inverse=True)
    need(current == start, 'whole word return')
    basis = [r.ONE] + [r.ZERO]*7
    wrong = r.gate(r.gate(basis, 'H', 0, normalizer=r.ONE), 'H', 0, normalizer=r.ONE)
    need(wrong != basis, 'omitted normalization detected')
    need(r.mul(r.ZETA, r.ZETA3) != r.ONE, 'wrong phase inverse detected')
    return {'gates': [list(g) for g in gates], 'inverse_columns': 56, 'prefixes': prefixes}


def compute():
    R, A, T, U = sources()
    witness = cut(R, A, T, U)
    changed = Z[:]
    changed[0] += 1
    try:
        cut(R, A, T, U, changed)
    except ValueError:
        pass
    else:
        raise ValueError('changed witness accepted')
    return {'schema_version': 1, 'status': 'PASS', 'ring': 'Z[zeta8,1/2]',
            'field': 'F5[t]/(t^2-2)', 'specialization': ring_checks(),
            'witness': witness, 'inverses': inverse_checks(R),
            'gate_controls': gate_checks(witness['y2_A']),
            'failure_controls': ['wrong field relation', 'odd denominator rejected',
                                 'inverse five admits unit', 'omitted H normalization',
                                 'wrong phase inverse', 'changed unread witness']}


def strict_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(strict_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(strict_equal(x, y) for x, y in zip(left, right))
    return left == right


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='emit recomputed JSON to stdout')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        need(strict_equal(result, read_json(PKG / 'RESULT.json')), 'exact typed receipt')
        print('PASS: source-bound 224 observations; F25 ring map; 56 inverse columns; six failure controls')


if __name__ == '__main__':
    main()
