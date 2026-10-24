#!/usr/bin/env python3
"""Exact Q(omega) linearization of four qutrit mutually unbiased bases."""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path

ZERO = (F(0), F(0))
ONE = (F(1), F(0))
S = (F(1), F(2))  # omega - conjugate(omega) = i sqrt(3)
ROOTS = (ONE, (F(0), F(1)), (F(-1), F(-1)))
WEIGHTS = (3, 3, 3, 2, 6, 2, 6, 2, 6)*4
MINOR_ROWS = (0, 1, 3, 4, 9, 10, 12, 13, 18, 19, 21, 22, 27, 28, 36, 37)


def need(condition, message):
    if not condition:
        raise ValueError(message)


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


def real(x):
    return x[0] - x[1]/2


def matrix():
    return [[ZERO for _ in range(3)] for _ in range(3)]


def dagger(a):
    return [[conj(a[j][i]) for j in range(3)] for i in range(3)]


def product(a, b):
    out = matrix()
    for i, j in itertools.product(range(3), repeat=2):
        for k in range(3):
            out[i][j] = add(out[i][j], mul(a[i][k], b[k][j]))
    return out


def bases():
    identity = matrix()
    for i in range(3):
        identity[i][i] = ONE
    return [identity] + [
        [[ROOTS[(a*x*x + b*x) % 3] for b in range(3)] for x in range(3)]
        for a in range(3)]


def skew_basis():
    out = []
    for i in range(3):
        a = matrix()
        a[i][i] = S
        out.append(a)
    for i, j in itertools.combinations(range(3), 2):
        a, b = matrix(), matrix()
        a[i][j], a[j][i] = ONE, neg(ONE)
        b[i][j] = b[j][i] = S
        out.extend([a, b])
    return out


def rref(rows):
    need(0 < len(rows) <= 60, "row capacity")
    width = len(rows[0])
    need(0 < width <= 60 and all(len(r) == width for r in rows), "column capacity")
    a = [[F(x) for x in row] for row in rows]
    pivots = []
    for col in range(width):
        candidates = [i for i in range(len(pivots), len(a)) if a[i][col]]
        if not candidates:
            continue
        row = len(pivots)
        pivot = candidates[0]
        a[row], a[pivot] = a[pivot], a[row]
        value = a[row][col]
        a[row] = [x/value for x in a[row]]
        for i in range(len(a)):
            if i != row:
                value = a[i][col]
                a[i] = [x-value*y for x, y in zip(a[i], a[row])]
        pivots.append(col)
    return a, pivots


def coordinates(a):
    out = [a[i][i][1]/2 for i in range(3)]
    for i, j in itertools.combinations(range(3), 2):
        out.extend([real(a[i][j]), a[i][j][1]/2])
    reconstructed = matrix()
    for c, basis in zip(out, skew_basis()):
        for i, j in itertools.product(range(3), repeat=2):
            reconstructed[i][j] = add(reconstructed[i][j], (c*basis[i][j][0], c*basis[i][j][1]))
    need(a == reconstructed, "matrix outside real skew-Hermitian span")
    return out


def linearization():
    aa, hh, norms = bases(), skew_basis(), (1, 3, 3, 3)
    rows = []
    for a, b in itertools.combinations(range(4), 2):
        overlap = product(dagger(aa[a]), aa[b])
        for i, j in itertools.product(range(3), repeat=2):
            need(real(mul(conj(overlap[i][j]), overlap[i][j])) == F(norms[a]*norms[b], 3), "MUB fixture")
            row = [F(0)]*36
            for k, h in enumerate(hh):
                derivative = product(product(dagger(aa[a]), h), aa[b])[i][j]
                value = 2*real(mul(conj(overlap[i][j]), derivative))/(norms[a]*norms[b])
                row[9*a+k], row[9*b+k] = -value, value
            rows.append(row)
    return rows


def gauge_vectors():
    aa, norms = bases(), (1, 3, 3, 3)
    vectors = []
    for k in range(9):
        vectors.append([F(int(j % 9 == k)) for j in range(36)])
    for a in range(4):
        for k in range(3):
            phase = matrix()
            phase[k][k] = S
            h = product(product(aa[a], phase), dagger(aa[a]))
            h = [[(x[0]/norms[a], x[1]/norms[a]) for x in row] for row in h]
            vector = [F(0)]*36
            vector[9*a:9*a+9] = coordinates(h)
            vectors.append(vector)
    return vectors


