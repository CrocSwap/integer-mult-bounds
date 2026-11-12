"""Exact impulse on the seven frozen remaining R148 three-role bank segments."""
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
 'inputs/PRICE.json':'8b71d05eddb3aee641ffa41a57a3922292bc4d45c5eb8aae8f2e4514388f6524',
 'inputs/IMPULSE.json':'d7b30091bd881711f4de7339216368ef8de1649e35cddb00d4dd29be2185b3af',
 'inputs/PREFIX.json':'e17e9b4dfb359eed4e478ea6ae7d2cc247687867054f3991f19bbd51e4ab73d9',
 'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
}
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
CAP,EVENTS,SECONDS=7,76466,20


def unique(items):
    out=dict(items)
    assert len(out)==len(items)
    return out


def read(root,name):
    b=(root/name).read_bytes()
    assert sha256(b).hexdigest()==PINS[name],('changed dependency',name)
    return b


def freeze(root):
    p,g,b=(loads(read(root,'inputs/'+x+'.json'),object_pairs_hook=unique) for x in ('PRICE','IMPULSE','PREFIX'))
    assert p['head']==g['head']==HEAD and p['caller']==g['caller']==CALLER
    assert g['price_sha256']==PINS['inputs/PRICE.json'] and b['pins']['lead/IMPULSE.json']==PINS['inputs/IMPULSE.json']
    assert b['counts']=={'exact_rank_exclusion':8} and len(b['rows'])==8 and len(b['unvisited'])==CAP
    assert all(x['proof']['separating_covector']=={'1251':'1','1481':'4'} and Q(x['proof']['separated_target'])==-4 for x in b['rows'])
    lookup={}
    for r in g['unresolved']:
        i,j,c,_,_=r['range']
        lo,hi=(r['segment'][k] for k in ('first','last'))
        lookup[i,j,1454,c,hi]=[i,j,1454,c,lo,hi]
    assert len(lookup)==15 and set(lookup)=={tuple(r['key']) for r in b['rows']}|set(map(tuple,b['unvisited']))
    ranges=[lookup[tuple(k)] for k in b['unvisited']]
    assert all(j==1481 and third==1454 and c==245 and i not in (1251,1481) for i,j,third,c,_,_ in ranges)
    return {'head':HEAD,'caller':CALLER,'pins':PINS,'ranges':ranges,'raw_cuts':sum(hi-lo+1 for *_,lo,hi in ranges),
            'target_response':'-4','input_impulse':{'1251':'1','1481':'4'},
            'caps':{'ranges':CAP,'events':EVENTS,'seconds':SECONDS}}


@cache
def q(s):
    return Q(s)


def disposition(row):
    return 'prefix excluded' if all(v==0 for v in row) else 'unresolved'


def controls():
    assert disposition([Q(0)]*3)=='prefix excluded'
    assert disposition([Q(0),Q(0),Q(-1,2)])=='unresolved'
    return ['exact three-row zero response','nonzero third response remains unresolved']


def audit(word,scope,deadline,progress):
    n,m,tape=(word[k] for k in ('public','owned_fields','program'))
    assert (n,m,len(tape))==(1501,68,EVENTS)
    state=word['initial']+[None]*m
    impulse={int(j):q(v) for j,v in scope['input_impulse'].items()}
    values=[impulse.get(j,Q(0)) for j in range(n+m)]
    wants=defaultdict(list)
    ranges=scope['ranges']
    for k,(*_,lo,hi) in enumerate(ranges):
        for t in range(lo,hi+1):
            wants[t].append(k)
    rows=[{'range':r,'cuts_checked':0,'first_nonzero':None} for r in ranges]
    fresh=set()
    for t,event in enumerate(tape):
        progress['first_unvisited_event']=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError('forward exact cap')
        for k in wants.get(t,()):
            i,j,third,c,_,_=ranges[k]
            assert state[i]==state[j]==state[third]==c
            assert impulse.get(i,0)-impulse[j]==q(scope['target_response'])
            r=rows[k]
            bank=[values[x] for x in (i,j,third)]
            if r['first_nonzero'] is None and disposition(bank)=='unresolved':
                r['first_nonzero']=[t,*map(str,bank)]
            r['cuts_checked']+=1
        op,d,*a=event
        if op=='MOVE':
            old,new,owned=a
            assert state[d]==old and owned==(d>=n)
            state[d]=new
            fresh.discard(d)
        elif op=='INIT':
            assert d>=n and state[d] is None
            state[d],values[d]=a[0],Q(0)
            fresh.add(d)
        elif op=='CLEAR':
            assert d>=n and state[d]==a[0]
            state[d],values[d]=None,Q(0)
            fresh.discard(d)
        elif op=='SCALE':
            assert state[d]==a[-1]
            values[d]*=q(a[0])
            fresh.discard(d)
        else:
            assert op in ('ADD','COPY')
            s,k,c=a
            assert s!=d and state[s]==state[d]==c
            assert op!='COPY' or d>=n and d in fresh and values[d]==0
            values[d]=(values[d] if op=='ADD' else 0)+q(k)*values[s]
            fresh.discard(d)
        progress['events']+=1
    assert not fresh and state==word['final']+[None]*m
    assert [r['cuts_checked'] for r in rows]==[hi-lo+1 for *_,lo,hi in ranges]
    progress['first_unvisited_event']=None
    return [r|{'status':'prefix excluded' if r['first_nonzero'] is None else 'unresolved'} for r in rows]


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--root',type=Path,default=ROOT)
    cli.add_argument('--freeze',action='store_true')
    args=cli.parse_args()
    scope=freeze(args.root)
    tests=controls()
    if args.freeze:
        print(dumps(scope,sort_keys=True,indent=2));return
    key_data=(args.root/'lead/KEYS.json').read_bytes()
    assert key_data==(dumps(scope,sort_keys=True,indent=2)+'\n').encode()
    def stop(*_):
        raise TimeoutError('hard 20-second limit')
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+SECONDS-1
    progress={'events':0}
    out={'head':HEAD,'caller':CALLER,'pins':PINS,'controls':tests,'progress':progress,'keys_sha256':sha256(key_data).hexdigest()}
    try:
        raw=decompress(read(args.root,'inputs/7334-WORD.json.gz'))
        assert sha256(raw).hexdigest()==PAYLOAD
        rows=audit(loads(raw,object_pairs_hook=unique),scope,deadline,progress)
        out|={'rows':rows,'raw_cuts':sum(r['cuts_checked'] for r in rows),
              'unresolved':[r['range'] for r in rows if r['status']=='unresolved']}
    except TimeoutError as e:
        out|={'timeout':str(e),'unresolved':scope['ranges']}
    finally:
        alarm(0)
    print(dumps(out,sort_keys=True,indent=2))
    if 'timeout' in out:
        raise SystemExit(2)


if __name__=='__main__':
    main()
