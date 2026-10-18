#!/usr/bin/env python3
"""Exhaust the seven-source, two-occurrence prefix paths for masks of weight <= 3."""

from collections import Counter
import json
from pathlib import Path


N = 7
PATH = Path(__file__).resolve().parent


def targets():
    return tuple(
        mask
        for mask in range(1, 1 << N)
        if mask.bit_count() <= 3
    )


def pairings(mask=0, pairs=()):
    """Each perfect matching of positions 0..13 appears exactly once."""
    if len(pairs) == N:
        yield pairs
        return
    first = next(i for i in range(2 * N) if not (mask >> i) & 1)
    for other in range(first + 1, 2 * N):
        if (mask >> other) & 1:
            continue
        yield from pairings(
            mask | (1 << first) | (1 << other),
            pairs + ((first, other),),
        )


def word_from_pairs(pairs):
    word = [None] * (2 * N)
    for label, (first, second) in enumerate(pairs):
        word[first] = label
        word[second] = label
    return tuple(word)


def prefixes(word):
    result = [0]
    for label in word:
        result.append(result[-1] ^ (1 << label))
    return tuple(result)


def differences(q):
    return {q[i] ^ q[j] for i in range(len(q)) for j in range(i + 1, len(q))}


def first_readout_pairs(q, wanted):
    result = {}
    for mask in sorted(wanted, key=lambda x: (x.bit_count(), x)):
        for i in range(len(q)):
            for j in range(i + 1, len(q)):
                if q[i] ^ q[j] == mask:
                    result[str(mask)] = [i, j]
                    break
            if str(mask) in result:
                break
    return result


def main():
    wanted = set(targets())
    histogram = Counter()
    total = hits = 0
    best = -1
    witness = None
    best_witness = None
    for pairs in pairings():
        total += 1
        word = word_from_pairs(pairs)
        q = prefixes(word)
        cover = differences(q)
        score = len(wanted & cover)
        histogram[score] += 1
        if score > best:
            best = score
            best_witness = (word, q, cover)
        if score == len(wanted):
            hits += 1
            if witness is None:
                witness = (word, q)

    record = {
        "schema_version": 1,
        "sources": N,
        "source_calls": 2 * N,
        "target_mask_weights": [1, 2, 3],
        "target_masks": len(wanted),
        "canonical_pairings_enumerated": total,
        "full_cover_paths": hits,
        "maximum_target_coverage": best,
        "coverage_histogram": {str(k): histogram[k] for k in sorted(histogram)},
    }
    if best_witness is not None:
        word, q, cover = best_witness
        support = sorted(wanted & cover)
        source_incidence = [sum((mask >> j) & 1 for mask in support) for j in range(N)]
        weight_counts = {
            str(k): sum(mask.bit_count() == k for mask in support)
            for k in (1, 2, 3)
        }
        record["maximum_word"] = list(word)
        record["maximum_prefix_states"] = list(q)
        record["maximum_covered_masks"] = support
        record["maximum_missing_masks"] = sorted(wanted - cover)
        record["maximum_readout_pairs"] = first_readout_pairs(q, support)
        record["attained_subset_cost"] = {
            "weight_counts": weight_counts,
            "source_incidence_per_map": source_incidence,
            "star_source_calls": 2 * sum(source_incidence),
            "shared_source_calls": 2 * N,
            "target_calls": 2 * len(support),
            "star_total_calls": 2 * sum(source_incidence) + 2 * len(support),
            "shared_total_calls": 2 * N + 2 * len(support),
            "source_calls_saved": 2 * sum(source_incidence) - 2 * N,
            "star_instruction_bits": 4 * 2 * sum(source_incidence) + 7 * 2 * len(support),
            "shared_instruction_bits": 4 * 2 * N + 7 * 2 * len(support),
        }
    full_incidences = sum(mask.bit_count() for mask in wanted)
    record["full_family_cost_screen"] = {
        "source_incidence": full_incidences,
        "star_source_calls": 2 * full_incidences,
        "hypothetical_shared_source_calls": 2 * N,
        "target_calls": 2 * len(wanted),
        "star_total_calls": 2 * full_incidences + 2 * len(wanted),
        "hypothetical_shared_total_calls": 2 * N + 2 * len(wanted),
        "source_calls_savings_if_cover_existed": 2 * full_incidences - 2 * N,
        "star_instruction_bits": 4 * 2 * full_incidences + 7 * 2 * len(wanted),
        "hypothetical_shared_instruction_bits": 4 * 2 * N + 7 * 2 * len(wanted),
        "attained": False,
    }
    if witness is not None:
        word, q = witness
        record["witness_word"] = list(word)
        record["prefix_states"] = list(q)
        record["readout_pairs"] = first_readout_pairs(q, wanted)
    (PATH / "RESULT.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "SEVEN_SOURCE_WEIGHT123_SEARCH "
        f"pairings={total} targets={len(wanted)} hits={hits} best={best}"
    )
    if witness is not None:
        print("word=" + " ".join(str(x) for x in witness[0]))
        print("prefixes=" + " ".join(str(x) for x in witness[1]))
    if best_witness is not None:
        print("maximum_word=" + " ".join(str(x) for x in best_witness[0]))
        print("maximum_missing=" + " ".join(str(x) for x in sorted(wanted - best_witness[2])))


if __name__ == "__main__":
    main()
