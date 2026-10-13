#!/usr/bin/env python3
"""Replay PR681 against its pinned historical #626 checkpoint.

The imported packages remain unchanged. An isolated source closure supplies
the historical selected-record bytes, so a newer frontier cannot invalidate
this opt-in circuit experiment. No production selection is overwritten.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REL = Path('research/supplier-circuit-consolidation')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--hosted', action='store_true')
    p.add_argument('--out', type=Path)
    p.add_argument('--package-tests', action='store_true')
    p.add_argument('--component-tests', action='store_true', help='Also replay each of the six original component entry points')
    a = p.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Assertions must remain enabled')
    if a.out and (a.out.exists() or a.out.resolve().is_relative_to(ROOT)):
        raise SystemExit('Use a fresh output directory outside the repository')
    pins = json.loads((ROOT / REL / 'SOURCES.json').read_text())
    with tempfile.TemporaryDirectory(prefix='supplier-consolidation-sources-') as tmp:
        root = Path(tmp).resolve()
        for rel in pins['files']:
            source = ROOT / ('certificates/checkpoints/k492626.json'
                             if rel == 'certificates/selected-result.json' else rel)
            target = root / rel
            if not target.resolve().is_relative_to(root) or not source.resolve().is_relative_to(ROOT):
                raise ValueError('Source path outside closure')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        shutil.copytree(ROOT / REL, root / REL, ignore=shutil.ignore_patterns('__pycache__'))
        command = [sys.executable, '-B', str(root / REL / 'verify.py')]
        if a.hosted:
            command.append('--hosted')
        if a.out:
            command += ['--out', str(a.out.resolve())]
        subprocess.run(command, check=True, cwd=root)
        if a.component_tests:
            packages = ('r420-two-block-composition', 'r420-quad13',
                        'r420-compensation-basis', 'complex-dyadic-lowering',
                        'r420-decoder-sharing', 'r420-target-basis')
            for package in packages:
                shutil.copytree(ROOT / 'research' / package, root / 'research' / package,
                                dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
                args = [sys.executable, '-B', str(root / 'research' / package / 'verify.py')]
                if a.hosted and package == 'r420-two-block-composition':
                    args.append('--hosted')
                subprocess.run(args, check=True, cwd=root)
            subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover',
                            '-s', 'research/r420-target-basis', '-p', 'test_*.py'],
                           check=True, cwd=root)
        if a.package_tests:
            subprocess.run([sys.executable, '-B', str(root / REL / 'test_package.py')],
                           check=True, cwd=root)


if __name__ == '__main__':
    main()
