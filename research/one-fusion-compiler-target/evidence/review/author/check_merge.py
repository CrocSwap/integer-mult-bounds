#!/usr/bin/env python3
"""Static source census and exact rational interval check, no native evaluation.
Prepared with substantial OpenAI Codex assistance; preserves Cao Yifan/#4610
and DreamingOfClouds/#5226 attribution. No root extraction or compiler replay.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256, sha1
from pathlib import Path
import gzip, json, re

HERE=Path(__file__).resolve().parent
F=HERE/'frozen'
def need(x, why):
    if not x: raise ValueError(why)
def logsmall(z):
    need(0<=z<=Q(1,3),'log reduced domain')
    n=40
    s=sum((2*z**(2*j+1)/(2*j+1) for j in range(n)),Q(0))
    return s,s+2*z**(2*n+1)/((2*n+1)*(1-z*z))
def logint(r):
    k=r.bit_length()-1;x=Q(r,2**k)
    a,b=logsmall((x-1)/(x+1));c,d=logsmall(Q(1,3))
    return a+k*c,b+k*d
def alt(x,n):
    need(0<=x<Q(1,50),'alternating exponential domain')
    s=term=Q(1)
    for j in range(1,n+1):term*=-x/j;s+=term
    return s
def power(r,C):
    a,b=logint(r)
    return r*alt(C*b,17),r*alt(C*a,18)
def moment(h,C):
    vals=[(n,power(r,C)) for r,n in h.items()]
    return tuple(sum((n*p[i] for n,p in vals),Q(0)) for i in (0,1))
def sub(a,b):return a[0]-b[1],a[1]-b[0]
def scale(a,n):return tuple(sorted((a[0]*n,a[1]*n)))
def dec(q,up=False):
    n=(q*10**30).__ceil__() if up else (q*10**30).__floor__()
    return ('-' if n<0 else '')+str(abs(n)//10**30)+'.'+str(abs(n)%10**30).zfill(30)
def interval(x):return {'lower':dec(x[0]),'upper':dec(x[1],True)}
def add(a,b):return a[0]+b[0],a[1]+b[1]
def rank(vs):
    basis={}
    for x in vs:
        while x:
            k=x.bit_length()-1
            if k not in basis:basis[k]=x;break
            x^=basis[k]
    return len(basis)

def main():
    A=json.loads((F/'4610-ARITHMETIC.json').read_text())
    H={int(k):n for k,n in A['local_helpers'].items()}
    N={int(k):n for k,n in A['local_paid'].items()}
    T={int(k):n for k,n in A['targets'].items()}
    P={int(k):n for k,n in A['paid'].items()}
    lean=(F/'4610-NumericalMoments.lean').read_text()
    def poly(name):
        s=re.search('def '+name+r' \(t : ℝ\) : ℝ :=(.*?)\n\n',lean,re.S).group(1)
        return {int(r):int(n) for n,r in re.findall(r'(\d+) \* \((\d+) : ℝ\) \^ t',s)}
    need(T==poly('targetMoment') and P==poly('paidMoment'),'public polynomial binding')
    t=Counter({r:18*n for r,n in H.items()});p=Counter({r:18*n for r,n in N.items()})
    t[145]+=224;p[1]+=15*112
    for length in (7,8):
        for j in range(1,length+1):t[1+8*(j+1)]+=224;p[8*(j+1)]+=224
    need(t==T and p==P,'18 LOCAL +15 thin +full IDLE/target formula')
    w=json.loads(gzip.decompress((F/'4610-ACTUAL-WORD.json.gz').read_bytes()))
    c=w['canonical'];frames=c['frames'];nf=len(c['start'])
    need(nf==632 and sum(H.values())==408,'distinct input census')
    R=[len(frames[c['final'][f]])-len(frames[c['start'][f]]) for f in range(nf)]
    need(R[:224]==[8]*224 and Counter(R[224:])==Counter(H),'net ranks')
    profile_results={}
    for direction,events in w['programs'].items():
        cur=list(c['start']);jobs=defaultdict(list);centres=0;warps=0
        for e in events:
            if e[0]=='climb':
                f,a,b,r=e[2:6];E,G=frames[a],frames[b]
                need(cur[f]==a and r==len(G)-len(E)>0,'climb chronology')
                need(rank(E)==len(E) and rank(G)==len(G) and rank(E+G)==len(G),'actual nested subspaces')
                jobs[f].append(r);cur[f]=b
            elif e[0]=='warp':
                f=e[1][1];a,b=e[3:5]
                need(cur[f]==a and len(frames[a])==len(frames[b]),'warp dimensions')
                cur[f]=b;warps+=1
            elif e[0]=='center':centres+=1
        need(cur==c['final'] and all(sum(jobs[f])==R[f] for f in range(nf)),'endpoint telescoping')
        h=Counter(r for js in jobs.values() for r in js);h[8]+=centres
        need(h==Counter(N) and centres==8 and warps==240,'exact local paid census')
        profile_results[direction]={'climbs':sum(len(js) for js in jobs.values()),'centres':centres,'warps':warps}
    C=Q('.0030233')
    base=sub(moment(T,C),moment(P,C))
    phi=sub(moment(H,C),moment(N,C))
    lam=sub(scale(power(8,C),-232),phi)
    # Gamma=full invoice minus18phi; Lambda*=Gamma/18-232*8^t.
    gamma=sub(base,scale(phi,18))
    star=sub(scale(gamma,Q(1,18)),scale(power(8,C),232))
    gain=sub((Q(2),Q(2)),power(2,C))
    gap=sub(lam,star)
    scenarios={}
    for m in (0,1,4,5):
        n=N.copy();n[1]-=2*m;n[2]+=m
        paid=P.copy();paid[1]-=36*m;paid[2]+=18*m
        result=sub(moment(T,C),moment(paid,C))
        predicted=add(base,scale(gain,18*m))
        need(max(result[0],predicted[0])<=min(result[1],predicted[1]),'independent delta agreement')
        need(result[1]<0 if m<5 else result[0]>0,'one/four fail and five pass raw bar')
        need(sum(r*x for r,x in paid.items())==sum(r*x for r,x in P.items()),'paid rank mass unchanged')
        scenarios[str(m)]={'local_paid':n,'whole_paid_H1':paid[1],'whole_paid_H2':paid[2],
            'whole_paid_count':sum(paid.values()),'whole_margin':interval(result),
            'per_native_residual_gain':interval(add(scale(gain,m),scale(gap,-1)))}
    one_whole=add(base,gain)
    need(one_whole[1]<0,'a single merge in whole caller also fails')
    lower_bar=Q('.003022')
    one_paid=P.copy();one_paid[1]-=36;one_paid[2]+=18
    one_lower=sub(moment(T,lower_bar),moment(one_paid,lower_bar))
    need(one_lower[0]>0,'one repeated pair does improve raw sign at a fixed smaller bar')
    # Negative controls distinguish wrong counting and free deletion from merging.
    controls={'single_whole_merge_does_not_meet_bar':one_whole[1]<0,
      'four_per_native_does_not_meet_bar':Q(scenarios['4']['whole_margin']['upper'])<0,
      'five_per_native_meets_raw_bar':Q(scenarios['5']['whole_margin']['lower'])>0,
      'merge_has_no_rank_mass_credit':sum(r*n for r,n in N.items())==sum(r*n for r,n in scenarios['1']['local_paid'].items()),
      'centre_retained':scenarios['5']['local_paid'][8]==8,
      'helper_once':sum(T.values())==10928 and 18*sum(H.values())==7344}
    need(all(controls.values()),'controls')
    out={'status':'PASS_STATIC_CENSUS_AND_CONDITIONAL_RAW_PROFILE_ARITHMETIC',
      'bar':str(C),'source_native_profile':N,'helpers':H,'native_paid_count':sum(N.values()),
      'native_paid_rank_mass':sum(r*n for r,n in N.items()),'whole_target_count':sum(T.values()),
      'whole_paid_count':sum(P.values()),'whole_rank_mass_surplus':sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items()),
      'static_profiles':profile_results,'baseline_margin':interval(base),'lambda':interval(lam),'lambda_star':interval(star),
      'per_native_gap':interval(gap),'one_merge_gain':interval(gain),'scenarios':scenarios,'controls':controls,
      'one_pair_fixed_lower_bar':{'saving':str(lower_bar),'margin':interval(one_lower),'first_crossing_and_funding_proved':False},
      'method':'rational log atanh40 with geometric tail; alternating exp(-C log r)17/18; outward decimal30 display',
      'scope':'formal unchanged-target profile only; no physical pair, funded compiler, first-crossing sufficiency or kappa admission',
      'source_sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(F.iterdir()) if p.is_file()}}
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__':main()
