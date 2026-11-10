#!/usr/bin/env python3
"""Characteristic polynomial of one weight-4 c=3 joint summand.

The pinned query is the historical 8-by-112 centre matrix. B = 4 A_3 is the
integer operator on sector c=3. The 16-dimensional space is the +1 eigenspace
of the explicit involution u inside the unique weight-4 sign character.
Acceptance uses explicit checks, so -O does not skip a theorem or a rejection
control.
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
# Blocks of M, the matrix of B, in the least-index basis of the u=+1 space.
# kind -1 is [[-4, 4], [4, -4]]; kind +1 is [[4, 4], [4, 4]].
BLOCK_PAIRS = (
    (0, 5, -1),
    (1, 4, -1),
    (2, 7, 1),
    (3, 6, 1),
    (8, 13, -1),
    (9, 12, -1),
    (10, 15, 1),
    (11, 14, 1),
)
CHI_A_SHA256 = "4207a8e80e73e3fcd16abc6cba001f8e9881023742eeb587cbd8fbadd9f24350"
CHI_B_SHA256 = "5030313ecab6822bd390a9e6847a3b6a9c9d701d2e7e247d7892ce5f55bfe717"
CHI_JOINT_A_SHA256 = "4078d16db1834dcd427c4f1094b96838a2c425c116c7cd1b60d46aa1f472f632"
CHI_JOINT_B_SHA256 = "04375398447c3b08683582cc785814e9955ed62fcaa6725dc3467484c8a41457"


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(path.read_bytes())


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


def chi15(element):
    sign = 1
    for coordinate in ODDS:
        sign *= element["eps"][coordinate]
    return sign


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
    return matrix, sizes


def block_matrix():
    matrix = [[0] * 16 for _ in range(16)]
    for left, right, kind in BLOCK_PAIRS:
        matrix[left][left] = -4 if kind < 0 else 4
        matrix[right][right] = -4 if kind < 0 else 4
        matrix[left][right] = 4
        matrix[right][left] = 4
    return matrix


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


def character_space(group_actions, extras):
    lattice = Lattice()
    for dest, sign, eigenvalue in group_actions:
        lattice.add_operator(dest, sign, eigenvalue)
    for dest, sign, eigenvalue in extras:
        lattice.add_operator(dest, sign, eigenvalue)
    return lattice.basis()


def payload(vectors):
    return {
        "roots": [root for root, _items in vectors],
        "vectors": [[[index, coeff] for index, coeff in items] for _root, items in vectors],
    }


def main():
    dump = "--dump-evidence" in sys.argv
    columns, ports = load_query()
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result.json bytes changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")
    certificate_bytes = CERTIFICATE.read_bytes()
    expect(sha256_bytes(certificate_bytes) == CERTIFICATE_SHA256, "one-slot certificate bytes changed")

    # Newton identity self-test on one block, before any matrix from the query is used.
    expect(charpoly_newton([[-4, 4], [4, -4]]) == [0, 8, 1], "Newton characteristic polynomial failed on the negative block")
    expect(charpoly_newton([[4, 4], [4, 4]]) == [0, -8, 1], "Newton characteristic polynomial failed on the positive block")

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
    expect(len(group) == 16, "the weight-4 sign stabilizer does not have order 16")
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

    group_actions = []
    for element in group:
        dest, sign = action_tables(element)
        closed = trace_s(element["inv"], element["eps"]) * fixed_addresses(element["T"])
        expect(action_trace(dest, sign) == closed, "a sign trace disagrees with the closed formula")
        group_actions.append((dest, sign, chi15(element)))
    trace_total = 0
    for element, (_dest, _sign, eigenvalue) in zip(group, group_actions):
        trace_total += eigenvalue * trace_s(element["inv"], element["eps"]) * fixed_addresses(element["T"])
    expect(trace_total % 16 == 0 and trace_total // 16 == 32, "the weight-4 trace formula is not dimension 32")

    u_dest, u_sign = action_tables(first)
    v_dest, v_sign = action_tables(second)
    character_vectors = character_space(group_actions, ())
    plus = character_space(group_actions, ((u_dest, u_sign, 1),))
    minus = character_space(group_actions, ((u_dest, u_sign, -1),))
    joint_plus = character_space(group_actions, ((u_dest, u_sign, 1), (v_dest, v_sign, 1)))
    joint_minus = character_space(group_actions, ((u_dest, u_sign, 1), (v_dest, v_sign, -1)))
    expect(len(character_vectors) == 32, "the explicit weight-4 basis does not have dimension 32")
    expect(len(plus) == 16 and len(minus) == 16, "u does not split the weight-4 character into 16+16")
    expect(len(joint_plus) == 8 and len(joint_minus) == 8, "v does not split the u=+1 space into 8+8")

    def ambient(items):
        return {index: coeff for index, coeff in items}

    def paired(left, right, sign):
        values = ambient(left)
        for index, coeff in right:
            expect(index not in values, "a v-pair of basis vectors has overlapping support")
            values[index] = sign * coeff
        return values

    for index in range(8):
        expect(
            ambient(joint_plus[index][1]) == paired(plus[index][1], plus[index + 8][1], -1),
            "a joint (+1,+1) vector is not the difference of a v-pair",
        )
        expect(
            ambient(joint_minus[index][1]) == paired(plus[index][1], plus[index + 8][1], 1),
            "a joint (+1,-1) vector is not the sum of a v-pair",
        )
    for _root, items in plus:
        expect(len(items) == 16, "a u=+1 basis vector does not have support 16")
        expect(fixed_by(u_dest, u_sign, items, 1), "a basis vector is not fixed by u with eigenvalue +1")
        for dest, sign, eigenvalue in group_actions:
            expect(fixed_by(dest, sign, items, eigenvalue), "a basis vector misses a character equation")

    columns_b = column_table(columns, ports)
    matrix, sizes = restriction_matrix(columns_b, columns, ports, plus)
    expect(sizes == [16] * 16, "the u=+1 supports are not uniformly 16")
    expect(matrix == block_matrix(), "the pinned basis does not put B into the eight 2-by-2 blocks")
    joint_matrix, joint_sizes = restriction_matrix(columns_b, columns, ports, joint_plus)
    expect(joint_sizes == [32] * 8, "the joint supports are not uniformly 32")
    expect(joint_matrix == [row[:8] for row in matrix[:8]], "the joint matrix is not the leading principal block")
    expect([row[8:] for row in matrix[8:]] == joint_matrix, "the two diagonal blocks of M are different")
    expect(all(row[8:] == [0] * 8 for row in matrix[:8]), "M is not block diagonal across the two v-eigenspaces")

    coefficients_b = charpoly_newton(matrix)
    expected_b = chi_b_from_blocks(4, 4)
    expect(coefficients_b == expected_b, "Newton characteristic polynomial disagrees with the block product")
    coefficients_a = scale_to_a(coefficients_b)
    expected_a = scale_to_a(expected_b)
    expect(coefficients_a == [0, 0, 0, 0, 0, 0, 0, 0, 256, 0, -256, 0, 96, 0, -16, 0, 1], "chi_A changed")
    expect(sha256_bytes(canonical(coefficients_a).encode()) == CHI_A_SHA256, "chi_A SHA256 changed")
    expect(sha256_bytes(canonical(coefficients_b).encode()) == CHI_B_SHA256, "chi_B SHA256 changed")
    joint_b = charpoly_newton(joint_matrix)
    expect(joint_b == chi_b_from_blocks(2, 2), "the joint characteristic polynomial disagrees with its four blocks")
    joint_a = scale_to_a(joint_b)
    expect(joint_a == [0, 0, 0, 0, 16, 0, -8, 0, 1], "the joint chi_A changed")
    expect(sha256_bytes(canonical(joint_a).encode()) == CHI_JOINT_A_SHA256, "joint chi_A SHA256 changed")
    expect(sha256_bytes(canonical(joint_b).encode()) == CHI_JOINT_B_SHA256, "joint chi_B SHA256 changed")
    expect(poly_mul(joint_a, joint_a) == coefficients_a, "the degree-16 polynomial is not the square of the degree-8 polynomial")
    for eigenvalue_u in (1, -1):
        for eigenvalue_v in (1, -1):
            vectors = character_space(
                group_actions,
                ((u_dest, u_sign, eigenvalue_u), (v_dest, v_sign, eigenvalue_v)),
            )
            expect(len(vectors) == 8, "a joint sign space of the explicit pair is not 8-dimensional")
            block, block_sizes = restriction_matrix(columns_b, columns, ports, vectors)
            expect(block_sizes == [32] * 8, "a joint basis vector does not have support 32")
            expect(
                scale_to_a(charpoly_newton(block)) == joint_a,
                "a joint sign space of the explicit pair has a different characteristic polynomial",
            )

    prime = 1_000_003
    expect(charpoly_mod(matrix, prime) == [coefficient % prime for coefficient in coefficients_b], "Hessenberg disagrees with Newton")
    for point in (0, 1, 2, 3, 5):
        shifted = [[(-entry) % prime for entry in row] for row in matrix]
        for index in range(16):
            shifted[index][index] = (shifted[index][index] + point) % prime
        expect(det_mod(shifted, prime) == horner(coefficients_b, point) % prime, "a determinant disagrees with chi_B")

    eigenvectors = []
    eigenvalues = []
    for left, right, kind in BLOCK_PAIRS:
        zero = [0] * 16
        other = [0] * 16
        if kind < 0:
            zero[left], zero[right] = 1, 1
            other[left], other[right] = 1, -1
            eigenvalues.append((zero, 0))
            eigenvalues.append((other, -2))
        else:
            zero[left], zero[right] = 1, -1
            other[left], other[right] = 1, 1
            eigenvalues.append((zero, 0))
            eigenvalues.append((other, 2))
        eigenvectors.extend((zero, other))
    for vector, eigenvalue in eigenvalues:
        image = mat_vec(matrix, vector)
        expect(image == [4 * eigenvalue * entry for entry in vector], "a block vector is not an eigenvector of A_3")
    eigen_matrix = [list(column) for column in zip(*eigenvectors)]
    expect(det_mod(eigen_matrix, prime) != 0, "the 16 block eigenvectors are linearly dependent")
    counts = {0: 0, 2: 0, -2: 0}
    for _vector, eigenvalue in eigenvalues:
        counts[eigenvalue] += 1
    expect(counts == {0: 8, 2: 4, -2: 4}, "geometric multiplicities are not 8, 4, 4")

    minus_matrix, _minus_sizes = restriction_matrix(columns_b, columns, ports, minus)
    expect(scale_to_a(charpoly_newton(minus_matrix)) == coefficients_a, "the u=-1 space has a different characteristic polynomial")

    described = splitting_involutions()
    expect((U_INV, U_EPS) in described and (V_INV, V_EPS) in described, "the explicit pair is missing from the described list")
    expect((product["inv"], product["eps"]) in described, "uv is missing from the described list")
    same_polynomial = 0
    for inv, eps in described:
        built = operator(inv, eps, port_of, lookup, port_basis, coords)
        expect(built is not None, "a described splitting involution is not a symmetry")
        expect(apply_linear(built["T"], SECTOR) == SECTOR, "a described splitting involution moves sector 3")
        expect(same_operator(compose(built, built), identity), "a described splitting involution does not square to the identity")
        dest, sign = action_tables(built)
        for eigenvalue in (1, -1):
            vectors = character_space(group_actions, ((dest, sign, eigenvalue),))
            expect(len(vectors) == 16, "a described eigenspace is not 16-dimensional")
            block, _sizes = restriction_matrix(columns_b, columns, ports, vectors)
            polynomial = scale_to_a(charpoly_newton(block))
            expect(polynomial == coefficients_a, "a described eigenspace has a different characteristic polynomial")
            expect(annihilated_by_split(block), "x(x-8)(x+8) does not kill a described matrix of B")
            same_polynomial += 1
    expect(same_polynomial == 192, "the described census did not cover both eigenvalues of all 96 involutions")

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

    basis_payload = {
        "index": "coordinate*512+address",
        "character": {"odds": list(ODDS), "value": "product of signs on coordinates 1,3,5,7"},
        "eigenvalues": {"H": "chi", "u": 1},
        "space": payload(plus),
        "joint_eigenvalues": {"u": 1, "v": 1},
        "joint_space": payload(joint_plus),
    }
    matrix_payload = {"rows": matrix, "joint_rows": joint_matrix}
    basis_path = PACKAGE / "evidence" / "basis.json"
    matrix_path = PACKAGE / "evidence" / "matrix.json"
    if dump:
        basis_path.parent.mkdir(parents=True, exist_ok=True)
        basis_path.write_text(canonical(basis_payload) + "\n")
        matrix_path.write_text(canonical(matrix_payload) + "\n")
    else:
        expect(json.loads(basis_path.read_text()) == basis_payload, "pinned basis does not match the recomputation")
        expect(json.loads(matrix_path.read_text()) == matrix_payload, "pinned matrix does not match the recomputation")

    transposition = operator((1, 0, 2, 3, 4, 5, 6, 7), (1,) * 8, port_of, lookup, port_basis, coords)
    expect(transposition is None, "a coordinate transposition was accepted as a symmetry")
    moved = dict(port_of)
    moved[columns[0]], moved[columns[1]] = port_of[columns[1]], port_of[columns[0]]
    swapped_lookup = {norm(column): moved[column] for column in moved}
    expect(operator(U_INV, U_EPS, moved, swapped_lookup, port_basis, coords) is None, "a swapped port label still looked like a symmetry")
    owners = {}
    for _root, items in plus:
        for index, _coeff in items:
            owners[index] = True
    for _root, items in plus:
        image = sector_one_image(items, columns, ports)
        expect(any(index not in owners for index in image), "the c=1 operator preserved a c=3 basis vector")
    without_u = character_space(group_actions, ())
    expect(len(without_u) == 32, "omitting u did not leave the 32-dimensional character")
    wrong_character = []
    flipped_character = False
    for element, (dest, sign, eigenvalue) in zip(group, group_actions):
        if not flipped_character and element["eps"] != (1,) * 8:
            wrong_character.append((dest, sign, -eigenvalue))
            flipped_character = True
        else:
            wrong_character.append((dest, sign, eigenvalue))
    expect(flipped_character, "the sign stabilizer had no non-identity element to flip")
    broken_sign = character_space(wrong_character, ((u_dest, u_sign, 1),))
    expect(len(broken_sign) != 16, "reversing one character value still left dimension 16")
    same_sign = operator((2, 1, 0, 3, 6, 5, 4, 7), (-1, 1, -1, 1, -1, 1, -1, 1), port_of, lookup, port_basis, coords)
    expect(same_sign is not None and apply_linear(same_sign["T"], SECTOR) == 48, "equal signs on both even cycles do not send sector 3 to 48")
    corrupted = [row[:] for row in matrix]
    corrupted[0][0] += 1
    expect(charpoly_mod(corrupted, prime) != charpoly_mod(matrix, prime), "changing a matrix entry preserved the characteristic polynomial")
    truncated = poly_mul(chi_b_from_blocks(3, 4), [0, 1])
    expect(truncated != coefficients_b, "dropping one (x+8) factor still matched chi_B")
    linked = None
    for dest, sign, eigenvalue in list(group_actions) + [(u_dest, u_sign, 1)]:
        for _root, items in plus:
            values = {index: coeff for index, coeff in items}
            for index, _coeff in items:
                if dest[index] != index and dest[index] in values:
                    linked = (dest, sign, eigenvalue, items, index)
                    break
            if linked:
                break
        if linked:
            break
    expect(linked is not None, "no signed involution links two basis coordinates")
    dest, sign, eigenvalue, items, index = linked
    expect(fixed_by(dest, sign, items, eigenvalue), "the unflipped basis vector is not fixed")
    flipped = [(item, -coeff if item == index else coeff) for item, coeff in items]
    expect(not fixed_by(dest, sign, flipped, eigenvalue), "a sign error in a basis vector was still fixed")

    print("PASS_C3_WEIGHT4_JOINT_CHARPOLY")
    print("selected kappa", SELECTED_KAPPA)
    print("weight-4 character dimension 32")
    print("u=+1 dimension 16; joint (u,v)=(+1,+1) dimension 8")
    print("chi_A = x^8 (x-2)^4 (x+2)^4")
    print("chi_joint = x^4 (x-2)^2 (x+2)^2")
    print("chi_A SHA256", CHI_A_SHA256)
    print("chi_B SHA256", CHI_B_SHA256)
    print("described involutions 96; both eigenvalues; same polynomial")
    print("geometric multiplicities on the pinned space", counts)


if __name__ == "__main__":
    main()
