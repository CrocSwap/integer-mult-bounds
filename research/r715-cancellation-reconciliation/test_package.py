#!/usr/bin/env python3
"""Independent frame oracle and controlled failures for the R715 companion.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r715_companion", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
ROOT = HERE.parents[1]


def fraction_rref(vectors):
    """Separate dense Gauss-Jordan implementation, with Fraction division."""
    a = [list(map(Fraction, row)) for row in vectors]
    pivot = 0
    for column in range(8):
        choices = [r for r in range(pivot, len(a)) if a[r][column]]
        if not choices:
            continue
        r = choices[0]
        a[pivot], a[r] = a[r], a[pivot]
        scale = a[pivot][column]
        a[pivot] = [x / scale for x in a[pivot]]
        for r in range(len(a)):
            if r != pivot:
                scale = a[r][column]
                a[r] = [x - scale * y for x, y in zip(a[r], a[pivot])]
        pivot += 1
    return tuple(tuple(row) for row in a[:pivot])


class ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before, cls.after, cls.record = V.load_sources(ROOT)
        cls.geo = V.geometry(cls.before)
        cls.positive = V.reconcile(cls.before, cls.after, cls.record)

    def test_complete_receipt(self):
        self.assertEqual(self.positive, json.loads((HERE / "RESULT.json").read_text()))

    def test_all_frame_bases_independent_fraction_oracle(self):
        for indices, actual in zip(self.before["frames"], self.geo[0]):
            expected = fraction_rref(self.before["lines"][i] for i in indices)
            normalized = tuple(tuple(Fraction(x, next(v for v in row if v))
                                     for x in row) for row in actual)
            self.assertEqual(normalized, expected)

    def test_omitted_pair_rejected(self):
        r = copy.deepcopy(self.record)
        r["changes"].pop()
        with self.assertRaisesRegex(V.Invalid, "20-pair"):
            V.deletion_audit(self.before, self.after, r)

    def test_duplicate_pair_rejected(self):
        r = copy.deepcopy(self.record)
        r["changes"][1] = r["changes"][0]
        with self.assertRaisesRegex(V.Invalid, "overlapping deletion"):
            V.deletion_audit(self.before, self.after, r)

    def test_wrong_gate_frame_rejected(self):
        r = copy.deepcopy(self.record)
        r["changes"][0]["gate"][0] = 0
        with self.assertRaisesRegex(V.Invalid, "identical framed"):
            V.deletion_audit(self.before, self.after, r)

    def test_noncommuting_middle_rejected_without_source_pins(self):
        w = copy.deepcopy(self.before)
        ph = self.record["changes"][0]["phase"]
        i, j = self.record["changes"][0]["removed_original_indices"]
        w[ph] = [[f, d, [s]] for f, d, s in V.flatten(w, ph)]
        # Introduce a dependency on the cancelled gate's destination.
        _, d, _ = w[ph][i]
        w[ph][i + 1] = [1, d + 1, [d]]
        with self.assertRaisesRegex(V.Invalid, "noncommuting crossed"):
            V.deletion_audit(w, self.after, self.record)

    def test_wrong_paid_profile_rejected_without_source_pins(self):
        r = copy.deepcopy(self.record)
        r["after_profile"]["1"] -= 1
        with self.assertRaisesRegex(V.Invalid, "after paid profile"):
            V.reconcile(self.before, self.after, r)

    def test_boolean_profile_rejected(self):
        r = copy.deepcopy(self.record)
        r["after_profile"]["7"] = True
        with self.assertRaisesRegex(V.Invalid, "integer profile"):
            V.reconcile(self.before, self.after, r)

    def test_one_unpaired_addition_breaks_dirty_endpoint(self):
        w = copy.deepcopy(self.after)
        # The first full-frame removed transvection is no longer paired.
        w["A"].append(copy.deepcopy(self.record["changes"][0]["gate"]))
        with self.assertRaisesRegex(V.Invalid, "arbitrary-dirty endpoint"):
            V.replay(w, self.geo)

    def test_skipped_helper_restoration_breaks_endpoint(self):
        w = copy.deepcopy(self.after)
        w["C"].pop()
        with self.assertRaisesRegex(V.Invalid, "arbitrary-dirty endpoint"):
            V.replay(w, self.geo)

    def test_missing_copy_use_breaks_endpoint(self):
        w = copy.deepcopy(self.after)
        next(row for row in w["scatter"] if row).pop()
        with self.assertRaisesRegex(V.Invalid, "arbitrary-dirty endpoint"):
            V.replay(w, self.geo)

    def test_empty_source_record_cannot_hide_frame_descent(self):
        w = copy.deepcopy(self.after)
        w["C"].append([0, 250, []])
        self.assertEqual(V.scalar_run(w, [1 << i for i in range(955)]),
                         V.scalar_run(self.after, [1 << i for i in range(955)]))
        with self.assertRaisesRegex(V.Invalid, "non-nested frame"):
            V.replay(w, self.geo)

    def test_scalar_preserving_empty_record_can_change_price(self):
        w = copy.deepcopy(self.before)
        bases = self.geo[0]
        current = [bases[f] for f in w["start"]]
        selected = None
        for ph in V.PHASES:
            for index, (f, d, srcs) in enumerate(w[ph]):
                for r in [d] + srcs:
                    # The helper's current clean-x support is inside its old
                    # frame. A containing intermediate frame splits a charge.
                    old, new = current[r], bases[f]
                    if r >= 240 and len(new) - len(old) >= 2:
                        for mid, b in enumerate(bases):
                            if len(old) < len(b) < len(new) and V.contained(old, b) and V.contained(b, new):
                                selected = ph, index, r, mid
                                break
                    if selected:
                        break
                    current[r] = new
                if selected:
                    break
            if selected:
                break
        self.assertIsNotNone(selected)
        self.assertEqual(selected, ("A", 4, 709, 6))
        ph, index, r, mid = selected
        w[ph].insert(index, [mid, r, []])
        receipt = V.replay(w, self.geo)
        self.assertEqual(receipt["phase_map_sha256"], self.positive["before"]["phase_map_sha256"])
        self.assertNotEqual(receipt["profile"], self.positive["before"]["profile"])
        self.assertEqual(receipt["rank_mass"], self.positive["before"]["rank_mass"])
        self.assertEqual(receipt["paid_children"], self.positive["before"]["paid_children"] + 1)

    def test_invalid_boolean_index_rejected(self):
        w = copy.deepcopy(self.after)
        w["A"][0][0] = True
        with self.assertRaisesRegex(V.Invalid, "gate frame index"):
            V.replay(w, self.geo)

    def test_relocated_optimized_cli_and_disk_corruptions(self):
        pins = json.loads((HERE / "SOURCE-PINS.json").read_text())["files"]
        with tempfile.TemporaryDirectory(prefix="r715-reconciliation-") as name:
            root = Path(name)
            package = root / "research/r715-cancellation-reconciliation"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for path in pins:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            manifest_path = "research/experiment-log/MANIFEST.json"
            shutil.copyfile(ROOT / manifest_path, root / manifest_path)
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            run = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            # Input-file, manifest-alias and receipt corruptions are separate.
            for path in (V.PARENT, V.CHILD, V.RECORD):
                target = root / path
                old = target.read_bytes()
                target.write_bytes(old + b" ")
                run = subprocess.run(command, cwd=root, capture_output=True, text=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("source pin", run.stderr)
                target.write_bytes(old)
            manifest = root / manifest_path
            changed_manifest = json.loads(manifest.read_text())
            # Unrelated archive additions are allowed; relevant aliases are not.
            changed_manifest["unrelated-new-record"] = "0" * 64
            manifest.write_text(json.dumps(changed_manifest))
            run = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            key = V.PARENT.removeprefix("research/experiment-log/")
            old_hash = changed_manifest[key]
            changed_manifest[key] = "0" * 64
            manifest.write_text(json.dumps(changed_manifest))
            run = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("parent alias manifest", run.stderr)
            changed_manifest[key] = old_hash
            manifest.write_text(json.dumps(changed_manifest))
            receipt = package / "RESULT.json"
            changed = json.loads(receipt.read_text())
            changed["after"]["paid_children"] -= 1
            receipt.write_text(json.dumps(changed))
            run = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("complete receipt equality", run.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
