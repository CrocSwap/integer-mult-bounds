# SPDX-License-Identifier: Apache-2.0
"""Lower bound on the certified local cost of EVERY exact restore-only rewrite of a BORROW-WORD (stdlib only).

A restore-only rewrite keeps the precondition, compensation, initial corrections, A (with its prelude), cut, warps, B,
start frames, helper end frames, removed helpers and buffers, and replaces the restore by an arbitrary scalar gate
sequence; all frames (A, B and restore) are re-solved. It is exact when PR2833's auditor (BORROW-WORD branch, vendored
unchanged) passes. The bound is

    bound(w) = LB_forced(w) + sum of forced restore-phase extras,

where LB_forced is the exact frame optimum of w with an EMPTY restore and the forced entry caps, and the extras are
charged by the lemmas below (README.md, section "Proof"):
  Lemma 1  auditor semantics: exact => every restored helper c ends with its own input row x_c and no live register keeps
           a restored input c outside c (the auditor's forward `require`s at the end of restore);
  Lemma 2  forced coordinates: restore-entry rows are linearly independent, so x_c = sum_q M[c][q] e_q is unique and every
           exact restore realizes row c of its linear map equal to M[c];
  Lemma 3  forced caps: M[c][r] != 0 (r != c) => r is read on a path to c whose gate frames are nested inside E_c, hence
           r's restore-entry frame F_r <= E_c;
  Lemma 4  merge: replacing every register's restore-phase climbs by one end climb gives a feasible assignment of the
           capped empty-restore problem and costs sum_r ov_r less (subadditive weights);
  Lemma 5  delivery/cleaning: a receiver's content leaves r through a gate reading r at a frame inside E_c; a non-restored
           register holding a restored input must be cleaned (written) below FULL (span of restored-input parts of FULL
           registers never shrinks and ends at 0);
  Lemma 6  departure (dual vectors): if r stays inside frame G until it jumps to a frame outside E_c for every c in O,
           the nonzero dual vector d_r is supported on Z = {r} u {y : L_y <= G} and M[O][Z] d_r = 0; full column rank
           of M[O][Z] therefore excludes that departure;
  Lemma 7  lifts: content that sits at frame F (or inside a restored source's end V) and must reach a receiver that
           cannot sit there is carried upward by a register that sits there; a non-restored carrier makes a visit
           (>= 2c1 - c2), a blocked one needs >= 3 restore-phase jumps.
Marius-Paul Dumitrean, with substantial AI assistance (Claude Code).
"""
import collections
import copy
from fractions import Fraction as Q

import frames_exact as FX

AL = FX._load('rank7sro_audit_local', FX.HERE / 'vendor' / 'audit_local.py')   # PR2833 auditor (walg_apply, run)
V = FX.V
basis, span, leq, join, meet, FULL9 = FX.basis, FX.span, FX.leq, FX.join, FX.meet, FX.FULL9


# ------------------------------------------------------------------------------------------------ exact algebra
def live_registers(w):
    n = 2 * V + w['report']['R']
    removed = set(w['removed'])
    return [q for q in range(n) if q not in removed]


def restored(w):
    return set(map(int, w['helper_final']))


def is_target(q):
    return V <= q < 2 * V


def program_pre_restore(w):
    """the auditor's forward program up to the end of B (corrections, precondition, compensation, A, cut, B with warps)"""
    corr = [['corr', t['target'], t['source'], tuple(t['operator_word']), Q(t['coefficient'])] for t in w['initial_corrections']]
    prog = corr + w['precondition'] + w['compensation'] + w['A'] + w['cut']
    byp = {}
    for op, rec in enumerate(w['warps'], 1):
        byp.setdefault(rec[0], []).append(op)
    for p in range(len(w['B']) + 1):
        for op in byp.get(p, []):
            prog.append(['warp', w['warps'][op - 1][1], op])
        if p < len(w['B']):
            prog.append(w['B'][p])
    return prog


def entry_rows(w):
    rows = {r: {(r, ()): Q(1)} for r in live_registers(w)}
    for e in program_pre_restore(w):
        AL.walg_apply(e, rows, False, 10 ** 6)
    return rows


def run_restore(restore, rows):
    rows = {r: dict(x) for r, x in rows.items()}
    for e in restore:
        AL.walg_apply(e, rows, False, 10 ** 6)
    return rows


