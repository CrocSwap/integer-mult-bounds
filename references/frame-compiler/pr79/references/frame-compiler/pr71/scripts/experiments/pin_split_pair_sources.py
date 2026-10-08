#!/usr/bin/env python3
"""Explicit source and finite-input freeze for the selected split/pair witness."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('split_pair_graph.py', 'split_pair_compiler.py', 'split_pair_arithmetic.py',
         'split_pair_engine.py',
         'split_pair_compose.py', 'verify_split_pair.py', 'pin_split_pair_sources.py',
         'joint_dual_reclaim_compiler.py', 'binary_frame_math.py', 'binary_frame_replay.py',
         'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')


def required_paths():
    names = {'scripts/experiments/'+name for name in NAMES}
    names.update(('Makefile', 'README.md', 'NOTICE', 'research/split-pair/README.md',
                  'research/split-pair/PROOF.md', 'research/split-pair/parameters.json',
                  'research/split-pair/engine-provenance.json', 'research/split-pair/engine-changes.patch',
                  'tests/test_split_pair.py', 'tests/test_split_pair_pending.py',
                  'certificates/split-pair-compiler.json'))
    for h in (23,25):
        names.add(f'research/split-pair/config-{h}.json')
        names.update(f'certificates/split-pair-{kind}-{h}.{extension}'
                     for kind,extension in (('word','json.gz'),('profiles','json'),('transitions','json')))
    for prior in ('48', '59-split-operation', '65', '67', '68'):
        relative = Path('references/frame-compiler/pr'+prior)
        manifest = json.loads((ROOT/relative/'SOURCE.json').read_text())
        names.add(str(relative/'SOURCE.json'))
        names.update(str(relative/name) for name in manifest['files'])
    return names


def run():
    result = dict(
        baseline_pr65_commit='49e84f939d15b618b50714eb039cabf97c74256a',
        profile_cost_pr67_commit='b3745601e947a94316bf25c2c6263d93c06e3364',
        pending_live_pr68_commit='734c58e225e9d2254570c3b50296ed96943f62ea',
        split_operation_pr59_commit='641f22e52913db784f3b6ff1176b0c2945aae45b',
        author='Chafik Boukhalfa with OpenAI Codex assistance',
        scope='Explicit source and finite-input freeze. Credited contributor originals and complete published PR65 physical/arithmetic baseline are preserved. Exact composition and validation receipts are derived.',
        files={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(required_paths())})
    (ROOT/'research/split-pair/SOURCE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return len(result['files'])


if __name__ == '__main__':
    print('Pinned',run(),'sources and finite inputs')
