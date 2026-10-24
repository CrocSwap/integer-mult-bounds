"""Idea 3: frame-reduced CP-SAT with symmetry breaking and Hadamard structure.

Same object as sat_k2.py (REPORT.md sections 2-3), with three additions:
 1. Symmetry breaking by lex-leader constraints x <=lex g(x) for a set of
    automorphisms g, all w.r.t. one row-major variable order (lines, then coords),
    which keeps them valid simultaneously:
      - negating a line      -> its first entry is +   (x = 0)
      - negating a coordinate-> its first entry is +
      - swapping two twin lines (same label)        -> rows in lex order
      - swapping two twin frame coordinates         -> columns in lex order
 2./3. Hadamard structure as redundant constraints: in every class the two
    collinearity groups are 16 x 16 Hadamard matrices, so their COLUMNS are also
    pairwise orthogonal (H^T H = 16 I). Classes interact only on their shared
    8 coordinates; that is left to the solver.
The spanning-forest gauge of sat_k2.py is NOT used (it is not compatible with 1).

Run:  py -3.12 sat_sb.py K [time_limit_s=1800] [workers=6] [nclasses, 0=all] [flags: nosb,nocol]
  K = 1: control, 48 lines in R^16 (3 unbiased bases; known to exist)
  K = 2: 120 lines in R^24 (decides the 510 object)
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


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def xor(model, a, c):
    y = model.NewBoolVar("")
    model.AddBoolXOr([a, c, y.Not()])  # y = a xor c
    return y


def lex_leq(model, A, B):
    """A <=lex B for equal-length lists of bool vars (0 < 1)."""
    e = None  # "prefix equal so far"; None means true
    for i, (a, c) in enumerate(zip(A, B)):
        if e is None:
            model.AddImplication(a, c)
        else:
            model.Add(a <= c).OnlyEnforceIf(e)
        if i == len(A) - 1:
            break
        d = xor(model, a, c)
        e2 = model.NewBoolVar("")
        if e is None:
            model.Add(e2 == 1 - d)
        else:
            model.Add(e2 <= e)
            model.Add(e2 <= 1 - d)
            model.Add(e2 >= e - d)
        e = e2


def main():
    K = int(sys.argv[1])
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 1800.0
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    nclasses = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != "0" else None
    flags = sys.argv[5].split(",") if len(sys.argv) > 5 else []
    use_sb, use_col = "nosb" not in flags, "nocol" not in flags
    m, pts, L, others, supp, T = build(K)
    key = {p: tuple(b(xx, p, K) for xx in L) for p in others}
    keys = sorted(set(key.values()))
    if nclasses is not None:
        keys = keys[:nclasses]
        others = [p for p in others if key[p] in keys]
    suf = f"_k{K}" + (f"_c{nclasses}" if nclasses else "") + "".join("_" + f for f in flags)
    lines = [(p, j) for p in others for j in range(m)]
    model = cp_model.CpModel()
    x = {}
    for li, (p, j) in enumerate(lines):
        for c in supp[p]:
            x[li, c] = model.NewBoolVar(f"x{li}_{c}")

    # pair constraints (rows of the Gram matrix)
    npairs = 0
    for (i1, (p, _)), (i2, (q, _)) in itertools.combinations(enumerate(lines), 2):
        I = sorted(set(supp[p]) & set(supp[q]))
        if not I:
            continue
        ys = [xor(model, x[i1, c], x[i2, c]) for c in I]
        if p == q or b(p, q, K) == 0:
            model.Add(sum(ys) == len(I) // 2)
        else:
            z = model.NewBoolVar("")
            model.Add(sum(ys) == len(I) // 2 - 2 + 4 * z)
        npairs += 1

    # 2./3. Hadamard column orthogonality inside every collinearity group
    ncol = 0
    for kk in (keys if use_col else []):
        members = [p for p in others if key[p] == kk]
        p0 = members[0]
        groups = [[q for q in members if q == p0 or b(p0, q, K) == 0]]
        groups.append([q for q in members if q not in groups[0]])
        for g in groups:
            rows = [li for li, (p, j) in enumerate(lines) if p in g]
            assert len(rows) == 16
            S = supp[g[0]]
            for c1, c2 in itertools.combinations(S, 2):
                model.Add(sum(xor(model, x[r, c1], x[r, c2]) for r in rows) == 8)
                ncol += 1

    # 1. symmetry breaking (lex-leader, row-major order)
    nsb = 0
    for li, (p, j) in (enumerate(lines) if use_sb else []):          # line negation
        model.Add(x[li, min(supp[p])] == 0)
        nsb += 1
    for c in (range(T) if use_sb else []):                            # coordinate negation
        first = next((li for li, (p, j) in enumerate(lines) if c in supp[p]), None)
        if first is not None:
            model.Add(x[first, c] == 0)
            nsb += 1
    for li, (p, j) in (enumerate(lines) if use_sb else []):          # twin lines: rows lex ordered
        if j + 1 < m:
            S = sorted(supp[p])
            lex_leq(model, [x[li, c] for c in S], [x[li + 1, c] for c in S])
            nsb += 1
    for c in (range(T) if use_sb else []):                            # twin frame coords: columns lex ordered
        if (c + 1) % m != 0:
            rows = [li for li, (p, j) in enumerate(lines) if c in supp[p]]
            if rows:
                lex_leq(model, [x[r, c] for r in rows], [x[r, c + 1] for r in rows])
                nsb += 1

    log(f"=== sat_sb.py start: k'={K}{' sub-test '+str(nclasses)+' classes' if nclasses else ''}, "
        f"{len(lines)} non-frame lines in R^{T}, {len(x)} sign bits, {npairs} pair + {ncol} column constraints, "
        f"{nsb} symmetry-breaking constraints, flags {flags}; CP-SAT {workers} workers, limit {limit:.0f} s ===")

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = limit
    solver.parameters.num_search_workers = workers
    solver.parameters.log_search_progress = True
    cplog = open(os.path.join(HERE, f"sat_sb{suf}_cpsat.log"), "w", encoding="utf-8")
    solver.log_callback = lambda s: (cplog.write(s + "\n"), cplog.flush())
    t0 = time.time()
    done = threading.Event()

    def heartbeat():
        while not done.wait(60):
            log(f"   sat_sb{suf} running, {time.time()-t0:.0f} s elapsed (limit {limit:.0f} s)")

    threading.Thread(target=heartbeat, daemon=True).start()
    status = solver.Solve(model)
    done.set()
    cplog.close()
    log(f"   CP-SAT status {solver.StatusName(status)} after {time.time()-t0:.1f} s")

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        vecs, lab = [], []
        for c in range(T):
            e = [0] * T
            e[c] = 4
            vecs.append(e)
            lab.append(L[c // m])
        for li, (p, j) in enumerate(lines):
            e = [0] * T
            for c in supp[p]:
                e[c] = -1 if solver.Value(x[li, c]) else 1
            vecs.append(e)
            lab.append(p)
        bad = 0
        for (a, va), (bb, vb) in itertools.combinations(list(zip(lab, vecs)), 2):
            dot = sum(s * t for s, t in zip(va, vb))
            want_orth = a == bb or b(a, bb, K) == 0
            if (want_orth and dot != 0) or (not want_orth and abs(dot) != 4):
                bad += 1
        norms_ok = all(sum(t * t for t in v) == 16 for v in vecs)
        log(f"   exact check of {len(vecs)} lines (4u, integer): norms ok={norms_ok}, bad pairs={bad}")
        with open(os.path.join(HERE, f"sat_sb{suf}_solution.json"), "w", encoding="utf-8") as f:
            json.dump({"note": "4*u in the frame basis; label per line", "labels": lab, "vectors": vecs}, f)
        log(f"   RESULT: FEASIBLE ({'sub-test only' if nclasses else 'full object exists'})")
    elif status == cp_model.INFEASIBLE:
        log("   RESULT: INFEASIBLE" + (" -> 510-line object does not exist" if K >= 2 else " (control FAILED: bug)"))
    else:
        log("   RESULT: UNKNOWN (time limit reached, no decision)")
    log("=== sat_sb.py done ===")


if __name__ == "__main__":
    main()
