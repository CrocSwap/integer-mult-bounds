#!/usr/bin/env python3
"""Fixed prime, seven completed ordinary levels and eta = 10^-24 on PR254's cohort-kernel construction.

Run from the repository root with assertions enabled:

    python3 -B research/fixed-prime-pr254/verify.py                      # pinned PR254 receipts
    python3 -B research/fixed-prime-pr254/verify.py --parent-output DIR  # receipts of a fresh PR254 run
    python3 -B research/fixed-prime-pr254/verify.py --write               # regenerate certificate.json

The script first reproduces PR254's published coarse saving and kappa from its own receipts with PR254's
parameters (rare density 10^-16, three ordinary levels, eta = 10^-12, 10^-17 grid). It then changes only
the fixed parameters of gabriele-nespoli's PR235: prime q = 2^127-1 fixed before every width, proved rare
density 2m^3/q with the full 32m^2 fallback still paid, seven acyclic completed ordinary levels, and
eta = 10^-24 (as in PR243 and the reviewed main result) on a 10^-24 kappa grid.
Standard library only. Apache-2.0. Prepared with Claude (Anthropic) assistance.
"""
import argparse, hashlib, importlib.util, json, sys
from fractions import Fraction as Q
from pathlib import Path
if not __debug__: raise SystemExit('assertions required')
sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
PARENT = ROOT / 'research/cohort-kernel-entrances132'
PRIME = 2 ** 127 - 1; DEPTH = 7; GRID = 10 ** 24; COARSE_GRID = 10 ** 27
PINS = {'vendor/moment.py': '9d465c716c6b910ff66e1453e3bf0057608a787b5f5361be93781f42cb3370f7',
        'vendor/base_two_moment.py': 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098',
        'vendor/outer.py': 'c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c'}
PARENT_RECEIPTS = {'COHORT-EXACT-PRICE.json': 'a886287a646e2fc3', 'COHORT-FINITE-INVOICE.json': 'de439b7448c11b4a'}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def require(ok, msg):
    if not ok: raise AssertionError(msg)
