# Adapted from DaysSky PR442 with Claude assistance; Eleven-stage R740 integration by chafreaky with OpenAI Codex. Apache-2.0.
"""Two exact moments for both hosted suppliers, fresh finite invoices with the hosted stock, and the strict outer
assembly of #434 (six bootstrap levels, 47 inequalities, next-grid and parameter controls).
usage: assemble.py VERIFIED458_DIR BIT_DIR"""
import gzip, hashlib, importlib.util, json, math, sys
from fractions import Fraction as Q
from pathlib import Path
parent458, bd = map(Path, sys.argv[1:3])
parent454=parent458/"parent454"
cd=parent458/"complex"
parent451=parent454/"parent451"
parent445=parent451/"parent445"
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"r740-hosted-rank149/code"))
parent444=parent445/"parent444"
upstream=parent444/"upstream442"
ap=bd/"AUDIT.json";outp=bd/"RESULT.json"
from row_bound import bound as row_bound, controls as row_controls
par=upstream / "parent/changed"

def load(name):
    sp = importlib.util.spec_from_file_location('hosted_' + name, par / 'work/pr361/code/engines' / (name + '.py'))
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod
M, Other, Outer = load('moment'), load('base_two_moment'), load('outer')
audit = json.loads(ap.read_text()); ua=json.loads((upstream/'AUDIT.json').read_text()); ur=json.loads((upstream/'RESULT.json').read_text()); bg = json.loads((bd / 'GLOBAL.json').read_text()); ch = json.loads((cd / 'GLOBAL.json').read_text()); ca=json.loads((cd/'AUDIT.json').read_text())
assert audit['template_sha256'] == bg['template_sha256'] and ca['template_sha256'] == ch['template_sha256']
assert json.loads((upstream/'RECEIPT.json').read_text())['status']=='PASS_FULL_IDLE_AXIS_HOSTING_COMPOSITION'
# ---------------- bit: two moments and the parent's invoice formulas with the hosted stock
P = {int(r): n for r, n in audit['profile'].items()}; m, W = 78, audit['live']; E = sum(P.values())
geo = json.loads((bd / 'GEOMETRY.json').read_text());pg=bg
T, L, R, V, K = 8, 11, 715, 120, 5
assert pg["replicas"]==T and pg["R"]==R
mass = sum(r * z for r, z in P.items()); assert m * W - mass == (2*K*V-L*72)*T
physical = W + 9; d = m * m; N = 2 * m
unit = L * T * pg['local_additions'] + pg['bridge_additions']
J = 8 * T * L * (2 * V + R) + 8 * (2 * K * V * T) + 2 * L * T * R + 2 * pg['copy_erase_episodes']   # every helper route charged (bank or hosted)
high = 16 * (d + 1) ** 2; good = 8 * m * m + 8; compiler = 128 * N ** 3
selectors = 2 * L * T * ((W - 1) + R * m * (geo['max_route_factors'] + 144 + 2 + (m - 1) + m))   # 144: residual isometry; +2: hosted slot permutation and idle basis U_q
prefix = int(pg['global_prefix_bound']); charged_prefix = 64 * ((prefix.bit_length() + 63) // 64)
assert prefix < 1<<charged_prefix and charged_prefix==pg['charged_prefix_bits']
assert audit['physical_prefix_bits']==prefix.bit_length()
coefficient = unit + J * high + J * physical + E * (good + compiler) + 16 * m ** 3 + pg['copy_erase_episodes'] + selectors + prefix + 1
two = (coefficient + 1) ** 3 * (E + 1) ** 3; charged_two = 64*((two.bit_length()+63)//64)
assert two < 1 << charged_two and 2 * max(P) ** 3 < m ** 3
assert coefficient < 1<<100000 and 32*m*(coefficient+1)**2 < 1<<210000
rows = row_bound(m,physical,max(P),3);row=rows["complete_row_coefficient"]
assert row==19431<20161
row_rejected=row_controls()
root = M.certify(P, m, W, True); c = Q(root['lower']); chi = Q(root['upper'])
fb = 32 * m * m * E
lo, hi = Other.moment(m, W, list(P.items()), c); bl, bh = Other.moment(m, W, [(1, fb)], c); assert hi + bh / 10 ** 16 < 1
lo2, hi2 = Other.moment(m, W, list(P.items()), chi); bl2, bh2 = Other.moment(m, W, [(1, fb)], chi); assert lo2 + bl2 / 10 ** 16 > 1
# ---------------- complex: two moments and the parent's invoice with the hosted stock
PC = {int(r): n for r, n in ca['profile'].items()}; mc, WC = 89, ca['live']; EC = sum(PC.values())
massc = sum(r * z for r, z in PC.items()); assert mc * WC - massc == 3264
rc = M.certify(PC, mc, WC, True); b = Q(rc['lower'])
assert b>Q(ur['complex_lower'])
fbc = 32 * mc * mc * EC
l3, h3 = Other.moment(mc, WC, list(PC.items()), b); b3, bh3 = Other.moment(mc, WC, [(1, fbc)], b); assert h3 + bh3 / 10 ** 16 < 1
bn=Q(rc['upper'])
l4,h4=Other.moment(mc,WC,list(PC.items()),bn);b4,bh4=Other.moment(mc,WC,[(1,fbc)],bn);assert l4+b4/10**16>1
physc=ch['physical'];Rc=560;v=120;hc=9;lc=11;tc=8;kc=5
checks=ch['source_local_checks'];private_centers=ch['private_centers']
compilerc=64*(mc+1)**3
macros=max(z['scalar_macros'] for z in checks.values());children=sum(checks['forward']['paid_profile'].values())
adapters=16*(macros+children+2*v+Rc+private_centers)+64*mc
# Eight restored rank-zero compiler groups for EACH pre/post wrapper,
# conservatively charged for all R helpers rather than only the 79 pivots.
wrapper_groups=2*Rc*8
assert ch['charged_wrapper_groups']==lc*tc*wrapper_groups and ch['wrapper_events']==lc*tc*158
adapters+=wrapper_groups
local_bound=max(z['real_component_primitive_bound'] for z in checks.values())+adapters*compilerc
scalar_primitives=tc*((kc+1)*checks['forward']['real_component_primitive_bound']+kc*checks['backward']['real_component_primitive_bound'])
bridge_adds=6*(kc-1)*v*tc;terminal_shifts=kc*v*tc;terminal_moves=2*kc*v*tc
# Retain the full unhosted idle count as an overcharge, and charge all helper
# selectors plus two additional hosting factors per helper occurrence.
nonlocal_items=4*v*tc*lc+2*v*tc*lc+4*lc*tc*Rc+(6*kc-4)*v*tc+bridge_adds+terminal_shifts+terminal_moves+WC+physc
outside=8*nonlocal_items+64*mc
pervertex=scalar_primitives+bridge_adds+terminal_shifts+terminal_moves+WC+(lc*tc*adapters+outside)*compilerc+64*physc
r_ = mc // 2; group = 2 ** (r_ * r_) * math.prod(2 ** (2 * i) - 1 for i in range(1, r_ + 1)); stock = group * physc
smass=group*massc;logical=group*pervertex+64;router=compilerc*(logical+1)*(stock+1)**2
GG, EE, C0 = 1 << 30000, 1 << 100000, 1 << 210000; BB = smass + EE
literal = 2 * GG * stock ** 2 + 8 * smass + 4 * stock + 4 + 32 * mc
assert local_bound<1<<48 and logical<1<<6050 and router<GG and literal<EE and BB<1<<100001 and 32*mc*BB*BB<C0 and 2*BB+18<C0
assert mc**2<=2*max(PC)**2 and mc**3>2*max(PC)**3
assert (pervertex+1)**3*(EC+1)**3<1<<1024
from complex_rows import bound as complex_row_bound, controls as complex_row_controls
complex_rows=complex_row_bound(stock.bit_length());complex_row_rejected=complex_row_controls()
rowc=complex_rows['retained_row_coefficient']
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
parent_k = Q(json.loads((parent458/'RESULT.json').read_text())['kappa'])
assert json.loads((parent444/'RECEIPT.json').read_text())['status']=='PASS_R740_REPLICATED_HOSTING'
res = dict(status='PASS_CONDITIONAL_R715_WHOLE_HOSTED', kappa=str(k), kappa_decimal=format(float(k), '.18f'),
           bit_lower=str(c), complex_lower=str(b), binding_component='bit' if c < (1 - beta) * b else 'complex',
           gain_over_pr458_percent=float(100 * (k / parent_k - 1)),
           bit=dict(live=W, physical=physical, maxchild=max(P), rank_mass=mass, hosted_residuals=audit['hosted_residuals'],
                    prefix_bits=prefix.bit_length(), charged_prefix_bits=charged_prefix, coefficient_bits=coefficient.bit_length(),
                    three_level_coefficient_bits=two.bit_length(), charged_three_level_coefficient_bits=charged_two, row_coefficient=row),
           complex=dict(live=WC, physical=physc, maxchild=max(PC), rank_mass=massc, hosted_residuals=ca['hosted_residuals'],
                        wrapper_events=ch['wrapper_events'], charged_wrapper_groups=ch['charged_wrapper_groups'], max_helpers_per_physical_family_per_call=1, physical_stock_bits=stock.bit_length(), router_bits=router.bit_length(), literal_bits=literal.bit_length(), row_coefficient=rowc, row_bound=complex_rows, row_controls=complex_row_rejected, local_bound=local_bound, pervertex=pervertex, halving_depth=3),
           strict_outer_constraints={n: str(x) for n, x in a['strict_constraints'].items()}, outer_controls=controls, bootstrap=cutoffs,
           bit_template_sha256=bg['template_sha256'], complex_template_sha256=ch['template_sha256'], complex_emitted_program_sha256=ch['emitted_program_sha256'], emitted_program_sha256=bg['emitted_program_sha256'], bank_assignments=audit['bank_assignments'], bit_profile=audit['profile'], parent_kappa=str(parent_k), additional_interface='Explicit paid two-sided residual adapters; distinct borrowed host families within every invocation; inherited Gaussian compiler and idle-data hosting',row_bound=rows,row_controls=row_rejected, halving_depth=3, finite_controls=['physical family prefix independently recomputed','three-level coefficient charged to next 64-bit block'])
outp.write_text(json.dumps(res, indent=2) + '\n')
print(res['status'], res['kappa_decimal'], 'binding', res['binding_component'], 'gain over #458 %.4f%%' % res['gain_over_pr458_percent'])
