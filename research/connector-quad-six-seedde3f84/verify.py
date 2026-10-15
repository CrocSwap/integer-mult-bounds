#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite screen for one arity-four connector bundle."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def check_pins() -> dict[str, str]:
    manifest = read_json(HERE / "SOURCES.json")
    digests = {}
    for row in manifest["files"]:
        source = HERE / "task-catalog-snapshot.json" if row["path"] == "docs/research/agent-task-catalog.json" else ROOT / row["path"]
        data = source.read_bytes()
        sha256 = hashlib.sha256(data).hexdigest()
        need(sha256 == row["sha256"], "source SHA256 mismatch: " + row["path"])
        need(git_blob_sha1(data) == row["git_blob"], "source Git blob mismatch: " + row["path"])
        digests[row["path"]] = sha256
    return digests


def target_mask(n: int) -> int:
    # Bits indexed by source mask; mask 0 is deliberately excluded.
    return (1 << (1 << n)) - 2


def difference_bits(states: list[int]) -> int:
    bits = 0
    for i, left in enumerate(states):
        for right in states[i + 1:]:
            bits |= 1 << (left ^ right)
    return bits


def difference_set(states: list[int]) -> set[int]:
    return {left ^ right for i, left in enumerate(states) for right in states[i + 1:] if left != right}


def mask_labels(mask: int, n: int) -> list[str]:
    return [format(x, f"0{n}b") for x in range(1, 1 << n) if (mask >> x) & 1]


def enumerate_profile(n: int, qmask: int, counts: list[int]) -> tuple[int, Counter[int], int, list[int], list[int]]:
    """Enumerate each distinct singleton order once after the unique Q edge."""
    total = best = 0
    histogram: Counter[int] = Counter()
    best_order: list[int] = []
    best_states: list[int] = []
    path = [0, qmask]
    best_bits = 0

    def visit(remaining: list[int], current: int, suffix: list[int]) -> None:
        nonlocal total, best, best_order, best_states, best_bits
        if not any(remaining):
            need(current == 0, "source path failed to restore the dirty connector")
            need(len(path) == (1 + sum(counts)) + 1, "wrong source-boundary count")
            bits = difference_bits(path)
            covered = (bits & ~1).bit_count()
            histogram[covered] += 1
            total += 1
            if covered > best:
                best, best_order, best_states, best_bits = covered, suffix.copy(), path.copy(), bits
            return
        for source, count in enumerate(remaining):
            if count:
                remaining[source] -= 1
                nxt = current ^ (1 << source)
                path.append(nxt)
                suffix.append(source)
                visit(remaining, nxt, suffix)
                suffix.pop()
                path.pop()
                remaining[source] += 1

    visit(counts.copy(), qmask, [])
    return total, histogram, best, best_order, best_states


def census(n: int) -> dict:
    need(n in (5, 6), "only the declared five- and six-source cases are in scope")
    qmask = 0b1111
    need(qmask < (1 << n), "four-source bundle exceeds the source dimension")
    # Every Q-source has odd singleton multiplicity; every outside source has
    # positive even multiplicity. Minimal profiles have 8 singletons at n=5,
    # and 10 at n=6. The next count is outside this exact minimal-profile census.
    singletons = 8 if n == 5 else 10
    base = [1, 1, 1, 1] + [2] * (n - 4)
    profiles = []
    for extra_source in range(n):
        counts = base.copy()
        counts[extra_source] += 2
        profiles.append((extra_source, counts))

    total = best = 0
    histogram: Counter[int] = Counter()
    best_example = None
    for extra_source, counts in profiles:
        need(sum(counts) == singletons, "profile has wrong singleton total")
        need(all(counts[j] % 2 == 1 for j in range(4)), "Q-source parity error")
        need(all(counts[j] > 0 and counts[j] % 2 == 0 for j in range(4, n)),
             "outside-source positivity/parity error")
        profile_total, profile_hist, profile_best, order, states = enumerate_profile(n, qmask, counts)
        total += profile_total
        histogram.update(profile_hist)
        if profile_best > best:
            best = profile_best
            best_example = {"extra_source": extra_source, "singleton_order": order, "states": states}

    expected = 15_120 if n == 5 else 756_000
    need(total == expected, f"distinct-order count mismatch for n={n}: {total}")
    return {
        "sources": n,
        "bundle_sources": [0, 1, 2, 3],
        "bundle_mask": qmask,
        "bundle_first_by_cycle_rotation": True,
        "singleton_calls": singletons,
        "source_transitions": singletons + 1,
        "boundary_values": singletons + 2,
        "multiplicity_profiles": len(profiles),
        "distinct_orders": total,
        "full_mask_covers": histogram.get((1 << n) - 1, 0),
        "maximum_covered_masks": best,
        "coverage_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "best_example": best_example,
        "best_missing_masks": mask_labels(
            target_mask(n) & ~difference_bits(best_example["states"]), n
        ),
    }


