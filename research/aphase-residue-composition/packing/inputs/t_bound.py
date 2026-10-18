"""Exact one-endpoint all-T pattern bound for unchanged PR2802 inventories.

No claim of native/controller realization at a different replica count.
"""
import collections,json,pathlib
from fractions import Fraction as Q
from net_screen import Screen
HERE=pathlib.Path(__file__).resolve().parent
s=Screen();r=json.loads((HERE/'T-NORMALIZED-RELAXATION.json').read_text())
# Prices reconstructed by the nine active pattern equations, row order:
# capacities8,16,32,48; widths4,5,7,8,9.
prices=[{3:Q(-3,20),48:Q(3,20),5:Q(1,4)},
        {3:Q(-3,10),48:Q(3,10),5:Q(1,2)},
        {3:Q(-3,5),48:Q(3,5),5:Q(1)}, {48:Q(1)},
        {1:Q(1),5:Q(-1)}, {5:Q(-1)},
        {3:Q(1,10),48:Q(-1,10),5:Q(-1,2)},
        {3:Q(3,20),48:Q(-3,20),5:Q(-1,4)},
        {3:Q(1,5),48:Q(-1,5)}]
nb={8:672,16:448,32:448,48:448};widths=s.model['width_alphabet']
rootq=Q(r['root_numerical']);floor=(rootq*10**24).__floor__();lo=Q(floor,10**24);hi=lo+Q(1,10**24)
cache={}
def h(rank,b):
    if not rank:return Q(0),Q(0)
    if (rank,b) not in cache:cache[rank,b]=s.engine.moment(73,1,[(rank,1)],b)
    return cache[rank,b]
def combine(coeff,b,upper=False):
    return sum(n*h(rank,b)[int((n>0)==upper)] for rank,n in coeff.items() if n)
slacks=[];tight=[]
for cap,p in s.checker.patterns:
    c=collections.defaultdict(Q,{cap-sum(p):Q(1)} if cap>sum(p) else {})
    for rank,n in prices[list(nb).index(cap)].items():c[rank]-=n
    for w in p:
        for rank,n in prices[4+widths.index(w)].items():c[rank]-=n
    c={rank:n for rank,n in c.items() if n}
    if not c:tight.append([cap,list(p)]);continue
    lower=combine(c,hi)
    if lower<=0:raise ValueError(('dual slack unresolved',cap,p,str(lower)))
    slacks.append(lower)
# Reconstruct the rational primal and all inventory equations directly.
usedbins=collections.defaultdict(Q);usedwidths=collections.defaultdict(Q);idle=collections.defaultdict(Q)
for cap,p,nstr in r['active_patterns']:
    n=Q(nstr)
    if n<0 or [cap,p] not in tight:raise ValueError('primal uses a nontight/negative pattern')
    usedbins[cap]+=n
    for w in p:usedwidths[w]+=n
    if cap>sum(p):idle[cap-sum(p)]+=n
if dict(usedbins)!=nb or dict(usedwidths)!={w:9*s.model['baseline_inventory'][w] for w in widths}:raise ValueError('primal inventory mismatch')
# Ten replicas clear every denominator. Exact endpoint signs use integer counts.
profile=collections.Counter({rank:90*n for rank,n in s.model['baseline_local'].items()})
for rank,n in idle.items():
    if (10*n).denominator!=1:raise ValueError('T10 nonintegral')
    profile[rank]+=int(10*n)
lower_sign=s.engine.moment(73,1,list(profile.items()),lo)[1]-8960
upper_sign=s.engine.moment(73,1,list(profile.items()),hi)[0]-8960
if not lower_sign<0<upper_sign:raise ValueError('root bracket not certified')
# On every tight column the residual indicator equals its symbolic dual
# coefficient vector. Thus each residual count is fixed by the RHS, even
# though there are eleven tight patterns and the pattern mix is not unique.
forced=collections.defaultdict(Q)
for rhs,price in zip(list(nb.values())+[9*s.model['baseline_inventory'][w] for w in widths],prices):
    for rank,a in price.items():forced[rank]+=rhs*a
forced={rank:n for rank,n in forced.items() if n}
if forced!=dict(idle):raise ValueError('symbolic residual inventory mismatch')
import math
if math.lcm(*(n.denominator for n in forced.values()))!=10:raise ValueError('divisibility mismatch')
report={'status':'PASS_EXACT_UNCHANGED_PR2802_ALL_T_PATTERN_CAP',
        'root_bracket':[str(lo),str(hi)],'upper_cap_decimal':'0.001717795810911820894838',
        'gain_cap_over_PR2818':str(hi-s.leader),
        'gain_cap_float':float(hi-s.leader),'pattern_count':len(s.checker.patterns),
        'strictly_positive_dual_slacks':len(slacks),'tight_patterns':tight,
        'minimum_slack_lower':str(min(slacks)),'lower_endpoint_margin_upper':str(lower_sign),
        'upper_endpoint_margin_lower':str(upper_sign),'idle_per_replica':{k:str(v) for k,v in idle.items()},
        'integral_optimal_pattern_iff_T_multiple_of':10,
        'examples':{T:{'calls':9*T,'live':896*T,'physical':896*T+408+8+72+2,'complete_pattern_integral':T%10==0} for T in [70,73,74,75,76,80]},
        'scope':'All positive T with fixed PR2802 local profile, widths and per-replica bins; exact pattern endpoint cap and forced optimum-residual divisibility at this endpoint. Does not establish chronological owners or a changed-T native/controller/precision/outer assembly.'}
(HERE/'T-EXACT-BOUND.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='gain_cap_over_PR2818'},indent=2))
