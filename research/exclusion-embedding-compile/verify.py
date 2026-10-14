#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for exclusion embedding compile.

Read-only by default. Regenerates no certificate. Timing is not a pass gate;
see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
import exclusion_circuit as production  # noqa: E402

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "b0e2f3e03d7de791ca936dfd92cee2134c7dd4f5"
ORIGINAL_SHA256 = "f9fbcd6e85e442cbd0926ac0887414e20735b2dc923d2d5822c803ceb46726d3"
OPTIMIZED_SHA256 = "f066ce9f88f0d8c0b82d7cb3a8d267249e12386e9d1ab65820a3bed54ff0ff78"
N45_VERIFY_SHA = "3b1a4d7731db2950040552672fbc56ebd172e36e3412129030ff2aec472d5f6c"

PINNED_CERTIFICATES = (
    "certificates/positive-side-core.json",
    "certificates/dyadic-central-factor.json",
    "certificates/ternary-side.json",
    "certificates/disjoint-tensor-compression.json",
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git_show(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{path}"], cwd=ROOT)


def check_duplicate_json_keys(text: str, rel: str) -> None:
    """Reject duplicate keys inside each JSON object (object-pairs hook)."""

    def pairs_hook(pairs):
        keys = [k for k, _ in pairs]
        require(len(keys) == len(set(keys)), f"{rel}: duplicate JSON key(s) {keys}")
        return dict(pairs)

    json.loads(text, object_pairs_hook=pairs_hook)


def check_baseline_bytes() -> None:
    baseline = PACKAGE / "baseline.py"
    original = git_show("scripts/exclusion_circuit.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base exclusion_circuit.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/exclusion_circuit.py"], cwd=ROOT
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base exclusion_circuit.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "exclusion_circuit.py") == OPTIMIZED_SHA256,
        "production exclusion_circuit.py does not match the claimed optimized digest",
    )


def check_compile_and_embedding(baseline, optimized) -> dict:
    records = []
    for n in (4, 6, 8, 12, 16, 24, 32, 45):
        circuit = optimized.ExclusionCircuit(n)
        old_code = baseline.ExclusionCircuit.compile(circuit)
        new_code = circuit.compile()
        require(old_code == new_code, f"compile map mismatch on n={n}")
        old = baseline.ExclusionCircuit.verify_embedding(circuit)
        new = circuit.verify_embedding()
        require(old == new, f"verify_embedding mismatch on n={n}")
        records.append(
            dict(
                n=n,
                roles=new_code["roles"],
                gates=len(new_code["gates"]),
                reversible_roles=new["reversible_roles"],
                forward_coefficient_map_exact=new["forward_coefficient_map_exact"],
                forward_support_frames_nested=new["forward_support_frames_nested"],
                reverse_support_frames_nested=new["reverse_support_frames_nested"],
                no_forbidden_source_target_path=new["no_forbidden_source_target_path"],
            )
        )
    require(records[-1]["reversible_roles"] == 12556, "unexpected n=45 reversible_roles")
    return {"cases": len(records), "records": records}


def check_verify_untouched(baseline, optimized) -> dict:
    """Leave-two-out verify receipts and closed-form masks stay in production."""
    circuit = optimized.ExclusionCircuit(45)
    old = baseline.ExclusionCircuit.verify(circuit)
    new = circuit.verify()
    require(old == new, "verify receipt drifted")
    require(new["circuit_sha256"] == N45_VERIFY_SHA, "unexpected n=45 circuit_sha256")
    text = (SCRIPTS / "exclusion_circuit.py").read_text(encoding="utf-8")
    require(
        "assert self.support[node]==full^(vertex[a]|vertex[b])" in text,
        "verify leave-two-out must retain the #2001 closed-form pair mask",
    )
    require(
        "assert reverse_frames[slot]==full^(vertex[a]|vertex[b])" in text,
        "verify_embedding must retain the closed-form reverse mask",
    )
    require("edge0" in text and "edge1" in text, "compile must use parallel edge0/edge1 maps")
    require(
        "for slot in set(ins+outs)" not in text,
        "historical set(ins+outs) nesting loops must be removed from production",
    )
    return {"verify_companion": True, "n45_circuit_sha256": N45_VERIFY_SHA}


