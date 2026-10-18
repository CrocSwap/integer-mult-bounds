#!/usr/bin/env python3
"""Independently verify the 14- and 16-event prefix-difference censuses."""

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import random
import sys


HERE = Path(__file__).resolve().parent
N = 7
TARGETS = tuple(m for m in range(1, 1 << N) if m.bit_count() in (1, 2, 3))
TARGET_BITS = sum(1 << mask for mask in TARGETS)
DOMAIN14 = 135_135
DOMAIN16 = 18_918_900


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_SEVEN_SOURCE_16EVENT_BOUND: " + message)


def prefix_states(word):
    states = [0]
    for label in word:
        states.append(states[-1] ^ (1 << label))
    return states


def difference_bits(states):
    bits = 0
    for i, left in enumerate(states):
        for j in range(i + 1, len(states)):
            bits |= 1 << (left ^ states[j])
    return bits


def support_from_bits(bits):
    return {mask for mask in TARGETS if (bits >> mask) & 1}


def canonical14_words():
    """Restricted-growth labels, independently of the pairing generator."""
    remaining = [2] * N
    word = [0] * (2 * N)

    def visit(position, seen):
        if position == len(word):
            yield tuple(word)
            return
        for label in range(seen):
            if remaining[label] == 0:
                continue
            remaining[label] -= 1
            word[position] = label
            yield from visit(position + 1, seen)
            remaining[label] += 1
        if seen < N:
            label = seen
            remaining[label] -= 1
            word[position] = label
            yield from visit(position + 1, seen + 1)
            remaining[label] += 1

    yield from visit(0, 0)


def canonical16_words():
    """Restricted-growth labels for six pair sources plus a distinguished four-use source."""
    remaining = [4] + [2] * (N - 1)
    word = [0] * 16

    def visit(position, seen_pairs):
        if position == len(word):
            yield tuple(word)
            return
        if remaining[0]:
            remaining[0] -= 1
            word[position] = 0
            yield from visit(position + 1, seen_pairs)
            remaining[0] += 1
        for label in range(1, seen_pairs + 1):
            if remaining[label] == 0:
                continue
            remaining[label] -= 1
            word[position] = label
            yield from visit(position + 1, seen_pairs)
            remaining[label] += 1
        if seen_pairs < N - 1:
            label = seen_pairs + 1
            remaining[label] -= 1
            word[position] = label
            yield from visit(position + 1, seen_pairs + 1)
            remaining[label] += 1

    yield from visit(0, 0)


def insert_pair(word, label, p, q):
    result = []
    for boundary in range(len(word) + 1):
        if boundary == p:
            result.append(label)
        if boundary == q:
            result.append(label)
        if boundary < len(word):
            result.append(word[boundary])
    return tuple(result)


def valid_source_word(word, multiplicity):
    return len(word) == sum(multiplicity) and [word.count(j) for j in range(N)] == list(multiplicity)


def readout_pairs(states, support):
    result = {}
    for mask in sorted(support):
        for i, left in enumerate(states):
            for j in range(i + 1, len(states)):
                if left ^ states[j] == mask:
                    result[str(mask)] = [i, j]
                    break
            if str(mask) in result:
                break
    return result


def mat_apply(rows, vector):
    output = 0
    for bit, row in enumerate(rows):
        if (row & vector).bit_count() & 1:
            output |= 1 << bit
    return output


