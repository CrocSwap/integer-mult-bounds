"""Independent every-contact sweep and distinct pending-owner price audit."""
from collections import Counter,defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
import json
from pathlib import Path
import sys

PINS={
    'public/native/WORD.json.gz':'c1caec11ca3ee264ef03018dd91037eac10c3e28950c4c525ee1b4bf5ee210e2',
    'public/native/RESULT.json':'59080d75e7281b1a8c1353930917fd15869ad747ff4200948898f78f11c14089',
    'round11/frontier/independent_adapter_price.py':'2a46157d156bdfc0e892289005fd3fb7c23708de48c9abd90c1914b0372bc726',
    'round18/complex/STOCK.json':'9198aaa1e8f10ac0616f3810de013fc0cd86b72b7eb7dd23e7dc298c646baa74',
}


def checked(path,key):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=PINS[key]:
        raise ValueError(f'SHA-256 mismatch: {key}')
    return raw


def independent_sweep(word,charts,reverse):
    events=word['program']
    p=word['public']
    at=[*word['final' if reverse else 'initial'],*([None]*word['owned_fields'])]
    states=[{i:Fraction(1)} for i in range(p)]+[{} for _ in range(word['owned_fields'])]
    columns=defaultdict(list)
    coeff={e[2 if e[0]=='SCALE' else 3]:Fraction(e[2 if e[0]=='SCALE' else 3])
           for e in events if e[0] in ('ADD','COPY','SCALE')}

    def record(j):
        if at[j] in charts and states[j]:
            columns[at[j]].append(states[j])

    def combine(dest,src,q):
        x=states[dest]
        y=states[src]
        support=x.keys()|y.keys()
        states[dest]={i:v for i in support if (v:=x.get(i,0)+q*y.get(i,0))}

    for j in range(p):
        record(j)
    for k in (range(len(events)-1,-1,-1) if reverse else range(len(events))):
        op,j,*a=events[k]
        touched=(j,a[0]) if op in ('ADD','COPY') else (j,)
        for t in touched:
            record(t)
        if op=='MOVE':
            before,after=a[:2]
            old,new=(after,before) if reverse else (before,after)
            assert at[j]==old
            at[j]=new
        elif op=='ADD':
            s=a[0]
            assert at[s]==at[j]==a[-1]
            combine(s,j,coeff[a[1]]) if reverse else combine(j,s,coeff[a[1]])
        elif op=='COPY':
            s=a[0]
            assert at[s]==at[j]==a[-1]
            if reverse:
                combine(s,j,coeff[a[1]])
                states[j]={p+k:Fraction(1)}
            else:
                states[j]={i:coeff[a[1]]*v for i,v in states[s].items()}
        elif op=='SCALE':
            assert at[j]==a[-1]
            states[j]={i:coeff[a[0]]*v for i,v in states[j].items()}
        else:
            assert op in ('INIT','CLEAR')
            chart=a[0]
            entering=(op=='CLEAR') if reverse else (op=='INIT')
            assert at[j] == (None if entering else chart)
            at[j]=chart if entering else None
            states[j]={}
        for t in touched:
            record(t)
    assert at==[*word['initial' if reverse else 'final'],*([None]*word['owned_fields'])]
    return columns


def insertion(row,basis,indices):
    x=row.copy()
    while selected := (x.keys()&indices if indices is not None else x.keys()):
        pivot=max(selected)
        if pivot not in basis:
            a=x[pivot]
            basis[pivot]={j:v/a for j,v in x.items()}
            return True
        right=basis[pivot]
        a=x[pivot]
        x={j:v for j in x.keys()|right.keys() if (v:=x.get(j,0)-a*right.get(j,0))}
    return x


def outside_image(rows,group):
    outside_coords=set().union(*(row.keys() for row in rows))-group
    outside={}
    inside={}
    for row in rows:
        x=insertion(row,outside,outside_coords)
        if isinstance(x,dict):
            insertion(x,inside,None)
    return inside,len(outside)


