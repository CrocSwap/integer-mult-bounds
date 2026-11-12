"""Exact closure test for a bounded family of common two-dimensional additions."""
from collections import Counter
from fractions import Fraction as F
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from math import floor,ceil
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

I=Path(__file__).resolve().parent/'inputs'
S=10**52


def stop(*_):
    raise TimeoutError('60-second plane cap')


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(60)
    raw=decompress((I/'7334-WORD.json.gz').read_bytes())
    assert sha256(raw).hexdigest()=='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
    w=loads(raw)
    inv=run_path(str(I/'inventory.py'))
    common=run_path(str(I/'target_closure.py'))
    groups,uses,spaces,chart,movable,edges=common['get_inventory'](w,inv)
    movable={g for g in movable if all(not end for _,_,end in groups[g])}
    edges=[e for e in edges if e[-1] and (e[1] in movable or e[2] in movable)]
    assert len(movable)==482 and len(edges)==2292
    h=run_path(str(I/'pricing.py'))['power_bounds']
    lo,hi=map(F,('0.00364665195644044790699554028334161','0.00364665195644044790699554028334162'))
    H={0:(F(0),F(0))}|{r:(h(r,hi)[0],h(r,lo)[1]) for r in range(1,10)}
    diff={(x,y):(0,0) if x==y else (floor(S*(H[x][0]-H[y][1])),ceil(S*(H[x][1]-H[y][0])))
          for x in range(10) for y in range(x+1)}
    prices=Counter({j:0 for j in range(1,512)})
    for _,a,_,ca,cb,d,_ in edges:
        if a in movable:
            for v in spaces[cb]-spaces[ca]:
                prices[v]+=diff[d,d-1][1]
    seeds=sorted(prices,key=lambda v:(-prices[v],v))[:4]
    planes=sorted({tuple(sorted((a,b,a^b))) for a in seeds for b in range(1,512) if a!=b})
    assert len(planes)<=1024
    solver=run_path(str(I/'closure.py'))['maxclosure']

    def price(plane,upper):
        k=[]
        for W in spaces:
            c=sum(v in W for v in plane)
            assert c in (0,1,3)
            k.append(2-(c+1).bit_length()+1)
        active=sorted(g for g in movable if k[chart[g]])
        ids={g:i for i,g in enumerate(active)}
        weight=[0]*len(active)
        implications=set()
        for _,a,b,ca,cb,d,_ in edges:
            x,y=ids.get(a),ids.get(b)
            if x is None and y is None:
                continue
            if not k[cb]:
                assert y is None and x is not None
                weight[x]+=diff[d,d-k[ca]][upper]
            else:
                debit=diff[d+k[cb],d][1-upper]
                if x is not None:
                    implications.add((x,y))
                    weight[x]+=debit+diff[d,d+k[cb]-k[ca]][upper]
                if y is not None:
                    weight[y]-=debit
        value,chosen=solver(weight,implications)
        return value,{active[i] for i in chosen},k

    result=[]
    witness=None
    capped=False
    try:
        for plane in planes:
            up,_,_=price(plane,1)
            result.append([plane,up])
            if not up:
                continue
            low,chosen,k=price(plane,0)
            if low<=0:
                continue
            rank_delta=Counter()
            check=0
            changed=[]
            def enlarged(c):
                return {x^v for x in spaces[c] for v in (0,*plane)}
            for t,a,b,ca,cb,d,_ in edges:
                x,y=a in chosen,b in chosen
                aa=enlarged(ca) if x else spaces[ca]
                bb=enlarged(cb) if y else spaces[cb]
                assert aa<=bb
                new=d+y*k[cb]-x*k[ca]
                if new!=d:
                    rank_delta[d]+=1
                    if new:
                        rank_delta[new]-=1
                    changed.append([t,d,new])
                    check+=diff[d,new][0] if new<d else -diff[new,d][1]
            assert check==low
            witness={'plane':plane,'groups':{g:groups[g] for g in sorted(chosen)},
                     'contacts':{g:uses[g] for g in sorted(chosen)},'changed':changed,
                     'paid_old_minus_new':{r:n for r,n in rank_delta.items() if n},'gain_lower':str(17*F(low,S))}
            break
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    print(dumps({'inputs':{p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(I.iterdir())},
                 'seed_vectors':seeds,'plane_count':len(planes),'total_planes':43435,
                 'planes_checked':len(result),'case_cap':1024,'seconds_cap':60,'capped':capped,
                 'max_upper_scaled':max((x[1] for x in result),default=None),'records':result,'witness':witness},
                sort_keys=True,indent=2))
    if capped:
        raise SystemExit(2)


if __name__=='__main__':
    main()
