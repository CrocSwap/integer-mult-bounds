# SPDX-License-Identifier: Apache-2.0
"""Independent PR2863 audit. No package modules or floating point trusted.

The dual is reconstructed from tight primal rows by rational Gaussian
elimination. Transcendentals use exact log series plus alternating exp(-t)
Taylor polynomials evaluated with outward decimal-rational intervals.
Developed with OpenAI Codex assistance; predecessor math belongs to PR2863.
"""
from collections import Counter
from fractions import Fraction as F
from functools import cache
import hashlib, json, math, sys
from pathlib import Path

S = 10**80
WIDTHS = (4, 5, 7, 8, 9)
CAPS = {8:672, 16:448, 32:448, 48:448}
INVENTORY = {4:26, 5:2, 7:62, 8:84, 9:234}
SUPPORT = [(8,(8,),F(672)), (16,(7,9),F(448)),
 (32,(9,9,9),F(120)), (32,(8,8,8,8),F(21)),
 (32,(7,7,9,9),F(55)), (32,(5,9,9,9),F(18)),
 (32,(4,9,9,9),F(234)), (48,(),F(1808,5)),
 (48,(9,9,9,9,9),F(432,5))]
LOW=F('0.00172010080541688592794400')
HIGH=F('0.00172010080541688592794401')

def require(p, label):
    if not p: raise ValueError(label)

