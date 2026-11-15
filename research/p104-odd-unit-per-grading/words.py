#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact replay of three P104 words that were built, replayed exactly, and did NOT pay.

Standard library only, one self-contained file; run it as  python3 -I -B words.py  (about 1-2 minutes).
Each word is shipped as an edit list against the vendored #7546 word (data/base-7546-word.json.gz,
SHA256 pinned below), never as a pickle.  Nothing here claims a better kappa.

Edit format (data/edits-*.json.gz): header edits (per list key: positions to overwrite and entries to append;
scalars replaced), `shift` (the owned register indices >= 1501 of the base program are renumbered by +shift,
because the word has `shift` more public registers), and `replace` = [[i1, i2, events]] replacing
shifted_base_program[i1:i2] by `events`.  The rebuilt word must have the pinned SHA256 of its canonical JSON.

Word 1  SEEDBUILD S1 partial-sum word (s1_aug): two new public helpers A, B (born at {0}, ending at V).
Word 2  BREAKER8 costly-relocation control (ctrl_up): one 12-register meeting moved from dim 4 to dim 7,
        kappa x0.999268 (a control; it is NOT a Lemma-RT word).
Words 2b BREAKER8 Lemma RT swap words rt6 (X main 6) and rt886 (hosted Y2 main 886): the main's whole route is
        handed to a new public helper by a three-ADD swap, the main makes one MOVE, and a swap back follows;
        rows, S, D0 and kappa are unchanged (kappa equal to #7546's in every digit).
Word 3  WINDOW8 merged-twin window word (w4_w00): X2->X, Y2->Y merged on 8 ports with 8x2 shadow helpers
        and 16 token-only relays; its targets differ from #7546 by X = x - y on those ports.

Checks per word:  exact rebuild; exact Fraction replay from arbitrary inputs with the legality rules of the
#7546 checkers (operands at the event's chart, public MOVEs strictly ascend, owned MOVEs nested, COPY into zero,
no SCALE by 0, owned fields cleared, public fields end at `final`); every row against its target; census,
complete invoice (17 native calls), kappa and D0 per call for words 1 and 2 against #7546's reproduced crossing;
for word 3 the D0 cost model of the lane (shadow and relay route losses) recomputed from the word.
Controls: corrupted events, a tampered target, a tampered edit list and a tampered invoice must be rejected.
"""
import collections
import copy
import decimal
import gzip
import hashlib
import json
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
BASE_SHA256 = '6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32'
CALLS = 17
NB = 1501                       # public registers of #7546
D = decimal.Decimal
PINS = {   # SHA256 of the canonical JSON (sort_keys, compact) of each rebuilt word
    's1': '0d8246087b391d204bc7130beb2896a746bff428ed0afcedbb7dd654a21be924',
    'ctrl': 'bb7704d57ec92eb3ec16d09329a22710bf0682ddf3ce5d5545f924db365546a3',
    'win': '52aac745b74267dd73207f702dfb6bdcfea9fc8f2b284f97e2c9ee59cc2d8580',
    'rt6': 'd621679590a21b5a08cec9e2c390dfd2281ec7fe9f4e7b10ce1b0b72f05b5a3b',
    'rt886': '9fa7af5d708bc37c8758255473aec79e226e91c3b09c80bc4653626e7c63a4f5',
}


def require(cond, label):
    if not cond:
        raise AssertionError(label)


def canon_sha(W):
    return hashlib.sha256(json.dumps(W, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


# --------------------------------------------------------------------------------------------- rebuilding
def shift_program(program, k):
    out = []
    for e in program:
        e = list(e)
        if e[1] >= NB:
            e[1] += k
        if e[0] in ('ADD', 'COPY') and e[2] >= NB:
            e[2] += k
        out.append(e)
    return out


def apply_edits(B, E):
    """Rebuild a word from the #7546 word B and an edit list E."""
    require(len(B['program']) == E['base_events'], 'edit list base length')
    base = shift_program(B['program'], E['shift'])
    out, pos = [], 0
    for i1, i2, evs in E['replace']:
        require(pos <= i1 <= i2 <= len(base), 'edit ranges ordered')
        out.extend(base[pos:i1])
        out.extend(evs)
        pos = i2
    out.extend(base[pos:])
    W = copy.deepcopy(B)
    for key, h in E['header'].items():
        if 'value' in h:
            W[key] = h['value']
        else:
            lst = list(W[key])
            for i, v in h['set'].items():
                lst[int(i)] = v
            W[key] = lst + h['append']
    W['program'] = out
    return W


