#!/usr/bin/env python3
"""Explicit source and finite-input freeze for split/dual joint compilation."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('split_dual_graph.py', 'split_dual_compiler.py', 'split_dual_compose.py',
         'verify_split_dual.py', 'pin_split_dual_sources.py',
         'joint_dual_reclaim_compiler.py', 'binary_frame_math.py',
         'binary_frame_replay.py', 'binary_frame_profile_prepare.py', 'binary_frame_profiles.cpp')


def run():
    names = {'scripts/experiments/'+name for name in NAMES}
    names.update(('Makefile', 'README.md', 'NOTICE', 'research/split-dual/README.md',
                  'research/split-dual/PROOF.md', 'tests/test_split_dual.py',
                  'certificates/split-dual-compiler.json'))
    for h in (23,25):
        names.add(f'research/split-dual/config-{h}.json')
        names.update(f'certificates/split-dual-{kind}-{h}.{extension}'
                     for kind,extension in (('word','json.gz'),('profiles','json'),('transitions','json')))
    for prior in (48,55,59,60):
        relative = Path(f'references/frame-compiler/pr{prior}')
        manifest = json.loads((ROOT/relative/'SOURCE.json').read_text())
        names.add(str(relative/'SOURCE.json'))
        names.update(str(relative/name) for name in manifest['files'])
    result = dict(
        split_pr59_commit='641f22e52913db784f3b6ff1176b0c2945aae45b',
        suffix_pr55_commit='03e991aa79f9df1a935726213bb6a8631cd0d823',
        ranked_pr60_commit='21a121960644b8c6fdf9c06fe39dea1944dd2231',
        author='Chafik Boukhalfa with OpenAI Codex assistance',
        scope='Explicit source and finite-input freeze. Original contributor files and the full PR60 comparison are preserved; arithmetic certificates and validation receipts are derived.',
        files={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(names)})
    (ROOT/'research/split-dual/SOURCE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return len(names)


if __name__ == '__main__':
    print('Pinned',run(),'sources and finite inputs')
