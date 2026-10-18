#!/usr/bin/env python3
"""Complete retained controls and observable parse/diagnostic regressions.

Nick Petalas. Apache-2.0. Substantial automated assistance was used.
"""
import gzip
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('negative_verifier', HERE / 'verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
fast, paired_checks = verify.setup()
retained = paired_checks.module(verify.ROOT / paired_checks.OLD / 'verify.py',
                                {'compare': fast.source})
oldtests = paired_checks.module(verify.PAIRED / 'test_compare.py')
# Run all fifteen PR2693 groups, including its CLI, against this successor.
oldtests.fast = fast
oldtests.HERE = HERE
oldtests.verify = paired_checks
fast.paired = fast.parent.paired
oldtests.oldtests.HERE = HERE
oldtests.oldtests.c = fast
ComparisonControls = oldtests.ComparisonControls


class RetainedAdapterControls(oldtests.AdapterControls):
    def test_source_change_invalidates_before_execution(self):
        # Retain the original comparator's source-pin control separately.
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            path = root / fast.parent.SOURCE
            path.parent.mkdir(parents=True)
            shutil.copyfile(verify.ROOT / fast.parent.SOURCE, path)
            fast.parent.load_source(root)
            path.write_bytes(path.read_bytes() + b'\nraise RuntimeError("must not execute")\n')
            with self.assertRaisesRegex(ValueError, 'SHA256 differs'):
                fast.parent.load_source(root)

    def test_full_result_differential_detects_python_equality_mutant(self):
        with patch.object(fast.parent, 'paired', lambda a, b, *args: a == b):
            args = ('a.json', b'{"x":true}', b'{"x":1}')
            self.assertNotEqual(fast.classify(*args), fast.original_classify(*args))


class ReuseControls(unittest.TestCase):
    def test_changed_parent_invalidates_before_execution(self):
        paths = (fast.PARENT, 'research/strict-payload-paired-walk/SOURCES.json')
        for changed in paths:
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as name:
                root = Path(name)
                for relative in paths:
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    raw = (verify.ROOT / relative).read_bytes()
                    path.write_bytes(raw + (b'\nraise RuntimeError("must not execute")\n'
                                            if relative == changed else b''))
                with self.assertRaisesRegex(ValueError, 'SHA256 differs'):
                    fast.load_parent(root)

    def test_mismatch_parses_and_decompresses_each_side_once(self):
        a = gzip.compress(b'{"proof":[1,2,3]}', mtime=0)
        b = gzip.compress(b'{"proof":[1,2,true]}', mtime=0)
        expected = {'cls': 'json-diff', 'verdict': 'proof-relevant-candidate',
                    'first_difference': {'path': [['string', 'proof'], 2],
                                         'kind': 'value-or-type',
                                         'reference': "('integer', 3)",
                                         'run': "('boolean', True)"}}
        for function, calls in ((fast.parent.classify, 4), (fast.classify, 2)):
            with patch.object(fast.source, 'read_json', wraps=fast.read_json) as parser:
                with patch.object(fast.source.gzip, 'decompress', wraps=gzip.decompress) as unzip:
                    self.assertEqual(function('p.json.gz', a, b), expected)
                    self.assertEqual(parser.call_count, calls)
                    self.assertEqual(unzip.call_count, calls)

    def test_sorted_diagnostic_and_invalid_sibling_precedence(self):
        cases = [
            (b'{"z":0,"a":0}', b'{"z":1,"a":true}', ()),
            (b'{"a":0,"z":1}', b'{"a":2,"z":NaN}', ()),
            (b'{"a":0,"t":1}', b'{"a":2,"t":false}', [('t',)]),
            (b'{"a":0,"x":1,"x":2}', b'{"a":2}', ()),
            (b'{"x":[1,2],"t":1}', b'{"x":[1,true],"t":2.0}', [('t',)]),
        ]
        for a, b, policy in cases:
            with self.subTest(a=a, b=b):
                args = ('p.json', a, b, fast.EMPTY, fast.EMPTY, policy)
                self.assertEqual(fast.classify(*args), fast.original_classify(*args))
        result = fast.classify('p.json', *cases[0][:2])
        self.assertEqual(result['first_difference']['path'], [['string', 'a']])


if __name__ == '__main__':
    unittest.main(verbosity=2)
