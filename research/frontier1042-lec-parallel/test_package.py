# SPDX-License-Identifier: Apache-2.0
"""Fast checks of the record/evaluate/replay runner (about 10 s).

Run: python3 -B -m unittest discover -s research/frontier1042-lec-parallel -p test_package.py -v
"""
import gzip
import json
import os
import signal
import sys
import time
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import audit_worker  # noqa: E402
import chain_lec  # noqa: E402
import lec_parallel as lp  # noqa: E402

PINS = json.loads((HERE / 'PINS.json').read_text())


def frames_word():
    with tarfile.open(lp.ROOT / PINS['archive']['path'], 'r:gz') as tar:
        return tar.extractfile(tar.getmember('chain/frames/FULL-WORD.json.gz')).read()


class Stop(Exception):
    pass


class RunnerTests(unittest.TestCase):
    def test_placeholder_satisfies_any_reason_check(self):
        msg = repr(lp.Placeholder())
        self.assertIsInstance(msg, str)
        for why in ("'arbitrary-dirt endpoint'", 'hpe cone pre-check (row / column)', 'anything at all'):
            self.assertIn(why, msg)

    def test_pins_match_runner_constants(self):
        self.assertEqual(lp.LAUNCHER_SHA256, PINS['launcher']['sha256'])
        self.assertEqual(lp.SCRIPT_SHA256, PINS['script']['sha256'])
        self.assertEqual(lp.T37_SCRIPT_SHA256, PINS['t37_script']['sha256'])
        self.assertEqual(sorted(lp.PINNED_SCRIPTS), sorted([lp.SCRIPT_SHA256, lp.T37_SCRIPT_SHA256]))
        self.assertEqual(audit_worker.AUDIT_SHA256, PINS['pr635_code']['audit_sha256'])
        self.assertEqual(chain_lec.ROUTING, lp.ROOT / PINS['routing']['path'])
        self.assertEqual(chain_lec.PR635_CODE, lp.ROOT / PINS['pr635_code']['path'])

    def test_chain_word_pins(self):
        pins = chain_lec.word_pins('k8')
        self.assertEqual(sorted(pins), ['frames', 'hyb', 'jx', 'p6n', 'promo'])
        # the re-indexed X4 exchange is the identity on the k8 word, so lec-jx audits lec-promo's word again
        self.assertEqual(pins['jx'], pins['promo'])
        self.assertEqual(pins['frames'][:8], 'db2c7cfb')

    def test_run_pinned_restores_global_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            word = Path(tmp) / 'w.json.gz'
            word.write_bytes(frames_word())
            before = (sys.argv, list(sys.path), sys.modules.get('hpe_audit_and_transport'), sys.stdout,
                      Path.write_text, gzip.compress)
            calls = []

            def stop(p, routing, out):
                calls.append(Path(p).read_bytes())
                raise Stop()
            os.environ['PR635_CODE'] = str(chain_lec.PR635_CODE)
            try:
                with self.assertRaises(Stop):
                    lp.run_pinned([word, chain_lec.ROUTING, Path(tmp) / 'out'], stop)
            finally:
                os.environ.pop('PR635_CODE', None)
            after = (sys.argv, list(sys.path), sys.modules.get('hpe_audit_and_transport'), sys.stdout,
                     Path.write_text, gzip.compress)
            self.assertEqual(before, after)
            self.assertEqual(len(calls), 1)
            # the launcher's portable gzip header reached the pinned script's trial word
            self.assertEqual(calls[0][9], 0xff)
            self.assertEqual(json.loads(gzip.decompress(calls[0])), json.loads(gzip.decompress(word.read_bytes())))

    def test_routing_key_keeps_the_path_trial_uses(self):
        # PR635's reader picks gzip or JSON from the suffix of the path it is given: never resolve symlinks
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / 'routing.json'
            link.symlink_to(chain_lec.ROUTING)
            path, digest = lp.routing_key(link, {})
            self.assertTrue(path.endswith('routing.json'))
            self.assertEqual(digest, PINS['routing']['sha256'])

    def test_worker_loss_fails_closed(self):
        runner = lp.Runner(chain_lec.PR635_CODE, 2)
        try:
            os.kill(runner.workers[0].pid, signal.SIGKILL)
            runner.workers[0].join(5)
            pending = runner.pool.apply_async(time.sleep, (3,))
            with self.assertRaises(RuntimeError):
                runner.wait(pending)
        finally:
            runner.terminate()

    def test_real_audit_accepts_word_and_rejects_corruption(self):
        audit_worker.init_worker(str(chain_lec.PR635_CODE))
        routing = str(chain_lec.ROUTING)
        data = frames_word()
        kind, args, text = audit_worker.evaluate((data, routing))
        self.assertEqual((kind, args), ('pass', ()))
        self.assertIn('"seconds"', text)
        w = json.loads(gzip.decompress(data))
        w['A'][0][3] = w['A'][0][3] * 2
        kind, args, text = audit_worker.evaluate((gzip.compress(json.dumps(w).encode(), mtime=0), routing))
        self.assertEqual(kind, 'assert')


if __name__ == '__main__':
    unittest.main()
