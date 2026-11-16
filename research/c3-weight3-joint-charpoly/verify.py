#!/usr/bin/env python3
"""Characteristic polynomial of one 12-dimensional weight-3 c=3 joint space.

The pinned query is the historical 8-by-112 centre matrix. B = 4 A_3 is the
integer operator on sector c=3. The pinned space is the joint eigenspace
u = +1, v = -1 inside character 7, the least weight-3 character of the
order-16 sign stabilizer. Acceptance uses explicit checks, so -O does not
skip a theorem or a rejection control.
"""

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PACKAGE = pathlib.Path(__file__).resolve().parent
INTERFACE = (
    ROOT
    / "research/centre-polynomial-cache-limits/frozen/work"
    / "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json"
)
CERTIFICATE = ROOT / "research/exact-one-slot-gram/CERTIFICATE.json"
SELECTED = ROOT / "certificates/selected-result.json"
INTERFACE_SHA256 = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
CERTIFICATE_SHA256 = "29e0b0d86c7fd8929ad36d9de48c2b8b55500491576dc5ac1d0b1ff076d27483"
SELECTED_SHA256 = "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
SELECTED_KAPPA = "781451/250000000"
SECTOR = 3
ODDS = (1, 3, 5, 7)
EVENS = (0, 2, 4, 6)
U_INV = (2, 1, 0, 3, 6, 5, 4, 7)
U_EPS = (-1, 1, -1, 1, 1, 1, 1, 1)
V_INV = (4, 1, 6, 3, 0, 5, 2, 7)
V_EPS = (-1, 1, 1, 1, -1, 1, 1, 1)
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
PINNED_CHARACTER = 7
PINNED_U = 1
PINNED_V = -1
CHI_A = [0, 0, 0, 0, 256, 0, -256, 0, 96, 0, -16, 0, 1]
CHI_B = [0, 0, 0, 0, 16777216, 0, -1048576, 0, 24576, 0, -256, 0, 1]
CHI_A_SHA256 = "589ce5d010f0e4c5cf6d78719150e69afee3650ddf71dd273b58de10a5082e45"
CHI_B_SHA256 = "bf3564eac70bdbb2ff2e0041ca84c8f69f1f215e9ba5678f5a10d8b90804106a"
# Polynomials recorded for the weight-4 character. They are compared only so
# this result cannot be mistaken for that one. This file does not rebuild
# the weight-4 matrix.
RECORDED_WEIGHT4_DEGREE16 = [0, 0, 0, 0, 0, 0, 0, 0, 256, 0, -256, 0, 96, 0, -16, 0, 1]
RECORDED_WEIGHT4_DEGREE8 = [0, 0, 0, 0, 16, 0, -8, 0, 1]


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


def action_trace(dest, sign):
    return sum(sign[index] for index in range(4096) if dest[index] == index)


def closed_trace(element):
    return trace_s(element["inv"], element["eps"]) * fixed_addresses(element["T"])


def chi_of(chi, element):
    sign = 1
    for index, coordinate in enumerate(ODDS):
        if (chi >> index) & 1:
            sign *= element["eps"][coordinate]
    return sign


def weight3_characters():
    characters = tuple(chi for chi in range(16) if chi.bit_count() == 3)
    expect(characters == (7, 11, 13, 14), "the weight-3 characters are not 7, 11, 13, 14")
    return characters


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


def character_space(group_actions, extras):
    lattice = Lattice()
    for dest, sign, eigenvalue in group_actions:
        lattice.add_operator(dest, sign, eigenvalue)
    for dest, sign, eigenvalue in extras:
        lattice.add_operator(dest, sign, eigenvalue)
    return lattice.basis()


def satisfies(dest, sign, items, eigenvalue):
    values = {index: coeff for index, coeff in items}
    for src in range(4096):
        expected = sign[src] * eigenvalue * values.get(src, 0)
        if values.get(dest[src], 0) != expected:
            return False
    return True


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


