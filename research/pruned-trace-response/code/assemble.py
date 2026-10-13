"""Fresh two-supplier exact assembly. Adapted from PR531/535 and PR539; Apache-2.0.
No approximate numerical evaluation is used for acceptance.
Usage: assemble.py PACKAGE BIT_INVOICE COMPLEX_GLOBAL OUT
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
ROOT, B, C, O = map(Path, sys.argv[1:5]); O.mkdir(parents=True, exist_ok=True)
BIT_COMMIT = '64edee18af02aab0c1696b677a0287dd0146381b'
BIT_EXPECTED_SHA256 = '19b861f69f7602e47b390d472b487d044bff4230b250520807537c213ad0249f'


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
owner = json.loads((C / 'audit/OWNERS-AND-PROFILE.json').read_text())
inv = json.loads((C / 'audit/PREFIX-AND-INVOICE.json').read_text())
host = json.loads((C / 'hosted/HOSTED.json').read_text())
assert owner['template_sha256'] == inv['template_sha256'] == host['template_sha256']
assert inv['owner_audit_sha256'] == sha(C / 'audit/OWNERS-AND-PROFILE.json')
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
assert max(bitP) == bit_inv['maxchild'] == 8
assert bm * bm > 2 * 64 * max(bitP)
assert bit_inv['physical'] == bW + 9 == 30729
assert bit_inv['hosted_residuals'] == 480 * 9 * 32
assert bit_inv['bank_assignments'] == 0
assert bit_inv['prefix_bits'] < 256
assert bit_inv['prefix_bits'] < bit_inv['charged_prefix_bits'] <= 256
assert bit_inv['two_level_coefficient_bits'] < bit_inv['charged_two_level_coefficient_bits'] == 512
assert bit_inv['row_coefficient'] < 20161
# PR539 exact fallback charge, applied to the freshly checked changed bit profile.
# Transfer of the source bad-class bound remains an explicit inherited premise.
from decimal import Decimal,localcontext,ROUND_FLOOR
N=2*bm;F=6*N*(N-1)+3*N+6*(N-1);delta=Q(2*bm**3,2**80);factor=delta*F*sum(bitP.values())
assert F==98682 and delta==Q(1,2**61)
with localcontext() as ctx:
    ctx.prec=90
    terms=[(Decimal(r*n)/Decimal(bm*bW),(Decimal(bm)/Decimal(r)).ln()) for r,n in bitP.items()]
    fb=Decimal(factor.numerator)/Decimal(factor.denominator)/Decimal(bm*bW);lm=Decimal(bm).ln();lo=Decimal(0);hi=Decimal('.003')
    for _ in range(250):
        a=(lo+hi)/2
        if sum(p*(a*l).exp() for p,l in terms)+fb*(a*lm).exp()<1:lo=a
        else:hi=a
    c=Q(int((lo*Decimal(10**24)).to_integral_value(rounding=ROUND_FLOOR)),10**24)
bit_receipts=[]
for endpoint,accept in [(c,True),(c+Q(1,10**24),False)]:
    lo,hi=M.moment(bitP,bm,bW,endpoint,False);fl,fh=M.moment({1:1},bm,bW,endpoint,False)
    a,z=Other.moment(bm,bW,list(bitP.items()),endpoint);g,h=Other.moment(bm,bW,[(1,1)],endpoint)
    lo+=factor*fl;hi+=factor*fh;a+=factor*g;z+=factor*h
    assert (hi<1 and z<1) if accept else (lo>1 and a>1)
    bit_receipts.append(dict(endpoint=str(endpoint),accept=accept,mercator=[str(lo-1),str(hi-1)],base_two=[str(a-1),str(z-1)]))
assert c>Q(bit['bit_lower'])


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

baselines = {'PR535': Q('0.001584931111785787'), 'prior_tn23': Q('0.001587212454640692'), 'PR539': Q('0.001584931113695072'),
             'PR531': Q('0.001517760977820331'),
             'rejected_POST208_checkpoint': Q('0.001543640781718742'),
             'PR533': Q('0.001524207950793244')}
res = dict(
    status='PASS_PRUNED_TRACE_RESPONSE_FRESH_BOTH_SUPPLIERS',
    complex_lower=str(b), complex_decimal=decimal(b, 24),
    next_b_rejected=str(bp), exact_moment_receipts=complex_receipts,
    bit_lower=str(c), bit_decimal=decimal(c, 24),
    bit_exact_moment_receipts=bit_receipts,
    bit_result_sha256=sha(B),
    complex_dependency={'pull_request':535,'commit':'8b758a103915179322766bed5798f9b6e7198011','path':'research/post-center-rank4-global'},
    bit_dependency={'pull_request':510,'commit':BIT_COMMIT,'changed_word':'prune227_trace20_steinberg7','fresh_bit_receipt_sha256':sha(B)},
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
    owner_audit_sha256=sha(C / 'audit/OWNERS-AND-PROFILE.json'),
    invoice_sha256=sha(C / 'audit/PREFIX-AND-INVOICE.json'),
    sharp_fallback={'source_PR':539,'bad_fraction':str(delta),'fallback_per_edge':F,'rank_one_mass':str(factor)},
    bit_scope='Both changed suppliers are freshly reconstructed and independently replayed locally and globally; exact fresh profiles are composed, without adding gains.',
    scope='Conditional finite witness under the retained all-size compiler, '
          'common-label/mutable-basis, whole-call hosting, restored-work, '
          'precision/tape and analytic-transfer contracts. Fresh changed-bit admission '
          'and finite invoices are separately hash-bound. PR539 bad-class transport is retained as a premise. No unconditional theorem is claimed.')
(O / 'EXACT-ASSEMBLY.json').write_text(json.dumps(res, indent=2) + '\n')
print(res['status'], 'b', res['complex_decimal'], 'kappa', res['kappa_decimal'])
print(json.dumps(res['improvements'], sort_keys=True))
