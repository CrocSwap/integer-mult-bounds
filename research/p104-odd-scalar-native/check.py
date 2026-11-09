#!/usr/bin/env python3
"""The mixed-port native word with odd gate scalars 1/3 and 1/5 (a declared framework change): exact replay of the word over A = Z[1/2, 1/3, 1/5] with the certificate S = 225, both roots, the joint caller,
the complete invoice and the outer constants.  Standard library only (plus the retained interval engines).
python3 -I -B check.py     (writes nothing)
Steps: (1) event-by-event exact replay of data/word.json.gz with the endpoint of each port type, the alphabet A, the odd certificate S (every prefix row and every pre-ADD product), heights, scans; the odd verifier and its rejections;
(2) both roots with failing controls; (3) the joint caller (78 roles, block diagonal, one stage value per stage) at the four central characters, with wrong-root, wrong-port-type and swapped-assignment controls;
(4) the invoice recounted from the emitted events and rebuilt from the two roots, with the baseline word, the #6919, #6917 and #6911 words and #6833 as controls; (5) raw bound by three definitions, the LAMBDA recharge, the root-scale and
per-input scale readings, growth; (6) BIT pins, interval engines, strictification, compiler and outer ledger; departures.  Prints PASS_P104_ODD_SCALAR_NATIVE.
(physical.py, physical_exact.py, caller_physical.py, native_maps.py, second_engine.py, mutants.py, reorder_check.py, division_pass.py, controls.py, ordinary.py are the other commands.)"""
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
SC = 225                                   # the declared certificate: S = 3^2 * 5^2
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
need(Smin == SC == 225 and not bad_S and all(sm(d_, (3, 5)) for d_ in odd_dens) and (h3, h5) == (2, 2),
     'certificate: S = 225 = 3^2 5^2 times every prefix row and every pre-ADD product has dyadic entries (0 failures over %d odd denominators); the 3-adic and 5-adic heights are %d and %d and no other prime occurs; S is minimal (the least common multiple of the odd parts of all denominators is %d)' % (len(odd_dens), h3, h5, Smin))
need(v2max == 15, 'width debt per unfinished context: 2-adic denominator height %d bits (odd part at most 225, 7.8 bits), largest denominator of any row or product 2^%.2f, magnitude 37.48 bits above (scale included); coefficients need |a| <= 40864 (16 bits)' % (v2max, math.log2(dmax)))
need(all(any(s_ % d_ for d_ in odd_dens) for s_ in (75, 45, 15, 25, 9, 1)), 'S = 75, 45, 15, 25, 9 and 1 are each insufficient (some odd denominator does not divide them)')
oddfinal = sum(1 for r in range(NR) if not all(dy(v) for v in row[r].values()))
need(oddfinal == 0, 'every one of the %d final rows (public and owned) has dyadic entries: no odd denominator survives to an output' % NR)
n_odd = sum(odd_events.values()); scans = 2 * n_odd
need(odd_events['SCALE'] == 59 and odd_events['ADD'] == 2942 and odd_events['COPY'] == 0 and n_odd == 3001 and scans == 6002,
     'odd divisions per call: %d SCALE and %d ADD events have an odd denominator = %d divisions = %d scans (one multiply-and-check, one division, each a least-significant-bit-first pass), listed separately from the reviewed scalar count' % (odd_events['SCALE'], odd_events['ADD'], n_odd, scans))
need(abs(math.log2(float(mass)) - 37.48) < 0.005, 'largest l1 mass of S times a row or product at any prefix: 2^%.2f (the magnitude debt per unfinished context, scale included)' % math.log2(float(mass)))
def vodd(*a):
    return subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'verify_host3_odd.py'), data('word.json.gz')] + [str(x) for x in a], capture_output=True, text=True)
