"""Regression checks for PR741 bridge-control identity binding."""

import importlib.util
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / 'scripts/verify_frontier741_bridge_coverage.py'
BIT_SOURCE = ROOT / 'research/community-frontier741-audit/bit'
REPLAY_ARCHIVE = ROOT / 'research/community-frontier741-audit/composed-replay-evidence.tar.gz'

spec = importlib.util.spec_from_file_location('verify_frontier741_bindings', CHECKER_PATH)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class Composition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive_tmp = tempfile.TemporaryDirectory()
        cls.archive_root = Path(cls.archive_tmp.name).resolve()
        cls._extract_archive(REPLAY_ARCHIVE, cls.archive_root)
        cls.complex = cls.archive_root / 'complex'

    @classmethod
    def tearDownClass(cls):
        cls.archive_tmp.cleanup()

    @staticmethod
    def _extract_archive(archive_path, destination):
        destination.mkdir(parents=True, exist_ok=True)
        root = destination.resolve()
        seen = set()
        with tarfile.open(archive_path, mode='r:gz') as archive:
            for member in archive.getmembers():
                if member.name in seen:
                    raise ValueError('Duplicate replay archive member')
                seen.add(member.name)
                target = (destination / member.name).resolve()
                if not target.is_relative_to(root):
                    raise ValueError('Invalid replay archive member')
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError('Unreadable replay archive member')
                    with target.open('wb') as output:
                        shutil.copyfileobj(source, output)
                else:
                    raise ValueError('Unsupported replay archive member')

    @staticmethod
    def _read(path):
        return json.loads(path.read_text())

    @staticmethod
    def _write(path, value):
        path.write_text(json.dumps(value, indent=2) + '\n')

    def _copy_bit(self, temporary_root):
        bit = temporary_root / 'bit'
        shutil.copytree(BIT_SOURCE, bit)
        return bit

    def _assert_rejected(self, mutate):
        with tempfile.TemporaryDirectory() as directory:
            bit = self._copy_bit(Path(directory))
            mutate(bit)
            with self.assertRaises(ValueError):
                checker.check(bit, self.complex)

    def test_complete_pinned_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            bit = self._copy_bit(Path(directory))
            result = checker.check(bit, self.complex)
        self.assertEqual(result['decimal'], '0.001661202643272239')

    def test_replacing_each_bridge_id_with_another_valid_id_is_rejected(self):
        for bridge_id in range(18):
            with self.subTest(bridge_id=bridge_id):
                def mutate(bit, bridge_id=bridge_id):
                    path = bit / 'cout/columns_k4.json'
                    value = self._read(path)
                    control = next(item for item in value['negative_controls']
                                   if item['omit_bridge'] == bridge_id)
                    control['omit_bridge'] = (bridge_id + 1) % 18
                    self._write(path, value)

                self._assert_rejected(mutate)

    def test_missing_each_bridge_id_is_rejected(self):
        for bridge_id in range(18):
            with self.subTest(bridge_id=bridge_id):
                def mutate(bit, bridge_id=bridge_id):
                    path = bit / 'cout/columns_k4.json'
                    value = self._read(path)
                    value['negative_controls'] = [
                        item for item in value['negative_controls']
                        if item['omit_bridge'] != bridge_id
                    ]
                    self._write(path, value)

                self._assert_rejected(mutate)

    def test_extra_bridge_control_is_rejected(self):
        def mutate(bit):
            path = bit / 'cout/columns_k4.json'
            value = self._read(path)
            value['negative_controls'].append({'omit_bridge': 0, 'rejected': True})
            self._write(path, value)

        self._assert_rejected(mutate)

    def test_negative_and_out_of_range_ids_are_rejected(self):
        for bridge_id in (-1, 18, 99):
            with self.subTest(bridge_id=bridge_id):
                def mutate(bit, bridge_id=bridge_id):
                    path = bit / 'cout/columns_k4.json'
                    value = self._read(path)
                    value['negative_controls'][0]['omit_bridge'] = bridge_id
                    self._write(path, value)

                self._assert_rejected(mutate)

    def test_boolean_float_and_string_ids_are_rejected(self):
        for bridge_id in (True, 0.0, '0'):
            with self.subTest(bridge_id=repr(bridge_id)):
                def mutate(bit, bridge_id=bridge_id):
                    path = bit / 'cout/columns_k4.json'
                    value = self._read(path)
                    value['negative_controls'][0]['omit_bridge'] = bridge_id
                    self._write(path, value)

                self._assert_rejected(mutate)

    def test_absent_id_is_rejected(self):
        def mutate(bit):
            path = bit / 'cout/columns_k4.json'
            value = self._read(path)
            value['negative_controls'][0].pop('omit_bridge')
            self._write(path, value)

        self._assert_rejected(mutate)

    def test_nonliteral_rejection_flags_are_rejected(self):
        for flag in (False, 1, 'true', None):
            with self.subTest(flag=repr(flag)):
                def mutate(bit, flag=flag):
                    path = bit / 'cout/columns_k4.json'
                    value = self._read(path)
                    value['negative_controls'][0]['rejected'] = flag
                    self._write(path, value)

                self._assert_rejected(mutate)

    def test_valid_bridge_reordering_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            bit = self._copy_bit(Path(directory))
            path = bit / 'cout/columns_k4.json'
            value = self._read(path)
            value['negative_controls'] = list(reversed(value['negative_controls']))
            self._write(path, value)
            result = checker.check(bit, self.complex)
        self.assertEqual(result['decimal'], '0.001661202643272239')


if __name__ == '__main__':
    unittest.main()
