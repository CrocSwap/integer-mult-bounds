# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Iterate the planL3 CP-SAT model until every block's node can reach rank 12 (gen_l3.plan_thirds succeeds).
Failing blocks get a no-good cut on the X bits and recipient choices of their served targets; random objectives
diversify the solutions.  usage: python -I planL3b.py OUT_PLAN.json [seed] [cycle]   (needs ortools; not run by verify.sh)"""
import os
import random
import sys

from ortools.sat.python import cp_model

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "e8-bit-carrier-skeleton", "code", "skeleton"))   # PR #493 on main
sys.path.insert(0, os.path.join(HERE, "..", "code"))
sys.path.insert(0, HERE)
from geom import Geom  # noqa: E402
from planL3 import build_model, save_plan, extract  # noqa: E402
from gen_l3 import plan_thirds  # noqa: E402

V = 120


def main():
    out = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    cyc = len(sys.argv) > 3 and sys.argv[3] == "cycle"
    G = Geom()
    rng = random.Random(seed)
    M, Vv = build_model(G, rank_mode="strong", cycle_only=cyc)
    # random objective on the Q-extra bits and recipients for diversity
    obj = []
    for k, b in Vv["X"].items():
        obj.append(rng.randrange(-3, 4) * b)
    for k, b in Vv["rcv"].items():
        obj.append(rng.randrange(-3, 4) * b)
    M.Maximize(sum(obj))
    for it in range(200):
        S = cp_model.CpSolver()
        S.parameters.max_time_in_seconds = 20.0
        S.parameters.num_workers = 4
        S.parameters.random_seed = seed + it
        r = S.Solve(M)
        if r not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print("iteration", it, "status", S.StatusName(r))
            return
        sol = extract(S, Vv)
        pt = plan_thirds(G, sol, random.Random(seed * 1000 + it), tries=4000)
        if pt[0] != "failed":
            save_plan(sol, out)
            print("iteration", it, "all blocks reach rank 12; plan saved", out)
            return
        failed = pt[1]
        print("iteration", it, "failed blocks", failed)
        for bi in failed:
            cb = G.comp[bi]
            us = [t for t in range(V) if G.blk[t] == cb]
            lits = []
            for u in us:
                for l in G.psi[G.phi[u]]:
                    b = Vv["X"][u, l]
                    lits.append(b.Not() if S.Value(b) else b)
            for (c, t), b in Vv["rcv"].items():
                if G.cblk[c] == cb:
                    lits.append(b.Not() if S.Value(b) else b)
            M.AddBoolOr(lits)


main()
