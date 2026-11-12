"""Exact coframe ranges for one fixed-paid endpoint exchange."""
from argparse import ArgumentParser
from collections import defaultdict
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PRICE='7b0ccc8fd85240568aeddfc1e2c036ac05ab0ec6e8473522bd902a4adcc1e9eb'
WORD='4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a'
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
PIVOT,EVENTS,CASES,SECONDS=1481,76466,615,25


def checked(root,name,expected):
    raw=(root/name).read_bytes()
    assert sha256(raw).hexdigest()==expected,('changed input',name)
    return raw


def unique(items):
    o=dict(items)
    assert len(o)==len(items)
    return o


def space(basis):
    out={0}
    for x in basis:
        assert x not in out
        out|={x^u for u in out}
    return out


def ranges(program,state,pivot,roles,deadline,progress):
    roles=set(roles)
    charts=defaultdict(set)
    for r in roles:
        charts[state[r]].add(r)
    opened={r:0 for r in charts[state[pivot]]}
    result=[]
    last_scalar={r:-1 for r in roles|{pivot}}
    for t,e in enumerate(program):
        progress['first_unvisited']=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError('literal geometry cap')
        op,d,*a=e
        touched={d,a[0]} if op in ('ADD','COPY') else {d}
        impacted=set(opened) if pivot in touched else opened.keys()&touched
        for r in impacted:
            result.append([r,pivot,state[pivot],opened.pop(r),t])
        if op=='MOVE':
            old,new,owned=a
            assert state[d]==old
            if d in roles:
                charts[old].remove(d)
                charts[new].add(d)
            state[d]=new
        elif op in ('INIT','CLEAR'):
            assert not (touched & (roles|{pivot}))
            state[d]=a[0] if op=='INIT' else None
        else:
            assert op in ('ADD','COPY','SCALE')
            assert all(state[r]==a[-1] for r in touched)
            for r in touched & last_scalar.keys():
                last_scalar[r]=t
        affected=charts[state[pivot]] if pivot in touched else touched & charts[state[pivot]]
        for r in affected:
            assert r not in opened
            opened[r]=t+1
        progress['events']+=1
    for r,lo in opened.items():
        result.append([r,pivot,state[pivot],lo,len(program)])
    progress['first_unvisited']=None
    ordered=sorted(result)
    assert all(a<=b for _,_,_,a,b in ordered)
    return ordered,last_scalar


def priority(rows,last):
    def key(row):
        i,j,c,a,b=row
        late=int(b>last[i])+int(b>last[j])
        return -late,-b,c,i,a
    return sorted(rows,key=key)


def controls():
    events=[['MOVE',0,0,1,False],['SCALE',2,'-1',1],['ADD',0,1,'-2',1],
            ['MOVE',0,1,2,False]]
    result,last=ranges(events,[0,1,1],1,[0],float('inf'),{'events':0})
    assert result==[[0,1,1,1,2],[0,1,1,3,3]]
    assert last=={0:2,1:2}
    assert priority(result,last)[0]==[0,1,1,3,3]
    return ['exact coframe begins after MOVE','disjoint scalar aliases','incident signed ADD splits the cut range']


def main():
    assert __debug__
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--controls-only',action='store_true')
    args=parser.parse_args()
    price=loads(checked(args.root,'lead/PRICE.json',PRICE),object_pairs_hook=unique)
    assert price['head']==HEAD and price['caller']==CALLER and price['word_sha256']==WORD
    assert price['one_fixed_helper']==PIVOT and price['whole_compatible_pair_cap']==1
    assert len(price['other_role_cohort'])==CASES
    tests=controls()
    if args.controls_only:
        print(dumps(tests))
        return
    def stop(*_):
        raise TimeoutError('hard 25-second cap')
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+SECONDS-1
    progress={'events':0}
    out={'head':HEAD,'caller':CALLER,'price_sha256':PRICE,'word_sha256':WORD,
         'caps':{'events':EVENTS,'partners':CASES,'seconds':SECONDS},'controls':tests,'progress':progress}
    try:
        raw=decompress(checked(args.root,'inputs/7334-WORD.json.gz',WORD))
        assert sha256(raw).hexdigest()==PAYLOAD
        w=loads(raw,object_pairs_hook=unique)
        roles=price['other_role_cohort']
        assert len(w['program'])==EVENTS and w['public']==1501 and w['owned_fields']==68
        for role in roles:
            assert (w['initial'][role],w['final'][role])==(3,127)
        assert (w['initial'][PIVOT],w['final'][PIVOT])==(745,245)
        fixed=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
        assert fixed.isdisjoint(set(roles)|{PIVOT})
        a,b,c,d=(space(w['frames'][z]) for z in (3,745,245,127))
        assert (len(a),len(b),len(c),len(d))==(1,8,256,512) and a<b<c<d
        state=w['initial']+[None]*w['owned_fields']
        spans,last=ranges(w['program'],state,PIVOT,roles,deadline,progress)
        assert state==w['final']+[None]*w['owned_fields']
        ranked=priority(spans,last)
        out|={'ranges':spans,'raw_cuts':sum(b-a+1 for _,_,_,a,b in spans),
              'exact_pairs':sorted({(i,j) for i,j,_,_,_ in spans}),
              'selected':[[i,j,c,b] for i,j,c,a,b in ranked[:16]],
              'unvisited_representatives':ranked[16:],
              'last_scalar':last}
    except TimeoutError as exc:
        out|={'timeout':str(exc),'unresolved_roles':price['other_role_cohort']}
    finally:
        alarm(0)
    print(dumps(out,indent=2,sort_keys=True))
    if 'timeout' in out:
        raise SystemExit(2)


if __name__=='__main__':
    main()