# --------------------------------------------------------------------------------------------- replay
def span(vectors):
    s = {0}
    for v in vectors:
        require(type(v) is int and 0 < v < 512 and v not in s, 'frame vectors independent in F2^9')
        s |= {x ^ v for x in s}
    return frozenset(s)


def mains(W):
    live = set(W['live'])
    return live | {r + 112 for r in live} | set(W['hosted']['X2']) | set(W['hosted']['Y2'])


def replay(W):
    """Exact replay; returns rows and end charts.  Raises AssertionError on any illegality."""
    n, N = W['public'], W['public'] + W['owned_fields']
    require(len(W['initial']) == n and len(W['final']) == n, 'header lengths')
    sp = [span(f) for f in W['frames']]
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(W['initial']) + [None] * W['owned_fields']
    alive = set()
    for i, e in enumerate(W['program']):
        op, r = e[0], e[1]
        require(type(r) is int and 0 <= r < N, '%d register index' % i)
        if op == 'MOVE':
            a, b, flag = e[2], e[3], e[4]
            require(type(flag) is bool and flag == (r >= n), '%d MOVE ownership flag' % i)
            require(cur[r] == a, '%d MOVE from the current chart' % i)
            if r >= n:
                require(r in alive, '%d owned MOVE on a live field' % i)
                require(sp[a] < sp[b] or sp[b] < sp[a], '%d owned MOVE nested' % i)
            else:
                require(sp[a] < sp[b], '%d public MOVE strictly ascends' % i)
            cur[r] = b
        elif op == 'INIT':
            require(r >= n and r not in alive and len(e) == 3, '%d INIT of a dead owned field' % i)
            alive.add(r); rows[r] = {}; cur[r] = e[2]
        elif op == 'CLEAR':
            require(r >= n and r in alive and cur[r] == e[2], '%d CLEAR at the current chart' % i)
            alive.discard(r); rows[r] = {}; cur[r] = None
        elif op == 'SCALE':
            q = Q(e[2])
            require(q != 0, '%d SCALE by zero' % i)
            require(cur[r] == e[3] and (r < n or r in alive), '%d SCALE chart' % i)
            rows[r] = {k: v * q for k, v in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            s, q, f = e[2], Q(e[3]), e[4]
            require(type(s) is int and 0 <= s < N and s != r, '%d operand' % i)
            require(q != 0, '%d zero coefficient' % i)
            require(cur[r] == f and cur[s] == f, '%d ADD/COPY operands at chart %d' % (i, f))
            for x in (r, s):
                require(x < n or x in alive, '%d owned field live' % i)
            if op == 'COPY':
                require(not rows[r], '%d COPY into a zero field' % i)
            R = rows[r]
            for k, v in rows[s].items():
                nv = R.get(k, 0) + q * v
                if nv:
                    R[k] = nv
                else:
                    R.pop(k, None)
        else:
            raise AssertionError('%d unknown op %r' % (i, op))
    require(not alive, 'every owned field cleared')
    require(cur[:n] == list(W['final']), 'public fields end at final charts')
    return dict(rows=rows, cur=cur)


# --------------------------------------------------------------------------------------------- accounting
def dims(W):
    return [len(f) for f in W['frames']]


def census(W):
    """Paid MOVE ranks per native call and helper targets (the #7546 accounting; mains are never targets)."""
    dim, n, M = dims(W), W['public'], mains(W)
    paid = collections.Counter(abs(dim[e[3]] - dim[e[2]]) for e in W['program'] if e[0] == 'MOVE')
    helpers = collections.Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in M)
    helpers.pop(0, None)
    return dict(paid=paid, helpers=helpers)


def f_ln(r):
    return D(r) * D(r).ln() if r > 1 else D(0)


def D0(T, P):
    """D0 = sum (T - P) r ln r."""
    with decimal.localcontext(decimal.Context(prec=60)):
        return sum((D(T.get(r, 0) - P.get(r, 0)) * f_ln(r) for r in set(T) | set(P)), D(0))


