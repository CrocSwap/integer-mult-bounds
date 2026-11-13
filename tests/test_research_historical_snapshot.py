"""Keep historical integration controls in the full-history replay job."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/historical-selected-replay-gap'


class HistoricalSnapshotRoutingTests(unittest.TestCase):
    def test_snapshot_controls_are_mandatory_in_full_history_replay(self):
        manifest = json.loads((PACKAGE / 'VERIFY.json').read_bytes())
        commands = [row for row in manifest['commands']
                    if row['argv'] == ['{python}', '-B', '{package}/test_snapshot.py']]
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]['timeout_seconds'], 120)
        self.assertTrue((PACKAGE / 'test_snapshot.py').is_file())
        workflow = (ROOT / '.github/workflows/research-package-batch.yml').read_text(encoding='utf-8')
        self.assertIn('fetch-depth: 0', workflow)
        self.assertIn('scripts/research_package.py --package', workflow)


    def test_onboarding_route_needs_no_historical_git_objects(self):
        with tempfile.TemporaryDirectory(prefix='onboarding-history-free-') as directory:
            fixture = Path(directory)
            names = ['tests/test_research_historical_snapshot.py',
                     'research/historical-selected-replay-gap/VERIFY.json',
                     'research/historical-selected-replay-gap/test_snapshot.py',
                     '.github/workflows/research-package-batch.yml']
            for name in names:
                target = fixture / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            self.assertFalse((fixture / '.git').exists())
            result = subprocess.run([sys.executable, '-B', str(fixture / names[0]),
                                     '-k', 'mandatory', '-v'], cwd=fixture,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('Ran 1 test', result.stderr)


if __name__ == '__main__':
    unittest.main()
