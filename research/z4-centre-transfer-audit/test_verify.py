#!/usr/bin/env python3
"""Behavioral checks for map-versus-cost and restoration boundaries."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('verify.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class BoundaryTests(unittest.TestCase):
    def test_equal_maps_can_have_different_child_invoices(self):
        trace = audit.echo(audit.batch([0,1,0], [0,1]))
        extra = trace + [('child',0,1), ('child',0,-1)]
        self.assertEqual(audit.typed_apply(trace), audit.typed_apply(extra))
        charges = {key:{8:4} for key in audit.child_counts(trace)}
        self.assertEqual(audit.tariff(trace,charges), {8:16})
        self.assertEqual(audit.tariff(extra,charges), {8:24})

    def test_extra_complete_phase_cycle_preserves_contract(self):
        trace = audit.echo(audit.batch([0,1,0], [0,1]))
        extra = [('P',4,1), ('Q',-4,1)] + trace
        self.assertEqual(audit.typed_apply(trace), audit.typed_apply(extra))
        self.assertEqual(audit.child_counts(trace), audit.child_counts(extra))

    def test_wrong_source_octet_fails_even_with_restored_workspace(self):
        wrong = audit.typed_apply(audit.echo(audit.batch([0,1,0], [0,2])))
        self.assertNotEqual(wrong, audit.expected([0,1]))
        self.assertEqual(wrong[8:], audit.identity()[8:])

    def test_missing_copy_out_corrupts_output_and_dirt(self):
        body = audit.batch([0,1,0], [0,1])
        wrong = audit.typed_apply([('copy',0,1)] + body + audit.inverse(body))
        self.assertNotEqual(wrong[32:], audit.identity()[32:])
        # This control deliberately does NOT claim that the output is correct:
        # the missing subtraction cancels the output increment in this word.
        self.assertNotEqual(wrong[:8], audit.expected([0,1])[:8])

    def test_same_counts_give_equal_arbitrary_nonnegative_tariffs(self):
        joint = audit.echo(audit.batch([0,1,0], [0,1]))
        separate = audit.echo(audit.batch([0,0], [0])) + audit.echo(audit.batch([0,0], [1]))
        for zero_key in audit.child_counts(joint):
            charges = {key:({} if key==zero_key else {1:2,8:3,48:1})
                       for key in audit.child_counts(joint)}
            self.assertEqual(audit.tariff(joint,charges), audit.tariff(separate,charges))


if __name__ == '__main__':
    unittest.main()
