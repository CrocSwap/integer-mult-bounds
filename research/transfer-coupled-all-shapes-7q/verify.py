#!/usr/bin/env python3
"""Transfer-coupled dual obstruction at Q=7; read-only default.

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
    SHAPES,
    census_all_shapes,
    census_shape,
    champion_checks,
    dual_R_from_walks,
    fair_path_X,
    need,
    shape_key,
    tariff_qrx,
    walk_slots,
    x0_covering_count_511,
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


def build_certificate(include_companions: bool):
    x0 = x0_covering_count_511()
    need(x0["covering"] == EXPECTED["x0_covering_511"], "X=0 covering must be 0")

    champs = champion_checks()

    crit = census_shape(5, 1, 1)
    need(crit["min_R"] == 84, "critical min R")
    need(crit["covering_pairs"] == EXPECTED["shapes"]["5_1_1"]["covering"], "511 cov")
    need(crit["histogram"] == EXPECTED["shapes"]["5_1_1"]["histogram"], "511 hist")

    second = census_shape(4, 1, 2)
    need(second["min_R"] == 86, "second min R")
    need(second["covering_pairs"] == EXPECTED["shapes"]["4_1_2"]["covering"], "412 cov")
    need(second["histogram"] == EXPECTED["shapes"]["4_1_2"]["histogram"], "412 hist")

    companions = None
    if include_companions:
        rest = [s for s in SHAPES if s not in ((5, 1, 1), (4, 1, 2))]
        companions = census_all_shapes(shapes=rest)
        for p, a, b in rest:
            key = shape_key(p, a, b)
            need(companions[key]["min_R"] == EXPECTED["shapes"][key]["min_R"], key)

    need(EXPECTED["min_even_path_X_for_covering"] == 2, "even X step")
    floor = tariff_qrx(7, 84, 2, 1)
    need(floor == 439, "floor 439")
    need(floor > 436, "no undercut")
    need(tariff_qrx(7, 86, 0, 1) == 439, "R86 floor")

    ch = EXPECTED["shapes"]["5_1_1"]["champion"]
    pref = tuple(ch["prefix"])
    sa = tuple(ch["suf_a"])
    sb = tuple(ch["suf_b"])
    need(dual_R_from_walks(walk_slots(pref, sa), walk_slots(pref, sb)) == 84, "recompute")
    need(fair_path_X(pref, sa, sb) is not None, "fair X defined")

    return {
        "schema_version": 1,
        "status": "PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Transfer-coupled dual walks at total Q=p+a+b=7 with shared prefix "
            "length p, divergent suffixes a,b, transfer surcharge C>=1, "
            "independent dirt, dual even-parity readout, and fair shared-prefix "
            "XOR billing. Answers #2779 OQ1 (transfer-coupled)."
        ),
        "claim": {
            "Q": 7,
            "transfer_C_min": 1,
            "global_covering_min_R": 84,
            "global_min_shape": [5, 1, 1],
            "second_min_R": 86,
            "second_min_shape": [4, 1, 2],
            "x0_covering_on_511": 0,
            "path_X_even": True,
            "covering_implies_X_ge_2_on_critical": True,
            "tariff_floor_after_complete_bill": 439,
            "endpoint_Q6_tariff": 436,
            "undercuts_436_after_complete_bill": False,
            "answers_independent_walks_transfer_coupled": True,
            "oq_answer": (
                "Every covering transfer-coupled dual at Q=p+a+b=7 (distinct "
                "labels, disjoint private suffixes, independent dirt, dual "
                "even-parity) has min R >= 84, attained only at shape (5,1,1). "
                "All other unordered shapes have min R >= 86, already giving "
                "tariff >= 439 at X=0 with C=1. On (5,1,1), Gray X=0 covering "
                "is empty, and fair path X is always even, so covering forces "
                "X >= 2 and tariff >= 38*7 + 2*84 + 2*2 + 1 = 439 > 436. "
                "Partitioned independent walks (#2779) remain at R=112; "
                "same-walk even-subset remains at R=82."
            ),
            "no_new_kappa": True,
        },
        "x0_lemma_511": x0,
        "critical_5_1_1": crit,
        "second_4_1_2": second,
        "companion_shapes": companions,
        "champions": champs,
        "unit_tariff": {"b": 38, "a": 2, "x": 2, "transfer_C": 1},
        "comparisons": {
            "partitioned_independent_min_R": EXPECTED["partitioned_min_R"],
            "same_walk_even_min_R": EXPECTED["same_walk_even_min_R"],
            "hypothetical_R84_X0_C1": 435,
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--write",
        action="store_true",
        help="rewrite CERTIFICATE.json (authoring; use with --full once)",
    )
    ap.add_argument(
        "--full",
        action="store_true",
        help="also census companion shapes (authoring / optional)",
    )
    ap.add_argument(
        "--quick",
        action="store_true",
        help="alias for default admission (critical+second only)",
    )
    args = ap.parse_args(argv)

    check_source_pins()
    include_companions = bool(args.full) or bool(args.write)
    pinned = None
    if not args.write:
        # Fail-fast on pinned claim / structure before the multi-minute census.
        pinned = load_json_reject_duplicates(CERT_PATH)
        need(pinned.get("status") == "PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION", "status")
        need(pinned["claim"]["global_covering_min_R"] == 84, "pinned global min R")
        need(pinned["claim"]["tariff_floor_after_complete_bill"] == 439, "pinned floor")
        need(pinned["claim"]["undercuts_436_after_complete_bill"] is False, "no undercut")
        need(pinned["claim"]["no_new_kappa"] is True, "no new kappa")
        need(pinned["x0_lemma_511"]["covering"] == 0, "pinned X0")
        need(pinned["critical_5_1_1"]["min_R"] == 84, "pinned 511")
        need(pinned["second_4_1_2"]["min_R"] == 86, "pinned 412")
        need(isinstance(pinned.get("companion_shapes"), dict), "pinned companions present")
        for p, a, b in SHAPES:
            if (p, a, b) in ((5, 1, 1), (4, 1, 2)):
                continue
            key = shape_key(p, a, b)
            need(key in pinned["companion_shapes"], f"missing pinned {key}")
            need(
                pinned["companion_shapes"][key]["min_R"]
                == EXPECTED["shapes"][key]["min_R"],
                f"pinned {key} min",
            )

    cert = build_certificate(include_companions=include_companions)

    if args.write:
        CERT_PATH.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
        pinned = load_json_reject_duplicates(CERT_PATH)

    need(pinned is not None, "certificate missing")

    need(pinned["status"] == cert["status"], "certificate status")
    need(
        pinned["critical_5_1_1"]["covering_pairs"]
        == cert["critical_5_1_1"]["covering_pairs"],
        "511 cov match",
    )
    need(
        pinned["second_4_1_2"]["covering_pairs"]
        == cert["second_4_1_2"]["covering_pairs"],
        "412 cov match",
    )
    if include_companions:
        for p, a, b in SHAPES:
            if (p, a, b) in ((5, 1, 1), (4, 1, 2)):
                continue
            key = shape_key(p, a, b)
            need(
                pinned["companion_shapes"][key]["min_R"]
                == cert["companion_shapes"][key]["min_R"],
                f"live {key}",
            )
            need(
                pinned["companion_shapes"][key]["covering_pairs"]
                == cert["companion_shapes"][key]["covering_pairs"],
                f"live {key} cov",
            )

    print(
        "PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION",
        f"global_min_R={cert['claim']['global_covering_min_R']}",
        f"shape={tuple(cert['claim']['global_min_shape'])}",
        f"tariff_floor={cert['claim']['tariff_floor_after_complete_bill']}",
        "x0_covering=0",
        "answers_independent_walks_transfer_coupled",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
