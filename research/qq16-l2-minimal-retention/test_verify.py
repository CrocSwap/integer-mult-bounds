#!/usr/bin/env python3
"""Failure-sensitive package behavior; mathematical controls live in verify.py."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('retention_verify', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Behavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = v.run()
        cls.encoded = json.dumps(cls.result, sort_keys=True, indent=2) + '\n'

    def test_committed_full_receipt(self):
        self.assertEqual((HERE / 'RESULT.json').read_text(), self.encoded)
        self.assertEqual(len(self.result['semantic_faults']), 8)
        self.assertEqual(len(self.result['retained_coordinate_omissions']), 24)

    def test_missing_changed_receipts_and_explicit_generation(self):
        with tempfile.TemporaryDirectory(prefix='qq16-retention-') as temp:
            target = Path(temp) / 'RESULT.json'
            with mock.patch.object(v, 'HERE', Path(temp)), mock.patch.object(v, 'run', return_value=self.result), \
                    contextlib.redirect_stdout(io.StringIO()):
                with mock.patch('sys.argv', ['verify.py']):
                    with self.assertRaises(FileNotFoundError):
                        v.main()
                    self.assertFalse(target.exists())
                    target.write_text(self.encoded.replace('"retained_arrays": 24', '"retained_arrays": 23'))
                    with self.assertRaisesRegex(ValueError, 'mismatching committed result'):
                        v.main()
                    target.write_text(self.encoded)
                    v.main()
                    self.assertEqual(target.read_text(), self.encoded)
                with mock.patch('sys.argv', ['verify.py', '--write-result']):
                    with self.assertRaises(FileExistsError):
                        v.main()
                    target.unlink()
                    v.main()
                    self.assertEqual(target.read_text(), self.encoded)

    def test_each_input_hash_rejects_changed_bytes(self):
        pins = json.loads((HERE / 'SOURCES.json').read_text())['files']
        original = Path.read_bytes
        for pin in pins:
            if pin['usage'] != 'input':
                continue
            path = v.ROOT / pin['path']
            def corrupted(p, selected=path):
                raw = original(p)
                return bytes([raw[0] ^ 1]) + raw[1:] if p == selected else raw
            with self.subTest(path=pin['path']), mock.patch.object(Path, 'read_bytes', corrupted):
                with self.assertRaisesRegex(ValueError, 'source hash:'):
                    v.source_bytes()

    def test_ineffective_mutation_is_a_failure(self):
        inputs = v.pair()
        with self.assertRaisesRegex(ValueError, 'ineffective semantic control'):
            v.rejected(inputs, inputs, 'identity mutant')
        changed = ({**inputs[0], 1: {}}, inputs[1])
        self.assertIsNotNone(v.rejected(inputs, changed, 'actual omission'))

    def test_ordered_word_algebra_on_noncommuting_maps(self):
        def multiply(a, b):
            return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                               for j in range(2)) for i in range(2))
        eye = ((1, 0), (0, 1))
        matrices = {1: ((1, 1), (0, 1)), -1: ((1, -1), (0, 1)),
                    2: ((1, 0), (1, 1)), -2: ((1, 0), (-1, 1))}
        def evaluate(word):
            result = eye
            for letter in word:
                result = multiply(result, matrices[letter])
            return result
        for word in ((1, 2, -2, -1), (1, 2, -1, -2), (2, -1, 1, 2, -2)):
            self.assertEqual(evaluate(word), evaluate(v.word_reduce(word)))
        self.assertNotEqual(evaluate((1, 2)), evaluate((2, 1)))
        self.assertNotEqual(v.move(1, v.move(2, v.variable(0))),
                            v.move(2, v.move(1, v.variable(0))))


if __name__ == '__main__':
    unittest.main()
