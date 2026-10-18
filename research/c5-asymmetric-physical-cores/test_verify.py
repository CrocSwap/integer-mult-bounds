#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Controls target the factor-to-certificate boundary and physical inputs."""

import json
import tempfile
import unittest
from pathlib import Path

import independent as other
import verify as main


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.planes = main.geometry()
        cls.local = tuple(cls.planes[i] for i in main.SOURCE_CORE)
        cls.rows = main.records(cls.local)

    def test_exact_case_budget(self):
        self.assertEqual(set(main.targets()), other.case_targets())
        self.assertEqual(len(main.targets()), 11)

    def test_rank_counts_alone_accept_false_decoder(self):
        chosen = {(28, 28), (19, 19), (7, 7), (14, 24), (1, 4)}
        rows = [row for row in self.rows if row[:2] in chosen]
        self.assertEqual(sum(row[2] for row in rows), 19)
        self.assertEqual(
            [sum(row[3][i] for row in rows) for i in range(6)], [4, 4, 4, 4, 2, 2]
        )
        self.assertEqual(sum(row[3][7] for row in rows), 4)
        target = main.BASE[:6] + (2,)
        self.assertTrue(main.reach(self.rows, target, traces=False)["reachable"])
        self.assertFalse(main.reach(self.rows, target)["reachable"])
        self.assertTrue(any(not main.trace_ok(row, target) for row in rows))

    def test_trace_oracles_on_all_source_supports(self):
        for target in main.targets():
            for row in self.rows:
                self.assertEqual(
                    main.trace_ok(row, target), other.consistent(row, target)
                )

    def test_free_terms_and_repeated_supports(self):
        free = [row for row in self.rows if row[2] == 0 and row[0] and row[1]]
        self.assertEqual(len(free), 20)
        self.assertTrue(all(not any(row[3]) for row in free))
        single = next(row for row in self.rows if row[:2] == (20, 20))
        target = tuple(4 * x for x in single[3][:7])
        self.assertTrue(main.reach([single] + free, target, traces=False)["reachable"])

    def test_real_tariffs_and_fit_on_every_covered_order(self):
        result = json.loads((main.HERE / "RESULT.json").read_bytes())
        distinct = set()
        for row in result["covered"]:
            local = tuple(self.planes[i] for i in row["order"])
            self.assertEqual(main.baseline(local), 20)
            actual = main.digest([r[2] for r in main.records(local)])
            self.assertEqual(actual, row["tariff_sha256"])
            distinct.add(actual)
        self.assertGreater(len(distinct), 1)
        wrong = list(self.local)
        wrong[1], wrong[2] = wrong[2], wrong[1]
        with self.assertRaisesRegex(ValueError, "strict scalar fit|cost20"):
            main.baseline(tuple(wrong))

    def test_fail_closed_source_inventory_and_bytes(self):
        source = json.loads((main.HERE / "SOURCES.json").read_bytes())
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            inventory = root / "inventory.json"
            for mutation in (
                source["files"] + [source["files"][-1]],
                source["files"][:3] + [source["files"][2]],
            ):
                inventory.write_text(json.dumps({"files": mutation}))
                with self.assertRaises(ValueError):
                    main.geometry(root, inventory)
            inventory.write_text(json.dumps(source))
            for row in source["files"]:
                if row["usage"] == "input":
                    target = root / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((main.ROOT / row["path"]).read_bytes())
            self.assertEqual(main.geometry(root, inventory), self.planes)
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                main.geometry(root, inventory)


if __name__ == "__main__":
    unittest.main()
