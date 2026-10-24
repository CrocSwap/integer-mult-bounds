#!/usr/bin/env python3
"""Independent directed scalar and literal census screen of PR5377.

Does not import/run either PR5377 interval engine or native verifier. Uses
newly written atanh60/Taylor32 directed rationals; reuses the separately
implemented PR5241 outer ledger formula only, explicitly below.
Substantial OpenAI Codex assistance. Predecessors: Cao Yifan, Cinna Davis,
zxv, Jacob Alan Sussman and Chris R/Clear1nsight.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import ast,gzip,json,hashlib,time
F=Path(__file__).resolve().parent/'frozen'
UNIT=10**55
def need(ok,s):
    if not ok: raise ValueError(s)
def dn(x):return Q(x.numerator*UNIT//x.denominator,UNIT)
def up(x):return -dn(-x)
def mul(a,b):
    v=[x*y for x in a for y in b];return dn(min(v)),up(max(v))
def div(a,b):
    need(b[0]>0,'positive divisor');return mul(a,(1/b[1],1/b[0]))
def logsmall(x):
    z=(x-1)/(x+1);s=Q(0);term=z
    need(0<=z<=Q(1,3),'log domain')
    for j in range(60):s+=2*term/(2*j+1);term*=z*z
    return dn(s),up(s+2*term/(121*(1-z*z)))
@lru_cache(None)
def logint(n):
    k=n.bit_length()-1;a,b=logsmall(Q(n,2**k));c,d=logsmall(Q(2));return a+k*c,b+k*d
def expone(x):
    if x<0:
        a,b=expone(-x);return dn(1/b),up(1/a)
    s=term=Q(1);shift=0
    while x>Q(1,32):x/=2;shift+=1
    for j in range(1,33):term*=x/j;s+=term
    tail=term*x/33/(1-x/34);a,b=dn(s),up(s+tail)
    for _ in range(shift):a,b=dn(a*a),up(b*b)
    return a,b
@lru_cache(None)
def power(r,t):
    a,b=logint(r);a,b=sorted([a*t,b*t]);return expone(a)[0],expone(b)[1]
def moment(p,t):return tuple(sum((n*power(r,t)[i] for r,n in p.items()),Q(0)) for i in (0,1))
def minus(a,b):return a[0]-b[1],a[1]-b[0]
def scalar(g):
    if g[0] in ('copy','clear'):return 2
    q=Q(*g[3:]) if g[0]=='add' else Q(*g[2:]);n,d=abs(q.numerator),q.denominator
    need(n>0 and d&(d-1)==0,'dyadic scalar')
    if g[0]=='scale':
        need(n&(n-1)==0,'dyadic unit');return 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
    need(g[0]=='add','scalar opcode');return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
def read(n):
    p=F/n;b=p.read_bytes();return json.loads(gzip.decompress(b) if n.endswith('.gz') else b)
def enc(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):enc(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [enc(v) for v in x]
    return x
def main():
    start=time.monotonic();src=read('ACTUAL-WORD.json.gz');cand=read('WORD.json.gz');ctl=read('controller-CONTROLLER.json');old=read('4610-round6-ARITHMETIC.json');author=read('RESULT.json')['arithmetic']
    local={};cost={};T=Counter();P=Counter();orient=Counter();queries=0
    c=cand['canonical']
    for d,events in cand['programs'].items():
        paid=Counter();cost[d]=0
        for e in events:
            if e[0] in ('climb','center'):paid[e[-1]]+=1
            elif e[0]=='scalar':cost[d]+=scalar(e[1])
        helpers=Counter(len(c['frames'][c['final'][i]])-len(c['frames'][c['start'][i]]) for i in range(224,632) if not (d=='backward' and i==230))
        local[d]=(paid,helpers)
        oldcost=sum(scalar(e[1]) for e in src['programs'][d] if e[0]=='scalar')
        need(cost[d]-oldcost==(46 if d=='backward' else 0),'all changed scalar operations charged')
    for e in ctl['physical_events']:
        if e[0]=='LOCAL':
            d='backward' if e[3] else 'forward';orient[d]+=1;P.update(local[d][0]);T.update(local[d][1])
        elif e[0]=='QUERY_SHEAR':queries+=1;P[1]+=112
        elif e[0]=='IDLE':P[8*len(e[2])]+=224
    for term in ctl['diagonal']:T[1+8*sum(term[1:])]+=112
    need(orient=={'backward':16,'forward':2} and queries==15,'literal controller orientations')
    priorT=Counter({int(k):v for k,v in old['targets'].items()});priorP=Counter({int(k):v for k,v in old['paid'].items()});priorT[9]-=16;priorP[1]-=16;priorP[8]-=16
    need(T==priorT and P==priorP,'old-to-new exact complete delta')
    need(dict(T)=={int(k):v for k,v in author['targets'].items()} and dict(P)=={int(k):v for k,v in author['paid'].items()},'author invoice crosscheck')
    need((sum(T.values()),sum(P.values()))==(10912,64372),'complete census')
    masses=[sum(r*n for r,n in p.items()) for p in (T,P)];need(masses==[239742,238990],'rank masses')
    k,s=Q('.00302235'),Q('.00302236');gap=(s-k)/7;t=1-s
    lo,hi=Q('.00302238736347'),Q('.00302238736348')
    signs=[minus(moment(T,1-x),moment(P,1-x)) for x in [lo,hi]]
    need(signs[0][0]>0>signs[1][1] and k<s<lo,'root endpoints and strict headroom')
    target,paid=moment(T,t),moment(P,t)
    ratios={'alpha':div(paid,target),'gamma':div(moment(P,t+Q(1,5)),mul(power(20,Q(1,5)),target)),'delta':div((Q(sum(T.values())*21),)*2,mul(power(20,s),target))}
    reserve=Q(1,10**9);theta=Q(63,64)
    need(ratios['alpha'][1]<1-reserve and all(ratios[x][1]<Q(97,100) for x in ['gamma','delta']),'reserve and both charged tails')
    for n,v in ratios.items():need(Q(author['strictification'][n]['lower'])<=v[0]<=v[1]<=Q(author['strictification'][n]['upper']),'author outward interval contains independent '+n)
    normalized=1/(1+1024*reserve)+Q(4,2**32);eta=mul((t,t),power(145,-1024*s))
    capacity={'normalized':normalized<1,'tail_block':Q(97,100)**128<Q(1,16),'total_tails':4*Q(97,100)**1024<Q(4,2**32),'split':20**64<21**63,'shifted_exits':2*(20**1024)**64<=(145**1024)**63,'eta':eta[0]>theta**1000,'initial_range':power(145,1024*s)[1]<2**1000}
    H,j=31385200000000,44836;step=gap.denominator
    capacity.update(height_encoding=H==step*j and gap==Q(1,700000000),height_domain=H>8*1024,integer_success=(H+1)**1000<2**j,preceding_grid_fails=(step*(j-1)+1)**1000>=2**(j-1))
    need(all(capacity.values()),'finite compiler capacities')
    # Concavity of log(step*j+1)-j*log(2)/1000 gives one positive
    # crossing; success and preceding-grid failure establish grid minimality.
    signed={r:T[r]-P[r] for r in T.keys()|P.keys()};derivative_lowers=[];away_uppers=[]
    for i in range(16):
        l,r=Q(i,320),Q(i+1,320);bound=Q(0)
        for rank,n in signed.items():
            term=mul(power(rank,1-r if n>0 else 1-l),logint(rank));bound+=n*term[0 if n>0 else 1]
        derivative_lowers.append(bound)
    for i in range(128):
        l,r=Q(1,20)+Q(19*i,2560),Q(1,20)+Q(19*(i+1),2560)
        away_uppers.append(sum(n*power(rank,1-l if n>0 else 1-r)[1 if n>0 else 0] for rank,n in signed.items()))
    need(min(derivative_lowers)>0 and max(away_uppers)<0,'global fixed-profile root uniqueness')
    # Independently transcribed selected5241 ledger, not the author ledger.
    tree=ast.parse((F/'compiler.py').read_text());node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='ledger');ns={'F':Q};exec(compile(ast.Module(body=[node],type_ignores=[]),str(F/'compiler.py'),'exec'),ns)
    params=dict(kappa=k,tested_saving=s,complex_uniform_saving=k+6*gap,b=k+5*gap,a=k+4*gap,q=k+3*gap,bit_saving=Q('.0034'),epsilon=1-gap,beta=1-3*gap,r0=gap/10,stop=gap,layout=gap,d=gap)
    m,strict,func=ns['ledger'](params)
    for group,values in [('margins',m),('strict_checks',strict),('functional_checks',func)]:need(values=={n:Q(v) for n,v in author['outer'][group].items()},'54+4 outer values agree '+group)
    need(len(strict)==54 and len(func)==4 and min(strict.values())>0 and min(func.values())>0,'complete outer inventory')
    controls={}
    for name,patch in [('old_BIT',{'bit_saving':Q('.0027')}),('closed_uniform',{'complex_uniform_saving':params['b']}),('unfunded_endpoint',{'kappa':s}),('closed_epsilon',{'epsilon':Q(1)})]:
        _,bad,_=ns['ledger'](dict(params,**patch));controls[name]=[n for n,v in bad.items() if v<=0];need(controls[name],'outer control '+name)
    bit=author['ordinary_BIT'];ordinary=(1-Q(bit['atom']))*Q(bit['after_cover'])+Q(bit['atom'])*Q('.0000384599');need(Q(bit['ordinary_saving'])==ordinary and Q(bit['atom'])>ordinary>Q(bit['admitted'])>s,'unchanged ordinary BIT domain')
    routes=(max(sum(x[0].values()) for x in local.values())+2*408+688+4)*1000
    raw=18*10**7+15*1792+32*112*(len(ctl['physical_events'])+sum(len(ctl['boundaries'][x+'_program']) for x in ['left','right']))
    need(routes==4806000 and max(cost.values())==158214 and routes+max(cost.values())<10**7 and raw==181098496<10**9,'fresh raw costs')
    out=dict(status='PASS_INDEPENDENT_SCALAR_CENSUS_MOMENT_COMPILER_OUTER_SCREEN',head='c448d13c71908647f968b06cddb795ce7d288139',kappa=k,tested=s,gain=k-Q('.0030217758'),root=[lo,hi],root_signs=signs,targets=T,paid=P,rank_masses=masses,local_scalar=cost,local_routes=routes,raw=raw,ratios=ratios,normalized=normalized,capacity=capacity,eta=eta,derivative_upper=-min(derivative_lowers),away_moment_upper=max(away_uppers),outer_min=min(strict.values()),outer_strict_count=len(strict),outer_functional_count=len(func),controls=controls,gap=gap,uniform_saving=k+6*gap,H=H,j=j,seconds=time.monotonic()-start,independent_native_replay=False,expanded_word_materialized=False,scope='Finite scalar/census check. Physical replacement and all-f specialization reviewed separately; same five conditional assumptions retained. Raw bound is not an expanded precision/storage bound.',sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in F.iterdir() if p.is_file()})
    print(json.dumps(enc(out),indent=2,sort_keys=True))
if __name__=='__main__':main()
