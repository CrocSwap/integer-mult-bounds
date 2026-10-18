"""Complete overlap coverage under nested, bounded Discussion first pages."""
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import find_overlap as overlap
sys.path.pop(0)


def node(key):
    return {'id': key, 'body': 'claim ' + key, 'url': 'https://example.invalid/' + key,
            'updatedAt': '2026-10-15T00:00:00Z'}


class DiscussionAPI:
    """An independently paginated backing data set, not scripted responses."""
    def __init__(self, busy=False):
        self.discussions = []
        self.comments = {}
        self.calls = []
        for d in range(23):
            discussion = {**node(f'D{d}'), 'number': d, 'title': f'thread {d}'}
            count = 130 if busy and d == 0 else (30 if busy and d == 12 else 2)
            comments = []
            for c in range(count):
                comment = node(f'D{d}C{c}')
                replies = (115 if c == 0 else 150) if busy and d == 0 and c in (0, 120) else 1
                comment['replies'] = [node(f'D{d}C{c}R{r}') for r in range(replies)]
                self.comments[comment['id']] = comment
                comments.append(comment)
            discussion['comments'] = comments
            self.discussions.append(discussion)

    @staticmethod
    def page(rows, size, cursor=None):
        offset = int(cursor) if cursor is not None else 0
        end = offset + size
        return {'nodes': rows[offset:end],
                'pageInfo': {'hasNextPage': end < len(rows), 'endCursor': str(end)}}

    def __call__(self, query, variables):
        self.calls.append((query, variables))
        sizes = {name: int(size) for name, size in
                 re.findall(r'(discussions|comments|replies)\(first:(\d+)', query)}
        if 'repository(owner:' in query:
            connection = self.page(self.discussions, sizes['discussions'], variables['cursor'])
            connection = copy.deepcopy(connection)
            for discussion in connection['nodes']:
                comments = discussion['comments']
                discussion['comments'] = self.page(comments, sizes['comments'])
                for comment in discussion['comments']['nodes']:
                    comment['replies'] = self.page(comment['replies'], sizes['replies'])
            return {'repository': {'discussions': connection}}
        if '... on DiscussionComment' in query:
            rows = self.comments[variables['id']]['replies']
            return {'node': {'replies': self.page(rows, sizes['replies'], variables['cursor'])}}
        discussion = next(d for d in self.discussions if d['id'] == variables['id'])
        connection = copy.deepcopy(self.page(discussion['comments'], sizes['comments'], variables['cursor']))
        for comment in connection['nodes']:
            comment['replies'] = self.page(comment['replies'], sizes['replies'])
        return {'node': {'comments': connection}}

    def expected(self):
        rows = []
        for discussion in self.discussions:
            common = {key: discussion[key] for key in ('number', 'title')}
            def emit(item, kind):
                rows.append({**common, 'kind': kind, 'body': item['body'],
                             'url': item['url'], 'updated_at': item['updatedAt']})
            emit(discussion, 'discussion')
            for comment in discussion['comments']:
                emit(comment, 'discussion-comment')
                for reply in comment['replies']:
                    emit(reply, 'discussion-reply')
        return rows


class DiscussionBatchTests(unittest.TestCase):
    def test_small_threads_share_only_three_requests(self):
        api = DiscussionAPI()
        with patch.object(overlap, 'graphql', side_effect=api):
            actual = overlap.fetch_discussions()
        self.assertEqual(actual, api.expected())
        self.assertEqual(len(api.calls), 3)

    def test_all_three_pagination_levels_preserve_every_record_in_order(self):
        api = DiscussionAPI(busy=True)
        with patch.object(overlap, 'graphql', side_effect=api):
            actual = overlap.fetch_discussions()
        self.assertEqual(actual, api.expected())
        self.assertEqual(len(actual), len({row['url'] for row in actual}))
        self.assertIn('https://example.invalid/D0C120R149', {row['url'] for row in actual})
        self.assertLess(len(api.calls), len(api.discussions))

    def test_failed_later_pages_preserve_complete_cached_source(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / 'overlap.json'
            old = {'fetched_at': overlap.now(), 'complete_pagination': True,
                   'records': [{'body': 'previous complete snapshot'}]}
            initial = {'schema_version': 1, 'repository': overlap.REPO,
                       'sources': {'discussions': old}}
            for fail_at in (2, 4, 7):
                with self.subTest(fail_at=fail_at):
                    cache.write_text(json.dumps(initial), encoding='utf-8')
                    api = DiscussionAPI(busy=True)
                    def fail(query, variables):
                        if len(api.calls) + 1 == fail_at:
                            raise ValueError('later GraphQL page unavailable')
                        return api(query, variables)
                    with patch.object(overlap, 'graphql', side_effect=fail), \
                         patch.object(overlap, 'gh_json', return_value=[[]]):
                        snapshot, warnings = overlap.remote_snapshot(cache, refresh=True)
                    self.assertTrue(any('discussions: refresh failed' in w for w in warnings))
                    self.assertEqual(snapshot['sources']['discussions'], old)
                    self.assertEqual(json.loads(cache.read_text())['sources']['discussions'], old)


if __name__ == '__main__':
    unittest.main()
