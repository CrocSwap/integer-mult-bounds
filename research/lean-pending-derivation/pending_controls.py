#!/usr/bin/env python3
"""Mutation controls for PendingDerivation.lean: each mutated copy must fail to compile.

usage: pending_controls.py LEAN OLEAN_DIR
OLEAN_DIR must already hold PendingScheduleData.olean and OwnershipDatumCore.olean.
Douglas Colkitt, with Claude (Anthropic) assistance. Apache-2.0.
"""
import os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = (ROOT / 'PendingDerivation.lean').read_text()
DATA = (ROOT / 'PendingScheduleData.lean').read_text()
MUTATIONS = {
    'level_minus_one_empty': ('PendingDerivation', 'if l = 0 then i == 0', 'if l = 0 then false'),
    'level_minus_one_whole_local_block': ('PendingDerivation', 'if l = 0 then i == 0', 'if l = 0 then i < 8'),
    'exterior_block_off_by_one_stage': ('PendingDerivation', 'exteriorBlocks.take (l - 1)', 'exteriorBlocks.take l'),
    'child1_advanced_before_selected_call': ('PendingScheduleData', '  .local 2 0,\n  .idle 1 1 7 2 3,',
                                             '  .idle 1 1 7 2 3,\n  .local 2 0,'),
    'child1_previous_block_claimed': ('PendingDerivation', 'pendingAxes 1 = List.range\' 15 7',
                                      'pendingAxes 1 = List.range\' 8 7'),
    'swapped_exterior_blocks': ('PendingScheduleData', '  [8, 9, 10, 11, 12, 13, 14],\n  [15, 16, 17, 18, 19, 20, 21],',
                                '  [15, 16, 17, 18, 19, 20, 21],\n  [8, 9, 10, 11, 12, 13, 14],'),
}


def main(lean, olean):
    results = {}
    for name, (module, old, new) in MUTATIONS.items():
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            env = dict(os.environ, LEAN_PATH=f'{tmp}{os.pathsep}{olean}')
            src = SRC
            if module == 'PendingScheduleData':
                assert DATA.count(old) == 1, name
                (tmp / 'd.lean').write_text(DATA.replace(old, new))
                r = subprocess.run([lean, f'--root={tmp}', '-o', str(tmp / 'PendingScheduleData.olean'), str(tmp / 'd.lean')],
                                   env=env, capture_output=True, text=True)
                assert r.returncode == 0, r.stdout + r.stderr
            else:
                assert src.count(old) == 1, name
                src = src.replace(old, new)
            (tmp / 'm.lean').write_text(src)
            r = subprocess.run([lean, f'--root={tmp}', str(tmp / 'm.lean')], env=env, capture_output=True, text=True)
            err = next((l for l in r.stdout.splitlines() if 'error' in l), '')
            assert 'unknown' not in err and 'object file' not in err, err   # fail on a proof, not on setup
            results[name] = ('rejected: ' + err.split('error: ', 1)[-1][:90]) if r.returncode != 0 else 'ACCEPTED'
            print(f'{name}: {results[name]}', flush=True)
    assert all(v.startswith('rejected') for v in results.values()), results
    print('PASS: all', len(results), 'mutations rejected')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
