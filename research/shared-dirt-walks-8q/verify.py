#!/usr/bin/env python3
"""Shared-dirt partitioned dual walks at Q=8; read-only default.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from model import (  # noqa: E402
    EXPECTED,
    champion_analysis,
    enumerate_partition_26,
    enumerate_partition_35,
    enumerate_partition_44,
    length1_invalid_examples,
    tariff_qrx,
    valid_restored_walk,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def check_source_pins():
    sources = load_json_reject_duplicates(SOURCES_PATH)
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live = ROOT / rec["path"]
        need(live.is_file(), f"missing input {rec['path']}")
        need(sha256(live) == rec["sha256"], f"source bytes mismatch: {rec['path']}")


def build_certificate():
    need(not valid_restored_walk((0,)), "length-1 invalid")
    length1 = length1_invalid_examples()

    census26 = enumerate_partition_26()
    need(census26["covering_pairs"] == EXPECTED["partition_26_covering"], "26 covering")
    need(census26["min_R"] == EXPECTED["partition_26_min_R"], "26 min")

    census35 = enumerate_partition_35()
    need(census35["covering_pairs"] == EXPECTED["partition_35_covering"], "35 covering")
    need(census35["min_R"] == EXPECTED["partition_35_min_R"], "35 min")

    census44 = enumerate_partition_44()
    need(census44["covering_pairs"] == EXPECTED["partition_44_covering"], "44 covering")
    need(census44["min_R"] == EXPECTED["partition_44_min_R"], "44 min")

    champ = champion_analysis()
    need(champ["partition_min_R"] == 82, "global min")
    need(champ["tariff_floor_at_X0"] == EXPECTED["tariff_floor_at_X0"], "floor")
    need(champ["undercuts_436_after_complete_bill"] is False, "no undercut")
    need(champ["beats_independent_floors"] is True, "beats independent")

    partition_min = min(census26["min_R"], census35["min_R"], census44["min_R"])
    need(partition_min == EXPECTED["partition_min_R"], "partition min")

    cert = {
        "schema_version": 1,
        "status": "PASS_SHARED_DIRT_WALKS_8Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898) at "
            "(b,a,x)=(38,2,2). Freestanding shared-dirt (single coefficient / "
            "joint even live-read parity) dual on distinct partitioned restored "
            "walks at total Q=8 on shapes (2,6), (3,5), and (4,4). Exact covering "
            "min R=82 (tariff floor 468>436). Undercuts independent-dirt floors "
            "92/98/100 but does not undercut tariff 436. Soft-overlap-safe vs "
            "deferred shared-XOR: R-side dirt coupling only. Answers preferred "
            "next18 / tworepeat OQ1–OQ2 without editing leave-alones through "
            "#2858 / #2851 or pending onerepeat/tworepeat tips."
        ),
        "claim": {
            "Q": 8,
            "partitions": [[2, 6], [3, 5], [4, 4]],
            "alphabet": "shared_dirt_partitioned_dual",
            "shared_dirt_26_covering": EXPECTED["partition_26_covering"],
            "shared_dirt_26_min_R": 82,
            "shared_dirt_26_histogram": EXPECTED["partition_26_histogram"],
            "shared_dirt_35_covering": EXPECTED["partition_35_covering"],
            "shared_dirt_35_min_R": 82,
            "shared_dirt_35_histogram": EXPECTED["partition_35_histogram"],
            "shared_dirt_44_covering": EXPECTED["partition_44_covering"],
            "shared_dirt_44_min_R": 82,
            "shared_dirt_44_histogram": EXPECTED["partition_44_histogram"],
            "partition_min_R": 82,
            "tariff_floor_at_X0": EXPECTED["tariff_floor_at_X0"],
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "undercuts_436_after_complete_bill": False,
            "beats_independent_dirt_floors": True,
            "independent_floors": {"26": 92, "35": 98, "44": 100},
            "answers_fourth_priced_alphabet_q8": True,
            "answers_tworepeat_oq2_shared_dirt": True,
            "soft_overlap_shared_xor": "safe_R_side_dirt_coupling_only",
            "oq_answer": (
                "The named fourth priced readout alphabet under PR1898 "
                "(b,a,x)=(38,2,2) beyond same-walk / dirty-shadow / partitioned "
                "dual / one-repeat / two-repeat is the shared-dirt (joint even "
                "live-read parity) dual on distinct partitioned walks at Q=8. "
                "Exact census: (2,6)/(3,5)/(4,4) covering mins all R=82 "
                "(histograms {82,88,96}); tariff floor 38·8+2·82=468>436. "
                "Shared dirt undercuts independent-dirt floors 92/98/100 on "
                "every covering shape's champion layer, but still cannot "
                "undercut the six-query endpoint after a complete dirty bill. "
                "Soft-overlap vs deferred shared-XOR is safe: only the R-side "
                "dirt coefficient is coupled; path-X / non-path XOR schedules "
                "are not shared. Leave-alones through #2858/#2851 and pending "
                "onerepeat/tworepeat tips are not reopened."
            ),
            "no_new_kappa": True,
        },
        "shared_dirt_2_plus_6": census26,
        "shared_dirt_3_plus_5": census35,
        "shared_dirt_4_plus_4": census44,
        "length1_invalid": length1,
        "champion": champ,
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X",
            "shared_dirt_floor_at_R82_X0": tariff_qrx(8, 82, 0),
            "independent_26_at_R92_X0": tariff_qrx(8, 92, 0),
            "one_repeat_at_R112_X0": tariff_qrx(8, 112, 0),
            "single_walk_at_R74_X0": tariff_qrx(8, 74, 0),
            "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        },
    }
    return cert


def compare_certificate(live, pinned):
    need(live["status"] == pinned["status"], "status")
    need(live["claim"] == pinned["claim"], "claim drift")
    need(
        live["shared_dirt_2_plus_6"]["covering_pairs"]
        == pinned["shared_dirt_2_plus_6"]["covering_pairs"],
        "26 covering drift",
    )
    need(
        live["shared_dirt_2_plus_6"]["min_R"] == pinned["shared_dirt_2_plus_6"]["min_R"],
        "26 min drift",
    )
    need(
        live["shared_dirt_2_plus_6"]["histogram"]
        == pinned["shared_dirt_2_plus_6"]["histogram"],
        "26 hist drift",
    )
    need(
        live["shared_dirt_3_plus_5"]["covering_pairs"]
        == pinned["shared_dirt_3_plus_5"]["covering_pairs"],
        "35 covering drift",
    )
    need(
        live["shared_dirt_3_plus_5"]["min_R"] == pinned["shared_dirt_3_plus_5"]["min_R"],
        "35 min drift",
    )
    need(
        live["shared_dirt_3_plus_5"]["histogram"]
        == pinned["shared_dirt_3_plus_5"]["histogram"],
        "35 hist drift",
    )
    need(
        live["shared_dirt_4_plus_4"]["covering_pairs"]
        == pinned["shared_dirt_4_plus_4"]["covering_pairs"],
        "44 covering drift",
    )
    need(
        live["shared_dirt_4_plus_4"]["min_R"] == pinned["shared_dirt_4_plus_4"]["min_R"],
        "44 min drift",
    )
    need(
        live["shared_dirt_4_plus_4"]["histogram"]
        == pinned["shared_dirt_4_plus_4"]["histogram"],
        "44 hist drift",
    )
    need(live["tariff_check"] == pinned["tariff_check"], "tariff drift")
    need(
        live["champion"]["undercuts_436_after_complete_bill"]
        == pinned["champion"]["undercuts_436_after_complete_bill"],
        "undercut drift",
    )
    need(
        live["champion"]["beats_independent_floors"]
        == pinned["champion"]["beats_independent_floors"],
        "beats-independent drift",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite CERTIFICATE.json (maintenance only)",
    )
    args = parser.parse_args(argv)

    check_source_pins()
    live = build_certificate()

    if args.write_certificate:
        CERT_PATH.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
        print("WROTE_CERTIFICATE", CERT_PATH)
        return 0

    pinned = load_json_reject_duplicates(CERT_PATH)
    compare_certificate(live, pinned)
    claim = pinned["claim"]
    print(
        "PASS_SHARED_DIRT_WALKS_8Q_OBSTRUCTION",
        f"partition_min_R={claim['partition_min_R']}",
        f"covering_26={claim['shared_dirt_26_covering']}",
        f"covering_35={claim['shared_dirt_35_covering']}",
        f"covering_44={claim['shared_dirt_44_covering']}",
        f"tariff_floor={claim['tariff_floor_at_X0']}",
        f"endpoint={claim['endpoint_Q6_tariff']}",
        "beats_independent_dirt_floors",
        "no_undercut_436",
        "answers_fourth_priced_alphabet_q8",
        "soft_overlap_shared_xor_safe",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
