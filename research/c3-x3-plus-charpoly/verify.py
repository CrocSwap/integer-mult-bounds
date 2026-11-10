#!/usr/bin/env python3
"""Characteristic polynomial of the 84-dimensional X_3=+1 subspace.

The space is the trivial character of the c=3 even-positive sign group H,
inside the joint (+1,+1) eigenspace of the explicit pair (u, v), cut by the
payload involution X_3 at eigenvalue +1. B = 4 A_1 is the integer operator
on Bell block c=3. Acceptance uses explicit checks, so python -O does not
skip a theorem or a rejection control.
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
SELECTED_SHA256 = "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
CERTIFICATE_SHA256 = "29e0b0d86c7fd8929ad36d9de48c2b8b55500491576dc5ac1d0b1ff076d27483"
SELECTED_KAPPA = "781451/250000000"
SECTOR = 3
CHARACTER = 508
ODDS = (1, 3, 5, 7)
U_INV = (2, 1, 0, 3, 6, 5, 4, 7)
U_EPS = (-1, 1, -1, 1, 1, 1, 1, 1)
V_INV = (4, 1, 6, 3, 0, 5, 2, 7)
V_EPS = (-1, 1, 1, 1, -1, 1, 1, 1)
CHI_A_SHA256 = "c4bcbd4e52f92d13f3ad451d92c9d22256e7725e4be24ee203bea1c96c129648"
CHI_B_SHA256 = "185b51cfd084f95c1dbd814b0b211ce4ab35b2d59604d7795715d65a0a4e5e65"
# Monic irreducible factors of chi_{A_1}, ascending coefficients, with multiplicity.
FACTORS = (
    (16, (0, 1)),
    (1, (-14, 1)),
    (1, (-12, 1)),
    (6, (-4, 1)),
    (14, (-2, 1)),
    (14, (2, 1)),
    (6, (4, 1)),
    (1, (12, 1)),
    (1, (14, 1)),
    (2, (16, -8, -16, 0, 1)),
    (2, (16, 8, -16, 0, 1)),
    (1, (-32, 32, 20, -12, 1)),
    (1, (-32, -32, 20, 12, 1)),
)
# Which published c=3, s=+1 sector polynomials, labelled by t, each factor divides.
SECTOR_HITS = (
    (0, 1),
    (0,),
    (1,),
    (0,),
    (0, 1),
    (0, 1),
    (1,),
    (0,),
    (1,),
    (1,),
    (0,),
    (0,),
    (1,),
)
# Square-free factors of the two Z_508 eigenspaces inside the 84-space.
FACTORS_T0 = (
    (1, (-14, 1)),
    (1, (12, 1)),
    (6, (-4, 1)),
    (6, (2, 1)),
    (8, (-2, 1)),
    (8, (0, 1)),
    (1, (-32, 32, 20, -12, 1)),
    (2, (16, 8, -16, 0, 1)),
)
FACTORS_T1 = (
    (1, (-12, 1)),
    (1, (14, 1)),
    (6, (-2, 1)),
    (6, (4, 1)),
    (8, (0, 1)),
    (8, (2, 1)),
    (1, (-32, -32, 20, 12, 1)),
    (2, (16, -8, -16, 0, 1)),
)
# Rational eigenvalues of A_1 and their common algebraic and geometric multiplicity.
RATIONAL_EIGENVALUES = (
    (0, 16),
    (2, 14),
    (-2, 14),
    (4, 6),
    (-4, 6),
    (12, 1),
    (-12, 1),
    (14, 1),
    (-14, 1),
)


def fail(message):
    raise SystemExit("FAIL: " + message)


def expect(condition, message):
    if not condition:
        fail(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def dot(left, right):
    return bin(left & right).count("1") & 1


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
    expect(sha256_bytes(raw) == INTERFACE_SHA256, "INTERFACE.json hash changed")
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result.json bytes changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")
    certificate_bytes = CERTIFICATE.read_bytes()
    expect(sha256_bytes(certificate_bytes) == CERTIFICATE_SHA256, "one-slot certificate bytes changed")
    data = json.loads(raw)
    ports = [int(port) for port in data["ports"]]
    rows = data["R"]
    columns = [
        tuple(int(rows[row].get(str(column), "0")) for row in range(8))
        for column in range(112)
    ]
    expect(len(ports) == 112 and len(set(ports)) == 112, "ports are not 112 distinct labels")
    expect(all(value in (-1, 0, 1) for column in columns for value in column), "a column entry is outside {-1,0,1}")
    gram = [[0] * 8 for _ in range(8)]
    for column in columns:
        expect(sum(value != 0 for value in column) == 4, "a column does not have weight 4")
        for index, value in enumerate(column):
            for other in range(8):
                gram[index][other] += value * column[other]
    expect(all(gram[i][k] == (56 if i == k else 0) for i in range(8) for k in range(8)), "RR^T is not 56 I")
    expect(all(dot(port, 511) == 1 for port in ports), "a port label has even weight")
    return columns, ports


def prepare(columns, ports):
    port_of = {column: port for column, port in zip(columns, ports)}
    lookup = {norm(column): port for column, port in port_of.items()}
    basis = []
    for port in ports:
        if rank_solve(basis + [port]) == len(basis) + 1:
            basis.append(port)
        if len(basis) == 9:
            break
    expect(len(basis) == 9, "the ports do not span F2^9")
    coords = {address: tuple(rank_solve(basis, address)) for address in range(512)}
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
            if dot(basis[left], basis[right]) != dot(images[left], images[right]):
                return None
    return {"inv": tuple(inv), "eps": tuple(eps), "T": tuple(matrix)}


def compose(left, right):
    inv = tuple(right["inv"][left["inv"][index]] for index in range(8))
    eps = tuple(left["eps"][index] * right["eps"][left["inv"][index]] for index in range(8))
    matrix = tuple(apply_linear(left["T"], column) for column in right["T"])
    return {"inv": inv, "eps": eps, "T": matrix}


def same_operator(left, right):
    return left["inv"] == right["inv"] and left["eps"] == right["eps"] and left["T"] == right["T"]


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


def translation_action(shift):
    dest = [0] * 4096
    sign = [1] * 4096
    for coordinate in range(8):
        for address in range(512):
            dest[coordinate * 512 + address] = coordinate * 512 + (address ^ shift)
    return dest, sign


def diagonal_action(character):
    dest = list(range(4096))
    sign = [0] * 4096
    for coordinate in range(8):
        for address in range(512):
            sign[coordinate * 512 + address] = -1 if dot(character, address) else 1
    return dest, sign


def compose_actions(left, right):
    left_dest, left_sign = left
    right_dest, right_sign = right
    dest = [0] * 4096
    sign = [0] * 4096
    for src in range(4096):
        mid = right_dest[src]
        dest[src] = left_dest[mid]
        sign[src] = right_sign[src] * left_sign[mid]
    return dest, sign


def action_trace(dest, sign):
    return sum(sign[index] for index in range(4096) if dest[index] == index)


class Lattice:
    """Solution space of v[dst] = sign * v[src] on Q^4096."""

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


def column_table(columns, ports, sector):
    raw = [{} for _ in range(4096)]
    for port, root in zip(ports, columns):
        support = [index for index in range(8) if root[index]]
        translating = dot(port, sector) == 1
        for coordinate in support:
            weight = root[coordinate]
            for address in range(512):
                src = coordinate * 512 + address
                if translating:
                    target = address ^ port
                    parity = 1
                else:
                    target = address
                    parity = -1 if dot(port, address) else 1
                bucket = raw[src]
                term = weight * parity
                for out_coordinate in support:
                    index = out_coordinate * 512 + target
                    bucket[index] = bucket.get(index, 0) + root[out_coordinate] * term
    return [{index: value for index, value in column.items() if value} for column in raw]


def literal_image(items, columns, ports, sector):
    image = {}
    for port, root in zip(ports, columns):
        support = [index for index in range(8) if root[index]]
        buckets = {}
        for index, coeff in items:
            coordinate, address = divmod(index, 512)
            if root[coordinate]:
                buckets[address] = buckets.get(address, 0) + root[coordinate] * coeff
        translating = dot(port, sector) == 1
        for address, acc in buckets.items():
            if translating:
                target = address ^ port
                parity = 1
            else:
                target = address
                parity = -1 if dot(port, address) else 1
            acc *= parity
            for coordinate in support:
                index = coordinate * 512 + target
                image[index] = image.get(index, 0) + root[coordinate] * acc
    return {index: value for index, value in image.items() if value}


def column_image(columns_b, items):
    image = {}
    for index, coeff in items:
        for target, value in columns_b[index].items():
            image[target] = image.get(target, 0) + coeff * value
    return {index: value for index, value in image.items() if value}


def operator_trace(columns_b, dest, sign):
    total = 0
    for src in range(4096):
        value = columns_b[dest[src]].get(src, 0)
        if value:
            total += sign[src] * value
    return total


def restriction_matrix(columns_b, columns, ports, vectors, sector):
    members = [items for _root, items in vectors]
    owners = {}
    for component, items in enumerate(members):
        for index, coeff in items:
            owners[index] = (component, coeff)
    matrix = [[0] * len(vectors) for _ in vectors]
    sizes = [len(items) for items in members]
    for column, items in enumerate(members):
        by_columns = column_image(columns_b, items)
        by_literal = literal_image(items, columns, ports, sector)
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
            matrix[component][column] = alpha
    for left in range(len(vectors)):
        for right in range(left + 1, len(vectors)):
            expect(
                sizes[left] * matrix[left][right] == sizes[right] * matrix[right][left],
                "the Gram identity size_r M_rs = size_s M_sr failed",
            )
    return matrix, sizes


def subspace_preserved(columns_b, vectors):
    owners = set()
    for _root, items in vectors:
        for index, _coeff in items:
            owners.add(index)
    for _root, items in vectors:
        for index in column_image(columns_b, items):
            if index not in owners:
                return False
    return True


def is_prime(number):
    if number < 2:
        return False
    if number % 2 == 0:
        return number == 2
    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def primes_past(limit):
    modulus = 1
    primes = []
    candidate = 1_000_003
    while modulus <= limit:
        if is_prime(candidate):
            primes.append(candidate)
            modulus *= candidate
        candidate += 2
    return primes, modulus


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
        minors.append([value % prime for value in output])
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


def crt_signed(residues, primes):
    value = 0
    modulus = 1
    for residue, prime in zip(residues, primes):
        increment = ((residue - value) % prime) * pow(modulus % prime, -1, prime) % prime
        value += increment * modulus
        modulus *= prime
    if value > modulus // 2:
        value -= modulus
    return value


def coeff_bound(size, row_sum):
    best = 1
    binomial = 1
    power = 1
    for degree in range(size + 1):
        term = binomial * power
        if term > best:
            best = term
        if degree < size:
            binomial = binomial * (size - degree) // (degree + 1)
            power *= row_sum
    return best


def charpoly(matrix):
    size = len(matrix)
    row_sum = max(sum(abs(entry) for entry in row) for row in matrix)
    bound = coeff_bound(size, row_sum)
    primes, modulus = primes_past(2 * bound)
    expect(modulus > 2 * bound, "CRT modulus does not exceed the coefficient bound")
    residues = [[] for _ in range(size + 1)]
    for prime in primes:
        polynomial = charpoly_mod(matrix, prime)
        for index, coefficient in enumerate(polynomial):
            residues[index].append(coefficient)
    coefficients = [crt_signed(residues[index], primes) for index in range(size + 1)]
    expect(coefficients[-1] == 1, "characteristic polynomial of B is not monic")
    expect(sum(matrix[index][index] for index in range(size)) == -coefficients[-2], "trace disagrees with chi_B")
    for point in (0, 1, 2, 3, 5):
        work = [[(-entry) % primes[0] for entry in row] for row in matrix]
        for index in range(size):
            work[index][index] = (work[index][index] + point) % primes[0]
        evaluated = 0
        power = 1
        for coefficient in coefficients:
            evaluated = (evaluated + coefficient * power) % primes[0]
            power = power * point % primes[0]
        expect(det_mod(work, primes[0]) == evaluated, "chi_B disagrees with det(tI-M) at " + str(point))
    for index, coefficient in enumerate(coefficients):
        expect(abs(coefficient) <= bound, "a coefficient exceeds the Gershgorin binomial bound")
        expect(coefficient % (4 ** (size - index)) == 0, "chi_A is not an integer polynomial")
    coefficients_a = [coefficient // (4 ** (size - index)) for index, coefficient in enumerate(coefficients)]
    return coefficients, coefficients_a


def poly_mul(left, right):
    output = [0] * (len(left) + len(right) - 1)
    for i, left_coeff in enumerate(left):
        for j, right_coeff in enumerate(right):
            output[i + j] += left_coeff * right_coeff
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


def scale_to_b(coefficients):
    degree = len(coefficients) - 1
    return [coefficient * 4 ** (degree - index) for index, coefficient in enumerate(coefficients)]


def monic_divides(divisor, target):
    work = list(target)
    degree = len(divisor) - 1
    while len(work) > 1 and work[-1] == 0:
        work.pop()
    while len(work) - 1 >= degree and not (len(work) == 1 and work[0] == 0):
        shift = len(work) - 1 - degree
        lead = work[-1]
        for index, coefficient in enumerate(divisor):
            work[shift + index] -= lead * coefficient
        while len(work) > 1 and work[-1] == 0:
            work.pop()
    return work == [0] or work == []


def divisor_pairs(constant):
    pairs = []
    seen = set()
    value = abs(constant)
    divisor = 1
    while divisor * divisor <= value:
        if value % divisor == 0:
            for left in (divisor, -divisor):
                for pair in ((left, constant // left), (constant // left, left)):
                    if pair not in seen and pair[0] * pair[1] == constant:
                        seen.add(pair)
                        pairs.append(pair)
        divisor += 1
    return pairs


def quadratic_factor(coefficients):
    """Return an integer quadratic factorization, or None. Degree 4 only."""
    expect(len(coefficients) == 5 and coefficients[-1] == 1, "quadratic search expected a monic quartic")
    constant, linear, quadratic, cubic, _lead = coefficients
    if constant == 0:
        return (0, 1), (0, 0, 1)
    for root, _other in divisor_pairs(constant):
        if constant + linear * root + quadratic * root ** 2 + cubic * root ** 3 + root ** 4 == 0:
            return (root, 1), None
    for left, right in divisor_pairs(constant):
        if right != left:
            numerator = linear - left * cubic
            denominator = right - left
            if numerator % denominator == 0:
                first = numerator // denominator
                second = cubic - first
                if left + right + first * second == quadratic:
                    return (left, first, 1), (right, second, 1)
            continue
        if left * cubic != linear:
            continue
        discriminant = cubic * cubic - 4 * (quadratic - 2 * left)
        if discriminant < 0:
            continue
        root = int(discriminant ** 0.5)
        while (root + 1) * (root + 1) <= discriminant:
            root += 1
        while root * root > discriminant:
            root -= 1
        if root * root != discriminant:
            continue
        for sign in (1, -1):
            if (cubic + sign * root) % 2 == 0:
                return (left, (cubic + sign * root) // 2, 1), (left, cubic - (cubic + sign * root) // 2, 1)
    return None


def prove_irreducible(coefficients):
    degree = len(coefficients) - 1
    expect(coefficients[-1] == 1, "a factor is not monic")
    if degree == 1:
        return
    expect(degree == 4, "a factor has degree other than 1 or 4")
    expect(quadratic_factor(coefficients) is None, "a degree-4 factor is reducible over Z")


def matmul(left, right):
    size = len(left)
    return [
        [sum(left[row][index] * right[index][column] for index in range(size)) for column in range(size)]
        for row in range(size)
    ]


def apply_polynomial(matrix, coefficients):
    size = len(matrix)
    value = [[0] * size for _ in range(size)]
    for coefficient in reversed(coefficients):
        value = matmul(value, matrix)
        for index in range(size):
            value[index][index] += coefficient
    return value


def is_zero(matrix):
    return all(entry == 0 for row in matrix for entry in row)


def kernel_vectors(matrix):
    """Integer kernel basis. Free coordinates form an identity submatrix."""
    size = len(matrix)
    work = [[Fraction(entry) for entry in row] for row in matrix]
    pivot_of_row = []
    rank = 0
    for column in range(size):
        pivot = None
        for row in range(rank, size):
            if work[row][column] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = work[rank][column]
        for row in range(size):
            if row == rank or work[row][column] == 0:
                continue
            factor = work[row][column] / inverse
            for index in range(column, size):
                work[row][index] -= factor * work[rank][index]
        pivot_of_row.append(column)
        rank += 1
    pivots = set(pivot_of_row)
    vectors = []
    free = [column for column in range(size) if column not in pivots]
    for chosen in free:
        raw = [Fraction(0)] * size
        raw[chosen] = Fraction(1)
        for row, column in enumerate(pivot_of_row):
            raw[column] = -work[row][chosen] / work[row][column]
        denominator = 1
        for value in raw:
            denominator = denominator * value.denominator // math_gcd(denominator, value.denominator)
        vectors.append([int(value * denominator) for value in raw])
    return free, vectors


def math_gcd(left, right):
    while right:
        left, right = right, left % right
    return left


def fixed_by(dest, sign, items, eigenvalue):
    values = {index: coeff for index, coeff in items}
    for index, coeff in items:
        image = dest[index]
        if values.get(image, 0) != sign[index] * eigenvalue * coeff:
            return False
    return True


def build_space(actions, extras):
    lattice = Lattice()
    for dest, sign in actions:
        lattice.add_operator(dest, sign, 1)
    for dest, sign, eigenvalue in extras:
        lattice.add_operator(dest, sign, eigenvalue)
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
    port_of, lookup, port_basis, coords = prepare(columns, ports)
    identity = operator(tuple(range(8)), (1,) * 8, port_of, lookup, port_basis, coords)
    expect(identity is not None and identity["T"] == tuple(1 << bit for bit in range(9)), "identity is not a symmetry")
    group = []
    for odds in range(16):
        eps = [1] * 8
        for index, coordinate in enumerate(ODDS):
            if (odds >> index) & 1:
                eps[coordinate] = -1
        built = operator(tuple(range(8)), tuple(eps), port_of, lookup, port_basis, coords)
        expect(built is not None, "a positive-even sign is not a symmetry of the query")
        expect(apply_linear(built["T"], SECTOR) == SECTOR, "H moves sector 3")
        group.append(built)
    expect(len(group) == 16, "H does not have order 16")
    first = operator(U_INV, U_EPS, port_of, lookup, port_basis, coords)
    second = operator(V_INV, V_EPS, port_of, lookup, port_basis, coords)
    expect(first is not None and second is not None, "u or v is not a symmetry")
    expect(same_operator(compose(first, first), identity), "u is not an involution")
    expect(same_operator(compose(second, second), identity), "v is not an involution")
    expect(same_operator(compose(first, second), compose(second, first)), "u and v do not commute")
    expect(apply_linear(first["T"], SECTOR) == SECTOR and apply_linear(second["T"], SECTOR) == SECTOR, "the pair moves sector 3")
    product = compose(first, second)
    actors = []
    for element in group:
        for extra in (identity, first, second, product):
            actors.append(compose(extra, element))
    expect(len({(item["inv"], item["eps"], item["T"]) for item in actors}) == 64, "the joint group does not have order 64")
    actions = [action_tables(element) for element in actors]
    x_action = translation_action(SECTOR)
    z_action = diagonal_action(CHARACTER)
    expect(compose_actions(x_action, x_action) == (list(range(4096)), [1] * 4096), "X_3 is not an involution")
    for dest, sign in actions:
        expect(compose_actions(x_action, (dest, sign)) == compose_actions((dest, sign), x_action), "X_3 does not commute with the joint group")
        expect(compose_actions(z_action, (dest, sign)) == compose_actions((dest, sign), z_action), "Z_508 does not commute with the joint group")
        expect((dest, sign) != x_action, "X_3 is already a signed permutation in the joint group")
    extended = actions + [compose_actions(x_action, action) for action in actions]
    expect(len(extended) == 128, "the group generated by H, u, v and X_3 does not have order 128")
    trace_sum = sum(action_trace(dest, sign) for dest, sign in extended)
    expect(trace_sum % 128 == 0 and trace_sum // 128 == 84, "the projector trace is not 84")
    x_trace = sum(action_trace(*compose_actions(x_action, action)) for action in actions)
    expect(x_trace % 64 == 0 and x_trace // 64 == -48, "the trace of X_3 on the 216-space is not -48")

    joint_vectors = build_space(actions, [])
    plus_vectors = build_space(actions, [(x_action[0], x_action[1], 1)])
    minus_vectors = build_space(actions, [(x_action[0], x_action[1], -1)])
    t0_vectors = build_space(actions, [(x_action[0], x_action[1], 1), (z_action[0], z_action[1], 1)])
    t1_vectors = build_space(actions, [(x_action[0], x_action[1], 1), (z_action[0], z_action[1], -1)])
    other_joint = build_space(
        [action_tables(compose(extra, element)) for element in group for extra in (identity, first)],
        [(action_tables(second)[0], action_tables(second)[1], -1), (x_action[0], x_action[1], 1)],
    )
    expect(len(joint_vectors) == 216, "the trivial (+1,+1) basis is not 216-dimensional")
    expect(len(plus_vectors) == 84 and len(minus_vectors) == 132, "X_3 does not split the 216-space as 84+132")
    expect(len(t0_vectors) == 42 and len(t1_vectors) == 42, "Z_508 does not split the 84-space as 42+42")
    expect(len(other_joint) == 116, "the (+1,-1) X_3=+1 space does not have dimension 116")
    sizes = [len(items) for _root, items in plus_vectors]
    expect(set(sizes) <= {8, 32, 64} and set(sizes) == {8, 32, 64}, "basis support sizes are not 8, 32 and 64")

    columns_b = column_table(columns, ports, SECTOR)
    predicted = sum(operator_trace(columns_b, dest, sign) for dest, sign in extended)
    expect(predicted % 128 == 0, "the trace of B is not integral on the projector")
    matrix, _matrix_sizes = restriction_matrix(columns_b, columns, ports, plus_vectors, SECTOR)
    matrix0, _sizes0 = restriction_matrix(columns_b, columns, ports, t0_vectors, SECTOR)
    matrix1, _sizes1 = restriction_matrix(columns_b, columns, ports, t1_vectors, SECTOR)
    expect(sum(matrix[index][index] for index in range(84)) == predicted // 128 == 0, "matrix trace is not the trace formula value 0")
    expect(sum(matrix0[index][index] for index in range(42)) == 168, "t=0 trace is not 168")
    expect(sum(matrix1[index][index] for index in range(42)) == -168, "t=1 trace is not -168")
    entries = [entry for row in matrix for entry in row]
    expect(min(entries) == -28 and max(entries) == 28, "matrix entries are not exactly the range -28..28")

    coefficients_b, coefficients_a = charpoly(matrix)
    coefficients_b0, coefficients_a0 = charpoly(matrix0)
    coefficients_b1, coefficients_a1 = charpoly(matrix1)
    expect(poly_mul(coefficients_b0, coefficients_b1) == coefficients_b, "the sector polynomials do not multiply to chi_B")
    expect(product_factors(FACTORS) == coefficients_a, "the pinned factors do not multiply to chi_A")
    expect(product_factors(FACTORS_T0) == coefficients_a0, "the t=0 factors do not multiply to that characteristic polynomial")
    expect(product_factors(FACTORS_T1) == coefficients_a1, "the t=1 factors do not multiply to that characteristic polynomial")
    expect(sha256_bytes(canonical(coefficients_a).encode()) == CHI_A_SHA256, "chi_A SHA256 changed")
    expect(sha256_bytes(canonical(coefficients_b).encode()) == CHI_B_SHA256, "chi_B SHA256 changed")
    for multiplicity, coefficients in FACTORS:
        prove_irreducible(list(coefficients))
        expect(multiplicity > 0, "a factor multiplicity is not positive")
    expect(quadratic_factor((1, 0, 2, 0, 1)) is not None, "the irreducibility test accepted (x^2+1)^2")

    certificate = json.loads(CERTIFICATE.read_bytes())
    expect(certificate["source_sha256"] == INTERFACE_SHA256, "published one-slot certificate names a different query")
    expect(certificate["operator"] == "B=4*A_1", "published certificate is not the integer operator B")
    sectors = {}
    for sector in certificate["sectors"]:
        if sector["c"] == SECTOR and sector["s"] == 1:
            sectors[sector["t"]] = [int(value) for value in sector["coefficients"]]
    expect(set(sectors) == {0, 1}, "the c=3 s=+1 sector polynomials are not both present")
    expect(len(sectors[0]) == 127 and len(sectors[1]) == 127, "a c=3 s=+1 sector polynomial does not have degree 126")
    for (multiplicity, coefficients), hits in zip(FACTORS, SECTOR_HITS):
        scaled = scale_to_b(coefficients)
        found = tuple(key for key in (0, 1) if monic_divides(scaled, sectors[key]))
        expect(found == hits, "sector divisibility of a factor changed")
        expect(hits, "a factor divides neither published c=3 s=+1 sector polynomial")
        expect(multiplicity >= 1, "multiplicity dropped out of the sector comparison")

    distinct = tuple((1, coefficients) for _multiplicity, coefficients in FACTORS)
    annihilator = apply_polynomial(matrix, product_factors(tuple((1, scale_to_b(coefficients)) for _mult, coefficients in distinct)))
    expect(is_zero(annihilator), "the degree-25 square-free polynomial does not annihilate B")
    for sector_matrix, sector_factors in ((matrix0, FACTORS_T0), (matrix1, FACTORS_T1)):
        distinct_sector = []
        seen = set()
        for _multiplicity, coefficients in sector_factors:
            if coefficients not in seen:
                seen.add(coefficients)
                distinct_sector.append((1, scale_to_b(coefficients)))
        expect(is_zero(apply_polynomial(sector_matrix, product_factors(tuple(distinct_sector)))), "a sector square-free polynomial does not annihilate")

    accounted = 0
    for eigenvalue, multiplicity in RATIONAL_EIGENVALUES:
        shifted = [row[:] for row in matrix]
        for index in range(84):
            shifted[index][index] -= 4 * eigenvalue
        free, vectors = kernel_vectors(shifted)
        expect(len(vectors) == multiplicity, "geometric multiplicity disagrees with the characteristic polynomial at " + str(eigenvalue))
        for vector in vectors:
            image = [
                sum(shifted[row][column] * vector[column] for column in range(84))
                for row in range(84)
            ]
            expect(image == [0] * 84, "a claimed kernel vector is not in the kernel")
        for position, vector in enumerate(vectors):
            expect(vector[free[position]] != 0, "a kernel vector vanishes on its free coordinate")
            for other, column in enumerate(free):
                expect(vector[column] == (vector[free[position]] if other == position else 0), "kernel vectors are dependent on the free coordinates")
        accounted += multiplicity
    expect(accounted == 60, "the rational eigenvalues do not account for 60 dimensions")

    basis_payload = {
        "index": "coordinate*512+address",
        "eigenvalues": {"H": 1, "u": 1, "v": 1, "X_3": 1},
        "roots": [root for root, _items in plus_vectors],
        "vectors": [[[index, coeff] for index, coeff in items] for _root, items in plus_vectors],
    }
    matrix_payload = {"rows": matrix}
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
    expect(transposition is None, "the coordinate transposition (0 1) was accepted as a symmetry")
    wrong_sector = column_table(columns, ports, 1)
    expect(not subspace_preserved(wrong_sector, plus_vectors), "the c=1 block operator preserves this c=3 subspace")
    shifted_once = translation_action(1)
    wrong_translation = build_space(actions, [(shifted_once[0], shifted_once[1], 1)])
    expect(len(wrong_translation) != 84, "translation by 1 still produced an 84-dimensional space")
    broken = Lattice()
    for dest, sign in actions[1:]:
        broken.add_operator(dest, sign, 1)
    flipped = list(actions[0][1])
    flipped[0] *= -1
    broken.add_operator(actions[0][0], flipped, 1)
    broken.add_operator(x_action[0], x_action[1], 1)
    expect(len(broken.basis()) != 84, "flipping one group sign still produced dimension 84")
    corrupted = [row[:] for row in matrix]
    corrupted[0][0] += 1
    expect(charpoly_mod(corrupted, 1000003) != charpoly_mod(matrix, 1000003), "changing a matrix entry preserved the characteristic polynomial")
    expect(product_factors(FACTORS[:-1]) != coefficients_a, "dropping a factor still multiplied to chi_A")
    linked = None
    for dest, sign in actions + [x_action]:
        for _root, items in plus_vectors:
            values = {index: coeff for index, coeff in items}
            for index, _coeff in items:
                if dest[index] != index and dest[index] in values:
                    linked = (dest, sign, items, index)
                    break
            if linked:
                break
        if linked:
            break
    expect(linked is not None, "no operator links two basis coordinates; the sign control is vacuous")
    dest, sign, items, index = linked
    flipped_items = [(item, -coeff if item == index else coeff) for item, coeff in items]
    expect(not fixed_by(dest, sign, flipped_items, 1), "a sign error in a basis vector was still fixed")

    print("PASS_C3_X3_PLUS_CHARPOLY")
    print("selected kappa", SELECTED_KAPPA)
    print("X_3 trace -48 on the 216-space; dimensions 84 and 132; Z_508 splits 42+42")
    print("chi_A SHA256", CHI_A_SHA256)
    print("chi_B SHA256", CHI_B_SHA256)
    print("minimal polynomial degree 25")
    for multiplicity, coefficients in FACTORS:
        print("factor", multiplicity, descending(coefficients))


if __name__ == "__main__":
    main()
