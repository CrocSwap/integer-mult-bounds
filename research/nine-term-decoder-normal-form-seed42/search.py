#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded heuristic search over one-sided nine-term decoders (Corollary C form).  NOT a proof.

Domain: the five frames of verify.py section F, each on P120 and on P120 minus the lines parallel to
frame normals ("self-punctured"); per-line options = every ratio class plus one generic t (exact).
Method: simulated annealing over per-line options, exact cost after every move.
Stopping rule: fixed iteration count per (frame, live set, seed); seeds 0..SEEDS-1.

    python3 -I -B research/nine-term-decoder-normal-form-seed42/search.py [--iters 3000] [--seeds 3]
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e8lab as E  # noqa: E402
import verify as V  # noqa: E402


def anneal(fr, live, iters, seed):
    rng = random.Random(seed)
    opts = {i: [c for t, c in fr.options(i)] for i in E.bits(live)}
    Y = [E.support(b, live) for b in fr.F]

    def cost(ch):
        X = [0] * 9
        for i, c in ch.items():
            for k, x in enumerate(c):
                if x != 0:
                    X[k] |= 1 << i
        return sum(E.pairing_rank(X[k], Y[k]) for k in range(9))
    ch = {i: min(o, key=lambda c: sum(1 for x in c if x != 0)) for i, o in opts.items()}
    c = cost(ch)
    start = best = c
    temp = 1.5
    movable = [i for i in opts if len(opts[i]) > 1]
    for _ in range(iters):
        i = rng.choice(movable)
        old = ch[i]
        ch[i] = rng.choice(opts[i])
        c2 = cost(ch)
        if c2 <= c or rng.random() < math.exp(-(c2 - c) / temp):
            c = c2
        else:
            ch[i] = old
        best = min(best, c)
        temp = max(0.05, temp * 0.9993)
    return start, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--iters', type=int, default=3000)
    ap.add_argument('--seeds', type=int, default=3)
    ap.add_argument('--out')
    a = ap.parse_args()
    frames = V.build_frames()
    rows = []
    for name, fr in frames.items():
        P = 0
        for b in fr.F:
            for i, l in enumerate(E.LINES):
                if E.q_rank([list(b), list(l)]) == 1:
                    P |= 1 << i
        for lname, live in (('P120', E.FULL), ('self-punctured', E.FULL & ~P)):
            if lname != 'P120' and P == 0:
                continue
            for s in range(a.seeds):
                st, b = anneal(fr, live, a.iters, s)
                v = E.popcount(live)
                rows.append({'frame': name, 'live': lname, 'v': v, 'seed': s, 'iters': a.iters,
                             'start_cost': st, 'best_cost': b, 'best_ratio': f'{b}/{v}'})
                print(f'{name:28s} {lname:15s} v={v:3d} seed={s} start={st} best={b} ratio={b / v:.4f}', flush=True)
    rec = {'domain': 'verify.py section F frames x {P120, self-punctured}; per-line ratio-class options',
           'stopping_rule': f'{a.iters} annealing moves per run, seeds 0..{a.seeds - 1}',
           'comparators': {'P120 eight-term floor': 72, 'P112 shipped': '64/112', 'PR968 best ratio': '56/104'},
           'runs': rows}
    if a.out:
        Path(a.out).write_text(json.dumps(rec, indent=1) + '\n')
    best = min(r['best_cost'] / r['v'] for r in rows)
    print(f'SEARCH_DONE runs={len(rows)} best_ratio={best:.4f} (7/13={7 / 13:.4f}, 4/7={4 / 7:.4f}); no candidate below 4/7'
          if best >= 4 / 7 else f'SEARCH_DONE runs={len(rows)} best_ratio={best:.4f} CANDIDATE BELOW 4/7')


if __name__ == '__main__':
    main()