def sector_one_image(items, columns, ports):
    """The c=1 operator, used only as a rejection control."""
    image = {}
    for port, root in zip(ports, columns):
        support = [index for index in range(8) if root[index]]
        buckets = {}
        for index, coeff in items:
            coordinate = index // 512
            address = index - 512 * coordinate
            if root[coordinate]:
                buckets[address] = buckets.get(address, 0) + root[coordinate] * coeff
        if port & 1:
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
    return matrix, sizes, owners


def pinned_matrix():
    """Integer matrix of B on the least-index basis of the pinned space."""
    matrix = [[0] * 12 for _ in range(12)]
    for left_pair, right_pair in (((0, 1), (8, 9)), ((2, 3), (10, 11))):
        for left in left_pair:
            for right in right_pair:
                matrix[left][right] = 4
                matrix[right][left] = 4
    matrix[4][4] = 8
    matrix[5][5] = -8
    matrix[6][6] = -8
    matrix[7][7] = 8
    return matrix


def pinned_eigenvectors():
    """Eigenvectors of A_3 in the pinned basis, with their eigenvalues."""
    vectors = []
    for index, eigenvalue in ((4, 2), (7, 2), (5, -2), (6, -2)):
        vector = [0] * 12
        vector[index] = 1
        vectors.append((vector, eigenvalue))
    patterns = (
        ((1, 1, 1, 1), 2),
        ((1, 1, -1, -1), -2),
        ((1, -1, 1, -1), 0),
        ((1, -1, -1, 1), 0),
    )
    for block in ((0, 1, 8, 9), (2, 3, 10, 11)):
        for pattern, eigenvalue in patterns:
            vector = [0] * 12
            for index, value in zip(block, pattern):
                vector[index] = value
            vectors.append((vector, eigenvalue))
    expect(len(vectors) == 12, "the pinned eigenbasis does not have 12 vectors")
    return vectors


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


def chi_b_from_blocks():
    """x^4 (x-8)^4 (x+8)^4, from two copies of x^2(x-8)(x+8) and four scalars."""
    quartic = [0, 0, -64, 0, 1]
    result = poly_pow(quartic, 2)
    result = poly_mul(result, poly_pow([-8, 1], 2))
    result = poly_mul(result, poly_pow([8, 1], 2))
    return result


def scale_to_a(coefficients):
    degree = len(coefficients) - 1
    expect(
        all(coefficients[index] % (4 ** (degree - index)) == 0 for index in range(degree + 1)),
        "chi_A is not integral",
    )
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


def charpoly_mod(matrix, prime):
    size = len(matrix)
    hess = [[entry % prime for entry in row] for row in matrix]
    for column in range(size - 2):
        pivot = None
        for row in range(column + 1, size):
            if hess[row][column]:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != column + 1:
            hess[column + 1], hess[pivot] = hess[pivot], hess[column + 1]
            for row in hess:
                row[column + 1], row[pivot] = row[pivot], row[column + 1]
        inverse = pow(hess[column + 1][column], -1, prime)
        for row in range(column + 2, size):
            factor = hess[row][column]
            if not factor:
                continue
            factor = factor * inverse % prime
            for index in range(column, size):
                hess[row][index] = (hess[row][index] - factor * hess[column + 1][index]) % prime
            for host in hess:
                host[column + 1] = (host[column + 1] + factor * host[row]) % prime
    minors = [[1], [(prime - hess[0][0]) % prime, 1]]
    for end in range(1, size):
        previous = minors[end]
        diagonal = hess[end][end]
        output = [0] * (end + 2)
        for index, coefficient in enumerate(previous):
            output[index + 1] = coefficient
            output[index] = (output[index] - diagonal * coefficient) % prime
        product = 1
        for start in range(end - 1, -1, -1):
            product = product * hess[start + 1][start] % prime
            if product == 0:
                break
            scale = hess[start][end] * product % prime
            if scale == 0:
                continue
            for index, coefficient in enumerate(minors[start]):
                output[index] = (output[index] - scale * coefficient) % prime
        expect(output[-1] % prime == 1, "Hessenberg characteristic polynomial is not monic")
        minors.append(output)
    return minors[size]


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


def horner(coefficients, point):
    value = 0
    for coefficient in reversed(coefficients):
        value = value * point + coefficient
    return value


