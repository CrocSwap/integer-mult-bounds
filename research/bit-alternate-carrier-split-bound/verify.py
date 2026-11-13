#!/usr/bin/env python3
"""Offline replay of two independent exact alternate-carrier certificates.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. This verifies a fixed-source obstruction, not supplier admission.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parent


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    need(spec is not None and spec.loader is not None, "local verifier module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exhaustive_toy_check(kernel, independent) -> dict:
    """Compare both criteria with all witness pairs in all two-field toys."""
    counts = {"contexts": 0, "paired": 0, "local_only": 0}
    for prefix in itertools.product(range(4), repeat=2):
        for suffix in itertools.product(range(4), repeat=2):
            for group in range(4):
                exterior = 3 ^ group
                left = [a for a in range(4)
                        if not (kernel.combine(prefix, a) & exterior)]
                right = [b for b in range(4)
                         if not (kernel.combine(suffix, b) & exterior)]
                local_rows, endpoint_rows = [], []
                paired = False
                for a in left:
                    x, y = 0, 0
                    for j, b in enumerate(right):
                        local = (a & b).bit_count() & 1
                        endpoint = (kernel.combine(prefix, a)
                                    & kernel.combine(suffix, b)).bit_count() & 1
                        x |= local << j
                        y |= endpoint << j
                        paired |= bool(local and endpoint)
                    local_rows.append(x)
                    endpoint_rows.append(y)
                ranks = independent.one_context(list(prefix), list(suffix), group, 2)
                need(ranks["delta_ab"] == independent.gf2_rank(local_rows),
                     "rank identity agrees with all local witness pairs")
                need(ranks["delta_helper"] == independent.gf2_rank(endpoint_rows),
                     "block rank agrees with all clean endpoint witness pairs")
                found, _ = kernel.witness(prefix, suffix, group, 2)
                need((found is not None) == paired,
                     "kernel constructor agrees with exhaustive paired witnesses")
                need(paired == (ranks["delta_ab"] > 0 and ranks["delta_helper"] > 0),
                     "joint nonzero forms characterize this scalar interface")
                counts["contexts"] += 1
                counts["paired"] += int(paired)
                counts["local_only"] += int(ranks["delta_ab"] > 0
                                            and ranks["delta_helper"] == 0)
    need(counts["contexts"] == 1024 and counts["paired"] > 0
         and counts["local_only"] > 0, "both accepting and rejecting controls ran")
    return counts


def altered_source_control(kernel, independent) -> None:
    raw = bytearray(kernel.INPUT.read_bytes())
    raw[len(raw) // 2] ^= 1
    with tempfile.TemporaryDirectory(prefix="alternate-carrier-control-") as tmp:
        bad = Path(tmp) / "changed-source.gz"
        bad.write_bytes(raw)
        for module, reader in ((kernel, kernel.source),
                               (independent, independent.read_source)):
            original = module.INPUT
            module.INPUT = bad
            rejected = False
            try:
                reader()
            except (ValueError, AssertionError) as exc:
                need("bytes" in str(exc), "source rejection precedes scientific replay")
                rejected = True
            finally:
                module.INPUT = original
            need(rejected, "each engine rejects altered source bytes")


def run() -> dict:
    kernel, independent = load("kernel_screen"), load("independent_screen")
    toy = exhaustive_toy_check(kernel, independent)
    altered_source_control(kernel, independent)
    first, second = kernel.run(), independent.run()
    for result, name in ((first, "EXPECTED-KERNEL.json"),
                         (second, "EXPECTED-INDEPENDENT.json")):
        expected = json.loads((ROOT / name).read_text())
        need(result == expected, "complete exact receipt: " + name)
    need(first["contexts"]["banks"] == second["changed_bank_contexts"]["changed_banks"],
         "independent bank coverage")
    need(first["contexts"]["bank_groups"]
         == second["changed_bank_contexts"]["bank_group_contexts"] == 4521,
         "independent group coverage")
    need(sorted(first["groups"], key=lambda r: r["boundary"]) == second["groups"],
         "independent boundary groups")
    need(second["clean_endpoint_pairing_zero_in_all_contexts"], "zero clean form")
    return {
        "status": "PASS_BIT_ALTERNATE_CARRIER_ZERO_PAIRING",
        "source_sha256": hashlib.sha256(kernel.INPUT.read_bytes()).hexdigest(),
        "changed_banks": 3908,
        "bank_group_contexts": 4521,
        "nonzero_clean_pairing_contexts": 0,
        "local_pairing_only_contexts": 76,
        "exhaustive_two_field_controls": toy,
        "altered_source_rejected_by_both_engines": True,
        "kappa_status": "No new kappa; fixed-source obstruction only",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
