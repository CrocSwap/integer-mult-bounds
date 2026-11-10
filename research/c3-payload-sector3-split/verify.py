#!/usr/bin/env python3
"""Prove that the degree-881 payload involutions split a c=3 joint space.

X_3 and Z_{3 xor 511} are the payload involutions attached to Bell block 3 in
research/exact-one-slot-gram/PROOF.md. They are not coordinate signed
permutations. On the explicit pair from research/c3-centre-sign-split, both
eigenvalues occur on every joint space. Acceptance uses explicit checks, so
python -O does not skip a step.
"""

import hashlib
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
ALL_ONE = 511
SHIFT = SECTOR
CHARACTER = SECTOR ^ ALL_ONE  # 508
ODDS = (1, 3, 5, 7)
U_SIGMA = (2, 1, 0, 3, 6, 5, 4, 7)  # (0 2)(4 6)
U_MASK = 5  # minus signs on (0 2)
V_SIGMA = (4, 1, 6, 3, 0, 5, 2, 7)  # (0 4)(2 6)
V_MASK = 17  # minus signs on (0 4)
JOINT_ORDER = ((1, 1), (1, -1), (-1, 1), (-1, -1))
# Published c=3 sign-character dimensions, indexed by the F_2^4 character.
CHARACTER_DIMENSIONS = (
    864, 432, 432, 192, 432, 192, 192, 80,
    432, 192, 192, 80, 192, 80, 80, 32,
)
# Joint (u, v) dimensions and X_3 traces, in JOINT_ORDER, by character weight.
# Z_{508} and the product have trace 0 on every one of these spaces.
EXPECTED_BY_WEIGHT = {
    0: ((216, 216, 216, 216), (-48, 16, 16, 16)),
    1: ((180, 84, 84, 84), (36, -12, -12, -12)),
    2: ((48, 48, 48, 48), (-24, 8, 8, 8)),
    3: ((44, 12, 12, 12), (12, -4, -4, -4)),
    4: ((8, 8, 8, 8), (0, 0, 0, 0)),
}


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def dot(left, right):
    return bin(left & right).count("1") & 1


def apply_map(matrix, address):
    image = 0
    for bit in range(9):
        if (address >> bit) & 1:
            image ^= matrix[bit]
    return image


def compose_maps(left, right):
    return tuple(apply_map(left, column) for column in right)


def inverse_map(matrix):
    inverse = [0] * 9
    for bit in range(9):
        image = matrix[bit]
        for row in range(9):
            if (image >> row) & 1:
                inverse[row] |= 1 << bit
    return tuple(inverse)


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
    return tuple(left[right[index]] for index in range(8))


def compose_signed(left_sigma, left_mask, right_sigma, right_mask):
    """Compose operators, right applied first.

    (Sv)_k = eps[k] * v[sigma^{-1}(k)].
    """
    sigma = compose_perm(left_sigma, right_sigma)
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


def coordinate_trace(sigma, mask):
    total = 0
    for index in range(8):
        if sigma[index] == index:
            total += -1 if (mask >> index) & 1 else 1
    return total


def chi_value(chi, mask):
    sign = 0
    for index, coordinate in enumerate(ODDS):
        if (chi >> index) & 1 and (mask >> coordinate) & 1:
            sign ^= 1
    return -1 if sign else 1


def payload_action(label, sector, address):
    """P_label(sector) on one address: image and sign."""
    if dot(label, sector):
        return address ^ label, 1
    sign = -1 if dot(label, address) else 1
    return address, sign


def address_trace_enumerate(matrix, translation, character):
    total = 0
    for address in range(512):
        image = apply_map(matrix, address)
        if (image ^ translation) == address:
            total += -1 if dot(character, image) else 1
    return total