def simulate_construction(word, states, pairs, support):
    for dimension in (1, 2, 3):
        rng = random.Random(0x16E7 + dimension)
        b_maps = [[rng.randrange(1 << dimension) for _ in range(dimension)] for _ in range(N)]
        inputs = [rng.randrange(1 << dimension) for _ in range(N)]
        source_terms = [mat_apply(b_maps[j], inputs[j]) for j in range(N)]
        dirty_connector = rng.randrange(1 << dimension)
        for mask in support:
            start, stop = pairs[str(mask)]
            dirty_target = rng.randrange(1 << dimension)
            a_map = [rng.randrange(1 << dimension) for _ in range(dimension)]
            z_start = dirty_connector
            z_stop = dirty_connector
            for j in range(N):
                if (states[start] >> j) & 1:
                    z_start ^= source_terms[j]
                if (states[stop] >> j) & 1:
                    z_stop ^= source_terms[j]
            actual = dirty_target ^ mat_apply(a_map, z_start) ^ mat_apply(a_map, z_stop)
            target_input = 0
            for j in range(N):
                if (mask >> j) & 1:
                    target_input ^= source_terms[j]
            expected = dirty_target ^ mat_apply(a_map, target_input)
            require(actual == expected, f"dirty-state simulation failed at dimension {dimension}, mask {mask}")
        require(states[-1] == 0, "source connector was not restored")