def certified_cost_screen(n6: dict) -> dict:
    # The existing six-source TRIO profile in PR2146 is (138,140) in the
    # uniform root-call/map-addition model. Q4 source-call counts are odd:
    # Q contributes four B additions, singleton total is even, and every
    # B_j must occur positively and evenly.
    max_pairs_at_nine_calls = (10 * 9) // 2
    d11 = n6["maximum_covered_masks"]
    missing_at_11 = 63 - d11
    need(0 <= d11 <= 63, "invalid n=6 difference coverage")
    return {
        "unit_model": "(root_call_count, map_addition_count) charged as (o,p); one Q4 costs four B additions plus one root transition before surcharge rho",
        "best_current_trio": {
            "root_calls": 138,
            "map_additions": 140,
            "source": "PR2146",
            "head": "302b0e87d9328fabc2a670248afb357bbb44041b",
            "url": "https://github.com/CrocSwap/integer-mult-bounds/pull/2146",
        },
        "duo_predecessor": {
            "root_calls": 140,
            "map_additions": 142,
            "source": "PR2128",
            "head": "697369a971eed02c0fbcd75ebefec9f59945f08e",
            "url": "https://github.com/CrocSwap/integer-mult-bounds/pull/2128",
        },
        "nine_source_calls": {
            "boundary_values": 10,
            "pair_slots_upper_bound": max_pairs_at_nine_calls,
            "unpairable_outputs_lower_bound": 63 - max_pairs_at_nine_calls,
            "output_calls_lower_bound": 2 * max_pairs_at_nine_calls + 4 * (63 - max_pairs_at_nine_calls),
            "root_calls_lower_bound": 9 + 2 * max_pairs_at_nine_calls + 4 * (63 - max_pairs_at_nine_calls),
            "map_additions_lower_bound": 12 + 2 * max_pairs_at_nine_calls + 4 * (63 - max_pairs_at_nine_calls),
        },
        "eleven_source_calls": {
            "boundary_values": 12,
            "exact_max_pair_covered_masks": d11,
            "unpairable_outputs_lower_bound": missing_at_11,
            "output_calls_lower_bound": 2 * d11 + 4 * missing_at_11,
            "root_calls_lower_bound": 11 + 2 * d11 + 4 * missing_at_11,
            "map_additions_lower_bound": 14 + 2 * d11 + 4 * missing_at_11,
            "exact_domain_orders": n6["distinct_orders"],
        },
        "thirteen_or_more_source_calls": {
            "minimum_source_calls": 13,
            "minimum_b_additions": 16,
            "minimum_output_calls": 126,
            "root_calls_lower_bound": 139,
            "map_additions_lower_bound": 142,
            "dominates_trio_componentwise": True,
        },
        "interpretation": "For n=6 with all 63 targets, arbitrary dirty connector and even positive output multiplicities, the 9-call case has at least 18 unpairable masks, the exact 11-call census leaves at least 22 unpairable masks, and every later parity-allowed source length is componentwise worse than the existing 138o+140p TRIO profile. Any extra Q4 overhead rho only increases these bills.",
    }


