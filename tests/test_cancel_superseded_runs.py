"""Cancellation must preserve current work and report failed API requests."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cancel_superseded_runs', ROOT / 'scripts/cancel_superseded_runs.py')
cancel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cancel)


def run_record(number, head='old', event='pull_request', **fields):
    return dict(id=number, event=event, path='.github/workflows/verify.yml',
                head_sha=head, created_at='2026-10-14T00:00:00Z', status='queued',
                pull_requests=[{'number': 42}], **fields)


class CandidateSelection(unittest.TestCase):
    def test_only_identified_outdated_pull_request_heads_are_candidates(self):
        records = [run_record(1), run_record(2, head='current'),
                   run_record(3, event='push'), run_record(4, event='schedule'),
                   run_record(5, event='workflow_dispatch'), run_record(6), run_record(7)]
        identities = {i: ('.github/workflows/verify.yml', 42) for i in range(1, 6)}
        identities[7] = ('.github/workflows/verify.yml', 43)
        result = cancel.superseded(records, identities, {42: 'current', 43: None})
        self.assertEqual([r['id'] for r in result], [1])

    def test_direct_identity_requires_exactly_one_pull_request(self):
        record = run_record(1)
        with patch.object(cancel, 'api') as api:
            self.assertEqual(cancel.identify('base/repo', record, {}), (record['path'], 42))
            record['pull_requests'].append({'number': 43})
            self.assertIsNone(cancel.identify('base/repo', record, {}))
            record['pull_requests'] = []
            self.assertIsNone(cancel.identify('base/repo', record, {}))
            api.assert_not_called()

    def test_fork_lookup_binds_both_repository_and_branch_and_caches(self):
        record = run_record(1, head_repository={'full_name': 'fork/repo'}, head_branch='topic')
        record['pull_requests'] = []
        wrong_repo = {'number': 50, 'head': {'ref': 'topic', 'repo': {'full_name': 'fork/other'}}}
        wrong_branch = {'number': 51, 'head': {'ref': 'other', 'repo': {'full_name': 'fork/repo'}}}
        correct = {'number': 52, 'head': {'ref': 'topic', 'repo': {'full_name': 'fork/repo'}}}
        cache = {}
        with patch.object(cancel, 'api', return_value=[[wrong_repo, wrong_branch, correct]]) as api:
            for _ in range(2):
                self.assertEqual(cancel.identify('base/repo', record, cache), (record['path'], 52))
            api.assert_called_once()
            self.assertIn('head=fork%3Atopic', api.call_args.args[0])

    def test_ambiguous_fork_lookup_is_kept(self):
        record = run_record(1, head_repository={'full_name': 'fork/repo'}, head_branch='topic')
        record['pull_requests'] = []
        candidates = [{'number': n, 'head': {'ref': 'topic', 'repo': {'full_name': 'fork/repo'}}}
                      for n in (42, 43)]
        with patch.object(cancel, 'api', return_value=[candidates]):
            self.assertIsNone(cancel.identify('base/repo', record, {}))

    def test_current_head_comes_from_pull_request_and_is_cached(self):
        cache = {}
        with patch.object(cancel, 'api', return_value=[{'head': {'sha': 'current'}}]) as api:
            self.assertEqual(cancel.current_head('base/repo', 42, cache), 'current')
            self.assertEqual(cancel.current_head('base/repo', 42, cache), 'current')
            api.assert_called_once_with('repos/base/repo/pulls/42')


class Command(unittest.TestCase):
    def execute(self, args, records, returncodes=()):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(cancel, 'list_runs', side_effect=[records, [], [], []]), \
                patch.object(cancel, 'current_head', return_value='current'), \
                patch.object(cancel.subprocess, 'run',
                             side_effect=[SimpleNamespace(returncode=c) for c in returncodes]) as post, \
                redirect_stdout(stdout), redirect_stderr(stderr):
            code = cancel.main(['--repo', 'base/repo', '--created', '2026-10-14'] + args)
        return code, post.call_args_list, stdout.getvalue(), stderr.getvalue()

    def test_dry_run_never_posts(self):
        code, calls, out, err = self.execute([], [run_record(1)])
        self.assertEqual(code, 0)
        self.assertEqual(calls, [])
        self.assertIn('would cancel run 1', out)
        self.assertEqual(err, '')

    def test_limit_bounds_cancellation(self):
        code, calls, out, err = self.execute(['--cancel', '--limit', '1'],
                                           [run_record(1), run_record(2)], [0])
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].args[0],
                         ['gh', 'api', '-X', 'POST', 'repos/base/repo/actions/runs/1/cancel'])
        self.assertNotIn('CANCEL run 2', out)
        self.assertEqual(err, '')

    def test_zero_limit_cancels_all_outdated_heads_only(self):
        records = [run_record(1), run_record(2, head='current'), run_record(3, event='push'),
                   run_record(4, event='schedule'), run_record(5, event='workflow_dispatch'),
                   run_record(6)]
        code, calls, out, err = self.execute(['--cancel', '--limit', '0'], records, [0, 0])
        self.assertEqual(code, 0)
        self.assertEqual([c.args[0][-1] for c in calls],
                         ['repos/base/repo/actions/runs/1/cancel', 'repos/base/repo/actions/runs/6/cancel'])
        self.assertEqual(err, '')

    def test_failed_post_does_not_prevent_other_cancellations_and_fails_command(self):
        code, calls, out, err = self.execute(['--cancel'], [run_record(1), run_record(2)], [1, 0])
        self.assertEqual(code, 1)
        self.assertEqual(len(calls), 2)
        self.assertIn('Cancellation failed for run(s): 1', err)
        self.assertNotIn('run(s): 1, 2', err)

    def test_negative_limit_is_rejected_before_querying_or_posting(self):
        with patch.object(cancel, 'list_runs') as query, patch.object(cancel.subprocess, 'run') as post, \
                redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit) as error:
            cancel.main(['--repo', 'base/repo', '--created', '2026-10-14', '--cancel', '--limit', '-1'])
        self.assertEqual(error.exception.code, 2)
        self.assertIn('--limit must be nonnegative', err.getvalue())
        query.assert_not_called()
        post.assert_not_called()


if __name__ == '__main__':
    unittest.main()
