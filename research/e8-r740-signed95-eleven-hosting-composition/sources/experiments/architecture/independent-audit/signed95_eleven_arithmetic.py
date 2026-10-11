from pathlib import Path
from fractions import Fraction as Q
import json,struct,hashlib,importlib.util
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/stage-search/pr445-signed95-eleven';rd=lambda p:json.loads(p.read_text());g=rd(S/'hosted/GLOBAL.json');geo=rd(S/'hosted/GEOMETRY.json');bnd=rd(S/'signed/GLOBAL-BOUND.json');nom=rd(S/'REFINED-NOMINATION.json');local=rd(S/'signed/RESULT.json');f=bnd['finite'];H={int(k):v for k,v in g['profile'].items()};m=78;W=9600;T=8;L=11;physical=9609;E=sum(H.values())
raw=list(struct.iter_unpack('<6i',(S/'signed/records/249-records.bin').read_bytes()));signed=list(struct.iter_unpack('<6i',(S/'signed/signed-records.bin').read_bytes()))
u=sum(abs(e[3]) for e in raw if e[0]==1);v=sum(abs(e[3]) for e in signed if e[0]==1);assert(u,v)==(15366,16640)
prefix=2**24*812**6*27414**5;rawprefix=2**24*784**6*18602**5
J=8*T*L*980+8*1200*T+2*65120+2*g['copy_erase_episodes'];d=m*m;selectors=2*L*T*((W-1)+740*m*(geo['max_route_factors']+144+2+(m-1)+m))
fixed=J*16*(d+1)**2+J*physical+E*(8*m*m+8+128*(2*m)**3)+16*m**3+g['copy_erase_episodes']+selectors+1
coef=88*v+g['bridge_additions']+fixed+prefix;cube=(coef+1)**3*(E+1)**3
assert J==f['route_items'] and selectors==f['selector_calls'];assert prefix==int(f['charged_prefix']) and coef==int(f['signed_coefficient']) and cube==int(f['signed_three_level_coefficient'])
assert prefix.bit_length()==156 and cube.bit_length()==523 and cube<2**1024 and cube>=2**512
assert m**2<=2*max(H)**2 and m**3>2*max(H)**3
assert 3*(m*(m+1)//2+9)+9909+252==19431
ENG=R/'experiments/stage-search/pr434-kernel/full/baseline/baseline/work/pr361/code/engines/base_two_moment.py';s=importlib.util.spec_from_file_location('base',ENG);M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
def moment(H,m,W,a):
 lo,hi=M.moment(m,W,list(H.items()),a);p,q=M.moment(m,W,[(1,32*m*m*sum(H.values()))],a);return lo+p/10**16,hi+q/10**16
c=Q(nom['bit_lower']);assert moment(H,m,W,c)[1]<1<moment(H,m,W,c+Q(1,10**24))[0]
cx=rd(R/'experiments/stage-search/pr441-signed75-hosting/complex-hosted/HOSTED.json');CH={int(k):v for k,v in cx['global_profile'].items()};b=Q(nom['complex_lower']);assert moment(CH,73,cx['live'],b)[1]<1<moment(CH,73,cx['live'],b+Q(1,10**24))[0]
beta=eta=Q(1,10**30);grid=Q(1,10**27);cap=min(c,(1-beta)*b);selected=Q(((cap-grid)*10**27).__floor__(),10**27);old=Q(384599,10**10)
for i,cut in enumerate(nom['bootstrap'],1):
 prev=selected+(old-selected)*selected**(i-1);new=selected+(old-selected)*selected**i;gap=min(selected-new,1-new-selected,1-new-selected*(1-prev),1-selected)
 assert gap==Q(cut['gap']);cutoff=int(cut['cutoff_log2']);assert cutoff*gap**2>=36 and cutoff*gap>=2056
q=new*(1-2*eta);ticks=(1-eta)*q/(1+q)/grid;k=Q((ticks.numerator-1)//ticks.denominator,10**27);assert k==Q(nom['kappa']);assert min(map(Q,nom['strict_constraints'].values()))>0 and len(nom['strict_constraints'])==47
out={'status':'PASS_INDEPENDENT_SIGNED95_ELEVEN_FINITE_INVOICE_SECOND_ENGINE_BOOTSTRAP_ARITHMETIC','kappa':str(k),'prefix_bits':156,'cube_bits':523,'charged_cube_bits':1024,'row_coefficient':19431,'local_signed_units':v,'incremental_units_per_local':v-u,'moment_profiles_source_bound':True,'scope':'Independently recomputed counted coefficient, both second-engine adjacent-grid signs, closed-form8bootstrap gaps/cutoffs and final strict-grid kappa. Recorded47slacks positive; full inherited outer formulas and all-size chart/compiler/precision/recovery/tape/prime/C_full hypotheses remain separate. Assignment/sigma endpoint gates separate.', 'inputs':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (S/'hosted/GLOBAL.json',S/'hosted/GEOMETRY.json',S/'signed/GLOBAL-BOUND.json',S/'REFINED-NOMINATION.json',S/'signed/signed-records.bin')}}
(P/'SIGNED95-ELEVEN-ARITHMETIC.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
