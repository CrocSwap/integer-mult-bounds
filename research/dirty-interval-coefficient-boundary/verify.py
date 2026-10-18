#!/usr/bin/env python3
"""Exact ideal interval audit; Arham Tahir + Codex, Apache-2.0.
Free words retain repeated indices and integer coefficients. No numerical leaves.
"""
import argparse
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import oracle


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bindings():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    expected = {'research/dirty-cubic-precision/vendor/628/dirty.py',
                'research/dirty-cubic-precision/PROOF.md'}
    require({row['path'] for row in sources['files'] if row['usage'] == 'input'} == expected,
            'source inventory mismatch')
    require({row['package_path'] for row in sources['pending_predecessor_files']} ==
            {'vendor/PR1085-PROOF.md', 'vendor/PR1278-PROOF.md'}, 'predecessor inventory mismatch')
    for row in sources['files']:
        if row['usage'] != 'input':
            continue  # Historical provenance: research_package.py checks Git.
        raw = (ROOT/row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source drift: '+row['path'])
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob == row['git_blob'], 'source Git blob drift')
    for row in sources['pending_predecessor_files']:
        raw = (HERE/row['package_path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'predecessor drift')
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob == row['git_blob'], 'predecessor Git blob drift')
    return ROOT/'research/dirty-cubic-precision/vendor/628/dirty.py'


def reverse(word):
    return tuple((x, y, j, -s) for x, y, j, s in reversed(word))


@lru_cache(None)
def emit(n, x=0, y=1, level=0, lo=0):
    require(n >= 1, 'positive factor count')
    if n == 1:
        return ((x, y, lo, 1),)
    m = n//2
    u = emit(m, x, level+2, level+1, lo)
    v = emit(n-m, level+2, y, level+1, lo+m)
    return u+v+reverse(u)+reverse(v)


def scalar_interval(word, factors, a, b, dimension):
    matrix = oracle.eye(dimension)
    operations = word[a:b] if a <= b else reverse(word[b:a])
    for x, y, j, sign in operations:
        matrix[y] = [v+sign*factors[j]*u for v, u in zip(matrix[y], matrix[x])]
    return matrix


def free_eye(d):
    return [[{(): 1} if i == j else {} for j in range(d)] for i in range(d)]


def free_step(matrix, instruction):
    x, y, j, sign = instruction
    require(x != y, 'distinct leaf registers')
    for col, p in enumerate(matrix[x]):
        q = matrix[y][col]
        for monomial, coefficient in p.items():
            key = (j,)+monomial  # No squarefree or commuting quotient.
            value = q.get(key, 0)+sign*coefficient
            if value:
                q[key] = value
            else:
                q.pop(key, None)
    return sum(abs(c) for p in matrix[y] for c in p.values())


def alignment(row, n):
    """Solve factor/input signs with exact F2 elimination."""
    pivots = {}
    for col, p in enumerate(row):
        for monomial, coefficient in p.items():
            mask = 1 << (n+col)
            for j in monomial:
                mask ^= 1 << j
            rhs = int(coefficient < 0)
            while mask:
                j = mask.bit_length()-1
                if j not in pivots:
                    pivots[j] = mask, rhs
                    break
                left, right = pivots[j]
                mask ^= left; rhs ^= right
            if not mask and rhs:
                return None
    solution = 0
    for j, (mask, rhs) in sorted(pivots.items()):
        if (mask & solution).bit_count()%2 != rhs:
            solution ^= 1 << j
    return tuple(-1 if solution >> j & 1 else 1 for j in range(n))


def census(n, source):
    d = (n-1).bit_length()+2
    maximum, witness, count = 1, None, 0
    for sign in (1, -1):
        word = emit(n) if sign == 1 else reverse(emit(n))
        require(word == tuple(oracle.source_events(source, n, sign)), 'literal source dispatcher mismatch')
        for a in range(len(word)):
            matrix = free_eye(d)
            for b in range(a, len(word)):
                mass = free_step(matrix, word[b])
                for p in matrix[word[b][1]]:
                    for monomial in p:
                        require(len(monomial) == len(set(monomial)), 'repeated factor survived')
                if mass > maximum:
                    maximum, witness = mass, None
                if mass == maximum and witness is None:
                    row = matrix[word[b][1]]
                    if alignment(row, n) is not None:
                        witness = sign, a, b+1, word[b][1], deepcopy(row)
                count += 1
    require(witness is not None, 'no scalar maximum witness at n='+str(n))
    sign, a, b, row_index, row = witness
    factors = alignment(row, n)
    word = emit(n) if sign == 1 else reverse(emit(n))
    actual = scalar_interval(word, factors, a, b, d)
    independent = oracle.two_cut(n, factors, a, b, sign)
    require(actual == independent, 'independent dense maximum witness mismatch')
    require(sum(abs(v) for v in actual[row_index]) == maximum, 'maximum not attained by scalar isometries')
    return dict(n=n, intervals=count, maximum=maximum, sign=sign, cuts=[a, b],
                row_index=row_index, factors=list(factors), row=list(actual[row_index]))


def family_data(h):
    n = 1 << h
    negative = {n-(1 << k)-1 for k in range(h-1)}
    factors = tuple(-1 if j in negative else 1 for j in range(n))
    a, b = 3*(4**(h-1))//5, (4**h+2)//3
    row = [(-1)**(h-1)*(1+h//2), 1]
    row.extend(j*(-1)**(h+j) for j in range(1, h+1))
    return n, factors, a, b, row


def family_checks(source):
    rows, leaves = [], 0
    for h in range(1, 9):
        n, factors, a, b, expected = family_data(h)
        word = emit(n)
        require(len(word) == 4**h, 'power-of-two word length')
        require(word == tuple(oracle.source_events(source, n, 1)), 'family source dispatcher mismatch')
        actual = scalar_interval(word, factors, a, b, h+2)
        independent = oracle.two_cut(n, factors, a, b)
        require(actual == independent, 'recursive dense interval mismatch')
        require(actual[1] == expected, 'family row formula mismatch')
        norm = h*h//2+h+2
        require(sum(map(abs, expected)) == norm, 'family norm formula')
        require(max(sum(map(abs, row)) for row in actual) == norm, 'family matrix norm')
        vector = [1 if v >= 0 else -1 for v in expected]
        require(sum(v*x for v, x in zip(expected, vector)) == norm, 'attaining dirt')
        vector[0] = 0
        require(sum(v*x for v, x in zip(expected, vector)) == 1+h*(h+1)//2,
                'fixed-source perturbation bound')
        negative_word = reverse(word)
        mirrored = scalar_interval(negative_word, factors, len(word)-a, len(word)-b, h+2)
        require(mirrored == actual, 'negative ordered-cut reflection')
        endpoint = scalar_interval(word, factors, 0, len(word), h+2)
        target = oracle.eye(h+2); target[1][0] = (-1)**(h-1)
        require(endpoint == target, 'full arbitrary-dirty restoration')
        prefix, inverse = oracle.eye(h+2), oracle.eye(h+2)
        peak = 1
        for x, y, j, sign in word:
            coefficient = sign*factors[j]
            prefix[y] = [v+coefficient*u for v, u in zip(prefix[y], prefix[x])]
            for row in inverse:
                row[x] -= coefficient*row[y]
            peak = max(peak, sum(map(abs, prefix[y])), *(sum(map(abs, r)) for r in inverse))
        require(peak <= h+2, 'retained prefix bound')
        leaves += len(word)
        rows.append(dict(h=h, n=n, cuts=[a, b], row=expected, norm=norm,
                         prefix_peak=peak, fixed_source_norm=1+h*(h+1)//2,
                         complete_leaves=len(word)))
    large = []
    for h in range(9, 21):
        n, factors, a, b, expected = family_data(h)
        matrix = oracle.two_cut(n, factors, a, b)
        require(matrix[1] == expected, 'large recursive family row')
        large.append(dict(h=h, n=n, row=expected, norm=sum(map(abs, expected))))
    return rows, large, leaves


def failure_controls(source):
    n, factors, a, b, expected = family_data(2); word = emit(n)
    def reject(name, fn, reason):
        try:
            fn()
        except ValueError as error:
            require(reason in str(error), 'wrong control rejection: '+name)
            return name
        raise ValueError('control accepted: '+name)
    controls = []
    controls.append(reject('prefix_bound_used_for_interval',
        lambda: require(sum(map(abs, expected)) <= 4, 'interval exceeds prefix coefficient'), 'prefix coefficient'))
    controls.append(reject('wrong_cut',
        lambda: require(scalar_interval(word, factors, a, b-1, 4)[1] == expected, 'wrong cut row'), 'wrong cut'))
    controls.append(reject('identity_factors_substituted',
        lambda: require(scalar_interval(word, (1,)*n, a, b, 4)[1] == expected, 'factor mutation'), 'factor mutation'))
    controls.append(reject('matrix_multiplication_order',
        lambda: require(oracle.wrong_order(n, factors, a, b)[1] == expected, 'matrix order'), 'matrix order'))
    endpoint = oracle.eye(4); endpoint[1][0] = -1
    controls.append(reject('one_restoration_leaf_omitted',
        lambda: require(scalar_interval(word[:-1], factors, 0, len(word)-1, 4) == endpoint,
                        'dirty restoration'), 'dirty restoration'))
    controls.append(reject('scratch_alias',
        lambda: oracle.source_events(source, 4, 1, alias=True), 'ancestor arrays distinct'))
    matrix = scalar_interval(emit(1), (2,), 0, 1, 2)
    require(sum(map(abs, matrix[1])) == 3 > 2, 'noncontractive boundary control')
    controls.append('noncontractive_factor_exceeds_finite_envelope')
    return controls


def compute():
    source = bindings()
    exhaustive = [census(n, source) for n in range(1, 17)]
    require([r['maximum'] for r in exhaustive] == [2, 3, 4, 6, 7, 8, 8, 9, 10, 10, 10, 12, 12, 12, 12, 14],
            'finite contraction envelope')
    family, large, leaves = family_checks(source)
    return dict(status='PASS_DIRTY_INTERVAL_COEFFICIENT_BOUNDARY',
                scope='Ideal complete-leaf intervals only; no rounded failure, supplier or kappa claim',
                exhaustive=exhaustive, intervals=sum(r['intervals'] for r in exhaustive),
                family=family, recursive_large=large, literal_family_leaves=leaves,
                controls=failure_controls(source))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='authoring only: write a new external receipt')
    parser.add_argument('--bindings-only', action='store_true', help='source integrity only; no mathematics')
    args = parser.parse_args()
    require(not (args.write and args.bindings_only), 'choose one verification mode')
    if args.bindings_only:
        bindings()
        print('PASS_INTERVAL_SOURCE_BINDINGS_ONLY')
        return
    result = compute()
    if args.write:
        with args.write.open('x') as stream:
            json.dump(result, stream, indent=2); stream.write('\n')
    else:
        require(result == json.loads((HERE/'CERTIFICATE.json').read_text()), 'certificate mismatch')
    print(result['status'], 'intervals='+str(result['intervals']),
          'literal_leaves='+str(result['literal_family_leaves']), 'controls='+str(len(result['controls'])))


if __name__ == '__main__':
    main()
