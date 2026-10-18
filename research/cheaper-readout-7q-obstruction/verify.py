#!/usr/bin/env python3
"""Odd-cardinality cheaper readout obstruction at Q=7; read-only default.

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
    CHAMPION_7,
    EXPECTED,
    champion_analysis,
    dirt_obstruction_examples,
    enumerate_distinct6_triple_spectrum,
    min_all_subset_R,
    min_even_subset_R,
    min_parity_repair_R,
    one_repeat_basis_census,
    path_X,
    tariff_qrx,
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


def check_claim_constants(cert):
    claim = cert["claim"]
    need(claim["all_subset_min_R"] == EXPECTED["all_subset_min_R"], "claim all min")
    need(claim["parity_repair_min_R"] == EXPECTED["parity_repair_min_R"], "claim repair min")
    need(claim["even_subset_min_R"] == EXPECTED["even_subset_min_R"], "claim even min")
    need(claim["undercuts_436_if_all_subset_free"] is True, "claim undercut flag")
    need(claim["undercuts_436_after_parity_repair"] is False, "claim repair undercut")
    need(claim["no_new_kappa"] is True, "kappa")
    need(claim["answers_7qr_oq1"] is True, "oq1 flag")


def build_certificate():
    champ = champion_analysis()
    need(champ["all_subset_R"] == EXPECTED["champion_all_R"], "champion all R")
    need(champ["even_subset_R"] == EXPECTED["champion_even_R"], "champion even R")
    need(champ["parity_repair_R"] == EXPECTED["champion_repair_R"], "champion repair R")
    need(champ["path_X"] == 6, "champion path X")
    need(champ["all_subset_odd_dirt_count"] > 0, "champion must show odd dirt")
    need(
        champ["hypothetical_tariff_all_X6"] == EXPECTED["hypothetical_all_subset_tariff_X6"],
        "hypothetical tariff",
    )
    need(champ["tariff_repair_X6"] == EXPECTED["parity_repair_tariff_X6"], "repair tariff")
    need(
        champ["hypothetical_tariff_all_X6"] < EXPECTED["endpoint_tariff_Q6"],
        "free all-subset would undercut",
    )
    need(
        champ["tariff_repair_X6"] > EXPECTED["endpoint_tariff_Q6"],
        "repair must not undercut",
    )

    dirt = dirt_obstruction_examples()
    need(len(dirt) >= 2, "dirt examples")

    # Closed champion identity for path_X only (readout alphabet change is the claim).
    need(path_X(CHAMPION_7) == 6, "closed champion X")
    need(min_all_subset_R(CHAMPION_7[:-1]) == 66, "closed all")
    need(min_even_subset_R(CHAMPION_7[:-1]) == 82, "closed even")
    need(min_parity_repair_R(CHAMPION_7[:-1]) == 82, "closed repair")
    need(
        tariff_qrx(7, 66, 6) == 410 and tariff_qrx(7, 82, 6) == 442,
        "tariff arithmetic",
    )

    distinct = enumerate_distinct6_triple_spectrum()
    need(distinct["covering_sets"] == EXPECTED["distinct6_covering"], "covering count")
    need(
        distinct["all_subset"]["attainable_R"] == EXPECTED["all_subset_attainable_R"],
        "all spectrum",
    )
    need(
        distinct["all_subset"]["histogram"] == EXPECTED["all_subset_histogram"],
        "all histogram",
    )
    need(distinct["all_subset"]["min_R"] == EXPECTED["all_subset_min_R"], "all min")
    need(
        distinct["even_subset"]["attainable_R"] == EXPECTED["even_subset_attainable_R"],
        "even spectrum",
    )
    need(
        distinct["even_subset"]["histogram"] == EXPECTED["even_subset_histogram"],
        "even histogram",
    )
    need(distinct["even_subset"]["min_R"] == EXPECTED["even_subset_min_R"], "even min")
    need(
        distinct["parity_repair"]["attainable_R"] == EXPECTED["parity_repair_attainable_R"],
        "repair spectrum",
    )
    need(
        distinct["parity_repair"]["histogram"] == EXPECTED["parity_repair_histogram"],
        "repair histogram",
    )
    need(distinct["parity_repair"]["min_R"] == EXPECTED["parity_repair_min_R"], "repair min")
    need(
        distinct["parity_repair"]["matches_even_on_covering"] == distinct["covering_sets"],
        "repair must match even on every covering distinct-6 set",
    )

    repeats_all = one_repeat_basis_census(min_all_subset_R)
    need(repeats_all["min_R"] == EXPECTED["one_repeat_all_subset_R"], "repeat all min")
    need(
        repeats_all["covering_walks"] == EXPECTED["one_repeat_all_subset_covering"],
        "repeat all covering",
    )
    need(repeats_all["attainable_R"] == [80], "repeat all spectrum")

    repeats_repair = one_repeat_basis_census(min_parity_repair_R)
    need(
        repeats_repair["min_R"] == EXPECTED["one_repeat_parity_repair_R"],
        "repeat repair min",
    )
    need(
        repeats_repair["covering_walks"] == EXPECTED["one_repeat_parity_repair_covering"],
        "repeat repair covering",
    )
    need(repeats_repair["attainable_R"] == [96], "repeat repair spectrum")

    return {
        "schema_version": 1,
        "status": "PASS_CHEAPER_READOUT_7Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Priced odd-cardinality (all-subset) connector-state readout at Q=7 "
            "versus dirty-parity repair back to even live-connector schedules. "
            "Answers #2686 OQ1 for this alphabet."
        ),
        "claim": {
            "Q": 7,
            "all_subset_min_R": 66,
            "even_subset_min_R": 82,
            "parity_repair_min_R": 82,
            "one_repeat_all_subset_min_R": 80,
            "one_repeat_parity_repair_min_R": 96,
            "undercuts_436_if_all_subset_free": True,
            "undercuts_436_after_parity_repair": False,
            "hypothetical_all_subset_tariff_at_X6": 410,
            "parity_repair_tariff_at_X6": 442,
            "endpoint_Q6_tariff": 436,
            "answers_7qr_oq1": True,
            "oq1_answer": (
                "Free all-subset (odd-cardinality) readout reaches R=66 and would "
                "tariff 410<436 at X=6, but odd live-connector R_m parity leaves "
                "arbitrary connector dirt on those outputs. Minimal zero-slot "
                "parity repair collapses every covering schedule to even-subset "
                "cost R>=82 (tariff 442), so this cheaper alphabet does not undercut "
                "the six-query endpoint under the PR1898 dirty-connector contract."
            ),
            "no_new_kappa": True,
        },
        "champion": champ,
        "dirt_obstruction_examples": dirt,
        "distinct6": distinct,
        "one_repeat_all_subset": repeats_all,
        "one_repeat_parity_repair": repeats_repair,
        "leave_alone": {
            "through": 2686,
            "includes": [2593, 2643, 2677, 2686],
            "pending_skeptical_not_edited": "cursor/odd-kernel-query-pair-60b9@c319093b",
            "deferred": [
                "mutable-source-7q-shared-xor soft-overlap #2643",
                "host screens",
            ],
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate CERTIFICATE.json (default is read-only compare)",
    )
    args = parser.parse_args(argv)

    check_source_pins()
    cert_existing = None
    if CERT_PATH.is_file():
        cert_existing = load_json_reject_duplicates(CERT_PATH)
        if not args.write:
            check_claim_constants(cert_existing)

    built = build_certificate()
    if args.write:
        CERT_PATH.write_text(json.dumps(built, indent=2) + "\n", encoding="utf-8")
        print("WROTE_CERTIFICATE", CERT_PATH)
    else:
        need(cert_existing is not None, "missing CERTIFICATE.json")
        need(built == cert_existing, "fresh rebuild differs from CERTIFICATE.json")

    print(
        "PASS_CHEAPER_READOUT_7Q_OBSTRUCTION",
        "all_subset_min_R=66",
        "parity_repair_min_R=82",
        "hypothetical_tariff=410",
        "repair_tariff=442",
        "no_undercut_after_dirty_parity_repair",
        "answers_7qr_oq1",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
