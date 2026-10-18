"""Fault controls for the independent node-boundary audit (standard library)."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("node_stock_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class NodeBoundaryControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rt = audit.runtime()

    def test_selected_stock_local_guard_and_descendant(self):
        values = audit.guard_records(self.rt)
        self.assertEqual(len(values), 6)
        self.assertEqual(values[0]["outcome"], "accepted_local_stock")
        self.assertEqual(values[-1]["outcome"], "complete fresh family factor")
        self.assertEqual(audit.stock_arithmetic()["quotient_cases"], 243)

    def test_literal_omitted_peel_rejects(self):
        with self.assertRaisesRegex(ValueError, "complete NODE family coordinates"):
            audit.run_case(audit.CASES[1], self.rt, mutant="lost_peel")

    def test_family_order_rejects_before_merge(self):
        with self.assertRaisesRegex(ValueError, "complete NODE family coordinates"):
            audit.run_case(audit.CASES[0], self.rt, mutant="family_order")

    def test_high_fibres_cannot_be_dropped(self):
        with self.assertRaisesRegex(ValueError, "complete canonical fresh-row split"):
            audit.run_case(audit.CASES[3], self.rt, mutant="lost_high_fibres")
        with self.assertRaisesRegex(ValueError, "complete fresh high factor"):
            audit.run_case(audit.CASES[3], self.rt, mutant="missing_high_stock")

    def test_spectator_is_not_fresh_stock(self):
        with self.assertRaisesRegex(ValueError, "fresh U is separate from spectators"):
            audit.run_case(audit.CASES[0], self.rt, mutant="spectator_as_stock")

    def test_wrong_frozen_prefix_weights_reject(self):
        with self.assertRaisesRegex(ValueError, "complete NODE family coordinates"):
            audit.run_case(audit.CASES[4], self.rt, mutant="wrong_prefix_weight")

    def test_return_port_cannot_alias_borrowed_source(self):
        with self.assertRaisesRegex(ValueError, "empty protected return port"):
            audit.run_case(audit.CASES[0], self.rt, mutant="return_alias")

    def test_noninvolutory_inverse_is_required(self):
        with self.assertRaisesRegex(ValueError, "noninvolutory inverse peel coordinates"):
            audit.noninvolutory_unit_peel(self.rt, wrong_inverse=True)

    def test_three_source_mutations_reject_before_loading(self):
        original = Path.read_bytes
        paths = (
            audit.ROOT / "certificates/selected-result.json",
            audit.SOURCE / "macro_machine.py",
            audit.SOURCE / "inputs/pr2753/predecessor/fresh_rows.py",
        )
        for target in paths:
            with self.subTest(path=target.name):
                def changed(path):
                    data = original(path)
                    return data + b"\nchanged\n" if path == target else data
                with patch.object(Path, "read_bytes", changed):
                    with self.assertRaisesRegex(ValueError, "source pin"):
                        audit.authenticate()

    def test_typed_receipt_comparison(self):
        original = json.loads((HERE / "RESULT.json").read_text())
        changed = copy.deepcopy(original)
        changed["new_kappa"] = 0
        self.assertEqual(changed, original)  # Python's ordinary equality is weaker.
        self.assertFalse(audit.typed_equal(changed, original))
        self.assertTrue(audit.typed_equal(original, copy.deepcopy(original)))


if __name__ == "__main__":
    unittest.main()