def address_trace_linear(matrix, translation, character):
    """Same trace by solving (T+I)a = translation over F_2."""
    rows = []
    for row in range(9):
        coef = 0
        for col in range(9):
            image = matrix[col] ^ (1 << col)
            if (image >> row) & 1:
                coef |= 1 << col
        rhs = (translation >> row) & 1
        rows.append(coef | (rhs << 9))
    pivot_of = [-1] * 9
    rank = 0
    for col in range(9):
        pivot = None
        for row in range(rank, 9):
            if (rows[row] >> col) & 1:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(9):
            if row != rank and (rows[row] >> col) & 1:
                rows[row] ^= rows[rank]
        pivot_of[rank] = col
        rank += 1
    for row in range(rank, 9):
        if (rows[row] >> 9) & 1:
            return 0
    particular = 0
    for row in range(rank):
        if (rows[row] >> 9) & 1:
            particular |= 1 << pivot_of[row]
    pivots = set(pivot_of[:rank])
    kernel = []
    for col in range(9):
        if col in pivots:
            continue
        vector = 1 << col
        for row in range(rank):
            if (rows[row] >> col) & 1:
                vector ^= 1 << pivot_of[row]
        kernel.append(vector)
    if any(dot(character, vector) for vector in kernel):
        return 0
    # On solutions, T(a) = a xor translation.
    sign_bit = dot(character, particular) ^ dot(character, translation)
    sign = -1 if sign_bit else 1
    return sign * (1 << len(kernel))


def address_trace(matrix, translation, character):
    enumerated = address_trace_enumerate(matrix, translation, character)
    solved = address_trace_linear(matrix, translation, character)
    expect(
        enumerated == solved,
        "address-trace methods disagree for translation "
        + str(translation)
        + " character "
        + str(character)
        + ": "
        + str(enumerated)
        + " vs "
        + str(solved),
    )
    return enumerated


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
    expect(
        all(value in (-1, 0, 1) for column in columns for value in column),
        "a column entry is outside {-1,0,1}",
    )
    gram = [[0] * 8 for _ in range(8)]
    for column in columns:
        weight = sum(1 for value in column if value)
        expect(weight == 4, "a column does not have weight 4")
        for index, value in enumerate(column):
            for other in range(8):
                gram[index][other] += value * column[other]
    expect(
        all(gram[i][k] == (56 if i == k else 0) for i in range(8) for k in range(8)),
        "RR^T is not 56 I",
    )
    expect(all(dot(port, ALL_ONE) == 1 for port in ports), "a port label has even weight")
    expect(dot(SHIFT, CHARACTER) == 0, "X_3 and Z_508 do not commute")
    expect(CHARACTER == 508, "the sector character is not 508")
    for port in ports:
        if dot(port, SECTOR) == 1:
            expect(dot(port, CHARACTER) == 0, "an odd port meets Z_508 while translating by the sector")
    return columns, ports


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
    basis_columns = [columns[ports.index(port)] for port in basis]
    return lookup, basis_columns, contrib


def realize(lookup, columns, ports, basis_columns, contrib, sigma, mask):
    inverse = inv_of(sigma)
    port_of = {}
    for column, port in zip(columns, ports):
        values = []
        for index in range(8):
            value = column[inverse[index]]
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
            value = column[inverse[index]]
            if value and (mask >> index) & 1:
                value = -value
            values.append(value)
        found = lookup[norm_code(values)]
        if found < 0:
            return None
        basis_images.append(found)
    matrix = []
    for bit in range(9):
        acc = 0
        for index in contrib[bit]:
            acc ^= basis_images[index]
        matrix.append(acc)
    matrix = tuple(matrix)
    for port, image in port_of.items():
        if apply_map(matrix, port) != image:
            return None
    for left in range(9):
        for right in range(left, 9):
            if dot(matrix[left], matrix[right]) != (1 if left == right else 0):
                return None
    block = coordinate_trace(sigma, mask) * address_trace(matrix, 0, 0)
    return {
        "sigma": sigma,
        "mask": mask,
        "T": matrix,
        "trace": block,
    }


