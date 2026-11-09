#!/usr/bin/env python3
"""The main-wire native word with gate scalars 1/3 and 1/5 (the declared framework change of #6932 and #6934): exact replay of the word over A = Z[1/2, 1/3, 1/5] with the certificate S = 1125, both roots, the joint caller,
the complete invoice and the outer constants.  Standard library only (plus the retained interval engines).
python3 -I -B check.py     (writes nothing)
Steps: (1) event-by-event exact replay of data/word.json.gz with the endpoint of each port type, the alphabet A, the odd certificate S (every prefix row and every pre-ADD product), heights, scans; the odd verifier and its rejections;
(2) both roots with failing controls; (3) the joint caller (78 roles, block diagonal, one stage value per stage) at the four central characters, with wrong-root, wrong-port-type and swapped-assignment controls;
(4) the invoice recounted from the emitted events and rebuilt from the two roots, with the #6934, #6932, #6931, #6919, #6917 and #6911 words and #6833 as controls; (5) raw bound by three definitions, the LAMBDA recharge, the root-scale and
per-input scale readings, growth; (6) BIT pins, interval engines, strictification, compiler and outer ledger; departures.  Prints PASS_P104_MAIN_WIRE_NATIVE.
(physical.py, physical_exact.py, caller_physical.py, native_maps.py, second_engine.py, mutants.py, division_pass.py, controls.py, ordinary.py, check_caller_blocks.py and check_a6.py are the other commands.)"""
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
def sm(m, ps=(2, 3, 5)):
    m = abs(m)
    for p_ in ps:
        while m % p_ == 0: m //= p_
    return m == 1
def oddpart(m):
    m = abs(m)
    while m % 2 == 0: m //= 2
    return m
SC = 1125                                  # the declared certificate: S = 3^2 * 5^3
odd_dens = set(); v2max = 0; dmax = 1; mass = Q(0); odd_div = Counter(); odd_events = Counter(); bad_S = Counter()
def note(rw, tag):
    global mass, v2max, dmax
    m = Q(0)
    for v in rw.values():
        d = v.denominator; v2max = max(v2max, (d & -d).bit_length() - 1); dmax = max(dmax, d)
        if d & (d - 1): odd_dens.add(oddpart(d))
        if not dy(SC * v): bad_S[tag] += 1
        m += abs(SC * v)
    if m > mass: mass = m
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
        if q == 0 or not sm(q.denominator) or not abs(q) + 1 < 2 ** 16: viol['coefficient alphabet'] += 1
        if oddpart(q.denominator) > 1: odd_events[op] += 1
        maxq = max(maxq, abs(q)); nbits = max(nbits, abs(q.numerator).bit_length()); dbits = max(dbits, q.denominator.bit_length())
        if op != 'SCALE': logq += math.log2(1 + float(abs(q)))
        if op == 'SCALE':
            if cur[r] != f or not sm(q.numerator): viol['SCALE'] += 1
            row[r] = {k: v * q for k, v in row[r].items()}; note(row[r], 'scale row')
            for v in row[r].values():
                if abs(v) > pmax: pmax = abs(v)
                if v.denominator.bit_length() > dmaxb: dmaxb = v.denominator.bit_length()
        else:
            s = e[2]
            if not (cur[r] == f == cur[s] and s != r): viol['common chart'] += 1
            if op == 'COPY':
                if not (r in owned and not row[r]): viol['COPY'] += 1
                row[r] = {}
            note({k: q * v for k, v in row[s].items()}, 'pre-ADD product')
            for k, v in row[s].items():
                t = row[r].get(k, 0) + q * v
                if t:
                    row[r][k] = t
                    if abs(t) > pmax: pmax = abs(t)
                    if t.denominator.bit_length() > dmaxb: dmaxb = t.denominator.bit_length()
                else: row[r].pop(k, None)
            note(row[r], 'ADD row')
need(not owned and cur[:n] == W['final'], 'owned all cleared; final frames as declared')
need(dict(viol) == {}, 'frame law, common chart, alphabet A = Z[1/2, 1/3, 1/5] with |q|+1 < 2^16, SCALE units of A, public ascent: no violation beyond the declared one')
up_mass = sum(k * v for k, v in owned_up.items())
need(up_mass == 56 and sum(owned_up.values()) == 23, 'declared OWNED UP: %d events, rank mass %d (convention: owned ascent)' % (sum(owned_up.values()), up_mass))
def verifier(name):
    return subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, name), data('word.json.gz')], capture_output=True, text=True).stdout
os_, or_ = verifier('verify_strict.py'), verifier('verify_relaxed.py')
rej = [int(x) for x in os_.split('indices')[1].split('\n')[0].split()]
need(os_.strip().endswith('REJECTED_STRICT') and rej == up_idx and "['move nesting']" in os_, 'rejection control: the strict (predecessor) verifier rejects this word at exactly the %d owned-ascent events and nothing else' % len(rej))
need(or_.strip().endswith('ACCEPTED_RELAXED'), 'relaxed verifier (only the owned-move direction rule changed, paid |delta dim| either way) accepts every event')
# ---- (1b) the odd grid (framework change): certificate, heights, odd divisions, scans, the odd verifier -------
Smin = 1
for d_ in odd_dens: Smin = Smin * d_ // math.gcd(Smin, d_)
def val_(m, p_):
    c = 0
    while m % p_ == 0: m //= p_; c += 1
    return c
h3 = max([val_(d_, 3) for d_ in odd_dens] or [0]); h5 = max([val_(d_, 5) for d_ in odd_dens] or [0])
need(Smin == SC == 1125 and not bad_S and all(sm(d_, (3, 5)) for d_ in odd_dens) and (h3, h5) == (2, 3),
     'certificate: S = 1125 = 3^2 5^3 times every prefix row and every pre-ADD product has dyadic entries (0 failures over %d odd denominators); the 3-adic and 5-adic heights are %d and %d and no other prime occurs; S is minimal (the least common multiple of the odd parts of all denominators is %d)' % (len(odd_dens), h3, h5, Smin))
need(v2max == 24, 'width debt per unfinished context: 2-adic denominator height %d bits (odd part at most 1125, 10.1 bits), largest denominator of any row or product 2^%.2f; the coefficients are given by their own bit lengths below (numerators up to %d bits, denominators up to %d bits)' % (v2max, math.log2(dmax), nbits, dbits))
need(all(any(s_ % d_ for d_ in odd_dens) for s_ in (375, 225, 75, 45, 15, 25, 9, 1)), 'S = 375 (= 1125/3), 225 (= 1125/5), 75, 45, 15, 25, 9 and 1 are each insufficient (some odd denominator does not divide them)')
oddfinal = sum(1 for r in range(NR) if not all(dy(v) for v in row[r].values()))
need(oddfinal == 0, 'every one of the %d final rows (public and owned) has dyadic entries: no odd denominator survives to an output' % NR)
n_odd = sum(odd_events.values()); scans = 2 * n_odd
need((odd_events['SCALE'], odd_events['ADD'], odd_events['COPY'], n_odd, scans) == (64, 4079, 0, 4143, 8286),
     'odd divisions per call: %d SCALE and %d ADD events have an odd denominator = %d divisions = %d scans (one multiply-and-check, one division, each a least-significant-bit-first pass), listed separately from the reviewed scalar count' % (odd_events['SCALE'], odd_events['ADD'], n_odd, scans))
need(abs(math.log2(float(mass)) - 36.54) < 0.005 and 2 * (math.log2(10) + math.log2(float(mass))) < 80, 'largest l1 mass of S times a row or product at any prefix: 2^%.2f (the magnitude debt per unfinished context, scale included); 2 (log2 10 + %.2f) = %.2f < 80, so 80 t < d replaces the 82 t < d of the dyadic-caller-mass placeholder form' % (math.log2(float(mass)), math.log2(float(mass)), 2 * (math.log2(10) + math.log2(float(mass)))))
def vodd(*a):
    return subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'verify_host3_odd.py'), data('word.json.gz')] + [str(x) for x in a], capture_output=True, text=True)
