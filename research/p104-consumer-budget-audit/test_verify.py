"""Behavioral controls and a Git-free export replay for this scoped audit.

All fault injection is in memory or in a TemporaryDirectory. The retained
sources and receipt are never rewritten. The export runs only the primary
and independent checkers, so the test suite cannot recursively invoke itself.
Written with OpenAI Codex assistance; Apache-2.0.
"""

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def snapshot(root):
    """Include every file and its bytes, so unexpected generated files fail."""
    return {
        path.relative_to(root).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }


def relative_path(value):
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
        raise ValueError("export input must be a contained relative path")
    return path


def export_fixture(destination):
    """Copy the package and all declared external inputs, without Git data."""
    package_relative = PACKAGE.relative_to(ROOT)
    shutil.copytree(PACKAGE, destination / package_relative,
                    ignore=shutil.ignore_patterns("__pycache__", ".git"))
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    verify = json.loads((PACKAGE / "VERIFY.json").read_text(encoding="utf-8"))
    external = {entry["path"] for entry in sources["files"] if entry["usage"] == "input"}
    external.update(verify["inputs"])
    for name in sorted(external):
        relative = relative_path(name)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return destination / package_relative


class ContractControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        namespace = runpy.run_path(str(PACKAGE / "verify.py"))
        cls.consumer = staticmethod(namespace["consumer"])
        cls.result = namespace["recompute"]()
        bounds = cls.result["bills"]["dual2725"]["lower_bounds"]
        cls.kappa = Fraction(bounds["selected_kappa"]["a"])
        cls.primitive = Fraction(bounds["selected_primitive"]["a"])

    def words(self):
        census = self.result["censuses"]
        return deepcopy(census["forward2458"]), deepcopy(census["dual2725"])

    def bill(self, forward, dual):
        return self.consumer(forward, dual, self.kappa, self.primitive)

    def test_extra_endpoint_credit_rejected(self):
        forward, dual = self.words()
        forward["persistent_endpoint_progress"] += 1
        with self.assertRaisesRegex(ValueError, "fixed credited boundary"):
            self.bill(forward, dual)

    def test_changed_rank_mass_rejected(self):
        forward, dual = self.words()
        dual["profile"]["1"] -= 1
        with self.assertRaisesRegex(ValueError, "audited discounted shape"):
            self.bill(forward, dual)

    def test_equal_mass_coarsening_is_not_rank_deletion(self):
        forward, dual = self.words()
        # Nine H1 children -> H9 preserves rank mass but changes the premise.
        forward["profile"]["1"] -= 9
        forward["profile"]["9"] = 1
        with self.assertRaisesRegex(ValueError, "audited discounted shape"):
            self.bill(forward, dual)

    def test_child_above_width_is_rejected(self):
        forward, dual = self.words()
        # Preserve mass to ensure this is not merely a total-mass fault.
        forward["profile"]["1"] -= 74
        forward["profile"]["74"] = 1
        with self.assertRaisesRegex(ValueError, "audited discounted shape"):
            self.bill(forward, dual)

    def test_saving_outside_proof_domain_is_rejected(self):
        forward, dual = self.words()
        for value in (Fraction(-1, 10), Fraction(1)):
            with self.subTest(a=value):
                with self.assertRaisesRegex(ValueError, "saving domain"):
                    self.consumer(forward, dual, value, self.primitive)


class ExportControls(unittest.TestCase):
    def run_checker(self, root, package, script, expected, succeeds=True):
        # sys.executable is absolute. An empty PATH also prevents accidentally
        # relying on a system Git binary for the claimed Git-free replay.
        environment = os.environ.copy()
        environment["PATH"] = ""
        before = snapshot(root)
        completed = subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(package / script)],
            cwd=root, env=environment, capture_output=True, text=True,
            timeout=45, check=False,
        )
        output = completed.stdout + completed.stderr
        self.assertEqual(snapshot(root), before,
                         "checker changed inputs, receipt, or export inventory")
        if succeeds:
            self.assertEqual(completed.returncode, 0, output)
        else:
            self.assertNotEqual(completed.returncode, 0,
                                "mutant unexpectedly accepted: " + output)
        self.assertIn(expected, output)

    def test_frozen_selected_input_in_both_engines(self):
        with TemporaryDirectory(prefix="p104-historical-input-") as temporary:
            root = Path(temporary) / "export"
            package = export_fixture(root)
            live = root / "certificates/selected-result.json"
            live.parent.mkdir(parents=True)
            live.write_text("different live selection\n")
            for script, marker in (("verify.py", "PASS_P104_CONSUMER_BUDGET_AUDIT"),
                                   ("independent_check.py", "PASS_INDEPENDENT_P104_CONSUMER_BUDGET")):
                self.run_checker(root, package, script, marker)
            frozen = package / "inputs/SELECTED-AT-BASE.json"
            frozen.write_bytes(frozen.read_bytes() + b"\n")
            for script in ("verify.py", "independent_check.py"):
                self.run_checker(root, package, script, "source SHA256", succeeds=False)

    def test_git_free_replay_and_artifact_faults(self):
        with TemporaryDirectory(prefix="p104-consumer-audit-") as temporary:
            root = Path(temporary) / "export"
            package = export_fixture(root)
            self.assertFalse(any(path.name == ".git" for path in root.rglob("*")))
            original = snapshot(root)
            self.run_checker(root, package, "verify.py",
                             "PASS_P104_CONSUMER_BUDGET_AUDIT")
            self.run_checker(root, package, "independent_check.py",
                             "PASS_INDEPENDENT_P104_CONSUMER_BUDGET")

            receipt = package / "RESULT.json"
            receipt_bytes = receipt.read_bytes()
            changed = json.loads(receipt_bytes)
            # Python equality equates 73 and 73.0; receipt typing must not.
            changed["contract"]["width"] = float(changed["contract"]["width"])
            try:
                receipt.write_text(json.dumps(changed), encoding="utf-8")
                self.run_checker(root, package, "verify.py",
                                 "typed receipt mismatch", succeeds=False)
            finally:
                receipt.write_bytes(receipt_bytes)

            changed = json.loads(receipt_bytes)
            key = next(iter(changed))
            duplicate = ("{" + json.dumps(key) + ":" + json.dumps(changed[key])
                         + "," + receipt_bytes.decode("utf-8").lstrip()[1:])
            try:
                receipt.write_text(duplicate, encoding="utf-8")
                self.run_checker(root, package, "verify.py",
                                 "duplicate JSON key", succeeds=False)
            finally:
                receipt.write_bytes(receipt_bytes)

            # A valid-JSON whitespace edit must still break the exact source pin.
            source = package / "inputs/PR2725-WORD.json"
            source_bytes = source.read_bytes()
            try:
                source.write_bytes(source_bytes + b"\n")
                self.run_checker(root, package, "verify.py",
                                 "source SHA256", succeeds=False)
                self.run_checker(root, package, "independent_check.py",
                                 "source SHA256", succeeds=False)
            finally:
                source.write_bytes(source_bytes)
            self.assertEqual(snapshot(root), original,
                             "fault injection did not restore the export exactly")


if __name__ == "__main__":
    unittest.main(verbosity=2)
