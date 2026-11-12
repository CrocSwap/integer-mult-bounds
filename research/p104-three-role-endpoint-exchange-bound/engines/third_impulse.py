"""Test the unique third public role at every inherited coframe cut."""
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
 'inputs/PRICE.json':'7b0ccc8fd85240568aeddfc1e2c036ac05ab0ec6e8473522bd902a4adcc1e9eb',
 'inputs/GEOMETRY.json':'f2aa238ed8c49f0633c3837c6961bfba19482385851a5606578fa6368db79542',
 'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
 'inputs/7334-READBACK.json':'337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82',
 'inputs/R96-PRICE.json':'a78be64c3e3ae8a0e532237c4dd3541aa9ad3fcbbc3c25d79c8a03fb7e07c525',
}
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
THIRD,EVENTS,RANGES,CUTS,SECONDS=1454,76466,20,20455,20


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
    p,g,r,b=(loads(checked(root,'inputs/'+x+'.json'),object_pairs_hook=unique)
             for x in ('PRICE','GEOMETRY','7334-READBACK','R96-PRICE'))
    assert p['head']==g['head']==r['head']==b['head']==HEAD
    assert p['caller']==g['caller']==r['caller_head']==b['caller']==CALLER
    assert g['price_sha256']==PINS['inputs/PRICE.json'] and p['word_sha256']==PINS['inputs/7334-WORD.json.gz']
    assert g['raw_cuts']==CUTS and len(g['ranges'])==RANGES and THIRD in b['cohort']
    assert p['whole_compatible_pair_cap']==1 and p['paid_delta']=={}
    assert p['productive_delta']=={'5':-17,'6':17,'8':17,'9':-17}
    assert Q(p['quote']['probe']['complete_one_margin'][0])>0
    assert Q(p['quote']['old_crossing_upper']['complete_one_margin_with_extra_rank_one'][1])<0
    assert (r['ordinary'],r['ordinary_headroom'],r['native_grid'],r['context_c'],r['context_headroom'])==(782715464,217284536,[1125,25],2430,1666)
    return {'head':HEAD,'caller':CALLER,'pins':PINS,'third':THIRD,'ranges':g['ranges'],'caps':{'raw_cuts':CUTS,'ranges':RANGES,'events':EVENTS,'seconds':SECONDS},
            'quote':p['quote'],'paid_delta':p['paid_delta'],'productive_delta':p['productive_delta'],
            'ordinary_baseline':r['ordinary'],'ordinary_headroom':r['ordinary_headroom'],
            'native_grid':r['native_grid'],'context_c':r['context_c'],'context_headroom':r['context_headroom']}


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
    return ['nonzero value on wrong chart ineligible','three zero donor responses exclude','nonzero third keeps key pending']


def audit(word,price,deadline,progress):
    n,m,tape=(word[k] for k in ('public','owned_fields','program'))
    assert (n,m,len(tape))==(1501,68,EVENTS)
    state=word['initial']+[None]*m
    values=[Q(0)]*(n+m)
    assert (word['initial'][THIRD],word['final'][THIRD])==(3,245)
    values[THIRD],values[1481]=Q(1),Q(-2)
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
            assert i not in (THIRD,1481) and j==1481
            assert state[i]==state[j]==chart and values[i]==values[j]==0
            kind=status(state[THIRD],chart,values[THIRD])
            r=records[k]
            r['counts'][kind]+=1
            progress['raw_cuts_checked']+=1
            if kind!='no coframe':
                sub=r['subranges']
                if sub and sub[-1]['last']+1==t and sub[-1]['revision']==revision:
                    assert sub[-1]['response']==str(values[THIRD])
                    sub[-1]['last']=t
                else:
                    sub.append({'first':t,'last':t,'revision':revision,'response':str(values[THIRD]),'status':kind})
        op,d,*args=e
        if THIRD==d or op in ('ADD','COPY') and args[0]==THIRD:
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
    cli.add_argument('--price-only',action='store_true')
    args=cli.parse_args()
    price=freeze(args.root)
    tests=controls()
    if args.price_only:
        print(dumps(price,indent=2,sort_keys=True));return
    p=(args.root/'lead/PRICE.json').read_bytes()
    assert p==(dumps(price,indent=2,sort_keys=True)+'\n').encode()
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
