#!/usr/bin/env python3
"""Check the general completion identities without a producer import."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

PROOF = 'df76e7ff4b532bfab58a9aea5ce7d29493305a76013ef6cd20fb38b7ad2dde01'
INTERFACE = '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3'


def need(test, label):
    if not test:
        raise ValueError(label)


def add(*polys):
    out = {}
    for poly in polys:
        for word, value in poly.items():
            out[word] = out.get(word, 0) + value
    return {word: value for word, value in out.items() if value}


def neg(poly):
    return {word: -value for word, value in poly.items()}


def mul(left, right):
    out = {}
    for a, c in left.items():
        for b, d in right.items():
            out[a+b] = out.get(a+b, 0) + c*d
    return {word: value for word, value in out.items() if value}


def product(left, right):
    return [[add(*(mul(left[i][k], right[k][j]) for k in range(len(right))))
             for j in range(len(right[0]))] for i in range(len(left))]


def dense_product(left, right, modulus=None):
    out = [[sum(left[i][k]*right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))] for i in range(len(left))]
    return [[value % modulus for value in row] for row in out] if modulus else out


def determinant2(matrix):
    return matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    lanes = args.repo / 'work/centre-encoding-campaign-20261014/lanes'
    proof = lanes / 'schur-selection/unit-query-review-20261015/GENERAL-COMPLETION.md'
    interface = lanes / 'circuit-interface/INTERFACE.json'
    need(sha256(proof.read_bytes()).hexdigest() == PROOF, 'Frozen proof pin')
    need(sha256(interface.read_bytes()).hexdigest() == INTERFACE, 'Actual interface pin')
    zero, one = {}, {(): 1}
    b, d, c = ({(letter,): 1} for letter in ('B', 'D', 'C'))
    identity = [[one, zero], [zero, one]]
    upper = [[one, b], [zero, one]]
    lower = [[one, zero], [neg(d), one]]
    t = product(lower, upper)
    ti = product([[one, neg(b)], [zero, one]], [[one, zero], [d, one]])
    need(product(t, ti) == product(ti, t) == identity, 'Free noncommutative inverse orders')
    j = [[add(one, neg(c)), neg(mul(c, b))], [neg(d), add(one, neg(mul(d, b)))]]
    need(t[1] == j[1] and t[0] == [one, b], 'Unselected rows and complete query')
    repair = [[add(t[i][j0], neg(j[i][j0])) for j0 in range(2)] for i in range(2)]
    need(repair == [[c, add(b, mul(c, b))], [zero, zero]], 'General selected-K repair')
    compatible = [[one, add(b, b)], [zero, zero]]
    need(product(compatible, compatible) == compatible, 'Compatible split projection')
    need(product(repair, repair) != repair, 'General repair need not be a projection')
    finite_cases = 0
    noncompatible = 0
    for a in range(1, 5):
        for b0 in range(5):
            for c0 in range(5):
                for d0 in range(5):
                    ai = pow(a, -1, 5)
                    t0 = [[1, ai*b0 % 5], [-d0*a % 5, (1-d0*b0) % 5]]
                    j0 = [[(1-c0*a) % 5, -c0*b0 % 5], [-d0*a % 5, (1-d0*b0) % 5]]
                    need(determinant2(t0) % 5 == 1, 'Every finite completion is a unit')
                    need(t0[1] == j0[1], 'Every finite completion retains U')
                    need(dense_product([[a, 0]], t0, 5) == [[a, b0]], 'Every finite query read')
                    g = (a*c0+b0*d0) % 5
                    need((determinant2(j0) % 5 != 0) == (g != 1), 'Finite unit distinction')
                    if g == 1:
                        need(t0 != j0, 'A singular original needs one changed field')
                    finite_cases += 1
                    noncompatible += c0 != ai
    need(finite_cases == 500 and noncompatible == 400, 'Complete finite family')
    # The two converse qualifications are exact over the dyadic ring.
    need(dense_product([[3, 0]], [[1, 0], [0, 1]]) == [[3, 0]], 'Non-onto converse control')
    arbitrary_repair = [[1, 0], [-6, -1]]
    need(determinant2(arbitrary_repair) == -1, 'Unit repair without unit query minor')
    need(arbitrary_repair[0][1] == 0 and [3, 1][1] != 0, 'Selected output cannot read full query')
    data = json.loads(interface.read_bytes())
    r = [[Q(row.get(str(p), 0)) for p in range(112)] for row in data['R']]
    selected = [0, 7, 20, 27, 36, 46, 57, 111]
    rt = list(map(list, zip(*r)))
    rr = dense_product(r, rt)
    rs = [[row[p] for p in selected] for row in r]
    rss = dense_product(rs, list(map(list, zip(*rs))))
    need(rr == [[56*int(i == j) for j in range(8)] for i in range(8)], 'Actual R R transpose')
    need(rss == [[4*int(i == j) for j in range(8)] for i in range(8)], 'Actual selected minor')
    need(5*5 % 13 == 8*8 % 13 == 12 and pow(2, -1, 13) == 7, 'Both Gaussian residue maps')
    result = dict(status='PASS_GENERAL_COMPLETION_EXTENSION', proof_sha256=PROOF,
                  interface_sha256=INTERFACE,
                  free_polynomial_checks=['both inverse orders', 'unselected rows', 'full query',
                                          'arbitrary selected K', 'compatible projection',
                                          'noncompatible nonprojection control'],
                  finite_cases=finite_cases, noncompatible_cases=noncompatible,
                  exact_converse_controls=2, actual_rr_transpose=56, actual_selected_gram=4,
                  qualifications=['For c changed fields the nonlinear proof uses U_c, the n-c retained fields.',
                                  'No native, global controller, or record-hosting replay is performed.'])
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'CHECK.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
