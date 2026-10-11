"""Fresh bit finite invoice and joint strict arithmetic for two changed suppliers.
icekylinx, with Codex assistance. Inherited all-size interfaces remain conditional.
"""
import json,hashlib,importlib.util
from pathlib import Path
from fractions import Fraction as Q
import os
ROOT=Path(os.environ['E8_OUTPUT']);D=ROOT/'bit426-source-centres/global';C=ROOT/'split-centres'
read=lambda p:json.loads(p.read_text())
g=read(D/'GLOBAL.json');geo=read(D/'GEOMETRY.json');audit=read(D/'AUDIT.json')
cx=read(C/'INTEGRATION.json');ca=read(C/'INDEPENDENT-REPLAY.json')
assert audit['template_sha256']==g['template_sha256'] and ca['template_sha256']==cx['global_template_sha256']
assert len(audit['mutations_rejected'])==8 and len(ca['mutation_controls_rejected'])==7
P={int(r):z for r,z in audit['profile'].items()};m,W=64,14403;E=sum(P.values());T,L,R,V,K=8,9,747,120,4
mass=sum(r*z for r,z in P.items());assert m*W-mass==2496 and g['live']==W
physical=g['physical'];d=m*m;N=2*m
unit=L*T*g['local_additions']+g['bridge_additions']
J=8*T*L*(2*V+R)+8*(2*K*V*T)+2*g['bank_assignments']+2*g['copy_erase_episodes']
high=16*(d+1)**2;good=8*m*m+8;compiler=128*N**3
selectors=2*L*T*((W-1)+R*m*(geo['max_route_factors']+(m-1)+m))
prefix=int(g['global_prefix_bound']);charged_prefix=64*((prefix.bit_length()+63)//64);assert prefix<1<<charged_prefix
coefficient=unit+J*high+J*physical+E*(good+compiler)+16*m**3+g['copy_erase_episodes']+selectors+prefix+1
two=(coefficient+1)**2*(E+1)**2
charged_two=64*((two.bit_length()+63)//64);assert two<1<<charged_two and 2*max(P)**2<m*m
row=2*(m*m+1)+9909+252;assert row==18355<20161
assert geo['bad_prime_factors']==[2] and geo['route_denominators']==[1,2,4]
def load(name):
 p=ROOT/'work/pr361/code/engines'/(name+'.py');sp=importlib.util.spec_from_file_location('joint_'+name,p);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
M,Other,Outer=load('moment'),load('base_two_moment'),load('outer')
root=M.certify(P,m,W,True);c=Q(root['lower']);grid=Q(1,10**18);b=Q(ca['complex_b'])
fb=32*m*m*E
lo,hi=Other.moment(m,W,list(P.items()),c);bl,bh=Other.moment(m,W,[(1,fb)],c)
assert hi+bh/10**16<1
eta=beta=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24)
assert 0<s<c and s<(1-beta)*b
chain=[Q(384599,10**10)];cutoffs=[]
def ceil(x):return -((-x.numerator)//x.denominator)
for j in range(6):
 old=chain[-1];a=(1-s)*s+s*old
 gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert old<a<s<1-a and gap>0
 cutoff=max(ceil(36/gap**2),ceil(2*(4+charged_two)/gap))
 assert cutoff*gap**2>=36 and cutoff*gap>=2*(4+charged_two)
 cutoffs.append(dict(gap=str(gap),cutoff_log2=str(cutoff)));chain.append(a)
q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin/grid;k=grid*((ticks.numerator-1)//ticks.denominator)
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
a=Outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta)
assert len(a['strict_constraints'])==47 and all(x>0 for x in a['strict_constraints'].values())
controls=[]
for name,kk,ee,bb in [('next_grid',k+grid,eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
 try:Outer.assembly(chain[-1],b,bridge,kk,eta=ee,beta=bb)
 except AssertionError:controls.append(name)
 else:raise AssertionError(name)
result=dict(status='PASS_CONDITIONAL_EARLY_RESET_REUSE_ASSEMBLY',kappa=str(k),kappa_decimal=format(float(k),'.18f'),bit_lower=str(c),complex_lower=str(b),binding_component='bit',gain_over_pr425_percent=float(100*(k/Q(1048005508028206,10**18)-1)),bit_invoice=dict(prefix_bits=prefix.bit_length(),charged_prefix_bits=charged_prefix,coefficient_bits=coefficient.bit_length(),two_level_coefficient_bits=two.bit_length(),charged_two_level_coefficient_bits=charged_two,row_coefficient=row,live=W,physical=physical),strict_outer_constraints={n:str(x) for n,x in a['strict_constraints'].items()},outer_controls=controls,bootstrap=cutoffs,bit_template_sha256=g['template_sha256'],complex_template_sha256=cx['global_template_sha256'],scope='Finite research composition with explicit changed words, exact local and global replay and incremental phase evidence. All-size correlated dirty-bank, compressed-window, compiler, restored-work, tape/common-grid, precision and analytic interfaces remain inherited assumptions. This certificate makes no unconditional integer-multiplication or Lean-kernel claim.')
(ROOT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],result['kappa_decimal'],result['gain_over_pr425_percent'],result['bit_invoice'])
