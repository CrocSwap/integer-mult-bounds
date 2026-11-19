"""Recover all Clifford terms in an exact tensor train."""

import argparse
from collections import Counter
import json
from math import isqrt
from pathlib import Path

from field import Basis, G, I, LETTERS, ONE, PHASES, ZERO, decimal_integer, dot, solve
from train import advance, cut_basis, cut_slices, exact_match, read_train


def group_order(n):
    order = 1 << (n*n + 2*n)
    for j in range(1, n+1):
        order *= 4**j - 1
    return order


COMPLETE_FIBRES = 226718


def guaranteed_size(n, flank):
    order = group_order(n)
    if n == 4 and flank >= 13:
        return order
    if n == 4 and flank == 12:
        return 256*(COMPLETE_FIBRES+1) - 1
    if n == 4 and flank == 11:
        return 447742
    q = 1 << flank
    elementary = max(flank + 1, 1 + isqrt(q-1))
    if elementary >= order or flank == 0:
        return min(order, elementary)
    # Round sqrt(q)-1 up for an integer upper bound on the near-edge weight.
    c = isqrt(q-1)
    lo, hi = 1, min(order+1, q+2)
    while hi - lo > 1:
        mid = (lo+hi)//2
        margin = q + c + 1 - mid
        if margin > 0 and margin*margin > c*c*(3*mid-2):
            lo = mid
        else:
            hi = mid
    return min(order, max(elementary, lo))


def global_cut(n, chain, balanced, requested):
    short = min(len(chain)-13, balanced, 12)
    if n != 4 or short < 1:
        return None
    threshold = guaranteed_size(n, short)
    positions = sorted({short, len(chain)-short}, key=lambda j: chain[j].left)
    for j in positions:
        bound = chain[j].left
        if bound >= threshold or (requested is not None and bound > requested):
            left = cut_basis(chain[:j])
            right = cut_basis(reversed(chain[j:]), backward=True)
            basis = Basis()
            for _, row in left:
                basis.add(tuple(dot(row, column) for _, column in right))
            bound, kind = len(basis.rows), "flattening_rank"
        else:
            kind = "packed_bond"
        if bound < threshold and (requested is None or bound <= requested):
            return dict(cut=j, bound=bound, kind=kind, independence=threshold)
    return None


def independent_letters(slices):
    """Identify zero slices and slices that differ by a fourth root of unity."""
    seen, letters, locations = {}, [], []
    for q, matrix in enumerate(slices):
        if not any(any(row) for row in matrix):
            locations.append(None)
            continue
        if matrix not in seen:
            j = len(letters)
            letters.append((q, matrix))
            for unit in PHASES:
                key = tuple(tuple(z*unit for z in row) for row in matrix)
                seen[key] = (j, unit)
        locations.append(seen[matrix])
    return letters, locations


def signatures(slices, d, cap):
    letters, locations = independent_letters(slices)
    found = []
    for anchor, (physical, reference) in enumerate(letters):
        if physical >= d:
            break
        anchor_rows = tuple(Basis().extend(reference).rows.values())
        paths = [((), Basis())]
        for j, (_, matrix) in enumerate(letters):
            choices = (ZERO,) if j < anchor else (ONE,) if j == anchor else LETTERS
            children = []
            for unit in choices:
                equations = [tuple(x - unit*y for x, y in zip(a, b, strict=True))
                             for a, b in zip(matrix, reference, strict=True)]
                equations = tuple(Basis().extend(equations).rows.values())
                for word, constraints in paths:
                    space = constraints.extend(equations)
                    # A nonzero value at the anchor must survive on its kernel.
                    if len(space.extend(anchor_rows).rows) > len(space.rows):
                        children.append((word + (unit,), space))
                        if len(found) + len(children) > cap:
                            return None
            paths = children
            if not paths:
                break
        for values, _ in paths:
            found.append(tuple(ZERO if loc is None else values[loc[0]] * loc[1]
                               for loc in locations))
    return found


