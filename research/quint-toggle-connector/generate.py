#!/usr/bin/env python3
"""Exact representative census for one all-five-source toggle."""
import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_CERT = ROOT / "research/universal-connector-boundary/CERTIFICATE.json"
CERT = HERE / "CERTIFICATE.json"
Q5 = 31
SOURCES = (1, 2, 4, 8, 16)
CASES = (
    ("m7_one_triple", (3, 1, 1, 1, 1), 5),
    ("m9_one_quintuple", (5, 1, 1, 1, 1), 5),
    ("m9_two_triples", (3, 3, 1, 1, 1), 10),
)


def prefixes(word):
    out = [0]
    for step in word:
        out.append(out[-1] ^ step)
    return out


def census(name, counts, orbit_size):
    singleton_calls = sum(counts)
    singleton_word = tuple(
        label for label, count in zip(SOURCES, counts) for _ in range(count)
    )
    orders = sorted(set(itertools.permutations(singleton_word)))
    histogram = Counter()
    best_coverage = -1
    best_word = None
    digest = hashlib.sha256()
    checked = 0

    for order in orders:
        for q5_slot in range(singleton_calls + 1):
            word = order[:q5_slot] + (Q5,) + order[q5_slot:]
            points = prefixes(word)
            assert points[-1] == 0, "parity class failed to restore connector"
            differences = {
                points[i] ^ points[j]
                for i in range(len(points))
                for j in range(i + 1, len(points))
            }
            assert 0 in differences, "closed walk must contribute the zero difference"
            coverage = len(differences) - 1
            histogram[coverage] += 1
            checked += 1
            row = json.dumps(
                [name, list(word), sorted(differences)],
                separators=(",", ":"),
            ).encode("ascii")
            digest.update(row + b"\n")
            if coverage > best_coverage:
                best_coverage = coverage
                best_word = list(word)

    record = {
        "case": name,
        "singleton_counts": list(counts),
        "symmetry_orbit_size": orbit_size,
        "representative_words": checked,
        "labeled_words": checked * orbit_size,
        "representative_histogram": dict(sorted(histogram.items())),
        "labeled_histogram": dict(
            sorted((key, value * orbit_size) for key, value in histogram.items())
        ),
        "max_nonzero_pair_differences": best_coverage,
        "maximizing_word": best_word,
        "representative_records_sha256": digest.hexdigest(),
    }
    missing_masks = 31 - best_coverage
    source_calls = 1 + singleton_calls
    source_adds = 5 + singleton_calls
    readouts = 62 + 2 * missing_masks
    record.update({
        "missing_masks_at_least": missing_masks,
        "source_calls": source_calls,
        "source_adds": source_adds,
        "readout_calls_at_least": readouts,
        "total_root_queries_at_least": source_calls + readouts,
        "total_elementary_adds_at_least": source_adds + readouts,
    })
    return record


def baseline_summary():
    data = json.loads(BASE_CERT.read_text(encoding="utf-8"))
    schedule = data["schedules"]["five_extra_source"]
    word = schedule["word"]
    source_word = [call[1] for call in word if call[0] == "B"]
    readouts = sum(call[0] == "A" for call in word)
    source_calls = sum(call[0] == "B" for call in word)
    points = prefixes([1 << label for label in source_word])
    differences = {
        points[i] ^ points[j]
        for i in range(len(points))
        for j in range(i + 1, len(points))
    }
    assert len(word) == schedule["queries"] == 74
    assert readouts == 62 and source_calls == 12
    assert schedule["source_word"] == source_word
    assert len(source_word) == 12 and points[-1] == 0
    assert differences == set(range(32)), "baseline path misses a five-source mask"
    q = 0
    row_prefixes = {row: [] for row in range(31)}
    for call in word:
        if call[0] == "B":
            q ^= 1 << call[1]
        elif call[0] == "A":
            row_prefixes[call[1]].append(q)
        else:
            raise AssertionError("unexpected call in singleton baseline")
    assert q == 0
    for row, observed in row_prefixes.items():
        assert len(observed) == 2
        assert observed[0] ^ observed[1] == row + 1
    return {
        "root_queries": len(word),
        "readout_calls": readouts,
        "source_calls": source_calls,
        "source_adds": source_calls,
        "total_elementary_adds": readouts + source_calls,
        "source_word": source_word,
        "covered_nonzero_masks": len(differences) - 1,
    }


def build_certificate():
    cases = [census(*case) for case in CASES]
    m9_histogram = Counter()
    for case in cases[1:]:
        m9_histogram.update(case["labeled_histogram"])
    return {
        "schema_version": 1,
        "field": "F2^5",
        "operation": {
            "symbol": "Q5",
            "definition": "z += sum_j B_j x_j, j=0..4",
            "maximum_uses": 1,
            "dispatches_per_use": 1,
            "elementary_source_adds_per_use": 5,
        },
        "target_batch": {
            "nonzero_masks": 31,
            "minimum_readout_calls": 62,
            "reason": "each dirty-output row needs an even positive number of A readouts",
        },
        "one_q5_source_walks": {
            "restoration_rule": "each singleton source count m_j is positive odd",
            "m5": {
                "singleton_counts": [1, 1, 1, 1, 1],
                "source_calls": 6,
                "source_adds": 10,
                "prefixes": 7,
                "upper_bound_nonzero_pair_differences": 20,
                "missing_masks_at_least": 11,
                "readout_calls_at_least": 84,
                "total_root_queries_at_least": 90,
                "total_elementary_adds_at_least": 94,
            },
            "m7_census": cases[0],
            "m9_censuses": cases[1:],
            "m9_aggregate": {
                "labeled_words": sum(case["labeled_words"] for case in cases[1:]),
                "labeled_histogram": dict(sorted(m9_histogram.items())),
                "max_nonzero_pair_differences": max(
                    case["max_nonzero_pair_differences"] for case in cases[1:]
                ),
                "missing_masks_at_least": 31 - max(
                    case["max_nonzero_pair_differences"] for case in cases[1:]
                ),
                "readout_calls_at_least": 70,
                "total_root_queries_at_least": 80,
                "total_elementary_adds_at_least": 84,
            },
            "m_at_least_11": {
                "source_calls_at_least": 12,
                "source_adds_at_least": 16,
                "readout_calls_at_least": 62,
                "total_root_queries_at_least": 74,
                "total_elementary_adds_at_least": 78,
            },
        },
        "singleton_alphabet_baseline_witness": baseline_summary(),
        "conclusion": (
            "With one Q5 at most, no completed five-source 31-mask schedule has "
            "a strictly lower (root-query, elementary-add) cost than the "
            "12-source-call singleton witness for any nonnegative per-query "
            "overhead and positive per-add price."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the regenerated certificate")
    args = parser.parse_args()
    actual = build_certificate()
    rendered = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    if args.write:
        CERT.write_text(rendered, encoding="utf-8")
        print("WROTE_QUINT_TOGGLE_CERTIFICATE")
        return 0
    expected = CERT.read_text(encoding="utf-8")
    if rendered != expected:
        print("FAIL_QUINT_TOGGLE_CERTIFICATE_MISMATCH")
        return 1
    print(
        "PASS_QUINT_TOGGLE_CENSUS m7=33600:max20 "
        "m9=1159200:max27"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
