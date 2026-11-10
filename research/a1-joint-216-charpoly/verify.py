#!/usr/bin/env python3
"""Characteristic polynomial of one 216-dimensional joint eigenspace of A_1.

The pinned query is the historical 8-by-112 centre matrix. B = 4 A_1 is the
integer operator on the c=1 Bell block. The space is the joint +1 eigenspace
of the c=1 sign stabilizer and of the two commuting involutions g and t from
the sign-stabilizer split. Acceptance uses explicit checks, so -O does not
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
# Monic factors of chi_{A_1} on the pinned (+1,+1) space, ascending
# coefficients, with algebraic multiplicity. The product is the polynomial.
FACTORS = (
    (24, (0, 1)),
    (12, (-2, 1)),
    (12, (2, 1)),
    (2, (-6, 1)),
    (2, (6, 1)),
    (1, (-4, -2, 1)),
    (1, (-4, 2, 1)),
    (2, (-12288, 102144, -196352, 115776, 19264, -33888, 2128, 3208, -192, -108, 2, 1)),
    (2, (12288, 102144, 196352, 115776, -19264, -33888, -2128, 3208, 192, -108, -2, 1)),
    (1, (-498401280, -739049472, 132964352, 453709824, 8403968, -86923264, -97024, 6293376, -173568, -202144, 10112, 2824, -180, -14, 1)),
    (1, (-498401280, 739049472, 132964352, -453709824, 8403968, 86923264, -97024, -6293376, -173568, 202144, 10112, -2824, -180, 14, 1)),
    (2, (-1167360, -702464, 3049472, 704000, -2179840, -260736, 621184, 44928, -76384, -3632, 4376, 136, -112, -2, 1)),
    (2, (-1167360, 702464, 3049472, -704000, -2179840, 260736, 621184, -44928, -76384, 3632, 4376, -136, -112, 2, 1)),
    (1, (-1702232064, -112656384, 3560341504, 1656389632, -1259880448, -773404672, 108563456, 105269248, -321280, -6136576, -277632, 173824, 11488, -2344, -180, 12, 1)),
    (1, (-1702232064, 112656384, 3560341504, -1656389632, -1259880448, 773404672, 108563456, -105269248, -321280, 6136576, -277632, -173824, 11488, 2344, -180, -12, 1)),
)
# Published c=1 sector labels (t, s) whose minimal polynomial is divisible by
# the corresponding factor of chi_B. This is a comparison with the published
# coefficient list, not a replay of that certificate.
SECTOR_HITS = (
    ((0, -1), (0, 1), (1, -1), (1, 1)),
    ((0, -1), (0, 1), (1, -1), (1, 1)),
    ((0, -1), (0, 1), (1, -1), (1, 1)),
    ((0, 1), (1, 1)),
    ((0, -1), (1, -1)),
    ((0, 1), (1, -1)),
    ((0, -1), (1, 1)),
    ((0, -1),),
    ((0, 1),),
    ((0, 1),),
    ((0, -1),),
    ((1, 1),),
    ((1, -1),),
    ((1, -1),),
    ((1, 1),),
)
CHI_A_SHA256 = "18114a297071c454cb935ef85cab42a745954fb065be2a6d7e4ff23ef26b771b"
CHI_B_SHA256 = "ec79276843b69dc6e064cdcb009a238e8231d0a8bf8f9c532c679c6a0cb6a81e"


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


def character_joint_dimension(group, actors):
    """Trace-formula dimension of the trivial character's (+1,+1) space."""
    identity = {"inv": tuple(range(8)), "eps": (1, 1, 1, 1, 1, 1, 1, 1), "T": tuple(1 << bit for bit in range(9))}

    def character_trace(element):
        total = 0
        for symmetry in group:
            composed = compose(element, symmetry)
            dest, sign = action_tables(composed)
            closed = trace_s(composed["inv"], composed["eps"]) * fixed_addresses(composed["T"])
            expect(action_trace(dest, sign) == closed, "permutation trace disagrees with the closed trace formula")
            total += closed
        expect(total % len(group) == 0, "trivial character trace is not integral")
        return total // len(group)

    traces = [character_trace(element) for element in (identity, actors[0], actors[1], compose(actors[0], actors[1]))]
    numerator = traces[0] + traces[1] + traces[2] + traces[3]
    expect(numerator % 4 == 0, "joint trace numerator is not divisible by 4")
    return traces[0], numerator // 4


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


