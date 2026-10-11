"""Whole-residual idle hosting as an exact assignment (CP-SAT), at profile level, for the eleven-stage bit template (m = 78, 120 sources,
240 copies per idle child, deficit D = 408).  Rule = PR #442's: a residual lies whole inside one copy of one idle child whose window contains its
stage; nothing is split.  Inputs are the local paid profile per call (C++ cohort legality) and the helper residual widths; the optimum is priced
with the exact two-engine moment certificate (PR #442/#443 engine, lower endpoint).  This reproduces the pipeline's hosted bit endpoint
(emit_k.py --discover with HiGHS) and is used to scan the number of pivots; it is a cross-check, the pipeline is the certificate.
needs: ortools (pip install ortools).   usage: hosting_model.py REPO_RESEARCH_DIR PROFILE.json   (PROFILE: {"local": {rank: n}, "widths": {w: n}})
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0."""
import sys, json, math, importlib.util
from collections import Counter
from fractions import Fraction as Q
sys.set_int_max_str_digits(0)

def engine(R, name='moment'):
    sp = importlib.util.spec_from_file_location('eng_' + name, str(R) + '/e8-r740-replica32/code/engines/' + name + '.py'); mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod

def events(K, a):
    """schedule of the K-bridge recipe: locals, bridges, idle children (rank a*(stage index))"""
    out, idx = [], [0]
    def local(s, p):
        out.append(dict(kind='local', stage=s, pair=p))
        def idle(pair, rank): out.append(dict(kind='idle', pair=pair, rank=rank, idx=idx[0])); idx[0] += 1
        if s % 2 == 1 and s <= 2 * K - 3: idle((s + 1) // 2, a * (s + 1))
        elif s % 2 == 0 and 2 <= s <= 2 * K - 2: idle(s // 2, a)
        elif s == 2 * K:
            for p2 in range(K): idle(p2, a * (2 * K - (2 * p2 + 2)))
    def bridge(d, s_): out.append(dict(kind='bridge', dst=d, src=s_))
    local(0, 0); st = 1
    for j in range(K):
        local(st, j); st += 1
        if j < K - 1: bridge(j, j + 1)
        local(st, j); st += 1
        if j < K - 1: bridge(j, j + 1)
    for j in reversed(range(K - 1)): bridge(j + 1, j)
    return out

def windows(schedule):
    """idle child -> (pair, rank, stages whose local invocation lies between the pair's last touch and the child, position)"""
    last, out, loc = {}, {}, []
    for pos, e in enumerate(schedule):
        k = e['kind']
        if k == 'local': loc.append((pos, e['stage'], e['pair'])); last[e['pair']] = pos
        elif k == 'bridge': last[e['dst']] = pos; last[e['src']] = pos
        elif k == 'idle':
            p = e['pair']; lo = last.get(p, -1)
            out[e['idx']] = (p, e['rank'], frozenset(s for q, s, pp in loc if lo < q < pos and pp != p), pos)
    return out

def patterns(rank, widths, maxk=14):
    ws = sorted(set(widths), reverse=True); out = []
    def rec(i, cur, s):
        if i == len(ws): out.append(tuple(cur)); return
        w = ws[i]; k = 0
        while s + k * w <= rank and len(cur) + k <= maxk:
            rec(i + 1, cur + [w] * k, s + k * w); k += 1
    rec(0, [], 0); return out

def solve(local, widths, S=11, V=120, a=7, T=1, q0=1.28e-3, tl=120, workers=4):
    from ortools.sat.python import cp_model
    K = (S - 1) // 2; m = 1 + a * S; C = 2 * V * T // T; SC = 10 ** 5
    win = windows(events(K, a)); D = T * (2 * K * V - 72 * S)
    g = lambda r: r * ((m / r) ** q0 - 1)
    f = lambda r: int(round(g(r) / q0 * SC)) if r else 0
    ch, fixed = {}, Counter()
    for i, (p, r, stg, pos) in win.items():
        if r == 0: continue
        if stg: ch[i] = dict(rank=r, stages=sorted(stg))
        else: fixed[r] += C * T
    supply = Counter()
    for s in range(S):
        for x, c in widths.items(): supply[s, x] += c
    ws = sorted(widths); M = cp_model.CpModel(); n = {}
    for i, c in ch.items():
        for s in c['stages']:
            for x in ws:
                if supply.get((s, x), 0): n[i, s, x] = M.NewIntVar(0, min(supply[s, x], (C * c['rank']) // x), 'n%d_%d_%d' % (i, s, x))
    for (s, x), av in supply.items():
        M.Add(sum(n[k] for k in n if k[1] == s and k[2] == x) == av)              # host all: every residual sits in some copy
    obj, ys = [], {}
    for i, c in ch.items():
        r = c['rank']; lst = []
        for pat in patterns(r, ws):
            v = M.NewIntVar(0, C, 'y%d_%s' % (i, '_'.join(map(str, pat)))); lst.append((pat, v)); obj.append(v * f(r - sum(pat)))
        M.Add(sum(v for _, v in lst) == C); ys[i] = lst
        for x in ws:
            if any((i, s, x) in n for s in c['stages']):
                M.Add(sum(n[i, s, x] for s in c['stages'] if (i, s, x) in n) == sum(pat.count(x) * v for pat, v in lst))
    M.Minimize(sum(obj)); sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = tl; sv.parameters.num_workers = workers
    st = sv.Solve(M); assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), sv.StatusName(st)
    rem = Counter()
    for i, lst in ys.items():
        for pat, v in lst:
            z = sv.Value(v)
            if z and ch[i]['rank'] - sum(pat): rem[ch[i]['rank'] - sum(pat)] += z
    prof = Counter({r: z * S * T for r, z in local.items()})
    for r, z in fixed.items(): prof[r] += z
    for r, z in rem.items(): prof[r] += z * T
    return dict(status=sv.StatusName(st), profile=dict(prof), remainder=dict(rem), m=m, deficit=D)

def price(R, res):
    """exact lower endpoint of c for the profile (W from m*W - mass = deficit)"""
    prof = {int(r): z for r, z in res['profile'].items() if z}; m, D = res['m'], res['deficit']
    mass = sum(r * z for r, z in prof.items()); assert (mass + D) % m == 0, 'W not integral'
    W = (mass + D) // m; ENG = engine(R)
    return Q(ENG.certify(prof, m, W, True)['lower']), W

if __name__ == '__main__':
    R, pp = sys.argv[1:3]; d = json.load(open(pp))
    res = solve({int(k): v for k, v in d['local'].items()}, {int(k): v for k, v in d['widths'].items()})
    c, W = price(R, res); print(json.dumps(dict(status=res['status'], c=float(c), c_exact='%d/%d' % (c.numerator, c.denominator), W=W, remainder=res['remainder'])))
