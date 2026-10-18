"""Changed-path matches beyond the first page and honest incomplete snapshots."""
import copy
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import find_overlap as overlap
sys.path.pop(0)


def page(paths, start=0):
    end = start + 100
    return {'nodes': [{'path': path} for path in paths[start:end]],
            'pageInfo': {'hasNextPage': end < len(paths), 'endCursor': str(end)}}


def fixture():
    paths = [f'research/case/{i:03d}.py' for i in range(250)]
    pull = {'number': 42, 'headRefOid': 'a' * 40, 'baseRefOid': 'd' * 40, 'changedFiles': len(paths), 'files': page(paths)}
    return paths, pull


class PullFilePages(unittest.TestCase):
    def test_late_path_is_searchable_after_all_pages(self):
        paths, pull = fixture()
        calls = []
        def api(query, variables):
            calls.append(variables)
            self.assertEqual(variables['number'], 42)
            continuation = {**pull, 'files': page(paths, int(variables['cursor']))}
            return {'repository': {'pullRequest': continuation}}
        with patch.object(overlap, 'graphql', side_effect=api):
            row = overlap.pull_file_record(pull)
        self.assertEqual(row, {'number': 42, 'head': 'a' * 40, 'base': 'd' * 40, 'paths': paths, 'truncated': False})
        self.assertEqual([c['cursor'] for c in calls], ['100', '200'])
        matches = overlap.path_report([], [row], ['research/case/249.py'])
        self.assertEqual(matches[0]['matched_paths'], [paths[-1]])
        self.assertFalse(matches[0]['truncated'])

    def test_head_change_count_change_missing_page_and_repeated_cursor_fail(self):
        paths, pull = fixture()
        good = {**pull, 'files': page(paths, 100)}
        variants = []
        for key, value in [('headRefOid', 'b' * 40), ('baseRefOid', 'e' * 40), ('baseRefOid', None), ('changedFiles', 251), ('files', None)]:
            variants.append({**good, key: value})
        stuck = copy.deepcopy(good)
        stuck['files']['pageInfo']['endCursor'] = '100'
        variants.append(stuck)
        for changed in variants:
            with self.subTest(changed=changed), patch.object(overlap, 'graphql',
                    return_value={'repository': {'pullRequest': changed}}):
                with self.assertRaises(ValueError):
                    overlap.pull_file_record(pull)

    def test_unavailable_or_short_response_never_claims_complete(self):
        _, pull = fixture()
        for connection in (None, {'nodes': [{'path': 'only.py'}],
                                 'pageInfo': {'hasNextPage': False}}):
            with self.subTest(connection=connection), patch.object(overlap, 'graphql',
                    side_effect=AssertionError('unexpected request')):
                row = overlap.pull_file_record({**pull, 'files': connection})
                self.assertTrue(row['truncated'])

    def test_continuation_failure_preserves_previous_complete_cache(self):
        paths, pull = fixture()
        listing = {'repository': {'pullRequests': {'nodes': [pull],
                   'pageInfo': {'hasNextPage': False}}}}
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / 'cache.json'
            old = {'records': [{'number': 7, 'paths': ['keep.py'], 'truncated': False}],
                   'fetched_at': overlap.now(), 'complete_pagination': True}
            cache.write_text(json.dumps({'schema_version': 1, 'repository': overlap.REPO,
                                        'sources': {'pr_files': old}}), encoding='utf-8')
            with patch.object(overlap, 'graphql', side_effect=[listing, ValueError('late failure')]), \
                 patch.object(overlap, 'gh_json', return_value=[[]]), \
                 patch.object(overlap, 'fetch_discussions', return_value=[]):
                snapshot, warnings = overlap.remote_snapshot(cache, refresh=True, need_files=True)
            self.assertTrue(any('pr_files: refresh failed' in w for w in warnings))
            self.assertEqual(snapshot['sources']['pr_files'], old)
            self.assertEqual(json.loads(cache.read_text())['sources']['pr_files'], old)

    def test_path_heads_are_not_borrowed_from_a_different_body_snapshot(self):
        body = {'kind': 'pr', 'number': 42, 'head': 'b' * 40, 'title': 'needle',
                'body': '', 'url': 'https://example.invalid/42'}
        files = {'number': 42, 'head': 'a' * 40, 'paths': ['old.py'], 'truncated': False}
        match = overlap.path_report([body], [files], ['old.py'])[0]
        self.assertEqual(match['head'], 'a' * 40)
        self.assertEqual(match['body_head'], 'b' * 40)
        self.assertFalse(match['head_matches'])
        body['head'] = 'a' * 40
        self.assertTrue(overlap.path_report([body], [files], ['old.py'])[0]['head_matches'])
        self.assertEqual(overlap.path_report([], [files], ['old.py'])[0]['head'], 'a' * 40)

    def test_legacy_file_cache_does_not_acquire_a_head_from_body_metadata(self):
        body = {'kind': 'pr', 'number': 42, 'head': 'b' * 40, 'title': 'needle'}
        files = {'number': 42, 'paths': ['old.py'], 'truncated': False}
        match = overlap.path_report([body], [files], ['old.py'])[0]
        self.assertIsNone(match['head'])
        self.assertEqual(match['body_head'], 'b' * 40)
        self.assertFalse(match['head_matches'])

    def test_cli_warns_about_unverified_heads_even_without_a_path_hit(self):
        body = {'kind': 'pr', 'number': 42, 'head': 'b' * 40, 'title': 'needle',
                'body': '', 'url': 'https://example.invalid/42'}
        for file_head in ('a' * 40, None):
            with self.subTest(file_head=file_head), tempfile.TemporaryDirectory() as directory:
                cache = Path(directory) / 'cache.json'
                files = {'number': 42, 'paths': ['old.py'], 'truncated': False}
                if file_head:
                    files['head'] = file_head
                sources = {name: {'fetched_at': overlap.now(), 'complete_pagination': True,
                                  'records': rows}
                           for name, rows in [('open_prs', [body]), ('discussions', []),
                                              ('pr_files', [files])]}
                raw = json.dumps({'schema_version': 1, 'repository': overlap.REPO,
                                  'sources': sources}).encode()
                cache.write_bytes(raw)
                for terms, pattern in [([], 'missing.py'), (['needle'], 'old.py')]:
                    output = io.StringIO()
                    argv = ['find_overlap.py', *terms, '--path', pattern, '--offline',
                            '--json', '--cache', str(cache)]
                    with (patch.object(overlap, 'ROOT', Path(directory) / 'repo'),
                          patch.object(sys, 'argv', argv), contextlib.redirect_stdout(output),
                          patch.object(overlap, 'gh_json', side_effect=AssertionError('network'))):
                        overlap.main()
                    report = json.loads(output.getvalue())
                    self.assertEqual(report['coverage']['pr_files']['unverified_heads'], [42])
                    self.assertTrue(any('file-head binding unverified' in w for w in report['warnings']))
                    if terms:
                        match = report['matches'][0]
                        self.assertEqual(match['head'], file_head)
                        self.assertEqual(match['body_head'], body['head'])
                        self.assertFalse(match['head_matches'])
                    else:
                        self.assertEqual(report['path_matches_total'], 0)
                    self.assertEqual(cache.read_bytes(), raw)

    def test_cli_covers_missing_inventory_and_matching_head_control(self):
        body = {'kind': 'pr', 'number': 42, 'head': 'a' * 40, 'base': 'd' * 40, 'title': 'needle', 'body': ''}
        bound = {'number': 42, 'head': 'a' * 40, 'base': 'd' * 40, 'paths': ['new.py'], 'truncated': False}
        for files, expected in [([], [42]), ([bound], [])]:
            with self.subTest(files=files), tempfile.TemporaryDirectory() as directory:
                sources = {name: {'fetched_at': overlap.now(), 'complete_pagination': True,
                                  'records': rows}
                           for name, rows in [('open_prs', [body]), ('discussions', []),
                                              ('pr_files', files)]}
                cache = Path(directory) / 'cache.json'
                cache.write_text(json.dumps({'schema_version': 1, 'repository': overlap.REPO,
                                             'sources': sources}), encoding='utf-8')
                output = io.StringIO()
                with (patch.object(overlap, 'ROOT', Path(directory) / 'repo'),
                      patch.object(sys, 'argv', ['find_overlap.py', '--path', 'new.py',
                                                '--json', '--cache', str(cache)]),
                      contextlib.redirect_stdout(output),
                      patch.object(overlap, 'gh_json', side_effect=AssertionError('network'))):
                    overlap.main()
                report = json.loads(output.getvalue())
                self.assertEqual(report['coverage']['pr_files']['unverified_heads'], expected)
                if expected:
                    self.assertTrue(any('file-head binding unverified' in w for w in report['warnings']))
                else:
                    self.assertEqual(report['warnings'], [])
                    self.assertTrue(report['path_matches'][0]['head_matches'])

    def test_failed_legacy_refresh_preserves_unknown_head_instead_of_relabelling(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / 'cache.json'
            old = {'fetched_at': overlap.now(), 'complete_pagination': True,
                   'records': [{'number': 42, 'paths': ['old.py'], 'truncated': False}]}
            sources = {name: {'fetched_at': overlap.now(), 'complete_pagination': True, 'records': []}
                       for name in ('open_prs', 'discussions')}
            sources['pr_files'] = old
            raw = json.dumps({'schema_version': 1, 'repository': overlap.REPO, 'sources': sources})
            cache.write_text(raw, encoding='utf-8')
            with patch.object(overlap, 'fetch_pr_files', side_effect=ValueError('later page failed')):
                snapshot, warnings = overlap.remote_snapshot(cache, need_files=True)
            self.assertTrue(any('pr_files: refresh failed' in w for w in warnings))
            self.assertEqual(snapshot['sources']['pr_files'], old)
            self.assertEqual(cache.read_text(encoding='utf-8'), raw)

    def test_fresh_legacy_cache_is_refetched_without_forcing_a_body_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / 'cache.json'
            sources = {name: {'fetched_at': overlap.now(), 'complete_pagination': True,
                              'records': rows}
                       for name, rows in [('open_prs', []), ('discussions', []),
                                          ('pr_files', [{'number': 42, 'paths': ['old.py']}])]}
            cache.write_text(json.dumps({'schema_version': 1, 'repository': overlap.REPO,
                                         'sources': sources}), encoding='utf-8')
            replacement = [{'number': 42, 'head': 'c' * 40, 'base': 'd' * 40, 'paths': ['new.py'], 'truncated': False}]
            with (patch.object(overlap, 'gh_json', side_effect=AssertionError('body refresh')),
                  patch.object(overlap, 'fetch_pr_files', return_value=replacement) as fetch):
                snapshot, warnings = overlap.remote_snapshot(cache, need_files=True)
            fetch.assert_called_once_with()
            self.assertEqual(warnings, [])
            self.assertEqual(snapshot['sources']['pr_files']['records'], replacement)


if __name__ == '__main__':
    unittest.main()
