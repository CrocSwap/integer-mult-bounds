#!/usr/bin/env python3
"""Real-process, exact-value and rejection controls. Apache-2.0.

Arham Tahir, with substantial OpenAI Codex assistance.
"""
from decimal import localcontext, Inexact, Rounded
import gzip
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('_integer_comparison_controls', HERE / 'compare.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def oracle(text):
    """Independent positional accumulation; no large decimal-string conversion."""
    negative = text.startswith('-')
    value = 0
    for digit in text.lstrip('-'):
        value = value * 10 + ord(digit) - ord('0')
    return -value if negative else value


class IntegerControls(unittest.TestCase):
    def test_values_and_types_are_exact_under_small_decimal_context(self):
        before = sys.get_int_max_str_digits()
        with localcontext() as context:
            context.prec = 2
            context.Emax = 9
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            for length in (1, 639, 640, 641, 4299, 4300, 4301, 10000):
                digits = ('1234567890' * (length // 10 + 1))[:length]
                for sign in ('', '-'):
                    text = sign + digits
                    value = c.read_json(text)
                    self.assertIs(type(value), int)
                    self.assertEqual(value, oracle(text))
            self.assertEqual(c.read_json('-0'), 0)
            self.assertIs(type(c.read_json('true')), bool)
            self.assertIs(type(c.read_json('1.0')), c.Decimal)
            self.assertEqual(context.flags[Inexact], False)
            self.assertEqual(context.flags[Rounded], False)
        self.assertEqual(sys.get_int_max_str_digits(), before)

    def test_identical_reformatted_and_recompressed_large_integers(self):
        before = sys.get_int_max_str_digits()
        for n in (641, 4301, 10000):
            a = b'{"numerator":' + b'9' * n + b'}'
            b = b'{ "numerator" : ' + b'9' * n + b' }'
            self.assertEqual(c.classify('r.json', a, a), {'cls': 'bytes'})
            self.assertEqual(c.classify('r.json', a, b), {'cls': 'json-format'})
            self.assertEqual(c.classify('r.json.gz', gzip.compress(a, mtime=0),
                                       gzip.compress(a, mtime=1)), {'cls': 'gzip-container'})
            self.assertEqual(c.classify('r.json.gz', gzip.compress(a), gzip.compress(b)),
                             {'cls': 'json-format'})
        self.assertEqual(sys.get_int_max_str_digits(), before)

    def test_integer_changes_and_type_changes_keep_typed_diagnostics(self):
        digits = b'7' * 5000
        for left, right in ((digits, digits[:-1] + b'8'),
                            (digits, b'-' + digits), (digits, digits + b'.0'),
                            (digits, b'true'), (digits, b'[]'),
                            (b'{"huge":' + digits + b'}', b'[]')):
            for prefix, suffix, path in ((b'', b'', []), (b'[', b']', [0]),
                                         (b'{"value":', b'}', [['string', 'value']])):
                result = c.classify('r.json', prefix + left + suffix, prefix + right + suffix)
                self.assertEqual(result['cls'], 'json-diff', result)
                self.assertEqual(result['verdict'], 'proof-relevant-candidate')
                self.assertEqual(result['first_difference']['path'], path)
                self.assertFalse(c.accepted(result))
                self.assertLess(len(json.dumps(result)), 1000)

    def test_malformed_duplicate_and_nonfinite_still_reject(self):
        big = b'9' * 5000
        for raw in (b'01', b'-01', b'+1', b'1_', b'1e', b'NaN', b'Infinity',
                    b'-Infinity', b'{"n":' + big + b',"n":0}'):
            with self.subTest(raw=raw[:40]):
                self.assertEqual(c.classify('r.json', raw, raw)['cls'], 'invalid')

    def test_timing_policy_and_roots_preserve_complete_checks(self):
        big = b'9' * 5000
        a = b'{"seconds":' + big + b',"/old/input":' + big + b'}'
        b = b'{"seconds":0,"/new/input":' + big + b'}'
        left, right = c.Roots([('W', '/old')]), c.Roots([('W', '/new')])
        result = c.classify('r.json', a, b, left, right, [('seconds',)])
        self.assertEqual(result, {'cls': 'json-diff', 'verdict': 'declared-timing'})
        changed = b[:-2] + b'8}'
        self.assertFalse(c.accepted(c.classify('r.json', a, changed, left, right, [('seconds',)])))
        for bad in (b'{"seconds":true}', b'{"seconds":-1}', b'{}'):
            self.assertEqual(c.classify('r.json', bad, bad, timing_paths=[('seconds',)])['cls'],
                             'invalid')

    def test_real_cli_across_environment_limits_and_optimization(self):
        with tempfile.TemporaryDirectory(prefix='integer cli ') as td:
            root = Path(td)
            left, right = root / 'reference', root / 'run'
            left.mkdir(); right.mkdir()
            for limit in (0, 640, 4300):
                for optimized in (False, True):
                    with self.subTest(limit=limit, optimized=optimized):
                        env = dict(os.environ, PYTHONINTMAXSTRDIGITS=str(limit))
                        env.pop('PYTHONOPTIMIZE', None)
                        report = root / 'report.json'
                        argv = [sys.executable, '-B'] + (['-O'] if optimized else [])
                        argv += [str(HERE / 'compare.py'), str(left), str(right), '--out', str(report)]
                        for n in (641, 4301):
                            a = b'{"n":' + b'9' * n + b'}'
                            b = b'{ "n": ' + b'9' * n + b'}'
                            (left / 'r.json').write_bytes(a)
                            (right / 'r.json').write_bytes(b)
                            report.unlink(missing_ok=True)
                            result = subprocess.run(argv, cwd=root, env=env, capture_output=True, timeout=30)
                            self.assertEqual(result.returncode, 0, result.stderr)
                            self.assertEqual(json.loads(report.read_bytes())['files']['r.json'],
                                             {'cls': 'json-format'})
                            (right / 'r.json').write_bytes(b[:-2] + b'8}')
                            report.unlink()
                            result = subprocess.run(argv, cwd=root, env=env, capture_output=True, timeout=30)
                            self.assertEqual(result.returncode, 1, result.stderr)
                            self.assertEqual(json.loads(report.read_bytes())['files']['r.json']['cls'],
                                             'json-diff')

    def test_predecessor_failure_is_reproduced_without_changing_parent_limit(self):
        snippet = '''import importlib.util,json,sys
s=importlib.util.spec_from_file_location('c',sys.argv[1]);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
a=b'{"n":'+b'9'*int(sys.argv[2])+b'}'; b=b'{ "n":'+b'9'*int(sys.argv[2])+b'}'
before=sys.get_int_max_str_digits(); result=c.classify('r.json',a,b)
print(json.dumps({'result':result,'limit':sys.get_int_max_str_digits(),'unchanged':before==sys.get_int_max_str_digits()}))
'''
        for limit, length, expected in ((640, 641, 'invalid'), (4300, 4301, 'invalid'),
                                        (0, 4301, 'json-format')):
            env = dict(os.environ, PYTHONINTMAXSTRDIGITS=str(limit))
            result = subprocess.run([sys.executable, '-B', '-c', snippet,
                                     str(c.ROOT / c.PREDECESSOR), str(length)],
                                    env=env, capture_output=True, check=True, timeout=30)
            value = json.loads(result.stdout)
            self.assertEqual(value['result']['cls'], expected)
            self.assertTrue(value['unchanged'])
            self.assertEqual(value['limit'], limit)
            result = subprocess.run([sys.executable, '-B', '-c', snippet,
                                     str(HERE / 'compare.py'), str(length)],
                                    env=env, capture_output=True, check=True, timeout=30)
            value = json.loads(result.stdout)
            self.assertEqual(value['result']['cls'], 'json-format')
            self.assertTrue(value['unchanged'])
            self.assertEqual(value['limit'], limit)

    def test_pinned_source_drift_is_rejected(self):
        from unittest.mock import patch
        original = Path.read_bytes
        def altered(path):
            raw = original(path)
            return raw + b'\n' if path == c.ROOT / c.PREDECESSOR else raw
        with patch.object(Path, 'read_bytes', altered):
            with self.assertRaisesRegex(ValueError, 'source bytes differ'):
                c.predecessor()


if __name__ == '__main__':
    unittest.main(verbosity=2)
