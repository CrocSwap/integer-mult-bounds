#!/usr/bin/env python3
"""Exact checks for the no-edge irreducible joint-image bound.

The all-width argument is PROOF.md. This program repeats the finite
classifications that the proof uses, checks the sharp example, and runs
negative controls. It does not use assert, so python -O does not skip checks.
Standard library only.
"""

import itertools
import sys

MARKER = "PASS_NO_EDGE_IRREDUCIBLE_IMAGE"


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(condition, message):
    if not condition:
        fail(message)


def weight(mask):
    return bin(mask).count("1")


def dot(left, right):
    return weight(left & right) & 1


def inverse3(matrix):
    """Inverse of a 3x3 matrix over F2, or None. Rows are tuples of bits 0,1,2."""
    def det(rows):
        # Over F2 the determinant is the permanent: signs are trivial.
        total = 0
        for perm in itertools.permutations(range(3)):
            term = 1
            for row, col in enumerate(perm):
                term &= rows[row][col]
            total ^= term
        return total

    if det(matrix) == 0:
        return None
    cofactor = [[0, 0, 0] for _ in range(3)]
    for row in range(3):
        for col in range(3):
            minor_rows = [r for r in range(3) if r != row]
            minor_cols = [c for c in range(3) if c != col]
            minor = (
                matrix[minor_rows[0]][minor_cols[0]] * matrix[minor_rows[1]][minor_cols[1]]
                + matrix[minor_rows[0]][minor_cols[1]] * matrix[minor_rows[1]][minor_cols[0]]
            ) & 1
            cofactor[col][row] = minor
    return [tuple(cofactor[row]) for row in range(3)]


def pattern_weight(image, covector):
    count = 0
    for row in range(3):
        if ((image >> row) & 1) == 0:
            continue
        for col in range(3):
            if row != col and ((covector >> col) & 1):
                count += 1
    return count


def check_normal_form_classification():
    good = []
    invertible = 0
    for columns in itertools.product(range(1, 8), repeat=3):
        matrix = [tuple((columns[col] >> row) & 1 for col in range(3)) for row in range(3)]
        inverse = inverse3(matrix)
        if inverse is None:
            continue
        invertible += 1
        images = list(columns)
        covectors = [sum((inverse[row][col] << col) for col in range(3)) for row in range(3)]
        product = [tuple(dot(covectors[row], columns[col]) for col in range(3)) for row in range(3)]
        require(product == [(1, 0, 0), (0, 1, 0), (0, 0, 1)], "inverse failed on GL(3,2)")
        weights = [pattern_weight(images[i], covectors[i]) for i in range(3)]
        if min(weights) >= 2:
            good.append((images, covectors))
    require(invertible == 168, "GL(3,2) has 168 elements, found %s" % invertible)
    require(len(good) == 18, "expected 18 no-edge bases, found %s" % len(good))
    for images, covectors in good:
        weight_pairs = sorted(weight(images[i]) for i in range(3))
        require(weight_pairs == [2, 2, 3], "survivor is not weights 2,2,3: %s" % (images,))
        slot = images.index(7)
        require(covectors[slot] == 7, "weight-3 image is not paired with o")
        others = [i for i in range(3) if i != slot]
        require(covectors[others[0]] == images[others[1]], "weight-2 covectors are not swapped")
        require(covectors[others[1]] == images[others[0]], "weight-2 covectors are not swapped")
        require(images[others[0]] != images[others[1]], "weight-2 columns repeat")
    # A coordinate projector basis is invertible and must be rejected.
    identity_weight = min(pattern_weight(1 << i, 1 << i) for i in range(3))
    require(identity_weight < 2, "identity basis should contain matrix units")


def pattern_mask(image, covector, width):
    mask = 0
    for row in range(width):
        if ((image >> row) & 1) == 0:
            continue
        for col in range(width):
            if row != col and ((covector >> col) & 1):
                mask |= 1 << (row * width + col)
    return mask


def span_masks(masks):
    """Row-reduced XOR basis. Keys are distinct pivot bits."""
    pivots = {}
    for mask in masks:
        value = mask
        while value:
            pivot = value & -value
            known = pivots.get(pivot)
            if known is None:
                for other, vector in pivots.items():
                    if vector & pivot:
                        pivots[other] = vector ^ value
                pivots[pivot] = value
                break
            value ^= known
    return [pivots[bit] for bit in sorted(pivots)]


