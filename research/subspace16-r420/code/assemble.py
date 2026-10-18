"""Compose independently verified R420 bit and freshly admitted subspace complex supplier.

Prepared for icekylinx with GPT-6 Astra assistance, Apache-2.0.
Adapted from the attributed PR531 assembly. Both rational moment engines and
the 47-constraint outer engine remain pinned inherited implementations.
Both changed operators are freshly reconstructed; the complex data controller is retained.
Adaptation: fresh bit invoice and source hashes replace the cited bit receipt.
Usage: assemble_meta.py PACKAGE BIT_RESULT OUTDIR COMPLEX_AUDIT COMPLEX_HOSTED
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
ROOT, B, O, CA, CH = map(Path, sys.argv[1:6]); O.mkdir(parents=True, exist_ok=True)
BIT_COMMIT = '2065fe4f72a914d907f1046603f5a36f17018535'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    path = ROOT / 'vendor/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines' / (name + '.py')
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
owner = json.loads((CA / 'OWNERS-AND-PROFILE.json').read_text())
inv = json.loads((CA / 'PREFIX-AND-INVOICE.json').read_text())
host = json.loads((CH / 'HOSTED.json').read_text())
assert owner['template_sha256'] == inv['template_sha256'] == host['template_sha256']
assert inv['owner_audit_sha256'] == sha(CA / 'OWNERS-AND-PROFILE.json')
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

# These checks bind and reprice the freshly reconstructed bit invoice.
# Native local and global physical admission are separately source-bound.
bit = json.loads(B.read_text())
assert bit['status'] == 'PASS_NINE_STAGE_WHOLE_HOSTED_BIT_PRICE_AND_CITED_ASSEMBLY'
bitP = {int(rank): count for rank, count in bit['bit_profile'].items()}
bit_inv = bit['bit']
bm, bW = 64, bit_inv['live']
assert (bm, bW, bit['stages'], bit['replicas']) == (64, 30720, 9, 32)
assert sum(rank * count for rank, count in bitP.items()) == bit_inv['rank_mass']
assert bm * bW - bit_inv['rank_mass'] == 9984
assert max(bitP) == bit_inv['maxchild'] == 42
assert bit_inv['halving_depth'] == 2 and 2 * max(bitP)**2 < bm**2
assert bit_inv['physical'] == bW + 9 == 30729
assert bit_inv['hosted_residuals'] == 420 * 9 * 32
assert bit_inv['bank_assignments'] == 0
assert bit_inv['prefix_bits'] < 256
assert bit_inv['prefix_bits'] < bit_inv['charged_prefix_bits'] == 192
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

baselines = {'PR547_updated':Q('0.001590984155135328'), 'PR535': Q('0.001584931111785787'), 'PR541': Q('0.001587212454640692'), 'PR542_543': Q('0.001587467473762886'), 'PR544': Q('0.001588602246663212'),
             'PR531': Q('0.001517760977820331'),
             'rejected_POST208_checkpoint': Q('0.001543640781718742'),
             'PR533': Q('0.001524207950793244')}
res = dict(
    status='PASS_SUBSPACE16_R420_BOTH_SUPPLIERS',
    complex_lower=str(b), complex_decimal=decimal(b, 24),
    next_b_rejected=str(bp), exact_moment_receipts=complex_receipts,
    bit_lower=str(c), bit_decimal=decimal(c, 24),
    bit_exact_moment_receipts=bit_receipts,
    bit_result_sha256=sha(B),
    complex_dependency={'source_pr':548,'commit':'66dbc2bffc1bfa8d50b3f9a2ac7ccba8fd9f6f36','local_word':'response-sliced and subspace-optimized static44','new_global_owners':False},
    bit_dependency={'pull_request':543,'commit':BIT_COMMIT,'changed_word':'PR543 R420 with interleaved phase-B source writes','fresh_bit_receipt_sha256':sha(B)},
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
    owner_audit_sha256=sha(CA / 'OWNERS-AND-PROFILE.json'),
    invoice_sha256=sha(CA / 'PREFIX-AND-INVOICE.json'),
    bit_scope='The R420 bit word is freshly reconstructed, replayed and admitted by this package by the native local and hosted-global checkers, with its interleaved source-write interface audited separately. The static44 complex supplier is freshly rebuilt and admitted separately.',
    scope='Conditional finite witness under the retained all-size compiler, '
          'common-label/mutable-basis, whole-call hosting, restored-work, '
          'precision/tape and analytic-transfer contracts. Fresh changed-bit admission '
          'and complex admission and finite invoices are separately hash-bound. The unchanged complex data controller remains a cited dependency. No unconditional theorem is claimed.')
(O / 'EXACT-ASSEMBLY.json').write_text(json.dumps(res, indent=2) + '\n')
print(res['status'], 'b', res['complex_decimal'], 'kappa', res['kappa_decimal'])
print(json.dumps(res['improvements'], sort_keys=True))
