#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for proof-critical trace and source boundaries."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "c5_verify", Path(__file__).with_name("verify.py")
)
if SPEC is None or SPEC.loader is None:
    raise ImportError("fixed verifier module is unavailable")
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class Controls(unittest.TestCase):
    def test_rank_counts_are_insufficient(self):
        cycle, weights = v.CORES[0]
        rows = v.records(tuple(v.geometry()[i] for i in cycle), weights)
        target, defect = v.cases(weights, 19)[0]
        self.assertFalse(v.reach(rows, weights, target, defect)["reachable"])
        self.assertTrue(
            v.reach(rows, weights, target, defect, traces=False)["reachable"]
        )
        # Literal cost19 count witness. This is not a scalar factorization.
        ids = (462, 809, 903, 1008, 1011)
        chosen = [rows[i] for i in ids]
        self.assertEqual(sum(r[2] for r in chosen), 19)
        self.assertEqual(
            tuple(sum(r[3][k] for r in chosen) for k in range(10)), v.RANKS
        )
        self.assertTrue(
            any(not v.trace_ok(r[0], r[1], r[3], target, weights) for r in chosen)
        )

    def test_tight_and_loose_blocks(self):
        weights = (1,) * 10
        hits = tuple(int(bool(5 & h)) for h in v.BLOCKS)
        target = tuple(v.RANKS)
        self.assertFalse(v.trace_ok(5, 5, hits, target, weights))
        loose = tuple(
            t + 1 if h.bit_count() == 2 else t
            for t, h in zip(target, v.BLOCKS, strict=True)
        )
        self.assertTrue(v.trace_ok(5, 5, hits, loose, weights))
        # A capped zero-weight block is never an equality premise.
        zero_weights = tuple(
            w if h.bit_count() == 1 else 0
            for w, h in zip(weights, v.BLOCKS, strict=True)
        )
        self.assertTrue(v.trace_ok(5, 5, hits, target, zero_weights))

    def test_actual_tariff_and_order(self):
        local = tuple(v.geometry()[i] for i in v.CORES[0][0])
        bad = (local[0], local[2], local[1], local[3], local[4])
        with self.assertRaisesRegex(ValueError, "actual induced C5"):
            v.records(bad, v.CORES[0][1])
        self.assertEqual(v.attainment(local), [4] * 5)

    def test_live_sources_are_authenticated(self):
        inventory = json.loads((v.HERE / "SOURCES.json").read_bytes())
        raw = v.sources()
        with tempfile.TemporaryDirectory(prefix="c5-source-control-") as tmp:
            root = Path(tmp)
            for name, payload in raw.items():
                path = root / v.INPUT / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            for name, payload in raw.items():
                path = root / v.INPUT / name
                path.write_bytes(payload + b" ")
                with self.assertRaisesRegex(ValueError, "source SHA256"):
                    v.sources(root)
                path.write_bytes(payload)
            manifest = root / "SOURCES.json"
            for mutation in ("usage", "duplicate", "extra", "schema"):
                wrong = copy.deepcopy(inventory)
                if mutation == "usage":
                    next(r for r in wrong["files"] if r["usage"] == "input")[
                        "usage"
                    ] = "provenance"
                elif mutation == "duplicate":
                    wrong["files"][0] = wrong["files"][1]
                elif mutation == "extra":
                    wrong["files"].append(wrong["files"][0])
                else:
                    wrong["files"][0]["unexpected"] = True
                manifest.write_text(json.dumps(wrong))
                with self.assertRaises(ValueError):
                    v.sources(root, manifest)

    def test_all_sub20_costs_are_present(self):
        result = v.build()
        self.assertEqual(
            [r["weighted_rank_sum"] for r in result["cores"]], [112, 112, 108, 112]
        )
        self.assertEqual(
            [[g["cost"] for g in r["checks"]] for r in result["cores"]],
            [[19], [19], [18, 19], [19]],
        )
        self.assertEqual(
            sum(len(g["cases"]) for r in result["cores"] for g in r["checks"]), 58
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
