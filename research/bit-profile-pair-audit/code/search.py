"""Searches on the exact paid-profile objective.

Move class (the one the merged tuner uses, PR #589 / research/e8-bit-p111-tuned/tune/tune.py):
single-operation transport with reframing.  Each open operation may be lifted out of the flat
elementary-op list and re-inserted at any slot it commutes to, at any catalogue frame that contains
the pre-frames and is contained in the post-frames of its two registers, subject to the retained-total
copy-rank rule.  Frame closure frames are created on demand by the frame catalogue.

Three searches are exposed:
  scan_singles   - every nominated single move, priced exactly (the complete one-move neighbourhood)
  exact_greedy   - steepest descent with a full re-nomination at every step
  pair_search    - complete two-move neighbourhood: by the register decomposition of the objective,
                   only pairs sharing a register can improve, so for every nominated move M1 every
                   nominated move on an operation touching a register of M1 is evaluated exactly.
"""
import bisect


def nominated(view, best_move, thr=1e9):
    """all (delta, q, frame) the tuner nominates for every operation of `view`"""
    out = []
    for i in range(len(view.ops)):
        c = best_move(view, i, thr=thr, all_=True)
        if c:
            out.append((i, c))
    return out


def scan_singles(T, S, best_move):
    """complete nominated one-move neighbourhood, exactly priced.  returns (base, [(d, sec, i, q, F)])"""
    base = S.objective()
    rows = []
    for sec in 'AB':
        V = T.view(sec)
        for i, cands in nominated(V, best_move):
            for (dproxy, q, F) in cands:
                from stateprof import apply_move, undo_move
                om = apply_move(V, i, q, F)
                S.rebuild_z()
                d = S.objective() - base
                undo_move(V, q, om)
                rows.append((d, dproxy, sec, i, q, F))
    return base, rows


def all_legal_moves(V, i, commute, best_move):
    """every legal (slot, frame) for operation i, not only the proxy's best frame per slot"""
    cat = V.cat
    ops = V.ops
    n = len(ops)
    op = ops[i]
    f0, t, s = op
    lo = i
    while lo > 0 and commute(op, ops[lo - 1]):
        lo -= 1
    hi = i
    while hi < n - 1 and commute(op, ops[hi + 1]):
        hi += 1

    def tl(r):
        return [j if j < i else j - 1 for j in V.touch[r] if j != i]

    tt, ts = tl(t), tl(s)

    def frame_of(e):
        return ops[e if e < i else e + 1][0]

    starts = sorted({lo} | {e + 1 for e in tt + ts if lo <= e + 1 <= hi} | ({i} if lo <= i <= hi else set()))
    out = []
    for k, st in enumerate(starts):
        en = (starts[k + 1] - 1) if k + 1 < len(starts) else hi
        q = min(max(i, st), en)

        def ctx(lst, r):
            kk = bisect.bisect_left(lst, q)
            p = frame_of(lst[kk - 1]) if kk > 0 else V.pre[r]
            nx = frame_of(lst[kk]) if kk < len(lst) else V.post[r]
            return p, nx, kk

        pt, nt, kt = ctx(tt, t)
        ps, ns, ks = ctx(ts, s)
        low = cat.masks[pt] | cat.masks[ps]
        high = cat.masks[nt] & cat.masks[ns]
        if low & ~high:
            continue
        Fs = [int(x) for x in cat.feasible(low, high)]
        F0 = cat.closure(low)
        if cat.masks[F0] & ~high == 0 and F0 not in Fs:
            Fs.append(F0)
        for F in Fs:
            ok = True
            for r, lst, kk in ((t, tt, kt), (s, ts, ks)):
                if r in T_ret(V) and kk == len(lst) and F != V.T.cp[r]:
                    ok = False
            if ok:
                out.append((q, F))
    return out


def T_ret(V):
    return V.T.ret


def exact_greedy(T, S, best_move, max_steps=200, tol=1e-9):
    """steepest descent on the exact objective with a full re-nomination at every step"""
    base = S.objective()
    applied = []
    for _ in range(max_steps):
        _, rows = scan_singles(T, S, best_move)
        rows.sort(key=lambda x: x[0])
        if not rows or rows[0][0] >= -tol:
            break
        d, _, sec, i, q, F = rows[0]
        V = T.view(sec)
        from stateprof import apply_move
        apply_move(V, i, q, F)
        S.rebuild_z()
        base = S.objective()
        applied.append(dict(section=sec, op=i, slot=q, frame=F, delta=d, objective=base))
    return base, applied


def pair_search(T, S, best_move, singles, verbose=False):
    """complete register-connected two-move neighbourhood, exactly priced"""
    from stateprof import apply_move, undo_move
    base = S.objective()
    best = None
    bestinfo = None
    npairs = 0
    singles = sorted(singles, key=lambda x: x[0])
    for (d1, dproxy, sec, i, q, F) in singles:
        V = T.view(sec)
        t, s = V.ops[i][1], V.ops[i][2]
        om = apply_move(V, i, q, F)
        S.rebuild_z()
        V.refresh()
        nbr = set()
        for r in (t, s):
            nbr.update(V.touch[r])
        for j in sorted(nbr):
            c2 = best_move(V, j, thr=1e9, all_=True)
            if not c2:
                continue
            for (dproxy2, q2, F2) in c2:
                om2 = apply_move(V, j, q2, F2)
                S.rebuild_z()
                tot = S.objective() - base
                undo_move(V, q2, om2)
                npairs += 1
                if best is None or tot < best:
                    best = tot
                    bestinfo = dict(delta1=d1, section1=sec, op1=i, slot1=q, frame1=F,
                                    op2=j, slot2=q2, frame2=F2, objective1=0.0)
        undo_move(V, q, om)
    return base, best, bestinfo, npairs
