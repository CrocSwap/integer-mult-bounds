"""Exact return-marker and cost-screen controls. SPDX-License-Identifier: Apache-2.0."""

import importlib.util
from itertools import product
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ghost_screen", HERE / "ghost_screen.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class GhostTests(unittest.TestCase):
    def test_rank_against_exhaustive_image_cardinality(self):
        for rows in product(range(8), repeat=3):
            image = {0}
            for row in rows:
                image |= {x ^ row for x in image}
            self.assertEqual(1 << g.rank_f2(rows), len(image))

    def test_complete_screen_and_failure_of_target_only_return(self):
        source = json.loads((HERE / "SOURCE.json").read_text())
        word = g.v.load_word(g.v.ROOT / source["word"]["path"], source)
        frames = g.v.build_receipt(word, source)
        assembly = json.loads((g.v.ROOT / source["assembly"]["path"]).read_text())
        result = g.screen(word, frames, assembly)
        self.assertEqual(result, json.loads((HERE / "GHOST-SCREEN.json").read_text()))
        values, _, _ = g.replay(word, [r["dimension"] for r in frames["frames"]], cleanup=False)
        self.assertTrue(all(values[120 + t] == (1 << (120 + t)) ^ (1 << t) for t in range(120)))
        with self.assertRaisesRegex(g.v.Reject, "restoration/target identity"):
            g.restored(values, word)


if __name__ == "__main__":
    unittest.main(verbosity=2)
