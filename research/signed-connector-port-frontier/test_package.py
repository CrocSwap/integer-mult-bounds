#!/usr/bin/env python3
"""Actual on-disk corruption rejection and read-only relocated complete replay.
Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def edit_json(path, mutate):
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data))


def run(package, receipts=False):
    command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]
    if receipts:
        command += ['--check-receipts-only']
    env = dict(os.environ, PYTHONOPTIMIZE='2')
    return subprocess.run(command, cwd=package.parent, env=env, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)


def main():
    mutations = [
        ('source corruption', 'sources/PR1651-COST.md', lambda p: p.write_text(p.read_text() + '\nCORRUPTION\n')),
        ('domain undercount', 'CERTIFICATE.json', lambda p: edit_json(p, lambda d: d.update(source_traces=7257599))),
        ('invented alternative port', 'CERTIFICATE.json', lambda p: edit_json(p, lambda d: d['counts'].__setitem__(34, 1))),
        ('wrong witness port', 'CERTIFICATE.json', lambda p: edit_json(p, lambda d: d['witnesses'][0]['word'][0].__setitem__(3, 1))),
        ('lost dirt sensitivity', 'independent-results.json', lambda p: edit_json(p, lambda d: d['controls']['omit_same_dirt_requirement_invalid'].update(feasible_source_trace_count=80))),
        ('underpriced head motion', 'DENSE.json', lambda p: edit_json(p, lambda d: d['witnesses'][0]['head_move_polynomial_descending'].__setitem__(1, 2043))),
        ('unlisted source', 'sources/extra.txt', lambda p: p.write_text('extra source')),
    ]
    with tempfile.TemporaryDirectory(prefix='port-package-controls-') as temp:
        root = Path(temp)
        for index, (name, relative, mutate) in enumerate(mutations):
            package = root / str(index)
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            mutate(package / relative)
            result = run(package, receipts=True)
            require(result.returncode != 0 and 'PASS_' not in result.stdout, 'corruption accepted: ' + name)
        relocated = root / 'read-only-package'
        shutil.copytree(HERE, relocated, ignore=shutil.ignore_patterns('__pycache__'))
        paths = list(relocated.rglob('*'))
        for path in paths:
            path.chmod(0o555 if path.is_dir() else 0o444)
        relocated.chmod(0o555)
        try:
            result = run(relocated)
            require(result.returncode == 0 and 'PASS_SIGNED_CONNECTOR_PORT_RIGIDITY' in result.stdout,
                    'read-only relocated full replay failed: ' + result.stdout + result.stderr)
        finally:
            relocated.chmod(0o755)
            for path in paths:
                if path.is_dir():
                    path.chmod(0o755)
    print('PASS_PORT_PACKAGE_CONTROLS corruptions=7 readonly_full_replay=true optimized=true')


if __name__ == '__main__':
    main()
