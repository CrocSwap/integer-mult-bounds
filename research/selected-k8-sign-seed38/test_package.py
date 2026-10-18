"""Arithmetic, provenance, recompression and offline relocation controls.

Scratch-net with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
import gzip
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import tarfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


def load(name):
    spec = importlib.util.spec_from_file_location("selected_test_" + name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class PackageTests(unittest.TestCase):
    def test_reject_archived_ancestors(self):
        primary = load("verify")
        pins = primary.source_check()
        with tarfile.open(ROOT / primary.INPUTS[2], "r:gz") as archive:
            def word(name):
                return json.loads(gzip.decompress(archive.extractfile(name).read()))
            selected = word("slots/local/FULL-WORD.json.gz")
            primary.selected_word_check(selected, pins)
            # Canonical word identity accepts a different JSON/gzip representation.
            recoded = gzip.compress(json.dumps(selected, indent=3).encode(), compresslevel=1, mtime=1234)
            primary.selected_word_check(json.loads(gzip.decompress(recoded)), pins)
            for name in ("base/cold44/FULL-WORD.json.gz", "chain/frames/FULL-WORD.json.gz"):
                with self.subTest(member=name), self.assertRaisesRegex(ValueError, "selected word content differs"):
                    primary.selected_word_check(word(name), pins)

    def test_integer_arithmetic_against_fraction(self):
        integer, rational = load("independent"), load("verify")
        rng = random.Random(38)
        registers = [("L", i) for i in range(4)]
        # A bounded differential test of the arithmetic, not an all-input theorem.
        for _ in range(500):
            rows, oracle = {}, {}
            for reg in registers:
                nums = {col: rng.randint(-16, 16) for col in registers}
                nums = {col: n for col, n in nums.items() if n}
                depth = rng.randrange(28)
                rows[reg] = integer.normalize(nums, depth)
                oracle[reg] = {col: Fraction(n, 1 << depth) for col, n in nums.items()}
            for _ in range(20):
                kind = rng.choice(("copy", "clear", "negate", "double", "halve", "add", "subtract"))
                dst, src = rng.sample(registers, 2)
                instruction = (kind, dst, src) if kind in ("copy", "add", "subtract") else (kind, dst)
                integer.step(rows, instruction)
                rational.step(oracle, instruction)
                for reg in registers:
                    nums, depth = rows[reg]
                    self.assertEqual({col: Fraction(n, 1 << depth) for col, n in nums.items()}, oracle[reg])

    def test_actual_word_controls(self):
        result = load("controls").run(load("verify"), load("independent"))
        self.assertEqual(result["actual_run_mutants_rejected"], 116)
        self.assertEqual(result["toy_mutants_rejected"], 4)

    def test_minimal_optimized_relocation_and_mutations(self):
        primary = load("verify")
        with tempfile.TemporaryDirectory(prefix="selected k8 sign ") as tmp:
            target = Path(tmp)
            for item in HERE.iterdir():
                if item.is_file():
                    dst = target / REL / item.name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(item, dst)
            for name in primary.INPUTS:
                dst = target / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dst)

            def run(script="check.py"):
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(target / REL / script)],
                                      cwd=target, capture_output=True, text=True, timeout=180)

            good = run()
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("controls=120", good.stdout)
            source = target / primary.INPUTS[0]
            original = source.read_bytes()
            source.write_bytes(original + b"\n# deliberate pin mutation\n")
            bad = run()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source pin differs", bad.stderr)
            source.write_bytes(original)
            # A receipt cannot claim an extra saving, omit a boundary or omit an orientation.
            receipt = target / REL / "EXPECTED.json"
            original_receipt = receipt.read_text()
            for mutate in (
                lambda x: x["programs"]["forward"].__setitem__("real_saved", 654),
                lambda x: x["programs"]["forward"]["changed_runs"].pop(),
                lambda x: x["programs"].pop("backward"),
            ):
                data = json.loads(original_receipt)
                mutate(data)
                receipt.write_text(json.dumps(data))
                bad = run("independent.py")
                self.assertNotEqual(bad.returncode, 0)
                self.assertIn("independent receipt differs", bad.stderr)
            receipt.write_text(original_receipt)
            archive = target / primary.INPUTS[2]
            archive.write_bytes(archive.read_bytes() + b"deliberate source archive mutation")
            bad = run()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source pin differs", bad.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
