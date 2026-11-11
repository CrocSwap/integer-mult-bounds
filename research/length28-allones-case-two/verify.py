#!/usr/bin/env python3
"""Finite corroboration of the length-28 all-ones case-II sumset split.

The argument is in README.md. These checks cover the distance parities, the
40320 permutation normalizations, the direct-sum flag table, the uniform
product bound, both turn-off orders of the three-pass insertion family, the
length-32 Gray control, and rejecting mutations. They do not search the
remaining complement orderings and they do not decide f(8).
"""

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_FLAGS = {
    (0, 1): ((1, 1, 7), (1, 7, 7)),
    (0, 2): ((1, 2, 6), (2, 6, 12)),
    (0, 3): ((1, 3, 5), (3, 5, 15)),
    (0, 4): ((1, 4, 4), (4, 4, 16)),
    (0, 5): ((1, 5, 3), (5, 3, 15)),
    (0, 6): ((1, 6, 2), (6, 2, 12)),
    (0, 7): ((1, 7, 1), (7, 1, 7)),
    (1, 2): ((2, 1, 6), (2, 12, 6)),
    (1, 3): ((2, 2, 5), (4, 10, 10)),
    (1, 4): ((2, 3, 4), (6, 8, 12)),
    (1, 5): ((2, 4, 3), (8, 6, 12)),
    (1, 6): ((2, 5, 2), (10, 4, 10)),
    (1, 7): ((2, 6, 1), (12, 2, 6)),
    (2, 3): ((3, 1, 5), (3, 15, 5)),
    (2, 4): ((3, 2, 4), (6, 12, 8)),
    (2, 5): ((3, 3, 3), (9, 9, 9)),
    (2, 6): ((3, 4, 2), (12, 6, 8)),
    (2, 7): ((3, 5, 1), (15, 3, 5)),
    (3, 4): ((4, 1, 4), (4, 16, 4)),
    (3, 5): ((4, 2, 3), (8, 12, 6)),
    (3, 6): ((4, 3, 2), (12, 8, 6)),
    (3, 7): ((4, 4, 1), (16, 4, 4)),
    (4, 5): ((5, 1, 3), (5, 15, 3)),
    (4, 6): ((5, 2, 2), (10, 10, 4)),
    (4, 7): ((5, 3, 1), (15, 5, 3)),
    (5, 6): ((6, 1, 2), (6, 12, 2)),
    (5, 7): ((6, 2, 1), (12, 6, 2)),
    (6, 7): ((7, 1, 1), (7, 7, 1)),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def differences(points):
    return {left ^ right for left in points for right in points}


def prefixes(word):
    state = 0
    states = []
    for label in word:
        states.append(state)
        state ^= 1 << label
    return tuple(states), state


def gray_block(offset):
    vertices = tuple(index ^ (index >> 1) for index in range(16)) + (0,)
    word = []
    for left, right in zip(vertices, vertices[1:]):
        difference = left ^ right
        require(difference.bit_count() == 1, "Gray step is not a source")
        word.append(offset + difference.bit_length() - 1)
    return tuple(word)


def apply_sigma(state, perm):
    image = 0
    for new, old in enumerate(perm):
        if (state >> old) & 1:
            image |= 1 << new
    return image


def standard_chain():
    state = 0
    chain = [0]
    for bit in range(8):
        state ^= 1 << bit
        chain.append(state)
    return tuple(chain)


def permutation_census():
    chain = standard_chain()
    require(chain[-1] == 255 and len(chain) == 9, "identity chain")
    checked = 0
    for perm in itertools.permutations(range(8)):
        states, final = prefixes(perm)
        require(final == 255, "a permutation arc missed all-ones")
        images = tuple(apply_sigma(state, perm) for state in states) + (apply_sigma(final, perm),)
        require(images == chain, "coordinate relabeling missed the identity chain")
        require(apply_sigma(255, perm) == 255, "a coordinate permutation moved all-ones")
        checked += 1
    require(checked == 40320, "permutation domain")
    return checked


def distance_parities():
    shorter = []
    for length in range(8, 15):
        if length % 2 == 0:
            other = 28 - length
            require(other % 2 == 0 and other >= length, "complementary all-ones length")
            shorter.append(length)
    require(shorter == [8, 10, 12, 14], "shorter all-ones distances")
    require(sum(1 for _ in range(8)) == 8, "eight odd coordinates")
    # Eight odd positive counts sum to an even number, and the minimum sum is 8.
    require(sum(8 * [1]) == 8 and (8 * 1) % 2 == 0, "minimum even length")


def composition_bound():
    seen = 0
    worst = 0
    for left in range(1, 8):
        for middle in range(1, 9 - left):
            right = 9 - left - middle
            if right < 1:
                continue
            products = (left * middle, left * right, middle * right)
            require(max(products) <= 16, "composition product")
            worst = max(worst, max(products))
            seen += 1
    require(seen == 28 and worst == 16, "positive compositions of 9")
    require(8 * 8 >= 64 and 8 + 8 + 8 <= 28, "abstract slice sizes remain possible")


def flag_sets(early, late):
    low_length = early
    middle_length = late - early - 1
    high_length = 7 - late
    low = {0}
    mask = 0
    for bit in range(low_length):
        mask |= 1 << bit
        low.add(mask)
    base = (1 << low_length) - 1
    middle = {base}
    for bit in range(middle_length):
        base |= 1 << (low_length + bit)
        middle.add(base)
    high_base = (1 << (low_length + middle_length)) - 1
    high = {high_base}
    for bit in range(high_length):
        high_base |= 1 << (low_length + middle_length + bit)
        high.add(high_base)
    return low, middle, high


def flag_table():
    worst = 0
    for early in range(8):
        for late in range(early + 1, 8):
            low, middle, high = flag_sets(early, late)
            sizes = (len(low), len(middle), len(high))
            sums = (
                len({x ^ y for x in low for y in middle}),
                len({x ^ y for x in low for y in high}),
                len({x ^ y for x in middle for y in high}),
            )
            require(sum(sizes) == 9, "arc flags are the nine arc prefixes")
            require(sums == tuple(left * right for left, right in (
                (sizes[0], sizes[1]), (sizes[0], sizes[2]), (sizes[1], sizes[2]))),
                    "flag sum collided")
            require(EXPECTED_FLAGS[(early, late)] == (sizes, sums), "flag table changed")
            worst = max(worst, max(sums))
    require(len(EXPECTED_FLAGS) == 28 and worst == 16, "flag table domain")
    return worst


def body_labels(early, late):
    return tuple(source for source in range(8) if source not in (early, late))


def project_body(state, labels):
    mask = 0
    for bit, source in enumerate(labels):
        if (state >> source) & 1:
            mask |= 1 << bit
    return mask


def arc_ranks(word, source):
    positions = [index for index, label in enumerate(word) if label == source]
    require(len(positions) == 2, "double occurrence count")
    left, right = positions
    forward = word[left + 1:right]
    backward = word[right + 1:] + word[:left]
    return len(set(forward)), len(set(backward))


def flip_pattern(sequence, source):
    bit = 1
    pattern = []
    for label in sequence:
        if label != source:
            continue
        pattern.append(0 if bit == 1 else 1)
        bit ^= 1
    return tuple(pattern), bit


def three_pass(early, late):
    triples = [source for source in range(8) if source not in (early, late)]
    return tuple(triples + triples[::-1] + triples)


def insert(early, late, early_at, late_at):
    background = three_pass(early, late)
    sequence = [None] * 20
    sequence[early_at] = early
    sequence[late_at] = late
    cursor = 0
    for index in range(20):
        if sequence[index] is None:
            sequence[index] = background[cursor]
            cursor += 1
    require(cursor == 18, "background length")
    return tuple(sequence)


def schedule_ok(sequence, early, late):
    counts = [0] * 8
    for label in sequence:
        counts[label] += 1
    expected = [3] * 8
    expected[early] = 1
    expected[late] = 1
    if counts != expected:
        return False
    ups = 0
    state = 255
    for label in sequence:
        if ((state >> label) & 1) == 0:
            ups += 1
        state ^= 1 << label
    if state != 0 or ups != 6:
        return False
    for source in range(8):
        pattern, final_bit = flip_pattern(sequence, source)
        if source in (early, late):
            if pattern != (0,) or final_bit != 0:
                return False
        elif pattern != (0, 1, 0) or final_bit != 0:
            return False
    return True


def slices_of(word, early, late):
    labels = body_labels(early, late)
    states, final = prefixes(word)
    require(final == 0 and len(states) == 28, "closed length-28 word")
    grouped = {quadrant: set() for quadrant in ((0, 0), (1, 0), (0, 1), (1, 1))}
    for state in states:
        quadrant = ((state >> early) & 1, (state >> late) & 1)
        grouped[quadrant].add(project_body(state, labels))
    return grouped


def first_witnesses():
    found = {"I": {}, "II": {}}
    examined = 0
    coverages = []
    minimum_rank = 8
    for early in range(8):
        for late in range(early + 1, 8):
            for early_at in range(20):
                for late_at in range(20):
                    if early_at == late_at:
                        continue
                    examined += 1
                    case = "I" if early_at < late_at else "II"
                    if (early, late) in found[case]:
                        continue
                    sequence = insert(early, late, early_at, late_at)
                    word = tuple(range(8)) + sequence
                    ranks = arc_ranks(word, early) + arc_ranks(word, late)
                    if min(ranks) < 4:
                        continue
                    require(schedule_ok(sequence, early, late), "witness schedule")
                    states, final = prefixes(word)
                    require(final == 0, "witness closure")
                    covered = len(differences(states))
                    require(covered < 256, "insertion witness was universal")
                    grouped = slices_of(word, early, late)
                    if case == "II":
                        require(not grouped[(0, 1)], "case II used quadrant (0,1)")
                        low, middle, high = flag_sets(early, late)
                        require(low <= grouped[(0, 0)], "P00 missed its flag")
                        require(middle <= grouped[(1, 0)], "P10 missed its flag")
                        require(high <= grouped[(1, 1)], "P11 missed its flag")
                        sums = (
                            len({x ^ y for x in grouped[(0, 0)] for y in grouped[(1, 0)]}),
                            len({x ^ y for x in grouped[(0, 0)] for y in grouped[(1, 1)]}),
                            len({x ^ y for x in grouped[(1, 0)] for y in grouped[(1, 1)]}),
                        )
                        require(min(sums) < 64, "a non-universal witness met every sumset")
                    else:
                        require(grouped[(0, 1)], "case I missed quadrant (0,1)")
                    found[case][(early, late)] = sequence
                    coverages.append(covered)
                    minimum_rank = min(minimum_rank, min(ranks))
    require(examined == 10640, "insertion family domain")
    require(len(found["I"]) == 28 and len(found["II"]) == 28, "a label pair missed a case")
    require(minimum_rank == 4, "rank floor of the recorded witnesses")
    require(max(coverages) == 111, "witness coverage marker")
    return found, max(coverages), minimum_rank


def failure_controls(witnesses):
    sample = witnesses["II"][(0, 1)]
    require(schedule_ok(sample, 0, 1), "sample witness")
    require(not schedule_ok((0,) * 20, 0, 1), "constant word passed the schedule check")
    shortened = sample[:-1]
    _states, final = prefixes(tuple(range(8)) + shortened)
    require(final != 0, "deleting the last complement step stayed closed")
    mutated = sample[:-1] + ((sample[-1] + 1) % 8,)
    require(not schedule_ok(mutated, 0, 1), "relabelled last step kept the legal schedule")
    word = gray_block(0) + gray_block(4)
    states, final = prefixes(word)
    require(final == 0 and len(word) == 32, "Gray closure")
    require(len(differences(states)) == 256, "Gray coverage")
    distances = []
    for left in range(32):
        for right in range(left + 1, 32):
            if states[left] ^ states[right] == 255:
                distances.append(min(right - left, 32 - (right - left)))
    require(distances == [16], "Gray all-ones distance")
    broken = (word[0] ^ 1,) + word[1:]
    broken_states, broken_final = prefixes(broken)
    broken_covered = len(differences(broken_states))
    require(broken_final != 0 or broken_covered < 256, "mutated Gray word stayed universal")
    return distances[0]


def cited_inputs():
    floor = (ROOT / "research/eight-source-singleton-floor/README.md").read_text(encoding="utf-8")
    rank = (ROOT / "research/length28-sojourn-rank/README.md").read_text(encoding="utf-8")
    require("28 <= f(8) <= 32" in floor, "cited floor statement")
    require("(4,4,4,4,4,4,2,2)" in floor, "cited multiplicity shape")
    require("at least four other sources" in rank, "cited rank floor")
    require("does not forbid an arc of rank 4" in rank, "cited rank-4 remainder")
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    require(selected["kappa"] == "363005817/100000000000", "selected kappa")


def main():
    distance_parities()
    composition_bound()
    permutations = permutation_census()
    worst = flag_table()
    _witnesses, coverage, minimum_rank = first_witnesses()
    distance = failure_controls(_witnesses)
    cited_inputs()
    print(
        "PASS_LENGTH28_ALLONES_CASE_TWO "
        f"permutations={permutations} flags=28 max_forced_sum={worst} "
        f"case_i=28 case_ii=28 min_rank={minimum_rank} "
        f"witness_coverage_max={coverage} gray_distance={distance}"
    )


if __name__ == "__main__":
    main()
