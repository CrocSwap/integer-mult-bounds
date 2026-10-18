#!/usr/bin/env python3
"""Package admission controls, separate from the circuit's mathematical controls."""
import copy
import gzip
import json
from pathlib import Path
import runpy
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))
C = V["C"]


class PackageTests(unittest.TestCase):
    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"a": 1, "a": 2}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                C["load"](path)

    def test_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"a": NaN}')
            with self.assertRaisesRegex(ValueError, "invalid JSON constant"):
                C["load"](path)

    def test_source_mutation(self):
        manifest = C["load"](HERE / "SOURCES.json")
        first = next(iter(manifest["files"]))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / first
            path.parent.mkdir(parents=True)
            path.write_bytes(b"changed source")
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                C["pins"](tmp)

    def test_recompression_preserves_payload(self):
        original = C["load"](HERE / "candidate.json.gz")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "recompressed.json.gz"
            path.write_bytes(gzip.compress(json.dumps(original, indent=1).encode(), compresslevel=1, mtime=12345))
            self.assertEqual(C["digest"](C["load"](path)), C["digest"](original))

    def test_frozen_context_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for name in ("common.py", "SOURCES.json"):
                (folder / name).write_bytes((HERE / name).read_bytes())
            (folder / "BASE-SELECTION.json").write_bytes(b"changed historical context")
            local = runpy.run_path(str(folder / "common.py"))
            with self.assertRaisesRegex(ValueError, "context hash mismatch"):
                local["pins"](C["ROOT"])

    def test_existing_output_preserved(self):
        build = runpy.run_path(str(HERE / "build.py"))
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "marker"
            marker.write_text("keep")
            with self.assertRaises(FileExistsError):
                build["run"](C["ROOT"], tmp)
            self.assertEqual(marker.read_text(), "keep")

    def test_certificate_price_mutation(self):
        word = C["load"](HERE / "candidate.json.gz")
        cert = C["load"](HERE / "CERTIFICATE.json")
        expected = {key: cert[key] for key in V["bill"](word)}
        expected["native_ADDs"] -= 221
        with self.assertRaisesRegex(ValueError, "mutated invoice"):
            V["same"](V["bill"](word), expected, "mutated invoice")

    def test_dirty_helper_mutation(self):
        word = C["load"](HERE / "candidate.json.gz")
        changed = copy.deepcopy(word)
        changed["D"][0][2][0] = changed["D"][1][2][0]
        self.assertNotEqual(V["d_rows"](word), V["d_rows"](changed))


if __name__ == "__main__":
    unittest.main()