def end_conditions(w, rows_final, rows_entry=None):
    """Lemma 1 end-of-restore conditions: (dirty restored helpers, leaks, changed targets)"""
    R = restored(w)
    dirty = sorted(c for c in R if rows_final[c] != {(c, ()): Q(1)})
    leaks = {}
    for r, row in rows_final.items():
        ks = sorted({var for var, word in row if var in R and var != r})
        if ks:
            leaks[r] = ks
    targets = sorted(t for t in rows_final if is_target(t) and rows_entry is not None and rows_final[t] != rows_entry[t])
    return dirty, leaks, targets


def _axpy(dst, src, f):
    for k, x in src.items():
        y = dst.get(k, Q(0)) + f * x
        if y:
            dst[k] = y
        else:
            dst.pop(k, None)


def coordinates(rows, targets):
    """coordinates of target rows in the basis of `rows` (Gaussian elimination with combination tracking, Fractions);
    raises if the rows are dependent or a target is outside their span"""
    order = lambda k: (k[0], len(k[1]), k[1])
    piv = {}
    for q in sorted(rows):
        v = dict(rows[q])
        comb = {q: Q(1)}
        while v:
            k = min(v, key=order)
            if k in piv:
                pr, pc = piv[k]
                f = -v[k] / pr[k]
                _axpy(v, pr, f)
                _axpy(comb, pc, f)
            else:
                piv[k] = (v, comb)
                break
        else:
            raise ValueError(('restore-entry rows are dependent', q))
    out = {}
    for name, t in targets.items():
        v = dict(t)
        comb = {}
        while v:
            k = min(v, key=order)
            if k not in piv:
                raise ValueError(('target outside the span of the entry rows', name, k))
            pr, pc = piv[k]
            f = v[k] / pr[k]
            _axpy(v, pr, -f)
            _axpy(comb, pc, f)
        out[name] = comb
    return out, len(piv)


def restore_map(w, restore=None):
    """register-level linear map of a restore program (final_r = sum_q map[r][q] entry_q)"""
    restore = w['restore'] if restore is None else restore
    M = {q: {q: Q(1)} for q in live_registers(w)}
    for g in restore:
        if g[0] == 'add':
            t, s, c = g[1], g[2], Q(g[3], g[4])
            row = dict(M[t])
            for k, x in M[s].items():
                y = row.get(k, Q(0)) + c * x
                if y:
                    row[k] = y
                else:
                    row.pop(k, None)
            M[t] = row
        else:
            q = Q(g[2], g[3])
            M[g[1]] = {k: q * x for k, x in M[g[1]].items()}
    return M


def end_frames(w):
    n = 2 * V + w['report']['R']
    E = {}
    for q in range(n):
        if q < V:
            E[q] = FULL9
        elif q < 2 * V:
            E[q] = FX.perp_port(w['ports'][q - V])
        else:
            E[q] = FULL9
    for q, U in w['helper_final'].items():
        E[int(q)] = basis(tuple(U))
    return E


