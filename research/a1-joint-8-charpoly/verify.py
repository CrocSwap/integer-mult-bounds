#!/usr/bin/env python3
"""Characteristic polynomial of one 8-dimensional c=1 joint eigenspace of A_1.

The pinned query is the historical 8-by-112 centre matrix. B = 4 A_1 is the
integer operator on the c=1 block. The space is the joint (+1,+1) eigenspace
of the unique 32-dimensional character of the c=1 sign stabilizer and of the
involutions g and t. Acceptance uses explicit checks, so -O does not skip a
theorem or a rejection control.
"""

import hashlib
import json
import pathlib
import sys
from fractions import Fraction

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
C1 = 1
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
T_INV = (0, 5, 6, 3, 4, 1, 2, 7)
T_EPS = (1, 1, 1, -1, 1, 1, 1, -1)
SIGN_COORDINATES = (1, 2, 5, 6)
JOINT_COORDINATE = {(1, 1): 0, (1, -1): 3, (-1, 1): 4, (-1, -1): 7}
CHARACTER_HISTOGRAM = {864: 1, 432: 4, 192: 6, 80: 4, 32: 1}
# Monic factors of chi_B and chi_{A_1} on the pinned (+1,+1) space.
FACTORS_B = ((4, (0, 1)), (2, (-8, 1)), (2, (8, 1)))
FACTORS_A = ((4, (0, 1)), (2, (-2, 1)), (2, (2, 1)))
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
# Kernel bases of M, M-8I and M+8I in the ordered basis of V.
KERNELS = {
    "0": (
        (1, 1, 0, 0, 0, 0, 0, 0),
        (0, 0, -1, 1, 0, 0, 0, 0),
        (0, 0, 0, 0, 1, 1, 0, 0),
        (0, 0, 0, 0, 0, 0, -1, 1),
    ),
    "8": (
        (-1, 1, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, -1, 1, 0, 0),
    ),
    "-8": (
        (0, 0, 1, 1, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 1, 1),
    ),
}
CHI_A_SHA256 = "4078d16db1834dcd427c4f1094b96838a2c425c116c7cd1b60d46aa1f472f632"
CHI_B_SHA256 = "04375398447c3b08683582cc785814e9955ed62fcaa6725dc3467484c8a41457"


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
    ports = [int(q) for q in data["ports"]]
    expect(len(rows) == 8 and len(ports) == 112 and len(set(ports)) == 112, "query shape")
    columns = [tuple(int(rows[i].get(str(j), "0")) for i in range(8)) for j in range(112)]
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
    expect(len(basis) == 9, "the 112 ports do not span F2^9")
    coords = {address: tuple(rank_solve(basis, address)) for address in range(512)}
    gram = [[0] * 8 for _ in range(8)]
    for column in columns:
        for i in range(8):
            for k in range(8):
                gram[i][k] += column[i] * column[k]
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


def sign_pattern(mask):
    return tuple([1] + [-1 if (mask >> bit) & 1 else 1 for bit in range(7)])


def sign_group(port_of, lookup, basis, coords, sector):
    identity = tuple(range(8))
    group = []
    for mask in range(128):
        eps = sign_pattern(mask)
        built = operator(identity, eps, port_of, lookup, basis, coords)
        if built is None:
            continue
        if apply_linear(built["T"], sector) == sector:
            group.append(built)
    return group


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
            dest[src] = image_coordinate * 512 + apply_linear(transform, address)
            sign[src] = image_sign
    return dest, sign


def action_trace(dest, sign):
    return sum(sign[index] for index in range(4096) if dest[index] == index)


def closed_trace(element):
    dest, sign = action_tables(element)
    closed = trace_s(element["inv"], element["eps"]) * fixed_addresses(element["T"])
    expect(action_trace(dest, sign) == closed, "permutation trace disagrees with the closed trace formula")
    return closed, dest, sign


