"""Boundary and replay-failure controls on disposable copies. Apache-2.0.

Prepared with substantial OpenAI Codex assistance.
"""

import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("bit17_verify", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def exported(root):
    package = root / "research" / HERE.name
    shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
    for row in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if row["usage"] == "input":
            destination = root / row["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row["path"], destination)
    return package


def replay(package, root, optimized=False):
    return subprocess.run([sys.executable, "-I", *(["-O"] if optimized else []),
                           "-B", str(package / "verify.py"), "--repo-root", str(root)],
                          capture_output=True, text=True, timeout=30)


class BoundaryTests(unittest.TestCase):
    def test_reducible_scalar_ring_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not define a field"):
            v.Field(2, 5)

    def test_pure_cancelling_block_and_outside_gate(self):
        f = v.Field(2, 7)
        _, cyclic = v.scalar_census(f)
        a = v.FRAMES[0]
        minus_a = tuple(-x for x in a)
        e0 = (1, 0, 0, 0)
        for n in cyclic:
            gates = [(a, n), (minus_a, n)]
            self.assertEqual(v.word(f, gates), {v.ZERO: v.ID})
            for cut in range(3):
                got = v.word(f, gates[:cut]+[(v.OUTSIDE, e0)]+gates[cut:])
                self.assertEqual(got == v.target(v.OUTSIDE, v.ZERO), cut in (0, 2))

    def test_acyclic_and_cyclic_projectors_all_attain_the_paid_bill(self):
        f = v.Field(2, 7)
        checked = 0
        for n in itertools.product(range(4), repeat=4):
            a, b, c, d = n
            if n == v.ZERO or f.table[a][d] ^ f.table[b][c] or f.mm(n, n) != n:
                continue
            gates = [(frame, n if i < 2 else v.add(v.ID, n))
                     for i, frame in enumerate(v.FRAMES)]
            self.assertEqual(v.word(f, gates), v.target(v.SHIFT, v.SHIFT))
            checked += 1
        self.assertEqual(checked, 20)

    def test_optimized_read_only_git_free_relocation(self):
        with tempfile.TemporaryDirectory(prefix="bit17 source with spaces ") as tmp:
            root = Path(tmp)
            package = exported(root)
            for path in root.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
            directories = [root, *(p for p in root.rglob("*") if p.is_dir())]
            for path in directories:
                path.chmod(0o555)
            try:
                result = replay(package, root, optimized=True)
            finally:
                for path in directories:
                    path.chmod(0o755)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_BIT_EXTENSION_ONE_RELATION", result.stdout)
            self.assertFalse(list(root.rglob("*.pyc")))

    def test_changed_live_source_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="bit17 source fault ") as tmp:
            root = Path(tmp)
            package = exported(root)
            source = root / "research/bit-one-relation-any-registers/PROOF.md"
            source.write_bytes(source.read_bytes()+b"\nchanged source\n")
            result = replay(package, root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source mismatch", result.stderr)

    def test_changed_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="bit17 receipt fault ") as tmp:
            root = Path(tmp)
            package = exported(root)
            receipt = package / "RESULT.json"
            data = json.loads(receipt.read_text())
            data["formal_F4"]["outside_placements_rejected"] -= 1
            receipt.write_text(json.dumps(data))
            result = replay(package, root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RESULT.json mismatch", result.stderr)

    def test_independent_coefficient_comparison_is_enforced(self):
        with tempfile.TemporaryDirectory(prefix="bit17 oracle fault ") as tmp:
            root = Path(tmp)
            package = exported(root)
            oracle = package / "independent.py"
            text = oracle.read_text()
            text = text.replace('print(json.dumps(counts, sort_keys=True))',
                                'counts["all_placement_coefficients_binary_sha256"] = "0"*64\n'
                                '    print(json.dumps(counts, sort_keys=True))')
            oracle.write_text(text)
            result = replay(package, root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete-coefficient stream mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
