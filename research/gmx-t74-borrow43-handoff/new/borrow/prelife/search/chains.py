"""(A) Exact alias-chain bound and pricing for the #2474 T74 borrow words.

A physical register carries a chain of streams x1 -> x2 -> ... ; x_{k+1} may follow x_k (dirty borrow
of a retired register, LIFO-mirrored by the FULL cleanup) iff
  (L) end(x_k) < start(x_{k+1})                                   (liveness)
  (F) dim(frame of x_k at its last touch) <= dim(first gate frame of x_{k+1})
      (fixed gate frames; a rank-0 K_G warp can re-seat the lender inside the follower's first frame)
Sources (live from t=0, hold an input) and targets/restored cold helpers (must hold their value at the
end) can never follow; targets and restored cold helpers can never lead.

Minimum helper registers = (#streams - max matching) - #source heads; deletable = 429 - that.
Price: an edge x->y removes x's final climb and y's entry climb and adds the link climb
(dim f1(y) - d(x)); this is additive, so a max-weight matching under the first-order price is the
best first-order alias set; it is then priced exactly (root of the package's global profile with the
freed mass as rank-48 idle, and ceiling.py ideal-idle).

Modes: literal (compensation dirt reads count as touches at their time) / relaxed (they do not).
usage: chains.py WORD.json.gz
"""
import sys, json, math
from collections import Counter, defaultdict
from wordmodel import Word, regs

M_, KAPPA = 73, 0.0017036763879936765
GLOBAL = {1: 1595615, 2: 420912, 3: 224424, 4: 79920, 5: 22013, 7: 2664, 8: 2664, 48: 25752}
WFAM, CALLS = 66304, 666


def c1(r, a=KAPPA, m=M_, R=48):
    """first-order moment price of one rank-r child replaced by r/R idle children of rank R"""
    if r <= 0:
        return 0.0
    return (r / m) ** (1 - a) - (r / R) * (R / m) ** (1 - a)


def root(prof, W=WFAM, m=M_):
    f = lambda a: sum(n * (r / m) ** (1 - a) for r, n in prof.items()) / W - 1
    lo, hi = 0.0, 0.05
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return lo


def price_root(base, P):
    """T74 package model: replace the per-call local profile base by P on all 666 calls, freed mass as rank-48 idle"""
    g = Counter(GLOBAL)
    for k, v in base.items():
        g[k] -= CALLS * v
    for k, v in P.items():
        g[k] += CALLS * v
    g[48] += CALLS * (sum(k * v for k, v in base.items()) - sum(k * v for k, v in P.items())) / 48
    a = root(dict(g))
    return dict(kappa=a, gain=a / root(GLOBAL) - 1)


def build_streams(Wd, relaxed):
    v = Wd.v
    restored = {int(q) for q in Wd.w.get('helper_final', {})}
    lend = {}
    for t, (sec, e) in enumerate(Wd.events):
        if sec == 'Bwarp':
            lend.setdefault(e[1], t)
    gf = Wd.gateframe
    S = []
    for r in Wd.live:
        if v <= r < 2 * v:
            continue
        tt = [(t, s) for t, s in Wd.touches.get(r, [])]
        cuts = [lend[r]] if r in lend else []
        parts = []
        if cuts:
            parts.append(('pre', [x for x in tt if x[0] < cuts[0]]))
            parts.append(('post', [x for x in tt if x[0] >= cuts[0]]))
        else:
            parts.append(('', tt))
        for k, (part, ts) in enumerate(parts):
            last_part = k == len(parts) - 1
            ft = [t for t, s in ts if t in gf]                 # framed gates
            if not ft and not ts:
                continue
            frames = [gf[t] for t in ft]
            dims = []
            for f in frames:
                if not dims or len(f) != dims[-1]:
                    dims.append(len(f))
            tsel = [t for t, s in ts if not (relaxed and s in ('precondition', 'compensation'))]
            if r < v and part != 'post':
                kind, st = 'source', 0
            else:
                kind = 'alias' if part == 'post' else 'helper'
                st = min(tsel) if tsel else (min(ft) if ft else 0)
            en = max(t for t, s in ts)
            if r in restored and last_part:
                en = Wd.T_END + 1
            sdim = len(Wd.start[r]) if part != 'post' else 0
            S.append(dict(reg=r, part=part, kind=kind, start=st, end=en, dims=dims,
                          sdim=sdim, enddim=len(Wd.end[r]), restored=(r in restored and last_part),
                          lastpart=last_part))
    return S