def verify_controls() -> dict:
    cert = read_json(ROOT / "research/universal-connector-boundary/CERTIFICATE.json")
    baseline = cert["schedules"]["five_extra_source"]["source_word"]
    counts = Counter(baseline)
    need(set(counts) == set(range(5)) and all(count > 0 and count % 2 == 0 for count in counts.values()),
         "pinned five-source positive control does not restore every source")
    states = [0]
    for source in baseline:
        states.append(states[-1] ^ (1 << source))
    need(states[-1] == 0, "pinned positive control does not close")
    bitset = difference_bits(states) & ~1
    as_set = difference_set(states)
    need(bitset == sum(1 << x for x in as_set), "independent set/bitset difference controls disagree")
    need(bitset == target_mask(5), "pinned universal connector positive control lost a mask")

    broken = baseline[:-1]
    broken_counts = Counter(broken)
    need(not (set(broken_counts) == set(range(5)) and all(c > 0 and c % 2 == 0 for c in broken_counts.values())),
         "source-deletion negative control unexpectedly restores every source")
    mutant = baseline.copy()
    mutant[0], mutant[3] = mutant[3], mutant[0]
    mutant_states = [0]
    for source in mutant:
        mutant_states.append(mutant_states[-1] ^ (1 << source))
    need((difference_bits(mutant_states) & ~1) != target_mask(5),
         "paired source-order mutation unexpectedly retains full mask coverage")
    return {
        "positive_control": "pinned five_extra_source word covers all 31 nonzero masks and restores all five sources",
        "independent_control": "set-based and bitset-based pair-difference implementations agree",
        "negative_controls": [
            "deleting the final singleton breaks source restoration",
            "swapping source steps 0 and 3 preserves multiplicities and restoration but lowers coverage to 27",
        ],
    }


def compute_result() -> dict:
    source_hashes = check_pins()
    n5 = census(5)
    n6 = census(6)
    controls = verify_controls()
    need(n5["maximum_covered_masks"] == 25 and n5["full_mask_covers"] == 0,
         "five-source pivot control changed")
    need(n6["maximum_covered_masks"] == 41 and n6["full_mask_covers"] == 0,
         "six-source census control changed")
    need(63 - n6["maximum_covered_masks"] == 22, "wrong unpaired six-source mask count")
    return {
        "schema_version": 1,
        "status": "PASS_QUAD4_SCOPED_OBSTRUCTION",
        "scope": "one four-source bundle plus the minimal parity-allowed singleton profile, with two readouts per nonzero output mask",
        "operation": "Q_S: z += sum(B_j*x_j for j in S), exactly one root transition and four charged B-map additions",
        "source_sha256": source_hashes,
        "runner_sha256": hashlib.sha256((HERE / "verify.py").read_bytes()).hexdigest(),
        "five_source_pivot": n5,
        "six_source_minimal_profile": n6,
        "cost_screen": certified_cost_screen(n6),
        "controls": controls,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = compute_result()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    receipt = HERE / "RESULT.json"
    if args.write_result:
        receipt.write_text(encoded, encoding="utf-8")
    else:
        need(receipt.is_file(), "missing RESULT.json; run with --write-result once")
        need(receipt.read_text(encoding="utf-8") == encoded,
             "RESULT.json differs from the exact recomputation")
    print("PASS_QUAD4_SCOPED_OBSTRUCTION",
          "n5", result["five_source_pivot"]["distinct_orders"],
          "max", result["five_source_pivot"]["maximum_covered_masks"],
          "n6", result["six_source_minimal_profile"]["distinct_orders"],
          "max", result["six_source_minimal_profile"]["maximum_covered_masks"],
          "full", result["six_source_minimal_profile"]["full_mask_covers"])


if __name__ == "__main__":
    main()
