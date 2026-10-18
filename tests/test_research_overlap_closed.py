"""Optional closed/merged body coverage, pagination failures and state changes."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import find_overlap as overlap
sys.path.pop(0)


def row(number, state='closed', updated='2026-10-14T00:00:00Z', body='needle'):
    return {'number': number, 'title': 'Prior contribution', 'body': body,
            'html_url': 'https://example.invalid/pull/' + str(number),
            'head': {'sha': str(number).zfill(40)}, 'updated_at': updated,
            'state': state, 'draft': False}


def cli(open_pages, closed_pages, seen):
    def run(argv, **kwargs):
        seen.append(argv)
        pages = closed_pages if any('state=closed' in part for part in argv) else open_pages
        if isinstance(pages, Exception):
            raise pages
        if '--paginate' not in argv:
            pages = pages[:1]
        return subprocess.CompletedProcess(argv, 0, '\n'.join(json.dumps(p) for p in pages) + '\n', '')
    return run


class ClosedOverlapTests(unittest.TestCase):
    def run_report(self, cache, argv=(), closed_pages=None, open_pages=None, seen=None):
        output = io.StringIO()
        with (patch.object(overlap, 'ROOT', cache.parent / 'empty-repo'),
              patch.object(sys, 'argv', ['find_overlap.py', 'needle', '--json', '--cache', str(cache), *argv]),
              patch.object(overlap.subprocess, 'run', side_effect=cli(open_pages or [[]], closed_pages or [[]], seen if seen is not None else [])),
              patch.object(overlap, 'fetch_discussions', return_value=[]),
              contextlib.redirect_stdout(output)):
            overlap.main()
        return json.loads(output.getvalue())

    def test_later_closed_page_is_searched_with_explicit_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            seen = []
            report = self.run_report(Path(tmp) / 'cache.json', ['--include-closed'],
                                     [[row(1, body='unrelated')], [row(2)]], seen=seen)
            self.assertEqual(report['warnings'], [])
            self.assertEqual(report['coverage']['closed_prs']['records'], 2)
            self.assertTrue(report['coverage']['closed_prs']['complete_pagination'])
            self.assertEqual([m['number'] for m in report['matches']], [2])
            self.assertEqual(report['matches'][0]['state'], 'closed')
            request = next(a for a in seen if any('state=closed' in p for p in a))
            self.assertIn('--paginate', request)
            self.assertNotIn('--slurp', request)

    def test_default_does_not_fetch_or_search_cached_closed_bodies(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'cache.json'
            self.run_report(cache, ['--include-closed'], [[row(2)]])
            seen = []
            report = self.run_report(cache, seen=seen)
            self.assertEqual(seen, [])
            self.assertNotIn('closed_prs', report['coverage'])
            self.assertEqual(report['matches_total'], 0)

    def test_offline_opt_in_reports_missing_closed_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'cache.json'
            self.run_report(cache)
            seen = []
            report = self.run_report(cache, ['--include-closed', '--offline'], seen=seen)
            self.assertEqual(seen, [])
            self.assertIsNone(report['coverage']['closed_prs'])
            self.assertTrue(any('closed_prs: no usable' in w for w in report['warnings']))

    def test_failed_later_page_preserves_complete_closed_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'cache.json'
            self.run_report(cache, ['--include-closed'], [[row(2)]])
            original = json.loads(cache.read_text())['sources']['closed_prs']
            failure = subprocess.CalledProcessError(1, ['gh'], output=json.dumps([row(9)]), stderr='later page failed')
            report = self.run_report(cache, ['--include-closed', '--refresh'], failure)
            self.assertTrue(any('closed_prs: refresh failed' in w for w in report['warnings']))
            self.assertEqual(json.loads(cache.read_text())['sources']['closed_prs'], original)
            self.assertEqual([m['number'] for m in report['matches']], [2])

    def test_failed_first_closed_fetch_cannot_claim_complete_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            failure = subprocess.CalledProcessError(1, ['gh'], stderr='denied')
            report = self.run_report(Path(tmp) / 'cache.json', ['--include-closed'], failure)
            self.assertIsNone(report['coverage']['closed_prs'])
            self.assertTrue(any('closed_prs: no usable' in w for w in report['warnings']))

    def test_state_change_keeps_one_newest_head_and_open_tie(self):
        for open_time, closed_time, expected in [('2026-10-14T00:00:00Z', '2026-10-15T00:00:00Z', 'closed'),
                                                 ('2026-10-15T00:00:00Z', '2026-10-14T00:00:00Z', 'open'),
                                                 ('2026-10-15T00:00:00Z', '2026-10-15T00:00:00Z', 'open')]:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as tmp:
                report = self.run_report(Path(tmp) / 'cache.json', ['--include-closed'],
                                         [[row(2, updated=closed_time)]], [[row(2, state='open', updated=open_time)]])
                self.assertEqual(report['matches_total'], 1)
                self.assertEqual(report['matches'][0]['state'], expected)

    def test_empty_closed_repository_is_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self.run_report(Path(tmp) / 'cache.json', ['--include-closed'])
            self.assertEqual(report['coverage']['closed_prs']['records'], 0)
            self.assertTrue(report['coverage']['closed_prs']['complete_pagination'])

    def test_closed_path_request_fails_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            seen = []
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                self.run_report(Path(tmp) / 'cache.json', ['--include-closed', '--path', 'research/*'], seen=seen)
            self.assertEqual(raised.exception.code, 2)
            self.assertEqual(seen, [])


if __name__ == '__main__':
    unittest.main()