def down(x): return F(x.numerator*S//x.denominator,S)
def up(x): return F(-((-x.numerator*S)//x.denominator),S)
def interval(x): return (down(x),up(x))
def plus(a,b): return (down(a[0]+b[0]),up(a[1]+b[1]))
def times(a,b):
    p=[x*y for x in a for y in b]
    return down(min(p)),up(max(p))
def scale(a,c): return times(a,(F(c),F(c)))

def log_reduced(x):
    require(1<=x<=2,'log reduction')
    z=(x-1)/(x+1); term=z; total=F(0)
    # Bound the tail by replacing all remaining denominators by the first.
    for k in range(90):
        total += 2*term/(2*k+1)
        term *= z*z
    tail=2*term/(181*(1-z*z))
    return down(total),up(total+tail)

@cache
def log_n(n):
    k=n.bit_length()-1
    return plus(scale(log_reduced(F(2)),k),log_reduced(F(n,2**k)))

def exp_minus(t, degree):
    # Horner evaluation of sum_{j=0}^degree (-t)^j/j!.
    require(0<=t[0]<=t[1]<1,'alternating remainder scope')
    minus=(-t[1],-t[0]); acc=interval(F(1,math.factorial(degree)))
    for j in range(degree-1,-1,-1):
        acc=plus(times(acc,minus),interval(F(1,math.factorial(j))))
    return acc

@cache
def power(n,alpha):
    if n==0:return F(0),F(0)
    t=scale(log_n(n),alpha)
    # Odd partial sum is a lower bound and even partial sum an upper bound.
    return scale((exp_minus(t,41)[0],exp_minus(t,40)[1]),n)

def clean(p):return {r:c for r,c in p.items() if c}
def poly_add(a,b):
    c=dict(a)
    for r,v in b.items():c[r]=c.get(r,F(0))+v
    return clean(c)
def poly_scale(a,c):return clean({r:v*c for r,v in a.items()})
def H(r):return {r:F(1)} if r else {}
def evaluate(poly,alpha=None):
    out=(F(0),F(0))
    for r,c in poly.items():
        a=power(r,HIGH)[0] if alpha is None else power(r,alpha)[0]
        b=power(r,LOW)[1] if alpha is None else power(r,alpha)[1]
        out=plus(out,scale((a,b),c))
    return out

def reconstruct_dual():
    # Unknowns: 4 capacity prices, 5 helper prices; each is a power polynomial.
    rows=[]
    for cap,widths,_ in SUPPORT:
        counts=Counter(widths)
        rows.append(([F(cap==c) for c in CAPS]+[F(counts[w]) for w in WIDTHS],H(cap-sum(widths))))
    for col in range(9):
        pivot=next((i for i in range(col,9) if rows[i][0][col]),None)
        require(pivot is not None,'unique dual from tight support')
        rows[col],rows[pivot]=rows[pivot],rows[col]
        a,b=rows[col]; d=a[col]
        rows[col]=([v/d for v in a],poly_scale(b,1/d))
        for i in range(9):
            if i==col:continue
            a,b=rows[i]; d=a[col]
            rows[i]=([x-d*y for x,y in zip(a,rows[col][0])],poly_add(b,poly_scale(rows[col][1],-d)))
    return {c:rows[i][1] for i,c in enumerate(CAPS)}, {w:rows[i+4][1] for i,w in enumerate(WIDTHS)}

def patterns(cap, start=0):
    # Recursive bounded weak compositions, independent of producer's product.
    if start==len(WIDTHS):
        yield (),cap; return
    w=WIDTHS[start]
    for n in range(cap//w+1):
        for suffix,left in patterns(cap-n*w,start+1):yield (n,)+suffix,left

def primal_check(support):
    caps=Counter(); inv=Counter(); idle={}
    for cap,widths,count in support:
        require(count>=0 and sum(widths)<=cap,'primal feasible bins')
        caps[cap]+=count
        for w in widths:inv[w]+=count
        idle=poly_add(idle,poly_scale(H(cap-sum(widths)),count))
    require(caps==CAPS,'capacity conservation')
    require(inv=={w:9*n for w,n in INVENTORY.items()},'inventory conservation')
    return idle

def moment(profile,alpha):return evaluate(poly_add(profile,{73:F(-896)}),alpha)
def strings(d):
    if isinstance(d,dict):return {str(k):strings(v) for k,v in d.items()}
    if isinstance(d,(tuple,list)):return [strings(v) for v in d]
    if isinstance(d,F):return str(d)
    return d
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    package=Path(sys.argv[1]); output=Path(sys.argv[2])
    paths=[package/'data/PROVIDERS.json',package/'data/PROFILE.json',package/'review/PROOF.md',package/'CLAIM.json']
    pins={str(p.relative_to(package)):sha(p) for p in paths}
    providers=json.loads(paths[0].read_text()); candidate=json.loads(paths[1].read_text())
    claim=json.loads(paths[3].read_text())
    require(claim['replicas']==185 and claim['live']==185*896 and claim['calls']==185*9,'actual normalization')
    require(claim['helper_roles']==claim['calls']*sum(INVENTORY.values()),'actual role count')
    require(claim['paid_profile']==candidate,'claim profile bound to data')
    require(F(claim['kappa'])==LOW-F(1,10**46)-F(1,10**70),'conservative outer headline only')
    require(F(claim['kappa'])-F(claim['baseline_kappa'])==F(claim['gain_over_full_pr2857']),'exact claimed rational improvement')
    for provider in providers.values():
        require(Counter(provider['widths'])==INVENTORY,'actual ordered inventory')
        require(provider['actual_paid_profile']==providers['extra']['actual_paid_profile'],'common native profile')
    native={int(r):F(n) for r,n in providers['extra']['actual_paid_profile'].items()}
    idle=primal_check(SUPPORT); profile=poly_add(poly_scale(native,9),idle)
    require(profile=={int(r):F(n,185) for r,n in candidate.items()},'actual profile equals feasible optimum')
    capprice,mu=reconstruct_dual()
    dual={}
    for c,n in CAPS.items():dual=poly_add(dual,poly_scale(capprice[c],n))
    for w,n in INVENTORY.items():dual=poly_add(dual,poly_scale(mu[w],9*n))
    require(dual==idle,'exact primal dual equality')
    records=[]; tight=[]; minimum=None
    for c in CAPS:
        for u,r in patterns(c):
            slack=poly_add(H(r),poly_scale(capprice[c],-1))
            for w,n in zip(WIDTHS,u):slack=poly_add(slack,poly_scale(mu[w],-n))
            if not slack:tight.append([c,u,r]); bounds=(F(0),F(0))
            else:
                bounds=evaluate(slack); require(bounds[0]>0,'dual feasibility')
                if minimum is None or bounds[0]<minimum[0]:minimum=(bounds[0],c,u,r,slack)
            records.append(dict(capacity=c,counts=u,remainder=r,slack=slack,interval=bounds))
    require(len(records)==1163 and len(tight)==11,'enumerated pattern count')
    lowmoment=moment(profile,LOW); highmoment=moment(profile,HIGH)
    require(lowmoment[1]<0<highmoment[0],'strict independent root bracket')
    controls=[]
    corrupt=list(SUPPORT); c,w,n=corrupt[2]; corrupt[2]=(c,w,n-1)
    try:primal_check(corrupt)
    except ValueError as e:controls.append('missing bin rejected: '+str(e))
    else:raise ValueError('accepted missing bin')
    corrupt=list(SUPPORT); c,w,n=corrupt[2]
    corrupt[2]=(c,w,n-1); corrupt.append((32,(8,9,9),F(1)))
    try:primal_check(corrupt)
    except ValueError as e:controls.append('unpaid helper change rejected: '+str(e))
    else:raise ValueError('accepted unpaid helper change')
    # A microscopic upward price corruption must fail a tight bin constraint.
    bad=poly_add(mu[9],{1:F(1,10**6)})
    slack=poly_scale(poly_add(poly_add(capprice[16],mu[7]),bad),-1)
    require(evaluate(slack)[1]<0,'reject corrupt dual helper price')
    controls.append('helper-9 price +1e-6 rejected by tight (7,9) bin')
    require(moment(poly_add(profile,H(1)),LOW)[0]>0,'reject one uncharged paid child')
    controls.append('one additional rank-one paid child destroys moment')
    # Every other currently priced helper swap can be screened against this
    # dual marginal. These are bounds, not attainable new constructions.
    thresholds={f'{a}->{b}':evaluate(poly_add(mu[b],poly_scale(mu[a],-1)))
                for a in WIDTHS for b in WIDTHS if a!=b}
    for p in paths:require(sha(p)==pins[str(p.relative_to(package))],'input unchanged')
    result=dict(status='PASS_INDEPENDENT_FIXED_MODEL_AUDIT',pr_head='34328b1d5e5bebac62d5cabec993dfbfd7b2123f',
       input_sha256=pins,arithmetic='exact Fraction log tail; alternating exp(-t) polynomials degrees 40/41; outward decimal rational intervals at scale 10^80',
       dual_reconstruction='nine tight support equations solved by exact rational Gaussian elimination',
       native_profile=native,primal_idle=idle,complete_per_replica=profile,
       dual_capacity=capprice,dual_helper=mu,pattern_count=len(records),tight_count=len(tight),
       minimum_strict_slack=minimum,root_bracket=[LOW,HIGH],moment_at_low=lowmoment,moment_at_high=highmoment,
       negative_controls=controls,marginal_inventory_cost_per_changed_call_role=thresholds,
       scope='All whole-role packings at fixed native paid profile, helper widths/counts, capacities and normalization; no changed circuit or integer multiplication theorem claim.')
    output.mkdir(parents=True,exist_ok=True)
    (output/'RESULT.json').write_text(json.dumps(strings(result),indent=2,sort_keys=True)+'\n')
    (output/'PATTERNS.json').write_text(json.dumps(strings(records),indent=2,sort_keys=True)+'\n')
    print(json.dumps(strings({k:result[k] for k in ['status','pattern_count','tight_count','root_bracket','negative_controls','minimum_strict_slack']}),indent=2))

if __name__=='__main__':main()
