"""Exact all-T continuous packing cap for the authenticated PR2833 providers.

Reuses the pinned prior symbolic dual, independently enumerates every integer
bin pattern, solves its nine-column primal exactly, and uses the unchanged
PR2827 rational moment engine. No solver or chronological construction runs.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from decimal import Decimal,localcontext
from functools import lru_cache
import argparse,ast,gzip,hashlib,json,math,types
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--bundle',type=Path,default=HERE.parent/'independent')
ap.add_argument('--owner',type=Path,required=True)
ap.add_argument('--moment',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args();BUNDLE=args.bundle.resolve();OUT=args.out.resolve()
if OUT.exists() or OUT.is_relative_to(HERE.parent) or OUT.is_relative_to(BUNDLE):raise ValueError('fresh output outside source package and bundles required')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw)if p.suffix=='.gz'else raw)
def dec(x):
 with localcontext()as c:c.prec=45;return str(Decimal(x.numerator)/Decimal(x.denominator))
PINS={'t_bound.py':'05bbea18531e4bb7ab3328a7def93db60e6cf5b0321aafedb0a8a7f5f971726b','T-NORMALIZED-RELAXATION.json':'846e24ff966402091534a766334bc737cb24b71b225ef978a8932111493a02c3','moment.py':'f6f38ef8e8fc1e634a2f89a45f3bf721f166a05313cec86c7a5cef9075e86be3'}
inputs=HERE/'inputs'
for n,pin in PINS.items():need(sha(inputs/n)==pin,'pinned arithmetic source '+n)
engine_source=inputs/'moment.py'
need(sha(BUNDLE/'source/independent_candidate_moment_retired7.py')==PINS['moment.py'],'same unchanged independent moment source')
bound_inputs=[inputs/n for n in PINS]+[BUNDLE/'source/independent_candidate_moment_retired7.py',BUNDLE/'provider/PROVIDERS.json',BUNDLE/'provider/GLOBAL-TEMPLATE.json.gz',BUNDLE/'provider/OUTER-CLAIM.json',args.owner,args.moment]
before={str(p.resolve()):sha(p)for p in bound_inputs}
engine=types.ModuleType('pinned_independent_moment');exec(compile(engine_source.read_bytes(),'pinned_independent_moment.py','exec'),engine.__dict__)
assign=next(n for n in ast.parse((inputs/'t_bound.py').read_bytes()).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='prices'for t in n.targets))
ctx={'Q':Q};exec(compile(ast.Module(body=[assign],type_ignores=[]),'<exact pinned symbolic dual>','exec'),ctx);prices=ctx['prices']
registry_path=BUNDLE/'provider/PROVIDERS.json';need(sha(registry_path)=='3666edf67d61b01336e58166ec9edebd72902cc37a2da693b05691ab2a387cda','actual P33 registry pin')
registry=read(registry_path);need(registry['gauge44']==registry['extra'],'same actual provider inventory/profile')
inventory=Counter(registry['gauge44']['widths']);local={int(k):v for k,v in registry['gauge44']['actual_paid_profile'].items()}
need(inventory=={4:26,5:2,7:62,8:80,9:238}and local=={1:2382,2:650,3:266,4:128,5:26,8:8},'P33 actual inventory/profile')
template_path=BUNDLE/'provider/GLOBAL-TEMPLATE.json.gz';need(sha(template_path)=='1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db','actual template pin')
template=read(template_path);bins=dict(sorted(Counter(c['rank']for c in template['idle_children']).items()))
need(len({(c['child'],c['port'])for c in template['idle_children']})==18*112,'one source bin per child and port')
need(bins=={8:672,16:448,32:448,48:448},'per-replica source bins')
caps=list(bins);widths=sorted(inventory);rhs=[Q(n)for n in bins.values()]+[Q(9*inventory[w])for w in widths]
patterns=[]
def enumerate_patterns(cap,start=0,items=()):
 patterns.append((cap,items))
 for i in range(start,len(widths)):
  if sum(items)+widths[i]<=cap:enumerate_patterns(cap,i,items+(widths[i],))
for cap in caps:enumerate_patterns(cap)
need(len(patterns)==1163 and len(set(patterns))==1163,'complete distinct pattern enumeration')
basis=[(cap,tuple(p))for cap,p,_ in read(inputs/'T-NORMALIZED-RELAXATION.json')['active_patterns']]
def column(cap,p):return [Q(c==cap)for c in caps]+[Q(p.count(w))for w in widths]
cols=[column(c,p)for c,p in basis];matrix=[[cols[j][i]for j in range(9)]+[rhs[i]]for i in range(9)]
for j in range(9):
 pivot=next(i for i in range(j,9)if matrix[i][j]);matrix[j],matrix[pivot]=matrix[pivot],matrix[j]
 scale=matrix[j][j];matrix[j]=[x/scale for x in matrix[j]]
 for i in range(9):
  if i!=j:
   q=matrix[i][j];matrix[i]=[a-q*b for a,b in zip(matrix[i],matrix[j])]
counts=[matrix[j][-1]for j in range(9)];need(all(n>=0 for n in counts),'nonnegative exact primal')
need([sum(cols[j][i]*counts[j]for j in range(9))for i in range(9)]==rhs,'all nine primal inventory equations')
idle=defaultdict(Q)
for (cap,p),n in zip(basis,counts):
 if cap>sum(p):idle[cap-sum(p)]+=n
idle=dict(idle);need(idle=={1:Q(234),3:Q(441,5),5:Q(129),48:Q(1799,5)},'normalized P33 idle')
hist=Counter({r:9*n for r,n in local.items()});hist.update(idle)
need(sum(r*n for r,n in hist.items())==65088,'normalized complete rank mass')
L,H=0.,.002
for _ in range(60):
 q=(L+H)/2;value=sum(float(n)*r*math.exp(q*math.log(73/r))for r,n in hist.items())/(73*896)
 if value<1:L=q
 else:H=q
grid=10**24;unit=10**12;mid=int(((L+H)/2)*10**12)*unit;L,H=mid-unit,mid+2*unit
while engine.moment(hist,Q(L,grid),896)[1]>=1:L-=unit
while engine.moment(hist,Q(H,grid),896)[0]<=1:H+=unit
while H-L>1:
 m=(L+H)//2;a,b=engine.moment(hist,Q(m,grid),896)
 if b<1:L=m
 elif a>1:H=m
 else:raise ValueError('independent moment enclosure too wide')
lo,hi=Q(L,grid),Q(H,grid);lower=engine.moment(hist,lo,896);upper=engine.moment(hist,hi,896)
need(lower[1]<1<upper[0],'directed strict continuous-root bracket')
@lru_cache(None)
def h(rank,q):return engine.moment({rank:1},q,1)if rank else(Q(0),Q(0))
def coeff(cap,p):
 c=defaultdict(Q,{cap-sum(p):Q(1)}if cap>sum(p)else{})
 for r,n in prices[caps.index(cap)].items():c[r]-=n
 for w in p:
  for r,n in prices[4+widths.index(w)].items():c[r]-=n
 return {r:n for r,n in c.items()if n}
slacks=[];tight=[]
for cap,p in patterns:
 c=coeff(cap,p)
 if not c:tight.append((cap,p));continue
 # Signed interval combination gives a rigorous lower slack, including all
 # negative price coefficients, at the cap's strict upper endpoint.
 slack=sum(n*h(r,hi)[0 if n>0 else 1]for r,n in c.items())
 need(slack>0,'all-column directed dual feasibility');slacks.append(slack)
need(all(p in tight for p in basis),'primal supported on symbolically tight columns')
forced=defaultdict(Q)
for b,price in zip(rhs,prices):
 for r,c in price.items():forced[r]+=b*c
forced={r:n for r,n in forced.items()if n};need(forced==idle,'symbolic primal/dual objective equality')
owner_path=args.owner;moment_path=args.moment;claim_path=BUNDLE/'provider/OUTER-CLAIM.json'
owner=read(owner_path);actual=read(moment_path);claim=read(claim_path)
need(owner['replicas']==124 and owner['status']=='PASS_INDEPENDENT_T_OWNER_CHRONOLOGY_MASKS'and len(owner['controls'])==7,'actual complete T124 geometry')
need(actual['status']=='PASS_INDEPENDENT_EXACT_CANDIDATE_MOMENT'and len(actual['controls'])==5 and actual['input_sha256']['owner_receipt']==sha(owner_path),'actual exact moment binding')
need(sha(claim_path)=='6f2c4195f0226c5a7f9ba604bc038cfd4100ba3caeeac8ed2defb6fb00632b70'and actual['best_claim_sha256']==sha(claim_path),'full exact headline comparator binding')
previous=Q(claim['kappa']);need(previous==Q(claim['kappa_rational']),'full exact headline equality')
target=Q(actual['proposed_outer_target']);gain=target-previous;need(0<gain<lo-previous,'positive realized gain below packing cap')
ratio_lo=gain/(hi-previous);ratio_hi=gain/(lo-previous)
tail={r:Q(owner['idle'].get(str(r),0))-124*idle.get(r,Q(0))for r in set(map(int,owner['idle']))|set(idle)};tail={r:n for r,n in tail.items()if n}
report=dict(status='PASS_EXACT_PR2833_ALL_T_CONTINUOUS_PATTERN_CAP',source_head='e9307b48d7d1b690939935ecef0f8e524e6d92f4',arithmetic_source_sha256=PINS,provider_registry_sha256=sha(registry_path),template_sha256=sha(template_path),comparison_claim_sha256=sha(claim_path),pattern_count=len(patterns),strict_positive_dual_slacks=len(slacks),tight_pattern_count=len(tight),tight_patterns=[[c,list(p)]for c,p in tight],minimum_dual_slack_lower=str(min(slacks)),symbolic_dual_prices=[{r:str(n)for r,n in p.items()}for p in prices],normalized_primal=[[c,list(p),str(n)]for(c,p),n in zip(basis,counts)],normalized_idle={r:str(n)for r,n in idle.items()},normalized_profile={r:str(n)for r,n in sorted(hist.items())},root_bracket=[str(lo),str(hi)],root_bracket_decimal=[dec(lo),dec(hi)],lower_moment_minus_one_upper=str(lower[1]-1),upper_moment_minus_one_lower=str(upper[0]-1),gain_cap_over_full_P33_bracket=[str(lo-previous),str(hi-previous)],gain_cap_over_full_P33_decimal=[dec(lo-previous),dec(hi-previous)],actual_T124=dict(owner_receipt_sha256=sha(owner_path),moment_receipt_sha256=sha(moment_path),proposed_outer_target=str(target),gain_over_full_P33=str(gain),gain_decimal=dec(gain),gain_fraction_of_continuous_cap_bracket=[str(ratio_lo),str(ratio_hi)],gain_fraction_decimal=[dec(ratio_lo),dec(ratio_hi)],additive_idle_tail={r:str(n)for r,n in tail.items()}),scope='Upper cap for every positive replica count with fixed PR2833 local paid profiles, width inventory, bin capacities and live896T normalization. The dual relaxes chronology/family/physical/native constraints, so it is an upper bound, not an integer or chronological attainment claim. The exact feasible continuous primal certifies the relaxation. T124 gain-fraction uses its independently certified proposed finite-moment target; full changed native/global/outer admission remains separate.')
need(before=={str(p.resolve()):sha(p)for p in bound_inputs},'input drift during cap proof')
OUT.parent.mkdir(parents=True,exist_ok=True)
with OUT.open('x',encoding='utf8',newline='\n')as target:target.write(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k]for k in ['status','pattern_count','strict_positive_dual_slacks','tight_pattern_count','normalized_idle','root_bracket_decimal','gain_cap_over_full_P33_decimal']},indent=2));print('actual_gain_fraction',dec(ratio_lo),dec(ratio_hi))