def check_involution(dest, sign, name):
    for src in range(4096):
        mid = dest[src]
        if dest[mid] != src or sign[src] * sign[mid] != 1:
            fail(name + " is not a signed involution")


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
        rd, sd = self.find(dst)
        rs, ss = self.find(src)
        if rd == rs:
            if sd != sgn * ss:
                self.dead[rd] = True
            return
        self.parent[rd] = rs
        self.rel[rd] = sgn * ss * sd
        if self.dead[rd] or self.dead[rs]:
            self.dead[rs] = True

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


def column_table(columns, ports):
    raw = [{} for _ in range(4096)]
    for port, root in zip(ports, columns):
        support = [k for k in range(8) if root[k]]
        if port & 1:
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
        support = [k for k in range(8) if root[k]]
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


def column_image(columns_b, items):
    image = {}
    for index, coeff in items:
        for target, value in columns_b[index].items():
            image[target] = image.get(target, 0) + coeff * value
    return {index: value for index, value in image.items() if value}


def operators_commute(columns_b, dest, sign):
    for src in range(4096):
        left_sign = sign[src]
        left = columns_b[dest[src]]
        right = {}
        for index, value in columns_b[src].items():
            image = dest[index]
            right[image] = right.get(image, 0) + sign[index] * value
        for key in set(left) | set(right):
            if left.get(key, 0) * left_sign != right.get(key, 0):
                return False
    return True


def restriction_matrix(columns_b, columns, ports, vectors):
    members = [items for _root, items in vectors]
    owners = {}
    grouped = [[] for _ in vectors]
    for component, items in enumerate(members):
        for index, coeff in items:
            owners[index] = (component, coeff)
            grouped[component].append((index, coeff))
    matrix = [[0] * len(vectors) for _ in vectors]
    sizes = [len(items) for items in members]
    for column, items in enumerate(members):
        by_columns = column_image(columns_b, items)
        by_literal = literal_image(items, columns, ports)
        expect(by_columns == by_literal, "the two actions of B disagree on a basis vector")
        alphas = {}
        for index, value in by_columns.items():
            info = owners.get(index)
            expect(info is not None, "B sends a basis vector outside the joint space")
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
        for right in range(left + 1, len(vectors)):
            expect(
                sizes[left] * matrix[left][right] == sizes[right] * matrix[right][left],
                "the Gram identity size_r M_rs = size_s M_sr failed",
            )
    return matrix


def mask_of(eps):
    return sum(1 << bit for bit in range(7) if eps[bit + 1] == -1)


def product_character(eps):
    sign = 1
    for coordinate in SIGN_COORDINATES:
        sign *= eps[coordinate]
    return sign


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
        expect(reduced == 0, "sign stabilizer is not an elementary abelian 2-group")
        return coef

    def value(chi, mask):
        sign = 1
        for index, bit in enumerate(coordinates(mask)):
            if bit and (chi >> index) & 1:
                sign = -sign
        return sign

    return basis, value


def twisted_trace(element, group, character):
    total = 0
    for symmetry in group:
        composed = compose(element, symmetry)
        trace, _dest, _sign = closed_trace(composed)
        total += character(symmetry["eps"]) * trace
    expect(total % len(group) == 0, "a character trace is not an integer")
    return total // len(group)


def poly_mul(left, right):
    output = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            output[i + j] += a * b
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


def product_factors(factors):
    value = [1]
    for multiplicity, coefficients in factors:
        value = poly_mul(value, poly_pow(list(coefficients), multiplicity))
    return value


def charpoly_2x2(block):
    a, b = block[0]
    c, d = block[1]
    # det(xI - block) = x^2 - tr x + det, ascending.
    return [a * d - b * c, -(a + d), 1]


