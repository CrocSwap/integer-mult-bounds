#!/usr/bin/env python3
"""Exact split of the c=1 sign characters moved by g and t.

The census is exhaustive inside the signed coordinate permutations of the
pinned 8-by-112 query. Checks are explicit, so Python -O does not skip them.
"""

import hashlib
import itertools
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
INTERFACE = (
    ROOT
    / "research/centre-polynomial-cache-limits/frozen/work"
    / "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json"
)
INTERFACE_SHA256 = (
    "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
)
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
T_INV = (0, 5, 6, 3, 4, 1, 2, 7)
T_EPS = (1, 1, 1, -1, 1, 1, 1, -1)
# sigma = (0 4 3 7)(5 6), stored inv = sigma^{-1}, all output signs +1.
S_INV = (7, 1, 2, 4, 0, 6, 5, 3)
S_EPS = (1, 1, 1, 1, 1, 1, 1, 1)
# (4 7)(5 6), all signs +1. Real split 264+168 on the 432-characters it preserves.
U432_INV = (0, 1, 2, 3, 7, 6, 5, 4)
U432_EPS = (1, 1, 1, 1, 1, 1, 1, 1)
# (1 2)(5 6) with signs on coordinates 0 and 3. Trace 0 on a 192-character.
U192_INV = (0, 2, 1, 3, 4, 6, 5, 7)
U192_EPS = (-1, 1, 1, -1, 1, 1, 1, 1)
INVOLUTION_TRACES = {
    432: {96: 96, -96: 96, 432: 16, -432: 16},
    192: {0: 112, 48: 32, -48: 32, 192: 16, -192: 16},
    80: {32: 96, -32: 96, 80: 16, -80: 16},
}
# Eigenvalue order is 1, i, -1, -i.
ORDER4_MULTIPLICITIES = {
    432: (144, 84, 120, 84),
    192: (48, 48, 48, 48),
    80: (32, 12, 24, 12),
}
# Multiplicity tuples use roots exp(2 pi i k / order) in order k = 0, 1, ..., order-1.
PRESERVER_PATTERNS = {
    432: {
        (432,): 1,
        (432, 0): 15,
        (0, 432): 16,
        (264, 168): 96,
        (168, 264): 96,
        (144, 84, 120, 84): 96,
        (120, 84, 144, 84): 96,
        (264, 0, 168, 0): 48,
        (168, 0, 264, 0): 48,
        (160, 136, 136): 32,
        (0, 136, 0, 160, 0, 136): 128,
        (160, 0, 136, 0, 136, 0): 96,
    },
    192: {
        (192,): 1,
        (192, 0): 15,
        (0, 192): 16,
        (96, 96): 112,
        (120, 72): 32,
        (72, 120): 32,
        (48, 48, 48, 48): 128,
        (0, 96, 0, 96): 64,
        (96, 0, 96, 0): 48,
        (120, 0, 72, 0): 32,
        (72, 0, 120, 0): 32,
    },
    80: {
        (80,): 1,
        (80, 0): 15,
        (0, 80): 16,
        (56, 24): 96,
        (24, 56): 96,
        (32, 12, 24, 12): 96,
        (24, 12, 32, 12): 96,
        (24, 0, 56, 0): 48,
        (56, 0, 24, 0): 48,
        (32, 24, 24): 32,
        (0, 24, 0, 32, 0, 24): 128,
        (32, 0, 24, 0, 24, 0): 96,
    },
}


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_file(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def norm(vector):
    for entry in vector:
        if entry < 0:
            return tuple(-item for item in vector)
        if entry > 0:
            return vector
    return vector


def rank_solve(vectors, target=None):
    width = len(vectors)
    matrix = [[(vector >> row) & 1 for vector in vectors] for row in range(9)]
    image = None if target is None else [(target >> row) & 1 for row in range(9)]
    pivot_at = [-1] * 9
    rank = 0
    for col in range(width):
        pivot = next((row for row in range(rank, 9) if matrix[row][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        if image is not None:
            image[rank], image[pivot] = image[pivot], image[rank]
        for row in range(9):
            if row != rank and matrix[row][col]:
                matrix[row] = [left ^ right for left, right in zip(matrix[row], matrix[rank])]
                if image is not None:
                    image[row] ^= image[rank]
        pivot_at[rank] = col
        rank += 1
        if rank == 9:
            break
    if target is None:
        return rank
    if any(image[row] for row in range(rank, 9)):
        return None
    coef = [0] * width
    for row in range(rank):
        coef[pivot_at[row]] = image[row]
    return tuple(coef)


def load_query():
    if sha256_file(INTERFACE) != INTERFACE_SHA256:
        fail("INTERFACE.json SHA256 does not match the pinned query")
    data = json.loads(INTERFACE.read_text())
    rows = data["R"]
    ports = [int(port) for port in data["ports"]]
    if len(rows) != 8 or len(ports) != 112 or len(set(ports)) != 112:
        fail("query shape is not an 8-by-112 matrix with distinct ports")
    columns = [
        tuple(int(rows[i].get(str(j), "0")) for i in range(8)) for j in range(112)
    ]
    return columns, ports


def prepare(columns, ports):
    gram = [[0] * 8 for _ in range(8)]
    for column in columns:
        for i in range(8):
            for k in range(8):
                gram[i][k] += column[i] * column[k]
    expect(
        all(gram[i][k] == (56 if i == k else 0) for i in range(8) for k in range(8)),
        "RR^T is not 56 I",
    )
    expect(all(bin(port).count("1") % 2 == 1 for port in ports), "a port label has even parity")
    expect(all(sum(entry != 0 for entry in column) == 4 for column in columns), "a column is not weight 4")
    port_of = {norm(column): port for column, port in zip(columns, ports)}
    expect(len(port_of) == 112, "normalized columns are not unique")
    basis = []
    for port in ports:
        if rank_solve(basis + [port]) == len(basis) + 1:
            basis.append(port)
        if len(basis) == 9:
            break
    expect(len(basis) == 9, "the 112 ports do not span F2^9")
    coords = {address: rank_solve(basis, address) for address in range(512)}
    basis_cols = [next(norm(column) for column, port in zip(columns, ports) if port == vector) for vector in basis]
    dots = [bin(basis[i] & basis[j]).count("1") & 1 for i in range(9) for j in range(i, 9)]
    return port_of, basis, coords, basis_cols, dots


def tetrads(columns):
    grouped = {}
    for column in columns:
        support = tuple(index for index, entry in enumerate(column) if entry)
        grouped.setdefault(support, []).append(norm(column))
    expect(len(grouped) == 14, "the query does not have 14 tetrads")
    for support, members in grouped.items():
        expect(len(support) == 4 and len(members) == 8, "a tetrad does not have eight columns")
        signs = set()
        for member in members:
            expect(member[support[0]] == 1, "a normalized column does not start positive on its tetrad")
            signs.add(tuple(member[index] for index in support[1:]))
        expect(len(signs) == 8, "a tetrad misses a projective sign pattern")
    return set(frozenset(support) for support in grouped)


def design_autos(supports):
    autos = []
    for perm in itertools.permutations(range(8)):
        if all(frozenset(perm[index] for index in block) in supports for block in supports):
            inv = [0] * 8
            for index, image in enumerate(perm):
                inv[image] = index
            autos.append(tuple(inv))
    expect(len(autos) == 1344, "the tetrad automorphism group does not have order 1344")
    return autos


def dot(left, right):
    return bin(left & right).count("1") & 1


def build_stabilizer(autos, columns, ports, port_of, coords, basis_cols, dots):
    """Every tetrad automorphism and every sign pattern preserves projective columns.

    A signed permutation can meet every column only when its underlying
    permutation preserves supports, because signs do not create or destroy
    zeros. The S_8 scan above found those permutations. Each tetrad carries
    every projective sign pattern, so every sign pattern on such a permutation
    lands on a column. The residual stabilizer R is the subset whose induced
    port map is F_2-linear, preserves the standard dot product, and fixes
    sector 1. Candidates whose basis image already moves sector 1 are excluded;
    a linear map is determined by that basis image.
    """
    stabilizer = []
    column_failures = 0
    form_failures = 0
    linear_failures = 0
    for inv in autos:
        for mask in range(256):
            eps = tuple(-1 if (mask >> bit) & 1 else 1 for bit in range(8))
            images = []
            missing = False
            for column in basis_cols:
                image = tuple(eps[index] * column[inv[index]] for index in range(8))
                port = port_of.get(norm(image))
                if port is None:
                    missing = True
                    break
                images.append(port)
            if missing:
                column_failures += 1
                continue
            cursor = 0
            formed = True
            for left in range(9):
                for right in range(left, 9):
                    if dot(images[left], images[right]) != dots[cursor]:
                        formed = False
                    cursor += 1
            if not formed:
                form_failures += 1
                continue
            predicted_sector = 0
            for index, flag in enumerate(coords[1]):
                if flag:
                    predicted_sector ^= images[index]
            if predicted_sector != 1:
                continue
            linear = True
            for column, port in zip(columns, ports):
                image = tuple(eps[index] * column[inv[index]] for index in range(8))
                target = port_of[norm(image)]
                predicted = 0
                for index, flag in enumerate(coords[port]):
                    if flag:
                        predicted ^= images[index]
                if predicted != target:
                    linear = False
                    break
            if not linear:
                linear_failures += 1
                continue
            matrix = []
            for bit in range(9):
                image = 0
                for index, flag in enumerate(coords[1 << bit]):
                    if flag:
                        image ^= images[index]
                matrix.append(image)
            stabilizer.append((inv, eps, tuple(matrix)))
    expect(column_failures == 0, "a tetrad automorphism failed to hit a basis column")
    expect(form_failures == 0, "a column-preserving candidate broke the dot product")
    expect(linear_failures == 0, "a sector-1 basis map failed to be linear on all ports")
    expect(len(stabilizer) == 3072, "the c=1 signed stabilizer does not have order 3072")
    return stabilizer


def apply_matrix(matrix, address):
    image = 0
    for bit in range(9):
        if (address >> bit) & 1:
            image ^= matrix[bit]
    return image


def nullity(matrix):
    rows = [
        [((matrix[col] >> row) & 1) ^ (1 if row == col else 0) for col in range(9)]
        for row in range(9)
    ]
    rank = 0
    for col in range(9):
        pivot = next((row for row in range(rank, 9) if rows[row][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(9):
            if row != rank and rows[row][col]:
                rows[row] = [left ^ right for left, right in zip(rows[row], rows[rank])]
        rank += 1
    return 9 - rank


def block_trace(inv, eps, matrix):
    fixed = sum(eps[index] for index in range(8) if inv[index] == index)
    return fixed * (1 << nullity(matrix))


def compose_key(left, right):
    inv = tuple(right[0][left[0][index]] for index in range(8))
    eps = tuple(left[1][index] * right[1][left[0][index]] for index in range(8))
    return inv, eps


def inverse_key(op):
    sigma = [0] * 8
    for index, image in enumerate(op[0]):
        sigma[image] = index
    eps = tuple(op[1][sigma[index]] for index in range(8))
    return tuple(sigma), eps


def mask_of(eps):
    return sum(1 << bit for bit in range(7) if eps[bit + 1] == -1)


def character_model(group):
    basis = []
    for mask in [mask_of(element[1]) for element in group]:
        reduced = mask
        for vector in basis:
            pivot = vector & -vector
            if reduced & pivot:
                reduced ^= vector
        if reduced:
            pivot = reduced & -reduced
            basis = [vector ^ reduced if vector & pivot else vector for vector in basis]
            basis.append(reduced)

    def coordinates(mask):
        reduced = mask
        coef = []
        for vector in basis:
            pivot = vector & -vector
            bit = 1 if reduced & pivot else 0
            coef.append(bit)
            if bit:
                reduced ^= vector
        if reduced:
            fail("the sign stabilizer is not elementary abelian")
        return coef

    def value(chi, mask):
        sign = 1
        for index, bit in enumerate(coordinates(mask)):
            if bit and (chi >> index) & 1:
                sign = -sign
        return sign

    dims = []
    order = len(group)
    for chi in range(1 << len(basis)):
        total = 0
        for element in group:
            total += value(chi, mask_of(element[1])) * element[3]
        if total % order:
            fail("a character trace is not divisible by the stabilizer order")
        dims.append(total // order)
    return dims, value


def index_group(stabilizer):
    indexed = []
    lookup = {}
    for inv, eps, matrix in stabilizer:
        trace = block_trace(inv, eps, matrix)
        lookup[(inv, eps)] = len(indexed)
        indexed.append((inv, eps, matrix, trace))
    expect(len(lookup) == len(indexed), "two stabilizer elements share a signed permutation")
    return indexed, lookup


def require(lookup, inv, eps):
    key = (inv, eps)
    if key not in lookup:
        fail("a required signed permutation is not in the c=1 stabilizer")
    return lookup[key]


def eigenvalue_pattern(traces):
    order = len(traces)
    if order == 1:
        return (traces[0],)
    if order == 2:
        identity, first = traces
        if (identity + first) % 2 or (identity - first) % 2:
            fail("an involution character trace is not even")
        return ((identity + first) // 2, (identity - first) // 2)
    if order == 3:
        identity, first, square = traces
        if first != square:
            fail("an order-3 character trace is not real")
        if (identity + 2 * first) % 3 or (identity - first) % 3:
            fail("an order-3 character trace is not divisible by 3")
        primitive = (identity - first) // 3
        return ((identity + 2 * first) // 3, primitive, primitive)
    if order == 4:
        return multiplicities(traces)
    if order == 6:
        identity, first, square, cube, fourth, fifth = traces
        if first != fifth or square != fourth:
            fail("an order-6 character trace is not real")
        total = identity + 2 * first + 2 * square + cube
        negative = identity - 2 * first + 2 * square - cube
        primitive = identity + first - square - cube
        if total % 6 or negative % 6 or primitive % 6:
            fail("an order-6 character trace is not divisible by 6")
        one = total // 6
        minus = negative // 6
        root = primitive // 6
        middle = identity - one - minus - 2 * root
        if middle % 2:
            fail("an order-6 multiplicity is not an integer")
        middle //= 2
        return (one, root, middle, minus, middle, root)
    fail("a residual permutation has order outside 1, 2, 3, 4 and 6")


def multiplicities(traces):
    identity, first, square, cube = traces
    for numerator in (
        identity + first + square + cube,
        identity - first + square - cube,
        identity - square,
        cube - first,
    ):
        if numerator % 4:
            fail("an order-4 character trace is not divisible by 4")
    if first != cube:
        fail("the multiplicity of i is not a rational integer")
    half = (identity - square) // 4
    return (
        (identity + first + square + cube) // 4,
        half,
        (identity - first + square - cube) // 4,
        half,
    )


def main():
    columns, ports = load_query()
    port_of, basis, coords, basis_cols, dots = prepare(columns, ports)
    supports = tetrads(columns)
    autos = design_autos(supports)
    raw = build_stabilizer(autos, columns, ports, port_of, coords, basis_cols, dots)
    group, lookup = index_group(raw)
    identity = require(lookup, tuple(range(8)), (1,) * 8)
    expect(group[identity][3] == 4096, "the identity trace is not 4096")
    expect(apply_matrix(group[identity][2], 1) == 1, "the identity moves sector 1")

    for index, element in enumerate(group):
        inv, eps = inverse_key(element)
        inverse = lookup.get((inv, eps))
        if inverse is None:
            fail("the c=1 stabilizer is not closed under inversion")
        composed = compose_key(element, group[inverse])
        if composed != (group[identity][0], group[identity][1]):
            fail("a stabilizer element does not invert to the identity")
        # The matrix of an inverse is the inverse matrix.
        original = element[2]
        inverted = group[inverse][2]
        for vector in basis:
            if apply_matrix(inverted, apply_matrix(original, vector)) != vector:
                fail("the stored label map does not invert")

    for left in group:
        for right in group:
            if compose_key(left, right) not in lookup:
                fail("the c=1 stabilizer is not closed under composition")

    first = require(lookup, G_INV, G_EPS)
    second = require(lookup, T_INV, T_EPS)
    splitter = require(lookup, S_INV, S_EPS)
    expect(compose_key(group[first], group[first]) == (group[identity][0], group[identity][1]), "g is not an involution")
    expect(compose_key(group[second], group[second]) == (group[identity][0], group[identity][1]), "t is not an involution")
    expect(compose_key(group[first], group[second]) == compose_key(group[second], group[first]), "g and t do not commute")
    expect(apply_matrix(group[first][2], 3) == 343, "g does not send sector 3 to 343")
    expect(apply_matrix(group[second][2], 3) == 3, "t does not preserve sector 3")
    expect(apply_matrix(group[first][2], 128) == 128 and apply_matrix(group[second][2], 128) == 128, "g or t moves sector 128")

    square = lookup[compose_key(group[splitter], group[splitter])]
    cube = lookup[compose_key(group[square], group[splitter])]
    fourth = lookup[compose_key(group[cube], group[splitter])]
    expect(fourth == identity and square != identity, "s does not have order 4")

    pure = [element for element in group if element[0] == tuple(range(8))]
    expect(len(pure) == 32, "the pure sign subgroup fixing sector 1 does not have order 32")
    signs = [element for element in pure if element[1][0] == 1]
    expect(len(signs) == 16, "the positive coordinate-0 sign stabilizer does not have order 16")
    dims, value = character_model(signs)
    expect(sum(dims) == 4096 and all(dim > 0 for dim in dims), "character dimensions do not cover the block")
    histogram = {}
    for dim in dims:
        histogram[dim] = histogram.get(dim, 0) + 1
    expect(histogram == {864: 1, 432: 4, 192: 6, 80: 4, 32: 1}, "the c=1 character histogram changed")
    expect(value(0, mask_of(signs[0][1])) == 1, "character 0 is not trivial on the identity")
    for element in signs:
        expect(value(0, mask_of(element[1])) == 1, "character 0 is not the trivial character")

    def conj_sign(actor_index, sign_element):
        # s^{-1} h s, with the stored composition applying the right factor first.
        inverse = lookup[inverse_key(group[actor_index])]
        half_key = compose_key(sign_element, group[actor_index])
        half = lookup.get(half_key)
        if half is None:
            fail("a sign conjugate left the c=1 stabilizer")
        image = lookup.get(compose_key(group[inverse], group[half]))
        if image is None:
            fail("a sign conjugate left the c=1 stabilizer")
        return image

    for actor in range(len(group)):
        for element in signs:
            image = conj_sign(actor, element)
            if group[image][0] != tuple(range(8)) or group[image][1][0] != 1:
                fail("the c=1 stabilizer does not normalize the sign stabilizer")

    sign_masks = [mask_of(element[1]) for element in signs]

    def image_character(actor_index, chi):
        target = []
        for element in signs:
            image = conj_sign(actor_index, element)
            target.append(value(chi, mask_of(group[image][1])))
        for candidate in range(16):
            if all(value(candidate, sign_masks[index]) == target[index] for index in range(16)):
                return candidate
        fail("a conjugate character is not a character of the sign stabilizer")

    def character_trace(actor_index, chi):
        total = 0
        for element in signs:
            product = lookup[compose_key(group[actor_index], element)]
            total += value(chi, mask_of(element[1])) * group[product][3]
        if total % 16:
            fail("a moved-character trace is not an integer")
        return total // 16

    def preserves(actor_index, chi):
        return image_character(actor_index, chi) == chi

    moved = []
    for chi, dim in enumerate(dims):
        fixed = preserves(first, chi) and preserves(second, chi)
        if dim in (864, 32):
            expect(fixed, "g and t do not preserve the predecessor's fixed characters")
        else:
            expect(not fixed, "g and t preserve a character they were recorded as moving")
            moved.append(chi)
    expect(len(moved) == 14, "the moved c=1 characters are not exactly the fourteen non-fixed ones")

    def orbit(generators, chi):
        seen = {chi}
        stack = [chi]
        while stack:
            current = stack.pop()
            for actor in generators:
                image = image_character(actor, current)
                if image not in seen:
                    seen.add(image)
                    stack.append(image)
        return seen

    pair_orbits = []
    seen = set()
    for chi in moved:
        if chi in seen:
            continue
        current = orbit((first, second), chi)
        seen |= current
        pair_orbits.append(sorted(current))
    pair_dims = [tuple(dims[chi] for chi in current) for current in pair_orbits]
    expect(sorted(pair_dims) == [(80, 80, 80, 80), (192, 192), (192, 192), (192, 192), (432, 432, 432, 432)],
           "the g,t orbits of moved characters changed")

    for dimension in (432, 192, 80):
        members = [chi for chi, dim in enumerate(dims) if dim == dimension]
        seen = set()
        stack = [members[0]]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            for actor in range(len(group)):
                image = image_character(actor, current)
                if image not in seen:
                    stack.append(image)
        expect(seen == set(members), "the residual stabilizer does not act transitively on a moved dimension")

    powers = (identity, splitter, square, cube)
    preserved_by_s = {dimension: [] for dimension in (432, 192, 80)}
    for chi in moved:
        if not preserves(splitter, chi):
            continue
        traces = [character_trace(power, chi) for power in powers]
        found = multiplicities(traces)
        expect(found == ORDER4_MULTIPLICITIES[dims[chi]], "the order-4 splitter has an unexpected eigenvalue pattern")
        preserved_by_s[dims[chi]].append(chi)
    expect([len(preserved_by_s[dimension]) for dimension in (432, 192, 80)] == [2, 2, 2],
           "s does not preserve two characters of each moved dimension")

    for dimension, members in preserved_by_s.items():
        for chi in members:
            # Every residual permutation that preserves the character and commutes
            # with s acts by a scalar fourth root on each complex eigenspace.
            centralizer = []
            for actor in range(len(group)):
                if not preserves(actor, chi):
                    continue
                if compose_key(group[splitter], group[actor]) != compose_key(group[actor], group[splitter]):
                    continue
                centralizer.append(actor)
            expect(len(centralizer) == 64, "the commuting residual stabilizer of s does not have order 64")
            target = ORDER4_MULTIPLICITIES[dimension]
            for actor in centralizer:
                samples = []
                current = actor
                for _ in range(4):
                    samples.append(character_trace(current, chi))
                    current = lookup[compose_key(group[splitter], group[current])]
                identity_trace, after_s, after_square, after_cube = samples
                numerators = (
                    identity_trace + after_s + after_square + after_cube,
                    identity_trace - after_square,
                    after_cube - after_s,
                    identity_trace - after_s + after_square - after_cube,
                )
                if any(numerator % 4 for numerator in numerators):
                    fail("a centralizer trace is not divisible by 4")
                eigenvalue_one = numerators[0] // 4
                imag_pair = (numerators[1] // 4, numerators[2] // 4)
                eigenvalue_minus = numerators[3] // 4
                if abs(eigenvalue_one) != target[0] or abs(eigenvalue_minus) != target[2]:
                    fail("a commuting residual permutation is not scalar on a real eigenspace")
                if imag_pair[0] != 0 and imag_pair[1] != 0:
                    fail("a commuting residual trace is not a fourth-root multiple of the multiplicity")
                if abs(imag_pair[0]) + abs(imag_pair[1]) != target[1]:
                    fail("a commuting residual permutation is not scalar on the i-eigenspace")

    for chi in moved:
        counts = {}
        dimension = dims[chi]
        for actor, element in enumerate(group):
            square_key = compose_key(element, element)
            if square_key != (group[identity][0], group[identity][1]):
                continue
            if not preserves(actor, chi):
                continue
            trace = character_trace(actor, chi)
            counts[trace] = counts.get(trace, 0) + 1
        expect(counts == INVOLUTION_TRACES[dimension], "the preserving-involution traces changed")
    expect((432 + 96) // 2 == 264 and (432 - 96) // 2 == 168, "the 432 involution split is not 264+168")
    expect((192 // 2) == 96 and (192 + 48) // 2 == 120 and (192 - 48) // 2 == 72, "the 192 involution splits changed")
    expect((80 + 32) // 2 == 56 and (80 - 32) // 2 == 24, "the 80 involution split is not 56+24")

    for dimension in (432, 192, 80):
        chi = preserved_by_s[dimension][0]
        patterns = {}
        preservers = 0
        for actor in range(len(group)):
            if not preserves(actor, chi):
                continue
            preservers += 1
            current = identity
            power_traces = []
            while True:
                power_traces.append(character_trace(current, chi))
                current = lookup[compose_key(group[actor], group[current])]
                if current == identity:
                    break
                if len(power_traces) > 6:
                    fail("a character preserver has order greater than 6")
            pattern = eigenvalue_pattern(power_traces)
            if sum(pattern) != dimension:
                fail("eigenvalue multiplicities do not cover a moved character")
            patterns[pattern] = patterns.get(pattern, 0) + 1
        if patterns != PRESERVER_PATTERNS[dimension]:
            fail("preserver eigenvalue patterns for dimension " + str(dimension) + " are " + str(patterns))
        expect(preservers == sum(PRESERVER_PATTERNS[dimension].values()),
               "the preserver count does not match the pattern census")

    for dimension in (432, 192, 80):
        source = preserved_by_s[dimension][0]
        source_traces = [character_trace(power, source) for power in powers]
        for chi in [index for index, dim in enumerate(dims) if dim == dimension]:
            carrier = None
            for actor in range(len(group)):
                if image_character(actor, source) == chi:
                    carrier = actor
                    break
            if carrier is None:
                fail("no residual permutation carries the order-4 split onto a moved character")
            conjugate = carrier
            # r s r^{-1}
            inverse = lookup[inverse_key(group[carrier])]
            moved_splitter = lookup[compose_key(group[carrier], group[lookup[compose_key(group[splitter], group[inverse])]])]
            expect(preserves(moved_splitter, chi), "the conjugate splitter does not preserve the image character")
            image_powers = [identity]
            current = moved_splitter
            for _ in range(3):
                image_powers.append(current)
                current = lookup[compose_key(group[moved_splitter], group[current])]
            image_traces = [character_trace(power, chi) for power in image_powers]
            expect(multiplicities(image_traces) == multiplicities(source_traces),
                   "conjugation does not transport the order-4 multiplicities")

    witness_432 = require(lookup, U432_INV, U432_EPS)
    expect(compose_key(group[witness_432], group[witness_432]) == (group[identity][0], group[identity][1]),
           "the 432-dimensional witness is not an involution")
    witness_432_characters = [
        chi for chi, dim in enumerate(dims) if dim == 432 and preserves(witness_432, chi)
    ]
    expect(len(witness_432_characters) == 2, "the real 432-witness does not preserve two 432-characters")
    for chi in witness_432_characters:
        trace = character_trace(witness_432, chi)
        expect(trace == 96, "the real 432-witness does not have character trace 96")
        expect((dims[chi] + trace) // 2 == 264 and (dims[chi] - trace) // 2 == 168, "the 264+168 split failed")

    witness_192 = require(lookup, U192_INV, U192_EPS)
    expect(compose_key(group[witness_192], group[witness_192]) == (group[identity][0], group[identity][1]),
           "the 192-dimensional witness is not an involution")
    witness_192_characters = [
        chi for chi, dim in enumerate(dims) if dim == 192 and preserves(witness_192, chi) and character_trace(witness_192, chi) == 0
    ]
    expect(len(witness_192_characters) >= 1, "no preserved 192-character has trace 0 under the witness")

    # Rejection controls.
    swap = (1, 0, 2, 3, 4, 5, 6, 7)
    expect(swap not in autos, "the coordinate transposition was accepted as a tetrad automorphism")
    moved_ports = dict(port_of)
    first_column, second_column = norm(columns[0]), norm(columns[1])
    expect(first_column != second_column, "the first two columns are the same")
    moved_ports[first_column], moved_ports[second_column] = moved_ports[second_column], moved_ports[first_column]
    swapped_linear = True
    images = []
    for column in basis_cols:
        image = tuple(G_EPS[index] * column[G_INV[index]] for index in range(8))
        port = moved_ports.get(norm(image))
        if port is None:
            swapped_linear = False
            break
        images.append(port)
    if swapped_linear:
        for column, port in zip(columns, ports):
            image = tuple(G_EPS[index] * column[G_INV[index]] for index in range(8))
            target = moved_ports[norm(image)]
            predicted = 0
            for index, flag in enumerate(coords[port]):
                if flag:
                    predicted ^= images[index]
            if predicted != target:
                swapped_linear = False
                break
    expect(not swapped_linear, "swapping two port labels left g linear")
    partial = signs[:-1]
    partial_trace = sum(element[3] for element in partial)
    expect(partial_trace % len(partial) != 0 or partial_trace // len(partial) != 864,
           "dropping a sign-stabilizer element still reproduced dimension 864")
    sign_fiber = 0
    for mask in range(256):
        eps = tuple(-1 if (mask >> bit) & 1 else 1 for bit in range(8))
        if (S_INV, eps) in lookup:
            sign_fiber += 1
    expect(sign_fiber == 32, "the order-4 splitter does not have exactly 32 sign lifts in the stabilizer")
    expect((S_INV, tuple(-1 if index == 0 else 1 for index in range(8))) not in lookup,
           "changing the coordinate-0 sign of s stayed inside the recorded 32-sign fiber")

    print("PASS_C1_MOVED_SIGN_SPLIT")
    print("c=1 residual stabilizer order 3072")
    print("moved characters 432^4 192^6 80^4")
    print("order-4 splitter multiplicities 144+84+120+84, 48^4, 32+12+24+12")
    print("involution splits 264+168, 96+96 and 120+72, 56+24")
    print("centralizer order 64 acts by fourth-root scalars on those eigenspaces")


if __name__ == "__main__":
    main()