v225, v75, v1 = vodd(225), vodd(75), vodd(1)
need('PASS_HOST3' in v225.stdout, 'odd verifier (verify_host3_odd.py: A-membership, |q|+1 < 2^16, S certificate on every prefix row and pre-ADD product, public rows dyadic) accepts the word at S = 225')
need(v75.returncode != 0 and v75.stderr.strip().endswith('AssertionError: 26563') and v1.returncode != 0 and v1.stderr.strip().endswith('AssertionError: 50'), 'odd verifier rejects S = 75 at event 26563 (SCALE -1/45) and S = 1 at event 50; controls.py runs the other rejections')
ro = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'reorder_check.py')], capture_output=True, text=True).stdout
need(ro.strip().endswith('PASS_REORDER') and 'FAIL' not in ro, 'reorder_check.py (run here): no pair of events that share a register with a writer changed order between the word before the 20 stops and the stop word (66,895 matched events); 120 rewritten and 76 tuned events are covered by the exact replay only')
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
W19 = json.load(gzip.open(data('prior_word_6919.json.gz'), 'rt')); WB = json.load(gzip.open(data('baseline_word.json.gz'), 'rt'))
need(peak == 36 and len(W['program']) == 67079 and n == 1451 and sum(hel.values()) == 1051, 'peak owned fields %d; events %d; public %d; helpers %d (the baseline word, data/baseline_word.json.gz: events %d, public %d, helpers %d)' % (peak, len(W['program']), n, sum(hel.values()), len(WB['program']), len(WB['initial']), len(WB['initial']) - 400))
sc = [e for e in W['program'] if e[0] == 'SCALE']
hX = {live[i] for i in BP}; gpos = {}
for k_, e in enumerate(W['program']):
    if e[0] == 'SCALE' and e[1] in hX and e[1] not in gpos: gpos[e[1]] = (k_, Q(e[2]))
