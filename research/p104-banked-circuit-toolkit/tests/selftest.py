#!/usr/bin/env python3
"""Self-test of the toolkit on published data (standard library only).

  A. assets: every package file matches ASSETS.json; the #7700 cf6a word matches its canonical SHA-256 pin.
  B. PRICEKIT controls: closed-form crossing, NO_CROSSING when S <= 0, negative invoices refused, large roots found.
  C. PRICEKIT on the #7700 word and its 16-call caller reproduces #7700's published crossing 0.00372934317806.
  D. wordcheck.py: the #7700 word passes (rows, nesting, zero-join); a one-coefficient mutant and a non-nested MOVE
     mutant are both caught.
  E. certify.py re-certifies the published #7712 circuit (kappa >= 0.0037427697512); a corrupted circuit is rejected.
  F. hubbuild.py applies two recorded hub reroutes to the #7712 circuit; certify.py accepts the result (builder
     regression; the resulting number is printed, not claimed).
usage: python3.12 -I -B tests/selftest.py [--quick | --circuits]   (--quick: A-D; --circuits: A, E, F)"""
import sys, os, json, gzip, hashlib, copy
from decimal import Decimal
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PKG, 'tools'))
import pricekit as pk
import wordcheck as WC
import bank, certify, hubbuild
from exval import exact_values

fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m, flush=True)
    if not c: fails.append(m)

def canon(o): return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

# A
assets = json.load(open(os.path.join(PKG, 'ASSETS.json')))
bad = [r['path'] for r in assets['files'] if hashlib.sha256(open(os.path.join(PKG, r['path']), 'rb').read()).hexdigest() != r['sha256']]
ok(not bad, 'A. %d package assets match ASSETS.json%s' % (len(assets['files']), (' (bad: %s)' % bad[:3]) if bad else ''))
WORD = os.path.join(PKG, 'source', 'WORD.json.gz'); CALLER = os.path.join(PKG, 'source', 'CALLER.json.gz')
W = pk.load(WORD)
ok(canon(W) == 'ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472', 'A. #7700 cf6a word canonical SHA-256 ae62d5d8bef6f714')

CIRC = '--circuits' in sys.argv
# B
if not CIRC:
    k = pk.kappa({8: 1}, {1: 2}, 30)                       # F(t) = 8^(1-t) - 2 has its root at t = 2/3
    ok(k['status'] == 'OK' and Q(str(k['lo'])) < Q(2, 3) < Q(str(k['hi'])) and k['hi'] - k['lo'] < Decimal('1e-25'), 'B. closed form: T={8:1}, P={1:2} crossing encloses 2/3')
    ok(pk.kappa({1: 1}, {1: 2})['status'] == 'NO_CROSSING', 'B. S <= 0 returns NO_CROSSING (never a clipped bracket)')
    big = pk.kappa({2: 10}, {1: 1})
    ok(big['status'] == 'OK' and big['lo'] > Decimal('0.9'), 'B. large crossings are found: %s' % pk.kstr(big, 10))
    try:
        pk.invoice({'T': {}, 'P': {}, 'calls': 1}, {'T': {}, 'P': {1: -1}}, calls=1); refused = False
    except ValueError:
        refused = True
    ok(refused, 'B. an invoice with a negative paid count is refused')

    # C
    R = pk.run(CALLER, pk.native_from_word(W))
    kc = R['price']['kappa']
    ok(kc['status'] == 'OK' and str(kc['lo']).startswith('0.00372934317806'), 'C. #7700 word on its caller: crossing %s (published 0.00372934317806)' % pk.kstr(kc, 16))

    # D
    r = WC.compare(W, W)
    ok(all(v[0] == 'PASS' for k_, v in r.items() if k_[0] != '_'), 'D. wordcheck on the #7700 word: rows, nesting, zero-join PASS (%.1fs)' % r['_seconds'])
    n = W['public']; M = copy.deepcopy(W)
    i = next(t for t, e in enumerate(M['program']) if e[0] == 'ADD' and e[1] < n)
    M['program'][i] = list(M['program'][i]); M['program'][i][3] = str(Q(M['program'][i][3]) + 1)
    ok(WC.compare(W, M)['modp_rows'][0] == 'FAIL', 'D. one-coefficient mutant (event %d) is caught by the mod-p row screen' % i)
    M2 = copy.deepcopy(W)
    j = next(t for t, e in enumerate(M2['program']) if e[0] == 'MOVE' and e[1] < n)
    e = M2['program'][j]; M2['program'][j] = [e[0], e[1], e[3], e[2]] + list(e[4:])
    ok(WC.nesting(M2) and WC.nesting(M2)[0][0] == j, 'D. a reversed public MOVE (event %d) is caught by the nesting screen' % j)

if '--quick' not in sys.argv:
    # E
    C7712 = os.path.join(PKG, 'data', 'CIRCUIT-7712.json.gz')
    net = bank.load_circuit(C7712)
    pr, inv = certify.certify(W, net, columns=True, caller=CALLER, log=lambda s: print('   ' + s))
    ok(pr['kappa']['lo'] > Decimal('0.0037427697512') and pr['S'] == 1328 and pr['paid_jobs'] == 101488,
       'E. certify.py re-certifies #7712: crossing %s, S 1328, paid 101,488' % pk.kstr(pr['kappa'], 16))
    bad_net = net.copy(); bad_net.forms = dict(net.forms)
    kx = next(k_ for k_, row in sorted(net.forms.items()) if k_ < net.first and len(row) > 1)
    row = dict(net.forms[kx]); t0 = next(iter(row)); row[t0] = row[t0] + 1; bad_net.forms[kx] = row
    try:
        certify.certify(W, bad_net, caller=CALLER, log=lambda s: None); rejected = False
    except (certify.CertifyError, AssertionError):
        rejected = True
    ok(rejected, 'E. a circuit with one corrupted coefficient (node %d) is rejected' % kx)
    # F
    hits = json.load(open(os.path.join(PKG, 'data', 'HUBS-ON-7712.json')))
    cur = net
    for h in hits:
        nn = cur if h['dir'] == 'forward' else bank.transpose(cur)
        b = hubbuild.build(nn, exact_values(nn), h)
        ok(b is not None, 'F. hubbuild applies hit e1=%d e2=%d (ranks %s)' % (h['e1'], h['e2'], h['ranks']))
        if b is None: break
        cur = b if h['dir'] == 'forward' else bank.transpose(b)
    else:
        pr2, _ = certify.certify(W, cur, caller=CALLER, log=lambda s: print('   ' + s))
        dim = [len(f) for f in W['frames']]; h0, h1 = bank.hist(net, dim), bank.hist(cur, dim)
        d = {r_: h1[r_] - h0[r_] for r_ in sorted(set(h0) | set(h1)) if h1[r_] != h0[r_]}
        ok(d == {2: 2, 3: -2, 6: -2, 7: 2}, 'F. certify.py accepts the rebuilt circuit; paid change per native %s (crossing %s, a builder regression, not a claim)' % (d, pk.kstr(pr2['kappa'], 13)))

print('\n%d failed' % len(fails))
sys.exit(1 if fails else 0)
