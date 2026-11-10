#!/usr/bin/env python3
"""Transporter of the 8-dimensional c=1 joint basis outside <H, g, t>.

The pinned query is the historical 8-by-112 centre matrix. This census lists
the order-3072 stabilizer of sector c=1 and tests which elements carry the
#7019 (+1,+1) basis onto another joint space of g and t. Acceptance uses
explicit checks, so -O does not skip a census step or a rejection control.
"""

import hashlib
import itertools
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PACKAGE = pathlib.Path(__file__).resolve().parent
INTERFACE = (
    ROOT
    / "research/centre-polynomial-cache-limits/frozen/work"
    / "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json"
)
SELECTED = ROOT / "certificates/selected-result.json"
INTERFACE_SHA256 = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
SELECTED_SHA256 = "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
SELECTED_KAPPA = "781451/250000000"
C1 = 1
SIGN_COORDINATES = (1, 2, 5, 6)
SUBSPACE = (0, 3, 4, 7)
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
T_INV = (0, 5, 6, 3, 4, 1, 2, 7)
T_EPS = (1, 1, 1, -1, 1, 1, 1, -1)
JOINT_COORDINATE = {(1, 1): 0, (1, -1): 3, (-1, 1): 4, (-1, -1): 7}
EXPECTED_ROOTS = (128, 129, 134, 135, 170, 171, 172, 173)
EXPECTED_FIRST = (
    (128, 1),
    (158, 1),
    (230, 1),
    (248, 1),
    (256, -1),
    (286, -1),
    (358, -1),
    (376, -1),
)
# Unsigned involution (0 3)(5 6). Stored as sigma[source] = image.
WITNESS_SIGMA = (3, 1, 2, 0, 4, 6, 5, 7)
WITNESS_EPS = (1, 1, 1, 1, 1, 1, 1, 1)
EXPECTED_MATRIX = (
    (4, -4, 0, 0, 0, 0, 0, 0),
    (-4, 4, 0, 0, 0, 0, 0, 0),
    (0, 0, -4, -4, 0, 0, 0, 0),
    (0, 0, -4, -4, 0, 0, 0, 0),
    (0, 0, 0, 0, 4, -4, 0, 0),
    (0, 0, 0, 0, -4, 4, 0, 0),
    (0, 0, 0, 0, 0, 0, -4, -4),
    (0, 0, 0, 0, 0, 0, -4, -4),
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


def rank_solve(vectors):
    width = len(vectors)
    matrix = [[(vector >> row) & 1 for vector in vectors] for row in range(9)]
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
        for row in range(9):
            if row != rank and matrix[row][col]:
                for entry in range(width):
                    matrix[row][entry] ^= matrix[rank][entry]
        rank += 1
        if rank == 9:
            break
    return rank


def rank_coordinates(vectors, target):
    width = len(vectors)
    matrix = [[(vector >> row) & 1 for vector in vectors] for row in range(9)]
    image = [(target >> row) & 1 for row in range(9)]
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
        image[rank], image[pivot] = image[pivot], image[rank]
        for row in range(9):
            if row != rank and matrix[row][col]:
                for entry in range(width):
                    matrix[row][entry] ^= matrix[rank][entry]
                image[row] ^= image[rank]
        pivot_at[rank] = col
        rank += 1
        if rank == 9:
            break
    if any(image[row] for row in range(rank, 9)):
        return None
    coef = [0] * width
    for row in range(rank):
        coef[pivot_at[row]] = image[row]
    return coef


def apply_matrix(matrix, address):
    image = 0
    for bit in range(9):
        if (address >> bit) & 1:
            image ^= matrix[bit]
    return image


def fixed_addresses(matrix):
    rows = [0] * 9
    for col in range(9):
        value = matrix[col] ^ (1 << col)
        row = 0
        while value:
            if value & 1:
                rows[row] |= 1 << col
            value >>= 1
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
    return 1 << (9 - rank)


def trace_s(inv, eps):
    return sum(eps[index] for index in range(8) if inv[index] == index)


def affine_planes():
    planes = set()
    for origin, left, right in itertools.combinations(range(8), 3):
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


def generate_permutations(generators):
    seen = {tuple(range(8))}
    queue = [tuple(range(8))]
    while queue:
        current = queue.pop()
        for generator in generators:
            for nxt in (compose_perm(generator, current), compose_perm(current, generator)):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    return seen


def load_query():
    expect(sha256_file(INTERFACE) == INTERFACE_SHA256, "INTERFACE.json hash changed")
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_file(SELECTED) == SELECTED_SHA256, "selected-result.json hash changed")
    selected = json.loads(selected_bytes)
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
        mask = 0
        weight = 0
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
    expect(all(gram[i][k] == (56 if i == k else 0) for i in range(8) for k in range(8)), "RR^T is not 56 I")
    expect(all(port.bit_count() % 2 == 1 for port in ports), "a port label has even parity")
    expect(len(supports) == 14, "the query does not have 14 supports")
    return columns, ports, supports


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
    coords = [rank_coordinates(basis, 1 << bit) for bit in range(9)]
    expect(all(row is not None for row in coords), "a basis bit is outside the port span")
    contrib = [[index for index, bit in enumerate(row) if bit] for row in coords]
    basis_columns = [columns[ports.index(port)] for port in basis]
    return lookup, basis, basis_columns, contrib


