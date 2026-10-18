#!/usr/bin/env python3
"""Exact weighted schedules for the five-source dirty connector interface."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
SEED = "1275309492f09fbd834a77649e96ad73"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
PREDECESSOR_CERT_SHA256 = "e733746ba3e5151c829b4e8728bfff5ae3ed24d8d203eb77c735d20758e8266a"
PREDECESSOR_EXPECTED_SHA256 = "658924c2940cbe193378d5ef09f4d62500fc7b385c16c0ea33846be836c429d2"
N_SOURCE = 5
N_TARGET = 31
NSTATE = N_SOURCE + 1 + N_TARGET
B_PRICE = (1, 4, 10, 16, 28)
A_PRICE = {mask: 1 for mask in range(1, 32)}
CERTIFICATE = PACKAGE / "CERTIFICATE.json"
UPSTREAM = ROOT / "research/universal-connector-boundary"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL_WEIGHTED_CONNECTOR_READOUTS: " + message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prefixes(source_word: list[int]) -> list[int]:
    q = 0
    result = [q]
    for source in source_word:
        need(0 <= source < N_SOURCE, "source label out of range")
        q ^= 1 << source
        result.append(q)
    return result


def difference_set(qs: list[int]) -> set[int]:
    return {a ^ b for a in qs for b in qs}


def first_readout_pair(qs: list[int], mask: int) -> list[int]:
    for left in range(len(qs)):
        for right in range(left + 1, len(qs)):
            if qs[left] ^ qs[right] == mask:
                return [left, right]
    raise SystemExit(f"FAIL_WEIGHTED_CONNECTOR_READOUTS: no readout pair for mask {mask}")


def full_slots(qs: list[int]) -> list[list[int]]:
    return [first_readout_pair(qs, mask) for mask in range(1, 32)]


def operations(source_word: list[int], rows: list[int], slots: list[list[int]]) -> list[list[int]]:
    need(rows == list(range(1, 32)), "target set must be exactly all nonzero masks")
    need(len(slots) == len(rows), "readout slot vector length mismatch")
    at_boundary: dict[int, list[int]] = {}
    for mask, places in zip(rows, slots):
        need(len(places) >= 2 and len(places) % 2 == 0, "dirty-target readout count must be even and at least two")
        need(len(set(places)) == len(places), "one target cannot be read twice at one boundary")
        need(all(0 <= t <= len(source_word) for t in places), "readout boundary out of range")
        for place in places:
            at_boundary.setdefault(place, []).append(mask)
    word: list[list[int]] = []
    for boundary in range(len(source_word) + 1):
        for mask in sorted(at_boundary.get(boundary, [])):
            word.append([1, mask])  # A_m: target y_m += connector z
        if boundary < len(source_word):
            word.append([0, source_word[boundary]])  # B_j: connector z += source x_j
    return word


def run(state: int, word: list[list[int]]) -> int:
    z_bit = 1 << N_SOURCE
    for kind, label in word:
        if kind == 0:
            if (state >> label) & 1:
                state ^= z_bit
        else:
            if (state >> N_SOURCE) & 1:
                state ^= 1 << (N_SOURCE + 1 + label - 1)
    return state


def columns(word: list[list[int]]) -> list[int]:
    return [run(1 << coordinate, word) for coordinate in range(NSTATE)]


def expected_columns() -> list[int]:
    result = []
    for coordinate in range(NSTATE):
        image = 1 << coordinate
        if coordinate < N_SOURCE:
            for mask in range(1, 32):
                if (mask >> coordinate) & 1:
                    image ^= 1 << (N_SOURCE + 1 + mask - 1)
        result.append(image)
    return result


def invoice(word: list[list[int]]) -> dict[str, int]:
    b_counts = Counter(label for kind, label in word if kind == 0)
    a_counts = Counter(label for kind, label in word if kind == 1)
    source_cost = sum(B_PRICE[j] * b_counts[j] for j in range(N_SOURCE))
    target_cost = sum(A_PRICE[m] * a_counts[m] for m in range(1, 32))
    return {
        "source_queries": sum(b_counts.values()),
        "target_queries": sum(a_counts.values()),
        "root_queries": len(word),
        "source_leaf_cost": source_cost,
        "target_leaf_cost": target_cost,
        "total_leaf_cost": source_cost + target_cost,
        **{f"B{j}_count": b_counts[j] for j in range(N_SOURCE)},
    }


def digest_word(word: list[list[int]]) -> str:
    payload = json.dumps(word, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write deterministic weighted certificate")
    args = parser.parse_args()

    need(hashlib.sha256((ROOT / "certificates/selected-result.json").read_bytes()).hexdigest() == SELECTED_SHA256,
         "selected record differs from the pinned base")
    cert_path = UPSTREAM / "CERTIFICATE.json"
    expected_path = UPSTREAM / "EXPECTED.json"
    need(sha256(cert_path) == PREDECESSOR_CERT_SHA256, "universal-connector certificate pin changed")
    need(sha256(expected_path) == PREDECESSOR_EXPECTED_SHA256, "universal-connector expected-results pin changed")
    prior = json.loads(cert_path.read_text(encoding="utf-8"))
    prior_expected = json.loads(expected_path.read_text(encoding="utf-8"))

    rows = prior["schedules"]["five_extra_output"]["rows"]
    need(rows == list(range(1, 32)), "predecessor output-mask set changed")
    ten_data = prior["schedules"]["five_extra_output"]
    twelve_data = prior["schedules"]["five_extra_source"]
    ten_sources = ten_data["source_word"]
    ten_slots = ten_data["readout_slots"]
    need(len(ten_sources) == 10, "ten-source-call source word changed")
    ten_qs = prefixes(ten_sources)
    ten_diff = difference_set(ten_qs)
    missing = sorted(set(range(1, 32)) - ten_diff)
    need(missing == [21], "pinned ten-call construction must miss exactly mask 21")
    need(sum(1 for s in ten_slots[20] if s is not None) == 4, "mask 21 must use four readouts")
    need(all(len(places) == 2 for i, places in enumerate(ten_slots) if i != 20),
         "all other ten-path targets must use two readouts")
    ten_word = operations(ten_sources, rows, ten_slots)

    old_sources = twelve_data["source_word"]
    need(len(old_sources) == 12, "pinned twelve-source-call word changed")
    old_slots = twelve_data["readout_slots"]
    old_word = operations(old_sources, rows, old_slots)
    old_invoice = invoice(old_word)

    # Swap labels 0 and 2 throughout the known universal word. This preserves
    # full F2^5 prefix-difference coverage while moving the repeated pair from
    # the price-10 source B2 to the price-1 source B0.
    weighted_sources = [2 if j == 0 else 0 if j == 2 else j for j in old_sources]
    weighted_qs = prefixes(weighted_sources)
    need(difference_set(weighted_qs) == set(range(32)), "relabelled twelve-call path lost universal coverage")
    weighted_slots = full_slots(weighted_qs)
    weighted_word = operations(weighted_sources, rows, weighted_slots)

    target = expected_columns()
    need(columns(old_word) == target, "pinned original twelve-call schedule does not realize the dirty map")
    need(columns(ten_word) == target, "ten-source/four-readout schedule misses the dirty map")
    need(columns(weighted_word) == target, "cheap-source relabelled schedule misses the dirty map")

    ten_invoice = invoice(ten_word)
    weighted_invoice = invoice(weighted_word)
    need(old_invoice["total_leaf_cost"] == 200, "pinned repeated-B2 schedule should cost 200")
    need(weighted_invoice["B0_count"] == 4 and all(weighted_invoice[f"B{j}_count"] == 2 for j in range(1, 5)),
         "weighted twelve-call schedule must repeat only the cheapest source")
    need(weighted_invoice["total_leaf_cost"] == 182, "relabelled schedule must cost 182")
    need(ten_invoice["total_leaf_cost"] == 182, "ten-call overread schedule must cost 182")
    need(ten_invoice["source_leaf_cost"] == 118 and ten_invoice["target_leaf_cost"] == 64,
         "ten-call invoice changed")
    need(weighted_invoice["source_leaf_cost"] == 120 and weighted_invoice["target_leaf_cost"] == 62,
         "weighted twelve-call invoice changed")
    need(ten_invoice["root_queries"] == weighted_invoice["root_queries"] == old_invoice["root_queries"] == 74,
         "all compared schedules must use 74 fixed-width root records")

    # Exact lower bound for every legal source length. Dirty restoration makes
    # each B_j count even; all 31 masks force each source to appear at least
    # twice. Length 11 is impossible, so only the 10-call case and >=12 remain.
    base_source = 2 * sum(B_PRICE)
    base_target = 2 * sum(A_PRICE.values())
    ten_case_lb = base_source + base_target + 2 * min(A_PRICE.values())
    longer_case_lb = base_source + 2 * min(B_PRICE) + base_target
    need((base_source, base_target, ten_case_lb, longer_case_lb) == (118, 62, 182, 182),
         "weighted lower-bound calculation changed")
    prior_census = next(x for x in prior_expected["censuses"] if x["sources"] == 5)
    need(prior_census == {"sources": 5, "pairings": 945, "max_coverage": 31},
         "pinned complete 945-path lemma changed")

    # Meaningful negative controls: an underread target and an un-restored
    # connector both fail the requested full-state map. The old B2 schedule is
    # semantically valid but must fail the claimed 182 cost cap.
    bad_ten_slots = [places[:] for places in ten_slots]
    bad_ten_slots[20] = bad_ten_slots[20][:2]
    bad_ten = operations(ten_sources, rows, bad_ten_slots)
    need(columns(bad_ten) != target, "two-readout mask-21 negative control unexpectedly passed")
    bad_restoration = weighted_word[:]
    bad_restoration.pop(next(i for i, op in enumerate(bad_restoration) if op == [0, 0]))
    need(columns(bad_restoration) != target, "omitted-source-restoration negative control unexpectedly passed")
    need(old_invoice["total_leaf_cost"] > weighted_invoice["total_leaf_cost"],
         "expensive repeated-source control should exceed the weighted optimum")

    result = {
        "schema_version": 1,
        "seed": SEED,
        "base_commit": BASE,
        "selected_record_sha256": SELECTED_SHA256,
        "model": {
            "field": "F2",
            "source_count": N_SOURCE,
            "target_masks": rows,
            "source_complete_leaf_prices": list(B_PRICE),
            "each_target_complete_leaf_price": 1,
            "state_bits": NSTATE,
            "all_inputs_dirty": True,
            "root_record_count": 74,
        },
        "schedules": {
            "pinned_repeated_B2": {
                "source_word": old_sources,
                "readout_slots": old_slots,
                "invoice": old_invoice,
                "operation_sha256": digest_word(old_word),
            },
            "weighted_relabelled_twelve": {
                "source_word": weighted_sources,
                "readout_slots": weighted_slots,
                "invoice": weighted_invoice,
                "operation_sha256": digest_word(weighted_word),
            },
            "ten_call_overread_mask21": {
                "source_word": ten_sources,
                "readout_slots": ten_slots,
                "invoice": ten_invoice,
                "operation_sha256": digest_word(ten_word),
            },
        },
        "lower_bound": {
            "ten_source_case": "945-path lemma implies at least one nonzero mask is absent; its dirty A readout count is at least four",
            "at_least_twelve_source_case": "all five B operators occur twice at baseline; any additional restored calls cost at least two times the minimum B price",
            "baseline_source_cost": base_source,
            "baseline_target_cost": base_target,
            "ten_case_minimum": ten_case_lb,
            "longer_case_minimum": longer_case_lb,
            "exact_optimum": 182,
            "inherited_path_census": prior_census,
        },
        "comparators": {
            "pinned_repeated_B2_cost": prior_expected["leaf_calls"]["five_extra_source"],
            "column_star_cost": prior_expected["star_comparators"]["column_stars"]["leaf_calls"],
            "row_star_cost": prior_expected["star_comparators"]["row_stars"]["leaf_calls"],
        },
        "negative_controls": [
            "two-readout substitute for missing mask 21 fails full dirty-state map",
            "delete one B0 call from the relabelled word; connector is not restored",
            "valid repeated-B2 word costs 200 and fails the 182 weighted cap",
        ],
        "map_sha256": hashlib.sha256(json.dumps(target, separators=(",", ":")).encode()).hexdigest(),
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        CERTIFICATE.write_text(encoded, encoding="utf-8")
    elif CERTIFICATE.exists():
        need(CERTIFICATE.read_text(encoding="utf-8") == encoded,
             "weighted certificate differs; run verify.py --write and review the deterministic change")
    print("PASS_WEIGHTED_CONNECTOR_READOUTS optimum=182 old_repeated_B2=200 saved=18 schedules=2 dirty_bits=37 root_queries=74 controls=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
