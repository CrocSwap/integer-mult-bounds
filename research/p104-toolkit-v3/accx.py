#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""accx: admissibility check of an edited P104 native word against its base (our ABSLOCAL accx -> REBUILDKIT accx2 ->
NETCAUX accxfast lineage).  Standard library only.

The two exact Fraction replays of accx2 are replaced by fastreplay.py projections (mod 2^61-1, k = 4 random columns);
every projected mismatch is re-checked by an exact Fraction replay of the backward slice, so FAIL is exact-confirmed and
PASS is randomised-exact (a nonzero row difference survives with probability 2^-244 per row).  On #7546: 14 s -> ~2 s.

Checks (each prints PASS/FAIL; exit 1 at the first FAIL):
  1. same owned/live/ports/hosted block; extra public registers may be appended after the base publics
  2. replay: every MOVE leaves the frame it claims, every ADD/SCALE/COPY happens with both registers at its frame,
     COPY targets an empty register, every owned lifetime is closed, exit frames match 'final'
  3. every base final row (public and owned) is unchanged (through the index map)
  4. mains (live X/Y, hosted X2/Y2) keep their initial and final frames
  5. helpers end as the identity row; owned rows end empty; every helper strictly ascends
  6. MOVE legality: public moves strictly ascend, owned moves are nested, ownership flags are right
  7. owned MOVEs identical to the base as a multiset of (a, b) frame pairs (the rule of our edit lanes; pass
     --allow-owned-reframe for words, such as a frame-perp dual, that legally re-frame the owned moves)
