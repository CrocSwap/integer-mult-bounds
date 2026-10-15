#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for exclusion embedding reverse masks.

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

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "aaa99986c4b81c5d4fbe016fd216a4818940bb95"
ORIGINAL_SHA256 = "b253f9d7318becda1c1f3b24e2287ed44a9c27fcea00cf9d531afb950d0457a0"
OPTIMIZED_SHA256 = "f9fbcd6e85e442cbd0926ac0887414e20735b2dc923d2d5822c803ceb46726d3"
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


def historical_expected(target_index, source) -> int:
    return sum(
        1 << i
        for target, i in target_index.items()
        if not set(source) & set(target)
    )


def closed_form_expected(full: int, vertex: list[int], a: int, b: int) -> int:
    return full ^ (vertex[a] | vertex[b])


def reverse_masks(circuit) -> tuple[int, list[int], dict]:
    target_index = {pair: i for i, pair in enumerate(sorted(circuit.outputs))}
    full = (1 << len(target_index)) - 1
    vertex = [0] * circuit.n
    for target, i in target_index.items():
        bit = 1 << i
        vertex[target[0]] |= bit
        vertex[target[1]] |= bit
    return full, vertex, target_index


def check_mask_equivalence() -> dict:
    """Closed-form reverse-frame masks must match the historical genexpr."""
    cases = 0
    for n in (4, 6, 8, 12, 16, 24, 32, 45):
        circuit = production.ExclusionCircuit(n)
        code = circuit.compile()
        full, vertex, target_index = reverse_masks(circuit)
        for source, _slot in code["sources"].items():
            old = historical_expected(target_index, source)
            new = closed_form_expected(full, vertex, source[0], source[1])
            require(old == new, f"mask mismatch n={n} source={source}")
            cases += 1
        # Mutant foil: XOR without the double-count fix keeps the (a,b) bit.
        source = next(iter(code["sources"]))
        a, b = source
        mutant = full ^ vertex[a] ^ vertex[b]
        correct = closed_form_expected(full, vertex, a, b)
        require(mutant != correct, f"xor-mutant must differ on n={n}")
    return {"mask_cases": cases, "xor_mutant": "rejected"}


def check_embedding_equivalence(baseline, optimized) -> dict:
    records = []
    for n in (4, 6, 8, 12, 16, 24, 32, 45):
        circuit = optimized.ExclusionCircuit(n)
        old = baseline.ExclusionCircuit.verify_embedding(circuit)
        new = circuit.verify_embedding()
        require(old == new, f"verify_embedding mismatch on n={n}")
        records.append(
            dict(
                n=n,
                reversible_roles=new["reversible_roles"],
                forward_coefficient_map_exact=new["forward_coefficient_map_exact"],
                forward_support_frames_nested=new["forward_support_frames_nested"],
                reverse_support_frames_nested=new["reverse_support_frames_nested"],
                no_forbidden_source_target_path=new["no_forbidden_source_target_path"],
            )
        )
    require(records[-1]["reversible_roles"] == 12556, "unexpected n=45 reversible_roles")
    return {"embedding_cases": len(records), "records": records}


def check_verify_untouched(baseline, optimized) -> dict:
    """Leave-two-out verify receipts stay identical; both closed forms co-land."""
    circuit = optimized.ExclusionCircuit(45)
    old = baseline.ExclusionCircuit.verify(circuit)
    new = circuit.verify()
    require(old == new, "verify receipt drifted")
    require(new["circuit_sha256"] == N45_VERIFY_SHA, "unexpected n=45 circuit_sha256")
    # Folded production with #2001: both leave-two-out and reverse-frame closed
    # forms live in scripts/exclusion_circuit.py with one source pin.
    text = (SCRIPTS / "exclusion_circuit.py").read_text(encoding="utf-8")
    require(
        "assert self.support[node]==full^(vertex[a]|vertex[b])" in text,
        "verify leave-two-out must use the #2001 closed-form pair mask",
    )
    require(
        "assert reverse_frames[slot]==full^(vertex[a]|vertex[b])" in text,
        "verify_embedding must use the closed-form reverse mask",
    )
    require(
        "sum(1<<i for i,p in enumerate(self.inputs) if a not in p and b not in p)" not in text,
        "historical leave-two-out genexpr must be removed from production",
    )
    require(
        "expected=sum(1<<i for target,i in target_index.items()" not in text,
        "historical reverse-frame assignment must be removed from production",
    )
    return {"verify_companion": True, "n45_circuit_sha256": N45_VERIFY_SHA}