def cutoff_log2(delta, C):
    # PR234 finite_check.cutoff_log2, unchanged.
    ceilq = lambda x: -((-x.numerator) // x.denominator)
    assert 0 < delta <= 1 and isinstance(C, int) and C >= 1
    return max(1, ceilq(36 / delta ** 2), ceilq(2 * (4 + (C - 1).bit_length()) / delta))

def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--parent-output', type=Path); ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    for rel, digest in PINS.items():
        require(sha(HERE / rel) == digest, 'vendored file changed: ' + rel)
    public = load('fp254_moment', HERE / 'vendor/moment.py'); independent = load('fp254_independent', HERE / 'vendor/base_two_moment.py')
    outer = load('fp254_outer', HERE / 'vendor/outer.py')
    if args.parent_output:
        price_path = args.parent_output / 'lead/COHORT-EXACT-PRICE.json'; inv_path = args.parent_output / 'temporal/COHORT-FINITE-INVOICE.json'
        cert = json.loads((args.parent_output / 'CERTIFICATE.json').read_text())
        require(cert['status'] == 'PASS_ALL_SEVEN_NATIVE_CHECKERS_AND_PINNED_RECEIPTS', 'parent run did not pass')
    else:
        price_path = PARENT / 'expected/COHORT-EXACT-PRICE.json'; inv_path = PARENT / 'expected/COHORT-FINITE-INVOICE.json'
    for p in (price_path, inv_path): require(sha(p).startswith(PARENT_RECEIPTS[p.name]), 'PR254 receipt differs: ' + p.name)
    price = json.loads(price_path.read_text())['cohort_candidate']; inv = json.loads(inv_path.read_text())
    cx = json.loads((HERE / 'vendor/complex-and-bridge.json').read_text())
    m = 120; W = price['stock']; H = {int(r): n for r, n in price['histogram'].items()}
    E = sum(H.values()); mass = sum(r * n for r, n in H.items())
    require((E, mass) == (price['calls'], price['rank_mass']) and m * W - mass == price['deficit'] == 35200 and max(H) < m // 2, 'profile')
    require(int(inv['full_counted_primitive_coefficient']) < 2 ** 80 < PRIME and int(inv['payload_bits']) < 127, 'finite bill must stay below the fixed prime')
    residues = [4]
    for _ in range(125): residues.append((residues[-1] ** 2 - 2) % PRIME)
    require(residues[-1] == 0 and all(127 % d for d in range(2, 12)), 'Lucas-Lehmer certificate')
    b = Q(cx['complex_coarse']); cp = cx['complex_profile']
    require(public.moment({int(r): n for r, n in cp['histogram'].items()}, cp['m'], cp['W'], b, False)[1] < 1, 'complex moment')
    bridge = cx['finite_bridge']; bridge['rows']['degree_gap'] = Q(bridge['rows']['degree_gap'])
    def paid(a, density):
        lo, hi = public.moment(H, m, W, a, False); l, u = public.logarithm(Q(m)); e, f = public.exponential(a * l, a * u)
        bill = density * Q(32 * m * E, W); return public.floor(lo + bill * e), public.ceil(hi + bill * f)
    def assemble(a, eta, grid, beta=Q(1, 10 ** 9)):
        require(a < (1 - beta) * b, 'complex cap active')
        z = a * (1 - 2 * eta); bound = (1 - eta) * z / (1 + z); t = bound * grid; k = Q((t.numerator - 1) // t.denominator, grid)
        r = outer.assembly(a, b, bridge, k, eta=eta, beta=beta)
        require(len(r['strict_constraints']) == 47 and len(r['margins']) == 7 and all(x > 0 for x in r['strict_constraints'].values()), 'outer 47')
        try: outer.assembly(a, b, bridge, k + Q(1, grid), eta=eta, beta=beta)
        except AssertionError: pass
        else: raise AssertionError('adjacent kappa grid point admitted')
        return k, bound, r
    def chain(c, depth):
        ch = [Q(384599, 10 ** 10)]
        for _ in range(depth): ch.append((1 - c) * c + c * ch[-1])
        return ch
    # 1. PR254 exactly, with its own parameters.
    c_old = Q(price['coarse'])
    require(paid(c_old, Q(1, 10 ** 16))[1] < 1 < paid(c_old + Q(1, 10 ** 17), Q(1, 10 ** 16))[0], 'PR254 coarse saving not reproduced')
    k_old, bound_old, _ = assemble(chain(c_old, 3)[-1], Q(1, 10 ** 12), 10 ** 17)
    require(k_old == Q(price['kappa']) == Q(71046520063283, 10 ** 17), 'PR254 kappa not reproduced')
    # 2. The fixed-prime refinement.
    rho = Q(2 * m ** 3, PRIME); require(0 < rho < Q(1, 10 ** 16), 'density')
    lo = int(c_old * COARSE_GRID); hi = lo + COARSE_GRID // 10 ** 8
    require(paid(Q(lo, COARSE_GRID), rho)[1] < 1 < paid(Q(hi, COARSE_GRID), rho)[0], 'coarse bracket')
    while hi - lo > 1:
        mid = (lo + hi) // 2; l, u = paid(Q(mid, COARSE_GRID), rho)
        if u < 1: lo = mid
        elif l > 1: hi = mid
        else: raise ValueError('inconclusive enclosure')
    c = Q(lo, COARSE_GRID); excluded = Q(hi, COARSE_GRID)
    pa, pe = paid(c, rho), paid(excluded, rho)
    il, iu = independent.moment(m, W, list(H.items()), c); fl, fu = independent.moment(m, W, [(1, 32 * m * m * E)], c)
    jl, ju = independent.moment(m, W, list(H.items()), excluded); gl, gu = independent.moment(m, W, [(1, 32 * m * m * E)], excluded)
    require(pa[1] < 1 < pe[0] and iu + rho * fu < 1 < jl + rho * gl, 'two independent paid-moment brackets')
    require(paid(c, Q(1, 10 ** 16))[0] > 1, 'the gain must rely on the proved rare density')
    ch = chain(c, DEPTH); steps = []
    for j in range(1, DEPTH + 1):
        a, old = ch[j], ch[j - 1]
        require(a == c - c ** j * (c - ch[0]) and old < a < c < 1 - a, 'acyclic completed level')
        gaps = dict(atom=c - a, borrowing=1 - a - c, remainder=1 - a - c * (1 - old), stock=1 - c)
        delta = min(gaps.values()); L = cutoff_log2(delta, 1); require(delta > 0 and L * delta ** 2 >= 36, 'cutoff gap')
        steps.append(dict(level=j, saving=str(a), minimum_gap=str(delta), cutoff_log2_at_C1=L))
    delta_linear = 1 - Q(mass, m * W) - rho * Q(32 * m * E, W); require(delta_linear > 0 and 1 - pa[1] > 0, 'recurrence gaps')
    k, bound, asm = assemble(ch[-1], Q(1, 10 ** 24), GRID)
    require(k > bound_old, 'no improvement over the unrounded PR254 bound')
    record = dict(schema='fixed-prime-pr254/1', parent='PR254 cohort-kernel-entrances132 at 9ce32ef', parent_kappa=str(k_old),
                  parent_unrounded_bound=str(bound_old), prime='2^127-1', lucas_lehmer_updates=125, rare_density=str(rho),
                  coarse=str(c), excluded_coarse=str(excluded), ordinary_levels=DEPTH, ordinary_chain=[str(x) for x in ch], steps=steps,
                  eta='1/10^24', beta='1/10^9', kappa_grid='10^-24', complex_saving=str(b), delta_linear=str(delta_linear),
                  delta_tau_lower=str(1 - pa[1]), kappa=str(k), kappa_decimal=public.decimal(k), gain_over_parent=str(k - k_old),
                  finite_bill_coefficient=str(inv['full_counted_primitive_coefficient']), payload_bits=inv['payload_bits'])
    path = HERE / 'certificate.json'
    if args.write: path.write_text(json.dumps(record, indent=1) + '\n')
    else: require(json.loads(path.read_text()) == record, 'certificate.json differs from the recomputation')
    print('PASS PR254 reproduced (kappa ' + str(k_old) + '); fixed-prime seven-level kappa = ' + str(k) + ' = ' + public.decimal(k))

if __name__ == '__main__': main()
