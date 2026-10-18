#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the window obstruction, including a separate oracle."""

import copy
import itertools
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


def subset_oracle(jobs, supplies):
    """Independent exhaustive matching by reachable subsets of individual slots."""
    slots = [time for time, count in enumerate(supplies) for _ in range(count)]
    states = {0}
    for first, last, count, *_ in jobs:
        for _ in range(count):
            previous = set(states)
            for state in previous:
                for i, time in enumerate(slots):
                    if first <= time <= last and not state & (1 << i):
                        states.add(state | (1 << i))
    return max(map(int.bit_count, states))


class WindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = v.authenticate()
        cls.template = v.decoded(cls.data[v.ALLOC + "vendor/TEMPLATE.json.gz"], True)
        cls.plan = v.decoded(cls.data[v.ALLOC + "vendor/PLAN.json.gz"], True)
        cls.source = v.source_types(cls.template, cls.plan)

    def test_matching_exhaustive_oracle(self):
        intervals = [(a, b) for a in range(3) for b in range(a, 3)]
        cases = 0
        for size in range(5):
            for selected in itertools.combinations_with_replacement(intervals, size):
                jobs = [(a, b, 1) for a, b in selected]
                for supplies in itertools.product(range(3), repeat=3):
                    actual, witness = v.interval_matching(jobs, supplies)
                    self.assertEqual(actual, subset_oracle(jobs, supplies))
                    self.assertEqual(actual, v.validate_matching(jobs, supplies, witness))
                    cases += 1
        self.assertEqual(cases, 5670)

    def test_boundary_and_capacity_controls(self):
        jobs = [(1, 1, 2)]
        self.assertEqual(v.interval_matching(jobs, [2, 1])[0], 1)
        self.assertEqual(v.interval_matching([(0, 1, 2)], [2, 1])[0], 2)
        with self.assertRaisesRegex(ValueError, "source window"):
            v.validate_matching(jobs, [2, 1], [(0, 0, 1)])
        with self.assertRaisesRegex(ValueError, "call capacity"):
            v.validate_matching(jobs, [2, 1], [(1, 0, 2)])
        with self.assertRaisesRegex(ValueError, "job capacity"):
            v.validate_matching(jobs, [2, 3], [(1, 0, 2), (1, 0, 1)])

    def test_source_cuts_and_all_plan_windows(self):
        self.assertEqual(v.check_published_windows(self.source, self.plan), 666)
        altered = copy.deepcopy(self.template)
        event = next(e for e in altered["execution_schedule"]
                     if e["kind"] == "idle_cover_sweep" and e["from_level"] == 1)
        event["from_level"] = 0
        with self.assertRaisesRegex(ValueError, "declared/actual"):
            v.source_types(altered, self.plan)
        plan = copy.deepcopy(self.plan)
        plan["windows"]["0,1"][1].insert(0, 0)
        with self.assertRaisesRegex(ValueError, "historical windows"):
            v.check_published_windows(self.source, plan)

    def test_physical_family_and_port_binding(self):
        plan = copy.deepcopy(self.plan)
        plan["sides"]["3"] = plan["sides"]["1"]
        with self.assertRaisesRegex(ValueError, "distinct physical families"):
            v.source_types(self.template, plan)
        template = copy.deepcopy(self.template)
        template["idle_children"].pop()
        with self.assertRaisesRegex(ValueError, "port domain"):
            v.source_types(template, self.plan)

    def test_closed_forms_and_published_positive(self):
        for replicas in (1, 2, 3, 20, 74):
            for kind in ("stage_major", "replica_major"):
                result = v.chronology_result(self.source, v.order_for(replicas, kind), kind)
                expected = 3 * (26 * replicas + 99) if kind == "stage_major" else 375 * replicas
                self.assertEqual(result["unmatched"], expected)
        published = v.decoded(self.data[v.ALLOC + "ORDER.json"])
        self.assertEqual(v.chronology_result(self.source, published, "positive")["unmatched"], 0)

    def test_call_identity_and_causality(self):
        order = v.order_for(2, "stage_major")
        order[0] = order[1]
        with self.assertRaisesRegex(ValueError, "unique call"):
            v.times_for(order)
        order = v.order_for(2, "stage_major")
        order[0], order[2] = order[2], order[0]
        with self.assertRaisesRegex(ValueError, "causal replica"):
            v.times_for(order)

    def test_provider_and_primal_mutants(self):
        data = dict(self.data)
        path = v.PREDECESSOR + "vendor/PROVIDERS.json"
        providers = v.decoded(data[path])
        providers["extra"]["widths"][2] = 7
        data[path] = json.dumps(providers).encode()
        with self.assertRaisesRegex(ValueError, "provider widths"):
            v.cap_premise(data)
        data = dict(self.data)
        path = v.PREDECESSOR + "vendor/CAP.json"
        cap = v.decoded(data[path])
        cap["basis_patterns"][0]["count_per_replica"] = "671"
        data[path] = json.dumps(cap).encode()
        with self.assertRaisesRegex(ValueError, "primal conservation"):
            v.cap_premise(data)

    def test_source_corruption_rejects(self):
        with tempfile.TemporaryDirectory(prefix="t20-source-") as directory:
            root = Path(directory)
            for name, raw in self.data.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            self.assertEqual(v.authenticate(root), self.data)
            target = root / (v.PREDECESSOR + "arithmetic.py")
            target.write_bytes(target.read_bytes() + b"\n# changed\n")
            with self.assertRaisesRegex(ValueError, "source bytes"):
                v.authenticate(root)

    def test_optimized_complete_cli(self):
        command = [sys.executable, "-I", "-O", "-Werror", "-B", str(v.PACKAGE / "verify.py")]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_COUPLED_T20_WINDOW_AUDIT", result.stdout)


if __name__ == "__main__":
    unittest.main()
