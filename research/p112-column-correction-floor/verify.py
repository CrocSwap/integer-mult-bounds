#!/usr/bin/env python3
"""Full bounded replay, with no optional omission of proof premises. Apache-2.0."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, digest, need, same, sources, strict_load, write_new
import fixtures
import geometry
import independent


def compute():
    source_receipt = sources()
    model = geometry.load_model()
    finite = geometry.census(model)
    second = independent.check(finite)
    examples = fixtures.examples(model, finite["free_boundary"])
    return {"schema_version": 1, "status": "PASS_P112_COLUMN_CORRECTION_FLOOR",
            "admitted": False, "new_kappa": False,
            "sources": source_receipt, "geometry": finite,
            "independent": second, "examples": examples,
            "theorem": {"coordinate_pairs": 28, "singleton_sites": 112,
                        "free_support": "any subset of the singleton's 52 odd neighbors",
                        "coefficients": "arbitrary complex; ordinary transpose",
                        "factor_change": "all GL(3,C), with six coordinate terms fixed",
                        "q_domain": "0<q<=1", "COPY_sum_floor": 64,
                        "COPY_power_floor": "8*8^q", "sharp": True,
                        "scope": "written proof plus complete finite geometric premises",
                        "extra_physical_charges": "optimistically zero for this COPY-only screen"},
            "summary": {"fixtures": len(examples),
                        "full_entries": sum(x["full_entries_checked"] for x in examples),
                        "boundary_ranks": examples[1]["replacement_ranks"],
                        "two_rank_eight_extension_falsified": True,
                        "native_or_supplier_admission_run": False}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=HERE/"EXPECTED.json")
    parser.add_argument("--write", type=Path, help="write a freshly computed receipt to a new path")
    args = parser.parse_args()
    if args.write is not None:
        need(not args.write.exists(), "refusing existing output")
    result = compute()
    if args.write is None:
        same(result, strict_load(args.receipt), "complete typed receipt mismatch")
    else:
        write_new(args.write, result)
    print("PASS_P112_COLUMN_GEOMETRY pairs=28 sites=112 survivor_slices=15680")
    print("PASS_P112_COLUMN_BOUNDARY ranks=7,8,7 COPY_sum_floor=64 q=0..1(open,closed)")
    print("PASS_P112_COLUMN_CORRECTION_FLOOR receipt_sha256="+digest(result))


if __name__ == "__main__":
    main()
