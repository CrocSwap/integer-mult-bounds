#!/usr/bin/env python3
"""What the word is made of, counted on the word and compared with the #6919 word (the ten further splits), the #6917 word and the #6911 word (standard library).  python3 -I -B cover_check.py
Counts the two port types (96 with second mains, 8 hosted), the events that touch second mains or the hosted ports, and runs controls on a random-evaluation replay (mod 2^61-1):
a wrong port type, a swapped assignment of two ports, and for sampled events a wrong weight (x2), a missing event and an event taken twice, are all rejected."""
import gzip, json, os, random
from collections import Counter
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
def load(n): return json.load(gzip.open(os.path.join(HERE, 'data', n), 'rt'))
new, old, w11, w19 = load('word.json.gz'), load('prior_word_6917.json.gz'), load('prior_word_6911.json.gz'), load('prior_word_6919.json.gz')
H = new['hosted']; X2 = H['X2']; Y2 = H['Y2']; live = new['live']; DP = H['Dports']
X = set(live); Y = {r + 112 for r in live}; M1 = X | Y; M2 = set(X2) | set(Y2); n = len(new['initial'])
BP = [i for i in range(104) if i not in set(DP)]
P = new['program']; lo = next(i for i, e in enumerate(P) if e[0] == 'MOVE'); hi = max(i for i, e in enumerate(P) if e[0] == 'MOVE'); Po = old['program']
hel_n = [r for r in range(n) if r not in M1 and r not in M2]
no = len(old['initial']); mo = set(old['live']) | {r + 112 for r in old['live']} | set(old['hosted']['X2']) | set(old['hosted']['Y2'])
print('  #6917 word: events %d, public %d, MOVEs %d' % (len(Po), no, sum(e[0] == 'MOVE' for e in Po)))
print('  this word : events %d, public %d (%d mains, %d helpers), MOVEs %d' % (len(P), n, len(M1) + len(M2), len(hel_n), sum(e[0] == 'MOVE' for e in P)))
need(len(DP) == 96 and len(BP) == 8 and len(M2) == 192 and len(M1 | M2) == 400 and n == 1441 and len(hel_n) == 1041, 'two port types: 96 ports with second mains and 8 hosted ports (no second mains): %d mains, %d helpers, %d public (the #6919 word: 400 mains, %d helpers, %d public; the 10 extra registers are the split pieces counted below)' % (len(M1 | M2), len(hel_n), n, len(w19['initial']) - 400, len(w19['initial'])))
mv_by = Counter()
for e in P:
    if e[0] == 'MOVE': mv_by['second main' if e[1] in M2 else 'first main' if e[1] in M1 else 'owned' if e[1] >= n else 'helper'] += 1
