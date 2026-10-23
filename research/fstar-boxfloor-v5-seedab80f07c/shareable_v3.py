#!/usr/bin/env python3
"""KB5L job 3 (shareable class): PR 2978's 21 not-found-in-cap v = 3
combinatorial gap patterns, pushed with an exact kernel solver.

Recomputed from scratch (the vendored box-search-kj-receipt.json ships empty):
vendored box_search_kj.job_b gives the 27 gap candidates; vendored
realize_kj.try_candidate classifies them (3 realized, 3 unrealizable-column,
21 not-found-in-cap in its alphabets).  This script pushes the realization
cap with an EXACT q-solver: for fixed P (anchor recipe: p_j(t) odd iff
j in a0(t)), the constraints on q(s) are

    p(t).q(s) = 0   for (t, s) in Z,      p(t).q(s) != 0   otherwise,
    q_j(s) odd iff j in b0(s), even nonzero otherwise.

The equations are solved exactly over the integer kernel of the zero-arc
predecessor rows; a solution exists iff p(t) is outside span{p(u) : (u,s) in
Z} for every t with (t,s) not in Z (finite union of hyperplanes over Q does
not cover W^perp unless one equals it).  Parity box + inequalities are
filtered over small integer kernel combinations.  Acceptance is engine-exact:
anchor data equals the pattern, zero set equals Z, identities replayed,
exact cert and box recomputed by the vendored PR 2914 engine.

Prints PASS_KL_* markers; writes data/shareable-v3-receipt.json.
Run: python3 -B shareable_v3.py
"""
import importlib.util
import itertools
import json
import os
import random
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
VEND = os.path.join(HERE, "predecessor", "pr3012", "predecessor", "pr2978")
sys.path.insert(0, os.path.join(VEND, "predecessor", "pr2963"))
import named_exact as ne  # noqa: E402

fg = ne.fg
spec = importlib.util.spec_from_file_location(
    "box_attack",
    os.path.join(VEND, "predecessor", "pr2963", "predecessor", "pr2936",
                 "box_attack.py"))
ba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ba)
spec2 = importlib.util.spec_from_file_location("box_search_kj",
                                              os.path.join(VEND, "box_search_kj.py"))
bsk = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(bsk)
spec3 = importlib.util.spec_from_file_location("realize_kj",
                                              os.path.join(VEND, "realize_kj.py"))
rk = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(rk)

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "predecessor", "pr3012"))
import box_floor_min as bm  # noqa: E402
from family_v5 import int_kernel3  # noqa: E402


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def dot3(u, w):
    return u[0] * w[0] + u[1] * w[1] + u[2] * w[2]


def rank3(rows):
    return bm.gf2_rank_int([list(r) for r in rows]) if rows else 0


def solve_q(P, Zcol, n_col, b0_line):
    """Exact q-row: kernel of {P[t] : t in Zcol}, inequalities against
    {P[t] : t in n_col}, parity box odd iff b0 bit (even nonzero otherwise).
    Returns a q tuple or None.  Zcol/n_col are PREDECESSOR index sets."""
    rows = [P[t] for t in Zcol]
    for t in n_col:
        W = rows
        if rank3(W + [P[t]]) == rank3(W) and P[t] != (0, 0, 0):
            # p(t) in span(W): every q orthogonal to W kills p(t) too
            return None
    ker = int_kernel3(rows)
    if not ker:
        return None
    want_parity = [(b0_line >> j) & 1 for j in range(3)]
    cands = []
    if len(ker) == 1:
        combos = [(c,) for c in range(-6, 7) if c]
    elif len(ker) == 2:
        combos = [(c1, c2) for c1 in range(-4, 5) for c2 in range(-4, 5)
                  if (c1, c2) != (0, 0)]
    else:
        combos = [(c1, c2, c3) for c1 in range(-3, 4) for c2 in range(-3, 4)
                  for c3 in range(-3, 4) if (c1, c2, c3) != (0, 0, 0)]
    for combo in combos:
        q = [0, 0, 0]
        for i, k in enumerate(ker):
            for j in range(3):
                q[j] += combo[i] * k[j]
        if any(x == 0 for x in q):
            continue
        if [abs(x) % 2 for x in q] != want_parity:
            continue
        if any(dot3(P[t], tuple(q)) == 0 for t in n_col):
            continue
        cands.append(tuple(q))
        if len(cands) >= 1:
            return cands[0]
    return None


