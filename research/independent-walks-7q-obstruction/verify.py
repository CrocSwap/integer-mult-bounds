#!/usr/bin/env python3
"""Partitioned independent-walks obstruction at Q=7; read-only default.

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
    enumerate_partition_25,
    enumerate_partition_34,
    even_sum_standard_F2_4,
    even_table,
    length1_invalid_examples,
    path_X,
    structural_25_identity,
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
    need(even_sum_standard_F2_4() == 40, "F2^4 even-sum identity")
    need(not valid_restored_walk((0,)), "length-1 invalid")
    length1 = length1_invalid_examples()

    part25 = enumerate_partition_25()
    need(part25["covering_pairs"] == EXPECTED["partition_25_covering"], "25 covering")
    need(part25["min_R"] == EXPECTED["partition_25_min_R"], "25 min R")
    need(part25["histogram"] == EXPECTED["partition_25_histogram"], "25 hist")
    need(part25["structural_ok"] == part25["covering_pairs"], "25 structural")
    need(part25["attainable_R"] == [112], "25 attainable")

    part34 = enumerate_partition_34()
    need(part34["covering_pairs"] == EXPECTED["partition_34_covering"], "34 covering")
    need(part34["min_R"] == EXPECTED["partition_34_min_R"], "34 min R")
    need(part34["histogram"] == EXPECTED["partition_34_histogram"], "34 hist")
    need(part34["attainable_R"] == [112], "34 attainable")

    champ = champion_analysis()
    need(champ["tariff_floor_at_X0"] == EXPECTED["tariff_floor_at_X0"], "tariff floor")
    need(champ["tariff_floor_at_X0"] > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(champ["champion_25"]["R"] == 112, "champ25 R")
    need(champ["champion_34"]["R"] == 112, "champ34 R")

    # Explicit dual recomputation on champions (not copied from constant).
    w25_a, w25_b = tuple(champ["champion_25"]["walks"][0]), tuple(
        champ["champion_25"]["walks"][1]
    )
    w34_a, w34_b = tuple(champ["champion_34"]["walks"][0]), tuple(
        champ["champion_34"]["walks"][1]
    )
    need(dual_R_short_long(even_table(w25_b), w25_a[1]) == 112, "recompute 25")
    need(
        dual_independent_R(even_table(w34_a), even_table(w34_b)) == 112,
        "recompute 34",
    )
    need(structural_25_identity(w25_a[1], w25_b)["R"] == 112, "recompute structural")

    # Same-walk baseline comparison: single even-subset floor is 82, not claimed here.
    need(EXPECTED["single_walk_even_min_R"] == 82, "baseline even floor constant")

    cert = {
        "schema_version": 1,
        "status": "PASS_INDEPENDENT_WALKS_7Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Partitioned independent dual walks at total Q=7 (valid restored "
            "lengths (2,5) and (3,4)): covering dual even-parity readout has "
            "exact R=112; tariff floor at X=0 is 490>436. Answers independent-"
            "walks OQ (partitioned case) after same-walk multi-connector."
        ),
        "claim": {
            "Q": 7,
            "partition_covering_min_R": 112,
            "partition_25_covering": part25["covering_pairs"],
            "partition_34_covering": part34["covering_pairs"],
            "partition_25_R_exact": 112,
            "partition_34_R_exact": 112,
            "tariff_floor_at_X0": EXPECTED["tariff_floor_at_X0"],
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "undercuts_436_after_complete_bill": False,
            "length1_walks_invalid": True,
            "answers_independent_walks_partitioned": True,
            "oq_answer": (
                "Every covering partitioned dual-walk schedule with total "
                "query count Q=n0+n1=7 (valid restored walks of lengths (2,5) "
                "or (3,4), distinct nonzero labels within each walk, "
                "independent dirt, dual even-parity readout) has exact R=112. "
                "At X=0 the abstract tariff is already 490>436; positive path "
                "X only increases the bill. Length-1 components are not "
                "restored (closed zero edge). Same-walk multi-connector remains "
                "the pending mc7q package; transfer-coupled schedules are out "
                "of scope here."
            ),
            "no_new_kappa": True,
        },
        "partition_2_plus_5": part25,
        "partition_3_plus_4": part34,
        "champion": champ,
        "length1_invalid_examples": length1,
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X",
            "at_R112_X0": tariff_qrx(7, 112, 0),
            "champion_25": tariff_qrx(
                7, 112, champ["champion_25"]["path_X"]
            ),
            "champion_34": tariff_qrx(
                7, 112, champ["champion_34"]["path_X"]
            ),
            "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        },
    }
    return cert


def compare_certificate(live, pinned):
    need(live["status"] == pinned["status"], "status")
    need(live["claim"] == pinned["claim"], "claim drift")
    need(
        live["partition_2_plus_5"]["covering_pairs"]
        == pinned["partition_2_plus_5"]["covering_pairs"],
        "25 covering drift",
    )
    need(
        live["partition_3_plus_4"]["covering_pairs"]
        == pinned["partition_3_plus_4"]["covering_pairs"],
        "34 covering drift",
    )
    need(
        live["partition_2_plus_5"]["histogram"]
        == pinned["partition_2_plus_5"]["histogram"],
        "25 hist drift",
    )
    need(
        live["partition_3_plus_4"]["histogram"]
        == pinned["partition_3_plus_4"]["histogram"],
        "34 hist drift",
    )
    need(live["tariff_check"] == pinned["tariff_check"], "tariff drift")
    need(live["champion"]["tariff_floor_at_X0"] == pinned["champion"]["tariff_floor_at_X0"], "floor")


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
        "PASS_INDEPENDENT_WALKS_7Q_OBSTRUCTION",
        f"partition_min_R={claim['partition_covering_min_R']}",
        f"covering_25={claim['partition_25_covering']}",
        f"covering_34={claim['partition_34_covering']}",
        f"tariff_floor={claim['tariff_floor_at_X0']}",
        f"endpoint={claim['endpoint_Q6_tariff']}",
        "no_undercut_partitioned_independent_walks",
        "answers_independent_walks_partitioned",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
