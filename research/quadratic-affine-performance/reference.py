"""Verbatim pre-change reference rows and rank witness for differential tests.

Copied from scripts/experiments/quadratic_affine.py at base commit
2921874911956718fcaaaf9396fe8267b3cfa9f0 (the `inner` function and the
`sum(1<<j ...)` row construction inside `rank_witness`). family/vector are
imported unchanged from the shipped module. Apache-2.0; with help from opencode.
"""
from hashlib import sha256
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from certify import require
from experiments.quadratic_affine import family, vector


def inner(v, w):
    s, a, b = v; u, c, e = w; common = s & u
    lo = (a ^ c) & common; hi = (b ^ e ^ (a & ~c)) & common
    return (common ^ lo).bit_count() - 2 * (hi & ~lo).bit_count(), lo.bit_count() - 2 * (hi & lo).bit_count()


def reference_rows(vectors, row_indices):
    """One inner call per (row, column) pair, exactly as the base commit ran."""
    rows = {}
    for i in row_indices:
        rows[i] = sum(1 << j for j, v in enumerate(vectors) if i == j or inner(vectors[i], v) == (0, 0))
    return rows


def rank_witness_reference(t, complex_phases, parity, sample, independent_rows):
    f = family(t, complex_phases, parity)
    require(sample and len(set(sample)) == len(sample) and all(type(i) is int and 0 <= i < f['n'] for i in sample),
            'Sample must contain distinct valid labels')
    require(independent_rows and len(set(independent_rows)) == len(independent_rows) and
            all(type(i) is int and 0 <= i < len(sample) for i in independent_rows), 'Invalid independent row indices')
    vectors = [vector(f, i) for i in sample]
    rows = reference_rows(vectors, independent_rows)
    basis = {}; digest = sha256(); bytewidth = (len(sample) + 7) // 8
    for i in independent_rows:
        row = rows[i]
        digest.update(row.to_bytes(bytewidth, 'little')); x = row
        while x:
            p = x.bit_length() - 1
            if p not in basis: basis[p] = x; break
            x ^= basis[p]
        require(x != 0, 'Claimed rows are linearly dependent')
    r = len(basis); ell = f['ell']; d = f['d']; n = f['n']
    return dict(t=t, complex_phases=complex_phases, parity=parity, n=n, d=d, ell=ell,
                normalized_dimension=Q(d, ell), counts_by_support_dimension=f['counts'],
                minor_columns=len(sample), binary_rank_lower=r, independent_row_sha256=digest.hexdigest(),
                positive_deficit_excluded=n * ell <= 6 * r * d,
                scope='Only I plus the full orthogonality relation on this exact vector family; no rank upper bound asserted')
