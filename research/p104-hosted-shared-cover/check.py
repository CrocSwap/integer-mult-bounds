#!/usr/bin/env python3
"""Exact replay of the hosted native word, the hosted chain-nested root, the complete invoice and the outer constants.
Standard library only.  python3 -I -B check.py     (writes nothing)
Steps: (1) event-by-event exact replay of data/word.json.gz; (2) root_check.py; (3) invoice rebuilt from the word and the root,
and the #6833 invoice rebuilt by the same code; (4) caller recount; (5) outer conditions with the retained interval engines.
Prints PASS_P104_HOSTED_CHAIN_ROOT.  (physical.py, run as a second command, replays the 512-component physical streams.)"""
import gzip, json, os, sys, subprocess, importlib.util, random, hashlib
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

# ---- (1) replay of the word -------------------------------------------------------------------
W = json.load(gzip.open(data('word.json.gz'), 'rt'))
def span(b):
    s = {0}
    for v in b:
        need_ = isinstance(v, int) and 0 < v < 512 and v not in s
        if not need_: raise SystemExit('FAIL dependent basis')
        s |= {x ^ v for x in s}
    return frozenset(s)
fr = W['frames']; sp = [span(b) for b in fr]; dim = [len(b) for b in fr]
n = len(W['initial']); NO = W['owned_fields']; NR = n + NO
cur = list(W['initial']) + [None] * NO; row = [({r: Q(1)} if r < n else {}) for r in range(NR)]
owned = set(); viol = Counter(); owned_up = Counter(); up_idx = []; paid = Counter(); peak = life = dirty = 0; maxq = Q(0)
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
        maxq = max(maxq, abs(q))
        if op == 'SCALE':
            if cur[r] != f or abs(q.numerator) & (abs(q.numerator) - 1): viol['SCALE'] += 1
            row[r] = {k: v * q for k, v in row[r].items()}
        else:
            s = e[2]
            if not (cur[r] == f == cur[s] and s != r): viol['common chart'] += 1
            if op == 'COPY':
                if not (r in owned and not row[r]): viol['COPY'] += 1
                row[r] = {}
            for k, v in row[s].items():
                t = row[r].get(k, 0) + q * v
                if t: row[r][k] = t
                else: row[r].pop(k, None)
need(not owned and cur[:n] == W['final'], 'owned all cleared; final frames as declared')
need(dict(viol) == {}, 'frame law, common chart, dyadic alphabet, public ascent: no violation beyond the declared one')
up_mass = sum(k * v for k, v in owned_up.items())
need(up_mass == 56 and sum(owned_up.values()) == 23, 'declared OWNED UP: %d events, rank mass %d (convention: owned ascent)' % (sum(owned_up.values()), up_mass))
def verifier(name):
    o = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, name), data('word.json.gz')], capture_output=True, text=True).stdout
    return o
os_, or_ = verifier('verify_strict.py'), verifier('verify_relaxed.py')
rej = [int(x) for x in os_.split('indices')[1].split('\n')[0].split()]
need(os_.strip().endswith('REJECTED_STRICT') and rej == up_idx and "['move nesting']" in os_, 'rejection control: the strict (predecessor) verifier rejects this word at exactly the %d owned-ascent events and nothing else' % len(rej))
need(or_.strip().endswith('ACCEPTED_RELAXED'), 'relaxed verifier (only the owned-move direction rule changed, paid |delta dim| either way) accepts every event')
al, be = Q(W['hosted']['alpha']), Q(W['hosted']['beta']); t = al * be
live = W['live']; X = set(live); Y = {r + 112 for r in live}
need(len(live) == len(W['ports']) == 104 and t == Q(-1, 2) and 1 + t != 0, 'hosted pair alpha=%s beta=%s t=%s, 1+t != 0' % (al, be, t))
bad = 0
for r in range(NR):
    if r >= n: ex = {}
    elif r in X: ex = {r: Q(1), r + 112: al}
    elif r in Y: ex = {r - 112: be, r: 1 + t}
    else: ex = {r: Q(1)}
    bad += row[r] != ex
