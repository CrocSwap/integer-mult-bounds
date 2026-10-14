"""Separate exact cost derivation for the explicit fine-padding point.

No import or execution of check_ledger.py; same-session implementation,
not independent human review of the all-size proof.
"""
import argparse
import json
from fractions import Fraction as F
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must be enabled')
P = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
claim = json.loads((P/'CLAIM.json').read_text())
spec = json.loads((P/'inputs/SUPPLIER-SPEC.json').read_text())
receipt = json.loads((P/'LEDGER.json').read_text())
row = receipt['rows']['fine_prime_padding_strassen']
rat = lambda x: F(x['rational'])

delta = F(1, 10**7)
E, B = 1-delta, 1-3*delta
assert (E, B) == (F(claim['epsilon']), F(claim['beta']))
nu, halo, core = claim['theta_power'], claim['halo_power'], claim['core_power']
assert (nu, halo, core) == (2, 48, 128)
tau = F(claim['matrix_exponent'])
assert tau == F(45, 16) and 2**45 > 7**16
c = (3-tau)/2
assert c == F(3, 32)
pinned = F(spec['expected']['complex_lower'])
b = pinned-F(1, 10**64)
q = b-F(1, 10**64)
a = (q+b)/2
r, z, slack, stop = F(1, 10**64), F(1, 10**66), F(1, 10**64), F(1, 10**70)
# Solve c+X-E=E*q+slack, independently of the ledger's stored X.
X = E+E*q+slack-c
assert (E, X, B) == tuple(rat(row[n]) for n in ('epsilon', 'xi', 'beta'))
assert 1-E+q*B-E*q == delta*(1-2*q) > 0
assert 0 < q < a < b < pinned < F('0.001733427039589844234749')
assert (1-stop)*b > a
assert F(1, 2) < X < E < 1 and 0 < B < E and X < nu
assert 1-B-2*(1-E) == delta
assert 1-B == 3*delta and E-B == 2*delta
assert 1-(2*X-nu)-r-B > z > 0
assert 1-E-r > 0 and core-halo-B > 0
assert halo > 43

costs = {
    'main_transform': 1-E*q,
    'global_coordinate_router': 1-a,
    'fused_gaussian': E-q*B,
    'group_bit_router': E-a*B,
    'group_scans': E-B,
    'boundary_algebraic_matrix': E-X+(tau-1)/2,
    'sparse_union_movement': E+F(1, 2)-X,
    'polynomial_products': 1-E,
    'microbox_face_corrections': E+B+halo-core+2,
}
# Here E*q is exactly on the retained decimal grid; no numerical floor needed.
assert (10**100) % (E*q).denominator == 0
k = E*q-F(1, 10**76)
headline = F(claim['kappa'])
assert k == rat(row['kappa']) and headline < k
assert max(costs.values()) == costs['main_transform']
assert all(x < 1-k for x in costs.values())
assert {n: 1-v for n, v in costs.items()} == {
    n: rat(v) for n, v in row['margins'].items()}
assert len(row['strict_checks']) == 56
assert all(rat(v) > 0 for v in row['strict_checks'].values())
assert len(receipt['rejecting_controls']['fine_prime_padding_strassen']) == 14
reported_1758 = F('0.001679745508802299051546533685199973672313473419790800679752457380932784242972585600630181672224983')
assert headline > reported_1758

rejected = {
    'old_theta_chirp_guard': 1-(2*X-E)-r-B < 0,
    'old_linear_guard': 1-X-r-B < 0,
    'old_two_beta_tag_budget': 1-2*B < 0,
    'old_per_axis_full_scan': E > 1-k,
    'old_g_union_scan': E+B+F(1, 2)-X > 1-k,
    'full_union_key_sort': costs['sparse_union_movement']+B+1-E > 1-k,
    'unsupported_strassen_exponent': 7**5 > 2**14,
    'epsilon_limit': not (F(1) < 1),
}
assert all(rejected.values())
report = dict(status='PASS_SEPARATE_FINE_PADDING_COST_DERIVATION',
    kappa=str(k), headline=str(headline), epsilon=str(E), cap=str(X), beta=str(B),
    theta_power=nu, halo_power=halo, core_power=core,
    matrix_exponent=str(tau), boundary_constant=str(c),
    main_gaussian_gap=str(delta*(1-2*q)),
    group_chirp_guard=str(1-(2*X-nu)-r-B),
    membership_gap=str(delta), normalization_power_gap=str(1-E-r),
    cost_powers={n: str(x) for n, x in costs.items()},
    strict_checks=56, ledger_controls=14, separate_fault_controls=rejected,
    gain_over_reported_1758=str(headline-reported_1758),
    scope='Separate exact implementation in one session. The cited prime theorem and written precision, locality and circuit arguments are mathematical inputs; finite tests do not prove the complete multiplication theorem.')
args.out.write_text(json.dumps(report, sort_keys=True, indent=2)+'\n')
print(report['status'])
