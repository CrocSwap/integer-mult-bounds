#!/usr/bin/env python3
"""Multi-connector / priced-shadow obstruction at Q=7; read-only default.

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
    clean_shadow_dirt_examples,
    dirty_shadow_symdiff_identities,
    dual_independent_same_walk_R,
    enumerate_distinct6_multi_connector,
    even_triangle_holds,
    mask_best_bundle,
    min_clean_shadow_R,
    min_dirty_shadow_R,
    min_even_subset_R,
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
    need(claim["legal_multi_connector_min_R"] == EXPECTED["dirty_shadow_min_R"], "legal min")
    need(claim["clean_shadow_counterfactual_min_R"] == EXPECTED["clean_shadow_min_R"], "clean min")
    need(claim["undercuts_436_if_clean_shadow_free"] is True, "clean undercut flag")
    need(claim["undercuts_436_after_complete_dirty_bill"] is False, "legal undercut")
    need(claim["no_new_kappa"] is True, "kappa")
    need(claim["answers_cr7q_oq1"] is True, "oq1 flag")


def build_certificate():
    champ = champion_analysis()
    need(champ["even_R"] == EXPECTED["champion_even_R"], "champion even")
    need(champ["dirty_shadow_min_R"] == EXPECTED["champion_dirty_shadow_min_R"], "champion dirty")
    need(champ["clean_shadow_min_R"] == EXPECTED["champion_clean_shadow_min_R"], "champion clean")
    need(champ["clean_best_k"] == EXPECTED["champion_clean_best_k"], "champion clean k")
    need(champ["dual_independent_R"] == EXPECTED["champion_even_R"], "champion dual")
    need(champ["path_X"] == 6, "champion path X")
    need(champ["legal_tariff_X6"] == EXPECTED["legal_tariff_at_X6"], "legal tariff")
    need(
        champ["hypothetical_clean_tariff_X6"] == EXPECTED["hypothetical_clean_tariff_at_X6"],
        "clean tariff",
    )
    need(champ["legal_tariff_X6"] > EXPECTED["endpoint_tariff_Q6"], "legal must not undercut")
    need(
        champ["hypothetical_clean_tariff_X6"] < EXPECTED["endpoint_tariff_Q6"],
        "free clean would undercut",
    )
    need(all(v == champ["even_R"] for v in champ["dirty_shadow_R_by_k"]), "dirty==even all k")

    # Dual triangle identity on champion and clean-71 witness.
    for slots in (CHAMPION_7[:-1], (0, 1, 2, 4, 8, 15, 16)):
        even = mask_best_bundle(slots)["even"]
        need(even_triangle_holds(even), f"triangle on {slots}")
        need(sum(even[1:]) == dual_independent_same_walk_R(slots), "dual==even")

    dirt = clean_shadow_dirt_examples()
    need(len(dirt) >= 2, "dirt examples")

    need(path_X(CHAMPION_7) == 6, "closed champion X")
    need(min_even_subset_R(CHAMPION_7[:-1]) == 82, "closed even")
    need(min_dirty_shadow_R(CHAMPION_7[:-1]) == 82, "closed dirty")
    need(min_clean_shadow_R(CHAMPION_7[:-1]) == 71, "closed clean")
    need(
        tariff_qrx(7, 82, 6) == 442 and tariff_qrx(7, 71, 6) == 420,
        "tariff arithmetic",
    )

    # Sym-diff identities on champion for every snapshot index.
    for k in range(7):
        need(dirty_shadow_symdiff_identities(CHAMPION_7[:-1], k) == 64, f"symdiff k={k}")

    distinct = enumerate_distinct6_multi_connector()
    need(distinct["covering_sets"] == EXPECTED["distinct6_covering"], "covering count")
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
        distinct["dual_independent"]["attainable_R"] == EXPECTED["dual_indep_attainable_R"],
        "dual spectrum",
    )
    need(
        distinct["dual_independent"]["histogram"] == EXPECTED["dual_indep_histogram"],
        "dual histogram",
    )
    need(distinct["dual_independent"]["min_R"] == EXPECTED["dual_indep_min_R"], "dual min")
    need(
        distinct["dual_independent"]["matches_even_on_covering"]
        == EXPECTED["dual_indep_matches_even_covering"],
        "dual matches even",
    )
    need(
        distinct["dual_independent"]["triangle_holds_on_covering"]
        == EXPECTED["distinct6_covering"],
        "dual triangle covering",
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

    repeats_even = one_repeat_basis_census(min_even_subset_R)
    need(repeats_even["min_R"] == EXPECTED["one_repeat_even_R"], "repeat even")
    need(repeats_even["covering_walks"] == EXPECTED["one_repeat_covering"], "repeat covering")
    need(repeats_even["attainable_R"] == [96], "repeat even spectrum")

    repeats_dirty = one_repeat_basis_census(min_dirty_shadow_R)
    need(repeats_dirty["min_R"] == EXPECTED["one_repeat_dirty_shadow_R"], "repeat dirty")
    need(repeats_dirty["covering_walks"] == EXPECTED["one_repeat_covering"], "repeat dirty cov")
    need(repeats_dirty["attainable_R"] == [96], "repeat dirty spectrum")

    repeats_clean = one_repeat_basis_census(min_clean_shadow_R)
    need(repeats_clean["min_R"] == EXPECTED["one_repeat_clean_shadow_R"], "repeat clean")
    need(repeats_clean["covering_walks"] == EXPECTED["one_repeat_covering"], "repeat clean cov")
    need(repeats_clean["attainable_R"] == [88], "repeat clean spectrum")

    return {
        "schema_version": 1,
        "status": "PASS_MULTI_CONNECTOR_7Q_OBSTRUCTION",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Priced multi-connector readout at Q=7: correlated dirty shadow "
            "snapshot, independent dual same-walk, and illegal clean-shadow "
            "counterfactual. Answers #2715 OQ1 (cr7q multi-connector)."
        ),
        "claim": {
            "Q": 7,
            "legal_multi_connector_min_R": 82,
            "dirty_shadow_min_R": 82,
            "dual_independent_min_R": 82,
            "even_subset_min_R": 82,
            "clean_shadow_counterfactual_min_R": 71,
            "one_repeat_legal_min_R": 96,
            "one_repeat_clean_counterfactual_min_R": 88,
            "undercuts_436_if_clean_shadow_free": True,
            "undercuts_436_after_complete_dirty_bill": False,
            "legal_tariff_at_X6": 442,
            "hypothetical_clean_tariff_at_X6": 420,
            "endpoint_Q6_tariff": 436,
            "answers_cr7q_oq1": True,
            "oq1_answer": (
                "A priced shadow snapshot with inherited correlated dirt collapses "
                "to even-subset cost R>=82 via sym-diff with the snapshot index "
                "(spectrum {82,88} on all 583296 covering distinct-6 sets). "
                "Two independently dirty connectors on the same walk likewise "
                "cannot beat R=82: dual R is computed as Σ_m min_a (e[a]+e[a⊕m]) "
                "and the even-subset triangle inequality is verified on every "
                "covering set (matches_even=triangle_holds=583296). A dirt-free "
                "shadow would reach R=71 and tariff 420<436, but cannot scrub "
                "inherited connector dirt under the PR1898 contract; shadow-only "
                "reads leave odd dirt. After a complete dirty bill, legal "
                "multi-connector alphabets stay at tariff >=442 and do not "
                "undercut the six-query endpoint 436."
            ),
            "no_new_kappa": True,
        },
        "champion": champ,
        "clean_shadow_dirt_examples": dirt,
        "distinct6": distinct,
        "one_repeat_even": repeats_even,
        "one_repeat_dirty_shadow": repeats_dirty,
        "one_repeat_clean_shadow_counterfactual": repeats_clean,
        "leave_alone": {
            "through": 2715,
            "includes": [2593, 2643, 2677, 2686, 2687, 2715],
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
        "PASS_MULTI_CONNECTOR_7Q_OBSTRUCTION",
        "legal_min_R=82",
        "dirty_shadow_min_R=82",
        "dual_indep_min_R=82",
        "clean_counterfactual_min_R=71",
        "legal_tariff=442",
        "hypothetical_clean_tariff=420",
        "no_undercut_after_complete_dirty_bill",
        "answers_cr7q_oq1",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
