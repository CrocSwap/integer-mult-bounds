#!/usr/bin/env python3
"""Source-corruption and optimized-entry-point controls, standard library only."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("coordinate_decoder", PACKAGE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class EntryPointControls(unittest.TestCase):
    def test_source_corruption(self):
        original_read = Path.read_bytes
        for relative in verify.PINS:
            with self.subTest(source=relative):
                target = verify.ROOT / relative
                data = bytearray(original_read(target))
                data[len(data) // 2] ^= 1
                damaged = bytes(data)

                def read_corrupted(path):
                    return damaged if path == target else original_read(path)

                with patch.object(Path, "read_bytes", read_corrupted):
                    with self.assertRaisesRegex(ValueError, "source hash mismatch: " + re.escape(relative)):
                        verify.load_sources()

    def test_optimized_replay(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in PACKAGE.iterdir() if p.is_file()}
        replay = subprocess.run([sys.executable, "-I", "-O", "-B", str(PACKAGE / "verify.py")],
                                capture_output=True, text=True, timeout=600, check=True)
        summary = json.loads(replay.stdout)
        self.assertEqual(summary["status"], "PASS_QQ16_COORDINATE_CUT_DECODER")
        self.assertEqual(summary["replayed_cases"], {"port_basis_placements": 224, "dense_signed_dyadic": 1})
        self.assertEqual(summary["controls_rejected"], 5)
        self.assertEqual(summary["result_sha256"], before["RESULT.json"])
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in PACKAGE.iterdir() if p.is_file()}
        self.assertEqual(before, after, "normal replay must not mutate package files")
        print(json.dumps({"optimized_replay": summary}), flush=True)


if __name__ == "__main__":
    unittest.main()
