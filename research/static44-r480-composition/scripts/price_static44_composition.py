"""Reprice actual static44 owner profile with the independently checked PR542 bit supplier.
Original moment/outer engines and literal bit charge are inherited unchanged.
Prepared for Rohan Arun with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
import json,sys,importlib.util,hashlib
R=Path(__file__).resolve().parent;P=R/'r480-minimal-publication/research/r480-sliced-minimal-frames';G=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();assert not out.exists()
def read(p):return json.loads(p.read_text())
def load(n):
 s=importlib.util.spec_from_file_location(n,P/'engines'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,B,A=[load(n)for n in ['moment','base_two_moment','outer']];owner=read(G/'audit/OWNERS-AND-PROFILE.json');inv=read(G/'audit/PREFIX-AND-INVOICE.json');host=read(G/'hosted/HOSTED.json');assert owner['template_sha256']==inv['template_sha256']==host['template_sha256'];assert all(inv['strict_checks'].values());assert inv['finite']['physical_row_coefficient']<20161
H={int(r):n for r,n in owner['paid_profile'].items()};m,W=73,owner['live'];assert m*W-sum(r*n for r,n in H.items())==2560
cert=M.certify(H,m,W,True);b=Q(cert['lower']);checks=[]
for z,ok in [(b,True),(b+Q(1,10**24),False)]:
 l,u=M.moment(H,m,W,z,True);ll,uu=B.moment(m,W,list(H.items()),z);fl,fu=B.moment(m,W,[(1,32*m*m*sum(H.values()))],z);ll+=fl/10**16;uu+=fu/10**16;assert(u<1 and uu<1)if ok else(l>1 and ll>1);checks.append(dict(side='complex',endpoint=str(z),accept=ok,bounds=[str(l-1),str(u-1),str(ll-1),str(uu-1)]))
e=read(P/'EXPECTED.json');BH={int(r):n for r,n in e['profile'].items()};c=Q(e['bit_lower']);factor=Q(98682,2**61)*sum(BH.values())
for z,ok in [(c,True),(c+Q(1,10**24),False)]:
 l,u=M.moment(BH,64,30720,z,False);fl,fu=M.moment({1:1},64,30720,z,False);l+=factor*fl;u+=factor*fu;ll,uu=B.moment(64,30720,list(BH.items()),z);fl,fu=B.moment(64,30720,[(1,1)],z);ll+=factor*fl;uu+=factor*fu;assert(u<1 and uu<1)if ok else(l>1 and ll>1);checks.append(dict(side='bit',endpoint=str(z),accept=ok,bounds=[str(l-1),str(u-1),str(ll-1),str(uu-1)]))
eta=beta=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24);chain=[Q(384599,10**10)];cuts=[]
for _ in range(6):
 old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert old<a<s<1-a and gap>0
 ceil=lambda x:-(-x.numerator//x.denominator);cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap));assert cut*gap**2>=36 and cut*gap>=2*(4+512);cuts.append(dict(gap=str(gap),cutoff_log2=str(cut)));chain.append(a)
q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18)
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}};assembly=A.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(assembly['strict_constraints'])==47 and all(v>0 for v in assembly['strict_constraints'].values())
controls=[]
for name,kk,ee,bb in [('next_grid',k+Q(1,10**18),eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
 try:A.assembly(chain[-1],b,bridge,kk,eta=ee,beta=bb)
 except AssertionError:controls.append(name)
 else:raise AssertionError(name)
def dec(a):
 with localcontext()as ctx:ctx.prec=60;return str(Decimal(a.numerator)/Decimal(a.denominator))
r=dict(status='PASS_FRESH_COMPLEX_GLOBAL_AND_CITED_PR542_BIT_ASSEMBLY',kappa=str(k),kappa_decimal=dec(k),complex_lower=str(b),complex_decimal=dec(b),bit_lower=str(c),binding='bit'if c<(1-beta)*b else'complex',gain_over542_percent=dec(100*(k/Q(e['kappa'])-1)),profile=H,moment_checks=checks,bootstrap=cuts,outer={n:str(v)for n,v in assembly['strict_constraints'].items()},controls=controls,complex_template_sha256=host['template_sha256'],bit_expected_sha256=hashlib.sha256((P/'EXPECTED.json').read_bytes()).hexdigest(),scope='Changed complex finite admission verified with reused hash-bound unchanged phase/data dependencies. PR542 finite bit operator cited and exact arithmetic repriced. All-size compiler, mutable-source, hosting and analytic-transfer assumptions remain conditional.')
out.write_text(json.dumps(r,indent=2)+'\n');print({n:r[n]for n in ['status','kappa_decimal','complex_decimal','binding','gain_over542_percent']},flush=True)
