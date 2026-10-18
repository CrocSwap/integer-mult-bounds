"""Batched draft generation retains exact pins and rejects before publication."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import new_research_package as scaffold
import research_package as package


class ScaffoldBatchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        package.git(self.root, 'init', '-q')
        for key, value in [('user.name', 'Fixture'), ('user.email', 'test@example.invalid'),
                           ('core.autocrlf', 'false')]:
            package.git(self.root, 'config', key, value)
        self.data = {f'inputs/source-{i:03}.bin': bytes([i]) * (i + 1) for i in range(64)}
        self.data.update({'inputs/empty': b'', 'inputs/space name': b'\0\xff\n' * 1000,
                          'inputs/unicode-\u03ba': b'Unicode filename',
                          'docs/research/agent-task-catalog.json': json.dumps({
                              'priority_revision': 4, 'tracks': [{'tasks': [{
                                  'id': 'fixture', 'question': 'Exact fixture'}]}]}).encode(),
                          'certificates/selected-result.json': b'{}'})
        if sys.platform != 'win32':
            self.data['inputs/line\nbreak'] = b'NUL-delimited request control'
        for name, data in self.data.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        package.git(self.root, 'add', '.')
        package.git(self.root, '-c', 'maintenance.auto=false', '-c', 'gc.auto=0', 'commit', '-qm', 'fixture')
        self.inputs = sorted(n for n in self.data if n.startswith('inputs/'))

    def create(self, slug='fixture', sources=None):
        return scaffold.create(self.root, slug, 'fixture', 'Fixture',
                               self.inputs if sources is None else sources)

    def test_exact_pins_binary_names_deduplication_and_constant_process_count(self):
        children, commands = [], []
        real = subprocess.Popen
        def tracked(argv, *args, **kwargs):
            child = real(argv, *args, **kwargs)
            children.append(child); commands.append(argv)
            return child
        with patch.object(subprocess, 'Popen', side_effect=tracked):
            target = self.create(sources=self.inputs + self.inputs[:3])
        self.assertEqual(len(commands), 3, commands)
        self.assertTrue(all(child.poll() is not None for child in children))
        rows = json.loads((target / 'SOURCES.json').read_bytes())['files']
        expected = []
        for name, data in sorted(self.data.items()):
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            expected.append({'path': name, 'usage': 'input' if name in self.inputs else 'provenance',
                             'git_blob': blob, 'sha256': hashlib.sha256(data).hexdigest()})
        self.assertEqual(rows, expected)
        self.assertEqual(json.loads((target / 'VERIFY.json').read_bytes())['inputs'], self.inputs)
        self.assertEqual({p.name for p in target.iterdir()},
                         {'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py', 'README.md'})

    def test_live_drift_rejects_first_and_last_inputs_without_draft_or_child_leak(self):
        real = subprocess.Popen
        for index, name in enumerate((self.inputs[0], self.inputs[-1])):
            with self.subTest(name=name):
                path = self.root / name
                path.write_bytes(b'changed live input')
                children = []
                def tracked(*args, **kwargs):
                    child = real(*args, **kwargs); children.append(child); return child
                with patch.object(subprocess, 'Popen', side_effect=tracked):
                    with self.assertRaisesRegex(ValueError, 'source has uncommitted changes'):
                        self.create('drift-' + str(index))
                self.assertFalse((self.root / 'research' / ('drift-' + str(index))).exists())
                self.assertTrue(all(child.poll() is not None for child in children))
                path.write_bytes(self.data[name])
                self.create('restored-' + str(index))

    def test_untracked_source_and_late_reader_failure_do_not_publish(self):
        path = self.root / 'inputs/untracked'
        path.write_bytes(b'not in pinned commit')
        with self.assertRaisesRegex(ValueError, 'missing or non-blob Git source'):
            self.create('missing', sources=[path.relative_to(self.root).as_posix()])
        self.assertFalse((self.root / 'research/missing').exists())
        original = scaffold.git_blobs
        closed = []
        def fails_after_last_row(*args):
            try:
                yield from original(*args)
                raise ValueError('injected final Git failure')
            finally:
                closed.append(True)
        with patch.object(scaffold, 'git_blobs', side_effect=fails_after_last_row):
            with self.assertRaisesRegex(ValueError, 'injected final Git failure'):
                self.create('late-failure')
        self.assertEqual(closed, [True])
        self.assertFalse((self.root / 'research/late-failure').exists())


if __name__ == '__main__':
    unittest.main()
