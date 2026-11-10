#!/usr/bin/env python3
"""Exhaustive sign-character split of the c=3 doubled centre block.

The verifier uses the pinned INTERFACE.json query. It proves that the
support automorphism group is AGL(3,2), enumerates the order-3072 stabilizer
of sector 3, and checks the commuting pair that splits every sign character.
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
SELECTED = ROOT / "certificates/selected-result.json"
INTERFACE_SHA256 = (
    "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
)
SELECTED_KAPPA = "781451/250000000"
SECTOR = 3
ODDS = (1, 3, 5, 7)
EVENS = (0, 2, 4, 6)
# sigma as the image tuple. Both are involutions.
U_SIGMA = (2, 1, 0, 3, 6, 5, 4, 7)  # (0 2)(4 6)
U_MASK = 5  # minus signs on the cycle (0 2)
V_SIGMA = (4, 1, 6, 3, 0, 5, 2, 7)  # (0 4)(2 6)
V_MASK = 17  # minus signs on the cycle (0 4)
G_SIGMA = (0, 2, 1, 3, 4, 6, 5, 7)  # r115 g = (1 2)(5 6)
G_MASK = (1 << 4) | (1 << 7)
T_SIGMA = (0, 5, 6, 3, 4, 1, 2, 7)  # r115 t = (1 5)(2 6), this tuple is inv
T_MASK = (1 << 3) | (1 << 7)
CHARACTER_DIMENSIONS = {
    0: 864,
    1: 432,
    2: 432,
    3: 192,
    4: 432,
    5: 192,
    6: 192,
    7: 80,
    8: 432,
    9: 192,
    10: 192,
    11: 80,
    12: 192,
    13: 80,
    14: 80,
    15: 32,
}
# Absolute character trace of every splitting involution, by character weight.
ABSOLUTE_TRACE_BY_WEIGHT = {0: 0, 1: 96, 2: 0, 3: 32, 4: 0}


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_file(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def mask_to_eps(mask):
    return tuple(-1 if (mask >> bit) & 1 else 1 for bit in range(8))


def eps_to_mask(eps):
    return sum(1 << bit for bit in range(8) if eps[bit] < 0)


def inv_of(sigma):
    inverse = [0] * 8
    for source, image in enumerate(sigma):
        inverse[image] = source
    return tuple(inverse)


def compose_perm(left, right):
    """Apply right first, then left. Both arguments are sigma tuples."""
    return tuple(left[right[index]] for index in range(8))


def compose_signed(left_sigma, left_mask, right_sigma, right_mask):
    """Compose operators whose sigma is stored, right applied first.

    (Sv)_k = eps[k] * v[sigma^{-1}(k)]. The composed sigma is left after right.
    """
    sigma = compose_perm(left_sigma, right_sigma)
    # eps_left[k] * eps_right[sigma_left^{-1}(k)], from the r115 composition.
    left_inv = inv_of(left_sigma)
    eps = []
    for index in range(8):
        left_sign = -1 if (left_mask >> index) & 1 else 1
        source = left_inv[index]
        right_sign = -1 if (right_mask >> source) & 1 else 1
        eps.append(left_sign * right_sign)
    return sigma, eps_to_mask(eps)


def norm_code(values):
    code = 0
    sign = 1
    seen = False
    for index, value in enumerate(values):
        if value == 0:
            continue
        if not seen:
            seen = True
            sign = 1 if value > 0 else -1
        signed = value * sign
        code |= (1 if signed > 0 else 2) << (2 * index)
    return code


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
                for entry in range(width):
                    matrix[row][entry] ^= matrix[rank][entry]
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


def load_query():
    expect(sha256_file(INTERFACE) == INTERFACE_SHA256, "INTERFACE.json hash changed")
    selected = json.loads(SELECTED.read_text())
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")
    data = json.loads(INTERFACE.read_text())
    ports = [int(port) for port in data["ports"]]
    rows = data["R"]
    columns = [
        tuple(int(rows[row].get(str(column), "0")) for row in range(8))
        for column in range(112)
    ]
    expect(len(ports) == 112 and len(set(ports)) == 112, "ports are not 112 distinct labels")
    expect(all(value in (-1, 0, 1) for column in columns for value in column), "a column entry is outside {-1,0,1}")
    gram = [[0] * 8 for _ in range(8)]
    supports = []
    seen = set()
    for column in columns:
        weight = 0
        mask = 0
        for index, value in enumerate(column):
            if value:
                weight += 1
                mask |= 1 << index
            for other in range(8):
                gram[index][other] += value * column[other]
        expect(weight == 4, "a column does not have weight 4")
        if mask not in seen:
            seen.add(mask)
            supports.append(mask)
    expect(
        all(gram[i][k] == (56 if i == k else 0) for i in range(8) for k in range(8)),
        "RR^T is not 56 I",
    )
    expect(all(bin(port).count("1") % 2 == 1 for port in ports), "a port label has even parity")
    expect(len(supports) == 14, "the query does not have 14 supports")
    return columns, ports, supports


def affine_planes():
    planes = set()
    for origin, left, right in itertools.combinations(range(8), 3):
        if left == origin or right == origin or left == right:
            continue
        block = frozenset((origin, left, right, origin ^ left ^ right))
        if len(block) == 4:
            planes.add(block)
    expect(len(planes) == 14, "xor geometry did not produce 14 planes")
    return planes


def plane_masks(planes):
    masks = set()
    for plane in planes:
        mask = 0
        for point in plane:
            mask |= 1 << point
        masks.add(mask)
    return masks


def gl_matrices():
    matrices = []
    for bits in range(512):
        images = [((bits >> (3 * column)) & 7) for column in range(3)]
        distinct = {
            images[0],
            images[1],
            images[2],
            images[0] ^ images[1],
            images[0] ^ images[2],
            images[1] ^ images[2],
            images[0] ^ images[1] ^ images[2],
        }
        if 0 not in distinct and len(distinct) == 7:
            matrices.append(tuple(images))
    expect(len(matrices) == 168, "GL(3,2) does not have order 168")
    return matrices


def affine_sigmas(matrices):
    sigmas = []
    for matrix in matrices:
        for translation in range(8):
            sigma = [0] * 8
            for point in range(8):
                image = translation
                for bit in range(3):
                    if (point >> bit) & 1:
                        image ^= matrix[bit]
                sigma[point] = image
            sigmas.append(tuple(sigma))
    expect(len(sigmas) == 1344 and len(set(sigmas)) == 1344, "affine maps are not 1344 distinct permutations")
    return sigmas


def support_autos(support_masks):
    autos = []
    for perm in itertools.permutations(range(8)):
        if all(
            sum(1 << perm[bit] for bit in range(8) if (mask >> bit) & 1) in support_masks
            for mask in support_masks
        ):
            autos.append(perm)
    return autos


def generate_permutations(generators):
    seen = {tuple(range(8))}
    queue = [tuple(range(8))]
    while queue:
        current = queue.pop()
        for generator in generators:
            nxt = compose_perm(generator, current)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
            nxt = compose_perm(current, generator)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def prepare_labels(columns, ports):
    lookup = [-1] * (1 << 16)
    for column, port in zip(columns, ports):
        lookup[norm_code(column)] = port
    basis = []
    for port in ports:
        if rank_solve(basis + [port]) == len(basis) + 1:
            basis.append(port)
        if len(basis) == 9:
            break
    expect(len(basis) == 9, "ports do not span F2^9")
    coords = [rank_solve(basis, 1 << bit) for bit in range(9)]
    contrib = [[index for index, bit in enumerate(row) if bit] for row in coords]
    basis_columns = []
    for port in basis:
        basis_columns.append(columns[ports.index(port)])
    basis_dot = [
        [
            bin(basis[left] & basis[right]).count("1") & 1
            for right in range(9)
        ]
        for left in range(9)
    ]
    return lookup, basis, basis_columns, contrib, basis_dot


def project_ports(lookup, basis_columns, inv, mask):
    images = []
    for column in basis_columns:
        code = 0
        sign = 1
        seen = False
        for index in range(8):
            value = column[inv[index]]
            if value and (mask >> index) & 1:
                value = -value
            if value == 0:
                continue
            if not seen:
                seen = True
                sign = 1 if value > 0 else -1
            signed = value * sign
            code |= (1 if signed > 0 else 2) << (2 * index)
        found = lookup[code]
        if found < 0:
            return None
        images.append(found)
    return images


def matrix_from_images(contrib, images):
    matrix = []
    for bit in range(9):
        acc = 0
        for index in contrib[bit]:
            acc ^= images[index]
        matrix.append(acc)
    return tuple(matrix)


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


def coordinate_trace(inv, mask):
    total = 0
    for index in range(8):
        if inv[index] == index:
            total += -1 if (mask >> index) & 1 else 1
    return total


def block_trace(inv, mask, matrix):
    return coordinate_trace(inv, mask) * fixed_addresses(matrix)


def orthogonal(basis, basis_dot, images):
    for left in range(9):
        for right in range(left, 9):
            image_dot = bin(images[left] & images[right]).count("1") & 1
            if image_dot != basis_dot[left][right]:
                return False
    return True


def full_operator(lookup, columns, ports, basis, basis_columns, contrib, basis_dot, sigma, mask):
    inv = inv_of(sigma)
    port_of = {}
    for column, port in zip(columns, ports):
        values = []
        for index in range(8):
            value = column[inv[index]]
            if value and (mask >> index) & 1:
                value = -value
            values.append(value)
        found = lookup[norm_code(values)]
        if found < 0:
            return None
        port_of[port] = found
    basis_images = []
    for column in basis_columns:
        values = []
        for index in range(8):
            value = column[inv[index]]
            if value and (mask >> index) & 1:
                value = -value
            values.append(value)
        basis_images.append(lookup[norm_code(values)])
    matrix = matrix_from_images(contrib, basis_images)
    for port, image in port_of.items():
        if apply_matrix(matrix, port) != image:
            return None
    basis_ports = [port_of[vector] for vector in basis]
    if not orthogonal(basis, basis_dot, basis_ports):
        return None
    return {
        "sigma": sigma,
        "inv": inv,
        "mask": mask,
        "T": matrix,
        "trace": block_trace(inv, mask, matrix),
    }


def chi_value(chi, mask):
    sign = 0
    for index, coordinate in enumerate(ODDS):
        if (chi >> index) & 1 and (mask >> coordinate) & 1:
            sign ^= 1
    return -1 if sign else 1


def character_trace(element, group, chi, traces):
    total = 0
    for member in group:
        sigma, mask = compose_signed(element["sigma"], element["mask"], member["sigma"], member["mask"])
        key = (sigma, mask)
        expect(key in traces, "a character product leaves the computed set")
        total += chi_value(chi, member["mask"]) * traces[key]
    expect(total % len(group) == 0, "character trace is not integral")
    return total // len(group)


def eigenvalue_split(dimension, trace):
    expect((dimension + trace) % 2 == 0, "involution trace has the wrong parity")
    return (dimension + trace) // 2, (dimension - trace) // 2


def joint_split(dimension, first, second, product):
    spaces = {}
    for left in (1, -1):
        for right in (1, -1):
            numerator = dimension + left * first + right * second + left * right * product
            expect(numerator % 4 == 0 and numerator >= 0, "joint dimension is not a nonnegative quarter")
            spaces[(left, right)] = numerator // 4
    expect(sum(spaces.values()) == dimension, "joint spaces miss the character")
    return spaces


def described_diagonal_masks():
    masks = []
    for odds in range(16):
        for even_sign in (0, 1):
            mask = even_sign * sum(1 << coordinate for coordinate in EVENS)
            for index, coordinate in enumerate(ODDS):
                if (odds >> index) & 1:
                    mask |= 1 << coordinate
            masks.append(mask)
    return masks


def described_splitting():
    """Three even double transpositions, opposite cycle signs, free odd signs."""
    cycles = (
        ((0, 2), (4, 6)),
        ((0, 4), (2, 6)),
        ((0, 6), (2, 4)),
    )
    elements = []
    for first, second in cycles:
        sigma = list(range(8))
        sigma[first[0]], sigma[first[1]] = first[1], first[0]
        sigma[second[0]], sigma[second[1]] = second[1], second[0]
        sigma = tuple(sigma)
        for negative in (0, 1):
            for odds in range(16):
                mask = 0
                chosen = first if negative == 0 else second
                mask |= 1 << chosen[0]
                mask |= 1 << chosen[1]
                for index, coordinate in enumerate(ODDS):
                    if (odds >> index) & 1:
                        mask |= 1 << coordinate
                elements.append((sigma, mask))
    return elements


def main():
    columns, ports, support_list = load_query()
    planes = affine_planes()
    support_masks = plane_masks(planes)
    expect(set(support_list) == support_masks, "column supports are not the AG(3,2) planes")
    matrices = gl_matrices()
    affine = affine_sigmas(matrices)
    affine_set = set(affine)
    for sigma in affine:
        for mask in support_masks:
            image = 0
            for bit in range(8):
                if (mask >> bit) & 1:
                    image |= 1 << sigma[bit]
            expect(image in support_masks, "an affine map misses a plane")
    autos = support_autos(support_masks)
    expect(set(autos) == affine_set, "support automorphisms are not exactly AGL(3,2)")

    # Two linear maps and three translations generate AGL(3,2).
    shear = tuple(point ^ (2 if point & 1 else 0) for point in range(8))  # (1 3)(5 7)
    singer = (0, 2, 4, 6, 3, 1, 7, 5)
    translations = [tuple(point ^ shift for point in range(8)) for shift in (1, 2, 4)]
    generated = generate_permutations([shear, singer, *translations])
    expect(generated == affine_set, "the listed generators do not generate AGL(3,2)")
    fixed_odds = [sigma for sigma in affine if all(sigma[point] == point for point in ODDS)]
    expect(
        set(fixed_odds) == {tuple(range(8)), U_SIGMA, V_SIGMA, compose_perm(U_SIGMA, V_SIGMA)},
        "AGL(3,2) does not fix the odd coordinates in exactly four maps",
    )

    lookup, basis, basis_columns, contrib, basis_dot = prepare_labels(columns, ports)

    def realize(sigma, mask):
        return full_operator(
            lookup, columns, ports, basis, basis_columns, contrib, basis_dot, sigma, mask
        )

    generators = [(tuple(range(8)), 1 << bit) for bit in range(8)]
    generators.extend((sigma, 0) for sigma in (shear, singer, *translations))
    generator_ops = []
    for sigma, mask in generators:
        built = realize(sigma, mask)
        expect(built is not None, "a declared generator is not a linear orthogonal symmetry")
        generator_ops.append(built)
    for left in generator_ops:
        for right in generator_ops:
            sigma, mask = compose_signed(left["sigma"], left["mask"], right["sigma"], right["mask"])
            product = realize(sigma, mask)
            expect(product is not None, "a generator product is not a symmetry")
            composed = tuple(apply_matrix(left["T"], column) for column in right["T"])
            expect(product["T"] == composed, "label maps do not multiply on generator products")

    # Every signed affine map is a word in the generators, hence a symmetry.
    # The scan below only evaluates T(3). Stabilizer candidates are rebuilt
    # with the full port check, and orbit-stabilizer names the exact count.
    orbit = {SECTOR}
    frontier = [SECTOR]
    while frontier:
        current = frontier.pop()
        for built in generator_ops:
            image = apply_matrix(built["T"], current)
            if image not in orbit:
                orbit.add(image)
                frontier.append(image)
    expect(len(orbit) == 112, "the generator orbit of sector 3 does not have size 112")
    group_order = 1344 * 256
    expect(group_order // len(orbit) == 3072, "orbit-stabilizer did not give stabilizer order 3072")

    stabilizer = []
    orbit_hits = {}
    for sigma in affine:
        inv = inv_of(sigma)
        for mask in range(256):
            images = project_ports(lookup, basis_columns, inv, mask)
            expect(images is not None, "a signed affine map missed a basis column")
            matrix = matrix_from_images(contrib, images)
            image = matrix[0] ^ matrix[1]
            orbit_hits[image] = orbit_hits.get(image, 0) + 1
            if image == SECTOR:
                stabilizer.append((sigma, mask, matrix))
    expect(len(stabilizer) == 3072, "the T(3)=3 scan did not find 3072 elements")
    expect(set(orbit_hits) == orbit, "the scanned orbit of sector 3 disagrees with the generators")
    expect(all(count == 3072 for count in orbit_hits.values()), "sector-3 fibers are not uniform")

    realized = {}
    for sigma, mask, matrix in stabilizer:
        built = realize(sigma, mask)
        expect(built is not None, "a scanned stabilizer element is not a full symmetry")
        expect(apply_matrix(built["T"], SECTOR) == SECTOR, "full rebuild does not fix sector 3")
        expect(built["T"] == matrix, "fast and full label maps disagree on the stabilizer")
        realized[(sigma, mask)] = built

    identity = realized[(tuple(range(8)), 0)]
    expect(identity["trace"] == 4096, "the identity trace is not 4096")

    diagonal_keys = described_diagonal_masks()
    expect(len(set(diagonal_keys)) == 32, "the diagonal description is not 32 masks")
    diagonal = []
    for mask in diagonal_keys:
        key = (tuple(range(8)), mask)
        expect(key in realized, "a described diagonal sign does not fix sector 3")
        diagonal.append(realized[key])
    pure_sign_keys = [
        key for key in realized if key[0] == tuple(range(8))
    ]
    expect(set(pure_sign_keys) == set((tuple(range(8)), mask) for mask in diagonal_keys),
           "sector 3 has a pure sign outside the even-equal description")
    sign_group = [element for element in diagonal if (element["mask"] & 1) == 0]
    expect(len(sign_group) == 16, "the positive-coordinate-0 sign stabilizer is not order 16")
    for element in sign_group:
        for coordinate in EVENS:
            expect((element["mask"] >> coordinate) & 1 == 0, "H moves an even coordinate")

    traces = {key: element["trace"] for key, element in realized.items()}
    dimensions = []
    for chi in range(16):
        total = sum(chi_value(chi, element["mask"]) * element["trace"] for element in sign_group)
        expect(total % 16 == 0, "a character dimension is not integral")
        dimensions.append(total // 16)
    expect(dimensions == [CHARACTER_DIMENSIONS[chi] for chi in range(16)], "c=3 character dimensions changed")
    expect(sum(dimensions) == 4096, "character dimensions do not cover the 4096-dimensional block")

    scalars = {}
    for element in diagonal:
        for chi in range(16):
            trace = character_trace(element, sign_group, chi, traces)
            dimension = dimensions[chi]
            expect(abs(trace) == dimension, "a diagonal sign does not act by a scalar on a character")
            scalars[(element["mask"], chi)] = trace // dimension

    def conjugate_mask(sigma, mask):
        inverse = inv_of(sigma)
        out = 0
        for index in range(8):
            if (mask >> inverse[index]) & 1:
                out |= 1 << index
        return out

    diagonal_mask_set = {element["mask"] for element in diagonal}
    preservers = []
    for key, element in realized.items():
        preserves = True
        for member in sign_group:
            image_mask = conjugate_mask(element["sigma"], member["mask"])
            if image_mask not in diagonal_mask_set:
                preserves = False
                break
            for chi in range(16):
                if scalars[(image_mask, chi)] != chi_value(chi, member["mask"]):
                    preserves = False
                    break
            if not preserves:
                break
        if preserves:
            preservers.append(element)
    expect(len(preservers) == 128, "the all-character preserver count is not 128")

    splitting_keys = set(described_splitting())
    expect(len(splitting_keys) == 96, "the splitting description is not 96 elements")
    preserver_keys = {(element["sigma"], element["mask"]) for element in preservers}
    diagonal_key_set = {(tuple(range(8)), mask) for mask in diagonal_keys}
    expect(preserver_keys == splitting_keys | diagonal_key_set, "preservers are not the described 128 elements")

    # The 128 elements form an elementary abelian 2-group, so every pair commutes.
    for left in preserver_keys:
        for right in preserver_keys:
            product = compose_signed(left[0], left[1], right[0], right[1])
            expect(product in preserver_keys, "the preserver set is not closed")
            expect(
                compose_signed(right[0], right[1], left[0], left[1]) == product,
                "two all-character preservers do not commute",
            )
        expect(compose_signed(left[0], left[1], left[0], left[1]) == (tuple(range(8)), 0),
               "an all-character preserver is not an involution")

    # Modulo diagonal signs there are four cosets, one per even double transposition.
    cosets = {}
    for sigma, mask in preserver_keys:
        coset = sigma
        cosets.setdefault(coset, set()).add(mask)
    expect(set(cosets) == {tuple(range(8)), U_SIGMA, V_SIGMA, compose_perm(U_SIGMA, V_SIGMA)},
           "preserver permutations are not the identity and the three even double transpositions")
    expect(all(len(masks) == 32 for masks in cosets.values()), "a preserver coset does not have size 32")

    splitting = [realized[key] for key in splitting_keys]
    for element in splitting:
        for chi, dimension in enumerate(dimensions):
            trace = character_trace(element, sign_group, chi, traces)
            weight = bin(chi).count("1")
            expect(abs(trace) == ABSOLUTE_TRACE_BY_WEIGHT[weight], "a splitting trace has an unexpected absolute value")
            positive, negative = eigenvalue_split(dimension, trace)
            expect(positive > 0 and negative > 0, "a splitting involution misses an eigenvalue")
            expect(positive + negative == dimension, "eigenvalues do not cover a character")

    first = realized[(U_SIGMA, U_MASK)]
    second = realized[(V_SIGMA, V_MASK)]
    product_key = compose_signed(U_SIGMA, U_MASK, V_SIGMA, V_MASK)
    expect(product_key in splitting_keys, "the explicit product is not a splitting involution")
    product = realized[product_key]
    expect(product["sigma"] == (6, 1, 4, 3, 2, 5, 0, 7), "the explicit product is not (0 6)(2 4)")
    expect(product["mask"] == 65, "the explicit product has an unexpected sign")
    four_way = 0
    for left_index, left in enumerate(splitting):
        for right in splitting[left_index + 1:]:
            product_sigma, product_mask = compose_signed(left["sigma"], left["mask"], right["sigma"], right["mask"])
            if (product_sigma, product_mask) in splitting_keys:
                four_way += 1
    expect(four_way == 3072, "the number of four-way splitting pairs changed")

    joint = {}
    for chi, dimension in enumerate(dimensions):
        joint[chi] = joint_split(
            dimension,
            character_trace(first, sign_group, chi, traces),
            character_trace(second, sign_group, chi, traces),
            character_trace(product, sign_group, chi, traces),
        )
        expect(all(value > 0 for value in joint[chi].values()), "the explicit pair misses a joint eigenvalue")
    expect(joint[0] == {(1, 1): 216, (1, -1): 216, (-1, 1): 216, (-1, -1): 216},
           "the trivial character does not split into four blocks of dimension 216")
    expect(joint[15] == {(1, 1): 8, (1, -1): 8, (-1, 1): 8, (-1, -1): 8},
           "the 32-dimensional character does not split into four blocks of dimension 8")
    expect(joint[1][(1, 1)] == 180 and joint[1][(1, -1)] == 84, "a 432-dimensional joint split changed")
    expect(joint[3][(1, 1)] == 48, "a 192-dimensional joint split changed")
    expect(joint[7][(1, 1)] == 44 and joint[7][(1, -1)] == 12, "an 80-dimensional joint split changed")

    # r115 pair: g moves sector 3, and t fixes it without preserving every character.
    old_g = realize(G_SIGMA, G_MASK)
    # T_SIGMA was stored as inv in the predecessor. Convert it to sigma.
    old_t_sigma = [0] * 8
    for index, source in enumerate(T_SIGMA):
        old_t_sigma[source] = index
    old_t = realize(tuple(old_t_sigma), T_MASK)
    expect(old_g is not None and old_t is not None, "the r115 involutions are not symmetries")
    expect(apply_matrix(old_g["T"], SECTOR) == 343, "g does not send sector 3 to 343")
    expect(apply_matrix(old_t["T"], SECTOR) == SECTOR, "t does not preserve sector 3")
    expect((old_t["sigma"], old_t["mask"]) not in preserver_keys, "t was classified as preserving every c=3 character")
    t_preserved = 0
    for chi in range(16):
        moved = False
        for member in sign_group:
            image_mask = conjugate_mask(old_t["sigma"], member["mask"])
            if image_mask not in diagonal_mask_set or scalars[(image_mask, chi)] != chi_value(chi, member["mask"]):
                moved = True
                break
        if not moved:
            t_preserved += 1
    expect(t_preserved == 8, "t does not preserve exactly eight c=3 characters")

    # Rejection controls.
    expect(realize((1, 0, 2, 3, 4, 5, 6, 7), 0) is None, "a coordinate transposition was accepted")
    same_cycle = realize(U_SIGMA, sum(1 << coordinate for coordinate in EVENS))
    expect(same_cycle is not None, "equal signs on both even cycles are not a symmetry")
    expect(apply_matrix(same_cycle["T"], SECTOR) != SECTOR,
           "equal signs on both even cycles still fix sector 3")
    partial = sign_group[:-1]
    partial_trace = sum(element["trace"] for element in partial)
    expect(
        partial_trace % len(partial) != 0 or partial_trace // len(partial) != 864,
        "dropping a sign still reproduced the trivial dimension",
    )

    print("PASS_C3_CENTRE_SIGN_SPLIT")
    print("symmetry group order", group_order)
    print("sector 3 stabilizer order", len(realized))
    print("all-character preservers", len(preservers))
    print("splitting involutions", len(splitting))
    print("four-way pairs", four_way)
    print("trivial joint", " ".join(str(joint[0][key]) for key in ((1, 1), (1, -1), (-1, 1), (-1, -1))))
    print("t preserves", t_preserved, "c=3 characters")
    print("g sends sector 3 to", apply_matrix(old_g["T"], SECTOR))


if __name__ == "__main__":
    main()
