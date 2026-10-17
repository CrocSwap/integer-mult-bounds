#!/usr/bin/env python3
"""Independent F4 check using binary linear maps, never field scalar products.

Each coefficient is a dense 4-by-4 F2 matrix, as four bit-packed rows.
Exact address polynomials retain their integer exponents. No primary code
is imported. Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""

from itertools import permutations, product
import hashlib
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


UNIT = (1, 2, 4, 8)
NULL = (0, 0, 0, 0)
ORIGIN = (0, 0, 0, 0)
ADDRESSES = ((2, 0, 0, 0), (0, 0, 0, 2),
             (1, 1, 1, 1), (1, -1, -1, 1))
EXTRA = (0, 2, 0, 0)


def xor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def matmul(a, b):
    rows = []
    for mask in a:
        row = 0
        for i in range(4):
            if mask & (1 << i):
                row ^= b[i]
        rows.append(row)
    return tuple(rows)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def block_matrix(a, b, c, d):
    # 0, 1, w, 1+w act on the basis (1,w); w^2=1+w.
    # Matrices are row-packed, not polynomial field arithmetic.
    blocks = ((0, 0), (1, 2), (2, 3), (3, 1))
    a, b, c, d = [blocks[x] for x in (a, b, c, d)]
    return (a[0] | (b[0] << 2), a[1] | (b[1] << 2),
            c[0] | (d[0] << 2), c[1] | (d[1] << 2))


def multiply_polynomials(left, right):
    out = {}
    for exponent1, coefficient1 in left.items():
        for exponent2, coefficient2 in right.items():
            exponent = tuple(x+y for x, y in zip(exponent1, exponent2))
            coefficient = xor(out.get(exponent, NULL),
                              matmul(coefficient1, coefficient2))
            if coefficient == NULL:
                out.pop(exponent, None)
            else:
                out[exponent] = coefficient
    return out


def execute(gates):
    # Multiply from the *opposite* end from the primary streamed gate engine.
    state = {ORIGIN: UNIT}
    for address, projector in reversed(gates):
        factor = {ORIGIN: xor(UNIT, projector), address: projector}
        state = multiply_polynomials(factor, state)
    return state


def endpoint(a, b):
    out = {a: (1, 2, 0, 0)}
    out[b] = xor(out.get(b, NULL), (0, 0, 4, 8))
    return out


def main():
    projectors = []
    cyclic = []
    for a, b, c, d in product(range(4), repeat=4):
        matrix = block_matrix(a, b, c, d)
        if rank(matrix) != 2 or matmul(matrix, matrix) != matrix:
            continue
        projectors.append(matrix)
        if b != 0 and c != 0:
            cyclic.append(matrix)
    need(len(set(projectors)) == 20 and len(cyclic) == 6, "binary inventory")
    direct = endpoint((2, 0, 0, 2), (2, 0, 0, 2))
    extra_target = endpoint((2, 2, 0, 2), (2, 0, 0, 2))
    e0 = (1, 2, 0, 0)
    counts = {"full_dirty_endpoints": 0, "rejected_single_omissions": 0,
              "outside_placements_accepted": 0, "outside_placements_rejected": 0}
    all_placements = []
    for n in cyclic:
        gates = [(address, n if i < 2 else xor(UNIT, n))
                 for i, address in enumerate(ADDRESSES)]
        for permutation in permutations(range(4)):
            order = [gates[i] for i in permutation]
            need(execute(order) == direct, "binary dirty endpoint")
            counts["full_dirty_endpoints"] += 1
            for i in range(4):
                need(execute(order[:i]+order[i+1:]) != direct, "binary omitted call")
                counts["rejected_single_omissions"] += 1
            for cut in range(5):
                got = execute(order[:cut]+[(EXTRA, e0)]+order[cut:])
                all_placements.append([list(n), list(permutation), cut,
                                       [[list(a), list(m)] for a, m in sorted(got.items())]])
                accepted = got == extra_target
                need(accepted == (cut in (0, 4)), "binary outside placement")
                key = "outside_placements_" + ("accepted" if accepted else "rejected")
                counts[key] += 1
    # Every F4 projector is binary rank two. It has a direct two-call
    # decomposition into complementary, orthogonal binary rank-one projectors.
    splits = 0
    for n in projectors:
        basis = []
        images = []
        # Build bases of image and kernel by exhaustive binary columns.
        for label in (1, 0):
            chosen = []
            for v in range(1, 16):
                image = sum(((row & v).bit_count() % 2) << i
                            for i, row in enumerate(n))
                if (image == v if label else image == 0):
                    if rank(chosen+[v]) > len(chosen):
                        chosen.append(v)
            need(len(chosen) == 2, "binary image/kernel dimensions")
            basis.extend(chosen)
            if label:
                images = list(chosen)
        need(rank(basis) == 4, "scalar basis is invertible")
        # Obtain dual rows by the defining values on this column basis.
        duals = []
        for j in range(2):
            duals.append(next(row for row in range(16)
                              if all(((row & v).bit_count() % 2) == int(i == j)
                                     for i, v in enumerate(basis))))
        pieces = [tuple(duals[j] if images[j] & (1 << i) else 0
                        for i in range(4)) for j in range(2)]
        need(all(rank(p) == 1 and matmul(p, p) == p for p in pieces), "rank-one pieces")
        need(matmul(pieces[0], pieces[1]) == NULL
             == matmul(pieces[1], pieces[0]), "orthogonal pieces")
        need(xor(*pieces) == n, "two binary paid calls")
        frame = ADDRESSES[0]
        need(execute([(frame, pieces[0]), (frame, pieces[1])])
             == execute([(frame, n)]), "exact formal binary simulation")
        splits += 1
    counts.update(projectors=20, cyclic_projectors=6,
                  binary_two_call_decompositions=splits,
                  projectors_binary_sha256=hashlib.sha256(
                      json.dumps(sorted(projectors), separators=(",", ":")).encode()
                  ).hexdigest(),
                  all_placement_coefficients_binary_sha256=hashlib.sha256(
                      json.dumps(all_placements, sort_keys=True,
                                 separators=(",", ":")).encode()).hexdigest(),
                  representation="full formal Laurent coefficients in M4(F2)")
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
