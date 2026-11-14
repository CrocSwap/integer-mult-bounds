"""P104 t = -1 callers: the MONOHUB joint caller, the four 20-odd-op floor callers, the form orbit, the sigma-ledger.
Standard library only; exact arithmetic in F_p, p = 2147483629 (p = 1 mod 4), i = sqrt(-1), q in {1, i, -1, -i}.

Inputs (data/, gzip with mtime 0, SHA256 hard-coded below and checked before use):
  joint_mono.json.gz   the exact t = -1 MONOHUB joint caller in PR #7113's JSON format (72 roles: A 0..35, B 36..71);
                       A events = MONOHUB hosted caller, B events and B pair (-1,1/2) = PR #7113 (Rohan Arun) verbatim.
  caller-7113.json.gz  the #7113 caller itself (control).
  livecaller-{live,hosted}free-{odd,even}.json.gz  four callers with one q-free plane at the odd-op floor.

Checks:
  1. MONOHUB joint caller replays with an idealised native HOST(-1,1) on A ports (B = #7113 verbatim): bad 0 at the four q;
     event census; 11 broken variants rejected; #7113 control with its own native bad 0, 2 controls rejected.
  2. Four floor callers: bad 0 at the four q, odd-op census (20 odd ops, or 2 QUERY + fields given up), controls rejected.
  3. Form orbit on joint_mono A: 3 new lines per J, 51 distinct lines of 68 forms, 17 input planes span 34, the 16
     consecutive output/input plane ranks all 4; controls.
  4. sigma-ledger o of every op and of J with H / SW, H-pair segment o = 4, the 8 fused SW + q^2 pairs fail, control.
Prints PASS_METHODS_CALLERS."""
import copy
import gzip
import hashlib
import json
import random
from collections import Counter
from fractions import Fraction as Fr
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
DATA = HERE / 'data'
P = 2147483629
IM = next(pow(g, (P - 1) // 4, P) for g in range(2, 99) if pow(g, (P - 1) // 2, P) == P - 1)
assert IM * IM % P == P - 1
HALF = (P + 1) // 2
QS = (1, IM, P - 1, P - IM)
QN = ('1', 'i', '-1', '-i')

SHA = {
    'joint_mono.json.gz': '4ffb61264d446d107de23fd9af05090db77aa16e64840165c6a0329ad0f3f3c4',
    'caller-7113.json.gz': '7e8038559cd158f6e32ef6d1a3bf15ab6a8ecc2239af32ab1699511ac28e26d9',
    'livecaller-livefree-odd.json.gz': '7b8e8c9dd04ce965f9162950da4270c7bbea1ee1fe97d11b99566abd014ce8b9',
    'livecaller-livefree-even.json.gz': 'ddfc96cda2c8e4001c6b81c5c5a088d60fdb5423516384cbd8a338d19531a5cd',
    'livecaller-hostedfree-odd.json.gz': 'a1fc419bb3c3eb7f756840c60cd3010f15c40bb09088983e56ccc8b24ff439ea',
    'livecaller-hostedfree-even.json.gz': '688f2464a8239562069be17b5b7e92593eaa7873975ebf86c1f6c6bd5cb49e83',
}


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def rejected(name, got):
    """negative control: bad counts (list) must contain a nonzero entry"""
    if not any(got):
        raise SystemExit('FAIL control %s NOT rejected: %r' % (name, got))
    say('ok  control rejected: %-60s bad %s' % (name, got))


def load(name):
    raw = (DATA / name).read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    if h != SHA[name]:
        raise SystemExit('FAIL sha256 mismatch for %s: %s' % (name, h))
    return json.loads(gzip.decompress(raw).decode())


def inv(a):
    return pow(a % P, P - 2, P)


@lru_cache(maxsize=None)
def fm(x):
    f = Fr(x)
    return f.numerator % P * inv(f.denominator) % P


def qp(q, e):
    return pow(q, e % 4, P)


# ---------------------------------------------------------------------------------------------------------------
# generic replay of a #7113-format caller (rows of R = current linear map; one J = A hosted pair + B hosted pair)
def replay(C, qv, Dv, A_pair=None, B_pair=None, a2=None, drop=(), A_form=None, live=None, hosted_q=None):
    n = C['roles']
    R = [[int(i == j) for j in range(n)] for i in range(n)]
    qi = inv(qv)
    form = A_form or C['types']['A']['form']
    a2 = fm(C['types']['A'].get('alpha2', '-1')) if a2 is None else fm(a2)
    TA = C['types']['A']
    if live is None:
        live = (fm(TA.get('live_coef', '1')), TA.get('live_qexp', -1))
    hq = TA.get('hosted_qexp', 1) if hosted_q is None else hosted_q

    def hostpair(src, dst, al, be):
        tt = al * be % P
        ns = [(x + al * qv % P * y) % P * d % P for x, y in zip(R[src], R[dst])]
        nd = [(be * qi % P * x + (1 + tt) * y) % P * d % P for x, y in zip(R[src], R[dst])]
        R[src], R[dst] = ns, nd

    for k, e in enumerate(C['events']):
        if k in drop:
            continue
        if e[0] == 'J':
            d = Dv[e[1]]
            if form in ('two-chain-HOST2', 'qfree-live-HOST2'):
                src, dst, x2, y2 = e[2]
                cl = live[0] * qp(qv, live[1]) % P
                R[dst] = [(a + cl * b) % P for a, b in zip(R[dst], R[src])]
                R[x2] = [(a + a2 * qp(qv, hq) % P * b) % P for a, b in zip(R[x2], R[y2])]
                for r in (src, dst, x2, y2):
                    R[r] = [a * d % P for a in R[r]]
            else:
                src, dst, al, be = e[2]
                al, be = (fm(al), fm(be)) if A_pair is None else (fm(A_pair[0]), fm(A_pair[1]))
                hostpair(src, dst, al, be)
                # the native's D multiplies src,dst (inside hostpair via d)
            src, dst, al, be = e[3]
            al, be = (fm(al), fm(be)) if B_pair is None else (fm(B_pair[0]), fm(B_pair[1]))
            hostpair(src, dst, al, be)
            continue
        op = e[1]
        if op == 'ADD':
            R[e[2]] = [(a + fm(e[4]) * b) % P for a, b in zip(R[e[2]], R[e[3]])]
        elif op == 'SCALE':
            c = fm(e[3])
            R[e[2]] = [a * c % P for a in R[e[2]]]
        elif op == 'SWAP':
            R[e[2]], R[e[3]] = R[e[3]], R[e[2]]
        elif op == 'QUERY':
            c = qp(qv, e[4])
            R[e[2]] = [(a + c * b) % P for a, b in zip(R[e[2]], R[e[3]])]
        elif op == 'LAMBDA':
            c = ((1 + e[3] * IM) * HALF + (1 - e[3] * IM) * HALF * qv * qv) % P
            R[e[2]] = [a * c % P for a in R[e[2]]]
        elif op in ('IDLE_ONE', 'IDLE_ODD'):
            c = qp(qv, e[4]) if op == 'IDLE_ODD' else 1
            for s in e[3]:
                c = c * Dv[s] % P
            R[e[2]] = [a * c % P for a in R[e[2]]]
        else:
            raise SystemExit('op ' + op)
    return R


def nbad(C, R, qv, Dv):
    b = 0
    for t in ('A', 'B'):
        T = C['types'][t]
        off = T['offset']
        for i, dg in enumerate(T['diagonal']):
            c = qp(qv, dg[0])
            for k, bit in enumerate(dg[2:]):
                if bit:
                    c = c * Dv[k + 1] % P
            r = off + i
            b += sum(R[r][j] != (c if j == r else 0) for j in range(C['roles']))
    return b


def run(C, **kw):
    rnd = random.Random(5)
    out = []
    for qv in QS:
        Dv = {s: rnd.randrange(2, P) for s in range(1, 18)}
        out.append(nbad(C, replay(C, qv, Dv, **kw), qv, Dv))
    return out


def a_events(C, op=None):
    return [k for k, e in enumerate(C['events']) if e[0] == 'A' and (op is None or e[1] == op)]


def check1():
    say('== 1. MONOHUB joint caller (joint_mono.json.gz, B = PR #7113 verbatim), idealised native, 72 roles')
    M = load('joint_mono.json.gz')
    C7 = load('caller-7113.json.gz')
    expect('roles / A form', (M['roles'], M['types']['A']['form']), (72, 'mono-HOST'))
    cen = Counter(e[1] for e in M['events'] if e[0] == 'A')
    cen['HOST'] = sum(1 for e in M['events'] if e[0] == 'J')
    expect('A event census', dict(sorted(cen.items())),
           {'ADD': 428, 'HOST': 17, 'IDLE_ONE': 47, 'LAMBDA': 76, 'QUERY': 3, 'SCALE': 69, 'SWAP': 101})
    expect('sum of A events', sum(cen.values()), 741)
    pairs = {(tuple(e[2][2:]), tuple(e[3][2:])) for e in M['events'] if e[0] == 'J'}
    expect('A pair (alpha,beta) and B pair on all 17 J', pairs, {(('-1', '1'), ('-1', '1/2'))})
    say('-- control: PR #7113 caller (Rohan Arun) with its own idealised native (live t=0 plane + hosted alpha2=-1 + B t=-1/2)')
    expect('#7113 bad at q=1,i,-1,-i', run(C7), [0, 0, 0, 0])
    rejected('#7113 with hosted alpha2=+1', run(C7, a2='1'))
    rejected('#7113 minus one A QUERY', run(C7, drop=(a_events(C7, 'QUERY')[0],)))
    say('-- MONOHUB joint caller with idealised A native HOST(alpha,beta)=(-1,1) (t=-1), B (-1,1/2)')
    expect('MONOHUB bad at q=1,i,-1,-i', run(M), [0, 0, 0, 0])
    rejected('A pair (-1,1/2)', run(M, A_pair=('-1', '1/2')))
    rejected('A pair (0,1) (transvection, t=0)', run(M, A_pair=('0', '1')))
    rejected('A pair (1,-1)', run(M, A_pair=('1', '-1')))
    rejected('B pair (-1,1) instead of (-1,1/2)', run(M, B_pair=('-1', '1')))
    qk = a_events(M, 'QUERY')
    expect('thin QUERY count', len(qk), 3)
    for j, k in enumerate(qk):
        rejected('drop thin QUERY #%d' % j, run(M, drop=(k,)))
    ids = a_events(M, 'IDLE_ONE')
    rejected('drop one A IDLE_ONE', run(M, drop=(ids[3],)))
    lam = a_events(M, 'LAMBDA')
    M2 = copy.deepcopy(M)
    M2['events'][lam[10]][3] *= -1
    rejected('flip one A LAMBDA (silent at q=1,-1 as in #7113)', run(M2))
    M3 = copy.deepcopy(M)
    M3['events'][ids[0]][3] = sorted(set(M3['events'][ids[0]][3]) ^ {17})
    rejected('idle stage set altered', run(M3))


# ---------------------------------------------------------------------------------------------------------------
def check2():
    say('== 2. four callers at the odd-op floor (one q-free plane), replay of all 72 roles')
    expect('floor arithmetic: 2 x 17 + 3 = 37 supply with H; target o = 36 needs >= 37; floor = 37 - 17', 37 - 17, 20)
    for fr, fl in (('live', 'odd'), ('live', 'even'), ('hosted', 'odd'), ('hosted', 'even')):
        nm = '%sfree-%s' % (fr, fl)
        C = load('livecaller-%s.json.gz' % nm)
        A = C['types']['A']
        say('-- caller %s: form %s, live q^%s, hosted q^%s' % (nm, A['form'], A['live_qexp'], A['hosted_qexp']))
        cen = Counter(e[1] for e in C['events'] if e[0] == 'A')
        odd = Counter(e[1] for e in C['events'] if e[0] == 'A' and e[1] in ('QUERY', 'IDLE_ODD') and e[4] % 2)
        say('   A census %s ; odd ops %s' % (dict(sorted(cen.items())), dict(odd)))
        if fl == 'odd':
            expect('%s odd ops per A port per word (2 QUERY + 18 IDLE_ODD)' % nm, sum(odd.values()), 20)
            expect('%s  composition' % nm, dict(odd), {'QUERY': 2, 'IDLE_ODD': 18})
        else:
            expect('%s odd ops (2 QUERY; the 18 phase fields given up as even)' % nm, dict(odd), {'QUERY': 2})
            expect('%s IDLE_ODD ops' % nm, cen.get('IDLE_ODD', 0), 0)
        expect('%s bad at q=1,i,-1,-i' % nm, run(C), [0, 0, 0, 0])
        if fr == 'live':
            rejected('free plane given back its q (live q^-1)', run(C, live=(fm('1'), -1)))
        else:
            rejected('free plane given back its q (hosted q^1)', run(C, hosted_q=1))
        rejected('hosted alpha2=+1', run(C, a2='1'))
        for k in a_events(C, 'QUERY'):
            rejected('drop A QUERY at event %d' % k, run(C, drop=(k,)))
        io = [k for k in a_events(C) if C['events'][k][1] in ('IDLE_ODD', 'IDLE_ONE')]
        rejected('drop last free-chain idle/phase op', run(C, drop=(io[-1],)))
        x = next(k for k in range(1, len(C['events'])) if C['events'][k - 1][0] == 'J')
        rejected('drop the cancel ADD after J1', run(C, drop=(x,)))
        if fl == 'odd':
            D2 = copy.deepcopy(C)
            x = next(k for k in a_events(D2, 'IDLE_ODD'))
            D2['events'][x][4] = 0
            rejected('one IDLE_ODD made even', run(D2))
        lam = a_events(C, 'LAMBDA')
        D3 = copy.deepcopy(C)
        D3['events'][lam[len(lam) // 2]][3] *= -1
        rejected('flip one A LAMBDA', run(D3))


# ---------------------------------------------------------------------------------------------------------------
# A-only 36x36 tools on joint_mono (native H = [[1,-q],[1/q,0]] on (src,dst) = (role 1, role 0), SW = q^-1 H)
NA = 36


def mkD(seed):
    r = random.Random(seed)
    return {s: r.randrange(2, P - 1) for s in range(1, 18)}


def eye(n=NA):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def Hn(q):
    return ((1, (-q) % P), (inv(q), 0))


def SWn(q):
    return ((inv(q), P - 1), (1, 0))


def lam(q, s):
    return ((1 + s * IM) * HALF + (1 - s * IM) * HALF * q * q) % P


def step(R, e, q, D, nat):
    if e[0] == 'J':
        d = D[e[1]]
        s, t = e[2][0], e[2][1]
        (a, b), (c, dd) = nat(q)
        x, y = R[s], R[t]
        R[s] = [(a * u + b * v) * d % P for u, v in zip(x, y)]
        R[t] = [(c * u + dd * v) * d % P for u, v in zip(x, y)]
        return
    op = e[1]
    if op == 'ADD':
        c = fm(e[4])
        R[e[2]] = [(u + c * v) % P for u, v in zip(R[e[2]], R[e[3]])]
    elif op == 'SCALE':
        c = fm(e[3])
        R[e[2]] = [c * u % P for u in R[e[2]]]
    elif op == 'SWAP':
        R[e[2]], R[e[3]] = R[e[3]], R[e[2]]
    elif op == 'QUERY':
        c = qp(q, e[4])
        R[e[2]] = [(u + c * v) % P for u, v in zip(R[e[2]], R[e[3]])]
    elif op == 'LAMBDA':
        c = lam(q, e[3])
        R[e[2]] = [c * u % P for u in R[e[2]]]
    elif op in ('IDLE_ONE', 'IDLE_ODD'):
        c = qp(q, e[4]) if op == 'IDLE_ODD' else 1
        for s_ in e[3]:
            c = c * D[s_] % P
        R[e[2]] = [c * u % P for u in R[e[2]]]
    else:
        raise SystemExit(op)


def rank(A):
    M = [r[:] for r in A]
    n = len(M)
    m = len(M[0]) if M else 0
    rk = 0
    for c in range(m):
        p = next((r for r in range(rk, n) if M[r][c]), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        iv = inv(M[rk][c])
        for r in range(n):
            if r != rk and M[r][c]:
                f = M[r][c] * iv % P
                M[r] = [(a - f * b) % P for a, b in zip(M[r], M[rk])]
        rk += 1
    return rk


def proj(v):
    k = next((i for i, x in enumerate(v) if x), None)
    if k is None:
        return None
    iv = inv(v[k])
    return tuple(x * iv % P for x in v)


class AWord:
    def __init__(self):
        self.C = load('joint_mono.json.gz')
        self.EV = [e for e in self.C['events'] if e[0] in ('J', 'A')]
        self.DIAG = self.C['types']['A']['diagonal']
        self.JIDX = [k for k, e in enumerate(self.EV) if e[0] == 'J']
        expect('A events + J in joint_mono', (len(self.EV), len(self.JIDX)), (741, 17))

    def target(self, q, D):
        T = [[0] * NA for _ in range(NA)]
        for i, dg in enumerate(self.DIAG):
            c = qp(q, dg[0])
            for k, bit in enumerate(dg[2:]):
                if bit:
                    c = c * D[k + 1] % P
            T[i][i] = c
        return T

    def word(self, q, D, natfor, lo=0, hi=None, extra=None):
        R = eye()
        hi = len(self.EV) if hi is None else hi
        for k in range(lo, hi):
            e = self.EV[k]
            jn = self.JIDX.index(k) if e[0] == 'J' else None
            step(R, e, q, D, natfor(jn) if jn is not None else None)
            if jn is not None and extra and jn in extra:
                for role, mult in extra[jn]:
                    R[role] = [v * mult(q) % P for v in R[role]]
        return R

    def bad(self, natfor, extra=None, seed=11):
        out = []
        for qi, q in enumerate(QS):
            D = mkD(seed + qi)
            R = self.word(q, D, natfor, extra=extra)
            T = self.target(q, D)
            out.append(sum(1 for i in range(NA) for j in range(NA) if R[i][j] != T[i][j]))
        return out


def check3(W):
    say('== 3. form orbit on joint_mono A (all 17 J on roles (X,Y) = (1,0), native H, 36 roles)')
    allnew, allcont = [], []
    for qi, q in enumerate(QS):
        for seed in (11, 29):
            D = mkD(seed + qi)
            R = eye()
            inp, outp = [], []
            for e in W.EV:
                if e[0] == 'J':
                    s, t = e[2][0], e[2][1]
                    inp.append((R[s][:], R[t][:]))
                    step(R, e, q, D, Hn)
                    outp.append((R[s][:], R[t][:]))
                else:
                    step(R, e, q, D, Hn)
            T = W.target(q, D)
            b = sum(1 for i in range(NA) for j in range(NA) if R[i][j] != T[i][j])
            allf = [v for pr in inp + outp for v in pr]
            lines = len(set(proj(v) for v in allf))
            span = rank([list(v) for v in allf])
            seen, new = set(), []
            for k in range(17):
                cur = set(proj(v) for v in inp[k]) | set(proj(v) for v in outp[k])
                new.append(len(cur - seen))
                seen |= cur
            insp = rank([list(v) for pr in inp for v in pr])
            cont = [rank([list(v) for v in outp[k]] + [list(v) for v in inp[k + 1]]) for k in range(16)]
            expect('q=%s seed %d: bad / distinct lines of 68 / span of 34 forms' % (QN[qi], seed), (b, lines, len(allf), span),
                   (0, 51, 68, 34))
            expect('   new lines per J', new, [3] * 17)
            expect('   input planes (17 x 2 forms) span', insp, 34)
            expect('   consecutive output/input plane rank (16 pairs)', cont, [4] * 16)
            allnew.append(new)
            allcont.append(cont)
    say('-- controls')
    rejected('replay with the t=0 native SW (not exact, so no orbit claim)', W.bad(lambda j: SWn))
    # the counting tool does detect repetition: 17 copies of one plane give 2 lines, span 2, plane rank 2
    v1, v2 = [1] + [0] * 35, [0, 1] + [0] * 34
    rep = [(v1, v2)] * 17
    got = (len(set(proj(v) for pr in rep for v in pr)), rank([list(v) for pr in rep for v in pr]))
    expect('control: 17 repeated planes would show 2 lines, span 2 (tool detects repetition; the data show 51, 34)', got, (2, 2))


# ---------------------------------------------------------------------------------------------------------------
def mul(A, B):
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(r, c)) % P for c in Bt] for r in A]


def minv(A):
    n = len(A)
    M = [row[:] + [int(i == j) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c])
        M[c], M[p] = M[p], M[c]
        iv = inv(M[c][c])
        M[c] = [v * iv % P for v in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c]
                M[r] = [(a - f * b) % P for a, b in zip(M[r], M[c])]
    return [row[n:] for row in M]


def det(A):
    M = [r[:] for r in A]
    n = len(M)
    d = 1
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c]), None)
        if p is None:
            return 0
        if p != c:
            M[c], M[p] = M[p], M[c]
            d = -d
        d = d * M[c][c] % P
        iv = inv(M[c][c])
        for r in range(c + 1, n):
            if M[r][c]:
                f = M[r][c] * iv % P
                M[r] = [(a - f * b) % P for a, b in zip(M[r], M[c])]
    return d % P


