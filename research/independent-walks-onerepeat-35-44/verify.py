#!/usr/bin/env python3
"""One-repeat (3,5)/(4,4) partitioned independent-walks at Q=8; read-only default.

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
    census_one_repeat_35,
    census_one_repeat_44,
    champion_analysis,
    dual_independent_R,
    even_table,
    is_one_repeat_nonzero,
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
    need(not valid_restored_walk((0, 1, 1)), "length-3 one-repeat invalid")

    census35 = census_one_repeat_35()
    need(census35["covering_pairs"] == EXPECTED["partition_35_covering"], "35 covering")
    need(census35["min_R"] == EXPECTED["partition_35_min_R"], "35 min R")
    need(census35["histogram"] == EXPECTED["partition_35_histogram"], "35 hist")

    census44 = census_one_repeat_44()
    need(census44["covering_pairs"] == EXPECTED["partition_44_covering"], "44 covering")
    need(census44["min_R"] == EXPECTED["partition_44_min_R"], "44 min R")
    need(census44["histogram"] == EXPECTED["partition_44_histogram"], "44 hist")
    need(census44["both_one_repeat_covering"] == 0, "both-or")

    champ = champion_analysis()
    need(champ["tariff_floor_at_X0"] == EXPECTED["tariff_floor_at_X0"], "tariff floor")
    need(champ["tariff_floor_at_X0"] > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(champ["one_repeat_35_min_R"] > champ["distinct_35_min_R"], "worsens 35")
    need(champ["one_repeat_44_min_R"] > champ["distinct_44_min_R"], "worsens 44")

    w35_a, w35_b = EXPECTED["champion_35_walks"]
    w44_a, w44_b = EXPECTED["champion_44_walks"]
    need(is_one_repeat_nonzero(w35_b), "champ 35 one-repeat")
    need(is_one_repeat_nonzero(w44_a), "champ 44 one-repeat")
    need(dual_independent_R(even_table(w35_a), even_table(w35_b)) == 112, "recompute 35")
    need(dual_independent_R(even_table(w44_a), even_table(w44_b)) == 112, "recompute 44")

    cert = {
        "schema_version": 1,
        "status": "PASS_INDEPENDENT_WALKS_ONEREPEAT_35_44_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898) at "
            "(b,a,x)=(38,2,2). Freestanding one-repeat layers inside partitioned "
            "independent dual walks at total Q=8 on shapes (3,5) and (4,4): every "
            "covering dual has exact R=112; tariff floor at X=0 is 528>436. "
            "Answers independent-walks-onerepeat-8q OQ1 without editing leave-alones "
            "through #2851 or pending onerepeat-(2,6)."
        ),
        "claim": {
            "Q": 8,
            "partitions": [[3, 5], [4, 4]],
            "one_repeat_35_covering": EXPECTED["partition_35_covering"],
            "one_repeat_35_min_R": 112,
            "one_repeat_44_covering": EXPECTED["partition_44_covering"],
            "one_repeat_44_min_R": 112,
            "one_repeat_44_both_or_covering": 0,
            "distinct_35_min_R": 98,
            "distinct_44_min_R": 100,
            "tariff_floor_at_X0": EXPECTED["tariff_floor_at_X0"],
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "undercuts_436_after_complete_bill": False,
            "beats_distinct_98": False,
            "beats_distinct_100": False,
            "answers_independent_walks_onerepeat_8q_oq1": True,
            "oq_answer": (
                "One-repeat layers on partitions (3,5) and (4,4) at Q=8 do not "
                "improve on distinct-label floors R=98 / R=100. Every covering "
                "distinct-L3 × one-repeat-L5 dual has R=112 (covering 2499840; "
                "spectrum {112}); length-3 cannot itself host a one-repeat "
                "(closed zero edge). Every covering one-repeat-L4 × distinct-L4 "
                "dual has R=112 (covering 1666560; spectrum {112}); both-sides "
                "one-repeat never covers. At X=0 the abstract tariff is already "
                "528>436 under (b,a,x)=(38,2,2). Leave-alones through #2851 and "
                "pending independent-walks-onerepeat-8q are not reopened."
            ),
            "no_new_kappa": True,
        },
        "one_repeat_3_plus_5": census35,
        "one_repeat_4_plus_4": census44,
        "champion": champ,
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X",
            "at_R112_X0": tariff_qrx(8, 112, 0),
            "champion_35": tariff_qrx(8, 112, champ["champion_35"]["path_X"]),
            "champion_44": tariff_qrx(8, 112, champ["champion_44"]["path_X"]),
            "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
            "distinct_35_floor_at_R98_X0": tariff_qrx(8, 98, 0),
            "distinct_44_floor_at_R100_X0": tariff_qrx(8, 100, 0),
        },
    }
    return cert


def compare_certificate(live, pinned):
    need(live["status"] == pinned["status"], "status")
    need(live["claim"] == pinned["claim"], "claim drift")
    need(
        live["one_repeat_3_plus_5"]["covering_pairs"]
        == pinned["one_repeat_3_plus_5"]["covering_pairs"],
        "35 covering drift",
    )
    need(
        live["one_repeat_3_plus_5"]["histogram"]
        == pinned["one_repeat_3_plus_5"]["histogram"],
        "35 hist drift",
    )
    need(
        live["one_repeat_3_plus_5"]["min_R"] == pinned["one_repeat_3_plus_5"]["min_R"],
        "35 min drift",
    )
    need(
        live["one_repeat_4_plus_4"]["covering_pairs"]
        == pinned["one_repeat_4_plus_4"]["covering_pairs"],
        "44 covering drift",
    )
    need(
        live["one_repeat_4_plus_4"]["histogram"]
        == pinned["one_repeat_4_plus_4"]["histogram"],
        "44 hist drift",
    )
    need(
        live["one_repeat_4_plus_4"]["min_R"] == pinned["one_repeat_4_plus_4"]["min_R"],
        "44 min drift",
    )
    need(
        live["one_repeat_4_plus_4"]["both_one_repeat_covering"]
        == pinned["one_repeat_4_plus_4"]["both_one_repeat_covering"],
        "both-or drift",
    )
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
        "PASS_INDEPENDENT_WALKS_ONEREPEAT_35_44_OBSTRUCTION",
        f"one_repeat_35_min_R={claim['one_repeat_35_min_R']}",
        f"one_repeat_44_min_R={claim['one_repeat_44_min_R']}",
        f"covering_35={claim['one_repeat_35_covering']}",
        f"covering_44={claim['one_repeat_44_covering']}",
        f"tariff_floor={claim['tariff_floor_at_X0']}",
        "answers_independent_walks_onerepeat_8q_oq1",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
