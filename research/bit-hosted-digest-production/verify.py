#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production hosted digest.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = (
    ROOT
    / "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage"
    / "vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py"
)
PARAMETERIZER = ROOT / "research/e8-bit-p111-tuned/code/adapt9p.py"
FIXTURE = ROOT / "research/community-hyperplane599-audit/pr589/bit589"
RETAINED_AUDIT = FIXTURE / "v9/hosted/AUDIT.json"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "8864ca9b942a3507171edca0cf6cbaaf10fcf434"
ORIGINAL_SHA256 = "57e558c80a2fea6e291587b04afd76dfaee3550729997798b61f33daf90b8ec9"
PRODUCTION_SHA256 = "9d0b44e37109128850192414bf0fefb1048bf96da2c78dff8e833980b20f61c7"
PRODUCTION_BLOB = "fefec67382782e2624016545f770f95b03cc5da5"
EMITTED_PROGRAM_SHA256 = "96c7ad2e744e9a503a4ef5ecd52d0f6a8899bdb5efac2e3aafa0db18adf99523"
EMITTED_EVENTS = 7843392
PARAMETERIZER_SHA256 = "14365d0eb8f4a7352edd28816196148fd28d5bbcb36044ebeeb15ca051bca9de"

def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json_unique(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def old_digest_block() -> str:
    baseline = (PACKAGE / "baseline.py").read_text(encoding="utf-8")
    marker = "def digest(t):"
    start = baseline.index(marker)
    end = baseline.index("def main():", start)
    return baseline[start:end]


def new_digest_block() -> str:
    production = PRODUCTION.read_text(encoding="utf-8")
    marker = "def _enc(value):"
    start = production.index(marker)
    end = production.index("def main():", start)
    return production[start:end]


def transform(source: str) -> str:
    old = old_digest_block()
    new = new_digest_block()
    require(source.count(old) == 1, "expected exactly one pairwise digest block in baseline")
    return source.replace(old, new)


def check_baseline_bytes() -> bytes:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py"],
        cwd=ROOT,
    )
    require(digest_file_bytes(original) == ORIGINAL_SHA256, "base audit_hosted_k.py sha256 drift")
    require(
        subprocess.check_output(
            [
                "git",
                "rev-parse",
                f"{BASE_COMMIT}:research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py",
            ],
            cwd=ROOT,
        )
        .decode()
        .strip()
        == ORIGINAL_BLOB,
        "base audit_hosted_k.py blob drift",
    )
    require(
        (PACKAGE / "baseline.py").read_bytes() == original,
        "baseline.py must be an exact copy of the base-commit source",
    )
    return original


def digest_file_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_production_transform(original: bytes) -> str:
    production = PRODUCTION.read_text(encoding="utf-8")
    expected = transform(original.decode("utf-8"))
    require(production == expected, "production audit_hosted_k.py != transform(baseline)")
    require(digest_file(PRODUCTION) == PRODUCTION_SHA256, "production sha256 drift")
    require("_enc" in production and "fragment reuse" in production, "fragment digest markers missing")
    require("Independent streamed hashing uses the same specified JSON" not in production,
            "pairwise digest comment still present")
    require(production.count("def digest(t):") == 1, "digest definition count")
    return production


def load_parameterized(source_path: Path):
    """Apply the five hosted-auditor adapt9p edits to a source file."""
    require(digest_file(PARAMETERIZER) == PARAMETERIZER_SHA256, "adapt9p.py sha256 drift")
    original = source_path.read_text(encoding="utf-8")
    adapter = PARAMETERIZER.read_text(encoding="utf-8")
    assignments = [
        n
        for n in ast.parse(adapter).body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "EDITS" for t in n.targets)
    ]
    require(len(assignments) == 1, "expected one EDITS dictionary")
    edits_dict = assignments[0].value
    entries = [
        v
        for k, v in zip(edits_dict.keys, edits_dict.values)
        if ast.literal_eval(k) == "audit_hosted_k.py"
    ]
    require(len(entries) == 1, "expected one hosted-auditor edit list")
    edits = ast.literal_eval(entries[0].elts[1])
    require(len(edits) == 5, "expected five parameterization edits")
    for old, new in edits:
        require(original.count(old) == 1, "parameterization anchor mismatch")
        original = original.replace(old, new)
    module = types.ModuleType("pinned_hosted_auditor")
    module.__file__ = str(source_path)
    # Assertions in the inherited auditor remain proof-relevant.
    code = compile(original, module.__file__, "exec")
    exec(code, module.__dict__)
    return module


def prepare_parent(work: Path) -> Path:
    parent = work / "parent"
    shutil.copytree(
        FIXTURE / "v9/nine",
        parent / "nine",
        ignore=shutil.ignore_patterns("AUDIT.json", "GEOMETRY.json"),
    )
    shutil.copytree(FIXTURE / "records", parent / "records")
    return parent


def run_audit(auditor, parent: Path, hosted: Path, output: Path) -> dict:
    argv = sys.argv
    try:
        sys.argv = [auditor.__file__, str(parent), str(hosted), str(output)]
        with contextlib.redirect_stdout(io.StringIO()):
            auditor.main()
    finally:
        sys.argv = argv
    return load_json_unique(output)


