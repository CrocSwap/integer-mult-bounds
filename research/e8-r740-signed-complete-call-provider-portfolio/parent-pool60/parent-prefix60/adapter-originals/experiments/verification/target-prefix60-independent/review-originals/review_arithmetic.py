"""Independent arithmetic screen; actual assignment/operator admission separate."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,importlib.util,struct,math
if not __debug__:raise SystemExit('Assertions required')
R=Path(__file__).resolve().parent.parent;P=R.parent/'architecture/target-prefix-multipair-complete/global';O=R/'target-prefix56-independent'
rd=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENG=R.parent/'stage-search/pr425-hamming/source/research/hamming-mutable-basis-complex/work/pr361/code/engines'
def load(n):
    s=importlib.util.spec_from_file_location('independent11_'+n,ENG/(n+'.py'));x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
M,N,Outer=[load(n)for n in ['moment','base_two_moment','outer']]
g=rd(P/'hosted/GLOBAL.json');geo=rd(P/'hosted/GEOMETRY.json');s=rd(O/'signed-rerun/RESULT.json');bill=rd(P/'signed/GLOBAL-BOUND.json');claim=rd(P/'REFINED-NOMINATION.json')
HB={int(k):v for k,v in g['profile'].items()};cg=rd(R.parent/'stage-search/pr441-signed75-hosting/complex-hosted/HOSTED.json');HC={int(k):v for k,v in cg['global_profile'].items()}
assert 78*g['live']-sum(r*n for r,n in HB.items())==3264 and g['live']==9600 and g['physical']==9609
assert 78**2<2*max(HB)**2 and 78**3>2*max(HB)**3
rf,rb=[g['local_checks'][k]['cancellation_free_row_l1']for k in ['forward','reverse']];sf,sb=[s[k]['max_prefix_row_l1']for k in ['forward','literal_signed_inverse']]
rawprefix=2**24*rf**6*rb**5;prefix=2**24*sf**6*sb**5;assert prefix==int(bill['finite']['charged_prefix'])and prefix.bit_length()==159
raw=list(struct.iter_unpack('<6i',(P/'signed/records/249-records.bin').read_bytes()));signed=list(struct.iter_unpack('<6i',(O/'signed-rerun/signed-records.bin').read_bytes()))
ru=sum(abs(c)for op,a,b,c,f,z in raw if op==1);su=sum(abs(c)for op,a,b,c,f,z in signed if op==1);assert su-ru==1274 and s['compensation']['even_additions']==400
m,W,T,L,RH,V,K=78,9600,8,11,740,120,5;events=sum(HB.values());J=8*T*L*(2*V+RH)+8*(2*K*V*T)+2*(g['bank_assignments']+g['hosted_residuals'])+2*g['copy_erase_episodes']
selectors=2*L*T*((W-1)+RH*m*(geo['max_route_factors']+144+2+(m-1)+m));selectors+=2*11*8*112*78*154
fixed=J*16*(m*m+1)**2+J*g['physical']+events*(8*m*m+8+128*(2*m)**3)+16*m**3+g['copy_erase_episodes']+selectors+1
coef=88*su+g['bridge_additions']+fixed+prefix;cube=(coef+1)**3*(events+1)**3
assert coef==int(bill['finite']['signed_coefficient'])and cube==int(bill['finite']['signed_three_level_coefficient'])and cube.bit_length()==530 and cube<2**1024
assert 88*ru+g['bridge_additions']+fixed+rawprefix==int(bill['finite']['raw_coefficient'])
overhead=1
while 3**overhead<=g['physical']:overhead+=1
row=3*(m*(m-1)//2+m+overhead)+9909+252;assert row==19431<20161 and 2**m<3**m and g['physical']<3**overhead
assert 3*(m*m+1)+9909+252==28416>20161
b,c=map(Q,[claim['complex_lower'],claim['bit_lower']]);bounds={}
for label,H,dim,stock,z in [('complex',HC,73,cg['live'],b),('bit',HB,78,W,c)]:
    intervals=[]
    for value in [z,z+Q(1,10**24)]:
        x=M.moment(H,dim,stock,value,True);lo,hi=N.moment(dim,stock,list(H.items()),value);bl,bh=N.moment(dim,stock,[(1,32*dim*dim*sum(H.values()))],value);y=(lo+bl/10**16,hi+bh/10**16)
        assert max(x[1],y[1])<1 if value==z else min(x[0],y[0])>1
        intervals.append((str(value),tuple(map(str,x)),tuple(map(str,y))))
    bounds[label]=intervals
eta=beta=Q(1,10**30);grid=Q(1,10**27);selected=Q(math.floor((min(c,(1-beta)*b)-grid)*10**27),10**27);chain=[Q(384599,10**10)];cuts=[]
for i in range(8):
    old=chain[-1];new=(1-selected)*selected+selected*old;gap=min(selected-new,1-new-selected,1-new-selected*(1-old),1-selected);assert old<new<selected<1-new and gap>0
    cutoff=max(math.ceil(36/gap**2),math.ceil(2*(4+1024)/gap));assert cutoff*gap**2>=36 and cutoff*gap>=2*(4+1024);cuts.append(dict(gap=str(gap),cutoff_log2=str(cutoff)));chain.append(new)
assert cuts==claim['bootstrap']
q=(1-2*eta)*chain[-1];ticks=(1-eta)*q/(1+q)/grid;k=Q((ticks.numerator-1)//ticks.denominator,10**27);assert k==Q(claim['kappa'])==Q(78712924282401861620781,62500000000000000000000000)
bridge=dict(semantic=dict(C0=dict(base=2,exponent=210000),strict_literal_gap=1),rows=dict(degree_gap=Q(10**6)-Q(51*20161,25)))
a=Outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(a['strict_constraints'])==47 and min(a['strict_constraints'].values())>0
assert {n:str(v)for n,v in a['strict_constraints'].items()}==claim['strict_constraints']
for leaf,kk in [(chain[-1],k+grid),((1-beta)*b,k)]:
    try:Outer.assembly(leaf,b,bridge,kk,eta=eta,beta=beta)
    except AssertionError:pass
    else:raise AssertionError('grid/cap mutation admitted')
result=dict(status='PASS_INDEPENDENT_ELEVEN95_THREE_DEPTH_FINITE_INVOICE_DUAL_MOMENTS_EIGHT47_SCREEN',source_nomination_sha256=sha(P/'REFINED-NOMINATION.json'),source_invoice_sha256=sha(P/'signed/GLOBAL-BOUND.json'),fresh_signed_sha256=sha(O/'signed-rerun/RESULT.json'),kappa=str(k),moment_bounds=bounds,prefix_bits=159,composed_bits=530,charged_composed_bits=1024,row_coefficient=row,strict_constraints=47,continuations=8,scope='Exact conditional arithmetic and signed-local prefix. Third-depth halving/compiler and hosted operator/sigma, correlated-bank/compressed-window, chart/precision/tape/common-prime/recovery/analytic/C_full interfaces remain explicit. No independent release admission until full source geometry and serialization gate.')
(O/'ARITHMETIC.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(result['status'],sha(O/'ARITHMETIC.json'))
