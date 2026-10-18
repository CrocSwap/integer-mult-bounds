"""Evidence contracts reject version drift and incomplete replay reuse."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_replay_coverage as coverage


class ContractVersion(unittest.TestCase):
    def test_current_producer_is_bound(self):
        contract = coverage.contract()
        self.assertEqual(contract['id'], 'pr741-sw4-v1')
        self.assertEqual(len(contract['stages']), 22)
        self.assertEqual(len(contract['artifacts']), 44)

    def test_changed_contract_and_producer_versions_fail(self):
        original = coverage.read(coverage.CONTRACT)
        mutations = [
            lambda x: x.update(schema='integer-mult-replay-coverage-v2'),
            lambda x: x.update(producer_sha256='0' * 64),
            lambda x: x['stages'].reverse(),
            lambda x: x['artifacts'].pop(),
            lambda x: x['artifacts'].append('../outside'),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'contract.json'
            for mutate in mutations:
                changed = deepcopy(original)
                mutate(changed)
                path.write_text(json.dumps(changed), encoding='utf-8')
                with self.subTest(mutation=changed), patch.object(coverage, 'CONTRACT', path):
                    with self.assertRaises(ValueError):
                        coverage.contract()

    def test_paths_cannot_leave_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ('../outside', '/absolute', 'C:/absolute', 'local\\file', 'local/../file'):
                with self.subTest(path=name), self.assertRaises(ValueError):
                    coverage.artifact_path(root, name)


if __name__ == '__main__':
    unittest.main()
