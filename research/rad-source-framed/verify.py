#!/usr/bin/env python3
"""Portable exact arithmetic replay of the frozen twelve-row source-frame audit.

This calls selected pure functions from unchanged independent review sources.
It does not invoke their machine-specific historical entry points, reconstruct
the finite graph, instantiate the native table, or prove the tape lemmas.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import sys
import tempfile
import time


SOURCE_PINS = {
    "review_asymmetric_motif.py": "15d6511b92ac6a3a3c1873106e3fc165db0590330898690db880e6b91e016552",
    "review_compact_generic.py": "bd780cc247a089cfe8bb3c20028ac096737146b87c18cf6859f8de056c0fe379",
    "review_packed_unrolling.py": "5363ab4769c760e8d518d4b942552bf0fa30f0a9ee7f97446c4408d737949bb3",
    "review_parameter_audit.py": "dca1a3e97c26209e59eceec3d5a86a8f5205ff90c9d46f1d40d7bab499ac6bd8",
    "review_semantic_bulk_assembly.py": "56cd4bc9c5ca85a4a4d0937b2c0c2311ec52fb06c7c009e455d2906e4dbc7ff5",
    "review_source_frame_inputs.py": "4d9d97c209caea05419aa354e71ef3d1c06233fc4e9fd10b415f0598724cb8b0",
    "review_source_framed_whole_assembly.py": "c10d869a1f2b658cb326fa2aea2c18d942fe87c67288bda447a2d21705c4987b",
    "review_whole_complex_assembly.py": "af2520cea6d81b9b6383119eb4f0a937db42686a99e2ad03bfa6956861e20460",
}
DATA_PINS = {
    "source-framed-producer.json": "f3a6c37709aa4ec4e27e3880e1cb671a3f8524ebfd3171e1b11d5c33eee5ce44",
    "independent-assembly.json": "f5f67e1b25c56f9c06a6dbf362cba8484d5bf8a675719d90f1293f4350f5fd85",
    "source-frame-inputs.json": "6f0d1dc3607fe48e1c77f4529e0fe6ae925eea9d7ad0a976d32f9db54349d045",
    "complex-finite-review.json": "67eb3d68e59355861444069f8839706884d5f44cb3e6464c41dd2b1cf6eab854",
    "analytic-assembly.json": "7e72e0731507a874ac6cb8b7578488201b1fb367f015c9b0b07564e7ae02597c",
    "finite-independent.json": "c957b06e16a781c11bc2a454b6c323a666e8ec2d47a17af7fe89089f3518939e",
    "source-frame-finite-review.json": "a15f9c1aa618afd435861e7f2e13c7f3a2056c8d46c0be8d49726ab5e77bd252",
    "selected-normal-input.json": "1a2dad1d8128370346da871a34671dfb45b4aee4b1f2b9606430dc4ac64fe321",
}
SELECTED_PARENT_SHA256 = "ca6ce8791888f67474b522a955bbd5465b73b94ee117b8b9a3709a97ff2a767e"
FINITE_REVIEW_SHA256 = "c957b06e16a781c11bc2a454b6c323a666e8ec2d47a17af7fe89089f3518939e"
CANDIDATE_ID = "439f31afa89e659a2bacb35a7d1474ba67e0410369a5d9cca22dcee4359ff741"
COMPILED_SHA256 = "c7eed569818909583b4df314dd0e05d809c2254905cebf6f6d405a3296f80484"
BEST_KAPPA = Fraction(5834475279233921242758637328164947, 5 * 10**39)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_manifest(bundle):
    """Check publication files separately from untouched historical metadata."""
    manifest_path = bundle / "provenance.json"
    manifest = read_json(manifest_path)
    files = manifest["files"]
    require(isinstance(files, dict), "The provenance files must be a path-to-hash mapping")
    checked = {}
    for relative, record in files.items():
        path = bundle / relative
        require(not Path(relative).is_absolute() and path.resolve().is_relative_to(bundle.resolve()),
                "Manifest path leaves the bundle: " + relative)
        expected = record["sha256"] if isinstance(record, dict) else record
        actual = digest(path)
        require(actual == expected, "Publication hash mismatch: " + relative)
        if isinstance(record, dict) and "bytes" in record:
            require(path.stat().st_size == record["bytes"], "Publication byte count mismatch: " + relative)
        checked[relative] = actual
    for name, expected in SOURCE_PINS.items():
        require(checked.get("code/" + name) == expected, "Frozen reviewer source changed: " + name)
    for name, expected in DATA_PINS.items():
        require(checked.get("data/" + name) == expected, "Frozen historical input changed: " + name)
    require("data/selected-normal-input.json" in checked, "Missing derived selected input hash")
    # The source input itself is recoverable in the pinned RaD evidence archive.
    # An extraction hash does not prove its parentage; the subsequent replay also
    # compares every field actually used with the frozen independent audit.
    selected_record = files["data/selected-normal-input.json"]
    require(isinstance(selected_record, dict)
            and selected_record.get("derived_from_original_sha256") == SELECTED_PARENT_SHA256
            and manifest["full_case_original_sha256"] == SELECTED_PARENT_SHA256,
            "Derived selected input must record the immutable parent SHA256")
    require(manifest["candidate_id"] == CANDIDATE_ID
            and manifest["compiled_sha256"] == COMPILED_SHA256,
            "Publication manifest names a different selected program")
    local_modules = {Path(name).stem for name in SOURCE_PINS}
    for name in SOURCE_PINS:
        tree = ast.parse((bundle / "code" / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = ([x.name for x in node.names] if isinstance(node, ast.Import)
                     else [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for imported in names:
                top = imported.split(".")[0]
                require(top in local_modules or top in sys.stdlib_module_names,
                        "Incomplete standard-library-only source closure: " + imported)
    return manifest, checked


def replay(bundle):
    manifest, hashes = verify_manifest(bundle)
    code = bundle / "code"
    sys.path.insert(0, str(code))
    from review_source_frame_inputs import reconstruct
    from review_source_framed_whole_assembly import audit_native, audit_row, phase_review

    data = bundle / "data"
    producer = read_json(data / "source-framed-producer.json")
    frozen = read_json(data / "independent-assembly.json")
    component = read_json(data / "source-frame-inputs.json")
    complex_finite = read_json(data / "complex-finite-review.json")
    analytic = read_json(data / "analytic-assembly.json")
    selected = read_json(data / "selected-normal-input.json")
    finite = read_json(data / "finite-independent.json")
    source_frame = read_json(data / "source-frame-finite-review.json")
    require(producer["status"] ==
            "PASS STRICT NONZERO-SOURCE-FRAMED WHOLE-COMPLEX ASSEMBLY; FINAL INDEPENDENT REVIEW REQUIRED",
            "Unexpected historical producer")
    require(frozen["status"] ==
            "PASS independent complete source-framed h53 zero one two protected whole-complex assembly",
            "Unexpected historical independent audit")
    require(component["status"] == "PASS independent source-frame generic characteristic arithmetic",
            "Unexpected source-frame input audit")
    require(selected["candidate_id"] == frozen["accepted_finite_candidate"]
            == component["candidate_id"] == CANDIDATE_ID,
            "Selected candidate identity differs")
    require(selected["checked"]["compiled_sha256"] == component["compiled_sha256"] == COMPILED_SHA256,
            "Selected compiled program identity differs")
    require(finite["status"] == "PASS INDEPENDENT CLOSING DIRECT-FIRST-ALLOCATION COMPOUND"
            and finite["candidate_id"] == CANDIDATE_ID
            and finite["full"]["final_compiled_sha256"] == COMPILED_SHA256
            and not finite["old_allocation_parent_jobs_replayed"],
            "Frozen complete finite-review record differs")
    require(source_frame == producer["source_frame_component_audit"],
            "Copied source-frame review differs from the producer's pinned component")
    finite_excerpt = producer["compound_finite_audit"]
    require(finite_excerpt["sha256"] == FINITE_REVIEW_SHA256
            and finite_excerpt["candidate_id"] == CANDIDATE_ID
            and finite_excerpt["compiled_sha256"] == COMPILED_SHA256
            and finite_excerpt["direct_first_allocation"]
            and finite_excerpt["source_actual_frames_all_rounds"]
            and not finite_excerpt["old_allocation_parent_jobs_replayed"]
            and not finite_excerpt["old_baseline_physical_replayed"],
            "Archived finite-review excerpt or program identity differs")
    base, budget = reconstruct(selected)
    require(budget == frozen["actual_bit_budget"] == component["actual_physical_budget"],
            "Reconstructed physical budget differs from the frozen audits")
    require(all(finite["full"]["exact_counts"][key] == base[key]
                for key in ("h", "v", "m", "N", "W", "L", "D", "s")),
            "Archived finite-review exact counts differ")
    require(producer["accepted_closing_twelve_row_regressions"]
            == frozen["unchanged_twelve_predecessor_rows"],
            "Frozen predecessor summaries differ")
    require(len(frozen["unchanged_twelve_predecessor_rows"]) == 12,
            "Missing historical predecessor summary")
    native, primitives = {}, {}
    for primitive in producer["generic_characteristics"]:
        identity = primitive["construction_id"]
        require(identity not in native, "Duplicate native variant")
        native[identity] = audit_native(primitive, base, component, budget)
        primitives[identity] = primitive
    require(native == frozen["independent_native_variants"]
            and {x["protected_centers"] for x in native.values()} == {0, 1, 2},
            "The three independently recomputed native variants differ")

    phase = phase_review(producer["witnesses"][0]["complex_branching_certificate"],
                         analytic["whole_complex_characteristic"], complex_finite["full"])
    require(phase == frozen["independent_phase_recertification"],
            "Recomputed complex phase characteristic differs")
    require(Fraction(producer["complex_new_coarse_saving"]) == Fraction(phase["saving"])
            and Fraction(producer["complex_new_coarse_gap"]) == Fraction(phase["strict_normalized_gap"])
            and producer["complex_accepted_child_histogram_unchanged"],
            "Frozen phase summary differs")
    previous = frozen["previous_accepted_kappa"]
    require(producer["previous_accepted_kappa"] == previous,
            "Historical previous saving differs")
    old_tight = {"parameters": {"kappa": previous}}
    rows = []
    for row in producer["witnesses"]:
        identity = row["native_construction_id"]
        primitive, own = primitives[identity], native[identity]
        require(row["bit_counts"] == primitive["counts"]
                and row["complex_counts"] == producer["complex_counts_unchanged"],
                "A row changed its physical counts")
        guard = row["native_bit_primitive"]["conservative_changed_center_bit_guard"]
        require(guard["G_upper"] == own["conservative_new_bit_G_upper"]
                and guard["E"] == own["bit_E_unchanged"]
                and guard["depth_upper"] == own["new_bit_depth_upper"]
                and guard["strict_slack"] == own["strict_new_bit_guard_slack"] > 0,
                "Changed native bit gates were not fully charged")
        require(phase_review(row["complex_branching_certificate"],
                             analytic["whole_complex_characteristic"], complex_finite["full"]) == phase,
                "A row changed its phase characteristic")
        ec = row["complex_branching_certificate"]
        a, b = Fraction(primitive["saving"]), Fraction(phase["saving"])
        require(Fraction(ec["new_native_bit_saving"]) == a
                and Fraction(ec["phase_above_twice_bit"]) == b - 2*a < 0
                and Fraction(ec["beta_half_leaf_above_bit"]) == b/2 - a < 0
                and Fraction(ec["beta_eighth_leaf_above_bit"]) == b*Fraction(7, 8) - a > 0,
                "Changed stopping threshold or old-half negative differs")
        contract = {k: v for k, v in row["whole_complex_transfer"].items()
                    if k not in ("changed_bit_product_stock", "old_combined_rows_historical_only")}
        require(contract == analytic["accepted_whole_complex_transfer"]
                and row["whole_complex_transfer"]["changed_bit_product_stock"] == row["compact_row_padding"],
                "Inherited mixed-phase, tail or product-stock contract differs")
        result = audit_row(row, old_tight, primitive, phase)
        result["native_construction_id"] = identity
        rows.append(result)
    expected = set(product(native, ("conservative", "tight"), ("original", "balanced")))
    require(len(rows) == 12 and
            {(r["native_construction_id"], r["mode"], r["prefix"]) for r in rows} == expected,
            "The twelve-row Cartesian product is incomplete")
    require(rows == frozen["rows"], "A complete independent numeric row differs")
    strongest = max(Fraction(row["kappa"]) for row in rows)
    require(strongest == BEST_KAPPA, "Final frozen saving differs")
    return {
        "status": "PASS PORTABLE TWELVE-ROW ARITHMETIC REPLAY",
        "scope": "Exact arithmetic and copied provenance replay; no finite graph, native-table or tape-proof rerun",
        "candidate_id": CANDIDATE_ID,
        "compiled_sha256": COMPILED_SHA256,
        "selected_parent_sha256": SELECTED_PARENT_SHA256,
        "archived_finite_review_sha256": FINITE_REVIEW_SHA256,
        "source_and_input_sha256": hashes,
        "publication_manifest_sha256": digest(bundle / "provenance.json"),
        "native_variants_recomputed": len(native),
        "rows_recomputed": len(rows),
        "complete_declared_strict_conditions_per_row":
            [row["complete_declared_strict_conditions"] for row in rows],
        "phase_saving_recomputed": phase["saving"],
        "strongest_kappa": str(strongest),
        "all_complete_numeric_rows_equal_frozen_independent_audit": True,
        "historical_metadata_rewritten": False,
        "giant_native_table_or_shared_prime_materialized": False,
        "limitations": frozen["limitations"],
        "independent_native_variants": native,
        "independent_phase_recertification": phase,
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path,
                        help="Fresh JSON output path; default is a new directory in the system temporary area")
    args = parser.parse_args()
    if args.output is not None:
        require(not args.output.exists(), "Choose a fresh output path")
    started = time.monotonic()
    result = replay(args.bundle.resolve())
    output = args.output or Path(tempfile.mkdtemp(prefix="rad-source-framed-")) / "verified-arithmetic.json"
    require(not output.exists(), "Choose a fresh output path")
    output.parent.mkdir(parents=True, exist_ok=True)
    result.update(generated_utc=datetime.now(timezone.utc).isoformat(),
                  verifier_sha256=digest(Path(__file__)),
                  python=platform.python_version(), wall_seconds=time.monotonic() - started)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print("Three native characteristics, one complex characteristic, twelve complete rows match.")
    print("kappa=" + result["strongest_kappa"])
    print("Fresh result: " + str(output))


if __name__ == "__main__":
    main()
