"""Preserve H6's historical benchmark without relaxing ordinary input pins."""
import hashlib
from pathlib import Path
import subprocess
from types import ModuleType
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ci = ModuleType('h6_ci_source')
ci.__file__ = str(HERE / 'ci.py')
exec(compile((HERE / 'ci.py').read_bytes(), ci.__file__, 'exec'), ci.__dict__)


class HistoricalBenchmark(unittest.TestCase):
    def setUp(self):
        self.root = Path('/unused-git-root')
        self.original = b'{"historical_price_target":"fixed"}\n'
        self.current = b'{"current_selected_metadata":"updated"}\n'
        self.ordinary = b'unchanged inherited source\n'
        self.pins = {
            ci.SELECTED_RECORD: dict(commit='1' * 40, sha256=hashlib.sha256(self.original).hexdigest()),
            'research/predecessor/source.py': dict(commit='2' * 40, sha256=hashlib.sha256(self.ordinary).hexdigest()),
        }
        self.contents = {ci.SELECTED_RECORD: self.current,
                         'research/predecessor/source.py': self.ordinary,
                         'research/h6-compensation-network/ci.py': b'current successor code'}

    def test_updated_live_record_exports_exact_historical_benchmark(self):
        before = dict(self.contents)
        with patch.object(ci.subprocess, 'check_output', return_value=self.original) as git:
            exported = ci.export_sources(self.root, self.pins, self.contents)
        git.assert_called_once_with(['git', 'show', '1' * 40 + ':' + ci.SELECTED_RECORD], cwd=self.root)
        self.assertEqual(self.contents, before)
        self.assertEqual(exported.pop(ci.SELECTED_RECORD), self.original)
        self.assertEqual(exported, {k: v for k, v in before.items() if k != ci.SELECTED_RECORD})

    def test_changed_ordinary_input_still_rejects(self):
        self.contents['research/predecessor/source.py'] += b'changed'
        with patch.object(ci.subprocess, 'check_output', return_value=self.original):
            with self.assertRaisesRegex(ValueError, 'CI inherited input binding: research/predecessor/source.py'):
                ci.export_sources(self.root, self.pins, self.contents)

    def test_wrong_historical_object_bytes_reject(self):
        with patch.object(ci.subprocess, 'check_output', return_value=self.current):
            with self.assertRaisesRegex(ValueError, 'CI inherited input binding: certificates/selected-result.json'):
                ci.export_sources(self.root, self.pins, self.contents)

    def test_wrong_historical_digest_rejects(self):
        self.pins[ci.SELECTED_RECORD]['sha256'] = '0' * 64
        with patch.object(ci.subprocess, 'check_output', return_value=self.original):
            with self.assertRaisesRegex(ValueError, 'CI inherited input binding: certificates/selected-result.json'):
                ci.export_sources(self.root, self.pins, self.contents)

    def test_missing_historical_git_object_rejects(self):
        failure = subprocess.CalledProcessError(128, ['git', 'show'])
        with patch.object(ci.subprocess, 'check_output', side_effect=failure):
            with self.assertRaises(subprocess.CalledProcessError):
                ci.export_sources(self.root, self.pins, self.contents)

    def test_missing_benchmark_pin_rejects(self):
        del self.pins[ci.SELECTED_RECORD]
        with self.assertRaisesRegex(ValueError, 'historical selected-record pin'):
            ci.export_sources(self.root, self.pins, self.contents)


if __name__ == '__main__':
    unittest.main()
