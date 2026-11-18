"""Check the A3 coset cuts and full formal endpoints for common-order words."""

from fractions import Fraction
from itertools import combinations, permutations, product
import json


IDENTITY = (0, 1, 2, 3)
LABELS = (0, 1, 2)
GENERATORS = ((1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2))
PRICE = tuple(Fraction(rank, rank + 1) for rank in range(4))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def target(order, mask):
    images = list(IDENTITY)
    for label in order:
        if mask & (1 << label):
            images[label], images[label + 1] = images[label + 1], images[label]
    return tuple(images)


def packed_word(order, masks, cap):
    word = []
    for label in order:
        roles = tuple(role for role, mask in enumerate(masks) if mask & (1 << label))
        for start in range(0, len(roles), cap):
            word.append((label, roles[start : start + cap]))
    return word


def formal_diagonal(word, role_count):
    # Each projector is diagonal. Its nontrivial entries act by left
    # multiplication on all 24 regular labels. The image of [e] determines
    # that full group-algebra entry. Every off-diagonal entry is zero.
    entries = [IDENTITY] * role_count
    for label, roles in reversed(word):
        generator = GENERATORS[label]
        for role in roles:
            entries[role] = tuple(generator[image] for image in entries[role])
    return tuple(entries)


def moves_base_coset(permutation, cut_size):
    return set(permutation[:cut_size]) != set(range(cut_size))


def check_fixture(order, masks, cap):
    word = packed_word(order, masks, cap)
    wanted = tuple(target(order, mask) for mask in masks) + (IDENTITY,)
    require(formal_diagonal(word, len(wanted)) == wanted, "wrong full endpoint")
    require(all(1 <= len(roles) <= cap for _, roles in word), "illegal paid rank")
    actual = sum(PRICE[len(roles)] for _, roles in word)
    lower = Fraction(0)
    for label in LABELS:
        demand = sum(moves_base_coset(entry, label + 1) for entry in wanted)
        rank_mass = sum(len(roles) for paid, roles in word if paid == label)
        require(rank_mass == demand, "coset demand and scheduled rank differ")
        batches, remainder = divmod(demand, cap)
        lower += batches * PRICE[cap] + PRICE[remainder]
    require(actual == lower, "paid price differs from the packed cuts")
    return word, wanted, actual


def rank_mod(rows, prime):
    # The crossing matrix has exactly two columns in every fixture.
    work = [list(row) for row in rows]
    rank = 0
    for column in range(2):
        pivot = next((i for i in range(rank, len(work)) if work[i][column] % prime), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        for i in range(rank + 1, len(work)):
            multiple = work[i][column] * inverse
            work[i] = [
                (value - multiple * top) % prime
                for value, top in zip(work[i], work[rank], strict=True)
            ]
        rank += 1
    return rank


def gate_crossing(entries, generator, cut_size):
    # Cosets of the parabolic in S4 are subsets of the given size. Apply
    # I + (generator - I) A to both roles over the base coset.
    base = tuple(range(cut_size))
    moved = tuple(sorted(generator[index] for index in base))
    rows = []
    for coset in combinations(IDENTITY, cut_size):
        for i in range(2):
            row = tuple(
                int(coset == base and i == j)
                + (int(coset == moved) - int(coset == base)) * entries[2 * i + j]
                for j in range(2)
            )
            if coset != base:
                rows.append(row)
    return rows


def check_gate_cuts():
    checks = 0
    for prime in (2, 3):
        for entries in product(range(prime), repeat=4):
            a, b, c, d = entries
            rank = 2 if (a * d - b * c) % prime else int(any(entries))
            for paid, generator in enumerate(GENERATORS):
                for cut in LABELS:
                    rows = gate_crossing(entries, generator, cut + 1)
                    expected = rank if cut == paid else 0
                    require(rank_mod(rows, prime) == expected, "wrong paid crossing rank")
                    checks += 1
    return checks


def check_mixed_example():
    masks = (1, 3, 6, 5, 7)
    word, wanted, price = check_fixture(LABELS, masks, 2)
    n = len(wanted)
    require(price == Fraction(11, 3), "wrong A3 example price")
    separate = sum(mask.bit_count() * PRICE[1] for mask in masks)
    inversions = sum(
        entry[i] > entry[j] for entry in wanted for i, j in combinations(IDENTITY, 2)
    )
    batches, remainder = divmod(inversions, 2)
    orbit_bound = batches * PRICE[2] + PRICE[remainder]
    require(orbit_bound == Fraction(10, 3) and separate == 5, "wrong example comparison")
    for index in range(len(word)):
        mutant = word[:index] + word[index + 1 :]
        require(formal_diagonal(mutant, n) != wanted, "omitting a batch preserved the endpoint")
    require(formal_diagonal(tuple(reversed(word)), n) != wanted, "order control failed")
    return {
        "price": str(price),
        "orbit_bound": str(orbit_bound),
        "separate_price": str(separate),
        "rejected_controls": len(word) + 1,
    }


def main():
    endpoints = 0
    for order in permutations(LABELS):
        for role_count in (1, 2, 3):
            for masks in product(range(8), repeat=role_count):
                for cap in (1, 2, 3):
                    check_fixture(order, masks, cap)
                    endpoints += 1
    result = {
        "status": "PASS_COXETER_COMMON_ORDER_TARIFF",
        "formal_endpoints": endpoints,
        "arbitrary_coupling_cuts": check_gate_cuts(),
        "mixed_a3": check_mixed_example(),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
