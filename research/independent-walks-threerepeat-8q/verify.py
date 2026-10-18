#!/usr/bin/env python3
"""Three-repeat partitioned independent-walks at Q=8; read-only default.

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
    census_three_repeat_26,
    census_three_repeat_35,
    census_three_repeat_44,
    champion_analysis,
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
    need(not valid_restored_walk((0, 1, 1, 1, 1)), "length-5 three-repeat invalid")

    census26 = census_three_repeat_26()
    need(census26["covering_pairs"] == EXPECTED["partition_26_covering"], "26 covering")
    need(census26["valid_walks"] == EXPECTED["partition_26_valid_walks"], "26 walks")
    need(census26["shape_32"] == EXPECTED["partition_26_shape_32"], "32")
    need(census26["shape_41"] == EXPECTED["partition_26_shape_41"], "41")

    census35 = census_three_repeat_35()
    need(census35["covering_pairs"] == EXPECTED["partition_35_covering"], "35 covering")
    need(
        census35["long_multisets"] == EXPECTED["partition_35_valid_multisets"],
        "35 multisets",
    )

    census44 = census_three_repeat_44()
    need(census44["covering_pairs"] == EXPECTED["partition_44_covering"], "44 covering")
    need(
        census44["valid_three_repeat_l4_walks"] == EXPECTED["partition_44_valid_walks"],
        "44 walks",
    )

    champ = champion_analysis()
    need(champ["covering_any_partition"] is False, "no covering")
    need(champ["undercuts_436_after_complete_bill"] is False, "no undercut")
    need(champ["tariff_floor_at_X0"] is None, "no R floor")

    cert = {
        "schema_version": 1,
        "status": "PASS_INDEPENDENT_WALKS_THREEREPEAT_8Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898) at "
            "(b,a,x)=(38,2,2). Freestanding three-repeat (excess-3) layers inside "
            "partitioned independent dual walks at total Q=8 on shapes (2,6), "
            "(3,5), and (4,4): every dual has covering count 0; no dirt-legal "
            "covering schedule exists, so none undercuts tariff 436. Answers "
            "preferred next19 / shared-dirt OQ1 (fifth priced alphabet) without "
            "editing leave-alones through #2861/#2860/#2858/#2851 or pending "
            "shared-dirt tip."
        ),
        "claim": {
            "Q": 8,
            "partitions": [[2, 6], [3, 5], [4, 4]],
            "alphabet": "three_repeat_partitioned_independent_dual",
            "three_repeat_26_covering": 0,
            "three_repeat_26_valid_walks": EXPECTED["partition_26_valid_walks"],
            "three_repeat_26_shape_32": EXPECTED["partition_26_shape_32"],
            "three_repeat_26_shape_41": EXPECTED["partition_26_shape_41"],
            "three_repeat_35_covering": 0,
            "three_repeat_35_valid_multisets": EXPECTED["partition_35_valid_multisets"],
            "three_repeat_44_covering": 0,
            "three_repeat_44_valid_walks": 0,
            "covering_min_R": None,
            "tariff_floor_at_X0": None,
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "undercuts_436_after_complete_bill": False,
            "beats_distinct_floors": False,
            "answers_fifth_priced_alphabet_q8": True,
            "answers_shared_dirt_oq1_fifth_alphabet": True,
            "soft_overlap_shared_dirt": "safe_independent_excess_axis_not_dirt_coupling",
            "oq_answer": (
                "The named fifth priced readout alphabet under PR1898 "
                "(b,a,x)=(38,2,2) beyond same-walk / dirty-shadow / partitioned "
                "dual / one-repeat / two-repeat / shared-dirt is the three-repeat "
                "(excess-3) companion of partitioned independent duals at Q=8. "
                "Exact covering census: (2,6) covering 0 on 930 valid longs "
                "(only shape {3,2}; {4,1} never restores; span ≤4 so coset union "
                "≤8); (3,5) covering 0 because shape {d:4} never restores; (4,4) "
                "covering 0 because excess 3 is impossible on length-4 (max "
                "excess 2). No covering R exists, so the alphabet cannot undercut "
                "tariff 436 after a complete dirty bill. Leave-alones through "
                "#2861/#2860/#2858/#2851 and pending shared-dirt tip are not "
                "reopened; soft-overlap with shared-dirt is avoided (excess axis, "
                "independent dirt)."
            ),
            "no_new_kappa": True,
        },
        "three_repeat_2_plus_6": census26,
        "three_repeat_3_plus_5": census35,
        "three_repeat_4_plus_4": census44,
        "champion": champ,
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X",
            "three_repeat_covering_floor": None,
            "distinct_26_at_R92_X0": tariff_qrx(8, 92, 0),
            "one_repeat_at_R112_X0": tariff_qrx(8, 112, 0),
            "shared_dirt_at_R82_X0": tariff_qrx(8, 82, 0),
            "endpoint_Q6": EXPECTED["endpoint_tariff_Q6"],
        },
    }
    return cert


def compare_certificate(live, pinned):
    need(live["status"] == pinned["status"], "status")
    need(live["claim"] == pinned["claim"], "claim drift")
    need(
        live["three_repeat_2_plus_6"]["covering_pairs"]
        == pinned["three_repeat_2_plus_6"]["covering_pairs"],
        "26 covering drift",
    )
    need(
        live["three_repeat_2_plus_6"]["valid_walks"]
        == pinned["three_repeat_2_plus_6"]["valid_walks"],
        "26 walks drift",
    )
    need(
        live["three_repeat_3_plus_5"]["covering_pairs"]
        == pinned["three_repeat_3_plus_5"]["covering_pairs"],
        "35 covering drift",
    )
    need(
        live["three_repeat_3_plus_5"]["long_multisets"]
        == pinned["three_repeat_3_plus_5"]["long_multisets"],
        "35 multisets drift",
    )
    need(
        live["three_repeat_4_plus_4"]["covering_pairs"]
        == pinned["three_repeat_4_plus_4"]["covering_pairs"],
        "44 covering drift",
    )
    need(
        live["three_repeat_4_plus_4"]["valid_three_repeat_l4_walks"]
        == pinned["three_repeat_4_plus_4"]["valid_three_repeat_l4_walks"],
        "44 walks drift",
    )
    need(live["tariff_check"] == pinned["tariff_check"], "tariff drift")
    need(
        live["champion"]["undercuts_436_after_complete_bill"]
        == pinned["champion"]["undercuts_436_after_complete_bill"],
        "undercut drift",
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
        "PASS_INDEPENDENT_WALKS_THREEREPEAT_8Q_OBSTRUCTION",
        f"covering_26={claim['three_repeat_26_covering']}",
        f"covering_35={claim['three_repeat_35_covering']}",
        f"covering_44={claim['three_repeat_44_covering']}",
        f"valid_26={claim['three_repeat_26_valid_walks']}",
        "answers_fifth_priced_alphabet_q8",
        "no_undercut_436",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
