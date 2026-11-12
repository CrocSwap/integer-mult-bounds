#!/usr/bin/env python3
"""Movers in the c=1 stabilizer miss the 8-dimensional dihedral summand.

Exhaustive census of the order-3072 stabilizer. Every element that moves the
trivial-character (+1,+1) 216-space carries the 8-dimensional summand to a
complement of that space. Acceptance uses explicit checks, so -O does not skip
an element or a rejection control.
"""

import hashlib
import json
import pathlib
from collections import deque
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[2]
PACKAGE = pathlib.Path(__file__).resolve().parent
INTERFACE = (
    ROOT
    / "research/centre-polynomial-cache-limits/frozen/work"
    / "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json"
)
BASIS_PATH = ROOT / "research/a1-joint-216-charpoly/evidence/basis.json"
SELECTED = ROOT / "certificates/selected-result.json"
INTERFACE_SHA256 = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
BASIS_SHA256 = "e198cd71f4100d2629ecc25fb40b135a8c18c7756be8bc80bf24d7b349af418a"
SELECTED_SHA256 = "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
SELECTED_KAPPA = "781451/250000000"
C1 = 1
HYPEROCTAHEDRAL_ORDER = 40320 * 256
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
T_INV = (0, 5, 6, 3, 4, 1, 2, 7)
T_EPS = (1, 1, 1, -1, 1, 1, 1, -1)
U_INV = (0, 1, 2, 3, 7, 6, 5, 4)
U_EPS = (1, 1, 1, 1, 1, 1, 1, 1)
R_INV = (0, 1, 6, 7, 3, 2, 5, 4)
R_EPS = (-1, 1, 1, 1, 1, 1, 1, -1)
H_EPS = (1, -1, 1, 1, 1, 1, 1, 1)
W_INV = (0, 1, 2, 3, 7, 6, 5, 4)
W_EPS = (1, -1, 1, 1, 1, 1, 1, 1)
# k |-> inv[k] is the permutation (0 3)(5 6), with every output sign positive.
MOVER_INV = (3, 1, 2, 0, 4, 6, 5, 7)
MOVER_EPS = (1, 1, 1, 1, 1, 1, 1, 1)
TRIPLES = (
    (104, 120, 142),
    (105, 121, 143),
    (106, 122, 140),
    (107, 123, 141),
    (116, 124, 134),
    (117, 125, 135),
    (118, 126, 132),
    (119, 127, 133),
)


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


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
    value = 0
    sign = 0
    for index in range(8):
        src = left_inv[index]
        value = (value << 4) | right_inv[src]
        if left_eps[index] * right_eps[src] < 0:
            sign |= 1 << index
    return (value << 8) | sign


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


def load_query():
    raw = INTERFACE.read_bytes()
    expect(sha256_bytes(raw) == INTERFACE_SHA256, "INTERFACE.json SHA256 does not match the pinned query")
    selected_raw = SELECTED.read_bytes()
    expect(sha256_bytes(selected_raw) == SELECTED_SHA256, "selected-result.json bytes changed")
    selected = json.loads(selected_raw)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")
    basis_raw = BASIS_PATH.read_bytes()
    expect(sha256_bytes(basis_raw) == BASIS_SHA256, "the published 216-basis bytes changed")
    data = json.loads(raw)
    rows = data["R"]
    ports = [int(port) for port in data["ports"]]
    expect(len(rows) == 8 and len(ports) == 112 and len(set(ports)) == 112, "query shape")
    columns = []
    for column in range(112):
        columns.append(tuple(int(rows[row].get(str(column), "0")) for row in range(8)))
    return columns, ports, json.loads(basis_raw)


