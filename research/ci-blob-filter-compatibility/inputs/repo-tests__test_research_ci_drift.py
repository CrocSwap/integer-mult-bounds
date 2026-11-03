"""Execute the registered replay's actual CI drift gate on real Git states."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/research-package-batch.yml'


def drift_script():
    """Read this simple run step without adding a YAML dependency to the suite."""
    marker = '      - name: Committed inputs remain unchanged\n'
    text = WORKFLOW.read_text()
    if text.count(marker) != 1:
        raise ValueError('expected one registered replay drift gate')
    step = text.split(marker, 1)[1].split('\n      - ', 1)[0].rstrip('\n')
    lines = step.splitlines()
    prefix = '        run: '
    if not lines or not lines[0].startswith(prefix):
        raise ValueError('unsupported drift gate step')
    run = lines[0][len(prefix):]
    if run == '|':
        if not lines[1:] or any(not line.startswith('          ') for line in lines[1:]):
            raise ValueError('unsupported drift gate run block')
        return textwrap.dedent('\n'.join(lines[1:]))
    if len(lines) != 1:
        raise ValueError('unsupported drift gate step fields')
    return run


@unittest.skipUnless(shutil.which('bash') and shutil.which('git'), 'requires bash and Git')
class RegisteredReplayDriftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = drift_script()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.input = self.root / 'input.txt'
        self.input.write_text('original\n')
        self.git('add', 'input.txt')
        self.git('commit', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.PIPE)

    def gate(self):
        # Match the fail-fast shell behavior of a GitHub Actions run step.
        return subprocess.run(['bash', '--noprofile', '--norc', '-e', '-o', 'pipefail',
                               '-c', self.script], cwd=self.root, capture_output=True,
                              timeout=10).returncode

    def test_unchanged_checkout_passes(self):
        self.assertEqual(self.gate(), 0)

    def test_untracked_replay_output_is_allowed(self):
        (self.root / 'receipt.json').write_text('{"verified": true}\n')
        self.assertEqual(self.gate(), 0)

    def test_unstaged_input_edit_is_rejected(self):
        self.input.write_text('regenerated\n')
        self.assertNotEqual(self.gate(), 0)

    def test_unstaged_input_deletion_is_rejected(self):
        self.input.unlink()
        self.assertNotEqual(self.gate(), 0)

    def test_staged_input_edit_is_rejected(self):
        self.input.write_text('regenerated\n')
        self.git('add', 'input.txt')
        self.assertNotEqual(self.gate(), 0)

    def test_staged_input_deletion_is_rejected(self):
        self.git('rm', '-q', 'input.txt')
        self.assertNotEqual(self.gate(), 0)

    def test_staged_new_file_is_rejected(self):
        (self.root / 'added.txt').write_text('new tracked content\n')
        self.git('add', 'added.txt')
        self.assertNotEqual(self.gate(), 0)

    def test_staged_edit_with_worktree_restored_to_head_is_rejected(self):
        self.input.write_text('regenerated\n')
        self.git('add', 'input.txt')
        self.input.write_text('original\n')
        # Comparing only the working tree to HEAD would miss this dirty index.
        self.assertEqual(self.git('diff', '--exit-code', 'HEAD', '--'), b'')
        self.assertNotEqual(self.gate(), 0)


if __name__ == '__main__':
    unittest.main()
