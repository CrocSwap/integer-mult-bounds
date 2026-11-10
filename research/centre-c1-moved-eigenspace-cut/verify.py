#!/usr/bin/env python3
"""Cut a moved 48-dimensional eigenspace of s by one explicit involution.

The c=1 stabilizer, its sign characters and the orbit basis are recomputed
from the pinned 8-by-112 query. Acceptance checks call expect(), so Python
-O does not skip them. The stabilizer scan follows the enumeration in
research/centre-c1-moved-sign-split (PR #7009).
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
INTERFACE_SHA256 = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
T_INV = (0, 5, 6, 3, 4, 1, 2, 7)
T_EPS = (1, 1, 1, -1, 1, 1, 1, -1)
# sigma = (0 4 3 7)(5 6), stored inverse, all output signs +1.
S_INV = (7, 1, 2, 4, 0, 6, 5, 3)
S_EPS = (1, 1, 1, 1, 1, 1, 1, 1)
# u = (4 7)(5 6), stored inverse, all output signs +1.
U_INV = (0, 1, 2, 3, 7, 6, 5, 4)
U_EPS = (1, 1, 1, 1, 1, 1, 1, 1)

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
def sigma_of(inv):
    sigma = [0] * 8
    for index, source in enumerate(inv):
        sigma[source] = index
    return tuple(sigma)


def act_state(sigma, eps, matrix, coord, address):
    new_coord = sigma[coord]
    return eps[new_coord], new_coord, apply_matrix(matrix, address)


def rref_rank(matrix):
    from fractions import Fraction

    rows = [[Fraction(entry) for entry in row] for row in matrix]
    if not rows:
        return 0, rows
    width = len(rows[0])
    rank = 0
    for col in range(width):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][col]:
                factor = rows[row][col]
                rows[row] = [entry - factor * rows[rank][col_index] for col_index, entry in enumerate(rows[row])]
        rank += 1
    return rank, rows


def integer_kernel(matrix):
    """Return an integral basis of the right kernel, each vector content-free."""
    from fractions import Fraction
    from math import gcd

    rank, reduced = rref_rank(matrix)
    width = len(matrix[0])
    pivot_col = {}
    for row_index, row in enumerate(reduced):
        if row_index >= rank:
            break
        col = next(index for index, entry in enumerate(row) if entry)
        pivot_col[col] = row_index
    free = [col for col in range(width) if col not in pivot_col]
    basis = []
    for free_col in free:
        vector = [Fraction(0)] * width
        vector[free_col] = Fraction(1)
        for col, row_index in pivot_col.items():
            vector[col] = -reduced[row_index][free_col]
        denominator = 1
        for entry in vector:
            denominator = denominator * entry.denominator // gcd(denominator, entry.denominator)
        ints = [int(entry * denominator) for entry in vector]
        content = 0
        for entry in ints:
            content = gcd(content, abs(entry))
        basis.append([entry // content for entry in ints])
    expect(len(basis) == width - rank, "kernel basis has the wrong cardinality")
    return basis


def normalize_orbit_vectors(raw_vectors):
    normalized = []
    pivot_keys = []
    for coord, acc in raw_vectors:
        pivot_address = min(acc)
        pivot = acc[pivot_address]
        expect(pivot != 0, "an orbit vector has a zero pivot")
        vector = {}
        for address, coef in acc.items():
            if coef % pivot:
                fail("an orbit coordinate is not an integer multiple of its pivot")
            quotient = coef // pivot
            expect(quotient in (-1, 1), "a normalized orbit entry is not ±1")
            vector[(coord, address)] = quotient
        if vector[(coord, pivot_address)] != 1:
            vector = {key: -value for key, value in vector.items()}
        expect(vector[(coord, pivot_address)] == 1, "the orbit pivot is not +1")
        pivot_keys.append((coord, pivot_address))
        normalized.append(vector)
    return normalized, pivot_keys


def support_index(normalized):
    owners = {}
    for index, vector in enumerate(normalized):
        for key in vector:
            if key in owners:
                fail("two orbit vectors meet")
            owners[key] = index
    return owners


def monomial_action(actor, group, sigmas, normalized, pivot_keys):
    """Signed permutation induced on the orbit basis, checked on every entry."""
    sigma = sigmas[actor]
    eps = group[actor][1]
    matrix = group[actor][2]
    perm = []
    edge = []
    for vector in normalized:
        image = apply_signed(sigma, eps, matrix, vector)
        coordinates = character_coordinates(image, normalized, pivot_keys)
        if coordinates is None:
            fail("a character preserver left the character space")
        nonzeros = [(index, value) for index, value in enumerate(coordinates) if value]
        if len(nonzeros) != 1 or nonzeros[0][1] not in (-1, 1):
            fail("a character preserver is not a signed permutation of the orbit basis")
        perm.append(nonzeros[0][0])
        edge.append(nonzeros[0][1])
    if len(set(perm)) != len(perm):
        fail("a signed permutation of the orbit basis is not bijective")
    return perm, edge


def cycles_of(perm, edge):
    seen = set()
    cycles = []
    for start in range(len(perm)):
        if start in seen:
            continue
        nodes = []
        cursor = start
        while cursor not in seen:
            seen.add(cursor)
            nodes.append(cursor)
            cursor = perm[cursor]
        product = 1
        for node in nodes:
            product *= edge[node]
        cycles.append((nodes, product))
    expect(len(seen) == len(perm), "the signed permutation missed a basis vector")
    return cycles


def plus_eigenspace(cycles, perm, edge):
    spaces = []
    for nodes, product in cycles:
        if product != 1:
            continue
        values = [0] * len(perm)
        values[nodes[0]] = 1
        for node in nodes[:-1]:
            values[perm[node]] = edge[node] * values[node]
        if edge[nodes[-1]] * values[nodes[-1]] != 1:
            continue
        spaces.append((nodes[0], values))
    return spaces


def restriction_ok(perm, edge, plus):
    """Return (preserves, trace, scalar or None, images of seeds) for the +1 space."""
    trace = 0
    scalar = None
    is_scalar = True
    for seed, values in plus:
        image = [0] * len(values)
        for index, value in enumerate(values):
            if value:
                image[perm[index]] += edge[index] * value
        coefficients = []
        for other_seed, _other in plus:
            coefficients.append(image[other_seed])
        reconstructed = [0] * len(values)
        for coefficient, (_seed, other) in zip(coefficients, plus):
            for index, value in enumerate(other):
                reconstructed[index] += coefficient * value
        if reconstructed != image:
            return False, None, None
        trace += image[seed]
        for other_seed, _other in plus:
            entry = image[other_seed]
            if other_seed == seed:
                if scalar is None:
                    scalar = entry
                elif entry != scalar:
                    is_scalar = False
            elif entry:
                is_scalar = False
    if not is_scalar:
        scalar = None
    return True, trace, scalar


def element_order(actor, group, lookup):
    identity = lookup[(tuple(range(8)), (1,) * 8)]
    current = actor
    order = 1
    while current != identity:
        current = lookup[compose_key(group[actor], group[current])]
        order += 1
        if order > 6:
            fail("a character preserver has order greater than 6")
    return order


def apply_signed(sigma, eps, matrix, ambient):
    image = {}
    for (coord, address), coef in ambient.items():
        sign, new_coord, new_address = act_state(sigma, eps, matrix, coord, address)
        key = (new_coord, new_address)
        image[key] = image.get(key, 0) + sign * coef
    return {key: value for key, value in image.items() if value}


def lift_character(coordinates, normalized):
    ambient = {}
    for index, coef in enumerate(coordinates):
        if not coef:
            continue
        for key, entry in normalized[index].items():
            ambient[key] = ambient.get(key, 0) + coef * entry
    return {key: value for key, value in ambient.items() if value}


def character_coordinates(ambient, normalized, pivot_keys):
    coordinates = [0] * len(normalized)
    seen = set()
    for index, vector in enumerate(normalized):
        coordinates[index] = ambient.get(pivot_keys[index], 0)
        for key, entry in vector.items():
            if ambient.get(key, 0) != coordinates[index] * entry:
                return None
            seen.add(key)
    for key in ambient:
        if key not in seen:
            return None
    return coordinates


def eigenspace_coordinates(character, plus):
    alphas = [character[seed] for seed, _values in plus]
    reconstructed = [0] * len(character)
    for alpha, (_seed, values) in zip(alphas, plus):
        for index, value in enumerate(values):
            reconstructed[index] += alpha * value
    if reconstructed != character:
        return None
    return alphas


def in_span(alphas, kernel):
    from fractions import Fraction

    if not kernel:
        return all(alpha == 0 for alpha in alphas)
    width = len(kernel)
    system = [[Fraction(kernel[basis_index][coord]) for basis_index in range(width)] + [Fraction(alphas[coord])] for coord in range(len(alphas))]
    rank = 0
    for col in range(width):
        pivot = next((row for row in range(rank, len(system)) if system[row][col]), None)
        if pivot is None:
            return False
        system[rank], system[pivot] = system[pivot], system[rank]
        scale = system[rank][col]
        system[rank] = [entry / scale for entry in system[rank]]
        for row in range(len(system)):
            if row != rank and system[row][col]:
                factor = system[row][col]
                system[row] = [entry - factor * system[rank][index] for index, entry in enumerate(system[row])]
        rank += 1
    return all(system[row][-1] == 0 for row in range(rank, len(system)))


def apply_block(ambient, columns, ports, shift_on_odd):
    image = {}
    for (coord, address), coef in ambient.items():
        for column, port in zip(columns, ports):
            weight = column[coord] * coef
            if weight == 0:
                continue
            if bool(port & 1) == shift_on_odd:
                new_address = address ^ port
                sign = 1
            else:
                new_address = address
                sign = -1 if bin(port & address).count("1") & 1 else 1
            for index, entry in enumerate(column):
                if entry == 0:
                    continue
                key = (index, new_address)
                image[key] = image.get(key, 0) + weight * entry * sign
    return {key: value for key, value in image.items() if value}


def apply_block_grouped(ambient, columns, ports):
    """Same operator as apply_block(..., shift_on_odd=True), summed by address first."""
    image = {}
    for column, port in zip(columns, ports):
        dots = {}
        for (coord, address), coef in ambient.items():
            if column[coord]:
                dots[address] = dots.get(address, 0) + column[coord] * coef
        for address, weight in dots.items():
            if weight == 0:
                continue
            if port & 1:
                new_address = address ^ port
                sign = 1
            else:
                new_address = address
                sign = -1 if bin(port & address).count("1") & 1 else 1
            for index, entry in enumerate(column):
                if entry:
                    key = (index, new_address)
                    image[key] = image.get(key, 0) + sign * weight * entry
    return {key: value for key, value in image.items() if value}


def transport_matches(actor, group, columns, ports, port_of):
    inv, eps, matrix, _trace = group[actor]
    raw_at = {port: column for column, port in zip(columns, ports)}
    for column, port in zip(columns, ports):
        image = tuple(eps[index] * column[inv[index]] for index in range(8))
        target = port_of[norm(image)]
        if apply_matrix(matrix, port) != target:
            return False
        stored = raw_at[target]
        relation = None
        for left, right in zip(image, stored):
            if left == 0 and right == 0:
                continue
            if left == 0 or right == 0 or abs(left) != abs(right):
                return False
            sign = 1 if left == right else -1
            if relation is None:
                relation = sign
            elif relation != sign:
                return False
        if relation is None:
            return False
    return True


def orthogonal_on_bits(matrix):
    images = [apply_matrix(matrix, 1 << bit) for bit in range(9)]
    for left in range(9):
        for right in range(9):
            if dot(images[left], images[right]) != (1 if left == right else 0):
                return False
    return True
def orbit_basis(chi, signs, value):
    data = [(element[1], element[2], value(chi, mask_of(element[1]))) for element in signs]
    raw_vectors = []
    for coord in range(8):
        seen = set()
        for start in range(512):
            if start in seen:
                continue
            acc = {}
            for eps, matrix, chi_value in data:
                sign, new_coord, new_address = act_state(sigma_of(tuple(range(8))), eps, matrix, coord, start)
                if new_coord != coord:
                    fail("a pure sign moved a query coordinate")
                acc[new_address] = acc.get(new_address, 0) + chi_value * sign
                seen.add(new_address)
            acc = {address: coef for address, coef in acc.items() if coef}
            if acc:
                raw_vectors.append((coord, acc))
    return normalize_orbit_vectors(raw_vectors)


def classify_preservers(chi, group, lookup, sigmas, normalized, pivot_keys, plus, splitter):
    counts = {}
    witness_trace = None
    for actor in range(len(group)):
        if image_character(actor, chi, group, lookup, signs_global, value_global, sign_masks_global) != chi:
            continue
        perm, edge = monomial_action(actor, group, sigmas, normalized, pivot_keys)
        preserves, trace, scalar = restriction_ok(perm, edge, plus)
        commutes = compose_key(group[splitter], group[actor]) == compose_key(group[actor], group[splitter])
        if not preserves:
            key = ("moved",)
        else:
            order = element_order(actor, group, lookup)
            side = "centralizer" if commutes else "outer"
            if scalar is not None:
                key = (side, "scalar", scalar)
            elif order == 2:
                key = (side, "involution", trace)
            elif order == 4:
                key = (side, "order4", trace)
            else:
                key = (side, "order", order, trace)
        counts[key] = counts.get(key, 0) + 1
        if actor == witness_index:
            witness_trace = (preserves, trace, scalar, commutes, element_order(actor, group, lookup))
    return counts, witness_trace


def image_character(actor, chi, group, lookup, signs, value, sign_masks):
    target = []
    for element in signs:
        inverse = lookup[inverse_key(group[actor])]
        half = lookup[compose_key(element, group[actor])]
        image = lookup[compose_key(group[inverse], group[half])]
        target.append(value(chi, mask_of(group[image][1])))
    for candidate in range(16):
        if all(value(candidate, sign_masks[index]) == target[index] for index in range(16)):
            return candidate
    fail("a conjugate of a sign character is not a character")


signs_global = None
value_global = None
sign_masks_global = None
witness_index = None


def matrix_on_plus(perm, edge, plus):
    rows = []
    for _seed, values in plus:
        image = [0] * len(values)
        for index, value in enumerate(values):
            if value:
                image[perm[index]] += edge[index] * value
        rows.append([image[other] for other, _values in plus])
    return rows


def analyse_character(label, chi, dims, group, lookup, sigmas, signs, value, columns, ports, splitter):
    expect(dims[chi] == 192, label + " is not 192-dimensional")
    normalized, pivot_keys = orbit_basis(chi, signs, value)
    expect(len(normalized) == 192, label + " orbit basis does not have dimension 192")
    perm, edge = monomial_action(splitter, group, sigmas, normalized, pivot_keys)
    cycles = cycles_of(perm, edge)
    cycle_type = {}
    for nodes, product in cycles:
        key = (len(nodes), product)
        cycle_type[key] = cycle_type.get(key, 0) + 1
    expect(cycle_type == {(4, 1): 40, (2, 1): 8, (2, -1): 8}, label + " cycle type changed")
    plus = plus_eigenspace(cycles, perm, edge)
    expect(len(plus) == 48, label + " eigenvalue-1 space is not 48-dimensional")
    counts, witness_trace = classify_preservers(
        chi, group, lookup, sigmas, normalized, pivot_keys, plus, splitter
    )
    expect(counts == EXPECTED_CENSUS, label + " preserver census is " + str(counts))
    expect(witness_trace == (True, 24, None, False, 2), label + " witness action is " + str(witness_trace))
    witness_perm, witness_edge = monomial_action(witness_index, group, sigmas, normalized, pivot_keys)
    rows = matrix_on_plus(witness_perm, witness_edge, plus)
    # rows[source] is the coordinate row of u(e_source). The column-vector
    # matrix of u+I therefore has entry (target, source) = rows[source][target] + delta.
    minus = [[rows[source][target] + (1 if source == target else 0) for source in range(48)] for target in range(48)]
    plus_op = [[rows[source][target] - (1 if source == target else 0) for source in range(48)] for target in range(48)]
    minus_rank, _reduced = rref_rank(minus)
    plus_rank, _reduced = rref_rank(plus_op)
    expect(minus_rank == 36 and plus_rank == 12, label + " involution ranks are not 36 and 12")
    kernel = integer_kernel(minus)
    expect(len(kernel) == 12, label + " kernel is not 12-dimensional")
    kernel_rank, _reduced = rref_rank(kernel)
    expect(kernel_rank == 12, label + " kernel vectors are dependent")
    for vector in kernel:
        image = [0] * 48
        for row, coef in enumerate(vector):
            for col in range(48):
                image[col] += coef * rows[row][col]
        expect(image == [-entry for entry in vector], label + " kernel vector is not a -1 eigenvector")
    # Geometric action of s and u on each lifted kernel vector, then B_1-invariance.
    s_sigma, s_eps, s_matrix = sigmas[splitter], group[splitter][1], group[splitter][2]
    u_sigma, u_eps, u_matrix = sigmas[witness_index], group[witness_index][1], group[witness_index][2]
    occupied = {key for vector in normalized for key in vector}
    for vector in kernel:
        coordinates = [0] * 192
        for coef, (seed, values) in zip(vector, plus):
            for index, value in enumerate(values):
                coordinates[index] += coef * value
        ambient = lift_character(coordinates, normalized)
        s_image = apply_signed(s_sigma, s_eps, s_matrix, ambient)
        u_image = apply_signed(u_sigma, u_eps, u_matrix, ambient)
        expect(s_image == ambient, label + " geometric s does not fix a kernel vector")
        expect(u_image == {key: -value for key, value in ambient.items()}, label + " geometric u is not -1 on a kernel vector")
        block = apply_block(ambient, columns, ports, True)
        grouped = apply_block_grouped(ambient, columns, ports)
        expect(block == grouped, label + " the two block implementations disagree")
        image_coordinates = character_coordinates(block, normalized, pivot_keys)
        expect(image_coordinates is not None, label + " B_1 left the character space")
        alphas = eigenspace_coordinates(image_coordinates, plus)
        expect(alphas is not None, label + " B_1 left the eigenvalue-1 space")
        expect(in_span(alphas, kernel), label + " B_1 left the 12-dimensional subspace")
        outside = next(
            (coord, address)
            for coord in range(8)
            for address in range(512)
            if (coord, address) not in occupied
        )
        tampered = dict(block)
        tampered[outside] = tampered.get(outside, 0) + 1
        expect(
            character_coordinates(tampered, normalized, pivot_keys) is None,
            label + " an off-support spike was accepted as a character vector",
        )
    return cycle_type


def sign_character(mask_values, dims, value, signs):
    found = []
    for chi, dim in enumerate(dims):
        if dim != 192:
            continue
        if all(value(chi, mask) == wanted for mask, wanted in mask_values):
            found.append(chi)
    expect(len(found) == 1, "the requested 192-character is not unique")
    return found[0]


def main():
    global signs_global, value_global, sign_masks_global, witness_index
    columns, ports = load_query()
    port_of, basis, coords, basis_cols, dots = prepare(columns, ports)
    supports = tetrads(columns)
    autos = design_autos(supports)
    raw = build_stabilizer(autos, columns, ports, port_of, coords, basis_cols, dots)
    group, lookup = index_group(raw)
    identity = lookup[(tuple(range(8)), (1,) * 8)]
    expect(group[identity][3] == 4096, "the identity trace is not 4096")
    for element in group:
        inv, eps = inverse_key(element)
        inverse = lookup.get((inv, eps))
        if inverse is None:
            fail("the c=1 stabilizer is not closed under inversion")
        if compose_key(element, group[inverse]) != (group[identity][0], group[identity][1]):
            fail("a stabilizer inverse does not compose to the identity")
        for vector in basis:
            if apply_matrix(group[inverse][2], apply_matrix(element[2], vector)) != vector:
                fail("a stored label map does not invert")
    for left in group:
        for right in group:
            if compose_key(left, right) not in lookup:
                fail("the c=1 stabilizer is not closed under composition")
    pure = [element for element in group if element[0] == tuple(range(8))]
    expect(len(pure) == 32, "the pure sign subgroup does not have order 32")
    signs = [element for element in pure if element[1][0] == 1]
    expect(len(signs) == 16, "the positive coordinate-0 signs do not have order 16")
    masks = {mask_of(element[1]) for element in signs}
    coordinate_masks = []
    for first in range(2):
        for second in range(2):
            for fifth in range(2):
                for sixth in range(2):
                    coordinate_masks.append(first | (second << 1) | (fifth << 4) | (sixth << 5))
    expect(masks == set(coordinate_masks), "H is not the sign group on coordinates 1, 2, 5 and 6")
    dims, value = character_model(signs)
    expect(sum(dims) == 4096, "character dimensions do not cover the block")
    splitter = lookup[(S_INV, S_EPS)]
    witness = lookup[(U_INV, U_EPS)]
    witness_index = witness
    signs_global, value_global, sign_masks_global = signs, value, [mask_of(element[1]) for element in signs]
    for actor in (splitter, witness):
        expect(apply_matrix(group[actor][2], 1) == 1, "s or u moves sector 1")
        expect(orthogonal_on_bits(group[actor][2]), "s or u is not orthogonal on the standard basis")
        expect(transport_matches(actor, group, columns, ports, port_of), "s or u fails the column transport identity")
    expect(element_order(splitter, group, lookup) == 4, "s does not have order 4")
    expect(element_order(witness, group, lookup) == 2, "u does not have order 2")
    expect(
        compose_key(group[splitter], group[witness]) != compose_key(group[witness], group[splitter]),
        "u commutes with s",
    )
    first = lookup[(G_INV, G_EPS)]
    second = lookup[(T_INV, T_EPS)]
    chi = sign_character(((1, -1), (2, -1), (16, 1), (32, 1)), dims, value, signs)
    twin = sign_character(((1, 1), (2, 1), (16, -1), (32, -1)), dims, value, signs)
    preserved = []
    for candidate, dim in enumerate(dims):
        if dim != 192:
            continue
        if image_character(splitter, candidate, group, lookup, signs, value, sign_masks_global) == candidate:
            preserved.append(candidate)
    expect(set(preserved) == {chi, twin}, "s does not preserve exactly these two 192-characters")
    expect(image_character(first, chi, group, lookup, signs, value, sign_masks_global) == chi, "g does not preserve chi")
    expect(image_character(first, twin, group, lookup, signs, value, sign_masks_global) == twin, "g does not preserve the twin")
    expect(image_character(second, chi, group, lookup, signs, value, sign_masks_global) == twin, "t does not swap chi with its twin")
    expect(image_character(second, twin, group, lookup, signs, value, sign_masks_global) == chi, "t does not swap the twin with chi")
    analyse_character("chi", chi, dims, group, lookup, [sigma_of(element[0]) for element in group], signs, value, columns, ports, splitter)
    analyse_character("twin", twin, dims, group, lookup, [sigma_of(element[0]) for element in group], signs, value, columns, ports, splitter)
    # Rejection controls.
    expect((1, 0, 2, 3, 4, 5, 6, 7) not in autos, "a coordinate transposition was accepted as a tetrad automorphism")
    flipped = tuple(-1 if index == 0 else 1 for index in range(8))
    expect((U_INV, flipped) not in lookup, "flipping the coordinate-0 sign of u stayed in the stabilizer")
    partial = signs[:-1]
    partial_trace = sum(element[3] for element in partial)
    expect(
        partial_trace % len(partial) != 0 or partial_trace // len(partial) != 864,
        "dropping a sign element still reproduced the trivial dimension",
    )
    # s itself does not cut E by a minus space: u is essential.
    sigmas = [sigma_of(element[0]) for element in group]
    normalized, pivot_keys = orbit_basis(chi, signs, value)
    perm, edge = monomial_action(splitter, group, sigmas, normalized, pivot_keys)
    plus = plus_eigenspace(cycles_of(perm, edge), perm, edge)
    rows = matrix_on_plus(perm, edge, plus)
    minus = [[rows[source][target] + (1 if source == target else 0) for source in range(48)] for target in range(48)]
    rank, _reduced = rref_rank(minus)
    expect(rank == 48, "s+I on the eigenvalue-1 space is singular")
    print("PASS_C1_MOVED_EIGENSPACE_CUT")
    print("witness u=(4 7)(5 6) cuts E_1(s) as 36+12 on both moved 192-characters preserved by s")
    print("the 12-dimensional -1 space is invariant under B_1=4 A_1")
    print("preserver census on each E_1: 64 centralizer scalars, 64 outer scalars, 96 cutting involutions, 32 order-4 nonscalars, 256 that move E")


EXPECTED_CENSUS = {
    ("centralizer", "scalar", 1): 32,
    ("centralizer", "scalar", -1): 32,
    ("outer", "scalar", 1): 32,
    ("outer", "scalar", -1): 32,
    ("outer", "involution", 24): 48,
    ("outer", "involution", -24): 48,
    ("outer", "order4", 24): 16,
    ("outer", "order4", -24): 16,
    ("moved",): 256,
}


if __name__ == "__main__":
    main()
