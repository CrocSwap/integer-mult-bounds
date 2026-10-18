"""Complete package coverage at both GitHub matrix boundaries."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('matrix_package', ROOT / 'scripts/research_package.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class MatrixBatchTests(unittest.TestCase):
    def test_exact_coverage_and_both_matrix_limits(self):
        for count in (0, 1, 255, 256, 257, 450, 65536):
            with self.subTest(count=count):
                names = ['research/p' + str(i) for i in range(count)]
                rows = package.replay_matrix(names, 256)['include']
                self.assertLessEqual(len(rows), 256)
                self.assertTrue(all(0 < len(row['packages']) <= 256 for row in rows))
                self.assertEqual([p for row in rows for p in row['packages']], names)

    def test_oversized_or_invalid_matrix_fails_without_truncation(self):
        with self.assertRaisesRegex(ValueError, 'no packages were truncated'):
            package.replay_matrix(['research/a'] * 65537, 256)
        for size in (0, -1, 257, True, 1.5):
            with self.subTest(size=size), self.assertRaises(ValueError):
                package.replay_matrix(['research/a'], size)

    def test_legacy_cli_shape_is_unchanged(self):
        self.assertEqual(package.replay_matrix(['research/a', 'research/b']),
                         {'include': [{'package': 'research/a'}, {'package': 'research/b'}]})

    def test_nested_workflow_change_selects_every_registered_package(self):
        committed = {str(Path(name).parent.as_posix())
                     for name in package.tracked_input_paths(ROOT)
                     if name.startswith('research/') and name.count('/') == 2
                     and name.endswith('/VERIFY.json')}
        materialized = {p.parent.relative_to(ROOT).as_posix()
                        for p in (ROOT / 'research').glob('*/VERIFY.json')}
        expected = sorted(committed | materialized)
        self.assertEqual(package.plan(ROOT, ['.github/workflows/research-package-batch.yml']), expected)

    def test_grouped_cli_output_keeps_total_package_count(self):
        expected = package.plan(ROOT, ['scripts/research_package.py'])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'github-output'
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/research_package.py'),
                                     '--changed-since', '0', '--matrix-batch-size', '256',
                                     '--github-output', str(output)], cwd=ROOT, text=True,
                                    capture_output=True, check=True)
            fields = dict(line.split('=', 1) for line in output.read_text().splitlines())
            matrix = json.loads(result.stdout)
            self.assertEqual(json.loads(fields['matrix']), matrix)
            self.assertEqual(int(fields['count']), len(expected))
            self.assertEqual([p for row in matrix['include'] for p in row['packages']], expected)


if __name__ == '__main__':
    unittest.main()
