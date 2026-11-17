#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check all forward and adjoint columns of the new paid child.

Ali Romman, with substantial OpenAI Codex assistance. The method retains
Hao Yan/7604 and DreamingOfClouds/7601; the exact interpreter is unchanged.
"""
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
BUILD = runpy.run_path(str(HERE / 'build.py'))
require = BUILD['require']


def normalize(state):
    values, denominator = state
    while denominator and values and all((a | b) % 2 == 0 for a, b in values.values()):
        values = {k: (a // 2, b // 2) for k, (a, b) in values.items()}
        denominator -= 1
    return values, denominator


def main():
    word = BUILD['build_word']()
    engine = runpy.run_path(str(HERE / 'retained/token-settled/chart.py'))
    frames = [word['frames'][i] for i in (3, 595, 603)]
    require([len(f) for f in frames] == [0, 1, 2], 'nested frame dimensions')
    frame, inv, compile_gate, run = (engine[k] for k in ('frame', 'inverse_circuit', 'compile_gate', 'run'))
    a, b, c = map(frame, frames)
    old, new = inv(a) + b + inv(b) + c, inv(a) + c
    for label, left, right in (('forward', old, new), ('adjoint', inv(old), inv(new))):
        left, right = list(map(compile_gate, left)), list(map(compile_gate, right))
        for column in range(512):
            require(normalize(run(left, column)) == normalize(run(right, column)),
                    label + ' Gaussian column ' + str(column))
    require(engine['child_rank'](frames[0], frames[2]) == 2, 'exact direct rank')
    good = list(map(compile_gate, new))
    bad = list(map(compile_gate, inv(b) + c))
    require(any(normalize(run(good, i)) != normalize(run(bad, i)) for i in range(512)),
            'reject wrong source frame')
    values, denominator = run(good, 0)
    rotated = {k: (-im, re) for k, (re, im) in values.items()}, denominator
    require(normalize((values, denominator)) != normalize(rotated), 'reject wrong absolute phase')
    print(json.dumps(dict(status='PASS_HELPER757_PHYSICAL', frames=[3, 595, 603],
                         forward_columns=512, adjoint_columns=512, direct_rank=2,
                         wrong_source_rejected=True, wrong_absolute_phase_rejected=True)))


if __name__ == '__main__':
    main()
