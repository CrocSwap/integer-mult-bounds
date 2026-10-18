# SPDX-License-Identifier: Apache-2.0
"""Fast checks of the record/evaluate/replay runner.

Run: python3 -B -m unittest discover -s research/layer-end-controls-parallel -p test_package.py -v
"""
import gzip
import json
import sys
import tarfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import audit_worker  # noqa: E402
import controls_parallel as cp  # noqa: E402

PINS = json.loads((HERE / 'PINS.json').read_text())


def barch_word():
    with tarfile.open(ROOT / PINS['t37_archive']['path'], 'r:gz') as tar:
        return tar.extractfile(tar.getmember(PINS['t37_archive']['word_member'])).read()


class RunnerTests(unittest.TestCase):
    def test_placeholder_satisfies_any_reason_check(self):
        msg = repr(cp.Placeholder())
        self.assertIsInstance(msg, str)
        for why in ("'arbitrary-dirt endpoint'", 'hpe cone pre-check (row / column)', 'anything at all'):
            self.assertIn(why, msg)

    def test_pins_match_runner_constants(self):
        self.assertEqual(cp.SCRIPT_SHA256, PINS['script']['sha256'])
        self.assertEqual(audit_worker.AUDIT_SHA256, PINS['pr635_code']['audit_sha256'])

    def test_real_audit_accepts_word_and_rejects_corruption(self):
        audit_worker.init_worker(str(ROOT / PINS['pr635_code']['path']))
        routing = str(ROOT / PINS['routing']['path'])
        data = barch_word()
        self.assertEqual(audit_worker.evaluate((data, routing)), ('pass', ()))
        w = json.loads(gzip.decompress(data))
        w['A'][0][3] = w['A'][0][3] * 2
        kind, args = audit_worker.evaluate((gzip.compress(json.dumps(w).encode(), mtime=0), routing))
        self.assertEqual(kind, 'assert')


if __name__ == '__main__':
    unittest.main()
