"""Fresh bit pooled-prefix invoice, two exact moments and conditional outer assembly."""
from pathlib import Path
from fractions import Fraction as Q
import json,math,sys,importlib.util
ROOT=Path(__file__).resolve().parent
bit,research=map(Path,sys.argv[1:3]);read=lambda p:json.loads(p.read_text())
mode='PINNED_COMPLEX_REPORT_FULL_PARENT_PENDING'
cx=read(ROOT/'data/complex-parent-result.json');ca=read(ROOT/'data/complex-parent-audit.json')
if len(sys.argv)>3:
 parent=Path(sys.argv[3]);receipt=read(parent/'RECEIPT.json');assert receipt['status']=='PASS_COMPLEX_ADAPTED_KERNEL_FULL_COMPOSITION' and receipt['mode']=='full'
 pin=read(ROOT/'SOURCE.json')['complex'];assert receipt['manifest_sha256']==pin['manifest_sha256'] and receipt['source_sha256']==pin['source_sha256']
 fresh=read(parent/'RESULT.json');assert all(fresh[k]==cx[k] for k in ['kappa','complex_lower','complex_template_sha256','complex_emitted_program_sha256','complex'])
 ca=read(parent/'complex/AUDIT.json');mode='COMPLETED_FULL_COMPLEX458_REUSED'
for key in ['template_sha256','emitted_program_sha256']:assert ca[key]==cx['complex_'+key]
g=read(bit/'GLOBAL.json');a=read(bit/'AUDIT.json');geo=read(bit/'GEOMETRY.json')
assert a['template_sha256']==g['template_sha256'] and a['emitted_program_sha256']==g['emitted_program_sha256']
assert a['physical_prefix_bits']==g['global_prefix_bits'] and a['charged_prefix_bits']==g['charged_prefix_bits']
def load(n):
 sp=importlib.util.spec_from_file_location(n,research/'e8-r740-replica32/code/engines'/(n+'.py'));mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
M,Other,Outer=load('moment'),load('base_two_moment'),load('outer')
P={int(k):v for k,v in a['profile'].items()};m=78;W=g['live'];T=g['replicas'];L=11;K=5;R=read(ROOT/'data/word.json')['R'];V=120;E=sum(P.values());physical=g['physical'];mass=sum(k*v for k,v in P.items())
assert m*W-mass==408*T and (T,W,physical)==(8,2*K*V*T,2*K*V*T+9)
unit=L*T*g['local_additions']+g['bridge_additions'];d=m*m;N=2*m
J=8*T*L*(2*V+R)+8*(2*K*V*T)+2*L*T*R+2*g['copy_erase_episodes']
high=16*(d+1)**2;good=8*m*m+8;compiler=128*N**3
# Two additional factors for the physical-family owner reassignment.
selectors=2*L*T*((W-1)+R*m*(geo['max_route_factors']+144+4+(m-1)+m))
prefix=int(g['global_prefix_bound']);charged_prefix=g['charged_prefix_bits'];assert charged_prefix==64*((prefix.bit_length()+63)//64) and prefix<1<<charged_prefix
coefficient=unit+J*high+J*physical+E*(good+compiler)+16*m**3+g['copy_erase_episodes']+selectors+prefix+1
three=(coefficient+1)**3*(E+1)**3;charged_three=64*((three.bit_length()+63)//64);assert three<1<<charged_three and m**3>2*max(P)**3
sys.path.insert(0,str(ROOT/'code'));from row_bound import bound,controls as row_controls
rows=bound(m,physical,max(P),3);assert rows['complete_row_coefficient']<20161
endpoints={}
for name,hist,dim,live,claim in [('bit',P,m,W,None),('complex',{int(k):v for k,v in ca['profile'].items()},89,ca['live'],Q(cx['complex_lower']))]:
 cert=M.certify(hist,dim,live,True);lo,hi=Q(cert['lower']),Q(cert['upper'])
 if claim is not None:assert lo==claim
 for x,below in [(lo,True),(hi,False)]:
  l,u=Other.moment(dim,live,list(hist.items()),x);ll,uu=Other.moment(dim,live,[(1,32*dim*dim*sum(hist.values()))],x)
  assert (u+uu/10**16<1) if below else (l+ll/10**16>1)
 endpoints[name]=lo
c,b=endpoints['bit'],endpoints['complex'];eta=beta=grid=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24);assert 0<s<c and s<(1-beta)*b
chain=[Q(384599,10**10)];cutoffs=[]
def ceil(x):return -((-x.numerator)//x.denominator)
for _ in range(6):
 old=chain[-1];nxt=(1-s)*s+s*old;gap=min(s-nxt,1-nxt-s,1-nxt-s*(1-old),1-s);assert old<nxt<s<1-nxt and gap>0
 limit=max(ceil(36/gap**2),ceil(2*(4+charged_three)/gap));assert limit*gap**2>=36 and limit*gap>=2*(4+charged_three)
 cutoffs.append(dict(gap=str(gap),cutoff_log2=str(limit)));chain.append(nxt)
q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin/grid;k=grid*((ticks.numerator-1)//ticks.denominator)
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
assembly=Outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(assembly['strict_constraints'])==47 and all(x>0 for x in assembly['strict_constraints'].values())
controls=[]
for name,kk,ee,bb in [('next_grid',k+grid,eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
 try:Outer.assembly(chain[-1],b,bridge,kk,eta=ee,beta=bb)
 except AssertionError:controls.append(name)
 else:raise AssertionError(name)
base=Q('0.001295508560071773');assert k>base
result=dict(status='PASS_R715_WARM_FACTORS_COMPONENT_INVOICE_AND_OUTER',mode=mode,kappa=str(k),kappa_decimal=format(float(k),'.18f'),gain_over_pr478_percent=float((k/base-1)*100),bit_lower=str(c),complex_lower=str(b),binding_component='bit' if c<=(1-beta)*b else 'complex',bit_template_sha256=g['template_sha256'],emitted_program_sha256=g['emitted_program_sha256'],bit_profile=g['profile'],bit=dict(live=W,physical=physical,prefix_bits=prefix.bit_length(),charged_prefix_bits=charged_prefix,coefficient_bits=coefficient.bit_length(),three_level_coefficient_bits=three.bit_length(),charged_three_level_coefficient_bits=charged_three,row_coefficient=rows['complete_row_coefficient']),complex_invoice=cx['complex'],strict_outer_constraints={n:str(x) for n,x in assembly['strict_constraints'].items()},bootstrap=cutoffs,controls=controls,row_controls=row_controls(),scope='Whole residuals on one family each; owner replica may differ. Retains conditional complete-call hosting and all inherited compiler/analytic contracts. Physical-family prefix overcharge is freshly recomputed; no old192-bit charge reused.')
(bit/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','mode','kappa_decimal','gain_over_pr478_percent','bit']},indent=2))
