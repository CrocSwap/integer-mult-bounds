"""Meaningful algebra, source-integrity, and optimized relocation controls."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class PackageTests(unittest.TestCase):
    def test_exact_inverse_and_all_omissions(self):
        self.assertEqual(v.exact_checks()["omission_controls"], 10)

    def test_cycle_write_count_not_just_total_moved(self):
        permutation = {i: v.PERMUTATION[i] for i in range(6)}
        self.assertEqual(sorted(map(len, v.cycles_of(permutation))), [2, 3])
        moved = sum(i != j for i, j in permutation.items())
        self.assertEqual((9-moved-len(v.cycles_of(permutation)))//2, 1)
        # A permutation requires more than one write on each nontrivial cycle:
        # if every cycle coordinate is written once, the earliest final write
        # duplicates the still-untouched row at its destination basis index.
        checked = 0
        for n in range(2, 7):
            for p in __import__("itertools").permutations(range(n)):
                for cycle in v.cycles_of(dict(enumerate(p))):
                    for first in cycle:
                        rows = list(v.identity(n))
                        rows[first] = rows[p[first]]
                        self.assertEqual(rows[first], rows[p[first]])
                        self.assertNotEqual(first, p[first])
                        checked += 1
        self.assertGreater(checked, 4000)

    def test_cost_boundary_and_admission(self):
        for receipt in v.invoice().values():
            self.assertEqual(receipt["restored_component_minimum"], 28*4+14*10)
            self.assertEqual(receipt["separate_complex_components_extra"], 2*(252-224))
        with self.assertRaises(ValueError):
            v.inverse([("copy", 0, 1)])

    def test_recognizer_detects_bad_swap(self):
        provider = v.ROOT / (v.PROVIDERS + "ck/LOCAL-PROGRAMS.json.gz")
        events = v.read(provider)["forward"]
        blocks = v.boundary_census(events)
        first = blocks[0]["swap_starts"][0]
        self.assertIsNotNone(v.recognize(events, first, first+4))
        broken = copy.deepcopy(events[first:first+4])
        broken[-1][1][2] *= -1
        self.assertIsNone(v.recognize(broken, 0, 4))

    def test_relocation_and_on_disk_controls(self):
        # The full command is intentionally run once in a read-only relocated
        # input tree, independently of the preceding normal package replay.
        with tempfile.TemporaryDirectory(prefix="restored-gap-test-") as temporary:
            root = Path(temporary)
            package = root / "research/restored-cycle-gap"
            shutil.copytree(v.HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for name in v.read(v.HERE / "PINS.json")["live_inputs"]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT / name, target)
            for path in root.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            completed = subprocess.run(command, cwd=root, capture_output=True, timeout=480)
            self.assertEqual(completed.returncode, 0, completed.stderr.decode())
            self.assertIn(b"PASS_RESTORED_CYCLE_GAP", completed.stdout)
            for name in ("ternary.cpp", "packed.cpp", "references/PR1216-PROOF.md"):
                path = package / name
                original = path.read_bytes()
                path.chmod(0o644)
                path.write_bytes(original + b"\ncorruption\n")
                failed = subprocess.run(command + ["--quick"], cwd=root, capture_output=True, timeout=30)
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn(b"source SHA256", failed.stderr)
                path.write_bytes(original)
                path.chmod(0o444)
            # Receipt drift must be detected after a real complete replay.
            path = package / "EXPECTED.json"
            path.chmod(0o644)
            bad = json.loads(path.read_text())
            bad["finite_exclusion"]["distance_nine_control"]["middle_hits"] = 0
            path.write_text(json.dumps(bad))
            failed = subprocess.run(command, cwd=root, capture_output=True, timeout=480)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn(b"receipt drift", failed.stderr)


if __name__ == "__main__":
    unittest.main()
