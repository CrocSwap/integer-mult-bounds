from pathlib import Path
import json,math,hashlib
P=Path(__file__).resolve().parent
ch=json.load(open(P/'hosted/GLOBAL.json'));ca=json.load(open(P/'hosted/AUDIT.json'))
assert ca['status']=='PASS_INDEPENDENT_COMPLEX_ELEVEN_AUDIT' and ca['template_sha256']==ch['template_sha256']
geometry=json.load(open(P/'geometry-audit/HOSTED-SIGMA.json'));assert geometry['status'].startswith('PASS')
prefix=json.load(open(P/'PREFIX.json'));assert prefix['conservative_bound_bits']<prefix['charged_prefix_bits']==512
PC={int(r):n for r,n in ca['profile'].items()};mc,WC=89,ca['live'];EC=sum(PC.values());massc=sum(r*n for r,n in PC.items())
physc=ch['physical'];Rc=560;v=120;hc=9;lc=11;tc=8;kc=5
checks=ch['source_local_checks'];private_centers=ch['private_centers']
compilerc=64*(mc+1)**3
macros=max(z['scalar_macros'] for z in checks.values());children=sum(checks['forward']['paid_profile'].values())
adapters=16*(macros+children+2*v+Rc+private_centers)+64*mc
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

result=dict(status='PASS_FRESH_COMBINED_DIRECT8_ELEVEN_FINITE_INVOICE',charged_prefix_bits=512,conservative_prefix_bits=prefix['conservative_bound_bits'],m=mc,live=WC,physical=physc,local_bound=local_bound,adapters=adapters,scalar_primitives=scalar_primitives,pervertex=pervertex,physical_stock_bits=stock.bit_length(),logical_bits=logical.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),precision_guard_bits=(32*mc*BB*BB).bit_length(),row_bound=complex_rows,row_controls=complex_row_rejected,profile=PC,rank_mass=massc,deficit=mc*WC-massc,compiler=compilerc,halving_depth=3,coefficient_envelope_bits=((pervertex+1)**3*(EC+1)**3).bit_length(),geometry_sha256=hashlib.sha256((P/'geometry-audit/HOSTED-SIGMA.json').read_bytes()).hexdigest(),primitive_replay_sha256=hashlib.sha256((P/'PRIMITIVE-REVIEW.json').read_bytes()).hexdigest(),source_audit_sha256=hashlib.sha256((P/'hosted/AUDIT.json').read_bytes()).hexdigest(),scope='Retains inherited all-size ADDRESS compiler, prime/common-grid, precision/tape and analytic obligations. Fresh local all800 dirty theorem and exact selected whole-helper geometry must pass separately.')
(P/'FINITE-INVOICE.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items()if k not in ('profile','row_bound')})
