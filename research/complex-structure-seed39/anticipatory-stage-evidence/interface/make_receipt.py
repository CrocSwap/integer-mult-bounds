#!/usr/bin/env python3
"""Bind the completed stage outputs and record the local cost interface."""
import gzip
import hashlib
import json
from pathlib import Path
import replay

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    replay.check_sources()
    records = {}
    for variant in ("base", "extra"):
        d = HERE / variant
        wordpath = HERE.parent / f"vendor/pr2339/words/BORROW-WORD-80{variant}.json.gz"
        word = read(wordpath); c = read(d / "CANONICAL-WORD.json.gz")
        transport = read(d / "SCALAR-FRAME-AUDIT.json")
        local = read(d / "LOCAL-CHECKS.json")
        independent = read(d / "INDEPENDENT-LOCAL-REPLAY.json")
        wrappers = read(d / "WRAPPER-CHECKS.json")
        phases = read(d / "CLIFFORD-REVIEW.json")
        recipes = read(d / "WARP-RECIPE-CHECKS.json")
        oriented = read(d / "ORIENTATION-CONTRACT.json")
        # These are proof-stage success labels, not incidental timing or scope text.
        for filename, report, expected in (
            ("SCALAR-FRAME-AUDIT.json", transport, "PASS_BORROW_WORD_FREE_ALGEBRA_ALL_COLUMNS_AND_NATIVE_FRAMES"),
            ("INDEPENDENT-LOCAL-REPLAY.json", independent, "PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY"),
            ("WRAPPER-CHECKS.json", wrappers, "PASS_RESIDUAL_WRAPPERS_ARE_EXACT"),
            ("CLIFFORD-REVIEW.json", phases, "PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES"),
            ("WARP-RECIPE-CHECKS.json", recipes, "PASS_WARP_RECIPES_EXACT_ON_ALL_512_COLUMNS"),
            ("ORIENTATION-CONTRACT.json", oriented, "PASS_EXPLICIT_FORWARD_DUAL_WARP_RECIPES"),
        ):
            need(report.get("status") == expected, f"unsuccessful stage: {filename}")
        chash = digest(d / "CANONICAL-WORD.json.gz")
        canonical_content_hash = hashlib.sha256(json.dumps(c, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        input_hash = hashlib.sha256(gzip.decompress(wordpath.read_bytes())).hexdigest()
        need(transport["input_content_sha256"] == input_hash, "transport not bound to pinned word")
        need(transport["canonical_content_sha256"] == hashlib.sha256(gzip.decompress((d / "CANONICAL-WORD.json.gz").read_bytes())).hexdigest(), "transport not bound to canonical word")
        need(transport["local_profile"] == c["local_profile"], "transport profile changed")
        need(independent["canonical_word_sha256"] == chash == phases["canonical_word_sha256"] == recipes["canonical_word_sha256"], "unbound canonical word")
        need(independent["local_programs_sha256"] == digest(d / "LOCAL-PROGRAMS.json.gz"), "unbound programs")
        need(phases["recipe_sha256"] == digest(d / "CLIFFORD-RECIPES.json") == recipes["recipe_sha256"], "unbound compiler recipes")
        need(oriented.get("canonical_content_sha256") == canonical_content_hash, "unbound orientation canonical word")
        need(oriented.get("paid_profile") == c["local_profile"], "orientation profile mismatch")
        need(oriented["oriented_recipe_content_sha256"] == hashlib.sha256(gzip.decompress((d / "ORIENTED-WARP-RECIPES.json.gz").read_bytes())).hexdigest(), "unbound dual recipes")
        need(len(independent["negative_controls_rejected"]) == 44, "local controls missing")
        need(len(wrappers["wrappers_reject"]) == 25, "wrapper controls missing")
        need(len(recipes["controls_rejected"]) == 13, "recipe controls missing")
        need(oriented["wrong_global_phase_controls_rejected"] == 448, "dual controls missing")
        need(phases["warp_recipes"] == 224, "missing warp")
        need(phases.get("warp_recipes_rank_zero") is True, "warp rank-zero proof missing")
        need(phases.get("warp_recipes_equal_exact_512_column_product") is True, "warp exact-product proof missing")
        need(phases.get("all_child_equalities_include_global_phase") is True, "global-phase proof missing")
        need(oriented["helpers"] == 400 and oriented["paid_mass"] == 5264 and oriented["helper_width_sum"] == 3408, "local invoice differs")
        for orientation in ("forward", "backward"):
            need(local[orientation]["paid_profile"] == c["local_profile"] == independent["paid_profiles"][orientation], "profile mismatch")
            need(local[orientation]["all_columns"] == 624 and local[orientation]["zero_buffers_returned_to_zero"] == 44, "local interface mismatch")
        lenders = sorted({t["source"] for t in word["initial_corrections"]})
        need(len(lenders) == 32 and len(word["initial_corrections"]) == 64, "anticipatory terms differ")
        inventory = read(HERE / (variant + "-tamper") / "TAMPER-RESULTS.json")
        need(len(inventory["tampers"]) == 13 and all(x["rejected"] and x["reason_matches"] for x in inventory["tampers"]), "word tamper coverage missing")
        records[variant] = dict(
            word_content_sha256=hashlib.sha256(gzip.decompress(wordpath.read_bytes())).hexdigest(),
            local_profile=c["local_profile"], helper_count=400, local_rank_mass=5264,
            helper_width_sum=3408, mass_minus_width=1856,
            compensation=dict(terms=64, source_origins=lenders, physical_warp_events=128,
                              recursive_rank_charge=0, source_restored_after_each_term=True),
            handoffs=[dict(op=i+1, lender_origin=w[1], old_rank=len(w[3]), new_rank=len(w[4])) for i,w in enumerate(word["warps"]) if w[1]<112],
            buffers=dict(count=44, allocation_phase="full_frame_cleanup", recursive_rank_charge=0,
                         origin_helpers=sorted(map(int,word["helper_final"])),
                         note="44 simultaneous private FULL-frame fields, distinct from restored helper fields; global physical reservation must provide them."),
            orientation_costs=local, directed_edges=phases["directed_edges"], warp_classes=224,
            native_checks=dict(local_controls=44, wrapper_controls=25, warp_recipe_controls=13,
                               explicit_dual_phase_controls=448, word_tampers=13))
    labels = read(HERE / "LEMMAG-CHECKS.json")
    need(len(labels) == 2, "missing label stage")
    for row in labels.values():
        need(all(all(x == 0 for x in o.values()) for o in row["honest"].values()), "label violations")
        need(len(row["mutants"]) == 3 and all(x["rejected"] for x in row["mutants"].values()), "adapter controls missing")
        need(len(row["borrow_mutants"]) == 7 and all(row["borrow_mutants"].values()), "borrow label controls missing")
    filecontrols = read(HERE / "extra-tamper-files/TAMPER-RESULTS.json")
    need(len(filecontrols["tampers"]) == 18 and all(x["rejected"] for x in filecontrols["tampers"]), "file controls missing")
    receipt = dict(status="PASS_PR2339_LOCAL_NATIVE_ADMISSION_WITHOUT_GLOBAL_BOUND",
                   construction_head="bf1742aee4d855efb8bbd44a8419eddb33a679e5",
                   compiler_head="b479fc5567bc09ab9185bffe89b62594f36d74e5",
                   records=records, lemmag_adapter_controls=6, lemmag_borrow_controls=14,
                   extra_word_and_file_tampers=18,
                   execution="All listed stages executed separately on CPython 3.14.7/NumPy 2.5.4; replay.py is the combined reproduction command, not a claim of a second single-process cold run.",
                   scope="Finite local native lowering and paid-rank interface only. No global owner fill, physical reserve proof, full outer ledger, changed kappa, or all-size multiplication theorem is certified here.")
    (HERE / "RESULT.json").write_text(json.dumps(receipt, indent=2)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
