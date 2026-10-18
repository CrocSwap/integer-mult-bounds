"""Package portability and concrete circuit/source/receipt corruption controls.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


def load(name):
    spec = importlib.util.spec_from_file_location("ck_test_" + name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PackageTests(unittest.TestCase):
    def test_actual_gain_run_mutants(self):
        primary, independent, compiler = load("verify"), load("check_independent"), load("compile")
        primary.source_check()
        lower = primary.module("ck_test_baseline", ROOT / primary.INPUTS[0]).lower
        programs = primary.read(ROOT / primary.INPUTS[1])
        rejected = 0
        for events in programs.values():
            for _, _, _, word in independent.split_events(events, lower):
                candidate = compiler.optimize_run(word)
                if len(candidate) >= len(word):
                    continue
                independent.compare(word, candidate)
                self.assertEqual(candidate[-1][0], "negate")
                with self.assertRaises(ValueError):
                    independent.compare(word, candidate[:-1])
                rejected += 1
                changed = list(candidate)
                index = next(i for i, p in enumerate(changed) if p[0] in ("add", "subtract"))
                old = changed[index]
                changed[index] = ("add" if old[0] == "subtract" else "subtract", *old[1:])
                with self.assertRaises(ValueError):
                    independent.compare(word, changed)
                rejected += 1
        self.assertEqual(rejected, 56)

    def test_copy_fanout_is_not_claimed_free(self):
        checker, compiler = load("check_independent"), load("compile")
        a, b, c = ("A", 0), ("B", 0), ("C", 0)
        word = [("negate", a), ("copy", b, a), ("copy", c, a)]
        candidate = compiler.optimize_run(word)
        checker.compare(word, candidate, 5)
        self.assertEqual(len(candidate) - len(word), 2)

    def test_minimal_relocation_recompression_and_corruption(self):
        primary = load("verify")
        with tempfile.TemporaryDirectory(prefix="ck sign minimal ") as tmp:
            target = Path(tmp)
            for item in HERE.iterdir():
                if item.is_file():
                    destination = target / REL / item.name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(item, destination)
            for name in primary.INPUTS:
                destination = target / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            program = target / primary.INPUTS[1]
            program.write_bytes(gzip.compress(gzip.decompress(program.read_bytes()), compresslevel=1, mtime=1234))
            def run():
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(target / REL / "check.py")],
                                      cwd=target, text=True, capture_output=True, timeout=120)
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_CK_SIGN_PACKAGE", result.stdout)
            source = target / primary.INPUTS[0]
            original = source.read_bytes()
            source.write_bytes(original + b"\n# deliberate source corruption\n")
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source pin:", result.stderr)
            source.write_bytes(original)
            receipt = target / REL / "EXPECTED.json"
            data = json.loads(receipt.read_text())
            data["programs"]["forward"]["real_saved"] += 2
            receipt.write_text(json.dumps(data))
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("primary receipt differs", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