need(mv_by['first main'] > mv_by['second main'] > 0, 'each register pays its own moves: first-plane mains %d MOVEs, second-plane mains %d MOVEs (no move is shared or fused)' % (mv_by['first main'], mv_by['second main']))
need(all(new['initial'][x2] == new['initial'][live[i]] and new['final'][x2] == new['final'][live[i]] and new['initial'][y2] == new['initial'][live[i] + 112] and new['final'][y2] == new['final'][live[i] + 112] for i, x2, y2 in zip(DP, X2, Y2)), 'second mains carry the same initial and final frame labels as the first mains of their port (declared)')
touch = [i for i, e in enumerate(P) if e[0] == 'ADD' and (e[1] in M2 or e[2] in M2)]
hmains = {live[i] for i in BP} | {live[i] + 112 for i in BP}
htouch = [i for i, e in enumerate(P) if e[0] == 'ADD' and (e[1] in hmains or e[2] in hmains)]
direct = [i for i in touch if (P[i][1] in M2 and P[i][2] in M1) or (P[i][2] in M2 and P[i][1] in M1)]
print('  events that read or write a second main: %d; events that read or write a hosted-port main: %d' % (len(touch), len(htouch)))
incore = [i for i in direct if lo <= i <= hi]
port_of = {}
for i_, r in enumerate(live): port_of[r] = i_; port_of[r + 112] = i_
hp = {port_of[P[i][2] if P[i][1] in M2 else P[i][1]] for i in incore}
# cross-type traffic, by an explicit definition: the type of a main is the type of its port (two-chain or hosted)
port = {}; role = {}
for i_, r in enumerate(live): port[r] = i_; role[r] = 'X'; port[r + 112] = i_; role[r + 112] = 'Y'
for i_, a_, b_ in zip(DP, X2, Y2): port[a_] = i_; role[a_] = 'X2'; port[b_] = i_; role[b_] = 'Y2'
DPs = set(DP); typ = lambda r: 'two-chain' if port[r] in DPs else 'hosted'
core_kinds = Counter((typ(P[i][1]) != typ(P[i][2]), port[P[i][1]] == port[P[i][2]]) for i in incore)
need(len(direct) == 228 and len(incore) == 60 and core_kinds == {(False, False): 33, (False, True): 14, (True, False): 13}, 'events that couple a second-plane main with a first-plane main directly: %d, of which %d lie in the two gate blocks and %d lie inside the core (between the first and the last MOVE); of the %d core events %d pair two ports of different types (a second main of a two-chain port with a main of a hosted port), %d pair two different two-chain ports and %d pair a second main with a first main of the SAME two-chain port (the #6919 word, same definition, counted below: 453, 30 in the core: 14, 12 and 4; the core is the stretch between the first and the last MOVE, which is longer in this word, the event list being rewritten)' % (len(direct), len(direct) - len(incore), len(incore), len(incore), core_kinds[(True, False)], core_kinds[(False, False)], core_kinds[(False, True)]))
cross = [(k, e) for k, e in enumerate(P) if e[0] in ('ADD', 'COPY') and e[1] in port and e[2] in port and typ(e[1]) != typ(e[2])]
cross2 = [(k, e) for k, e in cross if role[e[1]] in ('X2', 'Y2') or role[e[2]] in ('X2', 'Y2')]
hD = set(); hH = set()
for e in P:
    if e[0] == 'ADD':
        for a_, b_ in ((e[1], e[2]), (e[2], e[1])):
            if b_ in port and a_ < n and a_ not in port: (hD if typ(b_) == 'two-chain' else hH).add(a_)
need(len(cross) == 187 and len(cross2) == 66 and sum(1 for k, e in cross2 if e[4] != 127) == 17, 'cross-type main-main traffic (definition: an ADD or COPY whose destination and source are both mains and whose ports have different types): %d events, of which %d involve a second main (%d of those at a frame other than 127); legal (frame law clean: common chart); the #6919 word has 218, 123 and 25 by the same definition' % (len(cross), len(cross2), sum(1 for k, e in cross2 if e[4] != 127)))
need(len(hD & hH) == 328, '%d helpers have ADD events directly against mains of both port types (the 8 hosted ports share them with the two-chain ports; the #6919 word: 458)' % len(hD & hH))
rq = [({r: Q(1)} if r < n else {}) for r in range(n + new['owned_fields'])]; hold = 0
for e in P:
    op = e[0]; r = e[1]
    if op in ('INIT', 'CLEAR'): rq[r] = {}
    elif op == 'SCALE': rq[r] = {k: v * Q(e[2]) for k, v in rq[r].items()}
    elif op in ('ADD', 'COPY'):
        if op == 'COPY': rq[r] = {}
        R_ = rq[r]
        for k, v in rq[e[2]].items():
            t = R_.get(k, 0) + Q(e[3]) * v
            if t: R_[k] = t
            else: R_.pop(k, None)
        if r in port and any(k in port and typ(k) != typ(r) for k in R_): hold += 1
