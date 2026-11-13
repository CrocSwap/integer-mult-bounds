"""Independent endpoint-aware plane pricing using reverse inventory and direct cuts."""
from fractions import Fraction as F
from gzip import decompress
from hashlib import sha256
from itertools import product
from json import dumps, loads
from math import ceil, floor
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

ROOT = Path(__file__).resolve().parent
PINS = {
    "endpoint_replay.py": "24d63caf9e647840f47675fecf775803c509f5fbc7ae6fc6b5d450782ec1d81d",
    "cut_flow.py": "a16c67f11d216d0a7d7f4caf0b994cc0a1dcbc01d667ed0924691f72f0959cdb",
    "reverse_inventory.py": "ac01889cd8e917b5c3f93dcefaa19c159efc18bcdd6973b94b481f08185d0127",
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/R226-PLANES.json": "68ea271a02374de22edfa105e6033ebc670087d3627798f15bab14c9962479b8",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
PAYLOAD = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
SCALE = 10**52
CAP = 60


def unique(items):
    values = dict(items)
    assert len(values) == len(items), "duplicate JSON key"
    return values


def stop(*_):
    raise TimeoutError("60-second independent endpoint-plane cap")


def gaps(plane, points):
    return [{0: 2, 1: 1, 3: 0}[sum(v in space for v in plane)] for space in points]


def compile_plane(gap, allowed, edges):
    active = {g:i for i,g in enumerate(g for g in allowed if gap[g])}
    source, sink = len(active), len(active)+1
    hard, terms = set(), []
    # Term tuple: from, to, old gap, new gap, directed upper if True.
    for a,b,d,paid in edges:
        x,y = active.get(a),active.get(b)
        if x is None and y is None:
            continue
        ka,kb = gap[a],gap[b]
        assert ka >= kb
        both = d+kb-ka
        assert 0 <= both <= d <= d+kb <= 9
        if kb and x is not None:
            hard.add((x,y if y is not None else sink))
        if x is not None and not paid and not both:
            hard.add((x,sink))
        if paid:
            if x is not None and d != both:
                terms.append((source,x,both,d,True))
            if y is not None:
                terms.append((y,x if x is not None else sink,d,d+kb,False))
        else:
            if y is not None:
                terms.append((source,y,d,d+kb,True))
                if x is not None:
                    terms.append((x,sink,d,d+kb,True))
            if x is not None and both and d != both:
                terms.append((x,sink,both,d,False))
    return source,sink,hard,terms


def optimistic_score(gap, allowed, edges, price):
    active = {g for g in allowed if gap[g]}
    total = 0
    for a,b,d,paid in edges:
        ka,kb = gap[a],gap[b]
        if paid:
            if a in active and (not kb or b in active):
                total += price[d]-price[d+kb-ka]
        elif b in active:
            total += price[d+kb]-price[d]
    return total


def cumulative(increments):
    result = [0]
    for inc in increments:
        result.append(result[-1]+inc)
    return result


def cut_value(compiled, reward_price, penalty_price, arc, push):
    source,sink,hard,terms = compiled
    graph = [{} for _ in range(sink+1)]
    offered = 0
    for u,v,a,b,reward in terms:
        price = reward_price if reward else penalty_price
        cap = price[b]-price[a]
        assert cap > 0
        arc(graph,u,v,cap)
        offered += cap if u == source else 0
    # Subtract common terminal capacities, which are paid on every cut.
    for node in range(source):
        common = min(graph[source].get(node,0),graph[node].get(sink,0))
        if common:
            graph[source][node] -= common
            graph[node][sink] -= common
            offered -= common
    for u,v in sorted(hard):
        arc(graph,u,v,offered+1)
    flow,_,side = push(graph,source,sink,offered)
    assert all(u not in side or v in side for u,v in hard)
    return offered-flow


def controls(arc,push):
    # These spaces realize both equal paid charts and target collapse.
    checks = (
        ([2,2],[(0,1,0,True)]),
        ([2,1],[(0,1,1,False)]),
        ([2,1],[(0,1,2,False),(0,1,2,True)]),
        ([2,0],[(0,1,2,False),(0,1,2,True)]),
        ([2,1],[(0,1,2,False)]),
    )
    h = [0,4,7,9,10,11,12,13,14,15]
    count = 0
    for gap,edges in checks:
        for a,b in product((False,True),repeat=2):
            allowed = [i for i,t in enumerate((a,b)) if t]
            opts = [product((0,1) if i in allowed and gap[i] else (0,),repeat=1) for i in range(2)]
            values = []
            for (x,),(y,) in product(*opts):
                if x and gap[1] and not y:
                    continue
                new = [d+y*gap[1]-x*gap[0] for _,_,d,_ in edges]
                if any(not paid and not z for z,(_,_,_,paid) in zip(new,edges,strict=True)):
                    continue
                values.append(sum((h[d]-h[z])*(1 if paid else -1)
                                  for z,(_,_,d,paid) in zip(new,edges,strict=True)))
            assert cut_value(compile_plane(gap,allowed,edges),h,h,arc,push) == max(values)
            count += 1
    return count


def main(case_path):
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3,12)
    signal(SIGALRM,stop)
    alarm(CAP)
    for name,pin in PINS.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == pin, name
    raw = decompress((ROOT/"inputs/7481-WORD.json.gz").read_bytes())
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw,object_pairs_hook=unique)
    assert len(word["program"]) == 76475
    endpoint,rev,flow = [run_path(str(ROOT/(x+".py")))
                         for x in ("endpoint_replay","reverse_inventory","cut_flow")]
    points,allowed,edges = endpoint["inventory"](word,rev)
    arc,push = flow["arc"],flow["push_until_cut"]
    control_count = controls(arc,push)
    h = run_path(str(ROOT/"inputs/pricing.py"))["power_bounds"]
    k0,k1 = map(F,("9117702599223995588631135479313/2500000000000000000000000000000000","36470810396895982354524541917253/10000000000000000000000000000000000"))
    bounds = [(F(0),F(0))]+[(h(r,k1)[0],h(r,k0)[1]) for r in range(1,10)]
    increment_lo = [floor(SCALE*(bounds[r][0]-bounds[r-1][1])) for r in range(1,10)]
    increment_hi = [ceil(SCALE*(bounds[r][1]-bounds[r-1][0])) for r in range(1,10)]
    center = [a+b for a,b in zip(increment_lo,increment_hi,strict=True)]
    radius = sum(b-a for a,b in zip(increment_lo,increment_hi,strict=True))
    assert 0 < radius < min(center)
    price_lo,price_hi = map(cumulative,(increment_lo,increment_hi))
    vertices = []
    for r,sign in product(range(9),(-1,1)):
        inc = center.copy()
        inc[r] += sign*radius
        vertices.append(cumulative(inc))
    compressed_cases = case_path.read_bytes()
    case_bytes = decompress(compressed_cases) if case_path.suffix == ".gz" else compressed_cases
    source_cases = loads(case_bytes,object_pairs_hook=unique)
    lead_records = source_cases.get("records")
    if lead_records is None:
        planes = [tuple(p) for p in source_cases["planes"]]
    else:
        planes = [tuple(r["plane"]) for r in lead_records]
    pool = {tuple(p) for p,_ in loads((ROOT/"inputs/R226-PLANES.json").read_bytes(),object_pairs_hook=unique)["records"]}
    assert 1 <= len(planes) <= 256 and len(planes) == len(set(planes))
    assert set(planes) <= pool and len(pool) == 1014
    ranking = sorted(((optimistic_score(gaps(p,points),allowed,edges,price_hi),p) for p in pool),
                     key=lambda row:(-row[0],row[1]))
    assert [p for _,p in ranking[:len(planes)]] == planes
    if "ranking" in source_cases:
        assert source_cases["ranking"] == [[s,list(p)] for s,p in ranking]
    rows = []
    capped = False
    try:
        for rank,plane in enumerate(planes):
            compiled = compile_plane(gaps(plane,points),allowed,edges)
            upper = cut_value(compiled,price_hi,price_lo,arc,push)
            lower = cut_value(compiled,price_lo,price_hi,arc,push)
            cert = [cut_value(compiled,v,v,arc,push) for v in vertices] if upper and not lower else []
            if lead_records is not None:
                control = lead_records[rank]
                assert (control["score"],control["edgewise_upper"],control["edgewise_lower"],control["shared_price_upper"]) == (ranking[rank][0],upper,lower,cert),plane
            rows.append([plane,compiled[0],lower,upper,cert])
    except TimeoutError:
        capped = True
    finally:
        alarm(0)
    print(dumps(dict(pins=PINS,case_input_sha256=sha256(case_bytes).hexdigest(),
                     groups=len(points),eligible_groups=len(allowed),paid_edges=sum(e[-1] for e in edges),
                     target_edges=sum(not e[-1] for e in edges),case_cap=256,runner_cap_seconds=CAP,
                     scale=SCALE,shared_scale=2*SCALE,capped=capped,requested=len(planes),
                     controls=control_count,rows=rows),indent=2,sort_keys=True))
    if capped:
        raise SystemExit(2)


if __name__ == "__main__":
    assert len(argv) == 2
    main(Path(argv[1]))
