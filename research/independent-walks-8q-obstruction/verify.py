#!/usr/bin/env python3
"""Partitioned independent-walks obstruction at Q=8; read-only default.

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
    dual_R_short_long,
    dual_independent_R,
    enumerate_partition_26,
    enumerate_partition_35,
    enumerate_partition_44,
    even_table,
    length1_invalid_examples,
    structural_26_rank4_outside,
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

    part26 = enumerate_partition_26()
    need(part26["covering_pairs"] == EXPECTED["partition_26_covering"], "26 covering")
    need(part26["min_R"] == EXPECTED["partition_26_min_R"], "26 min R")
    need(part26["histogram"] == EXPECTED["partition_26_histogram"], "26 hist")

    part35 = enumerate_partition_35()
    need(part35["covering_pairs"] == EXPECTED["partition_35_covering"], "35 covering")
    need(part35["min_R"] == EXPECTED["partition_35_min_R"], "35 min R")
    need(part35["histogram"] == EXPECTED["partition_35_histogram"], "35 hist")

    part44 = enumerate_partition_44()
    need(part44["covering_pairs"] == EXPECTED["partition_44_covering"], "44 covering")
    need(part44["min_R"] == EXPECTED["partition_44_min_R"], "44 min R")
    need(part44["histogram"] == EXPECTED["partition_44_histogram"], "44 hist")

    partition_min = min(part26["min_R"], part35["min_R"], part44["min_R"])
    need(partition_min == EXPECTED["partition_min_R"] == 92, "global partition min")

    champ = champion_analysis()
    need(champ["tariff_floor_at_X0"] == EXPECTED["tariff_floor_at_X0"], "tariff floor")
    need(champ["tariff_floor_at_X0"] > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(champ["champion_26"]["R"] == 92, "champ26 R")
    need(champ["champion_35"]["R"] == 98, "champ35 R")
    need(champ["champion_44"]["R"] == 100, "champ44 R")

    w26_a, w26_b = tuple(champ["champion_26"]["walks"][0]), tuple(
        champ["champion_26"]["walks"][1]
    )
    w35_a, w35_b = tuple(champ["champion_35"]["walks"][0]), tuple(
        champ["champion_35"]["walks"][1]
    )
    w44_a, w44_b = tuple(champ["champion_44"]["walks"][0]), tuple(
        champ["champion_44"]["walks"][1]
    )
    need(dual_R_short_long(even_table(w26_b), w26_a[1]) == 92, "recompute 26")
    need(
        dual_independent_R(even_table(w35_a), even_table(w35_b)) == 98,
        "recompute 35",
    )
    need(
        dual_independent_R(even_table(w44_a), even_table(w44_b)) == 100,
        "recompute 44",
    )
    need(structural_26_rank4_outside(w26_a[1], w26_b)["R"] == 92, "recompute structural")
    need(EXPECTED["single_walk_even_min_R_Q8"] == 74, "baseline even floor constant")

    cert = {
        "schema_version": 1,
        "status": "PASS_INDEPENDENT_WALKS_8Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898) at "
            "(b,a,x)=(38,2,2). Freestanding partitioned independent dual walks "
            "at total Q=8 (valid restored lengths (2,6), (3,5), (4,4)): covering "
            "dual even-parity readout has global min R=92 at (2,6); tariff floor "
            "at X=0 is 488>436. Answers dirty-shadow/#2840 OQ2 / onerepeat OQ2 "
            "by naming one new priced alphabet at eight queries."
        ),
        "claim": {
            "Q": 8,
            "partition_covering_min_R": 92,
            "partition_26_covering": part26["covering_pairs"],
            "partition_35_covering": part35["covering_pairs"],
            "partition_44_covering": part44["covering_pairs"],
            "partition_26_min_R": 92,
            "partition_35_min_R": 98,
            "partition_44_min_R": 100,
            "tariff_floor_at_X0": EXPECTED["tariff_floor_at_X0"],
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "undercuts_436_after_complete_bill": False,
            "length1_walks_invalid": True,
            "answers_priced_alphabet_q8_oq": True,
            "oq_answer": (
                "Every covering partitioned dual-walk schedule with total "
                "query count Q=n0+n1=8 (valid restored walks of lengths (2,6), "
                "(3,5), or (4,4), distinct nonzero labels within each walk, "
                "independent dirt, dual even-parity readout) has R≥92, attained "
                "only on (2,6) (spectrum {92,96,104}; covering 3916416). "
                "Partitions (3,5) and (4,4) have min R 98 and 100. At X=0 the "
                "abstract tariff is already 488>436 under (b,a,x)=(38,2,2); "
                "positive path X only increases the bill. Length-1 components "
                "are not restored. Transfer-coupled / onerepeat / dirty-shadow "
                "leave-alones are not reopened."
            ),
            "no_new_kappa": True,
        },
        "partition_2_plus_6": part26,
        "partition_3_plus_5": part35,
        "partition_4_plus_4": part44,
        "champion": champ,
        "length1_invalid_examples": length1,
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X",
            "at_R92_X0": tariff_qrx(8, 92, 0),
            "champion_26": tariff_qrx(8, 92, champ["champion_26"]["path_X"]),
            "champion_35": tariff_qrx(8, 98, champ["champion_35"]["path_X"]),
            "champion_44": tariff_qrx(8, 100, champ["champion_44"]["path_X"]),
            "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        },
    }
    return cert


def compare_certificate(live, pinned):
    need(live["status"] == pinned["status"], "status")
    need(live["claim"] == pinned["claim"], "claim drift")
    for key in (
        "partition_2_plus_6",
        "partition_3_plus_5",
        "partition_4_plus_4",
    ):
        need(
            live[key]["covering_pairs"] == pinned[key]["covering_pairs"],
            f"{key} covering drift",
        )
        need(live[key]["histogram"] == pinned[key]["histogram"], f"{key} hist drift")
        need(live[key]["min_R"] == pinned[key]["min_R"], f"{key} min drift")
    need(live["tariff_check"] == pinned["tariff_check"], "tariff drift")
    need(
        live["champion"]["tariff_floor_at_X0"]
        == pinned["champion"]["tariff_floor_at_X0"],
        "floor",
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
        "PASS_INDEPENDENT_WALKS_8Q_OBSTRUCTION",
        f"partition_min_R={claim['partition_covering_min_R']}",
        f"covering_26={claim['partition_26_covering']}",
        f"covering_35={claim['partition_35_covering']}",
        f"covering_44={claim['partition_44_covering']}",
        f"tariff_floor={claim['tariff_floor_at_X0']}",
        f"endpoint={claim['endpoint_Q6_tariff']}",
        "no_undercut_partitioned_independent_walks_q8",
        "answers_priced_alphabet_q8_oq",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
