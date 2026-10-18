#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production HPE transport integer rows.

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
import types

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/complex-k492-owner-repair/code/hpe_audit_and_transport.py"
BASELINE = PACKAGE / "baseline.py"
ARCHIVE = ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz"
ROUTING = ROOT / (
    "research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/"
    "complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz"
)
OPT_IN_FAST = ROOT / "research/hpe-audit-fast-seed93/hpe_audit_fast.py"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "d5d3509d90c01fd91dd00b78743287614b532e48"
ORIGINAL_SHA256 = "c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3"
OPTIMIZED_SHA256 = "d777db4abe316594df5cd3dc1269b42f4af4a8c87d4d0df500d32655e3775b87"
ROUTING_SHA256 = "e070ae2c78b4a1b644b418774af62b40d8d16e6ba89602f0474afb557d507c37"
WORDS = ("p6n", "promo", "jx", "hyb", "frames")
SECTIONS = ("A", "B", "cut", "precondition", "cleanup")
FUZZ_TRIALS = 20
FUZZ_SEED = 93


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
    """Load a checker with assert statements enforced even when the driver runs under -O."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    # Keep assertions even when this wrapper is launched under -O.
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
    return module


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/complex-k492-owner-repair/code/hpe_audit_and_transport.py"],
        cwd=ROOT,
    )
    require(hashlib.sha256(original).hexdigest() == ORIGINAL_SHA256, "base hpe_audit_and_transport.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/complex-k492-owner-repair/code/hpe_audit_and_transport.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base hpe_audit_and_transport.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit transport auditor")
    require(
        digest_file(PRODUCTION) == OPTIMIZED_SHA256,
        "production hpe_audit_and_transport.py does not match the claimed optimized digest",
    )
    require(PRODUCTION.read_bytes() != original, "production must differ from the pairwise baseline")
    require(digest_file(ROUTING) == ROUTING_SHA256, "routing word pin drift")
    # Production must carry the opt-in integer-row markers.
    text = PRODUCTION.read_text(encoding="utf-8")
    require("def rows_identity(n):" in text, "production must define rows_identity")
    require("def rows_equal(rows, expected):" in text, "production must define rows_equal")
    require("from math import gcd" in text, "production must import gcd for row normalization")
    opt_in = OPT_IN_FAST.read_text(encoding="utf-8")
    require("def rows_identity(n):" in opt_in, "opt-in fast adapter missing rows_identity")


def outcome(module, raw: Path, out: Path):
    printed = io.StringIO()
    try:
        with contextlib.redirect_stdout(printed):
            module.run(raw, ROUTING, out)
    except Exception as exc:
        return ("raise", type(exc).__name__, repr(exc.args))
    files = {path.name: path.read_bytes() for path in sorted(out.iterdir())}
    receipt = json.loads(files.pop("SCALAR-FRAME-AUDIT.json"), object_pairs_hook=unique_object)
    receipt.pop("seconds", None)
    text = json.loads(printed.getvalue(), object_pairs_hook=unique_object)
    text.pop("seconds", None)
    return ("pass", files, receipt, text)


def load_words() -> dict:
    words = {}
    with tarfile.open(ARCHIVE) as archive:
        for name in WORDS:
            member = archive.extractfile(f"chain/{name}/FULL-WORD.json.gz")
            require(member is not None, f"missing archive member for {name}")
            words[name] = json.loads(gzip.decompress(member.read()))
    return words


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
        j = min(i + 1, len(w[sec]) - 1) if i + 1 < len(w[sec]) else i - 1
        w[sec][i], w[sec][j] = w[sec][j], w[sec][i]
    elif kind == "dup":
        w[sec].insert(i, copy.deepcopy(g))
    elif kind == "reg":
        g[1 + (rng.randrange(2) if g[0] == "add" else 0)] = rng.randrange(n)
    elif kind == "frame" and isinstance(g[-1], list) and g[-1]:
        j = rng.randrange(len(g[-1]))
        g[-1][j] ^= 1 << rng.randrange(9)
    return w


def check_identical_receipts() -> dict:
    baseline = load_module("hpe_transport_baseline", BASELINE)
    production = load_module("hpe_transport_production", PRODUCTION)
    words = load_words()
    with tempfile.TemporaryDirectory(prefix="hpe-transport-prod-") as tmp:
        tmp_path = Path(tmp)
        honest = 0
        for name, word in words.items():
            raw = tmp_path / f"honest-{name}.json.gz"
            raw.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
            base_out = outcome(baseline, raw, tmp_path / f"honest-{name}-base")
            prod_out = outcome(production, raw, tmp_path / f"honest-{name}-prod")
            require(base_out == prod_out, f"honest word mismatch: {name}")
            require(base_out[0] == "pass", f"honest word rejected: {name}")
            honest += 1
        rng = random.Random(FUZZ_SEED)
        fuzz_ok = 0
        for trial in range(FUZZ_TRIALS):
            name = WORDS[trial % len(WORDS)]
            mutant = mutate(words[name], rng)
            raw = tmp_path / f"fuzz-{trial}.json.gz"
            raw.write_bytes(gzip.compress(json.dumps(mutant).encode(), mtime=0))
            base_out = outcome(baseline, raw, tmp_path / f"fuzz-{trial}-base")
            prod_out = outcome(production, raw, tmp_path / f"fuzz-{trial}-prod")
            require(base_out == prod_out, f"fuzz mismatch trial={trial}")
            fuzz_ok += 1
    return {"honest": honest, "fuzz": fuzz_ok}


def check_assertions_preserved() -> int:
    def assertion_count(text: str) -> int:
        return sum(1 for n in ast.walk(ast.parse(text)) if isinstance(n, ast.Assert))

    base = assertion_count(BASELINE.read_text(encoding="utf-8"))
    prod = assertion_count(PRODUCTION.read_text(encoding="utf-8"))
    require(base == prod == 26, f"assertion count drift base={base} prod={prod}")
    # The sole intentional AST change replaces `actual == expected` with rows_equal(...).
    require("rows_equal(" in PRODUCTION.read_text(encoding="utf-8"),
            "production must keep the rows_equal admission helper")
    return prod


def check_temp_corruption_rejection() -> dict:
    """On-disk foil that drops ADD row updates must fail closed or diverge."""
    production = load_module("hpe_transport_production_corr", PRODUCTION)
    words = load_words()
    word = words["p6n"]
    with tempfile.TemporaryDirectory(prefix="hpe-transport-prod-honest-") as tmp:
        tmp_path = Path(tmp)
        raw = tmp_path / "honest.json.gz"
        raw.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
        honest = outcome(production, raw, tmp_path / "honest-out")
        require(honest[0] == "pass", "honest production control must pass")

    text = PRODUCTION.read_text(encoding="utf-8")
    needle = "        for j, x in list(sm.items()):\n            value = tm.get(j, 0) + fs*x\n            if value:\n                tm[j] = value\n            else:\n                tm.pop(j, None)"
    require(needle in text, "ADD update site missing for corruption control")
    foil_text = text.replace(
        needle,
        "        for j, x in list(sm.items()):\n            pass",
        1,
    )
    require(foil_text != text, "mutant must differ on disk")

    with tempfile.TemporaryDirectory(prefix="hpe-transport-prod-foil-") as tmp:
        tmp_path = Path(tmp)
        mutant = tmp_path / "hpe_audit_and_transport.py"
        mutant.write_text(foil_text, encoding="utf-8")
        foil = load_module("hpe_transport_foil", mutant)
        raw = tmp_path / "foil.json.gz"
        raw.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
        try:
            bad = outcome(foil, raw, tmp_path / "foil-out")
        except Exception as exc:
            return {"rejected": True, "mode": "subprocess_failure", "detail": str(exc)[:240]}
        require(bad != honest, "ADD-drop foil must change the transport outcome")
        return {"rejected": True, "mode": "receipt_divergence"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    # -O policy: require() gates remain; imported auditors still execute their asserts
    # because this process keeps them as ordinary assert statements in loaded modules
    # and the package VERIFY launches with python -I -O -B only on this driver.
    check_baseline_bytes()
    assertions = check_assertions_preserved()
    receipts = check_identical_receipts()
    corruption = check_temp_corruption_rejection()
    require(corruption["rejected"], "corruption control must reject")
    print(
        "PASS_HPE_TRANSPORT_INTEGER_PRODUCTION "
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
