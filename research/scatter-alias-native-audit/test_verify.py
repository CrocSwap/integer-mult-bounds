#!/usr/bin/env python3
"""Failure controls for the independent alias audit; Apache-2.0.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
"""
import copy
import json
from pathlib import Path
import tempfile
import types
import unittest

PACKAGE = Path(__file__).resolve().parent
# Read source explicitly, so a stale bytecode cache cannot substitute the audit.
audit = types.ModuleType("alias_audit")
audit.__file__ = str(PACKAGE / "verify.py")
exec(compile((PACKAGE / "verify.py").read_bytes(), audit.__file__, "exec"), audit.__dict__)


def toy():
    # n=4, v=1: target1 += source0, then two separate copies of dirty helper2.
    return [(1, 1, 0, 1, 0, 1),
            (2, 2, 4, 0, 0, 7), (1, 1, 4, 1, 0, 3), (3, 2, 4, 0, 0, 0),
            (2, 2, 4, 0, 0, 7), (1, 1, 4, 1, 0, 3), (3, 2, 4, 0, 0, 0)]


class Controls(unittest.TestCase):
    def test_alias_cancels_but_every_copy_is_charged(self):
        differences, invoice = audit.scalar_and_invoice(toy(), n=4, v=1)
        self.assertEqual(differences, [])
        self.assertEqual(invoice["copies"], 2)
        self.assertEqual(invoice["copy_rank_sum"], 14)
        self.assertEqual(invoice["adds"], 3)
        self.assertEqual(invoice["scatter_adds"], 2)

    def test_unpaired_and_distinct_helper_columns(self):
        rows = toy()
        del rows[5]
        self.assertEqual(audit.scalar_and_invoice(rows, n=4, v=1)[0],
                         [{"output": 1, "input_columns": [2]}])
        rows = list(toy())
        rows[4] = (2, 3, 4, 0, 0, 7)
        rows[6] = (3, 3, 4, 0, 0, 0)
        self.assertEqual(audit.scalar_and_invoice(rows, n=4, v=1)[0],
                         [{"output": 1, "input_columns": [2, 3]}])

    def test_lifecycle_and_alignment_failures(self):
        rows = toy()
        rows[-1] = (3, 3, 4, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "ERASE source binding"):
            audit.scalar_and_invoice(rows, n=4, v=1)
        with self.assertRaisesRegex(ValueError, "temporary not closed"):
            audit.scalar_and_invoice(toy()[:-1], n=4, v=1)
        raw = b"".join(audit.RECORD.pack(*r) for r in toy())
        with self.assertRaisesRegex(ValueError, "record alignment"):
            audit.read_records(raw[:-1])

    def test_prefix_counts_cancelling_adds_in_both_directions(self):
        self.assertEqual(audit.prefix_invoice(toy(), n=4),
                         {"forward": "4", "reverse": "4", "payload": "65536",
                          "bits": 17, "below_2_104": True})
        rows = list(toy())
        rows[5] = (1, 1, 4, -1, 0, 3)
        self.assertEqual(audit.prefix_invoice(rows, n=4), audit.prefix_invoice(toy(), n=4))

    def test_corrupted_exporter_rejected_before_execution(self):
        data = audit.sources()
        with tempfile.TemporaryDirectory(prefix="alias-source-control-") as temporary:
            root = Path(temporary)
            audit.snapshot(data, root)
            path = root / audit.EXPORT
            path.write_bytes(path.read_bytes() + b"\n# changed source\n")
            with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                audit.sources(root)

    def test_native_invoice_cannot_refund_alias_copy(self):
        # This uses the saved native receipt solely as a test fixture.
        data = json.loads((PACKAGE / "NATIVE.json").read_bytes())
        result = data["native"]["fixtures"]["balanced_alias"]["10"]
        local = data["fixtures"]["balanced_alias"]
        audit.reconcile_native(result, local, 10)
        wrong = copy.deepcopy(result)
        wrong["legality"]["receipt"]["rank_mass"] -= 7
        with self.assertRaisesRegex(ValueError, "native invoice mismatch"):
            audit.reconcile_native(wrong, local, 10)
        wrong = copy.deepcopy(result)
        wrong["columns"]["receipt"]["fresh_center_copies"] = 45
        with self.assertRaisesRegex(ValueError, "five-stage COPY bill"):
            audit.reconcile_native(wrong, local, 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