def try_kernel(cand, rng, p_tries):
    a0, b0 = cand["a0"], cand["b0"]
    Z = frozenset(tuple(z) for z in cand["Z"])
    col_active = [any((a0[t] >> j) & 1 for t in range(3)) for j in range(3)]
    col_b = [any((b0[t] >> j) & 1 for t in range(3)) for j in range(3)]
    for j in range(3):
        if col_b[j] and not col_active[j]:
            return dict(status="unrealizable-column",
                        reason="bit %d enters b0 but no a0 line attains m_j" % j)
    popts = [rk.p_options(a0[t], col_active, False) for t in range(3)]
    for attempt in range(p_tries):
        P = [tuple(opts[rng.randrange(len(opts))] for opts in popts[t])
             for t in range(3)]
        if rank3([list(p) for p in P]) != 3:
            continue
        rows = []
        ok = True
        for s in range(3):
            Zcol = [t for t in range(3) if t != s and (t, s) in Z]
            n_col = [t for t in range(3) if t == s or (t, s) not in Z]
            q = solve_q(P, Zcol, n_col, b0[s])
            if q is None:
                ok = False
                break
            rows.append(q)
        if not ok:
            continue
        Q = rows
        try:
            mod = fg.model(P, Q)
        except (AssertionError, ValueError):
            continue
        ad = fg.anchor_data(mod)
        if list(ad["a0"]) != list(a0) or list(ad["b0"]) != list(b0):
            continue
        if not (fg.tie_parity(mod, ad) and fg.scope_identity(mod, ad)):
            continue
        gotZ = frozenset((t, s) for (t, s) in mod["arcs"])
        if gotZ != Z:
            continue
        ce, cew = fg.cert_exact(mod, max_v=3)
        bx, bxw = ba.box_exact_tolerant(mod, ad)
        assert fg.replay_witness(mod, cew)
        assert bxw is None or fg.replay_witness(mod, bxw)
        return dict(status="realized", P=[list(p) for p in P],
                    Q=[list(q) for q in Q], cert=ce, box=bx,
                    cert_witness=cew, attempts=attempt + 1,
                    alphabet="kernel")
    return dict(status="not-found-in-cap", p_tries=p_tries,
                alphabet="kernel")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    nconf, cands = bsk.job_b()
    assert nconf == 3023 and len(cands) == 27, (nconf, len(cands))
    log("candidates recomputed: %d" % len(cands))
    rng = random.Random(20261017)
    out = []
    counterexamples = []
    for i, cand in enumerate(cands):
        # pass 1: PR 2978's EXACT pipeline (seed 20261017, original order and
        # caps) - reproduces its recorded 3/3/21 classification as an anchor
        res = rk.try_candidate(cand, rng, allow_zero=False)
        if res["status"] == "not-found-in-cap":
            res = rk.try_candidate(cand, rng, p_tries=4000, allow_zero=True)
        if res["status"] == "not-found-in-cap":
            res = rk.try_candidate(cand, rng, p_tries=6000, allow_zero=True,
                                   big=True)
        res.update(candidate=cand, stage="pr2978-replay")
        out.append(res)
        log("[%d/%d] %s a0=%s b0=%s Z=%s %s"
            % (i + 1, len(cands), res["status"], cand["a0"], cand["b0"],
               cand["Z"],
               ("cert=%s box=%s" % (res.get("cert"), res.get("box")))
               if res["status"] == "realized" else res.get("reason", "")))
        if res["status"] == "realized" and res.get("cert", 0) > res.get("box", 0):
            counterexamples.append(res)
            log("SHAREABLE-CLASS COUNTEREXAMPLE: cert=%d box=%d"
                % (res["cert"], res["box"]))
    counts = {}
    for r in out:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    log("pass 1 (PR 2978 replay) counts: %s" % json.dumps(counts, sort_keys=True))
    # pass 2: cap push on the not-found patterns (kernel solver + big alphabet)
    push_rng = random.Random(20261018)
    pushed = []
    for r in out:
        if r["status"] != "not-found-in-cap":
            continue
        cand = r["candidate"]
        res = try_kernel(cand, push_rng, p_tries=10000)
        if res["status"] == "not-found-in-cap":
            res2 = rk.try_candidate(cand, push_rng, p_tries=2000,
                                    allow_zero=True, big=True)
            if res2["status"] == "realized":
                res = res2
            else:
                res["vendored_big"] = res2["status"]
        res.update(candidate=cand, stage="cap-push")
        pushed.append(res)
        log("[push %d/%d] %s a0=%s b0=%s Z=%s %s"
            % (len(pushed), 21, res["status"], cand["a0"], cand["b0"],
               cand["Z"],
               ("cert=%s box=%s" % (res.get("cert"), res.get("box")))
               if res["status"] == "realized" else res.get("reason", "")))
        if res["status"] == "realized" and res.get("cert", 0) > res.get("box", 0):
            counterexamples.append(res)
            log("SHAREABLE-CLASS COUNTEREXAMPLE (push): cert=%d box=%d"
                % (res["cert"], res["box"]))
    counts2 = {}
    final_by_key = {}
    for r in out:
        key = (tuple(r["candidate"]["a0"]), tuple(r["candidate"]["b0"]),
               tuple(tuple(z) for z in r["candidate"]["Z"]))
        final_by_key[key] = r["status"]
    for r in pushed:
        key = (tuple(r["candidate"]["a0"]), tuple(r["candidate"]["b0"]),
               tuple(tuple(z) for z in r["candidate"]["Z"]))
        final_by_key[key] = r["status"]
    for st in final_by_key.values():
        counts2[st] = counts2.get(st, 0) + 1
    with open(os.path.join(HERE, "data", "shareable-v3-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(dict(generator="shareable_v3.py seeds 20261017/20261018",
                       replay_counts=counts, push_counts=counts2,
                       records=out, pushed=pushed,
                       counterexamples=counterexamples),
                  fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("PASS_KL_SHAREABLE candidates=%d replay=%s push-final=%s "
          "counterexamples=%d"
          % (len(cands), json.dumps(counts, sort_keys=True),
             json.dumps(counts2, sort_keys=True), len(counterexamples)))


if __name__ == "__main__":
    main()
