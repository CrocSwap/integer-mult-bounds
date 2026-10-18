#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Failure controls for the PR1293 logarithm enclosure audit (stdlib only)."""
import contextlib
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("log_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def mutant(old, new):
    source, _ = audit.subject_source()
    audit.require(source.count(old) == 1, "mutation anchor")
    namespace = {"__name__": "subject_mutant", "__file__": str(HERE / "vendor/pr1293_verify.py")}
    exec(compile(source.replace(old, new), namespace["__file__"], "exec"), namespace)
    return namespace


@contextlib.contextmanager
def relocated():
    """A source-export-like checkout: no Git metadata or hidden local output."""
    with tempfile.TemporaryDirectory(prefix="pr1293-audit-test-") as temp:
        root = Path(temp)
        package = root / "research/pr1293-log-enclosure-audit"
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((HERE / "SOURCES.json").read_text())
        for row in sources["files"]:
            if row["usage"] == "input":
                destination = root / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(audit.ROOT / row["path"], destination)
        yield root, package


def run_export(root, package, record=False):
    command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
    if record:
        command.extend(["--write-receipt", str(root / "regenerated.json")])
    return subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)


class MathematicalControls(unittest.TestCase):
    def test_exact_one(self):
        for repaired in (False, True):
            namespace = audit.load_subject(repaired)
            self.assertEqual(namespace["ln_exp_bisection"](Q(1)), (0, 0))
        self.assertEqual(audit.log_oracle(Q(1)), (0, 0))

    def test_minimal_counterexample(self):
        point = Q(1, 2)
        x = audit.polynomial(point, 48)
        self.assertGreater(audit.polynomial(point, 49), x)
        namespace = audit.load_subject()
        result = namespace["ln_exp_bisection"](x)
        self.assertEqual(result, (point, point))
        self.assertLess(audit.log_oracle(x)[1], result[0])

    def test_integer_counterexample(self):
        point = Q(4384212064881345387879, 590295810358705651712)
        self.assertEqual(audit.load_subject()["ln_exp_bisection"](Q(1681)), (point, point))
        self.assertGreater(audit.polynomial(point, 49), 1681)
        self.assertLess(audit.log_oracle(Q(1681))[1], point)
        with self.assertRaisesRegex(ValueError, audit.UNRESOLVED):
            audit.load_subject(True)["ln_exp_bisection"](Q(1681))

    def test_two_sided_strict_interior(self):
        for kind, point, x, relation in audit.counterexample_specs():
            if not kind.startswith("interior-"):
                continue
            namespace = audit.load_subject()
            lower, upper = namespace["exp_taylor"](point, 48)
            self.assertLess(lower, x)
            self.assertLess(x, upper)
            self.assertEqual(namespace["ln_exp_bisection"](x), (point, point))
            reference = audit.log_oracle(x)
            self.assertFalse(audit.encloses((point, point), reference))
            with self.assertRaisesRegex(ValueError, audit.UNRESOLVED):
                audit.load_subject(True)["ln_exp_bisection"](x)

    def test_existing_agreement_check_misses_fixture(self):
        ns = audit.load_subject()
        x = audit.polynomial(Q(1, 2), 48)
        lower, upper = ns["ln_sqrt"](x)
        bad_lower, bad_upper = ns["ln_exp_bisection"](x)
        # Exactly the predicate used for selected-rank agreement in PR1293.
        self.assertTrue(lower <= bad_upper and bad_lower <= upper and
                        upper - lower < Q(1, 10 ** 20))
        self.assertFalse(audit.encloses((bad_lower, bad_upper), audit.log_oracle(x)))
        with self.assertRaisesRegex(ValueError, audit.UNRESOLVED):
            audit.load_subject(True)["ln_exp_bisection"](x)

    def test_null_return_is_not_an_exception(self):
        ns = mutant(audit.OLD, "        else:\n            return None\n")
        value = audit.polynomial(Q(1, 2), 48)
        with self.assertRaisesRegex(ValueError, "must raise, not return None"):
            audit.traced_call(ns, value, repaired=True)
        # The actual strict patch still raises and is accepted as unresolved.
        result, trace = audit.traced_call(audit.load_subject(True), value, repaired=True)
        self.assertIsNone(result)
        self.assertIsNotNone(trace["overlap"])

    def test_wrong_lower_update(self):
        ns = mutant("            lo = hi = mid\n", "            lo = mid\n")
        x = audit.polynomial(Q(1, 2), 48)
        self.assertFalse(audit.encloses(ns["ln_exp_bisection"](x), audit.log_oracle(x)))

    def test_wrong_upper_update(self):
        ns = mutant("            lo = hi = mid\n", "            hi = mid\n")
        x = audit.exponential_upper(Q(1, 2), 48)
        self.assertFalse(audit.encloses(ns["ln_exp_bisection"](x), audit.log_oracle(x)))

    def test_omitted_taylor_tail(self):
        # At this larger permitted midpoint the omitted tail exceeds a 72-step
        # bracket. Remove the tail but retain the proposed fail-closed branch;
        # this tests exponential soundness separately from the original bug.
        source, _ = audit.subject_source()
        changed = audit.repaired_source(source).replace("return total, total + tail", "return total, total")
        ns = {"__name__": "tail_mutant", "__file__": str(HERE / "vendor/pr1293_verify.py")}
        exec(compile(changed, ns["__file__"], "exec"), ns)
        point = Q(15, 2)
        x = (audit.polynomial(point, 48) + audit.polynomial(point, 49)) / 2
        self.assertLess(audit.log_oracle(x)[1], point)
        self.assertFalse(audit.encloses(ns["ln_exp_bisection"](x), audit.log_oracle(x)))

    def test_oracle_power_reduction(self):
        lo, hi = audit.log_oracle(Q(3, 2))
        square = audit.log_oracle(Q(9, 4))
        self.assertLessEqual(square[0], 2 * hi)
        self.assertLessEqual(2 * lo, square[1])
        lo2, hi2 = audit.log_oracle(Q(2))
        lo64, hi64 = audit.log_oracle(Q(64))
        self.assertLessEqual(lo64, 6 * hi2)
        self.assertLessEqual(6 * lo2, hi64)

    def test_oracle_tail_is_material(self):
        low_order = audit.atanh_log_bounds(Q(2), 1)
        reference = audit.log_oracle(Q(2))
        self.assertTrue(audit.encloses(low_order, reference))
        self.assertGreater(reference[0], low_order[0])
        self.assertFalse(audit.encloses((low_order[0], low_order[0]), reference))

    def test_domain_rejection(self):
        for repaired in (False, True):
            namespace = audit.load_subject(repaired)
            with self.assertRaises(ValueError):
                namespace["ln_exp_bisection"](Q(0))
            with self.assertRaisesRegex(ValueError, "exp range"):
                namespace["ln_exp_bisection"](Q(3000))
        with self.assertRaises(ValueError):
            audit.log_oracle(Q(1, 2))
        with self.assertRaises(ValueError):
            audit.atanh_log_bounds(Q(2), 0)

    def test_default_precision(self):
        for repaired in (False, True):
            ns = audit.load_subject(repaired)
            self.assertEqual((ns["CROSS_ORDER"], ns["CROSS_BITS"]), (48, 72))

    def test_semantic_receipt(self):
        receipt = audit.make_receipt()
        stored = json.loads((HERE / "RESULT.json").read_text())
        self.assertEqual(receipt, stored)
        self.assertEqual(len(receipt["counterexamples"]), 10)
        self.assertEqual(receipt["integer_counterexample"]["input"], "1681")
        rows = sum(receipt["selected_arguments"].values(), [])
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(row["overlap_hits"] == 0 for row in rows))


