#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for partial-swap merge construction.

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

# Stacked on open CrocSwap/integer-mult-bounds#2039 tip (digest rewrite already applied).
BASE_COMMIT = "3b29a00f972bd15871baac0acf5ac204740a9863"
ORIGINAL_BLOB = "77a3672dce3b377eee30a6c3e993a63c2d3840d5"
ORIGINAL_SHA256 = "b27c8bfe1de3f7d2d5fb19ac742adf11597c2aaa7add68430443119997e646e8"
OPTIMIZED_SHA256 = "7290bd639600aecff11941d3faf95c9ce95589125cc6a7f7440fb86af7a0f17c"
BASE_CERT_SHA256 = "6e6ebabf06ee125e58f6871748aaa1fddc4cbf5e70338c61742bca85b9b3e7d4"
FULL_SIZE_SHA256 = "b0402f9eaaf138129939521c2a2ef1c3e8230b730de0a7bdea3596eb415dd173"
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


def circuit_structure(circuit) -> dict:
    return dict(
        args=circuit.args,
        core=circuit.core,
        union=circuit.union,
        provenance=circuit.provenance,
        outputs=dict(sorted(circuit.outputs.items())),
        active=sorted(circuit.active),
        additions=circuit.additions,
        merged=circuit.merged,
        pair_ids=circuit.pair_ids,
        variables=circuit.variables,
        points=circuit.points,
    )


def check_construction_equivalence(baseline, optimized) -> dict:
    records = []
    for h in (6, 8, 10, 12, 46):
        old = baseline.SharedPointCircuit(h)
        new = optimized.SharedPointCircuit(h)
        require(circuit_structure(old) == circuit_structure(new), f"structure mismatch on h={h}")
        old_receipt = old.verify()
        new_receipt = new.verify()
        require(old_receipt == new_receipt, f"verify mismatch on h={h}")
        require(
            baseline.SharedPointCircuit.verify(new) == new_receipt,
            f"cross-engine verify mismatch on h={h}",
        )
        records.append(
            dict(
                h=h,
                roles=new_receipt["roles"],
                additions=new_receipt["additions"],
                partial_outputs=new_receipt["partial_outputs"],
                merged_additions=new_receipt["merged_additions"],
                circuit_sha256=new_receipt["circuit_sha256"],
            )
        )
    require(records[-1]["additions"] == 486330, "unexpected full-size additions")
    require(records[-1]["roles"] == 531870, "unexpected full-size roles")
    require(records[-1]["merged_additions"] == 45706, "unexpected full-size merges")
    require(
        records[-1]["circuit_sha256"] == FULL_SIZE_SHA256,
        "unexpected full-size circuit_sha256",
    )
    return {"verify_cases": len(records), "records": records}


def check_reorder_mutant_rejected(baseline, optimized) -> dict:
    """A mutant that walks commons in reverse must change node allocation order."""
    from itertools import combinations

    circuit = optimized.SharedPointCircuit(8)
    local = circuit.local
    active_sorted = sorted(local.active)
    h = 8
    inputs = list(combinations(range(h), 3))
    variables = {t: i + 1 for i, t in enumerate(inputs)}
    args = [None] * (len(inputs) + 1)
    core = [0] + [sum(1 << i for i in t) for t in inputs]
    union = list(core)
    provenance = [None] * len(args)
    points = [[j for j in range(h) if j != i] for i in range(h)]
    lookup = {}
    merged = 0
    # Historical contract: commons ascend. Reverse order preserves per-common
    # topology but changes when cross-common merges are discovered.
    for common in range(h - 1, -1, -1):
        mapping = {}
        pts = points[common]
        for node in active_sorted:
            if local.args[node] is None:
                a, b = local.inputs[node - 1]
                t = tuple(sorted((common, pts[a], pts[b])))
                mapping[node] = variables[t]
                continue
            a, b = (mapping[x] for x in local.args[node])
            cval = core[a] & core[b]
            uval = union[a] | union[b]
            key = (cval, uval)
            if cval.bit_count() >= 2 and key in lookup:
                mapping[node] = lookup[key]
                merged += 1
                continue
            new = len(args)
            mapping[node] = new
            args.append((a, b))
            core.append(cval)
            union.append(uval)
            provenance.append((common, node))
            if cval.bit_count() >= 2:
                lookup[key] = new
    require(args != circuit.args, "reverse-common mutant must change args allocation")
    require(provenance != circuit.provenance, "reverse-common mutant must change provenance order")
    require(merged > 0, "mutant should still perform some merges")
    return {"reorder_mutant": "rejected"}


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
    baseline = load_module(PACKAGE / "baseline.py", "partial_swap_init_baseline")
    verifies = check_construction_equivalence(baseline, production)
    mutant = check_reorder_mutant_rejected(baseline, production)
    if __debug__:
        rejection = check_support_rejection(baseline, production)
    else:
        # Historical SharedPointCircuit.verify uses assert, stripped under -O.
        rejection = {"support_rejection": "skipped_under_-O"}
    maybe_write_certificate(args.write_certificate)
    pins = check_certificate_pin_discipline()
    print(
        "PASS_PARTIAL_SWAP_INIT",
        f"verify_cases={verifies['verify_cases']}",
        f"mutant={mutant['reorder_mutant']}",
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
