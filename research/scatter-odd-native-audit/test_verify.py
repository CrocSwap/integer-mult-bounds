#!/usr/bin/env python3
"""Behavioral controls for the source/CLI/scalar boundary; Apache-2.0.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Native semantic and truncation controls are in verify.py --native.
"""

import gzip
import importlib.util
import itertools
import json
from pathlib import Path
import struct
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("scatter_odd_verify", PACKAGE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def packed(rows):
    return b"".join(struct.pack("<6i", *row) for row in rows)


class BoundaryControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = verify.sources()
        cls.original = json.loads(gzip.decompress(cls.data[verify.WORD]))

    def test_selected_operator_and_changed_endpoint(self):
        expected = verify.expected_operator()
        for name in verify.FIXTURES:
            word = verify.fixture_word(self.original, name)
            self.assertEqual(verify.word_operator(word) == expected, name != "odd_absent")
        changed = verify.word_operator(verify.fixture_word(self.original, "odd_absent"))
        delta = verify.differences(changed, expected)
        self.assertEqual([row["register"] for row in delta], [111])
        self.assertIn(472, delta[0]["input_columns"])

    def test_bitset_operator_against_all_scalar_inputs(self):
        # Two ordinary ADDs and a fresh COPY/ERASE. All 64 dirty assignments,
        # evaluated as bits, independently check the linear bitset projection.
        rows = [(1, 2, 0, 1, 0, 1), (2, 2, 6, 0, 0, 1),
                (1, 3, 6, 1, 0, 3), (3, 2, 6, 0, 0, 0),
                (1, 5, 4, -1, 0, 4)]
        matrix = verify.record_operator(packed(rows), n=6)
        for inputs in itertools.product((0, 1), repeat=6):
            direct = list(inputs)
            direct[2] ^= direct[0]
            copied = direct[2]
            direct[3] ^= copied
            direct[5] ^= direct[4]
            encoded = sum(bit << i for i, bit in enumerate(inputs))
            self.assertEqual([(row & encoded).bit_count() % 2 for row in matrix], direct)

    def test_record_lifetimes_and_alignment_fail_closed(self):
        cp = (2, 2, 6, 0, 0, 1)
        er = (3, 2, 6, 0, 0, 0)
        add = (1, 3, 6, 1, 0, 3)
        invalid = [[], [add], [cp], [er], [cp, cp, er],
                   [cp, (3, 1, 6, 0, 0, 0)],
                   [cp, (1, 2, 0, 1, 0, 2), er],
                   [(1, 1, 1, 1, 0, 1)], [(7, 0, 0, 0, 0, 0)]]
        for rows in invalid:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                verify.record_operator(packed(rows), n=6)
        with self.assertRaisesRegex(ValueError, "alignment"):
            verify.record_operator(packed([cp, add, er])[:-1], n=6)

    def test_source_corruption_before_execution(self):
        with tempfile.TemporaryDirectory(prefix="odd-source-control-") as td:
            root = Path(td)
            verify.snapshot(self.data, root)
            for name, body in self.data.items():
                with self.subTest(source=name):
                    path = root / name
                    path.write_bytes(body + b"\nCORRUPTED")
                    with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                        verify.sources(root)
                    path.write_bytes(body)

    def test_duplicate_rejection_preserves_existing_outputs(self):
        with tempfile.TemporaryDirectory(prefix="odd-output-control-") as td:
            root = Path(td)
            verify.snapshot(self.data, root)
            output = root / "occupied"
            output.mkdir()
            preserved = {name: ("existing " + name).encode() for name in verify.ARTIFACTS}
            for name, body in preserved.items():
                (output / name).write_bytes(body)
            for name in ("even_absent", "odd_present", "odd_absent"):
                word = verify.fixture_word(self.original, name)
                argument = root / (name + ".json.gz")
                argument.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
                result = verify.python(root / verify.BOUNDARY, "export", argument, output)
                self.assertEqual(result.returncode, 2)
                self.assertIn("duplicate index", result.stderr)
                self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, preserved)

    def test_disabled_guard_is_detected_at_actual_cli(self):
        with tempfile.TemporaryDirectory(prefix="odd-disabled-guard-") as td:
            root = Path(td)
            verify.snapshot(self.data, root)
            wrapper = root / verify.BOUNDARY
            body = wrapper.read_text()
            anchor = "    validate_scatter(word)\n"
            self.assertEqual(body.count(anchor), 1)
            argument = root / "odd-present.json.gz"
            word = verify.fixture_word(self.original, "odd_present")
            argument.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
            for bypass in ("check", "export"):
                replacement = f'    if mode != "{bypass}": validate_scatter(word)\n'
                wrapper.write_text(body.replace(anchor, replacement))
                with self.subTest(bypass=bypass), self.assertRaisesRegex(ValueError, "guard did not reject"):
                    verify.guard_cli(root, argument, root, False, {})

    def test_occupied_receipt_directory_refused(self):
        with tempfile.TemporaryDirectory(prefix="odd-receipt-control-") as td:
            directory = Path(td)
            marker = directory / "RESULT.json"
            marker.write_bytes(b"preserve this prior evidence")
            result = verify.python(PACKAGE / "verify.py", "--write-receipts", directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt directory already exists", result.stderr)
            self.assertEqual(marker.read_bytes(), b"preserve this prior evidence")


if __name__ == "__main__":
    unittest.main()
