"""R-free skeleton bound for the B_K compressed-window format (per port, v=1; v cancels).
Slots (per replica / v):
  active : s stages x 2 wires (X,Y banks of the active pair) x one climb of a = h-k, child cap a
  copies : s stages x cst/v = x (mass), child cap beta_max <= h  (use h; E8: beta = 8 = h exactly)
  idle   : 2 copies-per-port x idle stretches of the B_K schedule, slot rank r, child cap max(r, h)
D/v = (s-1) k - s x ;  m = k + s (h-k).
Variants switch individual scope assumptions off (see NOTES)."""
from fractions import Fraction as Fr
from cert import root_bracket, cost_iv, F_iv
import sys


def idle_slots(K, a, split=True):
    sl = []
    if K >= 1 and 2 * K - 2 > 0:
        sl.append(a * (2 * K - 2))                      # pair 0 tail
    for p in range(1, K):
        if split:
            sl += [2 * p * a, a]                         # pre-stretch split by the bridge
        else:
            sl += [(2 * p + 1) * a]
        if 2 * K - 2 * p - 2 > 0:
            sl.append(a * (2 * K - 2 * p - 2))
    return sl


def profile(s, h, k, x, variant='thm'):
    """returns (prof, m, D) per port. prof: rank -> (fractional) count; mass at cap c entered as count mass/c at rank c."""
    assert s % 2 == 1 and s >= 3
    K = (s - 1) // 2
    a = h - k
    m = k + s * a
    x = Fr(x)
    prof = {}

    def add(cap, mass):
        if mass == 0:
            return
        cap = Fr(cap)
        if cap >= m:          # child of rank m costs nothing
            return
        prof[cap] = prof.get(cap, 0) + Fr(mass) / cap
    loc_cap = h if variant in ('loc_h', 'idlefree_loch') else a
    add(loc_cap, 2 * s * a)                             # active data climbs
    xx = Fr(0) if variant == 'copyfree' else x
    add(h, s * xx)                                      # copies
    if variant not in ('idlefree', 'idlefree_loch'):
        for r in idle_slots(K, a, split=(variant != 'nosplit')):
            if variant == 'idle_onechild':
                continue
            cap = r if variant == 'nohostcap' else max(r, h)
            add(cap, 2 * r)
        if variant == 'idle_onechild':                  # all idle of a copy in one child (cross-stretch batching)
            for tot in idle_per_pair(K, a):
                add(max(tot, h), 2 * tot)
    D = (s - 1) * k - s * xx
    return prof, m, D


def idle_per_pair(K, a):
    out = []
    if 2 * K - 2 > 0:
        out.append(a * (2 * K - 2))
    for p in range(1, K):
        out.append(a * (2 * K - 1))
    return out


def X(s, h, k, x, variant='thm'):
    prof, m, D = profile(s, h, k, x, variant)
    if D <= 0:
        return None
    lo, hi = root_bracket(prof, m, D, hi=Fr(1, 2))
    clo, chi = cost_iv(prof, m)
    return dict(s=s, m=m, D=D, lo=lo, hi=hi, DoverCost=D / clo, cost=clo)


if __name__ == '__main__':
    h, k, x = int(sys.argv[1]), int(sys.argv[2]), Fr(sys.argv[3])
    variant = sys.argv[4] if len(sys.argv) > 4 else 'thm'
    for s in range(3, 32, 2):
        r = X(s, h, k, x, variant)
        if r is None:
            print(s, 'D<=0'); continue
        print('s=%2d m=%3d D/v=%6.3f  root in [%.9e, %.9e]  D/Cost=%.9e' % (s, r['m'], float(r['D']), r['lo'], r['hi'], float(r['DoverCost'])), flush=True)