def leverrier(matrix):
    size = len(matrix)
    current = [[0] * size for _ in range(size)]
    coefficients = [0] * (size + 1)
    coefficients[0] = 1
    for step in range(1, size + 1):
        added = [row[:] for row in current]
        for index in range(size):
            added[index][index] += coefficients[step - 1]
        current = [[0] * size for _ in range(size)]
        for i in range(size):
            for t in range(size):
                weight = matrix[i][t]
                if weight == 0:
                    continue
                for j in range(size):
                    current[i][j] += weight * added[t][j]
        trace = sum(current[index][index] for index in range(size))
        expect(trace % step == 0, "Leverrier trace is not divisible by the step index")
        coefficients[step] = -trace // step
    return list(reversed(coefficients))


def bareiss_det(matrix):
    size = len(matrix)
    work = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for col in range(size - 1):
        if work[col][col] == 0:
            pivot = None
            for row in range(col + 1, size):
                if work[row][col]:
                    pivot = row
                    break
            if pivot is None:
                return 0
            work[col], work[pivot] = work[pivot], work[col]
            sign = -sign
        pivot = work[col][col]
        for row in range(col + 1, size):
            for index in range(col + 1, size):
                numerator = pivot * work[row][index] - work[row][col] * work[col][index]
                expect(numerator % previous == 0, "Bareiss division is not exact")
                work[row][index] = numerator // previous
            work[row][col] = 0
        previous = pivot
    return sign * work[-1][-1]


def evaluate(coefficients, point):
    value = 0
    power = 1
    for coefficient in coefficients:
        value += coefficient * power
        power *= point
    return value


def shifted_matrix(matrix, point):
    size = len(matrix)
    shifted = [[-entry for entry in row] for row in matrix]
    for index in range(size):
        shifted[index][index] += point
    return shifted


def matmul(left, right):
    size = len(left)
    output = [[0] * size for _ in range(size)]
    for i in range(size):
        for t in range(size):
            weight = left[i][t]
            if weight == 0:
                continue
            for j in range(size):
                output[i][j] += weight * right[t][j]
    return output


def matvec(matrix, vector):
    return [sum(entry * value for entry, value in zip(row, vector)) for row in matrix]


def rational_rank(matrix):
    if not matrix:
        return 0
    rows = [[Fraction(entry) for entry in row] for row in matrix]
    width = len(rows[0])
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, len(rows)):
            if rows[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][col]
        for index in range(width):
            rows[rank][index] /= pivot_value
        for row in range(len(rows)):
            if row == rank or rows[row][col] == 0:
                continue
            factor = rows[row][col]
            for index in range(width):
                rows[row][index] -= factor * rows[rank][index]
        rank += 1
    return rank


def det_mod(matrix, prime):
    size = len(matrix)
    work = [[entry % prime for entry in row] for row in matrix]
    determinant = 1
    for col in range(size):
        pivot = None
        for row in range(col, size):
            if work[row][col]:
                pivot = row
                break
        if pivot is None:
            return 0
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            determinant = (-determinant) % prime
        determinant = determinant * work[col][col] % prime
        inverse = pow(work[col][col], -1, prime)
        for row in range(col + 1, size):
            factor = work[row][col]
            if factor == 0:
                continue
            factor = factor * inverse % prime
            for index in range(col, size):
                work[row][index] = (work[row][index] - factor * work[col][index]) % prime
    return determinant


