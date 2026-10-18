"""Publication controls for missing/corrupted evidence and relocatability.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)


class PackageControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="source census package ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "relocated repository"
        self.package = self.root / PACKAGE
        self.package.mkdir(parents=True)
        for name in ("check.py", "enumerate.py", "CERTIFICATE.json", "SOURCES.json"):
            shutil.copyfile(HERE/name, self.package/name)
        for name in json.loads((HERE/"SOURCES.json").read_text())["runtime_inputs"]:
            dest = self.root/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, dest)

    def run_script(self, script="check.py", *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package/script), *map(str, args)],
                              cwd=self.temp.name, text=True, capture_output=True, timeout=60)

    def test_minimal_relocated_optimized_replay(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn("PASS_SOURCE_SUBSTITUTION_INDEPENDENT", result.stdout)
        result = self.run_script("enumerate.py")
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_source_corruption_fails_before_replay(self):
        pins = json.loads((self.package/"SOURCES.json").read_text())["runtime_inputs"]
        source = self.root/next(name for name in pins if name.endswith(".gz"))
        source.write_bytes(source.read_bytes()+b"changed")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source pin", result.stderr)

    def test_replaced_separator_is_rejected_mathematically(self):
        path = self.package/"CERTIFICATE.json"
        value = json.loads(path.read_text())
        row = next(x for x in value["helpers"] if x["status"] == "frame_obstruction")
        row["obstruction"]["normal"] = [0]*8
        path.write_text(json.dumps(value))
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nonseparating normal", result.stderr)

    def test_duplicate_json_key_rejected(self):
        path = self.package/"CERTIFICATE.json"
        path.write_text('{"schema":"forged",'+path.read_text()[1:])
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate JSON key", result.stderr)

    def test_generation_preserves_existing_output(self):
        path = self.root/"reserved.json"
        content = b"existing review evidence\n"
        path.write_bytes(content)
        result = self.run_script("enumerate.py", "--output", path)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
