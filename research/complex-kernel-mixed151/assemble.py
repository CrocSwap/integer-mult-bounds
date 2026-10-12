"""Exact composition of pinned PR458 complex and PR459 bit suppliers.
Screen mode cites pinned reports; full mode consumes freshly verified wrappers.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--research-root',type=Path,default=ROOT.parent);ap.add_argument('--complex-output',type=Path);ap.add_argument('--bit-output',type=Path);a=ap.parse_args()
read=lambda p:json.loads(p.read_text());source=read(ROOT/'SOURCE.json')
assert bool(a.complex_output)==bool(a.bit_output)
mode='FRESH_FULL_SUPPLIERS' if a.complex_output else 'PINNED_REPORT_SCREEN_FULL_REPLAY_PENDING'
if a.complex_output:
 cr=read(a.complex_output/'RECEIPT.json');br=read(a.bit_output/'RECEIPT.json')
 assert cr['status']=='PASS_COMPLEX_ADAPTED_KERNEL_FULL_COMPOSITION' and cr['mode']=='full'
 assert br['status']=='PASS_DUAL_ELEVEN_RANK151_HOSTING' and br['mode']=='full'
 for receipt,key in [(cr,'complex'),(br,'bit')]:assert receipt['manifest_sha256']==source[key]['manifest_sha256'] and receipt['source_sha256']==source[key]['source_sha256']
 cx=read(a.complex_output/'RESULT.json');bit=read(a.bit_output/'RESULT.json');audit=read(a.complex_output/'complex/AUDIT.json')
else:
 cx=read(ROOT/'evidence/COMPLEX-PARENT-RESULT.json');bit=read(ROOT/'evidence/BIT-PARENT-EXPECTED.json');audit=read(ROOT/'evidence/COMPLEX-PARENT-AUDIT.json')
for item,result in [(source['complex'],cx),(source['bit'],bit)]:
 expected=read(a.research_root/item['package']/'EXPECTED.json')
 for k,v in expected.items():assert result[k]==v,(item['package'],k)
assert audit['template_sha256']==cx['complex_template_sha256'] and audit['emitted_program_sha256']==cx['complex_emitted_program_sha256']
assert audit['max_helpers_per_physical_family_per_call']==1

def load(n):
 spec=importlib.util.spec_from_file_location(n,a.research_root/'e8-r740-replica32/code/engines'/(n+'.py'));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
M,Other,Outer=load('moment'),load('base_two_moment'),load('outer')
endpoints={}
for name,P,m,W,claimed in [('bit',bit['bit_profile'],78,bit['bit']['live'],bit['bit_lower']),('complex',audit['profile'],89,audit['live'],cx['complex_lower'])]:
 P={int(k):v for k,v in P.items()};assert m*W-sum(k*v for k,v in P.items())==3264
 cert=M.certify(P,m,W,True);lo,hi=Q(cert['lower']),Q(cert['upper']);assert lo==Q(claimed)
 for x,below in [(lo,True),(hi,False)]:
  u,v=Other.moment(m,W,list(P.items()),x);uu,vv=Other.moment(m,W,[(1,32*m*m*sum(P.values()))],x)
  assert (v+vv/10**16<1) if below else (u+uu/10**16>1)
 endpoints[name]=lo
# Preserve the suppliers' complete independent cost and row contracts.
assert bit['bit']['row_coefficient']==19431 and cx['complex']['row_coefficient']==20161
assert bit['bit']['three_level_coefficient_bits']<=bit['bit']['charged_three_level_coefficient_bits']==1024
assert cx['complex']['local_bound']<1<<48 and cx['complex']['router_bits']<=30000 and cx['complex']['literal_bits']<=100000
assert cx['complex']['charged_wrapper_groups']==788480 and cx['complex']['wrapper_events']==13904
c,b=endpoints['bit'],endpoints['complex'];eta=beta=Q(1,10**18);grid=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24);assert 0<s<c and s<(1-beta)*b
chain=[Q(384599,10**10)];cutoffs=[]
def ceil(x):return -((-x.numerator)//x.denominator)
for _ in range(6):
 old=chain[-1];nxt=(1-s)*s+s*old;gap=min(s-nxt,1-nxt-s,1-nxt-s*(1-old),1-s);assert old<nxt<s<1-nxt and gap>0
 bound=max(ceil(36/gap**2),ceil(2*(4+1024)/gap));assert bound*gap**2>=36 and bound*gap>=2*(4+1024)
 cutoffs.append(dict(gap=str(gap),cutoff_log2=str(bound)));chain.append(nxt)
q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin/grid;k=grid*((ticks.numerator-1)//ticks.denominator)
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
res=Outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(res['strict_constraints'])==47 and all(x>0 for x in res['strict_constraints'].values())
controls=[]
for name,kk,ee,bb in [('next_grid',k+grid,eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
 try:Outer.assembly(chain[-1],b,bridge,kk,eta=ee,beta=bb)
 except AssertionError:controls.append(name)
 else:raise AssertionError(name)
assert k>Q(cx['kappa'])
result=dict(status='PASS_PINNED_SUPPLIER_COMPOSITION_ARITHMETIC',mode=mode,kappa=str(k),kappa_decimal=format(float(k),'.18f'),gain_over_pr458_percent=float((k/Q(cx['kappa'])-1)*100),bit_lower=str(c),complex_lower=str(b),binding_component='bit' if c<(1-beta)*b else 'complex',bit_template_sha256=bit['bit_template_sha256'],bit_emitted_program_sha256=bit['emitted_program_sha256'],complex_template_sha256=cx['complex_template_sha256'],complex_emitted_program_sha256=cx['complex_emitted_program_sha256'],bit_invoice=bit['bit'],complex_invoice=cx['complex'],strict_outer_constraints={n:str(x) for n,x in res['strict_constraints'].items()},bootstrap=cutoffs,controls=controls,scope='Conditional composition of unchanged pinned suppliers and their union of assumptions. Screen mode is not full supplier verification; no unconditional theorem.')
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(result['kappa_decimal'],result['gain_over_pr458_percent'],mode)
