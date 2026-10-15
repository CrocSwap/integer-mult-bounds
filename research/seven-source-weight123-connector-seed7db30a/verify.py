#!/usr/bin/env python3
"""Independent exact replay and dirty-state controls for the seven-source result."""

import json
from pathlib import Path
import random


N = 7
ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def target_masks():
    return tuple(mask for mask in range(1, 1 << N) if mask.bit_count() <= 3)


def canonical_words():
    """Generate restricted-growth double-occurrence words, independently of pairings."""
    counts = [0] * N
    word = []

    def visit(next_label):
        if len(word) == 2 * N:
            if next_label == N:
                yield tuple(word)
            return
        for label in range(next_label):
            if counts[label] == 1:
                counts[label] = 2
                word.append(label)
                yield from visit(next_label)
                word.pop()
                counts[label] = 1
        if next_label < N:
            counts[next_label] = 1
            word.append(next_label)
            yield from visit(next_label + 1)
            word.pop()
            counts[next_label] = 0

    yield from visit(0)


def prefix_states(word):
    q = [0]
    for label in word:
        q.append(q[-1] ^ (1 << label))
    return tuple(q)


def difference_set(q):
    return {q[i] ^ q[j] for i in range(len(q)) for j in range(i + 1, len(q))}


def first_pair_for(q, mask):
    for left in range(len(q)):
        for right in range(left + 1, len(q)):
            if q[left] ^ q[right] == mask:
                return [left, right]
    return None


def matvec(rows, vector):
    result = 0
    for i, row in enumerate(rows):
        if (row & vector).bit_count() & 1:
            result |= 1 << i
    return result


def random_matrix(rng, width):
    return tuple(rng.randrange(1 << width) for _ in range(width))


def run_word(word, pairs, masks, source_maps, output_maps, sources, initial_outputs, z0,
             drop_late_readout=None):
    """Run the literal event schedule: reads at boundaries, then the next B toggle."""
    at_boundary = [[] for _ in range(len(word) + 1)]
    for mask in masks:
        left, right = pairs[str(mask)]
        at_boundary[left].append(mask)
        at_boundary[right].append(mask)
    z = z0
    outputs = dict(initial_outputs)
    for boundary in range(len(word) + 1):
        for mask in at_boundary[boundary]:
            if drop_late_readout == (mask, boundary):
                continue
            outputs[mask] ^= matvec(output_maps[mask], z)
        if boundary < len(word):
            source = word[boundary]
            z ^= matvec(source_maps[source], sources[source])
    return z, outputs


def expected_outputs(masks, source_maps, output_maps, sources, initial_outputs):
    expected = dict(initial_outputs)
    for mask in masks:
        source_sum = 0
        for source in range(N):
            if (mask >> source) & 1:
                source_sum ^= matvec(source_maps[source], sources[source])
        expected[mask] ^= matvec(output_maps[mask], source_sum)
    return expected


