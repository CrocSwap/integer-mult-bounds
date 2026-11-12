"""Exact all-clock chart capacity and deduplicated funded stock upper."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import argparse
import json
from pathlib import Path
from time import monotonic

PINS={
    'round13/alternative/reprice.py':'97f4524d11a08cd3a09ceb9abc6b90f45ca579ac1c529a176b80a67201ecd90a',
    'round17/complex/GLOBAL.json':'96307d0eafdd6fadc265e5f9772cb15f74a213629adb15cc01a335accf253477',
    'round17/complex/PROTOTYPE.json':'df449c543342a8dc2d8ff53bd4861c4d1b4a34d4f75d4cc9afa32b51292d0963',
}


class TimeCap(Exception):
    pass


def read(campaign,key):
    path=campaign/key.replace('round','kappa-moonshot-round',1)
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=PINS[key]:
        raise ValueError(f'SHA-256 mismatch: {key}')
    return path,raw


def load(campaign,key):
    p,_=read(campaign,key)
    spec=spec_from_file_location(p.stem,p)
    m=module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def add(a,b,c):
    r=a.copy()
    for j,v in b.items():
        x=r.get(j,0)+c*v
        if x:
            r[j]=x
        else:
            r.pop(j,None)
    return r


def scaled(row,c):
    return row if c==1 else {j:c*v for j,v in row.items()}


def scan(word,charts,check_time,reverse=False):
    """Keep span generators at chart boundary entries and adjoint COPY guards."""
    public=word['public']
    total=public+word['owned_fields']
    rows=[{i:Fraction(1)} for i in range(public)]+[{} for _ in range(total-public)]
    groups=defaultdict(list)
    start=word['final' if reverse else 'initial']
    for i,chart in enumerate(start):
        if chart in charts:
            groups[chart].append((('endpoint',i),rows[i]))
    tape=list(enumerate(word['program']))
    for count,(i,(op,j,*a)) in enumerate(reversed(tape) if reverse else tape):
        if count%256==0:
            check_time()
        if op=='MOVE':
            chart=a[0 if reverse else 1]
            if chart in charts and rows[j]:
                groups[chart].append(((i,j),rows[j]))
        elif op=='SCALE':
            rows[j]=scaled(rows[j],Fraction(a[0]))
        elif op=='ADD':
            k=a[0]
            dest,src=(k,j) if reverse else (j,k)
            if rows[src]:
                rows[dest]=add(rows[dest],rows[src],Fraction(a[1]))
        elif op=='COPY':
            k=a[0]
            if reverse:
                if rows[j]:
                    rows[k]=add(rows[k],rows[j],Fraction(a[1]))
                rows[j]={public+i:Fraction(1)}
                if a[-1] in charts:
                    groups[a[-1]].append(((i,j),rows[j]))
            else:
                rows[j]=scaled(rows[k],Fraction(a[1]))
        elif op in ('INIT','CLEAR'):
            rows[j]={}
        else:
            raise ValueError(op)
    assert all(not row for row in rows[public:])
    return groups


def reduce_row(row,basis,indices):
    r=row
    while True:
        pivot=min((j for j in r if indices(j)),default=None)
        if pivot is None:
            return r,None
        if pivot not in basis:
            return r,pivot
        r=add(r,basis[pivot],-r[pivot])


def intersection(observations,allowed,check_time):
    outside={}
    inside={}
    for label,row in observations:
        check_time()
        v,pivot=reduce_row(row,outside,lambda j:j not in allowed)
        if pivot is not None:
            outside[pivot]=scaled(v,1/v[pivot])
        else:
            v,pivot=reduce_row(v,inside,lambda j:True)
            if pivot is not None:
                inside[pivot]=scaled(v,1/v[pivot])
    return list(inside.values()),len(outside)


def rank_pair(left,right):
    basis={}
    for u in left:
        row={}
        for i,v in enumerate(right):
            z=sum(x*v.get(j,0) for j,x in u.items())
            if z:
                row[i]=z
        reduced,pivot=reduce_row(row,basis,lambda j:True)
        if pivot is not None:
            basis[pivot]=scaled(reduced,1/reduced[pivot])
    return len(basis)


def encode(rows):
    return [{str(k):str(v) for k,v in sorted(row.items())} for row in rows]


def layer_count(owners,capacity,shapes,minimum):
    """Maximum cardinality owner/chart b-matching for one price layer."""
    edges=defaultdict(list)
    for chart,roles in owners.items():
        if capacity[chart]>0 and shapes[chart]>=minimum:
            for role in roles:
                edges[role].append(chart)
    occupants=defaultdict(list)

    def augment(role,seen):
        for chart in edges[role]:
            if chart in seen:
                continue
            seen.add(chart)
            bucket=occupants[chart]
            if len(bucket)<capacity[chart]:
                bucket.append(role)
                return True
            for index,previous in enumerate(bucket):
                if augment(previous,seen):
                    bucket[index]=role
                    return True
        return False

    result=sum(augment(role,set()) for role in sorted(edges,key=lambda r:(len(edges[r]),r)))
    occupied=[role for b in occupants.values() for role in b]
    assert len(occupied)==len(set(occupied))==result
    assert all(len(b)<=capacity[f] for f,b in occupants.items())
    return result


def bounds(owners,capacity,shapes,tariffs,baseline,smaller):
    levels={k:layer_count(owners,capacity,shapes,k) for k in (2,3,4,5)}
    gain=sum((tariffs[k]-tariffs[k-1])*levels[k] for k in levels)
    return dict(layer_counts=levels,saving_rank9_upper=str(gain),margin_upper=str(baseline+smaller+gain))


def controls():
    # A coframed jointly dual stock need not survive an outside restriction.
    left=[(('toy',0),{0:Fraction(1),3:Fraction(1)}),
          (('toy',1),{1:Fraction(1),3:Fraction(1)})]
    right=[(('toy',2),{0:Fraction(1)})]
    p,_=intersection(left,{0,1},lambda:None)
    q,_=intersection(right,{0,1},lambda:None)
    assert rank_pair(p,q)==1
    # Adding a COPY guard as an outside coordinate removes the injection.
    q,_=intersection([(('toy',2),{0:Fraction(1),9:Fraction(1)})],{0,1},lambda:None)
    assert rank_pair(p,q)==0
    # Cross-chart assignment uses an augmenting route and never duplicates an owner.
    assert layer_count({1:[1,2],2:[1]},{1:1,2:1},{1:2,2:2},2)==2
    assert layer_count({1:[1],2:[1]},{1:1,2:1},{1:2,2:2},2)==1
    return dict(exact_pairing=1,copy_guarded_pairing=0,augmenting_owner_reassignment=True,duplicate_owner_rejected=True)


def run(inputs,campaign,cap,seconds):
    assert __debug__
    began=monotonic()
    def check_time():
        if monotonic()-began>=seconds:
            raise TimeCap
    price=load(campaign,'round13/alternative/reprice.py')
    previous=json.loads(read(campaign,'round17/complex/GLOBAL.json')[1])
    past=json.loads(read(campaign,'round17/complex/PROTOTYPE.json')[1])
    assert past['chart']==288 and past['aggregate_overgrant']['rank']==0
    word,result,caller=(price.authenticated(inputs,key) for key in price.PINS)
    targets,paid,_,_,stages,origins,visits,ranks,spaces=price.invoice(word,caller,result)
    assert stages==17 and sum(paid.values())==110519 and sum(targets.values())==22427
    group={j for j,p in origins.items() if p==(3,127,9)}
    assert len(group)==616
    owners=defaultdict(list)
    owner_paths={}
    for j in sorted(group):
        path=[]
        for f in sorted(visits[j]):
            if spaces[3]<spaces[f]<spaces[127]:
                path.append(f)
                owners[f].append(j)
        owner_paths[j]=path
    shapes={f:min(ranks[f],10-ranks[f]) for f in owners}
    assert set(shapes.values())<=set(range(1,6))
    assert all(max(shapes[f] for f in fs)==previous['any_old_rank9_midpoint_ideal_best_smaller_rank_by_role'][str(j)]
               for j,fs in owner_paths.items())
    tariff={1:Fraction()}
    for k in (2,3,4,5):
        h=Counter((k,10-k)); h[9]-=1; h[1]-=1
        tariff[k]=stages*price.dot(h,lambda r:price.power(r,price.TARGET))[1]
        assert tariff[k]>tariff[k-1]
    h=Counter(targets); h.subtract(paid)
    baseline=price.dot(h,lambda r:price.power(r,price.TARGET))[1]
    smaller=Fraction(previous['actual_smaller_funded_old_path_gain'][1])
    assert baseline==Fraction(previous['old_moment'][1])
    best={j:max(tariff[shapes[f]] for f in fs) for j,fs in owner_paths.items()}
    def key(chart):
        weight=tariff[shapes[chart]]
        direct=sum(best[j]-max((tariff[shapes[f]] for f in owner_paths[j] if f!=chart),default=0)
                   for j in owners[chart])
        proportional=sum(weight/len(owner_paths[j]) for j in owners[chart])
        return (-direct,-proportional,-len(owners[chart]),chart)
    order=sorted((f for f in owners if shapes[f]>1),key=key)
    capacity={f:len(roles) if shapes[f]>1 else 0 for f,roles in owners.items()}
    initial=bounds(owners,capacity,shapes,tariff,baseline,smaller)
    assert Fraction(initial['margin_upper'])==Fraction(previous['all_actual_old_midpoints_funded_upper'][1])
    records=[]
    checkpoints=[]
    reason='chart cap'
    try:
        prefix=scan(word,set(order[:cap]),check_time)
        suffix=scan(word,set(order[:cap]),check_time,True)
        for chart in order[:cap]:
            p,pr=intersection(prefix[chart],group,check_time)
            s,sr=intersection(suffix[chart],group,check_time)
            pair=rank_pair(p,s)
            capacity[chart]=min(pair,len(owners[chart]))
            records.append(dict(chart=chart,rank=ranks[chart],shape=shapes[chart],pair_rank=pair,
                                owner_capacity=capacity[chart],prefix_generators=len(prefix[chart]),
                                suffix_generators=len(suffix[chart]),prefix_outside_rank=pr,suffix_outside_rank=sr,
                                prefix_group=encode(p),suffix_group=encode(s)))
            if len(records)%8==0 or len(records)==len(order[:cap]):
                b=bounds(owners,capacity,shapes,tariff,baseline,smaller)
                checkpoints.append(dict(tested=len(records),**b))
                if Fraction(b['margin_upper'])<0:
                    reason='negative directed stock upper'
                    break
    except TimeCap:
        reason='time'
    final=bounds(owners,capacity,shapes,tariff,baseline,smaller)
    if Fraction(final['margin_upper'])<0:
        reason='negative directed stock upper'
    elif len(records)==len(order):
        reason='exhausted'
    return dict(status='NEGATIVE_STOCK_UPPER' if Fraction(final['margin_upper'])<0 else 'UNRESOLVED_OR_POSITIVE',
                reason=reason,pins={f'public/{k}':v for k,v in price.PINS.items()} | PINS,
                source_head='e3f8d39c43b07063dfc5b800f71c5d21015259e6',
                source_scientific_tree='6678a6718f29a2da57efa3e748fa8ba997f6a46c',
                target=str(price.TARGET),caps=dict(charts=cap,seconds=seconds),seed=None,
                owner_paths=owner_paths,chart_owners=owners,chart_shapes=shapes,order=order,
                old_margin_upper=str(baseline),smaller_actual_funded_upper=str(smaller),
                rank9_funded_tariff_upper={k:str(v) for k,v in tariff.items()},
                initial=initial,final=final,checkpoints=checkpoints,tested=records,
                zero_price_charts=sorted(f for f in owners if shapes[f]==1),
                pending=order[len(records):],controls=controls(),individual_site_tests=0,
                scope='Original paid and scalar tape, all-clock coframed gathers and injections on one literal chart '
                      'per split, individually outside/COPY-canceled, jointly dual in the common old group basis. '
                      'Grant free clocks, holding, ownership, routing, precision and tape; one paid terminal each stage.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs',type=Path)
    parser.add_argument('campaign',type=Path)
    parser.add_argument('--cap',type=int,choices=range(1,257),default=256)
    parser.add_argument('--seconds',type=int,choices=range(1,721),default=720)
    print(json.dumps(run(**vars(parser.parse_args())),indent=2,sort_keys=True))
