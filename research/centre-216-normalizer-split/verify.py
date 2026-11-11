#!/usr/bin/env python3
"""Centralizer census and normalizer splitting of one c=1 216-space.

The certificate uses the pinned INTERFACE.json query and the standard library.
It does not compute a characteristic polynomial of A_1.
"""

import hashlib
import json
import pathlib
from collections import deque

ROOT = pathlib.Path(__file__).resolve().parents[2]
INTERFACE = (
    ROOT
    / "research/centre-polynomial-cache-limits/frozen/work"
    / "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json"
)
INTERFACE_SHA256 = (
    "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
)
C1 = 1
# (S v)_k = eps[k] * v[inv[k]].
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
T_INV = (0, 5, 6, 3, 4, 1, 2, 7)
T_EPS = (1, 1, 1, -1, 1, 1, 1, -1)
U_INV = (0, 1, 2, 3, 7, 6, 5, 4)
U_EPS = (1, 1, 1, 1, 1, 1, 1, 1)
R_INV = (0, 1, 6, 7, 3, 2, 5, 4)
R_EPS = (-1, 1, 1, 1, 1, 1, 1, -1)
CHARACTER_HISTOGRAM = {864: 1, 432: 4, 192: 6, 80: 4, 32: 1}
HYPEROCTAHEDRAL_ORDER = 40320 * 256


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_file(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def load_query():
    if sha256_file(INTERFACE) != INTERFACE_SHA256:
        fail("INTERFACE.json SHA256 does not match the pinned query")
    data = json.loads(INTERFACE.read_text())
    rows = data["R"]
    ports = [int(port) for port in data["ports"]]
    if len(rows) != 8 or len(ports) != 112 or len(set(ports)) != 112:
        fail("query shape is not an 8-by-112 matrix with distinct ports")
    columns = []
    for column in range(112):
        columns.append(tuple(int(rows[row].get(str(column), "0")) for row in range(8)))
    return columns, ports


def norm(vector):
    for entry in vector:
        if entry:
            return tuple(entry * item for item in vector)
    return vector


def rank_solve(vectors, target=None):
    width = len(vectors)
    matrix = [[(vector >> row) & 1 for vector in vectors] for row in range(9)]
    image = None if target is None else [(target >> row) & 1 for row in range(9)]
    pivot_at = [-1] * 9
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, 9):
            if matrix[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        if image is not None:
            image[rank], image[pivot] = image[pivot], image[rank]
        for row in range(9):
            if row != rank and matrix[row][col]:
                for index in range(width):
                    matrix[row][index] ^= matrix[rank][index]
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
    return coef


def prepare(columns, ports):
    port_of = {columns[index]: ports[index] for index in range(112)}
    lookup = {norm(column): port_of[column] for column in columns}
    if len(lookup) != 112:
        fail("the 112 columns are not distinct lines")
    basis = []
    for port in ports:
        if rank_solve(basis + [port]) == len(basis) + 1:
            basis.append(port)
        if len(basis) == 9:
            break
    if len(basis) != 9:
        fail("the 112 ports do not span F2^9")
    coords = {address: tuple(rank_solve(basis, address)) for address in range(512)}
    gram = [[0] * 8 for _ in range(8)]
    for column in columns:
        for left in range(8):
            for right in range(8):
                gram[left][right] += column[left] * column[right]
    if any(gram[left][right] != (56 if left == right else 0) for left in range(8) for right in range(8)):
        fail("RR^T is not 56 I")
    if any(port.bit_count() % 2 == 0 for port in ports):
        fail("a port label has even parity")
    return port_of, lookup, basis, coords


def apply_matrix(matrix, address):
    image = 0
    for bit in range(9):
        if (address >> bit) & 1:
            image ^= matrix[bit]
    return image


def fixed_addresses(matrix):
    rows = [
        [((matrix[col] >> row) & 1) ^ (1 if row == col else 0) for col in range(9)]
        for row in range(9)
    ]
    rank = 0
    for col in range(9):
        pivot = None
        for row in range(rank, 9):
            if rows[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(9):
            if row != rank and rows[row][col]:
                rows[row] = [left ^ right for left, right in zip(rows[row], rows[rank])]
        rank += 1
    return 1 << (9 - rank)


def trace_s(inv, eps):
    return sum(eps[index] for index in range(8) if inv[index] == index)


def pack(inv, eps):
    value = 0
    for item in inv:
        value = (value << 4) | item
    sign = 0
    for bit, item in enumerate(eps):
        if item < 0:
            sign |= 1 << bit
    return (value << 8) | sign


def unpack(key):
    sign = key & 255
    value = key >> 8
    inv = [0] * 8
    for index in range(7, -1, -1):
        inv[index] = value & 15
        value >>= 4
    eps = tuple(-1 if (sign >> bit) & 1 else 1 for bit in range(8))
    return tuple(inv), eps


def compose(left, right):
    left_inv, left_eps = unpack(left)
    right_inv, right_eps = unpack(right)
    inv = tuple(right_inv[left_inv[index]] for index in range(8))
    eps = tuple(left_eps[index] * right_eps[left_inv[index]] for index in range(8))
    return pack(inv, eps)


def inverse(key):
    inv, eps = unpack(key)
    dest_of = [0] * 8
    for dest, src in enumerate(inv):
        dest_of[src] = dest
    return pack(tuple(dest_of), tuple(eps[dest_of[index]] for index in range(8)))


def image_vector(key, column):
    inv, eps = unpack(key)
    return tuple(eps[index] * column[inv[index]] for index in range(8))


def operator_t(key, port_of, lookup, basis, coords, check_orthogonal=False):
    inv, eps = unpack(key)
    mapping = {}
    for column, port in port_of.items():
        matched = lookup.get(norm(image_vector(key, column)))
        if matched is None:
            return None
        mapping[port] = matched
    matrix = []
    for bit in range(9):
        image = 0
        for index, flag in enumerate(coords[1 << bit]):
            if flag:
                image ^= mapping[basis[index]]
        matrix.append(image)
    for port, image in mapping.items():
        if apply_matrix(matrix, port) != image:
            return None
    if check_orthogonal:
        images = [mapping[vector] for vector in basis]
        for left in range(9):
            for right in range(left, 9):
                if (basis[left] & basis[right]).bit_count() % 2 != (
                    images[left] & images[right]
                ).bit_count() % 2:
                    return None
    return tuple(matrix)


def preserves_lines(key, columns, lookup):
    for column in columns:
        if norm(image_vector(key, column)) not in lookup:
            return False
    return True


def full_trace(key, group):
    inv, eps = unpack(key)
    return trace_s(inv, eps) * fixed_addresses(group[key])


def histogram(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_group(port_of, lookup, basis, coords):
    identity = pack(tuple(range(8)), (1,) * 8)
    generators = []
    for index in range(1, 8):
        eps = tuple(-1 if bit == index else 1 for bit in range(8))
        generators.append(pack(tuple(range(8)), eps))
    images = (
        (0, 1, 2, 3, 5, 4, 7, 6),
        (0, 1, 2, 3, 6, 7, 4, 5),
        (0, 1, 3, 2, 4, 5, 7, 6),
        (0, 1, 4, 5, 2, 3, 6, 7),
        (0, 2, 1, 3, 4, 6, 5, 7),
        (1, 0, 2, 3, 4, 5, 7, 6),
    )
    for image in images:
        inv = [0] * 8
        for src, dest in enumerate(image):
            inv[dest] = src
        generators.append(pack(tuple(inv), (1,) * 8))
    generator_t = []
    for generator in generators:
        matrix = operator_t(generator, port_of, lookup, basis, coords, check_orthogonal=True)
        if matrix is None:
            fail("a published centre symmetry does not preserve the query")
        generator_t.append(matrix)
    group = {identity: tuple(1 << bit for bit in range(9))}
    queue = deque([identity])
    while queue:
        current = queue.popleft()
        current_t = group[current]
        for generator, matrix in zip(generators, generator_t):
            nxt = compose(generator, current)
            if nxt not in group:
                group[nxt] = tuple(apply_matrix(matrix, column) for column in current_t)
                queue.append(nxt)
    return group, generators


def hyperoctahedral_generators():
    generators = []
    for index in range(7):
        inv = list(range(8))
        inv[index], inv[index + 1] = index + 1, index
        generators.append(pack(tuple(inv), (1,) * 8))
    for index in range(8):
        eps = tuple(-1 if bit == index else 1 for bit in range(8))
        generators.append(pack(tuple(range(8)), eps))
    return generators


def coset_representatives(group):
    identity = pack(tuple(range(8)), (1,) * 8)
    reps = [identity]
    queue = deque([identity])
    generators = hyperoctahedral_generators()
    while queue:
        rep = queue.popleft()
        for generator in generators:
            nxt = compose(generator, rep)
            if all(compose(inverse(old), nxt) not in group for old in reps):
                reps.append(nxt)
                queue.append(nxt)
    return reps


def character_traces(group_h, trace_of):
    """Traces of the identity on the sign characters, using an external trace function."""
    masks = []
    for key in group_h:
        eps = unpack(key)[1]
        masks.append(sum(1 << bit for bit in range(7) if eps[bit + 1] < 0))
    basis = []
    for mask in masks:
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

    order = len(group_h)
    dims = []
    for chi in range(1 << len(basis)):
        total = 0
        for key, mask in zip(group_h, masks):
            total += value(chi, mask) * trace_of(key)
        if total % order:
            fail("a character trace is not divisible by the stabilizer order")
        dims.append(total // order)
    if any(value(0, mask) != 1 for mask in masks):
        fail("character 0 is not the trivial character")
    return dims


def main():
    columns, ports = load_query()
    port_of, lookup, basis, coords = prepare(columns, ports)
    identity = pack(tuple(range(8)), (1,) * 8)
    first = pack(G_INV, G_EPS)
    second = pack(T_INV, T_EPS)
    reflection = pack(U_INV, U_EPS)
    rotation = pack(R_INV, R_EPS)
    group, _generators = build_group(port_of, lookup, basis, coords)
    expect(len(group) == 344064, "the symmetry group generated by the 13 published lifts does not have order 344064")
    reps = coset_representatives(group)
    expect(len(reps) == 30, "the hyperoctahedral coset count is not 30")
    expect(len(group) * len(reps) == HYPEROCTAHEDRAL_ORDER, "the coset decomposition does not cover the hyperoctahedral group")
    outside = [rep for rep in reps if rep != identity and preserves_lines(rep, columns, lookup)]
    expect(not outside, "a signed permutation outside the generated group preserves the root lines")

    def fixes(key, sector):
        return apply_matrix(group[key], sector) == sector

    stabilizer = [key for key in group if fixes(key, C1)]
    expect(len(stabilizer) == 3072, "the c=1 stabilizer does not have order 3072")
    signs = [
        key
        for key in stabilizer
        if unpack(key)[0] == tuple(range(8)) and unpack(key)[1][0] == 1
    ]
    expect(len(signs) == 16, "the c=1 sign stabilizer does not have order 16")

    def trace_of(key):
        if key not in group:
            fail("a trace was requested for an element outside the symmetry group")
        return full_trace(key, group)

    dims = character_traces(signs, trace_of)
    expect(histogram(dims) == CHARACTER_HISTOGRAM, "the c=1 sign-character histogram changed")
    expect(sum(dims) == 4096, "the c=1 character dimensions do not cover the block")

    def triv(key):
        total = sum(trace_of(compose(key, element)) for element in signs)
        if total % 16:
            fail("a trivial-character trace is not divisible by 16")
        return total // 16

    klein = (identity, first, second, compose(first, second))

    def joint(key):
        parts = [triv(compose(key, element)) for element in klein]
        out = {}
        for left in (1, -1):
            for right in (1, -1):
                numerator = parts[0] + left * parts[1] + right * parts[2] + left * right * parts[3]
                if numerator % 4:
                    fail("a joint trace is not divisible by 4")
                out[(left, right)] = numerator // 4
        return out

    anchor = joint(identity)
    expect(
        anchor == {(1, 1): 216, (1, -1): 216, (-1, 1): 216, (-1, -1): 216},
        "the trivial character does not split into four 216-dimensional joint spaces",
    )

    def commutes(left, right):
        return compose(left, right) == compose(right, left)

    centralizer = [key for key in stabilizer if commutes(key, first) and commutes(key, second)]
    expect(len(centralizer) == 16, "the centralizer of {g,t} does not have order 16")
    centralizer_patterns = set()
    for key in centralizer:
        expect(compose(key, key) == identity, "a centralizer element is not an involution")
        dims_key = joint(key)
        centralizer_patterns.add(tuple(sorted(dims_key.items())))
        for value in dims_key.values():
            if value not in (216, -216):
                fail("a centralizer element does not act by ±1 on a 216-dimensional joint space")
    expect(len(centralizer_patterns) == 8, "the centralizer sign patterns on the four joint spaces changed")

    def conj(actor, element):
        return compose(actor, compose(element, inverse(actor)))

    klein_set = set(klein)
    normalizer = [key for key in stabilizer if {conj(key, element) for element in klein} == klein_set]
    expect(len(normalizer) == 96, "the normalizer of {g,t} does not have order 96")
    sign_set = set(signs)
    for key in normalizer:
        if {conj(key, element) for element in signs} != sign_set:
            fail("a normalizer element does not normalize the sign stabilizer")
    expect(first in centralizer and second in centralizer, "g or t is missing from the centralizer")
    expect(reflection in normalizer and rotation in normalizer, "the dihedral generators are not in the normalizer")
    expect(reflection not in centralizer, "the extra involution u commutes with both g and t")

    def power(key, count):
        value = identity
        for _ in range(count):
            value = compose(value, key)
        return value

    expect(compose(reflection, reflection) == identity, "u is not an involution")
    expect(power(rotation, 6) == identity, "r does not have order dividing 6")
    expect(power(rotation, 1) != identity and power(rotation, 2) != identity and power(rotation, 3) != identity, "r has order less than 6")
    expect(conj(reflection, rotation) == power(rotation, 5), "u does not invert r")

    kernel = [key for key in normalizer if joint(key)[(1, 1)] == 216]
    expect(len(kernel) == 8, "the kernel of the normalizer action on the ++ space does not have order 8")
    kernel_set = set(kernel)
    words = [power(rotation, index) for index in range(6)]
    words += [compose(power(rotation, index), reflection) for index in range(6)]
    cosets = []
    for word in words:
        expect(word in set(normalizer), "a dihedral word is not in the normalizer")
        probe = compose(inverse(word), word)
        expect(probe == identity and probe in kernel_set, "the identity is not in the kernel")
        if all(compose(inverse(rep), word) not in kernel_set for rep in cosets):
            cosets.append(word)
    expect(len(cosets) == 12, "the twelve dihedral words are not distinct modulo the kernel")
    image_count = 0
    seen = []
    for key in normalizer:
        if all(compose(inverse(rep), key) not in kernel_set for rep in seen):
            seen.append(key)
            image_count += 1
    expect(image_count == 12, "the normalizer image does not have order 12")

    def name_klein(key):
        labels = {identity: "1", first: "g", second: "t", klein[3]: "gt"}
        if key not in labels:
            fail("a conjugate left the Klein group")
        return labels[key]

    def image_pair(actor, left, right):
        source_g = name_klein(conj(inverse(actor), first))
        source_t = name_klein(conj(inverse(actor), second))

        def evaluate(label):
            if label == "1":
                return 1
            if label == "g":
                return left
            if label == "t":
                return right
            return left * right

        return evaluate(source_g), evaluate(source_t)

    def preserved(actor):
        return [pair for pair in ((1, 1), (1, -1), (-1, 1), (-1, -1)) if image_pair(actor, *pair) == pair]

    expect(preserved(reflection) == [(1, 1), (1, -1)], "u does not preserve exactly the two g=+1 joint spaces")
    expect(preserved(rotation) == [(1, 1)], "r does not preserve exactly the ++ joint space")
    mixed = compose(rotation, reflection)
    expect(preserved(mixed) == [(1, 1), (-1, -1)], "ru does not preserve ++ and --")
    fourth = conj(rotation, reflection)
    expect(image_pair(fourth, -1, 1) == (-1, 1), "the r-conjugate of u does not preserve the -+ space")

    reflection_traces = joint(reflection)
    expect(reflection_traces[(1, 1)] == 72 and reflection_traces[(1, -1)] == 72, "u does not have trace 72 on both preserved 216-spaces")
    expect(joint(mixed)[(-1, -1)] == -72, "ru does not have trace -72 on the -- space")
    expect(abs(joint(fourth)[(-1, 1)]) == 72, "the conjugate involution does not have trace ±72 on the -+ space")
    rotation_traces = [joint(power(rotation, index))[(1, 1)] for index in range(6)]
    expect(rotation_traces == [216, -24, 24, -216, 24, -24], "the rotation traces on the ++ space changed")
    reflection_class = [joint(compose(power(rotation, index), reflection))[(1, 1)] for index in range(6)]
    expect(reflection_class == [72, -72, 72, -72, 72, -72], "the reflection traces on the ++ space changed")

    elements = [(index, False, rotation_traces[index]) for index in range(6)]
    elements += [(index, True, reflection_class[index]) for index in range(6)]

    def linear_multiplicity(minus_r, minus_u):
        total = 0
        for index, is_reflection, trace in elements:
            sign = (-1) ** index if minus_r else 1
            if is_reflection:
                sign *= -1 if minus_u else 1
            total += sign * trace
        if total % 12:
            fail("a linear-character inner product is not an integer")
        return total // 12

    expect(linear_multiplicity(False, False) == 0, "a linear character with r acting by +1 appears")
    expect(linear_multiplicity(False, True) == 0, "the other linear character with r acting by +1 appears")
    expect(linear_multiplicity(True, False) == 80, "the multiplicity-80 character changed")
    expect(linear_multiplicity(True, True) == 8, "the multiplicity-8 character changed")
    rho_sixty = {0: 2, 1: 1, 2: -1, 3: -2, 4: -1, 5: 1}
    rho_third = {0: 2, 1: -1, 2: -1, 3: 2, 4: -1, 5: -1}
    total_sixty = sum((0 if is_reflection else rho_sixty[index]) * trace for index, is_reflection, trace in elements)
    total_third = sum((0 if is_reflection else rho_third[index]) * trace for index, is_reflection, trace in elements)
    expect(total_sixty % 12 == 0 and total_sixty // 12 == 64, "the 2-dimensional dihedral character does not have multiplicity 64")
    expect(total_third % 12 == 0 and total_third // 12 == 0, "the dihedral character with r^3 acting as +1 appears")
    expect(8 + 80 + 2 * 64 == 216, "the isotypic dimensions do not cover the 216-space")
    rotation_only = sum(((-1) ** index) * rotation_traces[index] for index in range(6))
    expect(rotation_only == 528, "the cyclic subsum is not load-bearing against the reflection classes")
    expect(rotation_only != 96, "dropping the reflections still reproduced the multiplicity-8 numerator")

    # Rejection controls. Each must fail closed.
    transposition = list(range(8))
    transposition[0], transposition[1] = 1, 0
    expect(
        not preserves_lines(pack(tuple(transposition), (1,) * 8), columns, lookup),
        "a coordinate transposition was accepted as a symmetry",
    )
    partial = list(range(8))
    partial[4], partial[7] = 7, 4
    expect(
        not preserves_lines(pack(tuple(partial), (1,) * 8), columns, lookup),
        "swapping coordinates 4 and 7 without coordinates 5 and 6 still preserved the root lines",
    )
    moved = dict(port_of)
    moved[columns[0]], moved[columns[1]] = port_of[columns[1]], port_of[columns[0]]
    moved_lookup = {norm(column): moved[column] for column in columns}
    expect(
        operator_t(first, moved, moved_lookup, basis, coords, check_orthogonal=True) is None,
        "a swapped port label still looked like a symmetry",
    )
    noncommuting = [key for key in signs if not commutes(key, first)]
    expect(noncommuting, "every sign symmetry commutes with g; the commutativity test is insensitive")
    expect(all(key not in set(centralizer) for key in noncommuting), "a sign that does not commute with g was kept in the centralizer")

    for key in (first, second, reflection, rotation, power(rotation, 3)):
        stored = group[key]
        recomputed = operator_t(key, port_of, lookup, basis, coords, check_orthogonal=True)
        expect(recomputed == stored, "a stored label map disagrees with the column action")

    print("PASS_CENTRE_216_NORMALIZER_SPLIT")
    print("line-preserving signed permutations 344064")
    print("hyperoctahedral index 30")
    print("c=1 stabilizer 3072")
    print("centralizer 16 acts by ±1 on every 216-dimensional joint space")
    print("normalizer 96")
    print("dihedral image 12")
    print("trivial-character ++ isotypic dimensions 8 80 128")
    print("u splits the preserved 216-spaces as 72+144")


if __name__ == "__main__":
    main()