def main():
    result = json.loads((ROOT / "RESULT.json").read_text(encoding="utf-8"))
    wanted = target_masks()
    need(len(wanted) == 63, "target family must contain 63 masks")

    histogram = {}
    total = full = best = 0
    for word in canonical_words():
        total += 1
        score = len(set(wanted) & difference_set(prefix_states(word)))
        histogram[score] = histogram.get(score, 0) + 1
        if score > best:
            best = score
        if score == len(wanted):
            full += 1

    need(total == 135135, "independent restricted-growth census is incomplete")
    need(result.get("canonical_pairings_enumerated") == total, "pairing count mismatch")
    need(result.get("full_cover_paths") == full == 0, "full-cover count mismatch")
    need(result.get("maximum_target_coverage") == best == 56, "maximum coverage mismatch")
    need(result.get("coverage_histogram") == {str(k): histogram[k] for k in sorted(histogram)},
         "coverage histogram mismatch")

    word = tuple(result["maximum_word"])
    q = prefix_states(word)
    counts = [word.count(i) for i in range(N)]
    need(len(word) == 14 and counts == [2] * N, "maximum witness is not a 14-toggle word")
    need(list(q) == result["maximum_prefix_states"], "witness prefix states mismatch")
    cover = set(wanted) & difference_set(q)
    missing = set(wanted) - cover
    need(len(cover) == 56, "witness does not attain the enumerated maximum")
    need(sorted(cover) == result["maximum_covered_masks"], "witness covered-mask receipt mismatch")
    need(sorted(missing) == result["maximum_missing_masks"], "witness missing-mask receipt mismatch")
    need(len(missing) == 7, "expected seven missing weight-three masks")
    need(all(mask.bit_count() == 3 for mask in missing), "a singleton or pair mask is missing")
    pairs = result["maximum_readout_pairs"]
    need(set(map(int, pairs)) == cover, "readout table is not exactly the witnessed support")
    for mask in cover:
        endpoints = pairs[str(mask)]
        need(len(endpoints) == 2 and endpoints[0] < endpoints[1], "invalid readout endpoints")
        need(q[endpoints[0]] ^ q[endpoints[1]] == mask, "wrong readout difference")

    incidences = [sum((mask >> j) & 1 for mask in cover) for j in range(N)]
    weight_counts = {
        str(k): sum(mask.bit_count() == k for mask in cover)
        for k in (1, 2, 3)
    }
    subset_cost = {
        "weight_counts": weight_counts,
        "source_incidence_per_map": incidences,
        "star_source_calls": 2 * sum(incidences),
        "shared_source_calls": 2 * N,
        "target_calls": 2 * len(cover),
        "star_total_calls": 2 * sum(incidences) + 2 * len(cover),
        "shared_total_calls": 2 * N + 2 * len(cover),
        "source_calls_saved": 2 * sum(incidences) - 2 * N,
        "star_instruction_bits": 4 * 2 * sum(incidences) + 7 * 2 * len(cover),
        "shared_instruction_bits": 4 * 2 * N + 7 * 2 * len(cover),
    }
    need(result.get("attained_subset_cost") == subset_cost, "attained subset invoice mismatch")
    full_incidence = sum(mask.bit_count() for mask in wanted)
    full_screen = {
        "source_incidence": full_incidence,
        "star_source_calls": 2 * full_incidence,
        "hypothetical_shared_source_calls": 2 * N,
        "target_calls": 2 * len(wanted),
        "star_total_calls": 2 * full_incidence + 2 * len(wanted),
        "hypothetical_shared_total_calls": 2 * N + 2 * len(wanted),
        "source_calls_savings_if_cover_existed": 2 * full_incidence - 2 * N,
        "star_instruction_bits": 4 * 2 * full_incidence + 7 * 2 * len(wanted),
        "hypothetical_shared_instruction_bits": 4 * 2 * N + 7 * 2 * len(wanted),
        "attained": False,
    }
    need(result.get("full_family_cost_screen") == full_screen,
         "full-family optimistic cost screen mismatch")

    # Dirty-state replay on arbitrary small F2-linear maps and inputs.
    rng = random.Random(0x7DB30A45)
    masks = tuple(sorted(cover))
    for width in (1, 2, 3):
        for _ in range(4):
            source_maps = [random_matrix(rng, width) for _ in range(N)]
            output_maps = {mask: random_matrix(rng, width) for mask in masks}
            sources = [rng.randrange(1 << width) for _ in range(N)]
            initial_outputs = {mask: rng.randrange(1 << width) for mask in masks}
            z0 = rng.randrange(1 << width)
            expected = expected_outputs(masks, source_maps, output_maps, sources,
                                        initial_outputs)
            z, outputs = run_word(word, pairs, masks, source_maps, output_maps, sources,
                                  initial_outputs, z0)
            need(z == z0, "source word failed to restore arbitrary dirty connector")
            need(outputs == expected, "dirty-state output identity failed")

    # Negative control 1: delete one source toggle; a dirty connector residue remains.
    mutated_word = list(word)
    mutated_word.remove(0)
    identity = (1,)
    residue = 0
    for source in mutated_word:
        if source == 0:
            residue ^= 1  # B_0 x_0, with B_0=I and x_0=1.
    need(residue != 0, "deleted-source-toggle control did not detect lost restoration")

    # Negative control 2: delete the later readout for singleton mask 1.
    source_maps = [identity] + [(0,)] * (N - 1)
    output_maps = {mask: identity for mask in masks}
    sources = [0] * N
    initial_outputs = {mask: 0 for mask in masks}
    z, outputs = run_word(word, pairs, masks, source_maps, output_maps, sources,
                          initial_outputs, 1, drop_late_readout=(1, pairs["1"][1]))
    need(z == 1 and outputs[1] != 0,
         "deleted-readout control did not expose dirty connector leakage")

    # Negative control 3: replace the singleton endpoint pair by two equal boundaries.
    bad_pairs = dict(pairs)
    bad_pairs["1"] = [pairs["1"][0], pairs["1"][0]]
    sources = [1] + [0] * (N - 1)
    initial_outputs = {mask: 0 for mask in masks}
    expected = expected_outputs(masks, source_maps, output_maps, sources, initial_outputs)
    _, bad_outputs = run_word(word, bad_pairs, masks, source_maps, output_maps, sources,
                              initial_outputs, 0)
    need(bad_outputs != expected, "wrong-endpoint control did not detect an omitted mask")

    print(
        "PASS_SEVEN_SOURCE_WEIGHT123_PAIRING_BOUND "
        f"pairings={total} max={best} full_hits={full} "
        f"subset_calls={subset_cost['shared_total_calls']} controls=3"
    )


if __name__ == "__main__":
    main()
