"""Directed price and bounded two-transfer endpoint test on Type B."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from math import isqrt
from pathlib import Path
from runpy import run_path
from time import monotonic

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
CALLER_HEAD = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
ADMISSION = '41b8a189dffeb768e5843446cdc469f9cc2f0aa038d0a593cf2be43aa009a9a3'
PINS = {
    'admission/ADMITTED.json': ADMISSION,
    'inputs/7113/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/7298/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'inputs/7314/EARLY-RESULT.json': 'b5043855411432b24336ecc443cba9ebfae6392e2045ddd01c87cfe2c51f5f08',
    'inputs/r52/screen.py': 'cdf54b266ac31fd0efe544badbb9840598d4c63c4d3cd363f60ae9a74cc4b256',
    'inputs/r56/PRICE.json': '6f3510db09e18278c0f18d8e0cbe1242fc48e999dafc87cb04cc87e240b93819',
}


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError('Duplicate JSON key')
    return out


def decode(data):
    return loads(data, object_pairs_hook=unique)


def authenticated(root):
    files = {}
    for path,digest in PINS.items():
        raw = (root/path).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f'Changed input {path}')
        files[path] = raw
    a = decode(files['admission/ADMITTED.json'])
    assert a['head'] == HEAD and a['caller_sha256'] == PINS['inputs/7113/CALLER.json']
    assert a['status'] == 'independently_reproduced_comparable'
    assert set(a['stages']) == {'early','native','caller','frontier'}
    for row in [*a['stages'].values(), a['source_history']['evidence']]:
        assert sha256((root/'admission'/row['path']).read_bytes()).hexdigest() == row['sha256']
    return files


def inventory(r56):
    odd = {int(k):v for k,v in r56['odd_jobs'].items()}
    even = {int(k):v for k,v in r56['even_jobs'].items()}
    assert len(odd) == 4 and len(even) == 26 and not set(odd) & set(even)
    assert [k for k,v in even.items() if len(v[1]) == 8] == [2324,2337]
    return odd, even


def price(root, files):
    r56 = decode(files['inputs/r56/PRICE.json'])
    inv = decode(files['inputs/7314/EARLY-RESULT.json'])['invoice']
    assert r56['comparator_admission']['head'] == HEAD and r56['caller_head'] == CALLER_HEAD
    assert r56['complete_paid'] == inv['P'] and r56['complete_targets'] == inv['T']
    assert (sum(inv['P'].values()),sum(inv['T'].values()),inv['S'],inv['empty_root_credits']) == (110536,22461,1424,0)
    net = Counter({int(k):v for k,v in inv['T'].items()})
    net.subtract({int(k):v for k,v in inv['P'].items()})
    directed = run_path(str(root/'inputs/7298/pricing.py'))['cost']
    crossing = Fraction(r56['crossing_upper'])
    assert crossing == Fraction('0.0036462214364462343366888845568981')
    old = directed(net,crossing)
    assert old[1] < 0
    assert r56['type_b_ports'] == 8 and r56['copies'] == 17
    odd, even = inventory(r56)
    rank_prices = {}
    keys = []
    for o in combinations(sorted(odd),2):
        for e in combinations(sorted(even),2):
            m,n = sorted(len(even[i][1]) for i in e)
            key = f'{m},{n}'
            if key not in rank_prices:
                delta = Counter()
                for length in (m,n):
                    delta.update({9:8,8*length:8,8:-8,8*length+1:-8})
                assert sum(delta.values()) == sum(k*v for k,v in delta.items()) == 0
                changed = net.copy()
                changed.update(delta)
                credit = directed(delta,crossing)
                margin = directed(changed,crossing)
                changed[1] -= 1
                extra = directed(changed,crossing)
                assert credit[0] > 0 and margin[0] > 0 > extra[1]
                rank_prices[key] = {'net_delta':dict(delta),'credit':list(map(str,credit)),
                                    'margin':list(map(str,margin)),
                                    'extra_paid_rank_one_margin':list(map(str,extra))}
            keys.append({'odd':list(o),'even':list(e),'price':key})
    upper = max(Fraction(row['credit'][1]) for row in rank_prices.values())
    assert upper == Fraction(rank_prices['8,8']['credit'][1])
    assert upper == Fraction('72803865248455278947107190998539661213280058633/625000000000000000000000000000000000000000000000')
    assert len(keys) == 1950
    return {'head':HEAD,'caller_head':CALLER_HEAD,'input_sha256':PINS,'crossing_upper':str(crossing),
            'old_margin':list(map(str,old)),'complete_paid':inv['P'],'complete_targets':inv['T'],
            'copies':17,'odd_jobs':odd,'even_jobs':even,'prices':rank_prices,'keys':keys,
            'whole_optimistic_upper':str(upper),'scope':'exactly two simultaneous transfers',
            'limits':{'cases':1950,'primary_seconds':25,'independent_seconds':30,
                      'nonunit_seconds':25,'formal_cases':3,'formal_seconds':45,'binding_seconds':90}}


def check_stock(caller, frozen):
    b = caller['types']['B']
    assert (caller['stages'],b['offset'],b['roles'],len(b['ports'])) == (17,36,36,8)
    odd,even = inventory(frozen)
    got_odd,got_even = {},{}
    for i,e in enumerate(caller['events']):
        if e[:2] == ['B','IDLE_ODD']:
            assert e[4:] == [-1] and len(e[3]) == 1
            got_odd[i] = [e[2]-36,e[3]]
        if e[:2] == ['B','IDLE_ONE'] and len(e[3]) > 1:
            got_even[i] = [e[2]-36,e[3]]
    assert got_odd == odd and got_even == even
    return {clock:v[0] for clock,v in (odd|even).items()}


def dot(a,b,p):
    return sum(x*y for x,y in zip(a,b,strict=True)) % p


def linear(a,b,s,t,p):
    return [(s*x+t*y)%p for x,y in zip(a,b,strict=True)]


def prefixes(caller, site, decoder, body):
    p = decoder['MOD']
    n = 36
    assert p == 65521 and all(p%i for i in range(2,isqrt(p)+1))
    assert len(body) == 17 and all(v%p for v in body)
    clocks, gates = decoder['compile_gates'](caller,p-1,body)
    gate = dict(zip(clocks,gates,strict=True))
    rows = [[int(i==j) for i in range(n)] for j in range(n)]
    cols = [row.copy() for row in rows]
    out = {}
    for clock in sorted(set(gate)|set(site)):
        if clock in site:
            role = site[clock]
            u,v = tuple(cols[role]),tuple(rows[role])
            assert dot(v,u,p) == 1
            out[clock] = (u,v)
        if clock not in gate:
            continue
        _,op,i,j,c = gate[clock]
        if op == 'SWAP':
            rows[i],rows[j] = rows[j],rows[i]
            cols[i],cols[j] = cols[j],cols[i]
        elif op == 'ADD':
            rows[i] = linear(rows[i],rows[j],1,c,p)
            cols[j] = linear(cols[j],cols[i],1,-c,p)
        elif op == 'SCALE':
            inv = pow(c,-1,p)
            rows[i] = [c*x%p for x in rows[i]]
            cols[i] = [inv*x%p for x in cols[i]]
        else:
            assert op == 'J'
            a,b,c,d = c
            inv = pow((a*d-b*c)%p,-1,p)
            x,y = rows[i],rows[j]
            rows[i],rows[j] = linear(x,y,a,b,p),linear(x,y,c,d,p)
            x,y = cols[i],cols[j]
            cols[i],cols[j] = linear(x,y,inv*d,-inv*c,p),linear(x,y,-inv*b,inv*a,p)
    wanted = caller['types']['B']['diagonal']
    for j,diag in enumerate(wanted):
        coefficient = pow(p-1,diag[0]%4,p)
        for power,value in zip(diag[2:],body,strict=True):
            coefficient = coefficient*pow(value,power,p)%p
        assert rows[j] == [int(i==j)*coefficient for i in range(n)]
    assert all(dot(row,col,p) == int(i==j) for i,row in enumerate(rows) for j,col in enumerate(cols))
    assert len(out) == 30
    return out


def defect(left,right,p):
    u,v = left
    x,y = right
    t = 4*dot(v,x,p)
    return tuple((-2*a*b-2*c*d+t*a*d)%p for a,c in zip(u,x,strict=True)
                 for b,d in zip(v,y,strict=True))


def project(line,p):
    divisor = pow(dot(line,line,p),-1,p)
    return line,tuple(x*divisor%p for x in line)


def controls(p):
    a,b,c,d = [project(v,p) for v in [(1,0),(0,1),(3,4),(-4,3)]]
    assert a != b and c != d
    assert defect(d,c,p) == defect(a,b,p)
    assert defect(a,c,p) != defect(a,b,p)
    return ['different_orthogonal_bases_cancel_jointly','one_replaced_reflection_fails']


def support(root, files, frozen, stage, previous=None):
    caller = decode(files['inputs/7113/CALLER.json'])
    site = check_stock(caller,frozen)
    decoder = run_path(str(root/'inputs/r52/screen.py'))
    p = decoder['MOD']
    check = controls(p)
    start = monotonic()
    bodies = [(1,)*17] if stage == 'body-one' else list(decoder['BODIES'])
    matrices = [prefixes(caller,site,decoder,body) for body in bodies]

    @cache
    def pair(i,a,b):
        table = matrices[i]
        return defect(table[a],table[b],p)

    keys = frozen['keys'] if previous is None else previous['survivors']
    rows = []
    for key in keys:
        if monotonic() >= start+22:
            break
        a,b,c,d = sorted(key['odd']+key['even'])
        verdict = None
        for i in range(len(bodies)):
            first, second = pair(i,d,c),pair(i,a,b)
            if first != second:
                k = next(k for k,(x,y) in enumerate(zip(first,second,strict=True)) if x!=y)
                verdict = {'body_index':i,'row':k//36,'column':k%36,'left':first[k],'right':second[k]}
                break
        rows.append({'key':key,'chronological':[a,b,c,d],'mismatch':verdict})
    return {'head':HEAD,'caller_head':CALLER_HEAD,'mode':stage,'prime':p,'controls':check,
            'body_values':bodies,'visited':len(rows),'results':rows,'site_count':len(site),
            'cached_ordered_pairs':pair.cache_info().currsize,
            'unvisited':([] if previous is None else previous['unvisited'])+keys[len(rows):],
            'survivors':[row['key'] for row in rows if row['mismatch'] is None]}


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('stage',choices=['price','body-one','nonunit'])
    parser.add_argument('--price-sha')
    args = parser.parse_args()
    files = authenticated(args.root)
    frozen = price(args.root,files)
    if args.stage == 'price':
        result = frozen
    else:
        raw = (args.root/'PRICE.json').read_bytes()
        assert sha256(raw).hexdigest() == args.price_sha
        assert decode(raw) == decode(dumps(frozen))
        previous = None if args.stage == 'body-one' else decode((args.root/'BODY1.json').read_bytes())
        if previous is not None:
            assert previous['price_sha256'] == args.price_sha and previous['mode'] == 'body-one'
        result = support(args.root,files,frozen,args.stage,previous)
        result['price_sha256'] = args.price_sha
    print(dumps(result,sort_keys=True,indent=2))
