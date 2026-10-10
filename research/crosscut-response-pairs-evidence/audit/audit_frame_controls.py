#!/usr/bin/env python3
"""Reproduce six independent corruptions of the additive exact frame audit.

Runs small artificial frame-table controls only. This does not replace the
mandatory full frame-table audit or any native physical-word replay.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

if not __debug__:
    raise SystemExit('assertions required')
sys.dont_write_bytecode = True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--checker', type=Path, required=True,
                    help='source-bound verify_frame_tables.py')
    ap.add_argument('--export', type=Path, required=True,
                    help='regenerated CURRENT249-EXPORT directory')
    ap.add_argument('--lead', type=Path, required=True,
                    help='candidate directory containing COHORT249-FRAMES.json')
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists(), 'use a fresh output path'
    spec = importlib.util.spec_from_file_location('audited_frame_checker', a.checker)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    frames_path = a.lead / 'COHORT249-FRAMES.json'
    frames = json.loads(frames_path.read_text())
    key, good = next((key, frame) for key, frame in frames.items() if frame['dim'] == 2)
    controls = {}
    frame = copy.deepcopy(good)
    frame['B'][1] = frame['B'][0][:]
    controls['dependent_basis'] = frame
    frame = copy.deepcopy(good)
    frame['A'][1] = frame['A'][0][:]
    controls['dependent_annihilator'] = frame
    frame = copy.deepcopy(good)
    j = next(j for j, x in enumerate(frame['B'][0]) if x)
    frame['A'][0][j] += 1
    controls['nonorthogonal_annihilator'] = frame
    # u has ordinary squared norm 9 and coordinate sum 9, hence
    # u (I-J/9) u^T = 9-81/9 = 0. A is an exact rank-23 annihilator.
    u = [1]*9 + [0]*15
    annihilator = []
    for i in range(1, 9):
        row = [0]*24
        row[0], row[i] = -1, 1
        annihilator.append(row)
    for i in range(9, 24):
        row = [0]*24
        row[i] = 1
        annihilator.append(row)
    controls['degenerate_weighted_gram'] = {'dim': 1, 'B': [u], 'A': annihilator}
    frame = copy.deepcopy(good)
    frame['dim'] = 3
    controls['incorrect_dimension'] = frame
    frame = copy.deepcopy(good)
    frame['B'][0].pop()
    controls['short_basis_row'] = frame
    rejected = {}
    with tempfile.TemporaryDirectory(prefix='frame-controls-') as work:
        path = Path(work)
        (path/'COHORT249-RECORDS.bin').write_bytes(b'')
        (path/'COHORT249-FRAMES.json').write_text(json.dumps({key: good}))
        assert module.verify(a.export, path)['added_frames'] == 1
        for name, frame in controls.items():
            (path/'COHORT249-FRAMES.json').write_text(json.dumps({key: frame}))
            try:
                module.verify(a.export, path)
            except AssertionError as error:
                rejected[name] = str(error)
            else:
                raise AssertionError('corrupted frame admitted: ' + name)
    sources = {'frame_checker': a.checker, 'candidate_frames': frames_path,
               'inherited_frames': a.export/'frames.json'}
    result = dict(status='PASS_FRAME_CORRUPTION_CONTROLS',
                  full_physical_replay_claimed=False,
                  valid_rank_two_frame_admitted=True, valid_frame_id=key,
                  rejected=rejected,
                  sources={name: dict(path=str(path.resolve()),
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                           for name, path in sources.items()})
    a.output.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('status', 'valid_rank_two_frame_admitted', 'rejected')}))


if __name__ == '__main__':
    main()