def clifford_data(w, n):
    """Check the scaled unitary and its action on all Pauli generators."""
    d = 1 << n
    columns = [w[d*x:d*(x+1)] for x in range(d)]
    height = sum(bool(z) for z in columns[0])
    if not height or height & (height-1):
        return None
    for x, column in enumerate(columns):
        if sum(bool(z) for z in column) != height:
            return None
        adjoint = tuple(z.conjugate() for z in column)
        if any(dot(adjoint, old) for old in columns[:x]):
            return None
    images = []
    for bit in range(n):
        for is_z in (False, True):
            flip = 0 if is_z else 1 << bit

            def entry(out, source):
                total = ZERO
                for x, column in enumerate(columns):
                    z = columns[x ^ flip][out] * column[source].conjugate()
                    total += -z if is_z and x & (1 << bit) else z
                return total / G(height)

            first = tuple(entry(y, 0) for y in range(d))
            nonzero = [y for y, z in enumerate(first) if z]
            if len(nonzero) != 1:
                return None
            shift = nonzero[0]
            phase = first[shift]
            if phase not in PHASES:
                return None
            diagonal = tuple(entry(y ^ shift, y) for y in range(d))
            mask = sum(1 << t for t in range(n) if diagonal[1 << t] == -phase)
            if any(z != (-phase if (y & mask).bit_count() % 2 else phase)
                   for y, z in enumerate(diagonal)):
                return None
            images.append((shift, mask))
    return height.bit_length() - 1, tuple(images)


def amplitudes(chain, cut, left, labels):
    if not labels:
        return []
    chosen, matrix, reduced = [], [], Basis()
    for word, state in left:
        row = []
        for w in labels:
            z = ONE
            for q in word:
                z = z * w[q]
            row.append(z)
        if reduced.add(row):
            chosen.append(state)
            matrix.append(row)
            if len(chosen) == len(labels):
                break
    if len(chosen) != len(labels):
        return None
    pivots = [next(q for q, value in enumerate(w) if value) for w in labels]
    values = [ZERO] * len(labels)
    for a in sorted(set(pivots)):
        state = (ONE,)
        for core in reversed(chain[cut:]):
            state = advance(state, core.slices[a], core.left, backward=True)
        rhs = [dot(row, state) for row in chosen]
        solution = solve(matrix, rhs)
        for j, pivot in enumerate(pivots):
            if pivot == a:
                values[j] = solution[j]
    return values


def decode(data, max_terms=None):
    n, chain = read_train(data)
    width = len(chain)
    cut = (width - 1) // 2
    size = guaranteed_size(n, cut)
    fibre_limit = COMPLETE_FIBRES if n == 4 and cut == 12 else None
    limit = None if size == group_order(n) or fibre_limit is not None else size
    if max_terms is not None:
        if type(max_terms) is not int or max_terms < 0:
            raise ValueError("max_terms must be a nonnegative integer")
        max_terms = min(max_terms, group_order(n))
        if limit is not None and max_terms > limit:
            raise ValueError("unsupported width for the requested support bound")
        limit = max_terms
    result = dict(qubits=n, width=width, support_limit=limit, complete_fibre_limit=fibre_limit)
    unrestricted = size == group_order(n) and (limit is None or limit == size)
    certificate = None if unrestricted else global_cut(n, chain, cut, max_terms)
    result.update(full_span_decision=unrestricted or certificate is not None, cut_certificate=certificate)
    left = cut_basis(chain[:cut])
    right = cut_basis(reversed(chain[cut+1:]), backward=True)
    slices = cut_slices(left, chain[cut], right)
    cap = min(len(left), len(right))
    if limit is not None:
        cap = min(cap, limit)
    labels = signatures(slices, 1 << n, cap)
    if labels is not None:
        records = [clifford_data(w, n) for w in labels]
        if all(record is not None for record in records):
            if fibre_limit is not None:
                counts = Counter(images for _, images in records)
                if sum(size == 4**n for size in counts.values()) > fibre_limit:
                    return dict(result, status="outside_model")
            coefficients = amplitudes(chain, cut, left, labels)
            if coefficients is not None and all(coefficients) and exact_match(chain, labels, coefficients):
                terms = []
                e = G(2**(n//2)) * ((ONE+I) if n % 2 else ONE)
                for w, alpha, (h, _) in zip(labels, coefficients, records, strict=True):
                    weight = alpha * ((ONE+I)**h * e)**width
                    signature = "".join(".+i-j"[LETTERS.index(z)] for z in w)
                    terms.append(dict(signature=signature, h=h, coefficient=weight.pair()))
                return dict(result, status="member", terms=sorted(terms, key=lambda t:t["signature"]))
    return dict(result, status="outside_model")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--max-terms", type=decimal_integer)
    args = parser.parse_args()
    try:
        answer = decode(json.loads(args.input.read_text(), parse_int=decimal_integer), args.max_terms)
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        parser.exit(2, f"invalid input: {error}\n")
    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    main()
