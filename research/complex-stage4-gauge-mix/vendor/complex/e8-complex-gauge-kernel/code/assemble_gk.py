# Adapted from DaysSky PR442's assemble.py (complex half and strict outer assembly) and DreamingOfClouds' assemble_k.py by
# DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0.
"""Certified complex saving b for the gauge + kernel word under #442's whole-residual hosting: two exact moment engines, fresh
finite invoices with the hosted stock, then #434's strict outer assembly (six bootstrap levels, 47 inequalities, next-grid and
parameter controls) for each bit supplier listed in BITS.json (pinned inputs: c, charged two-level coefficient bits, row coefficient).
usage: assemble_gk.py PARENT_CHANGED PARENT_SC HOSTED_DIR AUDIT.json BITS.json OUT.json"""
import gzip, hashlib, importlib.util, json, math, sys
from fractions import Fraction as Q
from pathlib import Path
par, psc, cd, ap, bitsp, outp = map(Path, sys.argv[1:7])
def load(name):
    sp = importlib.util.spec_from_file_location('gk_' + name, par / 'work/pr361/code/engines' / (name + '.py'))
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod
M, Other, Outer = load('moment'), load('base_two_moment'), load('outer')
audit = json.loads(ap.read_text()); ch = json.loads((cd / 'HOSTED.json').read_text())
assert audit['complex_template_sha256'] == ch['template_sha256']
# ---------------- complex: two moments and the parent's invoice with the hosted stock
PC = {int(r): n for r, n in audit['complex_profile'].items()}; mc, WC = 73, audit['complex_live']; EC = sum(PC.values())
massc = sum(r * z for r, z in PC.items()); assert mc * WC - massc == 2496
rc = M.certify(PC, mc, WC, True); b = Q(int(Q(rc['lower']) * 10 ** 18), 10 ** 18)
fbc = 32 * mc * mc * EC
l3, h3 = Other.moment(mc, WC, list(PC.items()), b); b3, bh3 = Other.moment(mc, WC, [(1, fbc)], b); assert h3 + bh3 / 10 ** 16 < 1
grid = Q(1, 10 ** 18)
l4, h4 = Other.moment(mc, WC, list(PC.items()), b + grid); b4, bh4 = Other.moment(mc, WC, [(1, fbc)], b + grid); assert l4 + b4 / 10 ** 16 > 1   # next grid point rejected
integ = json.loads((psc / 'INTEGRATION.json').read_text()); inv = integ['finite_invoice']
physc = ch['physical']; v = 120
compilerc = 64 * (mc + 1) ** 3
pervertex = inv['pervertex'] - integ['physical'] * (64 + 1) + physc * (64 + 1) - integ['live'] + WC   # stock-dependent terms re-based
r_ = mc // 2; group = 2 ** (r_ * r_) * math.prod(2 ** (2 * i) - 1 for i in range(1, r_ + 1)); stock = group * physc
smass = group * massc; logical = group * max(pervertex, inv['pervertex']) + 64; router = compilerc * (logical + 1) * (stock + 1) ** 2
GG, EE, C0 = 1 << 30000, 1 << 100000, 1 << 210000; BB = smass + EE
literal = 2 * GG * stock ** 2 + 8 * smass + 4 * stock + 4 + 32 * mc
assert logical < 1 << 6050 and router < GG and literal < EE and BB < 1 << 100001 and 32 * mc * BB * BB < C0 and 2 * BB + 18 < C0
depth = 2; assert mc ** depth > 2 * max(PC) ** depth
rowc = depth * stock.bit_length() + 9909 + 252; assert rowc < 20161
# ---------------- outer assembly for each bit supplier, exactly as #434's combined.py
bits = json.loads(bitsp.read_text()); eta = beta = Q(1, 10 ** 18)
def ceil(x): return -((-x.numerator) // x.denominator)
def bootstrap(s_):
    chn = [Q(384599, 10 ** 10)]
    for j_ in range(6): chn.append((1 - s_) * s_ + s_ * chn[-1])
    q_ = chn[-1] * (1 - 2 * eta); mg = (1 - eta) * q_ / (1 + q_); tk = mg / grid
    return chn, grid * ((tk.numerator - 1) // tk.denominator)
results = []
for sup in bits:
    c = Q(sup['c']); two_bits = int(sup['charged_two_level_coefficient_bits']); row = int(sup['row_coefficient']); ALLOW = max(20161, row, rowc)
    s = min(c, (1 - beta) * b) - Q(1, 10 ** 24); assert 0 < s < c and s < (1 - beta) * b
    chain = [Q(384599, 10 ** 10)]; cutoffs = []
    for j in range(6):
        old = chain[-1]; a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s); assert old < a < s < 1 - a and gap > 0
        cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + two_bits) / gap)); assert cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + two_bits)
        cutoffs.append(dict(gap=str(gap), cutoff_log2=str(cutoff))); chain.append(a)
    q = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * q / (1 + q); ticks = margin / grid; k = grid * ((ticks.numerator - 1) // ticks.denominator)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1}, 'rows': {'degree_gap': Q(10 ** 6) - Q(51 * ALLOW, 25)}}
    a = Outer.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta)
    assert len(a['strict_constraints']) == 47 and all(x > 0 for x in a['strict_constraints'].values())
    controls = []
    for name, kk, ee, bb in [('next_grid', k + grid, eta, beta), ('zero_eta', k, Q(0), beta), ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1))]:
        try: Outer.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
        except AssertionError: controls.append(name)
        else: raise AssertionError(name)
    results.append(dict(label=sup['label'], source=sup.get('source', ''), bit_lower=str(c), kappa=str(k), kappa_decimal=format(float(k), '.18f'),
                        binding_component='bit' if c < (1 - beta) * b else 'complex', external_row_allowance=ALLOW,
                        strict_outer_constraints={n: str(x) for n, x in a['strict_constraints'].items()}, outer_controls=controls, bootstrap=cutoffs))
# kappa the complex supplier alone supports (a hypothetical bit supplier that does not bind)
c_hyp = b / (1 - beta) + Q(1, 10 ** 24); s_cx = min(c_hyp, (1 - beta) * b) - Q(1, 10 ** 24)
_, k_cx = bootstrap(s_cx)
res = dict(status='PASS_COMPLEX_GAUGE_KERNEL_CERTIFICATION', complex_lower=str(b), complex_decimal=format(float(b), '.18f'),
           complex_cap_kappa=str(k_cx), complex_cap_kappa_decimal=format(float(k_cx), '.18f'),
           complex=dict(live=WC, physical=physc, maxchild=max(PC), rank_mass=massc, hosted_residuals=audit['complex_hosted_residuals'],
                        physical_stock_bits=stock.bit_length(), router_bits=router.bit_length(), literal_bits=literal.bit_length(), row_coefficient=rowc,
                        pervertex_bits=pervertex.bit_length()),
           suppliers=results, complex_template_sha256=ch['template_sha256'], widths=audit['widths'])
outp.write_text(json.dumps(res, indent=2) + '\n')
print(res['status'], 'b', res['complex_decimal'], 'complex-cap kappa', res['complex_cap_kappa_decimal'])
for r_ in results: print('  ', r_['label'], 'kappa', r_['kappa_decimal'], 'binding', r_['binding_component'], 'controls', r_['outer_controls'])
