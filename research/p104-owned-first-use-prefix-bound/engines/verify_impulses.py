"""Authenticate and replay every first-use donor separator by grouped exact impulses."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    '7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'R80-OWNED.json': 'db293c67c896f54788681b7a8a9fec5f13da0e31fe5b3dd65fbe30e370ff1d2e',
    'R92-PRICE.json': '05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f',
    'R137-PRICE.json': '1e8270d9a48728327f7eab9610a272fbb8ef09518dc4ddc5ceb573be00ae2beb',
    'R137-LEAD-RESULT.json': 'a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db',
    'R137-PLAN.md': 'a19896a80e504a2df398059ef5e64df2ed598d7903eb3a66a3ffc1b2b9b332c7',
}
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PAYLOAD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
EVENTS,CASES,SECONDS = 76466,47,35
RANKS = {1:20,2:9,3:2,4:13,5:2,6:1}


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError('duplicate JSON key')
    return out


def read(root,path):
    data = (root/'inputs'/path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError('changed dependency '+path)
    return data


def authenticate(root):
    names = ('R80-OWNED','R92-PRICE','R137-PRICE','R137-LEAD-RESULT')
    stock,base,price,lead = (loads(read(root,p+'.json'),object_pairs_hook=unique) for p in names)
    read(root,'R137-PLAN.md')
    assert all(x['head'] == HEAD for x in (stock,base,price,lead))
    assert base['caller_head'] == price['caller'] == lead['caller'] == CALLER
    assert price['pins'] == lead['pins']
    assert all(price['pins']['inputs/'+name] == PINS[name] for name in ('7334-WORD.json.gz','R80-OWNED.json','R92-PRICE.json'))
    assert price['stock'] == stock['paid_owned_rank'] == {str(r):v for r,v in RANKS.items()}
    assert (price['case_cap'],price['event_cap'],price['runner_seconds']) == (CASES,EVENTS,SECONDS)
    assert not lead['unvisited'] and lead['counts'] == {'outside donor span':CASES}
    assert len(lead['records']) == CASES and len({r['move_clock'] for r in lead['records']}) == CASES
    return lead['records']


@cache
def scalar(s):
    q = Q(s)
    assert q
    return q


def combine(old,source,q):
    out = old.copy()
    for k,v in source.items():
        x = out.get(k,0)+q*v
        if x:
            out[k] = x
        else:
            out.pop(k,None)
    return out


def separator_check(row,donors,column,claimed):
    assert all(not d.get(column) for d in donors), 'donor separator value is nonzero'
    actual = row.get(column,0)
    assert actual == claimed and actual, 'owner separator value differs or is zero'
    return actual


def controls():
    assert combine({0:Q(1),1:Q(2)},{0:Q(2),2:Q(3)},Q(-1,2)) == {1:Q(2),2:Q(-3,2)}
    assert separator_check({0:Q(-1,2)},[{2:Q(1)}],0,Q(-1,2)) == Q(-1,2)
    try:
        separator_check({0:Q(-1,2)},[{0:Q(1)}],0,Q(-1,2))
    except AssertionError as e:
        assert 'donor separator' in str(e)
    else:
        raise AssertionError('mutated nonannihilating donor passed')
    return ['exact signed simultaneous impulse','known separator','mutated nonannihilating donor rejected']


def audit(word,records,deadline,progress,verified):
    n,m,tape = (word[k] for k in ('public','owned_fields','program'))
    assert (n,m,len(tape)) == (1501,68,EVENTS)
    state = word['initial']+[None]*m
    values = [{} for _ in state]
    distinct, cases = {},{}
    for r in records:
        q = tuple(sorted((int(j),scalar(v)) for j,v in r['separator'].items()))
        assert q and all(0 <= j < n for j,_ in q)
        if q not in distinct:
            k = distinct[q] = len(distinct)
            for j,v in q:
                values[j][k] = v
        cases[r['move_clock']] = r,distinct[q]
    pending,found,fresh = {},{},set()
    rank_counts = Counter()
    frames = word['frames']

    @cache
    def space(chart):
        out={0}
        for v in frames[chart]:
            assert v not in out
            out |= {x^v for x in out}
        return out

    for t,e in enumerate(tape):
        progress['first_unvisited_event'] = t
        if t%128 == 0 and monotonic() >= deadline:
            raise TimeoutError('cooperative 35-second cap')
        op,d,*args = e
        for role in (d,args[0]) if op in ('ADD','COPY') else (d,):
            if role not in pending:
                continue
            old_t,paid_rank = pending.pop(role)
            r,column = cases[old_t]
            assert (r['role'],r['first_clock'],r['first_event']) == (role,t,e)
            assert op in ('ADD','SCALE') and r['delay_events'] == t-old_t-1
            assert state[role] == r['chart_to']
            bank = [j for j,chart in enumerate(state) if j != role and chart == state[role]]
            recorded = set(r['bank_roles'])
            assert recorded <= set(bank) and r['bank_roles'] == sorted(recorded)
            claimed = Q(r['separator_value'])
            owner = separator_check(values[role],(values[j] for j in bank),column,claimed)
            assert sum(Q(r['row'].get(j,'0'))*Q(v) for j,v in r['separator'].items()) == owner
            found[old_t] = dict(move_clock=old_t,first_clock=t,role=role,paid_rank=paid_rank,lead_span_rank=r.get('span_rank'),
                                chart=r['chart_to'],owner_value=str(owner),donor_count=len(bank),
                                lead_bank_count=len(recorded), extra_live_donors=sorted(set(bank)-recorded),
                                owned_donors=[j for j in bank if j >= n])
            verified.append(old_t)
        if op == 'MOVE':
            a,b,owned = args
            assert owned == (d >= n) and state[d] == a
            assert space(a) < space(b) or owned and space(b) < space(a)
            state[d] = b
            fresh.discard(d)
            if owned:
                rank = abs(len(frames[a])-len(frames[b]))
                r,_ = cases[t]
                assert r['role'] == d and (r['chart_from'],r['chart_to'],r['rank']) == (a,b,rank)
                assert d not in pending
                pending[d] = (t,rank)
                rank_counts[rank] += 1
        elif op == 'INIT':
            assert d >= n and state[d] is None
            state[d],values[d] = args[0],{}
            fresh.add(d)
        elif op == 'CLEAR':
            assert d >= n and state[d] == args[0]
            state[d],values[d] = None,{}
            fresh.discard(d)
        elif op == 'SCALE':
            assert state[d] == args[-1]
            q=scalar(args[0])
            values[d]={k:q*v for k,v in values[d].items()}
            fresh.discard(d)
        else:
            s,q,chart=args
            assert op in ('ADD','COPY') and d != s and state[s] == state[d] == chart
            assert op != 'COPY' or d >= n and d in fresh
            values[d]=combine(values[d] if op == 'ADD' else {},values[s],scalar(q))
            fresh.discard(d)
        progress['events_visited'] += 1
    progress['first_unvisited_event'] = None
    assert not pending and not fresh and state == word['final']+[None]*m
    assert found.keys() == cases.keys() and rank_counts == RANKS
    return {'cases':[r for _,r in sorted(found.items())],'paid_owned_ranks':rank_counts,
            'grouped_impulses':len(distinct),'bank_role_checks':sum(r['donor_count'] for r in found.values())}


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--root',type=Path,default=ROOT)
    cli.add_argument('--controls-only',action='store_true')
    args=cli.parse_args()
    records=authenticate(args.root)
    checks=controls()
    if args.controls_only:
        print(dumps(checks))
        return
    def stop(*_):
        raise TimeoutError('hard 35-second cap')
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+SECONDS-1
    progress={'events_visited':0}
    verified=[]
    try:
        raw=decompress(read(args.root,'7334-WORD.json.gz'))
        assert sha256(raw).hexdigest() == PAYLOAD
        result=audit(loads(raw,object_pairs_hook=unique),records,deadline,progress,verified)
    except TimeoutError as exc:
        result={'timeout':str(exc)}
    finally:
        alarm(0)
    result |= {'head':HEAD,'caller':CALLER,'controls':checks,'progress':progress,
               'pins':{'inputs/'+p:d for p,d in PINS.items()},
               'unresolved':sorted({r['move_clock'] for r in records}-set(verified)),
               'caps':{'events':EVENTS,'cases':CASES,'seconds':SECONDS}}
    print(dumps(result,indent=2,sort_keys=True))
    if 'timeout' in result:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
