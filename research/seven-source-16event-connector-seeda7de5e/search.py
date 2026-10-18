#!/usr/bin/env python3
"""Search one-pair interval extensions, then the normalized 16-event class."""

from collections import Counter
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
N = 7
LENGTH = 16
TARGETS = tuple(m for m in range(1, 1 << N) if m.bit_count() in (1, 2, 3))
TARGET_SET = set(TARGETS)
DOMAIN_SIZE = 18_918_900


def prefixes(word):
    q = [0]
    for label in word:
        q.append(q[-1] ^ (1 << label))
    return q


def differences(q):
    return {q[i] ^ q[j] for i in range(len(q)) for j in range(i + 1, len(q))}


def coverage(q):
    return TARGET_SET.intersection(differences(q))


def readout_pairs(q, masks):
    result = {}
    for mask in sorted(masks, key=lambda m: (m.bit_count(), m)):
        for i in range(len(q)):
            for j in range(i + 1, len(q)):
                if q[i] ^ q[j] == mask:
                    result[str(mask)] = [i, j]
                    break
            if str(mask) in result:
                break
    return result


def insert_pair(word, label, p, q):
    """Insert two label toggles at slots p<=q among 15 original boundaries."""
    out = []
    for slot in range(len(word) + 1):
        if slot == p:
            out.append(label)
            if p == q:
                out.append(label)
        if slot == q and q != p:
            out.append(label)
        if slot < len(word):
            out.append(word[slot])
    return tuple(out)


def insertions(word):
    for label in range(N):
        for p in range(len(word) + 1):
            for q in range(p, len(word) + 1):
                yield label, p, q, insert_pair(word, label, p, q)


def canonical_words():
    """One word per orbit with one four-use label and six pair labels."""
    word = [None] * LENGTH
    for heavy in combinations(range(LENGTH), 4):
        heavy_mask = 0
        for position in heavy:
            word[position] = 0
            heavy_mask |= 1 << position

        def pair_remaining(remaining, next_label):
            if remaining == 0:
                yield tuple(word)
                return
            first_bit = remaining & -remaining
            first = first_bit.bit_length() - 1
            rest = remaining ^ first_bit
            choices = rest
            while choices:
                bit = choices & -choices
                other = bit.bit_length() - 1
                choices ^= bit
                word[first] = word[other] = next_label
                yield from pair_remaining(rest ^ bit, next_label + 1)

        yield from pair_remaining(((1 << LENGTH) - 1) ^ heavy_mask, 1)


def word_record(word, q, masks):
    return {
        "word": list(word),
        "prefix_states": list(q),
        "covered_masks": sorted(masks),
        "missing_masks": sorted(TARGET_SET - set(masks)),
        "readout_boundary_pairs": readout_pairs(q, masks),
    }


def main():
    predecessor = json.loads((HERE / "PREDECESSOR.json").read_text(encoding="utf-8"))
    task = json.loads((HERE / "TASK.json").read_text(encoding="utf-8"))
    expected = task["predecessors"][0]
    if predecessor["head"] != expected["head"] or predecessor["artifact_sha256"] != expected["sha256"]:
        raise SystemExit("predecessor pin mismatch")
    base_word = tuple(predecessor["maximum_word"])
    if prefixes(base_word) != predecessor["maximum_prefix_states"]:
        raise SystemExit("predecessor prefix receipt mismatch")

    insertion_histogram = Counter()
    insertion_best = None
    insertion_cases = 0
    for label, p, q_slot, word in insertions(base_word):
        insertion_cases += 1
        prefix = prefixes(word)
        masks = coverage(prefix)
        insertion_histogram[len(masks)] += 1
        if insertion_best is None or len(masks) > len(insertion_best["covered_masks"]):
            insertion_best = {
                "extra_source": label,
                "slots": [p, q_slot],
                **word_record(word, prefix, masks),
            }
        if masks == TARGET_SET:
            result = {
                "schema_version": 1,
                "result_type": "construction",
                "target_masks": len(TARGETS),
                "target_weights": [1, 2, 3],
                "predecessor": predecessor,
                "insertion_search": {
                    "domain_size": insertion_cases,
                    "full_cover_hits": 1,
                    "coverage_histogram": {str(k): insertion_histogram[k] for k in sorted(insertion_histogram)},
                    "best": insertion_best,
                },
                "fallback_search": {"domain_size": DOMAIN_SIZE, "words_examined": 0, "complete": False},
                "construction": {
                    **word_record(word, prefix, masks),
                    "source_multiplicity": [word.count(j) for j in range(N)],
                    "source_calls": LENGTH,
                    "target_calls": 2 * len(TARGETS),
                    "complete_calls": LENGTH + 2 * len(TARGETS),
                },
            }
            write_result(result)
            print(f"SEVEN_SOURCE_16EVENT_SEARCH insertions={insertion_cases} insertion_hits=1 fallback=not_needed calls=142 masks=63")
            print("word=" + " ".join(map(str, word)))
            return

    if insertion_cases != 840:
        raise SystemExit(f"internal insertion-domain error: {insertion_cases}")

    fallback_histogram = Counter()
    fallback_best = None
    fallback_examined = 0
    for word in canonical_words():
        fallback_examined += 1
        prefix = prefixes(word)
        masks = coverage(prefix)
        fallback_histogram[len(masks)] += 1
        if fallback_best is None or len(masks) > len(fallback_best["covered_masks"]):
            fallback_best = word_record(word, prefix, masks)
        if masks == TARGET_SET:
            result = {
                "schema_version": 1,
                "result_type": "construction",
                "target_masks": len(TARGETS),
                "target_weights": [1, 2, 3],
                "predecessor": predecessor,
                "insertion_search": {
                    "domain_size": insertion_cases,
                    "full_cover_hits": 0,
                    "coverage_histogram": {str(k): insertion_histogram[k] for k in sorted(insertion_histogram)},
                    "best": insertion_best,
                },
                "fallback_search": {
                    "domain_size": DOMAIN_SIZE,
                    "words_examined": fallback_examined,
                    "complete": False,
                    "coverage_histogram_prefix": {str(k): fallback_histogram[k] for k in sorted(fallback_histogram)},
                },
                "construction": {
                    **word_record(word, prefix, masks),
                    "source_multiplicity": [word.count(j) for j in range(N)],
                    "source_calls": LENGTH,
                    "target_calls": 2 * len(TARGETS),
                    "complete_calls": LENGTH + 2 * len(TARGETS),
                },
            }
            write_result(result)
            print(f"SEVEN_SOURCE_16EVENT_SEARCH insertions=840 insertion_hits=0 fallback_examined={fallback_examined} fallback_complete=false calls=142 masks=63")
            print("word=" + " ".join(map(str, word)))
            return

    if fallback_examined != DOMAIN_SIZE:
        raise SystemExit(f"internal fallback-domain error: {fallback_examined}")
    result = {
        "schema_version": 1,
        "result_type": "scoped_negative",
        "target_masks": len(TARGETS),
        "target_weights": [1, 2, 3],
        "predecessor": predecessor,
        "insertion_search": {
            "domain_size": insertion_cases,
            "full_cover_hits": 0,
            "coverage_histogram": {str(k): insertion_histogram[k] for k in sorted(insertion_histogram)},
            "best": insertion_best,
        },
        "fallback_search": {
            "domain_size": DOMAIN_SIZE,
            "words_examined": fallback_examined,
            "complete": True,
            "coverage_histogram": {str(k): fallback_histogram[k] for k in sorted(fallback_histogram)},
            "best": fallback_best,
        },
    }
    write_result(result)
    print(f"SEVEN_SOURCE_16EVENT_SEARCH insertions=840 insertion_hits=0 fallback_examined={fallback_examined} fallback_complete=true full_cover=0 best={len(fallback_best['covered_masks'])}")


