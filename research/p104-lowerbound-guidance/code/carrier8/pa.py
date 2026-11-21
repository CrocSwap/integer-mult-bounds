"""CARRIER8 pa.py (own code): PAST-ATTRIBUTION RELAY analysis of a pinned run (eng / fattr op format).
ops: ('INIT', r, C) | ('MOVE', r, D) | ('ADD', d, lam, s) | ('CLEAR', r).  init: {public: (chart, content)}.
Charts = frozensets of ints (F2-subspaces).  Contents = dict symbol -> scalar (Fraction, or int mod 2 if p == 2).
Steps:
 1 forward: contents, charts, UP-FA weights on publics -> owned output events (alpha), owned intakes.
 2 backward PA: content of public P at tau = sum_Q mu_Q final_Q + sum_e mu_e content(owned source at event e), e after tau.
 3 every owned intake = cold part (finals; checked cold at the taker chart K) + hot part (events; checked chart_e >= K).
   fold rule: if the hot part's net effective vector is cold at K it is moved into the cold part (no edge).
 4 epochs (intake block, output block) per lifetime; A' = meet(intake charts [+ chart at previous epoch's last output]);
   B = join(output charts); w = sum alpha; C = effective content at outputs; c = sum cold parts; N = relay coefficients.
 5 checks: C = c + N C exactly; odd receipts = sum_j w_j C_j^T; relay legality A'_j <= B_i on every edge;
   segment ascent >= dim(A'+B) - dim A' >= rank Q[supp w, supp c]; acyclicity; level cut R >= sum_m rank M_m."""
from fractions import Fraction as Fr
import sys
sys.setrecursionlimit(100000)

dot = lambda a, b: bin(a & b).count('1') & 1
fdim = lambda F: len(F).bit_length() - 1

def basis(F):
    piv = {}
    for v in F:
        while v:
            h = v.bit_length() - 1
            if h in piv: v ^= piv[h]
            else: piv[h] = v; break
    return list(piv.values())

def span(vs):
    S = {0}
    for v in vs:
        if v not in S: S |= {x ^ v for x in S}
    return frozenset(S)

def join(A, B): return span(basis(A) + basis(B))

class Fld:
    def __init__(s, p): s.p = p
    def c(s, x): return (int(x) % 2) if s.p == 2 else Fr(x)
    def z(s, x): return x == 0
    def norm(s, x): return x % 2 if s.p == 2 else x
    def inv(s, x): return 1 if s.p == 2 else 1 / Fr(x)

def addv(F, a, lam, b):
    for k, v in b.items():
        nv = F.norm(a.get(k, 0) + lam * v)
        if nv == 0: a.pop(k, None)
        else: a[k] = nv

def rank(F, rows):
    """rank of a list of dict-vectors"""
    piv = {}; r = 0
    for row in rows:
        v = {k: x for k, x in row.items() if x != 0}
        while v:
            k = max(v)
            if k in piv:
                pv = piv[k]; f = F.norm(v[k] * F.inv(pv[k]))
                addv(F, v, -f, pv)
            else:
                piv[k] = v; r += 1; break
    return r

def pairing_rank(P, D, S):
    piv = {}; r = 0
    for t in D:
        v = sum(1 << j for j, s in enumerate(S) if dot(P[t], P[s]))
        while v:
            h = v.bit_length() - 1
            if h in piv: v ^= piv[h]
            else: piv[h] = v; r += 1; break
    return r

