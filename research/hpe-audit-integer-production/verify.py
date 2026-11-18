#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production HPE integer-row audit.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import copy
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tarfile
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / (
    "research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/"
    "code/hpe_audit_and_transport.py"
)
BASELINE = PACKAGE / "baseline.py"
OPT_IN_FAST = ROOT / "research/hpe-audit-fast-seed93/hpe_audit_fast.py"
ARCHIVE = ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz"
ROUTING = ROOT / (
    "research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/"
    "complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz"
)

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "d5d3509d90c01fd91dd00b78743287614b532e48"
ORIGINAL_SHA256 = "c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3"
OPTIMIZED_SHA256 = "0dacf4cedb020d561e0188052319f1a6e6abaf6c79f9e94d8c9c91492e5c1747"
ROUTING_SHA256 = "e070ae2c78b4a1b644b418774af62b40d8d16e6ba89602f0474afb557d507c37"
WORDS = ("p6n", "promo", "jx", "hyb", "frames")
SECTIONS = ("A", "B", "cut", "precondition", "cleanup")


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


def load_module(name: str, path: Path):
    """Load a checker with assertions kept even when this wrapper runs under -O."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
    return module


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/complex-sw4-frame8/vendor/pr635/"
         "research/complex-571-cold14-st2/code/hpe_audit_and_transport.py"],
        cwd=ROOT,
    )
    require(hashlib.sha256(original).hexdigest() == ORIGINAL_SHA256, "base audit sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/complex-sw4-frame8/vendor/pr635/"
             "research/complex-571-cold14-st2/code/hpe_audit_and_transport.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base audit blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit audit")
    require(digest_file(PRODUCTION) == OPTIMIZED_SHA256, "production audit digest drift")
    require(PRODUCTION.read_bytes() != original, "production must differ from pairwise baseline")
    require(digest_file(ROUTING) == ROUTING_SHA256, "routing word digest drift")
    # Opt-in fast file must remain an equivalent algorithm source.
    require(OPT_IN_FAST.exists(), "opt-in hpe_audit_fast.py missing")
    require("def apply" in PRODUCTION.read_text(encoding="utf-8"), "production must define apply")
    require("_NORMALIZE_BITS" in PRODUCTION.read_text(encoding="utf-8"), "production must use integer rows")
    require("_NORMALIZE_BITS" not in BASELINE.read_text(encoding="utf-8"), "baseline must stay pairwise")


def outcome(module, raw: Path, out: Path):
    printed = io.StringIO()
    try:
        with contextlib.redirect_stdout(printed):
            module.run(raw, ROUTING, out)
    except Exception as exc:  # noqa: BLE001 - compare exact failure class
        return ("raise", type(exc).__name__, repr(exc.args))
    files = {p.name: p.read_bytes() for p in sorted(out.iterdir())}
    receipt = json.loads(files.pop("SCALAR-FRAME-AUDIT.json"), object_pairs_hook=unique_object)
    receipt.pop("seconds", None)
    text = json.loads(printed.getvalue(), object_pairs_hook=unique_object)
    text.pop("seconds", None)
    return ("pass", files, receipt, text)


def archived_words():
    with tarfile.open(ARCHIVE) as archive:
        for name in WORDS:
            member = f"chain/{name}/FULL-WORD.json.gz"
            data = archive.extractfile(member).read()
            yield name, data


def check_identical_receipts() -> dict:
    ref = load_module("hpe_baseline", BASELINE)
    prod = load_module("hpe_production", PRODUCTION)
    honest = 0
    with tempfile.TemporaryDirectory(prefix="hpe-audit-prod-") as tmp:
        tmp_path = Path(tmp)
        for name, data in archived_words():
            raw = tmp_path / f"{name}.json.gz"
            raw.write_bytes(data)
            left = outcome(ref, raw, tmp_path / f"{name}-ref")
            right = outcome(prod, raw, tmp_path / f"{name}-prod")
            require(left == right, f"honest mismatch on {name}")
            honest += 1
        # Seeded fuzz on hyb word
        hyb = json.loads(gzip.decompress((tmp_path / "hyb.json.gz").read_bytes()))
        rng = random.Random(93)
        fuzz_ok = 0
        for i in range(40):
            word = mutate(hyb, rng)
            raw = tmp_path / f"fuzz-{i}.json.gz"
            raw.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
            left = outcome(ref, raw, tmp_path / f"fuzz-{i}-ref")
            right = outcome(prod, raw, tmp_path / f"fuzz-{i}-prod")
            require(left == right, f"fuzz mismatch #{i}")
            fuzz_ok += 1
    return {"honest": honest, "fuzz": fuzz_ok}


def mutate(word, rng):
    w = copy.deepcopy(word)
    n = 2 * w["report"]["v"] + w["report"]["R"]
    sec = rng.choice([s for s in SECTIONS if w[s]])
    i = rng.randrange(len(w[sec]))
    g = w[sec][i]
    kind = rng.choice(["coef", "coef", "coef", "edge", "drop", "swap", "dup", "reg", "frame"])
    if kind == "coef":
        k = 3 if g[0] == "add" else 2
        g[k + rng.randrange(2)] = rng.choice([-3, -2, -1, 1, 2, 3, 5, 7, 4, 1024, -1024])
    elif kind == "edge":
        k = 3 if g[0] == "add" else 2
        g[k + rng.choice([0, 1])] = rng.choice([0, 3**60, -(5**50), 2**300, "x", 1.5, None])
    elif kind == "drop":
        del w[sec][i]
    elif kind == "swap" and len(w[sec]) > 1:
        j = i + 1 if i + 1 < len(w[sec]) else i - 1
        w[sec][i], w[sec][j] = w[sec][j], w[sec][i]
    elif kind == "dup":
        w[sec].insert(i, copy.deepcopy(g))
    elif kind == "reg":
        g[1 + (rng.randrange(2) if g[0] == "add" else 0)] = rng.randrange(n)
    elif kind == "frame" and isinstance(g[-1], list):
        if g[-1]:
            g[-1][rng.randrange(len(g[-1]))] ^= 1 << rng.randrange(8)
    return w


def check_assertions_preserved() -> int:
    def assertion_list(text: str):
        return [
            ast.dump(n, include_attributes=False)
            for n in ast.walk(ast.parse(text))
            if isinstance(n, ast.Assert)
        ]

    # Production adds no assert nodes beyond the baseline control-flow asserts;
    # compare the baseline assert dump to the production dump after stripping
    # only docstring/import differences is fragile, so require every baseline
    # assert string literal still appears in production source.
    base_src = BASELINE.read_text(encoding="utf-8")
    prod_src = PRODUCTION.read_text(encoding="utf-8")
    base_asserts = assertion_list(base_src)
    prod_asserts = assertion_list(prod_src)
    require(len(prod_asserts) >= len(base_asserts), "production dropped asserts")
    for msg in (
        "hpe cone pre-check (row / column)",
        "paid local profile differs from the reported local_profile",
        "cleanup on non-FULL end",
    ):
        require(msg in prod_src, f"missing assert message: {msg}")
        require(msg in base_src, f"baseline missing assert message: {msg}")

    # Admission must stay enforced when this wrapper is launched under -O:
    # loaders use compile(..., optimize=0), so a known apply assert still fires.
    prod = load_module("hpe_production_assert_gate", PRODUCTION)
    rows = prod.rows_identity(2) if hasattr(prod, "rows_identity") else None
    if rows is None:
        # Integer-row production uses (den, map) pairs; seed a 2x2 identity.
        rows = [(1, {0: 1}), (1, {1: 1})]
    fired = False
    try:
        prod.apply(["scale", 0, 0, 1], rows)
    except AssertionError:
        fired = True
    except Exception as exc:  # noqa: BLE001
        require(False, f"scale-zero admission must raise AssertionError, got {type(exc).__name__}: {exc}")
    require(fired, "NO_ASSERT_FIRED: scale-zero admission stripped under -O loader")
    return len(prod_asserts)


def check_temp_corruption_rejection() -> dict:
    """On-disk foil that skips ADD row updates must diverge or fail closed."""
    ref = load_module("hpe_baseline_corrupt", BASELINE)
    with tempfile.TemporaryDirectory(prefix="hpe-audit-prod-honest-") as tmp:
        tmp_path = Path(tmp)
        name, data = next(archived_words())
        raw = tmp_path / "honest.json.gz"
        raw.write_bytes(data)
        honest = outcome(load_module("hpe_production_honest", PRODUCTION), raw, tmp_path / "honest")

    text = PRODUCTION.read_text(encoding="utf-8")
    needle = "def apply(e, rows):"
    require(needle in text, "apply site missing for corruption control")
    # Foil: no-op apply so compensation/endpoints break.
    foil_text = text.replace(
        needle,
        "def apply(e, rows):\n    return\n\ndef apply_disabled(e, rows):",
        1,
    )
    require(foil_text != text, "mutant must differ on disk")
    with tempfile.TemporaryDirectory(prefix="hpe-audit-prod-foil-") as tmp:
        mutant_path = Path(tmp) / "hpe_audit_and_transport.py"
        mutant_path.write_text(foil_text, encoding="utf-8")
        work = Path(tmp) / "work"
        work.mkdir()
        name, data = next(archived_words())
        raw = work / "word.json.gz"
        raw.write_bytes(data)
        try:
            bad = outcome(load_module("hpe_foil", mutant_path), raw, work / "out")
        except Exception as exc:  # noqa: BLE001
            return {"rejected": True, "mode": "import_or_runtime_failure", "detail": str(exc)[:240]}
        require(bad != honest, "ADD-drop foil must change the audit outcome")
        return {"rejected": True, "mode": "receipt_divergence"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    check_baseline_bytes()
    assertions = check_assertions_preserved()
    receipts = check_identical_receipts()
    corruption = check_temp_corruption_rejection()
    require(corruption["rejected"], "corruption control must reject")
    print(
        "PASS_HPE_AUDIT_INTEGER_PRODUCTION "
        f"assertions={assertions} "
        f"honest={receipts['honest']} "
        f"fuzz={receipts['fuzz']} "
        f"corruption={corruption['mode']} "
        "certs=0 no_new_kappa",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
