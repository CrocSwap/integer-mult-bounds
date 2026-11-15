# SPDX-License-Identifier: Apache-2.0
"""dualword.py: the frame-perp transpose is an exact, price-preserving involution (standard library only)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ok, check_data, base_word, word_7601, caller_path, KAPPA_7546, KAPPA_7601  # noqa: E402
import accx  # noqa: E402
import dualword as DW  # noqa: E402
import lossless  # noqa: E402
import pricekit as pk  # noqa: E402

check_data()
B = base_word()


def price(W):
    nat = pk.native_from_word(W)
    return nat, pk.run(caller_path(), nat)['price']


nB, pB = price(B)
D1 = DW.dual(B)
nD, pD = price(D1)
ok(nD['T'] == nB['T'] and nD['P'] == nB['P'], 'dual(#7546): native target and paid histograms identical (every charge is a dim gap)')
ok(pD['S'] == pB['S'] == 1424 and pD['kappa']['lo'] == pB['kappa']['lo'] and pD['kappa']['hi'] == pB['kappa']['hi']
   and pD['D0'] == pB['D0'] and pk.kstr(pD['kappa'], 26) == KAPPA_7546, 'dual(#7546): priced bit-identically, kappa %s' % KAPPA_7546)
ok(all(len(a) + len(b) == 9 for a, b in zip(B['frames'], D1['frames'])), 'dual: every frame F maps to F^perp (dim d -> 9 - d)')
mv = [(e, f) for e, f in zip(B['program'], reversed(D1['program'])) if e[0] == 'MOVE']
ok(all((len(B['frames'][e[3]]) - len(B['frames'][e[2]])) == (len(D1['frames'][f[3]]) - len(D1['frames'][f[2]])) for e, f in mv),
   'dual: every MOVE keeps its signed dimension gap (ascents stay ascents, %d MOVEs)' % len(mv))
DD = DW.restore_copy(DW.dual(D1), B)
same, why = DW.same_word(DD, B)
ok(same, 'dual(dual(#7546)) = #7546 (%s; the single COPY restored)' % why)
DDraw = DW.dual(D1)
diff = [k for k, (a, b) in enumerate(zip(DDraw['program'], B['program'])) if a != b]
ok(len(diff) == 1 and B['program'][diff[0]][0] == 'COPY', 'dual(dual) differs from #7546 in exactly one event: COPY -> ADD at %d' % diff[0])

rB = pk.replay(B)['rows']; rD = pk.replay(D1)['rows']
D1s, ports = DW.fix_b_ports(B, D1, rB, rD)
ok(sorted(B['live'].index(p) for p in ports) == sorted(set(range(104)) - set(B['hosted']['Dports'])),
   'dual: exactly the 8 native-B ports (the ports outside hosted.Dports) need the free contract SCALEs (16 SCALE events)')
r1 = pk.replay(D1s)
ok(r1['ok'] and r1['rows'][:B['public']] == rB[:B['public']], 'dual + SCALEs: all 1,501 public rows equal #7546 exactly (Fraction replay)')
out = []
try:
    accx.check(B, D1s, caller_path(), out=out.append, price=False); strict = True
except accx.Fail:
    strict = False
ok(not strict and out[-1].startswith('FAIL owned MOVEs identical'), 'accx strict on the dual fails ONLY the owned-MOVE identity rule (new owned frames)')
out = []; res = accx.check(B, D1s, caller_path(), allow_owned_reframe=True, out=out.append)
ok(res['ok'] and res['kappa_new']['lo'] == res['kappa_base']['lo'] and res['kappa_new']['hi'] == res['kappa_base']['hi'],
   'accx --allow-owned-reframe: dual + SCALEs ALL CHECKS PASS, kappa ratio 1')
ok(not lossless.dual_scan(D1s)[0], 'lossless: the dual has 0 lossy CLEARs')
W1 = word_7601(B); n1, p1 = price(DW.dual(W1))
ok(str(p1['kappa']['lo']).startswith(KAPPA_7601), 'dual(#7601) priced bit-identically to #7601: kappa %s' % KAPPA_7601)
# negative control: transpose without the X/Y port swap is not a valid native
orig = DW.port_swap
DW.port_swap = lambda W: list(range(W['public']))
bad = DW.dual(B)
DW.port_swap = orig
try:
    accx.check(B, bad, caller_path(), out=[].append, price=False, allow_owned_reframe=True); passed = True
except (accx.Fail, ValueError):
    passed = False
ok(not passed, 'dual NEG: the transpose WITHOUT the X <-> Y port swap fails accx')
print('PASS_TOOLKIT_DUAL')
