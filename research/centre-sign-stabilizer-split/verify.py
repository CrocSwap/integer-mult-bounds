#!/usr/bin/env python3
"""Exact sign-stabilizer certificate for the doubled centre block at c=1.

The verifier uses only the pinned INTERFACE.json query. It checks two explicit
signed coordinate permutations, the order-16 sign stabilizer, its character
dimensions, and the resulting four 216-dimensional joint eigenspaces.
"""

import hashlib
import json
import pathlib
import sys

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
# sigma^{-1} and output signs: (Sv)_k = eps[k] * v[inv[k]].
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
T_INV = (0, 5, 6, 3, 4, 1, 2, 7)
T_EPS = (1, 1, 1, -1, 1, 1, 1, -1)
CHARACTER_HISTOGRAM = {864: 1, 432: 4, 192: 6, 80: 4, 32: 1}
C3_HISTOGRAM = {864: 1, 432: 4, 192: 6, 80: 4, 32: 1}
C128_HISTOGRAM = {512: 8}


def fail(message):
    raise SystemExit("FAIL: " + message)


def sha256_file(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def load_query():
    if sha256_file(INTERFACE) != INTERFACE_SHA256:
        fail("INTERFACE.json SHA256 does not match the pinned query")
    data = json.loads(INTERFACE.read_text())
    rows = data["R"]
    ports = [int(q) for q in data["ports"]]
    if len(rows) != 8 or len(ports) != 112 or len(set(ports)) != 112:
        fail("query shape is not an 8-by-112 matrix with distinct ports")
    columns = []
    for j in range(112):
        columns.append(tuple(int(rows[i].get(str(j), "0")) for i in range(8)))
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
                for j in range(width):
                    matrix[row][j] ^= matrix[rank][j]
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
    port_of = {columns[j]: ports[j] for j in range(112)}
    lookup = {norm(column): port_of[column] for column in columns}
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
        for i in range(8):
            for k in range(8):
                gram[i][k] += column[i] * column[k]
    if any(gram[i][k] != (56 if i == k else 0) for i in range(8) for k in range(8)):
        fail("RR^T is not 56 I")
    if any(bin(port).count("1") % 2 == 0 for port in ports):
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


def operator(inv, eps, port_of, lookup, basis, coords):
    mapping = {}
    for column, port in port_of.items():
        image = tuple(eps[index] * column[inv[index]] for index in range(8))
        matched = lookup.get(norm(image))
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
    for port in mapping:
        predicted = apply_matrix(matrix, port)
        if predicted != mapping[port]:
            return None
    images = [mapping[vector] for vector in basis]
    for left in range(9):
        for right in range(left, 9):
            if (bin(basis[left] & basis[right]).count("1") & 1) != (
                bin(images[left] & images[right]).count("1") & 1
            ):
                return None
    return {
        "inv": tuple(inv),
        "eps": tuple(eps),
        "T": tuple(matrix),
        "trace": trace_s(inv, eps) * fixed_addresses(matrix),
    }


def compose(left, right):
    inv = tuple(right["inv"][left["inv"][index]] for index in range(8))
    eps = tuple(
        left["eps"][index] * right["eps"][left["inv"][index]] for index in range(8)
    )
    matrix = tuple(apply_matrix(left["T"], column) for column in right["T"])
    return {
        "inv": inv,
        "eps": eps,
        "T": matrix,
        "trace": trace_s(inv, eps) * fixed_addresses(matrix),
    }


def same_operator(left, right):
    return left["inv"] == right["inv"] and left["eps"] == right["eps"] and left["T"] == right["T"]


def sign_group(port_of, lookup, basis, coords, sector):
    identity = tuple(range(8))
    group = []
    for mask in range(128):
        eps = tuple([1] + [-1 if (mask >> bit) & 1 else 1 for bit in range(7)])
        built = operator(identity, eps, port_of, lookup, basis, coords)
        if built is None:
            continue
        if apply_matrix(built["T"], sector) == sector:
            group.append(built)
    return group


def mask_of(eps):
    return sum(1 << bit for bit in range(7) if eps[bit + 1] == -1)


def character_model(group):
    basis = []
    for mask in [mask_of(element["eps"]) for element in group]:
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
            fail("sign stabilizer is not an elementary abelian 2-group")
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
            total += value(chi, mask_of(element["eps"])) * element["trace"]
        if total % order:
            fail("character trace is not divisible by the stabilizer order")
        dims.append(total // order)
    return dims, value


def histogram(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def character_trace(operator_element, group, chi, value):
    total = 0
    for element in group:
        total += value(chi, mask_of(element["eps"])) * compose(operator_element, element)["trace"]
    if total % len(group):
        fail("character trace is not an integer")
    return total // len(group)


def preserves(group, actor, chi, value):
    for element in group:
        image = mask_of(compose(actor, compose(element, actor))["eps"])
        if value(chi, image) != value(chi, mask_of(element["eps"])):
            return False
    return True


def joint_dimensions(identity, first, second, product):
    dims = {}
    for left_sign in (1, -1):
        for right_sign in (1, -1):
            numerator = (
                identity
                + left_sign * first
                + right_sign * second
                + left_sign * right_sign * product
            )
            if numerator % 4 or numerator < 0:
                fail("joint spectral formula is not a nonnegative multiple of 4")
            dims[(left_sign, right_sign)] = numerator // 4
    return dims


def split_preserved(group, actors, identity):
    dims, value = character_model(group)
    if any(value(0, mask_of(element["eps"])) != 1 for element in group):
        fail("character 0 is not the trivial character")
    preserved = [
        chi
        for chi in range(len(dims))
        if all(preserves(group, actor, chi, value) for actor in actors)
    ]
    splits = {}
    for chi in preserved:
        traces = [
            character_trace(element, group, chi, value)
            for element in (identity, actors[0], actors[1], compose(actors[0], actors[1]))
        ]
        splits[chi] = joint_dimensions(*traces)
        if sum(splits[chi].values()) != dims[chi]:
            fail("joint eigenspaces do not cover the character space")
    return dims, preserved, splits


def expect(condition, message):
    if not condition:
        fail(message)


def main():
    columns, ports = load_query()
    port_of, lookup, basis, coords = prepare(columns, ports)
    identity = {
        "inv": tuple(range(8)),
        "eps": (1, 1, 1, 1, 1, 1, 1, 1),
        "T": tuple(1 << bit for bit in range(9)),
        "trace": 8 * 512,
    }
    first = operator(G_INV, G_EPS, port_of, lookup, basis, coords)
    second = operator(T_INV, T_EPS, port_of, lookup, basis, coords)
    expect(first is not None and second is not None, "an explicit splitter is not a symmetry")
    expect(same_operator(compose(first, first), identity), "g is not an involution")
    expect(same_operator(compose(second, second), identity), "t is not an involution")
    expect(same_operator(compose(first, second), compose(second, first)), "g and t do not commute")
    expect(apply_matrix(first["T"], C1) == C1, "g does not preserve sector 1")
    expect(apply_matrix(second["T"], C1) == C1, "t does not preserve sector 1")
    expect(apply_matrix(first["T"], 128) == 128, "g does not preserve sector 128")
    expect(apply_matrix(second["T"], 128) == 128, "t does not preserve sector 128")
    expect(apply_matrix(first["T"], 3) == 343, "g does not send sector 3 to 343")
    expect(apply_matrix(second["T"], 3) == 3, "t does not preserve sector 3")

    group = sign_group(port_of, lookup, basis, coords, C1)
    expect(len(group) == 16, "c=1 sign stabilizer does not have order 16")
    dims, preserved, splits = split_preserved(group, (first, second), identity)
    expect(histogram(dims) == CHARACTER_HISTOGRAM, "c=1 character dimensions changed")
    expect(sum(dims) == 4096, "c=1 character dimensions do not cover the block")
    expect(all(dim > 0 for dim in dims), "a character dimension is not positive")
    expect(sorted(dims[chi] for chi in preserved) == [32, 864], "the preserved c=1 characters are not 864 and 32")
    expect(
        splits[0] == {(1, 1): 216, (1, -1): 216, (-1, 1): 216, (-1, -1): 216},
        "the trivial c=1 space does not split into four blocks of dimension 216",
    )
    small = next(chi for chi in preserved if dims[chi] == 32)
    expect(
        splits[small] == {(1, 1): 8, (1, -1): 8, (-1, 1): 8, (-1, -1): 8},
        "the 32-dimensional c=1 character does not split into four blocks of dimension 8",
    )

    group3 = sign_group(port_of, lookup, basis, coords, 3)
    expect(len(group3) == 16, "c=3 sign stabilizer does not have order 16")
    dims3, _value3 = character_model(group3)
    expect(histogram(dims3) == C3_HISTOGRAM, "c=3 character dimensions changed")

    group128 = sign_group(port_of, lookup, basis, coords, 128)
    expect(len(group128) == 8, "c=128 sign stabilizer does not have order 8")
    dims128, preserved128, splits128 = split_preserved(group128, (first, second), identity)
    expect(histogram(dims128) == C128_HISTOGRAM, "c=128 character dimensions changed")
    expect(len(preserved128) == 4, "c=128 does not have exactly four characters fixed by both involutions")
    expect(0 in preserved128, "the trivial c=128 character is not preserved")
    expect(
        splits128[0][(1, 1)] == 224,
        "the trivial c=128 joint (+1,+1) space does not have dimension 224",
    )
    for chi in preserved128:
        expect(
            histogram(splits128[chi].values()) == {224: 1, 96: 3},
            "a preserved c=128 character does not split as 224+96+96+96",
        )

    # Rejection controls. Each must fail closed without changing the theorem.
    # Every coordinate sign pattern preserves the projective columns, so flipping
    # one sign of g is not a valid negative. A transposition of two query
    # coordinates is not an affine map and must be rejected.
    transposition = (1, 0, 2, 3, 4, 5, 6, 7)
    expect(
        operator(transposition, (1, 1, 1, 1, 1, 1, 1, 1), port_of, lookup, basis, coords)
        is None,
        "a coordinate transposition was accepted as a symmetry",
    )
    noncommuting = None
    for element in group:
        if not same_operator(compose(first, element), compose(element, first)):
            noncommuting = element
            break
    expect(noncommuting is not None, "every sign symmetry commutes with g; the commutativity test is insensitive")
    moved = dict(port_of)
    first_column, second_column = columns[0], columns[1]
    moved[first_column] = port_of[second_column]
    moved[second_column] = port_of[first_column]
    swapped_lookup = {norm(column): moved[column] for column in moved}
    expect(
        operator(G_INV, G_EPS, moved, swapped_lookup, basis, coords) is None,
        "a swapped port label still looked like a symmetry",
    )
    partial = group[:-1]
    partial_trace = sum(element["trace"] for element in partial)
    expect(
        partial_trace % len(partial) != 0 or partial_trace // len(partial) != 864,
        "dropping a stabilizer element still reproduced the trivial dimension",
    )

    print("PASS_CENTRE_SIGN_STABILIZER_SPLIT")
    print("c=1 sign stabilizer order 16")
    print("character dimensions", " ".join(str(dim) for dim in dims))
    print("trivial joint eigenspaces 216 216 216 216")
    print("32-dimensional character joint eigenspaces 8 8 8 8")
    print("c=3 sign stabilizer order 16 with the same dimension histogram")
    print("c=128 four preserved characters each split as 224+96+96+96")


if __name__ == "__main__":
    main()
