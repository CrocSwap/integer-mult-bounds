#!/usr/bin/env python3
"""Census of c=1 signed permutations outside the {g,t} normalizer.

The certificate uses the pinned INTERFACE.json query and the standard library.
It enumerates the line-preserving signed permutations, tests every element of
the c=1 stabilizer against the trivial-character (+1,+1) 216-space, and checks
one explicit witness. It does not compute a characteristic polynomial.
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
SELECTED = ROOT / "certificates/selected-result.json"
INTERFACE_SHA256 = (
    "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
)
SELECTED_KAPPA = "781451/250000000"
C1 = 1
# (S v)_k = eps[k] * v[inv[k]].
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
T_INV = (0, 5, 6, 3, 4, 1, 2, 7)
T_EPS = (1, 1, 1, -1, 1, 1, 1, -1)
U_INV = (0, 1, 2, 3, 7, 6, 5, 4)
U_EPS = (1, 1, 1, 1, 1, 1, 1, 1)
H_EPS = (1, -1, 1, 1, 1, 1, 1, 1)
W_INV = (0, 1, 2, 3, 7, 6, 5, 4)
W_EPS = (1, -1, 1, 1, 1, 1, 1, 1)
# h g h^{-1} has the same coordinate permutation as g and these output signs.
CONJ_EPS = (1, -1, -1, 1, -1, 1, 1, -1)
CHARACTER_HISTOGRAM = {864: 1, 432: 4, 192: 6, 80: 4, 32: 1}
HYPEROCTAHEDRAL_ORDER = 40320 * 256
PRESERVER_TRACES = {216: 64, -216: 64, 72: 192, -72: 192, 24: 128, -24: 128}
OUTSIDE_TRACES = {216: 56, -216: 56, 72: 168, -72: 168, 24: 112, -24: 112}
NORMALIZER_TRACES = {216: 8, -216: 8, 72: 24, -72: 24, 24: 16, -24: 16}

UNPACK = {}


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


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
    cached = UNPACK.get(key)
    if cached is not None:
        return cached
    sign = key & 255
    value = key >> 8
    inv = [0] * 8
    for index in range(7, -1, -1):
        inv[index] = value & 15
        value >>= 4
    eps = tuple(-1 if (sign >> bit) & 1 else 1 for bit in range(8))
    cached = (tuple(inv), eps)
    UNPACK[key] = cached
    return cached


def compose(left, right):
    left_inv, left_eps = unpack(left)
    right_inv, right_eps = unpack(right)
    value = 0
    sign = 0
    for index in range(8):
        src = left_inv[index]
        value = (value << 4) | right_inv[src]
        if left_eps[index] * right_eps[src] < 0:
            sign |= 1 << index
    return (value << 8) | sign


def inverse(key):
    inv, eps = unpack(key)
    dest_of = [0] * 8
    for dest, src in enumerate(inv):
        dest_of[src] = dest
    value = 0
    sign = 0
    for index in range(8):
        src = dest_of[index]
        value = (value << 4) | src
        if eps[src] < 0:
            sign |= 1 << index
    return (value << 8) | sign


def sha256_file(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def load_query():
    if sha256_file(INTERFACE) != INTERFACE_SHA256:
        fail("INTERFACE.json SHA256 does not match the pinned query")
    selected = json.loads(SELECTED.read_text())
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")
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


def nullity(matrix):
    rows = [0] * 9
    for col in range(9):
        bits = matrix[col] ^ (1 << col)
        row = 0
        while bits:
            if bits & 1:
                rows[row] |= 1 << col
            bits >>= 1
            row += 1
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
        for row in range(rank + 1, 9):
            if (rows[row] >> col) & 1:
                rows[row] ^= rows[rank]
        rank += 1
    return 9 - rank


def trace_s(key):
    inv, eps = unpack(key)
    return sum(eps[index] for index in range(8) if inv[index] == index)


def image_vector(key, column):
    inv, eps = unpack(key)
    return tuple(eps[index] * column[inv[index]] for index in range(8))


def operator_t(key, port_of, lookup, basis, coords, check_orthogonal=False):
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
            fail("a published centre symmetry does not preserve the query orthogonally")
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
    return group


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


def histogram(pairs):
    counts = {}
    for value in pairs:
        counts[value] = counts.get(value, 0) + 1
    return counts


def main():
    columns, ports = load_query()
    port_of, lookup, basis, coords = prepare(columns, ports)
    identity = pack(tuple(range(8)), (1,) * 8)
    first = pack(G_INV, G_EPS)
    second = pack(T_INV, T_EPS)
    reflection = pack(U_INV, U_EPS)
    sign = pack(tuple(range(8)), H_EPS)
    witness = pack(W_INV, W_EPS)
    group = build_group(port_of, lookup, basis, coords)
    expect(len(group) == 344064, "the symmetry group generated by the 13 published lifts does not have order 344064")
    reps = coset_representatives(group)
    expect(len(reps) == 30, "the hyperoctahedral coset count is not 30")
    expect(len(group) * len(reps) == HYPEROCTAHEDRAL_ORDER, "the coset decomposition does not cover the hyperoctahedral group")
    outside = [rep for rep in reps if rep != identity and preserves_lines(rep, columns, lookup)]
    expect(not outside, "a signed permutation outside the generated group preserves the root lines")
    traces = {}
    for key, matrix in group.items():
        traces[key] = trace_s(key) * (1 << nullity(matrix))
    expect(traces[identity] == 4096, "the identity trace is not the block dimension")

    stabilizer = [key for key, matrix in group.items() if apply_matrix(matrix, C1) == C1]
    expect(len(stabilizer) == 3072, "the c=1 stabilizer does not have order 3072")
    signs = [
        key
        for key in stabilizer
        if unpack(key)[0] == tuple(range(8)) and unpack(key)[1][0] == 1
    ]
    expect(len(signs) == 16, "the c=1 sign stabilizer does not have order 16")
    expect(histogram(character_traces(signs, traces.get)) == CHARACTER_HISTOGRAM, "the c=1 sign-character histogram changed")

    klein = (identity, first, second, compose(first, second))
    labeled = [compose(factor, element) for factor in klein for element in signs]
    members = set(labeled)
    expect(len(labeled) == 64 and len(members) == 64, "H and {1,g,t,gt} do not give 64 distinct products")
    products = {compose(left, right) for left in members for right in members}
    expect(products == members, "the 64 products are not a group")
    order = len(members)
    member_list = tuple(members)
    total_trace = sum(traces[key] for key in member_list)
    expect(total_trace % order == 0 and total_trace // order == 216, "the M-invariant dimension is not 216")

    def triv(key):
        total = sum(traces[compose(key, element)] for element in signs)
        if total % 16:
            fail("a trivial-character trace is not divisible by 16")
        return total // 16

    joint_numerator = sum(triv(element) for element in klein)
    expect(joint_numerator % 4 == 0 and joint_numerator // 4 == 216, "the ++ joint dimension is not 216")
    expect(triv(identity) == 864, "the trivial character dimension is not 864")

    def conj(actor, element):
        return compose(actor, compose(element, inverse(actor)))

    klein_set = set(klein)
    normalizer = [key for key in stabilizer if {conj(key, element) for element in klein} == klein_set]
    normalizer_set = set(normalizer)
    expect(len(normalizer) == 96, "the normalizer of {1,g,t,gt} does not have order 96")
    expect(reflection in normalizer_set and first in normalizer_set and second in normalizer_set, "u, g, or t is missing from the normalizer")
    denom = order * order

    def correlation(key):
        sinv = inverse(key)
        total = 0
        for left in member_list:
            mid = compose(left, key)
            for right in member_list:
                total += traces[compose(compose(mid, right), sinv)]
        if total % denom:
            fail("a projector correlation is not an integer")
        return total // denom

    def trace_on_e(key):
        total = sum(traces[compose(element, key)] for element in member_list)
        if total % order:
            fail("a trace on E is not an integer")
        return total // order

    correlations = {}
    preservers = []
    for key in stabilizer:
        value = correlation(key)
        correlations[key] = value
        if value == 216:
            preservers.append(key)
    expect(set(correlations.values()) == {0, 216}, "a stabilizer element has a projector correlation other than 0 or 216")
    expect(len(preservers) == 768, "the setwise stabilizer of the ++ space does not have order 768")
    expect(all(key in set(preservers) for key in normalizer), "a normalizer element fails to preserve the ++ space")

    preserver_traces = histogram(trace_on_e(key) for key in preservers)
    outside = [key for key in preservers if key not in normalizer_set]
    outside_traces = histogram(trace_on_e(key) for key in outside)
    normalizer_traces = histogram(trace_on_e(key) for key in normalizer)
    expect(preserver_traces == PRESERVER_TRACES, "the preserver trace histogram changed")
    expect(outside_traces == OUTSIDE_TRACES, "the outside-preserver trace histogram changed")
    expect(normalizer_traces == NORMALIZER_TRACES, "the normalizer trace histogram changed")
    expect(len(outside) == 672, "the number of preserving elements outside the normalizer changed")
    nonscalar = [key for key in outside if trace_on_e(key) not in (216, -216)]
    expect(len(nonscalar) == 560, "the number of non-scalar outside preservers changed")
    expect(768 // PRESERVER_TRACES[216] == 12, "the image of the setwise stabilizer does not have order 12")
    expect(96 // NORMALIZER_TRACES[216] == 12, "the image of the normalizer does not have order 12")

    expect(compose(reflection, sign) == witness, "the witness is not u composed with the coordinate-1 sign")
    expect(compose(sign, reflection) == witness, "the coordinate-1 sign does not commute with u")
    expect(compose(witness, witness) == identity, "the witness is not an involution")
    expect(witness in set(stabilizer) and witness not in normalizer_set, "the witness is not a c=1 element outside the normalizer")
    expect(correlations[witness] == 216 and trace_on_e(witness) == 72, "the witness does not preserve the ++ space with trace 72")
    expect(sign in set(signs) and sign not in normalizer_set, "the coordinate-1 sign is not a sign symmetry outside the normalizer")
    expect(correlations[sign] == 216 and trace_on_e(sign) == 216, "the coordinate-1 sign does not act by +I on the ++ space")
    expect(trace_on_e(reflection) == 72 and reflection not in set(nonscalar), "u is not a normalizer element of trace 72")
    expect(conj(sign, first) == pack(G_INV, CONJ_EPS), "the conjugate of g by the coordinate-1 sign changed")
    expect(conj(sign, first) not in klein_set, "the coordinate-1 sign normalizes g")
    recomputed = operator_t(witness, port_of, lookup, basis, coords, check_orthogonal=True)
    expect(recomputed == group[witness] and apply_matrix(group[witness], C1) == C1, "the witness label map does not fix sector 1")

    omitted = total_trace - traces[first]
    expect(traces[first] != 216 and omitted != 216 * (order - 1), "dropping g from the projector still reproduced the dimension")
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

    print("PASS_C1_216_OUTSIDE_NORMALIZER")
    print("line-preserving signed permutations 344064")
    print("c=1 stabilizer 3072")
    print("++ preservers 768")
    print("outside the normalizer 672")
    print("non-scalar outside 560")
    print("dihedral image order 12")
    print("witness trace 72")
    print("selected kappa 781451/250000000")


if __name__ == "__main__":
    main()
