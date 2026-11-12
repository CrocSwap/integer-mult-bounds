"""Exact source-support incidence screen, maintaining chart support incrementally."""
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT=Path(__file__).resolve().parent
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
PINS={
 'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
 'inputs/COFRAME.json':'c3479d6524597b94a39889b1f4c4828f310cef6a37fe26ebefcbab84627dc1e5',
 'inputs/R200-RESULT.json':'54b1751413855db0b87b792206a18336c16aa934d1c9fbdc209daa4a58a692a5',
 'inputs/R92-PRICE.json':'05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f',
 'inputs/pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
 'inputs/reverse_span.py':'f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff',
}
CASES,SECONDS=967,25


def unique(pairs):
    out=dict(pairs)
    assert len(out)==len(pairs),'duplicate key'
    return out


def read(name):
    raw=(ROOT/name).read_bytes()
    assert sha256(raw).hexdigest()==PINS[name],name
    return raw


def decoded(name):
    return loads(read(name),object_pairs_hook=unique)


@cache
def coeff(text):
    x=Q(text)
    assert x
    return x


def stop(*_):
    raise TimeoutError('25-second exact support cap')


def inventory(word,cases,complete):
    n,owned=word['public'],word['owned_fields']
    charts=word['initial']+[None]*owned
    rows=[{j:Q(1)} for j in range(n)]+[{} for _ in range(owned)]
    support,bank=defaultdict(Counter),defaultdict(set)
    history=[deque(maxlen=3) for _ in rows]
    for j,chart in enumerate(charts[:n]):
        support[chart][j]+=1
        bank[chart].add(j)
    src_requests={c['clocks'][1]:c for c in cases}
    bank_requests={c['clocks'][2]:c for c in cases}
    assert len(src_requests)==len(bank_requests)==len(cases)
    source_rows={}
    detected=[]
    starts={}
    for t,event in enumerate(word['program']):
        op,d,*args=event
        current=charts[d]
        old=rows[d]
        if t in src_requests:
            case=src_requests[t]
            assert op=='ADD' and d==case['role'] and args[0]==case['peer']
            source_rows[t]=rows[args[0]].copy()
        if op=='MOVE':
            a,b,is_owned=args
            assert current==a and is_owned==(d>=n)
            bank[a].remove(d)
            bank[b].add(d)
            for j in old:
                support[a][j]-=1
                support[b][j]+=1
            charts[d]=b
        elif op=='INIT':
            f,=args
            assert d>=n and current is None and not old
            bank[f].add(d)
            charts[d]=f
            starts[d]=t
        elif op=='CLEAR':
            f,=args
            assert d>=n and current==f
            bank[f].remove(d)
            for j in old:
                support[f][j]-=1
            rows[d]={}
            charts[d]=None
            starts.pop(d)
        elif op=='SCALE':
            c,f=args
            assert current==f
            factor=coeff(c)
            rows[d]={j:factor*x for j,x in old.items()}
        else:
            assert op in ('COPY','ADD')
            s,c,f=args
            assert s!=d and current==charts[s]==f
            factor=coeff(c)
            if op=='COPY':
                assert d>=n and not old
                new={j:factor*x for j,x in rows[s].items()}
            else:
                new=old.copy()
                for j,x in rows[s].items():
                    value=new.get(j,0)+factor*x
                    if value:
                        new[j]=value
                    else:
                        new.pop(j,None)
            for j in old.keys()-new.keys():
                support[f][j]-=1
            for j in new.keys()-old.keys():
                support[f][j]+=1
            rows[d]=new
            history[s].append(t)
        history[d].append(t)
        if op=='MOVE' and len(history[d])==3:
            first,middle,last=history[d]
            x,y=word['program'][first],word['program'][middle]
            if x[0]=='MOVE' and y[:2]==['ADD',d]:
                detected.append((first,middle,last))
        if t in bank_requests:
            case=bank_requests[t]
            a,m,b=case['clocks']
            r=case['role']
            assert op=='MOVE' and r==d and t==b
            assert tuple(history[d])==(a,m,b)
            target=source_rows.pop(m)
            f=charts[d]
            donors=sorted(bank[f]-{d})
            hits={j:support[f][j]-int(j in rows[d]) for j in target}
            assert all(0<=c<=len(donors) for c in hits.values())
            missing=[j for j in sorted(hits) if not hits[j]]
            complete.append({'clocks':case['clocks'],'role':d,'peer':case['peer'],'chart':f,
                             'bank_count':len(donors),'bank_role_sha256':sha256(dumps(donors).encode()).hexdigest(),
                             'target_support_size':len(target),'missing_count':len(missing),
                             'missing_witness':[missing[0],str(target[missing[0]])] if missing else None,
                             'target_row':{j:str(x) for j,x in target.items()},
                             'peer_init':starts.get(case['peer']), 'ranks':case['ranks'],
                             'gross':case['gross']})
    assert not starts and not source_rows and charts==word['final']+[None]*owned
    assert sorted(detected)==sorted(tuple(c['clocks']) for c in cases)


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    raw=decompress(read('inputs/7334-WORD.json.gz'))
    assert sha256(raw).hexdigest()==PAYLOAD
    word=loads(raw,object_pairs_hook=unique)
    assert (word['public'],word['owned_fields'],len(word['program']))==(1501,68,76466)
    spec=decoded('inputs/COFRAME.json')
    old=decoded('inputs/R92-PRICE.json')
    control=decoded('inputs/R200-RESULT.json')
    assert (spec['head'],spec['caller'])==(old['head'],old['caller_head'])==(HEAD,CALLER)
    cases=[c for c in spec['cases'] if c['events'][1][1]==c['role']]
    assert len(cases)==CASES and len({tuple(c['clocks']) for c in cases})==CASES
    read('inputs/pricing.py')
    price=run_path(str(ROOT/'inputs/pricing.py'))['cost']
    for c in cases:
        ranks=[len(word['frames'][j]) for j in (c['events'][0][2],c['events'][0][3],c['events'][2][3])]
        a,b,r=abs(ranks[1]-ranks[0]),abs(ranks[2]-ranks[1]),abs(ranks[2]-ranks[0])
        assert r==a+b
        h=Counter((a,b));h[r]-=1
        quote=price({j:17*v for j,v in h.items() if v},Q(old['old_crossing_upper']))
        assert 0<quote[0]<=quote[1]<17
        c.update(ranks=[a,b,r],gross=list(map(str,quote)))
    complete=[]
    capped=False
    reason=None
    try:
        inventory(word,cases,complete)
    except TimeoutError as err:
        capped,reason=True,str(err)
    finally:
        alarm(0)
    observed={tuple(c['clocks']) for c in complete}
    unresolved=[c['clocks'] for c in cases if tuple(c['clocks']) not in observed]
    match=next((c for c in complete if c['clocks']==control['key'][:3]),None)
    if match:
        assert match['missing_witness']==[control['decision']['coordinate'],control['decision']['target_coefficient']]
        assert match['bank_count']==control['bank_cap']
    survivors=sorted((c for c in complete if c['missing_witness'] is None),
                     key=lambda c:(-Q(c['gross'][0]),c['clocks']))
    print(dumps({'head':HEAD,'caller':CALLER,'payload':PAYLOAD,'pins':PINS,'case_cap':CASES,
                 'seconds_cap':SECONDS,'capped':capped,'cap_reason':reason,'records':complete,
                 'excluded_count':sum(c['missing_witness'] is not None for c in complete),
                 'screen_survivors':survivors,'unvisited':unresolved,
                 'survivor_relaxed_gross_upper':str(sum(Q(c['gross'][1]) for c in survivors))},
                indent=2,sort_keys=True))
    if capped:
        raise SystemExit(2)


if __name__=='__main__':
    main()
