"""Fault controls for source binding, receipts and explicit kernel mode.

Adapted from our PR2341/2295 harness. These tests alone do not execute Lean.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify


def writable_copy(temporary):
    repo = Path(temporary) / "repo"
    root = repo / "research" / HERE.name
    shutil.copytree(HERE, root, copy_function=shutil.copyfile)
    for item in verify.read(HERE / "SOURCES.json")["files"]:
        if item["usage"] == "input":
            target = repo / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE.parents[1] / item["path"], target)
    for path in repo.rglob("*"):
        if path.is_dir():
            path.chmod(0o755)
    return root


class Controls(unittest.TestCase):
    def test_each_pinned_source(self):
        pins = verify.check_sources()
        with tempfile.TemporaryDirectory() as temporary:
            root = writable_copy(temporary)
            for name in pins["files"]:
                with self.subTest(source=name):
                    path = root / name
                    old = path.read_bytes()
                    path.write_bytes(old + b"\n")
                    with self.assertRaisesRegex(ValueError, "source bytes changed"):
                        verify.check_sources(root)
                    path.write_bytes(old)
            verify.check_sources(root)

    def test_proof_escape_after_rebound_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = writable_copy(temporary)
            path = root / "lean/RecordBridge.lean"
            old = path.read_text()
            pins = verify.read(root / "PROOF-SOURCES.json")
            for escape in ("axiom injected : False", "example : False := by sorry",
                           "example : False := by admit"):
                with self.subTest(escape=escape):
                    path.write_text(old + "\n" + escape + "\n")
                    pins["files"]["lean/RecordBridge.lean"] = hashlib.sha256(path.read_bytes()).hexdigest()
                    (root / "PROOF-SOURCES.json").write_text(json.dumps(pins))
                    with self.assertRaisesRegex(ValueError, "unapproved proof escape"):
                        verify.check_sources(root)

    def test_inventory_completeness(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = writable_copy(temporary)
            pins = verify.read(root / "PROOF-SOURCES.json")
            pins["files"].pop("lean/PhaseWords.lean")
            (root / "PROOF-SOURCES.json").write_text(json.dumps(pins))
            with self.assertRaisesRegex(ValueError, "incomplete proof source inventory"):
                verify.check_sources(root)

    def test_axiom_coverage_and_trust(self):
        targets = verify.check_sources()["axiom_targets"]
        lines = ["'" + name + "' depends on axioms: [propext, Classical.choice, Quot.sound]"
                 for name in targets]
        lines[-1] = "'" + targets[-1] + "' does not depend on any axioms"
        good = "\n".join(lines)
        self.assertEqual(set(verify.parse_axioms(good, targets)), set(targets))
        self.assertEqual(verify.parse_axioms(good, targets)[targets[-1]], [])
        for bad in ("\n".join(lines[:-1]), good + "\n" + lines[0],
                    good.replace("Quot.sound", "sorryAx", 1),
                    good.replace("Quot.sound", "untrustedAxiom", 1),
                    good + "\n'extra' does not depend on any axioms"):
            with self.subTest(report=bad[-80:]):
                with self.assertRaises(ValueError):
                    verify.parse_axioms(bad, targets)

    def test_strict_receipt_json(self):
        self.assertNotEqual(verify.encoded({"n": 1}), verify.encoded({"n": True}))
        self.assertNotEqual(verify.encoded({"n": 1}), verify.encoded({"n": 1.0}))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.json"
            for raw in ('{"n": 1, "n": 1}', '{"n": NaN}', '{"n": Infinity}'):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    verify.read(path)

    def test_receipt_drift_end_to_end(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = writable_copy(temporary)
            path = root / "FINITE.json"
            data = verify.read(path)
            data["phase_census"]["cases"] -= 1
            path.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(root / "verify.py")],
                                    cwd=temporary, capture_output=True, text=True, timeout=120)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("finite receipt differs", result.stderr)

    def test_historical_kernel_binding_end_to_end(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = writable_copy(temporary)
            path = root / "KERNEL.json"
            original = path.read_text()
            for change, expected in (("mode", "historical kernel receipt mode"),
                                     ("source", "historical proof source binding"),
                                     ("rejections", "historical rejection coverage")):
                with self.subTest(change=change):
                    data = json.loads(original)
                    if change == "mode":
                        data["kernel_checked"] = 1
                    elif change == "source":
                        data["proof_source_hashes"]["lean/RecordBridge.lean"] = "0" * 64
                    else:
                        data["rejected_invalid_proofs"].pop()
                    path.write_text(json.dumps(data))
                    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(root / "verify.py")],
                                            cwd=temporary, capture_output=True, text=True, timeout=120)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "keep.json"
            out.write_bytes(b"preserve evidence\n")
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                     "--out", str(out)], capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("output already exists", result.stderr)
            self.assertEqual(out.read_bytes(), b"preserve evidence\n")

    def test_kernel_requires_explicit_environment(self):
        for args in (["--lake", "/missing/lake"], ["--fetch-cache"],
                     ["--lake", "/missing/lake", "--work-dir", "/missing/work"]):
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"), *args],
                                    capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("PASS_", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
