"""Queue scheduling must never turn cached triage into scientific approval."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('pr_intake', Path(__file__).resolve().parents[1] / 'scripts/pr_intake.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def live(n=1, head='a' * 40, draft=False):
    return dict(number=n, headRefOid=head, isDraft=draft, title='contribution')


def state(status='waiting_revision'):
    return dict(schema_version=1, pull_requests=[dict(number=1, head='a' * 40,
                status=status, reason='Concrete unresolved source obligation', evidence=['review.json'],
                policy_version=1, watch_paths={'review.json': 'b' * 40}, watch_prs={})])


class IntakeTests(unittest.TestCase):
    def run_plan(self, s=None, prs=None, tree=None, **kw):
        return m.plan(s or state(), prs if prs is not None else [live()],
                      tree if tree is not None else {'review.json': 'b' * 40}, **kw)

    def test_unchanged_hold_is_not_selected(self):
        s = state(); before = copy.deepcopy(s)
        r = self.run_plan(s)
        self.assertEqual(r['selected'], [])
        self.assertEqual(r['counts'], {'waiting_revision': 1})
        self.assertEqual(s, before)

    def test_head_evidence_and_policy_changes_reactivate(self):
        self.assertEqual(self.run_plan(prs=[live(head='c' * 40)])['selected'][0]['lane'], 'reactivated')
        self.assertEqual(self.run_plan(tree={})['selected'][0]['lane'], 'reactivated')
        s = state(); s['pull_requests'][0]['policy_version'] = 0
        self.assertEqual(self.run_plan(s)['selected'][0]['lane'], 'reactivated')

    def test_dependency_change_and_closure_reactivate(self):
        s = state(); s['pull_requests'][0]['watch_prs'] = {'2': 'd' * 40}
        self.assertEqual(self.run_plan(s, [live(), live(2, 'd' * 40)])['pull_requests'][0]['lane'], 'waiting_revision')
        self.assertEqual(self.run_plan(s, [live(), live(2, 'e' * 40)])['pull_requests'][0]['lane'], 'reactivated')
        self.assertEqual(self.run_plan(s)['selected'][0]['lane'], 'reactivated')

    def test_pending_work_never_becomes_dormant(self):
        self.assertEqual(len(self.run_plan(state('pending_review'))['selected']), 1)
        self.assertEqual(len(self.run_plan(state('ready_to_integrate'))['selected']), 1)

    def test_explicit_wake_but_no_automatic_replay(self):
        self.assertFalse(self.run_plan(state('deferred_replay'))['selected'])
        self.assertEqual(self.run_plan(state('deferred_replay'), wake=[1])['selected'][0]['lane'], 'reactivated')

    def test_drafts_closed_and_new(self):
        self.assertFalse(self.run_plan(prs=[live(draft=True)], wake=[1])['selected'])
        self.assertEqual(self.run_plan(prs=[])['no_longer_open'], [1])
        self.assertEqual(self.run_plan(prs=[live(2)])['selected'][0]['lane'], 'new')

    def test_chunk_limit_does_not_drop_queue(self):
        r = self.run_plan(prs=[live(n) for n in range(2, 203)])
        self.assertEqual(len(r['selected']), 100)
        self.assertEqual(r['remaining_actionable'], 101)
        self.assertEqual(r['open_count'], 201)

    def test_malformed_state_fails_closed(self):
        for change in ('status', 'head', 'reason', 'watch_paths'):
            s = state(); s['pull_requests'][0][change] = {'../bad': None} if change == 'watch_paths' else ''
            with self.assertRaises(ValueError): self.run_plan(s)
        with self.assertRaises(ValueError): self.run_plan(prs=[live(), live()])
        with self.assertRaises(ValueError): self.run_plan(limit=101)


if __name__ == '__main__':
    unittest.main()
