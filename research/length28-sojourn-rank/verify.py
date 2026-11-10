#!/usr/bin/env python3
"""Finite corroboration of the length-28 sojourn-rank proof.

The argument itself is in README.md. These checks cover the numerical
bounds, the exhaustive size-at-most-4 difference census in F_2^3, the
length-32 Gray positive control, and rejecting mutations. They do not
search length-28 words.
"""

from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def differences(points):
    return {left ^ right for left in points for right in points}


def subset_points(mask):
    return tuple(index for index in range(8) if (mask >> index) & 1)


def gray_block(offset):
    vertices = tuple(index ^ (index >> 1) for index in range(16)) + (0,)
    word = []
    for left, right in zip(vertices, vertices[1:]):
        difference = left ^ right
        require(difference.bit_count() == 1, "Gray step is not a source")
        word.append(offset + difference.bit_length() - 1)
    return tuple(word)


def prefix_states(word, dimension):
    state = 0
    states = [state]
    for label in word:
        require(0 <= label < dimension, "label out of range")
        state ^= 1 << label
        states.append(state)
    return tuple(states)


def closed_coverage(word, dimension):
    states = prefix_states(word, dimension)
    closed = states[-1] == 0
    # The final return duplicates the start. The prefix set is the earlier states.
    covered = differences(states[:-1])
    return closed, len(covered), states


def small_subset_census():
    checked = 0
    worst_missed = 0
    for mask in range(1, 256):
        points = subset_points(mask)
        if len(points) > 4:
            continue
        covered = differences(points)
        missed = [value for value in range(8) if value not in covered]
        require(0 in covered, "a nonempty set missed 0")
        require(missed, "a set of size at most 4 covered F_2^3")
        require(all(value != 0 for value in missed), "the recorded miss was 0")
        worst_missed = max(worst_missed, len(missed))
        checked += 1
    require(checked == 162, "subset census domain")
    return checked, worst_missed


def short_flat_paths():
    """Walks of at most three flat steps visit at most four V-values."""
    checked = 0

    def walk(state, seen, remaining):
        nonlocal checked
        if remaining == 0:
            checked += 1
            require(len(differences(tuple(seen))) < 8, "short flat path covered F_2^3")
            return
        for bit in range(3):
            nxt = state ^ (1 << bit)
            walk(nxt, seen | {nxt}, remaining - 1)

    for start in range(8):
        for length in range(4):
            walk(start, {start}, length)
    require(checked == 320, "flat-path census domain")
    return checked


def five_point_witness():
    full = differences((0, 1, 2, 3, 4))
    require(full == set(range(8)), "five-point difference witness")
    subspace = differences((0, 1, 2, 3))
    require(subspace == {0, 1, 2, 3}, "subspace control")
    punctured = differences((0, 1, 2, 3, 4)[:-1])
    require(len(punctured) < 8, "dropping the fifth point must reopen a hole")


def arithmetic_bounds():
    products = tuple(rank_size * (28 - rank_size) for rank_size in range(1, 5))
    require(products == (27, 52, 75, 96), "rank-at-most-2 products")
    require(max(products) < 128, "low-rank product still covers")
    outside_steps = 3 * 4 + 2
    require(outside_steps == 14 and 1 + outside_steps < 16, "case A cosets")
    flat_supply = 4 + 4 + 2
    minimum_visiting_steps = 7
    insertions = flat_supply - minimum_visiting_steps
    values = insertions + 1
    pair_sums = 1 + values * (values - 1) // 2
    require((flat_supply, insertions, values, pair_sums) == (10, 3, 4, 7),
            "case B budget")
    require(pair_sums < 8, "four values cover F_2^3")
    counts = (4, 4, 4, 4, 4, 4, 2, 2)
    require(sum(counts) == 28 and all(count % 2 == 0 and count > 0 for count in counts),
            "multiplicity shape")


def gray_controls():
    word = gray_block(0) + gray_block(4)
    closed, covered, _states = closed_coverage(word, 8)
    require(closed and len(word) == 32 and covered == 256, "Gray upper control")
    counts = [0] * 8
    for label in word:
        counts[label] += 1
    require(all(count % 2 == 0 and count > 0 for count in counts), "Gray parity")
    mutated = (word[0] ^ 1,) + word[1:]
    mutated_closed, mutated_covered, _states = closed_coverage(mutated, 8)
    require((not mutated_closed) or mutated_covered < 256, "mutation was still universal")
    deleted = word[:-1]
    deleted_closed, deleted_covered, _states = closed_coverage(deleted, 8)
    require((not deleted_closed) or deleted_covered < 256, "deleted step was still universal")
    return covered


def main():
    arithmetic_bounds()
    checked, worst_missed = small_subset_census()
    paths = short_flat_paths()
    five_point_witness()
    covered = gray_controls()
    root = Path(__file__).resolve().parents[2]
    require((root / "certificates" / "selected-result.json").is_file(), "selected record")
    print(
        "PASS_LENGTH28_SOJOURN_RANK "
        f"subsets={checked} paths={paths} worst_missed={worst_missed} gray={covered}"
    )


if __name__ == "__main__":
    main()
