"""Independently reconstruct terminal inventory backward and the singleton obstruction."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
from signal import alarm

HERE = Path(__file__).resolve().parent


def reverse(word):
    n = word['public']
    program = word['program']
    order = list(range(n+word['owned_fields']))
    for op,d,*args in program:
        if op == 'SWAP':
            s = args[0]
            order[d],order[s] = order[s],order[d]
    assert set(order[:n]) == set(range(n))
    owner = order[:n]+[None]*word['owned_fields']
    chart = word['final']+[None]*word['owned_fields']
    landings = defaultdict(list)
    moves = Counter()

    def landing(i,t):
        if 222<=i<n and owner[i]==i:
            landings[i].append((t,chart[i]))

    for t in reversed(range(len(program))):
        op,d,*args = program[t]
        if op == 'SWAP':
            s = args[0]
            landing(d,t)
            landing(s,t)
            owner[d],owner[s] = owner[s],owner[d]
            chart[d],chart[s] = chart[s],chart[d]
        elif op == 'MOVE':
            a,b = args
            assert chart[d] == b and owner[d] is not None
            landing(d,t)
            moves[a,b] += 1
            chart[d] = a
        elif op == 'CLEAR':
            assert owner[d] is chart[d] is None and d>=n
            owner[d],chart[d] = n+t,args[0]
        elif op == 'INIT':
            assert owner[d]>=n and chart[d]==args[0]
            owner[d] = chart[d] = None
        else:
            assert op=='ADD' and chart[d]==chart[args[0]]==args[1]
    assert owner == list(range(n))+[None]*word['owned_fields']
    assert chart == word['start']+[None]*word['owned_fields']
    return moves, landings


def rank(rows):
    pivots = {}
    for raw in rows:
        row = list(raw)
        for col in range(len(row)):
            if not row[col]:
                continue
            if col not in pivots:
                pivots[col] = [x/row[col] for x in row]
                break
            p = row[col]
            row = [x-p*y for x,y in zip(row,pivots[col],strict=True)]
    return len(pivots)


def support_column(rows, pivot, adjoint):
    x = 1<<pivot
    for op,d,*args in rows:
        if op == 'ADD':
            s = args[0]
            if adjoint:
                s,d = d,s
            if x>>s&1:
                x ^= 1<<d
        elif op == 'SWAP':
            s = args[0]
            if ((x>>d)^(x>>s))&1:
                x ^= (1<<d)|(1<<s)
        elif op in ('INIT','CLEAR'):
            x &= ~(1<<d)
    return x


def verify(root, receipt):
    main = runpy.run_path(str(HERE/'worker.py'))
    raw = {}
    for p,h in main['PINS'].items():
        data = (root/p).read_bytes()
        assert sha256(data).hexdigest() == h
        raw[p] = data
    word = json.loads(gzip.decompress(raw['inputs/WORD.json.gz']))
    invoice = json.loads(raw['inputs/INVOICE.json'])
    price = runpy.run_path(str(root/'price.py'))
    audit = runpy.run_path(str(root/'audit.py'))
    _,edges,paid = audit['incidence'](word)
    assert len(edges)==62474
    moves,landings = reverse(word)
    assert Counter(paid)==moves
    dims = {int(f):row['dim'] for f,row in word['frames'].items()}
    bases = {int(f):[tuple(map(F,b)) for b in row['B']] for f,row in word['frames'].items()}
    assert all(rank(rows)==dims[f] for f,rows in bases.items())

    @cache
    def contained(lo,hi):
        return rank(bases[hi]+bases[lo])==dims[hi]

    native = Counter()
    for a,b in moves:
        lo,hi = sorted((a,b),key=dims.__getitem__)
        assert contained(lo,hi) and dims[lo]<dims[hi]
        native[dims[hi]-dims[lo]] += moves[a,b]
    signed,copies = price['profile'](invoice,native,word,dims)
    target = F(10018846261809,2500000000000000)
    baseline = price['cost'](signed,target)
    inv = json.loads((receipt/'INVENTORY.json').read_bytes())
    bound = json.loads((receipt/'PRICE.json').read_bytes())
    assert inv['relative_pins']==main['PINS']
    assert inv['copies']==bound['copies']==copies==36
    assert inv['paid_histogram']=={str(r):n for r,n in native.items()}
    assert inv['paid_moves']==sum(native.values())==2871
    assert bound['signed_baseline_interval']==list(map(str,baseline))
    assert F(bound['shortfall'])==-baseline[1]
    assert len(inv['helpers'])==word['public']-222==bound['total_native_helpers']

    @cache
    def credit(r,k):
        lo = price['power_bounds'](r,target)[0]
        return price['power_bounds'](k,target)[1]+price['power_bounds'](r-k,target)[1]-lo

    broad = fixed = F(0)
    ranked = []
    roles = set()
    count = 0
    rank_hist = Counter()
    for row in inv['helpers']:
        i = row['helper']
        assert i not in roles
        roles.add(i)
        lo,hi = word['start'][i],word['final'][i]
        r = dims[hi]-dims[lo]
        assert row['rank']==r and row['initial_chart']==lo and row['final_chart']==hi
        rank_hist[r] += 1
        best = max(credit(r,k) for k in range(1,r))
        broad += best
        assert row['observed_chart_landings']==len(landings[i])
        hits = sorted([t,f,dims[f]-dims[lo]] for t,f in landings[i]
                      if dims[lo]<dims[f]<dims[hi] and contained(lo,f) and contained(f,hi))
        assert hits==row['interior_landings']
        if hits:
            count += len(hits)
            k,t,f,left = min((-credit(r,left),t,f,left) for t,f,left in hits)
            ranked.append((k,t,i,f,left,r))
            fixed -= k
    assert roles == set(range(222,word['public']))
    assert rank_hist==Counter({int(r):n for r,n in bound['native_helper_histogram'].items()})
    assert len(ranked)==bound['fixed_route_pivots'] and count==bound['eligible_landings']
    assert F(bound['broad_saving_upper'])==copies*broad
    assert F(bound['fixed_route_saving_upper'])==copies*fixed
    assert F(bound['fixed_route_complete_margin_upper'])==baseline[1]+copies*fixed
    assert F(bound['broad_complete_margin_upper'])==baseline[1]+copies*broad
    assert str(target)==bound['target'] and baseline[1]+copies*fixed>0

    chosen = json.loads((receipt/'SUPPORT.json').read_bytes())
    _,t,pivot,frame,left,r = min(ranked)
    assert (chosen['clock'],chosen['pivot'],chosen['cut_chart'],chosen['split_ranks'])==(t,pivot,frame,[left,r-left])
    chart = word['start']+[None]*word['owned_fields']
    program = word['program']
    for op,d,*args in program[:t+1]:
        if op == 'SWAP':
            s = args[0]
            chart[d],chart[s] = chart[s],chart[d]
        elif op in ('MOVE','INIT'):
            chart[d] = args[-1]
        elif op == 'CLEAR':
            chart[d] = None
    assert [i for i,f in enumerate(chart) if f==frame] == chosen['bank'] == [pivot]
    group = [i for i in range(222,word['public']) if (word['start'][i],word['final'][i]) ==
             (word['start'][pivot],word['final'][pivot])]
    assert group == chosen['boundary_group']
    other = ((1<<word['public'])-1)^sum(1<<i for i in group)
    left = support_column(reversed(program[:t+1]),pivot,True)&other
    right = support_column(program[t+1:],pivot,False)&other
    assert left and right and chosen['left_dimension']==chosen['right_dimension']==0
    assert chosen['witness'] is None and not chosen['left_cases']

    malformed = native.copy()
    malformed[1] -= 1
    try:
        price['profile'](invoice,malformed,word,dims)
    except AssertionError:
        rejected_move = True
    else:
        raise AssertionError('omitted paid MOVE passed')
    return {'status':'PASS_INDEPENDENT_TERMINAL_STOCK_AND_SINGLETON_SUPPORT',
            'paid_lineage_edges':len(edges),'rejected_omitted_paid_move':rejected_move,
            'left_contaminating_boundary_columns':[i for i in range(word['public']) if left>>i&1],
            'right_contaminating_boundary_outputs':[i for i in range(word['public']) if right>>i&1],
            'fixed_route_support_unresolved_landings':count-1,
            'fixed_route_support_unresolved_pivots':len(ranked)-int(sum(x['helper']==pivot and len(x['interior_landings'])==1 for x in inv['helpers']))}


if __name__=='__main__':
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument('dependency_root',type=Path)
    p.add_argument('receipt',type=Path)
    a = p.parse_args()
    alarm(60)
    print(json.dumps(verify(a.dependency_root,a.receipt),sort_keys=True,indent=2))
    alarm(0)
