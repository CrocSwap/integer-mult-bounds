"""Reverse-contact audit of the exact #7314 public productive entrances."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD='9d0119eb12fbd9fa534b48cd37b68e7099757b91'
CALLER_HEAD='07a76c5e2738882c0cb322278e56f6cae3c9885d'
WORD='7314/WORD.json.gz'
CALLER='7113/CALLER.json'
PINS={
    WORD:'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9',
    CALLER:'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
}
OUTSIDE={863,1355,1568}
LIMIT=1101


def decode(raw):
    def unique(pairs):
        value=dict(pairs)
        assert len(value)==len(pairs),'duplicate JSON key'
        return value
    return json.loads(raw,object_pairs_hook=unique)


def audit(word,deadline):
    n=word['public']
    main=set(word['live']) | {r+112 for r in word['live']}
    main.update(word['hosted']['X2']+word['hosted']['Y2'])
    dimensions=list(map(len,word['frames']))
    first={}
    current=word['final']+[None]*word['owned_fields']
    tape=word['program']
    visited=0
    histogram=Counter()
    counted_moves=Counter()

    @cache
    def span(chart):
        vectors={0}
        for v in word['frames'][chart]:
            assert v not in vectors
            vectors.update({x^v for x in vectors})
        return vectors

    helpers=[]
    for r,(a,z) in enumerate(zip(word['initial'],word['final'],strict=True)):
        if r not in main:
            assert span(a)<span(z)
            size=dimensions[z]-dimensions[a]
            histogram[size]+=1
            helpers.append((r,a,z,size))
    assert len(helpers)<=LIMIT

    for t in range(len(tape)-1,-1,-1):
        if monotonic()>=deadline:
            break
        visited+=1
        event=tape[t]
        op,d,*rest=event
        if op=='MOVE':
            a,b,owned=rest
            assert owned==(d>=n) and current[d]==b
            assert span(a)<span(b) or owned and span(b)<span(a)
            counted_moves[abs(dimensions[b]-dimensions[a])]+=1
            current[d]=a
            contacts=((d,'move'),)
        elif op in ('INIT','CLEAR'):
            chart,=rest
            assert d>=n and current[d]==(chart if op=='INIT' else None)
            current[d]=None if op=='INIT' else chart
            contacts=((d,'lifetime'),)
        else:
            assert op in ('ADD','COPY','SCALE') and Fraction(rest[-2])
            contacts=((d,'destination'),(rest[0],'source')) if op in ('ADD','COPY') else ((d,'unary'),)
            assert len({r for r,_ in contacts})==len(contacts)
            assert all(current[r]==rest[-1] for r,_ in contacts)
            if op=='COPY':
                assert d>=n
        for r,access in contacts:
            if r<n and r not in main:
                # Overwrite on the backward walk, leaving the earliest exact touch.
                first[r]=(t,access,event)
    exhausted=visited==len(tape)
    if exhausted:
        assert current==word['initial']+[None]*word['owned_fields']

    decisions=[]
    for r,a,z,t in helpers if exhausted else ():
        if monotonic()>=deadline:
            break
        earliest=first.get(r)
        record=dict(role=r,initial=a,final=z,old_productive_rank=t,
                    first_clock=earliest[0] if earliest else None,
                    first_access=earliest[1] if earliest else None,
                    first_event=earliest[2] if earliest else None)
        if r in OUTSIDE:
            status='excluded_comparator_role'
        elif t<2:
            status='zero_residual_rank'
        elif earliest is None or earliest[2][0]!='MOVE':
            status='first_contact_not_move'
        else:
            _,d,u,v,owned=earliest[2]
            assert d==r and u==a and not owned
            if dimensions[v]-dimensions[u]!=1:
                status='first_move_not_rank_one'
            elif not span(u)<span(v)<span(z):
                status='first_move_not_strictly_inside'
            else:
                status='support_only'
                record.update(raised_entrance=v,new_productive_rank=t-1,
                              remove_move_clock=earliest[0],rank_deltas_per_copy={'P1':-1,'Told':-1,'Tnew':1})
        decisions.append(record | {'status':status})
    remaining=helpers[len(decisions):]
    return dict(literal_events=len(tape),visited_events=visited,reverse_exhausted=exhausted,
                first_unvisited_reverse_clock=None if exhausted else len(tape)-1-visited,
                complete=exhausted and not remaining,helpers=len(helpers),main_and_hosted_roles=len(main),
                productive_histogram=dict(histogram),paid_native_histogram_visited=dict(counted_moves),
                visited_helpers=len(decisions),remaining_roles=[row[0] for row in remaining],
                remaining_rank_histogram=dict(Counter(row[3] for row in remaining if row[0] not in OUTSIDE and row[3]>=2)),
                status_counts=dict(Counter(row['status'] for row in decisions)),
                survivors=[row for row in decisions if row['status']=='support_only'],rows=decisions)


def controls():
    toy=dict(public=2,owned_fields=0,frames=[[],[1],[1,2]],live=[],hosted={'X2':[],'Y2':[]},
        initial=[0,0],final=[2,2],program=[
            ['MOVE',0,0,1,False],['MOVE',0,1,2,False],['MOVE',1,0,2,False]])
    pass_=audit(toy,float('inf'))
    assert pass_['complete'] and len(pass_['survivors'])==1
    assert pass_['survivors'][0]['role']==0 and pass_['survivors'][0]['new_productive_rank']==1
    altered=toy | {'program':[['ADD',1,0,'-2',0]]+toy['program']}
    blocked=audit(altered,float('inf'))
    assert blocked['complete'] and not blocked['survivors']
    assert blocked['rows'][0]['first_access']=='source' and blocked['rows'][0]['first_clock']==0
    return ['strict_rank_two_nesting_passes','earlier_add_source_prevents_first_move']


def main():
    p=ArgumentParser()
    p.add_argument('inputs',type=Path,nargs='?',default=Path(__file__).resolve().parent/'inputs')
    p.add_argument('--price',type=Path)
    p.add_argument('--price-sha')
    p.add_argument('--seconds',type=int,default=20,choices=range(2,21),metavar='2..20')
    p.add_argument('--controls-only',action='store_true')
    a=p.parse_args()
    check=controls()
    if a.controls_only:
        print(json.dumps(check))
        return
    if a.price is None or a.price_sha is None:
        p.error('an exact saved price receipt and SHA-256 are required before support')

    def stop(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,stop)
    alarm(a.seconds)
    deadline=monotonic()+a.seconds-1
    try:
        price=a.price.read_bytes()
        assert sha256(price).hexdigest()==a.price_sha,'changed price receipt'
        assert decode(price)['head']==HEAD,'wrong price comparator'
        files={}
        for rel,digest in PINS.items():
            raw=(a.inputs/rel).read_bytes()
            assert sha256(raw).hexdigest()==digest,('changed input',rel)
            files[rel]=raw
        c=decode(files[CALLER])
        assert [e[1] for e in c['events'] if e[0]=='J']==list(range(1,18))
        result=audit(decode(gzip.decompress(files[WORD])),deadline)
        assert result['helpers']==LIMIT and result['main_and_hosted_roles']==400
        if result['complete']:
            assert result['visited_events']==76461 and result['visited_helpers']==LIMIT
    except TimeoutError:
        print(json.dumps(dict(head=HEAD,pins=PINS,status='hard_timeout',unverified=LIMIT)))
        raise SystemExit(2)
    finally:
        alarm(0)
    print(json.dumps(dict(head=HEAD,caller_head=CALLER_HEAD,pins=PINS,controls=check,
                          price_sha256=a.price_sha,copies=17,seconds_cap=a.seconds,
                          cap=LIMIT,**result),sort_keys=True,indent=2))


if __name__=='__main__':
    assert __debug__
    main()
