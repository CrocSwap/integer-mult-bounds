#!/usr/bin/env python3
"""Behavioral boundary controls. Arham Tahir with OpenAI Codex; Apache-2.0."""

import copy
import gzip
import json
from pathlib import Path
import runpy
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
boundary = runpy.run_path(str(PACKAGE / "boundary.py"))
verify = runpy.run_path(str(PACKAGE / "verify.py"))


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = verify["inputs"]()
        cls.word = json.loads(gzip.decompress(cls.data[verify["WORD"]]))

    def test_schema_and_coefficient_enumeration(self):
        self.assertEqual(verify["support_enumeration"](boundary["validate_scatter"]),
                         {"rows": 364, "accepted": 16, "rejected": 348})
        with self.assertRaisesRegex(ValueError, "multiplicity accepted"):
            verify["support_enumeration"](lambda word: None)
        for retained, rows in (([], [[]]), ([4], [[0]]), ([4, 5], [[1, 0]])):
            boundary["validate_scatter"]({"v": 1, "ret": retained, "scatter": rows})

    def test_malformed_schema_both_real_entry_modes(self):
        cases = []
        for row in ([0, 0], [0, 0, 0], [True], [0.0], ["0"], [-1], [9], "0", None):
            word = copy.deepcopy(self.word)
            word["scatter"][0] = row
            cases.append(word)
        for key, value in (("scatter", []), ("scatter", {}), ("ret", {}), ("v", True), ("v", 0)):
            cases.append({**self.word, key: value})
        cases.extend(([], {}, None))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = directory / "word.json"
            output = directory / "output"
            for word in cases:
                fixture.write_text(json.dumps(word))
                for mode in ("check", "export"):
                    with self.subTest(word=str(word)[:50], mode=mode):
                        result = verify["cli"](mode, fixture, output if mode == "export" else None)
                        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                        self.assertIn("REJECT simple-scatter-v1", result.stderr)
                        self.assertFalse(output.exists())

    def test_rejection_preserves_existing_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / "output"
            output.mkdir()
            sentinel = output / "249-records.bin"
            sentinel.write_bytes(b"existing evidence")
            paired = copy.deepcopy(self.word)
            paired["scatter"][0].extend([0, 0])
            fixture = directory / "word.json"
            fixture.write_text(json.dumps(paired))
            result = verify["cli"]("export", fixture, output)
            self.assertEqual(result.returncode, 2)
            self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()},
                             {"249-records.bin": b"existing evidence"})

    def test_permuted_simple_rows_keep_all_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = directory / "word.json"
            fixture.write_text(json.dumps(self.word))
            original = verify["cli"]("export", fixture, directory / "original")
            self.assertEqual(original.returncode, 0, original.stderr)
            permuted = {**self.word, "scatter": [row[::-1] for row in self.word["scatter"]]}
            fixture.write_text(json.dumps(permuted))
            before = fixture.read_bytes()
            self.assertEqual(verify["cli"]("check", fixture).returncode, 0)
            self.assertEqual(verify["cli"]("export", fixture, directory / "permuted").returncode, 0)
            self.assertEqual(before, fixture.read_bytes())
            for name in verify["ARTIFACTS"]:
                self.assertEqual((directory / "original" / name).read_bytes(),
                                 (directory / "permuted" / name).read_bytes())

    def test_original_input_replacement_cannot_bypass_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = directory / "word.json"
            paired = copy.deepcopy(self.word)
            paired["scatter"][0].extend([0, 0])
            real_run = subprocess.run
            snapshots = []

            def replace_original(command, **kwargs):
                fixture.write_text(json.dumps(paired))
                snapshots.append(Path(command[-1] if "check" == current_mode else command[-2]))
                self.assertEqual(json.loads(gzip.decompress(snapshots[-1].read_bytes())), self.word)
                return real_run(command, **kwargs, capture_output=True, text=True)

            for current_mode in ("check", "export"):
                fixture.write_text(json.dumps(self.word))
                with patch.object(subprocess, "run", side_effect=replace_original):
                    status = boundary["execute"](current_mode, fixture,
                                                  directory / "output" if current_mode == "export" else None)
                self.assertEqual(status, 0)
                self.assertTrue(all(not path.exists() for path in snapshots))
            actual, expected = verify["columns"]((directory / "output/249-records.bin").read_bytes(), self.word)
            self.assertEqual(actual, expected)

    def test_source_mismatch_before_delegation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = root / "word.json"
            fixture.write_text(json.dumps(self.word))
            for mode, name in boundary["SCRIPTS"].items():
                source = root / name
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(self.data[name] + b"\n")
                with self.subTest(mode=mode), patch.object(subprocess, "run") as child:
                    with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                        boundary["execute"](mode, fixture, root / "out" if mode == "export" else None, root)
                    child.assert_not_called()
                    self.assertFalse((root / "out").exists())

    def test_schema_does_not_replace_semantic_checker(self):
        single = copy.deepcopy(self.word)
        single["scatter"][0].append(0)
        boundary["validate_scatter"](single)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = directory / "word.json"
            fixture.write_text(json.dumps(single))
            result = verify["cli"]("check", fixture)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("targets not y + x", result.stdout)
            result = verify["cli"]("export", fixture, directory / "output")
            self.assertEqual(result.returncode, 0, result.stderr)
            actual, expected = verify["columns"]((directory / "output/249-records.bin").read_bytes(), single)
            self.assertNotEqual(actual, expected)

    def test_bad_input_and_argument_errors(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = directory / "word.json.gz"
            for body in (b"broken", gzip.compress(b"{")):
                fixture.write_bytes(body)
                result = verify["cli"]("export", fixture, directory / "output")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse((directory / "output").exists())
            fixture.write_bytes(self.data[verify["WORD"]])
            for mode, output in (("export", None), ("check", directory / "output")):
                self.assertEqual(verify["cli"](mode, fixture, output).returncode, 2)

    def test_export_mutation_controls(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = directory / "word.json"
            fixture.write_text(json.dumps(self.word))
            self.assertEqual(verify["cli"]("export", fixture, directory / "output").returncode, 0)
            raw = (directory / "output/249-records.bin").read_bytes()
            with self.assertRaisesRegex(ValueError, "aligned records"):
                verify["columns"](raw[:-1], self.word)
            records = list(struct.iter_unpack("<6i", raw))
            cut = next(i for i, record in enumerate(records) if record[0] == 1 and record[1] == 111)
            mutated = b"".join(struct.pack("<6i", *record) for i, record in enumerate(records) if i != cut)
            actual, expected = verify["columns"](mutated, self.word)
            self.assertNotEqual(actual, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