def conjugation_holds(matrix, ports):
    """U P_q(3) U^{-1} = P_{Tq}(3) on every address."""
    for port in ports:
        image_port = apply_map(matrix, port)
        for address in range(512):
            moved, sign = payload_action(port, SECTOR, address)
            transported = apply_map(matrix, moved)
            expected, expected_sign = payload_action(
                image_port, SECTOR, apply_map(matrix, address)
            )
            if transported != expected or sign != expected_sign:
                return False
    return True


def commutes_with_translation(port, shift):
    for address in range(512):
        moved, sign = payload_action(port, SECTOR, address)
        other, other_sign = payload_action(port, SECTOR, address ^ shift)
        if (moved ^ shift) != other or sign != other_sign:
            return False
    return True


def commutes_with_character(port, character):
    for address in range(512):
        moved, _sign = payload_action(port, SECTOR, address)
        if dot(character, moved) != dot(character, address):
            return False
    return True


def sign_masks():
    masks = []
    for odds in range(16):
        mask = 0
        for index, coordinate in enumerate(ODDS):
            if (odds >> index) & 1:
                mask |= 1 << coordinate
        masks.append(mask)
    return masks


def eigenvalue_split(dimension, trace):
    expect((dimension + trace) % 2 == 0, "involution trace has the wrong parity")
    positive = (dimension + trace) // 2
    negative = (dimension - trace) // 2
    expect(positive >= 0 and negative >= 0, "an eigenvalue dimension is negative")
    expect(positive + negative == dimension, "eigenvalues do not cover the space")
    return positive, negative


def four_way(dimension, trace_x, trace_z, trace_xz):
    spaces = {}
    for eigenvalue_x in (1, -1):
        for eigenvalue_z in (1, -1):
            sector_t = 0 if eigenvalue_z == 1 else 1
            numerator = (
                dimension
                + eigenvalue_x * trace_x
                + eigenvalue_z * trace_z
                + eigenvalue_x * eigenvalue_z * trace_xz
            )
            expect(numerator % 4 == 0 and numerator >= 0, "four-way dimension is not a nonnegative quarter")
            spaces[(eigenvalue_x, sector_t)] = numerator // 4
    expect(sum(spaces.values()) == dimension, "four-way spaces miss the joint space")
    return spaces


