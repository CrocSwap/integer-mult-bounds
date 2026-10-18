#!/usr/bin/env python3
"""Behavioral controls for integer-labels-v1; Apache-2.0, Codex assistance."""

import copy
from fractions import Fraction
import gzip
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
audit = runpy.run_path(str(PACKAGE / "verify.py"))
boundary = audit["boundary"]


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = audit["inputs"]()
        cls.word = json.loads(gzip.decompress(cls.data[audit["WORD"]]))

    def test_exact_integer_schema(self):
        boundary["validate_labels"](self.word)
        for value in (0.5, -0.5, 0.0, True, False, "0", None, [], {}, float("inf"), float("nan")):
            mutant = copy.deepcopy(self.word)
            mutant["lines"][0][1] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "exact integer"):
                boundary["validate_labels"](mutant)
        # Schema does not pretend to prove root geometry or bound integer size.
        integer = copy.deepcopy(self.word)
        integer["lines"][0][1] = 10 ** 100
        boundary["validate_labels"](integer)

    def test_row_and_header_shapes(self):
        cases = [None, [], {}, {**self.word, "h": True}, {**self.word, "h": 8.0},
                 {**self.word, "v": True}, {**self.word, "v": 0},
                 {**self.word, "lines": self.word["lines"][:-1]}]
        for row in (None, "00000000", [0] * 7, [0] * 9):
            word = copy.deepcopy(self.word)
            word["lines"][0] = row
            cases.append(word)
        for word in cases:
            with self.subTest(word=str(word)[:40]), self.assertRaises(ValueError):
                boundary["validate_labels"](word)

    def test_both_cli_modes_reject_before_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / "out"
            output.mkdir()
            (output / "249-records.bin").write_bytes(b"retained evidence")
            fixture = directory / "word.json"
            for value in (0.5, -0.5, 0.0, True, "0"):
                word = copy.deepcopy(self.word)
                word["lines"][0][1] = value
                fixture.write_text(json.dumps(word), encoding="utf-8")
                for mode in ("check", "export"):
                    with self.subTest(value=value, mode=mode):
                        result = audit["cli"](mode, fixture, output if mode == "export" else None)
                        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                        self.assertIn("exact integer", result.stderr)
                        self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()},
                                         {"249-records.bin": b"retained evidence"})

    def test_scatter_guard_is_retained(self):
        word = copy.deepcopy(self.word)
        word["scatter"][0].extend([0, 0])
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = directory / "word.json"
            fixture.write_text(json.dumps(word), encoding="utf-8")
            for mode in ("check", "export"):
                result = audit["cli"](mode, fixture, directory / "out" if mode == "export" else None)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("duplicate index", result.stderr)
            self.assertFalse((directory / "out").exists())

    def test_exact_rank_controls(self):
        rank = audit["rank"]
        self.assertEqual(rank([[2, 0], [4, 0]]), 1)
        self.assertEqual(rank([[2, Fraction(1, 2)], [4, 0]]), 2)
        self.assertEqual(rank([[0, 1], [1, 1], [2, 2]]), 2)
        self.assertEqual(rank([]), 0)

    def test_authenticated_dependencies_fail_before_delegate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = root / "word.json"
            fixture.write_text(json.dumps(self.word), encoding="utf-8")
            for name in (boundary["PREDECESSOR"], *boundary["SCRIPTS"].values()):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(self.data[name])
            for name in (boundary["PREDECESSOR"], *boundary["SCRIPTS"].values()):
                path = root / name
                path.write_bytes(self.data[name] + b"\n")
                mode = "export" if name == boundary["SCRIPTS"]["export"] else "check"
                with self.subTest(name=name), patch.object(subprocess, "run") as child:
                    with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                        boundary["execute"](mode, fixture, root / "out" if mode == "export" else None, root)
                    child.assert_not_called()
                    self.assertFalse((root / "out").exists())
                path.write_bytes(self.data[name])

    def test_input_replacement_cannot_change_validated_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = directory / "word.json"
            mutant = copy.deepcopy(self.word)
            mutant["lines"][0][1] = 0.5
            real_run = subprocess.run
            snapshots = []
            for mode in ("check", "export"):
                fixture.write_text(json.dumps(self.word), encoding="utf-8")

                def replace_original(command, **kwargs):
                    fixture.write_text(json.dumps(mutant), encoding="utf-8")
                    snapshot = Path(command[-1] if mode == "check" else command[-2])
                    snapshots.append(snapshot)
                    self.assertEqual(json.loads(gzip.decompress(snapshot.read_bytes())), self.word)
                    return real_run(command, **kwargs, capture_output=True, text=True)

                with patch.object(subprocess, "run", side_effect=replace_original):
                    code = boundary["execute"](mode, fixture, directory / "out" if mode == "export" else None)
                self.assertEqual(code, 0)
            self.assertTrue(all(not path.exists() for path in snapshots))
            frames = json.loads((directory / "out/frames.json").read_bytes())["frames"]
            self.assertEqual(frames["267"]["dim"], 4)

    def test_corrupt_record_is_not_a_scalar_pass(self):
        with self.assertRaisesRegex(ValueError, "record alignment"):
            audit["scalar_columns"](b"x", self.word)
        with self.assertRaisesRegex(ValueError, "scalar endpoint"):
            audit["scalar_columns"](b"", self.word)


if __name__ == "__main__":
    unittest.main(verbosity=2)