def chain_profile(chains, S):
    """profile (Counter of climb ranks) of a chain decomposition; chain = list of stream ids"""
    P = Counter()
    for ch in chains:
        x0 = S[ch[0]]
        cur = x0['sdim']
        enddim = None
        for k, i in enumerate(ch):
            x = S[i]
            for d in x['dims']:
                if d > cur:
                    P[d - cur] += 1
                    cur = d
                assert d >= cur
            enddim = x['enddim'] if x['restored'] or k == len(ch) - 1 else None
        last = S[ch[-1]]
        ed = last['enddim'] if last['restored'] else 9
        if ed > cur:
            P[ed - cur] += 1
    return P


def main():
    Wd = Word(sys.argv[1])
    out = {'word': sys.argv[1]}
    base_local = Counter(Wd.paid)
    TG = Counter(c[1] for r in range(Wd.v, 2 * Wd.v) for c in Wd.climbs.get(r, []))
    Wd.centre_paid = Wd.centre_paid + TG     # constant part: centre path + target climbs
    for mode in ('literal', 'relaxed'):
        S = build_streams(Wd, mode == 'relaxed')
        idx = {(x['reg'], x['part']): i for i, x in enumerate(S)}
        # positive control: the word's own chains (lender pre -> post) reproduce the local profile
        own = []
        for i, x in enumerate(S):
            if x['part'] == 'pre':
                own.append([i, idx[(x['reg'], 'post')]])
            elif x['part'] == '':
                own.append([i])
        P = chain_profile(own, S) + Wd.centre_paid
        assert dict(P) == dict(base_local), (mode, dict(P), dict(base_local))
        # positive control: the existing 51 alias edges satisfy (L) and (F)
        bad = []
        for ch in own:
            if len(ch) == 2:
                a, b = S[ch[0]], S[ch[1]]
                if not (a['end'] <= b['start'] and (not a['dims'] or not b['dims'] or a['dims'][-1] <= b['dims'][0])):
                    bad.append((a['reg'], a['end'], b['start'], a['dims'][-1:], b['dims'][:1]))
        res = {'streams': len(S), 'existing_alias_edges': sum(1 for c in own if len(c) == 2),
               'existing_edges_violating': bad}
        n = len(S)
        lead_ok = [x['kind'] != 'source' and not x['restored'] for x in S]
        lead_ok = [not x['restored'] for x in S]               # sources may lead (lend) after retiring
        follow_ok = [x['kind'] != 'source' for x in S]
        import forced
        Dm = {}
        for fr_ in (False, True):
            keep, fidx, N, desc, anc, fst = forced.build(Wd, mode, fr_)
            lendregs = {r for k, r, m in fst if k == 'alias'}
            mk, dk = {}, {}
            for k, r, m in fst:
                part = 'post' if k == 'alias' else ('pre' if r in lendregs else '')
                x, mm = 0, m
                while mm:
                    low = mm & -mm
                    x |= desc[low.bit_length() - 1]
                    mm ^= low
                mk[(r, part)] = m
                dk[(r, part)] = x
            Dm[fr_] = (mk, dk)
        for cond in ('L', 'LF', 'R', 'RF'):
            E = defaultdict(list)
            for i in range(n):
                a = S[i]
                if not lead_ok[i]:
                    continue
                for j in range(n):
                    if i == j or not follow_ok[j]:
                        continue
                    b = S[j]
                    if cond[0] == 'L':
                        if not a['end'] < b['start']:
                            continue
                    else:
                        mk, dk = Dm[cond == 'RF']
                        ka, kb = (a['reg'], a['part']), (b['reg'], b['part'])
                        if ka not in mk or kb not in mk:
                            continue
                        if dk[kb] & mk[ka]:
                            continue
                    if 'F' in cond and a['dims'] and b['dims'] and a['dims'][-1] > b['dims'][0]:
                        continue
                    # weight: x final climb removed, y entry removed, link added
                    da = a['dims'][-1] if a['dims'] else (a['sdim'] or 0)
                    fin_a = 9 - da
                    f1 = b['dims'][0] if b['dims'] else da
                    sy = b['sdim']
                    w = c1(fin_a) + c1(f1 - sy) - c1(max(f1 - da, 0))
                    E[i].append((j, w))
            # max cardinality matching (Hopcroft-Karp-lite via augmenting paths)
            matchR = {}

            def aug(u, seen):
                for j, _ in E[u]:
                    if j in seen:
                        continue
                    seen.add(j)
                    if j not in matchR or aug(matchR[j], seen):
                        matchR[j] = u
                        return True
                return False
            sys.setrecursionlimit(100000)
            mc = sum(1 for u in range(n) if aug(u, set()))
            heads = n - mc
            src = sum(1 for x in S if x['kind'] == 'source')
            Hmin = heads - src
            r = dict(edges=sum(len(e) for e in E.values()), max_matching=mc, registers_nontarget=heads,
                     helper_registers_min=Hmin, deletable_max=len(Wd.helpers) - Hmin)
            # max-weight matching (first-order price) with OR-tools
            from scipy.optimize import linear_sum_assignment as lsa
            import numpy as np
            BIG = 0.0
            C = np.zeros((n, n))
            for i, es in E.items():
                for j, w in es:
                    C[i, j] = -max(w, 0) * 1e6
            if cond in ('L', 'R'):
                # liveness only: price the cap as 'the k most valuable streams become frame-local'
                val = []
                for i, x in enumerate(S):
                    if x['kind'] == 'source':
                        continue
                    P1 = chain_profile([[i]], S)
                    val.append((sum(c1(k) * v for k, v in P1.items()), i))
                val.sort(reverse=True)
                drop = {i for _, i in val[:r['deletable_max']]}
                chains = [[i] for i in range(n) if i not in drop]
                Pn = chain_profile(chains, S) + Wd.centre_paid
                r['priced_as'] = 'top-%d streams frame-local' % len(drop)
                r['local_profile'] = dict(sorted(Pn.items()))
                r['local_mass'] = sum(k * v for k, v in Pn.items())
                res[cond] = r
                res[cond]['_P'] = Pn
                continue
            ri, cj = lsa(C)
            sel = [(i, j) for i, j in zip(ri, cj) if C[i, j] < 0]
            nxt = {i: j for i, j in sel}
            prv = {j: i for i, j in sel}
            chains = []
            for i in range(n):
                if i in prv:
                    continue
                ch = [i]
                while ch[-1] in nxt:
                    ch.append(nxt[ch[-1]])
                chains.append(ch)
            assert sum(len(c) for c in chains) == n
            Pn = chain_profile(chains, S) + Wd.centre_paid
            r['maxweight_edges'] = len(sel)
            ownset = {(S[c[0]]['reg'], S[c[1]]['reg']) for c in own if len(c) == 2}
            newe = [(S[i]['reg'], S[i]['part'], S[i]['kind'], S[i]['dims'], S[j]['reg'], S[j]['part'], S[j]['dims'])
                    for i, j in sel if (S[i]['reg'], S[j]['reg']) not in ownset]
            r['maxweight_new_edges'] = newe
            # envelope: every stream that can follow in some edge and is not followed now -> frame-local
            fol = sorted({j for es in E.values() for j, _ in es} - {j for c in own if len(c) == 2 for j in c[1:]})
            r['followable_not_aliased_now'] = [(S[j]['reg'], S[j]['part'], S[j]['dims']) for j in fol]
            r['maxweight_local_profile'] = dict(sorted(Pn.items()))
            r['maxweight_local_mass'] = sum(k * v for k, v in Pn.items())
            res[cond] = r
            res[cond]['_P'] = Pn
        out[mode] = res
    # ---- pricing
    base = dict(Wd.paid)
    bm = sum(k * v for k, v in base.items())
    a0 = root(GLOBAL)
    out['pricing_base_root'] = a0

    def price(P):
        g = Counter(GLOBAL)
        for k, v in base.items():
            g[k] -= CALLS * v
        for k, v in P.items():
            g[k] += CALLS * v
        freed = CALLS * (bm - sum(k * v for k, v in P.items()))
        g[48] += freed / 48
        return root(dict(g))

    sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),*(['..']*6),'research','complex-local-word-ceiling'))
    import ceiling as CE
    from fractions import Fraction as Q
    cb = CE.ceiling(base, 73, 896, 9, 64, grid=Q(1, 10 ** 10))[1]
    for mode in ('literal', 'relaxed'):
        for cond in ('L', 'LF', 'R', 'RF'):
            P = out[mode][cond].pop('_P')
            a = price(P)
            cc = CE.ceiling(dict(P), 73, 896, 9, 64, grid=Q(1, 10 ** 10))[1]
            out[mode][cond]['kappa_root_rank48_idle'] = a
            out[mode][cond]['gain_vs_2474'] = a / a0 - 1
            out[mode][cond]['ceiling_ratio'] = float(cc / cb)
    # ideal: every helper stream frame-local (all helper/alias climbs removed)
    P = Counter(Wd.centre_paid)
    SS = build_streams(Wd, True)
    P += chain_profile([[i] for i, x in enumerate(SS) if x['kind'] == 'source'], SS)
    for x in []:
        if x['kind'] == 'source':
            cur = 1
            for d in x['dims'] + [9]:
                if d > cur:
                    P[d - cur] += 1
                    cur = d
    a = price(P)
    out['ideal_all_helpers_free'] = dict(kappa=a, gain=a / a0 - 1,
                                         ceiling_ratio=float(CE.ceiling(dict(P), 73, 896, 9, 64, grid=Q(1, 10 ** 10))[1] / cb))
    print(json.dumps(out, indent=1, default=str))


if __name__ == '__main__':
    main()