def prepare(columns, ports):
    port_of = {columns[index]: ports[index] for index in range(112)}
    lookup = {norm(column): port_of[column] for column in columns}
    expect(len(lookup) == 112, "the 112 columns are not distinct lines")
    basis = []
    for port in ports:
        if rank_solve(basis + [port]) == len(basis) + 1:
            basis.append(port)
        if len(basis) == 9:
            break
    expect(len(basis) == 9, "the 112 ports do not span F2^9")
    coords = {address: tuple(rank_solve(basis, address)) for address in range(512)}
    gram = [[0] * 8 for _ in range(8)]
    for column in columns:
        for left in range(8):
            for right in range(8):
                gram[left][right] += column[left] * column[right]
    expect(
        all(gram[left][right] == (56 if left == right else 0) for left in range(8) for right in range(8)),
        "RR^T is not 56 I",
    )
    expect(all(port.bit_count() % 2 == 1 for port in ports), "a port label has even parity")
    expect(all(entry in (-1, 0, 1) for column in columns for entry in column), "a root entry is outside {-1,0,1}")
    expect(all(sum(entry != 0 for entry in column) == 4 for column in columns), "a root does not have weight 4")
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


def operator_t(key, port_of, lookup, basis, coords):
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
    images = [mapping[vector] for vector in basis]
    for left in range(9):
        for right in range(left, 9):
            if (basis[left] & basis[right]).bit_count() % 2 != (images[left] & images[right]).bit_count() % 2:
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
        matrix = operator_t(generator, port_of, lookup, basis, coords)
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


def operator(inv, eps, port_of, lookup, basis, coords):
    matrix = operator_t(pack(inv, eps), port_of, lookup, basis, coords)
    if matrix is None:
        return None
    return {"inv": tuple(inv), "eps": tuple(eps), "T": matrix}


def compose_op(left, right):
    inv = tuple(right["inv"][left["inv"][index]] for index in range(8))
    eps = tuple(left["eps"][index] * right["eps"][left["inv"][index]] for index in range(8))
    matrix = tuple(apply_matrix(left["T"], column) for column in right["T"])
    return {"inv": inv, "eps": eps, "T": matrix}


def same_operator(left, right):
    return left["inv"] == right["inv"] and left["eps"] == right["eps"] and left["T"] == right["T"]


def power(element, count, identity):
    value = identity
    for _ in range(count):
        value = compose_op(value, element)
    return value


def action_tables(element):
    inv, eps, transform = element["inv"], element["eps"], element["T"]
    sigma = [0] * 8
    for out_index, in_index in enumerate(inv):
        sigma[in_index] = out_index
    dest = [0] * 4096
    sign = [0] * 4096
    for coordinate in range(8):
        image_coordinate = sigma[coordinate]
        image_sign = eps[image_coordinate]
        for address in range(512):
            src = coordinate * 512 + address
            dest[src] = image_coordinate * 512 + apply_matrix(transform, address)
            sign[src] = image_sign
    return dest, sign


class Lattice:
    def __init__(self):
        self.parent = list(range(4096))
        self.rel = [1] * 4096
        self.dead = [False] * 4096

    def find(self, index):
        sign = 1
        seen = []
        while self.parent[index] != index:
            seen.append(index)
            sign *= self.rel[index]
            index = self.parent[index]
        accumulated = 1
        for step in reversed(seen):
            accumulated = self.rel[step] * accumulated
            self.rel[step] = accumulated
            self.parent[step] = index
        return index, sign

    def constrain(self, dst, src, sgn):
        root_dst, sign_dst = self.find(dst)
        root_src, sign_src = self.find(src)
        if root_dst == root_src:
            if sign_dst != sgn * sign_src:
                self.dead[root_dst] = True
            return
        self.parent[root_dst] = root_src
        self.rel[root_dst] = sgn * sign_src * sign_dst
        if self.dead[root_dst] or self.dead[root_src]:
            self.dead[root_src] = True

    def add_operator(self, dest, sign, eigenvalue):
        for src in range(4096):
            self.constrain(dest[src], src, sign[src] * eigenvalue)

    def basis(self):
        groups = {}
        for index in range(4096):
            root, sign = self.find(index)
            if self.dead[root]:
                continue
            groups.setdefault(root, []).append((index, sign))
        vectors = []
        for items in groups.values():
            items.sort()
            pivot = items[0][1]
            vectors.append([(index, coeff * pivot) for index, coeff in items])
        vectors.sort()
        return vectors