def analyze(ops, init, P, F, ports=None, fold=True, levels=True, quiet=True):
    T = len(P); n = max(P).bit_length() if ports is None else max(P).bit_length()
    nbits = max(max(P).bit_length(), max((max(c) for c, _ in init.values()), default=0).bit_length())
    isX = lambda r: r[0] == 'X'
    reg = {k: [C, dict(c)] for k, (C, c) in init.items()}
    start = {k: dict(c) for k, (C, c) in init.items()}
    pubs = set(init)
    W = {k: {} for k in init}
    owned = {}            # reg -> lifetime id
    L = []                # lifetimes: dict(reg, ev=[...], asc_at=[(i, asc)])
    evinfo = {}           # op index -> (life id, chart of owned source, effective content later)
    srcsnap = {}          # op index -> content of owned source (raw)
    bad = []; R = 0
    for i, op in enumerate(ops):
        t = op[0]
        if t == 'INIT':
            r, C = op[1], op[2]; reg[r] = [C, {}]; owned[r] = len(L)
            L.append(dict(reg=r, ev=[], asc=[], init=C, i0=i))
        elif t == 'CLEAR':
            r = op[1]; L[owned[r]]['end'] = i; del owned[r]; del reg[r]
        elif t == 'MOVE':
            r, D = op[1], op[2]; C = reg[r][0]
            if r in owned:
                if not (C <= D or D <= C): bad.append(('nest', i))
                if C <= D:
                    a = fdim(D) - fdim(C); R += a; L[owned[r]]['asc'].append((i, a))
            else:
                if not C <= D: bad.append(('pub-desc', i))
                if r[0] == 'Y' and any(dot(v, P[r[1]]) for v in basis(D)): bad.append(('Y-hot', i))
            reg[r][0] = D
        else:
            d, lam, s = op[1], F.c(op[2]), op[3]
            Cd, Cs = reg[d][0], reg[s][0]
            if d == s or not Cd <= Cs: bad.append(('add', i))
            if d in pubs:
                om = {}
                if isX(d): om[d[1]] = lam
                addv(F, om, -lam, W[d])
                if s in pubs: addv(F, W[s], 1, om)
                else:
                    L[owned[s]]['ev'].append(('O', i, Cs, om)); srcsnap[i] = dict(reg[s][1]); evinfo[i] = Cs
            else:
                lf = L[owned[d]]
                if s in pubs:
                    lf['ev'].append(('I', i, Cd, lam, None))
                else:
                    L[owned[s]]['ev'].append(('O', i, Cs, {})); srcsnap[i] = dict(reg[s][1]); evinfo[i] = Cs
                    lf['ev'].append(('I', i, Cd, lam, i))
                lf.setdefault('raw', {})[i] = {k: lam * v for k, v in reg[s][1].items()}
            addv(F, reg[d][1], lam, reg[s][1])
    fin = {k: dict(v[1]) for k, v in reg.items() if k in pubs}
    def eff(c):
        e = {}
        for k, v in c.items():
            if k[0] == 'y': e[k[1]] = F.norm(e.get(k[1], 0) + v)
            elif k[0] == 'x':
                for kk, vv in fin[('X', k[1])].items():
                    if kk[0] == 'y': e[kk[1]] = F.norm(e.get(kk[1], 0) - v * vv)
        return {a: b for a, b in e.items() if b != 0}
    # pinned checks
    pin = []
    for k, c in fin.items():
        C = reg[k][0]
        if k[0] == 'Y' and c != {('y', k[1]): 1}: pin.append(k)
        if k[0] == 'X' and (c.get(('x', k[1])) != 1 or any(sym[0] == 'x' and sym != ('x', k[1]) for sym in c)): pin.append(k)   # x-balance only (h allowed)
        if k[0] not in 'XY':
            if c != start[k] and any(sym[0] == 'x' for sym in c): pin.append(k)
            cold = all(not dot(v, P[sym[1]]) for sym in c if sym[0] == 'y' for v in basis(C))
            if not cold: pin.append(('helper-final-hot', k))
    effev = {i: eff(c) for i, c in srcsnap.items()}
    # backward PA
    expr = {k: {('F', k): 1} for k in pubs}
    intake_expr = {}
    for i in range(len(ops) - 1, -1, -1):
        op = ops[i]
        if op[0] != 'ADD': continue
        d, lam, s = op[1], F.c(op[2]), op[3]
        if d in pubs:
            if s in pubs: addv(F, expr[d], -lam, expr[s])
            else: addv(F, expr[d], -lam, {('E', i): 1})
        else:
            if s in pubs: intake_expr[i] = dict(expr[s])
    effin = {k: eff(c) for k, c in fin.items()}
    # epochs
    EP = []          # global epoch list
    chk = dict(pa_fail=0, cold_fail=0, chart_fail=0, Cconst_fail=0, rec_fail=0, CcN_fail=0, relay_fail=0, seg_fail=0,
               folded=0, hot_intakes=0, edges_hot=0, cri=0)
    ev2ep = {}
    for li, lf in enumerate(L):
        evs = lf['ev']; blocks = []
        for e in evs:
            if e[0] == 'I':
                if not blocks or blocks[-1]['phase'] == 'out': blocks.append(dict(ins=[], outs=[], phase='in'))
                blocks[-1]['ins'].append(e)
            else:
                if not blocks: blocks.append(dict(ins=[], outs=[], phase='out'))
                blocks[-1]['outs'].append(e); blocks[-1]['phase'] = 'out'
        prevZ = None; prev_last = lf['i0']; prev_id = None
        for b in blocks:
            j = len(EP)
            A = None
            for e in b['ins']: A = e[2] if A is None else A & e[2]
            Ap = A
            if prevZ is not None and A is not None: Ap = A & prevZ
            B = frozenset([0])
            for e in b['outs']: B = join(B, e[2])
            w = {}
            for e in b['outs']: addv(F, w, 1, e[3])
            last = b['outs'][-1][1] if b['outs'] else (b['ins'][-1][1] if b['ins'] else prev_last)
            seg = sum(a for (ii, a) in lf['asc'] if prev_last < ii <= last)
            ep = dict(life=li, A=A, Ap=Ap, B=B, w=w, c={}, N={}, seg=seg, first=b['ins'][0][1] if b['ins'] else None,
                      lastin=b['ins'][-1][1] if b['ins'] else -1, outs=[e[1] for e in b['outs']], ins=b['ins'])
            if prev_id is not None: ep['N'][prev_id] = 1
            EP.append(ep)
            for e in b['outs']: ev2ep[e[1]] = j
            if b['outs']: prevZ = b['outs'][-1][2]
            prev_last = last; prev_id = j
    # contents per epoch
    for j, ep in enumerate(EP):
        Cs = [effev[i] for i in ep['outs']]
        if any(c != Cs[0] for c in Cs): chk['Cconst_fail'] += 1
        ep['C'] = Cs[0] if Cs else None
    for j, ep in enumerate(EP):
        lf = L[ep['life']]
        for e in ep['ins']:
            i, K, lam, src = e[1], e[2], e[3], e[4]
            actual = eff(lf['raw'][i])
            coldset = [s for s in range(T) if all(not dot(v, P[s]) for v in basis(K))]
            cs = set(coldset)
            if src is not None:
                terms = {('E', src): lam}
            else:
                terms = {k: lam * v for k, v in intake_expr[i].items()}
            cold = {}; hot = {}; hv = {}
            for k, mu in terms.items():
                if mu == 0: continue
                if k[0] == 'F': addv(F, cold, mu, effin[k[1]])
                else:
                    hot[k[1]] = F.norm(hot.get(k[1], 0) + mu)
                    if not K <= evinfo[k[1]]: chk['chart_fail'] += 1
                    addv(F, hv, mu, effev[k[1]])
            hot = {a: b for a, b in hot.items() if b != 0}
            tot = dict(cold); addv(F, tot, 1, hv)
            if tot != actual: chk['pa_fail'] += 1
            if any(s not in cs for s in cold): chk['cold_fail'] += 1
            if fold and hot and all(s in cs for s in hv):
                addv(F, cold, 1, hv); hot = {}; chk['folded'] += 1
            if hot: chk['hot_intakes'] += 1
            addv(F, ep['c'], 1, cold)
            for evi, mu in hot.items():
                ii = ev2ep[evi]; ep['N'][ii] = F.norm(ep['N'].get(ii, 0) + mu); chk['edges_hot'] += 1
                if EP[ii]['lastin'] > i: chk['cri'] += 1          # cleaner re-intake after the pickup
        ep['N'] = {a: b for a, b in ep['N'].items() if b != 0}
    # acyclicity certificate: last-intake time strictly increases along every relay (CF class)
    chk['pot_viol'] = sum(1 for j, ep in enumerate(EP) for i2 in ep['N'] if not EP[i2]['lastin'] < ep['lastin'])
    # teeth: naive price (whole intake increment treated as cold, no PA split) exceeding the segment ascent
    chk['naive_gt_seg'] = 0
    for j, ep in enumerate(EP):
        if not ep['ins'] or not ep['w']: continue
        inc = {}
        for e in ep['ins']: addv(F, inc, 1, eff(L[ep['life']]['raw'][e[1]]))
        D = [t for t, v in ep['w'].items() if v != 0]; S = [s for s, v in inc.items() if v != 0]
        if D and S and pairing_rank(P, D, S) > ep['seg']: chk['naive_gt_seg'] += 1
    # C = c + N C
    for j, ep in enumerate(EP):
        if ep['C'] is None: continue
        v = dict(ep['c'])
        for i2, mu in ep['N'].items():
            if EP[i2]['C'] is None: continue
            addv(F, v, mu, EP[i2]['C'])
        if v != ep['C']: chk['CcN_fail'] += 1
        for i2 in ep['N']:
            if EP[i2]['C'] is None: continue
            if not (ep['Ap'] is None or ep['Ap'] <= EP[i2]['B']): chk['relay_fail'] += 1
    # receipts on odd cells
    rec = {}
    for (k, c) in fin.items():
        if k[0] == 'X':
            dlt = dict(c); addv(F, dlt, -1, start[k]); rec[k[1]] = {kk[1]: v for kk, v in dlt.items() if kk[0] == 'y'}
    for t in range(T):
        for s in range(T):
            if not dot(P[t], P[s]): continue
            val = 0
            for ep in EP:
                if ep['C'] is None: continue
                val = F.norm(val + ep['w'].get(t, 0) * ep['C'].get(s, 0))
            if val != rec.get(t, {}).get(s, 0): chk['rec_fail'] += 1
    # per-epoch price / segment
    own = 0; drops = 0
    for ep in EP:
        A = ep['Ap'] if ep['Ap'] is not None else None
        if ep['C'] is None or A is None:
            ep['drop'] = 0; ep['own'] = 0; continue
        AB = join(A, ep['B'])
        ep['drop'] = fdim(AB) - fdim(A)
        D = [t for t, v in ep['w'].items() if v != 0]; S = [s for s, v in ep['c'].items() if v != 0]
        ep['own'] = pairing_rank(P, D, S) if D and S else 0
        if not (ep['seg'] >= ep['drop'] >= ep['own']): chk['seg_fail'] += 1
        own += ep['own']; drops += ep['drop']
    # acyclicity
    order = topo(EP)
    res = dict(bad=bad, pinned=pin, R=R, own=own, drops=drops, chk=chk, EP=EP, acyclic=order is not None, rec=rec)
    if levels and order is not None:
        res['LS'] = {}
        for name, prt in [('all', range(T))] + ([('ports', ports)] if ports is not None else []):
            prt = set(prt); tot = 0; per = []
            for m in range(0, nbits + 1):
                Cm = {}
                for j in order:
                    ep = EP[j]
                    if ep['C'] is None: Cm[j] = {}; continue
                    v = dict(ep['c']) if (ep['Ap'] is not None and fdim(ep['Ap']) <= m) else {}
                    for i2, mu in ep['N'].items():
                        if i2 in Cm: addv(F, v, mu, Cm[i2])
                    Cm[j] = v
                rows = {}
                for j, ep in enumerate(EP):
                    if ep['C'] is None or ep['Ap'] is None: continue
                    if fdim(join(ep['Ap'], ep['B'])) <= m: continue
                    cv = {s: x for s, x in Cm[j].items() if s in prt}
                    if not cv: continue
                    for t, x in ep['w'].items():
                        if t in prt: rows.setdefault(t, {}); addv(F, rows[t], x, cv)
                rk = rank(F, list(rows.values())); per.append(rk); tot += rk
            res['LS'][name] = (tot, per)
    return res

def topo(EP):
    indeg = {j: 0 for j in range(len(EP))}; out = {j: [] for j in range(len(EP))}
    for j, ep in enumerate(EP):
        for i2 in ep['N']: indeg[j] += 1; out[i2].append(j)
    Q = [j for j in indeg if indeg[j] == 0]; order = []
    while Q:
        j = Q.pop(); order.append(j)
        for k in out[j]:
            indeg[k] -= 1
            if indeg[k] == 0: Q.append(k)
    return order if len(order) == len(EP) else None