def check_receipt_equivalence() -> dict:
    retained = load_json_unique(RETAINED_AUDIT)
    require(retained["emitted_program_sha256"] == EMITTED_PROGRAM_SHA256, "retained digest drift")
    require(retained["emitted_events"] == EMITTED_EVENTS, "retained event count drift")
    with tempfile.TemporaryDirectory(prefix="bit-hosted-digest-production-") as tmp:
        work = Path(tmp)
        parent = prepare_parent(work)
        hosted = FIXTURE / "v9/hosted"
        baseline_mod = load_parameterized(PACKAGE / "baseline.py")
        production_mod = load_parameterized(PRODUCTION)
        # adapt9p leaves V=None until main(); pairwise digest still reads module V.
        parent_v = load_json_unique(parent / "nine" / "GLOBAL.json")["v"]
        baseline_mod.V = parent_v
        production_mod.V = parent_v
        template = json.loads(gzip.decompress((hosted / "GLOBAL-TEMPLATE.json.gz").read_bytes()))
        require(baseline_mod.digest(template) == production_mod.digest(template), "digest tuple mismatch")
        require(production_mod.digest(template) == (EMITTED_PROGRAM_SHA256, EMITTED_EVENTS),
                "production digest != retained")
        base_receipt = run_audit(baseline_mod, parent, hosted, work / "baseline.json")
        prod_receipt = run_audit(production_mod, parent, hosted, work / "production.json")
        require(base_receipt == prod_receipt == retained, "full hosted audit receipt mismatch")
        require(
            (work / "baseline.json").read_bytes() == (work / "production.json").read_bytes(),
            "audit JSON output bytes differ",
        )
        require(len(prod_receipt["mutations_rejected"]) == 16, "inherited mutation coverage changed")
        return {
            "emitted_program_sha256": prod_receipt["emitted_program_sha256"],
            "emitted_events": prod_receipt["emitted_events"],
            "mutations_rejected": prod_receipt["mutations_rejected"],
        }


def check_corruption_rejection() -> str:
    """Temp-copy foil: permute a digest fragment so receipts diverge or the audit fails."""
    with tempfile.TemporaryDirectory(prefix="bit-hosted-digest-corrupt-") as tmp:
        work = Path(tmp)
        corrupt = work / "audit_hosted_k.py"
        text = PRODUCTION.read_text(encoding="utf-8")
        foil = "pending.extend(owners[destination])"
        require(text.count(foil) == 1, "corruption foil site missing")
        # Drop the destination owner fragment: changes the emitted stream.
        corrupt.write_text(text.replace(foil, "pending.extend(b'')  # foil"), encoding="utf-8")
        parent = prepare_parent(work)
        hosted = FIXTURE / "v9/hosted"
        module = load_parameterized(corrupt)
        template = json.loads(gzip.decompress((hosted / "GLOBAL-TEMPLATE.json.gz").read_bytes()))
        digest_hex, events = module.digest(template)
        require(digest_hex != EMITTED_PROGRAM_SHA256, "corruption foil left digest unchanged")
        require(events == EMITTED_EVENTS, "corruption foil changed event count unexpectedly")
        try:
            run_audit(module, parent, hosted, work / "corrupt.json")
        except (AssertionError, ValueError, subprocess.CalledProcessError):
            return "audit_assertion"
        # If main somehow returned, the receipt must still disagree.
        receipt = load_json_unique(work / "corrupt.json")
        require(receipt.get("emitted_program_sha256") != EMITTED_PROGRAM_SHA256,
                "corruption foil produced retained digest")
        return "receipt_mismatch"


def check_adapt9p_anchors(production: str) -> None:
    anchors = [
        "V=120\n",
        "DATA=2*K*V*T; DEFICIT=T*(2*K*V-9*8*L)",
        "def main():\n    par,bd,out=",
        "    t=template(bd/'GLOBAL-TEMPLATE.json.gz');g=read(bd/'GLOBAL.json');pg=read(par/'nine/GLOBAL.json')\n",
        "    DEFICIT=T*(2*K*V-9*8*L)\n",
    ]
    for anchor in anchors:
        require(production.count(anchor) == 1, "adapt9p anchor not unique: " + repr(anchor[:48]))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true", help="unused; verify is read-only")
    args = parser.parse_args(argv)
    require(not args.write_result, "verify.py is read-only; use benchmark.py --write-result")
    # Clear any inherited optimize flag for child semantics documentation.
    os.environ.pop("PYTHONOPTIMIZE", None)

    original = check_baseline_bytes()
    production = check_production_transform(original)
    check_adapt9p_anchors(production)
    receipt = check_receipt_equivalence()
    corruption = check_corruption_rejection()
    # Duplicate-key check already applied to retained/production receipts.
    load_json_unique(RETAINED_AUDIT)

    print(
        "PASS_BIT_HOSTED_DIGEST_PRODUCTION "
        f"events={receipt['emitted_events']} "
        f"digest={receipt['emitted_program_sha256'][:16]}… "
        f"mutations={len(receipt['mutations_rejected'])} "
        f"corruption={corruption} "
        "certs=1 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    # Under -O, re-exec an asserting child for the inherited auditor body.
    if not __debug__:
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(Path(__file__).resolve()), *sys.argv[1:]],
            cwd=ROOT,
        )
        raise SystemExit(proc.returncode)
    raise SystemExit(main())
