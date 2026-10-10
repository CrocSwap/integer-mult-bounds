#!/usr/bin/env python3
"""Fixed prime, seven finite levels and the assembly backoff eta = 10^-24 on PR244's retimed source527 five-stage banks.

Usage (repository root, Python 3.11+, assertions enabled, sympy==1.14.0):
    python3 -B research/five-stage-source527-retimed-fixed-prime/verify.py [--output NEW_DIR] [--dump PATH] [--write]
    python3 -B research/five-stage-source527-retimed-fixed-prime/verify.py --pr244-output DONE_DIR   # reuse a finished PR244 run

By default this first runs PR244's own immutable verifier (research/five-stage-source527-banks, same checkout) into a
new output directory: its package integrity check and all eight mandatory stages (raw, bit, scalar, primes, banks,
complex, math, finite), with PR244's published kappa required. Then, on PR244's verified banked profile unchanged:

* the fixed prime q = 2^127 - 1 (Lucas-Lehmer here; Prime.lean kernel-checks it), whose proved rare-class density
  2m^3/q replaces the 10^-16 envelope while every rare class still pays the full 32m^2 rank-one fallback;
* the coarse saving on the 10^-27 grid, bracketed by PR244's public engine (PR234's) and the independent atanh engine;
* seven finite ordinary levels a_j = (1-c)c + c a_(j-1) from the retained completed saving 384599/10^10, each with
  PR244's cutoff rule at its fully charged q-power coefficient;
* PR244's unchanged outer-47 assembly with eta = 10^-24 (PR244 uses 10^-12) and beta = 10^-9, on the 10^-24 kappa
  grid; the adjacent grid point is rejected;
* PR244's fully paid q-power coefficient (literal 60-replica stock and bank selectors), still below 2^80 < q.

The fixed-prime argument and the seven levels follow PR235 (Gabriele Nespoli, Apache-2.0, OpenAI Codex), applied here
to PR244's word (eumemic's retimed PR210 construction). Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse, importlib.util, json, subprocess, sys, tempfile
if sys.flags.optimize: raise SystemExit('Assertions required')
sys.set_int_max_str_digits(0); sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'research/five-stage-source527-banks'
DEPTH = 7; GRID = 10 ** 24; COARSE_GRID = 10 ** 27; PRIME = 2 ** 127 - 1
ETA = Q(1, 10 ** 24); PARENT_ETA = Q(1, 10 ** 12); BETA = Q(1, 10 ** 9)
PARENT_KAPPA = Q(710346589668175, 10 ** 18)
PARENT_STATUS = 'PASS_IMMUTABLE_PARITY_RETIMED_SOURCE527_FIVE_STAGE_BANKED_CONSTRUCTION'
PARENT_STAGES = ['banks', 'bit', 'complex', 'finite', 'math', 'primes', 'raw', 'scalar']


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


def read(out, name):
    return json.loads((out / name).read_text())


def arithmetic(out):
    public = load('pr244_moment', PARENT / 'moment.py')
    outer = load('pr244_outer47', PARENT / 'outer.py')
    cutoffs = load('pr244_finite_cutoff', PARENT / 'finite_check.py')
    independent = load('independent_atanh_moment', PARENT / 'base_two_moment.py')
    for text in [(PARENT / 'proof/three-stage-cover-bit.tex').read_text(), (PARENT / 'proof/INTEGRATED_PROOF.md').read_text()]:
        require('2m^3/q' in text and '32m^2' in text, 'Detached rare-density bound')
    report = read(out, 'verification.json')
    require(report['status'] == PARENT_STATUS and Q(report['kappa']) == PARENT_KAPPA and sorted(report['fresh_stages']) == PARENT_STAGES
            and report['inputs_unchanged'] is True, 'PR244 verifier did not pass')
    require(report['manifest_sha256'] == sha256((PARENT / 'MANIFEST.json').read_bytes()).hexdigest(), 'PR244 output from another package')
    math = read(out, 'math.json'); require(math['status'] == 'PASS_BANKED_FIVE_STAGE527_EXACT_MOMENTS_AND_OUTER47', 'PR244 math stage')
    ar = math['mathematics']; finite = read(out, 'finite.json'); primes = read(out, 'primes.json'); banks = read(out, 'banks.json')['banks']
    parent_cert = read(out, 'certificate.json')
    require(finite['status'] == 'PASS_LITERAL_PARITY_FUSED_BANKED_FIVE_STAGE527_FINITE_BILL' and Q(parent_cert['kappa']) == Q(ar['kappa']) == PARENT_KAPPA,
            'PR244 finite stage or certificate')
    prime = prime_certificate()
    bp = ar['bit_profile']; m = bp['m']; W = bp['W']
    H = {int(r): n for r, n in bp['histogram'].items()}
    E = sum(H.values()); mass = sum(r * n for r, n in H.items())
    require(m == 120 and m * W - mass == bp['deficit'] == 52800 and max(H) == bp['maxchild'] < m // 2
            and all(0 < r < m and n > 0 for r, n in H.items()) and E == bp['calls'] and mass == bp['rank_mass'], 'Changed banked profile')
    require(bp['literal_stock'] == 5 * W == banks['literal_stock'] and bp['physical_replicas'] == banks['physical_replicas'] == 60
            and bp['literal_children'] == 5 * E and bp['literal_rank_mass'] == 5 * mass, 'Literal stock is not five normalized copies')
    require(primes['all_remaining_factors_below_2_power_80'] is True and all(1 < p < 2 ** 80 for p in primes['prime_factors']),
            'Unverified excluded primes')
    require(max(banks['max_factor_numerator'], banks['max_denominator']) < 2 ** 80 and 1 < banks['normalizer_factor_bound'] < 2 ** 80
            and 0 < banks['conservative_extra_selector_calls'] < 2 ** 40, 'Ineligible bank charts')
    inv = finite['paid_inventory']
    require(inv['fallback_per_child'] == 32 * m * m and inv['positive_rank_children'] == 5 * E and inv['literal_stock'] == 5 * W,
            'Fallback count changed')
    coefficient = finite['q_power_bound']['coefficient']
    require(isinstance(coefficient, int) and 0 < coefficient < 2 ** 80 < PRIME, 'Invalid banked q-power overcharge')
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
    c0 = Q(ar['bit_coarse']); require(c0.denominator <= 10 ** 18, 'Parent coarse grid')
    require(public.moment(H, m, W, c0, True) == tuple(map(Q, ar['bit_moment_interval'])), 'Parent moment interval')
    require(paid(c0, Q(1, 10 ** 16))[1] < 1 and paid(c0)[1] < 1, 'Parent coarse point not accepted')
    lo = int(c0 * COARSE_GRID); hi = lo + COARSE_GRID // 10 ** 8
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
    base = Q(384599, 10 ** 10); b = Q(ar['complex_coarse'])
    parent_chain = [Q(x) for x in ar['ordinary_bootstrap_chain']]
    require(parent_chain[0] == base and len(parent_chain) == 4, 'Changed completed base supplier')
    for j in range(1, 4): require(parent_chain[j] == (1 - c0) * c0 + c0 * parent_chain[j - 1], 'Parent chain')
    require(Q(ar['complex_moment_interval'][1]) < 1 and b == Q(747454944651775, 10 ** 18), 'Complex moment')
    bridge = dict(proof='PROOF.md', representation='Exact powers with source-bound finite overcharges',
                  semantic=dict(G=dict(base=2, exponent=30000), E=dict(base=2, exponent=100000),
                                B_upper=dict(base=2, exponent=100001), C0=dict(base=2, exponent=210000), C1=1,
                                strict_literal_gap=1, induction_gap_lower=1),
                  rows=dict(coefficient=20161, degree=10 ** 6, suffix_slope=4 * 10 ** 6,
                            degree_gap=Q(10 ** 6) - Q(51 * 20161, 25)))
    require(serial(bridge) == ar['finite_bridge'], 'Changed finite bridge')
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
        delta = min(gaps.values()); L = cutoffs.cutoff_log2(delta, coefficient)
        require(L * delta ** 2 >= 36 and L * delta >= 2 * (4 + (coefficient - 1).bit_length()), 'Cutoff arithmetic')
        steps.append(dict(level=j, ordinary_predecessor=j - 1, saving=a, gaps=gaps, minimum_gap=delta,
                          cutoff_log2_at_charged_coefficient=L))
        chain.append(a)
    result = assemble(chain[-1])
    require(assemble(parent_chain[-1], 10 ** 18, PARENT_ETA)['kappa'] == PARENT_KAPPA, 'Published PR244 comparator')
    previous = assemble(parent_chain[-1])
    require(result['kappa'] > PARENT_KAPPA and result['kappa'] > previous['kappa'], 'No improvement over PR244')
    parent_eta_seven = assemble(chain[-1], GRID, PARENT_ETA)
    require(result['kappa'] > parent_eta_seven['kappa'], 'Smaller eta does not improve the grid point')
    sixth = assemble(chain[6]); third = assemble(chain[3]); fourth = assemble(chain[4])
    delta1 = 1 - Q(mass, m * W) - rho * Q(32 * m * E, W)
    require(delta1 > 0 and 1 - pa[1] > 0, 'Recurrence contraction gap')
    controls = []
    for name, j, pred, a in [('cyclic supplier', DEPTH, DEPTH, chain[-1]), ('unattained coarse ordinary leaf', DEPTH, DEPTH - 1, c)]:
        try: validate_step(j, pred, c, chain[-2], a)
        except ValueError: controls.append(name)
        else: raise ValueError('Invalid supplier admitted')
    corrupted = prime['residues'][:]; corrupted[37] += 1
    require(any(corrupted[i + 1] != (corrupted[i] ** 2 - 2) % PRIME for i in range(125)), 'Corrupt prime residue accepted')
    controls += ['corrupt Lucas-Lehmer residue', 'old-density paid moment at new coarse point', 'adjacent coarse and kappa grid points']
    return serial(dict(schema='five-stage-source527-retimed-fixed-prime/1', scope='Conditional on the unchanged PR234/PR210/PR244 all-size and symbolic interfaces',
        prime=prime, rare_density=rho, depth=DEPTH, coarse_grid=COARSE_GRID, kappa_grid=GRID,
        banked_profile=bp, parent_coarse=c0, coarse=c, excluded_coarse=excluded, public_accepted=pa, public_excluded=pe,
        independent_accepted=ia, independent_excluded=ie, fallback_histogram=fallback,
        delta_linear=delta1, delta_tau_lower=1 - pa[1], ordinary_chain=chain, steps=steps,
        eta=ETA, parent_eta=PARENT_ETA, beta=BETA, complex_saving=b, kappa=result['kappa'],
        kappa_decimal=public.decimal(result['kappa']), pr244_kappa=PARENT_KAPPA, gain_over_pr244=result['kappa'] - PARENT_KAPPA,
        relative_gain_over_pr244=result['kappa'] / PARENT_KAPPA - 1,
        parent_eta_seven_level_kappa=parent_eta_seven['kappa'], three_level_kappa=third['kappa'],
        four_level_kappa=fourth['kappa'], six_level_kappa=sixth['kappa'],
        assembly=result['assembly'], minimum_margin=result['bound'],
        q_power_bound=dict(coefficient=coefficient, bound='coefficient < 2^80 < q', source='PR244 finite stage, literal 60-replica stock',
                           selector_calls=banks['conservative_extra_selector_calls'], normalizer_factor_bound=banks['normalizer_factor_bound']),
        pr244_manifest_sha256=report['manifest_sha256'], controls=controls))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, help='New directory for the fresh PR244 verifier outputs (default: a new temporary directory)')
    ap.add_argument('--pr244-output', type=Path, help='Reuse a finished PR244 verifier output directory instead of rerunning it')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--dump', type=Path, help='Also write the complete recomputed record here')
    a = ap.parse_args()
    import sympy
    require(sys.version_info >= (3, 11) and sympy.__version__ == '1.14.0', 'Python 3.11+ and sympy 1.14.0 required')
    if a.pr244_output:
        out = a.pr244_output.resolve(); print('Reusing PR244 verifier output ' + str(out), flush=True)
    else:
        out = a.output.resolve() if a.output else Path(tempfile.mkdtemp(prefix='pr244-source527-')) / 'out'
        print('Running PR244 verifier into ' + str(out), flush=True)
        subprocess.run([sys.executable, '-B', str(PARENT / 'verify.py'), '--output', str(out)], cwd=ROOT, check=True)
    result = arithmetic(out)
    result['pr244_certificate_sha256'] = sha256((out / 'certificate.json').read_bytes()).hexdigest()
    full = json.dumps(result, sort_keys=True, separators=(',', ':')).encode()
    if a.dump: a.dump.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    keys = ['schema', 'kappa', 'kappa_decimal', 'pr244_kappa', 'gain_over_pr244', 'relative_gain_over_pr244', 'parent_coarse', 'coarse',
            'excluded_coarse', 'rare_density', 'depth', 'eta', 'parent_eta', 'beta', 'complex_saving', 'coarse_grid',
            'kappa_grid', 'parent_eta_seven_level_kappa', 'three_level_kappa', 'four_level_kappa', 'six_level_kappa', 'controls',
            'pr244_certificate_sha256', 'pr244_manifest_sha256']
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
