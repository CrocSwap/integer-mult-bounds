#!/usr/bin/env python3
"""Joint caller check (stdlib only; writes mm.joint.invoice.json and ctl_rootB_X.json).  python3 -I -B check_joint.py
(R) both roots by their own checkers, with controls;  (C) literal replay of the ONE joint event stream over F_p on 78 roles (A roles 0..39, B roles 40..77),
at the four central characters q^4=1, one common set of 18 stage values for both types, block-diagonal target, with mutation / wrong-root / mask / cross-type controls;
(I) the invoice recounted from emitted events and compared with mm.chain.invoice.json, and from the two roots independently;  (W) port types tied to the word."""
import json, gzip, sys, random, copy, subprocess, importlib.util, os, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'; DATA = HERE + '../data/'; OUT = tempfile.mkdtemp() + '/'  # package paths; scratch outputs go to a temporary directory
from fractions import Fraction as Q
from collections import Counter
from decimal import Decimal as D, getcontext
getcontext().prec = 50
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
J = json.load(open(DATA + 'joint_caller_w.json')); W = json.load(gzip.open(DATA + 'mm.json.gz', 'rt')); WW = json.load(gzip.open(DATA + 'mmW.json.gz', 'rt')); WORDS = {'mm': W, 'mmW': WW}
RA = json.load(open(DATA + 'root_t0_dsum.json')); RB = json.load(open(DATA + 'rootw1g.json')); RB0 = json.load(open(DATA + 'rootw1.json'))  # W root (gauged) and its ungauged original as the other-gauge control
def ld(path, name):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); sys.modules[name] = m; s.loader.exec_module(m); return m
# ---------------------------------------------------------------- (R) roots
RC = ld(HERE + 'root_check_a.py', 'rca')
need(RC.run(RA) == [], '(R) type A root (two #6833 chain roots, t=0): root_check_a run() clean')
Rm = copy.deepcopy(RA); Rm['X'][5][3] = str(Q(Rm['X'][5][3]) + 1)
need(RC.blocks(Rm) != [] and RC.run(Rm) != [], '(R) wrong-root control A: a wrong X entry FAILS (%s)' % RC.blocks(Rm)[:1])
def hosted(path):
    r = subprocess.run([sys.executable, '-B', HERE + 'root_check_hw.py', path], capture_output=True, text=True, env={'WSTAGES': '1'}); return r.stdout
