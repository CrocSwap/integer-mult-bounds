#!/usr/bin/env python3
"""Mathematical counter-controls and standalone-package checks, Apache-2.0.

Ross Richardson with substantial OpenAI Codex assistance.
"""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v, oracle = load("verify"), load("oracle")


class MathematicalControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.source_check()
        cls.word = v.read(HERE / "sources/PR924-COMPOSITION.json")["replacement"]
        cls.lower = staticmethod(v.lowerer())
        cls.reference = v.replay(v.primitives(cls.word, cls.lower))[0]
        cls.result = v.census(cls.word)
        cls.positions = {0: 5, 1: 5, 2: 6, 5: 5, 6: 0, 7: 2}

    def test_every_gate_deletion_changes_map(self):
        for i in range(len(self.word)):
            with self.subTest(gate=i):
                mutant = self.word[:i] + self.word[i + 1:]
                self.assertNotEqual(v.replay(v.primitives(mutant, self.lower))[0], self.reference)

    def test_every_gate_sign_change_changes_map(self):
        for i in range(len(self.word)):
            with self.subTest(gate=i):
                mutant = copy.deepcopy(self.word)
                mutant[i][-3] *= -1
                self.assertNotEqual(v.replay(v.primitives(mutant, self.lower))[0], self.reference)

    def test_every_required_scale_is_necessary(self):
        self.assertEqual(sum(op[0] == "scale" for op in self.word), 6)
        for r in self.positions:
            p = self.positions.copy()
            del p[r]
            with self.assertRaisesRegex(ValueError, "placement inventory"):
                v.construct(self.word, p)

    def test_frame_alias_boolean_and_nonbinary_rejected(self):
        for reason, edit in (
            ("wrong frame", lambda w: w[0][-1].__setitem__(0, 391)),
            ("source alias", lambda w: w[0].__setitem__(2, w[0][1])),
            ("integer gate", lambda w: w[0].__setitem__(3, True)),
            ("signed power", lambda w: w[0].__setitem__(3, 3)),
        ):
            mutant = copy.deepcopy(self.word)
            edit(mutant)
            with self.assertRaisesRegex(ValueError, reason):
                v.model(mutant)

    def test_placement_limits(self):
        for bad in (-1, 8, True):
            p = self.positions | {0: bad}
            with self.assertRaisesRegex(ValueError, "placement range"):
                v.construct(self.word, p)

    def test_moving_a_scale_without_conjugation_fails(self):
        mutant = copy.deepcopy(self.word)
        i = next(i for i, op in enumerate(mutant) if op[:2] == ["scale", 0])
        mutant.insert(0, mutant.pop(i))
        self.assertNotEqual(v.replay(v.primitives(mutant, self.lower))[0], self.reference)

    def test_clean_work_cannot_be_assumed(self):
        stream = self.lower(["add", ["L", 0], ["L", 1], 2, 1])
        v.replay(stream)
        with self.assertRaisesRegex(ValueError, "work not cleared"):
            v.replay(stream[:-1])

    def test_independent_grid_cannot_round(self):
        with self.assertRaisesRegex(ValueError, "would round"):
            oracle.execute([("H", 0)] * 129 + [("Z", 8)])

    def test_independent_missing_clear_and_wrong_sign(self):
        ops = oracle.original_primitives(self.word)
        with self.assertRaisesRegex(ValueError, "work remains dirty"):
            oracle.execute([op for op in ops if op[0] != "Z"])
        mutant = list(ops)
        i = next(i for i, op in enumerate(mutant) if op[0] in ("A", "S"))
        mutant[i] = (("S" if mutant[i][0] == "A" else "A"),) + mutant[i][1:]
        self.assertNotEqual(oracle.execute(mutant), oracle.execute(ops))

    def test_worse_valid_placement_is_not_identity_failure(self):
        p = self.positions | {0: 4}
        candidate = v.construct(self.word, p)
        rows, stats = v.replay(v.primitives(candidate, self.lower))
        self.assertEqual(rows, self.reference)
        self.assertGreater(stats["primitives"], 73)

    def test_added_macro_is_valid_but_more_expensive(self):
        candidate = copy.deepcopy(self.word)
        i = next(i for i, op in enumerate(candidate) if op[:2] == ["scale", 0])
        candidate[i:i + 1] = [["scale", 0, 4, 1, candidate[i][-1]],
                              ["scale", 0, 1, 2, candidate[i][-1]]]
        rows, stats = v.replay(v.primitives(candidate, self.lower))
        self.assertEqual(rows, self.reference)
        self.assertEqual(len(candidate), 33)
        self.assertGreater(stats["primitives"] + 16 * (64 * 74 ** 3), 73)


class PackageControls(unittest.TestCase):
    def test_relocation_tampering_and_output_preservation(self):
        with tempfile.TemporaryDirectory(prefix="factory scale 27 ") as tmp:
            root = Path(tmp)
            dst = root / HERE.relative_to(v.ROOT)
            shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns("__pycache__"))
            for rel in v.read(HERE / "SOURCES.json")["files"]:
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copyfile(v.ROOT / rel, target)

            def run(*args):
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(dst / "verify.py"), *args],
                                      cwd=root, capture_output=True, text=True)

            good = run()
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            snapshot = dst / "sources/PR924-COMPOSITION.json"
            original = snapshot.read_bytes()
            snapshot.write_bytes(original + b" ")
            bad = run()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source pin", bad.stderr)
            snapshot.write_bytes(original)
            expected = dst / "EXPECTED.json"
            original = expected.read_bytes()
            changed = json.loads(original)
            changed["histogram_magnitude"]["73"] += 1
            expected.write_text(json.dumps(changed))
            bad = run()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("deterministic receipt differs", bad.stderr)
            expected.write_bytes(original)
            bad = run("--write", str(expected))
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(expected.read_bytes(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
