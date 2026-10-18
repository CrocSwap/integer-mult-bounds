"""Fail-closed reporting controls, not mathematical proof tests. Apache-2.0."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("replay", Path(__file__).with_name("replay.py"))
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class CensusControls(unittest.TestCase):
    theorems = [{"name": "N.a", "private": False}, {"name": "N.b", "private": True}]
    valid = ("'N.a' does not depend on any axioms\n"
             "'_private.AllAxioms.0.N.b' depends on axioms: [propext,\n Quot.sound]\n")

    def test_complete_report(self):
        result = replay.axiom_census(self.valid, self.theorems)
        self.assertEqual(result["theorem_count"], 2)
        self.assertEqual(result["axiom_union"], ["Quot.sound", "propext"])

    def test_reject_missing(self):
        with self.assertRaises(ValueError):
            replay.axiom_census(self.valid.splitlines()[0], self.theorems)

    def test_reject_duplicate(self):
        with self.assertRaises(ValueError):
            replay.axiom_census(self.valid + self.valid, self.theorems)

    def test_reject_foreign_declaration(self):
        with self.assertRaises(ValueError):
            replay.axiom_census(self.valid + "'N.c' does not depend on any axioms\n", self.theorems)

    def test_reject_custom_axiom(self):
        with self.assertRaises(ValueError):
            replay.axiom_census(self.valid.replace("propext", "Unproved.law"), self.theorems)

    def test_reject_sorry(self):
        with self.assertRaises(ValueError):
            replay.axiom_census(self.valid.replace("propext", "sorryAx"), self.theorems)

    def test_reject_errors_even_with_complete_records(self):
        for diagnostic in ("error: failed", "error(lean.unknownIdentifier): failed",
                           "warning: declaration uses 'sorry'"):
            with self.subTest(diagnostic=diagnostic), self.assertRaises(ValueError):
                replay.axiom_census(self.valid + diagnostic, self.theorems)

    def test_reject_wrong_private_binding(self):
        with self.assertRaises(ValueError):
            replay.axiom_census(self.valid.replace("_private.AllAxioms.0.", ""), self.theorems)


if __name__ == "__main__":
    unittest.main()
