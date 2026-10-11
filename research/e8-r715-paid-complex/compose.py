"""Exact composition of the unchanged PR #458 complex supplier (paid residual adapters, whole-residual hosting) with the R715
eleven-stage whole-residual bit supplier (research/e8-r715-eleven-stage-whole).  Full mode consumes freshly verified wrappers;
screen mode cites PR #458's pinned report (evidence/) and the bit package's EXPECTED.json.
Structure follows PR #460's assemble.py (Rohan Arun with OpenAI Codex assistance, Apache-2.0); the bit-side contracts are the
R715 package's (eleven stages, halving depth 3, two-level coefficient charged 576 bits, row coefficient 28,416 > 20,161, so the
outer row allowance is 28,416).  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0.
usage: compose.py OUT.json [--research-root R] [--complex-output DIR --bit-output DIR]"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, hashlib, importlib.util, json
ROOT = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(); ap.add_argument('output', type=Path); ap.add_argument('--research-root', type=Path, default=ROOT.parent)
ap.add_argument('--complex-output', type=Path); ap.add_argument('--bit-output', type=Path); a = ap.parse_args()
read = lambda p: json.loads(p.read_text()); sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest(); source = read(ROOT / 'SOURCE.json')
assert bool(a.complex_output) == bool(a.bit_output)
mode = 'FRESH_FULL_SUPPLIERS' if a.complex_output else 'PINNED_REPORT_SCREEN_FULL_REPLAY_PENDING'
bitpkg = a.research_root / source['bit']['package']
if a.complex_output:
    cr = read(a.complex_output / 'RECEIPT.json'); br = read(a.bit_output / 'RECEIPT.json')
    assert cr['status'] == 'PASS_COMPLEX_ADAPTED_KERNEL_FULL_COMPOSITION' and cr['mode'] == 'full'
    assert br['status'] == 'PASS_R715_ELEVEN_STAGE_WHOLE_RESIDUAL' and br['mode'] == 'full'
    for receipt, key in [(cr, 'complex'), (br, 'bit')]:
        assert receipt['manifest_sha256'] == source[key]['manifest_sha256'] and receipt['source_sha256'] == source[key]['source_sha256']
    cx = read(a.complex_output / 'RESULT.json'); audit = read(a.complex_output / 'complex/AUDIT.json')
    bit = read(a.bit_output / 'eleven/mixed_d3/RESULT.json')
else:
    cx = read(ROOT / 'evidence/COMPLEX-PARENT-RESULT.json'); audit = read(ROOT / 'evidence/COMPLEX-PARENT-AUDIT.json')
    bit = read(bitpkg / 'EXPECTED.json')['variants']['pr442']
# both suppliers' published expected fields
for k, v in read(a.research_root / source['complex']['package'] / 'EXPECTED.json').items(): assert cx[k] == v, ('complex', k)
ebit = read(bitpkg / 'EXPECTED.json')['variants']['pr442']
for k in ('bit_lower', 'bit_only_kappa', 'bit', 'bit_profile', 'halving_depth', 'external_row_allowance', 'bit_template_sha256', 'emitted_program_sha256'):
    assert bit[k] == ebit[k], ('bit', k)   # the bit supplier's own fields (the kappa there is paired with PR #442's complex)
assert audit['template_sha256'] == cx['complex_template_sha256'] and audit['emitted_program_sha256'] == cx['complex_emitted_program_sha256']
assert audit['max_helpers_per_physical_family_per_call'] == 1
def load(n):
    spec = importlib.util.spec_from_file_location(n, a.research_root / 'e8-r740-replica32/code/engines' / (n + '.py')); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
M, Other, Outer = load('moment'), load('base_two_moment'), load('outer')
endpoints = {}
for name, P, m, W, claimed in [('bit', bit['bit_profile'], 78, bit['bit']['live'], bit['bit_lower']), ('complex', audit['profile'], 89, audit['live'], cx['complex_lower'])]:
    P = {int(k): v for k, v in P.items()}; assert W % 1200 == 0 and m * W - sum(k * v for k, v in P.items()) == 408 * (W // 1200)
    cert = M.certify(P, m, W, True); lo, hi = Q(cert['lower']), Q(cert['upper']); assert lo == Q(claimed)
    for x, below in [(lo, True), (hi, False)]:
        u, v = Other.moment(m, W, list(P.items()), x); uu, vv = Other.moment(m, W, [(1, 32 * m * m * sum(P.values()))], x)
        assert (v + vv / 10 ** 16 < 1) if below else (u + uu / 10 ** 16 > 1)
    endpoints[name] = lo
# Preserve the suppliers' complete independent cost and row contracts.
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
K458, K460 = Q(cx['kappa']), Q(1274415506145115, 10 ** 18)
assert k > K458
result = dict(status='PASS_R715_PAID_COMPLEX_COMPOSITION', mode=mode, kappa=str(k), kappa_decimal=format(float(k), '.18f'),
              gain_over_pr458_percent=float((k / K458 - 1) * 100), gain_over_pr460_percent=float((k / K460 - 1) * 100),
              bit_lower=str(c), complex_lower=str(b), binding_component='bit' if c < (1 - beta) * b else 'complex',
              row_allowance=ALLOW, charged_coefficient_bits=COEF, bootstrap=cutoffs, strict_outer_constraints={n: str(x) for n, x in res['strict_constraints'].items()},
              outer_controls=controls, bit_template_sha256=bit['bit_template_sha256'], complex_template_sha256=cx['complex_template_sha256'])
a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(result, indent=2) + '\n'); print(result['kappa_decimal'], result['binding_component'], 'vs #460 %+.4f%%' % result['gain_over_pr460_percent'], mode)
