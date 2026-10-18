#!/usr/bin/env python3
"""Independent exact finite geometry audit for the E8 d=0 argument.

Prepared by conorholds with substantial OpenAI Codex assistance; Apache-2.0.
The E8/2E8 and decoder setting follows DreamingOfClouds' PR2816, PR2826,
PR2862 and PR2985.  This checker generates its own roots, normal orbits,
binary labels and rank calculations; it imports no predecessor or primary
verifier mathematics.  The parabolic completeness implication is a written
root-system argument, not a claim that enumerating 256 subsets proves it.
"""

from collections import Counter, deque
from fractions import Fraction
from itertools import combinations
from math import gcd
import json


class AuditFailure(RuntimeError):
    """A failed mathematical or coverage check, including under python -O."""


def check(condition, message):
    if not condition:
        raise AuditFailure(message)


def canonical(vector):
    for value in vector:
        if value:
            return tuple(vector) if value > 0 else tuple(-x for x in vector)
    raise AuditFailure("zero has no projective representative")


def integer_rank(rows):
    """Fraction-free row elimination, reducing each new row by its gcd."""
    rows = [list(row) for row in rows if any(row)]
    if not rows:
        return 0
    width = len(rows[0])
    check(all(len(row) == width for row in rows), "ragged rank input")
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_row = rows[rank]
        for i in range(rank + 1, len(rows)):
            coefficient = rows[i][column]
            if not coefficient:
                continue
            row = [pivot_row[column] * x - coefficient * y
                   for x, y in zip(rows[i], pivot_row)]
            divisor = 0
            for value in row:
                divisor = gcd(divisor, value)
            rows[i] = [value // divisor for value in row] if divisor else row
        rank += 1
        if rank == width:
            break
    return rank


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def inverse_integer_matrix(matrix):
    n = len(matrix)
    rows = [[Fraction(x) for x in row]
            + [Fraction(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        check(pivot is not None, "singular Cartan matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for i in range(n):
            if i != column and rows[i][column]:
                scale = rows[i][column]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[column])]
    result = [row[n:] for row in rows]
    check(all(x.denominator == 1 for row in result for x in row),
          "E8 Cartan inverse is not integral")
    return [[int(x) for x in row] for row in result]


class CartanModel:
    """Integral simple-root coordinates; only the frame uses a D8 bridge."""

    edges = ((0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7))
    simple_doubled = (
        (1, -1, -1, -1, -1, -1, -1, 1),
        (2, 2, 0, 0, 0, 0, 0, 0),
        (-2, 2, 0, 0, 0, 0, 0, 0),
        (0, -2, 2, 0, 0, 0, 0, 0),
        (0, 0, -2, 2, 0, 0, 0, 0),
        (0, 0, 0, -2, 2, 0, 0, 0),
        (0, 0, 0, 0, -2, 2, 0, 0),
        (0, 0, 0, 0, 0, -2, 2, 0),
    )

    def __init__(self):
        self.cartan = [[2 * (i == j) for j in range(8)] for i in range(8)]
        for i, j in self.edges:
            self.cartan[i][j] = self.cartan[j][i] = -1
        bridge_gram = [[sum(x * y for x, y in zip(a, b))
                        for b in self.simple_doubled] for a in self.simple_doubled]
        check(bridge_gram == [[4 * x for x in row] for row in self.cartan],
              "fixed coordinate bridge disagrees with Cartan matrix")
        self.inverse = inverse_integer_matrix(self.cartan)
        simple = [tuple(int(i == j) for i in range(8)) for j in range(8)]
        roots = set(simple)
        queue = deque(simple)
        while queue:
            root = queue.popleft()
            for generator in range(8):
                image = self.reflect(root, generator)
                if image not in roots:
                    roots.add(image)
                    queue.append(image)
        check(len(roots) == 240, "Cartan root orbit is incomplete")
        check(all(self.inner(root, root) == 2 for root in roots), "non-root in orbit")
        check(all(tuple(-x for x in root) in roots for root in roots), "missing negative root")
        self.roots = sorted({canonical(root) for root in roots})
        check(len(self.roots) == 120, "incorrect root-line quotient")
        check(all(all(x >= 0 for x in root) for root in self.roots),
              "positive roots have unexpected simple coordinates")
        self.index = {root: i for i, root in enumerate(self.roots)}
        self.labels = [256 | sum((x % 2) << i for i, x in enumerate(root))
                       for root in self.roots]
        self.gram = [[self.inner(a, b) for b in self.roots] for a in self.roots]
        self.full_mask = (1 << 120) - 1
        self.off_masks = [sum(1 << j for j, value in enumerate(row) if value)
                          for row in self.gram]
        self.permutations = []
        for generator in range(8):
            permutation = [self.index[canonical(self.reflect(root, generator))]
                           for root in self.roots]
            check(len(set(permutation)) == 120, "reflection does not permute roots")
            self.permutations.append(permutation)

        doubled_index = {canonical(self.to_doubled(root)): i
                         for i, root in enumerate(self.roots)}
        frame = []
        # Source PR2816 order: all four plus roots, then all four minus roots.
        for sign in (1, -1):
            for pair in range(4):
                vector = [0] * 8
                vector[2 * pair], vector[2 * pair + 1] = 2, 2 * sign
                check(tuple(vector) in doubled_index, "canonical frame root missing")
                frame.append(doubled_index[tuple(vector)])
        self.frame = frame
        self.frame_mask = sum(1 << i for i in frame)
        self.p112_mask = self.full_mask ^ self.frame_mask
        self.hyperplane_outside = [sum(1 << i for i, label in enumerate(self.labels)
                                      if (normal & label).bit_count() % 2)
                                   for normal in range(1, 512)]

    def inner(self, a, b):
        return sum(a[i] * sum(self.cartan[i][j] * b[j] for j in range(8))
                   for i in range(8))

    def reflect(self, vector, generator):
        coefficient = sum(self.cartan[generator][j] * vector[j] for j in range(8))
        result = list(vector)
        result[generator] -= coefficient
        return tuple(result)

    def to_doubled(self, vector):
        return tuple(sum(vector[i] * self.simple_doubled[i][j] for i in range(8))
                     for j in range(8))

    def mask_labels(self, mask):
        result = []
        while mask:
            bit = mask & -mask
            result.append(self.labels[bit.bit_length() - 1])
            mask ^= bit
        return result

    def vector_orbit(self, seed, expected_size):
        seen = {canonical(seed)}
        queue = deque(seen)
        while queue:
            vector = queue.popleft()
            for generator in range(8):
                image = canonical(self.reflect(vector, generator))
                if image not in seen:
                    seen.add(image)
                    queue.append(image)
        check(len(seen) == expected_size, "fundamental-normal Weyl orbit is incomplete")
        norm = self.inner(seed, seed)
        check(all(self.inner(x, x) == norm for x in seen), "normal orbit changes norm")
        check(all(gcd(*x) == 1 for x in seen), "normal orbit contains an imprimitive vector")
        return sorted(seen)

    def plane_orbit(self, seed, expected_size):
        seen = {tuple(sorted(seed))}
        queue = deque(seen)
        while queue:
            plane = queue.popleft()
            for permutation in self.permutations:
                image = tuple(sorted(permutation[i] for i in plane))
                if image not in seen:
                    seen.add(image)
                    queue.append(image)
        check(len(seen) == expected_size, "normal-plane Weyl orbit is incomplete")
        check(all(len(plane) == len(seed) for plane in seen), "normal-plane size changes")
        return sorted(seen)


def check_root_class_bijection(labels, quadratic_values):
    check(len(labels) == 120 and len(set(labels)) == 120,
          "root-class inventory is incomplete or repeated")
    check(all(label & 256 and 0 <= label < 512 for label in labels),
          "root labels have lost their affine coordinate")
    classes = {label ^ 256 for label in labels}
    check(classes == {i for i, value in enumerate(quadratic_values) if value},
          "roots are not exactly the nonsingular quadratic classes")


def quadratic_checks(model):
    values = []
    for value in range(256):
        vector = [(value >> i) & 1 for i in range(8)]
        norm = model.inner(vector, vector)
        check(norm % 2 == 0, "Cartan lattice is not even")
        values.append((norm // 2) % 2)
    check_root_class_bijection(model.labels, values)
    check(sum(1 - 2 * x for x in values) == 16, "quadratic form is not plus type")
    check(binary_rank(sum((model.cartan[i][j] % 2) << j for j in range(8))
                      for i in range(8)) == 8, "quadratic polar form is degenerate")
    for i, row in enumerate(model.gram):
        for j, value in enumerate(row):
            a, b = model.roots[i], model.roots[j]
            polar = sum((a[k] % 2) * (model.cartan[k][l] % 2) * (b[l] % 2)
                        for k in range(8) for l in range(8)) % 2
            check((1 + value) % 2 == (1 + polar) % 2,
                  "label pairing does not match root orthogonality")

    # Walsh transform verifies the Fourier identity used for every affine flat.
    transform = [1 - 2 * x for x in values]
    stride = 1
    while stride < 256:
        for start in range(0, 256, 2 * stride):
            for offset in range(stride):
                a, b = transform[start + offset], transform[start + offset + stride]
                transform[start + offset] = a + b
                transform[start + offset + stride] = a - b
        stride *= 2
    for value in range(256):
        normal = sum((sum(model.cartan[i][j] * ((value >> j) & 1)
                          for j in range(8)) % 2) << i for i in range(8))
        check(transform[normal] == 16 * (1 - 2 * values[value]),
              "quadratic Fourier identity failed")

    # Restriction to a dual space of dimension 1, 2, 3 or 4 is a quadratic polynomial
    # with zero constant. Enumerating these small polynomials is exhaustive;
    # it is not an enumeration or sampling of ambient affine flats.
    minima = {}
    for dimension in (1, 2, 3, 4):
        monomials = [1 << i for i in range(dimension)]
        monomials += [(1 << i) | (1 << j)
                      for i, j in combinations(range(dimension), 2)]
        sums = []
        for coefficients in range(1 << len(monomials)):
            total = 0
            for point in range(1 << dimension):
                q = sum(1 for i, support in enumerate(monomials)
                        if coefficients >> i & 1 and point & support == support) % 2
                total += 1 - 2 * q
            sums.append(total)
        minima[dimension] = min(sums)
    check(minima == {1: 0, 2: -2, 3: -4, 4: -8}, "small quadratic Gauss lower bounds changed")
    cap7 = (64 - (16 // 4) * minima[2]) // 2
    cap6 = (32 - (16 // 8) * minima[3]) // 2
    cap5 = (16 - (16 // 16) * minima[4]) // 2
    cap8 = max(120 - cut.bit_count() for cut in model.hyperplane_outside)
    check(cap8 == (128 - 8 * minima[1]) // 2,
          "dimension-eight hyperplane maximum disagrees with the Fourier bound")
    caps = {"1": 1, "2": 2, "3": 4, "4": 8, "5": cap5, "6": cap6, "7": cap7, "8": cap8}
    check(caps == {"1": 1, "2": 2, "3": 4, "4": 8, "5": 12, "6": 20, "7": 36, "8": 64},
          "full-E8 support-cap bound failed")
    # Attainment controls use coordinate D4/D5 subsets, not norm enumeration.
    for width, weight, count in ((4, 5, 12), (5, 6, 20)):
        subset = [i for i, root in enumerate(model.roots)
                  if all(x == 0 for x in model.to_doubled(root)[width:])]
        check(len(subset) == count, "D4/D5 cap witness has the wrong size")
        check(binary_rank(model.labels[i] for i in subset) == weight,
              "D4/D5 cap witness has the wrong label rank")
    return caps


def parabolic_checks(model):
    large = {}
    counts_by_rank = {}
    for subset in range(256):
        selected = [root for root in model.roots
                    if all(not value or subset >> i & 1
                           for i, value in enumerate(root))]
        rank = subset.bit_count()
        check(integer_rank(selected) == rank, "standard parabolic rank mismatch")
        counts_by_rank.setdefault(rank, Counter())[len(selected)] += 1
        if rank <= 7 and len(selected) >= 28:
            large[(rank, len(selected))] = subset
    expected = {(6, 30), (6, 36), (7, 28), (7, 37), (7, 42), (7, 63)}
    check(set(large) == expected and len(large) == 6,
          "large proper parabolic inventory changed")
    check(max(count for rank, counts in counts_by_rank.items() if rank <= 5
              for count in counts) == 20, "rank<=5 parabolic maximum is not 20")
    for key in expected:
        check(counts_by_rank[key[0]][key[1]] == 1, "large parabolic seed is not unique")
    return large, {"subsets_checked": 256,
                   "large_proper_types": [list(key) for key in sorted(large)]}


EXPECTED_PROFILES = {
    "norm4": [[70, 14, 8, 128], [73, 13, 8, 896], [76, 12, 7, 56]],
    "norm6": [[77, 25, None, 2688], [79, 24, None, 448], [80, 24, None, 224]],
    "norm8": [[84, 28, None, 1024]],
    "a2_plane": [[78, 26, None, 896], [80, 24, None, 224]],
    "a1_squared_plane": [[82, 26, None, 448], [84, 24, None, 2688]],
}


def validate_class_inventory(classes):
    check(set(classes) == set(EXPECTED_PROFILES), "incomplete non-root normal-class inventory")


def normal_filter_checks(model, parabolics):
    summary = {}
    relaxed_pass = False

    def profile(class_name, masks, orbit_size):
        nonlocal relaxed_pass
        counts = Counter()
        for off in masks:
            size = off.bit_count()
            if size > 84:
                continue
            deletions = [(off & outside) for outside in model.hyperplane_outside]
            minimum = min(mask.bit_count() for mask in deletions)
            small = [mask for mask in deletions if mask.bit_count() <= 20]
            if small:
                minimum_rank = min(binary_rank(model.mask_labels(mask)) for mask in small)
                check(minimum_rank >= 7, "a non-root normal passes the kappa<=6 gate")
                relaxed_pass |= minimum_rank == 7
            else:
                minimum_rank = None
                check(minimum > 20, "deletion cardinality gate is incomplete")
            counts[(size, minimum, minimum_rank)] += 1
        profiles = [list(key) + [count] for key, count in sorted(counts.items())]
        check(profiles == EXPECTED_PROFILES[class_name],
              "normal deletion profile differs for " + class_name)
        summary[class_name] = {"orbit_size": orbit_size, "profiles": profiles}

    for norm, root_count, orbit_size in ((2, 63, 120), (4, 42, 1080),
                                         (6, 37, 3360), (8, 28, 8640)):
        subset = parabolics[(7, root_count)]
        omitted = next(i for i in range(8) if not subset >> i & 1)
        seed = tuple(model.inverse[i][omitted] for i in range(8))
        check(model.inner(seed, seed) == norm, "fundamental normal has the wrong norm")
        check(all(sum(model.cartan[i][j] * seed[j] for j in range(8)) == 0
                  for i in range(8) if subset >> i & 1), "normal is not perpendicular")
        orbit = model.vector_orbit(seed, orbit_size)
        if norm == 2:
            check(set(orbit) == set(model.roots), "E7 normals do not give all roots")
            continue
        masks = []
        for vector in orbit:
            functional = [sum(model.cartan[i][j] * vector[j] for j in range(8))
                          for i in range(8)]
            off = sum(1 << i for i, root in enumerate(model.roots)
                      if sum(x * y for x, y in zip(functional, root)))
            masks.append(off & model.p112_mask)
        profile("norm" + str(norm), masks, orbit_size)

    for root_count, class_name, orbit_size, plane_size in (
            (36, "a2_plane", 1120, 3), (30, "a1_squared_plane", 3780, 2)):
        subset = parabolics[(6, root_count)]
        seed = [i for i, root in enumerate(model.roots)
                if all(sum(model.cartan[k][j] * root[j] for j in range(8)) == 0
                       for k in range(8) if subset >> k & 1)]
        check(len(seed) == plane_size and integer_rank(model.roots[i] for i in seed) == 2,
              "rank-six perpendicular plane has the wrong root system")
        planes = model.plane_orbit(seed, orbit_size)
        masks = []
        for plane in planes:
            check(all((model.gram[a][b] != 0) == (plane_size == 3)
                      for a, b in combinations(plane, 2)), "normal-plane root type changed")
            off = 0
            for root in plane:
                off |= model.off_masks[root]
            masks.append(off & model.p112_mask)
        profile(class_name, masks, orbit_size)
    validate_class_inventory(summary)
    check(relaxed_pass, "relaxing the binary rank gate has no positive control")
    return summary


def full_code_checks(model):
    minimum = 8
    for outside in model.hyperplane_outside:
        roots = [root for i, root in enumerate(model.roots) if outside >> i & 1]
        rank = integer_rank(roots)
        minimum = min(minimum, rank)
        check(rank == 8, "a nonzero full codeword can lie in a binary hyperplane")
    # The complement-rank test proves weight9 for every nonzero direction,
    # including directions not represented by finite normal orbits.
    for off in model.off_masks:
        check(binary_rank(model.mask_labels(off)) == 9, "root codeword weight is not 9")
    return {"hyperplanes_checked": 511, "minimum_complement_real_rank": minimum}


def remainder_checks(model):
    expected = Counter({0: 1, 24: 126, 28: 256, 32: 126, 56: 2})
    for i, off in enumerate(model.off_masks):
        remainder = off ^ (1 << i)
        check(remainder.bit_count() == 56, "root remainder has the wrong size")
        check(binary_rank(model.mask_labels(remainder)) == 8, "root remainder rank is not 8")
        check(Counter((remainder & outside).bit_count()
                      for outside in model.hyperplane_outside) == expected,
              "root-remainder cocircuit profile changed")
    return {"directions_checked": 120, "size": 56, "minimum_nonzero_deletion": 24}


def rejection_controls(model):
    rejected = 0

    def expect_failure(operation):
        nonlocal rejected
        try:
            operation()
        except AuditFailure:
            rejected += 1
        else:
            raise AuditFailure("a deliberately invalid control was accepted")

    quadratic_values = [0] * 256
    for label in model.labels:
        quadratic_values[label ^ 256] = 1
    expect_failure(lambda: check_root_class_bijection(model.labels[:-1], quadratic_values))
    expect_failure(lambda: check_root_class_bijection(
        [label & 255 for label in model.labels], quadratic_values))
    expect_failure(lambda: validate_class_inventory(set(EXPECTED_PROFILES) - {"norm8"}))
    expect_failure(lambda: check(binary_rank(model.mask_labels(model.off_masks[0])) <= 8,
                                 "false full-code weight8 claim"))
    frame_remainder = model.off_masks[model.frame[0]] ^ (1 << model.frame[0])
    minimum = min((frame_remainder & outside).bit_count()
                  for outside in model.hyperplane_outside if frame_remainder & outside)
    expect_failure(lambda: check(minimum <= 23, "false remainder erasure threshold"))
    return rejected


def run_audit():
    model = CartanModel()
    check(len(set(model.frame)) == 8, "canonical frame repeats a line")
    check(all(model.gram[a][b] == 0 for a, b in combinations(model.frame, 2)),
          "canonical frame is not orthogonal")
    check(binary_rank(model.labels[i] for i in model.frame) == 4,
          "canonical frame label rank is not 4")
    caps = quadratic_checks(model)
    parabolics, parabolic_summary = parabolic_checks(model)
    full_code = full_code_checks(model)
    remainders = remainder_checks(model)
    normal_filter = normal_filter_checks(model, parabolics)
    return {
        "schema_version": 1,
        "model": {"root_lines": 120, "frame_lines": 8, "frame_label_rank": 4,
                  "quadratic_gauss_sum": 16},
        "full_cap_bounds": caps,
        "full_code": full_code,
        "root_remainders": remainders,
        "parabolics": parabolic_summary,
        "normal_filter": normal_filter,
        "rejection_controls": rejection_controls(model),
    }


if __name__ == "__main__":
    print(json.dumps(run_audit(), sort_keys=True, indent=2))
    print("PASS_E8_D0_GEOMETRY_AUDIT")