foreign = sum(1 for r in port if any(k in port and typ(k) != typ(r) for k in rq[r]))
need(foreign == 0 and hold == 2747, 'the endpoint rows of all %d mains hold no input of a port of the other type; transiently a main holds a foreign-type input after %d events, and it cancels' % (len(port), hold))
def coupling(Wd):
    """the counts of the core and cross-type coupling events, by one definition, on any word of this line"""
    Hd = Wd['hosted']; Pd = Wd['program']; nd = len(Wd['initial']); lv = Wd['live']; DPd = Hd['Dports']
    M1d = set(lv) | {r + 112 for r in lv}; M2d = set(Hd['X2']) | set(Hd['Y2'])
    lod = next(i for i, e in enumerate(Pd) if e[0] == 'MOVE'); hid = max(i for i, e in enumerate(Pd) if e[0] == 'MOVE')
    touch_ = [i for i, e in enumerate(Pd) if e[0] == 'ADD' and (e[1] in M2d or e[2] in M2d)]
    direct_ = [i for i in touch_ if (Pd[i][1] in M2d and Pd[i][2] in M1d) or (Pd[i][2] in M2d and Pd[i][1] in M1d)]
    incore_ = [i for i in direct_ if lod <= i <= hid]
    port_ = {}; role_ = {}
    for i_, r in enumerate(lv): port_[r] = i_; role_[r] = 'X'; port_[r + 112] = i_; role_[r + 112] = 'Y'
    for i_, a_, b_ in zip(DPd, Hd['X2'], Hd['Y2']): port_[a_] = i_; role_[a_] = 'X2'; port_[b_] = i_; role_[b_] = 'Y2'
    DPs_ = set(DPd); typ_ = lambda r: 'two-chain' if port_[r] in DPs_ else 'hosted'
    kinds_ = Counter((typ_(Pd[i][1]) != typ_(Pd[i][2]), port_[Pd[i][1]] == port_[Pd[i][2]]) for i in incore_)
    cross_ = [(k, e) for k, e in enumerate(Pd) if e[0] in ('ADD', 'COPY') and e[1] in port_ and e[2] in port_ and typ_(e[1]) != typ_(e[2])]
    cross2_ = [(k, e) for k, e in cross_ if role_[e[1]] in ('X2', 'Y2') or role_[e[2]] in ('X2', 'Y2')]
    hD_ = set(); hH_ = set()
    for e in Pd:
        if e[0] == 'ADD':
            for a_, b_ in ((e[1], e[2]), (e[2], e[1])):
                if b_ in port_ and a_ < nd and a_ not in port_: (hD_ if typ_(b_) == 'two-chain' else hH_).add(a_)
    rq_ = [({r: Q(1)} if r < nd else {}) for r in range(nd + Wd['owned_fields'])]; hold_ = 0
    for e in Pd:
        op = e[0]; r = e[1]
        if op in ('INIT', 'CLEAR'): rq_[r] = {}
        elif op == 'SCALE': rq_[r] = {k: v * Q(e[2]) for k, v in rq_[r].items()}
        elif op in ('ADD', 'COPY'):
            if op == 'COPY': rq_[r] = {}
            R_ = rq_[r]
            for k, v in rq_[e[2]].items():
                t = R_.get(k, 0) + Q(e[3]) * v
                if t: R_[k] = t
                else: R_.pop(k, None)
            if r in port_ and any(k in port_ and typ_(k) != typ_(r) for k in R_): hold_ += 1
    foreign_ = sum(1 for r in port_ if any(k in port_ and typ_(k) != typ_(r) for k in rq_[r]))
    return dict(touch=len(touch_), direct=len(direct_), incore=len(incore_), kinds=dict(kinds_), cross=len(cross_), cross2=len(cross2_), cross2_off127=sum(1 for k, e in cross2_ if e[4] != 127), both=len(hD_ & hH_), hold=hold_, foreign=foreign_, nports=len(port_), core=(lod, hid))
