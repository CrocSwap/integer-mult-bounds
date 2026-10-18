#!/usr/bin/env python3
"""Choose the 19 orbit representatives and pivots, and regenerate UNITS.json and PROOFS.json.gz, which
verify.py replays (needs python-sat; verify.py itself does not).

    python3 -I -B research/complex-rank8-rigidity-p109/make_proof.py --out-dir /new/dir

Representative: the first triple of each open orbit in verify.py's order. Pivot: the first frame inside the
live set, in line order, that passes (I3), (I4), gluing and Lemma 9 connectivity. Deletion lines are dropped
from the solver's DRUP output (verify.py's checker ignores them anyway). Any DRUP-producing solver may be
substituted; verify.py checks the proof, not the solver.
"""
import argparse
import gzip
import hashlib
import itertools
import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

SOLVER = 'g4'


def unit(X):
    from pysat.solvers import Solver
    live = [i for i in V.P112 if i not in X]
    F = next(F for F in V.frames_inside(live) if V.passes(V.inputs(live, F)))
    cnf, zvars = V.build_cnf(live, F)
    with Solver(name=SOLVER, bootstrap_with=cnf.clauses + [zvars], with_proof=True) as s:
        if s.solve():
            raise SystemExit(f'{X}: UNEXPECTED satisfiable')
        proof = [ln for ln in s.get_proof() if not ln.startswith('d')]
    text = '\n'.join(proof) + '\n'
    return F, text, V.cnf_digest(cnf.clauses + [zvars])


def main():
    global SOLVER
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--solver', default='g4')
    ap.add_argument('--jobs', type=int, default=8)
    args = ap.parse_args()
    SOLVER = args.solver
    out = Path(args.out_dir)
    for f in ('UNITS.json', 'PROOFS.json.gz'):
        if (out / f).exists():
            print(f'refusing to overwrite {out / f}')
            return 2
    frames = V.frames_inside(V.P112)
    inframe = {X for F in frames for X in itertools.combinations(F, 3)}
    open_ = [o for o in V.triple_orbits(V.stabiliser(V.FRAME0)[::V.GEN_STEP]) if o[0] not in inframe]
    reps = [o[0] for o in open_]
    with Pool(args.jobs, initializer=_init, initargs=(SOLVER,)) as pool:
        res = pool.map(unit, reps)
    units, proofs = {}, {}
    for n, (X, o, (F, text, cdig)) in enumerate(zip(reps, open_, res), 1):
        name = f'u{n:02d}'
        units[name] = {'orbit_size': len(o), 'triple': [V.LINES[i] for i in X], 'pivot': [V.LINES[i] for i in F],
                       'proof_sha256': hashlib.sha256(text.encode()).hexdigest(), 'cnf_sha256': cdig,
                       'lemmas': text.count('\n')}
        proofs[name] = text
        print(f"{name}: orbit {len(o)}, odd pairs {V.odd_pairs(X)}, {text.count(chr(10))} lemmas")
    (out / 'UNITS.json').write_text(json.dumps(units, indent=1) + '\n')
    (out / 'PROOFS.json.gz').write_bytes(gzip.compress(json.dumps(proofs, sort_keys=True).encode(), mtime=0))
    return 0


def _init(solver):
    global SOLVER
    SOLVER = solver


if __name__ == '__main__':
    sys.exit(main())
