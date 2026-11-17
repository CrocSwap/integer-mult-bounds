#!/usr/bin/env python3
"""Exact spectral certificate for one joint space in centre sector 3."""

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

WIDTH = 512
DIMENSION = 8 * WIDTH
QUERY = Path(
    "research/centre-polynomial-cache-limits/frozen/work/"
    "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json"
)
QUERY_HASH = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(bits):
    return bits.bit_count() % 2


def load_query(root):
    raw = (root / QUERY).read_bytes()
    require(sha256(raw).hexdigest() == QUERY_HASH, "unexpected query bytes")
    record = json.loads(raw)
    rows, ports = record["R"], record["ports"]
    require(len(rows) == 8 and len(set(ports)) == len(ports) == 112, "query shape")
    require(all(0 < port < WIDTH and parity(port) for port in ports), "query labels")
    columns = tuple(tuple(int(row.get(str(i), 0)) for row in rows) for i in range(112))
    return tuple(zip(ports, columns, strict=True))


def projective(column):
    first = next((value for value in column if value), 0)
    require(first in (-1, 1), "invalid projective column")
    return tuple(first * value for value in column)


def address_action(query, permutation, signs):
    lookup = {projective(column): port for port, column in query}
    require(len(lookup) == len(query), "duplicate projective column")
    span = {0: 0}
    for port, column in query:
        signed = projective(tuple(signs[i] * column[permutation[i]] for i in range(8)))
        require(signed in lookup, "missing signed column")
        image = lookup[signed]
        if port in span:
            require(span[port] == image, "port action is not linear")
        else:
            span.update({key ^ port: value ^ image for key, value in span.items()})
    require(len(span) == WIDTH and span[3] == 3, "action does not fix sector 3")
    require(len(set(span.values())) == WIDTH, "noninvertible address action")
    for first in range(9):
        for second in range(9):
            image_dot = parity(span[1 << first] & span[1 << second])
            require(image_dot == (first == second), "nonorthogonal address action")
    return tuple(span[address] for address in range(WIDTH))


def generators(query):
    identity = tuple(range(8))
    specs = [(identity, 1 << digit, -1 if digit != 7 else 1) for digit in (1, 3, 5, 7)]
    specs += [((2, 1, 0, 3, 6, 5, 4, 7), 5, 1), ((4, 1, 6, 3, 0, 5, 2, 7), 17, 1)]
    actions = []
    for permutation, mask, eigenvalue in specs:
        signs = tuple((-1) ** ((mask >> i) & 1) for i in range(8))
        addresses = address_action(query, permutation, signs)
        destinations = tuple(permutation[i] * WIDTH + a for i in range(8) for a in addresses)
        weights = tuple(eigenvalue * signs[i] for i in range(8) for _ in range(WIDTH))
        actions.append(tuple(zip(destinations, weights, strict=True)))
    return tuple(actions)


def check_generators(actions):
    for action in actions:
        for index, (image, sign) in enumerate(action):
            require(action[image] == (index, sign), "generator is not an involution")
    for left, right in combinations(actions, 2):
        for (i, left_sign), (j, right_sign) in zip(left, right, strict=True):
            left_right, sign_j = left[j]
            right_left, sign_i = right[i]
            require(
                (left_right, sign_j * right_sign) == (right_left, sign_i * left_sign),
                "generators do not commute",
            )


def orbit_basis(actions):
    seen = set()
    basis = []
    discarded = 0
    for seed in range(DIMENSION):
        if seed in seen:
            continue
        orbit = [(seed, 1)]
        for action in actions:
            orbit += [(action[index][0], value * action[index][1]) for index, value in orbit]
        values = dict(orbit)
        require(not seen.intersection(values) and min(values) == seed, "bad orbit partition")
        seen.update(values)
        if any(values[index] != value for index, value in orbit):
            discarded += 1
            continue
        for action in actions:
            for index, value in values.items():
                destination, sign = action[index]
                require(values.get(destination) == sign * value, "basis violates an equation")
        basis.append(values)
    require(len(seen) == DIMENSION, "incomplete orbit partition")
    return tuple(basis), discarded


