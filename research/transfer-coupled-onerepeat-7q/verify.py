#!/usr/bin/env python3
"""One-repeat transfer-coupled (5,1,1) obstruction at Q=7; read-only default.

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
    champion_checks,
    dual_R_from_walks,
    full_census,
    is_one_repeat,
    need,
    tariff_qrx,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"


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
    champs = champion_checks()
    census = full_census()
    floor = tariff_qrx(7, 96, 0, 1)
    need(floor == 459, "floor 459")
    need(floor > 436, "no undercut")
    need(census["prefix_dup"]["min_R"] == 98, "P min")
    need(census["suffix_hit"]["min_R"] == 96, "S min")

    for key in ("prefix_dup_champion", "suffix_hit_champion"):
        ch = EXPECTED[key]
        pref = tuple(ch["prefix"])
        sa = tuple(ch["suf_a"])
        sb = tuple(ch["suf_b"])
        need(is_one_repeat(pref, sa[0], sb[0]), key)
        need(dual_R_from_walks(pref + sa, pref + sb) == ch["R"], f"recompute {key}")

    return {
        "schema_version": 1,
        "status": "PASS_TRANSFER_COUPLED_ONEREPEAT_7Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Transfer-coupled dual at shape (5,1,1) with exactly one repeated "
            "nonzero label among the six nonzero schedule slots (prefix-internal "
            "double, or one suffix colliding with a distinct prefix), divergent "
            "suffixes, transfer C>=1, independent dirt, dual even-parity readout. "
            "Answers #2836 OQ1 (non-distinct / one-repeat layer)."
        ),
        "claim": {
            "Q": 7,
            "shape": [5, 1, 1],
            "transfer_C_min": 1,
            "distinct_label_min_R": 84,
            "one_repeat_min_R": 96,
            "prefix_dup_min_R": 98,
            "suffix_hit_min_R": 96,
            "combined_covering": 4166400,
            "tariff_floor_after_complete_bill": 459,
            "endpoint_Q6_tariff": 436,
            "undercuts_436_after_complete_bill": False,
            "improves_on_distinct_R84": False,
            "answers_all_shapes_oq1_onerepeat": True,
            "oq_answer": (
                "Every covering one-repeat transfer-coupled (5,1,1) dual has "
                "R>=96 (suffix-hit layer; all 1666560 covering pairs at R=96) or "
                "R=98 (prefix-dup layer; all 2499840 covering pairs). Combined "
                "min R=96 > distinct-label min R=84. Abstract tariff at X=0,C=1 "
                "is 38*7+2*96+1=459>436. One-repeat layers do not improve on the "
                "distinct-label floor and cannot undercut the six-query endpoint."
            ),
            "no_new_kappa": True,
        },
        "prefix_dup": census["prefix_dup"],
        "suffix_hit": census["suffix_hit"],
        "champion_checks": champs,
        "tariff": {
            "formula": "38*Q + 2*R + 2*X + C",
            "at_min_R_X0_C1": floor,
            "endpoint_Q6": 436,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args(argv)

    check_source_pins()
    cert = build_certificate()

    if args.write_certificate:
        CERT_PATH.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
        print(f"WROTE {CERT_PATH}")
    else:
        pinned = load_json_reject_duplicates(CERT_PATH)
        need(pinned["status"] == cert["status"], "certificate status drift")
        need(pinned["claim"] == cert["claim"], "certificate claim drift")
        need(
            pinned["prefix_dup"]["min_R"] == cert["prefix_dup"]["min_R"],
            "prefix_dup drift",
        )
        need(
            pinned["suffix_hit"]["min_R"] == cert["suffix_hit"]["min_R"],
            "suffix_hit drift",
        )
        need(
            pinned["prefix_dup"]["covering_pairs"] == cert["prefix_dup"]["covering_pairs"],
            "prefix covering drift",
        )
        need(
            pinned["suffix_hit"]["covering_pairs"] == cert["suffix_hit"]["covering_pairs"],
            "suffix covering drift",
        )

    print(
        "PASS_TRANSFER_COUPLED_ONEREPEAT_7Q_OBSTRUCTION "
        f"combined_min_R={cert['claim']['one_repeat_min_R']} "
        f"covering={cert['claim']['combined_covering']} "
        f"tariff_floor={cert['claim']['tariff_floor_after_complete_bill']} "
        "answers_all_shapes_oq1_onerepeat no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
