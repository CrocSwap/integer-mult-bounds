#!/usr/bin/env python3
"""PR148 source-retention projection regressions; no historical code execution.

ywz65, with OpenAI Codex assistance. Apache-2.0.
The retained source proof and recovered files are Thiago Goulart's PR1572 work.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reconcile_pr_queue as queue

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/pr148-source-retention'


class RetentionProjection(unittest.TestCase):
    def setUp(self):
        self.receipt = json.loads((PACKAGE / 'RESULT.json').read_text())
        self.coverage = json.loads((PACKAGE / 'COVERAGE.json').read_text())
        original = json.loads((ROOT / 'research/pr-reconciliation-20261012/decisions.json').read_text())
        # The stale source-gap decision remains immutable historical evidence.
        self.item = deepcopy(original['decisions']['148'])
        self.item.update(number=148, current_head=self.receipt['head_commit'],
                         evidence=[], draft=True, github_state='OPEN', closure=None)

    def apply(self):
        queue.apply_pr148_retention(self.item, self.receipt, self.coverage)

    def test_actual_receipt_resolves_only_source_gap(self):
        before = deepcopy(self.item)
        self.apply()
        self.assertTrue(self.item['source_retention']['applies_to_current_head'])
        self.assertIn('Whole-PR mathematical review remains open', self.item['unresolved_question'])
        allowed = {'unresolved_question', 'source_retention', 'evidence'}
        self.assertEqual({k: v for k, v in before.items() if k not in allowed},
                         {k: v for k, v in self.item.items() if k not in allowed})
        self.assertEqual(self.item['disposition'], 'partially_reviewed')
        once = deepcopy(self.item)
        self.apply()
        self.assertEqual(self.item, once)

    def test_changed_head_keeps_current_obligation(self):
        self.item.update(current_head='a'*40, disposition='changed_since_review',
                         unresolved_question='Review the new head, including its new source files.')
        before = deepcopy(self.item)
        self.apply()
        self.assertFalse(self.item['source_retention']['applies_to_current_head'])
        for key in ('current_head', 'disposition', 'unresolved_question', 'closure', 'github_state'):
            self.assertEqual(self.item[key], before[key])
        self.assertEqual(self.item['evidence'][-1]['head'], self.receipt['head_commit'])

    def test_later_whole_review_is_not_reopened(self):
        self.item.update(disposition='incorporated', unresolved_question=None,
                         github_state='MERGED', closure={'kind': 'merged'})
        before = deepcopy(self.item)
        self.apply()
        for key in ('disposition', 'unresolved_question', 'github_state', 'closure'):
            self.assertEqual(self.item[key], before[key])

    def test_inconsistent_receipts_fail_before_mutation(self):
        for fault in ('head', 'status', 'missing', 'duplicate', 'count', 'direct', 'recovered'):
            with self.subTest(fault=fault):
                self.setUp()
                if fault == 'head': self.receipt['head_commit'] = 'b'*40
                if fault == 'status': self.receipt['status'] = 'FAILED'
                if fault == 'missing': self.coverage['rows'].pop()
                if fault == 'duplicate': self.coverage['rows'][-1] = self.coverage['rows'][0]
                if fault == 'count': self.receipt['coverage']['recovered'] -= 1
                if fault == 'direct': self.receipt['direct_changed_paths'].pop()
                if fault == 'recovered': self.receipt['recovered_paths'].pop()
                before = deepcopy(self.item)
                with self.assertRaises(ValueError): self.apply()
                self.assertEqual(self.item, before)


if __name__ == '__main__':
    unittest.main()