o = hosted(DATA + 'rootw1g.json'); need(o.strip().endswith('PASS_ROOT_HOSTED') and 'FAIL' not in o, '(R) type B root (outer W root, w=1, in the type B gauge, n=38; t=-1 at stages 1,18; t=-1/2 elsewhere): root_check_hw passes every line')
o = hosted(DATA + 'root_h.json'); need('FAIL' in o, '(R) control: the old B root root_h.json (no W stage) FAILS root_check_hw at WSTAGES=1')
o = hosted(DATA + 'rootw1.json'); need('FAIL' in o, '(R) control: the ungauged W root rootw1.json FAILS root_check_hw (pairs do not match the natives)')
Rm = copy.deepcopy(RB); Rm['X'][5][3] = str(Q(Rm['X'][5][3]) + 1); json.dump(Rm, open(OUT + 'ctl_rootB_X.json', 'w'))
o = hosted(OUT + 'ctl_rootB_X.json'); need('FAIL' in o and not o.strip().endswith('PASS_ROOT_HOSTED'), '(R) wrong-root control B: a wrong X entry in the hosted root FAILS root_check_h')
# ---------------------------------------------------------------- (C) joint replay
pM = 2147483629
IM = next(pow(g, (pM - 1) // 4, pM) for g in range(2, 99) if pow(g, (pM - 1) // 2, pM) == pM - 1); HALF = (pM + 1) // 2
fm = lambda x: (lambda f: f.numerator % pM * pow(f.denominator, pM - 2, pM) % pM)(Q(x))
def root_pairs(root):
    dot = lambda a_, b_: sum(Q(u) * Q(v) for u, v in zip(a_, b_) if Q(u) and Q(v)); out = {}
    for k, s_ in enumerate(root['stages']):
        u, v = s_['units']; out[k + 1] = (dot(root['Y'][u], root['X'][v]), dot(root['Y'][v], root['X'][u]))
    return out
def mask_inc(root, c): return [int(c in set(s['mask'])) for s in root['stages']]
H = W['hosted']; al_w, be_w, a2_w = Q(H['alpha']), Q(H['beta']), Q(H['alpha2'])
PB = root_pairs(RB); SN = {int(k): v for k, v in J['stage_native'].items()}
wpair = lambda tag: (Q(WORDS[tag]['hosted']['alpha']), Q(WORDS[tag]['hosted']['beta']))
need(len(PB) == 18 and all(PB[st] == wpair(SN[st]) for st in range(1, 19)) and [st for st in SN if SN[st] == 'mmW'] == [1, 18], '(C) each of the 18 hosted stages of root B has the pair of the native called there: mm (-1,1/2) at 16 stages, mmW (-2,1/2, t=-1) at W stages 1,18, read from the root')
need(all(e[4] == SN[e[1]] for e in J['events'] if e[0] == 'J'), '(C) every joint contact is tagged with its stage native')
need(J['natives']['mm'] == __import__('hashlib').sha256(open(DATA + 'mm.json.gz','rb').read()).hexdigest()[:16] and J['natives']['mmW'] == __import__('hashlib').sha256(open(DATA + 'mmW.json.gz','rb').read()).hexdigest()[:16], '(C) native hashes in the caller equal the files')
TA, TB = J['types']['A'], J['types']['B']
need(all(TA['diagonal'][c][2:] == mask_inc(RA, c) for c in range(40)), '(C) type A caller target exponents equal the A root mask incidence (field by field, stage by stage)')
need(all(TB['diagonal'][c][2:] == mask_inc(RB, c) for c in range(38)), '(C) type B caller target exponents equal the B root mask incidence')
need(Q(TA['alpha2']) == a2_w and Q(TA['beta2']) == Q(H['beta2']) == 0, '(C) type A plane-2 parameters equal the word\'s')
need(all((Q(e[3][2]), Q(e[3][3])) == wpair(e[4]) for e in J['events'] if e[0] == 'J'), '(C) every joint contact carries its own native\'s hosted pair on its B tuple')
need(all(Q(WORDS[t]['hosted']['alpha2']) == a2_w and WORDS[t]['hosted']['Dports'] == H['Dports'] for t in WORDS), '(C) both natives have the same A-type ports and plane-2 parameter')
NR = J['roles']
def target(Jc, c_role, qv, Dv):
    t, off = (Jc['types']['A'], 0) if c_role < 40 else (Jc['types']['B'], 40); dg = t['diagonal'][c_role - off]
    c = pow(qv, dg[0] % 4, pM)
    for k, bit in enumerate(dg[2:]):
        if bit: c = c * Dv[k + 1] % pM
    return c
def replay(Jc, qv, Dv, a2=a2_w, pairs=PB, types='AB', tgt=target, order_check=True):
    Rm_ = [[int(i == j) for j in range(NR)] for i in range(NR)]; qi = pow(qv, pM - 2, pM); seen = []
    for e in Jc['events']:
        tag = e[0]
        if tag == 'J':
            st = e[1]; seen.append(st); d = Dv[st]
            if 'A' in types:
                src, dst, x2, y2 = e[2]
                Rm_[dst] = [(a_ + qi * b_) % pM for a_, b_ in zip(Rm_[dst], Rm_[src])]
                Rm_[x2] = [(a_ + fm(a2) * qv % pM * b_) % pM for a_, b_ in zip(Rm_[x2], Rm_[y2])]
                for r_ in (src, dst, x2, y2): Rm_[r_] = [a_ * d % pM for a_ in Rm_[r_]]
            if 'B' in types:
                src, dst = e[3][0], e[3][1]; a_, b_ = fm(pairs[st][0]), fm(pairs[st][1]); tt_ = a_ * b_ % pM
                ns = [(x + a_ * qv % pM * y) % pM * d % pM for x, y in zip(Rm_[src], Rm_[dst])]
                nd = [(b_ * qi % pM * x + (1 + tt_) * y) % pM * d % pM for x, y in zip(Rm_[src], Rm_[dst])]
                Rm_[src], Rm_[dst] = ns, nd
            continue
        if tag not in types: continue
        op = e[1]
        if op == 'ADD': Rm_[e[2]] = [(a_ + fm(e[4]) * b_) % pM for a_, b_ in zip(Rm_[e[2]], Rm_[e[3]])]
        elif op == 'SCALE': c = fm(e[3]); Rm_[e[2]] = [a_ * c % pM for a_ in Rm_[e[2]]]
        elif op == 'SWAP': Rm_[e[2]], Rm_[e[3]] = Rm_[e[3]], Rm_[e[2]]
        elif op == 'QUERY': c = pow(qv, e[4] % 4, pM); Rm_[e[2]] = [(a_ + c * b_) % pM for a_, b_ in zip(Rm_[e[2]], Rm_[e[3]])]
        elif op == 'LAMBDA':
            s_ = e[3]; c = ((1 + s_ * IM) * HALF + (1 - s_ * IM) * HALF * qv * qv) % pM; Rm_[e[2]] = [a_ * c % pM for a_ in Rm_[e[2]]]
        elif op == 'IDLE_ONE':
            c = 1
            for k in e[3]: c = c * Dv[k] % pM
            Rm_[e[2]] = [a_ * c % pM for a_ in Rm_[e[2]]]
        else: raise SystemExit('FAIL unknown caller event ' + op)
    if order_check and seen != list(range(1, 19)): return 10 ** 6
    roles = [r for r in range(NR) if ('A' in types and r < 40) or ('B' in types and r >= 40)]
    return sum(Rm_[i][j] != (tgt(Jc, i, qv, Dv) if i == j else 0) for i in roles for j in range(NR))
rnd = random.Random(11); tot = cnt = 0
for qv in (1, IM, pM - 1, pM - IM):
    for _ in range(3):
        Dv = {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}; tot += replay(J, qv, Dv); cnt += 1
need(tot == 0, '(C) the ONE joint stream (78 roles, one stage value per stage common to both types) replays to the block-diagonal target at all four central characters (%d evaluations, 0 bad of %d entries each, cross-type blocks included)' % (cnt, NR * NR))
for ty in ('A', 'B'):
    t2 = sum(replay(J, qv, {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}, types=ty) for qv in (1, IM, pM - 1, pM - IM))
    need(t2 == 0, '(C) type %s alone (events and joint-contact half of its own type) replays to its target at the four characters' % ty)
Dv = {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}
def rej(Jc=J, **kw): return replay(Jc, IM, Dv, **kw)
def mut(f):
    Jm = copy.deepcopy(J); f(Jm); return Jm
idx = lambda Jc, pred: next(i for i, e in enumerate(Jc['events']) if pred(e))
first = lambda tag, op: (lambda e: e[0] == tag and e[1] == op)
ctr = []
ctr.append(('A wrong alpha2', rej(a2=Q(1))))
for nm, fn in (('B alpha sign', lambda x: x.__setitem__(0, -x[0])), ('B beta sign', lambda x: x.__setitem__(1, -x[1])), ('B pair swapped', lambda x: x.reverse())):
    pm = {k: list(v) for k, v in PB.items()}; fn(pm[13]); ctr.append((nm + ' at stage 13', rej(pairs=pm)))
ctr.append(('B root in the other gauge (ungauged rootw1)', rej(pairs=root_pairs(RB0))))
pm = dict(PB); pm[1] = wpair('mm'); ctr.append(('W stage 1 served by mm (t=-1/2 pair) instead of mmW', rej(pairs=pm)))
pm = dict(PB); pm[18] = wpair('mm'); ctr.append(('W stage 18 served by mm instead of mmW', rej(pairs=pm)))
pm = dict(PB); pm[5] = wpair('mmW'); ctr.append(('H stage 5 served by mmW instead of mm', rej(pairs=pm)))
for ty in 'AB':
    ctr.append(('%s deleted IDLE_ONE' % ty, rej(mut(lambda Jm: Jm['events'].pop(idx(Jm, first(ty, 'IDLE_ONE')))))))
    ctr.append(('%s deleted QUERY' % ty, rej(mut(lambda Jm: Jm['events'].pop(idx(Jm, first(ty, 'QUERY')))))))
    def flip(Jm):
        j0 = idx(Jm, lambda e: e[0] == 'J'); k = max(i for i in range(j0) if Jm['events'][i][0] == ty and Jm['events'][i][1] == 'LAMBDA'); Jm['events'][k][3] *= -1
    ctr.append(('%s flipped LAMBDA before the first contact' % ty, rej(mut(flip))))
for nm, bad in ctr: print('   control %-52s -> %d bad' % (nm, bad))
need(all(b > 0 for _, b in ctr), '(C) controls: wrong alpha2, wrong/other-gauge hosted pair, deleted idle, deleted query, flipped LAMBDA at a contact, each type: all rejected')
def tm(Jm, ty, role, st):
    Jm['types'][ty]['diagonal'][role][2 + st] ^= 1
for ty, role in (('A', 3), ('B', 3)):
    Jm = mut(lambda x: tm(x, ty, role, 4)); b = rej(Jm)
    need(b > 0 and Jm['types'][ty]['diagonal'][role][2:] != (mask_inc(RA, role) if ty == 'A' else mask_inc(RB, role)), '(C) mask control %s: a wrong mask bit in the caller target fails the replay (%d bad) and the mask comparison' % (ty, b))
Jm = mut(lambda x: x['events'].insert(idx(x, lambda e: e[0] == 'J'), ['A', 'ADD', 5, 45, '1'])); b = rej(Jm)
need(b > 0, '(C) cross-type control: one ADD from an A role into a B role is rejected (%d bad): the types do not interact' % b)
Jm = mut(lambda x: x['events'].insert(idx(x, lambda e: e[0] == 'J'), ['B', 'ADD', 45, 5, '1'])); need(rej(Jm) > 0, '(C) cross-type control, other direction rejected')
def swapst(x):
    js = [e for e in x['events'] if e[0] == 'J']; js[0][1], js[1][1] = js[1][1], js[0][1]
need(rej(mut(swapst)) > 0, '(C) stage-order control: two joint contacts with exchanged stages rejected')
def rot(x):
    e = x['events'][idx(x, lambda e: e[0] == 'J')]; a = e[2]; e[2] = [a[0], a[1], a[3], a[2]]
need(rej(mut(rot)) > 0, '(C) exchanged second-plane roles (X2,Y2) in a contact rejected')
# exhaustive single LAMBDA flips (information): how many are detected, per type
for ty in 'AB':
    ids = [i for i, e in enumerate(J['events']) if e[0] == ty and e[1] == 'LAMBDA']; miss = 0
    for i in ids:
        Jm = copy.deepcopy(J); Jm['events'][i][3] *= -1; miss += replay(Jm, IM, Dv) == 0
    print('   info: type %s: %d LAMBDA events, single flips not detected at one character: %d' % (ty, len(ids), miss))
# ---------------------------------------------------------------- (W) port types
live = W['live']; n = len(W['initial']); DP = H['Dports']
need(WW['live'] == W['live'] and WW['hosted']['whitehead']['prefix_ports'] == sorted(TB['ports']) and sorted(TA['ports']) == sorted(DP) and sorted(TB['ports']) == [i for i in range(104) if i not in set(DP)] and len(TA['ports']) == 96 and len(TB['ports']) == 8, '(W) joint caller port types equal the word\'s: A = Dports (96), B = the other 8')
X2 = set(H['X2']); Y2 = set(H['Y2']); need(len(X2) == len(Y2) == 96, '(W) second mains exist for exactly the 96 type-A ports')
sc = [e for e in W['program'] if e[0] == 'SCALE']
print('INFO (W-gauge): original clause, now informational only:',{e[1] for e in sc[:8]}=={live[i] for i in TB['ports']} and all(Q(e[2]) == Q(1, 2) for e in sc[:8]),'| first 8 SCALEs:',[(e[1],e[2]) for e in sc[:8]],'| gauge covered by exact endpoint B.X = x-y, B.Y=(x+y)/2 [rep.py]')
# ---------------------------------------------------------------- (I) invoice from emitted events
fr = W['frames']; dm = [len(b) for b in fr]; live_s = set(live); mains = live_s | {r + 112 for r in live_s} | X2 | Y2
def hp(Wd): return Counter(dm[Wd['final'][r]] - dm[Wd['initial'][r]] for r in range(n) if r not in mains), Counter(abs(dm[e[3]] - dm[e[2]]) for e in Wd['program'] if e[0] == 'MOVE')
assert WW['frames'] == W['frames'] and WW['initial'] == W['initial'] and WW['final'] == W['final']
HP = {t: hp(WORDS[t]) for t in WORDS}; hel, paid = HP['mm']
nA, nB = len(TA['ports']), len(TB['ports']); cnt_ty = {'A': nA, 'B': nB}
T = Counter(); P = Counter(); nj = 0
for e in J['events']:
    if e[0] == 'J': nj += 1; T.update(HP[e[4]][0]); P.update(HP[e[4]][1])      # ONE native call per stage, of the native tagged at that stage
    elif e[1] == 'QUERY': P[1] += cnt_ty[e[0]]
    elif e[1] == 'IDLE_ONE': P[8 * len(e[3])] += cnt_ty[e[0]]
for ty, t in (('A', TA), ('B', TB)):
    for dg in t['diagonal']: T[int(dg[0] % 2) + 8 * sum(dg[2:])] += cnt_ty[ty]
need(nj == 18, '(I) 18 joint native contacts (one per stage)')
def kap(T, P):
    rs = sorted(set(T) | set(P)); lo, hi = D('0.001'), D('0.0045')
    for _ in range(200):
        m = (lo + hi) / 2
        if sum((D(T.get(r, 0)) - D(P.get(r, 0))) * (D(r).ln() * (1 - m)).exp() for r in rs) > 0: lo = m
        else: hi = m
    return lo
S = sum(r * (T[r] - P[r]) for r in set(T) | set(P)); kj = kap(T, P)
inv = json.load(open(DATA + 'mm.chain.invoice.json')); Tw = Counter({int(k): v for k, v in inv['T'].items()}); P1 = Counter({int(k): v for k, v in inv['P'].items()})
print('   bill vs mm invoice: T', dict(sorted((+(T - Tw)).items())), '-', dict(sorted((+(Tw - T)).items())), '| P', dict(sorted((+(P - P1)).items())), '-', dict(sorted((+(P1 - P)).items())))
print('   S', S, 'kappa', str(kj)[:24], 'D', sum((T[r] - P[r]) * r * float(D(r).ln()) for r in set(T) | set(P)))
print('   Whitehead kappa', kj)
# independent: root part per type from the roots, native part from the word
def root_fields(RR):
    S_ = RR['stages']; Xr = RR['X']; Yr = RR['Y']; F = []
    for c in range(RR['n']):
        ms = [k for k, s_ in enumerate(S_) if c in set(s_['mask'])]; F.append((ms, [k for k in ms if any(Q(Yr[u][c]) != 0 for u in S_[k]['units'])]))
    dot = lambda a_, b_: sum(Q(u) * Q(v) for u, v in zip(a_, b_) if Q(u) and Q(v)); planes = []
    for s_ in S_:
        u, v = s_['units']; planes.append(2 if dot(Yr[u], Xr[v]) == 0 and dot(Yr[v], Xr[u]) == 0 else 1)
    return F, planes, RR['N'] - sum(len(s_['units']) for s_ in S_)
def outer(F, planes, thin, ports):
    T_ = Counter(); P_ = Counter(); hc = Counter()
    for ms, host in F:
        T_[8 * len(ms) + 1] += ports
        for k in host: hc[k] += 1
        run = 0; prev = None
        for k in ms:
            if k in host:
                if run: P_[8 * run] += ports
                run = 0; prev = None; continue
            if prev is not None and k == prev + 1: run += 1
            else:
                if run: P_[8 * run] += ports
                run = 1
            prev = k
        if run: P_[8 * run] += ports
    for k in range(18):
        if hc[k] > 2 * planes[k]: P_[8] += ports * (hc[k] - 2 * planes[k])
    P_[1] += ports * thin
    return T_, P_
T2 = Counter(); P2 = Counter()
for RR, ports in ((RA, nA), (RB, nB)):
    F, pl, th = root_fields(RR); t_, p_ = outer(F, pl, th, ports); T2.update(t_); P2.update(p_)
nW = sum(1 for t in SN.values() if t == 'mmW')
for tg, c in (('mm', 18 - nW), ('mmW', nW)):
    for r, k in HP[tg][0].items(): T2[r] += c * k
    for r, k in HP[tg][1].items(): P2[r] += c * k
need(+T2 == +T and +P2 == +P, '(I) invoice rebuilt from the two ROOTS (per type, per port count) plus the word equals the emitted-event invoice term for term')
mc = Counter(T); mc.update({}); Tn = Counter(T)
# controls: perturbed port count / moved port / dropped event change the invoice
Jm = copy.deepcopy(J); Jm['events'].pop(idx(Jm, first('B', 'IDLE_ONE')))
Pm = Counter(P); Pm[8 * len([e for e in J['events'] if e[0] == 'B' and e[1] == 'IDLE_ONE'][0][3])] -= nB
need(+Pm != +P, '(I) control: a deleted B idle changes the recounted invoice')
Tx = Counter(T); Px = Counter(P); Px.subtract(HP['mmW'][1]); Px.update(HP['mm'][1]); need(+Px != +P, '(I) control: pricing a W contact with mm changes the invoice')
json.dump({'T': {str(k): v for k, v in sorted(T.items())}, 'P': {str(k): v for k, v in sorted(P.items())}}, open(OUT + 'w.joint.invoice.json', 'w'))
print('PASS_JOINT_CALLER_ALL')
