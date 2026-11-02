#!/usr/bin/env python3
"""Exact finite corroboration of the multilinear dirty-input query theorem."""

from fractions import Fraction
from hashlib import sha256
from heapq import heappop, heappush
from itertools import product
import json
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_prices(prices, read_price=1):
    require(isinstance(prices, tuple), "prices must be a tuple")
    require(1 <= len(prices) <= 8, "dimension must be in 1..8")
    for value in prices + (read_price,):
        require(type(value) in (int, Fraction), "exact prices required")
        value = Fraction(value)
        require(0 < value <= 4096, "price outside (0,4096]")
        require(value.denominator <= 4096, "denominator exceeds 4096")


def cube_word(prices):
    """Use cheap coordinates for the frequent reflected-Gray transitions."""
    checked_prices(prices)
    dimension = len(prices)
    order = tuple(index for _, index in sorted(
        (-price, index) for index, price in enumerate(prices)))
    word = []
    previous = 0
    for time in range(1 << dimension):
        gray = time ^ (time >> 1)
        if time:
            bit = (previous ^ gray).bit_length() - 1
            word.append(("S", order[dimension - 1 - bit]))
        word.append(("E", -1))
        previous = gray
    word.append(("S", order[0]))
    require(len(word) == 2 << dimension, "wrong total word length")
    return tuple(word)


def nested_word(dimension):
    """Literal commutators, with expensive coordinates at outer levels."""
    require(1 <= dimension <= 8, "nested dimension outside 1..8")
    word = (("E", -1),)
    for index in range(dimension - 1, -1, -1):
        word = (("S", index),) + word + (("S", index),) + word[::-1]
    require(len(word) == 3 * (1 << dimension) - 2, "nested size")
    return word


def signature(word, dimension):
    require(1 <= dimension <= 8, "signature dimension outside 1..8")
    require(isinstance(word, tuple) and len(word) <= 1024, "word capacity")
    position = 0
    reads = [0] * (1 << dimension)
    toggles = [0] * dimension
    for operation, index in word:
        require(operation in ("S", "E"), "unknown operation")
        if operation == "S":
            require(type(index) is int and 0 <= index < dimension, "source")
            position ^= 1 << index
            toggles[index] += 1
        else:
            require(index == -1, "evaluation has no source index")
            reads[position] += 1
    return position, tuple(reads), tuple(toggles)


def polynomial_coefficients(reads):
    require(len(reads) in (2, 4, 8, 16, 32, 64, 128, 256), "cube size")
    return tuple(sum(reads[mask] for mask in range(len(reads))
                     if mask & subset == subset) % 2
                 for subset in range(len(reads)))


def valid_word(word, dimension):
    position, reads, _ = signature(word, dimension)
    target = (0,) * ((1 << dimension) - 1) + (1,)
    return position == 0 and polynomial_coefficients(reads) == target


def price(word, prices, read_price=1):
    checked_prices(prices, read_price)
    _, reads, toggles = signature(word, len(prices))
    return sum(reads) * read_price + sum(
        count * cost for count, cost in zip(toggles, prices, strict=True))


def optimum(prices, read_price=1):
    checked_prices(prices, read_price)
    descending = tuple(sorted(prices, reverse=True))
    transition = 2 * descending[0] + sum(
        (1 << index) * descending[index] for index in range(1, len(prices)))
    return transition + (1 << len(prices)) * read_price


def walk_oracle(prices):
    """Dijkstra on position/visited states; repetitions and detours allowed."""
    checked_prices(prices)
    dimension = len(prices)
    require(dimension <= 3, "oracle dimension exceeds three")
    vertices = 1 << dimension
    full = (1 << vertices) - 1
    distance = {(0, 1): 0}
    heap = [(0, 0, 1)]
    settled = 0
    # At most one successful relaxation per directed state edge.
    pop_limit = 1 + dimension * vertices * (1 << vertices)
    for _ in range(pop_limit):
        require(bool(heap), "oracle exhausted before reaching the goal")
        cost, position, visited = heappop(heap)
        if distance[(position, visited)] != cost:
            continue
        settled += 1
        if position == 0 and visited == full:
            return cost, settled
        for index in range(dimension):
            next_position = position ^ (1 << index)
            next_visited = visited | (1 << next_position)
            key = next_position, next_visited
            candidate = cost + prices[index]
            old = distance.get(key)
            if old is None or candidate < old:
                distance[key] = candidate
                heappush(heap, (candidate, next_position, next_visited))
    raise ValueError("oracle pop capacity exceeded")


def scalar_replay(word, dimension, source, dirt, target):
    workspace = dirt
    output = target
    for operation, index in word:
        if operation == "S":
            workspace ^= source & (1 << index)
        else:
            output ^= int(workspace == (1 << dimension) - 1)
    return workspace, output


def matrix_product(left, right):
    result = 0
    for row in range(2):
        for column in range(2):
            bit = 0
            for inner in range(2):
                bit ^= ((left >> (2 * row + inner)) & 1) & (
                    (right >> (2 * inner + column)) & 1)
            result |= bit << (2 * row + column)
    return result


def matrix_replay(word, sources, initial, target):
    workspace = list(initial)
    output = target
    for operation, index in word:
        if operation == "S":
            workspace[index] ^= sources[index]
        else:
            value = 9  # The 2-by-2 identity, in row-major bit order.
            for matrix in workspace:
                value = matrix_product(value, matrix)
            output ^= value
    return tuple(workspace), output