CN, C19 = coupling(new), coupling(w19)
need(CN['direct'] == len(direct) and CN['incore'] == len(incore) and CN['cross'] == len(cross) and CN['hold'] == hold, 'the same counts computed by the function used for both words agree with the counts above for this word')
need((C19['direct'], C19['incore'], C19['cross'], C19['cross2'], C19['cross2_off127'], C19['both'], C19['hold'], C19['foreign'], C19['kinds']) == (453, 30, 218, 123, 25, 458, 3135, 0, {(False, False): 12, (True, False): 14, (False, True): 4}), 'the #6919 word by the same function: %d direct couplings (%d in the core), %d cross-type events (%d with a second main, %d off frame 127), %d helpers against both types, %d transient foreign holdings, kinds %s: the figures stated by the #6919 package' % (C19['direct'], C19['incore'], C19['cross'], C19['cross2'], C19['cross2_off127'], C19['both'], C19['hold'], sorted(C19['kinds'].items())))
# random-evaluation replay with the endpoint of each port type; types may be altered for the controls
M = (1 << 61) - 1
al, be, a2 = Q(H['alpha']), Q(H['beta']), Q(H['alpha2'])
fm = lambda q: (lambda f: f.numerator % M * pow(f.denominator, M - 2, M) % M)(Q(q)); X2s = set(X2); Y2s = set(Y2)
def endpoint_ok(prog, dports=DP, K=2, seed=3, Wd=new):
    n = len(Wd['initial']); NR = n + Wd['owned_fields']; rnd = random.Random(seed); dX = {live[i] for i in dports}; x2of = dict(zip(X2, Y2))
    v0 = [[rnd.randrange(M) for _ in range(K)] for _ in range(n)]; v = [x[:] for x in v0] + [[0] * K for _ in range(Wd['owned_fields'])]
    for e in prog:
        op = e[0]
        if op in ('INIT', 'CLEAR'): v[e[1]] = [0] * K
        elif op == 'SCALE':
            c = fm(e[2]); v[e[1]] = [a * c % M for a in v[e[1]]]
        elif op in ('ADD', 'COPY'):
            c = fm(e[3]); s = v[e[2]]
            if op == 'COPY': v[e[1]] = [c * b % M for b in s]
            else: v[e[1]] = [(a + c * b) % M for a, b in zip(v[e[1]], s)]
    for r in range(NR):
        if r >= n: ex = [0] * K
        elif r in X: ex = list(v0[r]) if r in dX else [(v0[r][k] + fm(al) * v0[r + 112][k]) % M for k in range(K)]
        elif r in Y: ex = [(v0[r - 112][k] + v0[r][k]) % M for k in range(K)] if r - 112 in dX else [(fm(be) * v0[r - 112][k] + fm(1 + al * be) * v0[r][k]) % M for k in range(K)]
        elif r in X2s: ex = [(v0[r][k] + fm(a2) * v0[x2of[r]][k]) % M for k in range(K)]
        elif r in Y2s: ex = list(v0[r])
        else: ex = v0[r]
        if v[r] != ex: return False
    return True
need(endpoint_ok(P), 'random-evaluation replay accepts the word (endpoint exact on every public and owned row, both port types)')
need(not endpoint_ok(P, dports=DP[1:]), 'control: wrong port type: one two-chain port declared hosted fails (the endpoint rows of that port differ)')
need(not endpoint_ok(P, dports=sorted(DP[1:] + [BP[0]])), 'control: swapped assignment: a two-chain port and a hosted port exchanged in the type list fails')
rnd = random.Random(9); smp = rnd.sample(touch, 8) + rnd.sample(htouch, 8); bw = bm = bd = 0
for i in smp:
    e = list(P[i]); e[3] = str(Q(e[3]) * 2)
    bw += not endpoint_ok(P[:i] + [e] + P[i + 1:])
    bm += not endpoint_ok(P[:i] + P[i + 1:])
    bd += not endpoint_ok(P[:i + 1] + [P[i]] + P[i + 1:])
need(bw == bm == bd == len(smp), 'controls on %d sampled events (8 that read or write a second main, 8 that read or write a hosted-port main): a wrong weight (x2), a missing event and an event taken twice are all rejected' % len(smp))
adds = [i for i in range(lo, hi + 1) if P[i][0] == 'ADD']
need(not endpoint_ok(P[:adds[0]] + P[adds[0] + 1:]), 'control: removing the first core ADD is rejected')
sample = rnd.sample(adds, 12); broke = sum(not endpoint_ok(P[:i] + P[i + 1:]) for i in sample)
need(broke >= 9, 'control: removing any one of 12 sampled core ADDs breaks the endpoint in %d cases' % broke)
# ---- valves, deletions and flips: the #6917 word against the #6911 word (both are in data/) -----------------------
w17 = old; P17 = w17['program']
def hclass(W):
    Hh = W['hosted']; lv = W['live']; mn = set(lv) | {r + 112 for r in lv} | set(Hh['X2']) | set(Hh['Y2']); dd = [len(b) for b in W['frames']]
    return {r: (dd[W['initial'][r]], dd[W['final'][r]]) for r in range(len(W['initial'])) if r not in mn}
