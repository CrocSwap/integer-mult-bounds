# SPDX-License-Identifier: Apache-2.0
"""Fast checks of the parallel phase runner.

Run: python3 -B -m unittest discover -s research/phase-recipes-parallel -p test_package.py -v
"""
import gzip
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import phases_parallel as pp  # noqa: E402

PINS = json.loads((HERE / 'PINS.json').read_text())


def member(name):
    with tarfile.open(ROOT / PINS['t37_archive']['path'], 'r:gz') as tar:
        return tar.extractfile(tar.getmember(name)).read()


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.word = Path(cls.tmp.name) / 'CANONICAL-WORD.json.gz'
        cls.word.write_bytes(member(PINS['canonical_word']['member']))
        cls.clifford = ROOT / Path(PINS['clifford_exact']['path']).parent
        pp.init_worker(str(cls.clifford), str(cls.word))
        cls.ref = json.loads(member('native/local/CLIFFORD-RECIPES.json'))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_edge_order_and_first_recipes(self):
        c = json.load(gzip.open(self.word))
        edges = sorted(set(map(tuple, c['edges'])) | {(a, b) for f in c['center_frames'] for a, b in ((f, 0), (0, f))})
        self.assertEqual(len(edges), len(self.ref['children']))
        got = [pp.edge_task(e) for e in edges[:40]]
        want = self.ref['children'][:40]
        self.assertEqual(json.loads(json.dumps(got)), want)

    def test_first_adapters(self):
        items = [(i, role) for i in range(3) for role in ('source', 'target')]
        got = [pp.adapter_task(x) for x in items]
        self.assertEqual(json.loads(json.dumps(got)), self.ref['endpoint_adapters'][:6])


if __name__ == '__main__':
    unittest.main()
