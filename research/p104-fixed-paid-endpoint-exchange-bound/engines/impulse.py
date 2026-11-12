"""Check all remaining R143 role1481 bank cuts with one exact input impulse."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
 'inputs/GEOMETRY.json':'f2aa238ed8c49f0633c3837c6961bfba19482385851a5606578fa6368db79542',
 'inputs/BASIS.json':'0688a6fe35487c3b79abaca48b583c6cad6a865bd7ae6b5addba846549807092',
 'inputs/PRICE.json':'7b0ccc8fd85240568aeddfc1e2c036ac05ab0ec6e8473522bd902a4adcc1e9eb',
 'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
}
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
CAP,EVENTS,SECONDS=12,76466,20


def unique(items):
    out=dict(items)
    assert len(out)==len(items)
    return out


def read(root,name,pin=None):
    b=(root/name).read_bytes()
    assert sha256(b).hexdigest()==(pin or PINS[name]),('changed dependency',name)
    return b


def freeze(root):
    g,b,p=(loads(read(root,'inputs/'+x+'.json'),object_pairs_hook=unique) for x in ('GEOMETRY','BASIS','PRICE'))
    assert g['head']==p['head']==HEAD and g['caller']==p['caller']==CALLER
    assert g['price_sha256']==PINS['inputs/PRICE.json'] and b['pins']['lead/GEOMETRY.json']==PINS['inputs/GEOMETRY.json']
    assert len(g['ranges'])==20 and len(b['rows'])==8 and not b['unvisited']
    for row in b['rows']:
        assert row['decision']=='prefix excluded' and row['prefix']['separating_covector']=={'1454':'1','1481':'-2'}
    done={tuple(r['key']) for r in b['rows']}
    remaining=[r for r in g['ranges'] if (*r[:3],r[4]) not in done]
    assert len(remaining)==CAP and all(j==1481 and i not in (1454,1481) for i,j,_,_,_ in remaining)
    return {'head':HEAD,'caller':CALLER,'inputs':PINS,'range_cap':CAP,'events':EVENTS,'seconds':SECONDS,
            'ranges':remaining,'raw_cuts':sum(b-a+1 for _,_,_,a,b in remaining),
            'input_impulse':{'1454':'1','1481':'-2'},'target_response':'2'}


@cache
def q(s):
    return Q(s)


def evaluate(role_a,role_b,value_a,value_b,impulse):
    target=impulse.get(role_a,0)-impulse.get(role_b,0)
    assert target
    return bool(not value_a and not value_b),target


def controls():
    assert evaluate(4,8,Q(0),Q(0),{2:Q(1),8:Q(-2)})==(True,Q(2))
    assert evaluate(4,8,Q(1,2),Q(0),{2:Q(1),8:Q(-2)})==(False,Q(2))
    return ['annihilating exact input','nonzero donor remains unresolved']


def audit(word,price,deadline,progress):
    n,m,tape=(word[k] for k in ('public','owned_fields','program'))
    assert (n,m,len(tape))==(1501,68,EVENTS)
    state=word['initial']+[None]*m
    impulse={int(i):q(v) for i,v in price['input_impulse'].items()}
    values=[impulse.get(i,Q(0)) for i in range(n+m)]
    fresh=set()
    wants=defaultdict(list)
    ranges=price['ranges']
    for key,(_,_,_,a,b) in enumerate(ranges):
        for t in range(a,b+1):
            wants[t].append(key)
    observed=[0]*len(ranges)
    first_failure={}
    for t,event in enumerate(tape):
        progress['first_unvisited']=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError('forward impulse cap')
        for k in wants.get(t,()):
            i,j,chart,_,_=ranges[k]
            assert state[i]==state[j]==chart
            success,target=evaluate(i,j,values[i],values[j],impulse)
            assert target==q(price['target_response'])
            if not success:
                first_failure.setdefault(k,[t,str(values[i]),str(values[j])])
            observed[k]+=1
        op,d,*args=event
        if op=='MOVE':
            a,b,owned=args
            assert state[d]==a and owned==(d>=n)
            state[d]=b
            fresh.discard(d)
        elif op=='INIT':
            assert d>=n and state[d] is None
            state[d]=args[0]
            values[d]=Q(0)
            fresh.add(d)
        elif op=='CLEAR':
            assert d>=n and state[d]==args[0]
            state[d]=None
            values[d]=Q(0)
            fresh.discard(d)
        elif op=='SCALE':
            assert state[d]==args[-1]
            values[d]*=q(args[0])
            fresh.discard(d)
        else:
            assert op in ('ADD','COPY')
            s,coeff,chart=args
            assert s!=d and state[s]==state[d]==chart
            assert op!='COPY' or d>=n and d in fresh and values[d]==0
            values[d]=(values[d] if op=='ADD' else 0)+q(coeff)*values[s]
            fresh.discard(d)
        progress['events']+=1
    assert not fresh and state==word['final']+[None]*m
    progress['first_unvisited']=None
    assert observed==[b-a+1 for _,_,_,a,b in ranges]
    return [{'range':r,'raw_cuts':observed[k],'first_nonzero':first_failure.get(k),
             'status':'prefix excluded' if k not in first_failure else 'unresolved'} for k,r in enumerate(ranges)]


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--root',type=Path,default=ROOT)
    cli.add_argument('--freeze',action='store_true')
    args=cli.parse_args()
    price=freeze(args.root)
    tests=controls()
    if args.freeze:
        print(dumps(price,indent=2,sort_keys=True));return
    stored=(args.root/'lead/KEYS.json').read_bytes()
    assert stored==(dumps(price,indent=2,sort_keys=True)+'\n').encode()
    def stop(*_):
        raise TimeoutError('hard 20-second cap')
    signal(SIGALRM,stop)
    alarm(SECONDS)
    progress={'events':0}
    out={'head':HEAD,'caller':CALLER,'controls':tests,'progress':progress,'keys_sha256':sha256(stored).hexdigest()}
    try:
        raw=decompress(read(args.root,'inputs/7334-WORD.json.gz'))
        assert sha256(raw).hexdigest()==PAYLOAD
        rows=audit(loads(raw,object_pairs_hook=unique),price,monotonic()+SECONDS-1,progress)
        out|={'rows':rows,'raw_cuts':sum(r['raw_cuts'] for r in rows),
              'unresolved':[r['range'] for r in rows if r['status']=='unresolved']}
    except TimeoutError as exc:
        out|={'timeout':str(exc),'unresolved':price['ranges']}
    finally:
        alarm(0)
    print(dumps(out,indent=2,sort_keys=True))
    if 'timeout' in out:
        raise SystemExit(2)


if __name__=='__main__':
    main()
