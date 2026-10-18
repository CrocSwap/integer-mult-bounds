#!/usr/bin/env python3
"""Behavior checks for the arbitrary-dirty complete-word acceptance boundary."""
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("frame73", HERE / "verify.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class CompleteWordTests(unittest.TestCase):
    def setUp(self):
        source = HERE.parent / "universal-connector-boundary" / "CERTIFICATE.json"
        self.fixture = json.loads(source.read_text())["schedules"]["five_extra_output"]

    def check(self, word, rows=None):
        return verifier.check_unframed_word(
            word, self.fixture["sources"], self.fixture["rows"] if rows is None else rows
        )

    def test_complete_74_call_construction(self):
        self.assertEqual(self.check(self.fixture["word"]), (32, tuple(range(1, 32))))

    def test_missing_source_restore_rejects(self):
        word = self.fixture["word"].copy()
        index = max(i for i, event in enumerate(word) if event[0] == "B")
        del word[index]
        with self.assertRaisesRegex(ValueError, "connector restoration"):
            self.check(word)

    def test_missing_readout_rejects_arbitrary_connector_dirt(self):
        word = self.fixture["word"].copy()
        index = next(i for i, event in enumerate(word) if event == ["A", 20])
        del word[index]
        with self.assertRaisesRegex(ValueError, "output map"):
            self.check(word)

    def test_wrong_nonzero_target_rejects(self):
        rows = self.fixture["rows"].copy()
        rows[20] ^= 1
        with self.assertRaisesRegex(ValueError, "output map"):
            self.check(self.fixture["word"], rows)


if __name__ == "__main__":
    unittest.main()
