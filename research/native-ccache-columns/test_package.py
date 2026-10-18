"""Actual-input and receipt failure controls; no native execution is implied.

Gareth Davidson with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as v
import benchmark as b


def clone(temporary):
    root = Path(temporary) / "repo"
    package = root / "research" / HERE.name
    shutil.copytree(HERE, package, copy_function=shutil.copyfile)
    for row in v.source_pins():
        dst = root / row["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(v.ROOT / row["path"], dst)
    for item in root.rglob("*"):
        if item.is_dir():
            item.chmod(0o755)
    return root, package


class Controls(unittest.TestCase):
    def test_source_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, package = clone(temporary)
            for row in v.source_pins(root, package):
                with self.subTest(source=row["path"]):
                    p = root / row["path"]
                    old = p.read_bytes()
                    p.write_bytes(old + b"\n")
                    with self.assertRaisesRegex(ValueError, "source hash"):
                        v.source_pins(root, package)
                    p.write_bytes(old)

    def test_fixture_bytes_and_payload_binding(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package = clone(temporary)
            meta = v.read(package / "FIXTURES.json")
            for label, row in meta["inputs"].items():
                with self.subTest(fixture=label):
                    p = package / row["path"]
                    old = p.read_bytes()
                    p.write_bytes(old + b"changed")
                    with self.assertRaisesRegex(ValueError, "immutable fixture container"):
                        v.fixtures(package)
                    p.write_bytes(old)
            meta["inputs"]["baseline"]["payload_sha256"] = "0" * 64
            (package / "FIXTURES.json").write_text(json.dumps(meta))
            with self.assertRaisesRegex(ValueError, "fixture payload"):
                v.fixtures(package)

    def test_missing_undo_is_a_mathematical_failure(self):
        with self.assertRaisesRegex(ValueError, "local defining full column"):
            v.independent(v.fixtures()["missing-undo"])

    def test_location_must_bind_before_normalization(self):
        raw = v.fixtures()["baseline"]
        expected = v.read(HERE / "NATIVE.json")["baseline"]
        receipt = dict(expected, local_scalar_stream="/expected/input.bin", seconds=0.1)
        self.assertEqual(v.normalize(receipt, Path("/expected/input.bin"), raw), expected)
        with self.assertRaisesRegex(ValueError, "native input path binding"):
            v.normalize(receipt, Path("/different/input.bin"), raw)
        wrong = raw[:-1] + bytes([raw[-1] ^ 1])
        self.assertNotEqual(v.canonical(v.normalize(receipt, Path("/expected/input.bin"), wrong)),
                            v.canonical(expected))

    def test_only_elapsed_and_bound_location_normalize(self):
        raw = v.fixtures()["baseline"]
        expected = v.read(HERE / "NATIVE.json")["baseline"]
        receipt = dict(expected, local_scalar_stream="/input.bin", seconds=1.0)
        bad = []
        r = copy.deepcopy(receipt); r["stages"][1]["signed_inverse"] = 1; bad.append(r)
        r = copy.deepcopy(receipt); r["negative_controls"].pop(); bad.append(r)
        r = copy.deepcopy(receipt); r["local_raw_H"][0][1] += 1; bad.append(r)
        r = copy.deepcopy(receipt); r["payload_prefix_upper"] = "1"; bad.append(r)
        r = copy.deepcopy(receipt); del r["scope"]; bad.append(r)
        r = copy.deepcopy(receipt); r["bridge_additions"] -= 1; bad.append(r)
        for r in bad:
            self.assertNotEqual(v.canonical(v.normalize(r, Path("/input.bin"), raw)), v.canonical(expected))
        for elapsed in (None, True, float("nan"), -1):
            with self.subTest(elapsed=elapsed), self.assertRaisesRegex(ValueError, "native elapsed field"):
                v.normalize(dict(receipt, seconds=elapsed), Path("/input.bin"), raw)

    def test_strict_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary) / "bad.json"
            for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
                p.write_text(text)
                with self.assertRaises(ValueError):
                    v.read(p)

    def test_inherited_cache_policy_is_removed(self):
        with patch.dict(os.environ, {"CCACHE_SLOPPINESS": "time_macros,system_headers",
                                     "CCACHE_COMPILERCHECK": "none", "CCACHE_REMOTE_STORAGE": "unused",
                                     "CCACHE_DIR": "/outside", "CCACHE_DISABLE": "1"}):
            env = b.clean_environment()
        self.assertFalse(any(key.startswith("CCACHE_") for key in env))
        self.assertEqual(env["LC_ALL"], "C")
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            cenv = b.cache_environment(work, env)
            self.assertEqual(cenv["CCACHE_DIR"], str(work / "cache"))
            self.assertEqual(cenv["CCACHE_CONFIGPATH"], str(work / "ccache.conf"))
            config = (work / "ccache.conf").read_text()
            self.assertIn("compiler_check = content\n", config)
            self.assertIn("direct_mode = false\n", config)
            self.assertIn("sloppiness =\n", config)
            self.assertIn("remote_storage =\n", config)

    def test_corrupted_receipt_actual_entry_point(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, package = clone(temporary)
            p = package / "NATIVE.json"
            data = v.read(p)
            data["deferred"]["local_scalar_additions"] -= 1
            p.write_text(json.dumps(data))
            r = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                               cwd=temporary, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("independent native field: local_scalar_additions", r.stderr)

    def test_existing_work_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary) / "keep"
            p.write_bytes(b"preserve evidence\n")
            r = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "benchmark.py"),
                                "--work", temporary, "--cxx", "/missing", "--ccache", "/missing"],
                               capture_output=True, text=True, timeout=30)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("fresh external work directory required", r.stderr)
            self.assertEqual(p.read_bytes(), b"preserve evidence\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
