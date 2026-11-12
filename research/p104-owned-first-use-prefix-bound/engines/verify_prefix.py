"""Verify every owned private-prefix barrier and separating covector."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
PINS={
    '7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'R137-RESULT.json':'a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db',
    'R137-PRICE.json':'1e8270d9a48728327f7eab9610a272fbb8ef09518dc4ddc5ceb573be00ae2beb',
    'grouped_impulses.py':'9d63b7db64604c53a102b48c413cd656a97040a40c991f20ee190cc70057ecfc',
}
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
KEYS={30529,34515,36315,39866,39875,40554,41637,41996,42491,44242,44244}
RANKS={1:3,2:1,3:1,4:4,5:1,6:1}
EVENTS,SECONDS=76466,30


def checked(root,name,digest=None):
    raw=(root/'inputs'/name).read_bytes()
    if sha256(raw).hexdigest() != (digest or PINS[name]):
        raise ValueError('changed dependency '+name)
    return raw


def load(root,name,unique,digest=None):
    return loads(checked(root,name,digest),object_pairs_hook=unique)


def private(event,role):
    return event[0] in ('ADD','SCALE') and event[1] == role


def predecessors(root, engine):
    unique=engine['unique']
    price=load(root,'R137-PRICE.json',unique)
    result=load(root,'R137-RESULT.json',unique)
    assert price['head']==result['head']==HEAD and price['caller']==result['caller']==CALLER
    assert len(result['records'])==47 and not result['unvisited']
    stock={r['move_clock']:r for r in result['records'] if private(r['first_event'],r['role'])}
    assert stock.keys()==KEYS and Counter(r['rank'] for r in stock.values())==RANKS
    return stock


def controls(engine):
    assert private(['ADD',5,1,'1/2',4],5)
    assert private(['SCALE',5,'-1',4],5)
    assert not private(['ADD',1,5,'-1/2',4],5)
    assert not private(['COPY',5,1,'1/2',4],5)
    return engine['controls']()+['private owner write','outward ADD and COPY remain barriers']


def audit(word,stock,records,engine,deadline,progress):
    n,m,tape=(word[k] for k in ('public','owned_fields','program'))
    assert (n,m,len(tape))==(1501,68,EVENTS)
    state=word['initial']+[None]*m
    values=[{} for _ in state]
    fresh=set()
    impulses,columns={},{}
    for clock,r in records.items():
        if 'separator' not in r:
            continue
        weights=tuple(sorted((int(j),Q(v)) for j,v in r['separator'].items()))
        assert weights and all(0 <= j < n and v for j,v in weights)
        if weights not in impulses:
            c=impulses[weights]=len(impulses)
            for j,v in weights:
                values[j][c]=v
        columns[clock]=impulses[weights]
    pending={}
    output={}
    combine,scalar,sep=(engine[k] for k in ('combine','scalar','separator_check'))
    frames=word['frames']

    @cache
    def span(chart):
        out={0}
        for v in frames[chart]:
            assert v not in out
            out|={u^v for u in out}
        return out

    for t,event in enumerate(tape):
        progress['first_unvisited_event']=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError('literal scan')
        op,d,*a=event
        for role in (d,a[0]) if op in ('ADD','COPY') else (d,):
            if role not in pending:
                continue
            move,updates=pending[role]
            p=stock[move]
            assert state[role]==p['chart_to']
            if private(event,role):
                if not updates:
                    assert (t,event)==(p['first_clock'],p['first_event'])
                updates.append([t,event])
                continue
            assert updates
            pending.pop(role)
            r=records[move]
            expected_clock,expected_event=r['barrier_clock'],r['barrier']
            assert (t,event)==(expected_clock,expected_event), (move,t,event,r)
            assert updates==r['writes'], (move,updates,r)
            bank=[j for j,c in enumerate(state) if c==state[role] and j!=role]
            item=dict(move_clock=move,role=role,paid_rank=p['rank'],barrier=[t,event],private_prefix=updates)
            if op=='CLEAR':
                assert d==role
                item['decision']='observer-free CLEAR'
            elif op not in ('ADD','MOVE'):
                item['decision']='outside scope'
            elif move in columns:
                assert set(r['bank_roles']) <= set(bank)
                q=sep(values[role],(values[j] for j in bank),columns[move],Q(r['separator_value']))
                assert sum(Q(r['row'].get(j,'0'))*Q(v) for j,v in r['separator'].items())==q
                item|={'decision':'outside donor span','separator_value':str(q),
                       'live_donor_checks':len(bank),'owned_donor_checks':sum(j>=n for j in bank),
                       'extra_live_donors':sorted(set(bank)-set(r['bank_roles']))}
            else:
                item['decision']='requires exact candidate replay'
            output[move]=item
        if op=='MOVE':
            old,new,owned=a
            assert state[d]==old and owned==(d>=n)
            assert span(old)<span(new) or owned and span(new)<span(old)
            state[d]=new
            fresh.discard(d)
            if t in stock:
                p=stock[t]
                assert owned and p['role']==d
                assert (old,new,abs(len(frames[old])-len(frames[new])))==(p['chart_from'],p['chart_to'],p['rank'])
                assert d not in pending
                pending[d]=(t,[])
        elif op=='INIT':
            assert d>=n and state[d] is None
            state[d],values[d]=a[0],{}
            fresh.add(d)
        elif op=='CLEAR':
            assert d>=n and state[d]==a[0]
            state[d],values[d]=None,{}
            fresh.discard(d)
        elif op=='SCALE':
            assert state[d]==a[-1]
            q=scalar(a[0])
            values[d]={k:q*v for k,v in values[d].items()}
            fresh.discard(d)
        else:
            s,q,chart=a
            assert op in ('ADD','COPY') and d!=s and state[d]==state[s]==chart
            assert op!='COPY' or d>=n and d in fresh
            values[d]=combine(values[d] if op=='ADD' else {},values[s],scalar(q))
            fresh.discard(d)
        progress['events_visited']+=1
    progress['first_unvisited_event']=None
    assert not pending and not fresh and state==word['final']+[None]*m
    assert output.keys()==stock.keys()
    return [x for _,x in sorted(output.items())],len(impulses)


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--root',type=Path,default=ROOT)
    cli.add_argument('--price-sha')
    cli.add_argument('--lead-sha')
    cli.add_argument('--controls-only',action='store_true')
    args=cli.parse_args()
    checked(args.root,'grouped_impulses.py')
    engine=run_path(str(args.root/'inputs/grouped_impulses.py'))
    stock=predecessors(args.root,engine)
    tests=controls(engine)
    if args.controls_only:
        print(dumps(tests))
        return
    if not args.price_sha or not args.lead_sha:
        cli.error('authenticate both frozen price and lead result')
    unique=engine['unique']
    price=load(args.root,'R138-PRICE.json',unique,args.price_sha)
    lead=load(args.root,'R138-LEAD-RESULT.json',unique,args.lead_sha)
    assert price['head']==lead['head']==HEAD and price['caller']==lead['caller']==CALLER
    assert price['case_cap']==len(KEYS) and price['event_cap']==EVENTS and price['runner_seconds_cap']==SECONDS
    assert {int(k):v for k,v in price['rank_counts'].items()}==RANKS
    assert {r['move_clock'] for r in price['rows']}==KEYS
    assert not lead['unvisited'] and lead['counts']=={'outside donor span':len(KEYS)}
    records={r['move_clock']:r for r in lead['rows']}
    assert records.keys()==KEYS
    def stop(*_):
        raise TimeoutError('hard 30-second limit')
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+SECONDS-1
    progress={'events_visited':0}
    result={'head':HEAD,'caller':CALLER,'controls':tests,'progress':progress,
            'pins':PINS|{'R138-PRICE.json':args.price_sha,'R138-LEAD-RESULT.json':args.lead_sha},
            'caps':{'events':EVENTS,'cases':len(KEYS),'seconds':SECONDS}}
    try:
        raw=decompress(checked(args.root,'7334-WORD.json.gz'))
        assert sha256(raw).hexdigest()==PAYLOAD
        cases,k=audit(loads(raw,object_pairs_hook=unique),stock,records,engine,deadline,progress)
        result|=dict(cases=cases,grouped_impulses=k,counts=Counter(x['decision'] for x in cases),
                     unresolved=[x['move_clock'] for x in cases if x['decision']=='requires exact candidate replay'])
    except TimeoutError as e:
        result|=dict(timeout=str(e),unresolved=sorted(KEYS))
    finally:
        alarm(0)
    print(dumps(result,indent=2,sort_keys=True))
    if 'timeout' in result:
        raise SystemExit(2)


if __name__=='__main__':
    main()
