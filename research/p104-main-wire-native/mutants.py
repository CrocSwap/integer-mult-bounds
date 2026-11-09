#!/usr/bin/env python3
"""Second value engine with mutants (standard library).  python3 -I -B mutants.py WORD.json.gz
The word is replayed over Z/(2^61 - 1) on 2 random input vectors (own forward evaluation, independent of the Fraction replay of check.py) and compared with the endpoint.
Mutants are scored with an adjoint trick (sensitivity of a random output functional to a change after each event), which is cross-checked against a direct full re-run on sampled mutants.
Mutants: every ADD or COPY coefficient doubled (61,053) and sign-flipped; every SCALE doubled and sign-flipped (3,660); on the odd-denominator events numerator + 1, sign flip and a factor 3;
300 sampled swaps of adjacent events that do not commute.  Expected: everything is caught except seven ADD mutants (events 33201, 37661, 39201, 40052, 40053, 40076, 42666), which are shown here by an exact Fraction replay of the mutated word, doubled and negated, to leave the endpoint unchanged:
six are dead stores into an owned register that is never read before its CLEAR, one (42666) is a temporary pair whose effect cancels downstream.  Ends PASS_MUTANTS."""
import gzip, json, sys, random
from fractions import Fraction as Q
sys.dont_write_bytecode = True
p = (1 << 61) - 1
W = json.load(gzip.open(sys.argv[1], 'rt')); P = W['program']; n = W['public']; NO = W['owned_fields']; NR = n + NO
rnd = random.Random(2024)
def fm(q): q = Q(q); return q.numerator % p * pow(q.denominator, -1, p) % p
live = W['live']; h = W['hosted']; Dp = set(h['Dports']); X2 = dict(zip(h['Dports'], h['X2'])); Y2 = dict(zip(h['Dports'], h['Y2'])); hf = fm(Q(1, 2))
def target(c):
    t = list(c) + [0] * NO
    for i, x in enumerate(live):
        y = x + 112
        if i in Dp: t[x] = c[x]; t[y] = (c[x] + c[y]) % p; a, b = X2[i], Y2[i]; t[a] = (c[a] - c[b]) % p; t[b] = c[b]
        else: t[x] = (c[x] - c[y]) % p; t[y] = hf * (c[x] + c[y]) % p
    return t
NC = 2
cs = [[rnd.randrange(p) for _ in range(n)] for _ in range(NC)]; ts = [target(c) for c in cs]; cache = {}
def f(x):
    if x not in cache: cache[x] = fm(x)
    return cache[x]
def run(prog):
    vals = [c + [0] * NO for c in cs]; cur = list(W['initial']) + [None] * NO; viol = 0
    for e in prog:
        o = e[0]; r = e[1]
        if o == 'MOVE':
            if cur[r] != e[2]: viol += 1
            cur[r] = e[3]
        elif o == 'SCALE':
            if cur[r] != e[3]: viol += 1
            q = f(e[2])
            for v in vals: v[r] = v[r] * q % p
        elif o in ('ADD', 'COPY'):
            q = f(e[3]); s = e[2]
            if not (cur[r] == e[4] == cur[s] and s != r): viol += 1
            for v in vals:
                if o == 'COPY': v[r] = 0
                v[r] = (v[r] + q * v[s]) % p
        elif o == 'INIT':
            cur[r] = e[2]
            for v in vals: v[r] = 0
        elif o == 'CLEAR':
            if cur[r] != e[2]: viol += 1
            cur[r] = None
            for v in vals: v[r] = 0
    viol += sum(cur[r] != W['final'][r] for r in range(n))
    return viol, sum(sum(1 for r in range(NR) if v[r] != t[r]) for v, t in zip(vals, ts))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
