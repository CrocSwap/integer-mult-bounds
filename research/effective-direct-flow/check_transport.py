#!/usr/bin/env python3
"""Replay a minimal source copy without Git and reject actual input corruptions.

No source artifact is written. Temporary copies are deleted by TemporaryDirectory.
Prepared for @alephnan with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest_tree(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    manifest = json.loads((HERE/'VERIFY.json').read_text(encoding='utf-8'))
    inputs = manifest['inputs']
    require(len(inputs) == 5, 'unexpected input closure')
    commands = []
    with tempfile.TemporaryDirectory(prefix='effective-flow-') as folder:
        root = Path(folder)
        package = root/'research/effective-direct-flow'
        package.mkdir(parents=True)
        for p in HERE.iterdir():
            if p.is_file():
                shutil.copyfile(p, package/p.name)
        for name in inputs:
            destination = root/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, destination)
        require(not (root/'.git').exists(), 'unexpected Git metadata')
        initial = digest_tree(root)
        env = dict(os.environ, PATH='')
        positive = 0
        rejected = 0
        outputs = []
        for optimized in (False, True):
            argv = [sys.executable, '-I'] + (['-O'] if optimized else [])
            argv += ['-W', 'error', '-B', str(package/'verify.py')]
            result = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                                    text=True, timeout=120)
            require(result.returncode == 0, 'isolated positive replay failed: '+result.stderr)
            value = json.loads(result.stdout)
            require(value['status'] == 'PASS_EFFECTIVE_DIRECT_FLOW', 'positive status')
            require(digest_tree(root) == initial, 'positive replay changed a file')
            outputs.append(value)
            positive += 1
            commands.append(['{python}', '-I'] + (['-O'] if optimized else [])
                            + ['-W', 'error', '-B', 'research/effective-direct-flow/verify.py'])
            for name in inputs:
                path = root/name
                original = path.read_bytes()
                try:
                    path.write_bytes(original+b'\n')
                    result = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                                            text=True, timeout=120)
                    require(result.returncode != 0 and 'source SHA256 mismatch' in result.stderr,
                            'actual corrupted input escaped source gate: '+name)
                    rejected += 1
                finally:
                    path.write_bytes(original)
            require(digest_tree(root) == initial, 'mutation restoration failed')
        require(outputs[0] == outputs[1], 'normal/optimized results differ')
    print(json.dumps({'status': 'PASS_SOURCE_TRANSPORT_CONTROLS',
                      'positive_replays': positive, 'actual_input_corruption_rejections': rejected,
                      'declared_external_inputs': len(inputs), 'git_available': False,
                      'child_PATH': '', 'source_files_unchanged': True,
                      'commands': commands}, indent=2))


if __name__ == '__main__':
    main()
