"""Endpoint-domain, source and snapshot controls. Apache-2.0.

Mihir Srivastava, with substantial OpenAI Codex assistance.
"""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import boundary as B

WORD = B.ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = json.loads(gzip.decompress(WORD.read_bytes()))

    def test_valid_domain_is_nonmutating(self):
        word = deepcopy(self.word)
        self.assertEqual(B.validate_endpoints(word), 661)
        self.assertEqual(word, self.word)
        # This sufficient syntactic guard does not enforce endpoint geometry.
        word["final"][0] = 0
        self.assertEqual(B.validate_endpoints(word), 661)

    def test_exact_integer_ids_at_both_ends(self):
        for name in ("start", "final"):
            for value in (False, True, 0.0, 1.0, "0", None, [], {}, -1, 636):
                with self.subTest(name=name, value=value):
                    word = deepcopy(self.word)
                    word[name][0] = value
                    with self.assertRaisesRegex(ValueError, "exact in-range integer"):
                        B.validate_endpoints(word)

    def test_endpoint_lengths_and_containers(self):
        for name in ("start", "final"):
            for value in (None, {}, (), [], self.word[name][:-1], self.word[name] + [0]):
                with self.subTest(name=name, length=len(value) if value is not None else None):
                    word = deepcopy(self.word)
                    word[name] = value
                    with self.assertRaisesRegex(ValueError, "exactly one entry"):
                        B.validate_endpoints(word)

    def test_header_and_frame_table_domain(self):
        for key, value in (("v", True), ("v", 0), ("v", 257), ("R", False),
                           ("R", -1), ("R", 4097), ("frames", []), ("frames", {})):
            with self.subTest(key=key, value=value):
                word = deepcopy(self.word)
                word[key] = value
                with self.assertRaises(ValueError):
                    B.validate_endpoints(word)
        with self.assertRaises(ValueError):
            B.validate_endpoints([])

    def test_invalid_endpoint_precedes_all_delegation(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            word = deepcopy(self.word)
            word["final"][0] = True
            path = directory / "bad.json"
            path.write_text(json.dumps(word), encoding="utf-8")
            for mode in ("check", "export"):
                output = directory / "new-output" if mode == "export" else None
                with patch.object(B, "sources", side_effect=AssertionError("delegate reached")):
                    with self.assertRaisesRegex(ValueError, "final\\[0\\]"):
                        B.execute(mode, path, output)
                self.assertFalse((directory / "new-output").exists())

    def test_every_delegate_is_authenticated(self):
        bodies = B.sources(B.ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path, body in bodies.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
            self.assertEqual(B.sources(root), bodies)
            for path, body in bodies.items():
                with self.subTest(path=path):
                    (root / path).write_bytes(body + b" ")
                    with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                        B.sources(root)
                    (root / path).write_bytes(body)

    def test_original_replacement_cannot_change_validated_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "candidate.json"
            path.write_text(json.dumps(self.word), encoding="utf-8")
            source_reader = B.sources

            def replace_after_validation(root):
                bodies = source_reader(root)
                bad = deepcopy(self.word)
                bad["final"][0] = True
                path.write_text(json.dumps(bad), encoding="utf-8")
                return bodies

            with patch.object(B, "sources", side_effect=replace_after_validation):
                result = B.execute("check", path)
            self.assertEqual(result["schema"], B.SCHEMA)
            with self.assertRaisesRegex(ValueError, "final\\[0\\]"):
                B.execute("check", path)

    def test_existing_output_and_invalid_mode_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "output"
            output.mkdir()
            sentinel = output / "sentinel"
            sentinel.write_bytes(b"preserve me")
            with self.assertRaisesRegex(ValueError, "output already exists"):
                B.execute("export", WORD, output)
            self.assertEqual(sentinel.read_bytes(), b"preserve me")
            for mode, destination in (("unknown", None), ("check", output), ("export", None)):
                with self.assertRaises(ValueError):
                    B.execute(mode, WORD, destination)

    def test_compressed_size_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "large.gz"
            path.write_bytes(gzip.compress(b"x" * (B.MAX_BYTES + 1), mtime=0))
            with self.assertRaisesRegex(ValueError, "exceeds 5 MiB"):
                B.read_bounded(path, compressed=True)


if __name__ == "__main__":
    unittest.main()
