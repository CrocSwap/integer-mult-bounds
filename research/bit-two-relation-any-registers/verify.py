#!/usr/bin/env python3
"""Exact finite lemma and controls for the four-register two-relation proof.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The universal group-lattice theorem is in PROOF.md; this is not formalization.
Only Python's standard library is used. Checks remain active under -O.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations, product
import json
from pathlib import Path


class VerificationError(Exception):
    pass


def need(condition, message):
    if not condition:
        raise VerificationError(message)


def span(vectors):
    result = {0}
    for vector in vectors:
        result |= {value ^ vector for value in tuple(result)}
    return result


def brank(vectors):
    return len(span(vectors)).bit_length() - 1


def subspaces(n):
    masks = set()
    for dimension in range(1, n):
        for basis in combinations(range(1, 1 << n), dimension):
            values = span(basis)
            if len(values) == 1 << dimension:
                masks.add(sum(1 << value for value in values))
    return sorted(masks)


def rows(matrix, n=4):
    return tuple((matrix >> (n * i)) & ((1 << n) - 1) for i in range(n))


def packed(matrix):
    n = len(matrix)
    return sum(row << (n * i) for i, row in enumerate(matrix))


def apply(matrix, vector):
    return sum(((row & vector).bit_count() & 1) << i
               for i, row in enumerate(matrix))


def multiply(left, right):
    return tuple(xor_rows(row, right) for row in left)


def xor_rows(mask, matrix):
    result = 0
    for i, row in enumerate(matrix):
        if mask >> i & 1:
            result ^= row
    return result


def invariant(matrix, space):
    return all(space >> apply(matrix, v) & 1
               for v in range(1 << len(matrix)) if space >> v & 1)


def proper_space(space, n=4):
    if type(space) is not int or not 0 < space < (1 << (1 << n)) - 1:
        return False
    values = [v for v in range(1 << n) if space >> v & 1]
    return len(values) > 1 and 0 in values and all(
        space >> (u ^ v) & 1 for u in values for v in values)


def catalogue():
    # Exhaust all 65,536 matrices, not merely a list of supplied outer products.
    diagonal = sum(1 << (4 * i + i) for i in range(4))
    found = {}
    for matrix in range(1 << 16):
        rr = rows(matrix)
        nonzero = set(rr) - {0}
        if len(nonzero) != 1:
            continue  # A nonzero binary rank-one matrix has one nonzero row value.
        if multiply(rr, rr) != rr:
            continue
        y = next(iter(nonzero))
        x = sum((row != 0) << i for i, row in enumerate(rr))
        need((x & y).bit_count() % 2 == 1, "idempotent self-pairing")
        found[matrix] = (matrix & ~diagonal, x, y)
    patterns = sorted({entry[0] for entry in found.values()} - {0})
    planes = sorted({tuple(sorted((p, q, p ^ q)))
                     for p, q in combinations(patterns, 2)})
    need(len(found) == 120, "120 rank-one idempotents")
    need(len(patterns) == 104, "104 nonzero patterns")
    need(len(planes) == 4964, "4964 pattern planes")
    return found, patterns, planes


def pool(found, plane):
    return sorted(m for m, (pattern, _, _) in found.items() if pattern in plane)


def canonical_full_rank_pools():
    result = set()
    for p in permutations(range(4)):
        result.add(tuple(sorted(
            (1 << (4 * p[a] + p[a])) | (1 << (4 * p[b] + p[c]))
            for a, b, c in ((0, 0, 1), (1, 0, 1), (2, 2, 3), (3, 2, 3)))))
    need(len(result) == 12, "twelve disjoint-edge pools")
    return result


def make_certificate(found, planes, spaces):
    records = []
    for plane in planes:
        matrices = [rows(m) for m in pool(found, plane)]
        witness = next((s for s in spaces if all(invariant(m, s) for m in matrices)), None)
        need(witness is not None, "an irreducible pool was found")
        records.append([*plane, witness])
    return {"schema_version": 1,
            "encoding": "matrix bit 4*i+j is entry (i,j); subspace bit v marks binary vector v",
            "records": records}


def check_certificate(document, found, planes):
    need(document.get("schema_version") == 1, "certificate schema")
    records = document.get("records")
    need(type(records) is list and len(records) == len(planes), "plane coverage count")
    seen = set()
    sizes, ranks = Counter(), Counter()
    full_rank = set()
    for record in records:
        need(type(record) is list and len(record) == 4, "record shape")
        p, q, r, space = record
        plane = (p, q, r)
        need(plane not in seen, "duplicate plane")
        seen.add(plane)
        need(proper_space(space), "witness is not a proper binary subspace")
        matrices = pool(found, plane)
        need(matrices, "empty pool")
        for matrix in matrices:
            need(invariant(rows(matrix), space), "noninvariant witness")
        rx = brank(found[m][1] for m in matrices)
        ry = brank(found[m][2] for m in matrices)
        sizes[len(matrices)] += 1
        ranks[rx, ry] += 1
        if rx == ry == 4:
            full_rank.add(tuple(matrices))
    need(seen == set(planes), "complete plane domain differs")
    need(dict(sizes) == {2: 3814, 3: 1012, 4: 114, 5: 24}, "pool-size census")
    need(full_rank == canonical_full_rank_pools(), "full-rank pool characterization")
    return {"idempotents": 120, "patterns": 104, "planes": len(seen),
            "pool_sizes": sorted(sizes.items()),
            "image_covector_ranks": [list(key) + [value] for key, value in sorted(ranks.items())],
            "full_rank_pools": len(full_rank), "irreducible_pools": 0}


def reject(function, description):
    try:
        function()
    except VerificationError:
        return description
    raise VerificationError("negative control accepted: " + description)


def inverse(matrix):
    n = len(matrix)
    work = [row | (1 << (n + i)) for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if work[i] >> j & 1), None)
        need(pivot is not None, "basis is singular")
        work[j], work[pivot] = work[pivot], work[j]
        for i in range(n):
            if i != j and work[i] >> j & 1:
                work[i] ^= work[j]
    return tuple(row >> n for row in work)


def adapted_basis(space):
    basis = []
    for value in range(1, 16):
        if space >> value & 1 and value not in span(basis):
            basis.append(value)
    dimension = len(basis)
    for value in range(1, 16):
        if value not in span(basis):
            basis.append(value)
    return tuple(sum(((basis[j] >> i) & 1) << j for j in range(4))
                 for i in range(4)), dimension


def structural_controls(found, patterns, spaces):
    count = 0
    for space in spaces:
        basis, d = adapted_basis(space)
        inv = inverse(basis)
        for matrix in found:
            rr = rows(matrix)
            if not invariant(rr, space):
                continue
            block = multiply(multiply(inv, rr), basis)
            need(all(not (block[i] & ((1 << d) - 1)) for i in range(d, 4)), "lower block")
            left = tuple(block[i] & ((1 << d) - 1) for i in range(d))
            right = tuple(block[i] >> d for i in range(d, 4))
            need(bool(any(left)) != bool(any(right)), "exactly one active block")
            active = left if any(left) else right
            need(multiply(active, active) == active and brank(active) == 1, "active block projector")
            count += 1
    coordinates = [1 << (4 * i + i) for i in range(4)]
    for pattern in patterns:
        matrices = [rows(m) for m, entry in found.items() if entry[0] == pattern]
        matrices += [rows(m) for m in coordinates]
        need(any(all(invariant(m, s) for m in matrices) for s in spaces), "one-pattern reduction")

    # P,Q,R from #720: irreducible on three active coordinates, reducible on four.
    exceptional = ((3, 0, 0), (2, 2, 0), (0, 5, 5))
    need(not any(all(invariant(m, s) for m in exceptional) for s in subspaces(3)),
         "three-register exception must not be labelled triangular")
    embedded = tuple(tuple(m) + (0,) for m in exceptional)
    need(all(invariant(m, (1 << 0) | (1 << 8)) for m in embedded), "embedded invariant line")

    overlapping = [(7, 7, 7, 0), (0, 14, 14, 14)]
    with_coordinates = overlapping + [rows(m) for m in coordinates]
    need(any(all(invariant(m, s) for m in overlapping) for s in spaces), "noncoordinate reduction")
    need(not any(all(invariant(m, s) for m in with_coordinates) for s in spaces),
         "coordinate calls cannot be retained in general pool lemma")

    # Repeated target values can preserve a non-coordinate line; separating them cannot.
    line = {0, 3}
    def diagonal_preserves(groups):
        return all((v & group) in line for v in line for group in groups)
    need(diagonal_preserves((3, 4, 8)), "equal-target invariant decomposition")
    need(not diagonal_preserves((1, 6, 8)), "separated-target rejection")
    return {"proper_subspaces": len(spaces), "invariant_block_cases": count,
            "one_pattern_pools": len(patterns), "nontriangular_control": True,
            "coordinate_split_control": True, "repeated_target_control": True}


def qrank(matrix):
    matrix = [[Fraction(x) for x in row] for row in matrix]
    if not matrix:
        return 0
    rank = 0
    for j in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][j]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scalar = matrix[rank][j]
        matrix[rank] = [value / scalar for value in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank:
                scalar = matrix[i][j]
                matrix[i] = [a - scalar * b for a, b in zip(matrix[i], matrix[rank])]
        rank += 1
        if rank == len(matrix):
            break
    return rank


ZERO = (0, 0, 0, 0)


def polynomial_product(left, right):
    result = set()
    for a in left:
        for b in right:
            exponent = tuple(x + y for x, y in zip(a, b))
            result.symmetric_difference_update((exponent,))
    return result


def formal_word(calls, n):
    result = [[{ZERO} if i == j else set() for j in range(n)] for i in range(n)]
    for frame, x, y in calls:
        need(len(frame) == 4 and frame != ZERO and (x & y).bit_count() % 2, "legal formal call")
        factor = [[{ZERO} if i == j else set() for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(n):
                if x >> i & 1 and y >> j & 1:
                    factor[i][j].symmetric_difference_update((ZERO, frame))
        new = [[set() for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    new[i][j].symmetric_difference_update(polynomial_product(result[i][k], factor[k][j]))
        result = new
    return result


def endpoint(targets):
    return [[{target} if i == j else set() for j in range(len(targets))]
            for i, target in enumerate(targets)]


def exact_word_controls():
    # Six rank-one integer frames in Sym_2, span three; all address arithmetic stays over Z.
    frames = [(2, 0, 0, 0), (0, 0, 0, 2), (2, 0, 0, 0),
              (0, 0, 0, 4), (3, 3, 3, 3), (1, -1, -1, 1)]
    calls = [(frame, 1 << (j // 2), 1 << (j // 2)) for j, frame in enumerate(frames)]
    targets = [(2, 0, 0, 2), (2, 0, 0, 4), (4, 2, 2, 4), ZERO]
    need(qrank(frames) == 3, "six-call frame span three")
    need(all(qrank((f[:2], f[2:])) == 1 for f in frames), "rank-one rational frames")
    need(all(qrank((c[:2], c[2:])) == 2 for c in targets[:3]), "invertible targets")
    need(formal_word(calls, 4) == endpoint(targets), "six-call exact endpoint")
    for j in range(6):
        need(formal_word(calls[:j] + calls[j + 1:], 4) != endpoint(targets), "deleted-call rejection")
    # C1^-1 C2=diag(1,2), C1^-1 C3=[[2,1],[1,2]]: commutator determinant one.
    u = tuple(Fraction(v, 2) for v in targets[1])
    v = tuple(Fraction(value, 2) for value in targets[2])
    def product2(a, b):
        return tuple(sum(a[2 * i + k] * b[2 * k + j] for k in range(2))
                     for i in range(2) for j in range(2))
    commutator = tuple(a - b for a, b in zip(product2(u, v), product2(v, u)))
    need(commutator[0] * commutator[3] - commutator[1] * commutator[2] == 1,
         "no-common-algebraic-flag witness")
    helper = (1, 0, 0, 0)
    restored = calls + [(helper, 8, 8), (tuple(-x for x in helper), 8, 8)]
    need(formal_word(restored, 4) == endpoint(targets), "arbitrary helper restoration")
    need(formal_word(restored[:-1], 4) != endpoint(targets), "missing helper cleanup")
    return {"sharp_six_call_words": 1, "rational_frame_span": 3,
            "deleted_call_rejections": 6, "helper_cleanup_rejection": 1,
            "nonflag_commutator_determinant": 1}


def joint_image_controls():
    """Bounded corroboration of the written all-width lemma; not extrapolation."""
    report = []
    for n in range(2, 6):
        diagonal = sum(1 << (n * i + i) for i in range(n))
        by_pattern = {}
        total = 0
        for x in range(1, 1 << n):
            for y in range(1, 1 << n):
                if not (x & y).bit_count() % 2:
                    continue
                total += 1
                matrix = sum((y if x >> i & 1 else 0) << (n * i) for i in range(n))
                pattern = matrix & ~diagonal
                if pattern:
                    by_pattern.setdefault(pattern, []).append(x)
        for pattern, images in by_pattern.items():
            need(len(images) == (2 if pattern.bit_count() == 1 else 1), "inherited fiber control")
        planes = {tuple(sorted((p, q, p ^ q))) for p, q in combinations(by_pattern, 2)}
        histogram = Counter()
        two_edges_realized = 0
        for plane in planes:
            images = [x for pattern in plane for x in by_pattern.get(pattern, [])]
            dimension = brank(images)
            need(dimension <= 4, "joint image exceeds four")
            histogram[dimension] += 1
            edges = [p for p in plane if p.bit_count() == 1]
            if dimension == 4:
                need(len(edges) == 2 and edges[0] ^ edges[1] not in by_pattern,
                     "dimension four must have exactly two realized edge patterns")
                endpoints = [coordinate for edge in edges
                             for coordinate in divmod(edge.bit_length() - 1, n)]
                need(len(set(endpoints)) == 4, "dimension-four edges must have disjoint endpoints")
            if len(edges) == 2 and edges[0] ^ edges[1] in by_pattern:
                a, b = divmod(edges[0].bit_length() - 1, n)
                c, d = divmod(edges[1].bit_length() - 1, n)
                need(a == c or b == d, "realized two-edge pattern must share row or column")
                need(dimension <= 3, "two-edge realized pool dimension")
                two_edges_realized += 1
        if n >= 4:
            need(max(histogram) == 4, "sharp image dimension four")
        report.append({"width": n, "idempotents": total, "patterns": len(by_pattern),
                       "planes": len(planes), "image_dimensions": sorted(histogram.items()),
                       "realized_two_edge_planes": two_edges_realized})
    return report


def common_j_controls():
    """Exact bounded checks for the new odd-core quadratic and endpoint steps."""
    prefix_cases = 0
    for s in (3, 5, 7):
        # Stars have the one all-sum relation, independent of the J pattern.
        stars = [tuple(((1 << s) - 1) ^ (1 << i) if row == i else (1 << i)
                       for row in range(s)) for i in range(s)]
        packed_stars = [packed(m) for m in stars]
        j_off = packed(tuple(((1 << s) - 1) ^ (1 << i) for i in range(s)))
        need(brank(packed_stars) == s - 1, "star relation rank")
        need(j_off not in span(packed_stars), "J pattern independent of stars")
        # One coordinate occurrence per role. Universal proof covers all multiplicities.
        for h in (2, 3, 4):
            prefixes = [0] + [(1 << gap) - 1 for gap in range(1, h)]
            for placements in product(prefixes, repeat=s):
                common = None
                for i in range(s - 1):
                    columns = [0] * s
                    columns[i], columns[-1] = placements[i], placements[-1]
                    nonzero = set(columns) - {0}
                    if len(nonzero) > 1:
                        common = set()
                        break
                    if nonzero:
                        j_factor = next(iter(nonzero))
                        c_factor = sum((bool(value)) << j for j, value in enumerate(columns))
                        factors = {("J", j_factor), ("coordinate", c_factor)}
                        common = factors if common is None else common & factors
                divisible = common is None or bool(common)
                single_gap = len(set(placements) - {0}) <= 1
                need(divisible == single_gap, "shared linear divisor versus single gap")
                prefix_cases += 1
        j = (1 << s) - 1
        b, a = (1, 0, 0, 0), (0, 0, 0, 1)
        minus_b, minus_a = tuple(-v for v in b), tuple(-v for v in a)
        positive = [(b, j, j), (a, 1, 1), (minus_a, 1, 1), (minus_b, j, j)]
        negative = [(b, j, j), (a, 1, 1), (minus_b, j, j), (minus_a, 1, 1)]
        need(formal_word(positive, s) == endpoint([ZERO] * s), "odd-core one-gap cancellation")
        bad = formal_word(negative, s)
        need(any(bad[i][k] for i in range(s) for k in range(s) if i != k),
             "separated internal gaps rejected by exact endpoint")
    # A five-coordinate common-J pool plus coordinates is irreducible. The
    # arbitrary-width case needs the quadratic proof, not a four-dimensional image shortcut.
    spaces5 = subspaces(5)
    need(len(spaces5) == 372, "five-coordinate proper subspace count")
    matrices = [(31,) * 5] + [tuple(1 << i if row == i else 0 for row in range(5)) for i in range(5)]
    need(not any(all(invariant(m, space) for m in matrices) for space in spaces5),
         "odd-width full common-pattern alphabet must remain irreducible")
    return {"odd_core_sizes": [3, 5, 7], "quadratic_prefix_cases": prefix_cases,
            "one_gap_positive_words": 3, "separated_gap_negative_words": 3,
            "width_five_irreducible_control": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-certificate", type=Path)
    args = parser.parse_args()
    found, patterns, planes = catalogue()
    spaces = subspaces(4)
    need(len(spaces) == 65, "65 proper nonzero binary subspaces")
    if args.emit_certificate:
        document = make_certificate(found, planes, spaces)
        args.emit_certificate.write_text(json.dumps(document, separators=(",", ":")) + "\n")
    else:
        document = json.loads(Path(__file__).with_name("CERTIFICATE.json").read_text())
    census = check_certificate(document, found, planes)
    controls = []
    bad = dict(document, records=document["records"][:-1])
    controls.append(reject(lambda: check_certificate(bad, found, planes), "omitted plane"))
    bad_records = [list(row) for row in document["records"]]
    first_pool = pool(found, tuple(bad_records[0][:3]))
    bad_records[0][3] = next(s for s in spaces if not all(invariant(rows(m), s) for m in first_pool))
    controls.append(reject(lambda: check_certificate(dict(document, records=bad_records), found, planes),
                           "proper but noninvariant witness"))
    report = {"census": census, "structural_controls": structural_controls(found, patterns, spaces),
              "exact_word_controls": exact_word_controls(), "certificate_rejections": controls,
              "joint_image_controls": joint_image_controls(), "common_j_controls": common_j_controls()}
    print("PASS_TWO_RELATION_ANY_REGISTERS")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
