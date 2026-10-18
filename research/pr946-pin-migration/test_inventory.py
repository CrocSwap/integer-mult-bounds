"""Adversarial inputs for the literal provenance inventory; no repository edits."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("pin_inventory", Path(__file__).with_name("verify.py"))
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)
PATH = "scripts/audit_complex_centers.py"
OLD = "a" * 64
NEW = "b" * 64


class InventoryControls(unittest.TestCase):
    def test_escaped_path_and_large_number_do_not_hide_pin(self):
        # Five actual historical JSON files exceeded Python's default digit
        # limit. Escaping the slash must not defeat coverage either.
        raw = ('{"scripts\\u002faudit_complex_centers.py":"' + OLD +
               '","unrelated_integer":' + "9" * 15000 + '}').encode()
        refs = list(inventory.references(inventory.scan_json(raw), {PATH}))
        self.assertEqual([(r[0], r[1]) for r in refs], [(PATH, OLD)])

    def test_numeric_digest_is_not_a_string_pin(self):
        raw = ('{"' + PATH + '":' + '1' * 64 + '}').encode()
        self.assertEqual(list(inventory.references(inventory.scan_json(raw), {PATH})), [])

    def test_duplicate_key_fails_instead_of_hiding_old_pin(self):
        raw = ('{"' + PATH + '":"' + OLD + '","' + PATH + '":"' + NEW + '"}').encode()
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            inventory.scan_json(raw)

    def test_other_digest_is_not_a_newly_introduced_conflict(self):
        self.assertEqual(inventory.classify("c" * 64, OLD, NEW), "other_digest")
        self.assertEqual(inventory.classify(NEW, OLD, NEW), "proposed_bytes_reference")
        self.assertEqual(inventory.classify(OLD, OLD, NEW), "old_bytes_reference")
        self.assertEqual(inventory.classify(OLD, OLD, OLD), "unchanged")

    def test_same_digest_with_different_path_is_not_dependency(self):
        obj = {"scripts/unrelated.py": OLD, "message": PATH, "sha256": OLD}
        self.assertEqual(list(inventory.references(obj, {PATH})), [])

    def test_nested_records_have_precise_json_pointers(self):
        obj = {"x/y~": [{"repository_path": PATH, "sha256": OLD},
                         {PATH: {"sha256": NEW}}]}
        refs = list(inventory.references(obj, {PATH}))
        self.assertEqual({r[2] for r in refs}, {
            "/x~1y~0/0/sha256", "/x~1y~0/1/scripts~1audit_complex_centers.py/sha256"})


if __name__ == "__main__":
    unittest.main()
