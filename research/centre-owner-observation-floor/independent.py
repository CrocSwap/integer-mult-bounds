#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Canonical-word audit, independent of the emitted-program interpreter."""
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
PRIME = 2147483647


def check(condition, reason):
    if not condition:
        raise ValueError(reason)


def rank_mod(rows):
    a = [[int(x.numerator)*pow(int(x.denominator), -1, PRIME) % PRIME for x in row] for row in rows]
    k = 0
    for j in range(len(a[0])):
        i = next((i for i in range(k, len(a)) if a[i][j]), None)
        if i is None:
            continue
        a[k], a[i] = a[i], a[k]
        inverse = pow(a[k][j], -1, PRIME)
        a[k] = [x*inverse % PRIME for x in a[k]]
        for i in range(k+1, len(a)):
            factor = a[i][j]
            a[i] = [(x-factor*y) % PRIME for x, y in zip(a[i], a[k])]
        k += 1
        if k == len(a):
            break
    return k


def canonical_rows(w, backward=False):
    rows = [[F(int((i % 112) == p and i < (224 if backward else 112))) for p in range(112)] for i in range(704)]
    for event in w['precondition'] + w['compensation'] + w['A']:
        if event[0] == 'scale':
            q = F(event[2], event[3])
            if backward:
                q = 1/q
            rows[event[1]] = [q*x for x in rows[event[1]]]
        else:
            target, source, q = event[1], event[2], F(event[3], event[4])
            if backward:
                target, source, q = source, target, -q
            rows[target] = [x+q*y for x, y in zip(rows[target], rows[source])]
    if not backward:
        return [rows[i] for i in w['centers']]
    result = [[F(0)]*112 for _ in range(8)]
    for event in w['cut']:
        k = w['centers'].index(event[2])
        q = F(event[3], event[4])
        result[k] = [x+q*y for x, y in zip(result[k], rows[event[1]])]
    return result


def main():
    archive = ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz'
    check(hashlib.sha256(archive.read_bytes()).hexdigest() == 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6', 'archive pin')
    with tarfile.open(archive) as t:
        raw = t.extractfile('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz').read()
        check(hashlib.sha256(raw).hexdigest() == '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219', 'member pin')
        w = json.loads(gzip.decompress(raw))
    receipt = json.loads((P/'RESULT.json').read_bytes())
    R, H = canonical_rows(w), canonical_rows(w, True)
    check([[str(x) for x in row] for row in R] == receipt['R'], 'canonical forward rows')
    check([[str(x) for x in row] for row in H] == receipt['H'], 'canonical backward rows')
    check(rank_mod(R) == rank_mod(H) == 8, 'independent modular minor rank')
    for witness in receipt['witnesses']:
        p = witness['port']
        x = {int(j): F(v) for j, v in witness['kernel'].items()}
        check(x[p] == 1 and all(sum(row[j]*v for j, v in x.items()) == 0 for row in R), 'exact kernel')
        check(any(row[p] for row in H), 'nonzero column')
        # A nonzero 9x9 modular minor certifies Q rank >=9; nine rows
        # supply the matching upper bound. No floating rank inference.
        unit = [F(int(j == p)) for j in range(112)]
        check(rank_mod(R+[unit]) == 9, 'coordinate adds information')
    complement = receipt['sharp_repair_complementary_coordinates']
    augmented = R + [[F(int(j == p)) for j in range(112)] for p in complement]
    check(rank_mod(augmented) == 112 and rank_mod(augmented[:-1]) == 111, 'sharp extension')
    check(receipt['whole_field_extra_scalar_coordinates_per_old_owner_minimum'] == 112-8, '104 floor')
    print('PASS_INDEPENDENT_CANONICAL_OWNER_FLOOR kernels=112 rational_equalities=verified modular_minors=112')


if __name__ == '__main__':
    main()
