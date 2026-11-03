#!/usr/bin/env python3
"""Exact finite corroboration of the new half-line spectrum and rank-error law."""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
import math
from pathlib import Path

MAX_DEGREE = 33
MODES = 16
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = 'research/gaussian-half-line-operator-limit/PROOF.md'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def trim(p: tuple[F, ...]) -> tuple[F, ...]:
    for j in range(len(p) - 1, -1, -1):
        if p[j]:
            return p[:j + 1]
    return (F(0),)


def add(p: tuple[F, ...], q: tuple[F, ...]) -> tuple[F, ...]:
    size = max(len(p), len(q))
    return trim(tuple((p[i] if i < len(p) else F(0)) +
                      (q[i] if i < len(q) else F(0)) for i in range(size)))


def scale(p: tuple[F, ...], c: F) -> tuple[F, ...]:
    return trim(tuple(c * v for v in p))


def derivative(p: tuple[F, ...]) -> tuple[F, ...]:
    return trim(tuple(i * p[i] for i in range(1, len(p))))


def hermite_explicit(n: int) -> tuple[F, ...]:
    require(type(n) is int and 0 <= n <= MAX_DEGREE, 'invalid degree')
    p = [F(0)] * (n + 1)
    for j in range(n // 2 + 1):
        p[n - 2 * j] = F((-1)**j * math.factorial(n) * 2**(n - 2 * j),
                         math.factorial(j) * math.factorial(n - 2 * j))
    return tuple(p)


def hermite_recurrence() -> tuple[tuple[F, ...], ...]:
    terms = [(F(1),), (F(0), F(2))]
    for n in range(1, MAX_DEGREE):
        terms.append(add((F(0),) + scale(terms[-1], F(2)),
                         scale(terms[-2], F(-2 * n))))
    require(len(terms) == MAX_DEGREE + 1, 'recurrence capacity')
    return tuple(terms)


def reverse_integral(p: tuple[F, ...]) -> tuple[F, ...]:
    """Solve 2x Q-Q'=P by descending coefficients, not a Hermite recurrence."""
    require(1 < len(p) <= MAX_DEGREE + 1 and len(p) % 2 == 0,
            'odd degree required')
    require(all(not p[i] for i in range(0, len(p), 2)), 'odd parity required')
    residual = list(p)
    q = [F(0)] * (len(p) - 1)
    for j in range(len(p) - 2, -1, -2):
        q[j] = residual[j + 1] / 2
        residual[j + 1] -= 2 * q[j]
        if j:
            residual[j - 1] += j * q[j]
    require(not any(residual), 'antiderivative remainder')
    return trim(tuple(q))


def gram(p: tuple[F, ...], q: tuple[F, ...]) -> F:
    """Integral_0^infinity P Q exp(-x^2) dx / sqrt(pi), same parity only."""
    result = F(0)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            if a and b:
                require((i + j) % 2 == 0, 'mixed parity integral')
                m = (i + j) // 2
                moment = F(math.factorial(2 * m), 2 * 4**m * math.factorial(m))
                result += a * b * moment
    return result


def spectrum_square(b: F, rank: int, copies: int = 2) -> F:
    require(type(b) is F and 0 < b <= 16, 'invalid b')
    require(type(rank) is int and 0 <= rank <= 4096, 'invalid rank')
    require(type(copies) is int and 1 <= copies <= 2, 'invalid copies')
    return 1 / (4 * b * (2 * (rank // copies) + 1))


def threshold(epsilon: F) -> int:
    require(type(epsilon) is F and F(1, 32) <= epsilon <= 1, 'invalid tolerance')
    x = (1 / epsilon**2 - 1) / 2
    return 2 * ((x.numerator + x.denominator - 1) // x.denominator)


def polynomial_checks() -> dict[str, int]:
    hs = hermite_recurrence()
    for n, p in enumerate(hs):
        require(p == hermite_explicit(n), 'independent Hermite formula')
    for n in range(MAX_DEGREE):
        weighted = add((F(0),) + scale(hs[n], F(2)), scale(derivative(hs[n]), F(-1)))
        require(weighted == hs[n + 1], 'weighted derivative')
    for k in range(MODES):
        require(reverse_integral(hs[2*k + 1]) == hs[2*k], 'literal inverse integral')
        for parity in range(2):
            n = 2*k + parity
            for j in range(MODES):
                expected = F(2**n * math.factorial(n), 2) if j == k else F(0)
                require(gram(hs[n], hs[2*j + parity]) == expected, 'Gaussian Gram')
        ratio = gram(hs[2*k], hs[2*k]) / gram(hs[2*k+1], hs[2*k+1])
        require(ratio == spectrum_square(F(1, 2), k, 1), 'singular normalization')
    return {'Hermite_polynomials': len(hs), 'weighted_derivatives': MAX_DEGREE,
            'literal_antiderivatives': MODES, 'Gaussian_Gram_entries': 2*MODES**2,
            'singular_normalizations': MODES}


def mixture_checks() -> int:
    hs = tuple(hermite_explicit(n) for n in range(8))
    count = 0
    for cs in itertools.product((-1, 0, 1), repeat=4):
        p, q = (F(0),), (F(0),)
        for k, c in enumerate(cs):
            p = add(p, scale(hs[2*k + 1], F(c)))
            q = add(q, scale(hs[2*k], F(c)))
        if any(cs):
            require(reverse_integral(p) == q, 'coherent integral mixture')
            predicted = sum(F(c*c * 2**(2*k) * math.factorial(2*k), 2)
                            for k, c in enumerate(cs))
            require(gram(q, q) == predicted, 'coherent output norm')
            require(gram(q, q) <= gram(p, p) / 2, 'contraction on mixture')
        else:
            require(q == (F(0),), 'zero mixture')
        count += 1
    return count


def rank_checks() -> dict[str, int]:
    subset_count = 0
    for b in (F(1, 8), F(1, 4), F(1, 2), F(1), F(7, 3)):
        weights = tuple(spectrum_square(b, r) for r in range(8))
        for r in range(8):
            errors = []
            for retained in itertools.combinations(range(8), r):
                errors.append(max(v for j, v in enumerate(weights) if j not in retained))
                subset_count += 1
            require(min(errors) == spectrum_square(b, r), 'best coordinate truncation')
    tolerances = set(F(i, j) for j in range(1, 33) for i in range(1, j + 1))
    for e in sorted(tolerances):
        rank = threshold(e)
        require(spectrum_square(F(1, 4), rank) <= e**2, 'threshold sufficiency')
        if rank:
            require(spectrum_square(F(1, 4), rank - 1) > e**2, 'threshold necessity')
    mixed = 0
    for a, b, c, d in itertools.product((-1, 0, 1), repeat=4):
        if a*d == b*c:
            if a or b:
                v = (b, -a)
            elif c or d:
                v = (d, -c)
            else:
                v = (1, 0)
            require(v != (0, 0) and a*v[0] + b*v[1] == 0 and
                    c*v[0] + d*v[1] == 0, 'rank-one mixed-edge kernel')
            mixed += 1
    return {'coordinate_truncations': subset_count, 'exact_tolerances': len(tolerances),
            'mixed_edge_rank_one_matrices': mixed}


def controls() -> int:
    bad = ((0, 0, 2), (F(0), 0, 2), (F(1), -1, 2),
           (F(1), True, 2), (F(1), 4097, 2), (F(1), 1, 0))
    count = 0
    for args in bad:
        try:
            spectrum_square(*args)
        except ValueError:
            count += 1
        else:
            raise ValueError('invalid spectrum accepted')
    for e in (F(0), F(1, 33), F(2), 0.5):
        try:
            threshold(e)
        except ValueError:
            count += 1
        else:
            raise ValueError('invalid tolerance accepted')
    require(spectrum_square(F(1), 1) != spectrum_square(F(1), 1, 1),
            'one-edge mutant must differ')
    require(spectrum_square(F(1, 2), 2, 1) != F(1, 2*(2+1)), 'parity mutant')
    require(spectrum_square(F(1, 8), 2) != spectrum_square(F(1, 2), 2),
            'missing dilation mutant')
    require(threshold(F(1, 2)) == 4 and threshold(F(1, 10)) == 100,
            'threshold fixtures')
    require(spectrum_square(F(1, 4), 1) == 1, 'rank-one duplicated top')
    return count + 5


def file_hashes() -> dict[str, str]:
    paths = sorted(PACKAGE.iterdir())
    require(1 <= len(paths) <= 16, 'package file count')
    result = {}
    for path in paths:
        require(path.is_file() and not path.is_symlink(), 'unexpected package entry')
        require(path.stat().st_size <= 1024*1024, 'package file capacity')
        result[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    rows = [row for row in manifest['files'] if row['path'] == SOURCE]
    require(len(rows) == 1, 'missing source theorem pin')
    source = ROOT / SOURCE
    require(source.stat().st_size <= 1024*1024, 'source file capacity')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    require(digest == rows[0]['sha256'], 'source theorem bytes changed')
    result[SOURCE] = digest
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    before = file_hashes()
    counts = polynomial_checks()
    counts['coherent_mixtures'] = mixture_checks()
    counts.update(rank_checks())
    counts['rejection_and_semantic_controls'] = controls()
    require(file_hashes() == before, 'proof inputs changed during verification')
    receipt = {'status': 'PASS_GAUSSIAN_INVERSE_RANK_ERROR', 'counts': counts,
               'claim_type': 'scoped written proof with finite exact corroboration',
               'sha256': before}
    encoded = json.dumps(receipt, sort_keys=True, indent=2) + '\n'
    if args.receipt is not None:
        path = args.receipt.resolve()
        require(not path.is_relative_to(ROOT), 'receipt must be outside the checkout')
        with path.open('x', encoding='utf-8') as stream:
            require(stream.write(encoded) == len(encoded), 'incomplete receipt write')
    print(encoded, end='')


if __name__ == '__main__':
    main()