def bell_image(query, vector, sector=3):
    image = [0] * DIMENSION
    coordinates = tuple((divmod(index, WIDTH), weight) for index, weight in vector.items())
    for port, column in query:
        translation = parity(port & sector)
        support = tuple((i, scalar) for i, scalar in enumerate(column) if scalar)
        for (i, address), weight in coordinates:
            if translation:
                target_address = address ^ port
                sign = 1
            else:
                target_address = address
                sign = (-1) ** parity(port & address)
            coefficient = sign * column[i] * weight
            for j, entry in support:
                image[j * WIDTH + target_address] += coefficient * entry
    return image


def restriction(query, basis, sector=3):
    roots = tuple(min(vector) for vector in basis)
    columns = []
    for vector in basis:
        image = bell_image(query, vector, sector)
        coordinates = tuple(image[root] for root in roots)
        reconstructed = [0] * DIMENSION
        for value, basis_vector in zip(coordinates, basis, strict=True):
            for index, weight in basis_vector.items():
                reconstructed[index] = value * weight
        require(image == reconstructed, "Bell image leaves the joint space")
        columns.append(coordinates)
    return tuple(zip(*columns, strict=True))


def charpoly(matrix):
    """Faddeev-LeVerrier, descending coefficients of det(xI - matrix)."""
    size = len(matrix)
    residual = [[int(i == j) for j in range(size)] for i in range(size)]
    coefficients = [1]
    for degree in range(1, size + 1):
        columns = tuple(zip(*residual, strict=True))
        residual = [
            [sum(a * b for a, b in zip(row, col, strict=True)) for col in columns]
            for row in matrix
        ]
        coefficient, remainder = divmod(-sum(residual[i][i] for i in range(size)), degree)
        require(remainder == 0, "characteristic coefficient is not integral")
        coefficients.append(coefficient)
        for i in range(size):
            residual[i][i] += coefficient
    require(all(not any(row) for row in residual), "Cayley-Hamilton residual")
    return coefficients


def multiply(left, right):
    product = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            product[i + j] += a * b
    return product


def claimed_polynomial():
    # Descending coefficients for A_3. The matrix represents 4 A_3.
    factors = (
        (1,) + (0,) * 10,
        (1, 0, -36),
        *((1, 0, -4),) * 5,
        *((1, 0, -12, 8),) * 2,
        *((1, 0, -12, -8),) * 2,
        (1, 4, -60, -176, 640, 768),
        (1, -4, -60, 176, 640, -768),
    )
    polynomial = [1]
    for factor in factors:
        polynomial = multiply(polynomial, factor)
    return polynomial


def wrong_sector_control(query, basis):
    try:
        restriction(query, basis, sector=1)
    except ValueError as error:
        require(str(error) == "Bell image leaves the joint space", "wrong failure")
    else:
        raise ValueError("sector-1 substitution should fail")


def main():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    query = load_query(root)
    actions = generators(query)
    check_generators(actions)
    basis, discarded = orbit_basis(actions)
    require(len(basis) == 44 and all(len(vec) == 8 for vec in basis), "wrong basis")
    matrix = restriction(query, basis)
    coefficients = claimed_polynomial()
    scaled = [coefficient * 4**degree for degree, coefficient in enumerate(coefficients)]
    require(charpoly(matrix) == scaled, "characteristic polynomial differs")
    wrong_sector_control(query, basis)
    result = {
        "status": "PASS_C3_WEIGHT3_PLUS_PLUS_CHARPOLY",
        "ambient_addresses": DIMENSION,
        "basis_vectors": len(basis),
        "discarded_orbits": discarded,
        "basis_support": len(basis[0]),
        "full_coefficients_checked": len(basis) * DIMENSION,
        "charpoly_A3_descending": coefficients,
        "charpoly_4A3_descending": scaled,
        "matrix_sha256": sha256(json.dumps(matrix, separators=(",", ":")).encode()).hexdigest(),
        "wrong_sector_rejected": True,
        "package_sha256": {
            name: sha256((package / name).read_bytes()).hexdigest()
            for name in ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
        },
        "query_sha256": QUERY_HASH,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
