#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production packed omission atlas.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import random
import subprocess
import sys
import tempfile
import types
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ATLAS = ROOT / "research/r439-omission-atlas-seed81"
PRODUCTION = ATLAS / "verify.py"
BASELINE = PACKAGE / "baseline.py"
CERTIFICATE = ATLAS / "CERTIFICATE.json"
OPT_IN_REPLAY = ROOT / "research/omission-lanes-seed92/replay.py"

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "759d18d73dbab5d7620ce61395110aa57c06f901"
ORIGINAL_SHA256 = "127d7679fb26e264018548a1301b2f0f437d834eb1f0ffa215556243077ff866"
OPTIMIZED_SHA256 = "6c3c94b01e3db5fb6d9e45eda4f60628252de1fab218e6e8233cc7949afd8966"
CERT_SHA256 = "05c44b5d818862563a6674131024b1460d1e7bcb7828e4ebee4ec0198129e4e7"


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


def load_checker(name: str, source: Path):
    """Load atlas checker with assertions kept even when this wrapper runs under -O.

    `__file__` is always the live atlas path so HERE/SOURCES/CERTIFICATE resolve.
    """
    module = types.ModuleType(name)
    module.__file__ = str(PRODUCTION)
    exec(compile(source.read_bytes(), str(PRODUCTION), "exec", optimize=0), module.__dict__)
    return module


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/r439-omission-atlas-seed81/verify.py"],
        cwd=ROOT,
    )
    require(hashlib.sha256(original).hexdigest() == ORIGINAL_SHA256, "base atlas sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/r439-omission-atlas-seed81/verify.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base atlas blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit atlas")
    require(digest_file(PRODUCTION) == OPTIMIZED_SHA256, "production atlas digest drift")
    require(PRODUCTION.read_bytes() != original, "production must differ from literal baseline")
    require(digest_file(CERTIFICATE) == CERT_SHA256, "certificate digest drift")
    require(OPT_IN_REPLAY.exists(), "opt-in packed replay missing")
    prod_text = PRODUCTION.read_text(encoding="utf-8")
    base_text = BASELINE.read_text(encoding="utf-8")
    require("def packed_replays(" in prod_text, "production must define packed_replays")
    require("mutants=packed_replays(gates,N)" in prod_text.replace(" ", ""),
            "production must consume packed mutants")
    require("def packed_replays(" not in base_text, "baseline must stay literal")
    require("changed=replay(gates,k)" in base_text.replace(" ", ""),
            "baseline must keep per-omission replay")


def outcome(module) -> tuple:
    printed = io.StringIO()
    try:
        with redirect_stdout(printed):
            result = module.run()
            # Match CLI certificate binding without writing.
            module.need(
                module.canonical(module.load(module.canonical(result)))
                == module.canonical(module.load(CERTIFICATE.read_bytes())),
                "certificate mismatch",
            )
    except Exception as exc:  # noqa: BLE001 - compare exact failure class/message
        return ("raise", type(exc).__name__, str(exc))
    return ("pass", module.canonical(result), printed.getvalue())


def check_identical_receipts() -> dict:
    ref = load_checker("omission_baseline", BASELINE)
    prod = load_checker("omission_production", PRODUCTION)
    left = outcome(ref)
    right = outcome(prod)
    require(left == right, "honest mismatch on R439 omission atlas")
    require(left[0] == "pass", "honest atlas must pass")
    expected = ref.canonical(ref.load(CERTIFICATE.read_bytes()))
    require(left[1] == expected, "honest receipt must match CERTIFICATE.json")

    # Independent packed/literal matrix stream agreement (same as opt-in).
    gates = ref.expand(ref.load_inputs()[0])
    count = 0
    for k, actual in enumerate(prod.packed_replays(gates, ref.N)):
        expected_rows = ref.replay(gates, k)
        require(actual == expected_rows, f"full literal matrix mismatch: {k}")
        count += 1
    require(count == 5563, "full literal omission coverage")

    # Seeded short-word / batch-boundary agreement.
    rng = random.Random(92)
    edges = [(d, s, 0, 0) for d in range(3) for s in range(3) if d != s]
    from itertools import product

    words = [word for length in range(5) for word in product(edges, repeat=length)]
    words += [
        tuple(rng.choice(edges) for _ in range(length))
        for length in (15, 16, 17, 31, 32, 33, 63, 64, 65)
    ]
    short_ok = 0
    for word in words:
        expected_maps = [ref.replay(word, k)[:3] for k in range(len(word))]
        for size in (1, 2, 3, 16, 64):
            require(
                list(prod.packed_replays(word, 3, size)) == expected_maps,
                "short-word or batch-boundary mismatch",
            )
            short_ok += 1
    return {"honest": 1, "matrices": count, "short_checks": short_ok}


def check_temp_corruption_rejection() -> dict:
    """On-disk foil that flips one packed mutant bit must reject closed."""
    text = PRODUCTION.read_text(encoding="utf-8")
    needle = "changed=next(mutants,None)"
    require(needle in text, "packed mutant site missing for corruption control")
    foil = (
        "changed=next(mutants,None)\n"
        "        if changed is not None and k==16:\n"
        "            changed=list(changed);changed[-1]^=1<<(N-1)\n"
    )
    foil_text = text.replace(needle + "\n", foil, 1)
    require(foil_text != text, "mutant must differ on disk")
    with tempfile.TemporaryDirectory(prefix="omission-lanes-prod-foil-") as tmp:
        mutant_path = Path(tmp) / "verify.py"
        mutant_path.write_text(foil_text, encoding="utf-8")
        # Point HERE at atlas via __file__, but execute foil bytes.
        module = types.ModuleType("omission_foil")
        module.__file__ = str(PRODUCTION)
        exec(compile(mutant_path.read_bytes(), str(PRODUCTION), "exec", optimize=0), module.__dict__)
        printed = io.StringIO()
        try:
            with redirect_stdout(printed):
                module.run()
            raise AssertionError("corruption accepted")
        except ValueError as exc:
            require(
                "literal omission delta disagrees at 16" in str(exc),
                f"wrong rejection: {exc}",
            )
    return {"corruption": 1}


def check_duplicate_json_keys() -> None:
    raw = CERTIFICATE.read_bytes()
    json.loads(raw, object_pairs_hook=unique_object)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    check_baseline_bytes()
    receipts = check_identical_receipts()
    corruption = check_temp_corruption_rejection()
    check_duplicate_json_keys()
    print(
        "PASS_OMISSION_LANES_PRODUCTION "
        f"honest={receipts['honest']} matrices={receipts['matrices']} "
        f"short_checks={receipts['short_checks']} "
        f"corruption={corruption['corruption']} certs=1 no_new_kappa",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
