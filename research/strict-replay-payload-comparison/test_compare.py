#!/usr/bin/env python3
"""Semantic and failure controls for the opt-in comparator. Apache-2.0.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compare as c
import verify as audit


class ComparisonControls(unittest.TestCase):
    def classify(self, a, b, **kwargs):
        return c.classify('receipt.json', a, b, **kwargs)

    def test_exact_typed_scalars_at_every_container_shape(self):
        pairs = [(b'true', b'1'), (b'false', b'0'), (b'1', b'1.0'),
                 (b'9007199254740992.0', b'9007199254740993.0'),
                 (b'68', b'68.000000000000000000000001')]
        for left, right in pairs:
            for before, after in ((b'', b''), (b'[', b']'), (b'{"x":', b'}')):
                with self.subTest(left=left, before=before):
                    self.assertFalse(c.accepted(self.classify(before + left + after,
                                                              before + right + after)))
        self.assertEqual(self.classify(b'{"n":1.2500}', b'{"n":125e-2}')['cls'], 'json-format')

    def test_ambiguous_and_nonfinite_inputs_even_when_identical(self):
        for raw in (b'{"rank":0,"rank":1}', b'NaN', b'Infinity', b'-Infinity', b'{'):
            with self.subTest(raw=raw):
                self.assertEqual(self.classify(raw, raw)['cls'], 'invalid')
        # Arbitrarily large *finite* decimal exponents are not converted to float infinity.
        self.assertEqual(self.classify(b'1e999', b'10e998')['cls'], 'json-format')

    def test_root_mapping_is_injective_and_keeps_literal_tokens(self):
        roots = c.Roots([('W', '/work'), ('N', '/work/nested')])
        values = ['/work', '/work/a', '/work/nested', '/work/nested/a', '/workish/a',
                  'W/a', 'N/a', '<WORK>/a', '/outside/a', '', '/work/a/../b']
        self.assertEqual(len({roots.string(v) for v in values}), len(values))
        left, right = c.Roots([('W', '/a')]), c.Roots([('W', '/b')])
        self.assertTrue(c.accepted(self.classify(b'{"/a/file":1}', b'{"/b/file":1}',
                                               ref_roots=left, run_roots=right)))
        for raw in (b'{"W/file":1}', b'{"/b/file":1,"W/file":0}',
                    b'{"/a/file":1}', b'{"/b/file2":1}'):
            self.assertFalse(c.accepted(self.classify(b'{"/a/file":1}', raw,
                                                    ref_roots=left, run_roots=right)))
        # The identical-byte shortcut cannot hide a stale absolute input path.
        self.assertFalse(c.accepted(self.classify(b'"/a/file"', b'"/a/file"',
                                                ref_roots=left, run_roots=right)))

    def test_invalid_root_declarations(self):
        for pairs in ([('W', '/a'), ('W', '/b')], [('A', '/a'), ('B', '/a')],
                      [('W', 'relative')], [('W', '/a/../b')], [('W', '/a/')]):
            with self.subTest(pairs=pairs), self.assertRaises(c.InvalidPayload):
                c.Roots(pairs)
        with self.assertRaises(c.InvalidPayload):
            self.classify(b'{}', b'{}', ref_roots=c.Roots([('A', '/a')]),
                          run_roots=c.Roots([('B', '/b')]))

    def test_timing_is_an_exact_typed_path(self):
        policy = [('stages', 0, 'seconds')]
        left = b'{"stages":[{"seconds":1.0}],"proof/seconds":17}'
        good = b'{"stages":[{"seconds":2}],"proof/seconds":17}'
        self.assertTrue(c.accepted(self.classify(left, good, timing_paths=policy)))
        changed = b'{"stages":[{"seconds":2}],"proof/seconds":18}'
        self.assertFalse(c.accepted(self.classify(left, changed, timing_paths=policy)))
        for value in (b'true', b'null', b'-1', b'"2"', b'NaN'):
            raw = b'{"stages":[{"seconds":' + value + b'}],"proof/seconds":17}'
            self.assertEqual(self.classify(left, raw, timing_paths=policy)['cls'], 'invalid')
        for path in ([('stages', False, 'seconds')], [('stages', -1, 'seconds')],
                     [('stages', '0', 'seconds')], [policy[0], policy[0]], None):
            self.assertEqual(self.classify(left, good, timing_paths=path)['cls'], 'invalid')

    def test_gzip_covers_complete_payload_and_corruption(self):
        left = gzip.compress(b'{"rank":1}', mtime=0)
        right = gzip.compress(b'{"rank":1}', mtime=1)
        self.assertEqual(c.classify('word.json.gz', left, right)['cls'], 'gzip-container')
        for raw in (gzip.compress(b'{"rank":true}'), gzip.compress(b'{"rank":2}'), left[:-5]):
            self.assertFalse(c.accepted(c.classify('word.json.gz', left, raw)))
        ambiguous = gzip.compress(b'{"rank":1,"rank":2}')
        self.assertEqual(c.classify('word.json.gz', ambiguous, ambiguous)['cls'], 'invalid')

    def test_complete_containers_and_unfamiliar_fields(self):
        for a, b in ((b'{}', b'{"new":{}}'), (b'[]', b'[null]'),
                     (b'{"a":[]}', b'{"a":{}}'), (b'{"x/y":1}', b'{"x":{"y":1}}'),
                     (b'{"proof":{"seconds":1}}', b'{"proof":{"seconds":2}}')):
            self.assertFalse(c.accepted(self.classify(a, b)))
        self.assertEqual(c.classify('raw.bin', b'\xff', b'\xfe')['cls'], 'binary-diff')

    def test_cli_exit_status_and_inventory(self):
        with tempfile.TemporaryDirectory(prefix='strict-cli-') as temporary:
            root = Path(temporary)
            left, right = root / 'left', root / 'right'
            left.mkdir(); right.mkdir()
            a, b = left / 'a.json', right / 'a.json'
            a.write_bytes(b'{"checked":true}'); b.write_bytes(b'{ "checked": true }')
            command = [sys.executable, '-I', '-O', '-B', str(HERE / 'compare.py'), str(left), str(right)]
            def run():
                return subprocess.run(command, capture_output=True, text=True, check=False)
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            b.write_bytes(b'{"checked":1}')
            self.assertEqual(run().returncode, 1)
            b.unlink()
            self.assertEqual(c.compare(left, right)['a.json']['cls'], 'missing')
            b.write_bytes(a.read_bytes()); (right / 'extra').write_bytes(b'x')
            self.assertEqual(c.compare(left, right)['extra']['cls'], 'extra')
            self.assertEqual(run().returncode, 1)
            command += ['--ref-root', 'X=/a']
            self.assertEqual(run().returncode, 2)

    def test_source_pin_is_not_a_payload_quotient(self):
        with tempfile.TemporaryDirectory(prefix='strict-source-') as temporary:
            root = Path(temporary)
            for name in audit.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(audit.ROOT / name, target)
            audit.bound_inputs(root)
            path = root / audit.ARCHIVE
            raw = bytearray(path.read_bytes())
            raw[4] ^= 1  # only the gzip MTIME header; decompressed tar is unchanged
            self.assertEqual(gzip.decompress(raw), gzip.decompress(path.read_bytes()))
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'source SHA256 mismatch'):
                audit.bound_inputs(root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