v1125, v375, v225, v1 = vodd(1125), vodd(375), vodd(225), vodd(1)
need('PASS_HOST3' in v1125.stdout, 'odd verifier (verify_host3_odd.py: A-membership, |q|+1 < 2^16, S certificate on every prefix row and pre-ADD product, public rows dyadic) accepts the word at S = 1125')
need(v375.returncode != 0 and v375.stderr.strip().endswith('AssertionError: 36997') and v225.returncode != 0 and v225.stderr.strip().endswith('AssertionError: 1103') and v1.returncode != 0 and v1.stderr.strip().endswith('AssertionError: 2'), 'odd verifier rejects S = 375 at event 36997 and S = 225 at event 1103 (the two divisors of 1125 by 3 and by 5), and S = 1 at event 2; controls.py runs the other rejections')
H = W['hosted']; al, be = Q(H['alpha']), Q(H['beta']); a2, b2 = Q(H['alpha2']), Q(H['beta2']); DP = H['Dports']
live = W['live']; X = set(live); Y = {r + 112 for r in live}; X2 = H['X2']; Y2 = H['Y2']; X2s = set(X2); Y2s = set(Y2)
BP = [i for i in range(104) if i not in set(DP)]; dX = {live[i] for i in DP}
need(H['mode'] == 'mix-t0' and (al, be, a2, b2) == (-1, Q(1, 2), -1, 0) and len(DP) == len(set(DP)) == len(X2) == len(Y2) == 96 and len(BP) == 8 and not ((X2s | Y2s) & (X | Y)) and len(X2s | Y2s) == 192 and len(live) == len(W['ports']) == 104,
     'two port types: 96 ports in the two-chain form (second mains, plane 2 alpha2=%s beta2=%s) and 8 ports in the hosted form (pair alpha=%s beta=%s, t = %s, no second mains)' % (a2, b2, al, be, al * be))
x2of = dict(zip(X2, Y2)); bad = 0
for r in range(NR):
    if r >= n: ex = {}
    elif r in X: ex = {r: Q(1)} if r in dX else {r: Q(1), r + 112: al}
    elif r in Y: ex = {r - 112: Q(1), r: Q(1)} if r - 112 in dX else {r - 112: be, r: 1 + al * be}
    elif r in X2s: ex = {r: Q(1), x2of[r]: a2}
    elif r in Y2s: ex = {r: Q(1)}
    else: ex = {r: Q(1)}
    bad += row[r] != ex
need(bad == 0, 'endpoint exact on all %d public and owned rows: two-chain ports X=x, Y=x+y, X2=x2-y2, Y2=y2; hosted ports X=x-y, Y=(x+y)/2; helpers identity, owned empty' % NR)
for i, (r, q) in enumerate(zip(live, W['ports'])):
    if fr[W['initial'][r]] != [q] or dim[W['final'][r]] != 9 or dim[W['initial'][r + 112]] != 0 or sp[W['final'][r + 112]] != frozenset(x for x in range(512) if not (x & q).bit_count() % 2): raise SystemExit('FAIL main frames')
for i, x2, y2 in zip(DP, X2, Y2):
    r = live[i]
    if W['initial'][x2] != W['initial'][r] or W['final'][x2] != W['final'][r] or W['initial'][y2] != W['initial'][r + 112] or W['final'][y2] != W['final'][r + 112]: raise SystemExit('FAIL second main frames')
need(True, '104 literal central ports; the second mains of the 96 two-chain ports carry the same initial and final frame labels as the first mains (declared: same-label second mains)')
main = X | Y | X2s | Y2s
hel = Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in main)
need(min(hel) > 0 and all(sp[W['initial'][r]] < sp[W['final'][r]] for r in range(n) if r not in main), 'every helper strictly ascends (rank > 0); %d helpers, %d mains, %d public' % (sum(hel.values()), len(main), n))
print('  events', len(W['program']), 'public', n, 'owned roles', NO, 'peak owned', peak, 'owned lifetimes', life, 'dirty owned erasures', dirty, 'max |coefficient|', maxq)
W19 = json.load(gzip.open(data('prior_word_6919.json.gz'), 'rt')); WB = json.load(gzip.open(data('prior_word_6934.json.gz'), 'rt')); W32 = json.load(gzip.open(data('prior_word_6932.json.gz'), 'rt')); W31 = json.load(gzip.open(data('prior_word_6931.json.gz'), 'rt'))
need(peak == 43 and len(W['program']) == 71144 and n == 1461 and sum(hel.values()) == 1061 and len(WB['program']) == 71069 and len(WB['initial']) == 1452 and n - len(WB['initial']) == 9 and len(W['program']) - len(WB['program']) == 75, 'peak owned fields %d; events %d; public %d; helpers %d (the #6934 word, data/prior_word_6934.json.gz: events %d, public %d, helpers %d; nine public registers added (seven wires and two split tails), 145 events added and 70 removed)' % (peak, len(W['program']), n, sum(hel.values()), len(WB['program']), len(WB['initial']), len(WB['initial']) - 400))
def lives_of(Wx):
    st = {}; lf = Counter(); om = Counter()
    for e_ in Wx['program']:
        if e_[0] == 'INIT': st[e_[1]] = e_[2]
        elif e_[0] == 'CLEAR': lf[(st.pop(e_[1]), e_[2])] += 1
        elif e_[0] == 'MOVE' and e_[4]: om[(e_[2], e_[3])] += 1
    return lf, om
lfn, omn = lives_of(W); lfo, omo = lives_of(WB)
pkWB = 0; lvWB = 0
for e_ in WB['program']:
    if e_[0] == 'INIT': lvWB += 1; pkWB = max(pkWB, lvWB)
    elif e_[0] == 'CLEAR': lvWB -= 1
need(W['frames'] == WB['frames'] and lfn == lfo and omn == omo and sum(lfn.values()) == 54 and W['owned_fields'] == WB['owned_fields'] == 51 and sum(omn.values()) == sum(omo.values()),
     'owned side against the #6934 word: the same frame table (%d frames), the same %d owned lifetimes as a multiset of (initial frame, clear frame), the same multiset of %d owned MOVEs (a, b), the same %d owned fields; only the timing differs, so the peak of concurrent owned fields is %d here and %d there (retiming only)' % (len(W['frames']), sum(lfn.values()), sum(omn.values()), W['owned_fields'], peak, pkWB))

# ---- (1c) the move against the #6934 word: seven shared helper wires -------------------------------------------------
nold = len(WB['initial']); shn = n - nold
def renum(e):
    e = list(e); op = e[0]; f = lambda x: x + shn if x >= nold else x
    e[1] = f(e[1])
    if op in ('ADD', 'COPY'): e[2] = f(e[2])
    return tuple(e)
PA_ = [renum(e) for e in WB['program']]; PB_ = [tuple(e) for e in W['program']]
ca_, cb_ = Counter(PA_), Counter(PB_); rem_, add_ = ca_ - cb_, cb_ - ca_; com_ = ca_ & cb_
newh = set(range(nold, n)); dd_ = [len(b_) for b_ in W['frames']]
rA = Counter(e_[0] for e_ in rem_.elements()); aA = Counter(e_[0] for e_ in add_.elements())
tch = lambda e_: e_[1] in newh or (e_[0] in ('ADD', 'COPY') and e_[2] in newh)
need(all(W[k_] == WB[k_] for k_ in ('frames', 'live', 'hosted', 'ports')) and W['initial'][:nold] == WB['initial'] and W['final'][:nold] == WB['final'] and W['owned_fields'] == WB['owned_fields'],
     'against the #6934 word: frame table, live set, hosted pairs, ports, and the initial and final frame of each of the %d old public registers are identical; the %d owned register numbers move up by %d; %d helper registers are added (the endpoint check above covers their final rows)' % (nold, W['owned_fields'], shn, shn))
need(sum(rem_.values()) == 70 and dict(rA) == {'MOVE': 56, 'ADD': 14} and sum(add_.values()) == 145 and dict(aA) == {'ADD': 88, 'MOVE': 49, 'SCALE': 8},
     'multiset difference of the two event lists after renumbering: %d events removed (%d MOVE, %d ADD) and %d added (%d ADD, %d MOVE, %d SCALE); %d events are common' % (sum(rem_.values()), rA['MOVE'], rA['ADD'], sum(add_.values()), aA['ADD'], aA['MOVE'], aA['SCALE'], sum(com_.values())))
hm_ = Counter(e_[1] for e_ in add_.elements() if e_[0] == 'MOVE' and e_[1] in newh)
nha_ = sum(1 for e_ in add_.elements() if e_[0] == 'ADD' and tch(e_)); nom_ = sum(1 for e_ in add_.elements() if e_[0] == 'MOVE' and e_[1] not in newh)
need(all(tch(e_) for e_ in add_.elements() if e_[0] == 'ADD') and not any(tch(e_) for e_ in rem_.elements()) and sum(hm_.values()) == 21 and sorted(hm_.values()) == [1, 1, 2, 2, 3, 3, 3, 3, 3] and nom_ == 28,
     'every added ADD (%d) reads or writes one of the %d new registers (seven wires and two split tails: 21 MOVEs in all, %d counted, 3 per wire before the two splits); the other %d added MOVEs are chain steps of registers that lose intermediate stops; no removed event touches a new helper' % (nha_, len(newh), sum(hm_.values()), nom_))