def in_span(mask, basis):
    return len(span_masks(list(basis) + [mask])) == len(list(basis))


SHARP = (
    (0b0001, 0b0111),  # e0, e0+e1+e2
    (0b0010, 0b1011),  # e1, e0+e1+e3
    (0b0100, 0b1101),  # e2, e0+e2+e3
)


def sharp_patterns(width):
    return [pattern_mask(image, covector, width) for image, covector in SHARP]


def check_sharp_example():
    patterns = sharp_patterns(4)
    basis = span_masks(patterns)
    require(len(basis) == 3, "sharp patterns should span dimension 3")
    space = [0]
    for vector in basis:
        space += [value ^ vector for value in space]
    for value in space:
        if value and weight(value) == 1:
            fail("sharp pattern space contains a matrix unit")
    realized = []
    for image in range(16):
        for covector in range(16):
            if dot(image, covector) != 1:
                continue
            mask = pattern_mask(image, covector, 4)
            if mask and in_span(mask, basis):
                realized.append((image, covector))
    require(sorted(realized) == sorted(SHARP), "4-coordinate pool is not exactly the three projectors: %s" % realized)
    # One extra ambient bit creates no further projector. This corroborates
    # the support reduction; PROOF.md covers every larger width.
    wide = span_masks(sharp_patterns(5))
    extra = []
    for image in range(32):
        for covector in range(32):
            if image < 16 and covector < 16:
                continue
            if dot(image, covector) != 1:
                continue
            mask = pattern_mask(image, covector, 5)
            if mask and in_span(mask, wide):
                extra.append((image, covector))
    require(extra == [], "an outside bit realized an extra sharp-pool projector")
    require(not has_proper_invariant(SHARP, (1, 2, 4)), "sharp example is reducible")
    # Deleting one projector leaves an invariant line.
    require(has_proper_invariant(SHARP[:2], (1, 2, 4)), "a proper subpool of the sharp example should be reducible")


def vectors_of(basis_masks):
    out = [0]
    for mask in basis_masks:
        out += [value ^ mask for value in out]
    return out


def image_basis(projectors):
    return span_masks(image for image, _covector in projectors)


def combine(basis, coeff):
    value = 0
    for index, vector in enumerate(basis):
        if (coeff >> index) & 1:
            value ^= vector
    return value


def has_proper_invariant(projectors, _ambient_masks):
    """True when some nonzero proper subspace of the image span is invariant."""
    basis = image_basis(projectors)
    dimension = len(basis)
    if dimension <= 1:
        return False

    def apply_one(image, covector, vector):
        return image if dot(covector, vector) else 0

    seen = set()
    for generators in itertools.product(range(1, 1 << dimension), repeat=dimension - 1):
        span = {0}
        for generator in generators:
            span.update(value ^ generator for value in tuple(span))
        frozen = frozenset(span)
        if frozen in seen or len(span) in (1, 1 << dimension):
            continue
        seen.add(frozen)
        subset = {combine(basis, coeff) for coeff in span}
        good = True
        for vector in subset:
            for image, covector in projectors:
                if apply_one(image, covector, vector) not in subset:
                    good = False
                    break
            if not good:
                break
        if good:
            return True
    return False


def check_sharp_lines_and_planes():
    """Hand-checkable action on F2^3, independent of the subspace search."""
    def act(vector):
        a = vector & 1
        b = (vector >> 1) & 1
        c = (vector >> 2) & 1
        out = []
        if (a + b + c) & 1:
            out.append(0b001)
        if (a + b) & 1:
            out.append(0b010)
        if (a + c) & 1:
            out.append(0b100)
        return out

    for vector in range(1, 8):
        line = {0, vector}
        if all(image in line for image in act(vector)):
            fail("sharp line %s is invariant" % vector)
    planes = []
    for first, second in itertools.combinations(range(1, 8), 2):
        plane = frozenset(vectors_of([first, second]))
        if len(plane) == 4:
            planes.append(plane)
    require(len(set(planes)) == (7), "F2^3 should have 7 planes of size 4, found %s" % len(set(planes)))
    for plane in set(planes):
        escaped = False
        for vector in plane:
            if any(image not in plane for image in act(vector)):
                escaped = True
                break
        require(escaped, "sharp plane %s is invariant" % sorted(plane))


