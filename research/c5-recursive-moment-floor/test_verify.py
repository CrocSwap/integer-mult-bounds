#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral and mathematical boundary controls for the moment certificate."""

import copy
import importlib.util
import itertools
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


v = module("verify")
w = module("independent")


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local = v.geometry()
        cls.rows = v.records(cls.local)

    def test_all_rectangular_tariffs(self):
        separate = w.table(w.read_geometry())
        self.assertEqual([t.cost for t in self.rows], [r[2] for r in separate])
        self.assertEqual(v.attainment(self.local), [4] * 5)
        self.assertEqual(len(v.targets(18)), 1)
        self.assertEqual(len(v.targets(19)), 10)
        self.assertEqual(len(v.targets(20)), 49)

    def test_trace_equations_and_dropped_trace_control(self):
        targets = (v.targets(18)[0], v.targets(20)[0], v.targets(20)[-1])
        for target in targets:
            for t in self.rows:
                self.assertEqual(
                    v.trace_ok(t, target),
                    w.consistent(t.left, t.right, t.increment, target),
                )
        target = v.targets(18)[0]
        self.assertFalse(v.maximize(self.rows, target, 18)["reachable"])
        self.assertTrue(v.maximize(self.rows, target, 18, traces=False)["reachable"])

    def test_term_count_premise_is_necessary(self):
        # This FOUR-term count image passes the cost20 trace relaxation and
        # has product 5**20. It is not a scalar fitting decomposition.
        target = (4, 4, 4, 4, 2, 2, 4)
        terms = [
            self.rows[a * 32 + b] for a, b in ((28, 28), (28, 28), (27, 7), (27, 7))
        ]
        self.assertTrue(all(v.trace_ok(t, target) for t in terms))
        self.assertEqual(
            tuple(sum(t.increment[i] for t in terms) for i in range(7)), target
        )
        self.assertGreaterEqual(sum(t.increment[7] for t in terms), 4)
        self.assertEqual(sum(t.cost for t in terms), 20)
        self.assertGreater(5**20, 4**20)

    def test_six_term_exact_split_is_not_rank_rigidity(self):
        # Split one edge outer square into two unequal-support factors.
        factors = []
        for i in range(5):
            ports = (2 * i + 1, 2 * ((i + 1) % 5))
            lefts = ((ports[0],), (ports[1],)) if i == 0 else (ports,)
            factors.extend((left, ports) for left in lefts)
        matrix = [[0] * 10 for _ in range(10)]
        ranks = []
        for left, right in factors:
            a = sum(1 << i for i in {p // 2 for p in left})
            b = sum(1 << i for i in {p // 2 for p in right})
            ranks.append(self.rows[a * 32 + b].cost)
            for i, j in itertools.product(left, right):
                matrix[i][j] += 1
        for i, j in itertools.product(range(10), repeat=2):
            if i // 2 == j // 2 or v.rank_pair(self.local[i // 2], self.local[j // 2]):
                self.assertEqual(matrix[i][j], int(i == j))
        self.assertEqual(ranks, [2, 2, 4, 4, 4, 4])
        self.assertEqual(sum(ranks), 20)
        self.assertLess(2**4 * 4**16, 4**20)

    def test_undercharge_and_saving_interval_boundaries(self):
        term = self.rows[3 * 32 + 3]
        self.assertEqual(term.cost, 4)
        self.assertEqual(term.increment[6], 0)
        undercharged = (
            2 * (term.cost - 1) - 2 * sum(term.increment[:4]) - sum(term.increment[4:6])
        )
        self.assertLess(undercharged, 0)
        self.assertLess(9 * 20**20, 4 * 21**20)
        self.assertGreater(9 * 20**16, 4 * 21**16)

    def test_source_corruption_and_input_reclassification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in v.LIVE:
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT / path, destination)
            self.assertEqual(v.geometry(root), self.local)
            path = root / (v.PREFIX + "MATCHING.json")
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                v.geometry(root)
            sources = json.loads((HERE / "SOURCES.json").read_bytes())
            mutant = copy.deepcopy(sources)
            next(r for r in mutant["files"] if r["usage"] == "input")["usage"] = (
                "provenance"
            )
            inventory = root / "inventory.json"
            inventory.write_text(json.dumps(mutant))
            with self.assertRaisesRegex(ValueError, "source usages"):
                v.geometry(inventory=inventory)


if __name__ == "__main__":
    unittest.main()
