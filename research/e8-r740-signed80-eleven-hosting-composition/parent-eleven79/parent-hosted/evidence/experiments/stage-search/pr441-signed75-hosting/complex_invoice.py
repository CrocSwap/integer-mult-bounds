from pathlib import Path
from fractions import Fraction as Q
import json,math,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[2];A=ROOT/'experiments/stage-search/pr433-split/full';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ch=read(P/'complex-hosted/HOSTED.json');ci=read(A/'split-centres/INTEGRATION.json');sig=read(P/'complex-hosted/HOSTED-SIGMA.json');assert sig['status'].startswith('PASS')
mc,WC=73,ch['live'];H={int(r):n for r,n in ch['global_profile'].items()};mass=sum(r*n for r,n in H.items());assert mc*WC-mass==2496 and 2*max(H)**2<mc**2
inv=ci['finite_invoice'];phys=ch['physical'];extra_selectors=2*9*8*560*73*2
pervertex=max(inv['pervertex'],inv['pervertex']-ci['physical']*65+phys*65-ci['live']+WC)+extra_selectors
r_=mc//2;group=2**(r_*r_)*math.prod(2**(2*i)-1 for i in range(1,r_+1));stock=group*phys;smass=group*mass;logical=group*pervertex+64;router=64*(mc+1)**3*(logical+1)*(stock+1)**2
G,E,C0=1<<30000,1<<100000,1<<210000;B=smass+E;literal=2*G*stock**2+8*smass+4*stock+4+32*mc
assert logical<1<<6050 and router<G and literal<E and B<1<<100001 and 32*mc*B*B<C0 and 2*B+18<C0
row=inv['physical_row_coefficient']+4*mc;assert row<20161
result=dict(status='PASS_OWN_FULLPHASE_COMPLEX_HOSTING_CONSERVATIVE_FINITE_INVOICE',extra_selector_factors_per_helper=2,extra_selector_calls=extra_selectors,retained_parent_pervertex=inv['pervertex'],charged_pervertex=pervertex,logical_bits=logical.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),physical_stock_bits=stock.bit_length(),row_coefficient=row,retained_row=20161,G_exponent=30000,E_exponent=100000,C0_exponent=210000,parent_fullphase_invoice_sha256=sha(A/'split-centres/INTEGRATION.json'),operator_sigma_sha256=sha(P/'complex-hosted/HOSTED-SIGMA.json'),hosted_template_sha256=ch['template_sha256'],scope='Full-phase signed complex local programs remain unchanged, hosted exact operator and all-character phase identity independently checked; retains parent larger per-vertex upper bill and additionally charges two route selector factors per every helper.')
(P/'complex-hosted/FINITE-INVOICE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(result['status'],row)
