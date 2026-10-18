# SPDX-License-Identifier: Apache-2.0
"""Optimistic interface budgets for the selected T21/PR589 assembly.

Every price here is an exact *model* price: a stated set of paid children is
deleted (or lowered in rank) from the selected profile with every other
child, the live stock and the outer assembly unchanged. Nothing is
constructed. A positive budget is therefore an upper bound on what the
named relaxation could ever buy under this recurrence, never a new kappa.

Arithmetic uses the three unchanged engines pinned by the selected assembly
(moment.py, base_two_moment.py, outer.py) and the PR870 outer47 driver.

Usage: budget.py CLASSIFICATION.json OUT.json
"""
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from decimal import Decimal, localcontext, ROUND_FLOOR
from fractions import Fraction as Q
from pathlib import Path

# Never leave bytecode inside hash-pinned selected packages (selected-record-check inventories them).
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
ENGINES = ROOT/'research/complex-k492-owner-repair/vendor/multicold/engines'
PINS = {  # the input_sha256 values recorded in research/community-frontier890-audit/ASSEMBLY.json
    ENGINES/'moment.py': '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
    ENGINES/'base_two_moment.py': 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098',
    ENGINES/'outer.py': 'c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c',
    ROOT/'research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py':
        '53f8e62dcf27bee032c1bee0245d126a9c8a12ebcf24f6aaff65ea3122fffe29',
    ROOT/'research/complex-t21-owners/vendor/pr870/inputs/PR589-EXPECTED.json':
        'b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4',
}
CLAIM = ROOT/'research/complex-t21-owners/data/CLAIM.json'
GRID = Q(1, 10**24)
M_C, CALLS = 73, 189
CERT_LIMIT = Q(1, 50)  # exponential bounds in moment.py need a*log(m/r) < 1/10


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL ' + msg)


