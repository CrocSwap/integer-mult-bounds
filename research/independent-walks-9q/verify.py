#!/usr/bin/env python3
"""Partitioned independent-walks obstruction at Q=9; read-only default.

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
    enumerate_partition_27,
    enumerate_partition_36,
    enumerate_partition_45,
    even_table,
    length1_invalid_examples,
    quick_checks,
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

    part27 = enumerate_partition_27()
    need(part27["covering_pairs"] == EXPECTED["partition_27_covering"], "27 covering")
    need(part27["min_R"] == EXPECTED["partition_27_min_R"], "27 min R")
    need(part27["histogram"] == EXPECTED["partition_27_histogram"], "27 hist")

    part36 = enumerate_partition_36()
    need(part36["covering_pairs"] == EXPECTED["partition_36_covering"], "36 covering")
    need(part36["min_R"] == EXPECTED["partition_36_min_R"], "36 min R")
    need(part36["histogram"] == EXPECTED["partition_36_histogram"], "36 hist")

    part45 = enumerate_partition_45()
    need(part45["covering_pairs"] == EXPECTED["partition_45_covering"], "45 covering")
    need(part45["min_R"] == EXPECTED["partition_45_min_R"], "45 min R")
    need(part45["histogram"] == EXPECTED["partition_45_histogram"], "45 hist")

    partition_min = min(part27["min_R"], part36["min_R"], part45["min_R"])
    need(partition_min == EXPECTED["partition_min_R"] == 80, "global partition min")

    champ = champion_analysis()
    need(champ["tariff_floor_at_X0"] == EXPECTED["tariff_floor_at_X0"], "tariff floor")
    need(champ["tariff_floor_at_X0"] > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(champ["champion_27"]["R"] == 80, "champ27 R")
    need(champ["champion_36"]["R"] == 88, "champ36 R")
    need(champ["champion_45"]["R"] == 92, "champ45 R")

    w27_a, w27_b = tuple(champ["champion_27"]["walks"][0]), tuple(
        champ["champion_27"]["walks"][1]
    )
    w36_a, w36_b = tuple(champ["champion_36"]["walks"][0]), tuple(
        champ["champion_36"]["walks"][1]
    )
    w45_a, w45_b = tuple(champ["champion_45"]["walks"][0]), tuple(
        champ["champion_45"]["walks"][1]
    )
    need(dual_R_short_long(even_table(w27_b), w27_a[1]) == 80, "recompute 27")
    need(
        dual_independent_R(even_table(w36_a), even_table(w36_b)) == 88,
        "recompute 36",
    )
    need(
        dual_independent_R(even_table(w45_a), even_table(w45_b)) == 92,
        "recompute 45",
    )
    need(EXPECTED["same_walk_q9_floor"] == 466, "same-walk Q9 floor constant")

    cert = {
        "schema_version": 1,
        "status": "PASS_INDEPENDENT_WALKS_9Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898) at "
            "(b,a,x)=(38,2,2). Freestanding partitioned independent dual walks "
            "at total Q=9 (valid restored lengths (2,7), (3,6), (4,5)): covering "
            "dual even-parity readout has global min R=80 at (2,7); tariff floor "
            "at X=0 is 502>436 (also above same-walk Q=9 floor 466 of #2677). "
            "Answers preferred next20 / threerepeat OQ2 without editing "
            "leave-alones through #2867 or pending three-repeat tip."
        ),
        "claim": {
            "Q": 9,
            "partition_covering_min_R": 80,
            "partition_27_covering": part27["covering_pairs"],
            "partition_36_covering": part36["covering_pairs"],
            "partition_45_covering": part45["covering_pairs"],
            "partition_27_min_R": 80,
            "partition_36_min_R": 88,
            "partition_45_min_R": 92,
            "tariff_floor_at_X0": EXPECTED["tariff_floor_at_X0"],
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "same_walk_q9_floor": EXPECTED["same_walk_q9_floor"],
            "undercuts_436_after_complete_bill": False,
            "length1_walks_invalid": True,
            "answers_priced_alphabet_q9_companion": True,
            "answers_threerepeat_oq2": True,
            "oq_answer": (
                "Every covering partitioned dual-walk schedule with total "
                "query count Q=n0+n1=9 (valid restored walks of lengths (2,7), "
                "(3,6), or (4,5), distinct nonzero labels within each walk, "
                "independent dirt, dual even-parity readout) has R≥80, attained "
                "only on (2,7) (spectrum {80,82,86,88,92,100}; covering "
                "20512576). Partitions (3,6) and (4,5) have min R 88 and 92. At "
                "X=0 the abstract tariff is already 502>436 under "
                "(b,a,x)=(38,2,2), and also above the same-walk Q=9 floor 466 of "
                "#2677; positive path X only increases the bill. Length-1 "
                "components are not restored. Leave-alones through #2867 and "
                "pending three-repeat tip are not reopened."
            ),
            "no_new_kappa": True,
        },
        "partition_2_plus_7": part27,
        "partition_3_plus_6": part36,
        "partition_4_plus_5": part45,
        "champion": champ,
        "length1_invalid_examples": length1,
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X",
            "at_R80_X0": tariff_qrx(9, 80, 0),
            "champion_27": tariff_qrx(9, 80, champ["champion_27"]["path_X"]),
            "champion_36": tariff_qrx(9, 88, champ["champion_36"]["path_X"]),
            "champion_45": tariff_qrx(9, 92, champ["champion_45"]["path_X"]),
            "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
            "same_walk_q9_floor": EXPECTED["same_walk_q9_floor"],
        },
    }
    return cert


def compare_certificate(live, pinned):
    need(live["status"] == pinned["status"], "status")
    need(live["claim"] == pinned["claim"], "claim drift")
    for key in (
        "partition_2_plus_7",
        "partition_3_plus_6",
        "partition_4_plus_5",
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


def compare_quick(pinned):
    quick = quick_checks()
    claim = pinned["claim"]
    need(claim["partition_covering_min_R"] == 80, "pinned min R")
    need(claim["tariff_floor_at_X0"] == 502, "pinned floor")
    need(claim["undercuts_436_after_complete_bill"] is False, "pinned undercut")
    need(claim["answers_threerepeat_oq2"] is True, "pinned oq2")
    need(quick["champion"]["champion_27"]["R"] == 80, "quick champ 27")
    need(quick["champion"]["champion_36"]["R"] == 88, "quick champ 36")
    need(quick["champion"]["champion_45"]["R"] == 92, "quick champ 45")
    need(
        quick["champion"]["tariff_floor_at_X0"] == claim["tariff_floor_at_X0"],
        "quick floor match",
    )
    need(
        pinned["tariff_check"]["at_R80_X0"] == tariff_qrx(9, 80, 0) == 502,
        "tariff arithmetic",
    )
    need(
        pinned["partition_2_plus_7"]["covering_pairs"]
        == EXPECTED["partition_27_covering"],
        "pinned 27 covering constant",
    )
    need(
        pinned["partition_3_plus_6"]["covering_pairs"]
        == EXPECTED["partition_36_covering"],
        "pinned 36 covering constant",
    )
    need(
        pinned["partition_4_plus_5"]["covering_pairs"]
        == EXPECTED["partition_45_covering"],
        "pinned 45 covering constant",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite CERTIFICATE.json (maintenance only)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="champion/tariff/pin checks without full census",
    )
    args = parser.parse_args(argv)

    check_source_pins()
    pinned = load_json_reject_duplicates(CERT_PATH)

    if args.quick:
        compare_quick(pinned)
        claim = pinned["claim"]
        print(
            "PASS_INDEPENDENT_WALKS_9Q_QUICK",
            f"partition_min_R={claim['partition_covering_min_R']}",
            f"tariff_floor={claim['tariff_floor_at_X0']}",
            f"endpoint={claim['endpoint_Q6_tariff']}",
            "answers_threerepeat_oq2",
            "no_undercut_partitioned_independent_walks_q9",
            "no_new_kappa",
        )
        return 0

    live = build_certificate()

    if args.write_certificate:
        CERT_PATH.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
        print("WROTE_CERTIFICATE", CERT_PATH)
        return 0

    compare_certificate(live, pinned)
    claim = pinned["claim"]
    print(
        "PASS_INDEPENDENT_WALKS_9Q_OBSTRUCTION",
        f"partition_min_R={claim['partition_covering_min_R']}",
        f"covering_27={claim['partition_27_covering']}",
        f"covering_36={claim['partition_36_covering']}",
        f"covering_45={claim['partition_45_covering']}",
        f"tariff_floor={claim['tariff_floor_at_X0']}",
        f"endpoint={claim['endpoint_Q6_tariff']}",
        "no_undercut_partitioned_independent_walks_q9",
        "answers_priced_alphabet_q9_companion",
        "answers_threerepeat_oq2",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
