#!/usr/bin/env python3
"""KB5j job 2: realize (or refute by search) the v = 3 combinatorial
candidates of box_search_kj.py job B.

A combinatorial candidate is (a0, b0, Z): sub-anchor masks per line with
tau(t) = |a0(t) intersect b0(t)| >= 1, a zero-arc set Z with |a0(t) intersect
b0(s)| even on every arc (Lemma SG), and full-label cert_max(Z) = 3 > 2 =
box(a0, b0, Z). Realization asks for an EXACT 3-total integer decoder
M = P Q^T whose anchor data IS (a0, b0) and whose zero pattern IS Z.

Realization recipe (canonical reduced normalization, m_j = 0 per used total):
  - p_j(t) odd  iff j in a0(t);  even nonzero otherwise (or the whole
    p-column zero when j is in no a0(t) - then m_j = SENTINEL and no b0 can
    contain j, a hard unrealizability witness if violated);
  - q_j(t) odd  iff j in b0(t);  even nonzero otherwise;
  then v2(p_j(t)) + v2(q_j(t)) = 0 on a0(t) intersect b0(t) = tied bits,
  Lemma SG's scope identity is automatic (parity of odd terms of M_ts), and
  the candidate's tau and masks reproduce exactly. All entries nonzero where
  allowed keeps pi = sg = full so cert is the full-label value.

For fixed P the constraints on each row q(s) are independent (M_ts = p(t).q(s)
is linear in q(s)): every q(s) is enumerated exhaustively over its alphabet
(odd {+1,-1,+3,-3}, even {+2,-2}); P is sampled with deterministic restarts.

Writes data/realize-kj-receipt.json. Stdlib, deterministic.
Run: python3 -B realize_kj.py
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
sys.path.insert(0, os.path.join(HERE, "predecessor", "pr2963"))
import named_exact as ne  # noqa: E402

fg = ne.fg
spec = importlib.util.spec_from_file_location(
    "box_attack",
    os.path.join(HERE, "predecessor", "pr2963", "predecessor", "pr2936",
                 "box_attack.py"))
ba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ba)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


ODD = (1, -1, 3, -3)
EVEN = (2, -2)
EVEN0 = (2, -2, 0)
ODD_BIG = (1, -1, 3, -3, 5, -5, 7, -7)
EVEN0_BIG = (2, -2, 4, -4, 6, -6, 0)


def row_options(b0_line, col_active, allow_zero):
    """Alphabet per position for one q-row."""
    even = EVEN0 if allow_zero else EVEN
    opts = []
    for j in range(3):
        if not col_active[j]:
            opts.append(even)  # p-column zero: parity free
        elif (b0_line >> j) & 1:
            opts.append(ODD)
        else:
            opts.append(even)
    return opts


def p_options(a0_line, col_active, allow_zero):
    even = EVEN0 if allow_zero else EVEN
    opts = []
    for j in range(3):
        if not col_active[j]:
            opts.append((0,))
        elif (a0_line >> j) & 1:
            opts.append(ODD)
        else:
            opts.append(even)
    return opts


def dot3(u, w):
    return u[0] * w[0] + u[1] * w[1] + u[2] * w[2]


def try_candidate(cand, rng, p_tries=4000, allow_zero=False, big=False):
    a0, b0, Z = cand["a0"], cand["b0"], frozenset(tuple(z) for z in cand["Z"])
    col_active = [any((a0[t] >> j) & 1 for t in range(3)) for j in range(3)]
    col_b = [any((b0[t] >> j) & 1 for t in range(3)) for j in range(3)]
    for j in range(3):
        if col_b[j] and not col_active[j]:
            return dict(status="unrealizable-column",
                        reason="bit %d enters b0 but no a0 line attains m_j"
                               % j)
    if big:
        global ODD, EVEN0
        odd_save, even_save = ODD, EVEN0
        ODD, EVEN0 = ODD_BIG, EVEN0_BIG
    popts = [p_options(a0[t], col_active, allow_zero) for t in range(3)]
    qopts = [row_options(b0[s], col_active, allow_zero) for s in range(3)]
    for attempt in range(p_tries):
        P = [tuple(opts[rng.randrange(len(opts))] for opts in popts[t])
             for t in range(3)]
        rows = []
        ok = True
        for s in range(3):
            found = None
            for q in itertools.product(*qopts[s]):
                good = True
                for t in range(3):
                    v = dot3(P[t], q)
                    if t == s:
                        if v == 0:
                            good = False
                            break
                    elif ((t, s) in Z) != (v == 0):
                        good = False
                        break
                if good:
                    found = q
                    break
            if found is None:
                ok = False
                break
            rows.append(found)
        if not ok:
            continue
        Q = rows
        mod = fg.model(P, Q)
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
        if big:
            ODD, EVEN0 = odd_save, even_save
        return dict(status="realized", P=[list(p) for p in P],
                    Q=[list(q) for q in Q], cert=ce, box=bx,
                    cert_witness=cew, attempts=attempt + 1,
                    alphabet=("big" if big else
                              "nonzero" if not allow_zero else "with-zeros"))
    if big:
        ODD, EVEN0 = odd_save, even_save
    return dict(status="not-found-in-cap", p_tries=p_tries,
                alphabet=("big" if big else
                          "nonzero" if not allow_zero else "with-zeros"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    with open(os.path.join(HERE, "data", "box-search-kj-receipt.json"),
              encoding="utf-8") as fh:
        kj = json.load(fh)
    cands = kj["job_b"]["candidates"]
    log("candidates: %d" % len(cands))
    rng = random.Random(20261017)
    out = []
    counterexamples = []
    for i, cand in enumerate(cands):
        res = try_candidate(cand, rng, allow_zero=False)
        if res["status"] == "not-found-in-cap":
            res = try_candidate(cand, rng, p_tries=4000, allow_zero=True)
        if res["status"] == "not-found-in-cap":
            res = try_candidate(cand, rng, p_tries=6000, allow_zero=True,
                                big=True)
        res.update(candidate=cand)
        out.append(res)
        log("[%d/%d] %s a0=%s b0=%s Z=%s -> %s"
            % (i + 1, len(cands), res["status"], cand["a0"], cand["b0"],
               cand["Z"],
               ("cert=%s box=%s" % (res.get("cert"), res.get("box")))
               if res["status"] == "realized" else res.get("reason", "")))
        if res["status"] == "realized" and res["cert"] > res["box"]:
            counterexamples.append(res)
            log("BOX-COMPLETENESS COUNTEREXAMPLE: cert=%d box=%d P=%s Q=%s"
                % (res["cert"], res["box"], res["P"], res["Q"]))
    counts = {}
    for r in out:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    with open(os.path.join(HERE, "data", "realize-kj-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(dict(generator="realize_kj.py seed 20261017",
                       status_counts=counts, records=out,
                       counterexamples=counterexamples),
                  fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("PASS_KJ_REALIZE candidates=%d status=%s counterexamples=%d"
          % (len(cands), counts, len(counterexamples)))


if __name__ == "__main__":
    main()