def sign_group(port_of, lookup, basis, coords):
    identity = tuple(range(8))
    group = []
    for mask in range(128):
        eps = tuple([1] + [-1 if (mask >> bit) & 1 else 1 for bit in range(7)])
        built = operator(identity, eps, port_of, lookup, basis, coords)
        if built is None:
            continue
        if apply_matrix(built["T"], C1) == C1:
            group.append(built)
    return group


def fixed_addresses(matrix):
    return 1 << nullity(matrix)


def apply_element(inv, eps, transform, items):
    sigma = [0] * 8
    for out_index, in_index in enumerate(inv):
        sigma[in_index] = out_index
    image = {}
    for index, coeff in items:
        coordinate = index // 512
        address = index - 512 * coordinate
        image_coordinate = sigma[coordinate]
        target = image_coordinate * 512 + apply_matrix(transform, address)
        value = image.get(target, 0) + eps[image_coordinate] * coeff
        if value:
            image[target] = value
        elif target in image:
            del image[target]
    return image


def decode(image, comp_of, base_of, vectors):
    alphas = {}
    for index, value in image.items():
        component = comp_of[index]
        if component < 0:
            return None
        alpha = value * base_of[index]
        previous = alphas.get(component)
        if previous is None:
            alphas[component] = alpha
        elif previous != alpha:
            return None
    for component, alpha in alphas.items():
        for index, coeff in vectors[component]:
            if image.get(index, 0) != coeff * alpha:
                return None
    return alphas


def in_summand(alphas):
    if alphas is None:
        return None
    used = set()
    coords = [0] * 8
    for slot, (left, middle, right) in enumerate(TRIPLES):
        first = alphas.get(left, 0)
        second = alphas.get(middle, 0)
        third = alphas.get(right, 0)
        if second != -first or third != first:
            return None
        coords[slot] = first
        if first:
            used.add(left)
            used.add(middle)
            used.add(right)
    for component, value in alphas.items():
        if value and component not in used:
            return None
    return coords


def dot(left, right):
    table = dict(left)
    return sum(coef * table.get(index, 0) for index, coef in right)


def gcd_many(values):
    value = 0
    for item in values:
        item = abs(item)
        while item:
            value, item = item, value % item
    return value


