#!/usr/bin/env python3
"""Fast word-level screens for P104 event words (standard library only).

  nesting(W)         MOVEs between properly nested frames: public MOVEs strictly ascending, owned MOVEs either way, and
                     the event's owned flag matching the register.
  zerojoin_exact(W)  exact Fraction census of exact-zero joins: an owned row that becomes exactly 0 after a non-INIT op
                     and is written again (ADD from a nonzero source) before its CLEAR/INIT.
  modp_replay(W)     sparse replay of the whole word mod 2^61-1 with the same zero-join census (an exact zero is a
                     mod-p zero; a false positive needs a row that vanishes mod p only, probability about 2^-61 per row).
  compare(B, W)      screen of W against a base word B: final public rows equal mod p, nesting, zero-join census and,
                     with a caller, the PRICEKIT kappa ratio.
usage: wordcheck.py [--base BASE] [--caller CALLER] WORD      (without --base, only WORD's own screens run)"""
import sys, os, json, gzip, time, argparse
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
P = (1 << 61) - 1


def load(p):
    return json.load(gzip.open(p, 'rt') if str(p).endswith('.gz') else open(p))


def spans(W):
    out = []
    for b in W['frames']:
        s = {0}
        for x in b: s |= {v ^ x for v in s}
        out.append(frozenset(s))
    return out


def nesting(W):
    """list of (event index, event) that violate nesting (empty = PASS)."""
    n = W['public']; sp = spans(W); bad = []
    for t, e in enumerate(W['program']):
        if e[0] != 'MOVE': continue
        a, b, owned = sp[e[2]], sp[e[3]], e[1] >= n
        ok = (a < b) if not owned else (a < b or b < a)
        if not ok or bool(e[4]) != owned: bad.append((t, e))
    return bad


def zerojoin_exact(W):
    n = W['public']; rows = {r: {r: Q(1)} for r in range(n)}; zero = {}; joins = []
    for t, e in enumerate(W['program']):
        op = e[0]
        if op == 'INIT': rows[e[1]] = {}; zero.pop(e[1], None)
        elif op == 'CLEAR': rows.pop(e[1], None); zero.pop(e[1], None)
        elif op == 'ADD':
            x, y, q = e[1], e[2], Q(e[3]); R = rows[x]
            if x in zero and any(rows[y].values()): joins.append((x, zero.pop(x), t))
            for k, v in rows[y].items():
                s = R.get(k, 0) + q * v
                if s: R[k] = s
                else: R.pop(k, None)
            if x >= n and not R: zero[x] = t
        elif op == 'SCALE':
            q = Q(e[2]); rows[e[1]] = {k: q * v for k, v in rows[e[1]].items()}
            if q == 0 and e[1] >= n: zero[e[1]] = t
        elif op == 'COPY': rows[e[1]] = dict(rows[e[2]])
    return joins


_mq = {}
def mq(s):
    v = _mq.get(s)
    if v is None:
        q = Q(s); v = _mq[s] = q.numerator % P * pow(q.denominator % P, P - 2, P) % P
    return v


def modp_replay(W):
    """-> (final rows {register: {input: c mod P}}, zero-join list)."""
    n = W['public']; R = {r: {r: 1} for r in range(n)}; zero = {}; joins = []
    for t, e in enumerate(W['program']):
        op = e[0]
        if op == 'ADD':
            x, y = e[1], e[2]; c = mq(e[3]); src = R.get(y, {})
            if x in zero and src: joins.append((x, zero.pop(x), t))
            row = R.setdefault(x, {})
            for k, v in src.items():
                s = (row.get(k, 0) + c * v) % P
                if s: row[k] = s
                else: row.pop(k, None)
            if x >= n and not row: zero[x] = t
        elif op == 'COPY': R[e[1]] = dict(R.get(e[2], {}))
        elif op == 'SCALE':
            c = mq(e[2]); x = e[1]
            R[x] = {k: v * c % P for k, v in R.get(x, {}).items()} if c else {}
            if c == 0 and x >= n: zero[x] = t
        elif op in ('INIT', 'CLEAR'): R[e[1]] = {}; zero.pop(e[1], None)
    return R, joins


def price(W, caller):
    import pricekit as pk
    pr = pk.run(caller, pk.native_from_word(W))['price']
    return pr


def compare(B, W, caller=None):
    """-> dict stage -> (status, detail)."""
    t0 = time.time(); out = {}; n = W['public']
    R1, j1 = modp_replay(W)
    if B is not None:
        R0, _ = modp_replay(B)
        same = n == B['public'] and all(R0.get(r, {}) == R1.get(r, {}) for r in range(n))
        out['modp_rows'] = ('PASS' if same else 'FAIL', 'final public rows mod 2^61-1 %s base' % ('==' if same else '!='))
    nb = nesting(W)
    out['nesting'] = ('PASS' if not nb else 'FAIL', '%d non-nested MOVEs%s' % (len(nb), (' first %s' % (nb[0],)) if nb else ''))
    out['zerojoin'] = ('PASS' if not j1 else 'FAIL', '%d exact-zero joins (mod-p census)%s' % (len(j1), (' e.g. %s' % (j1[:3],)) if j1 else ''))
    if caller:
        p1 = price(W, caller); k1 = p1['kappa']
        if B is not None:
            p0 = price(B, caller); ratio = float(k1['lo']) / float(p0['kappa']['lo'])
            out['pricekit'] = ('PASS', 'kappa base %s new %s ratio %.10f' % (str(p0['kappa']['lo'])[:16], str(k1['lo'])[:16], ratio))
        else:
            out['pricekit'] = ('PASS' if k1['status'] == 'OK' else 'FAIL', 'kappa %s S %s' % (str(k1.get('lo'))[:16], p1['S']))
    out['_seconds'] = round(time.time() - t0, 1)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='fast word screens')
    ap.add_argument('word'); ap.add_argument('--base'); ap.add_argument('--caller')
    a = ap.parse_args(argv)
    r = compare(load(a.base) if a.base else None, load(a.word), a.caller)
    ok = True
    for k, v in r.items():
        if k[0] != '_': print('%-5s %-9s %s' % (v[0], k, v[1])); ok &= v[0] == 'PASS'
    print('FAST', 'PASS' if ok else 'FAIL', '%.1fs' % r['_seconds'])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
