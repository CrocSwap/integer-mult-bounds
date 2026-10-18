"""Execution-based controls for the joint continuation history lemma."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify


class JointHistoryTests(unittest.TestCase):
    def setUp(self):
        self.predecessor = verify.authenticate()
        self.modules = self.predecessor.load_source()

    def tearDown(self):
        for name in ("words", "records", "matrices", "controller"):
            sys.modules.pop(name, None)

    def execute(self, modes="TB", residue_bits=32, **options):
        return verify.execute(
            self.predecessor, self.modules, modes, residue_bits, **options
        )

    def test_attaining_scalar_dominant_history(self):
        result = self.execute(quota=349)
        self.assertEqual(result["lengths"], (173, 35, 106, 35))
        self.assertEqual(result["backing"], 349)
        binary = self.execute("BB")
        self.assertEqual(binary["backing"], 343)

    def test_short_quota_rejects_and_restores_observers(self):
        records, controller = self.modules[1:]
        before = records.Tape.write, records.Stack.pop, controller.Callback.weight
        with self.assertRaisesRegex(ValueError, "^joint capacity$"):
            self.execute(quota=348)
        self.assertEqual(
            before, (records.Tape.write, records.Stack.pop, controller.Callback.weight)
        )
        self.assertEqual(self.execute(quota=349)["backing"], 349)

    def test_entry_quota_rejection_restores_observers(self):
        records = self.modules[1]
        before = records.Tape.write, records.Stack.pop
        with self.assertRaisesRegex(ValueError, "^joint capacity$"):
            self.execute(warm=(700, 2, 300, 1), quota=10)
        self.assertEqual(before, (records.Tape.write, records.Stack.pop))
        self.assertEqual(self.execute()["backing"], 349)

    def test_repeated_fixed_program_and_arbitrary_warm_arrays(self):
        self.assertEqual(self.execute(repeats=2)["lengths"], (173, 35, 106, 35))
        self.assertEqual(
            self.execute(warm=(700, 2, 300, 1))["lengths"], (700, 35, 300, 35)
        )

    def test_changed_grammar_retains_incompatible_maxima(self):
        first = self.execute("TR")
        self.assertEqual(first["lengths"], (176, 35, 71, 35))
        second = self.execute(warm=first["lengths"])
        self.assertEqual(second["lengths"], (176, 35, 106, 35))
        self.assertEqual(second["backing"], 352)

    def test_coordinate_dependent_metadata_is_outside_the_bound(self):
        result = verify.nonuniform_control(self.predecessor, self.modules)
        self.assertEqual(result["backing"], 850)
        self.assertEqual(result["uniform_envelope"], 827)
        self.assertEqual(self.execute()["backing"], 349)

    def test_actual_gl64_weight_and_root_case(self):
        actual = self.execute("BB", 3, literal=True)
        self.assertEqual(actual["lengths"], (145, 44, 19, 6))
        root = self.execute("", 32)
        self.assertEqual(root["lengths"], (21, 20, 36, 35))

    def test_bad_source_hash_rejects_before_loading(self):
        manifest = json.loads((verify.PACKAGE / "SOURCES.json").read_text())
        next(item for item in manifest["files"] if item["usage"] == "input")[
            "sha256"
        ] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            (path / "SOURCES.json").write_text(json.dumps(manifest))
            with patch.object(verify, "PACKAGE", path):
                with self.assertRaisesRegex(ValueError, "input SHA256"):
                    verify.authenticate()

    def test_boundary_inputs_reject_and_valid_case_still_executes(self):
        for args in ((-1, 14, 32), (True, 14, 32), (2, 1, 32), (2, 14, False)):
            with self.assertRaises(ValueError):
                verify.envelope(*args)
        with self.assertRaises(ValueError):
            self.execute("X")
        self.assertEqual(self.execute()["backing"], 349)


if __name__ == "__main__":
    unittest.main()
