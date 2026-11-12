"""Coupled one-vector productive endpoint and paid interior chart moves."""
from collections import Counter
from fractions import Fraction as F
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import ceil, floor
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

H = Path(__file__).resolve().parent
I = H / 'inputs'
S = 10**52


def timed_out(*_):
    raise TimeoutError


def get_inventory(w, base):
    public, groups, uses, incident = base['inventory'](w)
    spaces = list(map(base['span'],w['frames']))
    chart = {g: members[0][1] for g,members in groups.items()}
    movable = {g for g,members in groups.items() if all(r in public for r,_,_ in members)}
    endpoint = {(r,c):g for g,members in groups.items() for r,c,b in members if b and r in public}
    assert len(endpoint) == 2202
    ends = {}
    for g, rows in incident.items():
        for t,_,side in rows:
            ends.setdefault(t,{})[side] = g
    edges = [(t, e['source'], e['target'], True) for t,e in sorted(ends.items())]
    edges += [(r,endpoint[r,w['initial'][r]],endpoint[r,w['final'][r]],False) for r in sorted(public)]
    out = []
    for t,a,b,paid in edges:
        if a not in movable and b not in movable:
            continue
        ca,cb = chart[a],chart[b]
        assert spaces[ca] < spaces[cb]
        assert not paid or w['program'][t][-1] is False
        out.append((t,a,b,ca,cb,len(w['frames'][cb])-len(w['frames'][ca]),paid))
    return groups,uses,spaces,chart,movable,out


def bound(v, active, spaces, edges, inc, maxclosure, high):
    ids = {g:i for i,g in enumerate(active)}
    weights = [0]*len(active)
    imp = set()
    for _,a,b,ca,cb,d,paid in edges:
        x,y = ids.get(a), ids.get(b)
        if x is None and y is None:
            continue
        if v in spaces[cb]:
            assert x is not None and y is None
            if paid:
                weights[x] += inc[d][high]
            elif d==1:
                imp.add((x,None))
            else:
                weights[x] -= inc[d][1-high]
        else:
            slope = -inc[d+1][1-high] if paid else inc[d+1][high]
            if x is not None:
                imp.add((x,y))
                weights[x] -= slope
            if y is not None:
                weights[y] += slope
    value,chosen = maxclosure(weights,imp)
    return value,{active[i] for i in chosen}


def certify(v, chosen, edges, spaces, inc):
    price = [0,0]
    dp,dt = Counter(),Counter()
    p,tg = [],[]
    for t,a,b,ca,cb,d,paid in edges:
        x,y=a in chosen,b in chosen
        a2=spaces[ca]|{u^v for u in spaces[ca]} if x else spaces[ca]
        b2=spaces[cb]|{u^v for u in spaces[cb]} if y else spaces[cb]
        assert a2<=b2
        dn=d+y-x
        assert paid or dn>0
        if dn==d:
            continue
        hist,delta,records=(dp,-1,p) if paid else (dt,1,tg)
        hist[d]-=delta
        if dn:
            hist[dn]+=delta
        records.append([t,d,dn])
        l,h = inc[max(d,dn)]
        if paid==(dn<d):
            price[0]+=l
            price[1]+=h
        else:
            price[0]-=h
            price[1]-=l
    return price,dp,dt,p,tg


def main():
    assert __debug__
    signal(SIGALRM,timed_out)
    alarm(60)
    raw = decompress((I/'7334-WORD.json.gz').read_bytes())
    assert sha256(raw).hexdigest()=='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
    w = loads(raw)
    base = run_path(str(I/'inventory.py'))
    groups,uses,spaces,chart,movable,edges=get_inventory(w,base)
    maxclosure=run_path(str(I/'closure.py'))['maxclosure']
    h=run_path(str(I/'pricing.py'))['power_bounds']
    lo,hi=map(F,('0.00364665195644044790699554028334161','0.00364665195644044790699554028334162'))
    h0={0:(F(0),F(0))}|{r:(h(r,hi)[0],h(r,lo)[1]) for r in range(1,10)}
    inc={r:(floor(S*(h0[r][0]-h0[r-1][1])),ceil(S*(h0[r][1]-h0[r-1][0]))) for r in range(1,10)}
    results=[]
    witness=None
    capped=False
    try:
        for v in range(1,512):
            active=sorted(g for g in movable if v not in spaces[chart[g]])
            up,_=bound(v,active,spaces,edges,inc,maxclosure,1)
            results.append([v,len(active),up])
            if up<=0:
                continue
            lower,choice=bound(v,active,spaces,edges,inc,maxclosure,0)
            if lower<=0:
                continue
            price,dp,dt,p,tg=certify(v,choice,edges,spaces,inc)
            assert price[0]==lower and price[1]<=up
            witness={'vector':v,'groups':{g:groups[g] for g in sorted(choice)},
                     'contacts':{g:uses[g] for g in sorted(choice)},'changed_paid':p,'changed_targets':tg,
                     'paid_old_minus_new':{r:n for r,n in dp.items() if n},
                     'target_new_minus_old':{r:n for r,n in dt.items() if n},
                     'gain':[str(17*F(x,S)) for x in price]}
            break
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    print(dumps({'inputs':{p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(I.iterdir())},
                 'groups':len(groups),'eligible_groups':len(movable),'vectors_checked':len(results),
                 'target_edges':sum(not e[-1] for e in edges),'paid_edges':sum(e[-1] for e in edges),
                 'case_cap':511,'seconds_cap':60,'results':results,'witness':witness,'capped':capped},
                sort_keys=True,indent=2))
    if capped:
        raise SystemExit(2)


if __name__=='__main__':
    main()
