#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for shared-point frame contains.

Read-only by default. Regenerates no certificate. Timing is not a pass gate;
see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
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
import shared_point_circuit as production  # noqa: E402

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "32bdbb7e0e7fc4658b7885bc3755d7813a3eba0d"
ORIGINAL_SHA256 = "f5abbf6d61f3c10349416a3e1a1ed038bbd1279ed223367f2df549de46dd7ea5"
OPTIMIZED_SHA256 = "360d9bffc0f55315fe294789b72c71c79e0991524555b3a5f42a2ca504d7da95"


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
    original = git_show("scripts/shared_point_circuit.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base shared_point_circuit.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/shared_point_circuit.py"], cwd=ROOT
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base shared_point_circuit.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "shared_point_circuit.py") == OPTIMIZED_SHA256,
        "production shared_point_circuit.py does not match the claimed optimized digest",
    )


def check_no_duplicate_json_keys() -> dict:
    """Reject accidental duplicate keys in package JSON manifests."""

    def object_pairs(pairs):
        seen = set()
        out = {}
        for key, value in pairs:
            require(key not in seen, f"duplicate JSON key {key!r}")
            seen.add(key)
            out[key] = value
        return out

    scanned = 0
    for path in sorted(PACKAGE.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        json.loads(text, object_pairs_hook=object_pairs)
        scanned += 1
    return {"json_files_scanned": scanned}


def check_verify_and_frames(baseline, optimized) -> dict:
    records = []
    for h in (6, 8, 10, 12, 46):
        circuit = optimized.SharedPointCircuit(h)
        old_verify = baseline.SharedPointCircuit.verify(circuit)
        new_verify = circuit.verify()
        require(old_verify == new_verify, f"verify mismatch on h={h}")
        code = circuit.compile()
        old_frames = baseline.SharedPointCircuit.verify_frames(circuit, code)
        new_frames = circuit.verify_frames(code)
        require(old_frames == new_frames, f"verify_frames mismatch on h={h}")
        # Pointwise support_in identity on a sample of active nodes × commons.
        checked = 0
        for node in list(circuit.active)[:200]:
            bits = circuit.core[node]
            while bits:
                bit = bits & -bits
                bits -= bit
                common = bit.bit_length() - 1
                old = baseline.SharedPointCircuit.support_in(circuit, node, common)
                new = circuit.support_in(node, common)
                require(old == new, f"support_in mismatch h={h} node={node} common={common}")
                checked += 1
        records.append(
            dict(
                h=h,
                roles=new_verify["roles"],
                additions=new_verify["additions"],
                partial_outputs=new_verify["partial_outputs"],
                merged_additions=new_verify["merged_additions"],
                circuit_sha256=new_verify["circuit_sha256"],
                frame_roles=new_frames["roles"],
                support_in_checks=checked,
            )
        )
    require(records[-1]["additions"] == 486330, "unexpected full-size additions")
    require(records[-1]["roles"] == 531870, "unexpected full-size roles")
    require(records[-1]["merged_additions"] == 45706, "unexpected full-size merges")
    require(records[-1]["frame_roles"] == 531870, "unexpected full-size frame roles")
    return {"cases": len(records), "records": records}


def check_nesting_rejection(baseline, optimized) -> dict:
    circuit = optimized.SharedPointCircuit(8)
    code = circuit.compile()
    node = next(n for n in circuit.active if circuit.args[n])
    a, _b = circuit.args[node]
    # Drop one child from the recorded core intersection; both engines must reject.
    circuit.core[node] = circuit.core[a]
    # Invalidate dense cache if the optimized engine already filled it.
    circuit.__dict__.pop("_support_in_cache", None)
    with _expect_assertion():
        optimized.SharedPointCircuit.verify_frames(circuit, code)
    with _expect_assertion():
        baseline.SharedPointCircuit.verify_frames(circuit, code)
    return {"nesting_rejection": "preserved"}


class _expect_assertion:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        require(exc_type is AssertionError, "expected AssertionError from corrupted core")
        return True


def check_certificate_not_pinning_source() -> dict:
    bit = json.loads((ROOT / "certificates/bit-compression-audit.json").read_text())
    pins = bit.get("source_sha256", {})
    require(
        "scripts/shared_point_circuit.py" not in pins,
        "unexpected certificate pin of shared_point_circuit.py",
    )
    return {"bit_compression_certificate_pins_shared_point": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true", help="unused; kept for API parity")
    args = parser.parse_args()
    require(not args.write_certificate, "this package does not rewrite certificates")

    check_baseline_bytes()
    keys = check_no_duplicate_json_keys()
    baseline = load_module(PACKAGE / "baseline.py", "shared_point_frame_contains_baseline")
    cases = check_verify_and_frames(baseline, production)
    if __debug__:
        rejection = check_nesting_rejection(baseline, production)
    else:
        # Historical nesting checks use assert, stripped under -O.
        rejection = {"nesting_rejection": "skipped_under_-O"}
    pins = check_certificate_not_pinning_source()
    print(
        "PASS_SHARED_POINT_FRAME_CONTAINS",
        f"cases={cases['cases']}",
        f"json_files={keys['json_files_scanned']}",
        "certs=0",
        "no_new_kappa",
    )
    print(
        "controls",
        rejection["nesting_rejection"],
        "certificate_pin=" + str(pins["bit_compression_certificate_pins_shared_point"]),
        flush=True,
    )


if __name__ == "__main__":
    main()