def check_compile_mutant(baseline, optimized) -> dict:
    """Corrupt one compiled gate mapping; both checkers must reject nesting."""
    circuit = optimized.ExclusionCircuit(8)
    real_compile = optimized.ExclusionCircuit.compile

    def compile_flip(self):
        code = real_compile(self)
        pairs = list(code["outputs"].items())
        require(len(pairs) >= 2, "need two outputs to flip")
        (p0, s0), (p1, s1) = pairs[0], pairs[1]
        code = dict(code)
        outs = dict(code["outputs"])
        outs[p0], outs[p1] = s1, s0
        code["outputs"] = outs
        return code

    optimized.ExclusionCircuit.compile = compile_flip
    try:
        with _expect_assertion():
            optimized.ExclusionCircuit.verify_embedding(circuit)
        with _expect_assertion():
            baseline.ExclusionCircuit.verify_embedding(circuit)
    finally:
        optimized.ExclusionCircuit.compile = real_compile
    return {"compile_mutant": "rejected"}


class _expect_assertion:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        require(exc_type is AssertionError, "expected AssertionError from corrupted compile map")
        return True


def check_certificate_pin_discipline() -> dict:
    """Certificates may update exclusion_circuit.py and companion disjoint_tensor.py pins."""
    companion_key = "scripts/experiments/disjoint_tensor.py"
    companion_orig = "102dd59bf96033f96ba0dab4c2aba77b3a7a73b67b0f96929ff8b20a98b91cd8"
    companion_opt = "085600fc922ae167b5981505e1a5caba4d1c1df15482f61d83d2c086fa89eac1"
    # Open #2117 may advance the disjoint_tensor pin further; accept either live hash.
    companion_open_2117 = "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac"
    reports = {}
    for rel in PINNED_CERTIFICATES:
        raw = (ROOT / rel).read_text(encoding="utf-8")
        check_duplicate_json_keys(raw, rel)
        base = json.loads(git_show(rel).decode())
        live = json.loads(raw)
        base_pin = base["source_sha256"]["scripts/exclusion_circuit.py"]
        live_pin = live["source_sha256"]["scripts/exclusion_circuit.py"]
        require(base_pin == ORIGINAL_SHA256, f"{rel}: unexpected base pin")
        require(live_pin == OPTIMIZED_SHA256, f"{rel}: optimized pin missing")
        restored = deepcopy(live)
        restored["source_sha256"]["scripts/exclusion_circuit.py"] = ORIGINAL_SHA256
        if companion_key in live["source_sha256"]:
            require(
                live["source_sha256"][companion_key]
                in {companion_orig, companion_opt, companion_open_2117},
                f"{rel}: unexpected companion disjoint_tensor pin",
            )
            restored["source_sha256"][companion_key] = companion_orig
            # Base tip may already carry the post-#2001 companion opt pin.
            base_companion = base["source_sha256"].get(companion_key)
            if base_companion in {companion_opt, companion_open_2117}:
                restored["source_sha256"][companion_key] = base_companion
        require(restored == base, f"{rel}: changed fields beyond allowed source pins")
        reports[rel] = {
            "base_pin": base_pin,
            "live_pin": live_pin,
            "only_pin_changed": True,
        }
    return reports


def check_temp_corruption_rejection() -> dict:
    """On-disk corruption of a temp production copy must fail the digest gate."""
    import tempfile

    src = (SCRIPTS / "exclusion_circuit.py").read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "exclusion_circuit.py"
        path.write_bytes(src + b"\n# corrupted\n")
        require(digest_file(path) != OPTIMIZED_SHA256, "corruption must change digest")
    return {"temp_corruption": "rejected"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true", help="unused; kept for API parity")
    args = parser.parse_args()
    require(not args.write_certificate, "this package does not rewrite certificate payloads")

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "exclusion_embedding_compile_baseline")
    cases = check_compile_and_embedding(baseline, production)
    verify_guard = check_verify_untouched(baseline, production)
    if __debug__:
        mutant = check_compile_mutant(baseline, production)
    else:
        mutant = {"compile_mutant": "skipped_under_-O"}
    pins = check_certificate_pin_discipline()
    corruption = check_temp_corruption_rejection()
    print(
        "PASS_EXCLUSION_EMBEDDING_COMPILE",
        f"cases={cases['cases']}",
        f"certs={len(pins)}",
        "no_new_kappa",
    )
    print(
        "controls",
        mutant["compile_mutant"],
        f"verify_companion={verify_guard['verify_companion']}",
        corruption["temp_corruption"],
    )


if __name__ == "__main__":
    main()
