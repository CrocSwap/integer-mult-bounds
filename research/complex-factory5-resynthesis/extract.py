#!/usr/bin/env python3
"""Observe the pinned, unchanged PR622 constructor; do not patch its source.

Prepared for alluri-ritual with substantial OpenAI Codex assistance. Apache-2.0.
"""
import contextlib
import copy
import io
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONSTRUCTOR = ROOT / 'research/complex-k492-owner-repair/code/construct_k_triangle.py'


def extract(out):
    if sys.flags.optimize:
        raise RuntimeError('The inherited constructor requires assertions enabled')
    lines = CONSTRUCTOR.read_text().splitlines()
    begin = lines.index('    regs=retired') + 1
    end = lines.index('    for i,r in zip(c,regs):') + 1
    snapshots = {}

    def trace(frame, event, arg):
        if frame.f_code.co_filename != str(CONSTRUCTOR):
            return None
        if event == 'line' and frame.f_lineno in (begin, end):
            f = frame.f_locals
            index = sorted(f['blocks']).index(tuple(f['c']))
            snapshot = snapshots.setdefault(index, {})
            if frame.f_lineno == begin:
                snapshot.update(block=list(f['c']), start=len(f['A']),
                                registers=f['retired'][:], frame=list(f['F']),
                                entry_frames=[list(f['cur'][r]) for r in f['retired']])
            else:
                snapshot.update(end=len(f['A']),
                                gates=copy.deepcopy(f['A'][snapshot['start']:]),
                                exit_frames=[list(f['cur'][r]) for r in f['regs']])
        return trace

    old_argv, old_trace = sys.argv, sys.gettrace()
    try:
        sys.argv = [str(CONSTRUCTOR),
                    str(ROOT / 'research/direct-delivery504-global/inputs/hamming'),
                    str(out),
                    str(ROOT / 'research/complex-k492-owner-repair/data/TRI-SCHEDULE.json')]
        sys.settrace(trace)
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(CONSTRUCTOR), run_name='__main__')
    finally:
        sys.settrace(old_trace)
        sys.argv = old_argv
    expected = {'block', 'start', 'registers', 'frame', 'entry_frames',
                'end', 'gates', 'exit_frames'}
    if set(snapshots) != set(range(14)) or any(set(w) != expected for w in snapshots.values()):
        raise ValueError('Constructor windows not observed completely')
    (out / 'WINDOWS.json').write_text(json.dumps(snapshots, indent=2) + '\n')


if __name__ == '__main__':
    extract(Path(sys.argv[1]).resolve())