class BindingAndReplayControls(unittest.TestCase):
    def test_live_inventory_regeneration_mutations(self):
        for mutation in ("delete", "demote", "duplicate", "repin"):
            with self.subTest(mutation=mutation), relocated() as (root, package):
                path = package / "SOURCES.json"
                metadata = json.loads(path.read_text())
                index = next(i for i, row in enumerate(metadata["files"]) if row["usage"] == "input")
                if mutation == "delete":
                    del metadata["files"][index]
                elif mutation == "demote":
                    metadata["files"][index]["usage"] = "provenance"
                elif mutation == "duplicate":
                    metadata["files"].append(copy.deepcopy(metadata["files"][index]))
                else:
                    row = metadata["files"][index]
                    data_path = root / row["path"]
                    data_path.write_bytes(data_path.read_bytes() + b"\n")
                    row["sha256"] = audit.sha256(data_path.read_bytes())
                path.write_text(json.dumps(metadata))
                result = run_export(root, package, record=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, "inventory mismatch|duplicate source row|pin drift")
                self.assertFalse((root / "regenerated.json").exists())

    def test_subject_identity_regeneration_mutations(self):
        for field in audit.SUBJECT_ID:
            with self.subTest(field=field), relocated() as (root, package):
                path = package / "SUBJECT.json"
                metadata = json.loads(path.read_text())
                metadata[field] = 1293.0 if field == "pull_request" else "altered-" + str(metadata[field])
                path.write_text(json.dumps(metadata))
                result = run_export(root, package, record=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("subject identity drift", result.stderr)
                self.assertFalse((root / "regenerated.json").exists())

    def test_subject_symlink_rejected(self):
        with relocated() as (root, package):
            source = package / "vendor/pr1293_verify.py"
            external = root / "same-bytes.py"
            external.write_bytes(source.read_bytes())
            source.unlink()
            source.symlink_to(external)
            result = run_export(root, package, record=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("internal ordinary file", result.stderr)

    def test_receipt_json_types_and_duplicate_keys(self):
        for mutation in ("float", "bool", "duplicate-key"):
            with self.subTest(mutation=mutation), relocated() as (root, package):
                path = package / "RESULT.json"
                value = json.loads(path.read_text())
                if mutation == "float":
                    value["default_order"] = 48.0
                elif mutation == "bool":
                    value["selected_arguments"]["selected_bit"][0]["overlap_hits"] = False
                text = json.dumps(value)
                if mutation == "duplicate-key":
                    text = '{"default_order": 48,' + text[1:]
                path.write_text(text)
                result = run_export(root, package)
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, "receipt drift|duplicate JSON key")

    def test_source_drift(self):
        source, metadata = audit.subject_source()
        with self.assertRaisesRegex(ValueError, "SHA256 drift"):
            audit.validate_subject_bytes((source + "\n").encode(), metadata)
        altered = copy.deepcopy(metadata)
        altered["git_blob"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "Git blob drift"):
            audit.validate_subject_bytes(source.encode(), altered)

    def test_repair_anchor_and_patch(self):
        source, _ = audit.subject_source()
        self.assertEqual(audit.repair_diff(source), (HERE / "repair.patch").read_text())
        with self.assertRaisesRegex(ValueError, "unique"):
            audit.repaired_source(source + audit.OLD)
        with self.assertRaisesRegex(ValueError, "unique"):
            audit.repaired_source(source.replace(audit.OLD, ""))

    def test_clean_optimized_relocation(self):
        with relocated() as (root, package):
            result = run_export(root, package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_PR1293_LOG_ENCLOSURE_AUDIT", result.stdout)

    def test_source_corruption_in_subprocess(self):
        with relocated() as (root, package):
            source = package / "vendor/pr1293_verify.py"
            source.write_bytes(source.read_bytes() + b"\n")
            result = run_export(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("subject SHA256 drift", result.stderr)

    def test_live_input_corruption_in_subprocess(self):
        with relocated() as (root, package):
            source = root / "research/community-frontier1094-audit/ASSEMBLY.json"
            source.write_bytes(source.read_bytes() + b"\n")
            result = run_export(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("live input drift", result.stderr)

    def test_receipt_corruption_in_subprocess(self):
        with relocated() as (root, package):
            path = package / "RESULT.json"
            value = json.loads(path.read_text())
            value["counterexamples"][0]["original_return"] = ["0", "0"]
            path.write_text(json.dumps(value))
            result = run_export(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt drift", result.stderr)

    def test_patch_corruption_in_subprocess(self):
        with relocated() as (root, package):
            path = package / "repair.patch"
            path.write_text(path.read_text().replace("do not report", "do report"))
            result = run_export(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("repair patch drift", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
