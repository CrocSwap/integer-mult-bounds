"""Two exact moment engines and strict outer composition of a new PR484 rehosting
with the unchanged published PR493 bit supplier. Prepared by OpenAI Codex; arithmetic
engines are pinned inherited PR361/Mercator and independent base-two code.
Usage: assemble_candidate.py AUDIT_OUT PARENT_VARIANT HOSTED BIT_RESULT
"""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,sys,hashlib,importlib.util
O,V,H,B=map(Path,sys.argv[1:5]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):
 p=V/'work/pr361/code/engines'/(n+'.py');s=importlib.util.spec_from_file_location('candidate_'+n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,Other,Outer=[load(n)for n in ['moment','base_two_moment','outer']]
owner=json.loads((O/'OWNERS-AND-PROFILE.json').read_text());inv=json.loads((O/'PREFIX-AND-INVOICE.json').read_text());host=json.loads((H/'HOSTED.json').read_text());bit=json.loads(B.read_text())["eleven"];P={int(r):n for r,n in owner['paid_profile'].items()};m,W=73,owner['live'];assert m*W-sum(r*n for r,n in P.items())==2496
rc=M.certify(P,m,W,True);b=Q(rc['lower']);bp=Q(rc['upper']);assert bp-b==Q(1,10**24)
fallback=32*m*m*sum(P.values());receipts=[]
for z,accept in[(b,True),(bp,False)]:
 ml,mh=M.moment(P,m,W,z,True);a,c=Other.moment(m,W,list(P.items()),z);d,e=Other.moment(m,W,[(1,fallback)],z);a+=d/10**16;c+=e/10**16
 assert (mh<1 and c<1)if accept else(ml>1 and a>1)
 receipts.append(dict(endpoint=str(z),mercator=[str(ml-1),str(mh-1)],base_two=[str(a-1),str(c-1)],accept=accept))
# Reprice the cited unchanged bit histogram, clearly separate from bit operator verification.
bitP={int(r):n for r,n in bit['profile'].items()};bitc=Q(bit['bit_lower']);bitnext=bitc+Q(1,10**24)
for zz,accepted in [(bitc,True),(bitnext,False)]:
 bl,bh=M.moment(bitP,78,9600,zz,True)
 ol,oh=Other.moment(78,9600,list(bitP.items()),zz)
 fl,fh=Other.moment(78,9600,[(1,32*78*78*sum(bitP.values()))],zz)
 assert (bh<1 and oh+fh/10**16<1) if accepted else (bl>1 and ol+fl/10**16>1)
c=Q(bit['bit_lower']);eta=beta=Q(1,10**18);grid=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24)
assert 0<s<c and s<(1-beta)*b
coeff=int(bit['bit']['charged_three_level_coefficient_bits']);row=max(20161,int(bit['bit']['row_coefficient']),inv['finite']['physical_row_coefficient']);chain=[Q(384599,10**10)];cuts=[]
def ceil(x):return -(-x.numerator//x.denominator)
for i in range(6):
 old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert old<a<s<1-a and gap>0
 cut=max(ceil(36/gap**2),ceil(2*(4+coeff)/gap));assert cut*gap**2>=36 and cut*gap>=2*(4+coeff);cuts.append(dict(gap=str(gap),cutoff_log2=str(cut)));chain.append(a)
q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin/grid;kap=grid*((ticks.numerator-1)//ticks.denominator)
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*row,25)}}
a=Outer.assembly(chain[-1],b,bridge,kap,eta=eta,beta=beta);assert len(a['strict_constraints'])==47 and all(x>0 for x in a['strict_constraints'].values());controls=[]
for name,k,e,be in [('next_grid',kap+grid,eta,beta),('zero_eta',kap,Q(0),beta),('zero_beta',kap,eta,Q(0)),('unit_beta',kap,eta,Q(1))]:
 try:Outer.assembly(chain[-1],b,bridge,k,eta=e,beta=be)
 except AssertionError:controls.append(name)
 else:raise AssertionError(name)
res=dict(status='PASS_ASYNC_COMPLEX_AND_CITED_BIT_EXACT_ASSEMBLY',complex_lower=str(b),complex_decimal=rc['lower'],next_b_rejected=str(bp),exact_moment_receipts=receipts,bit_lower=str(c),bit_result_sha256=sha(B),bit_template_sha256=bit['emitted_program_sha256'],bit_prefix_bits=bit['bit']['charged_prefix_bits'],bit_charged_three_level_coefficient_bits=coeff,external_row_allowance=row,kappa=str(kap),kappa_decimal=f'{float(kap):.18f}',binding_component='bit'if c<(1-beta)*b else'complex',strict_outer_constraints={k:str(v)for k,v in a['strict_constraints'].items()},outer_controls=controls,bootstrap=cuts,complex_template_sha256=host['template_sha256'],owner_audit_sha256=sha(O/'OWNERS-AND-PROFILE.json'),invoice_sha256=sha(O/'PREFIX-AND-INVOICE.json'),bit_scope='PR493 published profile and operator reused as a pinned dependency; this verifier reprices its published profile but does not reconstruct that unchanged bit operator.',scope='Conditional finite witness. Inherited compiler, precision/tape and analytic-transfer contracts remain assumed; changed-host operator admission recorded separately.')
(O/'EXACT-ASSEMBLY.json').write_text(json.dumps(res,indent=2)+'\n');print(res['status'],'b',res['complex_decimal'],'kappa',res['kappa_decimal'],flush=True)
