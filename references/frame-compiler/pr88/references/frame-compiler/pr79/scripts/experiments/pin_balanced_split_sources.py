#!/usr/bin/env python3
"""Explicit source and finite-input freeze for the selected split/pair witness."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('balanced_split_graph.py', 'balanced_split_compiler.py', 'split_pair_arithmetic.py',
         'balanced_split_engine.py', 'balanced_split_exchange_engine.py',
         'balanced_split_compose.py', 'audit_balanced_split_completion.py', 'audit_balanced_split_exchange.py',
         'split_pair_engine.py', 'verify_balanced_split.py', 'pin_balanced_split_sources.py',
         'joint_dual_reclaim_compiler.py', 'binary_frame_math.py', 'binary_frame_replay.py',
         'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')


def required_paths():
    names = {'scripts/experiments/'+name for name in NAMES}
    names.update(('.gitattributes', 'Makefile', 'README.md', 'NOTICE', '.github/workflows/verify.yml', 'research/balanced-split/README.md',
                  'research/balanced-split/PROOF.md', 'research/balanced-split/parameters.json',
                  'research/balanced-split/engine-provenance.json', 'research/balanced-split/engine-relocation-23.patch',
                  'research/balanced-split/engine-relocation-25.patch',
                  'tests/test_balanced_split.py', 'tests/test_balanced_split_pending.py',
                  'certificates/balanced-split-compiler.json'))
    for h in (23,25):
        names.add(f'research/balanced-split/config-{h}.json')
        names.update(f'certificates/balanced-split-{kind}-{h}.{extension}'
                     for kind,extension in (('word','json.gz'),('profiles','json'),('transitions','json')))
    for prior in ('48', '59-split-operation', '65', '67', '68', '69', '70', '71'):
        relative = Path('references/frame-compiler/pr'+prior)
        manifest = json.loads((ROOT/relative/'SOURCE.json').read_text())
        names.add(str(relative/'SOURCE.json'))
        names.update(str(relative/name) for name in manifest['files'])
    return names


def run():
    result = dict(
        baseline_pr71_commit='1bef94fd40a746452548c84a4a8f8834670a3113',
        coarse_pr69_commit='91aa1f17e6e3fc063241686a41a34ddd0dc24c50',
        exchange_pr70_commit='98147912b80a2656da0416487be53f1f5e8dfdcc',
        baseline_pr65_commit='49e84f939d15b618b50714eb039cabf97c74256a',
        profile_cost_pr67_commit='b3745601e947a94316bf25c2c6263d93c06e3364',
        pending_live_pr68_commit='734c58e225e9d2254570c3b50296ed96943f62ea',
        split_operation_pr59_commit='641f22e52913db784f3b6ff1176b0c2945aae45b',
        author='Chafik Boukhalfa with OpenAI Codex assistance',
        scope='Explicit source and finite-input freeze. Credited contributor originals and complete published PR71 physical/arithmetic baseline are preserved. Exact composition and validation receipts are derived.',
        files={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(required_paths())})
    (ROOT/'research/balanced-split/SOURCE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return len(result['files'])


if __name__ == '__main__':
    print('Pinned',run(),'sources and finite inputs')
