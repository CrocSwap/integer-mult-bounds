#!/usr/bin/env python3
"""Exhaust the six-label, one-TRIO, thirteen-singleton closed-path class."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
N = 13
PROFILES = {(1, 2, 2, 2, 3, 3), (1, 1, 2, 2, 2, 5)}


def differences(prefixes):
    result = 0
    for i, left in enumerate(prefixes):
        for right in prefixes[i + 1:]:
            result |= 1 << (left ^ right)
    return result & ~1


def analyze_word(word):
    if len(word) != N or any(type(x) is not int or not 0 <= x < 6 for x in word):
        raise ValueError("word must contain thirteen labels from 0..5")
    seen = set()
    next_label = 0
    counts = [0] * 6
    prefixes = [0]
    state = 0
    for label in word:
        if label > next_label or (label == next_label and next_label >= 6):
            raise ValueError("word is not a restricted-growth string")
        if label == next_label:
            next_label += 1
        seen.add(label)
        counts[label] += 1
        state ^= 1 << label
        prefixes.append(state)
    if len(seen) != 6 or tuple(sorted(counts)) not in PROFILES:
        raise ValueError("word is outside the two charged source-map profiles")
    trio = state
    if trio.bit_count() != 3:
        raise ValueError("closing TRIO must toggle exactly three odd-count labels")
    return counts, trio, prefixes, differences(prefixes)


def four_readout_representations(prefixes, target):
    # Return lexicographically first four distinct boundary indices whose
    # prefix values XOR to target. The path certificate has distinct states.
    for a in range(len(prefixes)):
        for b in range(a + 1, len(prefixes)):
            for c in range(b + 1, len(prefixes)):
                for d in range(c + 1, len(prefixes)):
                    if prefixes[a] ^ prefixes[b] ^ prefixes[c] ^ prefixes[d] == target:
                        return [a, b, c, d]
    return None


def singleton_positive_control():
    # The incumbent six-source word from universal-connector-six-source.
    word = [0, 1, 0, 2, 0, 1, 0, 2, 3, 4, 3, 5, 3, 4, 3, 5]
    prefixes = [0]
    state = 0
    for label in word:
        state ^= 1 << label
        prefixes.append(state)
    if state != 0 or differences(prefixes) != (1 << 64) - 2:
        raise ValueError("positive control failed to cover all 63 nonzero masks")
    return word, prefixes


def enumerate_class():
    histogram = Counter()
    nodes = complete = eligible = 0
    record_hash = hashlib.sha256()
    best_size = -1
    best_word = best_prefixes = best_counts = best_trio = None
    counts = [0] * 6
    word = [0] * N
    prefixes = [0]

    def visit(depth, used, cover):
        nonlocal nodes, complete, eligible
        nonlocal best_size, best_word, best_prefixes, best_counts, best_trio
        nodes += 1
        if depth == N:
            if used != 6:
                return
            complete += 1
            profile = tuple(sorted(counts))
            if profile not in PROFILES:
                return
            eligible += 1
            size = (cover & ~1).bit_count()
            histogram[size] += 1
            # Fixed-width records make the full exact census auditable.
            record_hash.update(bytes(word))
            record_hash.update(cover.to_bytes(8, "big"))
            if size > best_size:
                best_size = size
                best_word = word.copy()
                best_prefixes = prefixes.copy()
                best_counts = counts.copy()
                best_trio = prefixes[-1]
            return

        for label in range(min(used + 1, 6)):
            word[depth] = label
            counts[label] += 1
            new_state = prefixes[-1] ^ (1 << label)
            new_cover = cover
            for old_state in prefixes:
                new_cover |= 1 << (new_state ^ old_state)
            prefixes.append(new_state)
            visit(depth + 1, max(used, label + 1), new_cover)
            prefixes.pop()
            counts[label] -= 1

    visit(0, 0, 0)
    if sum(histogram.values()) != eligible or best_size != max(histogram):
        raise ValueError("internal enumeration accounting failure")
    covered = differences(best_prefixes)
    missing = [mask for mask in range(1, 64) if not (covered >> mask & 1)]
    reps = {str(mask): four_readout_representations(best_prefixes, mask) for mask in missing}
    singleton_word, singleton_prefixes = singleton_positive_control()
    return {
        "schema": "six-source-single-trio-path-census-v1",
        "domain": {
            "sources": 6,
            "singleton_calls": 13,
            "trio_calls": 1,
            "trio_position": "last, by commuting source updates",
            "canonicalization": "restricted-growth strings over six labels",
            "allowed_sorted_singleton_count_profiles": [list(x) for x in sorted(PROFILES)],
            "prefixes_tested": "p0 through p13; p14=p0 after closing TRIO",
            "coverage_rule": "pairwise XOR differences of p0..p13",
            "repeated_prefixes_allowed": True,
        },
        "enumeration": {
            "rgs_nodes_including_root": nodes,
            "complete_six_label_words": complete,
            "words_in_allowed_profiles": eligible,
            "records_sha256": record_hash.hexdigest(),
            "histogram_nonzero_pair_masks": {str(k): histogram[k] for k in sorted(histogram)},
            "maximum_coverage": best_size,
            "number_at_maximum": histogram[best_size],
        },
        "maximum_witness": {
            "singleton_word": best_word,
            "singleton_counts": best_counts,
            "closing_trio_mask": best_trio,
            "total_source_map_counts": [best_counts[j] + ((best_trio >> j) & 1) for j in range(6)],
            "prefixes": best_prefixes,
            "covered_nonzero_masks": best_size,
            "missing_masks": missing,
            "four_readout_indices_for_missing_masks": reps,
        },
        "positive_control": {
            "incumbent_singleton_word": singleton_word,
            "prefixes": singleton_prefixes,
            "nonzero_masks_covered": 63,
            "root_calls": 142,
        },
        "cost": {
            "incumbent": {"source_map_applications": 16, "source_calls": 16, "output_readouts": 126, "root_calls": 142},
            "best_one_trio_with_four_readout_repairs": {"source_map_applications": 16, "source_calls": 14, "output_readouts": 130, "root_calls": 144},
            "delta_formula": "-2*f + 4*g + rho; f=source-call frame/dispatch cost, g=one output readout cost, rho=all additional TRIO-specific expense",
            "unit_call_delta": 2,
            "scope_note": "The source-map multiplicity multiset matches the incumbent's (2,2,2,2,4,4); at unit call prices the completed one-TRIO path loses by 2 before rho.",
        },
    }


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("--write", "--check"):
        print("usage: search.py --write|--check", file=sys.stderr)
        return 2
    result = enumerate_class()
    path = HERE / "CERTIFICATE.json"
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if sys.argv[1] == "--write":
        path.write_text(encoded, encoding="utf-8")
    elif not path.is_file() or path.read_text(encoding="utf-8") != encoded:
        print("FAIL_CERTIFICATE_MISMATCH", file=sys.stderr)
        return 1
    print("PASS_SINGLE_TRIO_CENSUS nodes=%d eligible=%d max=%d/%d at_max=%d" % (
        result["enumeration"]["rgs_nodes_including_root"],
        result["enumeration"]["words_in_allowed_profiles"],
        result["enumeration"]["maximum_coverage"], 63,
        result["enumeration"]["number_at_maximum"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
