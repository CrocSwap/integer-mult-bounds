"""Independent reverse/forward census of four ascending MOVE incidences at a mixed ADD."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from time import monotonic

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
CROSSING = Fraction('0.0036462214364462343366888845568981')
PINS = {
    'WORD.json.gz': 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9',
    'EARLY-RESULT.json': 'b5043855411432b24336ecc443cba9ebfae6392e2045ddd01c87cfe2c51f5f08',
    'pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
}
PROTECTED = {863, 1355, 1568}
LIMIT = 128
SECONDS = 22


def unique(rows):
    obj = dict(rows)
    if len(rows) != len(obj):
        raise ValueError('duplicate JSON key')
    return obj


def read(raw):
    return json.loads(raw, object_pairs_hook=unique)


def checked(path, digest):
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError('changed input: ' + path.name)
    return data


def contact(event):
    tag, dest, *args = event
    if tag in ('ADD', 'COPY'):
        assert dest != args[0]
        return dest, args[0]
    assert tag in ('MOVE', 'SCALE', 'INIT', 'CLEAR')
    return (dest,)


def is_mixed(event, public):
    return event[0] == 'ADD' and (event[1] < public) != (event[2] < public)


def contacts(events, n, fields, deadline):
    later = [None] * fields
    next_at = {}
    for clock in range(len(events)-1, -1, -1):
        if clock % 128 == 0 and monotonic() >= deadline:
            return [], ['reverse', clock]
        event = events[clock]
        roles = contact(event)
        if is_mixed(event, n):
            next_at[clock] = tuple(later[r] for r in roles)
        for r in roles:
            later[r] = clock
    prior = [None] * fields
    result = []
    for clock, event in enumerate(events):
        if clock % 128 == 0 and monotonic() >= deadline:
            return result, ['forward', clock]
        roles = contact(event)
        if clock in next_at:
            result.append((clock, roles, tuple(prior[r] for r in roles), next_at[clock]))
        for r in roles:
            prior[r] = clock
    return result, None


def remainder(value, pivots):
    while value:
        high = value.bit_length()-1
        if high not in pivots:
            break
        value ^= pivots[high]
    return value


def frame_tests(frames):
    @cache
    def echelon(frame):
        pivots = {}
        for vector in frames[frame]:
            left = remainder(vector, pivots)
            assert left
            pivots[left.bit_length()-1] = left
        return pivots

    @cache
    def nested(left, right):
        return len(frames[left]) < len(frames[right]) and not any(
            remainder(vector, echelon(right)) for vector in frames[left])
    return nested


def structure(word, deadline):
    n = word['public']
    events = word['program']
    forbidden = PROTECTED | set(word['live']) | {r+112 for r in word['live']}
    forbidden.update(word['hosted']['X2'] + word['hosted']['Y2'])
    nested = frame_tests(word['frames'])
    stock, pending = contacts(events, n, n+word['owned_fields'], deadline)
    decisions = []
    for clock, roles, prev, next_ in stock:
        chart = events[clock][-1]
        row = {'clock':clock,'roles':roles,'old_chart':chart,'before':prev,'after':next_}
        if set(roles) & forbidden:
            status = 'protected_operand'
        elif any(t is None or events[t][0]!='MOVE' for t in prev+next_):
            status = 'neighbor_not_move'
        else:
            assert len(set(prev+next_)) == 4 and Fraction(events[clock][3])
            endpoints = []
            for role, a, b in zip(roles, prev, next_, strict=True):
                _, source_role, start, left_chart, left_owned = events[a]
                _, dest_role, right_chart, finish, right_owned = events[b]
                assert source_role == dest_role == role and left_chart == right_chart == chart
                assert left_owned == right_owned == (role >= n)
                endpoints.append((start,finish))
            row['endpoints'] = endpoints
            status = 'all_ascending' if all(nested(a,chart) and nested(chart,b) for a,b in endpoints) else 'nonascending_move'
        decisions.append(row | {'status':status})
    return decisions, pending, nested


def signed_delta(old, new):
    delta = Counter(old)
    delta.subtract(new)
    assert sum(delta.values()) == sum(r*v for r,v in delta.items()) == 0
    return tuple(sorted((r,17*v) for r,v in delta.items() if v))


def limits(row, dimensions):
    outer = [(dimensions[a],dimensions[b]) for a,b in row['endpoints']]
    old_dim = dimensions[row['old_chart']]
    old = tuple(rank for a,b in outer for rank in (old_dim-a,b-old_dim))
    for d in range(max(a for a,b in outer)+1,min(b for a,b in outer)):
        if d == old_dim:
            continue
        new = tuple(rank for a,b in outer for rank in (d-a,b-d))
        yield d,old,new,signed_delta(old,new)


def contains(nested, endpoints, chart):
    return all(nested(a,chart) and nested(chart,b) for a,b in endpoints)


def controls():
    word = {'public':1,'owned_fields':1,'live':[],'hosted':{'X2':[],'Y2':[]},
            'frames':[[],[1,2],[1,2,4,8],[1],[16]], 'program':[
            ['INIT',1,0],['MOVE',0,0,1,False],['MOVE',1,0,1,True],['ADD',0,1,'3/2',1],
            ['MOVE',1,1,2,True],['MOVE',0,1,2,False],['CLEAR',1,2]]}
    rows,pending,nested = structure(word,float('inf'))
    assert pending is None and [r['status'] for r in rows] == ['all_ascending']
    assert contains(nested,rows[0]['endpoints'],3) and not contains(nested,rows[0]['endpoints'],4)
    assert list(limits(rows[0],[0,2,4,1,1]))[0] == (1,(2,2,2,2),(1,3,1,3),((1,-34),(2,68),(3,-34)))
    blocked = word | {'program':[*word['program'][:4],['ADD',1,0,'-1',1],*word['program'][4:]]}
    rows,pending,_ = structure(blocked,float('inf'))
    assert pending is None and all(r['status']=='neighbor_not_move' for r in rows)
    return ['same_coframe_spreads_paid_rank','wrong_coframe_rejected','intervening_source_read_rejected']


def audit(word, price, cost, baseline, deadline):
    decisions,pending,nested = structure(word,deadline)
    stock = [r for r in decisions if r['status']=='all_ascending']
    dimensions = [len(basis) for basis in word['frames']]
    dim_notes, variants = [], []

    @cache
    def directed(delta):
        new = baseline.copy()
        new.update(dict(delta))
        credit = cost(dict(delta),CROSSING)
        margin = cost(new,CROSSING)
        return credit,margin

    for row in stock if pending is None else ():
        for dim,old,new,delta in limits(row,dimensions):
            credit,margin = directed(delta)
            item = {'clock':row['clock'],'dimension':dim,'old_ranks':old,'new_ranks':new,
                    'signed_net_delta':dict(delta),'gross':list(map(str,credit)),'margin':list(map(str,margin))}
            dim_notes.append(item)
            if margin[1] > 0:
                variants.extend((row,chart,item) for chart,rank in enumerate(dimensions) if rank == dim)
    results = []
    for row,chart,item in variants:
        if len(results) >= LIMIT or monotonic() >= deadline:
            break
        legal = contains(nested,row['endpoints'],chart)
        status = 'wrong_nested_chart' if not legal else 'eligible' if Fraction(item['margin'][0]) > 0 else 'price_inconclusive'
        results.append({'chart':chart,'status':status,**item})
    unvisited = [[row['clock'],chart,item['margin'][1]] for row,chart,item in variants[len(results):]]
    unresolved = [r for r in results if r['status']=='price_inconclusive']
    return {'status':'EXHAUSTED' if pending is None and not unvisited and not unresolved else 'INCOMPLETE',
            'word_events':len(word['program']),'mixed_adds':len(decisions),
            'status_counts':dict(Counter(r['status'] for r in decisions)),
            'structural':stock,'clock_rows':decisions,'first_unvisited_contact':pending,
            'priced_dimensions':dim_notes,'variant_count':len(variants),'tested_variants':len(results),
            'variants':results,'survivors':[r for r in results if r['status']=='eligible'],
            'unvisited':unvisited,'unresolved':unresolved,
            'one_edit_optimistic_upper':price.get('one_edit_optimistic_upper')}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,default=Path('inputs'))
    parser.add_argument('--price',type=Path)
    parser.add_argument('--price-sha')
    parser.add_argument('--controls-only',action='store_true')
    args = parser.parse_args()
    assert __debug__
    checks = controls()
    if args.controls_only:
        print(json.dumps(checks))
        return
    if args.price is None or args.price_sha is None:
        parser.error('frozen price and SHA-256 required before decoding')
    deadline = monotonic()+SECONDS
    price = read(checked(args.price,args.price_sha))
    assert price['head']==HEAD and price.get('caller_head',price.get('caller'))==CALLER
    data = {name:checked(args.inputs/name,digest) for name,digest in PINS.items()}
    assert read(data['CALLER.json'])['stages']==17
    invoice = read(data['EARLY-RESULT.json'])['invoice']
    p,t = (Counter({int(r):v for r,v in invoice[key].items()}) for key in ('P','T'))
    assert (sum(p.values()),sum(t.values()),invoice['S'],invoice['empty_root_credits'])==(110536,22461,1424,0)
    baseline = t.copy()
    baseline.subtract(p)
    cost = run_path(str(args.inputs/'pricing.py'))['cost']
    assert cost(baseline,CROSSING)[1] < 0
    result = audit(read(decompress(data['WORD.json.gz'])),price,cost,baseline,deadline)
    assert len(result['structural']) <= 47
    print(json.dumps(result | {'head':HEAD,'caller_head':CALLER,'price_sha256':args.price_sha,
                               'input_sha256':PINS,'controls':checks},sort_keys=True,indent=2))


if __name__=='__main__':
    main()
