#!/usr/bin/env python3
"""Degree-8 factors of one odd-sign cross-coset pair in the weight-4 c=3 character.

The pinned query is the historical 8-by-112 centre matrix. B = 4 A_3 is the
integer operator on sector c=3. The named pair puts a minus sign on odd
coordinate 1 and uses the explicit opposite even-cycle signs. Acceptance uses
explicit checks, so -O does not skip a theorem, the 96-element census, or a
rejection control.

The operator, lattice, and characteristic-polynomial routines follow the
weight-4 package of upstream PR #7021. The 96 involutions are the list
described by research/c3-centre-sign-split. This file recomputes both from
the pinned query.
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
INTERFACE_SHA256 = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
SELECTED_SHA256 = "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
SELECTED_KAPPA = "781451/250000000"
SECTOR = 3
ODDS = (1, 3, 5, 7)
EVENS = (0, 2, 4, 6)
# Explicit pair with no odd minuses, as recorded by #6965 and #7021.
U_INV = (2, 1, 0, 3, 6, 5, 4, 7)  # (0 2)(4 6)
U_EPS = (-1, 1, -1, 1, 1, 1, 1, 1)  # minuses on 0 and 2
V_INV = (4, 1, 6, 3, 0, 5, 2, 7)  # (0 4)(2 6)
V_EPS = (-1, 1, 1, 1, -1, 1, 1, 1)  # minuses on 0 and 4
W_INV = (6, 1, 4, 3, 2, 5, 0, 7)  # (0 6)(2 4)
W_EPS = (-1, 1, 1, 1, 1, 1, -1, 1)  # minuses on 0 and 6
# Named cross-coset pair: the same even signs, minus on odd coordinate 1 only.
NAMED_U_EPS = (-1, -1, -1, 1, 1, 1, 1, 1)
NAMED_V_EPS = (-1, -1, 1, 1, -1, 1, 1, 1)
# Ascending coefficients. These fingerprints match the polynomials recorded by #7021.
CHI_JOINT_A = [0, 0, 0, 0, 16, 0, -8, 0, 1]
CHI_A_16 = [0, 0, 0, 0, 0, 0, 0, 0, 256, 0, -256, 0, 96, 0, -16, 0, 1]
CHI_JOINT_A_SHA256 = "4078d16db1834dcd427c4f1094b96838a2c425c116c7cd1b60d46aa1f472f632"
CHI_A_SHA256 = "4207a8e80e73e3fcd16abc6cba001f8e9881023742eeb587cbd8fbadd9f24350"
PRIME = 1_000_003

def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def load_query():
    raw = INTERFACE.read_bytes()
    expect(sha256_bytes(raw) == INTERFACE_SHA256, "INTERFACE.json SHA256 does not match the pinned query")
    data = json.loads(raw)
    rows = data["R"]
    ports = [int(port) for port in data["ports"]]
    expect(len(rows) == 8 and len(ports) == 112 and len(set(ports)) == 112, "query shape")
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
    expect(all(gram[i][k] == (56 if i == k else 0) for i in range(8) for k in range(8)), "RR^T is not 56 I")
    expect(all(bin(port).count("1") % 2 == 1 for port in ports), "a port label has even parity")
    expect(all(entry in (-1, 0, 1) for column in columns for entry in column), "a root entry is outside {-1,0,1}")
    expect(all(sum(entry != 0 for entry in column) == 4 for column in columns), "a root does not have weight 4")
    return port_of, lookup, basis, coords


def apply_linear(matrix, address):
    image = 0
    for bit in range(9):
        if (address >> bit) & 1:
            image ^= matrix[bit]
    return image


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
    for port, image in mapping.items():
        if apply_linear(matrix, port) != image:
            return None
    images = [mapping[vector] for vector in basis]
    for left in range(9):
        for right in range(left, 9):
            if (bin(basis[left] & basis[right]).count("1") & 1) != (
                bin(images[left] & images[right]).count("1") & 1
            ):
                return None
    return {"inv": tuple(inv), "eps": tuple(eps), "T": tuple(matrix)}


def compose(left, right):
    inv = tuple(right["inv"][left["inv"][index]] for index in range(8))
    eps = tuple(left["eps"][index] * right["eps"][left["inv"][index]] for index in range(8))
    matrix = tuple(apply_linear(left["T"], column) for column in right["T"])
    return {"inv": inv, "eps": eps, "T": matrix}


def same_operator(left, right):
    return left["inv"] == right["inv"] and left["eps"] == right["eps"] and left["T"] == right["T"]


def identity_operator():
    return {
        "inv": tuple(range(8)),
        "eps": (1, 1, 1, 1, 1, 1, 1, 1),
        "T": tuple(1 << bit for bit in range(9)),
    }


def action_tables(element):
    inv, eps, transform = element["inv"], element["eps"], element["T"]
    sigma = [0] * 8
    for out_index, in_index in enumerate(inv):
        sigma[in_index] = out_index
    dest = [0] * 4096
    sign = [0] * 4096
    for coordinate in range(8):
        image_coordinate = sigma[coordinate]
        for address in range(512):
            src = coordinate * 512 + address
            dest[src] = image_coordinate * 512 + apply_linear(transform, address)
            sign[src] = eps[image_coordinate]
    return dest, sign



class Lattice:
    """Solution space of v[dst] = sign * v[src] equations on Q^4096."""

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
            vectors.append((items[0][0], [(index, coeff * pivot) for index, coeff in items]))
        vectors.sort()
        return vectors


def fixed_by(dest, sign, items, eigenvalue):
    values = {index: coeff for index, coeff in items}
    for index, coeff in items:
        image = dest[index]
        if values.get(image, 0) != sign[index] * eigenvalue * coeff:
            return False
    return all(coeff != 0 for _index, coeff in items)


def moves(port):
    """q·3 = 1, the parity of the two low bits of the port label."""
    return (port & SECTOR).bit_count() & 1


def column_table(columns, ports):
    raw = [{} for _ in range(4096)]
    for port, root in zip(ports, columns):
        support = [index for index in range(8) if root[index]]
        if moves(port):
            for coordinate in support:
                weight = root[coordinate]
                for address in range(512):
                    src = coordinate * 512 + address
                    target = address ^ port
                    bucket = raw[src]
                    for out_coordinate in support:
                        index = out_coordinate * 512 + target
                        bucket[index] = bucket.get(index, 0) + root[out_coordinate] * weight
        else:
            for coordinate in support:
                weight = root[coordinate]
                for address in range(512):
                    src = coordinate * 512 + address
                    parity = -1 if (port & address).bit_count() & 1 else 1
                    term = weight * parity
                    bucket = raw[src]
                    for out_coordinate in support:
                        index = out_coordinate * 512 + address
                        bucket[index] = bucket.get(index, 0) + root[out_coordinate] * term
    return [{index: value for index, value in column.items() if value} for column in raw]


def literal_image(items, columns, ports):
    image = {}
    for port, root in zip(ports, columns):
        support = [index for index in range(8) if root[index]]
        buckets = {}
        for index, coeff in items:
            coordinate = index // 512
            address = index - 512 * coordinate
            if root[coordinate]:
                buckets[address] = buckets.get(address, 0) + root[coordinate] * coeff
        if moves(port):
            for address, acc in buckets.items():
                target = address ^ port
                for coordinate in support:
                    index = coordinate * 512 + target
                    image[index] = image.get(index, 0) + root[coordinate] * acc
        else:
            for address, acc in buckets.items():
                if (port & address).bit_count() & 1:
                    acc = -acc
                for coordinate in support:
                    index = coordinate * 512 + address
                    image[index] = image.get(index, 0) + root[coordinate] * acc
    return {index: value for index, value in image.items() if value}


def column_image(columns_b, items):
    image = {}
    for index, coeff in items:
        for target, value in columns_b[index].items():
            image[target] = image.get(target, 0) + coeff * value
    return {index: value for index, value in image.items() if value}




def restriction_matrix(columns_b, columns, ports, vectors):
    owners = {}
    grouped = []
    for component, (_root, items) in enumerate(vectors):
        grouped.append(items)
        for index, coeff in items:
            expect(index not in owners, "two basis components share a coordinate")
            owners[index] = (component, coeff)
    matrix = [[0] * len(vectors) for _ in vectors]
    sizes = [len(items) for _root, items in vectors]
    for column, (_root, items) in enumerate(vectors):
        by_columns = column_image(columns_b, items)
        by_literal = literal_image(items, columns, ports)
        expect(by_columns == by_literal, "the two actions of B disagree on a basis vector")
        alphas = {}
        for index, value in by_columns.items():
            info = owners.get(index)
            expect(info is not None, "B sends a basis vector outside the space")
            component, coeff = info
            alpha = value * coeff
            previous = alphas.get(component)
            expect(previous is None or previous == alpha, "B image is not constant on a component")
            alphas[component] = alpha
        for component, alpha in alphas.items():
            for index, coeff in grouped[component]:
                expect(by_columns.get(index, 0) == coeff * alpha, "B image misses a component coordinate")
            matrix[component][column] = alpha
    for left in range(len(vectors)):
        for right in range(len(vectors)):
            expect(
                sizes[left] * matrix[left][right] == sizes[right] * matrix[right][left],
                "the Gram identity size_r M_rs = size_s M_sr failed",
            )
    return matrix, sizes



def poly_mul(left, right):
    output = [0] * (len(left) + len(right) - 1)
    for i, coeff in enumerate(left):
        for j, other in enumerate(right):
            output[i + j] += coeff * other
    return output


def poly_pow(base, exponent):
    result = [1]
    while exponent:
        if exponent & 1:
            result = poly_mul(result, base)
        exponent >>= 1
        if exponent:
            base = poly_mul(base, base)
    return result


def chi_b_from_blocks(negative_blocks, positive_blocks):
    """Characteristic polynomial of an orthogonal sum of the two block types."""
    negative = poly_pow([0, 8, 1], negative_blocks)  # x(x+8)
    positive = poly_pow([0, -8, 1], positive_blocks)  # x(x-8)
    return poly_mul(negative, positive)


def scale_to_a(coefficients):
    degree = len(coefficients) - 1
    expect(all(coefficients[index] % (4 ** (degree - index)) == 0 for index in range(degree + 1)), "chi_A is not integral")
    return [coefficients[index] // (4 ** (degree - index)) for index in range(degree + 1)]


def charpoly_newton(matrix):
    """Monic det(xI-M) by the Newton identities. Coefficients are ascending."""
    size = len(matrix)
    auxiliary = [[0] * size for _ in range(size)]
    coefficient = 1
    coefficients = [0] * (size + 1)
    coefficients[size] = 1
    for step in range(1, size + 1):
        product = [[0] * size for _ in range(size)]
        for row in range(size):
            for col in range(size):
                acc = matrix[row][col] * coefficient
                for mid in range(size):
                    acc += matrix[row][mid] * auxiliary[mid][col]
                product[row][col] = acc
        auxiliary = product
        trace = sum(auxiliary[index][index] for index in range(size))
        expect(trace % step == 0, "Newton trace is not divisible by the step")
        coefficient = -trace // step
        coefficients[size - step] = coefficient
    return coefficients


def det_mod(matrix, prime):
    size = len(matrix)
    work = [[entry % prime for entry in row] for row in matrix]
    determinant = 1
    for column in range(size):
        pivot = None
        for row in range(column, size):
            if work[row][column]:
                pivot = row
                break
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = (-determinant) % prime
        determinant = determinant * work[column][column] % prime
        inverse = pow(work[column][column], -1, prime)
        for row in range(column + 1, size):
            factor = work[row][column]
            if not factor:
                continue
            factor = factor * inverse % prime
            for index in range(column, size):
                work[row][index] = (work[row][index] - factor * work[column][index]) % prime
    return determinant


def annihilated_by_split(matrix):
    """Return whether x(x-8)(x+8) kills the matrix, i.e. M(M^2-64 I)=0."""
    size = len(matrix)
    square = [[sum(matrix[row][mid] * matrix[mid][col] for mid in range(size)) for col in range(size)] for row in range(size)]
    for row in range(size):
        square[row][row] -= 64
    product = [[sum(matrix[row][mid] * square[mid][col] for mid in range(size)) for col in range(size)] for row in range(size)]
    return all(entry == 0 for row in product for entry in row)


def splitting_involutions():
    """The 96 involutions described by the c=3 sign-split certificate."""
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
        expect(tuple(sigma[sigma[index]] for index in range(8)) == tuple(range(8)), "a described permutation is not an involution")
        for chosen in (first, second):
            for odds in range(16):
                eps = [1] * 8
                eps[chosen[0]] = -1
                eps[chosen[1]] = -1
                for index, coordinate in enumerate(ODDS):
                    if (odds >> index) & 1:
                        eps[coordinate] = -1
                elements.append((tuple(sigma), tuple(eps)))
    expect(len(elements) == 96 and len(set(elements)) == 96, "the described splitting list is not 96 distinct elements")
    return elements


def chi15(element):
    sign = 1
    for coordinate in ODDS:
        sign *= element["eps"][coordinate]
    return sign


def character_space(group_actions, extras):
    lattice = Lattice()
    for dest, sign, eigenvalue in group_actions:
        lattice.add_operator(dest, sign, eigenvalue)
    for dest, sign, eigenvalue in extras:
        lattice.add_operator(dest, sign, eigenvalue)
    return lattice.basis()


def apply_operator(dest, sign, items):
    """Apply the signed permutation that sends e_src to sign[src] e_dest[src]."""
    image = {}
    for index, coeff in items:
        target = dest[index]
        image[target] = image.get(target, 0) + sign[index] * coeff
    return {index: value for index, value in image.items() if value}


def scaled_vector(items, scalar):
    return {index: scalar * coeff for index, coeff in items}


def operator_scalar(dest, sign, items):
    """Return ±1 when the operator acts on this vector by that scalar, else None."""
    image = apply_operator(dest, sign, items)
    if image == scaled_vector(items, 1):
        return 1
    if image == scaled_vector(items, -1):
        return -1
    return None


def relative_scalar(dest, sign, ref_dest, ref_sign, items):
    image = apply_operator(dest, sign, items)
    reference = apply_operator(ref_dest, ref_sign, items)
    if image == reference:
        return 1
    negated = {index: -value for index, value in reference.items()}
    if image == negated:
        return -1
    return None


def diagonal_ratio(rep_inv, rep_eps, element_eps):
    """Diagonal d such that compose(representative, d) reproduces element_eps.

    compose(left, right) applies left first. With d diagonal,
    eps[i] = rep_eps[i] * d_eps[rep_inv[i]], so
    d_eps[j] = element_eps[rep_inv[j]] * rep_eps[rep_inv[j]].
    """
    return tuple(element_eps[rep_inv[index]] * rep_eps[rep_inv[index]] for index in range(8))


def diagonal_scalar(eps):
    """Predicted scalar on the weight-4 space for a uniform-even diagonal sign."""
    even_signs = {eps[index] for index in EVENS}
    expect(len(even_signs) == 1, "a ratio diagonal does not have one common even sign")
    odd_product = 1
    for index in ODDS:
        odd_product *= eps[index]
    return odd_product * next(iter(even_signs))


def uniform_diagonals():
    """The 32 diagonal signs whose even coordinates are equal and whose odds are free."""
    elements = []
    for even_sign in (1, -1):
        for odds in range(16):
            eps = [even_sign if index in EVENS else 1 for index in range(8)]
            for index, coordinate in enumerate(ODDS):
                if (odds >> index) & 1:
                    eps[coordinate] = -1
            elements.append(tuple(eps))
    expect(len(set(elements)) == 32, "the uniform-even diagonals are not 32 distinct signs")
    return elements


def coordinate_rows(space, vectors):
    """Coordinates of vectors in a lattice basis whose components have disjoint supports."""
    owners = {}
    for component, (_root, items) in enumerate(space):
        for index, coeff in items:
            expect(index not in owners, "two basis components share a coordinate")
            owners[index] = (component, coeff)
    rows = []
    for _root, items in vectors:
        alphas = {}
        for index, value in items:
            info = owners.get(index)
            expect(info is not None, "a joint vector leaves the one-involution eigenspace")
            component, coeff = info
            alpha = value * coeff
            previous = alphas.get(component)
            expect(previous in (None, alpha), "a joint vector is not constant on a component")
            alphas[component] = alpha
        row = [0] * len(space)
        for component, alpha in alphas.items():
            row[component] = alpha
        rows.append(row)
    return rows


def main():
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result.json bytes changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")

    expect(charpoly_newton([[-4, 4], [4, -4]]) == [0, 8, 1], "Newton failed on the negative block")
    expect(charpoly_newton([[4, 4], [4, 4]]) == [0, -8, 1], "Newton failed on the positive block")
    expect(scale_to_a(chi_b_from_blocks(2, 2)) == CHI_JOINT_A, "the degree-8 block polynomial changed")
    expect(scale_to_a(chi_b_from_blocks(4, 4)) == CHI_A_16, "the degree-16 block polynomial changed")
    expect(poly_mul(CHI_JOINT_A, CHI_JOINT_A) == CHI_A_16, "the degree-16 polynomial is not the square")
    expect(sha256_bytes(canonical(CHI_JOINT_A).encode()) == CHI_JOINT_A_SHA256, "degree-8 fingerprint changed")
    expect(sha256_bytes(canonical(CHI_A_16).encode()) == CHI_A_SHA256, "degree-16 fingerprint changed")

    columns, ports = load_query()
    port_of, lookup, port_basis, coords = prepare(columns, ports)

    def realize(inv, eps):
        built = operator(inv, eps, port_of, lookup, port_basis, coords)
        expect(built is not None, "a required signed permutation is not a symmetry")
        return built

    group = []
    for odds in range(16):
        eps = [1] * 8
        for index, coordinate in enumerate(ODDS):
            if (odds >> index) & 1:
                eps[coordinate] = -1
        built = realize(tuple(range(8)), tuple(eps))
        expect(apply_linear(built["T"], SECTOR) == SECTOR, "an element of H moves sector 3")
        expect(all(built["eps"][index] == 1 for index in EVENS), "an element of H has a negative even sign")
        group.append(built)
    expect(len(group) == 16, "H does not have order 16")

    group_actions = []
    for element in group:
        dest, sign = action_tables(element)
        group_actions.append((dest, sign, chi15(element)))
    character = character_space(group_actions, ())
    expect(len(character) == 32, "the weight-4 character basis does not have dimension 32")
    for _root, items in character:
        expect(items and all(coeff in (-1, 1) for _index, coeff in items), "a character basis vector is not a signed orbit")
        for dest, sign, eigenvalue in group_actions:
            expect(fixed_by(dest, sign, items, eigenvalue), "a basis vector misses a character equation")
            expect(
                operator_scalar(dest, sign, items) == eigenvalue,
                "the action convention does not reproduce the character scalar",
            )

    diagonals = []
    for eps in uniform_diagonals():
        built = realize(tuple(range(8)), eps)
        expect(apply_linear(built["T"], SECTOR) == SECTOR, "a uniform-even diagonal moves sector 3")
        expect(same_operator(compose(built, built), identity_operator()), "a uniform-even diagonal is not an involution")
        dest, sign = action_tables(built)
        predicted = diagonal_scalar(eps)
        for _root, items in character:
            expect(
                operator_scalar(dest, sign, items) == predicted,
                "a uniform-even diagonal does not act by the predicted scalar on the weight-4 space",
            )
        diagonals.append(built)
    expect(len(diagonals) == 32, "the uniform-even diagonal census is not 32 elements")
    odd_one = next(element for element in diagonals if element["eps"] == (1, -1, 1, 1, 1, 1, 1, 1))
    even_all = next(element for element in diagonals if element["eps"] == tuple(-1 if index in EVENS else 1 for index in range(8)))
    expect(diagonal_scalar(odd_one["eps"]) == -1, "minus on coordinate 1 is not the scalar -1")
    expect(diagonal_scalar(even_all["eps"]) == -1, "all-even minus is not the scalar -1")

    representatives = {
        U_INV: realize(U_INV, U_EPS),
        V_INV: realize(V_INV, V_EPS),
        W_INV: realize(W_INV, W_EPS),
    }
    identity = identity_operator()
    for representative in representatives.values():
        expect(apply_linear(representative["T"], SECTOR) == SECTOR, "a representative moves sector 3")
        expect(same_operator(compose(representative, representative), identity), "a representative is not an involution")
        expect(all(representative["eps"][index] == 1 for index in ODDS), "a representative has an odd minus")
    expect(
        same_operator(compose(representatives[U_INV], representatives[V_INV]), representatives[W_INV]),
        "the explicit product is not w0",
    )
    expect(
        same_operator(compose(representatives[U_INV], representatives[V_INV]), compose(representatives[V_INV], representatives[U_INV])),
        "the explicit representatives do not commute",
    )

    named_u = realize(U_INV, NAMED_U_EPS)
    named_v = realize(V_INV, NAMED_V_EPS)
    expect(same_operator(compose(representatives[U_INV], odd_one), named_u), "named u is not u0 composed with minus on coordinate 1")
    expect(same_operator(compose(representatives[V_INV], odd_one), named_v), "named v is not v0 composed with minus on coordinate 1")
    expect(same_operator(compose(named_u, named_u), identity), "named u is not an involution")
    expect(same_operator(compose(named_v, named_v), identity), "named v is not an involution")
    expect(same_operator(compose(named_u, named_v), compose(named_v, named_u)), "the named pair does not commute")
    expect(same_operator(compose(named_u, named_v), representatives[W_INV]), "the named product is not the no-odd-minus w0")
    expect(apply_linear(named_u["T"], SECTOR) == SECTOR and apply_linear(named_v["T"], SECTOR) == SECTOR, "the named pair moves sector 3")
    expect(named_u["inv"] != named_v["inv"], "the named pair is not cross-coset")

    described = splitting_involutions()
    expect((U_INV, NAMED_U_EPS) in described and (V_INV, NAMED_V_EPS) in described, "the named pair is outside the described list")
    expect((U_INV, U_EPS) in described and (V_INV, V_EPS) in described and (W_INV, W_EPS) in described, "a representative is outside the described list")
    sign_counts = {inv: {1: 0, -1: 0} for inv in representatives}
    cross_pairs = 0
    for left_index, (left_inv, _left_eps) in enumerate(described):
        for right_inv, _right_eps in described[left_index + 1:]:
            if left_inv != right_inv:
                cross_pairs += 1
    expect(cross_pairs == 3 * 32 * 32, "the described list does not have 3072 unordered cross-coset pairs")

    rep_actions = {inv: action_tables(element) for inv, element in representatives.items()}
    for inv, eps in described:
        element = realize(inv, eps)
        expect(apply_linear(element["T"], SECTOR) == SECTOR, "a described involution moves sector 3")
        expect(same_operator(compose(element, element), identity), "a described involution does not square to the identity")
        ratio_eps = diagonal_ratio(inv, representatives[inv]["eps"], eps)
        ratio = realize(tuple(range(8)), ratio_eps)
        expect(same_operator(compose(representatives[inv], ratio), element), "a described involution is not representative composed with its diagonal ratio")
        predicted = diagonal_scalar(ratio_eps)
        dest, sign = action_tables(element)
        ref_dest, ref_sign = rep_actions[inv]
        for _root, items in character:
            expect(
                relative_scalar(dest, sign, ref_dest, ref_sign, items) == predicted,
                "a described involution does not act as the predicted scalar times its representative",
            )
        sign_counts[inv][predicted] += 1
    for inv, counts in sign_counts.items():
        expect(counts == {1: 16, -1: 16}, "a permutation coset does not contain both scalars 16 times")

    named_u_action = action_tables(named_u)
    named_v_action = action_tables(named_v)
    explicit_u_action = rep_actions[U_INV]
    explicit_v_action = rep_actions[V_INV]
    for items_root in character:
        items = items_root[1]
        expect(relative_scalar(*named_u_action, *explicit_u_action, items) == -1, "named u does not act as -u0")
        expect(relative_scalar(*named_v_action, *explicit_v_action, items) == -1, "named v does not act as -v0")

    def joint_basis(u_action, v_action, eigenvalue_u, eigenvalue_v):
        return character_space(
            group_actions,
            ((u_action[0], u_action[1], eigenvalue_u), (v_action[0], v_action[1], eigenvalue_v)),
        )

    named_joints = {}
    explicit_joints = {}
    for eigenvalue_u in (1, -1):
        for eigenvalue_v in (1, -1):
            named_joints[(eigenvalue_u, eigenvalue_v)] = joint_basis(named_u_action, named_v_action, eigenvalue_u, eigenvalue_v)
            explicit_joints[(eigenvalue_u, eigenvalue_v)] = joint_basis(explicit_u_action, explicit_v_action, eigenvalue_u, eigenvalue_v)
            expect(len(named_joints[(eigenvalue_u, eigenvalue_v)]) == 8, "a named joint space is not 8-dimensional")
    for eigenvalue_u in (1, -1):
        for eigenvalue_v in (1, -1):
            expect(
                named_joints[(eigenvalue_u, eigenvalue_v)] == explicit_joints[(-eigenvalue_u, -eigenvalue_v)],
                "flipping both named eigenvalues does not recover the explicit joint basis",
            )

    columns_b = column_table(columns, ports)

    def factored(vectors):
        matrix, sizes = restriction_matrix(columns_b, columns, ports, vectors)
        polynomial = scale_to_a(charpoly_newton(matrix))
        expect(annihilated_by_split(matrix), "x(x-8)(x+8) does not kill a joint matrix of B")
        return matrix, sizes, polynomial

    joint_polynomials = {}
    for key, vectors in named_joints.items():
        _matrix, sizes, polynomial = factored(vectors)
        expect(sizes == [32] * 8, "a named joint basis vector does not have support 32")
        expect(polynomial == CHI_JOINT_A, "a named joint space does not have the common degree-8 polynomial")
        joint_polynomials[key] = polynomial

    for eigenvalue_u in (1, -1):
        space = character_space(group_actions, ((named_u_action[0], named_u_action[1], eigenvalue_u),))
        expect(len(space) == 16, "a named one-involution eigenspace is not 16-dimensional")
        matrix, sizes = restriction_matrix(columns_b, columns, ports, space)
        expect(sizes == [16] * 16, "a named 16-dimensional basis vector does not have support 16")
        polynomial = scale_to_a(charpoly_newton(matrix))
        expect(polynomial == CHI_A_16, "a named 16-dimensional space does not have the inherited degree-16 polynomial")
        expect(annihilated_by_split(matrix), "x(x-8)(x+8) does not kill a named 16-dimensional matrix of B")
        plus = named_joints[(eigenvalue_u, 1)]
        minus = named_joints[(eigenvalue_u, -1)]
        expect(poly_mul(joint_polynomials[(eigenvalue_u, 1)], joint_polynomials[(eigenvalue_u, -1)]) == polynomial,
               "the two degree-8 factors do not multiply to the degree-16 polynomial")
        rows = coordinate_rows(space, plus) + coordinate_rows(space, minus)
        expect(len(rows) == 16 and det_mod(rows, PRIME) != 0, "the two joint bases do not span the 16-dimensional eigenspace")
        for eigenvalue_v, vectors in ((1, plus), (-1, minus)):
            for _root, items in vectors:
                expect(fixed_by(named_u_action[0], named_u_action[1], items, eigenvalue_u), "a joint vector misses the u eigenvalue")
                expect(fixed_by(named_v_action[0], named_v_action[1], items, eigenvalue_v), "a joint vector misses the v eigenvalue")

    # Rejection controls. Each one names the false statement it must reject.
    expect(operator((1, 0, 2, 3, 4, 5, 6, 7), (1,) * 8, port_of, lookup, port_basis, coords) is None,
           "a coordinate transposition was accepted as a symmetry")
    bare = realize(U_INV, (1, -1, 1, 1, 1, 1, 1, 1))
    expect(apply_linear(bare["T"], SECTOR) == 48, "minus on coordinate 1 with unsigned even cycles does not send sector 3 to 48")
    same_cycle = realize(U_INV, (-1, -1, -1, 1, -1, 1, -1, 1))
    expect(apply_linear(same_cycle["T"], SECTOR) == 48, "equal even-cycle signs do not send sector 3 to 48")
    mixed_even = tuple(-1 if index == 0 else 1 for index in range(8))
    mixed = realize(tuple(range(8)), mixed_even)
    mixed_dest, mixed_sign = action_tables(mixed)
    expect(
        any(operator_scalar(mixed_dest, mixed_sign, items) is None for _root, items in character),
        "a diagonal with unequal even signs still acted by a scalar on every character basis vector",
    )
    sample_matrix, _sizes, _sample_polynomial = factored(named_joints[(1, 1)])
    corrupted = [row[:] for row in sample_matrix]
    corrupted[0][0] += 1
    expect(charpoly_newton(corrupted) != charpoly_newton(sample_matrix), "changing a matrix entry preserved the characteristic polynomial")
    expect(chi_b_from_blocks(3, 1) != chi_b_from_blocks(2, 2), "replacing one (x+8) factor by (x-8) still matched the degree-8 polynomial")
    same_coset_conflict = character_space(
        group_actions,
        ((named_u_action[0], named_u_action[1], 1), (explicit_u_action[0], explicit_u_action[1], 1)),
    )
    same_coset_repeat = character_space(
        group_actions,
        ((named_u_action[0], named_u_action[1], 1), (explicit_u_action[0], explicit_u_action[1], -1)),
    )
    expect(len(same_coset_conflict) == 0, "same-coset eigenvalues +1 and +1 were compatible")
    expect(len(same_coset_repeat) == 16, "a same-coset pair split the 16-dimensional eigenspace further")
    expect(cross_pairs == 3072, "the cross-coset count drifted")
    wrong_character = []
    flipped_character = False
    for element, (dest, sign, eigenvalue) in zip(group, group_actions):
        if not flipped_character and element["eps"] != (1,) * 8:
            wrong_character.append((dest, sign, -eigenvalue))
            flipped_character = True
        else:
            wrong_character.append((dest, sign, eigenvalue))
    expect(flipped_character, "H had no non-identity element to flip")
    expect(len(character_space(wrong_character, ())) != 32, "reversing one character value still left dimension 32")
    moved = dict(port_of)
    moved[columns[0]], moved[columns[1]] = port_of[columns[1]], port_of[columns[0]]
    swapped_lookup = {norm(column): moved[column] for column in moved}
    expect(
        operator(U_INV, U_EPS, moved, swapped_lookup, port_basis, coords) is None,
        "a swapped port label still looked like a symmetry",
    )
    linked = None
    for dest, sign, eigenvalue in group_actions:
        for _root, items in character:
            values = {index: coeff for index, coeff in items}
            for index, _coeff in items:
                if dest[index] != index and dest[index] in values:
                    linked = (dest, sign, eigenvalue, items, index)
                    break
            if linked is not None:
                break
        if linked is not None:
            break
    expect(linked is not None, "no character equation links two basis coordinates")
    dest, sign, eigenvalue, witness, index = linked
    expect(fixed_by(dest, sign, witness, eigenvalue), "the unflipped character vector is not fixed")
    flipped = [(item, -coeff if item == index else coeff) for item, coeff in witness]
    expect(not fixed_by(dest, sign, flipped, eigenvalue), "a sign error in a character vector was still fixed")

    print("PASS_C3_WEIGHT4_ODD_SIGN_FACTORS")
    print("selected kappa", SELECTED_KAPPA)
    print("named pair u=(0 2)(4 6) minuses 0,1,2; v=(0 4)(2 6) minuses 0,1,4")
    print("both degree-8 factors x^4 (x-2)^2 (x+2)^2")
    print("degree-16 polynomial x^8 (x-2)^4 (x+2)^4")
    print("described involutions 96; each coset scalars", {1: 16, -1: 16})
    print("unordered cross-coset pairs", cross_pairs)
    print("evidence direct-factorisation-and-exhaustive-census")


if __name__ == "__main__":
    main()