def mat_vec(matrix, vector):
    size = len(matrix)
    return [sum(matrix[row][col] * vector[col] for col in range(size)) for row in range(size)]


def annihilated_by_split(matrix):
    """Return whether x(x-8)(x+8) kills the matrix, i.e. M(M^2-64 I)=0."""
    size = len(matrix)
    square = [
        [sum(matrix[row][mid] * matrix[mid][col] for mid in range(size)) for col in range(size)]
        for row in range(size)
    ]
    for row in range(size):
        square[row][row] -= 64
    product = [
        [sum(matrix[row][mid] * square[mid][col] for mid in range(size)) for col in range(size)]
        for row in range(size)
    ]
    return all(entry == 0 for row in product for entry in row)


def character_trace(element, group, chi):
    total = 0
    for member in group:
        product = compose(element, member)
        total += chi_of(chi, member) * closed_trace(product)
    expect(total % 16 == 0, "a character trace is not divisible by 16")
    return total // 16


def joint_dimension(dimension, first, second, product, left, right):
    numerator = dimension + left * first + right * second + left * right * product
    expect(numerator % 4 == 0 and numerator >= 0, "joint dimension is not a nonnegative quarter")
    return numerator // 4


def payload(vectors):
    return {
        "roots": [root for root, _items in vectors],
        "vectors": [[[index, coeff] for index, coeff in items] for _root, items in vectors],
    }