def determinant(rows):
    need(len(rows) == 16 and all(len(row) == 16 for row in rows), "minor capacity")
    a = [row[:] for row in rows]
    result = F(1)
    for k in range(16):
        candidates = [i for i in range(k, 16) if a[i][k]]
        if not candidates:
            return F(0)
        pivot = candidates[0]
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            result = -result
        value = a[k][k]
        result *= value
        for i in range(k+1, 16):
            scale = a[i][k]/value
            for j in range(k+1, 16):
                a[i][j] -= scale*a[k][j]
    return result


def gram_check(rows):
    gram = [[sum(row[i]*row[j] for row in rows) for j in range(36)] for i in range(36)]
    for i, j in itertools.product(range(36), repeat=2):
        square = sum(gram[i][k]*gram[k][j]/WEIGHTS[k] for k in range(36))
        need(square == 3*gram[i][j], "normal singular-value identity")
    need(sum(gram[i][i]/WEIGHTS[i] for i in range(36)) == 48, "normal rank trace")


def analyze(rows, gauges):
    reduced, pivots = rref(rows)
    _, gauge_pivots = rref(gauges)
    need(len(pivots) == 16, "Jacobian rank is not sixteen")
    need(len(gauge_pivots) == 20, "gauge rank is not twenty")
    need(all(sum(x*y for x, y in zip(row, g)) == 0 for row in rows for g in gauges), "gauge not in kernel")
    minor = determinant([[rows[i][j] for j in pivots] for i in MINOR_ROWS])
    need(minor == F(-64, 2187), "rank witness determinant")
    gram_check(rows)
    return {"jacobian_rows": 54, "tangent_dimension": 36,
            "jacobian_rank": len(pivots), "gauge_rank": len(gauge_pivots),
            "normal_squared_singular_value": 3,
            "minor_rows": list(MINOR_ROWS), "minor_columns": pivots,
            "minor_determinant": str(minor),
            "rref_sha256": hashlib.sha256(json.dumps([[str(x) for x in row] for row in reduced]).encode()).hexdigest()}


def compute():
    result = analyze(linearization(), gauge_vectors())
    for n, a in enumerate(bases()):
        norm = 1 if n == 0 else 3
        need(product(dagger(a), a) == [[(F(norm*int(i == j)), F(0)) for j in range(3)] for i in range(3)], "unitarity")
    return result


def right_coordinate_check():
    # Independent overlap differential -K_a M + M K_b, transported to left coordinates.
    aa, hh, norms = bases(), skew_basis(), (1, 3, 3, 3)
    rows = linearization()
    checked = 0
    for a, b in itertools.combinations(range(4), 2):
        overlap = product(dagger(aa[a]), aa[b])
        offset = list(itertools.combinations(range(4), 2)).index((a, b))*9
        for role, sign in ((a, -1), (b, 1)):
            for h in hh:
                transported = product(product(aa[role], h), dagger(aa[role]))
                transported = [[(x[0]/norms[role], x[1]/norms[role]) for x in row] for row in transported]
                vector = coordinates(transported)
                derivative = product(h, overlap) if role == a else product(overlap, h)
                for i, j in itertools.product(range(3), repeat=2):
                    direct = sign*2*real(mul(conj(overlap[i][j]), derivative[i][j]))/(norms[a]*norms[b])
                    left = sum(rows[offset+3*i+j][9*role+k]*vector[k] for k in range(9))
                    need(left == direct, "left/right coordinate differential disagreement")
                    checked += 1
    need(checked == 972, "differential coverage")
    return checked


def source_check():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    sources = json.loads((package/'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((root/row['path']).read_bytes()).hexdigest() == row['sha256'], "source pin mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    source_check()
    result = compute()
    result['right_coordinate_checks'] = right_coordinate_check()
    package = Path(__file__).resolve().parent
    result['file_sha256'] = {name: hashlib.sha256((package/name).read_bytes()).hexdigest()
                             for name in ('verify.py', 'PROOF.md')}
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
        need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True), "receipt mismatch")
        print('PASS_QUTRIT_MUB_STABILITY rank=16 kernel=gauge=20 normal_squared_singular_value=3 exponent=1/2 differential_checks=972')


if __name__ == '__main__':
    main()