rem_adds = [e_ for e_ in rem_.elements() if e_[0] == 'ADD']; Xs_ = set(W['live']); Ys_ = {r_ + 112 for r_ in W['live']}; X2_ = set(W['hosted']['X2']); Y2_ = set(W['hosted']['Y2']); mn_ = Xs_ | Ys_ | X2_ | Y2_
need(len(rem_adds) == 14 and all(e_[1] in mn_ and e_[2] in mn_ for e_ in rem_adds) and all(e_[1] in mn_ for e_ in rem_.elements() if e_[0] == 'MOVE'),
     'the %d removed ADDs are direct main-to-main contacts (both registers are mains: seven contacts, one forward and one mirror pair each) and all %d removed MOVEs are MOVEs of mains' % (len(rem_adds), rA['MOVE']))
cred_ = lambda e_: dd_[W['final'][e_]] - dd_[W['initial'][e_]]
hcr_ = sorted(cred_(h_) for h_ in newh)
spl_ = sorted((a_, b_) for a_ in newh for b_ in newh if a_ != b_ and W['final'][a_] == W['initial'][b_]); tails_ = {b_ for _, b_ in spl_}
mcr_ = sorted(cred_(h_) + sum(cred_(b_) for a_, b_ in spl_ if a_ == h_) for h_ in newh if h_ not in tails_)
partn_ = {h_: set() for h_ in newh}
for e_ in add_.elements():
    if e_[0] == 'ADD':
        if e_[1] in newh: partn_[e_[1]].add(e_[2])
        if e_[2] in newh: partn_[e_[2]].add(e_[1])
grp_ = {h_: {h_} | {b_ for a_, b_ in spl_ if a_ == h_} for h_ in newh if h_ not in tails_}
shared_ = all(set().union(*(partn_[x_] for x_ in g_)) & (Xs_ | Ys_) and set().union(*(partn_[x_] for x_ in g_)) & (X2_ | Y2_) for g_ in grp_.values())
need(all(sp[W['initial'][h_]] < sp[W['final'][h_]] and h_ not in mn_ for h_ in newh) and hcr_ == [1, 1, 7, 7, 7, 7, 8, 8, 9] and mcr_ == [7, 7, 8, 8, 8, 8, 9] and spl_ == [(1452, 1459), (1455, 1460)] and len(grp_) == 7 and all(cred_(b_) == 1 for b_ in tails_) and shared_ and Counter(e_[1] for e_ in add_.elements() if e_[0] == 'SCALE') == {1452: 2, 1455: 2, 1459: 2, 1460: 2},
     'the nine new registers are public non-main registers whose frames strictly ascend, credit ranks (dim final - dim initial) %s, rank mass %d; the two split pairs %s are plain splits (the second starts at the frame where the first ends, both credits at least 1, concatenated they cover the unsplit wire; merged credits %s); each of the seven wires is read or written by a first main (X or Y: F) and a second main (X2 or Y2: R): one wire, shared' % (hcr_, sum(hcr_), spl_, mcr_))
def lab_(P_, c_):
    cc_ = Counter(c_); seen_ = Counter(); out_ = []
    for e_ in P_:
        if cc_[e_] > 0: cc_[e_] -= 1; seen_[e_] += 1; out_.append((e_, seen_[e_]))
    return out_
def acc_(e_):
    op_ = e_[0]
    if op_ in ('MOVE', 'INIT', 'CLEAR', 'SCALE'): return [(e_[1], 'M')]
    if op_ == 'COPY': return [(e_[1], 'M'), (e_[2], 'R')]
    return [(e_[1], 'A'), (e_[2], 'R')]
def runs_(L_):
    sq_ = {}
    for e_, k_ in L_:
        for r_, c_ in acc_(e_): sq_.setdefault(r_, []).append((c_, (e_, k_)))
    out_ = {}
    for r_, sq in sq_.items():
        rr_ = []
        for c_, x_ in sq:
            if rr_ and rr_[-1][0] == c_ and c_ in 'RA': rr_[-1][1].add(x_)
            else: rr_.append((c_, {x_}))
        out_[r_] = [(c_, frozenset(st_)) for c_, st_ in rr_]
    return out_
RA_, RB_ = runs_(lab_(PA_, com_)), runs_(lab_(PB_, com_))
need(set(RA_) <= set(RB_) and all(RA_[r_] == RB_[r_] for r_ in RA_) and len(RA_) > 0,
     'reordering is legal: over the %d common events each of %d registers sees the same ordered sequence of access classes (MOVE, SCALE, INIT, CLEAR exclusive; ADD destination and ADD source taken as runs of sets, since adds into one destination commute and reads commute): 0 registers differ, so every read sees the value it saw in the #6934 word' % (sum(com_.values()), len(RA_)))
def mchains_(Wx, sh_):
    c_ = {}
    for e_ in Wx['program']:
        if e_[0] == 'MOVE':
            r_ = e_[1] + (sh_ if e_[1] >= nold else 0)
            if r_ not in c_: c_[r_] = [e_[2]]
            assert c_[r_][-1] == e_[2]; c_[r_].append(e_[3])
    return c_
cA_, cB_ = mchains_(WB, shn), mchains_(W, 0)
chg_ = [r_ for r_ in set(cA_) | set(cB_) if cA_.get(r_) != cB_.get(r_)]
def issub_(a_, b_):
    it_ = iter(a_); return bool(a_ and b_ and a_[0] == b_[0] and a_[-1] == b_[-1] and all(x_ in it_ for x_ in b_))
mass_ = lambda c_: sum(abs(dd_[y_] - dd_[x_]) for x_, y_ in zip(c_, c_[1:]))
oth_ = [r_ for r_ in chg_ if r_ not in newh]
need(all(issub_(cA_[r_], cB_[r_]) and mass_(cA_[r_]) == mass_(cB_[r_]) for r_ in oth_) and set(chg_) - set(oth_) == newh and len(oth_) == 28,
     'the MOVE chain of each of the %d other registers that changed (the partners of the seven contacts) is an endpoint-preserving subsequence of its chain in the #6934 word with the same total rank change (a serial merge of consecutive ascending MOVEs of the same register); the new helpers are the only registers with a new chain' % len(oth_))
sc = [e for e in W['program'] if e[0] == 'SCALE']
hX = {live[i] for i in BP}; gpos = {}
for k_, e in enumerate(W['program']):
    if e[0] == 'SCALE' and e[1] in hX and e[1] not in gpos: gpos[e[1]] = (k_, Q(e[2]))
first_use_ = {}
for k_, e in enumerate(W['program']):
    for r_ in ([e[1]] if e[0] in ('MOVE', 'INIT', 'CLEAR', 'SCALE') else [e[1], e[2]]): first_use_.setdefault(r_, []).append(k_)
need(len(gpos) == 8 and {v for _, v in gpos.values()} == {Q(1, 2)} and all(first_use_[r_][0] == gpos[r_][0] for r_ in gpos), 'gauge: each of the 8 hosted-port mains X has its first SCALE by 1/2, and that SCALE is the first event that touches it (events %s): the SCALE comes before the first use of the register. The clause of the dyadic words that the first 8 events are the 8 gauge SCALEs is %s for this word (the first %d events: %s); the gauge is in any case covered by the exact endpoint X = x - y, Y = (x + y)/2' % (sorted(k for k, _ in gpos.values()), 'literally true' if sorted(k for k, _ in gpos.values()) == list(range(8)) else 'not literally true, and is replaced by this statement', 8, [e_[0] + ':' + str(e_[1]) for e_ in W['program'][:8]]))

# ---- (2) the roots ------------------------------------------------------------------------------
RC = ldmod(os.path.join(HERE, 'root_check.py'), 'rootcheck')
RA = json.load(open(data('root_A.json'))); RB = json.load(open(data('root_B.json'))); RB0 = json.load(open(data('control_root_B_other_gauge.json')))
need(RC.run(RA) == [], 'type A root (two #6833 chain roots, t = 0): 21/21 units of each chain regenerated, cross Gram 0, SPEC-level identities, each stage variable once and affine')
Rm = copy.deepcopy(RA); Rm['X'][5][3] = str(Q(Rm['X'][5][3]) + 1)
need(RC.blocks(Rm) != [] and RC.run(Rm) != [], 'wrong-root control A: a wrong X entry in the type A root FAILS (%s)' % RC.blocks(Rm)[:1])
hsrc = open(os.path.join(HERE, 'root_check_hosted.py')).read()
def hosted_run(RR):
    """root_check_hosted.py (the checker of the hosted root of #6889) executed on RR; returns its list of failed lines."""
    code = hsrc.replace("R=json.load(open(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'data','root.json')))", 'R=_R').replace('sys.exit(1 if bad else 0)', '')
    ns = {'_R': RR, 'sys': sys, '__file__': os.path.join(HERE, 'root_check_hosted.py'), 'print': lambda *a, **k: None}
    exec(compile(code, 'root_check_hosted.py', 'exec'), ns)
    return ns['bad']