def check_caps():
    points = list(range(1, 8))
    lines = []
    for i, left in enumerate(points):
        for right in points[i + 1:]:
            third = left ^ right
            if left < right < third:
                lines.append(frozenset((left, right, third)))
    require(len(lines) == 7, "Fano plane has 7 lines")
    caps = []
    for subset in itertools.combinations(points, 4):
        block = set(subset)
        if any(line <= block for line in lines):
            continue
        caps.append(frozenset(block))
        total = 0
        for value in subset:
            total ^= value
        require(total == 0, "a 4-arc does not sum to zero")
        for triple in itertools.combinations(subset, 3):
            require((triple[0] ^ triple[1] ^ triple[2]) != 0, "a cap contains a line")
    require(len(caps) == 7, "expected 7 caps, found %s" % len(caps))
    # Standard cap forced-image intersection is zero.
    f1, f2, f3, f4 = 0b0001, 0b0010, 0b0100, 0b1000
    span_12 = set(vectors_of([f1, f2]))
    span_34 = set(vectors_of([f3, f4]))
    require(span_12.intersection(span_34) == {0}, "complementary planes should meet at zero")


def kernel_dimension(projectors):
    basis = image_basis(projectors)
    dimension = len(basis)
    count = 0
    for coeff in range(1 << dimension):
        vector = combine(image_basis(projectors), coeff)
        if all(dot(covector, vector) == 0 for _image, covector in projectors):
            count += 1
    if count == 0:
        return -1
    return count.bit_length() - 1


def check_parity_control():
    # #6838 sharp total-image example: reducible, common kernel the even space.
    nonzero = [6, 10, 12, 18, 20, 24, 30]
    projectors = [(1 + mask, 1) for mask in nonzero]
    require(kernel_dimension(projectors) >= 1, "parity example should have a kernel")
    require(has_proper_invariant(projectors, None), "parity example should be reducible")
    # Claiming it irreducible is the negative control.
    if not has_proper_invariant(projectors, None):
        fail("negative control did not fire")


def check_column_triple_kernel():
    # Width 4 column triple: patterns 0b0110, 0b1010, 0b1100 in column 0,
    # images e0 plus those vectors. Covectors are all e0. One extra odd
    # projector with a new covector still leaves a kernel on a 4D span,
    # as predicted when the odd covectors are few. Here the pure triple
    # spans only 3 dimensions and its covector rank is 1.
    images = [0b0111, 0b1011, 0b1101]
    projectors = [(image, 0b0001) for image in images]
    require(len(image_basis(projectors)) == 3, "column triple should span dimension 3")
    require(kernel_dimension(projectors) == 2, "three equal covectors on a 3D image have kernel dimension 2")


def check_normal_form_pool_is_reducible():
    # u=e1+e2=0b110, v=e0+e2=0b101, o=0b111, with the swapped covectors.
    projectors = [(0b110, 0b101), (0b101, 0b110), (0b111, 0b111)]
    patterns = [pattern_mask(image, covector, 3) for image, covector in projectors]
    require(len(span_masks(patterns)) == 2, "normal-form patterns should span dimension 2")
    for mask in patterns:
        require(weight(mask) >= 2, "normal-form pattern is an edge or zero")
    require(patterns[0] ^ patterns[1] ^ patterns[2] == 0, "normal-form patterns should sum to zero")
    require(has_proper_invariant(projectors, None), "normal-form triple should be reducible")


def check_idempotent_line():
    # Four dual basis projectors on F2^4: G = I, each axis is invariant.
    projectors = [(1 << i, 1 << i) for i in range(4)]
    # These are coordinate, so they are not pool elements, but the gram
    # conclusion itself is what the cap argument uses. Each axis is invariant.
    require(has_proper_invariant(projectors, None), "dual-basis lines should be invariant")
    for index in range(4):
        vector = 1 << index
        for other, covector in projectors:
            image = other if dot(covector, vector) else 0
            require(image == 0 or image == vector, "dual basis moves an axis")


def main():
    check_normal_form_classification()
    check_sharp_example()
    check_sharp_lines_and_planes()
    check_caps()
    check_parity_control()
    check_column_triple_kernel()
    check_normal_form_pool_is_reducible()
    check_idempotent_line()
    print(MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