def exact_bad(prog):
    """number of rows of the exact endpoint that differ, by Fraction replay (frames are not touched by a coefficient change)"""
    row = [({r: Q(1)} if r < n else {}) for r in range(NR)]
    for e in prog:
        o = e[0]; r = e[1]
        if o == 'SCALE': q = Q(e[2]); row[r] = {k: x * q for k, x in row[r].items()}
        elif o in ('ADD', 'COPY'):
            q = Q(e[3])
            if o == 'COPY': row[r] = {}
            R = row[r]
            for k, x in row[e[2]].items():
                t = R.get(k, 0) + q * x
                if t: R[k] = t
                else: R.pop(k, None)
        elif o in ('INIT', 'CLEAR'): row[r] = {}
    one = Q(1); al = Q(h['alpha']); be = Q(h['beta']); a2 = Q(h['alpha2']); bad = 0; X2d = dict(zip(h['X2'], h['Y2']))
    ex = {}
    for i, x in enumerate(live):
        y = x + 112
        if i in Dp: ex[x] = {x: one}; ex[y] = {x: one, y: one}
        else: ex[x] = {x: one, y: al}; ex[y] = {x: be, y: 1 + al * be}
    for a, b in X2d.items(): ex[a] = {a: one, b: a2}; ex[b] = {b: one}
    for r in range(NR):
        want = ex.get(r, {r: one} if r < n else {})
        bad += row[r] != want
    return bad
t0_viol, t0_bad = run(P)
need((t0_viol, t0_bad) == (0, 0), 'clean word: 0 frame violations, 0 endpoint mismatches on %d random evaluations mod 2^61-1' % NC)
w = [[rnd.randrange(1, p) for _ in range(NR)] for _ in range(NC)]
vals = [c + [0] * NO for c in cs]; L = len(P); vs = [None] * L
for i, e in enumerate(P):
    o = e[0]; r = e[1]
    if o == 'SCALE':
        vs[i] = tuple(v[r] for v in vals); q = f(e[2])
        for v in vals: v[r] = v[r] * q % p
    elif o in ('ADD', 'COPY'):
        q = f(e[3]); s = e[2]; vs[i] = tuple(v[s] for v in vals)
        for v in vals:
            if o == 'COPY': v[r] = 0
            v[r] = (v[r] + q * v[s]) % p
    elif o in ('INIT', 'CLEAR'):
        for v in vals: v[r] = 0
u = [list(x) for x in w]; sens = [None] * L
for i in range(L - 1, -1, -1):
    e = P[i]; o = e[0]; r = e[1]; sens[i] = tuple(x[r] for x in u)
    if o in ('ADD', 'COPY'):
        q = f(e[3]); s = e[2]
        for x in u:
            a = x[r]
            if o == 'COPY': x[r] = 0
            x[s] = (x[s] + q * a) % p
    elif o == 'SCALE':
        q = f(e[2])
        for x in u: x[r] = x[r] * q % p
    elif o in ('INIT', 'CLEAR'):
        for x in u: x[r] = 0
def detected(i, coef): return any(coef * vs[i][k] % p * sens[i][k] % p for k in range(NC))
adds = [i for i, e in enumerate(P) if e[0] in ('ADD', 'COPY')]; scs = [i for i, e in enumerate(P) if e[0] == 'SCALE']
qq = lambda i: fm(P[i][3])
def score(name, idx, coeff):
    und = [i for i in idx if coeff(i) != 0 and not detected(i, coeff(i))]
    print('  %-48s mutants %6d detected %6d undetected %d %s' % (name, len(idx), len(idx) - len(und), len(und), und[:6]), flush=True); return und
u_add = score('ADD x2 (all)', adds, lambda i: qq(i)); u_neg = score('ADD sign flip (all)', adds, lambda i: (-2 * qq(i)) % p)
u_sc = score('SCALE x2 (all)', scs, lambda i: fm(P[i][2])); u_scn = score('SCALE sign flip (all)', scs, lambda i: (-2 * fm(P[i][2])) % p)
def odd(i):
    d = Q(P[i][3] if P[i][0] != 'SCALE' else P[i][2]).denominator
    while d % 2 == 0: d //= 2
    return d > 1
