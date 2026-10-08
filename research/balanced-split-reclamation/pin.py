#!/usr/bin/env python3
"""Explicitly freeze the candidate; verification never refreshes this file."""
from hashlib import sha256
import json
from pathlib import Path
from support import HERE, ROOT, write_json


def main():
    local = [p for p in HERE.rglob('*') if p.is_file() and p.name not in ('SOURCE.json', 'VALIDATION.json')
             and p.suffix not in ('.pyc', '.log', '.aux', '.out') and '__pycache__' not in p.parts]
    inherited = [ROOT/p for p in (
        'research/pair-assembly/pair_graph.py', 'research/pair-assembly/frame/frame_verify.py',
        'research/pair-assembly/frame/frame-compiler.json',
        'scripts/experiments/binary_frame_math.py', 'scripts/experiments/binary_frame_replay.py',
        'scripts/experiments/binary_frame_profile_prepare.py', 'scripts/experiments/binary_frame_profiles.cpp',
        'scripts/exclusion_circuit.py', 'scripts/partial_swap/paired.py', 'scripts/partial_swap/shared.py',
        'references/frame-compiler/pr48/SOURCE.json', '.github/workflows/balanced-split.yml')]
    manifest = json.loads((ROOT/'references/frame-compiler/pr48/SOURCE.json').read_text())
    inherited += [ROOT/'references/frame-compiler/pr48'/p for p in manifest['files']]
    files = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sorted(set(local+inherited))}
    write_json(HERE/'SOURCE.json', dict(files=files, scope='Explicit source and artifact freeze; no automatic refresh in verification',
        upstream=dict(pr67='b3745601e947a94316bf25c2c6263d93c06e3364',
                      pr68='8778fdb52e834a2a14371590d80ea6e0c734a866',
                      pr69='91aa1f17e6e3fc063241686a41a34ddd0dc24c50',
                      pr71='1bef94fd40a746452548c84a4a8f8834670a3113')))
    print('Pinned', len(files), 'source and artifact files')


if __name__ == '__main__':
    main()
