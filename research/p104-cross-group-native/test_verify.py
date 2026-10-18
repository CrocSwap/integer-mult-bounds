"""Behavioral tests adapted from ywz65 / PR2572, Apache-2.0.
Additional cross-group source and physical-boundary controls for commdata2338,
with substantial OpenAI Codex assistance.
"""
from pathlib import Path
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("cross_group_test_check", Path(__file__).with_name("verify.py"))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class BindingTests(unittest.TestCase):
    def command(self, root, script, *args, expected=None):
        package = root / "research/p104-cross-group-native"
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script), *map(str, args)],
                                cwd=root, text=True, encoding="utf-8", capture_output=True, timeout=300)
        text = result.stdout + result.stderr
        if expected is None:
            self.assertEqual(result.returncode, 0, text)
        else:
            self.assertNotEqual(result.returncode, 0, text)
            self.assertIn(expected, text)
        return text

    def test_complete_regeneration(self):
        with tempfile.TemporaryDirectory(prefix="cross-group-regenerate-") as tmp:
            output = Path(tmp) / "NATIVE.json.gz"
            self.command(check.ROOT, "build.py", "--out", output)
            self.assertEqual(check.canonical(check.load(output, True)), check.canonical(check.load(check.HERE / "NATIVE.json.gz", True)))
            self.command(check.ROOT, "build.py", "--out", output, expected="output already exists")

    def test_equivalent_frame_bases(self):
        original, correction = check.authenticate()
        oracle = check.module(check.NATIVE / "vendor/native_verify.py", "equivalent_oracle")
        convert, ports, _ = check.geometry(oracle)
        expected = check.assemble(original, correction, convert)
        altered = copy.deepcopy(correction)
        def change(frame):
            result = list(reversed(frame))
            if len(result) > 1:
                result[0] ^= result[1]
            return result
        for boundary in ("initial_frames", "final_frames"):
            altered[boundary] = {r: change(f) for r, f in altered[boundary].items()}
        for part in altered["insertions"]:
            for event in part["events"]:
                if event[0] == "transport":
                    event[2], event[3] = change(event[2]), change(event[3])
                else:
                    event[-1] = change(event[-1])
        actual = check.assemble(original, altered, convert)
        self.assertEqual(check.canonical(actual), check.canonical(expected))
        self.assertEqual(check.replay(actual, ports)["added_rank_mass"], 810)

    def test_git_free_export_and_evidence_controls(self):
        with tempfile.TemporaryDirectory(prefix="cross-group-export-") as tmp:
            root = Path(tmp)
            package = root / "research/p104-cross-group-native"
            shutil.copytree(check.HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for name in check.REQUIRED_INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(check.ROOT / name, target)
            def inventory():
                return {p.relative_to(root).as_posix(): check.digest(p.read_bytes()) for p in root.rglob("*") if p.is_file()}
            before = inventory()
            for path in root.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
            self.assertIn("PASS_P104_CROSS_GROUP_NATIVE", self.command(root, "verify.py"))
            self.assertEqual(before, inventory())
            for path in root.rglob("*"):
                if path.is_file():
                    path.chmod(0o666)
            result = package / "RESULT.json"
            self.command(root, "verify.py", "--out", result, expected="output already exists")
            oracle = root / "research/p104-native-channel/vendor/native_verify.py"
            old = oracle.read_bytes()
            oracle.write_text("raise RuntimeError('EXECUTED_DRIFTED_ORACLE')\n", encoding="utf-8")
            text = self.command(root, "verify.py", expected="external source drift")
            self.assertNotIn("EXECUTED_DRIFTED_ORACLE", text)
            oracle.write_bytes(old)
            source = package / "inputs/PR2521-CIRCUIT.json"
            old = source.read_bytes()
            source.write_bytes(old + b" ")
            self.command(root, "verify.py", expected="retained source drift")
            source.write_bytes(old)
            native = package / "NATIVE.json.gz"
            saved = native.read_bytes()
            native.unlink()
            self.command(root, "verify.py", expected="FileNotFoundError")
            native.write_bytes(saved)
            manifest = package / "SOURCES.json"
            saved_manifest = manifest.read_bytes()
            changed = json.loads(saved_manifest)
            changed["files"] = [r for r in changed["files"] if r.get("path") != "research/p104-native-channel/vendor/native_verify.py"]
            manifest.write_text(json.dumps(changed), encoding="utf-8")
            self.command(root, "verify.py", expected="required external source set")
            manifest.write_bytes(saved_manifest)
            receipt = json.loads(result.read_bytes())
            # Python considers 146 == 146.0; the typed JSON receipt must not.
            receipt["added_profile"]["1"] = float(receipt["added_profile"]["1"])
            result.write_text(json.dumps(receipt), encoding="utf-8")
            self.command(root, "verify.py", expected="complete receipt mismatch")


if __name__ == "__main__":
    unittest.main()
