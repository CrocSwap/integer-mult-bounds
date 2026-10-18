# GL-cover and sharp-fallback variant by OpenAI Codex; source provenance retained below.
# Adapted from DaysSky PR442 with Claude assistance; R740 integration by chafreaky with OpenAI Codex. Apache-2.0.
# Generalised to an arbitrary odd stage count, halving depth D and an enlarged external row allowance by DreamingOfClouds
# with Claude Opus 5.5 (Anthropic), via Claude Code.  At the nine-stage defaults (D = 2, allowance 20161) every value
# equals PR #444's assemble.py.
"""Two exact moments for both hosted suppliers, fresh finite invoices with the hosted stock, and the strict outer
assembly of #434 (six bootstrap levels, 47 inequalities, next-grid and parameter controls).
usage: assemble_k.py PARENT_CANDIDATE VERIFIED_COMPLEX_DIR BIT_DIR AUDIT.json OUT.json [--parent-kappa FRACTION] [--label TEXT] [--route-extra N]"""
import gzip, hashlib, importlib.util, json, math, sys
from fractions import Fraction as Q
from pathlib import Path
argv = [x for x in sys.argv[1:] if not x.startswith('--')]
opt = {sys.argv[i]: sys.argv[i + 1] for i in range(1, len(sys.argv) - 1) if sys.argv[i].startswith('--')}
for k_, v_ in opt.items(): argv.remove(v_)
base, bd, ap, outp = map(Path, argv[:4])
root = Path(__file__).resolve().parent
engines=Path(opt.get('--engines',str(root/'source/upstream478/engines')))
receipt_dir=Path(opt.get('--inherited',str(root/'source/upstream478/inherited')))
def load(name):
 sp=importlib.util.spec_from_file_location('weave_'+name,engines/(name+'.py'))
 mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
