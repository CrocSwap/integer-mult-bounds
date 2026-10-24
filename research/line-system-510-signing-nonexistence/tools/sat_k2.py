"""Idea 3, decisive small test: does the k'=2 descendant exist?
120 unit lines in R^24, labels W(3,2) with multiplicity 8, |cos| in {0, 1/4},
saturated. Frame-reduced encoding E2 (REPORT.md section 3), solved with CP-SAT.

If INFEASIBLE: the 510-line object in R^30 cannot exist (descent, REPORT.md section 2).
If FEASIBLE: the solution is rebuilt as exact integer vectors and every pairwise
product is re-checked; the vectors go to sat_k2_solution.json.

Run:  py -3.12 sat_k2.py [time_limit_seconds=1800] [workers=8]
Progress lines go to progress.log every 60 s; CP-SAT's own log to sat_k2_cpsat.log.
"""
import datetime
import itertools
import json
import os
import sys
import threading
import time

from ortools.sat.python import cp_model

from frame_reduction import b, build

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "progress.log")
K = 2


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    limit = float(sys.argv[1]) if len(sys.argv) > 1 else 1800.0
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    nclasses = int(sys.argv[3]) if len(sys.argv) > 3 else None
    m, pts, L, others, supp, T = build(K)
    if nclasses is not None:
        # sub-test: keep only the first nclasses classes p0 + L (a necessary condition)
        keys = sorted({tuple(b(xx, p, K) for xx in L) for p in others})[:nclasses]
        others = [p for p in others if tuple(b(xx, p, K) for xx in L) in keys]
        log(f"   sub-test: only {nclasses} of {2**K - 1} classes, {len(others)} points kept")
    suf = f"_c{nclasses}" if nclasses else ""
    lines = [(p, j) for p in others for j in range(m)]
    model = cp_model.CpModel()
    x = {}
    for li, (p, j) in enumerate(lines):
        for c in supp[p]:
            x[li, c] = model.NewBoolVar(f"x{li}_{c}")
    # gauge: x = 0 on a spanning forest of the line/coordinate incidence graph
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    fixed = 0
    for li, (p, j) in enumerate(lines):
        for c in supp[p]:
            ra, rb = find(("l", li)), find(("c", c))
            if ra != rb:
                parent[ra] = rb
                model.Add(x[li, c] == 0)
                fixed += 1
    npairs = 0
    for (i1, (p, _)), (i2, (q, _)) in itertools.combinations(enumerate(lines), 2):
        I = sorted(set(supp[p]) & set(supp[q]))
        if not I:
            continue
        ys = []
        for c in I:
            y = model.NewBoolVar("")
            model.AddBoolXOr([x[i1, c], x[i2, c], y.Not()])  # y = x1 xor x2
            ys.append(y)
        if p == q or b(p, q, K) == 0:
            model.Add(sum(ys) == len(I) // 2)
        else:
            z = model.NewBoolVar("")
            model.Add(sum(ys) == len(I) // 2 - 2 + 4 * z)
        npairs += 1
    log(f"=== sat_k2.py start: k'={K}, {len(lines)} non-frame lines in R^{T}, {len(x)} sign bits, "
        f"{npairs} pair constraints, {fixed} gauge-fixed; CP-SAT {workers} workers, limit {limit:.0f} s ===")

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = limit
    solver.parameters.num_search_workers = workers
    solver.parameters.log_search_progress = True
    cplog = open(os.path.join(HERE, f"sat_k2{suf}_cpsat.log"), "w", encoding="utf-8")
    solver.log_callback = lambda s: (cplog.write(s + "\n"), cplog.flush())

    t0 = time.time()
    done = threading.Event()

    def heartbeat():
        while not done.wait(60):
            log(f"   sat_k2 running, {time.time()-t0:.0f} s elapsed (limit {limit:.0f} s)")

    threading.Thread(target=heartbeat, daemon=True).start()
    status = solver.Solve(model)
    done.set()
    cplog.close()
    name = solver.StatusName(status)
    log(f"   CP-SAT status {name} after {time.time()-t0:.1f} s")

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # exact rebuild: 4*u as integer vectors in the frame basis
        vecs = []
        for c in range(T):
            e = [0] * T
            e[c] = 4
            vecs.append(("frame", c, e))
        for li, (p, j) in enumerate(lines):
            e = [0] * T
            for c in supp[p]:
                e[c] = -1 if solver.Value(x[li, c]) else 1
            vecs.append((p, j, e))
        lab = [L[v[1] // m] if v[0] == "frame" else v[0] for v in vecs]
        bad = 0
        for (a, va), (bb, vb) in itertools.combinations(list(zip(lab, [v[2] for v in vecs])), 2):
            dot = sum(s * t for s, t in zip(va, vb))
            want_orth = a == bb or b(a, bb, K) == 0
            if (want_orth and dot != 0) or (not want_orth and abs(dot) != 4):
                bad += 1
        norms_ok = all(sum(t * t for t in v[2]) == 16 for v in vecs)
        log(f"   exact check of {len(vecs)} lines: norms ok={norms_ok}, bad pairs={bad}")
        with open(os.path.join(HERE, f"sat_k2{suf}_solution.json"), "w", encoding="utf-8") as f:
            json.dump({"note": "4*u in the frame basis; label per line", "labels": lab,
                       "vectors": [v[2] for v in vecs]}, f)
        log("   RESULT: FEASIBLE" + (" (sub-test only: says nothing decisive)" if nclasses else ": 120-line descendant EXISTS (k'=2 does not kill the 510 object)"))
    elif status == cp_model.INFEASIBLE:
        log("   RESULT: INFEASIBLE -> no 120-line descendant -> the 510-line object in R^30 does not exist")
    else:
        log("   RESULT: UNKNOWN (time limit reached, no decision)")
    log("=== sat_k2.py done ===")


if __name__ == "__main__":
    main()
