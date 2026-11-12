"""Certify a shared price vector by an enclosing exact L1 polytope."""
from fractions import Fraction as F
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from math import ceil,floor
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

I=Path(__file__).resolve().parent/'inputs'
S=10**52


def stop(*_):
    raise TimeoutError('60-second shared price cap')


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(60)
    raw=decompress((I/'7334-WORD.json.gz').read_bytes())
    assert sha256(raw).hexdigest()=='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
    w=loads(raw)
    common=run_path(str(I/'target_closure.py'))
    inv=run_path(str(I/'inventory.py'))
    groups,uses,spaces,chart,movable,edges=common['get_inventory'](w,inv)
    solver=run_path(str(I/'closure.py'))['maxclosure']
    h=run_path(str(I/'pricing.py'))['power_bounds']
    lo,hi=map(F,('0.00364665195644044790699554028334161','0.00364665195644044790699554028334162'))
    h0={0:(F(0),F(0))}|{r:(h(r,hi)[0],h(r,lo)[1]) for r in range(1,10)}
    box={r:(floor(S*(h0[r][0]-h0[r-1][1])),ceil(S*(h0[r][1]-h0[r-1][0]))) for r in range(1,10)}
    mid={r:l+u for r,(l,u) in box.items()}
    radius=sum(u-l for l,u in box.values())
    assert radius>0 and min(mid.values())>radius
    # Quantities here use scale 2*S. The nine price intervals lie inside this L1 ball.
    vertices=[{r:(m+sign*radius*(r==j),)*2 for r,m in mid.items()} for j in range(1,10) for sign in (-1,1)]
    rows=[]
    capped=False
    running=None
    try:
        for v in range(1,512):
            active=sorted(g for g in movable if v not in spaces[chart[g]])
            running=[v,[]]
            for vals in vertices:
                value,_=common['bound'](v,active,spaces,edges,vals,solver,1)
                running[1].append(value)
            rows.append(running)
            running=None
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    print(dumps({'pins':{p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(I.iterdir())},
                 'scale':2*S,'directed_increment_box':box,'radius':radius,'center':mid,
                 'vectors_checked':len(rows),'vertex_count':len(vertices),'runner_cap_seconds':60,
                 'rows':rows,'partial_row':running,'capped':capped,'eligible_groups':len(movable),
                 'max':max((max(a) for _,a in rows),default=None)},sort_keys=True,indent=2))
    if capped:
        raise SystemExit(2)


if __name__=='__main__':
    main()
