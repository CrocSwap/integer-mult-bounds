#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production data-corner columns.

Read-only by default. Regenerates no certificate unless --write-certificate is
passed. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research" / "copied-fixed" / "data_corners.cpp"
RECEIPT = ROOT / "research" / "copied-fixed" / "data-corners.json"
CERTIFICATE = ROOT / "research" / "copied-fixed" / "certificate.json"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "251f6c87cca42619a0c1b6d83705df5cad0e9c33"
ORIGINAL_SHA256 = "d134f43d31b896daf504511991be8608c6ba9d20a6606c57e2e12d4b203b7d44"
BASE_CERTIFICATE_SHA256 = "0b796a06420b9366f96b26b83d84e6c8804f41c5dfe7633c208483f838418889"
RECEIPT_SHA256 = "82dc2d3e116fc003348d6e9ff0cce90fd70d3d6c156580b769ff3d38b3399e17"

GUARD = '#ifdef NDEBUG\n#error "Data-corner replay requires assertions"\n#endif\n'
OLD_INVERSE = "int inv=power(value,prime-2);"
NEW_INVERSE = OLD_INVERSE + """
    int columns[d],length=0;
    for(int j=0;j<d;j++)if(available[j]&&M[i][j])columns[length++]=j;"""
OLD_UPDATE = "for(int j=0;j<d;j++)if(available[j]&&M[i][j]){"
NEW_UPDATE = "for(int k=0;k<length;k++){\n      int j=columns[k];"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json_unique(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def transform(source: str) -> str:
    for old, new in ((OLD_INVERSE, NEW_INVERSE), (OLD_UPDATE, NEW_UPDATE)):
        require(source.count(old) == 1, "Expected exactly one update site: " + old[:40])
        source = source.replace(old, new)
    return source


def compile_program(source: str, output: Path, compiler: list[str]) -> None:
    path = output.with_suffix(".cpp")
    path.write_text(GUARD + source, encoding="utf-8")
    subprocess.run(
        [*compiler, "-O3", "-std=c++17", str(path), "-o", str(output)],
        check=True,
        capture_output=True,
    )


def run_program(executable: Path) -> bytes:
    result = subprocess.run([str(executable)], capture_output=True, check=True)
    return result.stdout


def check_baseline_bytes() -> bytes:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/copied-fixed/data_corners.cpp"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base data_corners.cpp sha256 drift")
    require(
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/copied-fixed/data_corners.cpp"],
            cwd=ROOT,
        )
        .decode()
        .strip()
        == ORIGINAL_BLOB,
        "base data_corners.cpp blob drift",
    )
    require(
        (PACKAGE / "baseline.cpp").read_bytes() == original,
        "baseline.cpp must be an exact copy of the base-commit source",
    )
    return original


def check_production_transform(original: bytes) -> str:
    production = PRODUCTION.read_text(encoding="utf-8")
    expected = transform(original.decode("utf-8"))
    require(production == expected, "production data_corners.cpp != transform(baseline)")
    require("columns[d],length=0" in production, "cached column list missing")
    require(production.count(OLD_UPDATE) == 0, "pairwise update loop still present")
    return production


def check_receipt_equivalence(original_source: str, production_source: str) -> dict:
    require(digest_file(RECEIPT) == RECEIPT_SHA256, "data-corners.json receipt drift")
    expected = load_json_unique(RECEIPT)
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    with tempfile.TemporaryDirectory(prefix="data-corner-prod-") as tmp:
        work = Path(tmp)
        compile_program(original_source, work / "original", compiler)
        compile_program(production_source, work / "optimized", compiler)
        original_out = run_program(work / "original")
        optimized_out = run_program(work / "optimized")
    require(original_out == optimized_out, "baseline/production stdout bytes differ")
    require(json.loads(optimized_out) == expected, "production receipt differs from pinned JSON")
    return expected


def check_temp_corruption(production_source: str) -> str:
    """Mutate the cached-column fill in a temp copy; expect receipt mismatch or abort."""
    with tempfile.TemporaryDirectory(prefix="data-corner-corrupt-") as tmp:
        work = Path(tmp)
        mutant_source = production_source.replace(
            "if(available[j]&&M[i][j])columns[length++]=j;",
            "if(available[j]&&M[i][j]&&j>c)columns[length++]=j;",
            1,
        )
        require(mutant_source != production_source, "corruption edit did not change source")
        compiler = shlex.split(os.environ.get("CXX", "c++"))
        compile_program(production_source, work / "honest", compiler)
        compile_program(mutant_source, work / "mutant", compiler)
        honest = run_program(work / "honest")
        proc = subprocess.run([str(work / "mutant")], capture_output=True, check=False)
        if proc.returncode != 0:
            return "subprocess_failure"
        require(proc.stdout != honest, "corruption preserved the complete receipt")
        return "receipt_mismatch"


def check_certificate(write: bool) -> None:
    path = CERTIFICATE
    if write:
        # Recompute only the local_sha256 entry for data_corners.cpp.
        cert = load_json_unique(path)
        cert["local_sha256"]["research/copied-fixed/data_corners.cpp"] = digest_file(PRODUCTION)
        path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    committed = path.read_text(encoding="utf-8")
    load_json_unique(path)
    base = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/copied-fixed/certificate.json"],
        cwd=ROOT,
    )
    require(sha256(base).hexdigest() == BASE_CERTIFICATE_SHA256, "base certificate sha256 drift")
    old = json.loads(base.decode("utf-8"))
    new = json.loads(committed)
    old_pin = old["local_sha256"].pop("research/copied-fixed/data_corners.cpp")
    new_pin = new["local_sha256"].pop("research/copied-fixed/data_corners.cpp")
    require(old_pin == ORIGINAL_SHA256, "unexpected base local pin")
    require(new_pin == digest_file(PRODUCTION), "certificate pin != working source")
    require(old == new, "certificate changed outside the single data_corners.cpp local_sha256 pin")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite research/copied-fixed/certificate.json local pin (default: read-only)",
    )
    args = parser.parse_args(argv)

    original = check_baseline_bytes()
    production = check_production_transform(original)
    expected = check_receipt_equivalence(original.decode("utf-8"), production)
    corruption = check_temp_corruption(production)
    check_certificate(write=args.write_certificate)
    print(
        "PASS_DATA_CORNER_PRODUCTION "
        f"pairs={expected['pairs']} good={expected['good']} "
        f"fallback={expected['fallback']} corruption={corruption} "
        "certs=1 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
