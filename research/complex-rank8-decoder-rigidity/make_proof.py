#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the DRUP refutation checked by verify.py (needs python-sat; verify.py itself does not).

    python3 -I -B research/complex-rank8-decoder-rigidity/make_proof.py --live P112 --out /new/proof-P112.drup

The CNF is built by verify.build_zero_cnf with its deterministic variable numbering, conjoined with the
clause "some pattern variable is true" (some entry of K[:,F] or K[F,:] vanishes on its block).  A DRUP
proof produced by any solver can be substituted; verify.py replays it with its own RUP checker.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--live', default='P112', help='P112, P120, or an extension unit name (P111, P104-44, P104-2222, P104-11111111)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--solver', default='g4', help='pysat solver name with proof support (g4 = Glucose 4.1)')
    ap.add_argument('--families', default=None, help='comma-separated clause families (default all: two,four,diag,trans)')
    args = ap.parse_args()
    from pysat.solvers import Solver
    if args.live in ('P112', 'P120'):
        live = V.P112 if args.live == 'P112' else V.P120
        F = V.choose_pivot(live)
    else:
        units = V.extension_units()[0]
        live, F, _desc = units[args.live]
        F = list(F)
        if args.families is None:
            args.families = ','.join(V.EXPECTED['EXT']['units'][args.live]['families'])
    rel = V.blocks_relative(F, live)
    fams = None if args.families is None else set(args.families.split(','))
    cnf, zvars, stats = V.build_zero_cnf(live, F, rel, options=fams)
    clauses = [list(c) for c in cnf.clauses] + [list(zvars)]
    with Solver(name=args.solver, bootstrap_with=clauses, with_proof=True) as s:
        sat = s.solve()
        proof = s.get_proof()
    if sat:
        print('UNEXPECTED: satisfiable; a nontrivial zero pattern exists')
        return 1
    out = Path(args.out)
    if out.exists():
        print(f'refusing to overwrite {out}')
        return 2
    out.write_text('\n'.join(proof) + '\n')
    print(f'UNSAT; wrote {len(proof)} proof lines to {out} (vars {len(cnf.names)}, clauses {len(clauses)}, {stats})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