cn_, co_ = Counter(hclass(w17).values()), Counter(hclass(w11).values())
dcls = {k: cn_[k] - co_[k] for k in set(cn_) | set(co_) if cn_[k] != co_[k]}
need(dcls == {(0, 9): 4, (5, 9): -8, (1, 9): -1} and sum(cn_.values()) == 962 and sum(co_.values()) == 967, 'valves, deletions and flips of the #6917 word, helper classes (initial, final rank) against the #6911 word: %s; 962 helpers against 967. This is consistent with 4 valves (4 new registers of class (0,9)), 8 flipped helpers (8 registers of class (5,9) fewer) and one register dropped after the deletions; the individual valves, flips and deletions are not recoverable from the word, their effect is what is counted and replayed' % sorted(dcls.items()))
def cnt(W):
    Pw = W['program']; a = next(i for i, e in enumerate(Pw) if e[0] == 'MOVE'); b = max(i for i, e in enumerate(Pw) if e[0] == 'MOVE')
    return dict(core=Counter(e[0] for e in Pw[a:b + 1]), pre=a, post=len(Pw) - b - 1)
cw, cp = cnt(w17), cnt(w11)
need((cp['core']['ADD'], cw['core']['ADD'], cp['core']['SCALE'], cw['core']['SCALE'], cp['core']['MOVE'], cw['core']['MOVE']) == (6636, 6639, 739, 739, 6421, 6379) and (cp['pre'], cp['post'], cw['pre'], cw['post']) == (26427, 19586, 25686, 18378),
     'core of the #6917 word against the #6911 word: ADDs 6636 -> 6639, SCALEs 739 (unchanged), MOVEs 6421 -> 6379; events before the core 26,427 -> 25,686, after 19,586 -> 18,378')
cls17 = hclass(w17); lo17 = next(i for i, e in enumerate(P17) if e[0] == 'MOVE'); hi17 = max(i for i, e in enumerate(P17) if e[0] == 'MOVE')
chg = [i for i in range(lo17, hi17 + 1) if P17[i][0] == 'ADD' and ((P17[i][1] in cls17 and cls17[P17[i][1]] in ((0, 9), (5, 9))) or (P17[i][2] in cls17 and cls17[P17[i][2]] in ((0, 9), (5, 9))))]
scl = [i for i in range(lo17, hi17 + 1) if P17[i][0] == 'SCALE' and P17[i][1] in cls17]
ok17 = lambda prog: endpoint_ok(prog, Wd=w17)
need(ok17(P17), 'the #6917 word is accepted by the same random-evaluation replay (control for the controls below)')
rnd = random.Random(21); smp = rnd.sample(chg, 12); bw = bm = bd = 0
for i in smp:
    e = list(P17[i]); e[3] = str(Q(e[3]) * 2)
    bw += not ok17(P17[:i] + [e] + P17[i + 1:]); bm += not ok17(P17[:i] + P17[i + 1:]); bd += not ok17(P17[:i + 1] + [P17[i]] + P17[i + 1:])
need(bw == bm == bd == len(smp), 'controls on %d sampled ADD events of the #6917 word that touch helpers of the changed classes (the valve and flip registers): a wrong weight, a missing event and an event taken twice are all rejected' % len(smp))
sm2 = rnd.sample(scl, 12); sw = sm = sd = 0
for i in sm2:
    e = list(P17[i]); e[2] = str(Q(e[2]) * 2)
    sw += not ok17(P17[:i] + [e] + P17[i + 1:]); sm += not ok17(P17[:i] + P17[i + 1:]); e3 = list(P17[i]); e3[2] = '-1/2' if Q(e3[2]) != Q(-1, 2) else '1/2'
    sd += not ok17(P17[:i] + [e3] + P17[i + 1:])
need(sw == sm == sd == len(sm2), 'controls on %d sampled core SCALE events of helpers of the #6917 word: a wrong scale (x2), a missing scale and a scale replaced by 1/2 or -1/2 are all rejected (flips use gates with s = 1/2, so a wrong scale must fail)' % len(sm2))

# ---- ten further helper splits: this word against the #6919 word (data/prior_word_6919.json.gz) -----------------------------------
def span(b):
    t = {0}
    for v in b:
        if not (isinstance(v, int) and 0 < v < 512 and v not in t): raise SystemExit('FAIL dependent basis')
        t |= {x ^ v for x in t}
    return frozenset(t)
spn = [span(b) for b in new['frames']]; dn = [len(b) for b in new['frames']]; nold = len(w19['initial'])
def paths(W):
    d = {}
    for e in W['program']:
        if e[0] == 'MOVE' and e[1] < len(W['initial']): d.setdefault(e[1], []).append((e[2], e[3], e[4]))
    return d
