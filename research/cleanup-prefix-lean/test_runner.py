#!/usr/bin/env python3
"""Focused exact-version controls; temporary stubs never build Lean proofs.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cleanup_prefix_runner', HERE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

# Actual banner recorded by the independently reviewed pinned toolchain.
RELEASE_BANNER = (
    'Lean (version 4.27.0, x86_64-unknown-linux-gnu, '
    'commit db93fe1608548721853390a10cd40580fe7d22ae, Release)\n'
)
REJECTED_VERSIONS = (
    '4.27.0-rc1', '4.27.0-dev', '4.27.0+build.1',
    '4.26.0', '4.27.1', '4.27.00', '14.27.0',
)


class RunnerVersionTests(unittest.TestCase):
    def test_complete_version_token(self):
        self.assertEqual(runner.reported_lean_version(RELEASE_BANNER), runner.VERSION)
        for version in REJECTED_VERSIONS:
            with self.subTest(version=version):
                banner = RELEASE_BANNER.replace('4.27.0', version)
                self.assertEqual(runner.reported_lean_version(banner), version)
                self.assertNotEqual(runner.reported_lean_version(banner), runner.VERSION)
        for malformed in ('', '4.27.0', 'unrelated version 4.27.0', 'Lean (version )'):
            with self.subTest(malformed=malformed):
                self.assertIsNone(runner.reported_lean_version(malformed))

    def test_cli_gate_precedes_source_checks_and_build(self):
        for version in (runner.VERSION, *REJECTED_VERSIONS):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                bin_dir = root / 'bin'
                bin_dir.mkdir()
                events = root / 'events.txt'
                shutil.copyfile(HERE / 'run.py', root / 'run.py')

                def write_stub(path, event, body=''):
                    path.write_text(
                        f'#!{sys.executable}\nfrom pathlib import Path\n'
                        f'with Path({str(events)!r}).open("a") as log:\n'
                        f'    log.write({event + chr(10)!r})\n' + body
                    )
                    path.chmod(0o755)

                banner = RELEASE_BANNER.replace('4.27.0', version)
                write_stub(bin_dir / 'lean', 'lean',
                           'import sys\nassert sys.argv[1:] == ["--version"]\n'
                           f'print({banner!r}, end="")\n')
                for name in ('check_source.py', 'generate_lean.py'):
                    write_stub(root / name, name)
                theorem_names = (
                    'CleanupPrefix.commute_sound',
                    'CleanupPrefix.sourceExtract_in_context',
                    'CleanupPrefix.CK.checked',
                    'CleanupPrefix.CK.scalar_rewrite',
                    'CleanupPrefix.CK.source_coefficient_rewrite',
                )
                audit_output = '\n'.join(
                    f"'{name}' depends on axioms: [propext]" for name in theorem_names
                )
                write_stub(bin_dir / 'lake', 'lake',
                           'import sys\nassert sys.argv[1:] == ["build"]\n'
                           f'print({audit_output!r})\n')
                result = subprocess.run(
                    [sys.executable, '-B', str(root / 'run.py'), '--lean-bin', str(bin_dir)],
                    cwd=root, text=True, capture_output=True, timeout=10,
                )
                observed = events.read_text().splitlines()
                if version == runner.VERSION:
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(observed,
                                     ['lean', 'check_source.py', 'generate_lean.py', 'lake'])
                    self.assertIn('PASS_CLEANUP_PREFIX_LEAN', result.stdout)
                else:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Lean 4.27.0 required', result.stderr)
                    self.assertEqual(observed, ['lean'],
                                     'Rejected versions must not run source checks or builds')


if __name__ == '__main__':
    unittest.main(verbosity=2)
