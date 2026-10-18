"""Behavioral and integrity controls, including optimized Python execution."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify
from census import failure_case, run_case


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = verify.load_sources()

    def test_good_underbudget_restores_real_entry(self):
        failure_case(self.modules, "good", 42, bounds=(37671, 22))

    def test_fallback_underbudget_restores_real_entry(self):
        failure_case(self.modules, "fallback", bounds=(32768, 22))

    def test_nested_evaluation_failure_restores_real_entry(self):
        failure_case(self.modules, "fallback", bounds=(36750, 22), depth=1, history="P")

    def test_index_constructor_failure_restores_real_entry(self):
        failure_case(self.modules, "good", bounds=(37672, 2))

    def test_page_binding_failure_restores_real_entry(self):
        def mutate(case):
            case.plan.negative_sign = not case.plan.negative_sign
        failure_case(self.modules, "fallback", mutate=mutate)

    def test_wrong_expected_scalar_rejects_literal_result(self):
        with self.assertRaisesRegex(ValueError, "independent adapter coefficient"):
            run_case(self.modules, "good", mutate=lambda case: setattr(case, "expected", 0))

    def test_repeated_call_preserves_unrelated_residents(self):
        record = run_case(self.modules, "good", modulus=9, depth=1, borrowed=7, repeats=2)
        self.assertEqual(record["coefficient"], 8)
        self.assertEqual(record["entry"], [9, 8])

    def test_borrowed_entry_corruption_rejects(self):
        def mutate(case):
            case.residents[0].cells[1] = 1
        with self.assertRaisesRegex(ValueError, "borrowed values"):
            run_case(self.modules, "good", mutate=mutate)

    def test_entry_head_precondition_rejects(self):
        def mutate(case):
            case.residents[0].head = 2
        with self.assertRaisesRegex(ValueError, "entry numerical heads"):
            run_case(self.modules, "good", mutate=mutate)

    def test_typed_receipt_rejects(self):
        with self.assertRaisesRegex(ValueError, "typed receipt"):
            verify.check_receipt({"peak": 1}, {"peak": True})

    def test_source_corruption_rejects_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "package"
            shutil.copytree(verify.PACKAGE, target)
            source = target / "vendor" / "numeric.py"
            source.write_bytes(source.read_bytes() + b"\nraise RuntimeError('untrusted')\n")
            with patch.object(verify, "PACKAGE", target), self.assertRaisesRegex(ValueError, "source SHA256"):
                verify.authenticated_sources()

    def test_closed_source_inventory(self):
        expected = {name + ".py" for name in verify.NAMES} | {"NOTICE.md"}
        self.assertEqual(set(verify.authenticated_sources()), expected)
        manifest = json.loads((verify.PACKAGE / "SNAPSHOT.json").read_text())
        self.assertEqual(manifest["head"], "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1")


if __name__ == "__main__":
    unittest.main()