print('  gauge SCALEs of the 8 hosted-port mains X (informational; declared clause of the dyadic words "the first 8 SCALEs are the gauge 1/2" is not used here): first SCALE of each at events %d to %d, values %s; the gauge is covered by the exact endpoint X = x - y, Y = (x + y)/2' % (min(k for k, _ in gpos.values()), max(k for k, _ in gpos.values()), sorted({str(v) for _, v in gpos.values()})))

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
need(abs(kn - D('0.00362105861374814608')) < D('1e-17'), 'new kappa %s' % str(kn)[:26])
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
Wbase = WB; hb_, pb_ = census(Wbase); Tb0, Pb0 = invoice_roots(hb_, pb_, ((RA, nA), (RB, nB))); kbase = kappa(Tb0, Pb0)
need(abs(kbase - D('0.0036041048151080063894')) < D('1e-17'), 'control: the baseline word (data/baseline_word.json.gz, the word this one is compared with) through the two roots (96 + 8 ports) and the same code gives %s' % str(kbase)[:26])
print('  gain over the baseline word: %.5f%% (exactly kappa_new / kappa_baseline - 1 = %s)' % (100 * float(kn / kbase - 1), str(kn / kbase - 1)[:12]))
need(str(100 * (kn / kbase - 1))[:5] == '0.470', 'the gain over the baseline word (crossing %s) is +0.470%% (ratio - 1 = %s)' % (str(kbase)[:22], str(kn / kbase - 1)[:12]))
dT = {r: Tn[r] - Tb0[r] for r in sorted(set(Tn) | set(Tb0)) if Tn[r] != Tb0[r]}; dPp = {r: Pn[r] - Pb0[r] for r in sorted(set(Pn) | set(Pb0)) if Pn[r] != Pb0[r]}
print('  T change against the baseline word (all 18 calls):', dT); print('  P change against the baseline word (all 18 calls):', dPp)
need(dT == {2: 36, 3: 126, 4: 18, 5: 36, 6: 126, 9: -162} and dPp == {1: -1404, 2: 702} and sum(r * c for r, c in dT.items()) == 0 and sum(r * c for r, c in dPp.items()) == 0,
     'T and P change against the baseline word, per call (all 18 calls divided by 18): T %s (ten more productive fields), P %s (78 paid jobs of rank 1 become 39 of rank 2); the rank mass of T and of P is unchanged (S stays %d)' % ({r: c // 18 for r, c in dT.items()}, {r: c // 18 for r, c in dPp.items()}, S))
dDT = sum(c * r * D(r).ln() for r, c in dT.items()) / 18; dDP = -sum(c * r * D(r).ln() for r, c in dPp.items()) / 18
need(round(float(-dDT), 2) == 55.24 and abs(dDP + 39 * 2 * D(2).ln()) < D('1e-30'), 'the whole gain is in the kernel term D = sum (T - P) r ln r, per call: the ten new helper registers lower it by %s (T change), the 39 merged stops by %s (P change: 39 jobs of rank 2 at 2 ln 2 each, the jobs of rank 1 cost nothing, ln 1 = 0); the rank mass S stays %d' % (str(-dDT)[:7], str(-dDP)[:7], S))
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
need((raw_lit, raw_act, raw_rev) == (962308192, 972123664, 985187200) and max(raw_lit, raw_act, raw_rev) < 10 ** 9, 'raw bound, all three definitions below 10^9: literal %d, actual per-call work %d, reviewed scalar upper %d (margins %d, %d, %d); the 3,001 odd divisions are inside these bit-length terms (argued) and are also listed as %d scans per call' % (raw_lit, raw_act, raw_rev, 10 ** 9 - raw_lit, 10 ** 9 - raw_act, 10 ** 9 - raw_rev, scans))
debit = 1000 * lam_cost
need(raw_rev + debit == 997747200 and raw_rev + debit < 10 ** 9, 'conservative recharge: the reviewed upper count %d already contains every LAMBDA event of the caller (through the envelope 32 * roles * ports * len(events); rest_of: the events of each type include its LAMBDA events); the second check of #6913 counts the LAMBDA translations a second time, %d LAMBDA jobs at 1,000 each = %d for this mix, on top of the whole reviewed bound; with the scale applied once at the root (no per-call charge) the total is %d, below 10^9 (margin %d); no term of the outer ledger reads either count' % (raw_rev, lam_cost, debit, raw_rev + debit, 10 ** 9 - raw_rev - debit))
sc_cost = 4 * (SC.bit_length() + 1 + 1) + 4 * (1 + SC.bit_length() + 1)      # one SCALE by 225 at entry and one by 1/225 at exit, at the reviewed upper rate 4 * (bits(a) + bits(d) + 1)
per_in = 18 * n * sc_cost
need(sc_cost == 80 and raw_rev + per_in == 987276640 and raw_rev + per_in + debit == 999836640 and raw_rev + per_in + debit < 10 ** 9, 'per-input scale reading (every one of the %d public registers scaled by 225 at entry and unscaled at exit on each of the 18 calls, %d x %d x 18 = %d, an upper reading): upper %d; with the second LAMBDA count %d, below 10^9 (margin %d)' % (n, sc_cost, n, per_in, raw_rev + per_in, raw_rev + per_in + debit, 10 ** 9 - raw_rev - per_in - debit))
Rm_paid = sum(r_ * v_ for r_, v_ in Pn.items())
print('  CONSTANT SUBSTITUTION (FINITE-PRECOMPILATION.md:278-283): events %d; scalar allowance %d; reviewed scalar upper %d; routes %d; per call %d or %d; raw upper %d (allowance) or %d (reviewed upper); paid rank mass R = %d; growth bound 2^(raw + R f) = 2^(%d + %d f) on the conservative count' % (len(W['program']), allow, upper, routes, per_call, per_up, raw_act, raw_rev, Rm_paid, raw_rev, Rm_paid))
src_ep = open(os.path.join(HERE, 'retained', 'runtime', 'endpoint.py')).read()
need(not any(t_ in src_ep for t_ in ('10**9', '10 ** 9', '10**7', '10 ** 7', '1e9')), 'the outer ledger source contains no scalar-work or 10^9 term')
def logsum(Wx): return sum(math.log2(1 + float(abs(Q(e_[3])))) for e_ in Wx['program'] if e_[0] in ('ADD', 'COPY'))
l02 = logsum(WB)
print('  GROWTH: events %d (baseline word %d); sum of log2(1+|q|) over the ADD coefficients %d (baseline %d) against 416000; peak |row entry| on any prefix 2^%.2f; peak row denominator 2^%d; coefficient bits numerator <= %d, denominator <= %d; largest |q| %s' % (len(W['program']), len(WB['program']), round(logq), round(l02), math.log2(float(pmax)), dmaxb - 1, nbits, dbits, maxq))
big_ = sum(1 for e_ in W['program'] if e_[0] in ('ADD', 'COPY') and abs(Q(e_[3])) >= 2 ** 12)
need(round(logq) == 71153 and maxq == Q(40864) and (nbits, dbits) == (16, 16) and big_ == 45 and maxq + 1 < 2 ** 16, 'sum of log2(1+|q|) %d (below 416000; the baseline word %d); largest |q| %s with |q| + 1 < 2^16; coefficient bits %d / %d (the baseline word: largest |q| %s); %d ADD events here have |q| >= 2^12' % (round(logq), round(l02), maxq, nbits, dbits, max(abs(Q(e_[3])) for e_ in WB['program'] if e_[0] in ('ADD', 'COPY')), big_))
cb = max(abs(Q(e_[4] if e_[1] == 'ADD' else e_[3])).numerator.bit_length() for e_ in J['events'] if e_[1] in ('ADD', 'SCALE')); cd = max(Q(e_[4] if e_[1] == 'ADD' else e_[3]).denominator.bit_length() for e_ in J['events'] if e_[1] in ('ADD', 'SCALE'))
need((cb, cd) == (9, 8) and round(math.log2(float(pmax)), 2) == 25.64 and dmaxb - 1 == 18, 'coefficients: caller coefficient bits %d / %d (SCALE 256 and the gauge 1/128, unchanged); word: largest |q| %s, peak |row entry| 2^%.2f, peak row denominator 2^%d (odd part at most 225)' % (cb, cd, maxq, math.log2(float(pmax)), dmaxb - 1))
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
need(peakb == 36 and peak_owned(W) == peak, 'peak owned fields: %d in the baseline word, %d in this word (same number of owned lifetimes %d against %d)' % (peakb, peak, life, sum(e_[0] == 'INIT' for e_ in WB['program'])))
need((len(oy), len(ox), len(ox2), len(oyY)) == (8, 9, 2, 0) and ob == (8, 9, 2, 0), 'owned registers reading a main register: %d events read Y2 %s, %d read X %s, %d read X2 %s, none reads Y (the baseline word: %d, %d, %d, %d for Y2, X, X2, Y); the same kinds and number of read as in the baseline word; declared with A6; peak owned fields %d' % (len(oy), oy, len(ox), ox, len(ox2), ox2, ob[0], ob[1], ob[2], ob[3], peak))


# ---- (6) outer conditions ----------------------------------------------------------------------
E, SE, OUT = ldmod(os.path.join(HERE, 'retained', 'runtime', 'intervals.py'), 'intervals'), ldmod(os.path.join(HERE, 'retained', 'runtime', 'second_intervals.py'), 'second_intervals'), ldmod(os.path.join(HERE, 'retained', 'runtime', 'endpoint.py'), 'endpoint')
BITF = json.load(open(os.path.join(HERE, 'retained', 'bit', 'FRAGMENT-BIT-ADMISSION.json')))
need(hashlib.sha256(open(os.path.join(HERE, 'retained', 'bit', 'FRAGMENT-BIT-ADMISSION.json'), 'rb').read()).hexdigest() == '86955dcd74bc3fa1a940419474d45054fa7b0366b71b242568680366923d9311' and BITF['status'] == 'PASS_TWO_FRAGMENTS_BIT_ORDINARY_00376669' and Q(BITF['ordinary_admitted']) == PIN, 'BIT pin %s = ordinary_admitted of the pinned #6726 admission file (status %s); not re-derived here' % (float(PIN), BITF['status']))
KAPPA, TESTED = Q('.00362105861'), Q('.0036210586107')
LOW, UP = Q('.003621058613748'), Q('.003621058613749')
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
cutoff, floor, power, offset = 11, 12, 1920, Q(1, 7); LPMIN, LP = 2222, 2223
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
need(lp_ == LPMIN and Q(63, 64) ** (LPMIN - 1) > eta[0] and Q(63, 64) ** 2212 > eta[0], 'logarithm power: on the literal carrier 153 the smallest admissible value at this price is %d (%d fails), written as %d (it is a free parameter, LOG-MAJORANT.md:110-122); the 2212 written for the baseline word does not suffice for this word' % (lp_, LPMIN - 1, LP))
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
    ('FRAMEWORK CHANGE (this package): odd gate scalars', 'the scalar alphabet of the native word. Dyadic coefficients and SCALE units (local.py:146,149, the verifier copies, native.py:65) become elements and units of A = Z[1/2, 1/3, 1/5], with |q|+1 < 2^16 kept, a declared certificate S = 3^e 5^g (here 225) for which S times every prefix row and every pre-ADD product is dyadic, and dyadic public output rows; execution multiplies every root input by S once, divides by the odd part of each denominator after a checked divisibility, and divides by S at the exit. Words with %d odd divisions (%d SCALE, %d ADD), %d scans per call. Maintainers must accept this clause; it is not a result of this package. PROOF.md names the changed clauses, the replacement and the penalty; exactness is conditional on exact child returns.' % (n_odd, odd_events['SCALE'], odd_events['ADD'], scans)),
    ('new form: per-port root', 'unchanged from the baseline word: type A (96 ports) is the two-chain root of #6902 (two #6833 roots, t = 0, n = 40), type B (8 ports) is the hosted root of #6889 (t = -1/2, n = 38); the caller is block diagonal over 78 roles, with one stage variable per stage common to both types and 18 joint contacts, each one native event serving both types (HOST2 at the type A ports, HOST at the type B ports). Type A fails the same three family lines as #6902 (t != 0, alpha and beta dyadic units, strongly connected); type B passes every line of its checker. No new failing line.'),
    ('new form', 'unchanged: the 8 hosted ports keep the hosted form with no second mains (their X and Y are single planes); the 96 other ports have second mains with the same frame labels as the first mains; 400 mains in total (96 x 4 + 8 x 2). The gauge SCALE 1/2 of the hosted mains is informational here (the endpoint X = x - y, Y = (x + y)/2 covers it).'),
    ('convention (A6, load-bearing)', 'owned ascent: 23 owned rises (rank mass 56) against native.py:55 / local.py:126; peak owned %d; owned registers read mains: Y2 %d events, X %d events, X2 %d events (%d events in all, as in the baseline word). No ascent, no word.' % (peak, len(oy), len(ox), len(ox2), len(oy) + len(ox) + len(ox2))),
    ('new form: helper splits and merged stops', 'against the baseline word (data/baseline_word.json.gz, replayed exactly here): ten more helper registers (public %d against %d; T per call rank 2 +2, rank 3 +7, rank 4 +1, rank 5 +2, rank 6 +7, rank 9 -9; kernel term %s) and 39 merged stops (78 paid jobs of rank 1 replaced by 39 of rank 2 on the same frames; kernel term %s); the rank mass of T and of P is unchanged, S = 1520. Twenty of the 39 stops come from a reordering of commuting events (reorder_check.py, from the two stage words in data/). The helper-split lemma is Ali Romman (#5599); its application to the shared native word is CubeJerry (#6916). The splits, sinks, valves, flips and deletions of the baseline word are inherited with it.' % (n, len(WB['initial']), str(dDT)[:7], str(dDP)[:7])),
    ('verifier', 'endpoint literal native.py:75-77 / local.py:168: the target is X=x, Y=x+y, X2=x2-y2, Y2=y2 at 96 ports and X=x-y, Y=(x+y)/2 at 8 ports; verify_host3_odd.py replaces the dyadic clauses as above (diff against verify_host3_dyadic.py: the helper lines, the SCALE clause, the ADD and COPY clause with the S certificate, the public-row clause).'),
    ('verifier', 'events %d, public %d, owned roles %d, lifetimes %d, peak owned %d against local.py:52,54,103 and pricing.py:84-87 literals; per-call scalar work %d against the displayed 10^7 (pricing.py:93); coefficient bits %d/%d against 8/7 (pricing.py:96-97).' % (len(W['program']), n, NO, life, peak, per_call, nbits, dbits)),
    ('convention', 'LAMBDA (%d + %d = 206 events by type), IDLE_ONE (32 + 68 events) as in the baseline word; not on main; the price of LAMBDA is a review question (above).' % (nlA, nlB)),
    ('assumption', 'dirty owned erasure (%d erasures): the owned_erasure assumption, unchanged.' % dirty)):
    print('  [%s] %s' % (cls, what))
need(True, 'departures listed')
print('PASS_P104_ODD_SCALAR_NATIVE')
