"""Independent reverse-word inventory and direct edge cuts for the R226 sample."""
from collections import Counter
from fractions import Fraction as F
from gzip import decompress
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from math import ceil, floor
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
PINS = {
    "7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "cut_flow.py": "a16c67f11d216d0a7d7f4caf0b994cc0a1dcbc01d667ed0924691f72f0959cdb",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "reverse_inventory.py": "ac01889cd8e917b5c3f93dcefaa19c159efc18bcdd6973b94b481f08185d0127",
}
SCALE = 10**52
CAP = 60


def stop(*_):
    raise TimeoutError("60-second independent common-plane cap")


def plane_cut(plane, spaces, eligible, edges, diff, add_arc, max_flow):
    gap = [{0:2, 1:1, 3:0}[sum(p in space for p in plane)] for space in spaces]
    active = {g:i for i,g in enumerate(g for g in sorted(eligible) if gap[g])}
    source, sink = len(active), len(active)+1
    graph = [{} for _ in range(sink+1)]
    hard = set()
    offered = 0
    for a,b,d in edges:
        x,y = active.get(a),active.get(b)
        if x is None and y is None:
            continue
        ka,kb = gap[a],gap[b]
        assert ka >= kb
        if x is not None:
            if kb and y is None:
                hard.add((x,sink))
            else:
                if y is not None:
                    hard.add((x,y))
                reward = diff[d,d+kb-ka][1]
                if reward:
                    add_arc(graph,source,x,reward)
                    offered += reward
        if y is not None:
            cost = diff[d+kb,d][0]
            assert cost > 0
            add_arc(graph,y,x if x is not None else sink,cost)
    for x,y in sorted(hard):
        add_arc(graph,x,y,offered+1)
    value, pushes, chosen = max_flow(graph,source,sink,offered)
    assert all(x not in chosen or y in chosen for x,y in hard)
    return offered-value, offered, pushes


def control(diff, add_arc, max_flow):
    plane = (1,2,3)
    spaces = [{0},{0,1,4,5},set(range(8))]
    edges = [(0,1,2),(1,2,1)]
    wanted = diff[2,1][1]+diff[1,0][1]
    assert plane_cut(plane,spaces,{0,1},edges,diff,add_arc,max_flow)[0] == wanted
    assert plane_cut(plane,spaces,{0},edges,diff,add_arc,max_flow)[0] == 0


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3,12)
    signal(SIGALRM,stop)
    alarm(CAP)
    for name, pin in PINS.items():
        assert sha256((INPUTS/name).read_bytes()).hexdigest() == pin
    data = decompress((INPUTS/"7334-WORD.json.gz").read_bytes())
    assert sha256(data).hexdigest() == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word = loads(data)
    assert len(word["program"]) == 76466
    inv = run_path(str(INPUTS/"reverse_inventory.py"))
    flow = run_path(str(INPUTS/"cut_flow.py"))
    spaces,eligible,edges = flow["exact_inventory"](word,inv["reverse_trace"],inv["frame_space"])
    assert (len(eligible),len(edges)) == (482,2292)
    h = run_path(str(INPUTS/"pricing.py"))["power_bounds"]
    lo,hi = map(F,("0.00364665195644044790699554028334161","0.00364665195644044790699554028334162"))
    levels = [(F(0),F(0))]+[(h(r,hi)[0],h(r,lo)[1]) for r in range(1,10)]
    diff = {(a,b):(floor(SCALE*(levels[a][0]-levels[b][1])),ceil(SCALE*(levels[a][1]-levels[b][0])))
            if a!=b else (0,0) for a in range(10) for b in range(a+1)}
    score = Counter({v:0 for v in range(1,512)})
    for a,b,d in edges:
        if a in eligible:
            for v in spaces[b]-spaces[a]:
                score[v] += diff[d,d-1][1]
    seeds = sorted(score,key=lambda v:(-score[v],v))[:4]
    assert seeds == [365,244,327,371]
    planes = {tuple(sorted((u,v,u^v))) for u,v in combinations(range(1,512),2) if u in seeds or v in seeds}
    assert len(planes) == 1014
    add_arc,max_flow = flow["arc"],flow["push_until_cut"]
    control(diff,add_arc,max_flow)
    result = []
    total_offered = total_pushes = 0
    for plane in sorted(planes):
        upper,offered,pushes = plane_cut(plane,spaces,eligible,edges,diff,add_arc,max_flow)
        total_offered += offered
        total_pushes += pushes
        result.append([plane,upper])
    alarm(0)
    print(dumps(dict(pins=PINS,seed_vectors=seeds,records=result,planes_checked=len(result),
                     total_planes=43435,untested_planes=43435-len(result),case_cap=1014,
                     eligible_groups=len(eligible),incident_edges=len(edges),seconds_cap=CAP,
                     scale=SCALE,total_offered_scaled=total_offered,total_augmenting_paths=total_pushes,
                     max_upper_scaled=max(r[1] for r in result)),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