def main():
    dump = "--dump-evidence" in sys.argv
    block = [
        [0, 0, 4, 4],
        [0, 0, 4, 4],
        [4, 4, 0, 0],
        [4, 4, 0, 0],
    ]
    expect(charpoly_newton([[8]]) == [-8, 1], "Newton characteristic polynomial failed on [8]")
    expect(charpoly_newton([[-8]]) == [8, 1], "Newton characteristic polynomial failed on [-8]")
    expect(charpoly_newton(block) == [0, 0, -64, 0, 1], "Newton characteristic polynomial failed on the 4-by-4 block")
    expect(chi_b_from_blocks() == CHI_B, "the block product is not x^4 (x-8)^4 (x+8)^4")
    expect(scale_to_a(CHI_B) == CHI_A, "scaling chi_B by 4 did not produce chi_A")
    expect(CHI_A != RECORDED_WEIGHT4_DEGREE16 and CHI_A != RECORDED_WEIGHT4_DEGREE8, "chi_A collides with a weight-4 polynomial")
    expect(sha256_bytes(canonical(CHI_A).encode()) == CHI_A_SHA256, "chi_A SHA256 constant does not match the coefficient list")
    expect(sha256_bytes(canonical(CHI_B).encode()) == CHI_B_SHA256, "chi_B SHA256 constant does not match the coefficient list")

    columns, ports = load_query()
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result.json bytes changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")
    certificate_bytes = CERTIFICATE.read_bytes()
    expect(sha256_bytes(certificate_bytes) == CERTIFICATE_SHA256, "one-slot certificate bytes changed")

    port_of, lookup, port_basis, coords = prepare(columns, ports)
    group = []
    for odds in range(16):
        eps = [1] * 8
        for index, coordinate in enumerate(ODDS):
            if (odds >> index) & 1:
                eps[coordinate] = -1
        built = operator(tuple(range(8)), tuple(eps), port_of, lookup, port_basis, coords)
        expect(built is not None, "a positive-even sign pattern is not a symmetry")
        expect(apply_linear(built["T"], SECTOR) == SECTOR, "a positive-even sign pattern moves sector 3")
        group.append(built)
    expect(len(group) == 16, "the sign stabilizer does not have order 16")
    expect(all(element["eps"][coordinate] == 1 for element in group for coordinate in EVENS), "an even sign is negative")

    first = operator(U_INV, U_EPS, port_of, lookup, port_basis, coords)
    second = operator(V_INV, V_EPS, port_of, lookup, port_basis, coords)
    expect(first is not None and second is not None, "the explicit pair is not a symmetry")
    identity = identity_operator()
    expect(same_operator(compose(first, first), identity), "u is not an involution")
    expect(same_operator(compose(second, second), identity), "v is not an involution")
    expect(same_operator(compose(first, second), compose(second, first)), "u and v do not commute")
    product = compose(first, second)
    expect(product["inv"] == (6, 1, 4, 3, 2, 5, 0, 7), "uv is not (0 6)(2 4)")
    expect(product["eps"] == (-1, 1, 1, 1, 1, 1, -1, 1), "uv does not have minus signs on coordinates 0 and 6")
    expect(apply_linear(first["T"], SECTOR) == SECTOR and apply_linear(second["T"], SECTOR) == SECTOR, "the explicit pair moves sector 3")
    old_g = operator(G_INV, G_EPS, port_of, lookup, port_basis, coords)
    expect(old_g is not None and apply_linear(old_g["T"], SECTOR) == 343, "g does not send sector 3 to 343")

    group_tables = []
    for element in group:
        dest, sign = action_tables(element)
        expect(action_trace(dest, sign) == closed_trace(element), "a sign trace disagrees with the closed formula")
        group_tables.append((dest, sign))
    u_dest, u_sign = action_tables(first)
    v_dest, v_sign = action_tables(second)
    expect(action_trace(u_dest, u_sign) == closed_trace(first), "the trace of u disagrees with the closed formula")
    expect(action_trace(v_dest, v_sign) == closed_trace(second), "the trace of v disagrees with the closed formula")

    columns_b = column_table(columns, ports)
    characters = weight3_characters()
    pinned = None
    checked = 0
    for chi in characters:
        group_actions = [
            (dest, sign, chi_of(chi, element))
            for element, (dest, sign) in zip(group, group_tables)
        ]
        dimension_trace = sum(eigenvalue * closed_trace(element) for element, (_dest, _sign, eigenvalue) in zip(group, group_actions))
        expect(dimension_trace % 16 == 0 and dimension_trace // 16 == 80, "a weight-3 trace formula is not dimension 80")
        character_vectors = character_space(group_actions, ())
        expect(len(character_vectors) == 80, "a weight-3 character basis does not have dimension 80")
        trace_u = character_trace(first, group, chi)
        trace_v = character_trace(second, group, chi)
        trace_uv = character_trace(product, group, chi)
        expect((trace_u, trace_v, trace_uv) == (32, 32, 32), "an explicit-pair weight-3 trace is not +32")
        for eigenvalue_u in (1, -1):
            for eigenvalue_v in (1, -1):
                expected = joint_dimension(80, trace_u, trace_v, trace_uv, eigenvalue_u, eigenvalue_v)
                vectors = character_space(
                    group_actions,
                    ((u_dest, u_sign, eigenvalue_u), (v_dest, v_sign, eigenvalue_v)),
                )
                expect(len(vectors) == expected, "a joint lattice dimension disagrees with the trace formula")
                if expected == 44:
                    expect((eigenvalue_u, eigenvalue_v) == (1, 1), "the 44-dimensional slot is not (+1,+1)")
                    continue
                expect(expected == 12, "a weight-3 joint space is neither 44- nor 12-dimensional")
                for _root, items in vectors:
                    expect(len(items) == 8, "a 12-dimensional basis vector does not have support 8")
                    expect(all(coeff in (-1, 1) for _index, coeff in items), "a basis coefficient is not a unit sign")
                    for dest, sign, eigenvalue in group_actions:
                        expect(satisfies(dest, sign, items, eigenvalue), "a basis vector misses a character equation")
                    expect(satisfies(u_dest, u_sign, items, eigenvalue_u), "a basis vector misses the eigenvalue of u")
                    expect(satisfies(v_dest, v_sign, items, eigenvalue_v), "a basis vector misses the eigenvalue of v")
                matrix, sizes, _owners = restriction_matrix(columns_b, columns, ports, vectors)
                expect(sizes == [8] * 12, "the joint supports are not uniformly 8")
                coefficients_b = charpoly_newton(matrix)
                coefficients_a = scale_to_a(coefficients_b)
                expect(coefficients_b == CHI_B, "a 12-dimensional space has a different chi_B")
                expect(coefficients_a == CHI_A, "a 12-dimensional space has a different chi_A")
                expect(annihilated_by_split(matrix), "x(x-8)(x+8) does not kill a 12-dimensional matrix of B")
                checked += 1
                if chi == PINNED_CHARACTER and eigenvalue_u == PINNED_U and eigenvalue_v == PINNED_V:
                    pinned = (vectors, matrix)
    expect(checked == 12, "the weight-3 census did not cover 12 joint spaces")
    expect(pinned is not None, "the pinned character-7 space was not built")

    weight4_actions = [
        (dest, sign, chi_of(15, element))
        for element, (dest, sign) in zip(group, group_tables)
    ]
    expect(len(character_space(weight4_actions, ())) == 32, "the weight-4 character is not 32-dimensional")
    expect(
        len(character_space(weight4_actions, ((u_dest, u_sign, 1), (v_dest, v_sign, 1)))) == 8,
        "the weight-4 joint space is not 8-dimensional",
    )

    vectors, matrix = pinned
    expect(matrix == pinned_matrix(), "the pinned basis does not put B into the stated blocks")
    expect(charpoly_newton(matrix) == chi_b_from_blocks(), "Newton characteristic polynomial disagrees with the block product")
    prime = 1_000_003
    expect(
        charpoly_mod(matrix, prime) == [coefficient % prime for coefficient in CHI_B],
        "Hessenberg disagrees with Newton",
    )
    for point in (0, 1, 2, 3, 5, 8, -8):
        shifted = [[(-entry) % prime for entry in row] for row in matrix]
        for index in range(12):
            shifted[index][index] = (shifted[index][index] + point) % prime
        expect(det_mod(shifted, prime) == horner(CHI_B, point) % prime, "a determinant disagrees with chi_B")

    eigenvalues = pinned_eigenvectors()
    counts = {0: 0, 2: 0, -2: 0}
    eigen_columns = []
    for vector, eigenvalue in eigenvalues:
        image = mat_vec(matrix, vector)
        expect(image == [4 * eigenvalue * entry for entry in vector], "a block vector is not an eigenvector of A_3")
        counts[eigenvalue] += 1
        eigen_columns.append(vector)
    expect(counts == {0: 4, 2: 4, -2: 4}, "geometric multiplicities are not 4, 4, 4")
    eigen_matrix = [list(column) for column in zip(*eigen_columns)]
    expect(det_mod(eigen_matrix, prime) != 0, "the 12 block eigenvectors are linearly dependent")

    basis_payload = {
        "index": "coordinate*512+address",
        "character": {
            "index": PINNED_CHARACTER,
            "odds": list(ODDS),
            "support": [1, 3, 5],
            "value": "product of signs on coordinates 1, 3 and 5",
        },
        "eigenvalues": {"H": "chi", "u": PINNED_U, "v": PINNED_V},
        "space": payload(vectors),
    }
    matrix_payload = {"rows": matrix}
    basis_path = PACKAGE / "evidence" / "basis.json"
    matrix_path = PACKAGE / "evidence" / "matrix.json"
    if dump:
        basis_path.parent.mkdir(parents=True, exist_ok=True)
        basis_path.write_text(canonical(basis_payload) + "\n")
        matrix_path.write_text(canonical(matrix_payload) + "\n")
    else:
        expect(basis_path.is_file() and matrix_path.is_file(), "pinned evidence is missing; rerun with --dump-evidence")
        expect(json.loads(basis_path.read_text()) == basis_payload, "pinned basis does not match the recomputation")
        expect(json.loads(matrix_path.read_text()) == matrix_payload, "pinned matrix does not match the recomputation")

    # One cross-coset pair with a single odd minus. This is a witness, not a
    # census of the 3072 pairs, and it is not the weight-4 degree-16 question.
    odd_u = operator(
        (2, 1, 0, 3, 6, 5, 4, 7),
        (-1, -1, -1, 1, 1, 1, 1, 1),
        port_of,
        lookup,
        port_basis,
        coords,
    )
    odd_v = operator(
        (4, 1, 6, 3, 0, 5, 2, 7),
        (-1, -1, 1, 1, -1, 1, 1, 1),
        port_of,
        lookup,
        port_basis,
        coords,
    )
    expect(odd_u is not None and odd_v is not None, "the odd-sign witness pair is not a symmetry")
    expect(
        apply_linear(odd_u["T"], SECTOR) == SECTOR and apply_linear(odd_v["T"], SECTOR) == SECTOR,
        "the odd-sign witness pair moves sector 3",
    )
    expect(same_operator(compose(odd_u, odd_u), identity), "the odd-sign u is not an involution")
    expect(same_operator(compose(odd_v, odd_v), identity), "the odd-sign v is not an involution")
    expect(same_operator(compose(odd_u, odd_v), compose(odd_v, odd_u)), "the odd-sign witness pair does not commute")
    expect(odd_u["eps"][1] == -1 and odd_v["eps"][1] == -1, "the witness does not put a minus on coordinate 1")
    expect(
        all(odd_u["eps"][coordinate] == 1 and odd_v["eps"][coordinate] == 1 for coordinate in (3, 5, 7)),
        "the witness minus is not confined to coordinate 1 among the odd coordinates",
    )
    odd_u_dest, odd_u_sign = action_tables(odd_u)
    odd_v_dest, odd_v_sign = action_tables(odd_v)
    odd_product = compose(odd_u, odd_v)
    odd_actions = [
        (dest, sign, chi_of(PINNED_CHARACTER, element))
        for element, (dest, sign) in zip(group, group_tables)
    ]
    odd_trace_u = character_trace(odd_u, group, PINNED_CHARACTER)
    odd_trace_v = character_trace(odd_v, group, PINNED_CHARACTER)
    odd_trace_uv = character_trace(odd_product, group, PINNED_CHARACTER)
    expect((odd_trace_u, odd_trace_v, odd_trace_uv) == (-32, -32, 32), "the odd-sign character traces are not -32, -32, +32")
    odd_dimensions = {}
    for eigenvalue_u in (1, -1):
        for eigenvalue_v in (1, -1):
            odd_vectors = character_space(
                odd_actions,
                ((odd_u_dest, odd_u_sign, eigenvalue_u), (odd_v_dest, odd_v_sign, eigenvalue_v)),
            )
            odd_expected = joint_dimension(80, odd_trace_u, odd_trace_v, odd_trace_uv, eigenvalue_u, eigenvalue_v)
            expect(len(odd_vectors) == odd_expected, "the odd-sign lattice disagrees with the trace formula")
            odd_dimensions[(eigenvalue_u, eigenvalue_v)] = len(odd_vectors)
            if len(odd_vectors) != 12:
                continue
            odd_matrix, odd_sizes, _odd_owners = restriction_matrix(columns_b, columns, ports, odd_vectors)
            expect(odd_sizes == [8] * 12, "an odd-sign basis vector does not have support 8")
            expect(scale_to_a(charpoly_newton(odd_matrix)) == CHI_A, "the odd-sign witness changed chi_A")
            expect(annihilated_by_split(odd_matrix), "x(x-8)(x+8) does not kill the odd-sign witness")
    expect(
        odd_dimensions == {(1, 1): 12, (1, -1): 12, (-1, 1): 12, (-1, -1): 44},
        "the odd-sign witness did not move the 44-dimensional slot to (-1,-1)",
    )

    certificate = json.loads(certificate_bytes)
    expect(certificate["source_sha256"] == INTERFACE_SHA256, "published one-slot certificate names a different query")
    sectors = {}
    for sector in certificate["sectors"]:
        if sector["c"] == SECTOR:
            sectors[(sector["t"], sector["s"])] = [int(value) for value in sector["coefficients"]]
    expect(set(sectors) == {(0, 1), (0, -1), (1, 1), (1, -1)}, "c=3 sector labels changed")
    for key, polynomial in sectors.items():
        expect(polynomial[-1] == 1, "a c=3 sector polynomial is not monic")
        for point in (0, 8, -8):
            expect(horner(polynomial, point) == 0, "a chi_B factor does not divide sector " + str(key))

    transposition = operator((1, 0, 2, 3, 4, 5, 6, 7), (1,) * 8, port_of, lookup, port_basis, coords)
    expect(transposition is None, "a coordinate transposition was accepted as a symmetry")
    moved = dict(port_of)
    moved[columns[0]], moved[columns[1]] = port_of[columns[1]], port_of[columns[0]]
    swapped_lookup = {norm(column): moved[column] for column in moved}
    expect(operator(U_INV, U_EPS, moved, swapped_lookup, port_basis, coords) is None, "a swapped port label still looked like a symmetry")
    owners = {}
    for _root, items in vectors:
        for index, _coeff in items:
            owners[index] = True
    for _root, items in vectors:
        image = sector_one_image(items, columns, ports)
        expect(any(index not in owners for index in image), "the c=1 operator preserved a c=3 basis vector")
    pinned_actions = [
        (dest, sign, chi_of(PINNED_CHARACTER, element))
        for element, (dest, sign) in zip(group, group_tables)
    ]
    expect(
        len(character_space(pinned_actions, ())) == 80,
        "omitting u and v did not leave the 80-dimensional character",
    )
    expect(
        len(character_space(pinned_actions, ((u_dest, u_sign, 1), (v_dest, v_sign, 1)))) == 44,
        "the (+1,+1) space of character 7 is not 44-dimensional",
    )
    wrong_character = []
    flipped_character = False
    for element, (dest, sign, eigenvalue) in zip(group, pinned_actions):
        if not flipped_character and element["eps"] != (1,) * 8:
            wrong_character.append((dest, sign, -eigenvalue))
            flipped_character = True
        else:
            wrong_character.append((dest, sign, eigenvalue))
    expect(flipped_character, "the sign stabilizer had no non-identity element to flip")
    broken = character_space(wrong_character, ((u_dest, u_sign, PINNED_U), (v_dest, v_sign, PINNED_V)))
    expect(len(broken) != 12, "reversing one character value still left dimension 12")
    same_sign = operator((2, 1, 0, 3, 6, 5, 4, 7), (-1, 1, -1, 1, -1, 1, -1, 1), port_of, lookup, port_basis, coords)
    expect(same_sign is not None and apply_linear(same_sign["T"], SECTOR) == 48, "equal signs on both even cycles do not send sector 3 to 48")
    corrupted = [row[:] for row in matrix]
    corrupted[0][8] += 1
    expect(charpoly_mod(corrupted, prime) != charpoly_mod(matrix, prime), "changing a matrix entry preserved the characteristic polynomial")
    truncated = poly_mul(poly_pow([0, 0, -64, 0, 1], 2), poly_pow([-8, 1], 2))
    truncated = poly_mul(truncated, [8, 1])
    expect(truncated != CHI_B, "dropping one (x+8) factor still matched chi_B")
    sample_root, sample_items = vectors[0]
    expect(satisfies(u_dest, u_sign, sample_items, PINNED_U), "the unflipped basis vector is not fixed by u")
    flipped_items = [(index, -coeff if index == sample_root else coeff) for index, coeff in sample_items]
    expect(not satisfies(u_dest, u_sign, flipped_items, PINNED_U), "a sign error in a basis vector was still fixed")

    print("PASS_C3_WEIGHT3_JOINT_CHARPOLY")
    print("selected kappa", SELECTED_KAPPA)
    print("pinned character 7; joint eigenvalues u=+1, v=-1; dimension 12")
    print("chi_A = x^4 (x-2)^4 (x+2)^4")
    print("chi_B = x^4 (x-8)^4 (x+8)^4")
    print("chi_A SHA256", CHI_A_SHA256)
    print("chi_B SHA256", CHI_B_SHA256)
    print("weight-3 characters 7, 11, 13, 14; twelve 12-dimensional spaces; same polynomial")
    print("one odd-sign witness on character 7; three 12-dimensional spaces; same polynomial")
    print("geometric multiplicities on the pinned space", counts)


if __name__ == "__main__":
    main()
