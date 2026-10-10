#!/usr/bin/env python3
"""Fixed prime, seven finite levels and the assembly backoff eta = 10^-24 on PR240's banked five-stage word.

Usage (repository root, assertions enabled, sympy==1.14.0):
    python3 -B research/five-stage-493-fixed-prime/verify.py --pr210-root <PR210 @ 1331149> --pr234-root <PR234 @ af3fe33> [--full] [--write]

First runs PR240's own verifier (research/five-stage-banks-493, same checkout): the 493-source helper on every
column, telescope, five-stage lowering, geometry, primes, finite bill, 231 charts, 176,915 banks and the coloring,
and requires its stored certificate to be reproduced. Then, on PR240's banked profile unchanged:

* the fixed prime q = 2^127 - 1 (Lucas-Lehmer here; Prime.lean kernel-checks it), whose proved rare-class density
  2m^3/q replaces the 10^-16 envelope while every rare class still pays the full 32m^2 rank-one fallback;
* the coarse saving on the 10^-27 grid, bracketed by PR234's public engine and an independent atanh engine;
* seven finite ordinary levels a_j = (1-c)c + c a_(j-1) from the retained completed saving 384599/10^10;
* PR234's unchanged outer-47 assembly with eta = 10^-24 (PR234/240 used 10^-12; all 47 strict inequalities and
  7 margins are recomputed) and beta = 10^-9, on the 10^-24 kappa grid; the adjacent grid point is rejected;
* the fully paid prime-dependent constant, with PR240's fresh finite-bill values.

The fixed-prime argument and the seven levels follow PR235 (Gabriele Nespoli, Apache-2.0, OpenAI Codex), applied here
to PR240's word. Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse, importlib.util, json, subprocess, sys
if sys.flags.optimize: raise SystemExit('Assertions required')
sys.set_int_max_str_digits(0); sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR240 = ROOT / 'research/five-stage-banks-493'
V8 = 'research/five-stage-source-bound-v8'
DEPTH = 7; GRID = 10 ** 24; COARSE_GRID = 10 ** 27; PRIME = 2 ** 127 - 1
ETA = Q(1, 10 ** 24); PARENT_ETA = Q(1, 10 ** 12); BETA = Q(1, 10 ** 9)
PR240_KAPPA = Q(28376976266399, 40000000000000000)


def require(ok, message):
    if not ok: raise ValueError(message)


def serial(x):
    if isinstance(x, Q): return str(x)
    if isinstance(x, dict): return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)): return [serial(v) for v in x]
    return x


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def point(x, grid=GRID):
    z = x * grid; return Q((z.numerator - 1) // z.denominator, grid)


def prime_certificate():
    require(all(127 % d for d in range(2, 12)), 'Composite Mersenne exponent')
    values = [4]
    for _ in range(125): values.append((values[-1] ** 2 - 2) % PRIME)
    require(values[-1] == 0 and PRIME > 2 ** 80 and PRIME % 2 == 1, 'Ineligible prime')
    return dict(q=PRIME, p=127, iterations=125, residues=values,
                criterion='Lucas-Lehmer sufficiency, independently kernel-checked in Prime.lean', fixed_before_all_widths=True)


def validate_step(j, predecessor, c, old, a):
    require(1 <= j <= DEPTH and predecessor == j - 1, 'Cyclic completed supplier')
    require(a == (1 - c) * c + c * old and old < a < c < 1 - a, 'Unpaid finite toll or unattained coarse leaf')
    gaps = dict(atom=c - a, borrowing=1 - a - c, remainder=1 - a - c * (1 - old), stock=1 - c)
    require(min(gaps.values()) > 0, 'Nonpositive cutoff gap')
    return gaps


def arithmetic(P234, parent):
    public = load('pr234_moment', P234 / V8 / 'code/five_stage_bit_cost_20261009.py')
    outer = load('pr234_outer47', P234 / V8 / 'code/paired_cube_assembly.py')
    cutoffs = load('pr234_finite_cutoff', P234 / V8 / 'finite_check.py')
    independent = load('independent_atanh_moment', HERE / 'base_two_moment.py')
    proof = (P234 / V8 / 'proof/three-stage-cover-bit.tex').read_text()
    require('bad fraction at most $2m^3/q<10^{-16}$' in proof, 'Detached rare-density bound')
    ar = parent['arithmetic']; physical = parent['physical']; finite = parent['checks']['finite']
    prime = prime_certificate()
    bp = ar['bit_profile']; m = bp['m']; W = bp['W']
    H = {int(r): n for r, n in bp['histogram'].items()}
    E = sum(H.values()); mass = sum(r * n for r, n in H.items())
    require(m == 120 and m * W - mass == bp['deficit'] == 52800 and max(H) < m // 2 and all(0 < r < m and n > 0 for r, n in H.items()),
            'Changed banked profile')
    require(parent['checks']['primes']['prime_factors'] == [2, 3, 5, 7] and parent['checks']['primes']['all_remaining_factors_below_2_power_80'],
            'Unverified excluded primes')
    require(max(physical['max_num'], physical['max_den']) < 2 ** 80 and physical['conservative_selector_calls'] < 2 ** 40, 'Ineligible bank charts')
    require(finite['fallback_children'] == 32 * m * m, 'Fallback count changed')
    rho = Q(2 * m ** 3, PRIME); require(0 < rho < Q(1, 10 ** 16), 'Fallback omitted or no density improvement')
    fallback = [(1, 32 * m * m * E)]
    def paid(a, density=rho):
        lo, hi = public.moment(H, m, W, a, False)
        l, u = public.logarithm(Q(m)); e, f = public.exponential(a * l, a * u)
        bill = density * Q(32 * m * E, W)
        return public.floor(lo + bill * e), public.ceil(hi + bill * f)
    def separate(a):
        lo, hi = independent.moment(m, W, list(H.items()), a)
        fl, fu = independent.moment(m, W, fallback, a)
        return lo + rho * fl, hi + rho * fu
    c0 = Q(ar['bit_coarse_saving']); lo = int(c0 * COARSE_GRID); hi = lo + COARSE_GRID // 10 ** 8
    require(paid(Q(lo, COARSE_GRID))[1] < 1 < paid(Q(hi, COARSE_GRID))[0], 'Coarse bracket')
    while hi - lo > 1:
        mid = (lo + hi) // 2; l, u = paid(Q(mid, COARSE_GRID))
        if u < 1: lo = mid
        elif l > 1: hi = mid
        else: raise ValueError('Inconclusive rational moment enclosure')
    c = Q(lo, COARSE_GRID); excluded = Q(hi, COARSE_GRID)
    pa, pe, ia, ie = paid(c), paid(excluded), separate(c), separate(excluded)
    require(pa[1] < 1 < pe[0] and ia[1] < 1 < ie[0], 'Independent paid moment bracket')
    require(paid(c, Q(1, 10 ** 16))[0] > 1, 'Improvement does not depend on the certified smaller density')
    base = Q(384599, 10 ** 10); b = Q(ar['complex_saving'])
    require(Q(ar['ordinary_chain'][0]) == base, 'Changed completed base supplier')
    require(Q(ar['complex_moment_interval'][1]) < 1, 'Complex moment')
    bridge = dict(proof='PROOF.md', representation='Exact powers with source-bound finite overcharges',
                  semantic=dict(G=dict(base=2, exponent=30000), E=dict(base=2, exponent=100000),
                                B_upper=dict(base=2, exponent=100001), C0=dict(base=2, exponent=210000), C1=1,
                                strict_literal_gap=1, induction_gap_lower=1),
                  rows=dict(coefficient=20161, degree=10 ** 6, suffix_slope=4 * 10 ** 6,
                            degree_gap=Q(10 ** 6) - Q(51 * 20161, 25)))
    def assemble(a, grid=GRID, eta=ETA):
        require(a < (1 - BETA) * b, 'Complex cap became active')
        z = a * (1 - 2 * eta); bound = (1 - eta) * z / (1 + z); k = point(bound, grid)
        result = outer.assembly(a, b, bridge, k, eta=eta, beta=BETA)
        require(len(result['strict_constraints']) == 47 and len(result['margins']) == 7, 'Incomplete outer assembly')
        require(all(v > 0 for v in result['strict_constraints'].values()) and all(v > k for v in result['margins'].values()), 'Non-strict outer inequalities')
        try: outer.assembly(a, b, bridge, k + Q(1, grid), eta=eta, beta=BETA)
        except AssertionError: pass
        else: raise ValueError('Adjacent kappa point admitted')
        return dict(kappa=k, bound=bound, assembly=result)
    chain = [base]; steps = []
    for j in range(1, DEPTH + 1):
        old_a = chain[-1]; a = (1 - c) * c + c * old_a; gaps = validate_step(j, j - 1, c, old_a, a)
        require(a == c - c ** j * (c - base), 'Recurrence mismatch')
        delta = min(gaps.values()); L = cutoffs.cutoff_log2(delta, 1)
        require(L * delta ** 2 >= 36 and L * delta >= 8, 'Cutoff arithmetic')
        steps.append(dict(level=j, ordinary_predecessor=j - 1, saving=a, gaps=gaps, minimum_gap=delta, cutoff_log2_at_C_equals_1=L))
        chain.append(a)
    result = assemble(chain[-1])
    require(assemble(Q(ar['ordinary_chain'][-1]), 10 ** 18, PARENT_ETA)['kappa'] == Q(ar['kappa']) == PR240_KAPPA, 'Published PR240 comparator')
    previous = assemble(Q(ar['ordinary_chain'][-1]))
    require(result['kappa'] > PR240_KAPPA and result['kappa'] > previous['kappa'], 'No improvement over PR240')
    parent_eta_seven = assemble(chain[-1], GRID, PARENT_ETA)
    require(result['kappa'] > parent_eta_seven['kappa'], 'Smaller eta does not improve the grid point')
    sixth = assemble(chain[6]); third = assemble(chain[3])
    delta1 = 1 - Q(mass, m * W) - rho * Q(32 * m * E, W)
    require(delta1 > 0 and 1 - pa[1] > 0, 'Recurrence contraction gap')
    base_coefficient = finite['q_power_coefficient']; J = finite['route_and_final_exchange_families']
    d = m * m; N = 2 * m; K = physical['conservative_selector_calls']
    per_selector = 16 * (d + 1) ** 2 + (W + 12 * 24) + 128 * N ** 3 + (8 * m * m + 8) + 1
    enlarged_role_charge = 12 * J * (W + 12 * 24)
    coefficient = 12 * base_coefficient + enlarged_role_charge + K * per_selector
    require(coefficient < 2 ** 80 < PRIME, 'Invalid banked q-power overcharge')
    controls = []
    for name, j, pred, a in [('cyclic supplier', DEPTH, DEPTH, chain[-1]), ('unattained coarse ordinary leaf', DEPTH, DEPTH - 1, c)]:
        try: validate_step(j, pred, c, chain[-2], a)
        except ValueError: controls.append(name)
        else: raise ValueError('Invalid supplier admitted')
    corrupted = prime['residues'][:]; corrupted[37] += 1
    require(any(corrupted[i + 1] != (corrupted[i] ** 2 - 2) % PRIME for i in range(125)), 'Corrupt prime residue accepted')
    controls += ['corrupt Lucas-Lehmer residue', 'old-density paid moment at new coarse point', 'adjacent coarse and kappa grid points']
    return serial(dict(schema='five-stage-493-fixed-prime/1', scope='Conditional on the unchanged PR234/PR240 all-size and symbolic interfaces',
        prime=prime, rare_density=rho, depth=DEPTH, coarse_grid=COARSE_GRID, kappa_grid=GRID,
        banked_profile=bp, coarse=c, excluded_coarse=excluded, public_accepted=pa, public_excluded=pe,
        independent_accepted=ia, independent_excluded=ie, fallback_histogram=fallback,
        delta_linear=delta1, delta_tau_lower=1 - pa[1], ordinary_chain=chain, steps=steps,
        eta=ETA, parent_eta=PARENT_ETA, beta=BETA, complex_saving=b, kappa=result['kappa'],
        kappa_decimal=public.decimal(result['kappa']), pr240_kappa=PR240_KAPPA, gain_over_pr240=result['kappa'] - PR240_KAPPA,
        relative_gain_over_pr240=result['kappa'] / PR240_KAPPA - 1,
        parent_eta_seven_level_kappa=parent_eta_seven['kappa'], three_level_kappa=third['kappa'], six_level_kappa=sixth['kappa'],
        assembly=result['assembly'], minimum_margin=result['bound'],
        q_power_bound=dict(coefficient=coefficient, low_matrix_power=14400, strict_upper='q^14401', original_copies=12,
                           original_coefficient=base_coefficient, enlarged_role_charge=enlarged_role_charge,
                           per_selector_coefficient=per_selector, route_families=J, selector_calls=K),
        controls=controls))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pr210-root', type=Path, required=True)
    ap.add_argument('--pr234-root', type=Path, required=True)
    ap.add_argument('--full', action='store_true', help='Pass --full to PR240 (also runs PR234 fresh verifier)')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--dump', type=Path, help='Also write the complete recomputed record here')
    a = ap.parse_args()
    cmd = [sys.executable, '-B', str(PR240 / 'verify.py'), '--pr210-root', str(a.pr210_root), '--pr234-root', str(a.pr234_root)]
    if a.full: cmd.append('--full')
    print('Running PR240 verifier', flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)
    parent = json.loads((PR240 / 'certificate.json').read_text())
    result = arithmetic(a.pr234_root.resolve(), parent)
    result['pr240_certificate_sha256'] = sha256((PR240 / 'certificate.json').read_bytes()).hexdigest()
    full = json.dumps(result, sort_keys=True, separators=(',', ':')).encode()
    if a.dump: a.dump.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    keys = ['schema', 'kappa', 'kappa_decimal', 'pr240_kappa', 'gain_over_pr240', 'relative_gain_over_pr240', 'coarse',
            'excluded_coarse', 'rare_density', 'depth', 'eta', 'parent_eta', 'beta', 'complex_saving', 'coarse_grid',
            'kappa_grid', 'parent_eta_seven_level_kappa', 'three_level_kappa', 'six_level_kappa', 'controls',
            'pr240_certificate_sha256']
    summary = {k: result[k] for k in keys}
    summary['prime'] = {k: v for k, v in result['prime'].items() if k != 'residues'}
    summary['prime_residues_sha256'] = sha256(json.dumps(result['prime']['residues']).encode()).hexdigest()
    summary['q_power_bound'] = result['q_power_bound']
    summary['strict_constraints'] = len(result['assembly']['strict_constraints'])
    summary['minimum_strict_constraint'] = min(result['assembly']['strict_constraints'].values(), key=lambda x: Q(x))
    summary['full_record_sha256'] = sha256(full).hexdigest()
    summary['full_record_note'] = 'SHA-256 of the compact sorted JSON of the complete recomputed record; write it out with --dump PATH.'
    path = HERE / 'certificate.json'
    if a.write: path.write_text(json.dumps(summary, sort_keys=True, indent=2) + '\n')
    else: require(summary == json.loads(path.read_text()), 'Certificate mismatch')
    print('PASS kappa=' + result['kappa'] + ' = ' + result['kappa_decimal'], flush=True)


if __name__ == '__main__': main()