def write_result(result):
    best = result.get("fallback_search", {}).get("best")
    if best is not None:
        support = best["covered_masks"]
        incidence = [sum((mask >> j) & 1 for mask in support) for j in range(N)]
        multiplicity = [best["word"].count(j) for j in range(N)]
        star_source_calls = [2 * value for value in incidence]
        saved_by_source = [star_source_calls[j] - multiplicity[j] for j in range(N)]
        star_b = sum(star_source_calls)
        shared_b = sum(multiplicity)
        target_calls = 2 * len(support)
        result["attained_subset_cost"] = {
            "support_size": len(support),
            "support_weight_counts": {
                str(w): sum(mask.bit_count() == w for mask in support)
                for w in (1, 2, 3)
            },
            "source_incidence_per_map": incidence,
            "source_multiplicity": multiplicity,
            "star_source_calls_per_map": star_source_calls,
            "source_calls_saved_per_map": saved_by_source,
            "star_source_calls": star_b,
            "shared_source_calls": shared_b,
            "target_calls_each_program": target_calls,
            "star_complete_calls": star_b + target_calls,
            "shared_complete_calls": shared_b + target_calls,
            "complete_calls_saved": star_b - shared_b,
            "star_event_bits": 4 * star_b + 7 * target_calls,
            "shared_event_bits": 4 * shared_b + 7 * target_calls,
            "event_bits_saved": 4 * (star_b - shared_b),
            "root_dispatches_saved": star_b - shared_b,
            "invoice_difference": "-sum_j source_calls_saved_per_map[j]*c(B_j) - event_bits_saved*lambda - root_dispatches_saved*delta",
            "charges": "Every complete B and A call is paid, including source/target access, arithmetic, writes, hosting, private scratch restoration and head return. Shared input admission and coefficient preparation cancel. The static event order encodes map identifiers and boundaries.",
        }

    if result.get("result_type") == "scoped_negative":
        result["whole_batch_142_call_analysis"] = {
            "scope": "Original one-root F2 source-toggle and single-target A-map event alphabet; arbitrary dirty source and target rows.",
            "per_map_call_parity": "Each active B_j and each required A_M must be called an even positive number of times, because its independent dirty/source contribution must cancel.",
            "minimum_profile": {"source_calls": 14, "target_calls": 126, "total": 140},
            "excluded_140_profile": "The 14-toggle all-two-source class has maximum prefix-difference coverage 56 of 63, so the all-targets-twice floor is impossible.",
            "142_call_splits": [
                {
                    "source_calls": 16,
                    "target_calls": 126,
                    "profile": [4, 2, 2, 2, 2, 2, 2],
                    "excluded_by": "The complete 18,918,900-word census in this package has no full 63-mask cover; its maximum is 60."
                },
                {
                    "source_calls": 14,
                    "target_calls": 128,
                    "profile": "all seven B maps twice; one A_M four times and the other 62 A maps twice",
                    "excluded_by": "The 14-toggle census supports at most 56 masks by pairs, leaving at least seven unsupported. A single four-call A_M can serve at most one target, so at least six targets still lack a pair of prefix boundaries."
                }
            ],
            "conclusion": "No full 63-mask schedule uses 140 or 142 complete map calls in this event alphabet. All call totals are even, hence any such full batch needs at least 144 complete map calls. No 144-call schedule is constructed or excluded here."
        }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
