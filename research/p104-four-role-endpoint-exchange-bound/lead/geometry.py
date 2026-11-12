"""Exact four-role coframe and impulse geometry on the 20 inherited ranges."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
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
 'lead/PRICE.json':'e3f24ce27460372e8821bf9fcda50c40d14a776a06569182b7dd44da1c3e8c22',
 'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
}
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
THIRD,FOURTH,EVENTS,RANGES,CUTS,SECONDS=1454,1251,76466,20,20455,20


def unique(items):
    d=dict(items)
    if len(d)!=len(items):
        raise ValueError('duplicate JSON key')
    return d


def checked(root,name):
    b=(root/name).read_bytes()
    assert sha256(b).hexdigest()==PINS[name],('changed dependency',name)
    return b


def freeze(root):
    p=loads(checked(root,'lead/PRICE.json'),object_pairs_hook=unique)
    assert p['head']==HEAD and p['caller']==CALLER
    assert p['additional_roles']==[1454,1251] and p['extra_paid']==0 and p['compatible_edit_cap']==1
    assert p['raw_cuts']==CUTS and len(p['ranges'])==RANGES
    return p


@cache
def q(x):
    return Q(x)


def status(third_chart,chart,third_value):
    if third_chart!=chart:
        return 'no coframe'
    return 'separator excludes' if not third_value else 'prefix pending'


def controls():
    assert status(2,3,Q(1))=='no coframe'
    assert status(3,3,Q(0))=='separator excludes'
    assert status(3,3,Q(-1,2))=='prefix pending'
    return ['nonzero value on wrong chart ineligible','four zero donor responses exclude','nonzero fourth keeps key pending']


def audit(word,price,deadline,progress):
    n,m,tape=(word[k] for k in ('public','owned_fields','program'))
    assert (n,m,len(tape))==(1501,68,EVENTS)
    state=word['initial']+[None]*m
    values=[Q(0)]*(n+m)
    assert all((word['initial'][r],word['final'][r])==(3,245) for r in (THIRD,FOURTH))
    values[FOURTH],values[1481]=Q(1),Q(4)
    fresh=set()
    expected=price['ranges']
    wants=defaultdict(list)
    for k,(_,_,_,lo,hi) in enumerate(expected):
        for t in range(lo,hi+1):
            wants[t].append(k)
    records=[{'range':r,'counts':Counter(),'subranges':[]} for r in expected]
    revision=0
    for t,e in enumerate(tape):
        progress['first_unvisited_event']=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError('forward impulse cap')
        for k in wants.get(t,()):
            i,j,chart,_,_=expected[k]
            assert i not in (THIRD,FOURTH,1481) and j==1481
            assert state[i]==state[j]==chart
            coframed=state[THIRD]==state[FOURTH]==chart
            if coframed:
                assert values[i]==values[j]==values[THIRD]==0
            kind=status(chart if coframed else None,chart,values[FOURTH])
            r=records[k]
            r['counts'][kind]+=1
            progress['raw_cuts_checked']+=1
            if kind!='no coframe':
                sub=r['subranges']
                if sub and sub[-1]['last']+1==t and sub[-1]['revision']==revision:
                    assert sub[-1]['response']==str(values[FOURTH])
                    sub[-1]['last']=t
                else:
                    sub.append({'first':t,'last':t,'revision':revision,'response':str(values[FOURTH]),'status':kind})
        op,d,*args=e
        if d in (THIRD,FOURTH) or op in ('ADD','COPY') and args[0] in (THIRD,FOURTH):
            revision+=1
        if op=='MOVE':
            a,b,owned=args
            assert state[d]==a and owned==(d>=n)
            state[d]=b
            fresh.discard(d)
        elif op=='INIT':
            assert d>=n and state[d] is None
            state[d],values[d]=args[0],Q(0)
            fresh.add(d)
        elif op=='CLEAR':
            assert d>=n and state[d]==args[0]
            state[d],values[d]=None,Q(0)
            fresh.discard(d)
        elif op=='SCALE':
            assert state[d]==args[-1]
            values[d]*=q(args[0])
            fresh.discard(d)
        else:
            assert op in ('ADD','COPY')
            s,coefficient,chart=args
            assert s!=d and state[s]==state[d]==chart
            assert op!='COPY' or d>=n and d in fresh and values[d]==0
            values[d]=(values[d] if op=='ADD' else 0)+q(coefficient)*values[s]
            fresh.discard(d)
        progress['events']+=1
    assert not fresh and state==word['final']+[None]*m
    progress['first_unvisited_event']=None
    assert progress['raw_cuts_checked']==CUTS
    assert all(sum(r['counts'].values())==r['range'][-1]-r['range'][-2]+1 for r in records)
    return records


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--root',type=Path,default=ROOT)
    cli.add_argument('--controls-only',action='store_true')
    args=cli.parse_args()
    price=freeze(args.root)
    tests=controls()
    if args.controls_only:
        print(dumps(tests));return
    p=checked(args.root,'lead/PRICE.json')
    def stop(*_):
        raise TimeoutError('hard 20-second cap')
    signal(SIGALRM,stop)
    alarm(SECONDS)
    progress={'events':0,'raw_cuts_checked':0}
    result={'head':HEAD,'caller':CALLER,'controls':tests,'price_sha256':sha256(p).hexdigest(),'progress':progress}
    try:
        raw=decompress(checked(args.root,'inputs/7334-WORD.json.gz'))
        assert sha256(raw).hexdigest()==PAYLOAD
        rows=audit(loads(raw,object_pairs_hook=unique),price,monotonic()+SECONDS-1,progress)
        counts=Counter()
        for r in rows:
            counts.update(r['counts'])
        unresolved=[{'range':r['range'],'segment':s} for r in rows for s in r['subranges'] if s['status']=='prefix pending']
        result|={'rows':rows,'counts':counts,'unresolved':unresolved}
    except TimeoutError as e:
        result|={'timeout':str(e),'unresolved':'incomplete original raw cuts, no exclusion'}
    finally:
        alarm(0)
    print(dumps(result,sort_keys=True,indent=2))
    if 'timeout' in result:
        raise SystemExit(2)


if __name__=='__main__':
    main()
