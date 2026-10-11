"""Exact composition of the unchanged PR #458 complex supplier (paid residual adapters, whole-residual hosting) with the kernel-cap bit supplier
(R715 word, 112 rank-1 kernel pivots chosen by annealing).  Same contracts and the same outer assembly as research/e8-r715-paid-complex/compose.py
(PR #460's assemble.py structure): both exact rational moments with two engines, six bootstrap levels, all 47 strict outer inequalities, and the
next-grid / zero-eta / zero-beta / unit-beta rejection controls.  Screen mode cites the pinned endpoints of the two suppliers (this package's
EXPECTED.json and PR #458's report in e8-r715-paid-complex/evidence); full mode consumes freshly verified supplier outputs.
usage: compose.py OUT.json [--research-root R] [--complex-output DIR --bit-output DIR]
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0."""
from pathlib import Path
from fractions import Fraction as Q
import argparse, importlib.util, json, hashlib, os
ROOT = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(); ap.add_argument('output', type=Path); ap.add_argument('--research-root', type=Path, default=ROOT.parent)
ap.add_argument('--complex-output', type=Path); ap.add_argument('--bit-output', type=Path); a = ap.parse_args()
read = lambda p: json.loads(p.read_text()); sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest(); source = read(ROOT / 'SOURCE.json')
assert bool(a.complex_output) == bool(a.bit_output)
mode = 'FRESH_FULL_SUPPLIERS' if a.complex_output else 'PINNED_REPORT_SCREEN_FULL_REPLAY_PENDING'
RECORD = bool(os.environ.get('E8KCAP_RECORD')) and bool(a.complex_output)      # first recording run: nothing to compare with yet
R = a.research_root; cxpkg = R / source['complex']['package']; paid = R / source['paid']['package']
ebit = None if RECORD else read(ROOT / 'EXPECTED.json')['full']['bit']
if a.complex_output:
    cr = read(a.complex_output / 'RECEIPT.json'); br = read(a.bit_output / 'BIT-RECEIPT.json')
    assert cr['status'] == 'PASS_COMPLEX_ADAPTED_KERNEL_FULL_COMPOSITION' and cr['mode'] == 'full'
    assert br['status'] == 'PASS_R715_KERNEL_CAP_BIT' and br['mode'] == 'full'
    assert cr['manifest_sha256'] == source['complex']['manifest_sha256'] and cr['source_sha256'] == source['complex']['source_sha256']
    assert br['manifest_sha256'] == sha(ROOT / 'MANIFEST.json') and br['source_sha256'] == sha(ROOT / 'SOURCE.json')
    cx = read(a.complex_output / 'RESULT.json'); audit = read(a.complex_output / 'complex/AUDIT.json')
    bit = read(a.bit_output / 'eleven/mixed_d3/RESULT.json')
else:
    cx = read(paid / 'evidence/COMPLEX-PARENT-RESULT.json'); audit = read(paid / 'evidence/COMPLEX-PARENT-AUDIT.json'); bit = ebit
for k, v in read(cxpkg / 'EXPECTED.json').items(): assert cx[k] == v, ('complex', k)
for k in () if RECORD else ('bit_lower', 'bit_only_kappa', 'bit', 'bit_profile', 'halving_depth', 'external_row_allowance', 'bit_template_sha256', 'emitted_program_sha256'):
    assert bit[k] == ebit[k], ('bit', k)
assert audit['template_sha256'] == cx['complex_template_sha256'] and audit['emitted_program_sha256'] == cx['complex_emitted_program_sha256']
assert audit['max_helpers_per_physical_family_per_call'] == 1
def load(n):
    spec = importlib.util.spec_from_file_location(n, R / 'e8-r740-replica32/code/engines' / (n + '.py')); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
