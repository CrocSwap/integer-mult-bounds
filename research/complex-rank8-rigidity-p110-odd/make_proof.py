#!/usr/bin/env python3
"""Choose the two orbit representatives and pivots, and regenerate the DRUP refutations that verify.py
replays (needs python-sat; verify.py itself does not).

    python3 -I -B research/complex-rank8-rigidity-p110-odd/make_proof.py --out-dir /new/dir

Representatives: the lexicographically first odd pair (in verify.py's line order) with each FRAME0 meet.
Pivot: the first frame inside the live set, in line order, that passes (I3), (I4), gluing and Lemma 9
connectivity. Any DRUP-producing solver may be substituted; verify.py checks the proof, not the solver.
"""
import argparse
import hashlib
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402


def frames_in(live):
    live = sorted(live)
    out = []

    def grow(cur, cand):
        if len(cur) == 8:
            out.append(cur)
            return
        for n, j in enumerate(cand):
            grow(cur + [j], [k for k in cand[n + 1:] if V.G[j][k] == 0])

    grow([], live)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--solver', default='g4')
    args = ap.parse_args()
    from pysat.solvers import Solver
    out = Path(args.out_dir)
    for m in (4, 2):
        pair = next(p for p in itertools.combinations(V.P112, 2)
                    if V.G[p[0]][p[1]] != 0 and V.meet(frozenset(p)) == m)
        live = [i for i in V.P112 if i not in pair]
        F = next(F for F in frames_in(live) if V.passes(V.inputs(live, F)))
        cnf, zvars = V.build_cnf(live, F)
        with Solver(name=args.solver, bootstrap_with=cnf.clauses + [zvars], with_proof=True) as s:
            if s.solve():
                print(f'meet{m}: UNEXPECTED satisfiable')
                return 1
            proof = s.get_proof()
        path = out / f'proof-meet{m}.drup'
        if path.exists():
            print(f'refusing to overwrite {path}')
            return 2
        text = '\n'.join(proof) + '\n'
        path.write_text(text)
        print(f"meet{m}: pair {[V.LINES[i] for i in pair]}")
        print(f"meet{m}: pivot {[V.LINES[i] for i in F]}")
        print(f"meet{m}: {len(proof)} proof lines, sha256 {hashlib.sha256(text.encode()).hexdigest()}, "
              f"cnf {V.cnf_digest(cnf.clauses + [zvars])}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