def check_polynomials():
    contexts = 0
    parity_vectors = 0
    for dimension in range(1, 9):
        prices = tuple(Fraction(index + 1, index + 2)
                       for index in range(dimension))
        word = cube_word(prices)
        require(valid_word(word, dimension), "symbolic endpoint")
        require(valid_word(word[::-1], dimension), "symbolic inverse")
        require(price(word, prices, Fraction(2, 3)) ==
                optimum(prices, Fraction(2, 3)), "fractional tariff")
        _, reads, toggles = signature(word, dimension)
        require(reads == (1,) * (1 << dimension), "exactly one read per vertex")
        require(sum(toggles) == 1 << dimension, "Gray transition count")
        contexts += 1
        if dimension <= 3:
            survivors = []
            for encoded in range(1 << (1 << dimension)):
                row = tuple((encoded >> mask) & 1
                            for mask in range(1 << dimension))
                target = (0,) * ((1 << dimension) - 1) + (1,)
                if polynomial_coefficients(row) == target:
                    survivors.append(encoded)
                parity_vectors += 1
            require(survivors == [(1 << (1 << dimension)) - 1], "read uniqueness")
    return contexts, parity_vectors


def check_scalar_states():
    count = 0
    for dimension in range(1, 6):
        word = cube_word((1,) * dimension)
        old_word = nested_word(dimension)
        require(valid_word(old_word, dimension), "nested symbolic endpoint")
        for source, dirt, target in product(
                range(1 << dimension), range(1 << dimension), range(2)):
            wanted = dirt, target ^ int(source == (1 << dimension) - 1)
            result = scalar_replay(word, dimension, source, dirt, target)
            require(result == wanted, "scalar dirty endpoint")
            require(scalar_replay(old_word, dimension, source, dirt, target) ==
                    wanted, "matched nested endpoint")
            require(scalar_replay(word[::-1], dimension, source, *result) ==
                    (dirt, target), "scalar inverse restoration")
            count += 1
    return count


def check_matrix_states():
    word = cube_word((2, 1))
    count = 0
    for x0, x1, z0, z1 in product(range(16), repeat=4):
        sources, initial = (x0, x1), (z0, z1)
        wanted = initial, 9 ^ matrix_product(x0, x1)
        result = matrix_replay(word, sources, initial, 9)
        require(result == wanted, "noncommuting matrix endpoint")
        require(matrix_replay(word[::-1], sources, *result) ==
                (initial, 9), "matrix inverse restoration")
        count += 1
    require(matrix_product(2, 4) != matrix_product(4, 2), "noncommuting fixture")
    return count


def check_walk_optima():
    contexts = 0
    settled = 0
    for dimension in range(1, 4):
        for prices in product(range(1, 5), repeat=dimension):
            observed, visited = walk_oracle(prices)
            require(observed + (1 << dimension) == optimum(prices), "walk optimum")
            require(price(cube_word(prices), prices) == optimum(prices), "word price")
            contexts += 1
            settled += visited
    return contexts, settled


def check_controls():
    word = cube_word((1, 1))
    deletions = 0
    for index in range(len(word)):
        mutant = word[:index] + word[index + 1:]
        require(not valid_word(mutant, 2), "deleted event escaped")
        deletions += 1
    bad_prices = ((), (0,), (-1,), (True,), (1.0,), (4097,),
                  (Fraction(1, 4097),), (1,) * 9)
    for prices in bad_prices:
        try:
            cube_word(prices)
        except ValueError:
            continue
        raise ValueError("invalid price accepted")
    prices = (7, 3, 1)
    good, expensive = cube_word(prices), cube_word((1, 3, 7))
    require(valid_word(expensive, 3), "expensive legal control")
    require(price(good, prices) == 32 and price(expensive, prices) == 44,
            "price-order control")
    detour = (("S", 0), ("S", 0)) + good
    require(valid_word(detour, 3), "restored detour control")
    require(price(detour, prices) == price(good, prices) + 14, "detour charge")
    require(price(nested_word(2), (1, 1)) == 10 and len(word) == 8,
            "first strict improvement")
    return {"event_deletions": deletions, "invalid_prices": len(bad_prices),
            "legal_expensive_order": 1, "charged_detour": 1,
            "matched_nested_comparator": 1}


def source_hashes():
    root = Path(__file__).resolve().parent
    result = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py"):
        with (root / name).open("rb") as source:
            data = source.read(131073)
        require(len(data) <= 131072, "package source size cap")
        result[name] = sha256(data).hexdigest()
    return result


def main():
    symbolic, parities = check_polynomials()
    scalar = check_scalar_states()
    matrices = check_matrix_states()
    walks, settled = check_walk_optima()
    controls = check_controls()
    result = {"status": "PASS_MULTILINEAR_DIRTY_CUBE", "claim_type": "scoped proof",
              "symbolic_dimensions": symbolic, "read_parity_vectors": parities,
              "scalar_dirty_states": scalar, "matrix_dirty_input_tuples": matrices,
              "walk_price_contexts": walks, "walk_states_settled": settled,
              "controls": controls, "bilinear_calls": {"nested": 10, "cube": 8},
              "python": platform.python_version(), "files_sha256": source_hashes()}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
