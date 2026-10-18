#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with OpenAI Codex.
"""Controls for fresh reads, independent return values, and replay boundaries."""

import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from verify import JsonReader, authenticate


class JsonReaderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def test_plain_and_gzip_json_types_and_warm_hits(self):
        values = [None, False, 10**80, 1.25, "λ", [], {"rows": [True, None]}]
        reader = JsonReader()
        for suffix in (".json", ".json.gz"):
            for index, expected in enumerate(values):
                with self.subTest(suffix=suffix, value=expected):
                    path = self.directory / f"value-{index}{suffix}"
                    raw = json.dumps(expected).encode()
                    path.write_bytes(gzip.compress(raw) if suffix.endswith(".gz") else raw)
                    for _ in range(2):
                        actual = reader(path)
                        self.assertEqual(actual, expected)
                        self.assertIs(type(actual), type(expected))
        self.assertEqual(reader.misses, 2 * len(values))
        self.assertEqual(reader.hits, 2 * len(values))

    def test_same_size_same_mtime_replacement_and_restoration(self):
        for suffix in (".json", ".json.gz"):
            with self.subTest(suffix=suffix):
                reader = JsonReader()
                path = self.directory / f"changing{suffix}"
                original, changed = b'{"rows":[1]}', b'{"rows":[2]}'
                if suffix.endswith(".gz"):
                    original = gzip.compress(original, mtime=0)
                    changed = gzip.compress(changed, mtime=0)
                self.assertEqual(len(original), len(changed))
                path.write_bytes(original)
                before = path.stat()
                self.assertEqual(reader(path), {"rows": [1]})
                for raw, expected in ((changed, 2), (original, 1)):
                    path.write_bytes(raw)
                    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                    self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
                    self.assertEqual(reader(path), {"rows": [expected]})
                self.assertEqual(reader.misses, 2)
                self.assertEqual(reader.hits, 1)
                self.assertEqual(len(reader.cache), 1)
                self.assertEqual(reader(path), {"rows": [1]})
                self.assertEqual(reader.hits, 2)

    def test_changed_content_is_fresh_and_original_remains_cached(self):
        for suffix in (".json", ".json.gz"):
            with self.subTest(suffix=suffix):
                reader = JsonReader()
                path = self.directory / f"alternating{suffix}"
                original = b'{"rows":[{"values":[1]}]}'
                changed = b'{"rows":[{"values":[2]}]}'
                if suffix.endswith(".gz"):
                    original = gzip.compress(original, mtime=0)
                    changed = gzip.compress(changed, mtime=0)
                path.write_bytes(original)
                self.assertEqual(reader(path), {"rows": [{"values": [1]}]})
                path.write_bytes(changed)
                first_changed = reader(path)
                self.assertEqual(first_changed, {"rows": [{"values": [2]}]})
                first_changed["rows"][0]["values"].append(99)
                self.assertEqual(reader(path), {"rows": [{"values": [2]}]})
                path.write_bytes(original)
                self.assertEqual(reader(path), {"rows": [{"values": [1]}]})
                self.assertEqual(reader.misses, 3)
                self.assertEqual(reader.hits, 1)
                self.assertEqual(len(reader.cache), 1)

    def test_cold_and_warm_returns_have_independent_nested_values(self):
        for suffix in (".json", ".json.gz"):
            with self.subTest(suffix=suffix):
                reader = JsonReader()
                path = self.directory / f"mutable{suffix}"
                expected = {"rows": [{"values": [1]}]}
                raw = json.dumps(expected).encode()
                path.write_bytes(gzip.compress(raw) if suffix.endswith(".gz") else raw)
                for _ in range(3):
                    actual = reader(path)
                    self.assertEqual(actual, expected)
                    actual["rows"][0]["values"].append(99)
                    actual["rows"].append({"extra": True})
                    actual["added"] = "caller-owned"
                self.assertEqual(reader.misses, 1)
                self.assertEqual(reader.hits, 2)

    def test_malformed_content_after_warming_is_rejected(self):
        plain = b'{"value":1}'
        compressed = gzip.compress(plain, mtime=0)
        cases = [
            ("bad.json", plain, b"{", json.JSONDecodeError),
            ("bad-json.json.gz", compressed, gzip.compress(b"{"), json.JSONDecodeError),
            ("bad-gzip.json.gz", compressed, b"not gzip", gzip.BadGzipFile),
            ("truncated.json.gz", compressed, compressed[:-4], EOFError),
        ]
        for name, original, invalid, error in cases:
            with self.subTest(name=name):
                reader = JsonReader()
                path = self.directory / name
                path.write_bytes(original)
                self.assertEqual(reader(path), {"value": 1})
                self.assertEqual(reader(path), {"value": 1})
                path.write_bytes(invalid)
                for _ in range(2):
                    with self.assertRaises(error):
                        reader(path)
                path.write_bytes(original)
                self.assertEqual(reader(path), {"value": 1})

    def test_missing_warmed_path_is_rejected(self):
        reader = JsonReader()
        path = self.directory / "removed.json"
        path.write_bytes(b"[]")
        self.assertEqual(reader(path), [])
        self.assertEqual(reader(path), [])
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            reader(path)

    def test_paths_have_separate_entries(self):
        reader = JsonReader()
        first, second = self.directory / "first.json", self.directory / "second.json"
        first.write_bytes(b"[1]")
        second.write_bytes(b"[1]")
        self.assertEqual(reader(first), [1])
        self.assertEqual(reader(second), [1])
        second.write_bytes(b"[2]")
        self.assertEqual(reader(second), [2])
        self.assertEqual(reader(first), [1])
        self.assertEqual(len(reader.cache), 2)
        self.assertEqual(reader.misses, 3)
        self.assertEqual(reader.hits, 1)

    def test_suffix_controls_gzip_decoding(self):
        reader = JsonReader()
        plain = self.directory / "plain.json"
        compressed = self.directory / "compressed.json.gz"
        plain.write_bytes(b"[1]")
        compressed.write_bytes(b"[1]")
        self.assertEqual(reader(plain), [1])
        with self.assertRaises(gzip.BadGzipFile):
            reader(compressed)
        plain.write_bytes(gzip.compress(b"[1]"))
        with self.assertRaises(UnicodeDecodeError):
            reader(plain)

    def test_authenticate_rejects_changed_pinned_input(self):
        sources = json.loads(Path(__file__).with_name("SOURCES.json").read_bytes())
        pin = next(pin for pin in sources["files"] if pin["usage"] == "input")
        changed = self.directory / pin["path"]
        changed.parent.mkdir(parents=True)
        changed.write_bytes(b"changed input\n")
        with self.assertRaises(ValueError) as error:
            authenticate(root=self.directory)
        self.assertEqual(str(error.exception), "Input changed: " + pin["path"])

    def test_optimized_python_is_rejected(self):
        result = subprocess.run(
            [sys.executable, "-O", "-B", str(Path(__file__).resolve().with_name("verify.py"))],
            cwd=self.directory, capture_output=True, text=True, timeout=5,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Assertions must remain enabled", result.stderr)


if __name__ == "__main__":
    unittest.main()
