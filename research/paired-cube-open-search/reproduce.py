#!/usr/bin/env python3
"""Reproduce the open generator's results through PR161's unchanged physical checker, with exact replay.

Copyright 2026 Joel Pulikkan (GamingPuzzled). Apache-2.0. Prepared with Anthropic Claude assistance.

  1. PR161's own word is regenerated from its pinned sources (frozen arcs); its frozen physical plan is checked
     and must equal certificates/paired-cube-physical-input.json.
  2. The open generator plans frames and pairs for that same word; PR161's checker accepts them, including its
     exact numeric replay of the aliased signed word with arbitrary dirty scratch.
  3. The same pipeline on the cyclic all-but-one module, with open carrier matching (no frozen arcs).

Savings printed are float discovery scores of the complex supplier, not certificates; no kappa is claimed.
Usage: python3 research/paired-cube-open-search/reproduce.py    (Python 3.11+, numpy and scipy; a few minutes)
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generator
import search

PP = generator.PP
T0 = time.time()


def log(*a):
    print('[%4.0fs]' % (time.time() - T0), *a, flush=True)


def main():
    if sys.flags.optimize:
        raise SystemExit('run without -O')
    g, wit, word, record = PP.regenerated_word()
    frames_in = json.loads((PP.REF / 'frames.json').read_text())['frames']
    pairs_in = json.loads((PP.REF / 'pairs.json').read_text())['pairs']
    frozen = PP.physical(g, wit, word, record, frames_in, pairs_in)
    assert json.dumps(frozen, indent=2, sort_keys=True) + '\n' == PP.OUTPUT.read_text(), 'PR161 certificate differs'
    a0 = generator.float_saving(frozen)
    log('PASS PR161 frozen plan: %d frames, %d pairs, W %d, saving %.7e (equals its certificate)'
        % (frozen['changed_operation_frames'], frozen['pairs'], frozen['W_per_vertex'], a0))

    a1, res = generator.optimize(g, wit, word, record, passes=6, replay=True)
    log('PASS open generator on the PR161 word: %d frames, %d pairs, W %d, saving %.7e (%+.3f%%), replay %s'
        % (res['changed_operation_frames'], res['pairs'], res['W_per_vertex'], a1, 100 * (a1 / a0 - 1),
           res.get('scalar_replay') is not None))

    r = search.evaluate(dict(abo='cyclic'), passes=6, replay=True)
    assert r['saving'] > 0, r
    log('PASS cyclic all-but-one module with open matching: R %d, W %d, %d pairs, saving %.7e (%+.3f%%)'
        % (r['R'], r['W'], r['pairs'], r['saving'], 100 * (r['saving'] / a0 - 1)))


if __name__ == '__main__':
    main()
