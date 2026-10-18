"""Behavioral controls for the scatter/export boundary. Apache-2.0."""

import copy
import gzip
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = verify.sources(verify.ROOT)
        cls.word = json.loads(gzip.decompress(cls.data[verify.WORD]))

    def test_support_guard(self):
        verify.validate_scatter(self.word)
        for row in ([4, 4], [True], [-1], [9], "4", list(range(10))):
            mutant = copy.deepcopy(self.word)
            mutant["scatter"][0] = row
            with self.subTest(row=row), self.assertRaises(ValueError):
                verify.validate_scatter(mutant)
        mutant = copy.deepcopy(self.word)
        mutant["scatter"].pop()
        with self.assertRaisesRegex(ValueError, "row inventory"):
            verify.validate_scatter(mutant)

    def test_single_occurrence_is_not_null(self):
        checker = verify.checked_module(self.data[verify.CHECKER])
        mutant = copy.deepcopy(self.word)
        mutant["scatter"][0].append(0)
        with self.assertRaisesRegex(checker.Reject, r"targets not y \+ x: \[0\]"):
            checker.check(mutant)

    def test_exporter_identifies_single_and_pair(self):
        single, pair = copy.deepcopy(self.word), copy.deepcopy(self.word)
        single["scatter"][0].append(0)
        pair["scatter"][0].extend([0, 0])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = verify.export(self.data[verify.EXPORTER], single, root / "single")
            second = verify.export(self.data[verify.EXPORTER], pair, root / "pair")
            self.assertEqual(first, second)
            self.assertEqual(len(first) // 24, 27235)

    def test_record_oracle_against_literal_endpoint(self):
        base = b"".join(struct.pack("<6i", 1, 111 + i, i, 1, 0, 3) for i in range(111))
        _, differences = verify.replay(base, self.word)
        self.assertEqual(differences, [])
        extra = struct.pack("<6i", 1, 111, 472, 1, 0, 3)
        values, differences = verify.replay(base + extra, self.word)
        self.assertEqual(differences, [(111, 1 << 472)])
        self.assertEqual(
            verify.witness(values, differences, self.word),
            {
                "output_register": 111,
                "input_column": 472,
                "actual_bit": 1,
                "expected_bit": 0,
                "difference_support": [472],
            },
        )
        self.assertEqual(values[472], 1 << 472)

    def test_record_lifecycle_and_alignment(self):
        for raw in (
            b"x",
            struct.pack("<6i", 4, 0, 0, 0, 0, 0),
            struct.pack("<6i", 2, 472, 661, 0, 0, 0),
            struct.pack("<6i", 1, 111, 661, 1, 0, 0),
            struct.pack("<6i", 3, 472, 661, 0, 0, 0),
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                verify.replay(raw, self.word)

    def test_each_source_corruption_rejects(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path, body in self.data.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
            self.assertEqual(verify.sources(root), self.data)
            for path, body in self.data.items():
                target = root / path
                target.write_bytes(body + b" ")
                with (
                    self.subTest(path=path),
                    self.assertRaisesRegex(ValueError, "source:"),
                ):
                    verify.sources(root)
                target.write_bytes(body)
            self.assertEqual(verify.sources(root), self.data)

    def test_optimized_read_only_replay(self):
        before = {
            p.name: p.read_bytes() for p in verify.PACKAGE.iterdir() if p.is_file()
        }
        run = subprocess.run(
            [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(verify.PACKAGE / "verify.py"),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("PASS_SELECTED_SCATTER_EXPORT_PARITY_AUDIT", run.stdout)
        self.assertEqual(
            before,
            {p.name: p.read_bytes() for p in verify.PACKAGE.iterdir() if p.is_file()},
        )

    def test_typed_receipt_corruption(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("verify.py", "SOURCES.json", "RESULT.json"):
                shutil.copyfile(verify.PACKAGE / name, root / name)
            receipt = json.loads((root / "RESULT.json").read_bytes())
            receipt["normalized_export_equals_baseline"] = 1
            (root / "RESULT.json").write_text(json.dumps(receipt))
            run = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-O",
                    "-B",
                    str(root / "verify.py"),
                    "--root",
                    str(verify.ROOT),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("typed deterministic receipt", run.stderr)


if __name__ == "__main__":
    unittest.main()
