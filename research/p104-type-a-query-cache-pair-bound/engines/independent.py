"""Independent exact Type A QUERY source proportionality screen."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from math import prod
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HERE=Path(__file__).resolve().parent
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
PRICE='bbc486a3eb0e2aed03dd09f400fa94de1a59312058a9826880999155b10453bf'
CLOCKS=(1516,1580,1659,1721)
PROBES=((1,(1,)*17),(-1,(1,)*17),(-1,tuple(range(2,19))),
        (1,(19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89)))


class Capped(Exception):
    pass


def require(ok,message):
    if not ok:
        raise ValueError(message)


def unique(items):
    record=dict(items)
    require(len(record)==len(items),'Duplicate input key')
    return record


def read(raw):
    return loads(raw,object_pairs_hook=unique)


def pinned(path,digest):
    raw=path.read_bytes()
    require(sha256(raw).hexdigest()==digest,f'Changed input {path.name}')
    return raw


@cache
def fraction(token):
    return Q(token)


def add(rows,dst,src,q):
    require(dst!=src,'Aliased scalar source')
    for index,value in rows[src].items():
        new=rows[dst].get(index,0)+q*value
        if new:
            rows[dst][index]=new
        else:
            rows[dst].pop(index,None)


def scale(rows,dst,q):
    require(q!=0,'Singular scalar operation')
    if q!=1:
        rows[dst]={i:v*q for i,v in rows[dst].items()}


def safe_time(deadline):
    if monotonic()>=deadline:
        raise Capped


def replay(caller,clocks,q,bodies,deadline,check_endpoint):
    ty=caller['types']['A']; n=ty['roles']; alpha=Q(ty['alpha2'])
    require(q in (-1,1) and all(bodies) and ty['offset']==0,'Invalid signed specialization')
    rows=[{j:Q(1)} for j in range(n)]
    sources,writes,stages={},[],[]
    observed=[]
    for clock,event in enumerate(caller['events']):
        if clock%32==0 or clock in clocks:
            safe_time(deadline)
        kind,op,*args=event
        if kind=='J':
            stage=op; u,v,x,y=args[0]
            require(len(set((u,v,x,y)))==4 and max(u,v,x,y)<n,'Invalid Type A J roles')
            add(rows,v,u,Q(1,q)); add(rows,x,y,alpha*q)
            for r in (u,v,x,y):
                scale(rows,r,bodies[stage-1])
            if 1 in (u,v,x,y):
                writes.append([clock,'J',stage])
            stages.append(stage)
        elif kind=='A':
            dst,*tail=args
            if op=='QUERY':
                src,power=tail
                require(event==['A','QUERY',0,1,-1] and clock in clocks,'Unexpected literal QUERY')
                sources[clock]=rows[src].copy()
                observed.append(clock)
                add(rows,dst,src,Q(q)**power)
            elif op=='ADD':
                src,k=tail;add(rows,dst,src,fraction(k))
                if dst==1:writes.append([clock,op,src,k])
            elif op=='SCALE':
                k,=tail;scale(rows,dst,fraction(k))
                if dst==1:writes.append([clock,op,k])
            elif op=='SWAP':
                src,=tail;rows[dst],rows[src]=rows[src],rows[dst]
                if 1 in (dst,src):writes.append([clock,op,dst,src])
            elif op=='LAMBDA':
                sign,=tail
                require(sign in (-1,1),'Unexpected LAMBDA coefficient')
                # (1+i sign)/2+(1-i sign)q²/2 equals one at q=±1.
            elif op in ('IDLE_ONE','IDLE_ODD'):
                selected=tail[0]
                require(len(set(selected))==len(selected),'Duplicate idle stage')
                k=prod(bodies[s-1] for s in selected)
                if op=='IDLE_ODD':k*=Q(q)**tail[1]
                scale(rows,dst,k)
                if dst==1:writes.append([clock,op,*tail])
            else:
                raise ValueError(f'Unexpected Type A opcode {op}')
        elif kind!='B':
            raise ValueError(f'Unexpected caller region {kind}')
    require(tuple(observed)==tuple(clocks) and stages==list(range(1,len(bodies)+1)),
            'Changed QUERY/stage inventory')
    if check_endpoint:
        for r,endpoint in enumerate(ty['diagonal']):
            power,zero,*mask=endpoint
            require(zero==0 and len(mask)==len(bodies),'Unexpected endpoint signature')
            expected=Q(q)**power*prod(b**e for b,e in zip(bodies,mask,strict=True))
            require(rows[r]=={r:expected},'Specialized predecessor endpoint mismatch')
    return sources,writes


def proportional(first,second):
    require(first and second,'Zero source in invertible signed prefix')
    j=min(first)
    for k in sorted(first.keys() | second.keys()):
        determinant=first[j]*second.get(k,0)-first.get(k,0)*second.get(j,0)
        if determinant:
            return None,{'coordinates':[j,k],'first':[str(first[j]),str(first.get(k,0))],
                         'second':[str(second.get(j,0)),str(second.get(k,0))],
                         'determinant':str(determinant)}
    return second[j]/first[j],None


def compare(first,second,probes):
    common=None
    for label,rows in enumerate(probes):
        ratio,witness=proportional(rows[first],rows[second])
        if witness:
            return dict(status='exact_nonproportional_source',probe=label,witness=witness)
        if common is None:
            common=ratio
        elif ratio!=common:
            return dict(status='probe_dependent_ratio',probe=label,first_ratio=str(common),other_ratio=str(ratio))
    return dict(status='symbolic_gate_required',specialized_ratio=str(common))


def controls():
    base={'types':{'A':{'roles':5,'offset':0,'alpha2':'-1'}},'events':[
          ['A','QUERY',0,1,-1],['J',1,[1,2,3,4],[]],['A','QUERY',0,1,-1]]}
    unit,_=replay(base,(0,2),-1,(1,),float('inf'),False)
    twice,_=replay(base,(0,2),-1,(2,),float('inf'),False)
    require(compare(0,2,[unit])==dict(status='symbolic_gate_required',specialized_ratio='1'),
            'Repeat-source control failed')
    require(compare(0,2,[unit,twice])['status']=='probe_dependent_ratio','Body-dependent ratio control failed')
    mutant=base|{'events':[['A','QUERY',0,1,-1],['J',1,[1,2,3,4],[]],
                          ['A','ADD',1,3,'-2'],['A','QUERY',0,1,-1]]}
    changed,_=replay(mutant,(0,3),-1,(1,),float('inf'),False)
    residual=compare(0,3,[changed])
    require(residual['witness']['determinant']=='-2','Signed coefficient control failed')
    return ['repeated_source','body_dependent_ratio','signed_intervening_write']


def main():
    p=ArgumentParser(description=__doc__)
    actions=p.add_mutually_exclusive_group(required=True)
    actions.add_argument('--controls-only',action='store_true')
    actions.add_argument('--support',action='store_true')
    args=p.parse_args()
    assert __debug__
    tests=controls()
    if args.controls_only:
        print(dumps(dict(controls=tests),sort_keys=True,indent=2));return
    price=read(pinned(HERE/'inputs/PRICE.json',PRICE))
    require(price['head']==HEAD and price['caller_sha256']==CALLER,'Price provenance mismatch')
    pairs=list(combinations(CLOCKS,2))
    require(price['eligible_pairs_before_support']==[list(pair) for pair in pairs] and price['type_a_ports']==96,
            'Wrong frozen support stock')
    require(price['by_number_of_reused_queries']['1']['paid_delta']=={'1':-96},'Wrong one-use invoice')
    def watchdog(*_):
        raise TimeoutError('R75 20-second runner limit')
    signal(SIGALRM,watchdog)
    alarm(20)
    started=monotonic();sources=[];writes=[];decisions=[]
    try:
        deadline=started+17
        caller=read(pinned(HERE/'inputs/CALLER.json',CALLER))
        ty=caller['types']['A']
        require((caller['stages'],ty['roles'],ty['offset'],len(ty['ports']))==(17,36,0,96),'Wrong Type A signature')
        for q,bodies in PROBES:
            rows,history=replay(caller,CLOCKS,q,bodies,deadline,True)
            if writes:
                require(history==writes,'Inconsistent structural write receipt')
            else:
                writes=history
            sources.append(rows)
        for first,second in pairs:
            safe_time(deadline)
            rows=compare(first,second,sources)
            decisions.append(dict(pair=[first,second],intervening_source_writes=[w for w in writes if first<w[0]<second],**rows))
    except Capped:
        pass
    finally:
        alarm(0)
    snapshots=[{clock:{i:str(v) for i,v in row.items()} for clock,row in sample.items()} for sample in sources]
    result=dict(head=HEAD,caller_sha256=CALLER,price_sha256=PRICE,case_cap=6,seconds_cap=20,
                controls=tests,probes=[dict(q=q,bodies=bodies) for q,bodies in PROBES],
                sources=snapshots,endpoint_checks=len(sources),decisions=decisions,
                unvisited=pairs[len(decisions):],symbolic_only=[r['pair'] for r in decisions if r['status']=='symbolic_gate_required'],
                unresolved_credit_upper=price['by_number_of_reused_queries']['1']['exact_credit'])
    print(dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':
    main()
