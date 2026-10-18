"""Reject undercharged caller state and unauthenticated or mistyped evidence."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify
from probe import run_case


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = verify.load_sources()

    def test_undercharged_index_context_rejects_and_unwinds(self):
        with self.assertRaisesRegex(ValueError, "caller entry budget"):
            run_case(self.modules, bounds=(0, 11))

    def test_unpriced_retained_slot_at_actual_callback_rejects(self):
        with self.assertRaisesRegex(ValueError, "caller entry budget"):
            run_case(self.modules, retain_extra=True)

    def test_event_capacity_exhaustion_closes_suspended_trace(self):
        with self.assertRaisesRegex(ValueError, "trace event capacity"):
            run_case(self.modules, event_capacity=1)

    def test_exact_event_capacity_accepts_complete_trace(self):
        result = run_case(self.modules, event_capacity=8454)
        self.assertEqual(result["total_trace_events"], 8454)
        self.assertEqual(result["callback_samples"], 12)

    def test_adapter_proof_corruption_rejects(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "package"
            shutil.copytree(verify.PACKAGE, target)
            proof = target / "evidence" / "ADAPTER-LIFETIME.md"
            proof.write_bytes(proof.read_bytes() + b"\nchanged allowance\n")
            with (
                patch.object(verify, "PACKAGE", target),
                self.assertRaisesRegex(ValueError, "adapter proof SHA256"),
            ):
                verify.authenticate()

    def test_source_corruption_rejects_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "package"
            shutil.copytree(verify.PACKAGE, target)
            source = target / "vendor" / "consumer.py"
            source.write_bytes(
                source.read_bytes() + b"\nraise RuntimeError('untrusted')\n"
            )
            with (
                patch.object(verify, "PACKAGE", target),
                self.assertRaisesRegex(ValueError, "source SHA256"),
            ):
                verify.authenticate()

    def test_exact_original_path_rejects_alias(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "package"
            shutil.copytree(verify.PACKAGE, target)
            path = target / "SNAPSHOT.json"
            manifest = json.loads(path.read_text())
            manifest["files"][0]["source_path"] = (
                "research/selected-bit-node/../consumer.py"
            )
            path.write_text(json.dumps(manifest))
            with (
                patch.object(verify, "PACKAGE", target),
                self.assertRaisesRegex(ValueError, "original source path"),
            ):
                verify.authenticate()

    def test_typed_receipt_rejects_boolean(self):
        with self.assertRaisesRegex(ValueError, "typed receipt"):
            verify.check_receipt({"index": 1}, {"index": True})

    def test_wrong_composed_receipt_rejects(self):
        with self.assertRaisesRegex(ValueError, "typed receipt"):
            verify.check_receipt({"index": 34}, {"index": 33})

    def test_missing_source_inventory_rejects(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "package"
            shutil.copytree(verify.PACKAGE, target)
            path = target / "SNAPSHOT.json"
            manifest = json.loads(path.read_text())
            manifest["files"].pop()
            path.write_text(json.dumps(manifest))
            with (
                patch.object(verify, "PACKAGE", target),
                self.assertRaisesRegex(ValueError, "complete source inventory"),
            ):
                verify.authenticate()


if __name__ == "__main__":
    unittest.main()
