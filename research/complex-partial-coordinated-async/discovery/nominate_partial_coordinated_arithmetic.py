"""Exact arithmetic for a stage-dependent word nomination, not physical admission."""
from pathlib import Path
from fractions import Fraction as Q
import json,importlib.util
R=Path(__file__).resolve().parent;O=R/'partial-coordinated-arithmetic';O.mkdir(exist_ok=False)
nom=json.load(open(R/'partial-coordinated-restricted/NOMINATION.json'));P={int(r):n for r,n in nom['profile'].items()};parent=json.load(open(R/'pr507-async-admission/audit/EXACT-ASSEMBLY.json'));m,W=73,7680;assert m*W-sum(r*n for r,n in P.items())==2496
engine=R/'source496-review/vendor/complex/split-centres-global/vendor/engines'
def load(n):
 s=importlib.util.spec_from_file_location(n,engine/(n+'.py'));x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
M,B,Outer=[load(n) for n in ['moment','base_two_moment','outer']];rc=M.certify(P,m,W,True);b=Q(rc['lower']);bp=Q(rc['upper']);receipts=[]
for z,ok in [(b,True),(bp,False)]:
 a,c=M.moment(P,m,W,z,True);u,v=B.moment(m,W,list(P.items()),z);q,t=B.moment(m,W,[(1,32*m*m*sum(P.values()))],z);u+=q/10**16;v+=t/10**16;assert (c<1 and v<1) if ok else (a>1 and u>1);receipts.append(dict(endpoint=str(z),accept=ok,mercator=[str(a-1),str(c-1)],base_two=[str(u-1),str(v-1)]))
c=Q(parent['bit_lower']);eta=beta=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24);chain=[Q(384599,10**10)];cuts=[]
for _ in range(6):
 old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert old<a<s<1-a;ceil=lambda x:-(-x.numerator//x.denominator);cut=max(ceil(36/gap**2),ceil(2*(4+6464)/gap));cuts.append(dict(gap=str(gap),cutoff_log2=str(cut)));chain.append(a)
q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);tick=margin*10**18;k=Q((tick.numerator-1)//tick.denominator,10**18);bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}};outer=Outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(outer['strict_constraints'])==47 and all(v>0 for v in outer['strict_constraints'].values());controls=[]
for label,kap,e,be in [('next_grid',k+Q(1,10**18),eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
 try:Outer.assembly(chain[-1],b,bridge,kap,eta=e,beta=be)
 except AssertionError:controls.append(label)
 else:raise AssertionError(label)
r=dict(status='EXACT_ARITHMETIC_NOMINATION_PHYSICAL_ADMISSION_PENDING',complex_lower=str(b),next_b_rejected=str(bp),kappa=str(k),kappa_decimal=f'{float(k):.18f}',gain_over_previous_pr473=str(k-Q(parent['kappa'])),gain_percent=float(100*(k/Q(parent['kappa'])-1)),profile=P,live=W,bit_lower=str(c),moment_receipts=receipts,strict_outer_constraints={k:str(v) for k,v in outer['strict_constraints'].items()},outer_controls=controls,bootstrap=cuts,scope='Arithmetic assumes inherited row allowance20161 and bit coefficient6464. Actual new-factory scalar/phase/owner/prefix/finite-invoice admission remains required. No verified bound claim.')
(O/'EXACT-ARITHMETIC.json').write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items() if k not in ['moment_receipts','strict_outer_constraints','bootstrap']},flush=True)
