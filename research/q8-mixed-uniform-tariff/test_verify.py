"""Cold-export, scientific mutation, and fail-closed receipt controls."""
from pathlib import Path
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class Controls(unittest.TestCase):
    def test_faithful_replay_rejects_real_word_faults(self):
        primary = module("primary_test", HERE / "verify.py")
        independent = module("regular_test", HERE / "independent.py")
        fixture = {"targets": [4, 4, 1, 0], "prices": [2, 3],
                   "word": primary.direct([4, 4, 1, 0], (2, 3)), "attaining": True}
        self.assertEqual(independent.check([fixture])["fixtures"], 1)
        omitted = copy.deepcopy(fixture)
        omitted["word"].pop(0)
        with self.assertRaisesRegex(ValueError, "endpoint"):
            independent.check([omitted])
        leaked = {"targets": [1, 0], "prices": [1, 1], "word": [[1, 3, 1]], "attaining": True}
        with self.assertRaisesRegex(ValueError, "endpoint"):
            independent.check([leaked])
        wrong_label = copy.deepcopy(fixture)
        wrong_label["word"][-1][0] = 2
        with self.assertRaisesRegex(ValueError, "endpoint"):
            independent.check([wrong_label])
        expensive = copy.deepcopy(fixture)
        for factor in expensive["word"][:-1]:
            factor[0] = 2
        # Endpoint remains correct; the claimed weighted optimum is false.
        with self.assertRaisesRegex(ValueError, "tariff"):
            independent.check([expensive])

    def test_git_free_export_and_source_binding(self):
        with tempfile.TemporaryDirectory(prefix="q8-tariff-") as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package)
            manifest = json.loads((HERE / "SOURCES.json").read_bytes())
            for source in manifest["files"]:
                if source["usage"] == "input":
                    target = root / source["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / source["path"], target)
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            def run():
                return subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=60)
            positive = run()
            self.assertEqual(positive.returncode, 0, positive.stderr)
            self.assertFalse((root / ".git").exists())
            source = package / "inputs/pr2248-README.md"
            old = source.read_bytes()
            source.write_bytes(old + b"\nchanged predecessor\n")
            negative = run()
            self.assertNotEqual(negative.returncode, 0)
            self.assertIn("predecessor source drift", negative.stderr)
            source.write_bytes(old)
            source.unlink()
            self.assertNotEqual(run().returncode, 0)

    def test_complete_fixture_and_typed_receipt_rejection(self):
        primary = module("primary_controls", HERE / "verify.py")
        with tempfile.TemporaryDirectory(prefix="q8-receipt-") as directory:
            package = Path(directory)
            shutil.copytree(HERE, package, dirs_exist_ok=True)
            primary.HERE = package
            fixtures = json.loads((package / "FIXTURES.json").read_bytes())
            fixtures.pop()
            (package / "FIXTURES.json").write_bytes(primary.canonical(fixtures))
            with self.assertRaisesRegex(ValueError, "complete fixture regeneration"):
                primary.run()
            shutil.copyfile(HERE / "FIXTURES.json", package / "FIXTURES.json")
            receipt = json.loads((package / "RESULT.json").read_bytes())
            receipt["fixtures"] = float(receipt["fixtures"])
            self.assertNotEqual(primary.canonical(receipt), primary.canonical(primary.run()))
            occupied = package / "occupied.json"
            occupied.write_text("preserve", encoding="utf-8")
            out = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                  "--out", str(occupied)], capture_output=True, text=True, timeout=60)
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("output already exists", out.stderr)
            self.assertEqual(occupied.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main(verbosity=2)
