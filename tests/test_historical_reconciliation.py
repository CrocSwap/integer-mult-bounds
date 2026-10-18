"""Reject damaged provenance before extracting historical source snapshots."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'historical_replay', ROOT / 'research/community-historical-five-audit/replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class HistoricalSources(unittest.TestCase):
    def reject(self, name, mutate):
        original = replay.read
        altered = copy.deepcopy(original(name))
        mutate(altered)
        with patch.object(replay, 'read', side_effect=lambda key: altered if key == name else original(key)):
            with self.assertRaises((ValueError, KeyError)):
                replay.sources()

    def test_full_original_diff_cannot_lose_a_file(self):
        self.reject('SOURCES.json', lambda x: x['pull_requests'][0]['changed_files'].pop())

    def test_relabelled_head_is_not_the_original_pr(self):
        self.reject('SOURCES.json', lambda x: x['pull_requests'][0].update(head='0' * 40))

    def test_unsafe_path_and_source_mutation_reject(self):
        for update in ({'path': '../outside'}, {'mode': '120000'}, {'sha256': '0' * 64}):
            with self.subTest(update=update):
                self.reject('SOURCES.json', lambda x: x['pull_requests'][0]['files'][0].update(update))

    def test_missing_disposition_and_wrong_author_reject(self):
        self.reject('DISPOSITIONS.json', lambda x: x['pull_requests'][0]['file_dispositions'].popitem())
        self.reject('DISPOSITIONS.json', lambda x: x['pull_requests'][0]['metadata'].update(author={}))

    def test_artifact_receipt_cannot_bless_changed_certificate(self):
        self.reject('EXECUTION.json', lambda x: x['pull_requests'][0]['regenerated_sha256'].update(
            {'certificates/aligned-paired-network.json': '0' * 64}))

    def test_existing_destination_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as name:
            target = Path(name); sentinel = target / 'keep'; sentinel.write_text('original')
            with patch.object(replay, 'sources', return_value=([], {})), patch(
                'sys.argv', ['replay.py', '--pr', '2', '--extract', name]):
                with self.assertRaisesRegex(ValueError, 'already exists'):
                    replay.main()
            self.assertEqual(sentinel.read_text(), 'original')


if __name__ == '__main__':
    unittest.main()
