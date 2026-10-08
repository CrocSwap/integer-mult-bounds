#!/usr/bin/env python3
"""Explicit source/finite-input freeze for ranked reclamation after PR58.
Prepared by Chafik Boukhalfa with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import json
ROOT = Path(__file__).resolve().parents[2]
NAMES = ('joint_dual_compiler.py', 'joint_dual_compose.py', 'verify_joint_dual.py',
         'pin_joint_dual_sources.py', 'binary_frame_compiler.py', 'joint_dual_reclaim_compiler.py', 'binary_frame_math.py',
         'binary_frame_replay.py', 'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')

def run():
    names = {'scripts/experiments/'+name for name in NAMES}
    names.update(('Makefile', 'README.md', 'NOTICE', 'research/joint-dual/README.md',
                  'research/joint-dual/PROOF.md', 'certificates/joint-dual-compiler.json',
                  'certificates/skip-frame-kappa.json', 'tests/test_joint_reclaim.py'))
    for h in (23,25):
        names.update(f'certificates/joint-dual-{kind}-{h}.{extension}'
                     for kind,extension in (('word','json.gz'),('profiles','json'),('transitions','json')))
    for prior in (48,53,55,58):
        relative = Path(f'references/frame-compiler/pr{prior}')
        manifest = json.loads((ROOT/relative/'SOURCE.json').read_text())
        names.add(str(relative/'SOURCE.json'))
        names.update(str(relative/name) for name in manifest['files'])
    result = dict(
        base_pr57_commit='cd350f76c9bc01489ec83568bded532cb69be938',
        base_pr58_commit='bc2f7ed4c20dc18898305ab17165c0c995cbb804',
        producer_pr55_commit='03e991aa79f9df1a935726213bb6a8631cd0d823',
        author='Chafik Boukhalfa with OpenAI Codex assistance',
        scope='Explicit reviewed source and finite-input freeze; arithmetic certificates and validation receipts are derived.',
        files={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(names)})
    (ROOT/'research/joint-dual/SOURCE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return len(names)

if __name__ == '__main__':
    print('Pinned',run(),'sources and finite inputs')
