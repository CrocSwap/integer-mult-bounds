# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the fixed-matching monotone relay obstruction."""

import json
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def module(name):
    path = PACKAGE / (name + ".py")
    loaded = types.ModuleType(name)
    loaded.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), loaded.__dict__)
    return loaded


def cli(package, script, *arguments):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(package / script), *arguments],
        capture_output=True, text=True, timeout=30,
    )


class ConsistencyControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v, cls.i = module("verify"), module("independent")
        cls.inputs = cls.v.load_inputs()
        certificate, word, fixture, witness = cls.inputs
        cls.paths = cls.v.data_paths(word)
        cls.frames = cls.v.cover_frames(certificate, cls.paths)
        cls.edges = list(enumerate(witness["pairing"]))
        cls.layers = cls.v.interval_layers(cls.frames, cls.edges, cls.paths)
        cls.direct = [sum(1 << s for s in range(104) if
            set(cls.paths[f"X{s}"]) & set(cls.paths[f"Y{t}"])) for t in range(104)]
        cls.matrix = cls.v.correction(fixture)
        cls.required = [sum(1 << s for s in range(104) if cls.matrix[t][s])
                        for t in range(104)]
        cosets = cls.v.coset_masks(cls.frames[1][91], cls.frames[2][witness["pairing"][91]])
        quotients = cls.v.quotient_spaces()
        cls.choices = {d: cls.v.allowed_frames(cls.frames, cls.edges[91], d, cosets, quotients)
                       for d in range(3, 7)}

    def test_relaxed_baseline_and_exact_flag_domain(self):
        outputs = self.v.propagate([self.v.layer_plan(x) for x in self.layers], self.direct)
        self.assertEqual(outputs, [self.v.FULL] * 104)
        flags = list(self.v.full_flags(self.choices))
        self.assertEqual(len(flags), 9765)
        self.assertEqual(len(set(flags)), 9765)
        for indices in flags:
            chain = [self.choices[d][i] for d, i in zip(range(3, 7), indices, strict=True)]
            self.assertTrue(all(a & b == a for a, b in zip(chain, chain[1:])))

    def test_actual_nonnested_relay_restores_all_paths(self):
        selected = {}
        bounds4 = self.v.intervals(self.frames, self.edges, 4)
        bounds5 = self.v.intervals(self.frames, self.edges, 5)
        selected[4] = next(f for f in self.choices[4] if self.v.fits(bounds4[139], 4, f))
        selected[5] = next(f for f in self.choices[5] if self.v.fits(bounds5[83], 5, f))
        selected[3] = next(f for f in self.choices[3] if f & selected[4] == f)
        selected[6] = next(f for f in self.choices[6] if selected[5] & f == selected[5])
        self.assertNotEqual(selected[4] & selected[5], selected[4])
        self.assertEqual(list(self.v.full_flags({d: [selected[d]] for d in range(3, 7)})), [])
        plans = [self.v.layer_plan(x) for x in self.layers]
        for d, chosen in selected.items():
            changed = self.v.freeze_helper(self.layers[d - 1], self.frames, self.edges,
                                           self.paths, d, chosen)
            plans[d - 1] = self.v.layer_plan(changed)
        self.assertEqual(self.v.propagate(plans, self.direct), [self.v.FULL] * 104)

    def test_ignored_consistent_frame_fails_semantic_bound(self):
        with patch.object(self.v, "freeze_helper", side_effect=lambda layer, *args: layer):
            with self.assertRaisesRegex(ValueError, "uniform Y40 support bound"):
                self.v.flag_census(self.paths, self.frames, self.edges, self.layers,
                                   self.required, self.direct)

    def test_added_source_read_breaks_the_cut(self):
        chosen = next(self.v.full_flags(self.choices))
        layers = [tuple(part.copy() for part in layer) for layer in self.layers]
        for d, i in zip(range(3, 7), chosen, strict=True):
            layers[d - 1] = self.v.freeze_helper(layers[d - 1], self.frames, self.edges,
                                               self.paths, d, self.choices[d][i])
        before = self.v.propagate([self.v.layer_plan(x) for x in layers], self.direct)
        self.assertFalse(before[40] >> 1 & 1)
        layers[3][1][83] |= 1 << 1
        after = self.v.propagate([self.v.layer_plan(x) for x in layers], self.direct)
        self.assertTrue(after[40] >> 1 & 1)

    def test_independent_cut_and_false_premises(self):
        record = self.i.derive(*self.i.load_inputs())
        self.i.verify_cut(record)
        self.assertEqual(self.i.rejection_controls(record), 5)
        self.assertEqual(record["first_counterexample"]["coefficient"], "1/2")
        self.assertEqual(record["Y40_forced_missing_count"], 45)
        changed = deepcopy(record)
        changed["contacts_by_dimension"]["91"][7].append(83)
        with self.assertRaisesRegex(ValueError, "complete local contacts"):
            self.i.verify_cut(changed)

    def test_pairing_schema_and_incompatible_fixed_frame(self):
        pairing = self.edges.copy()
        values = [b for _, b in pairing]
        values[0] = True
        with self.assertRaisesRegex(ValueError, "pairing integers"):
            self.v.check_pairing(values, self.frames[-1])
        with self.assertRaisesRegex(ValueError, "fixed frame fits interval"):
            self.v.freeze_helper(self.layers[3], self.frames, self.edges, self.paths,
                                 4, self.v.span([1, 2, 4, 8]))

    def test_actual_optimized_cli_and_receipts(self):
        for script, receipt in (("verify.py", "RESULT.json"),
                                ("independent.py", "INDEPENDENT.json")):
            completed = cli(PACKAGE, script, "--emit")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout),
                             json.loads((PACKAGE / receipt).read_text()))
            rejected = cli(PACKAGE, script, "--unknown-option")
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("usage:", rejected.stderr)

    def test_gitfree_readonly_and_corruption(self):
        with tempfile.TemporaryDirectory(prefix="p104-flag-control-") as directory:
            export = Path(directory)
            target = export / "research/p104-fixed-matching-flag-consistency"
            shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns("__pycache__"))
            for name in self.v.INPUT_PINS:
                destination = export / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            files = [p for p in export.rglob("*") if p.is_file()]
            original = {p.relative_to(export): p.read_bytes() for p in files}
            try:
                for path in files:
                    path.chmod(0o444)
                for path in sorted(export.rglob("*"), reverse=True):
                    if path.is_dir():
                        path.chmod(0o555)
                export.chmod(0o555)
                for script in ("verify.py", "independent.py"):
                    completed = cli(target, script)
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(original, {p.relative_to(export): p.read_bytes() for p in files})
            finally:
                export.chmod(0o755)
                for path in export.rglob("*"):
                    path.chmod(0o755 if path.is_dir() else 0o644)
            source = export / next(iter(self.v.INPUT_PINS))
            raw = source.read_bytes()
            source.write_bytes(raw + b" ")
            for script in ("verify.py", "independent.py"):
                rejected = cli(target, script)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("hash", rejected.stderr.lower().replace("sha256", "hash"))
            source.write_bytes(raw)
            receipt = target / "RESULT.json"
            data = json.loads(receipt.read_text())
            data["census"]["passing_flags"] = 1
            receipt.write_text(json.dumps(data))
            rejected = cli(target, "verify.py")
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("exact typed receipt", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