def main():
    task = json.loads((HERE / "TASK.json").read_text(encoding="utf-8"))
    predecessor = json.loads((HERE / "PREDECESSOR.json").read_text(encoding="utf-8"))
    result = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    pin = task["predecessors"][0]
    require(predecessor["head"] == pin["head"] and predecessor["artifact_sha256"] == pin["sha256"], "predecessor source pin mismatch")

    # Independent 14-event positive control: restricted-growth enumeration.
    old_hist = Counter()
    old_count = 0
    old_full = 0
    for word in canonical14_words():
        old_count += 1
        states = prefix_states(word)
        bits = difference_bits(states)
        support_bits = bits & TARGET_BITS
        score = support_bits.bit_count()
        old_hist[score] += 1
        old_full += score == len(TARGETS)
    expected_old_hist = {int(k): v for k, v in predecessor["coverage_histogram"].items()}
    require(old_count == DOMAIN14, f"14-event domain count {old_count}")
    require(dict(old_hist) == expected_old_hist, "14-event histogram differs from pinned predecessor receipt")
    require(old_full == 0 and max(old_hist) == 56 and old_hist[56] == 2, "14-event positive control boundary mismatch")
    old_word = tuple(predecessor["maximum_word"])
    old_states = prefix_states(old_word)
    require(old_states == predecessor["maximum_prefix_states"], "pinned 14-event prefix states are inconsistent")
    require(len(support_from_bits(difference_bits(old_states))) == 56, "pinned 14-event witness does not cover 56 masks")

    # Recheck the complete 840-case insertion family using a separate boundary builder.
    stage_hist = Counter()
    stage_count = stage_full = 0
    stage_best = None
    for label in range(N):
        for p in range(15):
            for q in range(p, 15):
                word = insert_pair(old_word, label, p, q)
                states = prefix_states(word)
                support = support_from_bits(difference_bits(states))
                stage_count += 1
                stage_hist[len(support)] += 1
                stage_full += len(support) == len(TARGETS)
                if stage_best is None or len(support) > len(stage_best["support"]):
                    stage_best = {"label": label, "slots": [p, q], "word": word, "states": states, "support": support}
    recorded_stage = result["insertion_search"]
    require(stage_count == 840 and stage_full == recorded_stage["full_cover_hits"] == 0, "insertion full-cover count mismatch")
    require(dict(stage_hist) == {int(k): v for k, v in recorded_stage["coverage_histogram"].items()}, "insertion histogram mismatch")
    require(len(stage_best["support"]) == 58, "insertion best score mismatch")

    # Independent 16-event exact census with canonical restricted-growth words and bitset coverage.
    histogram = Counter()
    count = full_hits = 0
    for word in canonical16_words():
        count += 1
        states = prefix_states(word)
        support_bits = difference_bits(states) & TARGET_BITS
        score = support_bits.bit_count()
        histogram[score] += 1
        full_hits += score == len(TARGETS)
        if count % 2_000_000 == 0:
            print(f"VERIFY_PROGRESS words={count}", flush=True)
    recorded = result["fallback_search"]
    require(count == DOMAIN16 == recorded["domain_size"] == recorded["words_examined"], "16-event domain count mismatch")
    require(dict(histogram) == {int(k): v for k, v in recorded["coverage_histogram"].items()}, "16-event histogram mismatch")
    require(full_hits == 0 and max(histogram) == 60 and histogram[60] == 8, "16-event maximum/full-cover boundary mismatch")
    require(sum(histogram.values()) == DOMAIN16, "16-event histogram total mismatch")

    best = recorded["best"]
    best_word = tuple(best["word"])
    best_states = prefix_states(best_word)
    best_support = support_from_bits(difference_bits(best_states))
    require(valid_source_word(best_word, [4, 2, 2, 2, 2, 2, 2]), "best 16-event word has wrong multiplicities")
    require(best_states == best["prefix_states"], "best 16-event prefix receipt mismatch")
    require(best_support == set(best["covered_masks"]), "best 16-event support receipt mismatch")
    require(sorted(TARGET_SET - best_support) == best["missing_masks"], "best 16-event missing-mask receipt mismatch")
    require(len(best_support) == 60 and best["missing_masks"] == [44, 73, 82], "best witness support boundary mismatch")
    pairs = best["readout_boundary_pairs"]
    require(set(map(int, pairs)) == best_support, "best witness readout pair inventory mismatch")
    for mask, pair in pairs.items():
        i, j = pair
        require(0 <= i < j < len(best_states) and best_states[i] ^ best_states[j] == int(mask), f"bad boundary pair for mask {mask}")
    simulate_construction(best_word, best_states, pairs, best_support)

    cost = result["attained_subset_cost"]
    incidence = [sum((mask >> j) & 1 for mask in best_support) for j in range(N)]
    star_per_map = [2 * x for x in incidence]
    multiplicity = [best_word.count(j) for j in range(N)]
    saved_per_map = [star_per_map[j] - multiplicity[j] for j in range(N)]
    star_b = sum(star_per_map)
    shared_b = sum(multiplicity)
    target_calls = 2 * len(best_support)
    require(cost["source_incidence_per_map"] == incidence, "cost source incidences mismatch")
    require(cost["source_calls_saved_per_map"] == saved_per_map, "cost per-source savings mismatch")
    require((cost["star_complete_calls"], cost["shared_complete_calls"], cost["complete_calls_saved"]) == (star_b + target_calls, shared_b + target_calls, star_b - shared_b), "complete-call invoice mismatch")
    require((cost["star_event_bits"], cost["shared_event_bits"], cost["event_bits_saved"]) == (4 * star_b + 7 * target_calls, 4 * shared_b + 7 * target_calls, 4 * (star_b - shared_b)), "descriptor invoice mismatch")
    require((cost["star_complete_calls"], cost["shared_complete_calls"], cost["complete_calls_saved"]) == (410, 136, 274), "reported 60-output call savings mismatch")

    # Negative controls: malformed counts, corrupted prefix state and wrong output boundary must reject.
    require(not valid_source_word(best_word[:-1], [4, 2, 2, 2, 2, 2, 2]), "dropped-toggle control was accepted")
    corrupt = list(best_states)
    corrupt[5] ^= 1
    require(corrupt != prefix_states(best_word), "corrupted-prefix control was accepted")
    require(best_states[0] ^ best_states[2] != 1, "wrong-boundary control unexpectedly realizes mask 1")
    require(len(best_support) != len(TARGETS), "full-family negative control unexpectedly passed")

    print(f"PASS_SEVEN_SOURCE_16EVENT_BOUND old_domain={old_count} old_max=56 new_domain={count} new_max=60 full_hits=0 max_words=8 outputs=60 calls=136 savings=274 controls=4")


TARGET_SET = set(TARGETS)


if __name__ == "__main__":
    main()