need(bad == 0, 'endpoint exact on all %d public and owned rows: X=x+alpha y, Y=beta x+(1+t) y, helpers identity, owned empty' % NR)
need(all(row[y].get(y - 112) == be for y in Y), 'T[Y,X]=beta on all 104 ports; Tinv[X,Y]=-alpha (block det 1)')
for r, q in zip(live, W['ports']):
    if fr[W['initial'][r]] != [q] or dim[W['final'][r]] != 9 or dim[W['initial'][r + 112]] != 0 or sp[W['final'][r + 112]] != frozenset(x for x in range(512) if not (x & q).bit_count() % 2):
        raise SystemExit('FAIL main frames')
need(True, '104 literal central ports, full X final frame, empty Y initial frame, literal output hyperplane')
main = X | Y
hel = Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in main)
need(min(hel) > 0 and all(sp[W['initial'][r]] < sp[W['final'][r]] for r in range(n) if r not in main), 'every helper strictly ascends (rank > 0)')
print('  events', len(W['program']), 'public', n, 'owned roles', NO, 'peak owned', peak, 'owned lifetimes', life, 'dirty owned erasures', dirty, 'max |coefficient|', maxq)

# ---- (2) root ----------------------------------------------------------------------------------
out = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'root_check.py'), data('root.json')], capture_output=True, text=True).stdout
need(out.strip().endswith('PASS_ROOT_HOSTED') and 'FAIL' not in out, 'extended root checker: PASS_ROOT_HOSTED (relaxations declared in its header)')
R = json.load(open(data('root.json')))

# ---- (3) invoice -------------------------------------------------------------------------------
def kappa(T, P):
    rs = sorted(set(T) | set(P)); ln = {r: D(r).ln() for r in rs}
    e = lambda k: sum((D(T.get(r, 0)) - D(P.get(r, 0))) * (ln[r] * (1 - k)).exp() for r in rs)
    lo, hi = D('1e-6'), D('0.05')
    for _ in range(220):
        m = (lo + hi) / 2
        if e(m) > 0: lo = m
        else: hi = m
    return lo
def outer(F, thin):
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
    for k in range(18):
        if hc[k] > 2: P[8] += 104 * (hc[k] - 2)
    P[1] += 104 * thin
    return T, P
def invoice(hel_, paid_, F, thin):
    T, P = outer(F, thin)
    for r, k in hel_.items(): T[r] += 18 * k
    for r, k in paid_.items(): P[r] += 18 * k
    return T, P
bi = json.load(open(data('base_invoice.json')))
T0 = Counter({int(k): v for k, v in bi['targets'].items()}); P0 = Counter({int(k): v for k, v in bi['paid'].items()})
chain = [(list(range(18)), list(range(18)))] + [(list(range(i, 9)), [i]) for i in range(9)] + [(list(range(9, 10 + m)), [9 + m]) for m in range(9)] + [([], [])]
Tb, Pb = invoice({int(k): v for k, v in bi['helpers'].items()}, {int(k): v for k, v in bi['local_paid'].items()}, chain, 3)
need(+Tb == T0 and +Pb == P0, 'same code rebuilds the #6833 invoice term for term')
kb = kappa(T0, P0)
need(abs(kb - D(bi['kappa_literal'])) < D('1e-17'), 'base kappa %s' % str(kb)[:20])
ST = R['stages']; F = []
for c in range(R['n']):
    ms = [k for k, s in enumerate(ST) if c in set(s['mask'])]
    F.append((ms, [k for k in ms if any(Q(R['Y'][u][c]) != 0 for u in ST[k]['units'])]))
