#!/usr/bin/env python3
"""One-repeat partitioned independent-walks obstruction at Q=8; read-only default.

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
    census_one_repeat_26,
    champion_analysis,
    dual_R_short_long,
    even_table,
    is_one_repeat_long,
    structural_rank4_outside,
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

    census = census_one_repeat_26()
    need(census["covering_pairs"] == EXPECTED["covering_pairs"], "covering")
    need(census["min_R"] == EXPECTED["min_R"], "min R")
    need(census["histogram"] == EXPECTED["histogram"], "hist")
    need(census["valid_one_repeat_walks"] == EXPECTED["valid_one_repeat_walks"], "valid")
    need(
        census["rank4_one_repeat_walks"] == EXPECTED["rank4_one_repeat_walks"],
        "rank4",
    )
    need(
        census["valid_rank_lt4_walks"] == EXPECTED["valid_rank_lt4_walks"],
        "rank_lt4",
    )
    need(census["covering_rank_lt4"] == 0, "rank<4 never covers")

    champ = champion_analysis()
    need(champ["tariff_floor_at_X0"] == EXPECTED["tariff_floor_at_X0"], "tariff floor")
    need(champ["tariff_floor_at_X0"] > EXPECTED["endpoint_tariff_Q6"], "no undercut")
    need(champ["one_repeat_min_R"] > champ["distinct_partition_26_min_R"], "worsens")

    w_short, w_long = EXPECTED["champion_walks"]
    need(is_one_repeat_long(w_long), "champ one-repeat")
    need(dual_R_short_long(even_table(w_long), w_short[1]) == 112, "recompute R")
    need(structural_rank4_outside(w_short[1], w_long)["R"] == 112, "recompute struct")

    cert = {
        "schema_version": 1,
        "status": "PASS_INDEPENDENT_WALKS_ONEREPEAT_8Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898) at "
            "(b,a,x)=(38,2,2). Freestanding one-repeat layer inside partitioned "
            "independent dual walks at total Q=8 on the (2,6) Hamilton champion "
            "shape: every covering one-repeat length-6 long walk paired with "
            "short (0,σ) has exact R=112; tariff floor at X=0 is 528>436. "
            "Answers independent-walks-8q OQ1 without editing leave-alones "
            "through #2846 or pending iw8q."
        ),
        "claim": {
            "Q": 8,
            "partition": [2, 6],
            "one_repeat_covering": EXPECTED["covering_pairs"],
            "one_repeat_min_R": 112,
            "valid_one_repeat_walks": EXPECTED["valid_one_repeat_walks"],
            "rank4_one_repeat_walks": EXPECTED["rank4_one_repeat_walks"],
            "valid_rank_lt4_walks": EXPECTED["valid_rank_lt4_walks"],
            "covering_rank_lt4": 0,
            "distinct_partition_26_min_R": 92,
            "tariff_floor_at_X0": EXPECTED["tariff_floor_at_X0"],
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "undercuts_436_after_complete_bill": False,
            "beats_distinct_92": False,
            "answers_independent_walks_8q_oq1_onerepeat": True,
            "oq_answer": (
                "Every covering one-repeat partitioned dual on shape (2,6) "
                "(short walk (0,σ); long walk of length 6 whose five nonzero "
                "slots contain exactly one repeated nonzero label; independent "
                "dirt; dual even-parity readout) has R=112 exactly (covering "
                "59996160; spectrum {112}). Only rank-4 longs cover, always "
                "with Σe=40 and σ outside the long span (16 choices), so "
                "R=2·40+32=112 by the rank-4-outside identity; all 781200 "
                "rank<4 valid longs are admitted with covering_rank_lt4=0. "
                "Distinct-label "
                "(2,6) floor R=92 is not improved. At X=0 the abstract tariff "
                "is already 528>436 under (b,a,x)=(38,2,2). Leave-alones "
                "through #2846 and pending independent-walks-8q are not "
                "reopened."
            ),
            "no_new_kappa": True,
        },
        "one_repeat_2_plus_6": census,
        "champion": champ,
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X",
            "at_R112_X0": tariff_qrx(8, 112, 0),
            "champion": tariff_qrx(8, 112, champ["champion"]["path_X"]),
            "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
            "distinct_26_floor_at_R92_X0": tariff_qrx(8, 92, 0),
        },
    }
    return cert


def compare_certificate(live, pinned):
    need(live["status"] == pinned["status"], "status")
    need(live["claim"] == pinned["claim"], "claim drift")
    need(
        live["one_repeat_2_plus_6"]["covering_pairs"]
        == pinned["one_repeat_2_plus_6"]["covering_pairs"],
        "covering drift",
    )
    need(
        live["one_repeat_2_plus_6"]["valid_rank_lt4_walks"]
        == pinned["one_repeat_2_plus_6"]["valid_rank_lt4_walks"],
        "rank_lt4 drift",
    )
    need(
        live["one_repeat_2_plus_6"]["covering_rank_lt4"]
        == pinned["one_repeat_2_plus_6"]["covering_rank_lt4"]
        == 0,
        "rank_lt4 cover drift",
    )
    need(
        live["one_repeat_2_plus_6"]["histogram"]
        == pinned["one_repeat_2_plus_6"]["histogram"],
        "hist drift",
    )
    need(
        live["one_repeat_2_plus_6"]["min_R"] == pinned["one_repeat_2_plus_6"]["min_R"],
        "min drift",
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
        "PASS_INDEPENDENT_WALKS_ONEREPEAT_8Q_OBSTRUCTION",
        f"one_repeat_min_R={claim['one_repeat_min_R']}",
        f"covering={claim['one_repeat_covering']}",
        f"tariff_floor={claim['tariff_floor_at_X0']}",
        f"distinct_26_min_R={claim['distinct_partition_26_min_R']}",
        "answers_independent_walks_8q_oq1_onerepeat",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