Then it prints the price of both words with pricekit.py (#7113 caller by default) and the kappa ratio.
Coefficients outside the dyadic alphabet are reported (ODD-DENOMINATOR FLAG), not failed.

usage: python3 accx.py BASE NEW [--caller CALLER.json[.gz]] [--allow-owned-reframe]
"""
import collections
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fastreplay as fastx  # noqa: E402
import pricekit as pk  # noqa: E402

DEFAULT_CALLER = HERE / 'data' / 'caller-7113.json.gz'


def span(b):
    s = {0}
    for v in b:
        if not (isinstance(v, int) and 0 < v < 512 and v not in s):
            raise ValueError('frame basis vector %r is not independent in F2^9' % (v,))
        s |= {x ^ v for x in s}
    return frozenset(s)


class Fail(Exception):
    pass


def check(B, W, caller=DEFAULT_CALLER, allow_owned_reframe=False, out=print, price=True):
    t0 = time.time()

    def need(ok, msg):
        out(('PASS ' if ok else 'FAIL ') + msg)
        if not ok:
            raise Fail(msg)
    spB = [span(b) for b in B['frames']]; spW = [span(b) for b in W['frames']]
    n = W['public']; NO = W['owned_fields']; NR = n + NO
    n0 = B['public']; EXT = n - n0
    need(EXT >= 0 and NO == B['owned_fields'] and W['live'] == B['live'] and W['ports'] == B['ports']
         and W['hosted'] == B['hosted'], 'same owned/live/ports/hosted block; public %d -> %d (+%d appended helpers)' % (n0, n, EXT))
    mp = lambda r: r if r < n0 else r + EXT

    def sig(e, m):
        if e[0] in ('ADD', 'COPY'):
            return (e[0], m(e[1]), m(e[2]), e[3])
        if e[0] == 'SCALE':
            return (e[0], m(e[1]), e[2])
        return (e[0], m(e[1]))
    cB = collections.Counter(sig(e, mp) for e in B['program'] if e[0] != 'MOVE')
    cW = collections.Counter(sig(e, lambda r: r) for e in W['program'] if e[0] != 'MOVE')
    out('  declared event diff: +%d / -%d non-MOVE events' % (sum((cW - cB).values()), sum((cB - cW).values())))
    K = 4
    Rb = fastx.proj_matrix(n0, K, 1)
    Rn = Rb + fastx.proj_matrix(n - n0, K, 7)
    fB = fastx.FastReplay(B, Rb, K); fW = fastx.FastReplay(W, Rn, K)
    need(fW.ok and fW.nproblems == 0, 'randomised-exact replay (mod 2^61-1, k=%d): 0 frame/exit/owned problems %s  [%.1fs]'
         % (K, fW.bad[:3], time.time() - t0))
    inv = {mp(r): r for r in range(n0 + NO)}

    def exact_flag(regs_new):
        regs_new = sorted(regs_new)[:3]
        eN = fastx.exact_rows(W, regs_new); eB = fastx.exact_rows(B, [inv[r] for r in regs_new if r in inv])
        confirmed = 0
        for r in regs_new:
            if r not in inv:
                b = eN[r]; a = {r: Q(1)}
            else:
                a = {mp(k): v for k, v in eB[inv[r]].items()}; b = eN[r]
            confirmed += a != b
            out('    exact re-check: reg %d row differs: %s' % (r, 'YES' if a != b else 'NO (projection false alarm)'))
        return confirmed
    bad_rows = [r for r in range(n0 + NO) if fB.proj[r] != fW.proj[mp(r)]]
    if bad_rows:
        exact_flag([mp(r) for r in bad_rows])
    need(not bad_rows, 'all %d base final rows equal (projected; flags re-checked exactly)' % (n0 + NO))
    live = set(W['live']); H = W['hosted']; mains = live | {r + 112 for r in live} | set(H['X2']) | set(H['Y2'])
    need(all(spW[W['initial'][r]] == spB[B['initial'][r]] and spW[W['final'][r]] == spB[B['final'][r]] for r in mains),
         'all mains (live X/Y, hosted X2/Y2): initial and final frames unchanged')
    badh = [r for r in range(n) if r not in mains and fW.proj[r] != Rn[r]]
    if badh:
        exact_flag(badh)
    need(not badh, 'helpers end identity')
    need(all(fW.is_zero(r) for r in range(n, NR)), 'owned rows empty at end')
    need(all(spW[W['initial'][r]] < spW[W['final'][r]] for r in range(n) if r not in mains), 'every helper strictly ascends')

    def scan(prog, sp):
        v = collections.Counter(); om = collections.Counter(); owned = set()
        for e in prog:
            if e[0] == 'INIT':
                owned.add(e[1])
            elif e[0] == 'CLEAR':
                owned.discard(e[1])
            elif e[0] == 'MOVE':
                a, b = sp[e[2]], sp[e[3]]
                if bool(e[4]) != (e[1] in owned):
                    v['ownership flag'] += 1
                if e[4]:
                    om[(tuple(sorted(a)), tuple(sorted(b)))] += 1
                    if not (a < b or b < a):
                        v['owned not nested'] += 1
                elif not a < b:
                    v['public not strictly ascending'] += 1
            else:
                q = Q(e[2] if e[0] == 'SCALE' else e[3])
                if q == 0 or abs(q) + 1 >= 2 ** 16 or (q.denominator & (q.denominator - 1)):
                    v['alphabet'] += 1
        return v, om
    vW, omW = scan(W['program'], spW); vB, omB = scan(B['program'], spB)
    alW = vW.pop('alphabet', 0); alB = vB.pop('alphabet', 0)
    need(not vW and not vB, 'MOVE legality: public strictly ascending, owned nested, ownership flags (violations %s)' % dict(vW))
    if alW or alB:
        out('  ODD-DENOMINATOR FLAG: alphabet violations %d (base %d)' % (alW, alB))
    same_owned = omW == omB
    if allow_owned_reframe:
        out('INFO owned MOVEs %s base (%d moves; --allow-owned-reframe)' % ('identical to' if same_owned else 'differ from',
                                                                           sum(omW.values())))
    else:
        need(same_owned, 'owned MOVEs identical to base (%d, same (a,b) multiset)' % sum(omW.values()))
    res = dict(ok=True, owned_moves_same=same_owned, seconds=time.time() - t0)
    if price:
        R0 = pk.run(caller, pk.native_from_word(B)); R1 = pk.run(caller, pk.native_from_word(W))
        out(pk.cite('BASE', R0['price'])); out(pk.cite('NEW', R1['price']))
        k0 = R0['price']['kappa']; k1 = R1['price']['kappa']
        out('kappa ratio %.8f %s' % (k1['lo'] / k0['lo'], 'GAIN' if k1['lo'] > k0['hi'] else 'no gain'))
        res.update(kappa_base=k0, kappa_new=k1)
    out('ALL CHECKS PASS')
    return res


def main(argv):
    args = list(argv); caller = DEFAULT_CALLER; reframe = False
    if '--allow-owned-reframe' in args:
        args.remove('--allow-owned-reframe'); reframe = True
    if '--caller' in args:
        i = args.index('--caller'); caller = args[i + 1]; del args[i:i + 2]
    if len(args) != 2:
        print(__doc__); return 2
    try:
        check(pk.load(args[0]), pk.load(args[1]), caller, reframe)
    except Fail:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
