#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production frame-pair enumeration.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/complex-frame-pair-decoders/verify.py"
BASELINE = PACKAGE / "baseline.py"
FAST = ROOT / "research/frame-pair-enumeration-fast-seed93/fast.py"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "57dd8993e8ac016e8a92a9a885392b58014137bb"
ORIGINAL_SHA256 = "bdf7ee497dc04dfc634ee5b7848f6a2b39b0169668fb1a60a9715111dbd15395"
OPTIMIZED_SHA256 = "f7a9a39659c179853af3220f83a11b4c3cf52c8f3bccc0911a5629add10fbaff"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_module(path: Path, name: str):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    # Keep assertions even when this wrapper is launched under -O.
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
    return module


def canonical(obj):
    return json.dumps(
        json.loads(json.dumps(obj, allow_nan=False)),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def scoped_receipt(module) -> dict:
    """Replay PR968 sections D/E/H only (G binds the selected kappa record)."""
    stream = []
    rank_records = []
    original = module.frame_pair_solutions
    original_pair = module.pair_decoder

    def enumerate_pairs(a, b):
        result = original(a, b)
        stream.append([a, b, result])
        return result

    def pair_check(pairs, live):
        answer = original_pair(pairs, live)
        rank_records.append([pairs, live, answer])
        return answer

    module.frame_pair_solutions = enumerate_pairs
    module.pair_decoder = pair_check
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        frames, example, hist, kinds = module.section_d()
        chain = module.section_e(frames, example)
        module.section_h(example, frames, hist)
    require(not module.FAILS, f"predecessor checks failed: {module.FAILS}")
    require(
        len(frames) == 1260 and len(stream) == 2520 and len(rank_records) == 7168,
        "complete D/H enumeration/rank coverage",
    )
    return {
        "frames": len(frames),
        "enumerations": len(stream),
        "decoder_rank_checks": len(rank_records),
        "term_rank_checks": sum(len(record[2][1]) for record in rank_records),
        "ordered_solution_stream_sha256": digest(stream),
        "rank_stream_sha256": digest(rank_records),
        "histogram": sorted(hist.items()),
        "types": sorted((str(k), v) for k, v in kinds.items()),
        "example": example,
        "chain": chain,
        "log": capture.getvalue().splitlines(),
    }


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/complex-frame-pair-decoders/verify.py"],
        cwd=ROOT,
    )
    require(hashlib.sha256(original).hexdigest() == ORIGINAL_SHA256, "base verify.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/complex-frame-pair-decoders/verify.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base verify.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit verify.py")
    require(
        digest_file(PRODUCTION) == OPTIMIZED_SHA256,
        "production verify.py does not match the claimed optimized digest",
    )
    require(PRODUCTION.read_bytes() != original, "production must differ from the pairwise baseline")
    text = PRODUCTION.read_text(encoding="utf-8")
    require("neighbors = [sum(bool(IP[g][f])" in text, "production missing neighborhood masks")
    require("Eight-bit neighborhood masks" in text, "production missing credit comment")


def check_equivalence() -> dict:
    base = load_module(BASELINE, "frame_pair_baseline")
    prod = load_module(PRODUCTION, "frame_pair_production")
    base_receipt = scoped_receipt(base)
    prod_receipt = scoped_receipt(prod)
    require(base_receipt == prod_receipt, "D/E/H receipt mismatch between baseline and production")
    # Pointwise census over every second frame.
    frames = base.frames_in(base.P112)
    require(len(frames) == 1260, "frame count")
    for frame in frames:
        require(
            base.frame_pair_solutions(base.FRAME0, list(frame))
            == prod.frame_pair_solutions(prod.FRAME0, list(frame)),
            "pointwise frame_pair_solutions mismatch",
        )
    return {
        "frames": 1260,
        "decoders": 7168,
        "term_ranks": base_receipt["term_rank_checks"],
        "ordered_solution_stream_sha256": base_receipt["ordered_solution_stream_sha256"],
        "rank_stream_sha256": base_receipt["rank_stream_sha256"],
    }


def check_temp_corruption_rejection() -> dict:
    """On-disk mutant that never accepts a singleton neighborhood must fail."""
    honest = scoped_receipt(load_module(PRODUCTION, "frame_pair_honest"))
    with tempfile.TemporaryDirectory(prefix="frame-pair-prod-") as tmp:
        mutant_path = Path(tmp) / "verify.py"
        text = PRODUCTION.read_text(encoding="utf-8")
        needle = "if hit and hit & (hit - 1) == 0:"
        require(text.count(needle) == 2, "expected two singleton-neighborhood tests")
        foil = text.replace(needle, "if False and hit and hit & (hit - 1) == 0:", 1)
        mutant_path.write_text(foil, encoding="utf-8")
        require(mutant_path.read_bytes() != PRODUCTION.read_bytes(), "mutant must differ on disk")
        try:
            bad = scoped_receipt(load_module(mutant_path, "frame_pair_mutant"))
        except Exception as exc:  # noqa: BLE001 — foil may raise AssertionError or census TypeError
            return {"rejected": True, "mode": "subprocess_failure", "detail": f"{type(exc).__name__}: {exc}"[:240]}
        require(bad != honest, "disabled neighborhood test must change the D/E/H receipt")
        return {
            "rejected": True,
            "mode": "receipt_divergence",
            "honest_stream": honest["ordered_solution_stream_sha256"],
            "mutant_stream": bad["ordered_solution_stream_sha256"],
        }


def check_opt_in_fast_module() -> None:
    """Historical fast.py still matches production on the live IP table."""
    prod = load_module(PRODUCTION, "frame_pair_prod_fast_check")
    spec = types.ModuleType("fast_enum")
    exec(compile(FAST.read_bytes(), str(FAST), "exec", optimize=0), spec.__dict__)
    for frame in prod.frames_in(prod.P112):
        require(
            prod.frame_pair_solutions(prod.FRAME0, list(frame))
            == spec.frame_pair_solutions(prod.FRAME0, list(frame), prod.IP),
            "production diverges from opt-in fast.py",
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-result",
        action="store_true",
        help="unused placeholder; default verify is read-only and never writes certificates",
    )
    args = parser.parse_args(argv)
    require(not args.write_result, "default verify is read-only; do not pass --write-result")

    check_baseline_bytes()
    receipt = check_equivalence()
    corruption = check_temp_corruption_rejection()
    check_opt_in_fast_module()
    # Duplicate-key control on a tiny JSON object used by this package.
    json.loads('{"a":1,"b":2}', object_pairs_hook=unique_object)

    print(
        "PASS_FRAME_PAIR_ENUMERATION_PRODUCTION "
        f"frames={receipt['frames']} decoders={receipt['decoders']} "
        f"term_ranks={receipt['term_ranks']} "
        f"corruption={corruption['mode']} "
        "certs=0 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