def rank(rows):
    m = [list(r) for r in rows if any(r)]
    if not m:
        return 0
    rk = 0
    ncol = len(m[0])
    for c in range(ncol):
        piv = next((i for i in range(rk, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[rk], m[piv] = m[piv], m[rk]
        for i in range(len(m)):
            if i != rk and m[i][c] != 0:
                f = m[i][c] / m[rk][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[rk])]
        rk += 1
    return rk


# ------------------------------------------------------------------------------------------------ frames
def forced_caps(M, E, R):
    """Lemma 3: cap[r] = intersection of E_c over restored c != r with M[c][r] != 0; receivers per register"""
    capf = {}
    recv = collections.defaultdict(list)
    for c in sorted(R):
        for r, x in M[c].items():
            if r == c or not x:
                continue
            recv[r].append(c)
            capf.setdefault(r, set(span(FULL9)))
            capf[r] &= set(span(tuple(E[c])))
    return {r: basis(tuple(U)) for r, U in capf.items()}, {r: sorted(v) for r, v in recv.items()}


def empty_restore(w):
    w0 = dict(w)
    w0['restore'] = []
    return w0


def lb_forced(w, caps):
    return FX.frame_optimum(empty_restore(w), caps=caps)


def entry_bounds(w, lb):
    """per live register: L (forward lower bound) and U (cap from its other registers) at its last pre-restore vertex,
    in the capped empty-restore graph (valid for every exact restore-only rewrite)"""
    g = lb['graph']
    al = FX.aliases(w, lb['meta'])
    removed = set(w['removed'])
    out = {}
    mutable = set(g.mutable)
    for q, segs in al.items():
        if q in removed:
            continue
        v = segs[-1]
        last = None
        for k in g.chains[v]:
            if g.nodes[k][2] in ('tail', 'end'):
                break
            last = k
        L = tuple(g.lower[last])
        if last in mutable:
            U = set(span(FULL9))
            for t in g.nodes[last][0]:
                if t == v:
                    continue
                j = g.nxt.get((last, t))
                if j is not None:
                    U &= set(span(tuple(g.upper[j])))
            U = basis(tuple(U))
        else:
            U = tuple(lb['assign'].get(last, g.nodes[last][1]))
        out[q] = (L, U)
    return out


def subspaces_between(A, B):
    """all subspaces S with A <= S <= B, sorted by (dim, basis)"""
    extras = []
    cur = basis(tuple(A))
    for v in basis(tuple(B)):
        if v not in span(cur):
            extras.append(v)
            cur = basis(cur + (v,))
    d = len(extras)
    spaces = {()}
    frontier = [()]
    while frontier:
        nxt = []
        for Sb in frontier:
            sp = set(span(Sb))
            for v in range(1, 1 << d):
                if v not in sp:
                    T = basis(Sb + (v,))
                    if T not in spaces:
                        spaces.add(T)
                        nxt.append(T)
        frontier = nxt

    def lift(v):
        z = 0
        for i, x in enumerate(extras):
            if v >> i & 1:
                z ^= x
        return z
    return sorted({basis(tuple(A) + tuple(lift(v) for v in Sb)) for Sb in spaces}, key=lambda s: (len(s), s))


def compositions(D, kmin):
    out = []

    def rec(rem, pre):
        if rem == 0:
            if len(pre) >= kmin:
                out.append(tuple(pre))
            return
        for a in range(1, rem + 1):
            rec(rem - a, pre + [a])
    rec(D, [])
    return out


# ------------------------------------------------------------------------------------------------ the bound
def bound(w, rows=None, M=None, need_lb=None):
    """the restore lower bound with its complete certificate (JSON-serializable)"""
    c = FX.weights()
    visit_unit = 2 * c[1] - c[2]
    R = restored(w)
    E = end_frames(w)
    if rows is None:
        rows = entry_rows(w)
    if M is None:
        Mc, rk = coordinates(rows, {x: {(x, ()): Q(1)} for x in R})
        M = {q: dict(v) for q, v in Mc.items()}
    caps, recv = forced_caps(M, E, R)
    lb = need_lb if need_lb is not None else lb_forced(w, caps)
    LU = entry_bounds(w, lb)
    live = [q for q in LU if not is_target(q)]
    L = {q: LU[q][0] for q in LU}
    U = {q: LU[q][1] for q in LU}
    SL = {q: set(span(L[q])) for q in live}
    SE = {q: set(span(E[q])) for q in live}
    if not all(len(E[x]) < 9 for x in R):
        raise ValueError('a restored helper ends at FULL')
    if any(M[x].get(t) for x in R for t in range(V, 2 * V)):
        raise ValueError('a restored helper needs a target row')
    leak = {x: (sorted({var for var, word in rows[x] if var in R and var != x}) if x not in R else []) for x in live}
    cap = {x: caps.get(x, FULL9) for x in live}

    def P_at(G, x):
        SG = set(span(G))
        return [y for y in live if y != x and SL[y] <= SG and SG <= SE[y]]
    dep_cache = {}

    def departure_impossible(x, G):
        key = (x, G)
        if key not in dep_cache:
            SG = set(span(G))
            Z = [x] + [y for y in live if y != x and SL[y] <= SG]
            O = [cc for cc in sorted(R) if cc != x and not leq(E[x], E[cc])]
            mat = [[M[cc].get(q, Q(0)) for q in Z] for cc in O]
            dep_cache[key] = (rank([r_ for r_ in mat if any(r_)]) == len(Z), len(Z))
        return dep_cache[key][0]

    def partner_exists(x, X):
        if not leq(L[x], X):
            return False
        for s in live:
            if s == x:
                continue
            J = join(L[x], L[s])
            if len(J) < 9 and leq(J, X) and leq(J, E[s]):
                return True
        return False
    status = {}
    info = {}
    for x in live:
        rx = recv.get(x, [])
        if not rx and not leak[x]:
            continue
        rX = [cc for cc in rx if not leq(E[x], E[cc])]
        blocking = [cc for cc in rX if not partner_exists(x, meet(U[x], E[cc]))]
        leakblock = bool(leak[x]) and not partner_exists(x, U[x])
        status[x] = 'BLOCKED' if (blocking or leakblock) else 'OPEN'
        info[x] = dict(receivers=rx, leaks=leak[x], blocking=blocking, leak_blocked=leakblock)
    beta, min3, why = {}, {}, {}
    for x, st in status.items():
        if st != 'BLOCKED':
            continue
        dE = len(E[x])
        FU = meet(U[x], cap[x], E[x])
        rX = [cc for cc in recv.get(x, []) if not leq(E[x], E[cc])]
        rcap = meet(E[x], *[E[cc] for cc in rX]) if rX else E[x]
        fmax = min(len(rcap), 8)
        if not leq(L[x], FU):
            raise ValueError(('empty restore-entry interval', x))
        dmin, dmax = len(L[x]), len(FU)
        best2 = None
        excluded = []
        for G in (subspaces_between(L[x], rcap) if leq(L[x], rcap) else []):
            f = len(G)
            if f >= dE or f > fmax or f == dmin:
                continue
            if not P_at(G, x):
                excluded.append(dict(frame=list(G), why='no register can sit at G'))
                continue
            if departure_impossible(x, G):
                excluded.append(dict(frame=list(G), why='departure from G: M[O][Z] full column rank', Z=dep_cache[(x, G)][1]))
                continue
            dG = len(meet(G, FU))
            for d in range(dmin, min(dmax, dG, f - 1) + 1):
                o = c[f - d] + c[dE - f] - c[dE - d]
                if best2 is None or o < best2[0]:
                    best2 = (o, d, f, G)
        best3 = None
        for d in range(dmin, dmax + 1):
            for parts in compositions(dE - d, 3):
                if d + parts[0] > fmax:
                    continue
                o = sum(c[a] for a in parts) - c[sum(parts)]
                if best3 is None or o < best3[0]:
                    best3 = (o, d, parts)
        if best2 is None and best3 is None:
            raise ValueError(('no admissible restore chain', x))
        beta[x] = min(b[0] for b in (best2, best3) if b is not None)
        min3[x] = best3[0] if best3 is not None else None
        why[x] = dict(two_jump=(dict(overhead=best2[0], entry_dim=best2[1], visit_dim=best2[2], visit_frame=list(best2[3]))
                                if best2 else None),
                      three_or_more=(dict(overhead=best3[0], entry_dim=best3[1], jumps=list(best3[2])) if best3 else None),
                      excluded_two_jump_frames=excluded, entry_dims=[dmin, dmax], first_frame_cap=list(rcap))

    def blocked_cheap_lifter(h):
        """a blocked register has no gate at its entry frame: carrying content upward needs >= 3 restore-phase jumps"""
        return min3[h] is None or min3[h] < beta[h] + visit_unit
    groups = []
    open_info = {}
    for x, st in sorted(status.items()):
        if st != 'OPEN' or x in R or not recv.get(x):
            continue
        FU = meet(U[x], cap[x], E[x])
        feasible = []
        rejected = []
        for F in subspaces_between(L[x], FU):
            if len(F) >= 9:
                continue
            P = P_at(F, x)
            if not P:
                rejected.append(dict(frame=list(F), why='no reader at F'))
                continue
            if departure_impossible(x, F):
                rejected.append(dict(frame=list(F), why='departure from F: M[O][Z] full column rank', Z=dep_cache[(x, F)][1]))
                continue
            feasible.append((F, P))
        if not feasible:
            groups.append(dict(members=[x], kind='forced-visit', register=x))
            open_info[x] = dict(kind='forced-visit', rejected_skip_frames=rejected)
            continue
        payers = {x}
        charged = True
        frames_ = []
        for F, P in feasible:
            SF = set(span(F))
            needy = []
            for cc in recv[x]:
                if set(span(L[cc])) <= SF:
                    continue
                if any(h in R and (SE[h] & SE[cc]) > SF for h in P):
                    continue
                needy.append(cc)
            if not needy:
                charged = False
                frames_.append(dict(frame=list(F), free=True))
                break
            N = [h for h in P if h not in R]
            frames_.append(dict(frame=list(F), needy_receivers=needy, carriers=N))
            payers |= set(N)
        if not charged:
            open_info[x] = dict(kind='free-skip', skip_frames=frames_)
            continue
        cheap = sorted(h for h in payers if status.get(h) == 'BLOCKED' and blocked_cheap_lifter(h))
        if cheap:
            open_info[x] = dict(kind='uncharged (blocked carrier could lift inside its forced visit)', carriers=cheap)
            continue
        groups.append(dict(members=sorted(payers), kind='zero-sum', register=x))
        open_info[x] = dict(kind='zero-sum', skip_frames=frames_, rejected_skip_frames=rejected)
    lifts = []
    for cc in sorted(R):
        for q in sorted(M[cc]):
            if q == cc or q not in R or not M[cc][q]:
                continue
            Vq = E[q]
            SV = set(span(Vq))
            if leq(E[cc], Vq) or leq(L[cc], Vq):
                continue
            VE = meet(Vq, E[cc])
            SVE = set(span(VE))
            free = [h for h in live if h in R and h not in (q, cc) and SL[h] <= SVE and not (SE[h] & SE[cc]) <= SV]
            if free:
                continue
            N = sorted(h for h in live if h not in R and SL[h] <= SVE)
            if not N or any(status.get(h) == 'BLOCKED' and blocked_cheap_lifter(h) for h in N):
                continue
            lifts.append(dict(members=N, kind='lift', receiver=cc, source=q, region=list(Vq)))
    merged = []
    for grp in groups + lifts:
        P = set(grp['members'])
        hit = [m for m in merged if m['members'] & P]
        mem = set(P)
        parts = [grp]
        for m in hit:
            mem |= m['members']
            parts += m['parts']
        merged = [m for m in merged if m not in hit] + [dict(members=mem, parts=parts)]
    merged = sorted(merged, key=lambda m: min(m['members']))
    extras_blocked = sum(beta.values())
    extras_open = len(merged) * visit_unit
    return dict(bound=lb['cost'] + extras_blocked + extras_open, LB_forced=lb['cost'], LB_profile={str(k): v for k, v in lb['profile'].items()},
                forced_caps=len(caps), caps={str(r): dict(cap=list(U), receivers=recv[r]) for r, U in sorted(caps.items())},
                blocked=len(beta), extras_blocked=extras_blocked, groups=len(merged), extras_open=extras_open,
                beta={str(x): v for x, v in sorted(beta.items())}, why={str(x): v for x, v in sorted(why.items())},
                status={str(x): v for x, v in sorted(status.items())}, info={str(x): v for x, v in sorted(info.items())},
                open_info={str(x): v for x, v in sorted(open_info.items())},
                merged=[dict(members=sorted(m['members']), parts=[dict((k, v) for k, v in p.items() if k != 'members') for p in m['parts']])
                        for m in merged],
                _lb=lb, _LU=LU, _M=M, _E=E, _rows=rows)


# ------------------------------------------------------------------------------------------------ literal itineraries
def literal_restore_chains(w):
    """per register: literal frame at restore entry and its literal restore-phase jumps (the auditor's climb order)"""
    R_ = w['report']['R']
    n = 2 * V + R_
    start = [(p,) for p in w['ports']] + [()] * (V + R_)
    for q, U in w.get('start_extra', {}).items():
        start[int(q)] = basis(tuple(U))
    E = end_frames(w)
    cur = [basis(tuple(s)) for s in start]
    npre = w.get('prelude_events', 0)
    for e in w['A'][:npre]:
        if e[0] == 'warp':
            cur[e[1]] = basis(tuple(e[4]))
        else:
            for q in FX.regs_of(e):
                cur[q] = basis(tuple(e[-1]))
    for e in w['A'][npre:]:
        for q in FX.regs_of(e):
            cur[q] = basis(tuple(e[-1]))
    byp = {}
    for op, rec in enumerate(w['warps'], 1):
        byp.setdefault(rec[0], []).append(op)
    for p in range(len(w['B']) + 1):
        for op in byp.get(p, []):
            rec = w['warps'][op - 1]
            if cur[rec[1]] != basis(tuple(rec[3])):
                raise ValueError(('literal warp frame mismatch', op))
            cur[rec[1]] = basis(tuple(rec[4]))
        if p < len(w['B']):
            for q in FX.regs_of(w['B'][p]):
                cur[q] = basis(tuple(w['B'][p][-1]))
    entry = list(cur)
    seq = collections.defaultdict(list)
    for i, e in enumerate(w['restore']):
        for q in FX.regs_of(e):
            F = basis(tuple(e[-1]))
            if not leq(cur[q], F):
                raise ValueError(('literal restore frame not monotone', i, q))
            if len(F) > len(cur[q]):
                seq[q].append(('R%d' % i, len(F), len(F) - len(cur[q])))
            cur[q] = F
    c = FX.weights()
    out = {}
    for q in live_registers(w):
        if not leq(cur[q], E[q]):
            raise ValueError(('literal end frame below current frame', q))
        jumps = list(seq.get(q, []))
        if len(E[q]) > len(cur[q]):
            jumps.append(('end', len(E[q]), len(E[q]) - len(cur[q])))
        tot = sum(j for _, _, j in jumps)
        ov = sum(c[j] for _, _, j in jumps) - (c[tot] if tot else 0)
        out[q] = dict(entry_dim=len(entry[q]), entry_frame=list(entry[q]), jumps=[list(j) for j in jumps], overhead=ov)
    return out
