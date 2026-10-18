"""bound.py -- lower bound on the certified cost of ANY exact restore for a word's A/B (the restore re-synthesized freely).
bound(w) = LB_forced(w) + sum of forced restore-phase extras (exact arguments, see screen.py / screen4.py / lbforced.py):
  M = restore map of w (w exact => every restored helper c ends at its own input = FIXED combination of entry rows);
  caps: r's restore-entry frame inside E_c for every restored receiver c of r's entry content;
  LB_forced = certified optimum of w with an EMPTY restore and the caps;
  extras per register r with restored receivers or leaked restored inputs (L/U from the capped empty-restore graph):
    BLOCKED (for some receiver c, or for its leaks, no partner s != r with J = L_r+L_s, |J|<9, J <= U_r ^ E_c ^ E_s; for a
      restored r a receiver with E_r <= E_c does not block): min over entry dims d in [dim L_r, dim(U_r ^ cap)] and 2-splits
      (a, D-a), D = dim E_r - d, of c_a + c_{D-a} - c_D; a split whose first frame has dim d+1 (or equals the blocking cap) is
      dropped when no such frame admits partners passing the rank test (receivers' rows on r + partners must have rank <=
      #partners), since r itself cannot deliver;
    OPEN-but-forced 4,996: for every receiver c, every partner frame J has no free lifter (c cannot sit at J; every register
      that can sit at J and climb inside E_c is non-restored, or BLOCKED with no visit frame strictly above J); the payer
      groups ({r} u non-restored lifters) are disjoint between counted registers (overlaps are merged and counted once);
    otherwise 0 (optimistic, keeps the bound valid).
Calibration target: bound(WORD-3042-*) == certified cost 10,868,103,087."""
import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-mdumitrean-Desktop-dev-aigent-math-prime/c80ebb8e-fc28-4d1d-b7ef-b214d4660f98/scratchpad/r15/agents/K/code')
from screen4 import *
from lbforced import lb_forced
CC = bp.costs().c

def rank(rows):
    m = [list(r) for r in rows if any(r)]
    if not m: return 0
    rk = 0; ncol = len(m[0])
    for c in range(ncol):
        piv = next((i for i in range(rk, len(m)) if m[i][c] != 0), None)
        if piv is None: continue
        m[rk], m[piv] = m[piv], m[rk]
        for i in range(len(m)):
            if i != rk and m[i][c] != 0:
                f = m[i][c] / m[rk][c]; m[i] = [a - f * b for a, b in zip(m[i], m[rk])]
        rk += 1
    return rk

def entry_info_graph(g, assign, al, removed):
    out = {}
    for q, segs in al.items():
        if q in removed: continue
        v = segs[-1]; last = None
        for k in g.chains[v]:
            if g.nodes[k][2] in ('tail', 'end'): break
            last = k
        L = tuple(g.lower[last]); U = set(span(FULL))
        if last in set(g.mutable):
            for t in g.nodes[last][0]:
                if t == v: continue
                j = g.nxt.get((last, t))
                if j is not None: U &= set(span(tuple(g.upper[j])))
        else:
            U = set(span(tuple(assign.get(last, g.nodes[last][1]))))
        out[q] = dict(L=L, U=tuple(basis(tuple(U))))
    return out

def split_costs(D):
    return sorted((CC[a] + CC[D - a] - CC[D], a) for a in range(1, D))