def histogram(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def solve_joint(actions, eigenvalues, g_dest, g_sign, t_dest, t_sign, g_value, t_value):
    lattice = Lattice()
    for (dest, sign), eigenvalue in zip(actions, eigenvalues):
        lattice.add_operator(dest, sign, eigenvalue)
    lattice.add_operator(g_dest, g_sign, g_value)
    lattice.add_operator(t_dest, t_sign, t_value)
    return lattice.basis()


def descending(coefficients):
    parts = []
    for power, coefficient in reversed(list(enumerate(coefficients))):
        if coefficient == 0:
            continue
        if power == 0:
            body = str(abs(coefficient))
        else:
            letter = "x" if power == 1 else "x^" + str(power)
            body = letter if abs(coefficient) == 1 else str(abs(coefficient)) + letter
        if not parts:
            parts.append(body if coefficient > 0 else "-" + body)
        else:
            parts.append(("+ " if coefficient > 0 else "- ") + body)
    return " ".join(parts) if parts else "0"


def main():
    dump = "--dump-evidence" in sys.argv
    columns, ports = load_query()
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result.json bytes changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")
    certificate_bytes = CERTIFICATE.read_bytes()
    expect(sha256_bytes(certificate_bytes) == CERTIFICATE_SHA256, "one-slot certificate bytes changed")

    port_of, lookup, port_basis, coords = prepare(columns, ports)
    group = sign_group(port_of, lookup, port_basis, coords, C1)
    described = []
    for mask in range(128):
        eps = sign_pattern(mask)
        negatives = [index for index, sign in enumerate(eps) if sign < 0]
        if all(index in SIGN_COORDINATES for index in negatives):
            described.append(eps)
    expect(len(described) == 16, "the coordinate description of H does not have order 16")
    expect(len(group) == 16, "c=1 sign stabilizer does not have order 16")
    expect({element["eps"] for element in group} == set(described), "H is not the sign patterns supported on coordinates 1, 2, 5 and 6")
    for element in group:
        expect(element["inv"] == tuple(range(8)), "a sign-stabilizer element moves a coordinate")
        expect(same_operator(compose(element, element), {
            "inv": tuple(range(8)),
            "eps": (1, 1, 1, 1, 1, 1, 1, 1),
            "T": tuple(1 << bit for bit in range(9)),
        }), "a sign-stabilizer element is not an involution")

    first = operator(G_INV, G_EPS, port_of, lookup, port_basis, coords)
    second = operator(T_INV, T_EPS, port_of, lookup, port_basis, coords)
    expect(first is not None and second is not None, "an explicit splitter is not a symmetry")
    identity = {
        "inv": tuple(range(8)),
        "eps": (1, 1, 1, 1, 1, 1, 1, 1),
        "T": tuple(1 << bit for bit in range(9)),
    }
    expect(same_operator(compose(first, first), identity), "g is not an involution")
    expect(same_operator(compose(second, second), identity), "t is not an involution")
    expect(same_operator(compose(first, second), compose(second, first)), "g and t do not commute")
    expect(apply_linear(first["T"], C1) == C1 and apply_linear(second["T"], C1) == C1, "a splitter moves sector 1")
    expect(apply_linear(first["T"], 3) == 343, "g does not send sector 3 to 343")
    expect(apply_linear(second["T"], 3) == 3, "t does not preserve sector 3")
    for coordinate, (g_value, t_value) in (
        (0, (1, 1)),
        (3, (1, -1)),
        (4, (-1, 1)),
        (7, (-1, -1)),
    ):
        expect(G_INV[coordinate] == coordinate and T_INV[coordinate] == coordinate, "a reported support coordinate is moved")
        expect(G_EPS[coordinate] == g_value and T_EPS[coordinate] == t_value, "a support coordinate has the wrong sign pair")
        expect(JOINT_COORDINATE[(g_value, t_value)] == coordinate, "joint coordinate table is inconsistent")

    for element in group:
        conjugated_g = compose(first, compose(element, first))
        conjugated_t = compose(second, compose(element, second))
        expect(conjugated_g["inv"] == tuple(range(8)) and conjugated_t["inv"] == tuple(range(8)), "conjugation by g or t leaves H")
        expect(product_character(conjugated_g["eps"]) == product_character(element["eps"]), "g does not preserve chi")
        expect(product_character(conjugated_t["eps"]) == product_character(element["eps"]), "t does not preserve chi")
    expect(product_character(sign_pattern(1)) == -1, "chi is the trivial character")

    _f2_basis, dual_value = character_model(group)
    expect(len(_f2_basis) == 4, "the sign stabilizer does not have F2-rank 4")
    dimensions = []
    product_index = None
    for chi in range(16):
        total = 0
        matches_product = True
        for element in group:
            trace, _dest, _sign = closed_trace(element)
            sign = dual_value(chi, mask_of(element["eps"]))
            total += sign * trace
            if sign != product_character(element["eps"]):
                matches_product = False
        expect(total % 16 == 0, "a character dimension is not an integer")
        dimensions.append(total // 16)
        if matches_product:
            expect(product_index is None, "two dual characters equal the product character")
            product_index = chi
    expect(product_index is not None, "the product character is not a character of H")
    expect(histogram(dimensions) == CHARACTER_HISTOGRAM, "c=1 character dimensions changed")
    expect(dimensions[product_index] == 32, "the product character does not have dimension 32")
    expect(dimensions.count(32) == 1, "more than one character has dimension 32")
    expect(sum(dimensions) == 4096, "character dimensions do not cover the block")

    actions = []
    eigenvalues = []
    for element in group:
        _trace, dest, sign = closed_trace(element)
        check_involution(dest, sign, "stabilizer element")
        actions.append((dest, sign))
        eigenvalues.append(product_character(element["eps"]))
    g_trace, g_dest, g_sign = closed_trace(first)
    t_trace, t_dest, t_sign = closed_trace(second)
    check_involution(g_dest, g_sign, "g")
    check_involution(t_dest, t_sign, "t")
    expect(g_trace == trace_s(G_INV, G_EPS) * fixed_addresses(first["T"]), "g trace changed")
    character_trace = twisted_trace(identity, group, product_character)
    joint_traces = [
        twisted_trace(element, group, product_character)
        for element in (identity, first, second, compose(first, second))
    ]
    expect(character_trace == 32 and joint_traces[0] == 32, "trace formula does not give the 32-dimensional character")
    numerator = joint_traces[0] + joint_traces[1] + joint_traces[2] + joint_traces[3]
    expect(numerator % 4 == 0 and numerator // 4 == 8, "trace formula does not give an 8-dimensional (+1,+1) space")

    character = Lattice()
    for (dest, sign), eigenvalue in zip(actions, eigenvalues):
        character.add_operator(dest, sign, eigenvalue)
    character_vectors = character.basis()
    expect(len(character_vectors) == 32, "explicit character basis does not have dimension 32")
    allowed_coordinates = set(JOINT_COORDINATE.values())
    for _root, items in character_vectors:
        for index, _coeff in items:
            expect(index // 512 in allowed_coordinates, "the 32-dimensional character meets a moved coordinate")

    spaces = {}
    for g_value in (1, -1):
        for t_value in (1, -1):
            vectors = solve_joint(actions, eigenvalues, g_dest, g_sign, t_dest, t_sign, g_value, t_value)
            expect(len(vectors) == 8, "a joint eigenspace does not have dimension 8")
            coordinate = JOINT_COORDINATE[(g_value, t_value)]
            for _root, items in vectors:
                expect(len(items) == 8, "a joint basis vector does not have support 8")
                expect({coeff for _index, coeff in items} <= {-1, 1}, "a joint basis coefficient is not a sign")
                for index, _coeff in items:
                    expect(index // 512 == coordinate, "a joint basis vector leaves its sign coordinate")
                for (dest, sign), eigenvalue in zip(actions, eigenvalues):
                    expect(fixed_by(dest, sign, items, eigenvalue), "a basis vector misses the character eigenvalue")
                expect(fixed_by(g_dest, g_sign, items, g_value), "a basis vector misses the g eigenvalue")
                expect(fixed_by(t_dest, t_sign, items, t_value), "a basis vector misses the t eigenvalue")
            spaces[(g_value, t_value)] = vectors
    occupied = {}
    for key, vectors in spaces.items():
        for root, items in vectors:
            expect(items[0] == (root, 1), "the least basis index is not the positive representative")
            for index, _coeff in items:
                expect(index not in occupied, "joint basis supports are not disjoint")
                occupied[index] = key
    # Eight vectors in each of four spaces, each of support 8, on four distinct coordinates.
    expect(len(occupied) == 256, "the four joint bases do not have 256 disjoint coordinates")
    expect(len({root for vectors in spaces.values() for root, _items in vectors}) == 32, "the 32 joint basis vectors do not have distinct pivots")

    columns_b = column_table(columns, ports)
    for dest, sign in actions:
        expect(operators_commute(columns_b, dest, sign), "B does not commute with a sign symmetry")
    expect(operators_commute(columns_b, g_dest, g_sign), "B does not commute with g")
    expect(operators_commute(columns_b, t_dest, t_sign), "B does not commute with t")

    matrices = {}
    polynomials = {}
    for key, vectors in spaces.items():
        matrix = restriction_matrix(columns_b, columns, ports, vectors)
        expect(len(matrix) == 8 and all(len(row) == 8 for row in matrix), "a joint matrix is not 8 by 8")
        polynomials[key] = leverrier(matrix)
        matrices[key] = matrix
    primary = matrices[(1, 1)]
    expect(tuple(tuple(row) for row in primary) == EXPECTED_MATRIX, "the recomputed (+1,+1) matrix changed")
    blocks = (
        charpoly_2x2([row[:2] for row in EXPECTED_MATRIX[:2]]),
        charpoly_2x2([row[2:4] for row in EXPECTED_MATRIX[2:4]]),
        charpoly_2x2([row[4:6] for row in EXPECTED_MATRIX[4:6]]),
        charpoly_2x2([row[6:8] for row in EXPECTED_MATRIX[6:8]]),
    )
    expect(blocks == ([0, -8, 1], [0, 8, 1], [0, -8, 1], [0, 8, 1]), "a 2-by-2 block polynomial changed")
    coefficients_b = [1]
    for block in blocks:
        coefficients_b = poly_mul(coefficients_b, block)
    expect(coefficients_b == product_factors(FACTORS_B), "the block product is not x^4 (x-8)^2 (x+8)^2")
    expect(coefficients_b == polynomials[(1, 1)], "Leverrier disagrees with the block factorization")
    expect(all(polynomials[key] == coefficients_b for key in polynomials), "a joint sign pair has a different characteristic polynomial")
    expect(coefficients_b == [0, 0, 0, 0, 4096, 0, -128, 0, 1], "chi_B coefficients changed")
    for point in (0, 1, 2, 3, 5, 8, -2, 4):
        expect(bareiss_det(shifted_matrix(primary, point)) == evaluate(coefficients_b, point), "determinant disagrees with chi_B")
        expect(
            det_mod(shifted_matrix(primary, point), 1_000_003) == evaluate(coefficients_b, point) % 1_000_003,
            "modular determinant disagrees with chi_B",
        )
    expect(all(coefficient % (4 ** (8 - index)) == 0 for index, coefficient in enumerate(coefficients_b)), "chi_A is not an integer polynomial")
    coefficients_a = [coefficient // (4 ** (8 - index)) for index, coefficient in enumerate(coefficients_b)]
    expect(coefficients_a == product_factors(FACTORS_A), "the pinned factors do not multiply to chi_A")
    expect(coefficients_a == [0, 0, 0, 0, 16, 0, -8, 0, 1], "chi_A coefficients changed")
    # chi_A(x) = 4^{-8} chi_B(4x): the coefficient of x^k in chi_A, times 4^{8-k}, is the coefficient in chi_B.
    expect(
        [coefficient * (4 ** (8 - index)) for index, coefficient in enumerate(coefficients_a)] == coefficients_b,
        "chi_A is not 4^{-8} chi_B(4x)",
    )
    expect(sha256_bytes(canonical(coefficients_a).encode()) == CHI_A_SHA256, "chi_A SHA256 changed")
    expect(sha256_bytes(canonical(coefficients_b).encode()) == CHI_B_SHA256, "chi_B SHA256 changed")
    on_character = [1]
    for _key in range(4):
        on_character = poly_mul(on_character, coefficients_a)
    expect(on_character == poly_pow(coefficients_a, 4), "the fourth-power identity failed")

    for key, matrix in matrices.items():
        square = matmul(matrix, matrix)
        shifted = [row[:] for row in square]
        for index in range(8):
            shifted[index][index] -= 64
        annihilated = matmul(matrix, shifted)
        expect(all(entry == 0 for row in annihilated for entry in row), "M(M^2-64 I) is not zero on a joint space")
        for eigenvalue, nullity in ((0, 4), (8, 2), (-8, 2)):
            shifted_operator = [row[:] for row in matrix]
            for index in range(8):
                shifted_operator[index][index] -= eigenvalue
            expect(
                rational_rank(shifted_operator) == 8 - nullity,
                "a joint space does not have the pinned rational nullity",
            )
    for label, eigenvalue in (("0", 0), ("8", 8), ("-8", -8)):
        vectors = KERNELS[label]
        expect(rational_rank([list(vector) for vector in vectors]) == len(vectors), "pinned kernel vectors are dependent")
        for vector in vectors:
            image = matvec(primary, vector)
            expect(image == [eigenvalue * entry for entry in vector], "a pinned kernel vector is not an eigenvector")
        shifted_operator = [row[:] for row in primary]
        for index in range(8):
            shifted_operator[index][index] -= eigenvalue
        expect(rational_rank(shifted_operator) == 8 - len(vectors), "rational nullity disagrees with the pinned kernel")

    certificate = json.loads(certificate_bytes)
    expect(certificate["source_sha256"] == INTERFACE_SHA256, "published one-slot certificate names a different query")
    expect(certificate["operator"] == "B=4*A_1", "published certificate is not the integer operator B")
    sectors = {}
    for sector in certificate["sectors"]:
        if sector["c"] == 1:
            sectors[(sector["t"], sector["s"])] = [int(value) for value in sector["coefficients"]]
    expect(set(sectors) == {(0, 1), (0, -1), (1, 1), (1, -1)}, "c=1 sector labels changed")
    for key, coefficients in sectors.items():
        expect(coefficients[-1] == 1, "a c=1 sector polynomial is not monic")
        for root in (0, 8, -8):
            expect(evaluate(coefficients, root) == 0, "a sector minimal polynomial misses an eigenvalue of this block at " + str(key))

    basis_payload = {
        "index": "coordinate*512+address",
        "character": "product of signs on coordinates 1, 2, 5 and 6",
        "eigenvalues": {"g": 1, "t": 1},
        "support_coordinate": 0,
        "roots": [root for root, _items in spaces[(1, 1)]],
        "vectors": [[[index, coeff] for index, coeff in items] for _root, items in spaces[(1, 1)]],
    }
    matrix_payload = {"rows": primary}
    character_payload = {
        "negative_sign_coordinates": list(SIGN_COORDINATES),
        "formula": "eps[1] * eps[2] * eps[5] * eps[6]",
        "elements": [
            {"eps": list(element["eps"]), "chi": product_character(element["eps"])}
            for element in sorted(group, key=lambda item: mask_of(item["eps"]))
        ],
    }
    kernel_payload = {label: [list(vector) for vector in vectors] for label, vectors in KERNELS.items()}
    evidence = PACKAGE / "evidence"
    paths = {
        evidence / "basis.json": basis_payload,
        evidence / "matrix.json": matrix_payload,
        evidence / "character.json": character_payload,
        evidence / "kernels.json": kernel_payload,
    }
    if dump:
        evidence.mkdir(exist_ok=True)
        for path, payload in paths.items():
            path.write_text(canonical(payload) + "\n", encoding="utf-8")
    else:
        for path, payload in paths.items():
            expect(path.is_file(), "missing pinned evidence " + path.name)
            expect(json.loads(path.read_text(encoding="utf-8")) == payload, "pinned " + path.name + " does not match the recomputation")

    transposition = operator((1, 0, 2, 3, 4, 5, 6, 7), (1,) * 8, port_of, lookup, port_basis, coords)
    expect(transposition is None, "a coordinate transposition was accepted as a symmetry")
    moved = dict(port_of)
    moved[columns[0]], moved[columns[1]] = port_of[columns[1]], port_of[columns[0]]
    swapped_lookup = {norm(column): moved[column] for column in moved}
    expect(operator(G_INV, G_EPS, moved, swapped_lookup, port_basis, coords) is None, "a swapped port label still looked like a symmetry")
    trivial_actions = [(dest, sign) for dest, sign in actions]
    trivial_eigenvalues = [1 for _element in group]
    trivial_joint = solve_joint(trivial_actions, trivial_eigenvalues, g_dest, g_sign, t_dest, t_sign, 1, 1)
    expect(len(trivial_joint) == 216, "the trivial character joint space no longer has dimension 216")
    expect(len(trivial_joint) != 8, "the trivial-character control collapsed to dimension 8")
    shortened = Lattice()
    for (dest, sign), eigenvalue in zip(actions, eigenvalues):
        shortened.add_operator(dest, sign, eigenvalue)
    shortened.add_operator(t_dest, t_sign, 1)
    expect(len(shortened.basis()) == 16, "omitting g did not leave the 16-dimensional t=+1 space")
    other = Lattice()
    for element, (dest, sign) in zip(group, actions):
        eigenvalue = product_character(element["eps"])
        if element["eps"][1] == -1 and element["eps"][2] == element["eps"][5] == element["eps"][6] == 1:
            eigenvalue = -eigenvalue
        other.add_operator(dest, sign, eigenvalue)
    other.add_operator(g_dest, g_sign, 1)
    other.add_operator(t_dest, t_sign, 1)
    expect(len(other.basis()) != 8, "flipping chi on one generator still produced dimension 8")
    corrupted = [list(row) for row in primary]
    corrupted[0][0] += 1
    expect(leverrier(corrupted) != coefficients_b, "changing a matrix entry preserved chi_B")
    expect(product_factors(FACTORS_A[:-1]) != coefficients_a, "dropping a factor still multiplied to chi_A")
    linked = None
    checks = [(dest, sign, eigenvalue) for (dest, sign), eigenvalue in zip(actions, eigenvalues)]
    checks.append((g_dest, g_sign, 1))
    checks.append((t_dest, t_sign, 1))
    for dest, sign, eigenvalue in checks:
        for _root, items in spaces[(1, 1)]:
            values = {index: coeff for index, coeff in items}
            for index, _coeff in items:
                image = dest[index]
                if image != index and image in values:
                    linked = (dest, sign, items, index, eigenvalue)
                    break
            if linked is not None:
                break
        if linked is not None:
            break
    expect(linked is not None, "no signed symmetry links two basis coordinates; the sign control is vacuous")
    dest, sign, items, index, eigenvalue = linked
    flipped = [(item, -coeff if item == index else coeff) for item, coeff in items]
    expect(not fixed_by(dest, sign, flipped, eigenvalue), "a sign error in a basis vector was still fixed")

    print("PASS_A1_JOINT_8_CHARPOLY")
    print("selected kappa", SELECTED_KAPPA)
    print("character chi = eps1 eps2 eps5 eps6; dimension 32")
    print("joint (+1,+1) support coordinate 0; dimension 8")
    print("four joint sign pairs are isospectral and diagonalizable")
    print("chi_A =", descending(coefficients_a))
    print("chi_B =", descending(coefficients_b))
    print("chi_A SHA256", CHI_A_SHA256)
    print("chi_B SHA256", CHI_B_SHA256)
    print("nullities of B at 0, 8, -8 are 4, 2, 2")


if __name__ == "__main__":
    main()
