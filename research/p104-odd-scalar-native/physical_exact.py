#!/usr/bin/env python3
"""Physical integer run of the odd-scalar word, one column (standard library only).
python3 -I -B physical_exact.py WORD.json.gz [BASELINE_WORD.json.gz]
Each register is one column of 512 Gaussian coordinates held as (re, im) arrays of Python integers with F fractional bits; every root input is multiplied by S once.
Frames are D_f = WH diag(i^phi_f) WH / 512 (WH the Walsh-Hadamard transform, phi_f random in Z/4 per frame and coordinate): invertible, generic and commuting, with entries in Z[i, 1/2];
a MOVE a -> b is D_b D_a^-1 = WH diag(i^(phi_b - phi_a)) WH / 512, and the division by 512 is checked exact.
SCALE or ADD by a/b: multiply by a, CHECK that the result is divisible by b, divide.  At the exit every public row is divided by S (checked) and compared with the exact endpoint.
Cases: the word at S = 225 (all divisions exact, 0 bad public rows); smaller certificates and too few fractional bits rejected at a named event; truncated child return (low g bits dropped after every MOVE) rejected at the
first odd division, and the dyadic baseline word under the same truncation runs to the end and returns a wrong answer.
This is one column with generic commuting frames: not true Clifford frames, not tensor width 2, and the mod-p streams of physical.py do not test divisibility.  Ends PASS_PHYSICAL_EXACT."""
import gzip, json, sys, random
from fractions import Fraction as Q
sys.dont_write_bytecode = True
N = 512
class Rej(Exception): pass
def wh(v):
    h = 1
    while h < N:
        out = []
        for i in range(0, N, 2 * h):
            a = v[i:i + h]; b = v[i + h:i + 2 * h]
            out += [x + y for x, y in zip(a, b)]; out += [x - y for x, y in zip(a, b)]
        v = out; h *= 2
    return v