mvn = paths(new); P19 = w19['program']
pieces = list(range(nold, n)); mainsall = M1 | M2
need(new['frames'] == w19['frames'] and new['live'] == w19['live'] and new['hosted'] == w19['hosted'] and new['ports'] == w19['ports'] and new['owned_fields'] == w19['owned_fields'] and new['initial'][:nold] == w19['initial'],
     'same frame list (%d frames), mains, ports, hosted lists and owned roles as the #6919 word; the initial frame of each of its %d registers is unchanged' % (len(new['frames']), nold))
need(len(pieces) == 10 and all(r not in mainsall for r in pieces), 'splits, counted on the word: %d new helper registers (labels %d..%d), none of them a main (the #6919 word has %d public registers, this word %d)' % (len(pieces), nold, n - 1, nold, n))
changed = [r for r in range(nold) if new['final'][r] != w19['final'][r]]
need(len(changed) == 10 and not any(r in mainsall for r in changed), 'exactly %d registers of the #6919 word end at a different frame, none of them a main: %s' % (len(changed), changed))
cand = {z: [r for r in changed if new['final'][r] == new['initial'][z] and w19['final'][r] == new['final'][z]] for z in pieces}
need(all(cand[z] for z in pieces), 'every piece has a parent candidate by frame labels (new final of the parent = initial of the piece, old final of the parent = final of the piece); candidates per piece: %s' % sorted(Counter(len(c) for c in cand.values()).items()))
match = {}
def augment(z, seen):
    for p_ in cand[z]:
        if p_ in seen: continue
        seen.add(p_)
        if p_ not in match or augment(match[p_], seen): match[p_] = z; return True
    return False
need(all(augment(z, set()) for z in pieces) and len(match) == 10 and set(match) == set(changed), 'the 10 pieces are matched to the 10 changed registers, one piece each (augmenting-path matching; where several parents have the same frame labels the matching is not unique, and none of the facts below depends on which one is taken): no register is split twice and no piece is shared')
par = {z: p_ for p_, z in match.items()}
need(all(spn[new['initial'][p_]] < spn[new['final'][p_]] == spn[new['initial'][z]] < spn[new['final'][z]] == spn[w19['final'][p_]] and new['initial'][p_] == w19['initial'][p_] for z, p_ in par.items()), 'strictly nested frames on every split: initial(parent) < final(parent) = initial(piece) < final(piece) = final of the register in the #6919 word, as subspaces, strict at both steps (10 of 10)')
cls_split = Counter((dn[new['initial'][p_]], dn[new['final'][p_]] - dn[new['initial'][p_]], dn[new['final'][z]] - dn[new['final'][p_]]) for z, p_ in par.items())
print('  splits by (initial rank of the parent, rank climbed by the parent, rank climbed by the piece):', sorted(cls_split.items()))
need(all(dn[new['final'][p_]] - dn[new['initial'][p_]] + dn[new['final'][z]] - dn[new['final'][p_]] == dn[w19['final'][p_]] - dn[w19['initial'][p_]] for z, p_ in par.items()), 'one credit per helper: on each of the 10 splits the rank mass of the parent plus the rank mass of the piece equals the rank mass of the register in the #6919 word (the credit is cut in two, not doubled)')
mv_new = Counter((e[2], e[3], e[4]) for e in P if e[0] == 'MOVE'); mv_old = Counter((e[2], e[3], e[4]) for e in P19 if e[0] == 'MOVE')
need(mv_new == mv_old and sum(mv_new.values()) == 6374, 'the multiset of MOVEs (initial frame, final frame, owned flag) equals that of the #6919 word, %d MOVEs: the splits cut a path in two and add or remove no move, so the paid jobs P are unchanged' % sum(mv_new.values()))
bad = 0
for r in range(n):
    if r in mainsall: continue
    ch = mvn.get(r, []); cur = new['initial'][r]; mass = 0
    for a_, b_, ow in ch:
        if a_ != cur or not (spn[a_] < spn[b_]) or ow: bad += 1; break
        mass += dn[b_] - dn[a_]; cur = b_
    else:
        if cur != new['final'][r] or mass != dn[new['final'][r]] - dn[new['initial'][r]] or mass <= 0: bad += 1
