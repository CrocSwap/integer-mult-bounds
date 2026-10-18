# SPDX-License-Identifier: Apache-2.0
"""Focused package/receipt tests, not a repository-wide suite."""
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
spec = importlib.util.spec_from_file_location("staged_retirement", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = V.load()
        cls.receipt = json.loads((HERE / "CERTIFICATE.json").read_text())
        cls.actual = V.derive(cls.word)

    def test_complete_receipt_and_tampering(self):
        V.verify_receipt(self.actual, self.receipt)
        for key, value in (("complete_scalar_adds", 24303), ("copies_erased_before_cut", 8),
                           ("four_contact_witness", []), ("new_kappa", True)):
            wrong = copy.deepcopy(self.receipt)
            wrong[key] = value
            with self.assertRaisesRegex(ValueError, "certificate mismatch"):
                V.verify_receipt(self.actual, wrong)
        wrong = copy.deepcopy(self.receipt)
        wrong["first_least_join_failure"]["required_rank"] = 7
        with self.assertRaisesRegex(ValueError, "certificate mismatch"):
            V.verify_receipt(self.actual, wrong)

    def test_source_corruption(self):
        raw = (V.ROOT / V.WORD).read_bytes()
        with self.assertRaisesRegex(ValueError, "source hash"):
            V.authenticated_word(raw[:-1] + bytes([raw[-1] ^ 1]))

    def test_contact_order_and_endpoint_are_material(self):
        chain = list(V.CHAIN)
        chain[1], chain[2] = chain[2], chain[1]
        with self.assertRaisesRegex(ValueError, "chronology/connectivity"):
            V.check_chain(self.word, chain)
        changed = copy.deepcopy(self.word)
        changed["final"][111] = 1
        with self.assertRaisesRegex(ValueError, "annihilate"):
            V.check_chain(changed)

    def test_late_donor_order_cannot_repair_earlier_failure(self):
        w = self.word
        fb = [V.basis([w["lines"][i] for i in frame]) for frame in w["frames"]]
        rows, frames, _, _, _, _ = V.prefix(w, fb)
        stage = [("isolation", i, 0, f, t, s) for i, (f, t, s) in enumerate(V.STAGE)]
        isolated = V.execute(rows, stage)
        tail, _, _ = V.inlined_suffix(w)
        locations = [i for i, gate in enumerate(tail) if gate[0] == "B" and gate[1] == 653 and gate[2] == 0]
        self.assertEqual(len(locations), 9)
        changed = tail[:]
        for i, gate in zip(locations, reversed([tail[i] for i in locations])):
            changed[i] = gate
        self.assertEqual(V.execute(isolated, changed), V.expected_rows(w))
        initial = [fb[f] for f in frames]
        initial[163] = V.join(initial[163], fb[507])
        initial[465] = fb[512]
        failure, _, _ = V.least_joins(w, fb, initial, changed)
        self.assertEqual((failure["index"], failure["failed_register"]), (601, 111))

    def test_isolated_source_only_export(self):
        with tempfile.TemporaryDirectory(prefix="staged-retirement-export-") as temporary:
            root = Path(temporary)
            destination = root / "research" / HERE.name
            shutil.copytree(HERE, destination, ignore=shutil.ignore_patterns("__pycache__"))
            manifest = json.loads((HERE / "SOURCES.json").read_text())
            for item in manifest["files"]:
                if item["usage"] == "input":
                    source, target = V.ROOT / item["path"], root / item["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
            for script, marker in (("verify.py", "PASS_R439_STAGED_RETIREMENT"),
                                   ("independent.py", "PASS_R439_STAGED_INDEPENDENT"),
                                   ("literal_copies.py", "PASS_R439_LITERAL_COPY_CUT")):
                completed = subprocess.run([sys.executable, "-I", "-O", "-S", "-B", str(destination / script)],
                                           cwd=root, capture_output=True, text=True, timeout=120, check=True)
                self.assertIn(marker, completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
