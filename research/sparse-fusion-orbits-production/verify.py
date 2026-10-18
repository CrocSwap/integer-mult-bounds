#!/usr/bin/env python3
"""Equivalence, rejection and certificate controls for production orbit screens.

Read-only by default. Regenerates no certificate unless --write-certificate is
passed. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from math import comb
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from prepare_layers import serializable  # noqa: E402
import audit_sparse_fusion as production  # noqa: E402

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "4e8e789d686b85a49fc12d36f87619eed705d6a8"
ORIGINAL_SHA256 = "bbaa32f9786f083409e363b081bfb7a1e597c8d32e4183c13a4105c2170934ce"
BASE_CERTIFICATE_SHA256 = "b7f0976e757998011f16022181246ad1b70db5b17ed32167f7e92368d2b43ee6"
SCREEN_HEIGHTS = (22, 25, 28)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json_unique(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def load_base_certificate_bytes() -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:certificates/sparse-fusion-audit.json"],
        cwd=ROOT,
    )


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:scripts/audit_sparse_fusion.py"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base audit_sparse_fusion.py sha256 drift")
    require(
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/audit_sparse_fusion.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
        == ORIGINAL_BLOB,
        "base audit_sparse_fusion.py blob drift",
    )
    require(
        (PACKAGE / "baseline.py").read_bytes() == original,
        "baseline.py must be an exact copy of the base-commit source",
    )


def check_orbit_inventory() -> None:
    for h in SCREEN_HEIGHTS:
        reps = production.orbit_representatives(h)
        require(len(reps) == 8, f"expected eight orbits at h={h}")
        require(sum(weight for _, weight in reps) == comb(h, 3), f"orbit cover failed at h={h}")
        lows = sorted(t & 7 for t, _ in reps)
        require(lows == list(range(8)), f"orbit low masks incomplete at h={h}")


def check_screen_equivalence(baseline, optimized) -> list[dict]:
    rows = []
    for h in SCREEN_HEIGHTS:
        old = baseline.central_gate_screen(h)
        new = optimized.central_gate_screen(h)
        require(old == new, f"central_gate_screen receipt differs at h={h}")
        require(old["triples"] == comb(h, 3), f"triple count wrong at h={h}")
        require(old["joint_frame_pairs"] == 4096, f"joint pairs lost at h={h}")
        rows.append(old)
    return rows


def check_certificate_equivalence(baseline, optimized) -> dict:
    old = serializable(baseline.certificate())
    new = serializable(optimized.certificate())
    require(old == new, "complete sparse-fusion certificate differs from baseline")
    return new


def check_rejections(baseline, optimized) -> None:
    for eng, name in ((baseline, "baseline"), (optimized, "optimized")):
        try:
            eng.central_gate_screen(21)
            raise AssertionError(f"{name} accepted h=21")
        except ValueError as exc:
            require("admissible" in str(exc).lower(), str(exc))
    try:
        production.orbit_representatives(21)
        raise AssertionError("orbit_representatives accepted h=21")
    except ValueError as exc:
        require("admissible" in str(exc).lower(), str(exc))


def check_temp_corruption(optimized) -> None:
    with tempfile.TemporaryDirectory(prefix="sparse-fusion-orbits-prod-") as tmp:
        dest = Path(tmp) / "audit_sparse_fusion.py"
        shutil.copy2(SCRIPTS / "audit_sparse_fusion.py", dest)
        text = dest.read_text(encoding="utf-8")
        # Force every orbit weight to 1 so the unary sum undercounts while the
        # v=C(h,3) baseline stays large; the proved lower-bound require fails.
        mutated = text.replace(
            "comb(h - 3, 3 - low.bit_count())",
            "1",
            1,
        )
        require(mutated != text, "mutation did not edit production source text")
        dest.write_text(mutated, encoding="utf-8")
        mutant = load_module(dest, "audit_sparse_fusion_mutant")
        try:
            mutant.central_gate_screen(25)
            raise AssertionError("weight-omission mutant accepted the h=25 screen")
        except ValueError as exc:
            require(
                "lower bound" in str(exc).lower() or "central-frame" in str(exc).lower(),
                str(exc),
            )
        # Live production path still accepts the historical screen.
        optimized.central_gate_screen(25)


def check_certificate(write: bool, regenerated: dict) -> None:
    path = ROOT / "certificates" / "sparse-fusion-audit.json"
    text = json.dumps(regenerated, indent=2, sort_keys=True) + "\n"
    if write:
        path.write_text(text, encoding="utf-8")
    committed = path.read_text(encoding="utf-8")
    require(
        committed == text,
        "working certificates/sparse-fusion-audit.json does not match regenerated certificate()",
    )
    load_json_unique(path)
    base = load_base_certificate_bytes()
    require(sha256(base).hexdigest() == BASE_CERTIFICATE_SHA256, "base certificate sha256 drift")
    # This audit has no source_sha256 map; the mathematical certificate must
    # remain byte-identical to the base after the production wiring.
    require(committed.encode("utf-8") == base, "certificate bytes changed after orbit wiring")
    require(
        digest_file(SCRIPTS / "audit_sparse_fusion.py") != ORIGINAL_SHA256,
        "production source unexpectedly unchanged",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite certificates/sparse-fusion-audit.json (default: read-only check)",
    )
    args = parser.parse_args(argv)

    check_baseline_bytes()
    check_orbit_inventory()
    baseline = load_module(PACKAGE / "baseline.py", "audit_sparse_fusion_baseline")
    screens = check_screen_equivalence(baseline, production)
    regenerated = check_certificate_equivalence(baseline, production)
    check_rejections(baseline, production)
    check_temp_corruption(production)
    check_certificate(write=args.write_certificate, regenerated=regenerated)
    print(
        "PASS_SPARSE_FUSION_ORBITS_PRODUCTION "
        f"screen_heights={list(SCREEN_HEIGHTS)} "
        f"screen_cases={len(screens)} "
        "certs=1 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
