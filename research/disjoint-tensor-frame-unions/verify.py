#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for DisjointTensor.frame_data.

Read-only by default. Regenerates no certificate. Timing is not a pass gate;
see benchmark.py / RESULT.json.

Promotes the exact target-union propagation proved as an opt-in adapter in
research/disjoint-frame-unions/ (#1044) into the default production path, with
identical verify_frames receipts.
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
from experiments import disjoint_tensor as production  # noqa: E402

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "b842d0a8d4f0f782a1f0bef171f5f2cd96878e58"
ORIGINAL_SHA256 = "085600fc922ae167b5981505e1a5caba4d1c1df15482f61d83d2c086fa89eac1"
OPTIMIZED_SHA256 = "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac"

PINNED_CERTIFICATES = (
    "certificates/disjoint-tensor-compression.json",
    "certificates/ternary-side.json",
    "certificates/dyadic-central-factor.json",
    "certificates/parity-side.json",
)

H26_FRAME_TYPES = {"line": 27430, "coordinate": 65884, "complement": 27430}
H26_TRANSITIONS = 195345


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
    original = git_show("scripts/experiments/disjoint_tensor.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base disjoint_tensor.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/disjoint_tensor.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base disjoint_tensor.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "experiments" / "disjoint_tensor.py") == OPTIMIZED_SHA256,
        "production disjoint_tensor.py does not match the claimed optimized digest",
    )


def xor_mutant_target_unions(self):
    """Deliberate mutant: XOR target unions instead of OR while propagating.

    Skips rectangle require so the foil can be compared even when XOR creates
    empty or overlapping masks that the real checker would reject.
    """
    descendants = {node: 0 for node in self.active}
    target_union = {node: 0 for node in sorted(self.active)}
    for i, T in enumerate(sorted(self.outputs)):
        node = self.outputs[T]
        descendants[node] |= 1 << i
        target_union[node] ^= T  # MUTATION
    for node in sorted(self.active, reverse=True):
        if self.args[node]:
            for parent in self.args[node]:
                descendants[parent] |= descendants[node]
                target_union[parent] ^= target_union[node]  # MUTATION
    return descendants, target_union


def check_frame_equivalence(baseline, optimized) -> dict:
    map_cases = 0
    frame_cases = 0
    records = []
    for h in (8, 10, 12, 16, 20, 26):
        circuit = optimized.DisjointTensor(h)
        old_maps = baseline.DisjointTensor.frame_data(circuit)
        new_maps = circuit.frame_data()
        require(old_maps == new_maps, f"frame_data maps mismatch on h={h}")
        map_cases += 1
        old = baseline.DisjointTensor.verify_frames(circuit)
        new = circuit.verify_frames()
        require(old == new, f"verify_frames mismatch on h={h}")
        frame_cases += 1
        records.append(
            dict(
                h=h,
                distinct_nontrivial_transitions=new["distinct_nontrivial_transitions"],
                frame_types=new["frame_types"],
                exact_residual_bases_constructed=new["exact_residual_bases_constructed"],
            )
        )
    require(records[-1]["distinct_nontrivial_transitions"] == H26_TRANSITIONS, "unexpected h=26 transitions")
    require(records[-1]["frame_types"] == H26_FRAME_TYPES, "unexpected h=26 frame_types")
    return {"map_cases": map_cases, "frame_cases": frame_cases, "records": records}


def check_xor_mutant_rejected(optimized) -> dict:
    circuit = optimized.DisjointTensor(12)
    descendants, _sources, targets = circuit.frame_data()
    mutant_descendants, mutant_targets = xor_mutant_target_unions(circuit)
    require(mutant_descendants == descendants, "xor-mutant must preserve descendant bitsets")
    require(mutant_targets != targets, "xor-mutant target_union must differ on h=12")
    return {"xor_mutant": "rejected", "h": 12}


def check_rectangle_rejection(baseline, optimized) -> dict:
    circuit = optimized.DisjointTensor(10)
    # Widen a leaf source mask so source_union meets its nonempty target_union.
    leaf = min(n for n in circuit.active if circuit.args[n] is None)
    circuit.inputs[leaf - 1] = (1 << circuit.h) - 1
    with _expect_value_error():
        optimized.DisjointTensor.frame_data(circuit)
    with _expect_value_error():
        baseline.DisjointTensor.frame_data(circuit)
    return {"rectangle_rejection": "preserved", "corrupted_h": 10}


class _expect_value_error:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        require(exc_type is ValueError, "expected ValueError from corrupted rectangle")
        return True


def check_certificate_pin_discipline() -> dict:
    """Allow the explicitly checked PR2100 companion update; preserve all other fields."""
    reports = {}
    for rel in PINNED_CERTIFICATES:
        base = json.loads(git_show(rel).decode())
        live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        key = "scripts/experiments/disjoint_tensor.py"
        base_pin = base["source_sha256"][key]
        live_pin = live["source_sha256"][key]
        require(base_pin == ORIGINAL_SHA256, f"{rel}: unexpected base pin")
        require(live_pin == OPTIMIZED_SHA256, f"{rel}: optimized pin missing")
        restored = deepcopy(live)
        restored["source_sha256"][key] = ORIGINAL_SHA256
        companion = "scripts/experiments/ternary_side.py"
        if restored["source_sha256"].get(companion) != base["source_sha256"].get(companion):
            expected = "eba4acc6f44c5d56aa8d225266a4a951fc1f1cb84819cdc104e1847578403878"
            require(rel == "certificates/ternary-side.json" and
                    restored["source_sha256"].get(companion) == expected,
                    f"{rel}: unreviewed ternary companion pin")
            require(sha256((ROOT / companion).read_bytes()).hexdigest() == expected,
                    "ternary companion source drift")
            restored["source_sha256"][companion] = base["source_sha256"][companion]
        require(restored == base, f"{rel}: changed fields beyond reviewed source pins")
        reports[rel] = {
            "base_pin": base_pin,
            "live_pin": live_pin,
            "only_pin_changed": True,
        }
    return reports


def check_no_duplicate_json_keys() -> dict:
    """Reject duplicate JSON object keys in live certificates (stdlib load keeps last)."""
    import re

    key_re = re.compile(r'"([^\\"]*(?:\\.[^\\"]*)*)"\s*:')
    checked = 0
    for rel in PINNED_CERTIFICATES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        # Track keys per object nesting depth via a small scanner.
        stack: list[set[str]] = []
        i = 0
        in_string = False
        escape = False
        while i < len(text):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                i += 1
                continue
            if ch == '"':
                m = key_re.match(text, i)
                if m and stack:
                    key = json.loads(f'"{m.group(1)}"')
                    require(key not in stack[-1], f"{rel}: duplicate JSON key {key!r}")
                    stack[-1].add(key)
                    i = m.end()
                    continue
                in_string = True
                i += 1
                continue
            if ch == "{":
                stack.append(set())
            elif ch == "}":
                require(stack, f"{rel}: unbalanced }}")
                stack.pop()
            i += 1
        require(not stack, f"{rel}: unbalanced {{")
        checked += 1
    return {"duplicate_key_files_checked": checked}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true", help="unused; kept for API parity")
    args = parser.parse_args()
    require(not args.write_certificate, "this package does not rewrite certificate payloads")

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "disjoint_tensor_frame_unions_baseline")
    frames = check_frame_equivalence(baseline, production)
    mutant = check_xor_mutant_rejected(production)
    rejection = check_rectangle_rejection(baseline, production)
    pins = check_certificate_pin_discipline()
    keys = check_no_duplicate_json_keys()
    print(
        "PASS_DISJOINT_TENSOR_FRAME_UNIONS",
        f"frame_cases={frames['frame_cases']}",
        f"map_cases={frames['map_cases']}",
        f"certs={len(pins)}",
        "no_new_kappa",
    )
    print(
        "controls",
        mutant["xor_mutant"],
        rejection["rectangle_rejection"],
        f"dup_key_files={keys['duplicate_key_files_checked']}",
        f"h26_transitions={H26_TRANSITIONS}",
        flush=True,
    )


if __name__ == "__main__":
    main()