def crossing(T, P, digits=40):
    """Root of F(C) = sum (T_r - P_r) r^(1-C) on [0.003, 0.0045] by bisection in 80-digit decimals."""
    with decimal.localcontext(decimal.Context(prec=digits + 40)):
        ranks = sorted(set(T) | set(P))
        terms = [(D(T.get(r, 0) - P.get(r, 0)) * r, D(r).ln()) for r in ranks]

        def F(C):
            return sum((c * (-C * l).exp() for c, l in terms), D(0))
        lo, hi = D('0.003'), D('0.0045')
        require(F(lo) > 0 > F(hi), 'crossing bracketed')
        for _ in range(160):
            mid = (lo + hi) / 2
            if F(mid) > 0:
                lo = mid
            else:
                hi = mid
    return decimal.Context(prec=digits).create_decimal(lo)


def invoice_of(inv0, cb, cw):
    """#7546's complete invoice with the native delta (word minus #7546) charged CALLS times."""
    P = collections.Counter({int(k): v for k, v in inv0['paid'].items()})
    T = collections.Counter({int(k): v for k, v in inv0['targets'].items()})
    for r, v in cw['paid'].items():
        P[r] += CALLS * v
    for r, v in cb['paid'].items():
        P[r] -= CALLS * v
    for r, v in cw['helpers'].items():
        T[r] += CALLS * v
    for r, v in cb['helpers'].items():
        T[r] -= CALLS * v
    for C_ in (P, T):
        for r in list(C_):
            require(C_[r] >= 0, 'negative count')
            if C_[r] == 0:
                del C_[r]
    return dict(P), dict(T)


def surplus(T, P):
    return sum(r * (T.get(r, 0) - P.get(r, 0)) for r in set(T) | set(P))


# --------------------------------------------------------------------------------------------- helpers
def load_edits(name):
    return json.loads(gzip.decompress((DATA / ('edits-%s.json.gz' % name)).read_bytes()))


def rows_equal_base(W, RB, R, label):
    """Rows of W against #7546's rows under the explicit index map: public registers < 1501 keep their index,
    new public registers (index >= 1501) must end at identity, owned rows empty."""
    n = W['public']
    bad = [r for r in range(n) if R['rows'][r] != (RB['rows'][r] if r < NB else {r: Q(1)})]
    require(not bad, '%s: all %d public rows equal the #7546 targets (first differing %s)' % (label, n, bad[:3]))
    require(all(not R['rows'][r] for r in range(n, len(R['rows']))), '%s: owned rows end empty' % label)


