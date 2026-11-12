#!/usr/bin/env python3
"""Prove an odd minus on u keeps the X_3 trace -48 on (+1, +1).

The explicit c=3 pair from research/c3-centre-sign-split has

    u = (0 2)(4 6) with minus signs on coordinates 0 and 2,
    v = (0 4)(2 6) with minus signs on coordinates 0 and 4.

Open question 2 of the payload-involution certificate asks for the trace of
X_3 after one odd minus sign is added to u. This verifier repeats that trace
for the minus on coordinate 1, then evaluates the same formula on every
diagonal sign supported on the odd coordinates. Acceptance uses explicit
checks, so python -O does not skip a step.
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
SELECTED_SHA256 = (
    "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
)
SELECTED_KAPPA = "781451/250000000"
SECTOR = 3
ALL_ONE = 511
SHIFT = SECTOR
CHARACTER = SECTOR ^ ALL_ONE  # 508
ODDS = (1, 3, 5, 7)
EVENS = (0, 2, 4, 6)
U_SIGMA = (2, 1, 0, 3, 6, 5, 4, 7)  # (0 2)(4 6)
U_MASK = 5  # minus signs on coordinates 0 and 2
V_SIGMA = (4, 1, 6, 3, 0, 5, 2, 7)  # (0 4)(2 6)
V_MASK = 17  # minus signs on coordinates 0 and 4
PRODUCT_SIGMA = (6, 1, 4, 3, 2, 5, 0, 7)  # (0 6)(2 4)
ADDED_COORDINATE = 1
ADDED_MASK = 1 << ADDED_COORDINATE  # 2
JOINT_ORDER = ((1, 1), (1, -1), (-1, 1), (-1, -1))
# Published comparison point: joint dimensions and X_3 traces of the unvaried pair.
EXPECTED_BY_WEIGHT = {
    0: ((216, 216, 216, 216), (-48, 16, 16, 16)),
    1: ((180, 84, 84, 84), (36, -12, -12, -12)),
    2: ((48, 48, 48, 48), (-24, 8, 8, 8)),
    3: ((44, 12, 12, 12), (12, -4, -4, -4)),
    4: ((8, 8, 8, 8), (0, 0, 0, 0)),
}
CHARACTER_DIMENSIONS = (
    864, 432, 432, 192, 432, 192, 192, 80,
    432, 192, 192, 80, 192, 80, 80, 32,
)


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_file(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


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


def odd_masks():
    """Every diagonal sign supported on the odd coordinates, once each."""
    masks = []
    for bits in range(16):
        mask = 0
        for index, coordinate in enumerate(ODDS):
            if (bits >> index) & 1:
                mask |= 1 << coordinate
        masks.append(mask)
    return masks


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
    expect(sha256_file(SELECTED) == SELECTED_SHA256, "selected-result.json hash changed")
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
    return {
        "sigma": sigma,
        "mask": mask,
        "T": matrix,
        "coordinate_trace": coordinate_trace(sigma, mask),
    }


def fixes_labels(matrix):
    return (
        apply_map(matrix, SECTOR) == SECTOR
        and apply_map(matrix, ALL_ONE) == ALL_ONE
        and apply_map(matrix, CHARACTER) == CHARACTER
    )


def commutes_with_shift(matrix):
    for address in range(512):
        if apply_map(matrix, address ^ SHIFT) != (apply_map(matrix, address) ^ SHIFT):
            return False
    return True


def operator_trace(element, translation, character):
    counted = address_trace(element["T"], translation, character)
    return element["coordinate_trace"] * counted


def joint_traces(table, chi):
    """Return (dimensions, X_3 traces) in JOINT_ORDER."""
    dimensions = []
    traces = []
    for eps, delta in JOINT_ORDER:
        dimension_sum = 0
        trace_sum = 0
        for mask in table["masks"]:
            weight = chi_value(chi, mask)
            dimension_sum += weight * (
                table["I"][mask]
                + eps * table["u"][mask]
                + delta * table["v"][mask]
                + eps * delta * table["uv"][mask]
            )
            trace_sum += weight * (
                table["X"]["I"][mask]
                + eps * table["X"]["u"][mask]
                + delta * table["X"]["v"][mask]
                + eps * delta * table["X"]["uv"][mask]
            )
        expect(dimension_sum % 64 == 0, "a joint dimension is not a multiple of 64")
        expect(trace_sum % 64 == 0, "a joint trace is not a multiple of 64")
        dimensions.append(dimension_sum // 64)
        traces.append(trace_sum // 64)
    return tuple(dimensions), tuple(traces)


def build_table(build, identity, sign_group, u_element, v_element):
    product_sigma, product_mask = compose_signed(
        u_element["sigma"], u_element["mask"], v_element["sigma"], v_element["mask"]
    )
    back_sigma, back_mask = compose_signed(
        v_element["sigma"], v_element["mask"], u_element["sigma"], u_element["mask"]
    )
    expect(
        (product_sigma, product_mask) == (back_sigma, back_mask),
        "the varied pair does not commute",
    )
    product = build(product_sigma, product_mask)
    expect(product is not None, "the varied product is not a symmetry")
    bases = {"I": identity, "u": u_element, "v": v_element, "uv": product}
    stored = {"I": {}, "u": {}, "v": {}, "uv": {}, "X": {"I": {}, "u": {}, "v": {}, "uv": {}}}
    cosets = {}
    masks = []
    for name, base in bases.items():
        keys = []
        for member in sign_group:
            if name == "I":
                element = member
            else:
                sigma, mask = compose_signed(
                    base["sigma"], base["mask"], member["sigma"], member["mask"]
                )
                element = build(sigma, mask)
                expect(element is not None, "a varied product left the symmetry representation")
                expect(
                    element["T"] == compose_maps(base["T"], member["T"]),
                    "label maps do not multiply",
                )
            expect(
                compose_signed(element["sigma"], element["mask"], element["sigma"], element["mask"])
                == (tuple(range(8)), 0),
                "a varied group element does not square to the identity",
            )
            both = compose_signed(
                element["sigma"], element["mask"], member["sigma"], member["mask"]
            )
            reverse = compose_signed(
                member["sigma"], member["mask"], element["sigma"], element["mask"]
            )
            expect(both == reverse, "a varied group element does not commute with H")
            expect(fixes_labels(element["T"]), "a varied group element moves sector 3, 511, or 508")
            expect(commutes_with_shift(element["T"]), "X_3 does not commute with a varied group element")
            stored[name][member["mask"]] = operator_trace(element, 0, 0)
            stored["X"][name][member["mask"]] = operator_trace(element, SHIFT, 0)
            keys.append((element["sigma"], element["mask"]))
        cosets[name] = keys
        if name == "I":
            masks = [member["mask"] for member in sign_group]
    stored["masks"] = masks
    stored["product_sigma"] = product_sigma
    stored["product_mask"] = product_mask
    stored["u_mask"] = u_element["mask"]
    stored["cosets"] = cosets
    return stored


def eigenvalue_split(dimension, trace):
    expect((dimension + trace) % 2 == 0, "an involution trace has the wrong parity")
    positive = (dimension + trace) // 2
    negative = (dimension - trace) // 2
    expect(positive >= 0 and negative >= 0, "an eigenvalue dimension is negative")
    return positive, negative


def main():
    columns, ports = load_query()
    lookup, basis_columns, contrib = prepare_labels(columns, ports)

    def build(sigma, mask):
        return realize(lookup, columns, ports, basis_columns, contrib, sigma, mask)

    masks = odd_masks()
    expect(len(masks) == 16 and len(set(masks)) == 16, "the odd signs are not the 16 subsets")
    expect(
        all((mask & sum(1 << bit for bit in EVENS)) == 0 for mask in masks),
        "an odd-sign mask meets an even coordinate",
    )
    expect(ADDED_MASK in masks and ADDED_COORDINATE in ODDS, "coordinate 1 is not an odd sign")
    expect(chi_value(0, ADDED_MASK) == 1, "the trivial character is not +1 on the added sign")
    expect(chi_value(1, ADDED_MASK) == -1, "character 1 is not -1 on coordinate 1")

    identity = build(tuple(range(8)), 0)
    expect(identity is not None, "the identity is not a symmetry")
    expect(operator_trace(identity, 0, 0) == 4096, "the identity trace is not 4096")
    sign_group = []
    for mask in masks:
        element = build(tuple(range(8)), mask)
        expect(element is not None, "a positive-even sign is not a symmetry")
        sign_group.append(element)
    for left in sign_group:
        for right in sign_group:
            expect(
                compose_signed(left["sigma"], left["mask"], right["sigma"], right["mask"])
                == compose_signed(right["sigma"], right["mask"], left["sigma"], left["mask"]),
                "two odd signs do not commute",
            )
    u = build(U_SIGMA, U_MASK)
    v = build(V_SIGMA, V_MASK)
    expect(u is not None and v is not None, "the explicit pair is not a symmetry of the query")
    original = build_table(build, identity, sign_group, u, v)
    expect(original["product_sigma"] == PRODUCT_SIGMA, "the explicit product is not (0 6)(2 4)")
    expect(original["product_mask"] == 65, "the explicit product mask is not 65")
    original_sets = {name: set(original["cosets"][name]) for name in ("I", "u", "v", "uv")}
    expect(len(original_sets["I"]) == 16, "H does not have 16 distinct signs")
    expect(
        all(len(original_sets[name]) == 16 for name in original_sets),
        "a coset of the explicit pair is not 16 elements",
    )
    expect(len(set().union(*original_sets.values())) == 64, "the Klein coset of H is not 64 elements")

    dimensions = []
    for chi in range(16):
        total = sum(chi_value(chi, element["mask"]) * operator_trace(element, 0, 0) for element in sign_group)
        expect(total % 16 == 0, "a character dimension is not integral")
        dimensions.append(total // 16)
    expect(tuple(dimensions) == CHARACTER_DIMENSIONS, "c=3 character dimensions changed")

    original_by_character = {}
    for chi in range(16):
        dims, traces = joint_traces(original, chi)
        weight = bin(chi).count("1")
        expected_dims, expected_traces = EXPECTED_BY_WEIGHT[weight]
        expect(dims == expected_dims, "an unvaried joint dimension changed")
        expect(traces == expected_traces, "an unvaried X_3 joint trace changed")
        original_by_character[chi] = (dims, traces)
    expect(original_by_character[0][1] == (-48, 16, 16, 16), "the comparison trace is not -48, 16, 16, 16")

    trace_by_perm = {}
    for name in ("I", "u", "v", "uv"):
        for mask, key in zip(original["masks"], original["cosets"][name]):
            trace_by_perm[key] = (original[name][mask], original["X"][name][mask])

    assigned = None
    unchanged = 0
    for added in masks:
        varied_sigma, varied_mask = compose_signed(U_SIGMA, U_MASK, tuple(range(8)), added)
        expect(varied_sigma == U_SIGMA, "an odd sign changed the permutation of u")
        expect(varied_mask == (U_MASK ^ added), "an odd sign did not add by disjoint XOR")
        expect((varied_mask & sum(1 << bit for bit in EVENS)) == U_MASK, "an odd sign moved an even minus")
        element = build(varied_sigma, varied_mask)
        expect(element is not None, "an odd sign took u out of the symmetry representation")
        table = build_table(build, identity, sign_group, element, v)
        expect(table["product_sigma"] == PRODUCT_SIGMA, "an odd sign changed the product permutation")
        for name in ("I", "u", "v", "uv"):
            expect(
                set(table["cosets"][name]) == original_sets[name],
                "an odd sign moved a group element out of the explicit Klein coset",
            )
            for mask, key in zip(table["masks"], table["cosets"][name]):
                expect(key in trace_by_perm, "a varied element has no original trace")
                expect(
                    (table[name][mask], table["X"][name][mask]) == trace_by_perm[key],
                    "a fresh address trace disagrees with the same signed permutation",
                )
        for chi in range(16):
            dims, traces = joint_traces(table, chi)
            sign = chi_value(chi, added)
            old_dims, old_traces = original_by_character[chi]
            predicted_dims = []
            predicted_traces = []
            for eps, delta in JOINT_ORDER:
                source = JOINT_ORDER.index((eps * sign, delta))
                predicted_dims.append(old_dims[source])
                predicted_traces.append(old_traces[source])
            expect(dims == tuple(predicted_dims), "a joint dimension missed the character reindexing")
            expect(traces == tuple(predicted_traces), "an X_3 trace missed the character reindexing")
        trivial_dims, trivial_traces = joint_traces(table, 0)
        expect(trivial_dims == (216, 216, 216, 216), "a trivial joint dimension moved")
        expect(trivial_traces == (-48, 16, 16, 16), "the trace -48 moved off (+1,+1) or changed")
        expect(trivial_traces[0] == -48, "the (+1,+1) trace is not -48")
        positive, negative = eigenvalue_split(trivial_dims[0], trivial_traces[0])
        expect(positive == 84 and negative == 132, "the (+1,+1) split is not 84+132")
        unchanged += 1
        if added == ADDED_MASK:
            assigned = (table, trivial_dims, trivial_traces, positive, negative)

    expect(unchanged == 16, "the odd-sign census did not cover 16 patterns")
    expect(assigned is not None, "the coordinate-1 pair was not evaluated")
    table, trivial_dims, trivial_traces, positive, negative = assigned
    expect(table["u_mask"] == 7, "the assigned mask is not 7")
    expect(table["product_mask"] == 67, "the assigned product mask is not 67")
    moved_dims, moved_traces = joint_traces(table, 1)
    expect(moved_dims == (84, 84, 180, 84), "character 1 did not move its large dimension")
    expect(moved_traces == (-12, -12, 36, -12), "character 1 did not move its trace 36")
    expect(-48 not in moved_traces, "the trace -48 appeared on the moved weight-1 character")
    # Character 2 is the weight-1 character on coordinate 3. It is +1 on coordinate 1.
    stayed_dims, stayed_traces = joint_traces(table, 2)
    expect(chi_value(2, ADDED_MASK) == 1, "character 2 is not +1 on coordinate 1")
    expect(stayed_dims == (180, 84, 84, 84), "a weight-1 character fixed by the added sign moved its dimensions")
    expect(stayed_traces == (36, -12, -12, -12), "a weight-1 character fixed by the added sign moved its traces")
    expect(coordinate_trace(U_SIGMA, 7) == 2, "the assigned representative did not change coordinate trace")
    expect(coordinate_trace(U_SIGMA, U_MASK) == 4, "the unvaried coordinate trace is not 4")

    controls = 0
    even_flip = build(U_SIGMA, U_MASK ^ 1)
    expect(even_flip is not None, "the even-coordinate control was not a symmetry")
    expect(apply_map(even_flip["T"], SECTOR) == 470, "flipping coordinate 0 did not send sector 3 to 470")
    expect(apply_map(even_flip["T"], SECTOR) != SECTOR, "an even sign flip still fixed sector 3")
    controls += 1

    identity_trace = joint_traces(table, 0)[0][0]
    expect(identity_trace == 216 and identity_trace != trivial_traces[0], "the identity trace collapsed onto -48")
    controls += 1

    def plus_term(mask):
        return (
            table["X"]["I"][mask]
            + table["X"]["u"][mask]
            + table["X"]["v"][mask]
            + table["X"]["uv"][mask]
        )

    full_numerator = sum(plus_term(mask) for mask in table["masks"])
    expect(full_numerator == -48 * 64, "the assigned numerator is not -48 times 64")
    changed = [
        full_numerator - plus_term(mask)
        for mask in table["masks"]
        if plus_term(mask) != 0
    ]
    expect(changed, "every sign had a zero (+1,+1) contribution, so truncation was vacuous")
    expect(
        all(partial != -48 * 64 for partial in changed),
        "dropping a nonzero sign still reproduced the trace -48",
    )
    controls += 1

    moved = False
    assigned_u = build(U_SIGMA, 7)
    for address in range(512):
        if apply_map(assigned_u["T"], address ^ 1) != (apply_map(assigned_u["T"], address) ^ 1):
            moved = True
            break
    expect(moved, "translation by 1 commuted with the assigned u")
    controls += 1
    expect(build((1, 0, 2, 3, 4, 5, 6, 7), 0) is None, "a coordinate transposition was accepted")
    controls += 1
    expect(controls == 5, "a rejection control was not reached")

    print("PASS_C3_ODD_SIGN_TRACE_SLOT")
    print("assigned coordinate", ADDED_COORDINATE)
    print("assigned u mask", table["u_mask"])
    print("assigned product mask", table["product_mask"])
    print("trivial X traces", *trivial_traces)
    print("trace -48 slot +1 +1")
    print("plus split", positive, negative)
    print("weight-1 character 1 traces", *moved_traces)
    print("odd patterns", unchanged)
    print("controls", controls)


if __name__ == "__main__":
    main()
