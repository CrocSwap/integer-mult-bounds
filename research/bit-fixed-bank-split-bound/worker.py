"""Census all existing-pivot helper-support banks on the retained BIT word."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
from itertools import chain, combinations
import json
from pathlib import Path
import runpy
import sys
from time import monotonic

ADAPTER = {
    'worker.py': '278e2d1012db8c171c78c526681e3b2764da8f4b681f027a8682268a6efed2ea',
    'frozen/PRICE.json': '6706bb6225d5e41fa74eef932d92802dd48b722a6a9a6e3ea0040edd76e299f4',
    'frozen/INVENTORY.json': '8b9723cb93ce95163cf1aec8a830ba7e06f1a4274e50f5110ce09b8d6aa95472',
}


def authenticate(deps, adapter):
    raw = {}
    for name,digest in ADAPTER.items():
        blob = (adapter/name).read_bytes()
        assert sha256(blob).hexdigest() == digest, name
        raw[name] = blob
    old = runpy.run_path(str(adapter/'worker.py'))
    word,invoice,_ = old['load'](deps)
    return old,word,invoice,json.loads(raw['frozen/INVENTORY.json']),json.loads(raw['frozen/PRICE.json'])


def banks(word, slots, observe, reverse=False):
    """Yield only affected chart banks, including prefix rows and suffix columns."""
    n = word['public']
    program = word['program']
    left = [1<<i for i in range(n)]+[0]*word['owned_fields']
    right = left.copy()
    begin_right = {}
    for t in range(len(program)-1,-1,-1):
        op,d,*args = program[t]
        if op=='ADD':
            s = args[0]
            assert d!=s
            right[s] ^= right[d]
        elif op=='SWAP':
            s = args[0]
            right[s],right[d] = right[d],right[s]
        elif op=='INIT':
            begin_right[t] = right[d]
            right[d] = 0
        elif op=='CLEAR':
            right[d] = 0
    frame = word['start']+[None]*word['owned_fields']
    owner = list(range(n))+[None]*word['owned_fields']
    bank = defaultdict(set)
    for i,f in enumerate(frame[:n]):
        bank[f].add(i)

    def chart(i, f):
        if frame[i] is not None:
            bank[frame[i]].remove(i)
        frame[i] = f
        if f is not None:
            bank[f].add(i)

    for t,(op,d,*args) in enumerate(program):
        before = frame[d]
        changed = {before}
        if op=='ADD':
            s,f = args
            assert frame[d] == frame[s] == f and s!=d
            left[d] ^= left[s]
            right[s] ^= right[d]
        elif op=='SWAP':
            s = args[0]
            f = frame[s]
            changed.add(f)
            if f!=before:
                chart(s,before)
                chart(d,f)
            for array in (owner,left,right):
                array[d],array[s] = array[s],array[d]
        elif op=='MOVE':
            a,f = args
            assert a==before
            changed.add(f)
            chart(d,f)
        elif op=='INIT':
            f = args[0]
            assert owner[d] is None
            owner[d] = n+t
            left[d],right[d] = 0,begin_right[t]
            changed.add(f)
            chart(d,f)
        else:
            assert op=='CLEAR' and owner[d]>=n
            owner[d] = None
            left[d]=right[d]=0
            chart(d,None)
        for f in changed-{None}:
            roles = bank[f] & slots.get(f,set())
            if roles:
                roles = sorted(i for i in roles if owner[i]==i)
                if roles:
                    observe(t,f,roles,sorted(bank[f]),left,right)
    assert frame==word['final']+[None]*word['owned_fields']
    assert right==[1<<i for i in range(n)]+[0]*word['owned_fields']
    expected = right.copy()
    for i in range(111):
        expected[i+111] ^= 1<<i
    assert left==expected


def paired(rows,cols,exterior,kernel,fold):
    a = kernel([r&exterior for r in rows])
    if not a:
        return None
    b = kernel([c&exterior for c in cols])
    if not b:
        return None
    images = [(v,fold(cols,v)) for v in b]
    for u in chain(a,(x^y for x,y in combinations(a,2))):
        c = fold(rows,u)
        signs = {}
        for v,d in images:
            pair = (u&v).bit_count()%2,(c&d).bit_count()%2
            if pair==(1,1):
                return u,v,c,d
            if pair!=(0,0):
                signs[pair]=v,d
        if len(signs)==2:
            v,d = (x^y for x,y in zip(signs[0,1],signs[1,0],strict=True))
            return u,v,c,d
    return None


def main(deps,adapter,out,deadline):
    old,word,invoice,inv,previous = authenticate(deps,adapter)
    math = runpy.run_path(str(deps/'price.py'))
    target = old['TARGET']
    native,visits = old['moves_and_contacts'](word,lambda:None)
    dims = {int(k):r['dim'] for k,r in word['frames'].items()}
    paid = Counter()
    for (a,b),count in native.items():
        paid[abs(dims[b]-dims[a])] += count
    signed,copies = math['profile'](invoice,paid,word,dims)
    base = math['cost'](signed,target)
    assert list(map(str,base))==previous['signed_baseline_interval']
    assert inv['relative_pins']==old['PINS']
    assert inv['paid_histogram']=={str(r):n for r,n in paid.items()}
    slots = defaultdict(set)
    info = {}
    group_masks = defaultdict(int)
    roles_prior = {}
    rank_of = {}

    @cache
    def credit(r,l):
        delta = Counter((l,r-l))
        delta[r] -= 1
        return math['cost'](delta,target)

    for row in inv['helpers']:
        i,r = row['helper'],row['rank']
        group = row['initial_chart'],row['final_chart']
        group_masks[group] |= 1<<i
        rank_of[i]=r
        assert all((t,f) in visits[i] for t,f,_ in row['interior_landings'])
        for _,f,l in row['interior_landings']:
            slots[f].add(i)
            info[i,f]=group,l
            roles_prior[i]=max(roles_prior.get(i,F(0)),credit(r,l)[1])
    assert copies*sum(roles_prior.values())==F(previous['fixed_route_saving_upper'])
    all_public=(1<<word['public'])-1
    counters = Counter()
    best = {}
    coverage = Counter()
    last = [-1]

    def check(t,f,pivots,bank,left,right):
        if monotonic()>=deadline:
            raise TimeoutError
        last[0]=t
        counters['chart_banks']+=1
        groups = defaultdict(list)
        for i in pivots:
            g,l = info[i,f]
            groups[g].append((i,l))
            coverage[i]+=1
        rows = [left[i] for i in bank]
        cols = [right[i] for i in bank]
        for group,members in groups.items():
            counters['group_contexts']+=1
            result = paired(rows,cols,all_public^group_masks[group],old['kernel'],old['fold'])
            if result is None:
                continue
            counters['positive_group_contexts']+=1
            for i,l in members:
                u = credit(rank_of[i],l)[1]
                if i not in best or u>best[i][0]:
                    best[i]=(u,t,f,l,bank,result)

    complete = True
    try:
        banks(word,slots,check)
    except TimeoutError:
        complete=False
    charges = {i:data[0] for i,data in best.items()} if complete else roles_prior
    upper = copies*sum(charges.values(),F(0))
    receipt = {'status':'COMPLETE' if complete else 'TIME_CAP_UNRESOLVED',
               'adapter_relative_pins':ADAPTER,'dependency_relative_pins':old['PINS'],
               'whole_signed_baseline':list(map(str,base)),'whole_stock_saving_upper':str(upper),
               'whole_target_margin_upper':str(base[1]+upper),'target':str(target),'copies':copies,
               'covered_pivots':len(coverage),'positive_pivots':len(best),'stats':dict(counters),
               'pivot_event_counts':dict(coverage),'positive_pivot_credits':{i:str(x[0]) for i,x in best.items()},
               'unresolved_pivots':[] if complete else sorted(roles_prior),
               'last_tested_clock':last[0]}
    old['save'](out,'PRICE.json',receipt)
    if complete and base[1]+upper>=0 and best:
        i,(_,t,f,l,bank,result) = min(best.items(),key=lambda x:(-x[1][0],x[1][1],x[0]))
        old['save'](out,'SUPPORT.json',{'pivot':i,'clock':t,'chart':f,'bank':bank,
                    'rank_parts':[l,rank_of[i]-l], 'pairing_masks':list(map(hex,result))})
    old['save'](out,'DONE.json',{'status':receipt['status']})


if __name__=='__main__':
    assert __debug__
    main(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]),float(sys.argv[4]))
