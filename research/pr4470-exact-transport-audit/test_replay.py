"""Receipt comparison controls complement the scientific engine's controls."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("transport_replay", HERE / "replay.py")
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


class ReceiptTests(unittest.TestCase):
    def test_exact_and_reordered_object(self):
        value = R.load_expected()
        R.compare(dict(reversed(list(value.items()))), value)

    def test_scientific_and_scope_fields_are_not_ignored(self):
        value = R.load_expected()
        for field, change in (("physical_pairs", 422), ("new_kappa", True),
                              ("source_head", "0" * 40), ("not_covered", [])):
            actual = copy.deepcopy(value)
            actual[field] = change
            with self.assertRaises(ValueError):
                R.compare(actual, value)

    def test_boolean_is_not_interchangeable_with_integer(self):
        with self.assertRaises(ValueError):
            R.compare({"positive": 1}, {"positive": True})
        with self.assertRaises(ValueError):
            R.compare({"count": 1.0}, {"count": 1})

    def test_extra_and_missing_fields_reject(self):
        value = R.load_expected()
        for actual in ({**value, "ignored": 0}, {k: v for k, v in value.items() if k != "status"}):
            with self.assertRaises(ValueError):
                R.compare(actual, value)

    def test_corrupted_expected_receipt_and_engine_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture"
            path.write_bytes(b"{}\n")
            with self.assertRaises(ValueError):
                R.load_expected(path)
            with self.assertRaises(ValueError):
                R.authenticate_engine(path)


if __name__ == "__main__":
    unittest.main()