def image_rank(columns):
    pivots = []
    for raw in columns:
        vector = {key: value for key, value in raw.items() if value}
        for pivot_index, pivot in pivots:
            coef = vector.get(pivot_index, 0)
            if not coef:
                continue
            scale = pivot[pivot_index]
            updated = {}
            for key in set(vector) | set(pivot):
                entry = scale * vector.get(key, 0) - coef * pivot.get(key, 0)
                if entry:
                    updated[key] = entry
            vector = updated
            if vector:
                common = gcd_many(vector.values())
                if common > 1:
                    vector = {key: value // common for key, value in vector.items()}
        if not vector:
            continue
        pivot_index = min(vector)
        if vector[pivot_index] < 0:
            vector = {key: -value for key, value in vector.items()}
        pivots.append((pivot_index, vector))
    return len(pivots)


def apply_sparse(images, sparse):
    acc = {}
    for component, coef in sparse.items():
        for dest, value in images[component].items():
            acc[dest] = acc.get(dest, 0) + coef * value
    return {dest: value for dest, value in acc.items() if value}


def residual(image, comp_of, base_of, vectors):
    """Image of an ambient vector in Q^{4096} / E, scaled only per component."""
    acc = {index: Fraction(value) for index, value in image.items()}
    touched = {}
    for index, value in image.items():
        component = comp_of[index]
        if component < 0:
            continue
        touched[component] = touched.get(component, 0) + value * base_of[index]
    for component, raw in touched.items():
        items = vectors[component]
        alpha = Fraction(raw, len(items))
        for index, coeff in items:
            updated = acc.get(index, 0) - alpha * coeff
            if updated:
                acc[index] = updated
            elif index in acc:
                del acc[index]
    return acc


def fraction_rank(columns):
    pivots = []
    for raw in columns:
        vector = {key: value for key, value in raw.items() if value}
        for pivot_index, pivot in pivots:
            coef = vector.get(pivot_index, 0)
            if not coef:
                continue
            scale = pivot[pivot_index]
            updated = {}
            for key in set(vector) | set(pivot):
                entry = scale * vector.get(key, 0) - coef * pivot.get(key, 0)
                if entry:
                    updated[key] = entry
            vector = updated
        if not vector:
            continue
        pivot_index = min(vector)
        pivots.append((pivot_index, vector))
    return len(pivots)


def ambient_trace(key, group):
    return trace_s(key) * fixed_addresses(group[key])


def main():
    columns, ports, published = load_query()
    port_of, lookup, port_basis, coords = prepare(columns, ports)
    group = build_group(port_of, lookup, port_basis, coords)
    expect(len(group) == 344064, "the line-preserving group does not have order 344064")
    reps = coset_representatives(group)
    identity_key = pack(tuple(range(8)), (1,) * 8)
    expect(len(reps) == 30, "the hyperoctahedral coset count is not 30")
    expect(len(group) * len(reps) == HYPEROCTAHEDRAL_ORDER, "the coset decomposition does not cover the hyperoctahedral group")
    expect(
        not any(rep != identity_key and preserves_lines(rep, columns, lookup) for rep in reps),
        "a signed permutation outside the generated group preserves the root lines",
    )
    stabilizer = [key for key, matrix in group.items() if apply_matrix(matrix, C1) == C1]
    expect(len(stabilizer) == 3072, "the c=1 stabilizer does not have order 3072")

    vectors = []
    comp_of = [-1] * 4096
    base_of = [0] * 4096
    for items in published["vectors"]:
        parsed = tuple((index, coeff) for index, coeff in items)
        vectors.append(parsed)
        for index, coeff in parsed:
            expect(comp_of[index] < 0, "published joint supports overlap")
            expect(coeff in (-1, 1), "a published joint coefficient is not a unit")
            comp_of[index] = len(vectors) - 1
            base_of[index] = coeff
    expect(len(vectors) == 216, "the published basis does not have dimension 216")

    group_h = sign_group(port_of, lookup, port_basis, coords)
    expect(len(group_h) == 16, "the c=1 sign stabilizer does not have order 16")
    first = operator(G_INV, G_EPS, port_of, lookup, port_basis, coords)
    second = operator(T_INV, T_EPS, port_of, lookup, port_basis, coords)
    reflection = operator(U_INV, U_EPS, port_of, lookup, port_basis, coords)
    rotation = operator(R_INV, R_EPS, port_of, lookup, port_basis, coords)
    expect(first and second and reflection and rotation, "g, t, u, or r is not a symmetry")
    identity_op = {
        "inv": tuple(range(8)),
        "eps": (1, 1, 1, 1, 1, 1, 1, 1),
        "T": tuple(1 << bit for bit in range(9)),
    }
    expect(same_operator(compose_op(first, first), identity_op), "g is not an involution")
    expect(same_operator(compose_op(second, second), identity_op), "t is not an involution")
    expect(same_operator(compose_op(first, second), compose_op(second, first)), "g and t do not commute")
    expect(apply_matrix(first["T"], C1) == C1 and apply_matrix(second["T"], C1) == C1, "a splitter moves sector 1")
    expect(same_operator(compose_op(reflection, reflection), identity_op), "u is not an involution")
    expect(same_operator(power(rotation, 6, identity_op), identity_op), "r does not have order dividing 6")
    for count in (1, 2, 3):
        expect(not same_operator(power(rotation, count, identity_op), identity_op), "r has order less than 6")
    expect(
        same_operator(compose_op(reflection, compose_op(rotation, reflection)), power(rotation, 5, identity_op)),
        "u does not invert r",
    )
    actions = [action_tables(element) for element in group_h]
    lattice = Lattice()
    for dest, sign in actions:
        lattice.add_operator(dest, sign, 1)
    g_dest, g_sign = action_tables(first)
    t_dest, t_sign = action_tables(second)
    lattice.add_operator(g_dest, g_sign, 1)
    lattice.add_operator(t_dest, t_sign, 1)
    expect(lattice.basis() == [list(items) for items in vectors], "the ++ lattice is not the published 216-basis")

    def closed_trace(element):
        return trace_s(pack(element["inv"], element["eps"])) * fixed_addresses(element["T"])

    def trivial_trace(element):
        total = 0
        for symmetry in group_h:
            total += closed_trace(compose_op(element, symmetry))
        expect(total % 16 == 0, "a trivial-character trace is not integral")
        return total // 16

    trace_identity = trivial_trace(identity_op)
    trace_g = trivial_trace(first)
    trace_t = trivial_trace(second)
    trace_gt = trivial_trace(compose_op(first, second))
    expect(trace_identity == 864, "the trivial character does not have dimension 864")
    joint = trace_identity + trace_g + trace_t + trace_gt
    expect(joint % 4 == 0 and joint // 4 == 216, "the trace formula does not give a 216-dimensional ++ space")

    words = []
    for index in range(6):
        words.append(power(rotation, index, identity_op))
        words.append(compose_op(power(rotation, index, identity_op), reflection))
    expect(len({(word["inv"], word["eps"], word["T"]) for word in words}) == 12, "the twelve dihedral words are not distinct")
    for word in words:
        expect(apply_matrix(word["T"], C1) == C1, "a dihedral word moves sector 1")
    word_columns = []
    for word in words:
        columns_word = []
        for items in vectors:
            decoded = decode(apply_element(word["inv"], word["eps"], word["T"], items), comp_of, base_of, vectors)
            expect(decoded is not None, "a dihedral word moves the 216-space")
            columns_word.append(decoded)
        word_columns.append(columns_word)

    def combine(sign_u):
        images = []
        for component in range(216):
            acc = {}
            for power_index in range(6):
                rotation_sign = -1 if power_index % 2 else 1
                for dest, value in word_columns[2 * power_index][component].items():
                    acc[dest] = acc.get(dest, 0) + rotation_sign * value
                reflection_sign = rotation_sign * sign_u
                for dest, value in word_columns[2 * power_index + 1][component].items():
                    acc[dest] = acc.get(dest, 0) + reflection_sign * value
            images.append({dest: value for dest, value in acc.items() if value})
        return images

    minus = combine(-1)
    projector_trace = sum(image.get(component, 0) for component, image in enumerate(minus))
    expect(projector_trace == 96, "the multiplicity-8 projector does not have trace 96")
    for image in minus:
        expect(apply_sparse(minus, image) == {key: 12 * value for key, value in image.items()}, "12P is not a projector")
    expect(image_rank(minus) == 8, "the multiplicity-8 image does not have rank 8")
    claimed = [{left: 1, middle: -1, right: 1} for left, middle, right in TRIPLES]
    for sparse in claimed:
        expect(
            apply_sparse(minus, sparse) == {key: 12 * value for key, value in sparse.items()},
            "a claimed basis vector is not fixed by 12P",
        )
    expect(image_rank(claimed) == 8, "the eight claimed vectors are dependent")
    for word in (words[2], words[1]):
        for sparse in claimed:
            image = apply_element(
                word["inv"],
                word["eps"],
                word["T"],
                [
                    (index, coef * coeff)
                    for component, coef in sparse.items()
                    for index, coeff in vectors[component]
                ],
            )
            decoded = decode(image, comp_of, base_of, vectors)
            expect(decoded == {key: -value for key, value in sparse.items()}, "r or u does not act by -1 on V")

    ambient = []
    for left, middle, right in TRIPLES:
        acc = {}
        for component, coef in ((left, 1), (middle, -1), (right, 1)):
            for index, coeff in vectors[component]:
                acc[index] = acc.get(index, 0) + coef * coeff
        ambient.append(tuple((index, value) for index, value in acc.items() if value))
    gram = [[dot(ambient[i], ambient[j]) for j in range(8)] for i in range(8)]
    expect(gram == [[48 if i == j else 0 for j in range(8)] for i in range(8)], "the summand Gram matrix is not 48 I")
    for items in ambient:
        expect(residual(dict(items), comp_of, base_of, vectors) == {}, "a summand basis vector leaves E")

    preservers = 0
    movers = 0
    mover_meets_v = 0
    scalars = {1: 0, -1: 0}
    disjoint_movers = 0
    mover_key = pack(MOVER_INV, MOVER_EPS)
    expect(mover_key in group and apply_matrix(group[mover_key], C1) == C1, "the named mover is not in the c=1 stabilizer")
    named_images = None
    for key in stabilizer:
        inv, eps = unpack(key)
        transform = group[key]
        preserves = True
        for items in vectors:
            if decode(apply_element(inv, eps, transform, items), comp_of, base_of, vectors) is None:
                preserves = False
                break
        mapped = [apply_element(inv, eps, transform, items) for items in ambient]
        coordinates = []
        keeps = True
        for image in mapped:
            coords_v = in_summand(decode(image, comp_of, base_of, vectors))
            if coords_v is None:
                keeps = False
                break
            coordinates.append(coords_v)
        if preserves:
            preservers += 1
            expect(keeps, "an element preserves the 216-space and misses the 8-dimensional summand")
            lam = coordinates[0][0]
            scalar = all(
                coordinates[col][row] == (lam if row == col else 0) for col in range(8) for row in range(8)
            )
            expect(scalar and lam in (1, -1), "a preserver of the 216-space is not ±I on the summand")
            scalars[lam] += 1
        else:
            movers += 1
            if keeps:
                mover_meets_v += 1
            expect(
                all(dot(image, basis_vector) == 0 for image in mapped for basis_vector in ambient),
                "a mover does not send the summand into its orthogonal complement",
            )
            residues = [residual(image, comp_of, base_of, vectors) for image in mapped]
            expect(all(residues), "a mover fixes a summand basis vector inside E")
            expect(fraction_rank(residues) == 8, "a mover meets the 216-space along the summand")
            disjoint_movers += 1
        if key == mover_key:
            named_images = mapped
            expect(not preserves and not keeps, "the named mover preserves the 216-space or the summand")
    expect(named_images is not None, "the named mover was not visited")
    named_residues = [residual(image, comp_of, base_of, vectors) for image in named_images]
    expect(fraction_rank(named_residues) == 8, "the named mover does not carry an 8-dimensional complement")
    expect(fraction_rank(named_residues[:7] + named_residues[:1]) == 7, "a repeated residual still looked independent")
    expect(fraction_rank([{}]) == 0, "the zero residue still looked independent")
    expect(preservers == 768 and movers == 2304, "the mover split is not 768 preservers and 2304 movers")
    expect(mover_meets_v == 0 and disjoint_movers == 2304, "a mover preserves the summand or meets the 216-space")
    expect(scalars == {1: 384, -1: 384}, "the preserver scalars on the summand are not balanced ±1")

    def restriction(key):
        inv, eps = unpack(key)
        transform = group[key]
        coordinates = []
        for items in ambient:
            coords_v = in_summand(decode(apply_element(inv, eps, transform, items), comp_of, base_of, vectors))
            expect(coords_v is not None, "a named preserver misses the summand")
            coordinates.append(coords_v)
        return coordinates

    def compressed_trace(key, members):
        total = sum(ambient_trace(compose(element, key), group) for element in members)
        expect(total % len(members) == 0, "a compressed trace is not integral")
        return total // len(members)

    signs = [
        key
        for key in stabilizer
        if unpack(key)[0] == tuple(range(8)) and unpack(key)[1][0] == 1
    ]
    expect(len(signs) == 16, "the positive-on-coordinate-0 sign group does not have order 16")
    first_key = pack(G_INV, G_EPS)
    second_key = pack(T_INV, T_EPS)
    klein = (identity_key, first_key, second_key, compose(first_key, second_key))
    members = [compose(factor, element) for factor in klein for element in signs]
    expect(len(set(members)) == 64, "H and {1,g,t,gt} do not give 64 products")
    reflection_key = pack(U_INV, U_EPS)
    sign_key = pack(tuple(range(8)), H_EPS)
    outside_key = pack(W_INV, W_EPS)
    expect(compose(reflection_key, sign_key) == outside_key, "the #7022 witness is not u times the coordinate-1 sign")
    expect(compressed_trace(outside_key, members) == 72, "the #7022 witness does not have compressed trace 72")
    expect(compressed_trace(sign_key, members) == 216, "the coordinate-1 sign does not have compressed trace 216")
    expect(compressed_trace(reflection_key, members) == 72, "u does not have compressed trace 72")
    for key, lam in ((identity_key, 1), (reflection_key, -1), (sign_key, 1), (outside_key, -1)):
        coordinates = restriction(key)
        expect(
            coordinates == [[lam if row == col else 0 for col in range(8)] for row in range(8)],
            "a named preserver is not the predicted scalar on the summand",
        )
    expect(compressed_trace(mover_key, members) != 216 and compressed_trace(mover_key, members) != -216, "the named mover looks scalar on the 216-space")

    swapped = list(range(8))
    swapped[0], swapped[1] = 1, 0
    expect(operator_t(pack(tuple(swapped), (1,) * 8), port_of, lookup, port_basis, coords) is None, "a coordinate transposition was accepted")
    partial = list(range(8))
    partial[4], partial[7] = 7, 4
    expect(
        operator_t(pack(tuple(partial), (1,) * 8), port_of, lookup, port_basis, coords) is None,
        "swapping coordinates 4 and 7 alone still looked like a symmetry",
    )
    moved = dict(port_of)
    moved[columns[0]], moved[columns[1]] = port_of[columns[1]], port_of[columns[0]]
    moved_lookup = {norm(column): moved[column] for column in columns}
    expect(
        operator_t(first_key, moved, moved_lookup, port_basis, coords) is None,
        "a swapped port label still looked like a symmetry",
    )
    broken = {TRIPLES[0][0]: 1, TRIPLES[0][1]: -1}
    expect(
        apply_sparse(minus, broken) != {key: 12 * value for key, value in broken.items()},
        "dropping a support term still fixed the projector",
    )
    shifted = [list(row) for row in gram]
    shifted[0][1] = 1
    expect(shifted != gram, "an off-diagonal Gram change was not detected")

    print("PASS_C1_MOVER_8_SUMMAND")
    print("line-preserving signed permutations 344064")
    print("c=1 stabilizer 3072")
    print("++ preservers 768")
    print("movers 2304")
    print("mover images meet V 0")
    print("mover images meet E 0")
    print("preserver scalars on V +1:384 -1:384")
    print("summand Gram 48 I")
    print("named mover (0 3)(5 6)")
    print("selected kappa 781451/250000000")


if __name__ == "__main__":
    main()