M,Other,Outer=load('moment'),load('base_two_moment'),load('outer')
audit=json.loads(ap.read_text());bg=json.loads((bd/'GLOBAL.json').read_text())
prior=json.loads((receipt_dir/'ASSEMBLY.json').read_text());expected=json.loads((receipt_dir/'EXPECTED.json').read_text())
assert prior['kappa']==expected['kappa']
assert audit['template_sha256']==bg['template_sha256']
cd=Path(opt['--complex']);ch=json.loads((cd/'GLOBAL.json').read_text());ca=json.loads((cd/'AUDIT.json').read_text())
assert ch['template_sha256']==ca['template_sha256']
# ---------------- bit: two moments and the parent's invoice formulas with the hosted stock
P = {int(r): n for r, n in audit['profile'].items()}; m, W = bg['m'], audit['live']; E = sum(P.values())
NINE = opt.get('--nine', 'nine')
geo = json.loads((base / NINE / 'GEOMETRY.json').read_text())
pg = json.loads((base / NINE / 'GLOBAL.json').read_text())
T, R, V = pg['replicas'], pg['R'], 120; L = (m - 1) // 7; K = (L - 1) // 2; assert L % 2 == 1 and m == 1 + 7 * L
RES_ISO = int(opt.get('--residual-isometry', 144))   # 144 for PR #443's explicit residual isometries, 0 for the R747 word of PR #434/#448
ROUTE_EXTRA = int(opt.get('--route-extra', 5))   # 2: hosted slot permutation and U_q; 3 with a cross-copy split (PR #448)
DEPTH = bg['halving_depth']; DEFICIT = T * (2 * K * V - 9 * 8 * L)
assert bg['m'] == m and bg['replicas'] == T and bg['R'] == R and bg['deficit'] == DEFICIT
mass = sum(r * z for r, z in P.items()); assert m * W - mass == DEFICIT
physical = W + 9; d = m * m; N = 2 * m
unit = L*T*max([pg['local_additions']]+[json.loads(Path(p).read_text())['local_additions'] for p in opt.get('--variant-globals','').split(';') if p])+pg['bridge_additions']+100000 # charged dispatch/owner-piece encoding overhead
J = 8 * T * L * (2 * V + R) + 8 * (2 * K * V * T) + 2 * L * T * R + 2 * pg['copy_erase_episodes']   # every helper route charged (bank or hosted)
high = 16 * (d + 1) ** 2; good = 8 * m * m + 8; compiler = 128 * N ** 3
selectors = 2 * L * T * ((W - 1) + R * m * (geo['max_route_factors'] + RES_ISO + ROUTE_EXTRA + (m - 1) + m))   # 144: residual isometry; +2: hosted slot permutation and idle basis U_q
# Whole-owner pooling can couple storage across replicas. Charge every complete
# invocation and each scalar bridge separately, without replica-independence shortcuts.
providers=[pg]+[json.loads(Path(p).read_text()) for p in opt.get('--variant-globals','').split(';') if p]
local_norm=max(v['cancellation_free_row_l1'] for g in providers for v in g['local_checks'].values())
prefix=int(bg['global_prefix_bound'])
assert prefix.bit_length()==audit['physical_prefix_bits'] and bg['charged_prefix_bits']==audit['charged_prefix_bits']
charged_prefix=64*((prefix.bit_length()+63)//64)

coefficient = unit + J * high + J * physical + E * (good + compiler) + 16 * m ** 3 + pg['copy_erase_episodes'] + selectors + prefix + 1
two = (coefficient + 1) ** DEPTH * (E + 1) ** DEPTH; charged_two = 512 if two.bit_length() <= 512 else 64 * ((two.bit_length() + 63) // 64)
assert two < 1 << charged_two and 2 * max(P) ** DEPTH < m ** DEPTH
from gl_rows import bound as row_bound, controls as row_controls
rows=row_bound(m,physical,max(P),DEPTH);row=rows['complete_row_coefficient'];ALLOW=28416;row_rejected=row_controls()
from sharp_charge import certify as sharp_certify, charges as sharp_charges
root = sharp_certify(M,P,m,W); c = Q(root['lower']); chi = Q(root['upper'])
fallback_children,bad_fraction=sharp_charges(m)
fb = fallback_children * E
lo, hi = Other.moment(m, W, list(P.items()), c); bl, bh = Other.moment(m, W, [(1, fb)], c); assert hi + bh * bad_fraction < 1
lo2, hi2 = Other.moment(m, W, list(P.items()), chi); bl2, bh2 = Other.moment(m, W, [(1, fb)], chi); assert lo2 + bl2 * bad_fraction > 1
# ---------------- complex: two moments and the parent's invoice with the hosted stock
PC = {int(r): n for r, n in ca['profile'].items()}; mc, WC = 89, ca['live']; EC = sum(PC.values())
massc = sum(r * z for r, z in PC.items()); assert mc * WC - massc == 408 * ch['replicas']
rc = M.certify(PC, mc, WC, True); b = Q(int(Q(rc['lower']) * 10 ** 18), 10 ** 18)
assert b>Q(prior['complex_lower'])
fbc = 32 * mc * mc * EC
l3, h3 = Other.moment(mc, WC, list(PC.items()), b); b3, bh3 = Other.moment(mc, WC, [(1, fbc)], b); assert h3 + bh3 / 10 ** 16 < 1
bn=b+Q(1,10**18)
l4,h4=Other.moment(mc,WC,list(PC.items()),bn);b4,bh4=Other.moment(mc,WC,[(1,fbc)],bn);assert l4+b4/10**16>1
physc=ch['physical'];Rc=560;v=120;hc=9;lc=11;tc=ch['replicas'];kc=5
checks=ch['source_local_checks'];private_centers=ch['private_centers']
compilerc=64*(mc+1)**3
macros=max(z['scalar_macros'] for z in checks.values());children=sum(checks['forward']['paid_profile'].values())
adapters=16*(macros+children+2*v+Rc+private_centers)+64*mc
local_bound=max(z['real_component_primitive_bound'] for z in checks.values())+16*Rc+adapters*compilerc
scalar_primitives=tc*((kc+1)*checks['forward']['real_component_primitive_bound']+kc*checks['backward']['real_component_primitive_bound'])
bridge_adds=6*(kc-1)*v*tc;terminal_shifts=kc*v*tc;terminal_moves=2*kc*v*tc
# Retain the full unhosted idle count as an overcharge, and charge all helper
# selectors plus two additional hosting factors per helper occurrence.
nonlocal_items=4*v*tc*lc+2*v*tc*lc+6*lc*tc*Rc+(6*kc-4)*v*tc+bridge_adds+terminal_shifts+terminal_moves+WC+physc
outside=8*nonlocal_items+64*mc
pervertex=scalar_primitives+bridge_adds+terminal_shifts+terminal_moves+WC+(lc*tc*adapters+outside)*compilerc+64*physc+lc*tc*Rc*16
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
ALLOW=max(ALLOW,rowc)
# ---------------- outer assembly exactly as #434's combined.py
eta = beta = Q(1, 10 ** 18); grid = Q(1, 10 ** 18); s = min(c, (1 - beta) * b) - Q(1, 10 ** 24)
assert 0 < s < c and s < (1 - beta) * b
chain = [Q(384599, 10 ** 10)]; cutoffs = []
def ceil(x): return -((-x.numerator) // x.denominator)
for j in range(6):
    old = chain[-1]; a = (1 - s) * s + s * old
    gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s); assert old < a < s < 1 - a and gap > 0
    cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + charged_two) / gap)); assert cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + charged_two)
    cutoffs.append(dict(gap=str(gap), normalized_local_cutoff_log2=str(cutoff))); chain.append(a)
q = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * q / (1 + q); ticks = margin / grid; k = grid * ((ticks.numerator - 1) // ticks.denominator)
bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1}, 'rows': {'degree_gap': Q(10 ** 6) - Q(51 * ALLOW, 25)}}
a = Outer.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta)
assert len(a['strict_constraints']) == 47 and all(x > 0 for x in a['strict_constraints'].values())
controls = []
for name, kk, ee, bb in [('next_grid', k + grid, eta, beta), ('zero_eta', k, Q(0), beta), ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1))]:
    try: Outer.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
    except AssertionError: controls.append(name)
    else: raise AssertionError(name)
