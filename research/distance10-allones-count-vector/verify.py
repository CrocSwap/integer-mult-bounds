#!/usr/bin/env python3
"""Corroborate the distance-10 all-ones short-arc count vector.

The argument is in README.md. These checks are exhaustive on the finite
domains named there: positive odd 8-tuples that can sum to 10, the 224
multiplicity alignments, the 120 normal-form arcs, and all 4,838,400
length-10 words of count type (3, 1^7). They do not search for a universal
word and they do not classify distances 12 or 14.
"""

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHORT = (3, 1, 1, 1, 1, 1, 1, 1)
COMPLEMENT = (3, 3, 3, 3, 3, 1, 1, 1)
KAPPA = "363005817/100000000000"
WITNESS_ARC = (0, 0, 0, 1, 2, 3, 4, 5, 6, 7)
WITNESS_COMPLEMENT = (0, 1, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7)
WITNESS_DIFFERENCES = 58


def require(condition, message):
    if not condition:
        raise ValueError(message)


def walk(word):
    state = 0
    states = [0]
    for label in word:
        require(0 <= label <= 7, "label outside the eight sources")
        state ^= 1 << label
        states.append(state)
    return tuple(states)


def counts_of(word):
    counts = [0] * 8
    for label in word:
        require(0 <= label <= 7, "label outside the eight sources")
        counts[label] += 1
    return tuple(counts)


def normal_word(positions):
    chosen = set(positions)
    require(len(chosen) == 3, "a normal form has three positions for source 0")
    word = []
    singleton = 1
    for index in range(10):
        if index in chosen:
            word.append(0)
        else:
            word.append(singleton)
            singleton += 1
    require(singleton == 8, "normal form missed a singleton source")
    return tuple(word)


def appearance_normal_form(word):
    counts = counts_of(word)
    if counts.count(3) != 1 or any(count not in (1, 3) for count in counts):
        raise ValueError("word is outside the distance-10 count type")
    triple = counts.index(3)
    mapping = {triple: 0}
    nxt = 1
    normalized = []
    for label in word:
        if label not in mapping:
            mapping[label] = nxt
            nxt += 1
        normalized.append(mapping[label])
    require(nxt == 8, "appearance order missed a source")
    return tuple(normalized)


def sorted_excess_shapes(excess):
    shapes = set()

    def rec(remaining, left, prefix):
        if left == 1:
            shapes.add(tuple(sorted(prefix + (remaining,), reverse=True)))
            return
        for value in range(remaining + 1):
            rec(remaining - value, left - 1, prefix + (value,))

    rec(excess, 8, ())
    return shapes


def odd_tuples_summing_to(total):
    found = set()
    for choice in itertools.product((1, 3, 5), repeat=8):
        if sum(choice) == total:
            found.add(tuple(sorted(choice, reverse=True)))
    return found


def turns_off_after_on(states):
    seen_on = False
    for state in states:
        if state & 1:
            seen_on = True
        elif seen_on:
            return True
    return False


def difference_count(states):
    return len({left ^ right for left in states for right in states})


def inherited_records():
    selected = json.loads(
        (ROOT / "certificates/selected-result.json").read_text(encoding="utf-8")
    )
    require(selected["kappa"] == KAPPA, "selected kappa moved")
    require(selected["decimal"] == "0.00363005817", "selected decimal moved")
    require(selected["previous_kappa"] == "781451/250000000", "previous record moved")
    floor = (ROOT / "research/eight-source-singleton-floor/README.md").read_text(
        encoding="utf-8"
    )
    require("28 <= f(8) <= 32" in floor, "inherited gap text missing")
    require(
        "exactly six equal four and two\nequal two." in floor,
        "inherited multiplicity sentence missing",
    )


def count_vector_census():
    excess_one = sorted_excess_shapes(1)
    require(excess_one == {(1, 0, 0, 0, 0, 0, 0, 0)}, "excess 1 is not unique")
    require(sorted_excess_shapes(0) == {(0, 0, 0, 0, 0, 0, 0, 0)}, "excess 0 drifted")
    require(len(sorted_excess_shapes(2)) > 1, "excess-1 uniqueness used a bad enumerator")
    counts = tuple(1 + 2 * value for value in (1, 0, 0, 0, 0, 0, 0, 0))
    require(tuple(sorted(counts, reverse=True)) == SHORT, "excess 1 missed the short vector")
    # Any positive odd entry of 7 or more already sums past 10 with seven 1s,
    # so every candidate tuple has entries in {1, 3, 5}. An entry of 5 does too.
    require(7 + 7 * 1 == 14 and 14 > 10, "seven-count lower bound")
    require(5 + 7 * 1 == 12 and 12 > 10, "five-count lower bound")
    require(odd_tuples_summing_to(10) == {SHORT}, "odd-tuple census drifted")
    require(sum(SHORT) == 10 and SHORT.count(3) == 1 and SHORT.count(1) == 7, "short vector")


