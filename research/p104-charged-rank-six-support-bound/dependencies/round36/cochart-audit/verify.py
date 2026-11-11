"""Independent rational audit of the 128 cocharted #7277 nominations."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
from itertools import groupby
import json
from pathlib import Path

PINS = {
    'complex/source/inputs/WORD.json.gz': '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756',
    'complex/source/inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'complex/source/inputs/EARLY-RESULT.json': '691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7',
}


def load(path):
    def unique(items):
        result = dict(items)
        assert len(result) == len(items)
        return result
    raw = path.read_bytes()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    return json.loads(raw, object_pairs_hook=unique)


def put(row, k, x):
    x += row.get(k,0)
    if x:
        row[k] = x
    else:
        row.pop(k,None)


def add(dst, src, a):
    for k,x in src.items():
        put(dst,k,a*x)


def linear(rows, op, d, s, q, reverse=False):
    if op in ('INIT','CLEAR'):
        rows[d] = {}
    elif op == 'SCALE':
        rows[d] = {k:q*x for k,x in rows[d].items()}
    elif op in ('ADD','COPY'):
        if reverse:
            add(rows[s], dict(rows[d]) if s==d else rows[d], q)
            if op=='COPY':
                assert s != d
                rows[d] = {}
        elif op == 'COPY':
            rows[d] = {k:q*x for k,x in rows[s].items()}
        else:
            add(rows[d], dict(rows[s]) if s==d else rows[s], q)


def pure_images(rows, current, group):
    # Coefficient-elimination order is independent of the lead checker.
    # Carry the complete image vector and eliminate greatest exterior
    # coordinate first, leaving an image basis spanning the pure image.
    exterior, interior = {}, {}
    for role in sorted(current, reverse=True):
        residual = rows[role].copy()
        while (lead := max((k for k in residual if k not in group), default=-1)) >= 0:
            if lead not in exterior:
                exterior[lead] = residual
                break
            old = exterior[lead]
            add(residual, old, -residual[lead]/old[lead])
        else:
            while residual:
                lead = max(residual)
                if lead not in interior:
                    interior[lead] = residual
                    break
                old = interior[lead]
                add(residual, old, -residual[lead]/old[lead])
    return tuple(interior.values())


def binary_span(rows):
    space = {0}
    for row in rows:
        assert row not in space
        space |= {row^x for x in space}
    return space


def geometry(word):
    public = word['public']
    main = set(word['live']) | {r+112 for r in word['live']}
    for hosted in ('X2','Y2'):
        main.update(word['hosted'][hosted])
    assert len(main)==400 and public==1501
    starts, ends = word['initial'], word['final']
    spaces = list(map(binary_span,word['frames']))
    ranks = list(map(len,word['frames']))
    groups = defaultdict(set)
    helpers = {}
    for role,(a,b) in enumerate(zip(starts,ends,strict=True)):
        if role not in main:
            assert spaces[a] < spaces[b]
            groups[a,b].add(role)
            helpers[role] = (a,b)
    chart = starts + [None]*word['owned_fields']
    at = defaultdict(set)
    for role,frame in enumerate(starts):
        at[frame].add(role)
    tape, cuts, contexts = [], defaultdict(list), {}
    paid = Counter()
    for t,(op,d,*args) in enumerate(word['program']):
        s,q = d,None
        if op == 'MOVE':
            a,b,owned = args
            assert chart[d]==a and owned==(d>=public)
            assert spaces[a]<spaces[b] or owned and spaces[b]<spaces[a]
            at[a].remove(d)
            at[b].add(d)
            chart[d] = b
            paid[abs(ranks[b]-ranks[a])] += 1
            changed = (a,b)
        elif op in ('INIT','CLEAR'):
            f = args[-1]
            if op=='INIT':
                assert chart[d] is None
                at[f].add(d)
                chart[d] = f
            else:
                assert chart[d]==f
                at[f].remove(d)
                chart[d] = None
            changed = (f,)
        else:
            f = args[-1]
            s = args[0] if op in ('ADD','COPY') else d
            q = Q(args[-2])
            assert chart[d]==chart[s]==f
            changed = (f,)
        tape.append((op,d,s,q))
        for f in changed:
            if f is None:
                continue
            tracked = sorted(at[f] & helpers.keys())
            if not tracked:
                continue
            distinct = {helpers[r] for r in tracked}
            for a,b in distinct:
                if spaces[a] < spaces[f] < spaces[b]:
                    cuts[a,b,f].append(t)
                    contexts[t,f] = tuple(at[f])
    assert chart==ends+[None]*word['owned_fields']
    return ranks,helpers,groups,tape,cuts,contexts,paid


@cache
def log_unit(value):
    z = (value-1)/(value+1)
    term,total = z,Q(0)
    for n in range(1,160,2):
        total += term/n
        term *= z*z
    return 2*total,2*(total+term/(161*(1-z*z)))


@cache
def power(r,k):
    exponent = r.bit_length()-1
    unit = log_unit(Q(r,1<<exponent))
    two = log_unit(Q(2))
    bound = [k*(u+exponent*t) for u,t in zip(unit,two,strict=True)]
    grid = 10**70
    lo,hi = Q((bound[0]*grid).__floor__(),grid),Q((bound[1]*grid).__ceil__(),grid)
    def e(x,n):
        term,total = Q(1),Q(1)
        for j in range(1,n+1):
            term *= -x/j
            total += term
        return total
    return r*e(hi,49),r*e(lo,50)


def price(ranks, helpers, paid, caller, early, cuts, inventory):
    copies = sum(event[0]=='J' for event in caller['events'])
    assert copies==17 and sum(paid.values())==6280
    p = Counter({r:n*copies for r,n in paid.items()})
    t = Counter()
    for a,b in helpers.values():
        t[ranks[b]-ranks[a]] += copies
    for item in caller['types'].values():
        for sign,offset,*bits in item['diagonal']:
            assert sign==-1 and offset==0 and len(bits)==copies
            t[1+8*sum(bits)] += len(item['ports'])
    for item,op,*args in (e for e in caller['events'] if e[0]!='J'):
        n = len(caller['types'][item]['ports'])
        if op=='QUERY':
            p[1] += n
        elif op in ('IDLE_ONE','IDLE_ODD'):
            p[8*len(args[1])+int(op=='IDLE_ODD')] += n
    assert p==Counter({int(r):v for r,v in early['invoice']['P'].items()})
    assert t==Counter({int(r):v for r,v in early['invoice']['T'].items()})
    k = Q(early['price']['independent_raw_bracket'][1])
    assert k == Q(inventory['crossing_upper'])
    tariffs = {r:power(r,k) for r in p.keys()|t.keys()|set(range(1,10))}
    def interval(hist):
        terms = [sorted(n*x for x in tariffs[r]) for r,n in hist.items() if n]
        return sum(x[0] for x in terms),sum(x[1] for x in terms)
    signed = t.copy()
    signed.subtract(p)
    lo,hi = interval(signed)
    base = list(map(Q,inventory['baseline']))
    assert base[0]<=lo<=hi<=base[1]<0
    ranked = []
    for a,b,f in cuts:
        x,y = ranks[f]-ranks[a],ranks[b]-ranks[f]
        profile = Counter([x,y])
        profile[x+y] -= 1
        gain = tuple(copies*v for v in interval(profile))
        ranked.append(((a,b,f),tuple(sorted((x,y))),gain))
    ranked.sort(key=lambda row:(-row[2][1],row[0]))
    assert len(ranked)==inventory['scope']==len(inventory['rows'])
    for (key,_,gain),old in zip(ranked,inventory['rows'],strict=True):
        oldlo,oldhi = map(Q,old['gain'])
        assert list(key)==old['key'] and old['cuts']==len(cuts[key])
        assert 0<oldlo<=gain[0]<=gain[1]<=oldhi<1
        assert Q(old['complete_upper'])==base[1]+oldhi
    by_price = [next(group)[2] for _,group in groupby(ranked,key=lambda row:row[1])]
    assert all(a[0]>b[1] for a,b in zip(by_price,by_price[1:]))
    assert all(lo+gain[0]>0 for _,_,gain in ranked[:128])
    return [key for key,_,_ in ranked[:128]],sum(p.values()),sum(t.values())


def test_cut():
    assert pure_images([{0:Q(1),2:Q(1)},{1:Q(1),2:Q(1)}],(0,1),{0,1}) == ({0:Q(1),1:Q(-1)},)
    assert pure_images([{2:Q(1)},{2:Q(1)}],(0,1),{0,1}) == ()
    assert pure_images([{0:Q(1)},{1:Q(1)}],(0,1),{0,1})


def run(root, receipts):
    paths = {str(root/p):h for p,h in PINS.items()}
    assert all(sha256(Path(p).read_bytes()).hexdigest()==h for p,h in paths.items())
    word,caller,early = (load(root/p) for p in PINS)
    inventory,search = (load(receipts/name) for name in ('INVENTORY.json','SEARCH.json'))
    assert search['candidate'] is None and search['phase']=='exhausted_nominations'
    ranks,helpers,groups,tape,cuts,contexts,native = geometry(word)
    keys,paid,productive = price(ranks,helpers,native,caller,early,cuts,inventory)
    selected = {tuple(row['key']):row for row in search['selected']}
    assert list(selected)==keys
    test_cut()
    schedule = defaultdict(list)
    counts = defaultdict(Counter)
    for key in keys:
        for t in cuts[key]:
            schedule[t].append(key)
    n = word['public']
    def basis():
        return [{i:Q(1)} for i in range(n)]+[{} for _ in range(word['owned_fields'])]
    forward = basis()
    surviving = defaultdict(list)
    for t,(op,d,s,q) in enumerate(tape):
        linear(forward,op,d,s,q)
        for a,b,f in schedule.get(t,()):
            k = (a,b,f)
            image = pure_images(forward,contexts[t,f],groups[a,b])
            counts[k]['prefix_checked'] += 1
            if image:
                counts[k]['prefix_nonzero'] += 1
                surviving[t].append((k,image))
    assert all(forward[r]=={r:Q(1)} for r in helpers)
    backward = basis()
    for t in reversed(range(len(tape))):
        for (a,b,f),prefix in surviving.get(t,()):
            k = (a,b,f)
            suffix = pure_images(backward,contexts[t,f],groups[a,b])
            counts[k]['suffix_checked'] += 1
            for c in prefix:
                for d in suffix:
                    assert not sum(v*d.get(i,0) for i,v in c.items()), (t,k,c,d)
        linear(backward,*tape[t],reverse=True)
    for key,count in counts.items():
        assert all(value==selected[key].get(name,0) for name,value in count.items())
        assert selected[key]['cuts']==count['prefix_checked']
    assert len(counts)==128 and len(cuts)-128==search['outside_signature_cap']
    totals = sum(counts.values(),Counter())
    return {'status':'PASS_INDEPENDENT_RATIONAL_COCHART_AUDIT',
            'head':inventory['head'],'pins':PINS | {f'incremental/run/{name}':sha256((receipts/name).read_bytes()).hexdigest() for name in ('INVENTORY.json','SEARCH.json')},
            'paid':paid,'productive':productive,'scope':len(cuts),'selected':len(counts),
            'outside_cap':len(cuts)-len(counts),'totals':dict(totals),'nonzero_pairs':0,
            'controls':['MIXED_OUTSIDE_CANCELLATION','ZERO_IMAGE_NOT_CREDITED','PURE_BASIS_POSITIVE']}


if __name__=='__main__':
    assert __debug__
    parser = ArgumentParser()
    parser.add_argument('dependency_root',type=Path)
    parser.add_argument('receipt_directory',type=Path)
    a = parser.parse_args()
    print(json.dumps(run(a.dependency_root,a.receipt_directory),sort_keys=True,indent=2))
