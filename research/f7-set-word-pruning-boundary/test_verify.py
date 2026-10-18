"""Failure controls for the source-bound set/word interface audit."""

import copy
import json
from pathlib import Path
import types
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
audit = types.ModuleType("boundary_audit")
audit.__file__ = str(HERE / "verify.py")
exec(compile((HERE / "verify.py").read_bytes(), audit.__file__, "exec"), audit.__dict__)


class BoundaryControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = audit.source_bytes()

    def test_actual_source_counterexamples_and_controls(self):
        subject = audit.load_bytes(self.sources[audit.OLD], audit.OLD)
        witnesses = audit.fixed_witnesses(subject)
        self.assertEqual(witnesses["degree_counterexample"]["filtered_covers"], 0)
        self.assertTrue(all(audit.controls(self.sources[audit.OLD]).values()))

    def test_changed_source_is_rejected_before_execution(self):
        original = Path.read_bytes
        target = audit.ROOT / audit.OLD

        def changed(path):
            data = original(path)
            return data + b"\n# corrupted audit subject\n" if path == target else data

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(audit.AuditFailure, "source hash mismatch"):
                audit.source_bytes()

    def test_wrong_partition_and_duplicate_output_are_rejected(self):
        with self.assertRaisesRegex(audit.AuditFailure, "wrong bit-0 partition"):
            audit.canonical_results([((0, 1), (2, 3))], 2, (2, 2))
        row = ((0, 2), (1, 3))
        with self.assertRaisesRegex(audit.AuditFailure, "duplicate returned cover"):
            audit.canonical_results([row, row], 2, (2, 2))

    def test_set_domain_catches_balanced_budget_mutant(self):
        data = self.sources[audit.OLD]
        anchor = b"budget = A + B - even_nonzero"
        replacement = b"budget = 2 * (((s+t)//2)*((s+t)//2-1)//2) - even_nonzero"
        mutant = audit.load_bytes(data.replace(anchor, replacement), audit.OLD)
        with self.assertRaisesRegex(audit.AuditFailure, "set disagreement"):
            audit.exhaustive_sets(mutant)

    def test_source_impact_rejects_new_degree_filter_caller(self):
        sources = self.sources.copy()
        path = "research/universal-f7-singleton-seedb859517b/search.py"
        sources[path] = sources[path].replace(
            b"joint_covers(5, splits10)",
            b"joint_covers(5, splits10, require_min_degree=True)")
        with self.assertRaisesRegex(audit.AuditFailure, "retained caller enables"):
            audit.source_impact(sources)

    def test_receipt_rejects_changed_count_or_missing_case(self):
        expected = json.loads((HERE / "RESULT.json").read_text())
        for kind in ("count", "case"):
            changed = copy.deepcopy(expected)
            if kind == "count":
                changed["small_domain"][3]["covers"] += 1
            else:
                changed["small_domain"][3]["cases"].pop()
            with self.assertRaisesRegex(audit.AuditFailure, "receipt mismatch"):
                audit.compare_receipt(changed, expected)


if __name__ == "__main__":
    unittest.main()
