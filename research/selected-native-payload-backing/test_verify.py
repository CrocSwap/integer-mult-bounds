"""Behavioral and integrity controls for the native payload storage receipt."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("payload_verify", PACKAGE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class PayloadBackingTests(unittest.TestCase):
    def test_actual_add_peak_includes_both_cleared_split_arrays(self):
        row = verify.execute_case("add", 3, 1, 1, 1, 1)
        self.assertEqual(row["peak"], 21)
        self.assertEqual(row["witness_sizes"], [4, 7, 10])
        self.assertTrue(row["cleared_retained"])
        self.assertGreater(row["peak"], row["volume"] + 1)

    def test_swap_second_pass_retains_its_incoming_intermediate(self):
        row = verify.execute_case("swap", 3, 2, 1, 1, 1)
        self.assertEqual(row["peak"], 254)
        self.assertEqual(row["witness_sizes"], [10] * 9 + [82, 82])
        self.assertGreater(row["peak"], 2 * row["volume"] + 3**2 + 1)

    def test_one_digit_sign_rotation_exceeds_its_digit_pass(self):
        row = verify.execute_case("sign", 3, 1, 1, 1, 1)
        self.assertEqual(row["peak"], 13)
        self.assertEqual(row["witness_sizes"], [2, 3, 4, 4])
        self.assertGreater(row["peak"], 2 * row["volume"] + 3 + 1)

    def test_linear_sign_comparison_is_same_volume_and_endpoint(self):
        old = verify.execute_case("sign", 3, 2, 1, 1, 1)
        new = verify.execute_case("linear_sign", 3, 2, 1, 1, 1)
        self.assertEqual((old["volume"], new["volume"]), (9, 9))
        self.assertEqual((old["peak"], new["peak"]), (32, 10))
        self.assertEqual(new["witness_sizes"], [10])

    def test_composition_prices_payload_beyond_structural_cuts(self):
        # PR2882: N=2,F=9,K=19,D=7,Q=4 gives structural M=92.
        add = verify.execute_case("add", 3, 1, 1, 1, 1)
        sign = verify.execute_case("sign", 3, 2, 1, 1, 1)
        linear = verify.execute_case("linear_sign", 3, 2, 1, 1, 1)
        self.assertEqual(verify.composed_bound(2, 9, 19, 7, 4, add["peak"]), 94)
        self.assertEqual(verify.composed_bound(2, 9, 19, 7, 4, sign["peak"]), 105)
        self.assertEqual(verify.composed_bound(2, 9, 19, 7, 4, linear["peak"]), 92)

    def test_observer_does_not_retain_discarded_payload(self):
        observer = verify.Observer()
        with verify.sources(observer) as modules:
            tape = modules["records"].Tape()
            # Register one explicit observational control, not a runtime fixture.
            import weakref
            observer.references.append(weakref.ref(tape))
            tape.append(1)
            self.assertEqual(observer.sample(), [2])
            del tape
            self.assertEqual(observer.sample(), [])

    def test_invalid_budget_domains(self):
        for args in (("bad", 3, 1, 9), ("add", True, 1, 9),
                     ("swap", 2, 1, 9), ("sign", 3, 0, 9), ("swap", 3, 2, 9)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                verify.payload_peak(*args)
        for args in ((0, 9, 19, 7, 4, 21), (2, 9, 18, 7, 4, 21),
                     (2, 9, 19, 6, 4, 21), (2, 9, 19, 7, True, 21),
                     (2, 9, 19, 7, 4, 9)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                verify.composed_bound(*args)

    def test_bounded_fixture_domain(self):
        for args in (("add", 3, 4, 1, 1, 1), ("swap", 5, 3, 1, 1, 1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                verify.execute_case(*args)

    def test_altered_export_rejects_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "package"
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            path = package / "sources/bitstream.py"
            path.chmod(0o600)
            path.write_bytes(path.read_bytes() + b"\n# changed source\n")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                verify.authenticate(package)

    def test_missing_source_inventory_rejects(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "package"
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            path = package / "SOURCES.json"
            path.chmod(0o600)
            manifest = json.loads(path.read_text())
            manifest["exports"] = [row for row in manifest["exports"]
                                 if row.get("export") != "sources/stream.py"]
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "inventory"):
                verify.authenticate(package)

    def test_preloaded_source_module_rejects(self):
        sys.modules["bitstream"] = types.ModuleType("bitstream")
        try:
            with self.assertRaisesRegex(ValueError, "preloaded"):
                with verify.sources(verify.Observer()):
                    self.fail("preloaded module accepted")
        finally:
            del sys.modules["bitstream"]

    def test_boolean_receipt_substitution_fails_actual_cli(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "package"
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            path = package / "RESULT.json"
            path.chmod(0o600)
            receipt = json.loads(path.read_text())
            receipt["cases"][0]["before"] = True  # Python equality would accept 1.
            path.write_text(json.dumps(receipt))
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt differs", result.stderr)

    def test_refuse_receipt_overwrite(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(PACKAGE / "verify.py"),
                                 "--write", str(PACKAGE / "RESULT.json")],
                                capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileExistsError", result.stderr)


if __name__ == "__main__":
    unittest.main()
