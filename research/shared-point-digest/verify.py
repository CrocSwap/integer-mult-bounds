#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for shared-point verify digests.

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

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "8347a0bda63fbfb51b86c6c6d10a7bf541816308"
ORIGINAL_SHA256 = "c9bb7a5df92d260a4e3ad532b53e26936730d7c93f7facfb0784957c1e81c8ba"
OPTIMIZED_SHA256 = "f5abbf6d61f3c10349416a3e1a1ed038bbd1279ed223367f2df549de46dd7ea5"


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


def check_encoding_foil() -> dict:
    """Hand-rolled lines must match json.dumps text, and mutants must differ."""
    node_samples = [
        (1, None, None),
        (5, (1, 2), (0, 3)),
        (999999, (0, 1), (2, 4)),
        (42, None, None),
        (7, (100, 200), (3, 9)),
    ]
    for node, edge, prov in node_samples:
        old = json.dumps((node, edge, prov), separators=(",", ":")) + "\n"
        if edge is None:
            new = f"[{node},null,null]\n"
        else:
            a, b = edge
            common, local = prov
            new = f"[{node},[{a},{b}],[{common},{local}]]\n"
        require(old == new, f"node encoding mismatch for {(node, edge, prov)}")
    output_samples = [
        (0, (0, 1, 2), 22),
        (5, (1, 3, 5), 100),
        (45, (0, 22, 45), 531870),
    ]
    for common, target, node in output_samples:
        old = json.dumps((common, target, node), separators=(",", ":")) + "\n"
        t0, t1, t2 = target
        new = f"[{common},[{t0},{t1},{t2}],{node}]\n"
        require(old == new, f"output encoding mismatch for {(common, target, node)}")
    # Mutant foils: Python None spelling and a dropped nested bracket.
    bad_none = "[0,None,None]\n"
    good_none = json.dumps((0, None, None), separators=(",", ":")) + "\n"
    require(bad_none != good_none, "mutant None spelling must differ from json null")
    bad_flat = "[5,1,2,0,3]\n"
    good_nested = json.dumps((5, (1, 2), (0, 3)), separators=(",", ":")) + "\n"
    require(bad_flat != good_nested, "mutant flat triple must differ from nested encoding")
    return {
        "node_encoding_cases": len(node_samples),
        "output_encoding_cases": len(output_samples),
        "none_mutant": "rejected",
        "flat_mutant": "rejected",
    }


def check_verify_equivalence(baseline, optimized) -> dict:
    records = []
    for h in (6, 8, 10, 12, 46):
        circuit = optimized.SharedPointCircuit(h)
        old = baseline.SharedPointCircuit.verify(circuit)
        new = circuit.verify()
        require(old == new, f"verify mismatch on h={h}")
        records.append(
            dict(
                h=h,
                roles=new["roles"],
                additions=new["additions"],
                partial_outputs=new["partial_outputs"],
                merged_additions=new["merged_additions"],
                circuit_sha256=new["circuit_sha256"],
            )
        )
    require(records[-1]["additions"] == 486330, "unexpected full-size additions")
    require(records[-1]["roles"] == 531870, "unexpected full-size roles")
    require(records[-1]["merged_additions"] == 45706, "unexpected full-size merges")
    return {"verify_cases": len(records), "records": records}


def check_support_rejection(baseline, optimized) -> dict:
    circuit = optimized.SharedPointCircuit(8)
    node = next(n for n in circuit.active if circuit.args[n])
    a, b = circuit.args[node]
    # Drop one child from the recorded core intersection; both engines must reject.
    circuit.core[node] = circuit.core[a]
    with _expect_assertion():
        optimized.SharedPointCircuit.verify(circuit)
    with _expect_assertion():
        baseline.SharedPointCircuit.verify(circuit)
    return {"support_rejection": "preserved"}


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
    baseline = load_module(PACKAGE / "baseline.py", "shared_point_digest_baseline")
    encoding = check_encoding_foil()
    verifies = check_verify_equivalence(baseline, production)
    if __debug__:
        rejection = check_support_rejection(baseline, production)
    else:
        # Historical SharedPointCircuit.verify uses assert, stripped under -O.
        rejection = {"support_rejection": "skipped_under_-O"}
    pins = check_certificate_not_pinning_source()
    print(
        "PASS_SHARED_POINT_DIGEST",
        f"verify_cases={verifies['verify_cases']}",
        f"encoding_cases={encoding['node_encoding_cases'] + encoding['output_encoding_cases']}",
        "certs=0",
        "no_new_kappa",
    )
    print(
        "controls",
        rejection["support_rejection"],
        "certificate_pin=" + str(pins["bit_compression_certificate_pins_shared_point"]),
        flush=True,
    )


if __name__ == "__main__":
    main()
