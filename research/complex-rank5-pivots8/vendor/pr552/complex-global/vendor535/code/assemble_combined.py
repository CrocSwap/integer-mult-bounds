"""Exact composition of the new complex supplier and pinned PR510 bit supplier.

Prepared for icekylinx with GPT-6 Astra assistance, Apache-2.0.
Adapted from the attributed PR531 assembly. Both rational moment engines and
the 47-constraint outer engine remain pinned inherited implementations.
The bit operator is a cited conditional dependency, not freshly reconstructed.
Usage: assemble_combined.py AUDIT BASE HOSTED PR510_EXPECTED
"""
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:
    raise SystemExit('Run with assertions enabled.')
assert __debug__, 'Run with assertions enabled.'
O, V, H, B = map(Path, sys.argv[1:5])
BIT_COMMIT = '64edee18af02aab0c1696b677a0287dd0146381b'
BIT_EXPECTED_SHA256 = '19b861f69f7602e47b390d472b487d044bff4230b250520807537c213ad0249f'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    path = V / 'work/pr361/code/engines' / (name + '.py')
    spec = importlib.util.spec_from_file_location('combined_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decimal(value, places):
    scaled = value * 10 ** places
    assert scaled.denominator == 1
    digits = str(scaled.numerator).zfill(places + 1)
    return digits[:-places] + '.' + digits[-places:]


M, Other, Outer = [load(name) for name in ['moment', 'base_two_moment', 'outer']]
owner = json.loads((O / 'OWNERS-AND-PROFILE.json').read_text())
inv = json.loads((O / 'PREFIX-AND-INVOICE.json').read_text())
host = json.loads((H / 'HOSTED.json').read_text())
assert owner['template_sha256'] == inv['template_sha256'] == host['template_sha256']
assert inv['owner_audit_sha256'] == sha(O / 'OWNERS-AND-PROFILE.json')
assert all(inv['strict_checks'].values())
P = {int(rank): count for rank, count in owner['paid_profile'].items()}
m, W = 73, owner['live']
assert m * W - sum(rank * count for rank, count in P.items()) == 2560


def two_moments(profile, dimension, live, lower):
    """Keep the full rational sign intervals for both independent engines."""
    fallback = 32 * dimension * dimension * sum(profile.values())
    receipts = []
    for endpoint, accept in [(lower, True), (lower + Q(1, 10**24), False)]:
        lo, hi = M.moment(profile, dimension, live, endpoint, True)
        a, b = Other.moment(dimension, live, list(profile.items()), endpoint)
        f, g = Other.moment(dimension, live, [(1, fallback)], endpoint)
        a += f / 10**16
        b += g / 10**16
        assert (hi < 1 and b < 1) if accept else (lo > 1 and a > 1)
        receipts.append(dict(endpoint=str(endpoint), accept=accept,
                             mercator=[str(lo - 1), str(hi - 1)],
                             base_two=[str(a - 1), str(b - 1)]))
    return receipts


cert = M.certify(P, m, W, True)
b, bp = Q(cert['lower']), Q(cert['upper'])
assert bp - b == Q(1, 10**24)
complex_receipts = two_moments(P, m, W, b)

# These checks bind and reprice published bit data. They do not stand in for
# the physical-operator and mutable-source realization dependency.
assert sha(B) == BIT_EXPECTED_SHA256
bit = json.loads(B.read_text())['nine']
bitP = {int(rank): count for rank, count in bit['profile'].items()}
bit_inv = bit['bit']
bm, bW = bit['m'], bit_inv['live']
assert (bm, bW, bit['stages'], bit['replicas']) == (64, 30720, 9, 32)
assert sum(rank * count for rank, count in bitP.items()) == bit_inv['rank_mass']
assert bm * bW - bit_inv['rank_mass'] == 9984
assert max(bitP) == bit_inv['maxchild'] == 8
assert bm * bm > 2 * 64 * max(bitP)
assert bit_inv['physical'] == bW + 9 == 30729
assert bit_inv['hosted_residuals'] == 480 * 9 * 32
assert bit_inv['bank_assignments'] == 0
assert bit['nine_stage_payload_bits'] < 104
assert bit_inv['prefix_bits'] < bit_inv['charged_prefix_bits'] == 256
assert bit_inv['two_level_coefficient_bits'] < bit_inv['charged_two_level_coefficient_bits'] == 512
assert bit_inv['row_coefficient'] < 20161
c = Q(bit['bit_lower'])
assert c == Q(bit['bit_lower_decimal'])
bit_receipts = two_moments(bitP, bm, bW, c)

eta = beta = grid = Q(1, 10**18)
s = min(c, (1 - beta) * b) - Q(1, 10**24)
assert 0 < s < c and s < (1 - beta) * b
coeff = bit_inv['charged_two_level_coefficient_bits']
row = max(20161, bit_inv['row_coefficient'], inv['finite']['physical_row_coefficient'])
chain, cuts = [Q(384599, 10**10)], []


def ceil(value):
    return -(-value.numerator // value.denominator)


for _ in range(6):
    old = chain[-1]
    a = (1 - s) * s + s * old
    gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
    assert old < a < s < 1 - a and gap > 0
    cut = max(ceil(36 / gap**2), ceil(2 * (4 + coeff) / gap))
    assert cut * gap**2 >= 36 and cut * gap >= 2 * (4 + coeff)
    cuts.append(dict(gap=str(gap), cutoff_log2=str(cut)))
    chain.append(a)
q = chain[-1] * (1 - 2 * eta)
margin = (1 - eta) * q / (1 + q)
ticks = margin / grid
kap = grid * ((ticks.numerator - 1) // ticks.denominator)
bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
          'rows': {'degree_gap': Q(10**6) - Q(51 * row, 25)}}
assembly = Outer.assembly(chain[-1], b, bridge, kap, eta=eta, beta=beta)
assert len(assembly['strict_constraints']) == 47
assert all(value > 0 for value in assembly['strict_constraints'].values())
controls = []
for name, k, e, be in [('next_grid', kap + grid, eta, beta),
                       ('zero_eta', kap, Q(0), beta),
                       ('zero_beta', kap, eta, Q(0)),
                       ('unit_beta', kap, eta, Q(1))]:
    try:
        Outer.assembly(chain[-1], b, bridge, k, eta=e, beta=be)
    except AssertionError:
        controls.append(name)
    else:
        raise AssertionError(name)

baselines = {'PR531': Q('0.001517760977820331'),
             'rejected_POST208_checkpoint': Q('0.001543640781718742'),
             'PR533': Q('0.001524207950793244')}
res = dict(
    status='PASS_ASYNC_COMPLEX_AND_CITED_BIT_EXACT_ASSEMBLY',
    complex_lower=str(b), complex_decimal=decimal(b, 24),
    next_b_rejected=str(bp), exact_moment_receipts=complex_receipts,
    bit_lower=str(c), bit_decimal=decimal(c, 24),
    bit_exact_moment_receipts=bit_receipts,
    bit_result_sha256=sha(B),
    bit_dependency={'pull_request': 510, 'commit': BIT_COMMIT,
                    'path': 'research/e8-r480-nine-stage',
                    'expected_sha256': BIT_EXPECTED_SHA256},
    bit_prefix_bits=bit_inv['charged_prefix_bits'],
    bit_charged_two_level_coefficient_bits=coeff,
    external_row_allowance=row,
    kappa=str(kap), kappa_decimal=decimal(kap, 18),
    binding_component='bit' if c < (1 - beta) * b else 'complex',
    improvements={name: {'baseline': str(value),
                         'relative_gain': str(kap / value - 1),
                         'percent_display': f'{float(100 * (kap / value - 1)):.8f}'}
                  for name, value in baselines.items()},
    strict_outer_constraints={k: str(v) for k, v in assembly['strict_constraints'].items()},
    outer_controls=controls, bootstrap=cuts,
    complex_template_sha256=host['template_sha256'],
    owner_audit_sha256=sha(O / 'OWNERS-AND-PROFILE.json'),
    invoice_sha256=sha(O / 'PREFIX-AND-INVOICE.json'),
    bit_scope='Pinned PR510 published profile and operator are cited dependencies. '
              'Both exact moments are freshly repriced here; the unchanged physical '
              'bit operator is not cold-reconstructed. See PR510-MUTABLE-SOURCE-CARRYOVER.md.',
    scope='Conditional finite witness under the retained all-size compiler, '
          'common-label/mutable-basis, whole-call hosting, restored-work, '
          'precision/tape and analytic-transfer contracts. Fresh complex admission '
          'and finite invoice are separately hash-bound; no unconditional theorem is claimed.')
(O / 'EXACT-ASSEMBLY.json').write_text(json.dumps(res, indent=2) + '\n')
print(res['status'], 'b', res['complex_decimal'], 'kappa', res['kappa_decimal'])
print(json.dumps(res['improvements'], sort_keys=True))