def run(data,report,price_path):
    w=json.loads(gzip.decompress(checked(data/'native/WORD.json.gz','public/native/WORD.json.gz')))
    native=json.loads(checked(data/'native/RESULT.json','public/native/RESULT.json'))
    r=json.loads(checked(report,'round18/complex/STOCK.json'))
    checked(price_path,'round11/frontier/independent_adapter_price.py')
    spec=spec_from_file_location('independent_power',price_path)
    price=module_from_spec(spec)
    spec.loader.exec_module(price)
    assert price.TARGET==Fraction(r['target'])
    main={*w['live'],*(j+112 for j in w['live']),*w['hosted']['X2'],*w['hosted']['Y2']}
    helpers={j:(a,b) for j,(a,b) in enumerate(zip(w['initial'],w['final'],strict=True)) if j not in main}
    group={j for j,pair in helpers.items() if pair==(3,127)}
    assert len(group)==616
    dims=list(map(len,w['frames']))
    paths=defaultdict(list)
    for op,j,*a in w['program']:
        if op=='MOVE' and j in helpers:
            paths[j].append(a[1])
    chart_owners=defaultdict(list)
    for j in sorted(group):
        old=paths[j][:-1]
        assert len(set(old))==len(old)
        assert sorted(old)==r['owner_paths'][str(j)]
        for f in old:
            chart_owners[f].append(j)
    assert {str(k):v for k,v in chart_owners.items()}==r['chart_owners']
    chart_shapes={f:min(dims[f],10-dims[f]) for f in chart_owners}
    assert {str(k):v for k,v in chart_shapes.items()}==r['chart_shapes']
    tested={x['chart']:x for x in r['tested']}
    assert all(x['pair_rank']==x['owner_capacity']==0 for x in tested.values())
    assert set(tested)|set(r['pending'])|set(r['zero_price_charts'])==set(chart_owners)
    assert len(tested)+len(r['pending'])+len(r['zero_price_charts'])==len(chart_owners)
    assert [row['chart'] for row in r['tested']]+r['pending']==r['order']
    sides={}
    touch_counts={}
    for side,reverse in (('prefix',False),('suffix',True)):
        snapshots=independent_sweep(w,tested,reverse)
        touch_counts[side]=sum(map(len,snapshots.values()))
        side_bases={}
        for f,record in tested.items():
            basis,rank=outside_image(snapshots[f],group)
            assert rank==record[f'{side}_outside_rank']
            serialized=record[f'{side}_group']
            assert len(basis)==len(serialized)
            for row in serialized:
                value={int(j):Fraction(x) for j,x in row.items()}
                assert insertion(value,basis,None)=={}
            side_bases[f]=basis
        sides[side]=side_bases
    for f in tested:
        for u in sides['prefix'][f].values():
            for v in sides['suffix'][f].values():
                assert not sum(x*v.get(i,0) for i,x in u.items())

    pending=set(r['pending'])
    best={j:max((chart_shapes[f] for f in paths[j] if f in pending),default=1) for j in group}
    layer={k:sum(s>=k for s in best.values()) for k in range(2,6)}
    assert {str(k):v for k,v in layer.items()}==r['final']['layer_counts']

    def dot(h):
        lo=hi=Fraction()
        for d,n in h.items():
            a,b=price.price(d)
            lo+=n*(a if n>=0 else b)
            hi+=n*(b if n>=0 else a)
        return lo,hi

    def gain(r,d,funded):
        h=Counter((d,r+funded-d))
        h[r]-=1
        h[1]-=funded
        return tuple(17*x for x in dot(h))

    def plus(a,b):
        return tuple(a[i]+b[i] for i in (0,1))

    h=Counter({int(k):n for k,n in native['price']['after']['T'].items()})
    h.subtract({int(k):n for k,n in native['price']['after']['P'].items()})
    assert sum(native['price']['after']['T'].values())==22427
    assert sum(native['price']['after']['P'].values())==110519
    old=dot(h)
    funded=old
    free=old
    free_smaller=(Fraction(),Fraction())
    free_shapes=Counter()
    for j,(a,b) in helpers.items():
        opts=[(Fraction(),Fraction())]
        rank=dims[b]-dims[a]
        if j in group:
            if best[j]>1:
                funded=plus(funded,gain(9,best[j],1))
            # Rank-one charts had zero funded value and remain pending for
            # the separate strictly better unfunded ledger.
            allowed=(f for f in paths[j][:-1] if f not in tested)
            d=max((min(dims[f],9-dims[f]) for f in allowed),default=0)
            if d:
                free=plus(free,gain(9,d,0))
                free_shapes[d]+=1
        else:
            d={dims[f]-dims[a] for f in paths[j][:-1]}
            ideal_funded=opts+[gain(rank,x,1) for x in d]
            ideal_free=opts+[gain(rank,x,0) for x in d]
            funded=plus(funded,tuple(max(x[i] for x in ideal_funded) for i in (0,1)))
            contribution=tuple(max(x[i] for x in ideal_free) for i in (0,1))
            free=plus(free,contribution)
            free_smaller=plus(free_smaller,contribution)
    assert funded[0]<=funded[1]<=Fraction(r['final']['margin_upper'])<0
    assert free[0]>0
    threshold=None
    count=0
    partial=plus(old,free_smaller)
    for d in sorted(free_shapes,reverse=True):
        for _ in range(free_shapes[d]):
            before=partial
            partial=plus(partial,gain(9,d,0))
            count+=1
            if partial[0]>0 and threshold is None:
                assert before[1]<0
                threshold=dict(minimum_rank9_owners=count,preceding_upper=price.encode(before)[1],
                               first_lower=price.encode(partial)[0],last_shape=[d,9-d])
    assert threshold is not None and partial==free
    return dict(status='PASS_INDEPENDENT_EVERY_CONTACT_SWEEP_AND_OWNER_PRICE',pins=PINS,
                charts_verified=len(tested),touch_generators_audited=touch_counts,
                owner_layer_counts=layer,raw_funded_margin=price.encode(funded),
                separate_unfunded_pending_stock_margin=price.encode(free),
                separate_unfunded_pending_best_shape_stock=free_shapes,
                separate_unfunded_smaller_actual_ideal_gain=price.encode(free_smaller),
                separate_unfunded_minimum_rank9_owner_threshold=threshold,
                separate_unfunded_is_only_geometric_and_support_overgrant=True)


if __name__=='__main__':
    assert __debug__
    print(json.dumps(run(*map(Path,sys.argv[1:])),indent=2,sort_keys=True))