def run(W, S, F, g=0):
    n = W['public']; NO = W['owned_fields']; nf = len(W['frames']); rng = random.Random(777); phi = {}
    def ph(f):
        if f not in phi: phi[f] = [rng.randrange(4) for _ in range(N)]
        return phi[f]
    for f in range(nf): ph(f)
    cnt = [0, 0]
    def div(v, d, i, why):
        cnt[0] += 1
        if d == 1: return v
        if any(x % d for x in v): raise Rej((i, '%s event %s: not divisible by %d' % (why, i, d)))
        cnt[1] += 1; return [x // d for x in v]
    def mv(re, im, a, b, i):
        pa, pb = ph(a), ph(b); A, B = wh(re), wh(im); r = [0] * N; m = [0] * N
        for c in range(N):
            k = (pb[c] - pa[c]) % 4
            r[c], m[c] = ((A[c], B[c]), (-B[c], A[c]), (-A[c], -B[c]), (B[c], -A[c]))[k]
        return div(wh(r), 512, i, 'frame'), div(wh(m), 512, i, 'frame')
    pr = random.Random(5); inp = []
    for r in range(n):
        t = r % 5
        if t == 0: a = [pr.randrange(-1024, 1025) for _ in range(N)]; b = [pr.randrange(-1024, 1025) for _ in range(N)]
        elif t == 1: a = [pr.choice((-1024, 1024)) for _ in range(N)]; b = [pr.choice((-1024, 1024)) for _ in range(N)]
        elif t == 2 and r >= 5: a, b = list(inp[r - 2][0]), [-x for x in inp[r - 2][1]]
        elif t == 3: a = [int(x == r % N) for x in range(N)]; b = [0] * N
        else: a = [0] * N; b = [0] * N if r % 2 else [pr.randrange(-3, 4) for _ in range(N)]
        inp.append((a, b))
    sc = (1 << F) * S
    RE = [[x * sc for x in a] for a, b in inp] + [None] * NO; IM = [[x * sc for x in b] for a, b in inp] + [None] * NO
    tr = lambda v: [(abs(x) >> g << g) * (1 if x >= 0 else -1) for x in v]
    Z = lambda: [0] * N
    try:
        for i, e in enumerate(W['program']):
            op, r = e[0], e[1]
            if op == 'MOVE':
                RE[r], IM[r] = mv(RE[r], IM[r], e[2], e[3], i)
                if g: RE[r], IM[r] = tr(RE[r]), tr(IM[r])
            elif op == 'INIT': RE[r] = Z(); IM[r] = Z()
            elif op == 'CLEAR': RE[r] = IM[r] = None
            elif op == 'SCALE':
                q = Q(e[2]); RE[r] = div([x * q.numerator for x in RE[r]], q.denominator, i, 'scale'); IM[r] = div([x * q.numerator for x in IM[r]], q.denominator, i, 'scale')
            else:
                s = e[2]; q = Q(e[3]); x = div([u * q.numerator for u in RE[s]], q.denominator, i, 'add'); y = div([u * q.numerator for u in IM[s]], q.denominator, i, 'add')
                if op == 'COPY': RE[r] = Z(); IM[r] = Z()
                RE[r] = [u + v for u, v in zip(RE[r], x)]; IM[r] = [u + v for u, v in zip(IM[r], y)]
    except Rej as z:
        return dict(status='REJECTED', event=z.args[0][0], msg=z.args[0][1], divisions=cnt[0])
    H = W['hosted']; al, be, a2 = Q(H['alpha']), Q(H['beta']), Q(H['alpha2']); live = W['live']; X = set(live); Y = {r + 112 for r in live}
    DP = H['Dports']; dX = {live[i] for i in DP}; X2s = dict(zip(H['X2'], H['Y2']))
    def ex(r):
        if r in X: return {r: Q(1)} if r in dX else {r: Q(1), r + 112: al}
        if r in Y: return {r - 112: Q(1), r: Q(1)} if r - 112 in dX else {r - 112: be, r: 1 + al * be}
        if r in X2s: return {r: Q(1), X2s[r]: a2}
        return {r: Q(1)}
    bad = 0; mx = 0
    for r in range(n):
        try: x, y = div(RE[r], S, -1, 'exit'), div(IM[r], S, -1, 'exit')
        except Rej as z: return dict(status='REJECTED', event=-1, msg=z.args[0][1], divisions=cnt[0])
        ea = [0] * N; eb = [0] * N
        for k, c in ex(r).items():
            a, b = mv([v << F for v in inp[k][0]], [v << F for v in inp[k][1]], W['initial'][k], W['final'][r], -2); f2 = 2 * c.numerator // c.denominator
            ea = [u + v * f2 for u, v in zip(ea, a)]; eb = [u + v * f2 for u, v in zip(eb, b)]
        d = max(max(abs(2 * p - q) for p, q in zip(x, ea)), max(abs(2 * p - q) for p, q in zip(y, eb)))
        bad += d != 0; mx = max(mx, d)
    return dict(status='DONE', divisions=cnt[0], nonunit=cnt[1], bad=bad, rows=n, maxerr=mx)
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
W = json.load(gzip.open(sys.argv[1], 'rt')); B = json.load(gzip.open(sys.argv[2], 'rt')) if len(sys.argv) > 2 else None
r = run(W, 225, 24)
print('  S=225 F=24:', r, flush=True)
need(r['status'] == 'DONE' and r['bad'] == 0 and r['maxerr'] == 0, 'S = 225, F = 24: %d divisions (%d by a non-unit), every one exact; 0 bad of %d public rows; the exit division by S is exact' % (r['divisions'], r['nonunit'], r['rows']))
first = {}
for S, F, g, key in ((75, 24, 0, 'S=75'), (45, 24, 0, 'S=45'), (15, 24, 0, 'S=15'), (1, 24, 0, 'S=1'), (225, 20, 0, 'F=20')):
    r = run(W, S, F, g); first[key] = r; print('  %s:' % key, r, flush=True)
    need(r['status'] == 'REJECTED', 'control %s is rejected: %s' % (key, r['msg']))
need(first['S=75']['msg'].endswith('not divisible by 45') and first['S=45']['event'] == first['S=15']['event'], 'S = 75 fails at a division by 45; S = 45 and S = 15 fail at the same earlier event')
for g in (44, 50):
    r = run(W, 225, 60, g); print('  truncated child return, F=60 g=%d:' % g, r, flush=True)
    need(r['status'] == 'REJECTED', 'truncated child return (g = %d low bits dropped after every MOVE): rejected, %s' % (g, r['msg']))
r = run(W, 225, 60, 20); print('  F=60 g=20:', r, flush=True)
need(r['status'] == 'DONE' and r['bad'] == 0, 'a milder truncation (g = 20) is absorbed by the fractional bits: 0 bad rows')
if B is not None:
    r = run(B, 1, 60, 44); print('  dyadic baseline word, S=1, F=60 g=44:', r, flush=True)
    need(r['status'] == 'DONE' and r['bad'] > 0, 'control: the dyadic baseline word under the same truncation (g = 44) runs to the end and returns a wrong answer on %d of %d public rows' % (r['bad'], r['rows']))
print('PASS_PHYSICAL_EXACT')