def main():
    dump = "--dump-evidence" in sys.argv
    columns, ports = load_query()
    selected_bytes = SELECTED.read_bytes()
    expect(sha256_bytes(selected_bytes) == SELECTED_SHA256, "selected-result.json bytes changed")
    selected = json.loads(selected_bytes)
    expect(selected["kappa"] == SELECTED_KAPPA, "selected kappa is not 781451/250000000")

    port_of, lookup, port_basis, coords = prepare(columns, ports)
    group = sign_group(port_of, lookup, port_basis, coords, C1)
    expect(len(group) == 16, "c=1 sign stabilizer does not have order 16")
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

    actions = [action_tables(element) for element in group]
    g_dest, g_sign = action_tables(first)
    t_dest, t_sign = action_tables(second)
    for dest, sign in actions:
        check_involution(dest, sign, "stabilizer element")
    check_involution(g_dest, g_sign, "g")
    check_involution(t_dest, t_sign, "t")
    trivial_dimension, joint_dimension = character_joint_dimension(group, (first, second))
    expect(trivial_dimension == 864, "trivial character dimension is not 864")
    expect(joint_dimension == 216, "trace formula does not give a 216-dimensional (+1,+1) space")

    trivial = Lattice()
    for dest, sign in actions:
        trivial.add_operator(dest, sign, 1)
    trivial_vectors = trivial.basis()
    expect(len(trivial_vectors) == 864, "explicit trivial-character basis does not have dimension 864")
    owners = {}
    grouped = [[] for _ in trivial_vectors]
    for component, (_root, items) in enumerate(trivial_vectors):
        for index, coeff in items:
            owners[index] = (component, coeff)
            grouped[component].append((index, coeff))

    def preserves_trivial(dest, sign):
        for _root, items in trivial_vectors:
            image = {}
            for index, coeff in items:
                target = dest[index]
                image[target] = image.get(target, 0) + sign[index] * coeff
            alphas = {}
            for index, value in image.items():
                if not value:
                    continue
                info = owners.get(index)
                if info is None:
                    return False
                component, coeff = info
                alpha = value * coeff
                if component in alphas and alphas[component] != alpha:
                    return False
                alphas[component] = alpha
            for component, alpha in alphas.items():
                for index, coeff in grouped[component]:
                    if image.get(index, 0) != coeff * alpha:
                        return False
        return True

    expect(preserves_trivial(g_dest, g_sign), "g does not preserve the trivial character space")
    expect(preserves_trivial(t_dest, t_sign), "t does not preserve the trivial character space")

    spaces = {}
    for g_value in (1, -1):
        for t_value in (1, -1):
            lattice = Lattice()
            for dest, sign in actions:
                lattice.add_operator(dest, sign, 1)
            lattice.add_operator(g_dest, g_sign, g_value)
            lattice.add_operator(t_dest, t_sign, t_value)
            vectors = lattice.basis()
            expect(len(vectors) == 216, "a joint eigenspace does not have dimension 216")
            for dest, sign in actions:
                for _root, items in vectors:
                    expect(fixed_by(dest, sign, items, 1), "a basis vector is not fixed by the sign stabilizer")
            for _root, items in vectors:
                expect(fixed_by(g_dest, g_sign, items, g_value), "a basis vector misses the g eigenvalue")
                expect(fixed_by(t_dest, t_sign, items, t_value), "a basis vector misses the t eigenvalue")
            spaces[(g_value, t_value)] = vectors

    columns_b = column_table(columns, ports)
    for dest, sign in actions:
        expect(operators_commute(columns_b, dest, sign), "B does not commute with a sign symmetry")
    expect(operators_commute(columns_b, g_dest, g_sign), "B does not commute with g")
    expect(operators_commute(columns_b, t_dest, t_sign), "B does not commute with t")

    matrices = {}
    for key, vectors in spaces.items():
        matrices[key], _sizes = restriction_matrix(columns_b, columns, ports, vectors)
    primary = matrices[(1, 1)]
    expect(len(primary) == 216 and all(len(row) == 216 for row in primary), "primary matrix is not 216 by 216")
    bound = coeff_bound(216, row_sum(primary))
    for key, matrix in matrices.items():
        other = coeff_bound(216, row_sum(matrix))
        if other > bound:
            bound = other
    primes, modulus = primes_past(2 * bound)
    expect(modulus > 2 * bound, "CRT modulus does not exceed the coefficient bound")

    residues = {key: [[] for _ in range(217)] for key in matrices}
    for prime in primes:
        primary_poly = None
        for key, matrix in matrices.items():
            polynomial = charpoly_mod(matrix, prime)
            expect(len(polynomial) == 217 and polynomial[-1] == 1, "modular characteristic polynomial has the wrong degree")
            if key == (1, 1):
                primary_poly = polynomial
                if prime in primes[:3]:
                    for point in (0, 1, 2, 3, 5):
                        expect(
                            evaluate(polynomial, point, prime) == shifted_det(matrix, point, prime),
                            "Hessenberg characteristic polynomial disagrees with a determinant",
                        )
            else:
                expect(polynomial == primary_poly, "a joint sign pair has a different characteristic polynomial")
            for index, coefficient in enumerate(polynomial):
                residues[key][index].append(coefficient)
    coefficients_b = [crt_signed(residues[(1, 1)][index], primes) for index in range(217)]
    expect(coefficients_b[-1] == 1, "characteristic polynomial of B is not monic")
    expect(all(coefficient == 0 for index, coefficient in enumerate(coefficients_b) if index % 2), "chi_B is not an even polynomial")
    expect(sum(primary[index][index] for index in range(216)) == -coefficients_b[215], "trace disagrees with the degree-215 coefficient")
    for index, coefficient in enumerate(coefficients_b):
        expect(abs(coefficient) <= bound, "a coefficient exceeds the Gershgorin binomial bound")
        shift = 216 - index
        expect(coefficient % (4 ** shift) == 0, "chi_A is not an integer polynomial")
    coefficients_a = [coefficient // (4 ** (216 - index)) for index, coefficient in enumerate(coefficients_b)]
    expanded = product_factors(FACTORS)
    expect(expanded == coefficients_a, "the pinned factors do not multiply to chi_A")
    expect(canonical(coefficients_a) and sha256_bytes(canonical(coefficients_a).encode()) == CHI_A_SHA256, "chi_A SHA256 changed")
    expect(sha256_bytes(canonical(coefficients_b).encode()) == CHI_B_SHA256, "chi_B SHA256 changed")
    for multiplicity, coefficients in FACTORS:
        prove_irreducible(list(coefficients))
        expect(multiplicity > 0, "a factor multiplicity is not positive")

    certificate = json.loads(CERTIFICATE.read_bytes())
    expect(certificate["source_sha256"] == INTERFACE_SHA256, "published one-slot certificate names a different query")
    sectors = {}
    for sector in certificate["sectors"]:
        if sector["c"] == 1:
            sectors[(sector["t"], sector["s"])] = [int(value) for value in sector["coefficients"]]
    expect(set(sectors) == {(0, 1), (0, -1), (1, 1), (1, -1)}, "c=1 sector labels changed")
    for (multiplicity, coefficients), hits in zip(FACTORS, SECTOR_HITS):
        scaled = scale_to_b(coefficients)
        found = tuple(key for key in ((0, -1), (0, 1), (1, -1), (1, 1)) if monic_divides(scaled, sectors[key]))
        expect(found == hits, "sector divisibility of a factor changed")
        expect(hits, "a factor divides none of the published c=1 sector polynomials")
        expect(multiplicity >= 1, "multiplicity dropped out of the sector comparison")

    basis_payload = {
        "index": "coordinate*512+address",
        "eigenvalues": {"H": 1, "g": 1, "t": 1},
        "roots": [root for root, _items in spaces[(1, 1)]],
        "vectors": [[[index, coeff] for index, coeff in items] for _root, items in spaces[(1, 1)]],
    }
    matrix_payload = {"rows": primary}
    basis_path = PACKAGE / "evidence" / "basis.json"
    matrix_path = PACKAGE / "evidence" / "matrix.json"
    if dump:
        basis_path.write_text(canonical(basis_payload) + "\n")
        matrix_path.write_text(canonical(matrix_payload) + "\n")
    else:
        expect(json.loads(basis_path.read_text()) == basis_payload, "pinned basis does not match the recomputation")
        expect(json.loads(matrix_path.read_text()) == matrix_payload, "pinned matrix does not match the recomputation")

    # Rejection controls. Each must fail closed.
    transposition = operator((1, 0, 2, 3, 4, 5, 6, 7), (1,) * 8, port_of, lookup, port_basis, coords)
    expect(transposition is None, "a coordinate transposition was accepted as a symmetry")
    moved = dict(port_of)
    first_column, second_column = columns[0], columns[1]
    moved[first_column], moved[second_column] = port_of[second_column], port_of[first_column]
    swapped_lookup = {norm(column): moved[column] for column in moved}
    expect(operator(G_INV, G_EPS, moved, swapped_lookup, port_basis, coords) is None, "a swapped port label still looked like a symmetry")
    without_g = Lattice()
    for dest, sign in actions:
        without_g.add_operator(dest, sign, 1)
    without_g.add_operator(t_dest, t_sign, 1)
    expect(len(without_g.basis()) == 432, "omitting g did not leave the 432-dimensional t=+1 space")
    wrong_sign = list(actions[0][1])
    wrong_sign[0] *= -1
    broken = Lattice()
    for dest, sign in actions[1:]:
        broken.add_operator(dest, sign, 1)
    broken.add_operator(actions[0][0], wrong_sign, 1)
    broken.add_operator(g_dest, g_sign, 1)
    broken.add_operator(t_dest, t_sign, 1)
    expect(len(broken.basis()) != 216, "flipping one stabilizer sign still produced dimension 216")
    corrupted = [row[:] for row in primary]
    corrupted[0][0] += 1
    expect(charpoly_mod(corrupted, 1000003) != charpoly_mod(primary, 1000003), "changing a matrix entry preserved the characteristic polynomial")
    truncated = product_factors(FACTORS[:-1])
    expect(truncated != coefficients_a, "dropping a factor still multiplied to chi_A")
    linked = None
    for dest, sign in actions + [(g_dest, g_sign), (t_dest, t_sign)]:
        for _root, items in spaces[(1, 1)]:
            values = {index: coeff for index, coeff in items}
            for index, _coeff in items:
                image = dest[index]
                if image != index and image in values:
                    linked = (dest, sign, items, index)
                    break
            if linked:
                break
        if linked:
            break
    expect(linked is not None, "no signed involution links two basis coordinates; the sign control is vacuous")
    dest, sign, items, index = linked
    flipped = [(item, -coeff if item == index else coeff) for item, coeff in items]
    expect(not fixed_by(dest, sign, flipped, 1), "a sign error in a basis vector was still fixed")

    print("PASS_A1_JOINT_216_CHARPOLY")
    print("selected kappa", SELECTED_KAPPA)
    print("space trivial character 864; joint (+1,+1) dimension 216")
    print("four joint sign pairs are isospectral")
    print("chi_A SHA256", CHI_A_SHA256)
    print("chi_B SHA256", CHI_B_SHA256)
    print("chi_A = 4^(-216) chi_B(4x)")
    for multiplicity, coefficients in FACTORS:
        print("factor", multiplicity, descending(coefficients))


if __name__ == "__main__":
    main()
