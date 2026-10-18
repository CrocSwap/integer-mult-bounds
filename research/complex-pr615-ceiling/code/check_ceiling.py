"""Exact fixed-supplier ceiling for PR615's inherited capacity geometry.
Independent integer pattern weighting and rational moment intervals; no solver.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import argparse,gzip,hashlib,importlib.util,json
package=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);args=ap.parse_args();work=args.work.resolve()
helper=package/'code/exact_intervals.py'
s=importlib.util.spec_from_file_location('intervals',helper);E=importlib.util.module_from_spec(s);s.loader.exec_module(E)
def require(ok,message):
    if not ok:raise ValueError(message)
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
plan=load(package/'data/PLAN.json');result=load(work/'RESULT.json')
weights={4:-4,5:-41,7:-19,8:-8,9:3};upper={8:-8,16:-16,32:-32,48:0}
paid={};widths={};source_hashes={}
for pid in ('jp8','atm3'):
    raw=work/f'{pid}-local/CANONICAL-WORD.json.gz';canon=load(raw)
    programs=load(work/f'{pid}-local/LOCAL-PROGRAMS.json.gz')
    widths[pid]=[len(canon['frames'][canon['final'][h]])-len(canon['frames'][canon['start'][h]])for h in range(224,728)]
    require(widths[pid]==plan['provider_registry'][pid]['widths'],'actual widths')
    paid[pid]=Counter(g[-1]for g in programs['forward']if g[0]in('climb','center'))
    require(paid[pid]==Counter(g[-1]for g in programs['backward']if g[0]in('climb','center')),'both orientations')
    for artifact in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz'):
        path=work/f'{pid}-local'/artifact;source_hashes[f'{pid}-local/{artifact}']=hashlib.sha256(path.read_bytes()).hexdigest()
capacities=Counter(c for c,times in plan['windows'].values())
require(capacities==Counter({8:48,16:32,32:32,48:32}),'fixed capacity geometry')
stock=112*sum(c*n for c,n in capacities.items())
inventory_weight={pid:sum(weights[w]for w in ws)for pid,ws in widths.items()}
require(inventory_weight=={'jp8':-3042,'atm3':-2046},'supplier weight identity')
capacity_weight=112*sum(upper[c]*n for c,n in capacities.items())
require(capacity_weight-72*inventory_weight['jp8']==4*996,'four-call exact bound')
best={0:0};patterns={0:[]}
for total in range(1,49):
    choices=[(best[total-w]+value,patterns[total-w]+[w])for w,value in weights.items()if total-w in best]
    if choices:best[total],patterns[total]=max(choices)
require(all(best[c]==upper[c]for c in capacities),'all full patterns obey integer weights')
idle0=stock-72*sum(widths['jp8']);dm=sum(widths['jp8'])-sum(widths['atm3'])
require((idle0,dm)==(97200,84),'idle mass identity')
base=Counter({int(k):n for k,n in result['global_profile'].items()})
constructed=Counter({r:68*paid['jp8'][r]+4*paid['atm3'][r]for r in set(paid['jp8'])|set(paid['atm3'])});constructed[48]+=2032
require(base==constructed and sum(r*n for r,n in base.items())==520704,'actual baseline profile')

def add_signed(interval,coefficient,other):
    lo,hi=other
    if coefficient<0:lo,hi=hi,lo
    return interval[0]+coefficient*lo,interval[1]+coefficient*hi

b0=Q(result['complex_lower']);bu=b0+Q(1,10**24)
F={0:(Q(0),Q(0))}
for r in range(1,49):
    lo,hi=E.log(Q(73,r));x,y=E.exp(bu*lo,bu*hi);F[r]=(r*x,r*y)
moment_lower=sum(n*F[r][0]for r,n in base.items())/Q(73*7168)
require(moment_lower>1,'upper endpoint must violate moment')
D=(Q(0),Q(0))
for r in set(paid['jp8'])|set(paid['atm3']):D=add_signed(D,paid['atm3'][r]-paid['jp8'][r],F[r])
D=add_signed(D,Q(7,4),F[48]);require(D[1]<0,'ATM3 improves relaxed ideal-idle cost')
checks=[]
for cap in sorted(capacities):
    for used,value in sorted(best.items()):
        if used>cap:continue
        rem=cap-used;delta=value-upper[cap]
        if rem in (0,48):
            require(delta==0,'zero fragmentation cases');lo=Q(0)
        else:
            gap=(F[rem][0]-Q(rem,48)*F[48][1],F[rem][1]-Q(rem,48)*F[48][0])
            lo,hi=add_signed(gap,Q(delta,996),D)
            require(lo>0,'fragmentation does not pay for extra ATM3: '+str((cap,rem,delta)))
        checks.append(dict(capacity=cap,remainder=rem,maximum_pattern_weight=value,delta=delta,lower_margin=str(lo),maximizing_pattern=patterns[used]))
record=dict(status='PASS_EXACT_PR615_FIXED_SUPPLIER_ALL_DISPATCH_CEILING',
    source_hashes=source_hashes,interval_helper_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),
    weights=weights,capacity_weight_upper=upper,inventory_weight=inventory_weight,
    perfect_idle_atm3_count_upper=4,upper_b=str(bu),upper_kappa=str(bu/(1+bu)),
    moment_lower_at_upper_b=str(moment_lower),ideal_idle_atm3_increment_interval=list(map(str,D)),
    pattern_remainder_checks=checks,
    scope='All 72-call choices of these two exact native suppliers and whole-helper allocations into the fixed 8/16/32/48 capacity inventory, allowing arbitrary times as a relaxation. Uses the inherited native moment and outer conversion kappa < b/(1+b). Does not bound changed suppliers, geometry, compiler, moment, outer conversion, or other multiplication algorithms.')
(work/'EXACT-CEILING.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS',len(checks),'integer pattern/remainder checks; kappa <',record['upper_kappa'],flush=True)