def role_census():
    legal = 0
    illegal = 0
    for doubles in itertools.combinations(range(8), 2):
        for triple in range(8):
            total = [4] * 8
            total[doubles[0]] = 2
            total[doubles[1]] = 2
            short = [1] * 8
            short[triple] = 3
            if triple in doubles:
                require(total[triple] - short[triple] < 0, "a double cannot host three visits")
                illegal += 1
                continue
            complement = tuple(total[source] - short[source] for source in range(8))
            require(tuple(sorted(complement, reverse=True)) == COMPLEMENT, "complement vector")
            require(complement[triple] == 1, "repeated quadruple keeps one complement visit")
            require(all(count % 2 == 1 and count > 0 for count in complement), "complement parity")
            ons = sum(count // 2 for count in complement)
            require(ons == 5, "complement on-steps")
            legal += 1
    require(legal == 28 * 6 and illegal == 28 * 2, "role domain")
    require(sum(COMPLEMENT) == 18, "complement length")
    ons, offs = 5, 13
    require(ons + offs == 18 and 8 + ons - offs == 0, "weight identity")


def normal_form_census():
    forms = {}
    for positions in itertools.combinations(range(10), 3):
        word = normal_word(positions)
        states = walk(word)
        require(states[-1] == 255, "normal form missed all-ones")
        require(counts_of(word) == (3, 1, 1, 1, 1, 1, 1, 1), "normal form counts")
        require(word == appearance_normal_form(word), "normal form is not idempotent")
        require(turns_off_after_on(states), "source 0 stayed monotone")
        require((states[-1] & 1) == 1, "source 0 did not finish on")
        forms[positions] = word
    require(len(forms) == 120, "normal-form domain")
    require(len(set(forms.values())) == 120, "normal forms collided")
    hits = {positions: 0 for positions in forms}
    checked = 0
    for triple in range(8):
        labels = [source for source in range(8) if source != triple]
        for positions in forms:
            slots = [index for index in range(10) if index not in positions]
            for perm in itertools.permutations(labels):
                word = [0] * 10
                for index in positions:
                    word[index] = triple
                for index, label in zip(slots, perm):
                    word[index] = label
                require(
                    appearance_normal_form(word) == forms[positions],
                    "relabeling left its normal form",
                )
                hits[positions] += 1
                checked += 1
    require(checked == 120 * 40320 == 8 * 120 * 5040, "normalization domain")
    require(all(count == 40320 for count in hits.values()), "orbit size")
    return forms


def distance_eight_contrast():
    word = tuple(range(8))
    states = walk(word)
    require(states == tuple((1 << bit) - 1 for bit in range(9)), "identity chain")
    for bit in range(8):
        seen_on = False
        for state in states:
            on = (state >> bit) & 1
            if seen_on:
                require(on == 1, "identity chain turned a bit off")
            seen_on = seen_on or on == 1
    require(counts_of(word) == (1, 1, 1, 1, 1, 1, 1, 1), "distance 8 is not distance 10")
    try:
        appearance_normal_form(word)
    except ValueError:
        return
    raise ValueError("distance-8 identity was accepted as a distance-10 word")


def witness_and_mutations(forms):
    require(forms[(0, 1, 2)] == WITNESS_ARC, "worked arc drifted")
    states = walk(WITNESS_ARC)
    require(
        states == (0, 1, 0, 1, 3, 7, 15, 31, 63, 127, 255),
        "worked prefixes drifted",
    )
    require(states[1] & 1 == 1 and states[2] & 1 == 0, "worked bit 0 did not turn off")
    full = WITNESS_ARC + WITNESS_COMPLEMENT
    require(len(full) == 28, "witness length")
    totals = counts_of(full)
    require(tuple(sorted(totals, reverse=True)) == (4, 4, 4, 4, 4, 4, 2, 2), "witness shape")
    require(totals[0] == 4 and totals[1] == 2 and totals[2] == 2, "witness roles")
    full_states = walk(full)
    require(full_states[10] == 255 and full_states[-1] == 0, "witness endpoints")
    require(
        difference_count(full_states[:-1]) == WITNESS_DIFFERENCES,
        "witness difference count",
    )
    require(WITNESS_DIFFERENCES < 256, "witness was marked universal")
    swapped = (0, 0, 0, 2, 1, 3, 4, 5, 6, 7)
    require(appearance_normal_form(swapped) == WITNESS_ARC, "label swap did not renormalize")
    broken = WITNESS_ARC + WITNESS_COMPLEMENT[:-1] + (1,)
    require(walk(broken)[-1] != 0, "odd mutation closed")
    try:
        appearance_normal_form((0, 0, 0, 0, 1, 2, 3, 4, 5, 6))
    except ValueError:
        return
    raise ValueError("a four-visit arc was accepted")


def main():
    inherited_records()
    count_vector_census()
    role_census()
    forms = normal_form_census()
    distance_eight_contrast()
    witness_and_mutations(forms)
    require(len(list(itertools.combinations(range(7), 2))) == 21, "double-label index")
    print(
        "PASS_DISTANCE10_ALLONES_COUNT_VECTOR"
        " short=(3,1,1,1,1,1,1,1)"
        " complement=(3,3,3,3,3,1,1,1)"
        " normal_forms=120"
        " double_pairs=21"
        " index=2520"
        " classes=4838400"
        " witness_differences=58"
        " kappa=363005817/100000000000"
    )


if __name__ == "__main__":
    main()