M, Other, Outer = load('moment'), load('base_two_moment'), load('outer')
endpoints = {}
for name, P, m, W, claimed in [('bit', bit['bit_profile'], 78, bit['bit']['live'], bit['bit_lower']), ('complex', audit['profile'], 89, audit['live'], cx['complex_lower'])]:
    P = {int(k): v for k, v in P.items()}; assert W % 1200 == 0 and m * W - sum(k * v for k, v in P.items()) == 408 * (W // 1200)
    cert = M.certify(P, m, W, True); lo, hi = Q(cert['lower']), Q(cert['upper']); assert lo == Q(claimed)
    for x, below in [(lo, True), (hi, False)]:
        u, v = Other.moment(m, W, list(P.items()), x); uu, vv = Other.moment(m, W, [(1, 32 * m * m * sum(P.values()))], x)
        assert (v + vv / 10 ** 16 < 1) if below else (u + uu / 10 ** 16 > 1)
    endpoints[name] = lo
assert bit['halving_depth'] == 3 and bit['bit']['row_coefficient'] == 28416 and bit['bit']['charged_two_level_coefficient_bits'] == 576
assert bit['bit']['two_level_coefficient_bits'] <= 576
assert cx['complex']['row_coefficient'] == 20161
assert cx['complex']['local_bound'] < 1 << 48 and cx['complex']['router_bits'] <= 30000 and cx['complex']['literal_bits'] <= 100000
assert cx['complex']['charged_wrapper_groups'] == 788480 and cx['complex']['wrapper_events'] == 13904
ALLOW = max(bit['bit']['row_coefficient'], cx['complex']['row_coefficient'], 20161); COEF = bit['bit']['charged_two_level_coefficient_bits']
c, b = endpoints['bit'], endpoints['complex']; eta = beta = Q(1, 10 ** 18); grid = Q(1, 10 ** 18); s = min(c, (1 - beta) * b) - Q(1, 10 ** 24); assert 0 < s < c and s < (1 - beta) * b
chain = [Q(384599, 10 ** 10)]; cutoffs = []
def ceil(x): return -((-x.numerator) // x.denominator)
for _ in range(6):
    old = chain[-1]; nxt = (1 - s) * s + s * old; gap = min(s - nxt, 1 - nxt - s, 1 - nxt - s * (1 - old), 1 - s); assert old < nxt < s < 1 - nxt and gap > 0
    bound = max(ceil(36 / gap ** 2), ceil(2 * (4 + COEF) / gap)); assert bound * gap ** 2 >= 36 and bound * gap >= 2 * (4 + COEF)
    cutoffs.append(dict(gap=str(gap), cutoff_log2=str(bound))); chain.append(nxt)
q = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * q / (1 + q); ticks = margin / grid; k = grid * ((ticks.numerator - 1) // ticks.denominator)
bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1}, 'rows': {'degree_gap': Q(10 ** 6) - Q(51 * ALLOW, 25)}}
res = Outer.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta); assert len(res['strict_constraints']) == 47 and all(x > 0 for x in res['strict_constraints'].values())
controls = []
for name, kk, ee, bb in [('next_grid', k + grid, eta, beta), ('zero_eta', k, Q(0), beta), ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1))]:
    try: Outer.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
    except AssertionError: controls.append(name)
    else: raise AssertionError(name)
K458, K460, K463 = Q(cx['kappa']), Q(1274415506145115, 10 ** 18), Q(641739651875561, 5 * 10 ** 17)
K472 = Q(1292100, 10 ** 9)      # PR #472 as quoted (7 digits); the gain over it is therefore a 7-digit figure
assert k > K463
result = dict(status='PASS_R715_KERNEL_CAP_COMPOSITION', mode=mode, kappa=str(k), kappa_decimal=format(float(k), '.18f'),
              gain_over_pr458_percent=float((k / K458 - 1) * 100), gain_over_pr460_percent=float((k / K460 - 1) * 100), gain_over_pr463_percent=float((k / K463 - 1) * 100),
              gain_over_pr472_percent_quoted=float((k / K472 - 1) * 100),
              bit_lower=str(c), complex_lower=str(b), binding_component='bit' if c < (1 - beta) * b else 'complex',
              row_allowance=ALLOW, charged_coefficient_bits=COEF, bootstrap=cutoffs, strict_outer_constraints={n: str(x) for n, x in res['strict_constraints'].items()},
              outer_controls=controls, bit_template_sha256=bit['bit_template_sha256'], complex_template_sha256=cx['complex_template_sha256'])
a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(result, indent=2) + '\n')
print(result['kappa_decimal'], result['binding_component'], 'vs #463 %+.4f%%' % result['gain_over_pr463_percent'], mode)
