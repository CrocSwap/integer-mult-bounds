#!/usr/bin/env python3
"""Public-CLI source-export, corruption, and output-safety checks."""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PACKAGE = "research/p104-no-relay-cover-audit"


def hashes(root):
    return {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


@contextmanager
def export():
    with tempfile.TemporaryDirectory(prefix="p104-cover-") as tmp:
        root = Path(tmp)
        shutil.copytree(HERE, root / PACKAGE, ignore=shutil.ignore_patterns("__pycache__"))
        manifest = json.loads((HERE / "VERIFY.json").read_text())
        for name in manifest["inputs"]:
            dst = root / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dst)
        try:
            yield root
        finally:
            for p in root.rglob("*"):
                p.chmod(0o755 if p.is_dir() else 0o644)
            root.chmod(0o755)


def run(root, script, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B",
                           str(root / PACKAGE / script), *args],
                          cwd=root, text=True, capture_output=True, timeout=120)


class ReplayTests(unittest.TestCase):
    def test_readonly_git_free_export(self):
        with export() as root:
            before = hashes(root)
            for p in root.rglob("*"):
                p.chmod(0o555 if p.is_dir() else 0o444)
            root.chmod(0o555)
            for script in ("verify.py", "independent.py"):
                result = run(root, script)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(hashes(root), before)

    def test_source_corruption_rejected(self):
        with export() as root:
            path = root / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
            path.write_bytes(path.read_bytes() + b" ")
            for script, message in (("verify.py", "source drift"),
                                    ("independent.py", "word source pin")):
                result = run(root, script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stdout + result.stderr)

    def test_certificate_corruption_rejected(self):
        with export() as root:
            path = root / PACKAGE / "CERTIFICATE.json"
            data = json.loads(path.read_text())
            data["extra_packing"].append(data["extra_packing"][0])
            path.write_text(json.dumps(data))
            for script, message in (("verify.py", "duplicate pair"),
                                    ("independent.py", "dual duplicate")):
                result = run(root, script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stdout + result.stderr)

    def test_result_corruption_rejected(self):
        with export() as root:
            path = root / PACKAGE / "RESULT.json"
            data = json.loads(path.read_text())
            data["primal_dual"]["exact_cover_minimum"] -= 1
            path.write_text(json.dumps(data))
            result = run(root, "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("result drift", result.stdout + result.stderr)

    def test_generator_and_exclusive_output(self):
        with export() as root:
            output = root / "generated.json"
            result = run(root, "generate.py", "--out", str(output))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(output.read_bytes(), (HERE / "CERTIFICATE.json").read_bytes())
            before = output.read_bytes()
            result = run(root, "verify.py", "--out", str(output))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("File exists", result.stdout + result.stderr)
            self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
