"""Bound simultaneous common-plane growth, with productive endpoints charged."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import ceil, floor
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

INPUTS = Path(__file__).resolve().parent / 'inputs'
PINS = {
    '7481-WORD.json.gz': 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9',
    'R226-PLANES.json': '68ea271a02374de22edfa105e6033ebc670087d3627798f15bab14c9962479b8',
    'closure.py': '64f57a509aac0c7f56c33ce5f84f99c3a4377d4ecc993f7424ad4115542a173f',
    'inventory.py': '347a7d90d34f0d7134d4dc68d95f135ee7cd9e002d6176eb5968f85f00db7d43',
    'pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'target_closure.py': '8ef8fbc45d4f2414944443d2a89147b4b9c2ba225d0faa065dc351f212b709fb',
}
CROSSING = (
    '9117702599223995588631135479313/2500000000000000000000000000000000',
    '36470810396895982354524541917253/10000000000000000000000000000000000',
)
SCALE = 10**52
CAP = 256


def authenticate():
    for name, digest in PINS.items():
        assert sha256((INPUTS / name).read_bytes()).hexdigest() == digest, name
    raw = decompress((INPUTS / '7481-WORD.json.gz').read_bytes())
    assert sha256(raw).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    saved = loads((INPUTS / 'R226-PLANES.json').read_bytes())
    planes = [tuple(p) for p, upper in saved['records']]
    seeds = saved['seed_vectors']
    expected = {tuple(sorted((a,b,a^b))) for a in seeds for b in range(1,512) if a!=b}
    assert len(planes) == len(expected) == 1014 and set(planes)==expected
    return loads(raw), planes


def price_tables():
    h = run_path(str(INPUTS/'pricing.py'))['power_bounds']
    low,high = map(Fraction,CROSSING)
    tariff = [(Fraction(0),Fraction(0))]+[(h(r,high)[0],h(r,low)[1]) for r in range(1,10)]
    box = [(floor(SCALE*(b[0]-a[1])),ceil(SCALE*(b[1]-a[0])))
           for a,b in zip(tariff,tariff[1:])]
    assert all(0<l<=u for l,u in box)
    center = [l+u for l,u in box]
    radius = sum(u-l for l,u in box)
    assert min(center) > radius > 0
    vertices = [[(m+s*radius*(i==j),)*2 for i,m in enumerate(center)]
                for j in range(9) for s in (-1,1)]
    return box,center,radius,vertices


def gain(old, new, paid, prices, upper):
    if old==new:
        return 0
    larger,smaller = max(old,new), min(old,new)
    positive = paid == (new<old)
    value = sum(prices[j][upper if positive else 1-upper] for j in range(smaller,larger))
    return value if positive else -value


def choices(plane, spaces, chart, movable, edges):
    increments = []
    for space in spaces:
        count=sum(v in space for v in plane)
        assert count in (0,1,3)
        increments.append({0:2,1:1,3:0}[count])
    active = sorted(g for g in movable if increments[chart[g]])
    index = {g:i for i,g in enumerate(active)}
    feasible = []
    for t,a,b,ca,cb,d,paid in edges:
        x,y = index.get(a),index.get(b)
        if x is None and y is None:
            continue
        ka,kb=increments[ca],increments[cb]
        if kb:
            assert ka>=kb
        new01 = d+kb if y is not None else None
        if x is None:
            new11 = None
        elif kb and y is None:
            new11 = None
        else:
            new11 = d+kb-ka
        assert new11 is None or new11 >= 0
        feasible.append((t,x,y,d,paid,new01,new11))
    return active,feasible


def score(edges, prices):
    # Sum per-edge available positive changes before imposing shared vertex choices.
    return sum(max(0,
                   gain(d,e1,paid,prices,1) if e1 is not None else 0,
                   gain(d,e2,paid,prices,1) if e2 is not None and (paid or e2) else 0)
               for _,_,_,d,paid,e1,e2 in edges)


def optimize(active, edges, prices, upper, solver):
    weights = [0]*len(active)
    implications=set()
    for _,x,y,d,paid,new01,new11 in edges:
        only_high=0
        if y is not None:
            only_high=gain(d,new01,paid,prices,upper)
            weights[y]+=only_high
        if x is not None:
            if new11 is None or (not paid and new11==0):
                implications.add((x,None))
            else:
                if y is not None:
                    implications.add((x,y))
                weights[x]+=gain(d,new11,paid,prices,upper)-only_high
    total, selected = solver(weights,implications)
    observed=0
    changes=[]
    for t,x,y,d,paid,new01,new11 in edges:
        new = new11 if x in selected else new01 if y in selected else d
        assert new is not None and (paid or new>0)
        observed+=gain(d,new,paid,prices,upper)
        if d!=new:
            changes.append([t,d,new,'paid' if paid else 'target'])
    assert observed==total
    return total,selected,changes


def timed_out(*_):
    raise TimeoutError('60-second discovery cap')


def main():
    assert __debug__
    signal(SIGALRM,timed_out)
    ranked, records, current = [], [], None
    witness=None
    capped=False
    inventory={}
    alarm(60)
    try:
        w,planes=authenticate()
        inv=run_path(str(INPUTS/'inventory.py'))
        common=run_path(str(INPUTS/'target_closure.py'))
        groups,uses,spaces,chart,movable,edges=common['get_inventory'](w,inv)
        inventory={'groups':len(groups),'eligible':len(movable),
                   'paid_edges':sum(e[-1] for e in edges),'target_edges':sum(not e[-1] for e in edges)}
        box,center,radius,vertices=price_tables()
        inventory.update({'increment_box':box,'center':center,'radius':radius,'scale':SCALE})
        solver=run_path(str(INPUTS/'closure.py'))['maxclosure']
        ranked=sorted(((score(choices(p,spaces,chart,movable,edges)[1],box),p) for p in planes),
                      key=lambda row:(-row[0],row[1]))
        for value,plane in ranked[:CAP]:
            current={'plane':plane,'score':value,'shared_price_upper':[]}
            active,case=choices(plane,spaces,chart,movable,edges)
            upper,_,_=optimize(active,case,box,1,solver)
            current['edgewise_upper']=upper
            lower,selected,changes=optimize(active,case,box,0,solver)
            current['edgewise_lower']=lower
            if lower>0:
                witness={'plane':plane,'components':{g:groups[g] for g in (active[i] for i in sorted(selected))},
                         'changed_edges':changes,'raw_lower':str(Fraction(17*lower,SCALE))}
            elif upper>0:
                for prices in vertices:
                    result,_,_=optimize(active,case,prices,1,solver)
                    current['shared_price_upper'].append(result)
            current['excluded'] = upper==0 or (
                len(current['shared_price_upper'])==18 and max(current['shared_price_upper'])==0
            )
            records.append(current)
            current=None
            if witness:
                break
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    result={'pins':PINS,'benchmark_head':'89eaa9d8cae37c1540de98f2d29a3abaabb96a2b',
            'crossing':CROSSING,'seconds_cap':60,'case_cap':CAP,'inventory':inventory,
            'ranking':ranked,'records':records,'capped':capped,'partial':current,'witness':witness,
            'open_planes':[row['plane'] for row in records if not row['excluded'] and
                           (witness is None or row['plane'] != witness['plane'])]+
                          [plane for _,plane in ranked[len(records):]],
            'untested_planes':[plane for _,plane in ranked[len(records):]],
            'planes_outside_saved_pool':43435-1014}
    print(dumps(result,sort_keys=True,indent=2))
    if capped:
        raise SystemExit(2)


if __name__=='__main__':
    main()
