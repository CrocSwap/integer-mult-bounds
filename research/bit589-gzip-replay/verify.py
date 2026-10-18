#!/usr/bin/env python3
"""Full-payload and frozen-shell controls; no full supplier replay.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay

WORDS = (
    "research/e8-bit-p111-tuned/data/bitE8mut-p111.json.gz",
    "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
)


class PayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        replay.check_sources()

    def test_original_words(self):
        for name in WORDS:
            path = replay.ROOT / name
            self.assertEqual(replay.compare_payloads(path, path),
                             hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest())
            for flags in ([], ["-O"]):
                p = subprocess.run([sys.executable, "-I", "-B", *flags,
                                    str(replay.HERE / "replay.py"), "--compare", str(path), str(path)],
                                   capture_output=True)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertIn(b"PASS_GZIP_PAYLOAD", p.stdout)

    def test_representations_rejected_by_cmp_pass_both_adapted_shell_sites(self):
        # Actual shell commands, filenames and $PYTHON invocation. Also exercise
        # a helper path containing spaces and a single quote.
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            helper = directory / "helper path 'quoted.py"
            helper.write_bytes((replay.HERE / "replay.py").read_bytes())
            script = '\n'.join(replay.COMPARISONS) + '\nprintf "%s\\n" "' + replay.OLD_MESSAGE + '"\n'
            adapted = replay.adapted_script(script, helper)
            for index, name in enumerate(WORDS):
                reference = replay.ROOT / name
                raw = reference.read_bytes()
                data = gzip.decompress(raw)
                half = len(data) // 2
                variants = {
                    "timestamp": raw[:4] + (123456789).to_bytes(4, "little") + raw[8:],
                    "level1": gzip.compress(data, compresslevel=1, mtime=0),
                    "stored": gzip.compress(data, compresslevel=0, mtime=0),
                    "members": gzip.compress(data[:half], mtime=1) + gzip.compress(data[half:], mtime=2),
                }
                for label, value in variants.items():
                    with self.subTest(word=name, representation=label):
                        self.assertNotEqual(value, raw)
                        self.assertEqual(gzip.decompress(value), data)
                        candidate = directory / ("base.json.gz" if index == 0 else "tuned.json.gz")
                        candidate.write_bytes(value)
                        other = directory / ("tuned.json.gz" if index == 0 else "base.json.gz")
                        other.write_bytes((replay.ROOT / WORDS[1-index]).read_bytes())
                        env = dict(os.environ, WD=str(directory), BASE=str(replay.ROOT / WORDS[0]),
                                   WORD=str(replay.ROOT / WORDS[1]), PYTHON=sys.executable)
                        old = subprocess.run(["bash", "-ec", script], env=env, capture_output=True)
                        new = subprocess.run(["bash", "-ec", adapted], env=env, capture_output=True)
                        self.assertEqual(old.returncode, 1, old.stderr)
                        self.assertEqual(new.returncode, 0, new.stderr)
                        self.assertIn(replay.NEW_MESSAGE.encode(), new.stdout)

    def test_payload_changes_and_corruption_fail_normal_and_optimized_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "candidate.gz"
            for name in WORDS:
                reference = replay.ROOT / name
                raw = reference.read_bytes()
                data = gzip.decompress(raw)
                word = json.loads(data)
                # Change a mathematical gate source without changing gate counts.
                word["A"][0][2][0] = (word["A"][0][2][0] + 1) % word["v"]
                crc = bytearray(raw)
                crc[-8] ^= 1
                cases = {
                    "gate": gzip.compress(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()),
                    "whitespace": gzip.compress(data + b"\n"),
                    "unknown_field": gzip.compress(data[:-1] + b',"unreviewed":true}'),
                    "crc": bytes(crc),
                    "truncated": raw[:-3],
                    "trailing_member": raw + gzip.compress(b"extra"),
                }
                for label, value in cases.items():
                    candidate.write_bytes(value)
                    for optimized in (False, True):
                        with self.subTest(word=name, mutation=label, optimized=optimized):
                            argv = [sys.executable, "-I", "-B"] + (["-O"] if optimized else [])
                            result = subprocess.run([*argv, str(replay.HERE / "replay.py"), "--compare",
                                                     str(candidate), str(reference)], capture_output=True)
                            self.assertNotEqual(result.returncode, 0)
                            self.assertNotIn(b"PASS_GZIP_PAYLOAD", result.stdout)

    def test_exact_shell_delta_and_fail_closed_anchors(self):
        source = (replay.ROOT / replay.SCRIPT).read_text(encoding="utf-8")
        adapted = replay.adapted_script(source)
        before, after = source.splitlines(), adapted.splitlines()
        self.assertEqual(len(before), len(after))
        differences = [(a, b) for a, b in zip(before, after) if a != b]
        self.assertEqual(len(differences), 3)
        self.assertEqual([a for a, _ in differences[:2]], list(replay.COMPARISONS))
        self.assertIn(replay.OLD_MESSAGE, differences[2][0])
        for old in (*replay.COMPARISONS, replay.OLD_MESSAGE):
            for changed in (source.replace(old, "changed"), source + "\n" + old + "\n"):
                with self.assertRaises(ValueError):
                    replay.adapted_script(changed)
        subprocess.run(["bash", "-n"], input=adapted.encode(), check=True)

    def test_source_drift_rejected(self):
        original = Path.read_bytes
        for target in (replay.SCRIPT, *WORDS, "research/e8-bit-p111-tuned/MANIFEST.sha256"):
            def changed(path):
                data = original(path)
                return data + b"drift" if path == replay.ROOT / target else data
            with patch.object(Path, "read_bytes", changed):
                with self.assertRaisesRegex(ValueError, "source drift"):
                    replay.check_sources()


if __name__ == "__main__":
    unittest.main(verbosity=2)