# kappa the bit supplier alone supports: the same bootstrap and strict assembly with a hypothetical complex saving b_hyp that does not bind
def bootstrap(s_):
    ch = [Q(384599, 10 ** 10)]
    for j_ in range(6): ch.append((1 - s_) * s_ + s_ * ch[-1])
    q_ = ch[-1] * (1 - 2 * eta); mg = (1 - eta) * q_ / (1 + q_); tk = mg / grid
    return ch, grid * ((tk.numerator - 1) // tk.denominator)
b_hyp = c / (1 - beta) + Q(1, 10 ** 24); s_bit = min(c, (1 - beta) * b_hyp) - Q(1, 10 ** 24); assert s_bit < c
chain_bit, k_bit = bootstrap(s_bit)
a_bit = Outer.assembly(chain_bit[-1], b_hyp, bridge, k_bit, eta=eta, beta=beta)
assert len(a_bit['strict_constraints']) == 47 and all(x > 0 for x in a_bit['strict_constraints'].values()) and k_bit >= k
try: Outer.assembly(chain_bit[-1], b_hyp, bridge, k_bit + grid, eta=eta, beta=beta)
except AssertionError: pass
else: raise AssertionError('bit-only next grid point accepted')
parent_k = Q(prior['kappa']); ref_k = Q(opt['--parent-kappa']) if '--parent-kappa' in opt else parent_k
res = dict(status='PASS_CONDITIONAL_R740_REPLICATED_HOSTING_ASSEMBLY' if L == 9 else 'PASS_CONDITIONAL_%s_STAGE_HOSTED_ASSEMBLY' % {11: 'ELEVEN', 13: 'THIRTEEN', 7: 'SEVEN', 5: 'FIVE'}[L], kappa=str(k), kappa_decimal=format(float(k), '.18f'),
           bit_lower=str(c), complex_lower=str(b), binding_component='bit' if c < (1 - beta) * b else 'complex',
           gain_over_pr442_percent=float(100 * (k / parent_k - 1)), reference_kappa=str(ref_k), reference_label=opt.get('--label', '#442'), gain_over_reference_percent=float(100 * (k / ref_k - 1)),
           halving_depth=DEPTH, external_row_allowance=ALLOW, bit_only_kappa=str(k_bit), bit_only_kappa_decimal=format(float(k_bit), '.18f'), bit_only_hypothetical_complex_b=str(b_hyp),
           complex_profile=ca['profile'], complex_wrapper_extra_primitives_per_entry=lc*tc*Rc*16, bit=dict(live=W, physical=physical, maxchild=max(P), rank_mass=mass, hosted_residuals=audit['hosted_residuals'],
                    prefix_bits=prefix.bit_length(), charged_prefix_bits=charged_prefix, coefficient_bits=coefficient.bit_length(), prefix_method='Independent emitted physical-family row-L1 recurrence, including every bridge and invocation',
                    two_level_coefficient_bits=two.bit_length(), charged_two_level_coefficient_bits=charged_two, row_coefficient=row),
           complex=dict(live=WC, physical=physc, maxchild=max(PC), rank_mass=massc, hosted_residuals=ch['hosted_residuals'],
                        physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),row_coefficient=rowc,row_bound=complex_rows,local_bound=local_bound,pervertex=pervertex),
           strict_outer_constraints={n: str(x) for n, x in a['strict_constraints'].items()}, outer_controls=controls, bootstrap=cutoffs,
           bit_template_sha256=bg['template_sha256'], complex_template_sha256=ch['template_sha256'], emitted_program_sha256=bg['emitted_program_sha256'], bank_assignments=audit['bank_assignments'], bit_profile=audit['profile'], parent_kappa=str(parent_k), additional_interface='PR442 whole-family hosting; PR450 target-label lemma; full-nine-axis two-sided monomial transport; same-owner borrowed identity spectators; paid active complements; complete invocations',route_extra=ROUTE_EXTRA,dispatch_overhead=100000,bit_cover='GL_78(Z/q^w)',bit_bad_fraction=str(bad_fraction),bit_bad_children=fallback_children,bit_row_bound=rows,bit_row_controls=row_rejected)
# Candidate endpoint is checked against its own source-bound EXPECTED receipt by the wrapper.
assert row==28416 and ALLOW==28416 and charged_two>=512
res['normalized_local_coefficient_bits']=charged_two
res['all_size_GL_routing_coefficient']=f'B_GL is an arbitrary finite nonnegative integer supplied by the retained fixed-GL-routing contract; total charged bits are {charged_two}+B_GL'
res['bootstrap_routing_contract']=[]
for item in cutoffs:
    gap=Q(item['gap'])
    res['bootstrap_routing_contract'].append(dict(gap=str(gap),quadratic_threshold=str(36/gap**2),affine_offset=str(2*(4+charged_two)/gap),affine_slope=str(2/gap),cutoff='ceil(max(quadratic_threshold, affine_offset + affine_slope * B_GL))'))
outp.write_text(json.dumps(res, indent=2) + '\n')
print(res['status'], res['kappa_decimal'], 'binding', res['binding_component'], 'gain over %s %.4f%%' % (res['reference_label'], res['gain_over_reference_percent']))