def o_of(Mf, q):
    """o(M) = rank(sigma(M) M^-1 - I), sigma: q -> -q; also det of the sigma-factor and whether it is -I"""
    S = mul(Mf((-q) % P), minv(Mf(q)))
    n = len(S)
    Sm = [[(S[i][j] - (i == j)) % P for j in range(n)] for i in range(n)]
    return rank(Sm), det(S), all(S[i][j] == ((P - 1) if i == j else 0) for i in range(n) for j in range(n))


def check4(W):
    say('== 4. sigma-sector (sigma: q -> -q) on joint_mono A: ledger, H-pair segments, fused SW + q^2 pairs')
    D = mkD(5)
    EV = W.EV
    first = {}
    for e in EV:
        key = e[1] if e[0] == 'A' else 'J'
        first.setdefault(key, e)
    ledger = {}
    for key in ('ADD', 'SCALE', 'SWAP', 'LAMBDA', 'IDLE_ONE', 'QUERY'):
        e = first[key]
        ledger[key] = [o_of(lambda q, e=e: (lambda R: (step(R, e, q, D, None), R)[1])(eye()), q)[:2] for q in (IM, 1)]
    for nm, nat in (('J(H)', Hn), ('J(SW)', SWn)):
        e = first['J']
        ledger[nm] = [o_of(lambda q, e=e, nat=nat: (lambda R: (step(R, e, q, D, nat), R)[1])(eye()), q)[:2] for q in (IM, 1)]
    qself = ('A', 'IDLE_ODD', 1, [], 1)
    ledger['QSELF'] = [o_of(lambda q: (lambda R: (step(R, qself, q, D, None), R)[1])(eye()), q)[:2] for q in (IM, 1)]
    want = {'ADD': 0, 'SCALE': 0, 'SWAP': 0, 'LAMBDA': 0, 'IDLE_ONE': 0, 'QUERY': 1, 'J(H)': 2, 'J(SW)': 1, 'QSELF': 1}
    for k, o in want.items():
        say('   ledger %-9s (o, det sigma-factor) at (i,-i): %s ; at (1,-1): %s' % (k, ledger[k][0], ledger[k][1]))
        expect('sigma-rank o of %s at both sigma pairs' % k, (ledger[k][0][0], ledger[k][1][0]), (o, o))
        expect('det of the sigma-factor of %s (+1; reflection QSELF -1)' % k,
               (ledger[k][0][1], ledger[k][1][1]), ((P - 1, P - 1) if k == 'QSELF' else (1, 1)))
    odd = [e for e in EV if e[0] == 'A' and e[1] == 'QUERY' and e[4] % 2]
    expect('odd ops in the joint_mono A caller', len(odd), 3)
    for q, qn in ((IM, 'i'), (1, '1')):
        expect('target o, det, scalar -I at q=%s' % qn, o_of(lambda x: W.target(x, D), q), (36, 1, True))
    expect('supply: H 17*2 + 3 (tight against the floor 36 + 1)', 17 * 2 + 3, 37)
    expect('supply: SW 17*1 + 3', 17 * 1 + 3, 20)
    say('-- controls: unit dropped / phases returned / H-pair segments / fused pairs')
    rejected('SW (= q^-1 H) with the unit dropped', W.bad(lambda j: SWn))
    ph = {j: [(1, lambda q: q), (0, lambda q: inv(q))] for j in range(17)}
    expect('SW + caller phases X*q (role 1), Y*q^-1 (role 0) on every J (= H) bad', W.bad(lambda j: SWn, extra=ph), [0, 0, 0, 0])
    ph1 = {j: ph[j] for j in range(16)}
    rejected('same phases on 16 of 17 J (one unit dropped)', W.bad(lambda j: SWn, extra=ph1))
    JI = W.JIDX
    po, ps = [], []
    for j in range(16):
        lo, hi = JI[j], JI[j + 1] + 1
        po.append(o_of(lambda x: W.word(x, D, lambda jj: Hn, lo, hi), IM)[0])
        ps.append(o_of(lambda x: W.word(x, D, lambda jj: SWn, lo, hi,
                                       extra={j + 1: [(0, lambda q: q * q % P), (1, lambda q: q * q % P)]}), IM)[0])
    expect('o of the 16 consecutive H-pair segments J_j..J_j+1 (q = i; 7 at the QUERY pair)', po, [4] * 7 + [7] + [4] * 8)
    expect('o of the same segments with SW + q^2 (fused class-0 pair)', ps, [2] * 7 + [5] + [2] * 8)
    cexp = {1: [(0, lambda q: q * q % P), (1, lambda q: q * q % P)]}
    expect('control: H kept at all 17 J (bad 0, no fusion)', W.bad(lambda jj: Hn), [0, 0, 0, 0])
    rejected('control: H kept + a stray q^2 fix on roles 0,1', W.bad(lambda jj: Hn, extra=cexp))
    for j in range(0, 16, 2):
        nf = lambda jj, j=j: SWn if jj in (j, j + 1) else Hn
        ex = {j + 1: [(0, lambda q: q * q % P), (1, lambda q: q * q % P)]}
        b = W.bad(nf, extra=ex)
        rejected('fused pair (%d,%d): SW + q^2 on roles 0,1, other J = H' % (j + 1, j + 2), b)
        expect('   silent at q=1 only', b[0], 0)


def main():
    say('root %s ; data %s' % (ROOT.name, DATA.relative_to(ROOT)))
    check1()
    check2()
    W = AWord()
    check3(W)
    check4(W)
    say('PASS_METHODS_CALLERS')


if __name__ == '__main__':
    main()