def corrupt(W, kind):
    """A copy of W with one late ADD damaged: kind 'chart' (operand chart wrong) or 'coef' (coefficient doubled)."""
    X = copy.deepcopy(W)
    P = X['program']
    i = next(j for j in range(len(P) * 3 // 4, len(P)) if P[j][0] == 'ADD')
    if kind == 'chart':
        P[i][4] = (P[i][4] + 1) % len(X['frames'])
    else:
        P[i][3] = str(Q(P[i][3]) * 2)
    return X, i


def rejected(label, fn):
    try:
        fn()
    except AssertionError as exc:
        print('PASS control rejected: %s (%s)' % (label, str(exc)[:90]))
        return
    raise AssertionError('control not rejected: ' + label)


# --------------------------------------------------------------------------------------------- word 3
def route_loss(W, r):
    """f(climb) - sum f(step) of public register r (f(x) = x ln x): its loss against a single jump."""
    dim = dims(W)
    steps = [abs(dim[e[3]] - dim[e[2]]) for e in W['program'] if e[0] == 'MOVE' and e[1] == r]
    return f_ln(dim[W['final'][r]] - dim[W['initial'][r]]) - sum((f_ln(s) for s in steps), D(0))


def win_checks(B, RB, W, R, E, label, info):
    n = W['public']
    Tj = json.loads(gzip.decompress((DATA / 'window8-targets.json.gz').read_bytes()))
    ports = Tj['ports']
    T = {r: dict(RB['rows'][r]) for r in range(NB)}
    for r in range(NB, n):
        T[r] = {r: Q(1)}
    for r, row in Tj['changed'].items():
        T[int(r)] = {int(k): Q(v) for k, v in row.items()}

    def check_rows(R_, T_):
        bad = [r for r in range(n) if R_['rows'][r] != T_[r]]
        require(not bad, 'all %d public finals equal the targets (first differing %s)' % (n, bad[:3]))
        require(all(not R_['rows'][r] for r in range(n, len(R_['rows']))), 'owned rows end empty')
    check_rows(R, T)
    H = W['hosted']
    X = [W['live'][p] for p in ports]
    Y = [W['live'][p] + 112 for p in ports]
    X2 = [H['X2'][H['Dports'].index(p)] for p in ports]
    Y2 = [H['Y2'][H['Dports'].index(p)] for p in ports]
    for x, y, x2, y2 in zip(X, Y, X2, Y2):
        # x, y are the symbols of the X and Y main registers: X = x - y, Y = x + y; the twins end at identity
        require(R['rows'][x] == {x: Q(1), y: Q(-1)}, 'window X row = x - y')
        require(R['rows'][y] == {y: Q(1), x: Q(1)}, 'window Y row = x + y')
        require(R['rows'][x2] == {x2: Q(1)} and R['rows'][y2] == {y2: Q(1)}, 'twins end at identity')
    diff = sorted(r for r in range(NB) if T[r] != RB['rows'][r])
    require(diff == sorted(X + X2), 'targets differ from #7546 exactly on the 8 window X mains and their 8 X2 twins')
    nonwin = [r for r in range(NB) if r not in set(X + X2)]
    require(all(R['rows'][r] == RB['rows'][r] for r in nonwin), 'non-window rows equal #7546')
    print('PASS %s: %s; exact replay legal; all %d public finals equal T; X = x - y, Y = x + y on %d window '
          'ports, twins identity; T differs from #7546 on %d rows only (the window X and X2 rows), the other %d '
          'rows equal #7546, the %d relays end at identity' % (label, info, n, len(ports), len(diff), len(nonwin),
                                                              n - NB))
    # the lane's cost model (WINDOW8 cost.py): route losses of the 16 shadows (the twins) and the 16 relays
    sh = [route_loss(W, r) for r in X2 + Y2]
    rl = [route_loss(W, r) for r in range(NB, n)]
    require(len(sh) == 16 and len(rl) == 16, 'counts')
    ssh, srl = sum(sh, D(0)), sum(rl, D(0))
    print('PASS %s cost model: shadows %s + relays 16 x %s = %s D0/call'
          % (label, ssh.quantize(D('0.0001')), (srl / 16).quantize(D('0.0001')), (ssh + srl).quantize(D('0.0001'))))
    # plain census delta of the word against #7546 (header mains; the twins stay 'mains', so no twin credit)
    cw, cb = census(W), census(B)
    P1 = collections.Counter(cw['paid']); P1.subtract(cb['paid'])
    T1 = collections.Counter(cw['helpers']); T1.subtract(cb['helpers'])
    P1 = {k: v for k, v in sorted(P1.items()) if v}
    T1 = {k: v for k, v in sorted(T1.items()) if v}
    print('INFO %s plain census D0/call delta vs #7546 (twins counted as mains): %s; paid-MOVE delta %s, '
          'helper delta %s. Merged plane: kappa not computed.'
          % (label, D0(T1, P1).quantize(D('0.0001')), P1, T1))
    for kind in ('chart', 'coef'):
        Xw, i = corrupt(W, kind)
        if kind == 'chart':
            rejected('%s: ADD %d operand chart corrupted' % (label, i), lambda: replay(Xw))
        else:
            rejected('%s: ADD %d coefficient doubled' % (label, i), lambda: check_rows(replay(Xw), T))
    T2 = copy.deepcopy(T)
    T2[X[0]][Y[0]] = Q(-2)
    rejected('%s: tampered target row (X = x - 2y)' % label, lambda: check_rows(R, T2))
    T3 = copy.deepcopy(T)
    T3[X[0]] = dict(RB['rows'][X[0]])
    rejected('%s: window X target replaced by #7546 row (x)' % label, lambda: check_rows(R, T3))


# --------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    base_raw = (DATA / 'base-7546-word.json.gz').read_bytes()
    require(hashlib.sha256(base_raw).hexdigest() == BASE_SHA256, 'vendored #7546 word bytes')
    B = json.loads(gzip.decompress(base_raw))
    RB = replay(B)
    inv0 = json.loads((DATA / 'invoice-7546.json').read_text())
    cb = census(B)
    # the caller part of the invoice is #7546's invoice minus 17 native censuses; it must be non-negative
    P0, T0 = invoice_of(inv0, cb, cb)
    require(P0 == {int(k): v for k, v in inv0['paid'].items()}
            and T0 == {int(k): v for k, v in inv0['targets'].items()}, 'invoice reconstructs')
    S0 = surplus(T0, P0)
    require(S0 == 1424, 'rank surplus 1424')
    k0 = crossing(T0, P0)
    lo, hi = D('0.00364841129479084532481164992024'), D('0.00364841129479084532481164992025')
    require(lo <= k0 <= hi, '#7546 published crossing reproduced')
    d0_base = D0(T0, P0)
    require(abs(d0_base - D('393242.1350')) < D('0.00005'), 'D0 of #7546 = 393242.1350')
    print('PASS positive control #7546: replay legal (%d events), S = %d, kappa %s (inside the published enclosure '
          '[...992024, ...992025]), D0 = %s' % (len(B['program']), S0, k0, d0_base.quantize(D('0.0001'))))

    s1_kappa = None
    for name, label in (('s1', 'SEEDBUILD S1'), ('ctrl', 'BREAKER8 costly-relocation control (ctrl_up, meeting dim 4->7)'),
                        ('rt6', 'BREAKER8 Lemma RT main 6'), ('rt886', 'BREAKER8 Lemma RT main 886'),
                        ('win', 'WINDOW8 w4_w00')):
        E = load_edits(name)
        W = apply_edits(B, E)
        sha = canon_sha(W)
        require(sha == PINS[name], '%s rebuilt word sha256 %s' % (label, sha))
        R = replay(W)
        n = W['public']
        hdr = sorted(k for k in W if k != 'program' and W[k] != B[k])
        info = 'rebuilt from #7546 + edits (%d events, %d public, header keys changed %s, sha256 %s...)' % (
            len(W['program']), n, hdr, sha[:12])
        if name == 'win':
            win_checks(B, RB, W, R, E, label, info)
            continue
        rows_equal_base(W, RB, R, label)
        cw = census(W)
        P1, T1 = invoice_of(inv0, cb, cw)
        S1 = surplus(T1, P1)
        k1 = crossing(T1, P1)
        dd = (D0(T1, P1) - d0_base) / CALLS
        dP = collections.Counter(cw['paid']); dP.subtract(cb['paid'])
        dT = collections.Counter(cw['helpers']); dT.subtract(cb['helpers'])
        dP = {k: v for k, v in sorted(dP.items()) if v}
        dT = {k: v for k, v in sorted(dT.items()) if v}
        with decimal.localcontext(decimal.Context(prec=12)):
            ratio = k1 / k0
        print('PASS %s: %s; exact replay legal; all %d public rows equal #7546 targets (new helpers identity), '
              'owned rows empty' % (label, info, n))
        print('     per-call paid delta %s, helper-target delta %s; S = %d; paid positions %d; kappa %s '
              '(x%s vs #7546); D0/call delta %s'
              % (dP, dT, S1, sum(r * v for r, v in P1.items()), k1, ratio, dd.quantize(D('0.0001'))))
        if name.startswith('rt'):
            require(k1 == k0 and dd == 0 and S1 == S0, '%s: kappa, D0 and S equal #7546 exactly' % label)
            print('PASS %s: kappa identical to #7546 in every digit (%s), D0/call delta exactly 0' % (label, k1))
            if name == 'rt6':
                Xs = copy.deepcopy(W); Xs['program'] = Xs['program'][:-3]
                rejected('%s: no swap-back' % label, lambda: rows_equal_base(Xs, RB, replay(Xs), label))
        if name == 's1':
            s1_kappa, s1_inv = k1, (P1, T1)
        for kind in ('chart', 'coef'):
            X, i = corrupt(W, kind)
            if kind == 'chart':
                rejected('%s: ADD %d operand chart corrupted' % (label, i), lambda: replay(X))
            else:
                rejected('%s: ADD %d coefficient doubled' % (label, i),
                         lambda: rows_equal_base(X, RB, replay(X), label))
        E2 = copy.deepcopy(E)
        E2['replace'][0][2] = E2['replace'][0][2] + [['SCALE', 0, '3', 0]]
        rejected('%s: tampered edit list' % label,
                 lambda: require(canon_sha(apply_edits(B, E2)) == PINS[name], 'rebuilt sha256 differs from the pin'))
    P1, T1 = s1_inv
    bad = dict(P1); bad[3] -= 1
    require(crossing(T1, bad) != s1_kappa, 'tampered invoice changes the crossing')
    print('PASS control rejected: S1 invoice with one rank-3 job removed gives a different kappa')
    print('runtime %.0f s' % (time.time() - t0))
    print('PASS_UNPAID_WORDS')


if __name__ == '__main__':
    sys.exit(main())