need(bad == 0, 'one credit per helper: all %d helpers (%d of the #6919 word, 10 pieces) follow ONE contiguous chain of strictly nested frames from the initial to the final frame, unowned, and the rank mass of the chain equals the rank gained (so each helper is one field, one job, one credit)' % (n - len(mainsall), nold - len(mainsall)))
need(all(new['initial'][r] == w19['initial'][r] and (new['final'][r] == w19['final'][r] or r in match) for r in range(nold)), 'no other register changes its initial or final frame: the 10 parents account for every change among the %d registers of the #6919 word' % nold)
cmv = lambda W: Counter(e[0] for e in W['program'])
print('  events by kind, this word / #6919 word:', dict(cmv(new)), dict(cmv(w19)))
need(cmv(new)['INIT'] == cmv(w19)['INIT'] == 54 and cmv(new)['CLEAR'] == cmv(w19)['CLEAR'] == 54 and cmv(new)['COPY'] == cmv(w19)['COPY'] == 1, 'owned lifetimes: 54 INIT, 54 CLEAR and 1 COPY in both words; the ADD and SCALE lists differ (ADD %d against %d, SCALE %d against %d: the event list of this word is rewritten, with same-frame stretches recompacted and ADDs merged, as well as split; the endpoint and the invoice are what the exact replay and the recount check)' % (cmv(new)['ADD'], cmv(w19)['ADD'], cmv(new)['SCALE'], cmv(w19)['SCALE']))
# controls: wrong split coefficient, missing and doubled events, aliased piece
pset = set(pieces); touchp = [i for i, e in enumerate(P) if e[0] == 'ADD' and (e[1] in pset or e[2] in pset)]
rnd = random.Random(33); smp = rnd.sample(touchp, 12); bw = bm = bd = 0
for i in smp:
    e = list(P[i]); e[3] = str(Q(e[3]) * 2)
    bw += not endpoint_ok(P[:i] + [e] + P[i + 1:]); bm += not endpoint_ok(P[:i] + P[i + 1:]); bd += not endpoint_ok(P[:i + 1] + [P[i]] + P[i + 1:])
need(bw == bm == bd == len(smp), 'controls on %d sampled ADD events that read or write a split piece (of %d such events): a wrong coefficient (x2), a missing event and an event taken twice are all rejected' % (len(smp), len(touchp)))
def frame_violations(initial, prog, final=None):
    """frame law: an ADD or COPY needs both registers at the same frame, a MOVE needs its source frame to be the current one"""
    cur = list(initial) + [None] * new['owned_fields']; bad_ = 0
    for e in prog:
        op = e[0]
        if op == 'MOVE': bad_ += cur[e[1]] != e[2]; cur[e[1]] = e[3]
        elif op in ('INIT', 'CLEAR'): cur[e[1]] = e[2] if op == 'INIT' else None
        elif op == 'SCALE': bad_ += cur[e[1]] != e[3]
        else: bad_ += not (cur[e[1]] == e[4] == cur[e[2]])
    return bad_
need(frame_violations(new['initial'], P) == 0, 'the frame law holds on every event of this word (a piece and its parent sit at the frame the event names)')
fw = 0
for z in pieces:
    ini = list(new['initial']); ini[z] = new['initial'][par[z]]      # the piece starts at the initial frame of its parent instead of at F
    fw += frame_violations(ini, P) > 0
need(fw == 10, 'control: giving a piece the initial frame of its parent (instead of the cut frame F) breaks the frame law on 10 of 10 pieces.')
acc = 0
for z in pieces:
    p_ = par[z]; Pa = [[e[0]] + [(p_ if x == z else x) if 1 <= k <= (2 if e[0] in ('ADD', 'COPY') else 1) and isinstance(x, int) else x for k, x in enumerate(e[1:], 1)] for e in P]
    acc += endpoint_ok(Pa)
print('  note: the endpoint replay alone does not see frames: rewriting every event of a piece to its parent label (aliasing) is still accepted by it on %d of 10 pieces, so aliasing is not used as a control; the frame control above is' % acc)
need(endpoint_ok(P), 'the random-evaluation replay accepts this word (control for the controls above)')
print('PASS_COVER_CHANGES')
