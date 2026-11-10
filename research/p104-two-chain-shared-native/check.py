#!/usr/bin/env python3
"""One native word serving two root chains: exact replay of the word, the two-chain root, the HOST2 caller, the complete invoice and the outer constants.
Standard library only (plus the retained interval engines).  python3 -I -B check.py     (writes nothing)
Steps: (1) event-by-event exact replay of data/word.json.gz, endpoint with two main planes per port; (2) the root, literally two #6833 chain roots, with a direct check that a wrong root X/Y FAILS;
(3) the HOST2 caller at the four central characters, its targets read from the root masks, with controls; (4) the invoice rebuilt from word, root and caller, with the #6889 word (through its own root) and #6833 as controls;
(5) raw bound by three definitions, growth figures; (6) BIT pins, interval engines, strictification, compiler and outer ledger; departures.
Prints PASS_P104_TWO_CHAIN_SHARED_NATIVE.  (physical.py, caller_physical.py, cover_check.py are the other commands.)"""
import gzip, json, os, sys, subprocess, importlib.util, random, hashlib, math, copy
from collections import Counter
from decimal import Decimal as D, getcontext
from fractions import Fraction as Q
getcontext().prec = 60
HERE = os.path.dirname(os.path.abspath(__file__))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
data = lambda n: os.path.join(HERE, 'data', n)
PIN = Q(376669, 100000000)     # ordinary BIT saving of the open #6726 two-fragment admission (retained/bit/FRAGMENT-BIT-ADMISSION.json)
def ldmod(path, name):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); sys.modules[name] = m; s.loader.exec_module(m); return m

# ---- (1) replay of the word -------------------------------------------------------------------
W = json.load(gzip.open(data('word.json.gz'), 'rt'))
def span(b):
    s = {0}
    for v in b:
        if not (isinstance(v, int) and 0 < v < 512 and v not in s): raise SystemExit('FAIL dependent basis')
        s |= {x ^ v for x in s}
    return frozenset(s)
fr = W['frames']; sp = [span(b) for b in fr]; dim = [len(b) for b in fr]
n = len(W['initial']); NO = W['owned_fields']; NR = n + NO
cur = list(W['initial']) + [None] * NO; row = [({r: Q(1)} if r < n else {}) for r in range(NR)]
owned = set(); viol = Counter(); owned_up = Counter(); up_idx = []; paid = Counter(); peak = life = dirty = 0; maxq = Q(0); logq = 0.0; pmax = Q(0); dmaxb = 0; nbits = dbits = 0
dy = lambda q: q.denominator & (q.denominator - 1) == 0
for i, e in enumerate(W['program']):
    op, r = e[0], e[1]
    if op == 'MOVE':
        _, r, a, b, pv = e
        if cur[r] != a or (r in owned) != bool(pv): viol['transport source or ownership'] += 1
        if pv:
            if sp[a] < sp[b]: owned_up[dim[b] - dim[a]] += 1; up_idx.append(i)
            elif not sp[b] < sp[a]: viol['owned move not nested'] += 1
        elif not sp[a] < sp[b]: viol['public move not strictly ascending'] += 1
        paid[abs(dim[b] - dim[a])] += 1; cur[r] = b
    elif op == 'INIT':
        if not (r >= n and r not in owned): viol['INIT'] += 1
        owned.add(r); life += 1; peak = max(peak, len(owned)); cur[r] = e[2]; row[r] = {}
    elif op == 'CLEAR':
        if not (r in owned and cur[r] == e[2]): viol['CLEAR'] += 1
        dirty += bool(row[r]); owned.discard(r); cur[r] = None; row[r] = {}
    else:
        q = Q(e[2] if op == 'SCALE' else e[3]); f = e[-1]
        if q == 0 or not dy(q) or not abs(q) + 1 < 2 ** 16: viol['coefficient alphabet'] += 1
        maxq = max(maxq, abs(q)); nbits = max(nbits, abs(q.numerator).bit_length()); dbits = max(dbits, q.denominator.bit_length())
        if op != 'SCALE': logq += math.log2(1 + float(abs(q)))
        if op == 'SCALE':
            if cur[r] != f or abs(q.numerator) & (abs(q.numerator) - 1): viol['SCALE'] += 1
            row[r] = {k: v * q for k, v in row[r].items()}
            for v in row[r].values():
                if abs(v) > pmax: pmax = abs(v)
                if v.denominator.bit_length() > dmaxb: dmaxb = v.denominator.bit_length()
        else:
            s = e[2]
            if not (cur[r] == f == cur[s] and s != r): viol['common chart'] += 1
            if op == 'COPY':
                if not (r in owned and not row[r]): viol['COPY'] += 1
                row[r] = {}
            for k, v in row[s].items():
                t = row[r].get(k, 0) + q * v
                if t:
                    row[r][k] = t
                    if abs(t) > pmax: pmax = abs(t)
                    if t.denominator.bit_length() > dmaxb: dmaxb = t.denominator.bit_length()
                else: row[r].pop(k, None)
