#!/usr/bin/env python3
"""Replay the independently frozen bit supplier, then expose its exact profile.

The nested package retains its own manifest, verifier, input pins and notices.
Prepared for eumemic with OpenAI Codex assistance; Apache-2.0.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Bit adapter requires assertions')
from pathlib import Path
from hashlib import sha256
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
BIT_MANIFEST_PIN = '1f8afd0109706437445fcc9b3bacff455c0d229b8ad2d3d106f3cd6c43bc58b3'
BIT_VERIFIER_PIN = '58ccce67e0a6ca9db91d195250eb9fdb8ccae27b5fe22fb6b1b32f512a476146'
MINIMAL_V_PIN = '298c11fb29ab0afdf8d762c64a9b99d19a1e58465f3a0cbc9d2a59367c438fb7'
MINIMAL_V_PATH = 'inputs/research/round8-foundations-minimal-v-word.json.gz'


def package_inventory(package):
    nested = package / 'bit-sharing'
    raw = (nested / 'MANIFEST.json').read_bytes()
    if sha256(raw).hexdigest() != BIT_MANIFEST_PIN:
        raise ValueError('Immutable bit-package manifest digest mismatch')
    manifest = json.loads(raw)
    files = manifest['sha256']
    if files.get('verify.py') != BIT_VERIFIER_PIN or files.get(MINIMAL_V_PATH) != MINIMAL_V_PIN:
        raise ValueError('Immutable bit verifier or minimal-V provenance digest mismatch')
    for name, expected in files.items():
        relative = Path(name)
        path = (nested / relative).resolve()
        if relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(nested.resolve()):
            raise ValueError('Unsafe nested bit manifest path: ' + name)
        if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Nested bit source hash mismatch: ' + name)
    return {'bit-sharing/MANIFEST.json': BIT_MANIFEST_PIN,
            **{'bit-sharing/' + name: value for name, value in files.items()}}


def main():
    package_inventory(HERE)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    environment.pop('PYTHONPATH', None)
    subprocess.run([sys.executable, str(HERE / 'bit-sharing/verify.py')],
                   cwd=HERE, env=environment, check=True)
    profile = json.loads((HERE / 'bit-sharing/profile161.json').read_text())
    assert profile['L'] == profile['total_rank'] - profile['W'] * profile['m'] + profile['N']
    (HERE / 'shared-bit-profile.json').write_text(json.dumps(profile, indent=2) + '\n')
    print('PASS full nested bit replay and shared-bit profile', flush=True)


if __name__ == '__main__':
    main()
