#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for the faster inplace-side prefix check.

Read-only by default. Regenerates no certificate unless --write-certificate is
passed. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from prepare_layers import serializable  # noqa: E402
from audit_inplace_side import certificate as production_certificate  # noqa: E402
from experiments import inplace_side as production  # noqa: E402


BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "db3de6f1d962ccc3a4eae31f83c72bba995ba44e"
ORIGINAL_SHA256 = "4e7cb3df2e263f6c7f5907c55e3ee04c08926e6dbc984bbda1722a27b0a48ff6"
BASE_CERTIFICATE_SHA256 = "1a2020c346e7d039e924a8c782dc6b3f0e94039eb1bec2b2644fc3de9d41ccdb"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    # baseline.py imports certify; scripts/ is already on sys.path
    spec.loader.exec_module(module)
    return module


def load_witnesses():
    return json.loads((SCRIPTS / "experiments/inplace_side_witnesses.json").read_text(encoding="utf-8"))


def load_base_certificate_bytes() -> bytes:
    import subprocess
    return subprocess.check_output(["git", "show", f"{BASE_COMMIT}:certificates/inplace-side.json"], cwd=ROOT)


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def compare_receipts(label: str, left: dict, right: dict) -> None:
    require(left == right, f"{label}: receipts differ: {left!r} vs {right!r}")


def check_baseline_bytes() -> None:
    baseline = PACKAGE / "baseline.py"
    # Strip the package docstring/header added above the frozen body: compare the
    # production historical blob to the functions by re-reading git.
    import subprocess
    original = subprocess.check_output(["git", "show", f"{BASE_COMMIT}:scripts/experiments/inplace_side.py"], cwd=ROOT)
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base inplace_side.py sha256 drift")
    require(
        subprocess.check_output(["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/inplace_side.py"], cwd=ROOT)
        .decode()
        .strip()
        == ORIGINAL_BLOB,
        "base inplace_side.py blob drift",
    )
    # baseline.py must match the original byte-for-byte after its own module docstring
    # is the frozen original file itself.
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")


def check_witness_equivalence(baseline, optimized) -> list[dict]:
    witnesses = load_witnesses()
    require([w["h"] for w in witnesses] == [42, 46, 50], "pinned witness set changed")
    rows = []
    for witness in witnesses:
        args = (witness["h"], witness["pivots"], witness["swaps"])
        old = baseline.verify_prefix(*args)
        new = optimized.verify_prefix(*args)
        compare_receipts(f"h={witness['h']}", old, new)
        require(old["no_positive_deficit"] is True, f"h={witness['h']} deficit gate failed")
        rows.append(old)
    return rows


def check_small_controls(baseline, optimized) -> None:
    for h in (6, 10):
        code = optimized.compile_side(h)
        require(code == baseline.compile_side(h), f"compile_side({h}) drifted")
        old = baseline.verify_prefix(h, code["pivots"], [])
        new = optimized.verify_prefix(h, code["pivots"], [])
        compare_receipts(f"small h={h}", old, new)


def check_rejections(baseline, optimized) -> None:
    code = optimized.compile_side(6)
    pivots = code["pivots"]

    def expect_value_error(eng, name, args, needle):
        try:
            eng.verify_prefix(*args)
            raise AssertionError(f"{name} accepted invalid input ({needle})")
        except ValueError as exc:
            require(needle.lower() in str(exc).lower(), f"{name} wrong rejection: {exc}")

    for eng, name in ((baseline, "baseline"), (optimized, "optimized")):
        expect_value_error(eng, name, (6, pivots, [(0, 1), (0, 2)]), "reuse")
        wrong = list(pivots)
        wrong[0], wrong[1] = wrong[1], wrong[0]
        expect_value_error(eng, name, (6, wrong, []), "prefix")
        expect_value_error(eng, name, (6, pivots, [(0, len(pivots) + 1)]), "switch")


