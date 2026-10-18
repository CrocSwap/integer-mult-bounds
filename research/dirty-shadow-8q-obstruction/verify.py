#!/usr/bin/env python3
"""Dirty-shadow sym-diff collapse at Q=8; read-only default.

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
    bit_enum_bundle,
    champion_analysis,
    clean_shadow_dirt_examples,
    dirty_shadow_symdiff_identities,
    enumerate_distinct7_shadow_spectrum,
    enumerate_one_duplicate_shadow_spectrum,
    mask_best_bundle,
    min_clean_shadow_R,
    min_dirty_shadow_R,
    min_even_subset_R,
    tariff_qrx,
    total_or_none,
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
    need(claim["dirty_shadow_min_R"] == EXPECTED["dirty_shadow_min_R"], "dirty min")
    need(claim["even_subset_min_R"] == EXPECTED["even_subset_min_R"], "even min")
    need(
        claim["clean_shadow_counterfactual_min_R"] == EXPECTED["clean_shadow_min_R"],
        "clean min",
    )
    need(claim["undercuts_436_if_clean_shadow_free"] is False, "clean undercut flag")
    need(claim["undercuts_436_after_complete_dirty_bill"] is False, "legal undercut")
    need(claim["matches_2677_even_floor"] is True, "2677 floor")
    need(claim["answers_mc7q_oq2"] is True, "oq2 flag")
    need(claim["no_new_kappa"] is True, "kappa")


def totals_from_bundle(info):
    even_r = total_or_none(info["even"])
    dirty_r = min(total_or_none(info["dirty"][k]) for k in range(len(info["dirty"])))
    clean_r = min(total_or_none(info["clean"][k]) for k in range(len(info["clean"])))
    return even_r, dirty_r, clean_r


def build_certificate():
    # DP vs bit-enum agreement on champion and nearby witnesses.
    for slots in (
        CHAMPION_8,
        (0, 1, 2, 3, 4, 8, 12, 16),
        (0, 1, 2, 3, 4, 5, 8, 16),
        (0, 0, 1, 2, 4, 8, 15, 16),
    ):
        dp = mask_best_bundle(slots)
        bit = bit_enum_bundle(slots)
        need(dp is not None and bit is not None, f"uncovered {slots}")
        need(totals_from_bundle(dp) == totals_from_bundle(bit), f"DP/bit mismatch {slots}")
        need(
            all(
                total_or_none(dp["dirty"][k]) == total_or_none(bit["dirty"][k])
                for k in range(len(slots))
            ),
            f"dirty-by-k mismatch {slots}",
        )
        need(
            all(
                total_or_none(dp["clean"][k]) == total_or_none(bit["clean"][k])
                for k in range(len(slots))
            ),
            f"clean-by-k mismatch {slots}",
        )

    champ = champion_analysis()
    need(champ["even_R"] == EXPECTED["champion_even_R"], "champion even")
    need(champ["dirty_shadow_min_R"] == EXPECTED["champion_dirty_shadow_min_R"], "champion dirty")
    need(champ["clean_shadow_min_R"] == EXPECTED["champion_clean_shadow_min_R"], "champion clean")
    need(champ["clean_best_k"] == EXPECTED["champion_clean_best_k"], "champion clean k")
    need(champ["legal_tariff_X0"] == EXPECTED["legal_tariff_at_X0"], "legal tariff")
    need(
        champ["hypothetical_clean_tariff_X0"] == EXPECTED["hypothetical_clean_tariff_at_X0"],
        "clean tariff",
    )
    need(champ["legal_tariff_X0"] > EXPECTED["endpoint_tariff_Q6"], "legal must not undercut")
    need(
        champ["hypothetical_clean_tariff_X0"] > EXPECTED["endpoint_tariff_Q6"],
        "clean also fails undercut at X=0",
    )
    need(all(v == champ["even_R"] for v in champ["dirty_shadow_R_by_k"]), "dirty==even all k")

    dirt = clean_shadow_dirt_examples()
    need(len(dirt) >= 2, "dirt examples")

    need(min_even_subset_R(CHAMPION_8) == 74, "closed even")
    need(min_dirty_shadow_R(CHAMPION_8) == 74, "closed dirty")
    need(min_clean_shadow_R(CHAMPION_8) == 67, "closed clean")
    need(
        tariff_qrx(8, 74, 0) == 452 and tariff_qrx(8, 67, 0) == 438,
        "tariff arithmetic",
    )

    # Sym-diff identities on champion for every snapshot index (2^{7}=128 odds).
    for k in range(8):
        need(dirty_shadow_symdiff_identities(CHAMPION_8, k) == 128, f"symdiff k={k}")

    distinct = enumerate_distinct7_shadow_spectrum()
    need(distinct["covering_sets"] == EXPECTED["distinct7_covering"], "covering count")
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
        distinct["dirty_shadow"]["attainable_R"] == EXPECTED["dirty_shadow_attainable_R"],
        "dirty spectrum",
    )
    need(
        distinct["dirty_shadow"]["histogram"] == EXPECTED["dirty_shadow_histogram"],
        "dirty histogram",
    )
    need(distinct["dirty_shadow"]["min_R"] == EXPECTED["dirty_shadow_min_R"], "dirty min")
    need(
        distinct["dirty_shadow"]["matches_even_on_covering"]
        == EXPECTED["dirty_shadow_matches_even_covering"],
        "dirty matches even",
    )
    need(
        distinct["clean_shadow_counterfactual"]["attainable_R"]
        == EXPECTED["clean_shadow_attainable_R"],
        "clean spectrum",
    )
    need(
        distinct["clean_shadow_counterfactual"]["histogram"]
        == EXPECTED["clean_shadow_histogram"],
        "clean histogram",
    )
    need(
        distinct["clean_shadow_counterfactual"]["min_R"] == EXPECTED["clean_shadow_min_R"],
        "clean min",
    )
    need(
        distinct["clean_shadow_counterfactual"]["legal_under_dirty_contract"] is False,
        "clean illegal flag",
    )

    one_dup = enumerate_one_duplicate_shadow_spectrum()
    need(one_dup["covering_multisets"] == EXPECTED["one_dup_covering"], "one-dup covering")
    need(
        one_dup["even_subset"]["attainable_R"] == EXPECTED["one_dup_even_attainable_R"],
        "one-dup even spectrum",
    )
    need(
        one_dup["even_subset"]["histogram"] == EXPECTED["one_dup_even_histogram"],
        "one-dup even hist",
    )
    need(one_dup["even_subset"]["min_R"] == EXPECTED["one_dup_even_min_R"], "one-dup even min")
    need(
        one_dup["dirty_shadow"]["attainable_R"] == EXPECTED["one_dup_dirty_attainable_R"],
        "one-dup dirty spectrum",
    )
    need(
        one_dup["dirty_shadow"]["histogram"] == EXPECTED["one_dup_dirty_histogram"],
        "one-dup dirty hist",
    )
    need(one_dup["dirty_shadow"]["min_R"] == EXPECTED["one_dup_dirty_min_R"], "one-dup dirty min")
    need(
        one_dup["dirty_shadow"]["matches_even_on_covering"]
        == EXPECTED["one_dup_dirty_matches_even"],
        "one-dup dirty matches",
    )
    need(
        one_dup["clean_shadow_counterfactual"]["attainable_R"]
        == EXPECTED["one_dup_clean_attainable_R"],
        "one-dup clean spectrum",
    )
    need(
        one_dup["clean_shadow_counterfactual"]["histogram"]
        == EXPECTED["one_dup_clean_histogram"],
        "one-dup clean hist",
    )
    need(
        one_dup["clean_shadow_counterfactual"]["min_R"] == EXPECTED["one_dup_clean_min_R"],
        "one-dup clean min",
    )

    return {
        "schema_version": 1,
        "status": "PASS_DIRTY_SHADOW_8Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Priced dirty-shadow snapshot readout at Q=8: sym-diff collapse to "
            "even-subset, plus illegal clean-shadow counterfactual. Answers "
            "#2761 OQ2 / #2764 OQ2 (dirty-shadow at eight queries)."
        ),
        "claim": {
            "Q": 8,
            "dirty_shadow_min_R": 74,
            "even_subset_min_R": 74,
            "clean_shadow_counterfactual_min_R": 67,
            "one_dup_dirty_min_R": 82,
            "one_dup_clean_counterfactual_min_R": 71,
            "undercuts_436_if_clean_shadow_free": False,
            "undercuts_436_after_complete_dirty_bill": False,
            "legal_tariff_at_X0": 452,
            "hypothetical_clean_tariff_at_X0": 438,
            "endpoint_Q6_tariff": 436,
            "matches_2677_even_floor": True,
            "answers_mc7q_oq2": True,
            "oq2_answer": (
                "The dirty-shadow sym-diff collapse extends verbatim to eight "
                "queries: on all 2430400 covering distinct-7 length-8 slot lists, "
                "priced dirty-shadow totals match even-subset exactly (spectrum "
                "{74,80,84}; matches_even=2430400), so legal R>=74 and tariff "
                ">=452>436 at X=0, matching #2677. One-duplicate multisets likewise "
                "collapse (spectrum {82,88} on 4083072 covering lists). A dirt-free "
                "shadow would reach R=67 (tariff 438) on distinct-7 and R=71 "
                "(tariff 446) on one-dup, but both still fail to undercut 436 at "
                "X=0 and remain illegal under PR1898 inherited dirt; shadow-only "
                "reads leave odd dirt. After a complete dirty bill, legal "
                "dirty-shadow alphabets stay at tariff >=452 and do not undercut "
                "the six-query endpoint 436."
            ),
            "no_new_kappa": True,
        },
        "champion": champ,
        "clean_shadow_dirt_examples": dirt,
        "distinct7": distinct,
        "one_duplicate": one_dup,
        "leave_alone": {
            "through": 2817,
            "includes": [
                2487,
                2593,
                2643,
                2677,
                2686,
                2687,
                2715,
                2761,
                2764,
                2779,
                2817,
            ],
            "deferred": [
                "transfer-coupled-dual-7q soft-overlap",
                "shared-xor soft-overlap #2643",
                "host screens",
            ],
            "do_not_touch_package": "research/transfer-coupled-7q-obstruction/",
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
        "PASS_DIRTY_SHADOW_8Q_OBSTRUCTION",
        "dirty_shadow_min_R=74",
        "even_subset_min_R=74",
        "clean_counterfactual_min_R=67",
        "legal_tariff=452",
        "hypothetical_clean_tariff=438",
        "no_undercut_even_if_clean_free_at_X0",
        "no_undercut_after_complete_dirty_bill",
        "answers_mc7q_oq2",
        "matches_2677_even_floor",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