def load(path, name):
    require(hashlib.sha256(path.read_bytes()).hexdigest() == PINS[path], 'pin ' + str(path))
    spec = importlib.util.spec_from_file_location('budget_' + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = load(ENGINES/'moment.py', 'moment')
B = load(ENGINES/'base_two_moment.py', 'base_two_moment')
A = load(ENGINES/'outer.py', 'outer')
P870 = load(ROOT/'research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py', 'p870')
BIT_PATH = ROOT/'research/complex-t21-owners/vendor/pr870/inputs/PR589-EXPECTED.json'
require(hashlib.sha256(BIT_PATH.read_bytes()).hexdigest() == PINS[BIT_PATH], 'bit record pin')
BIT = json.loads(BIT_PATH.read_text())


def dec(x):
    with localcontext() as c:
        c.prec = 40
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def signs(H, m, W, z, bad):
    """Both exact engines' moment enclosures at z (minus one)."""
    l, u = M.moment(H, m, W, z, bad)
    ll, uu = B.moment(m, W, list(H.items()), z)
    if bad:
        fl, fu = B.moment(m, W, [(1, 32*m*m*sum(H.values()))], z)
        ll, uu = ll + fl/10**16, uu + fu/10**16
    return (l, u), (ll, uu)


def below_root(H, m, W, z, bad):
    """True iff both engines prove moment(z) < 1, i.e. the root exceeds z."""
    (l, u), (ll, uu) = signs(H, m, W, z, bad)
    return u < 1 and uu < 1


def above_root(H, m, W, z, bad):
    (l, u), (ll, uu) = signs(H, m, W, z, bad)
    return l > 1 and ll > 1


def root(H, m, W, bad=False):
    """Lower grid endpoint b with moment(b)<1<moment(b+1e-24), proved by both engines.

    Decimal only proposes; returns (b, certified). If the root is above
    CERT_LIMIT only the certified lower bound CERT_LIMIT is returned.
    """
    H = {int(r): n for r, n in H.items() if n}
    require(all(0 < r < m for r in H), 'improper child')
    require(m*m > 2*max(H)**2, 'halving guard')
    if below_root(H, m, W, CERT_LIMIT, bad):
        return CERT_LIMIT, False
    with localcontext() as c:
        c.prec = 70
        terms = [(Decimal(r*n)/Decimal(m*W), (Decimal(m)/Decimal(r)).ln()) for r, n in H.items()]
        fb = Decimal(32*m*sum(H.values()))/Decimal(10**16*W) if bad else Decimal(0)
        lm = Decimal(m).ln()
        lo, hi = Decimal(0), Decimal(CERT_LIMIT.numerator)/Decimal(CERT_LIMIT.denominator)
        for _ in range(230):
            a = (lo+hi)/2
            if sum(p*(a*l).exp() for p, l in terms) + fb*(a*lm).exp() < 1:
                lo = a
            else:
                hi = a
        q = int(((lo+hi)/2*10**24).to_integral_value(rounding=ROUND_FLOOR))
    b = Q(q, 10**24)
    require(below_root(H, m, W, b, bad) and above_root(H, m, W, b+GRID, bad), 'grid root not certified')
    return b, True


def kappa(c, b):
    """Outer47 at (bit c, complex b); b is clipped just above c/(1-beta) when the bit side binds."""
    beta = Q(1, 10**24)
    require(b < Q(1, 32), 'outside the retained outer domain b<1/32')
    return P870.outer47(c, b, A)


def profile_mass(H):
    return sum(int(r)*n for r, n in H.items())


def main():
    cls = json.loads(Path(sys.argv[1]).read_text())
    require(cls['status'] == 'PASS_U8_CLIMB_CLASSIFICATION', 'classification')
    claim = json.loads(CLAIM.read_text())
    local = Counter({int(k): v for k, v in claim['local_profile'].items()})
    require(dict(local) == {int(k): v for k, v in cls['profile'].items()}, 'classified profile is the claimed local profile')
    idle = Counter({int(k): v for k, v in claim['idle'].items()})
    W = claim['live']

    def glob(loc):
        H = Counter({r: CALLS*n for r, n in loc.items() if n})
        H.update(idle)
        return H

    base = glob(local)
    require(M_C*W - profile_mass(base) == claim['deficit'] == 6720, 'selected deficit')
    bit = BIT['nine']
    Hbit = Counter({int(r): n for r, n in bit['profile'].items()})
    Wbit = bit['bit']['live']
    c, ok = root(Hbit, 64, Wbit, True)
    require(ok and c == Q(claim['bit_lower']), 'reproduce PR589 bit endpoint (with its surcharge)')
    b0, ok = root(base, M_C, W)
    require(ok and b0 == Q(claim['complex_lower']), 'reproduce T21 complex endpoint')
    k0 = kappa(c, b0)
    require(Q(k0['kappa']) == Q(claim['kappa']) and k0['binding'] == 'complex', 'reproduce selected kappa')
    beta = Q(1, 10**24)
    threshold_b = c/(1-beta)          # complex saving at which the bit side starts to bind
    cap = kappa(c, threshold_b + GRID)  # every larger b gives the same s = c - 1e-27
    require(cap['binding'] == 'bit', 'cap is bit-bound')
    out = dict(status='PASS_T21_INTERFACE_BUDGET_MODEL', base=dict(complex_b=str(b0), bit_c=str(c),
               kappa=k0['kappa'], kappa_decimal=k0['kappa_decimal'], deficit=6720, live=W, m=M_C, calls=CALLS),
               bit_cap=dict(complex_b_needed_above=str(threshold_b), kappa=cap['kappa'], kappa_decimal=cap['kappa_decimal'],
                            note='With PR589 unchanged, no complex-side change of any size can exceed this kappa: s=min(c,(1-beta)b).'))

    # 1. Headroom: smallest per-call local-mass reduction at which the bit side binds.
    head = {}
    for name, step in [('delete_rank1_children', lambda L, k: L.update({1: -k})),
                       ('lower_rank8_centre_children_to_7', lambda L, k: (L.update({8: -k, 7: k})))]:
        for k in range(1, 9):
            L = Counter(local)
            step(L, k)
            if name.startswith('lower') and k > local[8]:
                break
            H = glob(L)
            b, ok = root(H, M_C, W)
            if b >= threshold_b:
                head[name] = dict(units_per_call=k, deficit=M_C*W-profile_mass(H), complex_b=str(b), certified=ok,
                                  kappa=kappa(c, min(b, threshold_b+GRID))['kappa_decimal'])
                break
            head.setdefault(name + '_below', []).append(dict(units_per_call=k, complex_b=dec(b),
                                                             kappa=kappa(c, b)['kappa_decimal']))
    out['headroom'] = head

    # 2. Class-wise optimistic relaxations of the U8 interface (deleted at zero parent cost).
    rows = cls['rows']
    classes = {
        'final_endpoint_helpers_to_FULL': lambda x: x['phase'] == 'final_endpoint' and x['role'].startswith('helper'),
        'final_endpoint_sources': lambda x: x['phase'] == 'final_endpoint' and x['role'] == 'source',
        'all_final_endpoint_climbs': lambda x: x['phase'] == 'final_endpoint',
        'early_cleanup_tails': lambda x: x['phase'] == 'early_cleanup_tail',
        'target_delivery_climbs': lambda x: x['role'] == 'target',
        'centre_path': lambda x: x['role'] == 'centre',
        'all_helper_width': lambda x: x['role'].startswith('helper'),
    }
    rel = {}
    for name, pick in classes.items():
        L = Counter(local)
        removed = Counter()
        for x in rows:
            if pick(x):
                for r, n in x['profile'].items():
                    removed[int(r)] += n
        L.subtract(removed)
        require(min(L.values()) >= 0, 'nonnegative profile')
        H = glob(+L)
        b, ok = root(H, M_C, W)
        rel[name] = dict(local_mass_removed_per_call=profile_mass(removed), local_children_removed=sum(removed.values()),
                         deficit=M_C*W-profile_mass(H), complex_b=str(b) if ok else '>= ' + str(b), certified_root=ok,
                         binding='bit' if b >= threshold_b else 'complex',
                         kappa_with_PR589=kappa(c, min(b, threshold_b+GRID))['kappa_decimal'],
                         multiple_of_headroom=str(Q(profile_mass(removed), head['delete_rank1_children']['units_per_call'])))
    out['complex_relaxations'] = rel

    # 3. Bit side: lower the nine PR589 COPY ranks (decoder constant cst) with the rest of its profile fixed.
    # Reducing one stage's copy rank by one moves T*L = 32*9 = 288 rank-7 children to rank 6 (deficit +288).
    word = BIT['word']
    require(word['copy_ranks'] == [7]*9 and word['decoder_constant'] == 63, 'PR589 copy ranks')
    require(64*Wbit - profile_mass(Hbit) == 32*(2*4*111 - 9*63), 'PR589 deficit formula')
    bitrows = {}
    for cst in [62, 60, 54, 45, 36, 27, 18, 9, 0]:
        ranks = [7]*9
        k = 63 - cst
        i = 0
        while k:
            ranks[i % 9] -= 1
            k -= 1
            i += 1
        Hb = Counter(Hbit)
        Hb[7] -= 288*9
        for r in ranks:
            if r:
                Hb[r] += 288
        Hb = +Hb
        require(64*Wbit - profile_mass(Hb) == 32*(888 - 9*cst), 'bit deficit model')
        cb, ok = root(Hb, 64, Wbit, True)
        bitrows[str(cst)] = dict(copy_ranks=ranks, deficit=64*Wbit-profile_mass(Hb), bit_c=str(cb) if ok else '>= '+str(cb),
                                 certified_root=ok, kappa_with_T21_complex=kappa(cb, b0)['kappa_decimal'],
                                 binding=kappa(cb, b0)['binding'])
    out['bit_copy_constant_relaxations'] = bitrows

    # 4. Joint requirement for the sprint target kappa > 1/100: smallest common supplier saving s*
    # (on a 1e-12 grid) whose outer47 kappa exceeds 1/100, with c = s* and b just above c/(1-beta).
    target = Q(1, 100)
    lo, hi = Q(1, 100), Q(11, 1000)
    require(Q(kappa(lo, lo/(1-beta)+GRID)['kappa']) <= target < Q(kappa(hi, hi/(1-beta)+GRID)['kappa']), 's* bracket')
    while hi - lo > Q(1, 10**12):
        mid = (lo + hi)/2
        if Q(kappa(mid, mid/(1-beta)+GRID)['kappa']) > target:
            hi = mid
        else:
            lo = mid
    star = hi
    # Complex side, most favourable shape: delete rank-1 children until b >= s*.
    need = None
    a, z = 2, local[1]
    while a < z:
        k = (a + z)//2
        L = Counter(local)
        L[1] -= k
        if below_root(glob(+L), M_C, W, star, False):
            z = k
        else:
            a = k + 1
    L = Counter(local)
    L[1] -= a
    require(below_root(glob(+L), M_C, W, star, False), 'complex s* witness')
    L[1] += 1
    require(not below_root(glob(+L), M_C, W, star, False), 'complex s* minimality')
    need = a
    out['kappa_above_one_percent'] = dict(
        min_common_saving_s_star=str(star), s_star_decimal=dec(star),
        complex_rank1_units_per_call_needed=need,
        complex_deficit_needed=M_C*W - profile_mass(glob(+Counter({**local, 1: local[1]-need}))),
        bit_with_all_nine_copies_deleted=bitrows['0']['bit_c'],
        bit_copy_deletion_reaches_s_star=Q(bitrows['0']['bit_c']) >= star,
        note=('Complex: rank-1 deletion is the most favourable unit removal in this model. '
              'Bit: deleting every PR589 COPY child alone stays below s*, so its other children or '
              'template parameters must change as well.'))
    # 5. Same headroom for the T37 record (PR942) selected on main during this work.
    # It reuses the identical U8 local word in 333 calls with the same PR589 bit supplier.
    t37p = ROOT/'research/complex-t37-owners/CLAIM.json'
    require(hashlib.sha256(t37p.read_bytes()).hexdigest() ==
            'a383da34ee22da831fa436ad3483568ae1fcd62cd76581f2c2dd2b6473b346fb', 'T37 claim pin')
    t37 = json.loads(t37p.read_text())
    calls37, W37 = t37['calls'], t37['live']
    idle37 = Counter({int(r): n for r, n in t37['idle'].items()})
    prof37 = Counter({int(r): n for r, n in t37['profile'].items()})
    require(prof37 == Counter({r: calls37*n for r, n in local.items()}) + idle37, 'T37 = 333 x U8 + idle')
    g37 = lambda L: Counter({r: calls37*n for r, n in L.items() if n}) + idle37
    b37, ok = root(g37(local), M_C, W37)
    require(ok and dec(b37) == t37['complex_lower'] and Q(c) == Q(t37['bit_lower']), 'reproduce T37 endpoints')
    require(kappa(c, b37)['kappa_decimal'] == t37['kappa_decimal'], 'reproduce T37 kappa')
    rows37 = []
    for k in range(1, 9):
        L = Counter(local)
        L[1] -= k
        b, ok = root(g37(L), M_C, W37)
        rows37.append(dict(rank1_units_per_call=k, deficit=M_C*W37-profile_mass(g37(L)), complex_b=dec(b),
                           binding='bit' if b >= threshold_b else 'complex',
                           kappa=kappa(c, min(b, threshold_b+GRID))['kappa_decimal']))
        if b >= threshold_b:
            break
    out['selected_t37_headroom'] = dict(kappa=t37['kappa_decimal'], complex_b=dec(b37), deficit=t37['deficit'],
                                        calls=calls37, live=W37, rows=rows37,
                                        note='Same U8 word and PR589 bit supplier, so the class partition and the bit cap are unchanged.')
    out['scope'] = ('Exact model prices: listed children deleted/lowered with every other child, live stock, '
                    'idle hosting and the 47 outer inequalities unchanged. Not constructions, not lower bounds; '
                    'any real interface must also pay its parent-side work, which this model sets to zero.')
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == '__main__':
    require(__debug__, 'run without -O: the retained outer engine uses assertions')
    main()