def greatest_unused_mutant_verify_prefix(h, pivots, swaps):
    """Deliberate mutant: picks the greatest unused row instead of the least."""
    from experiments.inplace_side import triple_side
    triples, points, rows = triple_side(h)
    n = len(rows)
    require(h % 4 == 2 and 0 < len(pivots) <= n, "Need an invertible side and nonempty prefix")
    require(all(type(p) is int and 0 <= p < n for p in pivots) and len(set(pivots)) == len(pivots),
            "Pivot roles must be distinct")
    masks = [sum(1 << x for x in T) for T in triples]
    partners = {}
    at_step = {}
    for j, c in swaps:
        require(type(j) is int and type(c) is int and 0 <= j < c < len(pivots), "Invalid switch indices")
        require(j not in partners and c not in partners, "Switch paths reuse a physical role")
        partners[j] = c
        partners[c] = j
        at_step[c] = j
    unused = [True] * n
    for col, p in enumerate(pivots):
        mask = 1 << col
        expected = None
        for i in range(n - 1, -1, -1):  # MUTATION: greatest instead of least
            if unused[i] and rows[i] & mask:
                expected = i
                break
        require(expected is not None and p == expected, "Not the specified lexicographic elimination prefix")
        unused[p] = False
        if col in at_step:
            j = at_step[col]
            require(rows[pivots[j]] & mask, "Claimed switch gate is absent")
        if col + 1 < len(pivots):
            row = rows[p]
            for i in range(n):
                if i != p and rows[i] & mask:
                    rows[i] ^= row
    bad = []
    for j, p in enumerate(pivots):
        target = pivots[partners[j]] if j in partners else p
        if (masks[j] & masks[target]).bit_count() != 1:
            bad.append((j, target))
    k = len(bad)
    deficit_upper = n * n * (n - 6 * h * h - 6 * k)
    return dict(h=h, n=n, prefix_columns=len(pivots), disjoint_switches=len(swaps),
                certified_nonorthogonal_paths=k, bad_endpoints=bad,
                excess_per_invocation_lower=2 * k, deficit_upper=deficit_upper,
                no_positive_deficit=deficit_upper <= 0,
                all_internal_rational_frames_allowed=True,
                scope="Fixed data-copy/injection boundaries, central frames, lexicographic elimination and exactly n side roles")


def check_mutant_rejected(baseline) -> None:
    witnesses = load_witnesses()
    # On the target witnesses the least and greatest unused rows differ, so the
    # mutant must raise on the lexicographic prefix gate.
    raised = 0
    for witness in witnesses:
        try:
            greatest_unused_mutant_verify_prefix(witness["h"], witness["pivots"], witness["swaps"])
        except Exception as exc:
            require("lexicographic" in str(exc).lower() or "prefix" in str(exc).lower(), str(exc))
            raised += 1
            continue
        # If it somehow returned, the receipt must not match the baseline.
        raise AssertionError(f"mutant accepted witness h={witness['h']}")
    require(raised == len(witnesses), "mutant failed to reject every witness")
    # Positive small control still works on the true engines.
    code = baseline.compile_side(6)
    baseline.verify_prefix(6, code["pivots"], [])


def check_certificate(write: bool) -> dict:
    result = production_certificate()
    path = ROOT / "certificates/inplace-side.json"
    text = json.dumps(serializable(result), indent=2, sort_keys=True) + "\n"
    if write:
        path.write_text(text, encoding="utf-8")
    committed = path.read_text(encoding="utf-8")
    require(committed == text, "working certificates/inplace-side.json does not match regenerated certificate()")
    base = load_base_certificate_bytes()
    require(sha256(base).hexdigest() == BASE_CERTIFICATE_SHA256, "base certificate sha256 drift")
    old = json.loads(base.decode("utf-8"))
    new = json.loads(committed)
    # Only the production source pin for inplace_side.py may change.
    old_pin = old["source_sha256"].pop("scripts/experiments/inplace_side.py")
    new_pin = new["source_sha256"].pop("scripts/experiments/inplace_side.py")
    require(old_pin == ORIGINAL_SHA256, "unexpected base pin")
    require(new_pin == digest_file(SCRIPTS / "experiments/inplace_side.py"), "certificate pin != working source")
    require(old == new, "certificate changed outside the single inplace_side.py source pin")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true",
                        help="regenerate certificates/inplace-side.json (default: read-only compare)")
    args = parser.parse_args(argv)

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "inplace_side_baseline")
    optimized = production
    require(digest_file(SCRIPTS / "experiments/inplace_side.py") != ORIGINAL_SHA256,
            "production source still equals the unoptimized base pin")
    require(digest_file(PACKAGE / "baseline.py") == ORIGINAL_SHA256,
            "baseline.py must equal the original source sha256")

    receipts = check_witness_equivalence(baseline, optimized)
    check_small_controls(baseline, optimized)
    check_rejections(baseline, optimized)
    check_mutant_rejected(baseline)
    cert = check_certificate(write=args.write_certificate)

    print(
        "PASS_INPLACE_SIDE_PREFIX_FAST "
        f"witnesses={len(receipts)} "
        f"h={[r['h'] for r in receipts]} "
        f"paths={[r['certified_nonorthogonal_paths'] for r in receipts]} "
        f"optimize={sys.flags.optimize} "
        f"certificate_source_pin={cert['source_sha256']['scripts/experiments/inplace_side.py'][:12]} "
        "no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