need(hosted_run(RB) == [], 'type B root (the hosted root of #6889, t = -1/2, n = 38, pairs (-1, 1/2)): every line of its checker passes')
Rm = copy.deepcopy(RB); Rm['X'][5][3] = str(Q(Rm['X'][5][3]) + 1)
need(hosted_run(Rm) != [], 'wrong-root control B: a wrong X entry in the hosted root FAILS its checker')
Rm = copy.deepcopy(RA); Rm['X'][7], Rm['X'][9] = Rm['X'][9], Rm['X'][7]
need(RC.run(Rm) != [], 'wrong-root control: two unit rows swapped in the type A root FAIL')

# ---- (3) the joint caller -----------------------------------------------------------------------
J = json.load(open(data('caller.json')))
pM = 2147483629
IM = next(pow(g, (pM - 1) // 4, pM) for g in range(2, 99) if pow(g, (pM - 1) // 2, pM) == pM - 1); HALF = (pM + 1) // 2
fm = lambda x: (lambda f: f.numerator % pM * pow(f.denominator, pM - 2, pM) % pM)(Q(x))
def root_pairs(root):
    dot = lambda a_, b_: sum(Q(u) * Q(v) for u, v in zip(a_, b_) if Q(u) and Q(v)); out = {}
    for k, s_ in enumerate(root['stages']):
        u, v = s_['units']; out[k + 1] = (dot(root['Y'][u], root['X'][v]), dot(root['Y'][v], root['X'][u]))
    return out
mask_inc = lambda root, c: [int(c in set(s['mask'])) for s in root['stages']]
PB = root_pairs(RB); TA, TB = J['types']['A'], J['types']['B']
need(set(PB.values()) == {(al, be)} and len(PB) == 18, 'every one of the 18 hosted stages of root B has the word\'s pair (alpha,beta)=(%s,%s), read from the root' % (al, be))
need(all(TA['diagonal'][c][2:] == mask_inc(RA, c) for c in range(40)) and all(TB['diagonal'][c][2:] == mask_inc(RB, c) for c in range(38)), 'caller target exponents equal the mask incidence of the root of their type, field by field and stage by stage (type A 40 roles, type B 38 roles)')
need(Q(TA['alpha2']) == a2 and Q(TA['beta2']) == b2 and all(str(e[3][2]) == str(al) and str(e[3][3]) == str(be) for e in J['events'] if e[0] == 'J'), 'type A plane-2 parameters and every joint contact\'s hosted pair equal the word\'s')
need(J['roles'] == 78 and J['stages'] == 18 and sum(e[0] == 'J' for e in J['events']) == 18, 'joint caller: 78 roles (type A 0-39, type B 40-77), 18 joint contacts (one per stage; HOST2 at the two-chain ports and HOST at the hosted ports in one event)')
need(sorted(TA['ports']) == sorted(DP) and sorted(TB['ports']) == BP and len(TA['ports']) == 96 and len(TB['ports']) == 8, 'port types of the caller equal the word\'s: type A = the 96 two-chain ports, type B = the 8 hosted ports')
Jp = copy.deepcopy(J); Jp['types']['A']['ports'][0], Jp['types']['B']['ports'][0] = Jp['types']['B']['ports'][0], Jp['types']['A']['ports'][0]
need(sorted(Jp['types']['A']['ports']) != sorted(DP) or sorted(Jp['types']['B']['ports']) != BP, 'swapped-assignment control: exchanging the types of one two-chain port and one hosted port in the caller breaks the match with the word')
NRr = J['roles']
def target(Jc, role, qv, Dv):
    t, off = (Jc['types']['A'], 0) if role < 40 else (Jc['types']['B'], 40); dg = t['diagonal'][role - off]
    c = pow(qv, dg[0] % 4, pM)
    for k, bit in enumerate(dg[2:]):
        if bit: c = c * Dv[k + 1] % pM
    return c
def replay(Jc, qv, Dv, a2_=a2, pairs=PB, types='AB'):
    Rm_ = [[int(i == j) for j in range(NRr)] for i in range(NRr)]; qi = pow(qv, pM - 2, pM); seen = []
    for e in Jc['events']:
        tag = e[0]
        if tag == 'J':
            st = e[1]; seen.append(st); d = Dv[st]
            if 'A' in types:
                src, dst, x2, y2 = e[2]
                Rm_[dst] = [(a_ + qi * b_) % pM for a_, b_ in zip(Rm_[dst], Rm_[src])]
                Rm_[x2] = [(a_ + fm(a2_) * qv % pM * b_) % pM for a_, b_ in zip(Rm_[x2], Rm_[y2])]
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
    if seen != list(range(1, 19)): return 10 ** 6
    roles = [r for r in range(NRr) if ('A' in types and r < 40) or ('B' in types and r >= 40)]
    return sum(Rm_[i][j] != (target(Jc, i, qv, Dv) if i == j else 0) for i in roles for j in range(NRr))
rnd = random.Random(11); tot = cnt = 0
for qv in (1, IM, pM - 1, pM - IM):
    for _ in range(3):
        Dv = {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}; tot += replay(J, qv, Dv); cnt += 1
need(tot == 0, 'composition: the ONE joint stream (78 roles, one stage value per stage common to both types) replays to the block-diagonal target at all four central characters (%d evaluations, 0 bad of %d entries each; all cross-type blocks are 0)' % (cnt, NRr * NRr))
for ty in 'AB':
    t2 = sum(replay(J, qv, {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}, types=ty) for qv in (1, IM, pM - 1, pM - IM))
    need(t2 == 0, 'type %s alone replays to its own target at the four characters' % ty)
Dv = {s_: rnd.randrange(2, pM) for s_ in range(1, 19)}
def rej(Jc=J, **kw): return replay(Jc, IM, Dv, **kw)
def mut(f):
    Jm = copy.deepcopy(J); f(Jm); return Jm
idx = lambda Jc, pred: next(i for i, e in enumerate(Jc['events']) if pred(e))
first = lambda tag, op: (lambda e: e[0] == tag and e[1] == op)
ctr = [('type A wrong alpha2', rej(a2_=Q(1)))]
for nm, fn in (('type B alpha sign', lambda x: x.__setitem__(0, -x[0])), ('type B beta sign', lambda x: x.__setitem__(1, -x[1])), ('type B pair swapped', lambda x: x.reverse())):
    pm = {k: list(v) for k, v in PB.items()}; fn(pm[13]); ctr.append((nm + ' at stage 13', rej(pairs=pm)))
ctr.append(('type B root in the other gauge', rej(pairs=root_pairs(RB0))))
for ty in 'AB':
    ctr.append(('type %s deleted idle' % ty, rej(mut(lambda Jm: Jm['events'].pop(idx(Jm, first(ty, 'IDLE_ONE')))))))
    ctr.append(('type %s deleted query' % ty, rej(mut(lambda Jm: Jm['events'].pop(idx(Jm, first(ty, 'QUERY')))))))
    def flip(Jm):
        j0 = idx(Jm, lambda e: e[0] == 'J'); k = max(i for i in range(j0) if Jm['events'][i][0] == ty and Jm['events'][i][1] == 'LAMBDA'); Jm['events'][k][3] *= -1
    ctr.append(('type %s flipped LAMBDA before the first contact' % ty, rej(mut(flip))))
for nm, b in ctr: print('   control %-52s -> %d bad' % (nm, b))
need(all(b > 0 for _, b in ctr), 'controls: wrong alpha2, a wrong or other-gauge hosted pair, a deleted idle, a deleted query, a flipped LAMBDA at a contact, in each type: all rejected by the replay')
for ty, role in (('A', 3), ('B', 3)):
    Jm = mut(lambda x: x['types'][ty]['diagonal'][role].__setitem__(2 + 4, x['types'][ty]['diagonal'][role][2 + 4] ^ 1))
    need(rej(Jm) > 0 and Jm['types'][ty]['diagonal'][role][2:] != (mask_inc(RA, role) if ty == 'A' else mask_inc(RB, role)), 'mask control, type %s: a wrong mask bit in the caller target fails the replay and the mask comparison' % ty)
need(rej(mut(lambda x: x['events'].insert(idx(x, lambda e: e[0] == 'J'), ['A', 'ADD', 5, 45, '1']))) > 0 and rej(mut(lambda x: x['events'].insert(idx(x, lambda e: e[0] == 'J'), ['B', 'ADD', 45, 5, '1']))) > 0, 'cross-type controls: one ADD from a type A role into a type B role, and the other way, are rejected: the types do not interact')
def swapst(x):
    js = [e for e in x['events'] if e[0] == 'J']; js[0][1], js[1][1] = js[1][1], js[0][1]
def rot(x):
    e = x['events'][idx(x, lambda e: e[0] == 'J')]; a = e[2]; e[2] = [a[0], a[1], a[3], a[2]]
need(rej(mut(swapst)) > 0 and rej(mut(rot)) > 0, 'controls: two joint contacts with exchanged stages, and exchanged second-plane roles in a contact, are rejected')
print('  note: the composition reads each root only through its masks and pairs; wrong X or Y entries are caught by the root checkers above')

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
    dot = lambda a_, b_: sum(Q(u) * Q(v) for u, v in zip(a_, b_) if Q(u) and Q(v)); planes = []
    for s_ in S_:
        u, v = s_['units']; planes.append(2 if dot(Yr[u], Xr[v]) == 0 and dot(Yr[v], Xr[u]) == 0 else 1)
    return F, planes, RR['N'] - sum(len(s_['units']) for s_ in S_)
def outer(F, planes, thin, ports, nst=18):
    T = Counter(); P = Counter(); hc = Counter()
    for ms, host in F:
        T[8 * len(ms) + 1] += ports
        for k in host: hc[k] += 1
        run = 0; prev = None
        for k in ms:
            if k in host:
                if run: P[8 * run] += ports
                run = 0; prev = None; continue
            if prev is not None and k == prev + 1: run += 1
            else:
                if run: P[8 * run] += ports
                run = 1
            prev = k
        if run: P[8 * run] += ports
    for k in range(nst):
        if hc[k] > 2 * planes[k]: P[8] += ports * (hc[k] - 2 * planes[k])
    P[1] += ports * thin
    return T, P
def census(Wx):
    nx = len(Wx['initial']); lx = set(Wx['live']); mx = lx | {r_ + 112 for r_ in lx}
    if Wx.get('hosted', {}).get('X2'): mx |= set(Wx['hosted']['X2']) | set(Wx['hosted']['Y2'])
    dx = [len(b_) for b_ in Wx['frames']]
    return (Counter(dx[Wx['final'][r_]] - dx[Wx['initial'][r_]] for r_ in range(nx) if r_ not in mx), Counter(abs(dx[e_[3]] - dx[e_[2]]) for e_ in Wx['program'] if e_[0] == 'MOVE'))
def invoice_roots(hel_, paid_, roots):
    T = Counter(); P = Counter()
    for RR, ports in roots:
        F, pl, th = root_fields(RR); t_, p_ = outer(F, pl, th, ports); T.update(t_); P.update(p_)
    for r, k in hel_.items(): T[r] += 18 * k
    for r, k in paid_.items(): P[r] += 18 * k
    return T, P
bi = json.load(open(data('base_invoice.json')))
T0 = Counter({int(k): v for k, v in bi['targets'].items()}); P0 = Counter({int(k): v for k, v in bi['paid'].items()})
chain = [(list(range(18)), list(range(18)))] + [(list(range(i, 9)), [i]) for i in range(9)] + [(list(range(9, 10 + m)), [9 + m]) for m in range(9)] + [([], [])]
Tc_, Pc_ = outer(chain, [1] * 18, 3, 104)
Tb, Pb = Counter(Tc_), Counter(Pc_)
for r_, k_ in bi['helpers'].items(): Tb[int(r_)] += 18 * k_
for r_, k_ in bi['local_paid'].items(): Pb[int(r_)] += 18 * k_
need(+Tb == T0 and +Pb == P0, 'control: the same code rebuilds the #6833 invoice term for term')
kb = kappa(T0, P0)
need(abs(kb - D(bi['kappa_literal'])) < D('1e-17'), 'control: #6833 kappa %s' % str(kb)[:20])
nA, nB = len(TA['ports']), len(TB['ports']); cnt_ty = {'A': nA, 'B': nB}
T = Counter(); P = Counter(); nj = 0
for e in J['events']:
    if e[0] == 'J': nj += 1; T.update(hel); P.update(paid)
    elif e[1] == 'QUERY': P[1] += cnt_ty[e[0]]
    elif e[1] == 'IDLE_ONE': P[8 * len(e[3])] += cnt_ty[e[0]]
for ty, t in (('A', TA), ('B', TB)):
    for dg in t['diagonal']: T[int(dg[0] % 2) + 8 * sum(dg[2:])] += cnt_ty[ty]
T2, P2 = invoice_roots(hel, paid, ((RA, nA), (RB, nB)))
need(nj == 18 and +T == +T2 and +P == +P2, 'the invoice recounted from the emitted joint events equals the invoice rebuilt from the TWO ROOTS (per type, per port count) plus the word, term for term (18 native calls, helpers and paid jobs once per call)')
kn = kappa(T, P); Tn, Pn = T, P
need(abs(kn - D('0.00362701882959514439757905558830')) < D('1e-25'), 'new kappa %s' % str(kn)[:26])
S = sum(r * (Tn.get(r, 0) - Pn.get(r, 0)) for r in set(Tn) | set(Pn))
need(S == 1520, 'rank-mass surplus S = %d (104*34 - 36*56, net of the 56 owned-ascent mass per call)' % S)
Wp = json.load(gzip.open(data('prior_word_6911.json.gz'), 'rt')); hp, pp = census(Wp)
Tp, Pp = invoice_roots(hp, pp, ((RA, nA), (RB, nB))); kp = kappa(Tp, Pp)
need(abs(kp - D('0.0035194870841667550646')) < D('1e-17'), 'control: the #6911 word through the two roots (96 + 8 ports) and the same code gives %s (its crossing)' % str(kp)[:26])
W17 = json.load(gzip.open(data('prior_word_6917.json.gz'), 'rt')); h17, p17 = census(W17)
T17, P17 = invoice_roots(h17, p17, ((RA, nA), (RB, nB))); k17 = kappa(T17, P17)
need(abs(k17 - D('0.0035301044238995680260')) < D('1e-17'), 'control: the #6917 word through the two roots (96 + 8 ports) and the same code gives %s (its crossing)' % str(k17)[:26])
h19, p19 = census(W19); T19, P19 = invoice_roots(h19, p19, ((RA, nA), (RB, nB))); k19 = kappa(T19, P19)
need(abs(k19 - D('0.0035952826938257874494')) < D('1e-17'), 'control: the #6919 word (data/prior_word_6919.json.gz) through the two roots (96 + 8 ports) and the same code gives %s (the crossing of #6919)' % str(k19)[:26])
h31, p31 = census(W31); T31, P31 = invoice_roots(h31, p31, ((RA, nA), (RB, nB))); k31 = kappa(T31, P31)
need(abs(k31 - D('0.0036041048151080063894')) < D('1e-17'), 'control: the #6931 word (data/prior_word_6931.json.gz) through the two roots (96 + 8 ports) and the same code gives %s' % str(k31)[:26])
h32, p32 = census(W32); T32_, P32_ = invoice_roots(h32, p32, ((RA, nA), (RB, nB))); k32_ = kappa(T32_, P32_)
need(abs(k32_ - D('0.0036210586137481460837')) < D('1e-17'), 'control: the #6932 word (data/prior_word_6932.json.gz) through the two roots (96 + 8 ports) and the same code gives %s' % str(k32_)[:26])
h34, p34 = census(WB); Tb0, Pb0 = invoice_roots(h34, p34, ((RA, nA), (RB, nB))); kbase = kappa(Tb0, Pb0)
need(abs(kbase - D('0.0036238597350766513')) < D('1e-17'), 'control: the #6934 word (data/prior_word_6934.json.gz, the word this one is compared with) through the two roots (96 + 8 ports) and the same code gives %s' % str(kbase)[:26])
need(sum(r * (Tb0.get(r, 0) - Pb0.get(r, 0)) for r in set(Tb0) | set(Pb0)) == 1520, 'the #6934 word has rank-mass surplus S = 1520 as well')
def no_E(T_):
    T2_ = Counter(T_); T2_[1] -= 192; return T2_
kE_ = kappa(no_E(Tn), Pn); kEb_ = kappa(no_E(Tb0), Pb0)
print('  E CREDIT (declared premise, see README): rank-1 productive fields T[1] = %d over the 18 calls here (%d in the #6934 word); with the 192 rank-1 targets removed and paid unchanged, kappa = %s here (%s with them, %.2f%%) and %s for the #6934 word (%s with them, %.2f%%)' % (Tn[1], Tb0[1], str(kE_)[:10], str(kn)[:10], 100 * float(kE_ / kn - 1), str(kEb_)[:10], str(kbase)[:10], 100 * float(kEb_ / kbase - 1)))
e_roles = [i_ for i_, dg_ in enumerate(TA['diagonal']) if int(dg_[0] % 2) + 8 * sum(dg_[2:]) == 1]; e_roles_b = [i_ for i_, dg_ in enumerate(TB['diagonal']) if int(dg_[0] % 2) + 8 * sum(dg_[2:]) == 1]
nE_ = len(e_roles) * nA + len(e_roles_b) * nB
need(e_roles == [19, 39] and e_roles_b == [] and nE_ == 192 == 2 * nA, 'E count from the invoice: the type A root has %d empty-mask fields (roles %s), credited by the rule rank 1 + 8 |mask| = 1, over %d two-chain ports = %d productive rank-1 targets; the hosted type B root has %d; the credit removed below is exactly this count' % (len(e_roles), e_roles, nA, nE_, len(e_roles_b)))
need(Tn[1] >= 192 and Tb0[1] >= 192 and str(kEb_)[:9] == '0.0031631' and kE_ < kn, 'E credit control: removing 192 rank-1 targets from T, paid unchanged, gives %s for the #6934 word (about .0031631, the earlier reading) and %s for this word' % (str(kEb_)[:10], str(kE_)[:10]))
print('  gain over the #6934 word: %.5f%% (exactly kappa_new / kappa_6934 - 1 = %s)' % (100 * float(kn / kbase - 1), str(kn / kbase - 1)[:12]))
need(str(100 * (kn / kbase - 1))[:5] == '0.087', 'the gain over the #6934 word (crossing %s) is +0.087%% (ratio - 1 = %s); no other comparison is made' % (str(kbase)[:22], str(kn / kbase - 1)[:12]))
dT = {r: Tn[r] - Tb0[r] for r in sorted(set(Tn) | set(Tb0)) if Tn[r] != Tb0[r]}; dPp = {r: Pn[r] - Pb0[r] for r in sorted(set(Pn) | set(Pb0)) if Pn[r] != Pb0[r]}
print('  T change against the #6934 word (all 18 calls):', dT); print('  P change against the #6934 word (all 18 calls):', dPp)
need(dT == {1: 36, 7: 72, 8: 36, 9: 18} and dPp == {1: -342, 2: -180, 3: 198, 4: 18, 5: 90, 6: 54, 7: 36} and sorted(r_ for r_ in hcr_ for _ in range(18)) == sorted(r_ for r_, c_ in dT.items() for _ in range(c_)) and sum(r * c for r, c in dT.items()) == sum(r * c for r, c in dPp.items()),
     'T and P change against the #6934 word, per call (all 18 calls divided by 18): T %s (productive fields by rank: the credits of the nine new registers), P %s (paid jobs by rank: per MOVE, the merged main MOVEs and the new helper MOVEs); the rank mass of T and of P changes by the same amount (%d), so S stays %d' % ({r: c // 18 for r, c in dT.items()}, {r: c // 18 for r, c in dPp.items()}, sum(r * c for r, c in dT.items()) // 18, S))
dDT = sum(c * r * D(r).ln() for r, c in dT.items()) / 18; dDP = -sum(c * r * D(r).ln() for r, c in dPp.items()) / 18
need(dDT + dDP < 0, 'the whole gain is in the kernel term D = sum (T - P) r ln r, per call: the T change moves it by %s and the P change by %s (net %s; the rank mass S stays %d). The word differs from the #6934 word by the seven moves counted in step (1c), so this is the net effect of those seven moves and two splits' % (str(dDT)[:8], str(dDP)[:8], str(dDT + dDP)[:8], S))
nlA = sum(1 for e in J['events'] if e[0] == 'A' and e[1] == 'LAMBDA'); nlB = sum(1 for e in J['events'] if e[0] == 'B' and e[1] == 'LAMBDA')
lam_cost = nA * nlA + nB * nlB
need((nlA, nlB) == (124, 82) and S - lam_cost < 0, 'review question, stated plainly: type A callers have %d LAMBDA events and type B callers %d; if each LAMBDA had to be paid as a rank-1 job per port, the cost is %d*%d + %d*%d = %d and S = %d - %d = %d < 0, so no crossing exists; kappa rests on pricing LAMBDA as ordinary work, as in every caller of this line' % (nlA, nlB, nA, nlA, nB, nlB, lam_cost, S, lam_cost, S - lam_cost))

# ---- (5) raw bound, growth, alphabet --------------------------------------------------------------
def swaps(sel):
    wanted = set(range(len(sel))); return len(list(zip(sorted(set(sel) - wanted), sorted(wanted - set(sel)))))
def shim(ty):
    t = J['types'][ty]; off = t['offset']; ev = []
    for e in J['events']:
        if e[0] == 'J': ev.append(['HOST', e[1]])
        elif e[0] == ty:
            e = list(e[1:])
            if e[0] in ('ADD', 'SWAP', 'QUERY'): e[1] -= off; e[2] -= off
            else: e[1] -= off
            ev.append(e)
    return dict(events=ev, roles=t['roles'], ambient_rank=J['ambient_rank'], diagonal=t['diagonal'])
def rest_of(C, ports):
    ev = C['events']; roles = C['roles']; amb = C['ambient_rank']; mx = mn = mp = 0
    for role, (qp, zero, *sel) in enumerate(C['diagonal']):
        axes = ([0] if qp else []) + [a for st, y in enumerate(sel, 1) if y for a in range(9 + 8 * (st - 1), 9 + 8 * st)]
        k = swaps(axes); mx += 2 * k * ports; mn += 2 * bool(qp) * ports; mp += int(qp == -1) * ports
    ie = 0; qn = qph = 0
    for e in ev:
        if e[0] == 'IDLE_ONE': ie += 2 * swaps([a for st in e[2] for a in range(9 + 8 * (st - 1), 9 + 8 * st)]) * ports
        elif e[0] == 'QUERY': qn += 2 * ports; qph += int(e[3] == -1) * ports
    return 32 * roles * ports * len(ev) + sum(e[0] == 'QUERY' for e in ev) * 16 * ports + roles * ports * 26 + (mx + mn + mp) * 1000 + ie * 1000 + (qn + qph) * 1000
rest = rest_of(shim('A'), nA) + rest_of(shim('B'), nB)
allow = upper = 0
for e in W['program']:
    if e[0] in ('INIT', 'CLEAR'): allow += 2
    elif e[0] == 'SCALE':
        q = Q(e[2]); a_, d_ = abs(q.numerator), q.denominator
        allow += 2 * (abs(a_.bit_length() - d_.bit_length()) + int(q < 0)); upper += 4 * (a_.bit_length() + d_.bit_length() + 1)
    elif e[0] in ('ADD', 'COPY'):
        q = Q(e[3]); a_, d_ = abs(q.numerator), q.denominator
        allow += 2 * (3 + a_.bit_length() - 1 + bin(a_).count('1') + d_.bit_length() - 1); upper += 4 * (a_.bit_length() + bin(a_).count('1') + d_.bit_length() + 1)
routes = (sum(paid.values()) + 2 * sum(hel.values()) + 208 + 2 * nA + 4 * 104 + 4 * nA + 4 * life) * 1000     # boundary terms of the second planes only at the two-chain ports
per_call = allow + routes; per_up = upper + routes
raw_lit, raw_act, raw_rev = 18 * 10 ** 7 + rest, 18 * per_call + rest, 18 * per_up + rest
print('  raw pieces: per-port terms = %d; per call (word scalar + routes) = %d (allowance) or %d (reviewed upper) against the displayed 10^7' % (rest, per_call, per_up))
need((raw_lit, raw_act, raw_rev) == (802809952, 815970652, 832255648) and max(raw_lit, raw_act, raw_rev) < 10 ** 9, 'raw bound, all three definitions below 10^9: literal %d, actual per-call work %d, reviewed scalar upper %d (margins %d, %d, %d); the %d odd divisions are inside these bit-length terms (argued) and are also listed as %d scans per call' % (raw_lit, raw_act, raw_rev, 10 ** 9 - raw_lit, 10 ** 9 - raw_act, 10 ** 9 - raw_rev, n_odd, scans))
debit = 1000 * lam_cost
need(raw_rev + debit == 844815648 and raw_rev + debit < 10 ** 9, 'conservative recharge: the reviewed upper count %d already contains every LAMBDA event of the caller (through the envelope 32 * roles * ports * len(events); rest_of: the events of each type include its LAMBDA events); the second check of #6913 counts the LAMBDA translations a second time, %d LAMBDA jobs at 1,000 each = %d for this mix, on top of the whole reviewed bound; with the scale applied once at the boundary (no per-call charge) the total is %d, below 10^9 (margin %d), so no reading of the raw count exceeds 10^9 with this caller; no term of the outer ledger reads either count' % (raw_rev, lam_cost, debit, raw_rev + debit, 10 ** 9 - raw_rev - debit))
sc_cost = 4 * (SC.bit_length() + 1 + 1) + 4 * (1 + SC.bit_length() + 1)      # one SCALE by S = 1125 at entry and one by 1/1125 at exit, at the reviewed upper rate 4 * (bits(a) + bits(d) + 1)
per_in = 18 * n * sc_cost
need(sc_cost == 104 and raw_rev + per_in == 834990640 and raw_rev + per_in + debit == 847550640 and raw_rev + per_in + debit < 10 ** 9, 'per-input scale reading (every one of the %d public registers scaled by 1125 at entry and unscaled at exit on each of the 18 calls, %d x %d x 18 = %d, an upper reading): upper %d; with the second LAMBDA count %d, below 10^9 (margin %d)' % (n, sc_cost, n, per_in, raw_rev + per_in, raw_rev + per_in + debit, 10 ** 9 - raw_rev - per_in - debit))
Rm_paid = sum(r_ * v_ for r_, v_ in Pn.items())
print('  CONSTANT SUBSTITUTION (FINITE-PRECOMPILATION.md:278-283): events %d; scalar allowance %d; reviewed scalar upper %d; routes %d; per call %d or %d; raw upper %d (allowance) or %d (reviewed upper); paid rank mass R = %d; growth bound 2^(raw + R f) = 2^(%d + %d f) on the conservative count' % (len(W['program']), allow, upper, routes, per_call, per_up, raw_act, raw_rev, Rm_paid, raw_rev, Rm_paid))
src_ep = open(os.path.join(HERE, 'retained', 'runtime', 'endpoint.py')).read()
need(not any(t_ in src_ep for t_ in ('10**9', '10 ** 9', '10**7', '10 ** 7', '1e9')), 'the outer ledger source contains no scalar-work or 10^9 term')
def logsum(Wx): return sum(math.log2(1 + float(abs(Q(e_[3])))) for e_ in Wx['program'] if e_[0] in ('ADD', 'COPY'))
l02 = logsum(WB)
print('  GROWTH: events %d (#6934 word %d); sum of log2(1+|q|) over the ADD coefficients %d (#6934 word %d) against 416000; peak |row entry| on any prefix 2^%.2f; peak row denominator 2^%d; coefficient bits numerator <= %d, denominator <= %d; largest |q| %s' % (len(W['program']), len(WB['program']), round(logq), round(l02), math.log2(float(pmax)), dmaxb - 1, nbits, dbits, maxq))
big_ = sum(1 for e_ in W['program'] if e_[0] in ('ADD', 'COPY') and abs(Q(e_[3])) >= 2 ** 12)
need(round(logq) == 82828 and round(l02) == 82770 and maxq == Q(227445, 8) and (nbits, dbits) == (24, 19) and big_ == 10 and maxq + 1 < 2 ** 16, 'sum of log2(1+|q|) %d (below 416000; the #6934 word %d); largest |q| %s = %.1f with |q| + 1 < 2^16; coefficient bits %d / %d (the #6934 word: largest |q| %s, same widths); %d ADD events here have |q| >= 2^12' % (round(logq), round(l02), maxq, float(maxq), nbits, dbits, max(abs(Q(e_[3])) for e_ in WB['program'] if e_[0] in ('ADD', 'COPY')), big_))
cf_ = [(abs(Q(e_[3])).numerator, Q(e_[3]).denominator, i_) for i_, e_ in enumerate(W['program']) if e_[0] in ('ADD', 'COPY')]
num_max = max(cf_, key=lambda t_: (t_[0], -t_[2])); den_max = max(cf_, key=lambda t_: (t_[1], -t_[2])); n40k = sum(1 for t_ in cf_ if t_[0] > 40864)
need(num_max[0].bit_length() == nbits == 24 and den_max[1].bit_length() == dbits == 19 and (num_max[2], den_max[2], n40k) == (252, 2798, 864), 'temporaries: the coefficient numerators of the ADD events reach %d bits (largest numerator %d, first at event %d) and their denominators %d bits (largest denominator %d, at event %d); %d ADD events have a numerator above 40864 (the #6934 word: the same 24 / 19 bits). A multiply-by-a, check-divisibility, divide-by-b temporary holds a times a stored value, so its coefficient factor is %d bits wide, not 16' % (num_max[0].bit_length(), num_max[0], num_max[2], den_max[1].bit_length(), den_max[1], den_max[2], n40k, nbits))
cb = max(abs(Q(e_[4] if e_[1] == 'ADD' else e_[3])).numerator.bit_length() for e_ in J['events'] if e_[1] in ('ADD', 'SCALE')); cd = max(Q(e_[4] if e_[1] == 'ADD' else e_[3]).denominator.bit_length() for e_ in J['events'] if e_[1] in ('ADD', 'SCALE'))
need((cb, cd) == (9, 8) and round(math.log2(float(pmax)), 2) == 23.55 and dmaxb - 1 == 27, 'coefficients: caller coefficient bits %d / %d (SCALE 256 and the gauge 1/128, in the type B caller, unchanged; the type A caller now uses only +-1, +-2, SCALE -1 and SWAP); word: largest |q| %s, peak |row entry| 2^%.2f, peak row denominator 2^%d (odd part at most 1125)' % (cb, cd, maxq, math.log2(float(pmax)), dmaxb - 1))
nid = Counter(e_[0] for e_ in J['events'] if e_[1] == 'IDLE_ONE')
need(nid == Counter({'A': 32, 'B': 68}), 'IDLE_ONE events: %d in the type A caller, %d in the type B caller (one-site idles priced as whole H8 jobs; declared, inherited)' % (nid['A'], nid['B']))
Y2set = set(Y2)
oy = [i_ for i_, e_ in enumerate(W['program']) if e_[0] == 'ADD' and e_[1] >= n and e_[2] in Y2set]
ox = [i_ for i_, e_ in enumerate(W['program']) if e_[0] == 'ADD' and e_[1] >= n and e_[2] in X]
ox2 = [i_ for i_, e_ in enumerate(W['program']) if e_[0] == 'ADD' and e_[1] >= n and e_[2] in X2s]
oyY = [i_ for i_, e_ in enumerate(W['program']) if e_[0] == 'ADD' and e_[1] >= n and e_[2] in Y]
def owned_reads(Wx):
    nx = len(Wx['initial']); Hx = Wx['hosted']; lx = Wx['live']; Xs = set(lx); Ys = {r_ + 112 for r_ in lx}; X2x = set(Hx['X2']); Y2x = set(Hx['Y2'])
    return tuple(sum(1 for e_ in Wx['program'] if e_[0] == 'ADD' and e_[1] >= nx and e_[2] in grp) for grp in (Y2x, Xs, X2x, Ys))
ob = owned_reads(WB)
def peak_owned(Wx):
    live_, pk_ = 0, 0
    for e_ in Wx['program']:
        if e_[0] == 'INIT': live_ += 1; pk_ = max(pk_, live_)
        elif e_[0] == 'CLEAR': live_ -= 1
    return pk_
peakb = peak_owned(WB)
need(peakb == 40 == pkWB and peak_owned(W) == peak == 43, 'peak owned fields: %d in the #6934 word, %d in this word (same number of owned lifetimes %d against %d)' % (peakb, peak, life, sum(e_[0] == 'INIT' for e_ in WB['program'])))
need((len(oy), len(ox), len(ox2), len(oyY)) == (8, 7, 1, 0) and ob == (8, 7, 1, 0), 'owned registers reading a main register: %d events read Y2 %s, %d read X %s, %d read X2 %s, none reads Y: %d events in all (the #6934 word: %d, %d, %d, %d for Y2, X, X2, Y, %d in all); unchanged by the new registers; declared with A6; peak owned fields %d' % (len(oy), oy, len(ox), ox, len(ox2), ox2, len(oy) + len(ox) + len(ox2), ob[0], ob[1], ob[2], ob[3], sum(ob), peak))


# ---- (6) outer conditions ----------------------------------------------------------------------
E, SE, OUT = ldmod(os.path.join(HERE, 'retained', 'runtime', 'intervals.py'), 'intervals'), ldmod(os.path.join(HERE, 'retained', 'runtime', 'second_intervals.py'), 'second_intervals'), ldmod(os.path.join(HERE, 'retained', 'runtime', 'endpoint.py'), 'endpoint')
BITF = json.load(open(os.path.join(HERE, 'retained', 'bit', 'FRAGMENT-BIT-ADMISSION.json')))
need(hashlib.sha256(open(os.path.join(HERE, 'retained', 'bit', 'FRAGMENT-BIT-ADMISSION.json'), 'rb').read()).hexdigest() == '86955dcd74bc3fa1a940419474d45054fa7b0366b71b242568680366923d9311' and BITF['status'] == 'PASS_TWO_FRAGMENTS_BIT_ORDINARY_00376669' and Q(BITF['ordinary_admitted']) == PIN, 'BIT pin %s = ordinary_admitted of the pinned #6726 admission file (status %s); not re-derived here' % (float(PIN), BITF['status']))
KAPPA, TESTED = Q('.00362701882'), Q('.00362701882007')
LOW, UP = Q('.003627018829595'), Q('.003627018829596')
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
cutoff, floor, power, offset = 11, 12, 1920, Q(1, 7); LPMIN, LP = 2225, 2226
tt_ = 1 - TESTED; target, paidm = E.moment(Tq, tt_), E.moment(Pq, tt_)
alpha = E.divide(paidm, target); gamma = E.divide(E.moment(Pq, tt_ + offset), E.mul(E.power(cutoff, offset), target))
delta = E.divide((Q(sum(Tq.values()) * floor),) * 2, E.mul(E.power(cutoff, TESTED), target))
reserve, decay = Q(1, 10 ** 27), Q(31, 32)
need(alpha[1] < 1 - reserve and gamma[1] < decay and delta[1] < decay, 'tail ratios (interval engine): alpha %.12f gamma %.4f delta %.4f (cutoff 11, floor 12, offset 1/7, power 1920)' % (float(alpha[1]), float(gamma[1]), float(delta[1])))
normalized = 1 / (1 + power * reserve) + 4 * decay ** power
need(normalized < 1, 'composite bound (predecessor pricing.py:211): 1/(1+power*reserve) + 4*decay^power < 1 at power 1920 (excess over the first term %.2e)' % float(4 * decay ** power))
maxT = max(Tq); carrier = max(maxT, int(J['ambient_rank']))     # the compiler fit m*c <= N (FP:111-114) is on the literal carrier, 9 base rows + 8 per stage = 153
quarter = E.power(carrier, Q(power, 4) * TESTED); factor = E.mul(E.mul(quarter, quarter), E.mul(quarter, quarter))
eta = E.scale(E.divide((Q(1), Q(1)), factor), tt_)
need(eta[0] > Q(63, 64) ** LP and factor[1] < 2 ** LP and cutoff ** 64 < floor ** 63 and 2 * (cutoff ** power) ** 64 <= (carrier ** power) ** 63, 'compiler complement capacity and shifted exits at logarithm power %d on the literal carrier %d (the largest target rank is %d)' % (LP, carrier, maxT))
lp_ = LPMIN + 40
while eta[0] > Q(63, 64) ** (lp_ - 1): lp_ -= 1
need(lp_ == LPMIN and Q(63, 64) ** (LPMIN - 1) > eta[0], 'logarithm power: on the literal carrier 153 the smallest admissible value at this price is %d (%d fails), written as %d (it is a free parameter, LOG-MAJORANT.md:110-122); the written value %d is the one the compiler and outer ledger lines above use' % (lp_, LPMIN - 1, LP, LP))
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
Hw = step * hi_; Kbits = math.log2(power) + power * math.log2(carrier) + 2 * math.log2(Hw + 1)      # K_star = v m (H+1)^2, v = the chronological power 1920, m = carrier^v (#6901 eq. (4a))
CALLER_MASS_BITS, PATH_HEIGHT_BITS = 120.35, 157       # QUOTED, not recomputed here: majorants of the #6932 caller, computed by a script that is not part of this package
c_exact = 2 * max(v2max + PATH_HEIGHT_BITS, math.log2(float(mass)) + CALLER_MASS_BITS)
need(c_exact == 362 and abs(Kbits - 14072.3) < 0.1 and math.log2(c_exact + 1) + Kbits < Hw, 'K_star = v m (H+1)^2 with v = %d, m = %d^%d: log2 K_star = %.1f bits at the written H (computed here); with the QUOTED caller majorants (mass <= 2^%.2f, path-maximum height 157 bits; computed on the #6932 caller, not recomputed on this package\'s caller) the per-context bound is height <= %d + 157 = %d bits and magnitude <= %.2f + %.2f = %.2f bits, so c = %d and %d K_star < 2^H holds with %.3e bits to spare; status: argued from #6901 eq. (4a) and lines 299-304, computed, not reviewed' % (power, carrier, power, Kbits, CALLER_MASS_BITS, v2max, v2max + PATH_HEIGHT_BITS, math.log2(float(mass)), CALLER_MASS_BITS, math.log2(float(mass)) + CALLER_MASS_BITS, c_exact, c_exact + 1, Hw - math.log2(c_exact + 1) - Kbits))
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
    ('FRAMEWORK CHANGE (this package): odd gate scalars', 'the scalar alphabet of the native word. Dyadic coefficients and SCALE units (local.py:146,149, the verifier copies, native.py:65) become elements and units of A = Z[1/2, 1/3, 1/5], with |q|+1 < 2^16 kept, a declared certificate S = 3^e 5^g (here 1125 = 3^2 5^3) for which S times every prefix row and every pre-ADD product is dyadic, and dyadic public output rows; execution multiplies every root input by S, divides by the odd part of each denominator after a checked divisibility, and divides by S at the exit. The word has %d odd divisions (%d SCALE, %d ADD), %d scans per call. Maintainers must accept this clause; it is not a result of this package. PROOF.md names the changed clauses, the replacement and the penalty; exactness is conditional on exact child returns.' % (n_odd, odd_events['SCALE'], odd_events['ADD'], scans)),
    ('new form: per-port root', 'unchanged from the #6934 word: type A (96 ports) is the two-chain root of #6902 (two #6833 roots, t = 0, n = 40), type B (8 ports) is the hosted root of #6889 (t = -1/2, n = 38); the caller is block diagonal over 78 roles, with one stage variable per stage common to both types and 18 joint contacts, each one native event serving both types (HOST2 at the type A ports, HOST at the type B ports). Type A fails the same three family lines as #6902 (t != 0, alpha and beta dyadic units, strongly connected); type B passes every line of its checker. No new failing line.'),
    ('new form', 'unchanged: the 8 hosted ports keep the hosted form with no second mains (their X and Y are single planes); the 96 other ports have second mains with the same frame labels as the first mains; 400 mains in total (96 x 4 + 8 x 2). The gauge SCALE 1/2 of the hosted mains is informational here (the endpoint X = x - y, Y = (x + y)/2 covers it).'),
    ('new form: type A caller blocks', 'the constant blocks of the type A caller (maximal runs of ADD, SCALE -1 and SWAP between two nonconstant events or joint contacts) are the blocks of #6912 (CubeJerry); check_caller_blocks.py proves each changed block has the same 40 x 40 integer matrix and the joint caller the same 78 x 78 matrix at eight points; the type B caller is unchanged and not covered by that rewrite.'),
    ('convention (A6, load-bearing)', 'owned ascent: 23 owned rises (rank mass 56) against native.py:55 / local.py:126; peak owned %d; owned registers read mains: Y2 %d events, X %d events, X2 %d events (%d events in all; %d in the #6934 word). check_a6.py runs the rises as in #6914 and the width-2 phase test of #6930. No ascent, no word.' % (peak, len(oy), len(ox), len(ox2), len(oy) + len(ox) + len(ox2), sum(ob))),
    ('new form: seven main contacts moved onto shared helper wires', 'against the #6934 word (data/prior_word_6934.json.gz, replayed exactly here): public %d against %d registers (%d new registers: seven wires, each read by F and R mains through one register, and two plain split tails); %d events removed (%d main MOVEs, %d direct contact ADDs) and %d added; the frame table, the 54 owned lifetimes (as multisets) and the 51 owned fields are unchanged, the peak of concurrent owned fields is %d against %d (a retiming of owned INIT and CLEAR, commutations only); T and P differ as printed above (the rank mass of both changes by the same amount per call, S = 1520); the reorder of commuting events is checked register by register in step (1c).' % (n, nold, len(newh), sum(rem_.values()), rA['MOVE'], rA['ADD'], sum(add_.values()), peak, pkWB)),
    ('verifier', 'endpoint literal native.py:75-77 / local.py:168: the target is X=x, Y=x+y, X2=x2-y2, Y2=y2 at 96 ports and X=x-y, Y=(x+y)/2 at 8 ports; verify_host3_odd.py replaces the dyadic clauses as above (diff against verify_host3_dyadic.py: the helper lines, the SCALE clause, the ADD and COPY clause with the S certificate, the public-row clause).'),
    ('verifier', 'events %d, public %d, owned roles %d, lifetimes %d, peak owned %d against local.py:52,54,103 and pricing.py:84-87 literals; per-call scalar work %d against the displayed 10^7 (pricing.py:93); coefficient bits %d/%d against 8/7 (pricing.py:96-97); the event count is declared as this package\'s own bound (the retained 26,000 cap of other packages is not used).' % (len(W['program']), n, NO, life, peak, per_call, nbits, dbits)),
    ('convention', 'LAMBDA (%d + %d = 206 events by type), IDLE_ONE (32 + 68 events) as in the #6934 word; not on main; the price of LAMBDA is a review question (above).' % (nlA, nlB)),
    ('assumption', 'dirty owned erasure (%d erasures): the owned_erasure assumption, unchanged.' % dirty)):
    print('  [%s] %s' % (cls, what))
need(True, 'departures listed')
print('PASS_P104_MAIN_WIRE_NATIVE')
