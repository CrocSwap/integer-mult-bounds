#!/usr/bin/env python3
"""Exact corroboration; the all-arity proof is PROOF.md.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported. Checks remain active under -O.
"""
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
from math import isqrt
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = 'e54523517d0f03e58352e647c403a5af3e525a57'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rejected(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('negative control accepted')


def source_bytes(raw, row):
    require(sha256(raw).hexdigest() == row['sha256'], 'source SHA256 mismatch')
    obj = b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw
    require(sha1(obj).hexdigest() == row['git_blob'], 'source Git blob mismatch')


def check_sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    require(manifest['base_commit'] == BASE, 'wrong source base')
    rows = [row for row in manifest['files'] if row['usage'] == 'input']
    expected = {
        'research/cubic-three-query-arities/README.md',
        'research/dyadic-cubic-repair/PROOF.md',
        'research/cubic-pure-b-boundary/PROOF.md',
        'research/cubic-equal-step-classification/PROOF.md',
    }
    require({row['path'] for row in rows} == expected and len(rows) == 4,
            'wrong predecessor input set')
    for row in rows:
        raw = (ROOT / row['path']).read_bytes()
        source_bytes(raw, row)
        rejected(lambda: source_bytes(raw + b'\nMUTATED', row))
    return len(rows)


# Sparse Q-polynomials in indeterminates (r,n), used only for four cubic
# coefficients. This checks the universal residual without sampling r,n.
def add(*polynomials):
    out = {}
    for poly in polynomials:
        for monomial, coefficient in poly.items():
            out[monomial] = out.get(monomial, Q(0)) + coefficient
    return {m: c for m, c in out.items() if c}


def scale(poly, coefficient):
    return {m: c * coefficient for m, c in poly.items() if c * coefficient}


def mul(left, right):
    out = {}
    for (i, j), a in left.items():
        for (k, l), b in right.items():
            m = (i + k, j + l)
            out[m] = out.get(m, Q(0)) + a * b
    return {m: c for m, c in out.items() if c}


def symbolic_residual():
    one, r, n = {(0, 0): Q(1)}, {(1, 0): Q(1)}, {(0, 1): Q(1)}
    rm1 = add(r, scale(one, -1))
    d = scale(add(rm1, scale(n, -1)), Q(1, 2))
    e = scale(add(rm1, n), Q(1, 2))
    s1 = scale(mul(r, rm1), Q(1, 2))
    target = [{}, scale(s1, 3),
              mul(s1, add(scale(r, 2), scale(one, -1))), mul(s1, s1)]
    represented = [add(scale(r, -1), scale(r, Q(1, 2)), scale(r, Q(1, 2))),
                   scale(mul(r, add(d, e)), Q(3, 2)),
                   scale(mul(r, add(mul(d, d), mul(e, e))), Q(3, 2)),
                   scale(mul(r, add(mul(mul(d, d), d), mul(mul(e, e), e))), Q(1, 2))]
    pell = add(mul(r, r), scale(mul(n, n), -3), scale(one, -1))
    expected = [{}, {}, scale(mul(r, pell), Q(-1, 4)),
                scale(mul(mul(r, rm1), pell), Q(-1, 8))]
    residual = [add(a, scale(b, -1)) for a, b in zip(represented, target)]
    require(residual == expected, 'universal off-Pell residual identity')
    require(any(residual), 'residual incorrectly assumed identically zero')


def directions(r, n):
    require(type(r) is int and type(n) is int and r >= 3 and n > 0,
            'nondegenerate positive integer domain')
    require(r * r - 3 * n * n == 1, 'not a Pell solution')
    require((r - 1 - n) % 2 == 0, 'nonintegral direction')
    d, e = (r - 1 - n) // 2, (r - 1 + n) // 2
    require(0 < d < e < r, 'source direction order')
    return d, e


def moments(r, nodes, weights):
    require(len(nodes) == len(weights) == 3 and len(set(nodes)) == 3,
            'three distinct nodes required')
    require(all(w and w.denominator & (w.denominator - 1) == 0 for w in weights),
            'nonzero dyadic query weights required')
    s1 = Q(r * (r - 1), 2)
    expected = [Q(0), s1, s1 * Q(2 * r - 1, 3), s1 * s1]
    actual = [sum((w * Q(c) ** k for c, w in zip(nodes, weights)), Q(0))
              for k in range(4)]
    require(actual == expected, 'cubic coefficient mismatch')


def main():
    inputs = check_sources()
    symbolic_residual()
    r, n = 1, 0
    novel = 0
    for k in range(1, 97):
        r, n = 2 * r + 3 * n, r + 2 * n
        require(r * r - 3 * n * n == 1, 'recurrence norm')
        if k == 1:
            require((r, n) == (2, 1), 'degenerate initial term')
            rejected(lambda: directions(r, n))
            continue
        d, e = directions(r, n)
        moments(r, [0, d, e], [Q(-r), Q(r, 2), Q(r, 2)])
        previous = (2 * r - 3 * n, 2 * n - r)
        require(1 <= previous[0] < r and 0 <= previous[1] < n,
                'Pell descent did not decrease')
        require(previous[0] ** 2 - 3 * previous[1] ** 2 == 1, 'descent norm')
        if k % 2 == 0 and (k // 2) % 3:
            require(r % 9 == 7 and r % 2 == 1, 'new-class congruences')
            require(r & (r - 1) != 0, 'unexpected power of two')
            require((r - 1) & (r - 2) != 0, 'unexpected power of two plus one')
            novel += 1
    # Membership screening uses integer square roots, not recurrence.
    members = []
    for arity in range(3, 10001):
        square, rem = divmod(arity * arity - 1, 3)
        root = isqrt(square)
        if rem == 0 and root * root == square:
            d, e = directions(arity, root)
            moments(arity, [0, d, e], [Q(-arity), Q(arity, 2), Q(arity, 2)])
            members.append(arity)
    require(members == [7, 26, 97, 362, 1351, 5042], 'bounded arity membership')
    for r, n in [(1, 0), (2, 1), (7, -4), (7, 5), (15, 8), (Q(7), 4)]:
        rejected(lambda r=r, n=n: directions(r, n))
    rejected(lambda: moments(7, [0, 1, 5], [Q(-7), Q(7, 2), Q(9, 2)]))
    rejected(lambda: moments(7, [0, 2, 5], [Q(-7), Q(7, 2), Q(7, 2)]))
    rejected(lambda: moments(7, [0, 1, 5], [Q(7), Q(-7, 2), Q(-7, 2)]))
    rejected(lambda: moments(7, [0, 1, 5], [Q(-7), Q(7, 3), Q(7, 2)]))
    rejected(lambda: moments(7, [0, 1, 1], [Q(-7), Q(7, 2), Q(7, 2)]))
    print('PASS_CUBIC_PELL sources=' + str(inputs)
          + ' symbolic_coefficients=4 pell_terms=96 nondegenerate_terms=95'
          + ' novel_class_terms=' + str(novel)
          + ' arity_screen=9998 hits=6 source_mutants=4 algebra_domain_controls=12 no_new_kappa')


if __name__ == '__main__':
    main()
