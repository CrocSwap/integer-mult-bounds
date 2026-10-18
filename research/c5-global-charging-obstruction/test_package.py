#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Controls for proof-method boundaries and authenticated export inputs."""

import copy
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import (  # noqa: E402
    ROOT,
    geometry,
    identity_extension,
    obstruction,
    pairing_rank,
    require,
    sources,
)


class Controls(unittest.TestCase):
    def test_complete_plane_not_scalar_line(self):
        # One scalar coordinate carries its entire plane. Replacing the plane
        # by that coordinate's single binary label would undercharge this term.
        plane = geometry()[0]
        self.assertEqual(pairing_rank(plane, plane), 2)
        self.assertEqual(pairing_rank(plane[:1], plane[:1]), 1)

    def test_naive_sum_fails_on_actual_term(self):
        result = json.loads((HERE / "RESULT.json").read_bytes())
        local = sum(r["full_support_rank"] for r in result["cycles"])
        self.assertEqual(local, 193)
        self.assertGreater(local, result["global_full_support_rank"])
        self.assertEqual(local, result["naive_unit_weight_restricted_cost"])

    def test_false_large_certificate_rejected(self):
        # Any raw objective >=26 requires weight sum >=13/10. The test term
        # then costs at least91/10 locally, greater than global9. Final integer
        # rounding is a separate step, explicitly preserved in PROOF.md.
        self.assertGreater(7 * Fraction(26, 20), 9)
        self.assertLess(obstruction(9, [7, 8, 9], [20] * 3), 26)
        for bad in ([0], [-1], [10]):
            with self.assertRaises(ValueError):
                obstruction(9, bad, [20])
        with self.assertRaises(ValueError):
            obstruction(9, [7], [20, 20])

    def test_strict_fit_extension(self):
        self.assertEqual(identity_extension(112), 12433)
        self.assertEqual(identity_extension(2), 3)
        for n in (0, 113, True):
            with self.assertRaises(ValueError):
                identity_extension(n)

    def manifest_control(self, change):
        doc = json.loads((HERE / "SOURCES.json").read_bytes())
        change(doc)
        with tempfile.TemporaryDirectory(prefix="c5-charging-control-") as temp:
            path = Path(temp) / "SOURCES.json"
            path.write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                sources(ROOT, path)

    def test_manifest_inventory_and_usage(self):
        self.manifest_control(lambda d: d["files"].pop())
        self.manifest_control(
            lambda d: d["files"].append(copy.deepcopy(d["files"][-1]))
        )
        self.manifest_control(lambda d: d["files"][-1].update(usage="provenance"))
        self.manifest_control(lambda d: d["files"][-1].update(path="unexpected.json"))
        self.manifest_control(lambda d: d["files"][-1].update(extra=True))

    def test_authentication_and_actual_corruption(self):
        self.manifest_control(lambda d: d["files"][-1].update(sha256="0" * 64))
        self.manifest_control(lambda d: d["files"][-1].update(git_blob="0" * 40))
        with tempfile.TemporaryDirectory(prefix="c5-charging-input-") as temp:
            root = Path(temp)
            for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
                if row["usage"] == "input":
                    target = root / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT / row["path"]).read_bytes())
            self.assertEqual(len(geometry(root)), 56)
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                geometry(root)

    def test_controls_survive_optimization(self):
        with self.assertRaises(ValueError):
            require(False, "must fail with -O too")


if __name__ == "__main__":
    unittest.main()
