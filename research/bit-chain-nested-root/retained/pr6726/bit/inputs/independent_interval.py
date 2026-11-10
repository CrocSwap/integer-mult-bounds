#!/usr/bin/env python3
"""Independent rational arithmetic for the complete exchanged-forest invoice.

The interval implementation below is new and imports no proposer arithmetic.
Logarithms use an atanh series after binary range reduction; exponentials use
a positive Taylor series with a geometric bound on the full remainder.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from collections import Counter
import hashlib, json, time

HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):
    z=[x*y for x in a for y in b]
    return min(z),max(z)
def div(a,b):
    need(b[0]>0,'positive interval divisor')
    return mul(a,(1/b[1],1/b[0]))

def small_log(z):
    # log((1+z)/(1-z)), 0<=z<=1/3.
    need(0<=z<=Q(1,3),'range-reduced logarithm')
    acc=Q(0);term=z;N=40
    for k in range(N):
        acc+=term/Q(2*k+1);term*=z*z
    lo=2*acc;tail=2*term/(Q(2*N+1)*(1-z*z))
    return lo,lo+tail

@lru_cache(None)
def logarithm(r):
    need(r>=1,'positive integer rank')
    k=r.bit_length()-1;z=Q(r-(1<<k),r+(1<<k))
    a=small_log(Q(1,3));b=small_log(z)
    return k*a[0]+b[0],k*a[1]+b[1]

def exponential_at(z):
    if z<0:
        a,b=exponential_at(-z);return 1/b,1/a
    need(z<=4,'exponential range')
    acc=Q(1);term=Q(1);N=64
    for k in range(1,N+1):term*=z/k;acc+=term
    nxt=term*z/(N+1)
    return acc,acc+nxt/(1-z/(N+2))

@lru_cache(None)
def power(r,a):
    # Separate integer rank from the exponential for the near-one exponents.
    a=Q(a);v=mul((a-1,a-1),logarithm(r))
    lo=exponential_at(v[0])[0];hi=exponential_at(v[1])[1]
    return r*lo,r*hi

def moment(hist,a):
    out=(Q(0),Q(0))
    for r,n in hist.items():
        z=power(int(r),a);out=add(out,(n*z[0],n*z[1]))
    return out

def bounds_text(x,places=22):
    scale=10**places
    lo=(x[0]*scale).__floor__();hi=-((-x[1]*scale).__floor__())
    def show(z):
        sign='-' if z<0 else '';z=abs(z)
        return f'{sign}{z//scale}.{z%scale:0{places}d}'
    return {'lower':show(lo),'upper':show(hi)}

def audit(functional=False,version02=False,version04=False,version05=False,version06=False,version07=False):
    started=time.monotonic();base=HERE.parent/'architecture'
    receipt_name='FUNCTIONAL-KERNEL-07-FOREST-F19-ADMISSION.json'if version07 else'FUNCTIONAL-KERNEL-06-FOREST-F19-ADMISSION.json'if version06 else'FUNCTIONAL-KERNEL-05-FOREST-F19-ADMISSION.json'if version05 else'FUNCTIONAL-KERNEL-04-FOREST-F19-ADMISSION.json'if version04 else'FUNCTIONAL-KERNEL-02-FOREST-F19-ADMISSION.json'if version02 else'FUNCTIONAL-KERNEL-FOREST-F19-ADMISSION.json'if functional else'EXCHANGE-FOREST-F19-ADMISSION.json'
    receipt=json.loads((base/receipt_name).read_text())
    constants={
      'complex':(104,8,{1:18,2:7,3:4,4:107,5:14,7:9,8:18,9:385},
                 {1:2225,2:456,3:498,4:98,5:163,6:9,7:6}),
      'bit':(111,7,{4:30,8:419},{1:1411,2:1250,3:89,4:50,5:10,6:102,7:7})}
    if functional:constants['bit']=(111,7,{4:10,8:440},{1:1402,2:1229,3:69,4:49,5:10,6:123,7:18})
    if version02:constants['bit']=(111,7,{4:10,8:433},{1:1395,2:1236,3:62,4:49,5:10,6:116,7:18})
    if version04:constants['bit']=(111,7,{4:11,8:424},{1:1386,2:1244,3:55,4:50,5:8,6:108,7:18})
    if version05:constants['bit']=(111,7,{4:19,8:416},{1:1386,2:1245,3:62,4:49,5:9,6:108,7:10})
    if version06:constants['bit']=(111,7,{4:21,8:416},{1:1386,2:1247,3:62,4:47,5:9,6:110,7:10})
    if version07:constants['bit']=(111,7,{2:1,4:31,6:1,8:410},{1:1386,2:1252,3:63,4:53,5:9,6:105,7:9})
    result={'status':'PASS_INDEPENDENT_EXCHANGED_FOREST_PRICES_AND_FINITE_TAILS','functional_kernel_native':functional,'branches':{}}
    for branch,(n,s,hp,pp) in constants.items():
        name=('FUNCTIONAL-KERNEL-07-F19-BIT-CONTROLLER.json'if version07 else'FUNCTIONAL-KERNEL-06-F19-BIT-CONTROLLER.json'if version06 else'FUNCTIONAL-KERNEL-05-F19-BIT-CONTROLLER.json'if version05 else'FUNCTIONAL-KERNEL-04-F19-BIT-CONTROLLER.json'if version04 else'FUNCTIONAL-KERNEL-02-F19-BIT-CONTROLLER.json'if version02 else'FUNCTIONAL-KERNEL-F19-BIT-CONTROLLER.json')if(functional and branch=='bit')else f'EXCHANGE-F19-{branch.upper()}-CONTROLLER.json'
        path=base/name;raw=path.read_bytes();w=json.loads(raw)
        cert=receipt['branches'][branch];F=w['full_calls']
        T=Counter({r:F*v for r,v in hp.items()});P=Counter({r:F*v for r,v in pp.items()})
        actual_selected=sum(e['op']=='FULL' and e['selected_native_helper'] for e in w['events'])
        T[s+1]-=n*actual_selected
        for sites in w['target_body_sites']:T[1+s*len(sites)]+=n
        for e in w['events']:
            if e['op']=='THIN':P[1]+=n
            if e['op']=='IDLE':P[s*len(e['body_sites'])]+=2*n
        need(dict(T)=={int(k):v for k,v in cert['targets'].items()},'complete target recount')
        need(dict(P)=={int(k):v for k,v in cert['paid'].items()},'complete paid recount')
        need(sum(r*v for r,v in T.items())-sum(r*v for r,v in P.items())==48*F-n,
             'independent rank-mass surplus')
        a=cert['finite_admission'];C=Q(a['tested_saving']);t=1-C
        margins={}
        for k in [*map(Q,cert['raw_crossing_bracket']),C,Q(1,250)]:
            tt,ppp=moment(T,1-k),moment(P,1-k)
            g=(tt[0]-ppp[1],tt[1]-ppp[0]);margins[str(k)]=bounds_text(g)
            if k==Q(cert['raw_crossing_bracket'][0]):need(g[0]>0,'lower crossing endpoint')
            if k==Q(cert['raw_crossing_bracket'][1]):need(g[1]<0,'upper crossing endpoint')
            if k==C:need(g[0]>0,'strict selected raw saving')
        tt=moment(T,t);pt=moment(P,t)
        u=Q(a['paid_tail_offset']);z=Q(a['target_tail_offset'])
        c=a['cutoff_base'];b=a['floor_base'];v=a['tensor_power']
        alpha=div(pt,tt)
        gamma=div(moment(P,t+u),mul(power(c,u),tt))
        lam=div(mul(power(b,z),moment(T,t-z)),tt)
        claimed=list(map(Q,a['rational_upper_limits']))
        for interval,limit in zip((alpha,gamma,lam),claimed):
            need(0<interval[0]<=interval[1]<=limit<1,'independent rational tail enclosure')
        aa,gg,ll=claimed
        norm=1/(1+v*(1-aa))+2*gg**v+ll**v
        need(norm<1,'all charged finite tails')
        uniform=a['uniform_compiler'];gap=Q(uniform['gap']);H=uniform['H'];p=uniform['logarithm_power']
        exponent=uniform['integer_test_exponent']
        need(H==gap.denominator*exponent and (H+1)**p<2**exponent,'finite uniform integer gate')
        need(Q(uniform['uniform_saving'])==C-gap,'uniform saving debit')
        need(cert['ordinary_visible_record_bound']+cert['whole_job_route_record_bound']<cert['ordinary_record_allowance'],
             'ordinary finite allowance')
        if branch=='bit':
            previous=None
            for stage in cert['ordinary_bootstrap']:
                old=Q(stage['previous_ordinary']);atom=Q(stage['atom']);new=Q(stage['admitted'])
                if previous is not None:need(old==previous,'sequential bootstrap dependency')
                exact=(1-atom)*Q(cert['covered_saving'])+atom*old
                need(exact==Q(stage['full_envelope_limiting_term']) and atom>exact>new and atom<1-exact,
                     'complete ordinary bootstrap envelope')
                previous=new
            need(previous==Q(cert['ordinary_admitted']),'final ordinary claim')
        result['branches'][branch]={'controller_sha256':hashlib.sha256(raw).hexdigest(),
          'targets':dict(sorted(T.items())),'paid':dict(sorted(P.items())),
          'moment_intervals':margins,'alpha':bounds_text(alpha),'gamma':bounds_text(gamma),
          'lambda':bounds_text(lam),'normalized_upper':bounds_text((norm,norm)),
          'strict_raw_saving':str(C),'uniform_saving':uniform['uniform_saving'],
          'ordinary_saving':cert.get('ordinary_admitted'),
          'effective_uniform_rank_encoding':uniform['N']}
    result['seconds']=time.monotonic()-started
    result['scope']='Independent invoice, exact interval and finite-tail arithmetic; retained all-column native, physical realization and outer transfer premises are separate.'
    return result

if __name__=='__main__':
    import sys
    version07='--functional07'in sys.argv;version06='--functional06'in sys.argv;version05='--functional05'in sys.argv;version04='--functional04'in sys.argv;version02='--functional02'in sys.argv;functional='--functional'in sys.argv or version02 or version04 or version05 or version06 or version07
    r=audit(functional,version02,version04,version05,version06,version07);(HERE/('FUNCTIONAL-KERNEL-07-ADMISSION-INDEPENDENT.json'if version07 else'FUNCTIONAL-KERNEL-06-ADMISSION-INDEPENDENT.json'if version06 else'FUNCTIONAL-KERNEL-05-ADMISSION-INDEPENDENT.json'if version05 else'FUNCTIONAL-KERNEL-04-ADMISSION-INDEPENDENT.json'if version04 else'FUNCTIONAL-KERNEL-02-ADMISSION-INDEPENDENT.json'if version02 else'FUNCTIONAL-KERNEL-ADMISSION-INDEPENDENT.json'if functional else'EXCHANGE-ADMISSION-INDEPENDENT.json')).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'status':r['status'],'seconds':r['seconds'],
          'savings':{k:v['uniform_saving'] for k,v in r['branches'].items()}},indent=2))