need(not owned and cur[:n] == W['final'], 'owned all cleared; final frames as declared')
need(dict(viol) == {}, 'frame law, common chart, dyadic alphabet, public ascent: no violation beyond the declared one')
up_mass = sum(k * v for k, v in owned_up.items())
need(up_mass == 56 and sum(owned_up.values()) == 23, 'declared OWNED UP: %d events, rank mass %d (convention: owned ascent)' % (sum(owned_up.values()), up_mass))
def verifier(name):
    return subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, name), data('word.json.gz')], capture_output=True, text=True).stdout
os_, or_ = verifier('verify_strict.py'), verifier('verify_relaxed.py')
rej = [int(x) for x in os_.split('indices')[1].split('\n')[0].split()]
need(os_.strip().endswith('REJECTED_STRICT') and rej == up_idx and "['move nesting']" in os_, 'rejection control: the strict (predecessor) verifier rejects this word at exactly the %d owned-ascent events and nothing else' % len(rej))
need(or_.strip().endswith('ACCEPTED_RELAXED'), 'relaxed verifier (only the owned-move direction rule changed, paid |delta dim| either way) accepts every event')
H = W['hosted']; al, be = Q(H['alpha']), Q(H['beta']); a2, b2 = Q(H['alpha2']), Q(H['beta2'])
live = W['live']; X = set(live); Y = {r + 112 for r in live}; X2 = H['X2']; Y2 = H['Y2']; X2s = set(X2); Y2s = set(Y2)
need(H['mode'] == 'decoupled-t0' and (al, be, a2, b2) == (0, 1, -1, 0) and len(live) == len(W['ports']) == len(X2) == len(Y2) == 104 and not ((X2s | Y2s) & (X | Y)) and len(X2s | Y2s) == 208,
     'two main planes per port: plane 1 (alpha,beta)=(%s,%s), plane 2 (alpha2,beta2)=(%s,%s), t = 0 in both; 104 ports, 4 distinct main registers per port' % (al, be, a2, b2))
x2of = dict(zip(X2, Y2)); bad = 0
for r in range(NR):
    if r >= n: ex = {}
    elif r in X: ex = {r: Q(1), r + 112: al} if al else {r: Q(1)}
    elif r in Y: ex = {r - 112: be, r: 1 + al * be}
    elif r in X2s: ex = {r: Q(1), x2of[r]: a2}
    elif r in Y2s: ex = {r: Q(1)} if b2 == 0 else None
    else: ex = {r: Q(1)}
    bad += row[r] != ex
need(bad == 0, 'endpoint exact on all %d public and owned rows: X=x, Y=x+y, X2=x2-y2, Y2=y2, helpers identity, owned empty' % NR)
for r, q, x2, y2 in zip(live, W['ports'], X2, Y2):
    if fr[W['initial'][r]] != [q] or dim[W['final'][r]] != 9 or dim[W['initial'][r + 112]] != 0 or sp[W['final'][r + 112]] != frozenset(x for x in range(512) if not (x & q).bit_count() % 2): raise SystemExit('FAIL main frames')
    if W['initial'][x2] != W['initial'][r] or W['final'][x2] != W['final'][r] or W['initial'][y2] != W['initial'][r + 112] or W['final'][y2] != W['final'][r + 112]: raise SystemExit('FAIL second main frames')
need(True, '104 literal central ports; the second mains carry the same initial and final frame labels as the first mains (declared: same-label second mains)')
main = X | Y | X2s | Y2s
hel = Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in main)
need(min(hel) > 0 and all(sp[W['initial'][r]] < sp[W['final'][r]] for r in range(n) if r not in main), 'every helper strictly ascends (rank > 0); %d helpers, %d mains, %d public' % (sum(hel.values()), len(main), n))
print('  events', len(W['program']), 'public', n, 'owned roles', NO, 'peak owned', peak, 'owned lifetimes', life, 'dirty owned erasures', dirty, 'max |coefficient|', maxq)
need(peak == 30, 'peak owned fields 30 (#6889: 25)')

# ---- (2) the root -----------------------------------------------------------------------------
RC = ldmod(os.path.join(HERE, 'root_check.py'), 'rootcheck')
R = json.load(open(data('root.json')))
need(RC.run(R) == [], 'root checker: two #6833 chain roots regenerated (21/21 units of each), cross Gram 0, SPEC-level identities, each stage variable once and affine')
Rm = copy.deepcopy(R); Rm['X'][5][3] = str(Q(Rm['X'][5][3]) + 1)
need(RC.blocks(Rm) != [] and RC.run(Rm) != [], 'control: a wrong X entry in the root FAILS the block identities (%s)' % RC.blocks(Rm)[:1])
Rm = copy.deepcopy(R); Rm['Y'][30][23] = str(Q(Rm['Y'][30][23]) - 1)
need(RC.blocks(Rm) != [], 'control: a wrong Y entry in chain B FAILS the block identities (%s)' % RC.blocks(Rm)[:1])
Rm = copy.deepcopy(R); Rm['X'][7], Rm['X'][9] = Rm['X'][9], Rm['X'][7]
need(RC.run(Rm) != [], 'control: two unit rows swapped in chain A FAIL')
ST = R['stages']
mask_inc = lambda c, RR: [int(c in set(s['mask'])) for s in RR['stages']]

