# SPDX-License-Identifier: Apache-2.0
"""Independent logarithm/rational-root checks and complete retained entry points."""
import argparse
from contextlib import redirect_stdout
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import adapter


def need(ok,message):
    if not ok:raise ValueError(message)


def reject(fn,kind=ValueError):
    try:fn()
    except kind:return
    raise ValueError('negative control accepted')


@lru_cache(None)
def mercator(x):
    """Independent positive -log(1-z) series with a rational geometric tail."""
    need(Q(1)<=x<=Q(2),'oracle reduced domain')
    z=1-1/x
    if z==0:return Q(0),Q(0)
    power=z;total=Q(0);n=1
    while True:
        total+=power/n;power*=z
        tail=power/((n+1)*(1-z))
        if tail<Q(1,1<<340):return total,total+tail
        n+=1


def oracle_ln(k):
    exponent=k.bit_length()-1
    a,b=mercator(Q(2));c,d=mercator(Q(k,1<<exponent))
    return exponent*a+c,exponent*b+d


def oracle_exp(x):
    """Unscaled rational Taylor series; no predecessor exp/scaling implementation."""
    need(x>=0,'oracle nonnegative exponent')
    term=total=Q(1);n=0
    while True:
        n+=1;term*=x/n;total+=term
        ratio=x/(n+2)
        if ratio<1:
            tail=term*x/(n+1)/(1-ratio)
            if tail<Q(1,1<<340):return total,total+tail


def enclose(engine,k):
    low,high=engine.ln(k);a,b=oracle_ln(k)
    need(low<=a<=b<=high,'independent log enclosure '+str(k))


def retained_run(original):
    engine,blobs=adapter.load(original=original)
    saved=sys.modules.get('ceiling');old_argv=sys.argv[:];old_path=sys.path[:]
    calls=[];real=engine.ceiling
    def recorded(*args,**kwargs):
        result=real(*args,**kwargs);calls.append([str(x) for x in result]);return result
    engine.ceiling=recorded
    sys.modules['ceiling']=engine
    output=io.StringIO()
    try:
        with redirect_stdout(output):
            for name in ('levers.py','verify.py'):
                path='research/complex-local-word-ceiling/'+name
                ns={'__file__':str(adapter.ROOT/path),'__name__':'retained_entry'}
                sys.argv=[str(adapter.ROOT/path)]
                exec(compile(blobs[path],ns['__file__'],'exec'),ns)
                ns['main']()
    finally:
        sys.argv[:]=old_argv;sys.path[:]=old_path
        if saved is None:sys.modules.pop('ceiling',None)
        else:sys.modules['ceiling']=saved
    return calls,output.getvalue()


def run():
    # Fresh original module: this previously valid input fails on normal recursion settings.
    original,_=adapter.load(original=True)
    old_limit=sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(1000)
        reject(lambda:original.child_cost(16,1024,Q(1,1000)),RecursionError)
    finally:sys.setrecursionlimit(old_limit)
    engine,_=adapter.load()
    fixtures=list(range(1,129))+[255,256,257,511,512,513,1023,1024,1025,4095,4096,4097,1<<1000]
    for k in fixtures:enclose(engine,k)
    for bad in (0,-1,Q(3,2)):
        reject(lambda bad=bad:engine.ln(bad))
    need(engine.ln(1)==(Q(0),Q(0)),'exact log one')
    # A missing power-of-two term or wrong atanh sign would fail these exact enclosures.
    lo,hi=engine.ln(1024);need(lo>6,'nonzero binary exponent term')
    need(engine.ln(3)[0]>engine.ln(2)[1],'positive reduced term')
    exp_cases=[(Q(0),Q(0)),(Q(0),Q(1,2)),(Q(1,2),Q(1,2)),(Q(1,2),Q(1)),(Q(1),Q(1)),(Q(2),Q(3)),(Q(8),Q(8))]
    for low,high in exp_cases:
        a,b=engine.exp(low,high);olo,_=oracle_exp(low);_,ohi=oracle_exp(high)
        need(a<=olo<=ohi<=b,'independent unscaled exponential enclosure')
        if high<=Q(1,2):need((a,b)==original.exp(low,high),'exact bounded-domain delegation')
    for low,high in ((Q(-1),Q(0)),(Q(2),Q(1))):reject(lambda:engine.exp(low,high))
    rational_cases=[]
    for scale in (100,1024,10000):
        for p,q,n in ((3,4,2),(4,5,2),(2,3,3)):
            r=scale*p**n;m=scale*q**n;a=Q(1,n)
            lo,hi=engine.child_cost(r,m,a);exact=Q(p,q)**(n-1)
            need(lo<=exact<=hi,'exact rational power enclosure')
            rational_cases.append(dict(r=r,m=m,a=str(a),exact=str(exact)))
    for r,m,a,exact in ((1,64,Q(1,2),Q(1,8)),(1,73,Q(1),Q(1))):
        lo,hi=engine.child_cost(r,m,a);need(lo<=exact<=hi,'extended exact rational power')
        rational_cases.append(dict(r=r,m=m,a=str(a),exact=str(exact)))
    repaired=engine.child_cost(16,1024,Q(1,1000))
    need(Q(16,1024)<repaired[0]<repaired[1]<Q(17,1024),'repaired regression interval')
    baseline,stdout0=retained_run(True);fixed,stdout1=retained_run(False)
    need(baseline==fixed and stdout0==stdout1,'retained exact brackets and stdout')
    # A declared planning profile within the retained exponent enclosure domain.
    large=engine.ceiling({16:1},1024,10,1,0)
    need(engine.relax({16:1},1024,10,1,0,large[0])[1]<1,'large-model lower bracket')
    need(engine.relax({16:1},1024,10,1,0,large[1])[0]>1,'large-model upper bracket')
    # Log repair alone still fails the public ceiling's fixed upper probe.
    log_only,_=adapter.load(log_only=True)
    reject(lambda:log_only.ceiling({1:1},32768,10,1,0))
    extended=engine.ceiling({1:1},32768,10,1,0)
    need(engine.relax({1:1},32768,10,1,0,extended[0])[1]<1,'extended lower bracket')
    need(engine.relax({1:1},32768,10,1,0,extended[1])[0]>1,'extended upper bracket')
    return dict(status='PASS_CEILING_RANGE_REDUCTION',independent_log_cases=len(fixtures),
                rational_root_cases=rational_cases,independent_exp_cases=len(exp_cases),old_regression='RecursionError',
                regression=dict(r=16,m=1024,a='1/1000',interval=[str(x) for x in repaired]),
                retained_brackets=fixed,retained_stdout_sha256=hashlib.sha256(stdout1.encode()).hexdigest(),
                hypothetical_large_model=dict(local={'16':1},m=1024,families=10,stages=1,centre=0,bracket=[str(x) for x in large]),
                hypothetical_extended_model=dict(local={'1':1},m=32768,families=10,stages=1,centre=0,bracket=[str(x) for x in extended]),
                limits='Opt-in range reduction; logarithm and extended exponential intervals need not be bit-identical. Physical feasibility and selected supplier admission are unchanged.')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);args=ap.parse_args()
    if args.out:need(not args.out.exists(),'output already exists')
    result=run();data=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.out:
        with args.out.open('x',encoding='utf-8',newline='\n') as f:f.write(data)
    else:
        recorded=json.loads((HERE/'RESULT.json').read_bytes())
        # Python equality conflates True, 1 and 1.0. Preserve JSON scalar types.
        canonical=lambda obj:json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)
        need(canonical(result)==canonical(recorded),'result receipt')
    print(data,end='')
