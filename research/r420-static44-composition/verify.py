"""Exact two-supplier composition; unchanged physical operators are cited dependencies.
Prepared for Rohan Arun with OpenAI Codex assistance. Original engine notices retained.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
import sys,json,hashlib,importlib.util
if not __debug__:raise RuntimeError('Assertions required')
P=Path(__file__).resolve().parent;out=Path(sys.argv[1]).resolve();assert not out.exists()and not out.is_relative_to(P)
def read(p):return json.loads(p.read_text())
manifest=read(P/'MANIFEST.json');assert manifest=={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in P.rglob('*')if f.is_file()and f!=P/'MANIFEST.json'and '__pycache__'not in f.parts}
def load(n):
 s=importlib.util.spec_from_file_location(n,P/'engines'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,B,A=[load(n)for n in ['moment','base_two_moment','outer']];bit=read(P/'inputs/PR543-EXPECTED.json')['nine'];cp=read(P/'inputs/PR548-EXPECTED.json');c=Q(bit['bit_lower']);b=Q(cp['complex_lower']);receipts=[]
owner=read(P/'inputs/PR548-OWNERS.json');invoice=read(P/'inputs/PR548-INVOICE.json')
assert owner['paid_profile']==cp['complex_global_profile'] and owner['template_sha256']==invoice['template_sha256']==cp['complex_template_sha256']
assert hashlib.sha256((P/'inputs/PR548-OWNERS.json').read_bytes()).hexdigest()==invoice['owner_audit_sha256']
assert all(invoice['strict_checks'].values()) and invoice['finite']['physical_row_coefficient']<20161
for side,H,m,W,lower,deficit in [('bit',{int(r):n for r,n in bit['profile'].items()},64,bit['bit']['live'],c,9984),('complex',{int(r):n for r,n in cp['complex_global_profile'].items()},73,owner['live'],b,owner['deficit'])]:
 assert m*W-sum(r*n for r,n in H.items())==deficit and m*m>2*max(H)**2
 for z,ok in [(lower,True),(lower+Q(1,10**24),False)]:
  l,u=M.moment(H,m,W,z,True);ll,uu=B.moment(m,W,list(H.items()),z);fl,fu=B.moment(m,W,[(1,32*m*m*sum(H.values()))],z);ll+=fl/10**16;uu+=fu/10**16
  assert(u<1 and uu<1)if ok else(l>1 and ll>1)
  receipts.append(dict(side=side,endpoint=str(z),accept=ok,mercator=[str(l-1),str(u-1)],base_two=[str(ll-1),str(uu-1)]))
assert bit['bit']['two_level_coefficient_bits']<bit['bit']['charged_two_level_coefficient_bits']==512 and bit['bit']['row_coefficient']<20161
eta=beta=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24);assert 0<s<c and s<(1-beta)*b;chain=[Q(384599,10**10)];cuts=[]
for _ in range(6):
 old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert old<a<s<1-a and gap>0;ceil=lambda x:-(-x.numerator//x.denominator);cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap));assert cut*gap**2>=36 and cut*gap>=2*(4+512);cuts.append(dict(exponent=str(a),gap=str(gap),cutoff_log2=str(cut)));chain.append(a)
q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18)
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}};assembly=A.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(assembly['strict_constraints'])==47 and all(v>0 for v in assembly['strict_constraints'].values())
controls=[]
for name,kk,ee,bb in [('next_grid',k+Q(1,10**18),eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
 try:A.assembly(chain[-1],b,bridge,kk,eta=ee,beta=bb)
 except AssertionError:controls.append(name)
 else:raise AssertionError(name)
def dec(a):
 with localcontext()as ctx:ctx.prec=60;return str(Decimal(a.numerator)/Decimal(a.denominator))
r=dict(status='PASS_EXACT_CITED_R420_STATIC44_COMPOSITION',kappa=str(k),kappa_decimal=dec(k),complex_lower=str(b),complex_decimal=dec(b),bit_lower=str(c),bit_decimal=dec(c),binding='complex'if (1-beta)*b<c else'bit',gain_over_previous547_percent=dec(100*(k/Q(read(P/'history/PR547-initial-EXPECTED.json')['kappa'])-1)),gain_over548_percent=dec(100*(k/Q(cp['kappa'])-1)),moments=receipts,bootstrap=cuts,outer={n:str(v)for n,v in assembly['strict_constraints'].items()},controls=controls,scope='Exact arithmetic composition of PR543 bit and PR548 complex, with completed independent finite replays retained separately. This verifier does not rebuild either physical operator. Inherited all-size compiler, common-label/mutable-source, hosting, precision/tape and analytic interfaces remain conditional. R420 interleaved phase-B source writes rely on its stated H1-H5 interface argument.')
if(P/'EXPECTED.json').exists():assert r==read(P/'EXPECTED.json')
out.write_text(json.dumps(r,indent=2)+'\n');print({n:r[n]for n in ['status','kappa_decimal','binding','gain_over_previous547_percent']})
