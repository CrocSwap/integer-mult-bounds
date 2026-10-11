"""Exact assembly, adapted from #494's assemble_489.py (higherbeing; Apache-2.0): #493's R489 bit supplier (unchanged,
eleven-stage whole-residual hosting priced by #472's invoice) with a NEW hosted complex supplier, priced by #442's
finite invoice applied to the new word's own INTEGRATION.json and hosted stock; six bootstrap levels and the 47 strict
outer inequalities.  The only changes from assemble_489.py: the complex word directory and its parameters are
arguments, the deficit is an explicit argument instead of the literal 2496, and the result names #494 as reference.
usage: assemble_complex.py PR493_OUT PR493_PACKAGE UPSTREAM442_OUT WORD_DIR COMPLEX_DIR COMPLEX_AUDIT.json OUT.json
                           [--m 73] [--deficit 2496] [--status NAME] [--interface TEXT]
WORD_DIR holds the new word's INTEGRATION.json (finite_invoice, physical, live); COMPLEX_DIR holds HOSTED.json."""
import gzip, hashlib, importlib.util, json, math, sys
from fractions import Fraction as Q
from pathlib import Path
import argparse
ap = argparse.ArgumentParser()
for x in ('w493', 'pkg', 'up442', 'wd', 'cd', 'cap', 'outp'): ap.add_argument(x, type=Path)
ap.add_argument('--m', type=int, default=73); ap.add_argument('--deficit', type=int, default=2496)
ap.add_argument('--status', default='PASS_CONDITIONAL_R489_BIT_WITH_NEW_COMPLEX_ASSEMBLY')
ap.add_argument('--interface', default='complex side: PR442 idle-data hosting with PR448 cross-copy slots; bit side: whole-residual hosting only')
A = ap.parse_args()
w493, pkg, up442, wd, cd, cap, outp = A.w493, A.pkg, A.up442, A.wd, A.cd, A.cap, A.outp
bd = w493 / 'bit'
sys.path.insert(0, str(pkg / 'code/hub/r740-hosted-eleven/code'))
from row_bound import bound as row_bound, controls as row_controls
eng = pkg / 'code/hub/e8-r740-replica32/code/engines'
def load(name):
    sp = importlib.util.spec_from_file_location('hosted_' + name, eng / (name + '.py'))
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod
M, Other, Outer = load('moment'), load('base_two_moment'), load('outer')
audit = json.loads((bd / 'AUDIT.json').read_text()); bg = json.loads((bd / 'GLOBAL.json').read_text()); caud = json.loads(cap.read_text()); ch = json.loads((cd / 'HOSTED.json').read_text())
assert audit['template_sha256'] == bg['template_sha256'] and caud['complex_template_sha256'] == ch['template_sha256']
r493 = json.loads((w493 / 'RESULT.json').read_text())
assert json.loads((up442 / 'RECEIPT.json').read_text())['status'] == 'PASS_FULL_IDLE_AXIS_HOSTING_COMPOSITION'
# ---------------- bit: #472's eleven-stage invoice with R = 489 (exactly #493's code/eleven/assemble.py bit half)
P = {int(r): n for r, n in audit['profile'].items()}; m, W = 78, audit['live']; E = sum(P.values())
geo = json.loads((bd / 'GEOMETRY.json').read_text()); pg = bg
T, L, R, V, K = 8, 11, 489, 120, 5
assert pg['replicas'] == T and pg['R'] == R
mass = sum(r * z for r, z in P.items()); assert m * W - mass == (2 * K * V - L * 72) * T
physical = W + 9; d = m * m; N = 2 * m
unit = L * T * pg['local_additions'] + pg['bridge_additions']
J = 8 * T * L * (2 * V + R) + 8 * (2 * K * V * T) + 2 * L * T * R + 2 * pg['copy_erase_episodes']
high = 16 * (d + 1) ** 2; good = 8 * m * m + 8; compiler = 128 * N ** 3
selectors = 2 * L * T * ((W - 1) + R * m * (geo['max_route_factors'] + 144 + 2 + (m - 1) + m))
prefix = int(pg['global_prefix_bound']); charged_prefix = 64 * ((prefix.bit_length() + 63) // 64)
assert prefix < 1 << charged_prefix and charged_prefix == pg['charged_prefix_bits'] and audit['physical_prefix_bits'] == prefix.bit_length()
coefficient = unit + J * high + J * physical + E * (good + compiler) + 16 * m ** 3 + pg['copy_erase_episodes'] + selectors + prefix + 1
two = (coefficient + 1) ** 3 * (E + 1) ** 3; charged_two = 64 * ((two.bit_length() + 63) // 64)
assert two < 1 << charged_two and 2 * max(P) ** 3 < m ** 3
assert coefficient < 1 << 100000 and 32 * m * (coefficient + 1) ** 2 < 1 << 210000
rows = row_bound(m, physical, max(P), 3); row = rows['complete_row_coefficient']; assert row < 20161
row_rejected = row_controls()
root = M.certify(P, m, W, True); c = Q(root['lower']); chi = Q(root['upper'])
assert c == Q(r493['bit_lower']), ('bit root differs from #493', str(c), r493['bit_lower'])
fb = 32 * m * m * E
lo, hi = Other.moment(m, W, list(P.items()), c); bl, bh = Other.moment(m, W, [(1, fb)], c); assert hi + bh / 10 ** 16 < 1
lo2, hi2 = Other.moment(m, W, list(P.items()), chi); bl2, bh2 = Other.moment(m, W, [(1, fb)], chi); assert lo2 + bl2 / 10 ** 16 > 1
# ---------------- complex: the new hosted word, #442's invoice with the new word's integration and hosted stock
PC = {int(r): n for r, n in caud['complex_profile'].items()}; mc, WC = A.m, caud['complex_live']; EC = sum(PC.values())
massc = sum(r * z for r, z in PC.items()); assert mc * WC - massc == A.deficit, ('deficit', mc * WC - massc)
rc = M.certify(PC, mc, WC, True); b = Q(int(Q(rc['lower']) * 10 ** 18), 10 ** 18)
fbc = 32 * mc * mc * EC
l3, h3 = Other.moment(mc, WC, list(PC.items()), b); b3, bh3 = Other.moment(mc, WC, [(1, fbc)], b); assert h3 + bh3 / 10 ** 16 < 1
integ = json.loads((wd / 'INTEGRATION.json').read_text()); inv = integ['finite_invoice']
physc = ch['physical']; compilerc = 64 * (mc + 1) ** 3
pervertex = inv['pervertex'] - integ['physical'] * (64 + 1) + physc * (64 + 1) - integ['live'] + WC
r_ = mc // 2; group = 2 ** (r_ * r_) * math.prod(2 ** (2 * i) - 1 for i in range(1, r_ + 1)); stock = group * physc
smass = group * massc; logical = group * max(pervertex, inv['pervertex']) + 64; router = compilerc * (logical + 1) * (stock + 1) ** 2
GG, EE, C0 = 1 << 30000, 1 << 100000, 1 << 210000; BB = smass + EE
literal = 2 * GG * stock ** 2 + 8 * smass + 4 * stock + 4 + 32 * mc
assert logical < 1 << 6050 and router < GG and literal < EE and BB < 1 << 100001 and 32 * mc * BB * BB < C0 and 2 * BB + 18 < C0
depth = 2; assert mc ** depth > 2 * max(PC) ** depth
rowc = depth * stock.bit_length() + 9909 + 252; assert rowc < 20161
# ---------------- outer assembly exactly as #434's combined.py
eta = beta = Q(1, 10 ** 18); grid = Q(1, 10 ** 18); s = min(c, (1 - beta) * b) - Q(1, 10 ** 24)
assert 0 < s < c and s < (1 - beta) * b
chain = [Q(384599, 10 ** 10)]; cutoffs = []
def ceil(x): return -((-x.numerator) // x.denominator)
for j in range(6):
    old = chain[-1]; a = (1 - s) * s + s * old
    gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s); assert old < a < s < 1 - a and gap > 0
    cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + charged_two) / gap)); assert cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + charged_two)
    cutoffs.append(dict(gap=str(gap), cutoff_log2=str(cutoff))); chain.append(a)
q = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * q / (1 + q); ticks = margin / grid; k = grid * ((ticks.numerator - 1) // ticks.denominator)
bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1}, 'rows': {'degree_gap': Q(10 ** 6) - Q(51 * 20161, 25)}}
a = Outer.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta)
assert len(a['strict_constraints']) == 47 and all(x > 0 for x in a['strict_constraints'].values())
controls = []
for name, kk, ee, bb in [('next_grid', k + grid, eta, beta), ('zero_eta', k, Q(0), beta), ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1))]:
    try: Outer.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
    except AssertionError: controls.append(name)
    else: raise AssertionError(name)
ref = Q(358867191156973, 250000000000000000)  # #494
res = dict(status=A.status, kappa=str(k), kappa_decimal=format(float(k), '.18f'),
           bit_lower=str(c), complex_lower=str(b), binding_component='bit' if c < (1 - beta) * b else 'complex',
           kappa_pr493_with_pr471=r493['kappa']['pr471']['kappa'], kappa_pr493_information_only_with_pr448=r493['kappa']['pr448']['kappa'],
           bit=dict(live=W, physical=physical, maxchild=max(P), rank_mass=mass, hosted_residuals=audit['hosted_residuals'], prefix_bits=prefix.bit_length(),
                    charged_prefix_bits=charged_prefix, coefficient_bits=coefficient.bit_length(), three_level_coefficient_bits=two.bit_length(),
                    charged_three_level_coefficient_bits=charged_two, row_coefficient=row, row_controls_rejected=row_rejected),
           complex=dict(live=WC, physical=physc, maxchild=max(PC), rank_mass=massc, hosted_residuals=caud['complex_hosted_residuals'], split_residuals=caud['complex_split_residuals'],
                        physical_stock_bits=stock.bit_length(), router_bits=router.bit_length(), literal_bits=literal.bit_length(), row_coefficient=rowc),
           strict_outer_constraints={n: str(x) for n, x in a['strict_constraints'].items()}, outer_controls=controls, bootstrap=cutoffs,
           bit_template_sha256=bg['template_sha256'], complex_template_sha256=ch['template_sha256'], emitted_program_sha256=bg['emitted_program_sha256'],
           reference_pr494_kappa=str(ref), above_pr494=k > ref, gain_over_pr494_percent=format(float(100 * (k / ref - 1)), '.6f'),
           complex_deficit=A.deficit, complex_m=mc, additional_interface=A.interface)
outp.write_text(json.dumps(res, indent=2) + '\n')
print(res['status'], res['kappa_decimal'], 'binding', res['binding_component'])
