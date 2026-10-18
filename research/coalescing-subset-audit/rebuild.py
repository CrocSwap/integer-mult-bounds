"""Rebuild only the pinned raw word needed by this audit, not its admission.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import os
from pathlib import Path
import subprocess
import sys


def rebuild(root, work):
    parent = root / 'research/kernel-frame-coalescing/vendor/pr579'
    source = parent / 'vendor/pr575'
    gk = source / 'vendor/pr558/vendor/pr552/complex-local/static44/gk'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    env.pop('PYTHONOPTIMIZE', None)

    def run(script, *args):
        command = [sys.executable, '-B', str(script), *map(str, args)]
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f'{script.name} failed:\n{result.stdout}\n{result.stderr}')
        print('PASS rebuild', script.name, flush=True)

    run(source / 'code/reconstruct558_portable.py', '--out', work / 'baseline')
    run(source / 'code/build_cold_kernel.py',
        '--input', work / 'baseline/promoted/FULL-WORD.json.gz',
        '--recipe', source / 'data/EIGHT-COLD.json', '--gk-dir', gk,
        '--out', work / 'first')
    run(source / 'code/build_multicut_kernels.py',
        '--input', work / 'first/FULL-WORD.json.gz',
        '--recipe', source / 'data/EIGHT-MULTICOLD.json', '--gk-dir', gk,
        '--out', work / 'eight')
    run(source / 'code/build_entrance_promotions.py',
        '--word', work / 'eight/FULL-WORD.json.gz',
        '--recipes', source / 'data/width7/eight/RECIPES.json', '--gk-dir', gk,
        '--out', work / 'promoted')
    run(source / 'code/build_joint_prefix.py',
        '--input', work / 'promoted/FULL-WORD.json.gz',
        '--recipe', source / 'data/JOINT-PREFIX.json', '--variant', 'width7',
        '--gk-dir', gk, '--out', work / 'joint')
    run(parent / 'code/build_multicut_kernels.py',
        '--input', work / 'joint/FULL-WORD.json.gz',
        '--recipe', parent / 'data/P571K-MULTICOLD.json', '--gk-dir', gk,
        '--out', work / 'source')
    return work / 'source/FULL-WORD.json.gz'