# ---- (3) the caller -----------------------------------------------------------------------------
C = json.load(open(data('caller.json')))
pM = 2147483629
IM = next(pow(g, (pM - 1) // 4, pM) for g in range(2, 99) if pow(g, (pM - 1) // 2, pM) == pM - 1); HALF = (pM + 1) // 2
fm = lambda x: (lambda f: f.numerator % pM * pow(f.denominator, pM - 2, pM) % pM)(Q(x))
def replay(Wc, qv, Dv, a2_):
    n_ = Wc['roles']; Rm_ = [[int(i == j) for j in range(n_)] for i in range(n_)]; qi = pow(qv, pM - 2, pM); seen = []
    for e in Wc['events']:
        o = e[0]
        if o == 'ADD': Rm_[e[1]] = [(a_ + fm(e[3]) * b_) % pM for a_, b_ in zip(Rm_[e[1]], Rm_[e[2]])]
        elif o == 'SCALE': c = fm(e[2]); Rm_[e[1]] = [a_ * c % pM for a_ in Rm_[e[1]]]
        elif o == 'SWAP': Rm_[e[1]], Rm_[e[2]] = Rm_[e[2]], Rm_[e[1]]
        elif o == 'QUERY': c = pow(qv, e[3] % 4, pM); Rm_[e[1]] = [(a_ + c * b_) % pM for a_, b_ in zip(Rm_[e[1]], Rm_[e[2]])]
        elif o == 'LAMBDA':
            s_ = e[2]; c = ((1 + s_ * IM) * HALF + (1 - s_ * IM) * HALF * qv * qv) % pM; Rm_[e[1]] = [a_ * c % pM for a_ in Rm_[e[1]]]
        elif o == 'IDLE_ONE':
            c = 1
            for k in e[2]: c = c * Dv[k] % pM
            Rm_[e[1]] = [a_ * c % pM for a_ in Rm_[e[1]]]
        elif o == 'HOST2':
            st, src, dst, x2, y2 = e[1:]; d = Dv[st]; seen.append(st)
            Rm_[dst] = [(a_ + qi * b_) % pM for a_, b_ in zip(Rm_[dst], Rm_[src])]
            Rm_[x2] = [(a_ + fm(a2_) * qv % pM * b_) % pM for a_, b_ in zip(Rm_[x2], Rm_[y2])]
            for r_ in (src, dst, x2, y2): Rm_[r_] = [a_ * d % pM for a_ in Rm_[r_]]
        else: raise SystemExit('FAIL unknown caller event ' + o)
    if sorted(seen) != list(range(1, Wc['stages'] + 1)): return 10 ** 6
    bad_ = 0
    for i in range(n_):
        c = pow(qv, Wc['diagonal'][i][0] % 4, pM)
        for k, bit in enumerate(Wc['diagonal'][i][2:]):
            if bit: c = c * Dv[k + 1] % pM
        bad_ += sum(Rm_[i][j] != (c if i == j else 0) for j in range(n_))
    return bad_
need(C['roles'] == 40 and C['stages'] == 18 and Q(C['alpha2']) == a2 and Q(C['beta2']) == b2 and sum(e[0] == 'HOST2' for e in C['events']) == 18, 'caller: 40 roles, 18 HOST2 events (one native contact per stage serving both chains), plane parameters equal the word\'s')
need(all(C['diagonal'][c][2:] == mask_inc(c, R) for c in range(40)), 'caller target exponents equal the root mask incidence (field by field, stage by stage; roles 0-19 chain A, 20-39 chain B)')
rnd = random.Random(5); tot = cnt = 0
for qv in (1, IM, pM - 1, pM - IM):
    for _ in range(2):
        Dv = {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}; tot += replay(C, qv, Dv, a2); cnt += 1
need(tot == 0, 'composition: the caller with the shared native replays to the diagonal root target at all four central characters, random stage values (%d evaluations, 0 bad of 1600 coefficients each)' % cnt)
Dv = {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}
muts = []
Cm = copy.deepcopy(C); muts.append(replay(Cm, IM, Dv, Q(1)))                                   # wrong alpha2
Cm = copy.deepcopy(C); del Cm['events'][next(i for i, e in enumerate(Cm['events']) if e[0] == 'IDLE_ONE')]; muts.append(replay(Cm, IM, Dv, a2))
Cm = copy.deepcopy(C); del Cm['events'][next(i for i, e in enumerate(Cm['events']) if e[0] == 'QUERY')]; muts.append(replay(Cm, IM, Dv, a2))
Cm = copy.deepcopy(C); i = next(i for i, e in enumerate(Cm['events']) if e[0] == 'HOST2'); Cm['events'][i - 1][2] *= -1; muts.append(replay(Cm, IM, Dv, a2))   # one contact LAMBDA flipped
need(all(muts), 'controls: wrong alpha2, a deleted idle, a deleted thin query, a flipped LAMBDA at one contact are all rejected by the replay (bad %s)' % muts)
Cm = copy.deepcopy(C); Cm['diagonal'][3][2 + 4] ^= 1
need(replay(Cm, IM, Dv, a2) > 0 and Cm['diagonal'][3][2:] != mask_inc(3, R), 'control: a wrong mask bit in the caller target fails the replay and the mask comparison')
need(all(C['diagonal'][c][2:] == mask_inc(c, Rm) for c in range(40)), 'note (asserted): the composition reads the root only through the masks, so a wrong X or Y entry does not fail it; the block identities above do')

# ---- (4) invoice ---------------------------------------------------------------------------------
def kappa(T, P):
    rs = sorted(set(T) | set(P)); ln = {r: D(r).ln() for r in rs}
    e = lambda k: sum((D(T.get(r, 0)) - D(P.get(r, 0))) * (ln[r] * (1 - k)).exp() for r in rs)
    lo, hi = D('1e-6'), D('0.05')
    for _ in range(220):
        m = (lo + hi) / 2
        if e(m) > 0: lo = m
        else: hi = m
    return lo
def root_fields(RR):
    S_ = RR['stages']; Xr = RR['X']; Yr = RR['Y']; F = []
    for c in range(RR['n']):
        ms = [k for k, s_ in enumerate(S_) if c in set(s_['mask'])]
        F.append((ms, [k for k in ms if any(Q(Yr[u][c]) != 0 for u in S_[k]['units'])]))
    dot = lambda a_, b_: sum(Q(u) * Q(v) for u, v in zip(a_, b_) if Q(u) and Q(v))
    planes = []
    for s_ in S_:
        u, v = s_['units']; planes.append(2 if dot(Yr[u], Xr[v]) == 0 and dot(Yr[v], Xr[u]) == 0 else 1)
    return F, planes, RR['N'] - sum(len(s_['units']) for s_ in S_)
def outer(F, planes, thin, nst=18):
    T = Counter(); P = Counter(); hc = Counter()
    for ms, host in F:
        T[8 * len(ms) + 1] += 104
        for k in host: hc[k] += 1
        run = 0; prev = None
        for k in ms:
            if k in host:
                if run: P[8 * run] += 104
                run = 0; prev = None; continue
            if prev is not None and k == prev + 1: run += 1
            else:
                if run: P[8 * run] += 104
                run = 1
            prev = k
        if run: P[8 * run] += 104
    for k in range(nst):
        if hc[k] > 2 * planes[k]: P[8] += 104 * (hc[k] - 2 * planes[k])
    P[1] += 104 * thin
    return T, P
def invoice(hel_, paid_, RR):
    F, planes, thin = root_fields(RR); T, P = outer(F, planes, thin)
    for r, k in hel_.items(): T[r] += 18 * k
    for r, k in paid_.items(): P[r] += 18 * k
    return T, P
def census(Wx):
    nx = len(Wx['initial']); lx = set(Wx['live']); mx = lx | {r_ + 112 for r_ in lx}
    if Wx.get('hosted', {}).get('X2'): mx |= set(Wx['hosted']['X2']) | set(Wx['hosted']['Y2'])
    dx = [len(b_) for b_ in Wx['frames']]
    return (Counter(dx[Wx['final'][r_]] - dx[Wx['initial'][r_]] for r_ in range(nx) if r_ not in mx), Counter(abs(dx[e_[3]] - dx[e_[2]]) for e_ in Wx['program'] if e_[0] == 'MOVE'))
bi = json.load(open(data('base_invoice.json')))
T0 = Counter({int(k): v for k, v in bi['targets'].items()}); P0 = Counter({int(k): v for k, v in bi['paid'].items()})
chain = [(list(range(18)), list(range(18)))] + [(list(range(i, 9)), [i]) for i in range(9)] + [(list(range(9, 10 + m)), [9 + m]) for m in range(9)] + [([], [])]
Tc_, Pc_ = outer(chain, [1] * 18, 3)
Tb, Pb = Counter(Tc_), Counter(Pc_)
for r_, k_ in bi['helpers'].items(): Tb[int(r_)] += 18 * k_
for r_, k_ in bi['local_paid'].items(): Pb[int(r_)] += 18 * k_
need(+Tb == T0 and +Pb == P0, 'control: the same code rebuilds the #6833 invoice term for term')
kb = kappa(T0, P0)
need(abs(kb - D(bi['kappa_literal'])) < D('1e-17'), 'control: #6833 kappa %s' % str(kb)[:20])
Fn, plan_n, thin_n = root_fields(R)
need(all(p_ == 2 for p_ in plan_n) and thin_n == 6, 'root: every stage holds two separate planes (units of the two chains have zero cross terms); 6 thin units')
To, Po = outer(Fn, plan_n, thin_n)
need(To == Counter({r_: 2 * v_ for r_, v_ in Tc_.items()}) and Po == Counter({r_: 2 * v_ for r_, v_ in Pc_.items()}), 'the root part of the invoice is exactly twice the #6833 chain root part (no root discount: nothing is fused, each chain pays its own idles)')
Tn, Pn = invoice(hel, paid, R)
kn = kappa(Tn, Pn)
need(abs(kn - D('0.00351406186742169')) < D('1e-16'), 'new kappa %s' % str(kn)[:22])
Wp = json.load(gzip.open(data('prior_word_6889.json.gz'), 'rt')); Rp = json.load(open(data('prior_root_6889.json')))
hp, pp = census(Wp); Tp, Pp = invoice(hp, pp, Rp); kp = kappa(Tp, Pp)
need(abs(kp - D('0.00345694177515779')) < D('1e-17'), 'control: the #6889 word through its own hosted root and the same code gives %s (its crossing)' % str(kp)[:22])
print('  gain over #6889: %.4f%% (exactly kappa_new / kappa_6889 - 1 = %s)' % (100 * float(kn / kp - 1), str(100 * (kn / kp - 1))[:9]))
S = sum(r * (Tn.get(r, 0) - Pn.get(r, 0)) for r in set(Tn) | set(Pn))
need(S == 1520, 'rank-mass surplus S = %d (104*34 - 36*56, net of the 56 owned-ascent mass per call)' % S)
Tc = Counter(); Pc = Counter(); nh = 0
for e in C['events']:
    if e[0] == 'HOST2': Tc.update(hel); Pc.update(paid); nh += 1
    elif e[0] == 'QUERY': Pc[1] += 104
    elif e[0] == 'IDLE_ONE': Pc[8 * len(e[2])] += 104
    elif e[0] == 'IDLE': raise SystemExit('FAIL unexpected IDLE')
for tt in C['diagonal']: Tc[int(tt[0] % 2) + 8 * sum(tt[2:])] += 104
need(nh == 18 and +Tc == +Tn and +Pc == +Pn, 'emitted caller events recount the same invoice (18 native calls, 6 thin queries, one-site idles)')
need(sum(e[0] == 'LAMBDA' for e in C['events']) == 124, 'LAMBDA events in the caller: 124 (62 per chain)')
lam_neg = S - 124 * 104
need(lam_neg < 0, 'review question, stated plainly: if each LAMBDA had to be paid as a rank-1 job per port, S = %d - 124*104 = %d < 0 and no crossing exists (#6889: 1520 - 82*104 = %d); kappa rests on pricing LAMBDA as ordinary work, as in every caller of this line' % (S, lam_neg, 1520 - 82 * 104))

# ---- (5) raw bound, growth, alphabet --------------------------------------------------------------
def swaps(sel):
    wanted = set(range(len(sel))); return len(list(zip(sorted(set(sel) - wanted), sorted(wanted - set(sel)))))
amb = C['ambient_rank']; roles = C['roles']; evs = C['events']; main_maps = 0
for role, (qp, zero, *sel) in enumerate(C['diagonal']):
    axes = ([0] if qp else []) + [x_ for st, y_ in enumerate(sel, 1) if y_ for x_ in range(9 + 8 * (st - 1), 9 + 8 * st)]
    main_maps += 104 * (2 * swaps(axes) + 2 * bool(qp) + int(qp == -1))
idle_ex = qmaps = 0
for e in evs:
    if e[0] == 'IDLE_ONE': idle_ex += 104 * 2 * swaps([x_ for st in e[2] for x_ in range(9 + 8 * (st - 1), 9 + 8 * st)])
    elif e[0] == 'QUERY': qmaps += 104 * (2 + int(e[3] == -1))
rest = 32 * roles * 104 * len(evs) + sum(e[0] == 'QUERY' for e in evs) * 16 * 104 + roles * 104 * 26 + 1000 * main_maps + 1000 * idle_ex + 1000 * qmaps
allow = upper = 0
for e in W['program']:
    if e[0] in ('INIT', 'CLEAR'): allow += 2
    elif e[0] == 'SCALE':
        q = Q(e[2]); a_, d_ = abs(q.numerator), q.denominator
        allow += 2 * (abs(a_.bit_length() - d_.bit_length()) + int(q < 0)); upper += 4 * (a_.bit_length() + d_.bit_length() + 1)
    elif e[0] in ('ADD', 'COPY'):
        q = Q(e[3]); a_, d_ = abs(q.numerator), q.denominator
        allow += 2 * (3 + a_.bit_length() - 1 + bin(a_).count('1') + d_.bit_length() - 1); upper += 4 * (a_.bit_length() + bin(a_).count('1') + d_.bit_length() + 1)
routes = (sum(paid.values()) + 2 * sum(hel.values()) + 416 + 8 * 104 + 4 * life) * 1000      # main boundary terms doubled for the second planes
per_call = allow + routes; per_up = upper + routes
raw_lit, raw_act, raw_rev = 18 * 10 ** 7 + rest, 18 * per_call + rest, 18 * per_up + rest
print('  raw pieces: caller+thin+outputs+idle adapters+query adapters = %d; per call (word scalar + routes) = %d (allowance) or %d (reviewed upper) against the displayed 10^7' % (rest, per_call, per_up))
need((raw_lit, raw_act, raw_rev) == (963421184, 965490968, 971071328) and max(raw_lit, raw_act, raw_rev) < 10 ** 9, 'raw bound, all three definitions below 10^9: literal %d, actual per-call work %d, reviewed scalar upper %d (margins %d, %d, %d); the reviewed-upper line is under 10^9 for the first time in this line of work' % (raw_lit, raw_act, raw_rev, 10 ** 9 - raw_lit, 10 ** 9 - raw_act, 10 ** 9 - raw_rev))
Rm_paid = sum(r_ * v_ for r_, v_ in Pn.items())
print('  CONSTANT SUBSTITUTION (FINITE-PRECOMPILATION.md:278-283): events %d; scalar allowance %d; reviewed scalar upper %d; routes %d; per call %d or %d; caller envelope %d; raw upper %d (allowance) or %d (reviewed upper); paid rank mass R = %d; growth bound 2^(raw + R f) = 2^(%d + %d f) on the conservative count' % (len(W['program']), allow, upper, routes, per_call, per_up, 32 * roles * 104 * len(evs), raw_act, raw_rev, Rm_paid, raw_rev, Rm_paid))
src_ep = open(os.path.join(HERE, 'retained', 'runtime', 'endpoint.py')).read()
need(not any(t_ in src_ep for t_ in ('10**9', '10 ** 9', '10**7', '10 ** 7', '1e9')), 'the outer ledger source contains no scalar-work or 10^9 term')
def logsum(Wx): return sum(math.log2(1 + float(abs(Q(e_[3])))) for e_ in Wx['program'] if e_[0] in ('ADD', 'COPY'))
l89 = logsum(Wp)
print('  GROWTH (productive-controller PROOF.md section 5: fewer than 26000 events, |q|+1 < 2^16, local bound 2^(16*26000) = 2^416000):')
print('    events %d (#6889 word 164533), both above the 26000 of that text; sum of log2(1+|q|) over the ADD coefficients %d (#6889 %d) against 416000; peak |row entry| on any prefix 2^%.1f; peak row denominator 2^%d; coefficient bits numerator <= %d, denominator <= %d; largest |q| %s' % (len(W['program']), round(logq), round(l89), math.log2(float(pmax)), dmaxb, nbits, dbits, maxq))
need(round(logq) == 27718 and round(l89) == 282880 and maxq == 45, 'sum of log2(1+|q|): %d here and %d in the #6889 word, both below 416000; largest |q| %s, far below 2^16' % (round(logq), round(l89), maxq))
oy = [i_ for i_, e_ in enumerate(W['program']) if e_[0] == 'ADD' and e_[1] >= n and e_[2] in set(Y2)]
oyY = [i_ for i_, e_ in enumerate(W['program']) if e_[0] == 'ADD' and e_[1] >= n and e_[2] in Y]
need(oy == [14676, 14744, 14746, 14768, 14770, 14774, 14776, 18579] and oyY == [], 'owned registers reading a main Y2 register: 8 events %s (declared with A6; #6889 had one read of Y, this word none of Y); peak owned fields %d' % (oy, peak))
big_ = sum(1 for e_ in W['program'] if e_[0] in ('ADD', 'COPY') and abs(Q(e_[3])) >= 2 ** 12)
need(big_ == 0 and maxq + 1 < 2 ** 16, 'alphabet: no ADD has |q| >= 2^12 (largest %s)' % maxq)

# ---- (6) outer conditions ----------------------------------------------------------------------
E, SE, OUT = ldmod(os.path.join(HERE, 'retained', 'runtime', 'intervals.py'), 'intervals'), ldmod(os.path.join(HERE, 'retained', 'runtime', 'second_intervals.py'), 'second_intervals'), ldmod(os.path.join(HERE, 'retained', 'runtime', 'endpoint.py'), 'endpoint')
BITF = json.load(open(os.path.join(HERE, 'retained', 'bit', 'FRAGMENT-BIT-ADMISSION.json')))
need(hashlib.sha256(open(os.path.join(HERE, 'retained', 'bit', 'FRAGMENT-BIT-ADMISSION.json'), 'rb').read()).hexdigest() == '86955dcd74bc3fa1a940419474d45054fa7b0366b71b242568680366923d9311' and BITF['status'] == 'PASS_TWO_FRAGMENTS_BIT_ORDINARY_00376669' and Q(BITF['ordinary_admitted']) == PIN, 'BIT pin %s = ordinary_admitted of the pinned #6726 admission file (status %s); not re-derived here' % (float(PIN), BITF['status']))
KAPPA, TESTED = Q('.00351406'), Q('.00351406007')
LOW, UP = Q('.003514061867421'), Q('.003514061867422')
Tq = Counter({r: v for r, v in Tn.items() if v}); Pq = Counter({r: v for r, v in Pn.items() if v})
need(KAPPA < TESTED < LOW < UP and TESTED < PIN and Q(BITF['raw_crossing'][0]) > Q(BITF['raw_tested']) > PIN, 'claim %s, tested %s, both strictly below the raw crossing %s; BIT side: raw crossing > raw tested saving > pin > tested price' % (float(KAPPA), float(TESTED), str(kn)[:19]))
print('  BIT margins: pin - tested complex price = %.3e; raw BIT tested saving - pin = %.1e; raw BIT crossing lower bound - raw BIT tested saving = %.3e' % (float(PIN - TESTED), float(Q(BITF['raw_tested']) - PIN), float(Q(BITF['raw_crossing'][0]) - Q(BITF['raw_tested']))))
for name, k, pos in (('lower', LOW, 1), ('upper', UP, -1), ('tested', TESTED, 1)):
    a, b = E.moment(Tq, 1 - k), E.moment(Pq, 1 - k); first = (a[0] - b[1], a[1] - b[0])
    tl, th = SE.moment(Tq, k); pl, ph = SE.moment(Pq, k); second = (tl - ph, th - pl)
    need((first[0] > 0 and second[0] > 0) if pos > 0 else (first[1] < 0 and second[1] < 0), 'both interval engines (rational interval arithmetic, no Decimal): sign of the margin at the %s price endpoint' % name)
signed = Counter(Tq); signed.subtract(Pq); d = Q(0)
for r, c in signed.items():
    lg = E.log_bounds(r); d -= c * (E.mul(E.power(r, 1 - PIN), lg)[0] if c >= 0 else r * lg[1])
need(d < 0, 'unique raw crossing through the BIT pin (derivative upper bound negative at the pin)')
cutoff, floor, power, offset = 11, 12, 1920, Q(1, 7); LP = 2157
tt_ = 1 - TESTED; target, paidm = E.moment(Tq, tt_), E.moment(Pq, tt_)
alpha = E.divide(paidm, target); gamma = E.divide(E.moment(Pq, tt_ + offset), E.mul(E.power(cutoff, offset), target))
delta = E.divide((Q(sum(Tq.values()) * floor),) * 2, E.mul(E.power(cutoff, TESTED), target))
reserve, decay = Q(1, 10 ** 27), Q(31, 32)
need(alpha[1] < 1 - reserve and gamma[1] < decay and delta[1] < decay, 'tail ratios (interval engine): alpha %.12f gamma %.4f delta %.4f (cutoff 11, floor 12, offset 1/7, power 1920)' % (float(alpha[1]), float(gamma[1]), float(delta[1])))
normalized = 1 / (1 + power * reserve) + 4 * decay ** power
need(normalized < 1, 'composite bound (predecessor pricing.py:211): 1/(1+power*reserve) + 4*decay^power < 1 at power 1920 (excess over the first term %.2e)' % float(4 * decay ** power))
maxT = max(Tq); carrier = max(maxT, int(C['ambient_rank']))     # the compiler fit m*c <= N (FP:111-114) is on the literal carrier, 9 base rows + 8 per stage = 153, not on the largest target rank 145
quarter = E.power(carrier, Q(power, 4) * TESTED); factor = E.mul(E.mul(quarter, quarter), E.mul(quarter, quarter))
eta = E.scale(E.divide((Q(1), Q(1)), factor), tt_)
need(eta[0] > Q(63, 64) ** LP and factor[1] < 2 ** LP and cutoff ** 64 < floor ** 63 and 2 * (cutoff ** power) ** 64 <= (carrier ** power) ** 63, 'compiler complement capacity and shifted exits at logarithm power %d on the literal carrier %d (the largest target rank is %d; an earlier version used 145 and was too low)' % (LP, carrier, maxT))
lp_ = LP
while eta[0] > Q(63, 64) ** (lp_ - 1): lp_ -= 1
need(lp_ == 2156 and Q(63, 64) ** 2134 > eta[0] and Q(63, 64) ** 2155 > eta[0], 'logarithm power: on the literal carrier 153 the smallest admissible value at this price is %d, written as %d (the value 2134 written by an earlier version, computed with the largest target rank 145 in place of the carrier, and 2155 both FAIL; it is a free parameter, LOG-MAJORANT.md:110-122)' % (lp_, LP))
gap = (TESTED - KAPPA) / 7; need(gap.numerator == 1, 'compiler grid: (tested-kappa)/7 = %s' % gap)
step = gap.denominator
wins = lambda j: (step * j + 1) ** LP < 2 ** j
lo_, hi_ = 1, 2
while not wins(hi_): lo_, hi_ = hi_, 2 * hi_
while hi_ - lo_ > 1:
    m = (lo_ + hi_) // 2
    if wins(m): hi_ = m
    else: lo_ = m
need(step * hi_ > 8 * power and wins(hi_) and not wins(hi_ - 1), 'explicit uniform threshold H=%d (logarithm power %d)' % (step * hi_, LP))
params = {'kappa': KAPPA, 'tested_saving': TESTED, 'complex_uniform_saving': KAPPA + 6 * gap, 'b': KAPPA + 5 * gap, 'a': KAPPA + 4 * gap, 'q': KAPPA + 3 * gap, 'bit_saving': PIN,
          'epsilon': 1 - gap, 'beta': 1 - 3 * gap, 'r0': gap / 10, 'stop': gap, 'layout': gap, 'd': gap}
led = OUT.ledger(params); led['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta'] * (1 - Q(1, 250))
need(len(led['strict_checks']) == 54 and len(led['functional_checks']) == 4 and all(v > 0 for k in ('strict_checks', 'functional_checks') for v in led[k].values()), 'outer inventory: 54 strict and 4 functional inequalities all positive at the pin')
PINS = [('main admitted', Q('.0034'), False), ('.00343', Q('.00343'), False), ('main ordinary stock', Q('.0034363538396'), False), ('#5421', Q('.00344412'), False),
        ('#4760', Q('.0034597'), False), ('#4814', Q('.003475458'), False), ('#5512', Q('.003483969976'), False), ('#6726 (the pin used)', PIN, True)]
for lab_, pin_, want_ in PINS:      # the ledger needs bit_saving > kappa + 4 gap = .00351406004
    L_ = OUT.ledger(dict(params, bit_saving=pin_)); L_['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta'] * (1 - Q(1, 250))
    ok_ = TESTED < pin_ and all(v > 0 for kk in ('strict_checks', 'functional_checks') for v in L_[kk].values())
    need(ok_ == want_, 'ledger at the BIT saving %s (%s): %s%s' % (float(pin_), lab_, 'all 54 + 4 positive' if ok_ else 'fails', ', margin over the tested price %.3e' % float(pin_ - TESTED) if ok_ else ''))
need(any(v <= 0 for kk in ('strict_checks', 'functional_checks') for v in OUT.ledger(dict(params, bit_saving=params['a'] - Q(1, 10 ** 12)))[kk].values()), 'control: a BIT saving just below kappa + 4 gap (%s) is rejected' % float(params['a']))
plus = [(7, 1), (3, 1), (5, 1)]; minus = [(9, 1), (4, 1), (1, 2)]
def dlog(terms):
    lo = hi = Q(0)
    for x, c in terms:
        a_ = E.mul((Q(x), Q(x)), E.log_bounds(x)); lo += c * a_[0]; hi += c * a_[1]
    return lo, hi
def d2log(terms):
    hi = Q(0)
    for x, c in terms:
        a_ = E.mul(E.mul((Q(x), Q(x)), E.log_bounds(x)), E.log_bounds(x)); hi += c * a_[1]
    return hi
dpl, dmi = dlog(plus), dlog(minus); d1 = (dpl[0] - dmi[1], dpl[1] - dmi[0]); Mq = d2log(plus) + d2log(minus)
need(d1[1] + PIN * Mq < 0, 'input-lift saving lemma of #6833 (pricing.py:128-156), cap moved to the pin: g prime negative on 1-pin..1 (its crude bound holds to about .0037765)')
for nm, k_ in (('claim', KAPPA), ('tested', TESTED)):
    tl_ = 1 - k_; gl = sum(c * E.power(x, tl_)[0] for x, c in plus) - sum(c * E.power(x, tl_)[1] for x, c in minus)
    need(gl > 0 and k_ * (-d1[1]) - k_ * k_ * Mq / 2 > 0, 'input-lift saving positive at the %s price' % nm)

# ---- declared departures -----------------------------------------------------------------------
print('DEPARTURES (class; exact count here):')
for cls, what in (
    ('new family: reducible root', 'the root is literally two #6833 chain roots on orthogonal coordinates, t = 0 at every stage, Gram digraph with two components; the family lines t != 0 (the hosted family root check line "hosted t not 0, not -1"), alpha and beta dyadic units, and "Gram digraph strongly connected" (added by the #6883 root_check.py, not a SPEC line) do not hold. What the outer theorem requires is the unit identity and whole-job credit, which root_check.py re-proves (SPEC-level lines all pass).'),
    ('new event', 'HOST2: one native contact per stage that serves both chains (18 events, forward contact q^-1 on the first plane, q on the second, 124 LAMBDA events with the second chain flipped).'),
    ('new form', 'same-label second mains: X2 and Y2 carry the same initial and final frame labels as X and Y (asserted above); 4 main registers per port, 416 mains; per-port boundary terms are doubled in the raw count.'),
    ('convention (A6, load-bearing)', 'owned ascent: 23 owned rises (rank mass 56) against native.py:55 / local.py:126; peak owned 30; 8 owned reads of Y2 (events %s). No ascent, no word.' % oy),
    ('verifier', 'endpoint literal native.py:75-77 / local.py:168: the target is X=x, Y=x+y, X2=x2-y2, Y2=y2 on 104 ports.'),
    ('verifier', 'events %d, public %d, owned roles %d, lifetimes %d, peak owned %d against local.py:52,54,103 and pricing.py:84-87 literals; per-call scalar work %d against the displayed 10^7 (pricing.py:93).' % (len(W['program']), n, NO, life, peak, per_call)),
    ('convention', 'LAMBDA (124 events) and IDLE_ONE (32 events) inherited from the open callers #6726 and #6716/#6763; not on main; the price of LAMBDA is a review question (above).'),
    ('assumption', 'dirty owned erasure (%d erasures): the owned_erasure assumption, unchanged.' % dirty)):
    print('  [%s] %s' % (cls, what))
need(True, 'departures listed')
print('PASS_P104_TWO_CHAIN_SHARED_NATIVE')
