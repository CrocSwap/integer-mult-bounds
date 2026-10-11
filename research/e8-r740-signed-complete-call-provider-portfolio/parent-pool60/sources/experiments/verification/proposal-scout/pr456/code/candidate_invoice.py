# Adapted from DaysSky PR442 and chafreaky PR451/454; Apache-2.0.
# Whole-replica composition by Rohan Arun with OpenAI Codex assistance.
"""Reprice changed whole7 complex supplier, reuse pinned unchanged bit invoice.
Usage: candidate_invoice.py COMPLEX_DIR RESEARCH_ROOT [FULL_PARENT454_OUTPUT]
No third argument means a cited pinned bit supplier, distinctly labeled.
"""
from pathlib import Path
from fractions import Fraction as Q
import sys,json,math,importlib.util
cd,research=map(Path,sys.argv[1:3]);read=lambda p:json.loads(p.read_text())
anchor=read(research/'e8-target-mixing-whole/EXPECTED.json')
mode='CITED_PINNED_PR454_BIT'
if len(sys.argv)>3:
 parent=Path(sys.argv[3]);receipt=read(parent/'RECEIPT.json');actual=read(parent/'RESULT.json')
 assert receipt['status']=='PASS_TARGET_MIXING_WHOLE_HOSTING' and receipt['mode']=='full'
 for key,val in anchor.items():assert actual[key]==val,(key,actual[key],val)
 mode='FULL_PR454_REPLAY'
def load(name):
 spec=importlib.util.spec_from_file_location(name,research/'e8-r740-replica32/code/engines'/(name+'.py'))
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
M,Other,Outer=load('moment'),load('base_two_moment'),load('outer')
sys.path.insert(0,str(research/'r740-hosted-rank149/code'))
# Recheck both exact moment engines for the cited unchanged bit profile.
P={int(r):n for r,n in anchor['bit_profile'].items()};m=78;W=anchor['bit']['live']
cert=M.certify(P,m,W,True);c=Q(cert['lower']);assert c==Q(anchor['bit_lower'])
for x,below in [(c,True),(Q(cert['upper']),False)]:
 l,h=Other.moment(m,W,list(P.items()),x);ll,hh=Other.moment(m,W,[(1,32*m*m*sum(P.values()))],x)
 assert (h+hh/10**16<1) if below else (l+ll/10**16>1)
charged_two=anchor['bit']['charged_three_level_coefficient_bits']
ch=read(cd/'GLOBAL.json');ca=read(cd/'AUDIT.json')
assert ca['status']=='PASS_INDEPENDENT_WHOLE_REPLICA7_COMPLEX_AUDIT'
assert ch['template_sha256']==ca['template_sha256'] and ch['emitted_program_sha256']==ca['emitted_program_sha256']
# ---------------- complex: two moments and the parent's invoice with the hosted stock
PC = {int(r): n for r, n in ca['profile'].items()}; mc, WC = 89, ca['live']; EC = sum(PC.values())
massc = sum(r * z for r, z in PC.items()); assert mc * WC - massc == 408*ch["replicas"]
rc = M.certify(PC, mc, WC, True); b = Q(rc['lower'])
assert b>Q(anchor['complex_lower'])
fbc = 32 * mc * mc * EC
l3, h3 = Other.moment(mc, WC, list(PC.items()), b); b3, bh3 = Other.moment(mc, WC, [(1, fbc)], b); assert h3 + bh3 / 10 ** 16 < 1
bn=Q(rc['upper'])
l4,h4=Other.moment(mc,WC,list(PC.items()),bn);b4,bh4=Other.moment(mc,WC,[(1,fbc)],bn);assert l4+b4/10**16>1
physc=ch['physical'];Rc=560;v=120;hc=9;lc=11;tc=ch["replicas"];kc=5
assert tc==7 and WC==8400 and physc==8978
checks=ch['source_local_checks'];private_centers=ch['private_centers']
compilerc=64*(mc+1)**3
macros=max(z['scalar_macros'] for z in checks.values());children=sum(checks['forward']['paid_profile'].values())
adapters=16*(macros+children+2*v+Rc+private_centers)+64*mc
local_bound=max(z['real_component_primitive_bound'] for z in checks.values())+adapters*compilerc
scalar_primitives=tc*((kc+1)*checks['forward']['real_component_primitive_bound']+kc*checks['backward']['real_component_primitive_bound'])
bridge_adds=6*(kc-1)*v*tc;terminal_shifts=kc*v*tc;terminal_moves=2*kc*v*tc
# Retain the full unhosted idle count as an overcharge, and charge all helper
# selectors plus two additional hosting factors per helper occurrence.
nonlocal_items=4*v*tc*lc+2*v*tc*lc+6*lc*tc*Rc+(6*kc-4)*v*tc+bridge_adds+terminal_shifts+terminal_moves+WC+physc
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

parent_k=Q(anchor['kappa']);assert k>parent_k
result=dict(status='PASS_WHOLE_REPLICA7_COMPONENT_INVOICE_AND_OUTER',bit_supplier_mode=mode,
 kappa=str(k),kappa_decimal=format(float(k),'.18f'),bit_lower=str(c),complex_lower=str(b),binding_component='complex',
 gain_over_pr454_percent=float((k/parent_k-1)*100),complex_template_sha256=ch['template_sha256'],
 emitted_program_sha256=ch['emitted_program_sha256'],profile=ca['profile'],
 complex=dict(live=WC,physical=physc,maxchild=max(PC),physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),pervertex=pervertex,local_bound=local_bound,row_bound=complex_rows,halving_depth=3,three_level_coefficient_bits=((pervertex+1)**3*(EC+1)**3).bit_length(),charged_three_level_coefficient_bits=1024),
 strict_outer_constraints={n:str(x) for n,x in a['strict_constraints'].items()},outer_controls=controls,bootstrap=cutoffs,
 scope='Whole rank9 residuals on single physical families; owner replica may differ. Retains PR442 complete-call and all inherited compiler/analytic contracts.')
(cd/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal'],mode,flush=True)