def main():
    columns, ports = load_query()
    lookup, basis_columns, contrib = prepare_labels(columns, ports)

    def build(sigma, mask):
        return realize(lookup, columns, ports, basis_columns, contrib, sigma, mask)

    for port in ports:
        expect(commutes_with_translation(port, SHIFT), "X_3 fails to commute with a port operator")
        expect(commutes_with_character(port, CHARACTER), "Z_508 fails to commute with a port operator")

    identity = build(tuple(range(8)), 0)
    expect(identity is not None and identity["trace"] == 4096, "the identity trace is not 4096")
    u = build(U_SIGMA, U_MASK)
    v = build(V_SIGMA, V_MASK)
    expect(u is not None and v is not None, "the explicit pair is not a symmetry of the query")
    product_sigma, product_mask = compose_signed(U_SIGMA, U_MASK, V_SIGMA, V_MASK)
    expect(product_sigma == (6, 1, 4, 3, 2, 5, 0, 7), "the explicit product is not (0 6)(2 4)")
    expect(product_mask == 65, "the explicit product has an unexpected sign")
    uv = build(product_sigma, product_mask)
    expect(uv is not None, "the explicit product is not a symmetry")
    back_sigma, back_mask = compose_signed(V_SIGMA, V_MASK, U_SIGMA, U_MASK)
    expect((back_sigma, back_mask) == (product_sigma, product_mask), "u and v do not commute")

    sign_group = []
    for mask in sign_masks():
        element = build(tuple(range(8)), mask)
        expect(element is not None, "a positive-even sign is not a symmetry")
        sign_group.append(element)
    expect(len(sign_group) == 16, "H does not have order 16")

    bases = {"I": identity, "u": u, "v": v, "uv": uv}
    elements = {}
    for name, base in bases.items():
        for member in sign_group:
            if name == "I":
                element = member
            else:
                sigma, mask = compose_signed(
                    base["sigma"], base["mask"], member["sigma"], member["mask"]
                )
                element = build(sigma, mask)
                expect(element is not None, "a product left the symmetry representation")
                expect(
                    element["T"] == compose_maps(base["T"], member["T"]),
                    "label maps do not multiply",
                )
            expect(inv_of(element["sigma"]) == element["sigma"], "a group element is not an involution")
            expect(
                compose_signed(element["sigma"], element["mask"], element["sigma"], element["mask"])
                == (tuple(range(8)), 0),
                "a group element does not square to the identity",
            )
            matrix = element["T"]
            inverse = inverse_map(matrix)
            expect(apply_map(matrix, SECTOR) == SECTOR, "an element moves sector 3")
            expect(apply_map(matrix, ALL_ONE) == ALL_ONE, "an element moves the all-one label")
            expect(apply_map(matrix, CHARACTER) == CHARACTER, "an element moves 508")
            for address in range(512):
                expect(
                    apply_map(inverse, apply_map(matrix, address)) == address,
                    "a label map is not inverted by its transpose",
                )
                expect(
                    apply_map(matrix, address ^ SHIFT) == (apply_map(matrix, address) ^ SHIFT),
                    "X_3 does not commute with a group element",
                )
                expect(
                    dot(CHARACTER, apply_map(matrix, address)) == dot(CHARACTER, address),
                    "Z_508 does not commute with a group element",
                )
            expect(conjugation_holds(matrix, ports), "port conjugation fails on a group element")
            elements[(name, member["mask"])] = element
    expect(len(elements) == 64, "the Klein coset of H is not 64 elements")

    dimensions = []
    for chi in range(16):
        total = sum(chi_value(chi, element["mask"]) * element["trace"] for element in sign_group)
        expect(total % 16 == 0, "a character dimension is not integral")
        dimensions.append(total // 16)
    expect(tuple(dimensions) == CHARACTER_DIMENSIONS, "c=3 character dimensions changed")

    operators = {
        "I": (0, 0),
        "X": (SHIFT, 0),
        "Z": (0, CHARACTER),
        "XZ": (SHIFT, CHARACTER),
    }
    traces = {name: {} for name in operators}
    for key, element in elements.items():
        for name, (translation, character) in operators.items():
            counted = address_trace(element["T"], translation, character)
            if name in ("Z", "XZ"):
                expect(counted == 0, "Z_508 or the product fixes a weighted address")
            traces[name][key] = coordinate_trace(element["sigma"], element["mask"]) * counted
        expect(traces["I"][key] == element["trace"], "the identity payload trace drifted")

    def joint_trace(op_name, chi, eps, delta):
        total = 0
        for member in sign_group:
            chi_h = chi_value(chi, member["mask"])
            terms = (
                (1, "I"),
                (eps, "u"),
                (delta, "v"),
                (eps * delta, "uv"),
            )
            for coef, name in terms:
                total += chi_h * coef * traces[op_name][(name, member["mask"])]
        expect(total % 64 == 0, "a joint trace is not a multiple of 64")
        return total // 64

    sector_total = {(1, 0): 0, (1, 1): 0, (-1, 0): 0, (-1, 1): 0}
    x_positive = 0
    headline = None
    for chi in range(16):
        weight = bin(chi).count("1")
        expected_dims, expected_x = EXPECTED_BY_WEIGHT[weight]
        for index, (eps, delta) in enumerate(JOINT_ORDER):
            dimension = joint_trace("I", chi, eps, delta)
            trace_x = joint_trace("X", chi, eps, delta)
            trace_z = joint_trace("Z", chi, eps, delta)
            trace_xz = joint_trace("XZ", chi, eps, delta)
            expect(dimension == expected_dims[index], "a joint dimension changed")
            expect(trace_x == expected_x[index], "an X_3 joint trace changed")
            expect(trace_z == 0 and trace_xz == 0, "Z_508 or the product has a nonzero joint trace")
            positive, negative = eigenvalue_split(dimension, trace_x)
            expect(positive > 0 and negative > 0, "X_3 misses an eigenvalue on a joint space")
            z_positive, z_negative = eigenvalue_split(dimension, trace_z)
            expect(z_positive > 0 and z_negative > 0, "Z_508 misses an eigenvalue on a joint space")
            pieces = four_way(dimension, trace_x, trace_z, trace_xz)
            expect(all(value > 0 for value in pieces.values()), "a sector intersection is empty")
            expect(
                pieces[(1, 0)] + pieces[(1, 1)] == positive,
                "the +1 space of X_3 is not the sum of its Z sectors",
            )
            for key, value in pieces.items():
                sector_total[key] += value
            x_positive += positive
            if chi == 0 and (eps, delta) == (1, 1):
                headline = (dimension, trace_x, positive, negative, pieces)
    expect(sum(dimensions) == 4096, "characters do not cover the block")
    expect(sector_total == {(1, 0): 1024, (1, 1): 1024, (-1, 0): 1024, (-1, 1): 1024},
           "sector intersections do not rebuild the four 1024-dimensional sectors")
    expect(x_positive == 2048, "the +1 space of X_3 is not half the block")
    expect(headline is not None, "the trivial joint space was not reached")
    dimension, trace_x, positive, negative, pieces = headline
    expect(dimension == 216 and trace_x == -48, "the trivial ++ witness moved")
    expect(positive == 84 and negative == 132, "X_3 does not split 216 as 84+132")
    expect(
        pieces == {(1, 0): 42, (1, 1): 42, (-1, 0): 66, (-1, 1): 66},
        "the four sector intersections of the 216-space changed",
    )

    # X_3 and Z_508 are not signed permutations S tensor U, because U fixes 0.
    expect(apply_map(identity["T"], 0) == 0, "the identity label map moves 0")
    expect(SHIFT != 0, "the translation has a fixed address at 0")
    expect(dot(CHARACTER, 0) == 0 and dot(CHARACTER, 4) == 1, "Z_508 does not separate addresses 0 and 4")

    # Rejection controls. Each one must fire; a silent pass is a failure.
    controls = 0
    moved = False
    for address in range(512):
        if apply_map(u["T"], address ^ 1) != (apply_map(u["T"], address) ^ 1):
            moved = True
            break
    expect(moved, "translation by 1 commuted with u")
    controls += 1
    expect(
        any(not commutes_with_character(port, 1) for port in ports),
        "character 1 commuted with every port operator",
    )
    controls += 1
    partial = sign_group[:-1]
    partial_trace = sum(element["trace"] for element in partial)
    expect(
        partial_trace % len(partial) != 0 or partial_trace // len(partial) != 864,
        "dropping a sign still reproduced the trivial dimension",
    )
    controls += 1
    zero_shift = joint_trace("I", 0, 1, 1)
    expect(zero_shift == 216 and zero_shift != trace_x, "the identity trace collapsed onto the X_3 trace")
    controls += 1
    expect(build((1, 0, 2, 3, 4, 5, 6, 7), 0) is None, "a coordinate transposition was accepted")
    controls += 1
    expect(controls == 5, "a rejection control was not reached")

    print("PASS_C3_PAYLOAD_SECTOR3_SPLIT")
    print("trivial ++ dimension", dimension)
    print("X_3 trace", trace_x)
    print("X_3 split", positive, negative)
    print("Z_508 split", dimension // 2, dimension // 2)
    print(
        "sector intersections",
        pieces[(1, 0)],
        pieces[(1, 1)],
        pieces[(-1, 0)],
        pieces[(-1, 1)],
    )
    print("controls", controls)


if __name__ == "__main__":
    main()
