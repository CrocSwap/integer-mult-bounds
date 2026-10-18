#!/usr/bin/env python3
"""Reproduce a retained T16 packing variant without modifying the selected package.

Supply the completed local word from gauge44-slots/verify_slots.py. This is an
owner/assembly replay, not a substitute for that construction or bit ancestry.
Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pr', type=int, choices=[1022, 1028, 1031, 1042], required=True)
    p.add_argument('--local', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    a = p.parse_args()
    if sys.flags.optimize:
        raise ValueError('Supplier workers require assertions')
    work = a.work.resolve()
    if work.exists() or work.is_relative_to(ROOT):
        raise ValueError('Use fresh external output')
    work.mkdir(parents=True)
    package = work/'package'
    shutil.copytree(ROOT/'research/gauge44-slots-t16', package,
                    ignore=shutil.ignore_patterns('__pycache__'))
    if a.pr != 1042:
        variant = ROOT/f'research/community-batch1047-audit/variants/pr{a.pr}/research/gauge44-slots-t16'
        names = {p.relative_to(variant).as_posix() for p in variant.rglob('*') if p.is_file()}
        expected = {'MANIFEST.json', 'README.md', 'RESULT.json', 'data/OWNERS.json.gz', 'data/PLAN.json', 'data/SPEC.json'}
        if names != expected:
            raise ValueError('Incomplete variant source inventory')
        for name in names:
            shutil.copyfile(variant/name, package/name)
    subprocess.run([sys.executable, '-B', str(package/'verify_manifest.py')], check=True, cwd=ROOT)
    subprocess.run([sys.executable, '-B', str(package/'verify_t16.py'), '--main', str(ROOT),
                    '--local', str(a.local.resolve()), '--work', str(work/'replay')], check=True, cwd=ROOT)


if __name__ == '__main__':
    main()
