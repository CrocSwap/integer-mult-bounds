#!/usr/bin/env python3
"""Exact endpoint refill conditional on the source PR4359 construction.

Apache-2.0. Substantial OpenAI assistance. The mixed inventory and elementary
function enclosure are zxv's PR4359; mixed-target flow is Jacob Alan Sussman's
Theorem 1G. Outer formulas retain the attribution in PR4359 outer_parameters.py.
This file checks arithmetic, not the native or all-size proof hypotheses.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PREFIX = Path('research/kappa-rebuild')
OLD_BASELINE = Q('0.001730970419199163702738')
KAPPA = Q('0.00230509')
TESTED = Q('0.00230509019')
ROOT_UPPER = Q('0.002306')


def need(value, message):
    if not value:
        raise AssertionError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def ceil(value):
    value = Q(value)
    return -((-value.numerator) // value.denominator)


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def family(kappa, tested):
    """One explicit slack family approaching the same source mixed root."""
    need(Q(0) < kappa < tested < ROOT_UPPER, 'Positive strictly ordered savings')
    d = (tested-kappa)/7
    return {'kappa': kappa, 'tested_saving': tested,
            'complex_uniform_saving': kappa+6*d,
            'b': kappa+5*d, 'a': kappa+4*d, 'q': kappa+3*d,
            'bit_saving': Q('0.0027'), 'epsilon': 1-d, 'beta': 1-3*d,
            'r0': d/10, 'stop': d, 'layout': d, 'd': d}


def ledger(p):
    """Recompute all 54 named PR4359 checks with freely supplied parameters."""
    kappa, b, a, q = (p[key] for key in ('kappa', 'b', 'a', 'q'))
    epsilon, beta, r0, stop, layout = (p[key] for key in
                                      ('epsilon', 'beta', 'r0', 'stop', 'layout'))
    sigma, tau = 1-b, 1-a
    internal = tau+(1-stop)*max(sigma-tau, Q(0))
    leaf = sigma+stop*(1-sigma)
    lam, c = 1-(q+a)/2, Q(3, 32)
    xi, key = epsilon*(1+q)-c+layout, beta+1-epsilon
    margins = {
        'main_transform': epsilon*q,
        'global_coordinate_router': a,
        'fused_gaussian': 1-epsilon+q*beta,
        'group_bit_router': 1-epsilon+a*beta,
        'group_scans': 1-epsilon+beta,
        'boundary_algebraic_matrix': c+xi-epsilon,
        'sparse_union_movement': xi+Q(1, 2)-epsilon,
        'polynomial_products': epsilon,
        'microbox_face_corrections': 1-(epsilon+beta+48-128+2),
    }
    checks = {
        'actual_bit_above_effective': p['bit_saving']-a,
        'complex_above_effective': b-a,
        'q_positive': q, 'complex_endpoint': b-q, 'q_below_effective': a-q,
        'stop_positive': stop, 'stop_below_one': 1-stop,
        'leaf_saving_above_effective': (1-stop)*b-a,
        'q_below_internal': 1-internal-q, 'q_below_leaf': 1-leaf-q,
        'lambda_above_tau': lam-tau, 'lambda_above_sigma': lam-sigma,
        'lambda_above_internal': lam-internal,
        'lambda_prime_above_lambda': 1-q-lam,
        'lambda_prime_above_leaf': 1-q-leaf,
        'epsilon_positive': epsilon, 'epsilon_below_one': 1-epsilon,
        'cap_above_band': xi-Q(1, 2), 'cap_below_cell': epsilon-xi,
        'group_positive': beta, 'group_below_dimension': epsilon-beta,
        'support_router_span': 1-beta,
        'group_gauge_power_slack': 1-(2*xi-2)-r0-beta,
        'actual_logarithmic_group_guard': 1-(2*xi-2)-beta,
        'global_gamma_power_slack': 1-epsilon-r0,
        'actual_logarithmic_gamma_guard': 1-epsilon,
        'alpha_logarithm_absorption': r0,
        'group_key_fits_record': 1-key,
        'membership_arithmetic_fits_record': 1-beta-2*(1-epsilon),
        'microbox_halo_volume': 128-48-beta,
        'positive_layout_slack': layout,
        'short_record_fallback': epsilon-a,
        'complex_below_one_over_32': Q(1, 32)-b,
        'strassen_integer_power_gap': Q(2**45-7**16),
        'theta_positive_polynomial_power': Q(2),
        'cap_below_phase_cell_power': 2-xi,
        'halo_covers_generic_inverse_radius': Q(48-43),
        'union_tag_work_per_visit_fits_record': 1-beta,
        'union_header_fits_record': 1-beta,
        'source_axis_superpolynomial': 1-epsilon,
        'gaussian_above_main': margins['fused_gaussian']-margins['main_transform'],
        'new_complex_uniform_saving_above_b': p['complex_uniform_saving']-b,
        'improvement_over_user_baseline': kappa-OLD_BASELINE,
        'new_semantic_guard_with_C1_one': 1-epsilon,
        'fine_prime_halo_umbrella': 10-(2*2+2+Q(1, 2)),
    }
    checks.update({name+'_above_kappa': value-kappa for name, value in margins.items()})
    # These are the additional functional conditions in the independent
    # PR4359 outer_transfer_audit.py, beyond the 54-row parameter ledger.
    functional = {
        'new_semantic_group_guard': 1-beta,
        'new_BIT_row_stock_sublinear_in_active_group': beta*(1-Q(3, 1000)),
        'fixed_halo_explicit_metadata_branch': 128-48-epsilon-beta-1,
    }
    return {'parameters': dict(p, cap_xi=xi, lambda_=lam, lambda_prime=1-q),
            'margins': margins, 'strict_checks': checks, 'functional_checks': functional}


def compiler_rank(E, targets, paid, tested, uniform):
    """The original sufficient bound, re-instantiated for the new exponent."""
    m, kmin, rmax = max(targets), min(targets), max(paid)
    need((m, kmin, rmax) == (57, 6, 5), 'Pinned complex separation')
    t, z = 1-tested, 1-uniform
    z0, h = (t+z)/2, Q(1, 10)
    delta = z0-t
    need(0 < t < z0 < z < 1, 'Compiler exponent order')
    need(5**10 < 6**9 and 57 < 2**10, 'Exact source rank bounds')
    need(z0 > Q(1, 2) and (1-z0)*E.log_interval(m)[1] < E.log_interval(2)[0],
         'Original eta strictly exceeds 1/4')
    H0 = ceil((3+4*delta)/(h*delta))
    ratio = H0*(1-z0)/(z-z0)
    H1 = ratio.numerator//ratio.denominator+1
    need(H0 >= m.bit_length() and H0*h*delta >= 3+4*delta, 'Induction starts')
    need(H1*(z-z0) > H0*(1-z0), 'Strict winning uniform rank')
    need((H0-1)*h*delta < 3+4*delta, 'Reject one lower threshold exponent')
    need((H1-1)*(z-z0) <= H0*(1-z0), 'Reject one lower final exponent')
    return {'t': t, 'z0': z0, 'z': z, 'theta_upper': Q(9, 10),
            'H0': H0, 'H1': H1, 'N_encoding': '2^H1',
            'strict_final_gap': H1*(z-z0)-H0*(1-z0),
            'winning_word_materialized': False,
            'bound': 'Original sufficient inequality; a sharper bound is separate.'}


def run(source_root):
    base = source_root/PREFIX
    interval_path = base/'architecture/mixed_target_probe.py'
    spec = importlib.util.spec_from_file_location('pr4359_moment', interval_path)
    E = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E)
    cover = read(base/'controller/P3-NATIVE-COVER.json.gz')['cover']
    targets = {int(k): int(v) for k, v in cover['targets'].items()}
    paid = {int(k): int(v) for k, v in cover['paid'].items()}
    need(targets == {6: 192, 7: 56, 8: 93, 9: 1229, 25: 448, 57: 224},
         'Exact source productive inventory')
    need(paid == {1: 17623, 2: 5065, 3: 1738, 4: 714, 5: 254},
         'Exact source paid inventory')
    signed = Counter(targets)
    signed.subtract(paid)
    need(sum(k*v for k, v in signed.items()) == 224, 'Rank-one surplus')
    bracket = {'lower': E.moment(signed, TESTED), 'upper': E.moment(signed, ROOT_UPPER)}
    need(bracket['lower'][0] > 0 and bracket['upper'][1] < 0,
         'Strict mixed test and upper root bound')

    original = read(base/'controller/OUTER-PARAMETERS.json')['outer']
    old = ledger({'kappa': Q('0.0023'), 'complex_uniform_saving': Q('0.002304'),
                  'b': Q('0.002303'), 'a': Q('0.0023025'), 'q': Q('0.002302'),
                  'bit_saving': Q('0.0027'), 'epsilon': Q('0.99999'),
                  'beta': Q('0.99997'), 'r0': Q(1, 10**6),
                  'stop': Q(1, 10**8), 'layout': Q(1, 10**6)})
    for group in ('margins', 'strict_checks'):
        frozen = {key: Q(value['rational']) for key, value in original[group].items()}
        need(old[group] == frozen, 'Exact reproduction of every old '+group)
    p = family(KAPPA, TESTED)
    result = ledger(p)
    need(all(v > 0 for v in result['strict_checks'].values()), 'All 54 new outer predicates')
    need(all(v > 0 for v in result['functional_checks'].values()), 'Additional functional predicates')
    need(min(result['margins'].values()) == result['margins']['main_transform'],
         'Main transform remains limiting')
    need(result['parameters']['cap_xi'] == Q(29, 32)+(1-p['d'])*p['q'],
         'Cofinal cap simplification')
    controls = {}
    for label, updates in [('closed_epsilon_gap', {'epsilon': Q(1)}),
                           ('missing_layout', {'layout': Q(0)}),
                           ('unfunded_kappa', {'kappa': Q('0.002306')}),
                           ('BIT_below_effective', {'bit_saving': OLD_BASELINE}),
                           ('no_complex_slack', {'complex_uniform_saving': p['b']})]:
        tested = ledger(dict(p, **updates))
        failures = {k: v for k, v in tested['strict_checks'].items() if v <= 0}
        need(failures, 'Mutation rejected: '+label)
        controls[label] = failures
    need(E.moment(signed, Q('0.004'))[1] < 0, 'Unsupported mixed target is rejected')
    inputs = [interval_path, base/'controller/P3-NATIVE-COVER.json.gz',
              base/'controller/OUTER-PARAMETERS.json']
    return encode({'schema': 'pr4359-cofinal-outer-refill/1',
                   'status': 'PASS_EXACT_CONDITIONAL_ENDPOINT_REFILL',
                   'kappa': KAPPA, 'gain_over_PR4359': KAPPA-Q('0.0023'),
                   'unchanged_paid': paid, 'unchanged_targets': targets,
                   'mixed_test_saving': TESTED, 'mixed_test_margin': E.show(bracket['lower']),
                   'root_upper_test': ROOT_UPPER, 'root_upper_margin': E.show(bracket['upper']),
                   'old_ledger_crosscheck': {'matched_savings': len(old['margins']),
                                           'matched_checks': len(old['strict_checks'])},
                   'outer': result, 'limiting_margin': min(result['margins'].values())-KAPPA,
                   'compiler': compiler_rank(E, targets, paid, TESTED, p['complex_uniform_saving']),
                   'negative_controls': controls,
                   'source_sha256': {str(p.relative_to(source_root)): sha256(p.read_bytes()).hexdigest()
                                     for p in inputs},
                   'scope': 'Conditional arithmetic and specified finite rank. The PR4359 native, compiler, cover, precision, fixed-tape and outer hypotheses remain premises; no full theorem or practical word is certified.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=HERE/'source')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = run(args.source_root)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({key: result[key] for key in
                      ('status', 'kappa', 'gain_over_PR4359', 'limiting_margin', 'compiler')}, sort_keys=True))


if __name__ == '__main__':
    main()
