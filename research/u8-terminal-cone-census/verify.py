"""Reproduce the exact U8 census and controls, using two independent methods.

Standard library only, Python >=3.10. Apache-2.0.
Prepared with substantial OpenAI Codex assistance for ToikY.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_sources(root):
    manifest = json.loads((root / "MANIFEST.json").read_text())
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and p.name != "MANIFEST.json" and "__pycache__" not in p.parts}
    need(actual == set(manifest), "source closure differs from manifest")
    for name, expected in manifest.items():
        path = root / name
        need(path.resolve().is_relative_to(root.resolve()), "manifest path escapes package")
        need(digest(path) == expected, "source hash mismatch: " + name)
    sources = json.loads((root / "SOURCES.json").read_text())
    word = root / "inputs/U8-WORD.json.gz"
    need(digest(word) == sources["word_gzip_sha256"], "immutable input container mismatch")
    need(hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest()
         == sources["word_raw_sha256"], "word content mismatch")
    return len(manifest)


def load_census(root):
    spec = importlib.util.spec_from_file_location("u8_cone_primary", root / "census.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(script, arguments, optimized=False):
    flags = ["-I", "-B"] + (["-O"] if optimized else [])
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    return subprocess.run([sys.executable, *flags, str(script), *map(str, arguments)],
                          env=env, capture_output=True, text=True, timeout=30)


def record_controls(module, certificate):
    records = certificate["records"]
    need(len(records) == 504 and [r["helper"] for r in records] == list(range(504)),
         "not a complete unique helper census")
    current_ok, smaller_rejected = 0, 0
    for row in records:
        cone = tuple(row["minimal_necessary_terminal_frame"])
        old = tuple(row["current_terminal_frame"])
        need(module.included(cone, old), "old endpoint control rejected")
        current_ok += 1
        # Every deletion from the literal independent basis is a proper subspace.
        for index in range(len(old)):
            proposed = module.span(old[:index] + old[index + 1:])
            need(not module.included(cone, proposed), "proper endpoint deletion escaped")
            smaller_rejected += 1
    exceptions = [r for r in records if r["row_only_dimension_slack"]]
    need([r["helper"] for r in exceptions] == [347, 349, 359, 361, 370, 371, 372, 373],
         "row-only exception control")
    need(all(len(r["row_and_monotonicity_minimum"]) == 8
             and len(r["minimal_necessary_terminal_frame"]) == 9
             and r["column_blockers_for_row_minimum"] for r in exceptions),
         "omitted dirty-column control escaped")
    for row in exceptions:
        need(not module.included(tuple(row["minimal_necessary_terminal_frame"]),
                                 tuple(row["row_and_monotonicity_minimum"])),
             "row-only endpoint accepted")
    prefix = Counter({int(k): n for k, n in certificate["fixed_prefix_paid_profile"].items()})
    suffix = Counter({int(k): n for k, n in certificate["actual_old_suffix_paid_profile"].items()})
    local = Counter({int(k): n for k, n in certificate["local_profile"].items()})
    jump = Counter({int(k): n for k, n in certificate["all_register_minimal_one_jump_suffix_profile"].items()})
    mass = lambda counts: sum(r * n for r, n in counts.items())
    need(prefix + suffix == local and (mass(prefix), mass(suffix), mass(local)) == (4512, 1122, 5634),
         "prefix/suffix reconstruction or mass")
    need(mass(jump) == mass(suffix), "one-jump mass mismatch")
    width = sum(r["current_width"] for r in records)
    need(width == 3778 and 48384 - 9 * width == 14382, "complete width/idle bill")
    need(73 * 896 - (9 * mass(local) + 14382) == 320, "rank deficit")
    return {"old_endpoints_accepted": current_ok,
            "proper_basis_deletions_rejected": smaller_rejected,
            "row_only_false_admissions_rejected": len(exceptions),
            "complete_cost_mass_checks": "PASS"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--optimized", action="store_true", help="also optimize child interpreters")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    source_count = check_sources(root)
    expected = json.loads(gzip.decompress((root / "CERTIFICATE.json.gz").read_bytes()))
    module = load_census(root)
    controls = record_controls(module, expected)
    with tempfile.TemporaryDirectory(prefix="u8-terminal-cones-") as directory:
        tmp = Path(directory)
        primary = tmp / "primary.json"
        result = run(root / "census.py", ["--word", root / "inputs/U8-WORD.json.gz", "--out", primary],
                     args.optimized)
        need(result.returncode == 0, "primary failed: " + result.stderr)
        observed = json.loads(primary.read_text())
        observed.pop("seconds")
        need(observed == expected, "recomputed exact certificate mismatch")
        independent = tmp / "independent.json"
        result = run(root / "independent.py", ["--word", root / "inputs/U8-WORD.json.gz",
                     "--primary", primary, "--out", independent], args.optimized)
        need(result.returncode == 0, "independent failed: " + result.stderr)
        audit = json.loads(independent.read_text())
        need(audit["all_504_records_match_primary"] and all(
             r["positive"] and r["negative_rejected"] for r in audit["semantic_controls"]),
             "independent controls incomplete")
        row_frames = {r["helper"]: r["row_only_frame"] for r in audit["row_only_records"]}
        need(all(r["row_and_monotonicity_minimum"] == row_frames[r["helper"]]
                 for r in expected["records"]), "independent row-only frame mismatch")
        corrupt = tmp / "corrupt.json.gz"
        raw = bytearray(gzip.decompress((root / "inputs/U8-WORD.json.gz").read_bytes()))
        raw[-2] ^= 1
        corrupt.write_bytes(gzip.compress(raw, mtime=0))
        absent = tmp / "must-not-exist.json"
        result = run(root / "census.py", ["--word", corrupt, "--out", absent], args.optimized)
        need(result.returncode != 0 and "frozen word pin" in result.stderr and not absent.exists(),
             "corrupted input CLI control escaped")
        before = primary.read_bytes()
        result = run(root / "census.py", ["--word", root / "inputs/U8-WORD.json.gz", "--out", primary],
                     args.optimized)
        need(result.returncode != 0 and "refusing to overwrite" in result.stderr
             and primary.read_bytes() == before, "output-preservation control escaped")
    print(json.dumps({"status": "PASS_EXACT_INDEPENDENT_U8_TERMINAL_CONE_CENSUS",
          "source_files_checked": source_count, "helpers": 504, "arbitrary_columns": 728,
          "independent_semantic_mutations_rejected": len(audit["semantic_controls"]),
          "corrupted_input_cli_rejected": True, "existing_output_preserved": True,
          "controls": controls, "optimized_children": args.optimized,
          "scope": "fixed-prefix/end-B monotone common-frame endpoints; no kappa or tail-optimality claim"}, indent=2))


if __name__ == "__main__":
    main()
