#!/usr/bin/env python3
"""Bounded exact synthetic audit of kernel_scan.py's source-span predicate."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location(
    'kernel_scan_under_review', ROOT / 'kernel_screen.py')
K = importlib.util.module_from_spec(spec)
spec.loader.exec_module(K)


def require(ok, label):
    if not ok:
        raise AssertionError(label)


def row_add(dst, src, q):
    for i, x in src.items():
        y = dst.get(i, F(0)) + q * x
        if y:
            dst[i] = y
        else:
            dst.pop(i, None)


def row_scale(row, q):
    for i in list(row):
        row[i] *= q
        if not row[i]:
            del row[i]


def direct_nullspace(rows, active):
    """Independent RREF nullspace of row columns, over exact Q."""
    fields = sorted(active)
    width = len(fields)
    coords = sorted({i for a in fields for i in rows[a]})
    mat = [[rows[a].get(c, F(0)) for a in fields] for c in coords]
    pivots = []
    r = 0
    for c in range(width):
        q = next((i for i in range(r, len(mat)) if mat[i][c]), None)
        if q is None:
            continue
        mat[r], mat[q] = mat[q], mat[r]
        d = mat[r][c]
        mat[r] = [x / d for x in mat[r]]
        for i in range(len(mat)):
            if i != r and mat[i][c]:
                d = mat[i][c]
                mat[i] = [x - d * y for x, y in zip(mat[i], mat[r])]
        pivots.append(c)
        r += 1
        if r == len(mat):
            break
    free = [c for c in range(width) if c not in pivots]
    out = []
    for c in free:
        v = {fields[c]: F(1)}
        for i, p in enumerate(pivots):
            if mat[i][c]:
                v[fields[p]] = -mat[i][c]
        out.append(v)
    return out


def in_vector_span(target, vectors):
    basis = {}
    for raw in vectors:
        v = raw.copy()
        while v:
            p = min(v)
            if p not in basis:
                q = 1 / v[p]
                basis[p] = {i: x * q for i, x in v.items()}
                break
            row_add(v, basis[p], -v[p])
    v = target.copy()
    while v:
        p = min(v)
        if p not in basis:
            return False
        row_add(v, basis[p], -v[p])
    return True


def kernel_equal(kernel, expected, active):
    actual = [r.copy() for r in kernel]
    require(len(actual) == len(expected), 'synthetic relation rank')
    require(all(in_vector_span(r, expected) for r in actual),
            'kernel update sound against direct rows')
    require(all(in_vector_span(r, actual) for r in expected),
            'kernel update complete against direct rows')
    require(all(not any(a not in active and q for a, q in r.items())
                for r in actual), 'active coordinate support')


def check_all_bank_predicates(kernel, rows, active):
    checked = 0
    witnesses = 0
    fields = sorted(active)
    for a in fields:
        others = [x for x in fields if x != a]
        for size in range(len(others) + 1):
            for donor_tuple in combinations(others, size):
                donors = set(donor_tuple)
                expected = in_vector_span(rows[a], [rows[d] for d in donors])
                got = K.bank_relation(kernel, a, donors, float('inf'))
                require(got['inside'] == expected,
                        f'projection predicate for owner={a}, donors={donors}')
                if got['inside']:
                    witness = {int(i): F(q) for i, q in got['witness'].items()}
                    require(set(witness) <= donors,
                            'owner excluded from emitted donor witness')
                    rebuild = {}
                    for d, q in witness.items():
                        row_add(rebuild, rows[d], q)
                    require(rebuild == rows[a], 'exact synthetic donor witness')
                    witnesses += 1
                checked += 1
    return checked, witnesses


def run():
    # Public inputs begin independent; INIT adds a fresh zero row.
    rows = {0: {0: F(1)}, 1: {1: F(1)}}
    active = {0, 1}
    kernel = []
    kernel_equal(kernel, direct_nullspace(rows, active), active)

    rows[2] = {}
    active.add(2)
    kernel.append({2: F(1)})  # INIT
    kernel_equal(kernel, direct_nullspace(rows, active), active)

    # ADD from the zero row, then SCALE by a negative nonzero rational.
    rows[2] = {0: F(1)}
    K.scalar_add(kernel, 2, 0, F(1))
    kernel_equal(kernel, direct_nullspace(rows, active), active)
    row_scale(rows[2], F(-3, 2))
    for rel in kernel:
        if rel.get(2):
            rel[2] /= F(-3, 2)
    kernel_equal(kernel, direct_nullspace(rows, active), active)

    # Fresh INIT plus COPY into exact zero, followed by a dirty-coordinate case.
    rows[3] = {}
    active.add(3)
    kernel.append({3: F(1)})
    kernel_equal(kernel, direct_nullspace(rows, active), active)
    require(K.bank_relation(kernel, 3, set(), float('inf'))['inside'],
            'the freshly initialized COPY target is exactly zero')
    rows[3] = {1: F(2), 0: F(-1)}
    K.scalar_add(kernel, 3, 1, F(2))
    K.scalar_add(kernel, 3, 0, F(-1))
    kernel_equal(kernel, direct_nullspace(rows, active), active)
    checked, witnesses = check_all_bank_predicates(kernel, rows, active)
    require(not K.bank_relation(kernel, 3, {1}, float('inf'))['inside'],
            'reject a local relation with missing dirty donor')

    # COPY guard: only the exact-zero owned destination is admissible.
    fresh = [{2: F(1)}]
    require(K.bank_relation(fresh, 2, set(), float('inf'))['inside'],
            'exact-zero COPY destination accepted')
    require(not K.bank_relation(kernel, 0, set(), float('inf'))['inside'],
            'nonzero COPY destination rejected')

    # CLEAR intersects the relation space with c_a=0 and drops that coordinate.
    K.clear(kernel, 2)
    active.remove(2)
    del rows[2]
    kernel_equal(kernel, direct_nullspace(rows, active), active)
    checked2, witnesses2 = check_all_bank_predicates(kernel, rows, active)

    # Singular public prefix / dependent CLEAR control from the source helper.
    singular = [{2: F(1)}]
    K.scalar_add(singular, 2, 0, F(1))
    K.scalar_add(singular, 0, 2, F(-1))
    require(K.bank_relation(singular, 0, set(), float('inf'))['inside'],
            'singular prefix yields zero target')
    K.clear(singular, 2)
    require(K.bank_relation(singular, 0, set(), float('inf'))['inside'],
            'CLEAR retains independent zero relation')

    # Equal GF(2) subspaces share a bank key, even with a redundant generator.
    require(K.span([1, 2]) == K.span([1, 2, 3]),
            'GF(2) redundant frame generator merges')
    require(K.span([1, 2]) != K.span([1]), 'distinct GF(2) subspaces stay apart')

    result = dict(status='PASS', source_helper_sha256=hashlib.sha256(
                      (ROOT / 'kernel_screen.py').read_bytes()).hexdigest(),
                  synthetic_direct_kernel_comparisons=7,
                  exact_bank_predicates_checked=checked + checked2,
                  exact_witnesses_verified=witnesses + witnesses2,
                  controls=dict(init_zero=True, add=True, negative_scale=True,
                                copy_zero_guard=True, dirty_coordinate_rejection=True,
                                clear_intersection=True, singular_prefix=True,
                                dependent_clear=True, owner_exclusion=True,
                                exact_rational_witnesses=True,
                                gf2_redundant_frame_alias=True))
    return result


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