def column_code(column, inv, mask):
    values = []
    for index in range(8):
        value = column[inv[index]]
        if value and (mask >> index) & 1:
            value = -value
        values.append(value)
    return norm_code(values)


def project_ports(lookup, basis_columns, inv, mask):
    images = []
    for column in basis_columns:
        found = lookup[column_code(column, inv, mask)]
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


def orthogonal(basis, matrix):
    images = [apply_matrix(matrix, vector) for vector in basis]
    for left in range(9):
        for right in range(left, 9):
            if (basis[left] & basis[right]).bit_count() % 2 != (images[left] & images[right]).bit_count() % 2:
                return False
    return True


def ports_match(lookup, columns, ports, inv, mask, matrix):
    for column, port in zip(columns, ports):
        found = lookup[column_code(column, inv, mask)]
        if found != apply_matrix(matrix, port):
            return False
    return True


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
        vectors.sort(key=lambda items: items[0][0])
        return vectors


def action_tables(inv, eps, transform):
    sigma = [0] * 8
    for out_index, in_index in enumerate(inv):
        sigma[in_index] = out_index
    dest = [0] * 4096
    sign = [0] * 4096
    for coordinate in range(8):
        image_coordinate = sigma[coordinate]
        image_sign = eps[image_coordinate]
        base = coordinate * 512
        image_base = image_coordinate * 512
        for address in range(512):
            src = base + address
            dest[src] = image_base + apply_matrix(transform, address)
            sign[src] = image_sign
    return dest, sign


def compose_key(left_inv, left_eps, right_inv, right_eps):
    inv = tuple(right_inv[left_inv[index]] for index in range(8))
    eps = tuple(left_eps[index] * right_eps[left_inv[index]] for index in range(8))
    return inv, eps


def normalize(pairs):
    ordered = tuple(sorted(pairs))
    flip = ordered[0][1]
    return tuple((address, coeff * flip) for address, coeff in ordered)


