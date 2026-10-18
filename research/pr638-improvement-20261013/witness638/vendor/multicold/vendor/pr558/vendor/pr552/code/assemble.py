"""New exact two-supplier assembly, adapted from PR547 and PR535.
Usage: assemble.py PACKAGE FRESH_COMPLEX_GLOBAL OUTPUT_JSON
Original upstream attribution retained in the bundled engines and lineage notes.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
import sys,json,hashlib,importlib.util
if not __debug__:raise RuntimeError('Assertions required')
P=Path(sys.argv[1]).resolve();C=Path(sys.argv[2]).resolve();out=Path(sys.argv[3]).resolve();assert not out.exists()
def read(p):return json.loads(p.read_text())

def load(n):
 s=importlib.util.spec_from_file_location(n,P/'engines'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,B,A=[load(n)for n in ['moment','base_two_moment','outer']];bit=read(P/'inputs/PR543-EXPECTED.json')['nine'];c=Q(bit['bit_lower'])
owner=read(C/'audit/OWNERS-AND-PROFILE.json');inv=read(C/'audit/PREFIX-AND-INVOICE.json');host=read(C/'hosted/HOSTED.json')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert owner['template_sha256']==inv['template_sha256']==host['template_sha256']
assert inv['owner_audit_sha256']==sha(C/'audit/OWNERS-AND-PROFILE.json') and all(inv['strict_checks'].values())
H={int(r):n for r,n in owner['paid_profile'].items()};cert=M.certify(H,73,owner['live'],True);b=Q(cert['lower'])
cp={'complex_lower':str(b),'complex_global_profile':owner['paid_profile'],'complex_live':owner['live'],'complex_deficit':2560}
assert inv['global_prefix_bits']<inv['charged_prefix_bits']==512 and inv['finite']['physical_row_coefficient']<20161
receipts=[]
for side,H,m,W,lower,deficit in [('bit',{int(r):n for r,n in bit['profile'].items()},64,bit['bit']['live'],c,9984),('complex',{int(r):n for r,n in cp['complex_global_profile'].items()},73,cp['complex_live'],b,cp['complex_deficit'])]:
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
r=dict(status='PASS_FRESH_WAVE_COMPLEX_AND_CITED_R420_COMPOSITION',kappa=str(k),kappa_decimal=dec(k),complex_lower=str(b),complex_decimal=dec(b),bit_lower=str(c),bit_decimal=dec(c),binding='complex'if (1-beta)*b<c else'bit',gain_over547_percent=dec(100*(k/Q('0.001590711200057236')-1)),gain_over_prior_delivery_percent=dec(100*(k/Q('0.001590591090759927')-1)),complex_template_sha256=host['template_sha256'],complex_owner_audit_sha256=sha(C/'audit/OWNERS-AND-PROFILE.json'),complex_invoice_sha256=sha(C/'audit/PREFIX-AND-INVOICE.json'),complex_profile=owner['paid_profile'],moments=receipts,bootstrap=cuts,outer={n:str(v)for n,v in assembly['strict_constraints'].items()},controls=controls,scope='Exact composition of the freshly rebuilt and physically audited wave complex supplier with the pinned PR543 published bit receipt. The unchanged bit operator is cited, not rebuilt in this package. Inherited all-size compiler, common-label/mutable-source, hosting, precision/tape and analytic interfaces remain conditional. R420 interleaved phase-B source writes rely on its stated H1-H5 interface argument.')

out.write_text(json.dumps(r,indent=2)+'\n');print({n:r[n]for n in ['status','kappa_decimal','binding','gain_over547_percent']})
