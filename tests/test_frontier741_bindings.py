"""Regression checks for binding two actual supplier replays to one assembly."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('frontier741', ROOT / 'scripts/verify_frontier741_bindings.py')
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)


class Composition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name).resolve()
        with tarfile.open(ROOT / 'research/community-queue-20261013/pr741-fresh-replay.tar.gz') as archive:
            for member in archive:
                path = (cls.root / member.name).resolve()
                if not path.is_relative_to(cls.root):
                    raise ValueError('Invalid replay archive member')
                # The run contains compiler-workspace symlinks. The binding
                # receipt only consumes ordinary artifacts; never restore links.
                if member.isfile():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(archive.extractfile(member).read())
        cls.complex = cls.root / 'pr741-fresh-replay'
        cls.bit = ROOT / 'research/community-frontier741-audit/bit'

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_complete_pinned_replays(self):
        result = binding.check(self.bit, self.complex)
        self.assertEqual(result['decimal'], '0.001661202643272239')

    def test_wrong_supplier_and_incomplete_replays_rejected(self):
        cases = [
            (self.bit/'RESULT9.json', lambda x: x.update(bit_lower='1/100'), 'Rebuilt bit differs'),
            (self.bit/'v9/hosted/AUDIT.json', lambda x: x.update(hosted_residuals=120960), 'Bit owner inventory'),
            (self.bit/'cout/columns_k4.json', lambda x: x['negative_controls'].pop(), 'Bit bridge controls'),
            (self.complex/'RECEIPT.json', lambda x: x['stages'].pop(), 'Complex stage completion'),
            (self.complex/'RECEIPT.json', lambda x: x.update(manifest_sha256='0'*64), 'Complex source binding'),
            (self.complex/'RECEIPT.json', lambda x: x['artifacts'].update({'RESULT.json':'0'*64}), 'Complex artifact binding'),
            (self.complex/'global-replay/ASSEMBLY.json', lambda x: x.update(kappa='1/100'), 'Selected exact result'),
            (self.complex/'global-replay/ASSEMBLY.json', lambda x: x['outer'].update({next(iter(x['outer'])):'0'}), 'Strict outer constraints'),
        ]
        original = binding.read
        for path, mutate, reason in cases:
            value = deepcopy(original(path))
            mutate(value)
            def reader(p):
                return value if p == path else original(p)
            with self.subTest(reason=reason), patch.object(binding, 'read', reader):
                with self.assertRaisesRegex(ValueError, reason):
                    binding.check(self.bit, self.complex)


if __name__ == '__main__':
    unittest.main()