def pattern_of(items):
    coordinate = items[0][0] // 512
    pairs = []
    for index, coeff in items:
        expect(index // 512 == coordinate, "a basis vector meets two coordinates")
        pairs.append((index - 512 * coordinate, coeff))
    return coordinate, normalize(pairs)


def push_pattern(pattern, inv, eps, transform):
    dest = inv.index(0)
    out_sign = eps[dest]
    moved = [(apply_matrix(transform, address), out_sign * coeff) for address, coeff in pattern]
    return dest, normalize(moved)


def apply_signed(items, inv, eps, transform):
    acc = {}
    for index, coeff in items:
        coordinate = index // 512
        address = index - 512 * coordinate
        image_coordinate = inv.index(coordinate)
        image_index = image_coordinate * 512 + apply_matrix(transform, address)
        acc[image_index] = acc.get(image_index, 0) + eps[image_coordinate] * coeff
    return sorted((index, coeff) for index, coeff in acc.items() if coeff)


def satisfies(items, tables):
    values = {index: coeff for index, coeff in items}
    for dest, sign, eigenvalue in tables:
        for index, coeff in items:
            if values.get(dest[index], 0) != sign[index] * eigenvalue * coeff:
                return False
    return True


def apply_b(items, columns, ports):
    image = {}
    for port, column in zip(ports, columns):
        buckets = {}
        for index, coeff in items:
            coordinate = index // 512
            weight = column[coordinate]
            if weight:
                address = index - 512 * coordinate
                buckets[address] = buckets.get(address, 0) + weight * coeff
        if port & 1:
            for address, acc in buckets.items():
                target = address ^ port
                for coordinate, weight in enumerate(column):
                    if weight:
                        slot = coordinate * 512 + target
                        image[slot] = image.get(slot, 0) + weight * acc
        else:
            for address, acc in buckets.items():
                signed = -acc if (port & address).bit_count() & 1 else acc
                for coordinate, weight in enumerate(column):
                    if weight:
                        slot = coordinate * 512 + address
                        image[slot] = image.get(slot, 0) + weight * signed
    return {slot: value for slot, value in image.items() if value}


def restriction(vectors, columns, ports):
    pivots = [items[0][0] for items in vectors]
    columns_of_b = []
    for items in vectors:
        image = apply_b(items, columns, ports)
        coefficients = [image.get(pivot, 0) for pivot in pivots]
        reconstructed = {}
        for coeff, basis_items in zip(coefficients, vectors):
            if coeff == 0:
                continue
            for index, basis_coeff in basis_items:
                reconstructed[index] = reconstructed.get(index, 0) + coeff * basis_coeff
        reconstructed = {index: value for index, value in reconstructed.items() if value}
        expect(reconstructed == image, "B sends a joint basis vector outside the joint span")
        columns_of_b.append(coefficients)
    size = len(vectors)
    return tuple(
        tuple(columns_of_b[col][row] for col in range(size))
        for row in range(size)
    )


def constant_on_subspace_masks():
    masks = []
    level_bits = sum(1 << point for point in SUBSPACE)
    for low in range(16):
        for level in (0, 1):
            mask = level * level_bits
            for index, point in enumerate(SIGN_COORDINATES):
                if (low >> index) & 1:
                    mask |= 1 << point
            masks.append(mask)
    return sorted(masks)


def main():
    columns, ports, support_list = load_query()
    planes = affine_planes()
    support_masks = plane_masks(planes)
    expect(set(support_list) == support_masks, "column supports are not the affine planes")
    affine = affine_sigmas(gl_matrices())
    affine_set = set(affine)
    for sigma in affine:
        for mask in support_masks:
            image = sum(1 << sigma[bit] for bit in range(8) if (mask >> bit) & 1)
            expect(image in support_masks, "an affine map misses a plane")
    autos = []
    for perm in itertools.permutations(range(8)):
        if all(
            sum(1 << perm[bit] for bit in range(8) if (mask >> bit) & 1) in support_masks
            for mask in support_masks
        ):
            autos.append(perm)
    expect(set(tuple(perm) for perm in autos) == affine_set, "support automorphisms are not exactly AGL(3,2)")
    bare_swap = (3, 1, 2, 0, 4, 5, 6, 7)
    expect(bare_swap not in affine_set, "the single transposition (0 3) was accepted as affine")

    shear = tuple(point ^ (2 if point & 1 else 0) for point in range(8))
    singer = (0, 2, 4, 6, 3, 1, 7, 5)
    translations = [tuple(point ^ shift for point in range(8)) for shift in (1, 2, 4)]
    generated = generate_permutations([shear, singer, *translations])
    expect(generated == affine_set, "the listed generators do not generate AGL(3,2)")
    setwise = [sigma for sigma in affine if {sigma[point] for point in SUBSPACE} == set(SUBSPACE)]
    expect(len(setwise) == 96, "the setwise stabilizer of L does not have order 96")

    lookup, port_basis, basis_columns, contrib = prepare_labels(columns, ports)

    def fast_t(sigma, mask):
        images = project_ports(lookup, basis_columns, inv_of(sigma), mask)
        expect(images is not None, "a signed affine map missed a basis column")
        return matrix_from_images(contrib, images)

    generators = [(tuple(range(8)), 1 << bit) for bit in range(8)]
    generators.extend((sigma, 0) for sigma in (shear, singer, *translations))
    generator_t = []
    for sigma, mask in generators:
        matrix = fast_t(sigma, mask)
        inv = inv_of(sigma)
        expect(ports_match(lookup, columns, ports, inv, mask, matrix), "a generator misses a port")
        expect(orthogonal(port_basis, matrix), "a generator label map is not orthogonal")
        expect(rank_solve(list(matrix)) == 9, "a generator label map is singular")
        generator_t.append(matrix)
    for left, left_t in zip(generators, generator_t):
        for right, right_t in zip(generators, generator_t):
            sigma, mask = compose_signed(left[0], left[1], right[0], right[1])
            expect(fast_t(sigma, mask) == tuple(apply_matrix(left_t, column) for column in right_t),
                   "label maps do not multiply on a generator pair")

    orbit = {C1}
    frontier = [C1]
    while frontier:
        current = frontier.pop()
        for matrix in generator_t:
            image = apply_matrix(matrix, current)
            if image not in orbit:
                orbit.add(image)
                frontier.append(image)
    expect(len(orbit) == 112, "the generator orbit of sector 1 does not have size 112")
    expect(1344 * 256 // len(orbit) == 3072, "orbit-stabilizer did not give order 3072")

    stabilizer = {}
    orbit_hits = {}
    for sigma in affine:
        inv = inv_of(sigma)
        for mask in range(256):
            matrix = fast_t(sigma, mask)
            image = apply_matrix(matrix, C1)
            orbit_hits[image] = orbit_hits.get(image, 0) + 1
            if image == C1:
                stabilizer[(inv, mask_to_eps(mask))] = matrix
    expect(len(stabilizer) == 3072, "the T(1)=1 scan did not find 3072 elements")
    expect(set(orbit_hits) == orbit, "the scanned orbit of sector 1 disagrees with the generators")
    expect(all(count == 3072 for count in orbit_hits.values()), "sector-1 fibers are not uniform")
    for (inv, eps), matrix in stabilizer.items():
        expect(ports_match(lookup, columns, ports, inv, eps_to_mask(eps), matrix), "a stabilizer element misses a port")
        expect(orthogonal(port_basis, matrix), "a stabilizer label map is not orthogonal")
        expect(rank_solve(list(matrix)) == 9, "a stabilizer label map is singular")
        expect(apply_matrix(matrix, C1) == C1, "a recorded stabilizer element moves sector 1")

    stabilizer_perms = {inv_of(inv) for inv, _eps in stabilizer}
    expect(stabilizer_perms == set(setwise), "stabilizer permutations are not the setwise stabilizer of L")
    sign_fibers = {}
    for inv, _eps in stabilizer:
        sign_fibers[inv] = sign_fibers.get(inv, 0) + 1
    expect(len(sign_fibers) == 96 and set(sign_fibers.values()) == {32}, "sign fibers are not uniformly 32")

    identity = (tuple(range(8)), (1,) * 8)
    g_key = (G_INV, G_EPS)
    t_key = (T_INV, T_EPS)
    expect(identity in stabilizer and g_key in stabilizer and t_key in stabilizer, "identity, g or t misses the stabilizer")
    h_keys = []
    for bits in range(16):
        eps = [1] * 8
        for index, coordinate in enumerate(SIGN_COORDINATES):
            if (bits >> index) & 1:
                eps[coordinate] = -1
        key = (tuple(range(8)), tuple(eps))
        expect(key in stabilizer, "an element of H misses the stabilizer")
        h_keys.append(key)
    expect(len(h_keys) == 16, "H does not have order 16")

    def chi(eps):
        sign = 1
        for coordinate in SIGN_COORDINATES:
            sign *= eps[coordinate]
        return sign

    expect(chi(mask_to_eps(1 << 1)) == -1, "chi is trivial on the coordinate-1 sign")
    klein_keys = [identity, g_key, t_key, compose_key(*g_key, *t_key)]
    expect(len(set(klein_keys)) == 4, "g and t do not give four distinct permutation classes")
    group = {}
    for factor in klein_keys:
        for element in h_keys:
            key = compose_key(*factor, *element)
            matrix = tuple(apply_matrix(stabilizer[factor], column) for column in stabilizer[element])
            expect(key in stabilizer and stabilizer[key] == matrix, "a product of H, g and t leaves the stabilizer")
            group[key] = matrix
    expect(len(group) == 64, "H, g and t do not give 64 distinct products")
    for left in group:
        expect(left[0].index(0) == 0, "an element of <H,g,t> moves coordinate 0")
        for right in group:
            if compose_key(*left, *right) not in group:
                fail("the 64 products are not a group")
    expect(compose_key(*g_key, *g_key) == identity and compose_key(*t_key, *t_key) == identity, "g or t is not an involution")
    expect(compose_key(*g_key, *t_key) == compose_key(*t_key, *g_key), "g and t do not commute")

    def block_trace(key):
        return trace_s(*key) * fixed_addresses(stabilizer[key])

    def twisted(actor):
        total = sum(chi(element[1]) * block_trace(compose_key(*actor, *element)) for element in h_keys)
        expect(total % 16 == 0, "a twisted trace is not integral")
        return total // 16

    traces = [twisted(actor) for actor in klein_keys]
    expect(traces[0] == 32, "the product character does not have dimension 32")
    joint_dim = {}
    for left in (1, -1):
        for right in (1, -1):
            numerator = traces[0] + left * traces[1] + right * traces[2] + left * right * traces[3]
            expect(numerator % 4 == 0 and numerator >= 0, "a joint dimension is not a nonnegative quarter")
            joint_dim[(left, right)] = numerator // 4
    expect(list(joint_dim.values()) == [8, 8, 8, 8], "the trace formula does not give four spaces of dimension 8")

    h_tables = []
    for key in h_keys:
        dest, sign = action_tables(key[0], key[1], stabilizer[key])
        h_tables.append((dest, sign, chi(key[1])))
    g_dest, g_sign = action_tables(G_INV, G_EPS, stabilizer[g_key])
    t_dest, t_sign = action_tables(T_INV, T_EPS, stabilizer[t_key])
    spaces = {}
    patterns = {}
    occupied = set()
    for g_value in (1, -1):
        for t_value in (1, -1):
            lattice = Lattice()
            for dest, sign, eigenvalue in h_tables:
                lattice.add_operator(dest, sign, eigenvalue)
            lattice.add_operator(g_dest, g_sign, g_value)
            lattice.add_operator(t_dest, t_sign, t_value)
            vectors = lattice.basis()
            expect(len(vectors) == joint_dim[(g_value, t_value)], "the explicit joint basis misses the trace dimension")
            coordinate = JOINT_COORDINATE[(g_value, t_value)]
            bucket = set()
            for items in vectors:
                expect(len(items) == 8, "a joint basis vector does not have support 8")
                expect(all(coeff in (-1, 1) for _index, coeff in items), "a joint coefficient is not a sign")
                expect(items[0][1] == 1, "a joint pivot is not positive")
                found, pattern = pattern_of(items)
                expect(found == coordinate, "a joint basis vector leaves its sign coordinate")
                for address, _coeff in pattern:
                    index = coordinate * 512 + address
                    expect(index not in occupied, "joint supports are not disjoint")
                    occupied.add(index)
                bucket.add(pattern)
            expect(len(bucket) == 8, "a joint space does not have 8 patterns")
            spaces[(g_value, t_value)] = vectors
            patterns[coordinate] = bucket
    expect(len(occupied) == 256, "the four joint bases do not occupy 256 coordinates")
    plus = spaces[(1, 1)]
    expect(tuple(items[0][0] for items in plus) == EXPECTED_ROOTS, "the inherited (+1,+1) pivots changed")
    expect(tuple(plus[0]) == EXPECTED_FIRST, "the inherited first basis vector changed")
    minus = spaces[(1, -1)]
    expect(tuple(items[0][0] - 3 * 512 for items in minus) == EXPECTED_ROOTS, "the (+1,-1) pivots are not the shifted roots")

    plus_matrix = restriction(plus, columns, ports)
    minus_matrix = restriction(minus, columns, ports)
    expect(plus_matrix == EXPECTED_MATRIX, "B on the (+1,+1) basis is not the pinned matrix")
    expect(minus_matrix == EXPECTED_MATRIX, "B on the (+1,-1) basis is not the same matrix")

    witness_inv = inv_of(WITNESS_SIGMA)
    witness = (witness_inv, WITNESS_EPS)
    expect(WITNESS_SIGMA == (3, 1, 2, 0, 4, 6, 5, 7), "witness sigma changed")
    expect(witness_inv == WITNESS_SIGMA, "the witness involution is not equal to its inverse")
    expect(witness in stabilizer, "the unsigned involution (0 3)(5 6) does not fix sector 1")
    expect(witness not in group, "the witness lies in <H,g,t>")
    expect(witness_inv.index(0) == 3, "the witness does not send coordinate 0 to 3")
    witness_masks = sorted(eps_to_mask(eps) for inv, eps in stabilizer if inv == witness_inv)
    expect(witness_masks == constant_on_subspace_masks(), "the witness sign fiber is not the constant-on-L family")
    for source, target in zip(plus, minus):
        image = apply_signed(source, witness_inv, WITNESS_EPS, stabilizer[witness])
        expect(image == target, "the witness misses a canonical (+1,-1) basis vector")
        shifted = [(index + 3 * 512, coeff) for index, coeff in source]
        expect(image == shifted, "the witness changes the address pattern of a basis vector")

    target_tables = {}
    for eigenvalues, coordinate in JOINT_COORDINATE.items():
        g_value, t_value = eigenvalues
        target_tables[coordinate] = list(h_tables)
        target_tables[coordinate].append((g_dest, g_sign, g_value))
        target_tables[coordinate].append((t_dest, t_sign, t_value))
    source_patterns = [pattern_of(items)[1] for items in plus]
    onto = {(1, 1): 0, (1, -1): 0, (-1, 1): 0, (-1, -1): 0}
    onto_outside = {(1, 1): 0, (1, -1): 0, (-1, 1): 0, (-1, -1): 0}
    image_histogram = {}
    for key, matrix in stabilizer.items():
        inv, eps = key
        dest = inv.index(0)
        image_histogram[dest] = image_histogram.get(dest, 0) + 1
        images = [push_pattern(pattern, inv, eps, matrix) for pattern in source_patterns]
        expect({coordinate for coordinate, _pattern in images} == {dest}, "a basis vector left sigma(0)")
        image_patterns = {pattern for _coordinate, pattern in images}
        pattern_hit = dest in patterns and len(image_patterns) == 8 and image_patterns == patterns[dest]
        eigenvalue_hit = all(
            satisfies(apply_signed(items, inv, eps, matrix), target_tables[dest])
            for items in plus
        )
        expect(pattern_hit == eigenvalue_hit, "the pattern test disagrees with the eigenvalue test")
        expect(pattern_hit, "a stabilizer element does not carry the basis onto the joint space on sigma(0)")
        for eigenvalues, coordinate in JOINT_COORDINATE.items():
            if coordinate == dest:
                onto[eigenvalues] += 1
                if key not in group:
                    onto_outside[eigenvalues] += 1
    expect(image_histogram == {0: 768, 3: 768, 4: 768, 7: 768}, "sigma(0) is not uniform on L")
    expect(onto == {(1, 1): 768, (1, -1): 768, (-1, 1): 768, (-1, -1): 768}, "the four joint fibers are not equal")
    expect(onto_outside[(1, 1)] == 704, "the outside preservers of the (+1,+1) space are not 704")
    expect(onto_outside[(1, -1)] == 768 and onto_outside[(-1, 1)] == 768 and onto_outside[(-1, -1)] == 768,
           "a moved joint fiber is not entirely outside <H,g,t>")
    outside_other = 768 * 3
    expect(sum(onto_outside[key] for key in onto_outside if key != (1, 1)) == outside_other,
           "the outside transporter count is not 2304")
    expect(onto_outside[(1, 1)] + outside_other + len(group) == 3072, "the stabilizer is not partitioned by the census")

    # Rejection controls.
    transposition = (1, 0, 2, 3, 4, 5, 6, 7)
    expect(transposition not in affine_set, "a coordinate transposition was treated as affine")
    expect(project_ports(lookup, basis_columns, inv_of(transposition), 0) is None,
           "a coordinate transposition still mapped the basis columns")
    forbidden = (witness_inv, mask_to_eps(1))
    expect(forbidden not in stabilizer, "a lone minus sign on coordinate 0 still fixed sector 1")
    flipped = [(index, -coeff if index == 158 else coeff) for index, coeff in plus[0]]
    expect(not satisfies(flipped, target_tables[0]), "a sign error in the inherited basis still passed")
    damaged = set(patterns[0])
    damaged.pop()
    identity_patterns = {
        push_pattern(pattern, identity[0], identity[1], stabilizer[identity])[1]
        for pattern in source_patterns
    }
    expect(identity_patterns == patterns[0], "the identity does not preserve the (+1,+1) patterns")
    expect(identity_patterns != damaged, "deleting a pattern still matched the identity")
    expect(not satisfies(plus[0], target_tables[3]), "a (+1,+1) basis vector passed the (+1,-1) equations")

    print("PASS_C1_JOINT_8_TRANSPORTER")
    print("selected kappa", SELECTED_KAPPA)
    print("c=1 stabilizer", len(stabilizer))
    print("coordinate permutations", len(sign_fibers), "signs each", 32)
    print("group <H,g,t>", len(group))
    print("onto each joint space", 768)
    print("outside <H,g,t> onto another joint space", outside_other)
    print("witness sigma (0 3)(5 6), signs all +1, image joint (+1,-1)")
    print("B matrix on both ordered bases equals the pinned 8-by-8 matrix")


if __name__ == "__main__":
    main()