oa = [i for i in adds if odd(i)]; os_ = [i for i in scs if odd(i)]
uo = score('odd ADD: numerator + 1', oa, lambda i: fm(Q(1, Q(P[i][3]).denominator))) + score('odd ADD: coefficient x(-1)', oa, lambda i: (-2 * qq(i)) % p) + score('odd ADD: coefficient x3', oa, lambda i: (2 * qq(i)) % p)
uo += score('odd SCALE: numerator + 1', os_, lambda i: fm(Q(1, Q(P[i][2]).denominator))) + score('odd SCALE: x3', os_, lambda i: (2 * fm(P[i][2])) % p)
need(len(adds) == 61053 and len(scs) == 3660 and len(oa) == 4079 and len(os_) == 64 and not u_sc and not u_scn and not uo, 'all SCALE mutants (%d x2, %d sign flips) and all odd-event mutants (%d ADD, %d SCALE, three kinds each) are caught' % (len(scs), len(scs), len(oa), len(os_)))
need(u_add == u_neg and u_add == [33201, 37661, 39201, 40052, 40053, 40076, 42666], 'ADD mutants (x2 and sign flip, %d each): %d are not caught, the same seven events %s' % (len(adds), len(u_add), u_add))
# the seven: exact replay of the x2 and of the sign-flip mutant, and what each event is
def reads_before_clear(i):
    r = P[i][1]
    for e in P[i + 1:]:
        if e[0] in ('ADD', 'COPY') and e[2] == r: return True
        if e[0] == 'CLEAR' and e[1] == r: return False
        if e[0] == 'SCALE' and e[1] == r: pass
    return False
dead = [i for i in u_add if P[i][1] >= n and not reads_before_clear(i)]
need(exact_bad(P) == 0, 'exact replay of the unmutated word: 0 bad endpoint rows')
for i in u_add:
    for nm_, fac in (('x2', 2), ('sign flip', -1)):
        m = list(P); e = list(m[i]); e[3] = str(Q(e[3]) * fac); m[i] = e
        need(exact_bad(m) == 0, 'event %d (%s): the exact replay of its %s mutant leaves the endpoint unchanged (0 bad rows): equivalent, not a hole of the check' % (i, P[i], nm_))
need(len(dead) == 6 and [i for i in u_add if i not in dead] == [42666], '%d of the seven are ADDs into an owned register that is not read before its CLEAR (dead stores, registers %s); the seventh, event 42666, is a temporary whose contribution cancels downstream' % (len(dead), sorted({P[i][1] for i in dead})))
samp = rnd.sample(adds, 25) + rnd.sample(scs, 10); mism = 0
for i in samp:
    Q2 = [list(e) for e in P]
    if P[i][0] == 'SCALE': Q2[i][2] = str(Q(P[i][2]) * 2); c = fm(P[i][2])
    else: Q2[i][3] = str(Q(P[i][3]) * 2); c = qq(i)
    v, b = run(Q2); mism += (b > 0) != detected(i, c)
need(mism == 0, 'adjoint scoring agrees with a direct full re-run on %d sampled x2 mutants (0 disagreements)' % len(samp))
def rw(e): return ({e[2]}, {e[1]}) if e[0] in ('ADD', 'COPY') else (set(), {e[1]})
cand = []
for i in range(L - 1):
    a, b = P[i], P[i + 1]; Ra, Wa = rw(a); Rb, Wb = rw(b)
    if (Wa & Rb) or (Wb & Ra) or (a[0] == 'MOVE' and (b[1] == a[1] or (b[0] == 'ADD' and b[2] == a[1]))) or (b[0] == 'MOVE' and (a[1] == b[1] or (a[0] in ('ADD', 'COPY') and a[2] == b[1]))): cand.append(i)
samp = rnd.sample(cand, 300); und = 0
for i in samp:
    Q2 = list(P); Q2[i], Q2[i + 1] = P[i + 1], P[i]; v, b = run(Q2); und += v == 0 and b == 0
need(und == 0, '%d adjacent pairs of events share a register with a writer or a MOVE; 300 sampled swaps of such pairs: all %d rejected' % (len(cand), 300 - und))
print('PASS_MUTANTS')
