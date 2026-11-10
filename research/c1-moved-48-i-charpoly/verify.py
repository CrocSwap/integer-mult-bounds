#!/usr/bin/env python3
"""Characteristic polynomial over Q(i) of one eigenvalue-i eigenspace.

The space is the eigenvalue-i eigenspace of s = (0 4 3 7)(5 6), all signs +1,
inside the sign character eps[1]*eps[2] of the historical c=1 block. B = 4 A_1.
Acceptance uses explicit checks, so -O does not skip a theorem or a rejection
control.

The signed-permutation representation is the same construction used for the
eigenvalue ±1 computation. This file solves the eigenvalue-i equations over
Z[i] and does not recompute that ±1 characteristic polynomial.
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
INTERFACE_SHA256 = (
    "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
)
SELECTED_SHA256 = (
    "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa"
)
SELECTED_KAPPA = "781451/250000000"
C1 = 1
G_INV = (0, 2, 1, 3, 4, 6, 5, 7)
G_EPS = (1, 1, 1, 1, -1, 1, 1, -1)
T_INV = (0, 5, 6, 3, 4, 1, 2, 7)
T_EPS = (1, 1, 1, -1, 1, 1, 1, -1)
# sigma = (0 4 3 7)(5 6), stored as inv = sigma^{-1}, all output signs +1.
S_INV = (7, 1, 2, 4, 0, 6, 5, 3)
S_EPS = (1, 1, 1, 1, 1, 1, 1, 1)
# Values of the two s-preserved dimension-192 characters on the sign
# stabilizer, ordered by increasing sign mask. The canonical space uses the
# lexicographically least tuple.
CANONICAL_SIGNATURE = (1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1)
OTHER_SIGNATURE = (1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1)
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
    ports = [int(q) for q in data["ports"]]
    expect(len(rows) == 8 and len(ports) == 112 and len(set(ports)) == 112, "query shape")
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
    expect(len(basis) == 9, "the 112 ports do not span F2^9")
    coords = {address: tuple(rank_solve(basis, address)) for address in range(512)}
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


def sign_group(port_of, lookup, basis, coords, sector):
    identity = tuple(range(8))
    group = []
    for mask in range(128):
        eps = tuple([1] + [-1 if (mask >> bit) & 1 else 1 for bit in range(7)])
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
    for index, coeff in items:
        # Every preimage that the operator sends onto this support must agree.
        # The support check above is complete because the operator is a bijection
        # and the vector vanishes off the support: if rho v differed at an
        # outside index, some support source would map there.
        if coeff == 0:
            return False
    return True


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
        keys = set(left) | set(right)
        for key in keys:
            if left.get(key, 0) * left_sign != right.get(key, 0):
                return False
    return True


def restriction_matrix(columns_b, columns, ports, vectors):
    roots = [root for root, _items in vectors]
    position = {root: index for index, root in enumerate(roots)}
    members = []
    for _root, items in vectors:
        members.append(items)
    owners = {}
    grouped = [[] for _ in vectors]
    for component, items in enumerate(members):
        for index, coeff in items:
            owners[index] = (component, coeff)
            grouped[component].append((index, coeff))
    matrix = [[0] * len(vectors) for _ in vectors]
    sizes = [len(items) for _root, items in vectors]
    for column, (_root, items) in enumerate(vectors):
        by_columns = column_image(columns_b, items)
        by_literal = literal_image(items, columns, ports)
        expect(by_columns == by_literal, "the two actions of B disagree on a basis vector")
        alphas = {}
        for index, value in by_columns.items():
            info = owners.get(index)
            expect(info is not None, "B sends a basis vector outside the eigenspace")
            component, coeff = info
            alpha = value * coeff
            previous = alphas.get(component)
            expect(previous is None or previous == alpha, "B image is not constant on a component")
            alphas[component] = alpha
        for component, alpha in alphas.items():
            for index, coeff in grouped[component]:
                expect(by_columns.get(index, 0) == coeff * alpha, "B image misses a component coordinate")
            matrix[component][column] = alpha
        for index, value in by_columns.items():
            component, _coeff = owners[index]
            expect(component in alphas, "an image coordinate has no component value")
    for left in range(len(vectors)):
        for right in range(left + 1, len(vectors)):
            expect(
                sizes[left] * matrix[left][right] == sizes[right] * matrix[right][left],
                "the Gram identity size_r M_rs = size_s M_sr failed",
            )
    return matrix, sizes


# The integer-polynomial routines from here through check_factors prove that
# the factors of chi_A are irreducible over Q and divide the published c=1
# sector polynomials. They are not the computation of the eigenvalue-i
# polynomial. That polynomial is interpolate_characteristic below.
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
            target = hess[row]
            source = hess[column + 1]
            for index in range(column, size):
                target[index] = (target[index] - factor * source[index]) % prime
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
            target = work[row]
            source = work[column]
            for index in range(column, size):
                target[index] = (target[index] - factor * source[index]) % prime
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


def scale_to_b(coefficients):
    degree = len(coefficients) - 1
    return [coefficient * 4 ** (degree - index) for index, coefficient in enumerate(coefficients)]


def monic_divides(divisor, target):
    if len(divisor) == 1:
        return divisor == [1] and target == [0] or divisor == [1]
    work = list(target)
    degree = len(divisor) - 1
    while len(work) - 1 >= degree and not (len(work) == 1 and work[0] == 0):
        shift = len(work) - 1 - degree
        lead = work[-1]
        for index, coefficient in enumerate(divisor):
            work[shift + index] -= lead * coefficient
        while len(work) > 1 and work[-1] == 0:
            work.pop()
    return work == [0] or work == []


def trim(coefficients, prime):
    output = [coefficient % prime for coefficient in coefficients]
    while len(output) > 1 and output[-1] == 0:
        output.pop()
    return output


def monic_mod(coefficients, prime):
    inverse = pow(coefficients[-1], -1, prime)
    return [(coefficient * inverse) % prime for coefficient in coefficients]


def remainder_mod(numerator, divisor, prime):
    work = trim(numerator, prime)
    modulus = monic_mod(trim(divisor, prime), prime)
    degree = len(modulus) - 1
    while len(work) - 1 >= degree and not (len(work) == 1 and work[0] == 0):
        shift = len(work) - 1 - degree
        lead = work[-1]
        for index, coefficient in enumerate(modulus):
            work[shift + index] = (work[shift + index] - lead * coefficient) % prime
        while len(work) > 1 and work[-1] == 0:
            work.pop()
    return work


def gcd_mod(left, right, prime):
    first = trim(left, prime)
    second = trim(right, prime)
    while not (len(second) == 1 and second[0] == 0):
        first, second = second, remainder_mod(first, second, prime)
    if len(first) == 1 and first[0] == 0:
        return [0]
    return monic_mod(first, prime)


def pow_mod_poly(exponent, modulus, prime):
    result = [1]
    base = [0, 1]
    degree = len(modulus) - 1
    while exponent:
        if exponent & 1:
            result = remainder_mod(poly_mul(result, base), modulus, prime)
        exponent >>= 1
        if exponent:
            base = remainder_mod(poly_mul(base, base), modulus, prime)
        expect(len(result) <= degree + 1, "polynomial remainder grew past the modulus")
    return result


def is_square(number):
    if number < 0:
        return False
    root = int(number ** 0.5)
    while (root + 1) * (root + 1) <= number:
        root += 1
    while root * root > number:
        root -= 1
    return root * root == number


def x_minus_power(exponent, modulus, prime):
    power = pow_mod_poly(exponent, modulus, prime)
    if len(power) < 2:
        power = power + [0] * (2 - len(power))
    power = power[:]
    power[1] = (power[1] - 1) % prime
    return trim(power, prime)


def irreducible_mod(coefficients, prime):
    reduced = trim(coefficients, prime)
    if len(reduced) <= 2:
        return len(reduced) == 2
    if reduced[-1] % prime == 0:
        return False
    modulus = monic_mod(reduced, prime)
    degree = len(modulus) - 1
    derivative = [((index * coefficient) % prime) for index, coefficient in enumerate(modulus)][1:]
    if gcd_mod(modulus, derivative or [0], prime) != [1]:
        return False
    primes = []
    value = degree
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            primes.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1
    if value > 1:
        primes.append(value)
    if x_minus_power(prime ** degree, modulus, prime) != [0]:
        return False
    for factor in primes:
        if gcd_mod(x_minus_power(prime ** (degree // factor), modulus, prime), modulus, prime) != [1]:
            return False
    return True


def prove_irreducible(coefficients):
    degree = len(coefficients) - 1
    expect(coefficients[-1] == 1, "a factor is not monic")
    if degree == 1:
        return
    if degree == 2:
        discriminant = coefficients[1] * coefficients[1] - 4 * coefficients[0]
        expect(not is_square(discriminant), "a quadratic factor is reducible over Z")
        return
    candidate = 1009
    tried = 0
    while tried < 80:
        if is_prime(candidate) and irreducible_mod(coefficients, candidate):
            return
        if is_prime(candidate):
            tried += 1
        candidate += 2
    fail("no prime in the first 80 primes at or above 1009 proved a factor irreducible")


def descending(coefficients):
    terms = []
    for power, coefficient in enumerate(coefficients):
        if coefficient:
            terms.append((power, coefficient))
    parts = []
    for power, coefficient in reversed(terms):
        if power == 0:
            body = str(abs(coefficient))
            if not parts:
                parts.append(str(coefficient))
            else:
                parts.append(("+ " if coefficient > 0 else "- ") + body)
            continue
        magnitude = abs(coefficient)
        letter = "x" if power == 1 else "x^" + str(power)
        if magnitude == 1:
            body = letter
        else:
            body = str(magnitude) + letter
        if not parts:
            parts.append(body if coefficient > 0 else "-" + body)
        else:
            parts.append(("+ " if coefficient > 0 else "- ") + body)
    return " ".join(parts)


def row_sum(matrix):
    return max(sum(abs(entry) for entry in row) for row in matrix)


def evaluate(coefficients, point, prime):
    value = 0
    power = 1
    for coefficient in coefficients:
        value = (value + coefficient * power) % prime
        power = power * point % prime
    return value


def shifted_det(matrix, point, prime):
    size = len(matrix)
    work = [[(-entry) % prime for entry in row] for row in matrix]
    for index in range(size):
        work[index][index] = (work[index][index] + point) % prime
    return det_mod(work, prime)



def mask_of(eps):
    return sum(1 << bit for bit in range(7) if eps[bit + 1] == -1)


def character_values(group):
    basis = []
    for element in group:
        reduced = mask_of(element["eps"])
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
        expect(reduced == 0, "the sign stabilizer is not elementary abelian")
        return coef

    def value(chi, mask):
        sign = 1
        for index, bit in enumerate(coordinates(mask)):
            if bit and (chi >> index) & 1:
                sign = -sign
        return sign

    return value


def conjugate(actor, actor_inverse, element):
    return compose(actor_inverse, compose(element, actor))


def image_character(by_mask, value, actor, actor_inverse, chi):
    target = {}
    for mask, element in by_mask.items():
        image = conjugate(actor, actor_inverse, element)
        expect(
            image["inv"] == tuple(range(8)) and image["eps"][0] == 1,
            "a conjugate left the sign stabilizer",
        )
        target[mask] = value(chi, mask_of(image["eps"]))
    for candidate in range(16):
        if all(value(candidate, mask) == target[mask] for mask in by_mask):
            return candidate
    fail("a conjugate character is not a character of the sign stabilizer")


def trace_on_character(by_mask, value, actor, chi):
    total = 0
    for mask, element in by_mask.items():
        composed = compose(actor, element)
        closed = trace_s(composed["inv"], composed["eps"]) * fixed_addresses(composed["T"])
        total += value(chi, mask) * closed
    expect(total % 16 == 0, "a character trace is not an integer")
    return total // 16


def order4_multiplicities(traces):
    identity, first, square, cube = traces
    expect(first == cube, "the multiplicity of i is not a rational integer")
    for numerator in (
        identity + first + square + cube,
        identity - first + square - cube,
        identity - square,
    ):
        expect(numerator % 4 == 0, "an order-4 character trace is not divisible by 4")
    half = (identity - square) // 4
    return (
        (identity + first + square + cube) // 4,
        half,
        (identity - first + square - cube) // 4,
        half,
    )


def integer_characteristic(matrix):
    degree = len(matrix)
    bound = coeff_bound(degree, row_sum(matrix))
    primes, modulus = primes_past(2 * bound)
    expect(modulus > 2 * bound, "CRT modulus does not exceed the coefficient bound")
    residues = [[] for _ in range(degree + 1)]
    for prime in primes:
        polynomial = charpoly_mod(matrix, prime)
        expect(
            len(polynomial) == degree + 1 and polynomial[-1] == 1,
            "modular characteristic polynomial has the wrong degree",
        )
        if prime == primes[0]:
            for point in (0, 1, 2, 3, 5):
                expect(
                    evaluate(polynomial, point, prime) == shifted_det(matrix, point, prime),
                    "Hessenberg characteristic polynomial disagrees with a determinant",
                )
        for index, coefficient in enumerate(polynomial):
            residues[index].append(coefficient)
    coefficients_b = [crt_signed(residues[index], primes) for index in range(degree + 1)]
    expect(coefficients_b[-1] == 1, "characteristic polynomial of B is not monic")
    expect(
        sum(matrix[index][index] for index in range(degree)) == -coefficients_b[degree - 1],
        "trace disagrees with the degree n-1 coefficient",
    )
    for index, coefficient in enumerate(coefficients_b):
        expect(abs(coefficient) <= bound, "a coefficient exceeds the Gershgorin binomial bound")
        expect(coefficient % (4 ** (degree - index)) == 0, "chi_A is not an integer polynomial")
    coefficients_a = [coefficient // (4 ** (degree - index)) for index, coefficient in enumerate(coefficients_b)]
    return coefficients_a, coefficients_b, bound


def check_factors(coefficients_a, coefficients_b, factors, hits, sectors, sha_a, sha_b):
    expanded = product_factors(factors)
    expect(expanded == coefficients_a, "the pinned factors do not multiply to chi_A")
    expect(sha256_bytes(canonical(coefficients_a).encode()) == sha_a, "chi_A SHA256 changed")
    expect(sha256_bytes(canonical(coefficients_b).encode()) == sha_b, "chi_B SHA256 changed")
    for (multiplicity, coefficients), expected in zip(factors, hits):
        prove_irreducible(list(coefficients))
        expect(multiplicity > 0, "a factor multiplicity is not positive")
        scaled = scale_to_b(coefficients)
        found = tuple(
            key for key in ((0, -1), (0, 1), (1, -1), (1, 1)) if monic_divides(scaled, sectors[key])
        )
        expect(found == expected, "sector divisibility of a factor changed")
        expect(expected, "a factor divides none of the published c=1 sector polynomials")



# Characteristic polynomial over Q(i). The signed-permutation representation
# above is the construction used for the eigenvalue ±1 spaces. The lattice,
# matrix, and polynomial below are the eigenvalue-i computation.

from fractions import Fraction

ZERO = (0, 0)
ONE = (1, 0)
NEG_ONE = (-1, 0)
I_UNIT = (0, 1)
NEG_I = (0, -1)
UNITS = (ONE, NEG_ONE, I_UNIT, NEG_I)
CROSSCHECK_PRIME = 1_000_003
# Ascending-coefficient digests of chi_{A_1} and chi_B on the eigenvalue-i
# space. The same digests are printed by PR #7036 for the eigenvalue ±1
# polynomial on eps[5]*eps[6]. This file recomputes them on the eigenvalue-i
# space and does not rebuild that matrix.
CHI_A_SHA256 = "248dde5357601a63a3e5b548e370f6025e6cc457204723a43413d2eaa79833e3"
CHI_B_SHA256 = "d2d03090e33a628beb31eb51a8f332ec5ccbb18800a56f25186815bde4d81ffd"
# Monic irreducible factorization of chi_{A_1} over Q(i), ascending
# coefficients, with algebraic multiplicity.
FACTORS = (
    (10, (0, 1)),
    (5, (-2, 1)),
    (5, (2, 1)),
    (1, (32, 4, -8, 1)),
    (1, (-8, -12, 0, 1)),
    (1, (8, -12, 0, 1)),
    (1, (-32, 4, 8, 1)),
    (1, (-3072, 7296, -1728, -3264, 704, 296, -56, -6, 1)),
    (1, (-3072, -7296, -1728, 3264, 704, -296, -56, 6, 1)),
)
SECTOR_HITS = (
    ((0, -1), (0, 1), (1, -1), (1, 1)),
    ((0, -1), (0, 1), (1, -1), (1, 1)),
    ((0, -1), (0, 1), (1, -1), (1, 1)),
    ((0, 1),),
    ((1, -1),),
    ((1, 1),),
    ((0, -1),),
    ((1, 1),),
    ((1, -1),),
)


def gadd(left, right):
    return (left[0] + right[0], left[1] + right[1])


def gsub(left, right):
    return (left[0] - right[0], left[1] - right[1])


def gmul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def gconj(value):
    return (value[0], -value[1])


def gneg(value):
    return (-value[0], -value[1])


def gdiv(numerator, denominator):
    den_re, den_im = denominator
    modulus = den_re * den_re + den_im * den_im
    if modulus == 0:
        fail("division by zero in Z[i]")
    num_re, num_im = numerator
    real_part = num_re * den_re + num_im * den_im
    imag_part = num_im * den_re - num_re * den_im
    if real_part % modulus or imag_part % modulus:
        fail("Bareiss division in Z[i] was not exact")
    return (real_part // modulus, imag_part // modulus)


def gmod(value, prime):
    return (value[0] % prime, value[1] % prime)


def gadd_mod(left, right, prime):
    return ((left[0] + right[0]) % prime, (left[1] + right[1]) % prime)


def gsub_mod(left, right, prime):
    return ((left[0] - right[0]) % prime, (left[1] - right[1]) % prime)


def gmul_mod(left, right, prime):
    return (
        (left[0] * right[0] - left[1] * right[1]) % prime,
        (left[0] * right[1] + left[1] * right[0]) % prime,
    )


def ginv_mod(value, prime):
    norm = (value[0] * value[0] + value[1] * value[1]) % prime
    inverse = pow(norm, -1, prime)
    return ((value[0] * inverse) % prime, ((-value[1]) * inverse) % prime)


class GaussLattice:
    """Solutions of monomial equations v[dst] = unit * v[src] over Q(i)."""

    def __init__(self):
        self.parent = list(range(4096))
        self.rel = [ONE] * 4096
        self.dead = [False] * 4096

    def find(self, index):
        sign = ONE
        seen = []
        while self.parent[index] != index:
            seen.append(index)
            sign = gmul(self.rel[index], sign)
            index = self.parent[index]
        accumulated = ONE
        for step in reversed(seen):
            accumulated = gmul(self.rel[step], accumulated)
            self.rel[step] = accumulated
            self.parent[step] = index
        return index, sign

    def constrain(self, dst, src, unit):
        root_dst, sign_dst = self.find(dst)
        root_src, sign_src = self.find(src)
        if root_dst == root_src:
            if sign_dst != gmul(unit, sign_src):
                self.dead[root_dst] = True
            return
        # v[dst] = sign_dst v[root_dst] = unit v[src] = unit sign_src v[root_src].
        self.parent[root_dst] = root_src
        self.rel[root_dst] = gmul(gconj(sign_dst), gmul(unit, sign_src))
        if self.dead[root_dst] or self.dead[root_src]:
            self.dead[root_src] = True

    def add_monomial(self, dest, sign, reciprocal):
        """Impose rho v = lambda v, where reciprocal is the unit 1/lambda.

        The stored action satisfies (rho v)[dest[src]] = sign[src] v[src], so
        v[dest[src]] = sign[src] * (1/lambda) * v[src].
        """
        for src in range(4096):
            self.constrain(dest[src], src, gmul((sign[src], 0), reciprocal))

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
            scale = gconj(items[0][1])
            vectors.append(
                (items[0][0], [(index, gmul(coeff, scale)) for index, coeff in items])
            )
        vectors.sort()
        return vectors


def satisfies(dest, sign, items, eigenvalue):
    values = {index: coeff for index, coeff in items}
    for index, coeff in items:
        image = dest[index]
        if gmul((sign[index], 0), coeff) != gmul(eigenvalue, values.get(image, ZERO)):
            return False
        if coeff not in UNITS:
            return False
    return True


def gaussian_literal(items, columns, ports):
    image = {}
    real_items = [(index, coeff[0]) for index, coeff in items if coeff[0]]
    imag_items = [(index, coeff[1]) for index, coeff in items if coeff[1]]
    if real_items:
        for index, value in literal_image(real_items, columns, ports).items():
            image[index] = gadd(image.get(index, ZERO), (value, 0))
    if imag_items:
        for index, value in literal_image(imag_items, columns, ports).items():
            image[index] = gadd(image.get(index, ZERO), (0, value))
    return {index: value for index, value in image.items() if value != ZERO}


def gaussian_columns(columns_b, items):
    image = {}
    for index, coeff in items:
        for target, value in columns_b[index].items():
            image[target] = gadd(image.get(target, ZERO), gmul(coeff, (value, 0)))
    return {index: value for index, value in image.items() if value != ZERO}


def restriction(columns_b, columns, ports, vectors):
    members = [items for _root, items in vectors]
    owners = {}
    grouped = [[] for _ in vectors]
    for component, items in enumerate(members):
        for index, coeff in items:
            expect(index not in owners, "basis supports are not disjoint")
            owners[index] = (component, coeff)
            grouped[component].append((index, coeff))
    matrix = [[ZERO for _ in vectors] for _ in vectors]
    sizes = [len(items) for items in members]
    for column, items in enumerate(members):
        by_columns = gaussian_columns(columns_b, items)
        by_literal = gaussian_literal(items, columns, ports)
        expect(by_columns == by_literal, "the two actions of B disagree on a basis vector")
        alphas = {}
        for index, value in by_columns.items():
            info = owners.get(index)
            expect(info is not None, "B sends a basis vector outside the eigenspace")
            component, coeff = info
            alpha = gmul(value, gconj(coeff))
            previous = alphas.get(component)
            expect(previous is None or previous == alpha, "B image is not constant on a component")
            alphas[component] = alpha
        for component, alpha in alphas.items():
            for index, coeff in grouped[component]:
                expect(
                    by_columns.get(index, ZERO) == gmul(coeff, alpha),
                    "B image misses a component coordinate",
                )
            matrix[component][column] = alpha
    for left in range(len(vectors)):
        for right in range(len(vectors)):
            expect(
                gmul((sizes[left], 0), gconj(matrix[left][right]))
                == gmul((sizes[right], 0), matrix[right][left]),
                "the Hermitian Gram identity failed",
            )
    return matrix, sizes


def bareiss_determinant(matrix):
    """Exact determinant over Z[i] by fraction-free elimination."""
    size = len(matrix)
    work = [row[:] for row in matrix]
    sign = ONE
    previous = ONE
    for pivot_index in range(size - 1):
        if work[pivot_index][pivot_index] == ZERO:
            swap = None
            for row in range(pivot_index + 1, size):
                if work[row][pivot_index] != ZERO:
                    swap = row
                    break
            if swap is None:
                return ZERO
            work[pivot_index], work[swap] = work[swap], work[pivot_index]
            sign = gneg(sign)
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for col in range(pivot_index + 1, size):
                numerator = gsub(
                    gmul(pivot, work[row][col]),
                    gmul(work[row][pivot_index], work[pivot_index][col]),
                )
                work[row][col] = gdiv(numerator, previous)
            work[row][pivot_index] = ZERO
        previous = pivot
    return gmul(sign, work[-1][-1])


def determinant_at(matrix, point):
    shifted = [[gneg(entry) for entry in row] for row in matrix]
    for index in range(len(shifted)):
        shifted[index][index] = gadd(shifted[index][index], point)
    return bareiss_determinant(shifted)


def fadd(left, right):
    return (left[0] + right[0], left[1] + right[1])


def fsub(left, right):
    return (left[0] - right[0], left[1] - right[1])


def fmul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def interpolate_characteristic(matrix):
    """Monic characteristic polynomial, from exact values at 0, 1, ..., n."""
    degree = len(matrix)
    samples = [determinant_at(matrix, (point, 0)) for point in range(degree + 1)]
    column = [(Fraction(sample[0]), Fraction(sample[1])) for sample in samples]
    newton = [column[0]]
    for level in range(1, degree + 1):
        column = [
            ((column[index + 1][0] - column[index][0]) / level,
             (column[index + 1][1] - column[index][1]) / level)
            for index in range(degree + 1 - level)
        ]
        newton.append(column[0])
    polynomial = [(Fraction(0), Fraction(0)) for _ in range(degree + 1)]
    basis = [(Fraction(1), Fraction(0))]

    def accumulate(scale):
        for index, term in enumerate(basis):
            polynomial[index] = fadd(polynomial[index], fmul(term, scale))

    accumulate(newton[0])
    for degree_index in range(1, degree + 1):
        extended = [(Fraction(0), Fraction(0)) for _ in range(len(basis) + 1)]
        shift = degree_index - 1
        for index, term in enumerate(basis):
            extended[index + 1] = fadd(extended[index + 1], term)
            extended[index] = fsub(extended[index], (term[0] * shift, term[1] * shift))
        basis = extended
        accumulate(newton[degree_index])
    coefficients = []
    for real_part, imag_part in polynomial:
        expect(
            real_part.denominator == 1 and imag_part.denominator == 1,
            "the interpolating polynomial is not in Z[i][x]",
        )
        coefficients.append((real_part.numerator, imag_part.numerator))
    expect(coefficients[-1] == ONE, "the characteristic polynomial is not monic of degree 48")
    trace = ZERO
    for index in range(degree):
        trace = gadd(trace, matrix[index][index])
    expect(trace == gneg(coefficients[degree - 1]), "trace disagrees with the degree n-1 coefficient")
    return coefficients


def charpoly_field(matrix, prime):
    size = len(matrix)
    hess = [[gmod(entry, prime) for entry in row] for row in matrix]
    for column in range(size - 2):
        pivot = None
        for row in range(column + 1, size):
            if hess[row][column] != ZERO:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != column + 1:
            hess[column + 1], hess[pivot] = hess[pivot], hess[column + 1]
            for row in hess:
                row[column + 1], row[pivot] = row[pivot], row[column + 1]
        inverse = ginv_mod(hess[column + 1][column], prime)
        for row in range(column + 2, size):
            factor = hess[row][column]
            if factor == ZERO:
                continue
            factor = gmul_mod(factor, inverse, prime)
            target = hess[row]
            source = hess[column + 1]
            for index in range(column, size):
                target[index] = gsub_mod(target[index], gmul_mod(factor, source[index], prime), prime)
            for host in hess:
                host[column + 1] = gadd_mod(
                    host[column + 1], gmul_mod(factor, host[row], prime), prime
                )
    minors = [[ONE], [gsub_mod(ZERO, hess[0][0], prime), ONE]]
    for end in range(1, size):
        previous = minors[end]
        diagonal = hess[end][end]
        output = [ZERO] * (end + 2)
        for index, coefficient in enumerate(previous):
            output[index + 1] = coefficient
            output[index] = gsub_mod(output[index], gmul_mod(diagonal, coefficient, prime), prime)
        product = ONE
        for start in range(end - 1, -1, -1):
            product = gmul_mod(product, hess[start + 1][start], prime)
            if product == ZERO:
                break
            scale = gmul_mod(hess[start][end], product, prime)
            if scale == ZERO:
                continue
            for index, coefficient in enumerate(minors[start]):
                output[index] = gsub_mod(
                    output[index], gmul_mod(scale, coefficient, prime), prime
                )
        expect(output[-1] == ONE, "Hessenberg characteristic polynomial is not monic")
        minors.append(output)
    return minors[size]


def divide_by_four(coefficients):
    degree = len(coefficients) - 1
    output = []
    for index, coefficient in enumerate(coefficients):
        power = 4 ** (degree - index)
        expect(
            coefficient[1] == 0 and coefficient[0] % power == 0,
            "chi_A is not an integer polynomial",
        )
        output.append(coefficient[0] // power)
    return output


def reflected(coefficients):
    return [
        coefficient if index % 2 == 0 else -coefficient
        for index, coefficient in enumerate(coefficients)
    ]


def negative_reflected(coefficients):
    return [
        -coefficient if index % 2 == 0 else coefficient
        for index, coefficient in enumerate(coefficients)
    ]


def prove_irreducible_over_qi(coefficients):
    """Arithmetic hypotheses for the irreducibility argument in PROOF.md.

    A monic cubic in Z[x] with no integer root is irreducible over Q. A root
    in Q(i) that is not rational would force a distinct conjugate root and a
    quadratic factor over Q, which a cubic irreducible over Q cannot have.

    An octic irreducible modulo 1019 is irreducible over Q. The only remaining
    splitting over Q(i) would be a conjugate pair of monic quartics in Z[i][x].
    Their product would have nonnegative constant term, the norm of a Gaussian
    integer. Each octic here has constant term -3072.
    """
    degree = len(coefficients) - 1
    expect(coefficients[-1] == 1, "a factor is not monic")
    if degree == 1:
        return
    if degree == 3:
        constant = abs(coefficients[0])
        for root in range(-constant, constant + 1):
            if root == 0 or constant % abs(root):
                continue
            value = 0
            for coefficient in reversed(coefficients):
                value = value * root + coefficient
            expect(value != 0, "a cubic factor has an integer root")
        return
    if degree == 8:
        expect(is_prime(1019), "1019 is not prime")
        expect(irreducible_mod(coefficients, 1019), "an octic factor is reducible modulo 1019")
        expect(coefficients[0] < 0, "an octic constant term is nonnegative")
        return
    fail("a factor has an unexpected degree")


def solve_space(actions, by_mask, value, chi, s_dest, s_sign, reciprocal, eigenvalue, columns_b, columns, ports):
    lattice = GaussLattice()
    for mask in sorted(by_mask):
        dest, sign = actions[mask]
        lattice.add_monomial(dest, sign, (value(chi, mask), 0))
    lattice.add_monomial(s_dest, s_sign, reciprocal)
    vectors = lattice.basis()
    expect(len(vectors) == 48, "the eigenspace does not have dimension 48")
    for mask in sorted(by_mask):
        dest, sign = actions[mask]
        for _root, items in vectors:
            expect(
                satisfies(dest, sign, items, (value(chi, mask), 0)),
                "a basis vector misses its character eigenvalue",
            )
    for _root, items in vectors:
        expect(satisfies(s_dest, s_sign, items, eigenvalue), "a basis vector misses the eigenvalue of s")
        expect(items[0][1] == ONE, "the least-index coefficient is not +1")
    matrix, sizes = restriction(columns_b, columns, ports, vectors)
    return vectors, matrix, sizes


def character_index(by_mask, value):
    masks = sorted(by_mask)

    def product_signs(mask):
        left = -1 if mask & (1 << 0) else 1
        right = -1 if mask & (1 << 1) else 1
        return left * right

    target = tuple(product_signs(mask) for mask in masks)
    expect(target == CANONICAL_SIGNATURE, "eps[1]*eps[2] is not the canonical signature")
    found = None
    for chi in range(16):
        if tuple(value(chi, mask) for mask in masks) == target:
            found = chi
    expect(found is not None, "eps[1]*eps[2] is not a character of the sign stabilizer")
    return found


def payload_basis(vectors):
    return {
        "index": "coordinate*512+address",
        "character": "eps[1]*eps[2]",
        "eigenvalue_of_s": "i",
        "field": "Q(i)",
        "coefficient": "[re, im]",
        "roots": [root for root, _items in vectors],
        "vectors": [
            [[index, coeff[0], coeff[1]] for index, coeff in items]
            for _root, items in vectors
        ],
    }


def payload_matrix(matrix):
    return {"rows": [[[entry[0], entry[1]] for entry in row] for row in matrix]}


def main():
    dump = "--dump-evidence" in sys.argv
    columns, ports = load_query()
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result.json bytes changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")
    expect(CROSSCHECK_PRIME % 4 == 3 and is_prime(CROSSCHECK_PRIME), "cross-check prime is not inert")

    port_of, lookup, port_basis, coords = prepare(columns, ports)
    group = sign_group(port_of, lookup, port_basis, coords, C1)
    expect(len(group) == 16, "c=1 sign stabilizer does not have order 16")
    by_mask = {}
    for element in group:
        mask = mask_of(element["eps"])
        expect(element["inv"] == tuple(range(8)) and element["eps"][0] == 1, "a sign element is not a pure sign pattern")
        expect(mask not in by_mask, "two sign elements share a mask")
        by_mask[mask] = element
    value = character_values(group)
    actions = {mask: action_tables(element) for mask, element in by_mask.items()}
    for dest, sign in actions.values():
        check_involution(dest, sign, "stabilizer element")

    identity = {
        "inv": tuple(range(8)),
        "eps": (1, 1, 1, 1, 1, 1, 1, 1),
        "T": tuple(1 << bit for bit in range(9)),
    }
    splitter = operator(S_INV, S_EPS, port_of, lookup, port_basis, coords)
    first = operator(G_INV, G_EPS, port_of, lookup, port_basis, coords)
    second = operator(T_INV, T_EPS, port_of, lookup, port_basis, coords)
    expect(splitter is not None and first is not None and second is not None, "an explicit symmetry is missing")
    square = compose(splitter, splitter)
    cube = compose(square, splitter)
    fourth = compose(cube, splitter)
    expect(same_operator(fourth, identity) and not same_operator(square, identity), "s does not have order 4")
    expect(apply_linear(splitter["T"], C1) == C1, "s moves sector 1")
    chi = character_index(by_mask, value)
    dimension = trace_on_character(by_mask, value, identity, chi)
    expect(dimension == 192, "eps[1]*eps[2] is not 192-dimensional")
    traces = [
        trace_on_character(by_mask, value, actor, chi)
        for actor in (identity, splitter, square, cube)
    ]
    expect(traces == [192, 0, 0, 0], "power traces of s on eps[1]*eps[2] changed")
    expect(
        order4_multiplicities(traces) == (48, 48, 48, 48),
        "s does not have eigenvalue multiplicities 48, 48, 48, 48",
    )
    expect(image_character(by_mask, value, splitter, cube, chi) == chi, "s does not preserve eps[1]*eps[2]")
    expect(image_character(by_mask, value, first, first, chi) == chi, "g does not preserve eps[1]*eps[2]")
    expect(image_character(by_mask, value, second, second, chi) != chi, "t does not move eps[1]*eps[2]")

    s_dest, s_sign = action_tables(splitter)
    columns_b = column_table(columns, ports)
    for dest, sign in actions.values():
        expect(operators_commute(columns_b, dest, sign), "B does not commute with a sign symmetry")
    expect(operators_commute(columns_b, s_dest, s_sign), "B does not commute with s")

    real_lattice = Lattice()
    gauss_plus = GaussLattice()
    for mask in sorted(by_mask):
        dest, sign = actions[mask]
        eigenvalue = value(chi, mask)
        real_lattice.add_operator(dest, sign, eigenvalue)
        gauss_plus.add_monomial(dest, sign, (eigenvalue, 0))
    real_lattice.add_operator(s_dest, s_sign, 1)
    gauss_plus.add_monomial(s_dest, s_sign, ONE)
    real_basis = real_lattice.basis()
    gauss_basis = gauss_plus.basis()
    expect(len(real_basis) == 48 and len(gauss_basis) == 48, "the eigenvalue-+1 control lost dimension 48")
    for (real_root, real_items), (gauss_root, gauss_items) in zip(real_basis, gauss_basis):
        expect(real_root == gauss_root, "the Gaussian lattice moved an eigenvalue-+1 root")
        expect(
            [(index, coeff) for index, coeff in real_items]
            == [(index, coeff[0]) for index, coeff in gauss_items],
            "the Gaussian lattice disagrees with the integer ±1 lattice",
        )
        expect(all(coeff[1] == 0 for _index, coeff in gauss_items), "an eigenvalue-+1 coefficient became imaginary")

    vectors, matrix, sizes = solve_space(
        actions, by_mask, value, chi, s_dest, s_sign, NEG_I, I_UNIT, columns_b, columns, ports
    )
    histogram = {}
    for size in sizes:
        histogram[size] = histogram.get(size, 0) + 1
    expect(histogram == {8: 8, 16: 32, 32: 8}, "support histogram changed")
    flat = [entry for row in matrix for entry in row]
    expect(min(entry[0] for entry in flat) == -16 and max(entry[0] for entry in flat) == 16, "real entry range changed")
    expect(min(entry[1] for entry in flat) == -4 and max(entry[1] for entry in flat) == 4, "imaginary entry range changed")

    coefficients_b = interpolate_characteristic(matrix)
    modular = charpoly_field(matrix, CROSSCHECK_PRIME)
    expect(len(modular) == len(coefficients_b), "modular characteristic polynomial has the wrong degree")
    for coefficient, reduced in zip(coefficients_b, modular):
        expect(gmod(coefficient, CROSSCHECK_PRIME) == reduced, "exact and Hessenberg polynomials disagree")
    coefficients_a = divide_by_four(coefficients_b)
    expect(len(coefficients_a) == 49 and coefficients_a[-1] == 1, "chi_A does not have degree 48")

    vectors_minus, matrix_minus, _sizes_minus = solve_space(
        actions, by_mask, value, chi, s_dest, s_sign, I_UNIT, NEG_I, columns_b, columns, ports
    )
    coefficients_minus = interpolate_characteristic(matrix_minus)
    expect(
        coefficients_minus == [gconj(coefficient) for coefficient in coefficients_b],
        "the eigenvalue -i polynomial is not the conjugate",
    )
    expect(coefficients_minus == coefficients_b, "the eigenvalue -i polynomial is not equal to the eigenvalue-i polynomial")

    certificate = json.loads(CERTIFICATE.read_bytes())
    expect(certificate["source_sha256"] == INTERFACE_SHA256, "published one-slot certificate names a different query")
    sectors = {}
    for sector in certificate["sectors"]:
        if sector["c"] == 1:
            sectors[(sector["t"], sector["s"])] = [int(item) for item in sector["coefficients"]]
    expect(set(sectors) == {(0, 1), (0, -1), (1, 1), (1, -1)}, "c=1 sector labels changed")
    check_factors(coefficients_a, [coefficient[0] for coefficient in coefficients_b], FACTORS, SECTOR_HITS, sectors, CHI_A_SHA256, CHI_B_SHA256)
    for _multiplicity, factor in FACTORS:
        prove_irreducible_over_qi(list(factor))
    expect(list(FACTORS[2][1]) == negative_reflected(FACTORS[1][1]), "(x+2) is not the reflection of (x-2)")
    expect(list(FACTORS[6][1]) == negative_reflected(FACTORS[3][1]), "a cubic pair is not closed under x to -x")
    expect(list(FACTORS[5][1]) == negative_reflected(FACTORS[4][1]), "the second cubic pair is not closed under x to -x")
    expect(list(FACTORS[8][1]) == reflected(FACTORS[7][1]), "the octic pair is not closed under x to -x")
    expect(product_factors(FACTORS[:-1]) != coefficients_a, "dropping a factor still multiplied to chi_A")

    character_only = GaussLattice()
    for mask in sorted(by_mask):
        dest, sign = actions[mask]
        character_only.add_monomial(dest, sign, (value(chi, mask), 0))
    character_vectors = character_only.basis()
    expect(len(character_vectors) == 192, "dropping s did not leave the 192-dimensional character space")
    wrong = GaussLattice()
    for mask in sorted(by_mask):
        dest, sign = actions[mask]
        wrong.add_monomial(dest, sign, (value(chi, mask), 0))
    wrong.add_monomial(s_dest, s_sign, I_UNIT)
    wrong_vectors = wrong.basis()
    expect(len(wrong_vectors) == 48, "the reciprocal control did not produce a 48-dimensional space")
    expect(
        all(not satisfies(s_dest, s_sign, items, I_UNIT) for _root, items in wrong_vectors),
        "using 1/lambda = i still produced eigenvectors of eigenvalue i",
    )
    flipped_mask = sorted(by_mask)[1]
    expect(value(chi, flipped_mask) == -1, "the sign-flip control no longer targets a minus sign")
    broken = GaussLattice()
    for mask in sorted(by_mask):
        eigenvalue = value(chi, mask)
        if mask == flipped_mask:
            eigenvalue = -eigenvalue
        dest, sign = actions[mask]
        broken.add_monomial(dest, sign, (eigenvalue, 0))
    broken.add_monomial(s_dest, s_sign, NEG_I)
    expect(len(broken.basis()) != 48, "flipping one character sign still produced dimension 48")

    corrupted = [row[:] for row in matrix]
    corrupted[0][0] = gadd(corrupted[0][0], ONE)
    expect(
        charpoly_field(corrupted, CROSSCHECK_PRIME) != charpoly_field(matrix, CROSSCHECK_PRIME),
        "changing a matrix entry preserved the characteristic polynomial",
    )
    linked = None
    for _root, items in vectors:
        values = {index: coeff for index, coeff in items}
        for index, _coeff in items:
            image = s_dest[index]
            if image != index and image in values:
                linked = items
                break
        if linked:
            break
    expect(linked is not None, "s fixes every basis coordinate; the sign control is vacuous")
    changed_index = linked[0][0]
    flipped_items = [(index, gneg(coeff) if index == changed_index else coeff) for index, coeff in linked]
    expect(
        not satisfies(s_dest, s_sign, flipped_items, I_UNIT),
        "a sign error in a basis vector was still an i-eigenvector",
    )
    conjugated = [(index, gconj(coeff)) for index, coeff in linked]
    expect(
        not satisfies(s_dest, s_sign, conjugated, I_UNIT),
        "conjugating a basis vector preserved eigenvalue i",
    )

    transposition = operator((1, 0, 2, 3, 4, 5, 6, 7), (1,) * 8, port_of, lookup, port_basis, coords)
    expect(transposition is None, "a coordinate transposition was accepted as a symmetry")
    moved = dict(port_of)
    moved[columns[0]], moved[columns[1]] = port_of[columns[1]], port_of[columns[0]]
    swapped_lookup = {norm(column): moved[column] for column in moved}
    expect(
        operator(S_INV, S_EPS, moved, swapped_lookup, port_basis, coords) is None,
        "a swapped port label still looked like s",
    )

    basis_payload = payload_basis(vectors)
    matrix_payload = payload_matrix(matrix)
    basis_path = PACKAGE / "evidence" / "basis.json"
    matrix_path = PACKAGE / "evidence" / "matrix.json"
    if dump:
        basis_path.parent.mkdir(parents=True, exist_ok=True)
        basis_path.write_text(canonical(basis_payload) + "\n", encoding="utf-8")
        matrix_path.write_text(canonical(matrix_payload) + "\n", encoding="utf-8")
    else:
        expect(json.loads(basis_path.read_text(encoding="utf-8")) == basis_payload, "pinned basis does not match the recomputation")
        expect(json.loads(matrix_path.read_text(encoding="utf-8")) == matrix_payload, "pinned matrix does not match the recomputation")

    expect(vectors_minus, "the eigenvalue -i basis was not built")
    print("PASS_C1_MOVED_48_I_CHARPOLY")
    print("selected kappa", SELECTED_KAPPA)
    print("character eps[1]*eps[2], eigenvalue i, dimension 48 over Q(i)")
    print("eigenvalue -i is isospectral")
    print("chi_A lies in Z[x]")
    print("chi_A SHA256", CHI_A_SHA256)
    print("chi_B SHA256", CHI_B_SHA256)
    print("chi_A = 4^(-48) chi_B(4x)")
    for multiplicity, factor in FACTORS:
        print("factor", multiplicity, descending(list(factor)))


if __name__ == "__main__":
    main()