def check_reverse_rejection(baseline, optimized) -> dict:
    circuit = optimized.ExclusionCircuit(8)
    code = circuit.compile()
    source, slot = next(iter(code["sources"].items()))
    # Corrupt one reverse-frame bit after a normal run's expected value by
    # monkey-patching compile to flip the source slot after construction.
    # Simpler: flip a descendant bit used by reverse frames by corrupting an
    # output support index used only inside verify_embedding's reverse phase.
    # Direct approach: wrap verify_embedding body via corrupted outputs map.
    original_outputs = dict(circuit.outputs)
    # Flip one output node id mapping so reverse expected bits disagree.
    target = next(iter(circuit.outputs))
    circuit.outputs[target] = circuit.outputs[target]  # keep structure
    # Corrupt reverse_frames by mutating support of an output node after compile
    # path: change target_index ordering indirectly by renaming is hard.
    # Instead corrupt the compiled source slot's reverse expectation by
    # temporarily replacing compile to yield a flipped output bit assignment.
    real_compile = optimized.ExclusionCircuit.compile

    def compile_flip(self):
        code = real_compile(self)
        # Flip which output bit is written into one reverse_frames seed.
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
        circuit.outputs = original_outputs
    return {"reverse_rejection": "preserved", "corrupted_source": list(source), "slot": slot}


class _expect_assertion:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        require(exc_type is AssertionError, "expected AssertionError from corrupted reverse frame")
        return True


def check_certificate_pin_discipline() -> dict:
    """Certificates may update exclusion_circuit.py and companion disjoint_tensor.py pins."""
    companion_key = "scripts/experiments/disjoint_tensor.py"
    companion_orig = "102dd59bf96033f96ba0dab4c2aba77b3a7a73b67b0f96929ff8b20a98b91cd8"
    companion_opt = "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac"
    reports = {}
    for rel in PINNED_CERTIFICATES:
        base = json.loads(git_show(rel).decode())
        live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        base_pin = base["source_sha256"]["scripts/exclusion_circuit.py"]
        live_pin = live["source_sha256"]["scripts/exclusion_circuit.py"]
        require(base_pin == ORIGINAL_SHA256, f"{rel}: unexpected base pin")
        require(live_pin == OPTIMIZED_SHA256, f"{rel}: optimized pin missing")
        restored = deepcopy(live)
        restored["source_sha256"]["scripts/exclusion_circuit.py"] = ORIGINAL_SHA256
        if companion_key in live["source_sha256"]:
            require(
                live["source_sha256"][companion_key] in {companion_orig, companion_opt},
                f"{rel}: unexpected companion disjoint_tensor pin",
            )
            restored["source_sha256"][companion_key] = companion_orig
        require(restored == base, f"{rel}: changed fields beyond allowed source pins")
        reports[rel] = {
            "base_pin": base_pin,
            "live_pin": live_pin,
            "only_pin_changed": True,
        }
    return reports


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true", help="unused; kept for API parity")
    args = parser.parse_args()
    require(not args.write_certificate, "this package does not rewrite certificate payloads")

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "exclusion_embedding_masks_baseline")
    masks = check_mask_equivalence()
    embeddings = check_embedding_equivalence(baseline, production)
    verify_guard = check_verify_untouched(baseline, production)
    if __debug__:
        rejection = check_reverse_rejection(baseline, production)
    else:
        # Historical ExclusionCircuit.verify_embedding uses assert, stripped under -O.
        rejection = {"reverse_rejection": "skipped_under_-O"}
    pins = check_certificate_pin_discipline()
    print(
        "PASS_EXCLUSION_EMBEDDING_MASKS",
        f"embedding_cases={embeddings['embedding_cases']}",
        f"mask_cases={masks['mask_cases']}",
        f"certs={len(pins)}",
        "no_new_kappa",
    )
    print(
        "controls",
        rejection["reverse_rejection"],
        f"verify_companion={verify_guard['verify_companion']}",
        f"n45_roles={embeddings['records'][-1]['reversible_roles']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
