#!/usr/bin/env python3
"""Dirty-parity collapse at Q=8; read-only default.

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
    CHAMPION_8,
    EXPECTED,
    bit_enum_totals,
    champion_analysis,
    dirt_obstruction_examples,
    enumerate_distinct7_triple_spectrum,
    enumerate_one_duplicate_spectrum,
    min_all_subset_R,
    min_even_subset_R,
    min_parity_repair_R,
    spectrum_totals,
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
    need(claim["all_subset_min_R_distinct7"] == EXPECTED["all_subset_min_R"], "claim all")
    need(claim["parity_repair_min_R_distinct7"] == EXPECTED["parity_repair_min_R"], "claim repair")
    need(claim["even_subset_min_R_distinct7"] == EXPECTED["even_subset_min_R"], "claim even")
    need(claim["undercuts_436_if_all_subset_free"] is True, "claim undercut flag")
    need(claim["undercuts_436_after_parity_repair"] is False, "claim repair undercut")
    need(claim["matches_2677_even_floor"] is True, "2677 floor flag")
    need(claim["answers_cr7q_oq2"] is True, "oq2 flag")
    need(claim["no_new_kappa"] is True, "kappa")


def build_certificate():
    # DP vs bit-enum agreement on champion and nearby witnesses.
    for slots in (
        CHAMPION_8,
        (0, 1, 2, 3, 4, 8, 16, 30),
        (0, 1, 2, 4, 8, 15, 16, 3),
    ):
        need(spectrum_totals(slots) == bit_enum_totals(slots), f"DP/bit mismatch {slots}")

    champ = champion_analysis()
    need(champ["all_subset_R"] == EXPECTED["champion_all_R"], "champion all R")
    need(champ["even_subset_R"] == EXPECTED["champion_even_R"], "champion even R")
    need(champ["parity_repair_R"] == EXPECTED["champion_repair_R"], "champion repair R")
    need(champ["odd_dirt_mask_count"] > 0, "champion odd dirt")
    need(
        champ["hypothetical_tariff_X0"] == EXPECTED["hypothetical_all_subset_tariff_X0"],
        "hyp tariff",
    )
    need(champ["repair_tariff_X0"] == EXPECTED["parity_repair_tariff_X0"], "repair tariff")
    need(
        champ["hypothetical_tariff_X0"] < EXPECTED["endpoint_tariff_Q6"],
        "free all-subset would undercut",
    )
    need(
        champ["repair_tariff_X0"] > EXPECTED["endpoint_tariff_Q6"],
        "repair must not undercut",
    )

    dirt = dirt_obstruction_examples()
    need(len(dirt) >= 2, "dirt examples")

    need(min_all_subset_R(CHAMPION_8) == 61, "closed all")
    need(min_even_subset_R(CHAMPION_8) == 74, "closed even")
    need(min_parity_repair_R(CHAMPION_8) == 74, "closed repair")
    need(
        tariff_qrx(8, 61, 0) == 426 and tariff_qrx(8, 74, 0) == 452,
        "tariff arithmetic",
    )
    need(
        EXPECTED["parity_repair_min_R"] == EXPECTED["pr2677_even_distinct_floor"],
        "match #2677 floor",
    )

    distinct = enumerate_distinct7_triple_spectrum()
    need(distinct["covering_sets"] == EXPECTED["distinct7_covering"], "covering count")
    need(
        distinct["repair_equals_even_count"] == EXPECTED["repair_equals_even_count"],
        "repair==even count",
    )
    need(
        distinct["all_subset"]["attainable_R"] == EXPECTED["all_subset_attainable_R"],
        "all spectrum",
    )
    need(
        distinct["all_subset"]["histogram"] == EXPECTED["all_subset_histogram"],
        "all hist",
    )
    need(distinct["all_subset"]["min_R"] == EXPECTED["all_subset_min_R"], "all min")
    need(
        distinct["even_subset"]["attainable_R"] == EXPECTED["even_subset_attainable_R"],
        "even spectrum",
    )
    need(
        distinct["even_subset"]["histogram"] == EXPECTED["even_subset_histogram"],
        "even hist",
    )
    need(distinct["even_subset"]["min_R"] == EXPECTED["even_subset_min_R"], "even min")
    need(
        distinct["parity_repair"]["attainable_R"]
        == EXPECTED["parity_repair_attainable_R"],
        "repair spectrum",
    )
    need(
        distinct["parity_repair"]["histogram"] == EXPECTED["parity_repair_histogram"],
        "repair hist",
    )
    need(
        distinct["parity_repair"]["min_R"] == EXPECTED["parity_repair_min_R"],
        "repair min",
    )

    one_dup = enumerate_one_duplicate_spectrum()
    need(one_dup["covering_multisets"] == EXPECTED["one_dup_covering"], "one-dup covering")
    need(
        one_dup["all_subset"]["histogram"] == EXPECTED["one_dup_all_subset_histogram"],
        "one-dup all hist",
    )
    need(
        one_dup["all_subset"]["min_R"] == EXPECTED["one_dup_all_subset_min_R"],
        "one-dup all min",
    )
    need(
        one_dup["parity_repair"]["histogram"]
        == EXPECTED["one_dup_parity_repair_histogram"],
        "one-dup repair hist",
    )
    need(
        one_dup["parity_repair"]["min_R"] == EXPECTED["one_dup_parity_repair_min_R"],
        "one-dup repair min",
    )
    need(
        one_dup["all_subset"]["min_R"] > EXPECTED["all_subset_min_R"],
        "one-dup cannot beat distinct-7 free floor",
    )
    need(
        one_dup["parity_repair"]["min_R"] >= EXPECTED["parity_repair_min_R"],
        "one-dup repair at least distinct-7 repair",
    )

    return {
        "schema_version": 1,
        "status": "PASS_DIRTY_PARITY_8Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "All-subset vs even-subset vs zero-slot dirty-parity repair on "
            "restored length-8 slot lists. Answers #2715 OQ2."
        ),
        "claim": {
            "Q": 8,
            "all_subset_min_R_distinct7": EXPECTED["all_subset_min_R"],
            "even_subset_min_R_distinct7": EXPECTED["even_subset_min_R"],
            "parity_repair_min_R_distinct7": EXPECTED["parity_repair_min_R"],
            "one_dup_all_subset_min_R": EXPECTED["one_dup_all_subset_min_R"],
            "one_dup_parity_repair_min_R": EXPECTED["one_dup_parity_repair_min_R"],
            "undercuts_436_if_all_subset_free": True,
            "undercuts_436_after_parity_repair": False,
            "hypothetical_all_subset_tariff_at_X0": EXPECTED[
                "hypothetical_all_subset_tariff_X0"
            ],
            "parity_repair_tariff_at_X0": EXPECTED["parity_repair_tariff_X0"],
            "endpoint_Q6_tariff": EXPECTED["endpoint_tariff_Q6"],
            "matches_2677_even_floor": True,
            "answers_cr7q_oq2": True,
            "oq2_answer": (
                "Free all-subset readout at Q=8 reaches R=61 on distinct-7 covers "
                "(hypothetical tariff 426<436 even at X=0), but odd live-connector "
                "parity leaves connector dirt. Zero-slot parity repair collapses "
                "every covering distinct-7 schedule to even-subset cost R>=74 "
                "(tariff >=452), matching #2677's distinct-slot floor; "
                "one-duplicate covers repair to R>=82. The dirty-parity collapse "
                "therefore extends from Q=7 to Q=8."
            ),
            "no_new_kappa": True,
        },
        "champion": {
            "slots": champ["slots"],
            "all_subset_R": champ["all_subset_R"],
            "even_subset_R": champ["even_subset_R"],
            "parity_repair_R": champ["parity_repair_R"],
            "odd_dirt_mask_count": champ["odd_dirt_mask_count"],
            "hypothetical_tariff_X0": champ["hypothetical_tariff_X0"],
            "repair_tariff_X0": champ["repair_tariff_X0"],
        },
        "dirt_obstruction_examples": dirt,
        "distinct7": distinct,
        "one_duplicate": one_dup,
        "leave_alone": {
            "through_pr": 2715,
            "not_edited": [1898, 2455, 2593, 2643, 2677, 2686, 2687, 2715],
            "deferred_pending": [
                "cursor/multi-connector-7q-60b9 dual-census DEFER",
                "mutable-source-7q-shared-xor soft-overlap #2643",
                "host screens",
            ],
        },
    }


def compare_certificate(fresh, stored):
    need(fresh["status"] == stored["status"], "status")
    need(fresh["claim"] == stored["claim"], "claim drift")
    need(fresh["champion"]["slots"] == stored["champion"]["slots"], "champion slots")
    need(
        fresh["champion"]["all_subset_R"] == stored["champion"]["all_subset_R"],
        "champion all",
    )
    need(
        fresh["champion"]["parity_repair_R"] == stored["champion"]["parity_repair_R"],
        "champion repair",
    )
    need(
        fresh["distinct7"]["covering_sets"] == stored["distinct7"]["covering_sets"],
        "distinct7 covering",
    )
    need(
        fresh["distinct7"]["all_subset"]["histogram"]
        == stored["distinct7"]["all_subset"]["histogram"],
        "distinct7 all hist",
    )
    need(
        fresh["distinct7"]["parity_repair"]["histogram"]
        == stored["distinct7"]["parity_repair"]["histogram"],
        "distinct7 repair hist",
    )
    need(
        fresh["distinct7"]["repair_equals_even_count"]
        == stored["distinct7"]["repair_equals_even_count"],
        "repair equals even",
    )
    need(
        fresh["one_duplicate"]["covering_multisets"]
        == stored["one_duplicate"]["covering_multisets"],
        "one-dup covering",
    )
    need(
        fresh["one_duplicate"]["all_subset"]["histogram"]
        == stored["one_duplicate"]["all_subset"]["histogram"],
        "one-dup all hist",
    )
    need(
        fresh["one_duplicate"]["parity_repair"]["histogram"]
        == stored["one_duplicate"]["parity_repair"]["histogram"],
        "one-dup repair hist",
    )


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate CERTIFICATE.json (default is read-only compare).",
    )
    args = parser.parse_args(argv)

    check_source_pins()
    fresh = build_certificate()
    if args.write:
        CERT_PATH.write_text(json.dumps(fresh, indent=2) + "\n", encoding="utf-8")
        print(
            "WROTE_DIRTY_PARITY_8Q_OBSTRUCTION "
            f"all_min={EXPECTED['all_subset_min_R']} "
            f"repair_min={EXPECTED['parity_repair_min_R']} "
            f"hyp_tariff={EXPECTED['hypothetical_all_subset_tariff_X0']} "
            f"repair_tariff={EXPECTED['parity_repair_tariff_X0']}"
        )
        return 0

    stored = load_json_reject_duplicates(CERT_PATH)
    check_claim_constants(stored)
    compare_certificate(fresh, stored)
    print(
        "PASS_DIRTY_PARITY_8Q_OBSTRUCTION "
        f"all_subset_min_R={EXPECTED['all_subset_min_R']} "
        f"parity_repair_min_R={EXPECTED['parity_repair_min_R']} "
        f"hypothetical_tariff={EXPECTED['hypothetical_all_subset_tariff_X0']} "
        f"repair_tariff={EXPECTED['parity_repair_tariff_X0']} "
        "no_undercut_after_dirty_parity_repair "
        "answers_cr7q_oq2 matches_2677_even_floor no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
