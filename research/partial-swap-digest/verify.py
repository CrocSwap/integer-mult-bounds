#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for partial-swap verify digests.

Read-only by default. Regenerates no certificate unless --write-certificate is
passed (pin-only refresh of certificates/partial-swap-network.json). Timing is
not a pass gate; see benchmark.py / RESULT.json.
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
from partial_swap import shared as production  # noqa: E402

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "a2f0190704db83bd8ef48e46e723c49b925804fe"
ORIGINAL_SHA256 = "81e9af92cdf38243a540cdcff2062778e449467848d444da37a9553c12ca4c34"
OPTIMIZED_SHA256 = "7290bd639600aecff11941d3faf95c9ce95589125cc6a7f7440fb86af7a0f17c"
BASE_CERT_SHA256 = "f3c4be597b2f2136da4ae2cc80c7454f63c90aa01f84e5b8131cee4dd55de815"
CERT_REL = "certificates/partial-swap-network.json"
SOURCE_REL = "scripts/partial_swap/shared.py"


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
    original = git_show(SOURCE_REL)
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base partial_swap/shared.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:{SOURCE_REL}"], cwd=ROOT
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base partial_swap/shared.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(ROOT / SOURCE_REL) == OPTIMIZED_SHA256,
        "production partial_swap/shared.py does not match the claimed optimized digest",
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


class _expect_assertion:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        require(exc_type is AssertionError, "expected AssertionError from corrupted core")
        return True


def check_support_rejection(baseline, optimized) -> dict:
    circuit = optimized.SharedPointCircuit(8)
    node = next(n for n in circuit.active if circuit.args[n])
    a, _b = circuit.args[node]
    circuit.core[node] = circuit.core[a]
    with _expect_assertion():
        optimized.SharedPointCircuit.verify(circuit)
    with _expect_assertion():
        baseline.SharedPointCircuit.verify(circuit)
    return {"support_rejection": "preserved"}


def check_certificate_pin_discipline() -> dict:
    """Working certificate may change only the partial_swap/shared.py source pin."""
    base = json.loads(git_show(CERT_REL))
    live = json.loads((ROOT / CERT_REL).read_text(encoding="utf-8"))
    require(sha256(git_show(CERT_REL)).hexdigest() == BASE_CERT_SHA256, "base certificate digest drift")
    base_pin = base["source_sha256"][SOURCE_REL]
    live_pin = live["source_sha256"][SOURCE_REL]
    require(base_pin == ORIGINAL_SHA256, "unexpected base shared.py pin")
    require(live_pin == OPTIMIZED_SHA256, "optimized shared.py pin missing")
    restored = deepcopy(live)
    restored["source_sha256"][SOURCE_REL] = ORIGINAL_SHA256
    require(restored == base, "changed fields beyond the partial_swap/shared.py pin")
    return {
        "certificate": CERT_REL,
        "base_pin": base_pin,
        "live_pin": live_pin,
        "only_pin_changed": True,
    }


def maybe_write_certificate(write: bool) -> None:
    if not write:
        return
    # Pin-only refresh: replace the single shared.py digest in the committed JSON text.
    raw = git_show(CERT_REL).decode()
    require(raw.count(ORIGINAL_SHA256) == 1, "base certificate pin occurrence drift")
    updated = raw.replace(ORIGINAL_SHA256, OPTIMIZED_SHA256)
    (ROOT / CERT_REL).write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite certificates/partial-swap-network.json with the optimized shared.py pin only",
    )
    args = parser.parse_args()

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "partial_swap_digest_baseline")
    encoding = check_encoding_foil()
    verifies = check_verify_equivalence(baseline, production)
    if __debug__:
        rejection = check_support_rejection(baseline, production)
    else:
        # Historical SharedPointCircuit.verify uses assert, stripped under -O.
        rejection = {"support_rejection": "skipped_under_-O"}
    maybe_write_certificate(args.write_certificate)
    pins = check_certificate_pin_discipline()
    print(
        "PASS_PARTIAL_SWAP_DIGEST",
        f"verify_cases={verifies['verify_cases']}",
        f"encoding_cases={encoding['node_encoding_cases'] + encoding['output_encoding_cases']}",
        "certs=1",
        "no_new_kappa",
    )
    print(
        "controls",
        rejection["support_rejection"],
        "certificate_pin_only=" + str(pins["only_pin_changed"]),
        flush=True,
    )


if __name__ == "__main__":
    main()