thin = R['N'] - sum(len(s['units']) for s in ST)
Tn, Pn = invoice(hel, paid, F, thin)
kn = kappa(Tn, Pn)
need(abs(kn - D('0.00341603288178402')) < D('1e-17'), 'new kappa %s' % str(kn)[:22])
# comparison control: the #6883 word (data/prior_word.json.gz) through the same code
Wp = json.load(gzip.open(data('prior_word.json.gz'), 'rt')); mp_ = set(Wp['live']) | {r + 112 for r in Wp['live']}; dp_ = [len(b) for b in Wp['frames']]
hel_p = Counter(dp_[Wp['final'][r]] - dp_[Wp['initial'][r]] for r in range(len(Wp['initial'])) if r not in mp_)
paid_p = Counter(abs(dp_[e[3]] - dp_[e[2]]) for e in Wp['program'] if e[0] == 'MOVE')
Tp, Pp = invoice(hel_p, paid_p, F, thin); kp = kappa(Tp, Pp)
need(abs(kp - D('0.00339993013239573')) < D('1e-17'), 'control: the #6883 word through the same code gives %s (its published kappa)' % str(kp)[:22])
need(abs(kb - D(bi['kappa_literal'])) < D('1e-17'), 'secondary control: #6833 rebuilt, kappa %s' % str(kb)[:22])
print('  gain over #6883: %+.4f%%; over #6833: %+.4f%%' % (100 * float(kn / kp - 1), 100 * float(kn / kb - 1)))
S = sum(r * (Tn.get(r, 0) - Pn.get(r, 0)) for r in set(Tn) | set(Pn))
need(S == 656 + 48 * 18 and D(PIN.numerator) / D(PIN.denominator) > kn, 'rank-mass surplus S=%d (656+48h, already net of the 56 owned-ascent mass per host); kappa above the retained .0034 pin and below the .00376669 pin by %s' % (S, str(D(PIN.numerator) / D(PIN.denominator) - kn)[:10]))

# ---- (4) caller, composition, recount ---------------------------------------------------------
C = json.load(open(data('caller.json'))); Tc = Counter(); Pc = Counter(); nh = 0
for e in C['events']:
    if e[0] == 'HOST': Tc.update(hel); Pc.update(paid); nh += 1
    elif e[0] == 'QUERY': Pc[1] += 104
    elif e[0] == 'IDLE_ONE': Pc[8 * len(e[2])] += 104
    elif e[0] == 'IDLE': raise SystemExit('FAIL unexpected IDLE')