def bound(w, detail=False, rows=None, M=None):
    Rs = restored_set(w); E = end_frames(w)
    if M is None: M = restore_map(w)
    if rows is None: rows = entry_rows(w)
    lb = lb_forced(w, M=M); g = lb['graph']; al = aliases(lb['w0'], lb['meta'])
    EI = entry_info_graph(g, lb['assign'], al, set(w['removed']))
    regs = [q for q in EI if not (V <= q < 2 * V)]
    Lof = {q: EI[q]['L'] for q in EI}
    recv = {r: sorted(c for c in Rs if c != r and M[c].get(r)) for r in regs}
    leak = {r: sorted({var for var, word in rows[r] if var in Rs and var != r}) for r in regs}
    _sp = {}
    def SP(x):
        y = _sp.get(x)
        if y is None: y = _sp[x] = frozenset(span(x))
        return y
    SL = {s: SP(Lof[s]) for s in EI}; SE = {s: SP(E[s]) for s in EI}
    def partners(r, Ec):
        # J = L_r + L_s lies in X = U_r ^ E_c ^ E_s  <=>  L_r and L_s both lie in X (no join needed for the test)
        Lr = SL[r]; X0 = SP(EI[r]['U']) if Ec is None else (SP(EI[r]['U']) & SP(Ec))
        if not Lr <= X0: return []
        out = []
        for s in EI:
            if s == r: continue
            Es = SE[s]
            if Lr <= Es and SL[s] <= X0 and SL[s] <= Es:
                J = join(Lof[r], Lof[s])
                if len(J) < 9: out.append((s, J))
        return out
    status = {}; extra = {}; info = {}
    for r in regs:
        if not recv[r] and not leak[r]: continue
        blocking = []
        pc = {}
        for c in recv[r]:
            if r in Rs and leq(E[r], E[c]): continue
            ps = partners(r, E[c]); pc[c] = ps
            if not ps: blocking.append(c)
        pl = partners(r, None) if (leak[r] and r not in Rs) else []
        blocked = bool(blocking) or (bool(leak[r]) and r not in Rs and not pl)
        status[r] = 'BLOCKED' if blocked else 'OPEN'
        info[r] = dict(recv=recv[r], leak=leak[r], blocking=blocking, pc=pc)
    # visit-frame dims of blocked registers (for free-ride checks): entry dims and first-frame dims allowed
    def blocked_extra(r):
        Lr, Ur = Lof[r], EI[r]['U']; cap = set(span(FULL))
        for c in recv[r]: cap &= set(span(E[c]))
        capb = tuple(basis(tuple(cap & set(span(Ur)))))
        bcap = set(span(FULL))
        for c in info[r]['blocking'] or recv[r]: bcap &= set(span(E[c]))
        bcap = tuple(basis(tuple(bcap)))
        best = None; dE = len(E[r]); split_regions = []; best_enumerated_only = [False]
        for d in range(len(Lr), len(capb) + 1):
            D = dE - d
            if D < 2: continue
            for cost, a in split_costs(D):
                f = d + a
                feasible = True; enumerated = False
                if leq(Lr, bcap) and (f == len(Lr) + 1 and d == len(Lr) or f == len(bcap)) and f <= len(bcap):
                    enumerated = True
                    # enumerate first frames J1 of dim f with L_r <= J1 <= bcap; rank test with partners at J1
                    cands = set()
                    if f == len(bcap): cands.add(bcap)
                    else:
                        for z in span(bcap):
                            if z and not leq((z,), Lr): cands.add(join(Lr, (z,)))
                    ok = False; regions = set()
                    for J1 in cands:
                        P = [s for s in EI if s != r and leq(Lof[s], J1) and leq(J1, E[s])]
                        if not P: continue
                        cols = [r] + P
                        outs = [c for c in Rs if c != r and not (r in Rs and leq(E[r], E[c])) and any(M[c].get(q) for q in cols)]
                        if rank([[M[c].get(q, Q(0)) for q in cols] for c in outs]) <= len(P):
                            ok = True
                            SJ1 = set(span(J1)); need = False
                            for c in (info[r]['blocking'] or recv[r]):
                                SEc = set(span(E[c]))
                                if not (SJ1 < SEc) or leq(Lof[c], J1): continue
                                if any(h != r and leq(Lof[h], J1) and leq(J1, E[h]) and (set(span(E[h])) & SEc) > SJ1 for h in Rs): continue
                                ride = False
                                for h in EI:                     # a BLOCKED full-end register whose own visit could sit above J1
                                    if h == r or h in Rs or V <= h < 2 * V or not leq(Lof[h], J1): continue
                                    if status.get(h) != 'BLOCKED': continue
                                    caph = set(span(FULL))
                                    for c2 in recv.get(h, []): caph &= set(span(E[c2]))
                                    if (caph & SEc) > SJ1: ride = True; break
                                if ride: continue
                                need = True; break
                            regions.add(J1 if need else None)
                    feasible = ok
                    if ok: split_regions.append((cost, regions))
                elif f > len(bcap):
                    feasible = False
                if feasible:
                    if best is None or cost < best:
                        best = cost; best_enumerated_only[0] = enumerated
                    elif cost == best and not enumerated:
                        best_enumerated_only[0] = False
                    break
        if best is None:
            best = min(c for c, a in split_costs(dE - len(capb))) if dE - len(capb) >= 2 else 0
        # a lift region is forced only if EVERY feasible enumerated split of minimal cost needs a lift out of the same region and
        # no split without enumeration (assumed feasible, optimistic) achieves the same cost
        forced = None
        mins = [rg for c, rg in split_regions if c == best]
        if mins and best_enumerated_only[0]:
            allr = set().union(*mins)
            if None not in allr and len(allr) == 1: forced = next(iter(allr))
        return best, forced
    lift_regions = {}
    for r, st in status.items():
        if st == 'BLOCKED':
            extra[r], reg_ = blocked_extra(r)
            if reg_ is not None: lift_regions.setdefault(reg_, []).append(r)
    # OPEN-but-forced (non-restored r only):
    #  zero-sum: every partner frame J for receiver c needs a lift (J strictly inside E_c, c cannot sit at J), no restored
    #            register can sit at J and climb inside E_c, all partners are non-restored and not BLOCKED -> r or a partner pays;
    #  rank:     for receiver c every partner frame J fails the rank test on [r] + P_J -> r itself must climb above J.
    groups = []; Rs_list = sorted(Rs); group_frames = {}
    for r, st in status.items():
        if st != 'OPEN' or r in Rs or not recv[r]: continue
        rank_cache = {}
        kind = None; payers = {r}
        for c, ps in info[r]['pc'].items():
            if not ps: continue
            zs = True; rk_fail = True; seenJ = {}
            SEc = SP(E[c])
            for s, J in ps:
                SJ = SP(J)
                if not (SJ < SEc) or SL[c] <= SJ: zs = False
                if zs and any(SL[h] <= SJ and SJ <= SE[h] and (SE[h] & SEc) > SJ for h in Rs_list if h != r): zs = False
                if s in Rs or status.get(s) == 'BLOCKED': zs = False
                if rk_fail and J not in seenJ:
                    P = [h for h in EI if h != r and SL[h] <= SJ and SJ <= SE[h]]
                    key = frozenset(P)
                    if key not in rank_cache:
                        cols = [r] + P; outs = [c2 for c2 in Rs if any(M[c2].get(q) for q in cols)]
                        rank_cache[key] = rank([[M[c2].get(q, Q(0)) for q in cols] for c2 in outs]) <= len(P)
                    seenJ[J] = rank_cache[key]
                    if seenJ[J]: rk_fail = False
                payers.add(s)
            if rk_fail: kind = 'rank'; payers = {r}; break
            if zs and kind is None: kind = 'zero-sum'
        if kind: groups.append((r, payers, kind)); group_frames[r] = [(J, c) for c, ps in info[r]['pc'].items() for s, J in ps]
    # lift (the base's 61 case, checked by its premises): restored c whose entry content q sits inside V (E_q <= V) must be
    # carried above V inside E_c by a full-end register when no restored register can sit inside V and end above V in E_c.
    lifts = []
    for c in Rs:
        for q, x in M[c].items():
            if q == c or not x or q not in Rs: continue
            Vq = E[q]
            if leq(E[c], Vq) or leq(Lof[c], Vq): continue
            if any(h in Rs and leq(Lof[h], Vq) and not leq(E[h], Vq) and (set(span(E[h])) & set(span(E[c]))) > set(span(Vq)) for h in EI): continue
            lifts.append((c, Vq))
    lift_keys = []
    for c, Vq in sorted({(c, Vq) for c, Vq in lifts}):
        payers = {h for h in EI if h not in Rs and not (V <= h < 2 * V) and leq(Lof[h], Vq)}
        ride = False
        for h in payers:
            if h in extra:                       # BLOCKED: could its forced visit frame sit strictly above Vq inside E_c?
                caph = set(span(EI[h]['U'])) | set(span(FULL))
                caph = set(span(FULL))
                for c2 in recv.get(h, []): caph &= set(span(E[c2]))
                if (caph & set(span(E[c]))) > set(span(Vq)): ride = True; break
        if ride: continue
        lift_keys.append((c, Vq, frozenset(payers)))
    merged = []
    for r, P, kind in groups:
        hit = [m for m in merged if m[1] & P]
        rs_ = {r}; Ps = set(P)
        for m in hit: rs_ |= m[0]; Ps |= m[1]
        merged = [m for m in merged if m not in hit] + [(rs_, Ps)]
    open_forced = {('open',) + tuple(sorted(a)): CC[1] * 2 - CC[2] for a, _ in merged}
    regions_counted = set()
    for c, Vq, pay in lift_keys:
        if any(pay & m[1] for m in merged): continue          # shares a payer with a counted open group: count once
        if Vq in regions_counted: continue
        regions_counted.add(Vq); open_forced[('lift', c, Vq)] = CC[1] * 2 - CC[2]
    def shareable(J1, lift_recv, members):
        for r0 in members:
            for J, c in group_frames.get(r0, []):
                Jj = join(J, J1)
                if len(Jj) >= 9: continue
                if any(leq(Jj, E[c]) and leq(Jj, E[c1]) for c1 in lift_recv): return True
        return False
    for J1, rs_ in lift_regions.items():
        if J1 in regions_counted: continue
        pay = {h for h in EI if h not in Rs and not (V <= h < 2 * V) and leq(Lof[h], J1)}
        lift_recv = sorted({c for r0 in rs_ for c in (info[r0]['blocking'] or recv[r0]) if set(span(J1)) < set(span(E[c])) and not leq(Lof[c], J1)})
        if any((pay & m[1]) and shareable(J1, lift_recv, m[0]) for m in merged): continue
        regions_counted.add(J1); open_forced[('blocked-lift',) + tuple(sorted(rs_)) + (J1,)] = CC[1] * 2 - CC[2]
    tot = sum(extra.values()) + sum(open_forced.values())
    res = dict(bound=lb['cost'] + tot, LB_forced=lb['cost'], extras_blocked=sum(extra.values()), extras_open=sum(open_forced.values()),
               n_blocked=len(extra), n_open_forced=len(open_forced), lifts=[k for k in open_forced if k[0] != 'open'])
    if detail: res.update(extra=extra, open_groups=[(sorted(a), sorted(b)) for a, b in merged], open_kinds=[(r, k) for r, P, k in groups], status=status, info={r: dict(recv=v['recv'], leak=v['leak'], blocking=v['blocking']) for r, v in info.items()})
    return res

if __name__ == '__main__':
    w = W(sys.argv[1]); t0 = time.time(); b = bound(w, detail=True); cur = solve(w)
    print('current', cur['cost'], 'bound', b['bound'], 'gap', cur['cost'] - b['bound'], 'LB_forced', b['LB_forced'], 'blocked', b['n_blocked'], b['extras_blocked'],
          'open-forced', b['n_open_forced'], b['extras_open'], 'lifts', b['lifts'], round(time.time() - t0, 2), 's')
    print('open groups', b['open_groups'])
    print('open kinds', b['open_kinds'])
