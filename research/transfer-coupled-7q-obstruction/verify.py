#!/usr/bin/env python3
"""Transfer-coupled (5,1,1) obstruction at Q=7; read-only default.

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
    champion_recompute,
    dual_independent_R,
    enumerate_511,
    even_table_nz5,
    fair_X,
    other_shape_samples,
    r_undercut_threshold,
    tariff_qrx,
    transfer_C_controls,
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
    census = enumerate_511()
    need(census["covering_pairs"] == EXPECTED["covering_pairs"], "covering count")
    need(census["min_R"] == EXPECTED["min_R"], "min R")
    need(census["histogram"] == EXPECTED["histogram"], "histogram")
    need(census["attainable_R"] == EXPECTED["attainable_R"], "attainable R")
    need(census["n_R84"] == EXPECTED["n_R84"], "n R84")
    need(census["min_fair_X_at_R84"] == EXPECTED["min_fair_X_at_R84"], "min fair X")
    need(census["tariff_floor"] == EXPECTED["tariff_floor"], "tariff floor")
    need(census["tariff_floor"] > EXPECTED["endpoint_tariff_Q6"], "no undercut")

    champ = champion_recompute()
    need(champ["R"] == 84 and champ["fair_X"] == 9, "champion recompute")

    # Explicit dual recomputation (not copied from constant).
    prefix = tuple(champ["prefix"])
    a, b = champ["tips"]
    r = dual_independent_R(
        even_table_nz5(prefix[1:] + (a,)), even_table_nz5(prefix[1:] + (b,))
    )
    need(r == 84, "explicit dual")
    need(fair_X(prefix, a, b, C=1) == 9, "explicit fair X")

    controls = transfer_C_controls()
    need(controls["C0_rejected_by_need"], "C=0 must be rejected")
    need(controls["C1_fair_X"] == 9, "C=1 control")

    samples = other_shape_samples()
    need(samples["threshold_R_plus_X"] == 85, "undercut threshold")
    for key in ("shape_4_1_2", "shape_3_2_2", "shape_3_1_3"):
        obs = samples[key]["min_R_observed"]
        need(obs is not None and obs >= 86, f"{key} sample min R")

    need(tariff_qrx(7, 84, 9) == 452, "tariff arithmetic")
    # Endpoint 436 is the PR1898 six-query complete-call pin (not re-derived here).
    need(EXPECTED["endpoint_tariff_Q6"] == 436, "endpoint pin")
    need(tariff_qrx(7, 84, 9) > 436, "floor above endpoint")

    return {
        "schema_version": 1,
        "status": "PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Transfer-coupled dual at Q=7 with shape (p,a,b)=(5,1,1): shared "
            "prefix length 5, priced transfer C>=1, divergent length-1 tips, "
            "independent dirt, dual even-parity readout, fair shared-prefix XOR "
            "billing. Covering min R=84; min fair X at R=84 is 9; tariff floor "
            "452>436. Answers transfer-coupled OQ for the maximal-sharing fork."
        ),
        "claim": {
            "Q": 7,
            "shape": [5, 1, 1],
            "covering_pairs": census["covering_pairs"],
            "min_R": 84,
            "min_fair_X_at_R84": 9,
            "tariff_floor": 452,
            "endpoint_Q6_tariff": 436,
            "undercuts_436_after_complete_bill": False,
            "transfer_C_min": 1,
            "answers_transfer_coupled_511": True,
            "oq_answer": (
                "Every covering distinct-label transfer-coupled schedule of shape "
                "(5,1,1) at total Q=7 (shared restored prefix of length 5, two "
                "divergent nonzero tips, priced transfer C>=1, independent dirt, "
                "dual even-parity readout, fair shared-prefix XOR billing) has "
                "R>=84. Among the 1458240 covering pairs with R=84, every fair-X "
                "bill is >=9 (witness X=9). Abstract tariff floor is therefore "
                "38*7+2*84+2*9=452>436. C=0 is rejected. Other (p,a,b) shapes are "
                "out of full census here; spot samples show observed min R>=86, "
                "which already cannot undercut because R+X>=86>85."
            ),
            "no_new_kappa": True,
        },
        "census_5_1_1": census,
        "champion": champ,
        "transfer_C_controls": controls,
        "other_shape_samples": samples,
        "unit_tariff": {"b": 38, "a": 2, "x": 2},
        "tariff_check": {
            "formula": "38*Q + 2*R + 2*X  (C folded into fair X)",
            "floor_R84_X9": 452,
            "endpoint_Q6": 436,
            "undercut_requires_R_plus_X_lt": r_undercut_threshold(),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite CERTIFICATE.json (default is read-only check)",
    )
    args = ap.parse_args(argv)

    check_source_pins()
    cert = build_certificate()

    if args.write_certificate:
        CERT_PATH.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    else:
        need(CERT_PATH.is_file(), "missing CERTIFICATE.json")
        pinned = load_json_reject_duplicates(CERT_PATH)
        need(pinned["status"] == cert["status"], "certificate status")
        need(pinned["claim"] == cert["claim"], "certificate claim drift")
        need(
            pinned["census_5_1_1"]["covering_pairs"] == cert["census_5_1_1"]["covering_pairs"],
            "census covering drift",
        )
        need(
            pinned["census_5_1_1"]["histogram"] == cert["census_5_1_1"]["histogram"],
            "census histogram drift",
        )
        need(
            pinned["census_5_1_1"]["min_fair_X_at_R84"]
            == cert["census_5_1_1"]["min_fair_X_at_R84"],
            "fair X drift",
        )
        need(pinned["champion"]["tariff"] == cert["champion"]["tariff"], "champion drift")

    print(
        "PASS_TRANSFER_COUPLED_7Q_OBSTRUCTION "
        f"covering={cert['claim']['covering_pairs']} min_R={cert['claim']['min_R']} "
        f"min_fair_X={cert['claim']['min_fair_X_at_R84']} "
        f"tariff_floor={cert['claim']['tariff_floor']} "
        "answers_transfer_coupled_511 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