for tt in C['diagonal']: Tc[int(tt[0] % 2) + 8 * sum(tt[2:])] += 104
need(nh == 18 and +Tc == +Tn and +Pc == +Pn, 'emitted caller events recount the same invoice (18 hosted native calls, 4 thin queries, one-site idle jobs)')
pM = 2147483629
IM = next(pow(g, (pM - 1) // 4, pM) for g in range(2, 99) if pow(g, (pM - 1) // 2, pM) == pM - 1); HALF = (pM + 1) // 2
fm = lambda x: (lambda f: f.numerator % pM * pow(f.denominator, pM - 2, pM) % pM)(Q(x))
def root_pairs(root):
    """(alpha,beta) of every hosted stage, read from the root's own units: alpha=y_u.x_v, beta=y_v.x_u."""
    dot = lambda a_, b_: sum(Q(u) * Q(v) for u, v in zip(a_, b_) if Q(u) and Q(v))
    out = {}
    for k, s_ in enumerate(root['stages']):
        u, v = s_['units']; out[k + 1] = (dot(root['Y'][u], root['X'][v]), dot(root['Y'][v], root['X'][u]))
    return out
def replay(Wc, qv, D, pairs):
    """caller events over F_p at central character qv (q^4=1) and random stage values D; HOST uses the pair read from the ROOT, not from the event."""
    n_ = Wc['roles']; Rm = [[int(i == j) for j in range(n_)] for i in range(n_)]; qi = pow(qv, pM - 2, pM)
    for e in Wc['events']:
        o = e[0]
        if o == 'ADD': Rm[e[1]] = [(a_ + fm(e[3]) * b_) % pM for a_, b_ in zip(Rm[e[1]], Rm[e[2]])]
        elif o == 'SCALE': c = fm(e[2]); Rm[e[1]] = [a_ * c % pM for a_ in Rm[e[1]]]
        elif o == 'SWAP': Rm[e[1]], Rm[e[2]] = Rm[e[2]], Rm[e[1]]
        elif o == 'QUERY': c = pow(qv, e[3] % 4, pM); Rm[e[1]] = [(a_ + c * b_) % pM for a_, b_ in zip(Rm[e[1]], Rm[e[2]])]
        elif o == 'LAMBDA':
            s_ = e[2]; c = ((1 + s_ * IM) * HALF + (1 - s_ * IM) * HALF * qv * qv) % pM; Rm[e[1]] = [a_ * c % pM for a_ in Rm[e[1]]]
        elif o == 'IDLE_ONE':
            c = 1
            for k in e[2]: c = c * D[k] % pM
            Rm[e[1]] = [a_ * c % pM for a_ in Rm[e[1]]]
        elif o == 'HOST':
            st, src, dst = e[1:4]; a_, b_ = fm(pairs[st][0]), fm(pairs[st][1]); tt_ = a_ * b_ % pM; d = D[st]
            ns = [(x + a_ * qv % pM * y) % pM * d % pM for x, y in zip(Rm[src], Rm[dst])]
            nd = [(b_ * qi % pM * x + (1 + tt_) * y) % pM * d % pM for x, y in zip(Rm[src], Rm[dst])]
            Rm[src], Rm[dst] = ns, nd
        else: raise SystemExit('FAIL unknown caller event ' + o)
    bad = 0
    for i in range(n_):
        c = pow(qv, Wc['diagonal'][i][0] % 4, pM)
        for k, bit in enumerate(Wc['diagonal'][i][2:]):
            if bit: c = c * D[k + 1] % pM
        bad += sum(Rm[i][j] != (c if i == j else 0) for j in range(n_))
    return bad
rp = root_pairs(R)
need(set(rp.values()) == {(al, be)} and len(rp) == 18, 'every one of the 18 hosted stages of the root has the word\'s pair (alpha,beta)=(%s,%s)' % (al, be))
need(all(e[4] == str(al) and e[5] == str(be) for e in C['events'] if e[0] == 'HOST'), 'every HOST event carries the word\'s pair')
need(all(bool(C['diagonal'][c][2 + k]) == (c in set(ST[k]['mask'])) for c in range(R['n']) for k in range(18)), 'caller target exponents equal the root mask incidence (field by field, stage by stage)')
rnd = random.Random(5); tot = cnt = 0
for qv in (1, IM, pM - 1, pM - IM):
    for _ in range(2):
        Dv = {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}; tot += replay(C, qv, Dv, rp); cnt += 1
need(tot == 0, 'composition: caller with the hosted native replays to the diagonal root target at all four central characters, random stage values (%d evaluations, 0 bad of %d coefficients each)' % (cnt, R['n'] ** 2))
R0 = json.load(open(data('control_root_ungauged.json'))); rp0 = root_pairs(R0)
bad0 = replay(C, IM, {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}, rp0)
need(set(rp0.values()) != {(al, be)} and bad0 > 0, 'control: the same root in the other gauge (pairs (-1/2,1) at the right stages) is rejected: %d bad coefficients' % bad0)
muts = []
for name, fn in (('alpha sign', lambda x: x.__setitem__(0, -x[0])), ('beta sign', lambda x: x.__setitem__(1, -x[1])), ('swapped', lambda x: x.reverse())):
    pm = {k: list(v) for k, v in rp.items()}; fn(pm[13]); muts.append(replay(C, IM, {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}, pm))
need(all(muts), 'controls: wrong alpha sign / beta sign / swapped pair at one stage are rejected (bad %s)' % muts)
# departures that are counted rather than pinned
nums = [abs(Q(e[3] if e[0] == 'ADD' else e[2])) for e in C['events'] if e[0] in ('ADD', 'SCALE')]
hb = (max(x.numerator.bit_length() for x in nums), max(x.denominator.bit_length() for x in nums))
scal = 0
for e in W['program']:
    if e[0] in ('INIT', 'CLEAR'): scal += 2
    elif e[0] == 'SCALE':
        q = Q(e[2]); scal += 2 * (abs(q.numerator.bit_length() - q.denominator.bit_length()) + int(q < 0))
    elif e[0] in ('ADD', 'COPY'):
        q = Q(e[3]); scal += 2 * (3 + abs(q.numerator).bit_length() - 1 + bin(abs(q.numerator)).count('1') + q.denominator.bit_length() - 1)
routes = (sum(paid.values()) + 2 * sum(hel.values()) + 208 + 4 * 104 + 4 * life) * 1000
print('DEPARTURES (class; exact count here):')
for cls, what in (
    ('convention (A6, load-bearing)', 'owned ascent: 23 owned MOVEs rise in frame (rank mass 56); the predecessor native.py:55 / local.py:126 lets owned moves only descend. A6: an owned nested rise costs one paid H_r plus rank-0 adapters, no credit, on arbitrary contents, factorwise at every width, with CLEAR at any frame under owned_erasure. No ascent, no word; kappa is conditional on A6.'),
    ('verifier', 'endpoint literal: the predecessor native.py:75-77 / local.py:168 expect X=x, Y=x+y; the hosted target is X=x-y, Y=(x+y)/2 on 104 ports (proved exactly above and physically in physical.py).'),
    ('verifier', 'events %d, public %d, owned roles %d, lifetimes %d, peak owned %d against local.py:52,54,103 and pricing.py:84-87 literals (the predecessor word already exceeds the 26000 cap; counts are recounted, not pinned).' % (len(W['program']), n, NO, life, peak)),
    ('verifier', 'per-call scalar work %d against the displayed pricing.py:93 bound 10^7 (word scalar %d + routes %d); the outer ledger has no scalar-work term.' % (scal + routes, scal, routes)),
    ('verifier', 'coefficient height of the caller: numerators up to %d bits, denominators up to %d bits against the predecessor 8 and 7 bits (pricing.py:96-97).' % hb),
    ('convention', 'LAMBDA: 82 caller events (two-term two-sided scalar pass at width >= 2) inherited from the open predecessor callers (#6726, #6763); no compiler list names it and it is not on main; the text does not decide whether it is a scalar or a routing pass. It is checked algebraically by the composition replay at four central characters and counted in ordinary work, not by a physical contact check.'),
    ('convention', 'root family: N=n+2 and two units per stage instead of the shortest root with one full site per child (chain_root.py:79,82,83,98; check_root.py:26,133,141-145); the SPEC-level identities are re-proved in root_check.py.'),
    ('convention', 'pricing: the 36x104 one-site idle jobs at the hosted stages are PAID whole H8 idles (P[8]); targets get nothing for them. kappa rests on pricing them as whole H8 idles (the line construction attains that exactly); priced as 8 rank-1 jobs each, kappa would be 0.002995.'),
    ('assumption', 'owned erasure of dirty owned content (%d erasures, predecessor 45): the owned_erasure assumption of the predecessor, unchanged.' % dirty)):
    print('  [%s] %s' % (cls, what))
need(True, 'departures listed')

# ---- (4b) ordinary (non-recursive) raw bound: definition of the predecessor review ordinary() and pricing.py:93,102-113 ------
def swaps(sel):
    wanted = set(range(len(sel))); return len(list(zip(sorted(set(sel) - wanted), sorted(wanted - set(sel)))))
amb = C['ambient_rank']; roles = C['roles']; evs = C['events']
main_maps = 0
for role, (qp, zero, *sel) in enumerate(C['diagonal']):
    axes = ([0] if qp else []) + [x_ for st, y_ in enumerate(sel, 1) if y_ for x_ in range(9 + 8 * (st - 1), 9 + 8 * st)]
    main_maps += 104 * (2 * swaps(axes) + 2 * bool(qp) + int(qp == -1))
idle_ex = qmaps = 0
for e in evs:
    if e[0] == 'IDLE_ONE': idle_ex += 104 * 2 * swaps([x_ for st in e[2] for x_ in range(9 + 8 * (st - 1), 9 + 8 * st)])
    elif e[0] == 'QUERY': qmaps += 104 * (2 + int(e[3] == -1))
rest = 32 * roles * 104 * len(evs) + sum(e[0] == 'QUERY' for e in evs) * 16 * 104 + roles * 104 * 26 + 1000 * main_maps + 1000 * idle_ex + 1000 * qmaps
per_call = scal + routes
raw_lit, raw_act = 18 * 10 ** 7 + rest, 18 * per_call + rest
print('  raw bound pieces: caller+thin+outputs+idle adapters+query adapters = %d; per call (word scalar + routes) = %d against the displayed 10^7' % (rest, per_call))
need(raw_lit < 10 ** 9, 'raw bound, literal definition (18 calls x 10^7 + terms): %d < 10^9' % raw_lit)
need(raw_act < 10 ** 9, 'raw bound with the ACTUAL per-call work (18 x %d + terms): %d < 10^9, margin %.1f%%' % (per_call, raw_act, 100 * (1 - raw_act / 10 ** 9)))
print('  NOTE: per-call %d exceeds the displayed per-call bound 10^7 (pricing.py:93); the literal raw uses 10^7 per call, so only the actual-work total is self-consistent. The per-call work feeds raw only in that second total.' % per_call)
upper_rev = 0
for e in W['program']:
    if e[0] == 'SCALE':
        q = Q(e[2]); upper_rev += 4 * (abs(q.numerator).bit_length() + q.denominator.bit_length() + 1)
    elif e[0] in ('ADD', 'COPY'):
        q = Q(e[3]); upper_rev += 4 * (abs(q.numerator).bit_length() + bin(abs(q.numerator)).count('1') + q.denominator.bit_length() + 1)
raw_rev = 18 * (upper_rev + routes) + rest
print('  CONSTANT SUBSTITUTION (FINITE-PRECOMPILATION.md:278-283): events %d; scalar allowance %d; reviewed scalar upper %d; routes %d; per call %d (allowance) or %d (reviewed upper); caller envelope %d; raw upper %d (allowance) or %d (reviewed upper) against 10^9.' % (len(W['program']), scal, upper_rev, routes, per_call, upper_rev + routes, 32 * roles * 104 * len(evs), raw_act, raw_rev))
src_ep = open(os.path.join(HERE, 'retained', 'runtime', 'endpoint.py')).read()
need(not any(t in src_ep for t in ('10**9', '10 ** 9', '10**7', '10 ** 7', '1e9')), 'the outer ledger source contains no scalar-work or 10^9 term: the raw bound is a parameter of the precompilation constants, not an input of the 54+4 inequalities')
# net accounting: new = 2 x base + word part + lines
tk = kn; ex = lambda r_: (D(r_).ln() * (1 - tk)).exp()
mom = lambda H_: sum(v * ex(r_) for r_, v in H_.items())
bh = {int(k): v for k, v in bi['helpers'].items()}; bp = {int(k): v for k, v in bi['local_paid'].items()}
word_part = 18 * ((mom(hel) - mom(paid)) - 2 * (mom(bh) - mom(bp))); lines_part = -36 * 104 * ex(8)
net = (sum((Tn.get(r_, 0) - Pn.get(r_, 0)) * ex(r_) for r_ in set(Tn) | set(Pn)) - 2 * sum((T0.get(r_, 0) - P0.get(r_, 0)) * ex(r_) for r_ in set(T0) | set(P0)))
need(abs((word_part + lines_part) - net) < D('1e-6'), 'net accounting at the crossing: new = 2 x base %+.1f (hosted word vs 2 x predecessor native, 18 calls) %+.1f (36 whole H8 idle jobs per port) = net %+.2f' % (word_part, lines_part, net))

# ---- (5) outer conditions ----------------------------------------------------------------------
def ld(name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, 'retained', 'runtime', name + '.py')); m = importlib.util.module_from_spec(s); sys.modules[name] = m; s.loader.exec_module(m); return m
E, SE, OUT = ld('intervals'), ld('second_intervals'), ld('endpoint')
KAPPA, TESTED = Q('.00341603'), Q('.0034160307')
BITF = json.load(open(os.path.join(HERE, 'retained', 'bit', 'FRAGMENT-BIT-ADMISSION.json')))
need(hashlib.sha256(open(os.path.join(HERE, 'retained', 'bit', 'FRAGMENT-BIT-ADMISSION.json'), 'rb').read()).hexdigest() == '86955dcd74bc3fa1a940419474d45054fa7b0366b71b242568680366923d9311' and BITF['status'] == 'PASS_TWO_FRAGMENTS_BIT_ORDINARY_00376669' and Q(BITF['ordinary_admitted']) == PIN, 'BIT pin %s = ordinary_admitted of the pinned #6726 admission file (status %s); not re-derived here' % (float(PIN), BITF['status']))
need(Q(BITF['raw_crossing'][0]) > Q(BITF['raw_tested']) > PIN > TESTED, 'BIT side: raw crossing > raw tested saving 0.0037667 > pin > tested complex price')
Tq = Counter({r: v for r, v in Tn.items() if v}); Pq = Counter({r: v for r, v in Pn.items() if v})
for name, k, pos in (('lower', Q('.003416032881784'), 1), ('upper', Q('.003416032881785'), -1), ('tested', TESTED, 1)):
    a, b = E.moment(Tq, 1 - k), E.moment(Pq, 1 - k); first = (a[0] - b[1], a[1] - b[0])
    tl, th = SE.moment(Tq, k); pl, ph = SE.moment(Pq, k); second = (tl - ph, th - pl)
    need((first[0] > 0 and second[0] > 0) if pos > 0 else (first[1] < 0 and second[1] < 0), 'both interval engines: sign of the margin at the %s price endpoint' % name)
need(TESTED < PIN and Q('.003416032881784') > TESTED, 'tested price below the raw crossing and below the BIT pin .00376669')
signed = Counter(Tq); signed.subtract(Pq); d = Q(0)
for r, c in signed.items():
    lg = E.log_bounds(r); d -= c * (E.mul(E.power(r, 1 - PIN), lg)[0] if c >= 0 else r * lg[1])
need(d < 0, 'unique raw crossing through the BIT pin (derivative upper bound negative at the pin)')
cutoff, floor, power, offset = 11, 12, 1920, Q(1, 7)
tt_ = 1 - TESTED; target, paidm = E.moment(Tq, tt_), E.moment(Pq, tt_)
alpha = E.divide(paidm, target)
gamma = E.divide(E.moment(Pq, tt_ + offset), E.mul(E.power(cutoff, offset), target))
delta = E.divide((Q(sum(Tq.values()) * floor),) * 2, E.mul(E.power(cutoff, TESTED), target))
reserve, decay = Q(1, 10 ** 27), Q(31, 32)
need(alpha[1] < 1 - reserve and gamma[1] < decay and delta[1] < decay, 'tail ratios: alpha %.12f gamma %.4f delta %.4f (cutoff 11, floor 12, offset 1/7, power 1920)' % (float(alpha[1]), float(gamma[1]), float(delta[1])))
maxT = max(Tq); quarter = E.power(maxT, Q(power, 4) * TESTED); factor = E.mul(E.mul(quarter, quarter), E.mul(quarter, quarter))
eta = E.scale(E.divide((Q(1), Q(1)), factor), tt_)
need(eta[0] > Q(63, 64) ** 2100 and factor[1] < 2 ** 2100 and cutoff ** 64 < floor ** 63 and 2 * (cutoff ** power) ** 64 <= (maxT ** power) ** 63, 'compiler complement capacity and shifted exits (max target rank %d)' % maxT)
normalized = 1 / (1 + power * reserve) + 4 * decay ** power
need(normalized < 1 and normalized == 1 / (1 + power * reserve) + 4 * decay ** power, 'composite bound (predecessor pricing.py:211): 1/(1+power*reserve) + 4*decay^power < 1 at power 1920 (excess over the first term %.2e)' % float(4 * decay ** power))
gap = (TESTED - KAPPA) / 7; need(gap.numerator == 1, 'compiler grid: (tested-kappa)/7 = %s' % gap)
step = gap.denominator
wins = lambda j: (step * j + 1) ** 2100 < 2 ** j
lo_, hi_ = 1, 2
while not wins(hi_): lo_, hi_ = hi_, 2 * hi_
while hi_ - lo_ > 1:
    m = (lo_ + hi_) // 2
    if wins(m): hi_ = m
    else: lo_ = m
need(step * hi_ > 8 * power and wins(hi_) and not wins(hi_ - 1), 'explicit uniform threshold H=%d' % (step * hi_))
params = {'kappa': KAPPA, 'tested_saving': TESTED, 'complex_uniform_saving': KAPPA + 6 * gap, 'b': KAPPA + 5 * gap, 'a': KAPPA + 4 * gap, 'q': KAPPA + 3 * gap, 'bit_saving': PIN,
          'epsilon': 1 - gap, 'beta': 1 - 3 * gap, 'r0': gap / 10, 'stop': gap, 'layout': gap, 'd': gap}
led = OUT.ledger(params); led['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta'] * (1 - Q(1, 250))
need(len(led['strict_checks']) == 54 and len(led['functional_checks']) == 4 and all(v > 0 for k in ('strict_checks', 'functional_checks') for v in led[k].values()), 'outer inventory: 54 strict and 4 functional inequalities all positive')
need(any(v <= 0 for v in OUT.ledger(dict(params, bit_saving=Q('.0027')))['strict_checks'].values()), 'insufficient BIT budget is rejected')
need(any(v <= 0 for kk in ('strict_checks', 'functional_checks') for v in OUT.ledger(dict(params, bit_saving=params['a'] - Q(1, 10 ** 12)))[kk].values()), 'control: a BIT saving just below kappa + 4 gap is rejected')
# second hidden .0034: the input-lift saving lemma of the predecessor (pricing.py:128-156) with its cap moved to the pin
plus = [(7, 1), (3, 1), (5, 1)]; minus = [(9, 1), (4, 1), (1, 2)]
need(sum(x * c for x, c in plus) == sum(x * c for x, c in minus), 'input-lift saving: equal local rank mass 15 = 15')
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
need(d1[1] + PIN * Mq < 0, 'input-lift saving: g prime negative on 1-pin..1 (the predecessor cap .0034 moved to the pin; its crude bound holds to about .0037765)')
for nm, k_ in (('claim', KAPPA), ('tested', TESTED)):
    tl_ = 1 - k_; tot = lambda terms_, sgn: (sum(c * E.power(x, tl_)[0] for x, c in terms_), sum(c * E.power(x, tl_)[1] for x, c in terms_))
    gl = tot(plus, 1)[0] - tot(minus, 1)[1]
    need(gl > 0 and k_ * (-d1[1]) - k_ * k_ * Mq / 2 > 0, 'input-lift saving positive at the %s price' % nm)
# logarithm power: minimum for this tested price against the 2100 used
lp_ = 2100
while eta[0] > Q(63, 64) ** (lp_ - 1): lp_ -= 1
need(lp_ <= 2100, 'logarithm power: the smallest admissible value at this price is %d (2100 used; it is a free parameter, LOG-MAJORANT.md:110-122; 2100 suffices up to a tested price of about .00346)' % lp_)
print('PASS_P104_HOSTED_SHARED_COVER')
