"""Exact directed max closure for adding one binary vector to interior helper frames."""
from collections import Counter, deque
from fractions import Fraction as F
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import ceil, floor
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import setrecursionlimit

HERE = Path(__file__).resolve().parent
SCALE = 10**52
PINS = {
    'inputs/7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'inputs/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}


def maxclosure(weights, implications):
    count = len(weights)
    source, sink = count, count+1
    graph = [[] for _ in range(count+2)]
    positive = sum(max(0,w) for w in weights)
    inf = positive+1

    def edge(u,v,c):
        graph[u].append([v,c,len(graph[v])])
        graph[v].append([u,0,len(graph[u])-1])

    for i,w in enumerate(weights):
        if w>0:
            edge(source,i,w)
        elif w<0:
            edge(i,sink,-w)
    for u,v in implications:
        edge(u,sink if v is None else v,inf)
    flow = 0
    while True:
        level = [-1]*(count+2)
        level[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v,c,_ in graph[u]:
                if c and level[v]<0:
                    level[v] = level[u]+1
                    queue.append(v)
        if level[sink]<0:
            chosen = {i for i in range(count) if level[i]>=0}
            assert all(u not in chosen or v in chosen for u,v in implications)
            assert sum(weights[i] for i in chosen)==positive-flow
            return positive-flow,chosen
        at = [0]*(count+2)

        def push(u,budget):
            if u==sink:
                return budget
            while at[u]<len(graph[u]):
                e = graph[u][at[u]]
                v,c,rev = e
                if c and level[v]==level[u]+1:
                    amount = push(v,min(c,budget))
                    if amount:
                        e[1] -= amount
                        graph[v][rev][1] += amount
                        return amount
                at[u] += 1
            return 0

        while amount := push(source,inf):
            flow += amount


def stop(*_):
    raise TimeoutError('60-second binary-vector closure cap')


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(60)
    setrecursionlimit(20000)
    for n,h in PINS.items():
        assert sha256((HERE/n).read_bytes()).hexdigest()==h
    raw=decompress((HERE/'inputs/7334-WORD.json.gz').read_bytes())
    assert sha256(raw).hexdigest()=='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
    w=loads(raw)
    run=run_path(str(HERE/'inputs/inventory.py'))
    public,groups,uses,incident=run['inventory'](w)
    spaces=[run['span'](frame) for frame in w['frames']]
    ranks=list(map(len,w['frames']))
    chart={g:next(iter({c for _,c,_ in members})) for g,members in groups.items()}
    assert all({c for _,c,_ in members}=={chart[g]} for g,members in groups.items())
    movable={g for g,members in groups.items() if all(r in public and not end for r,_,end in members)}
    end_nodes={}
    for g,edges in incident.items():
        for t,_,side in edges:
            end_nodes.setdefault(t,{})[side]=g
    edges=[]
    for t,pair in sorted(end_nodes.items()):
        a,b=pair['source'],pair['target']
        if a not in movable and b not in movable:
            continue
        ca,cb=chart[a],chart[b]
        assert spaces[ca]<spaces[cb] and w['program'][t][-1] is False
        edges.append((t,a,b,ca,cb,ranks[cb]-ranks[ca]))
    h=run_path(str(HERE/'inputs/pricing.py'))['power_bounds']
    lo,hi=map(F,('0.00364665195644044790699554028334161','0.00364665195644044790699554028334162'))
    h0={0:(F(0),F(0))}|{r:(h(r,hi)[0],h(r,lo)[1]) for r in range(1,10)}
    inc={r:(floor(SCALE*(h0[r][0]-h0[r-1][1])),ceil(SCALE*(h0[r][1]-h0[r-1][0]))) for r in range(1,10)}
    assert all(0<a<=b for a,b in inc.values())
    assert maxclosure([5,-3],[(0,1)])==(2,{0,1})
    assert maxclosure([5,-3],[(0,1),(1,None)])==(0,set())
    results=[]
    witness=None
    capped=False
    try:
        for v in range(1,512):
            active=sorted(g for g in movable if v not in spaces[chart[g]])
            index={g:i for i,g in enumerate(active)}
            wl,wu=[0]*len(active),[0]*len(active)
            implications=set()
            for _,a,b,ca,cb,d in edges:
                ia,ib=index.get(a),index.get(b)
                if ia is None and ib is None:
                    continue
                if v in spaces[cb]:
                    assert ib is None and ia is not None
                    low,high=inc[d]
                    wl[ia]+=low
                    wu[ia]+=high
                else:
                    low,high=inc[d+1]
                    if ia is not None:
                        implications.add((ia,ib))
                        wl[ia]+=high
                        wu[ia]+=low
                    if ib is not None:
                        wl[ib]-=high
                        wu[ib]-=low
            upper,_=maxclosure(wu,implications)
            rec={'vector':v,'variables':len(active),'implications':len(implications),'upper_scaled':upper}
            if upper>0:
                lower,selected=maxclosure(wl,implications)
                rec['lower_scaled']=lower
                if lower>0:
                    chosen={active[i] for i in selected}
                    ranks_delta=Counter()
                    changed=[]
                    lower_check=upper_check=0
                    for t,a,b,ca,cb,d in edges:
                        x,y=a in chosen,b in chosen
                        da=spaces[ca]|{u^v for u in spaces[ca]} if x else spaces[ca]
                        db=spaces[cb]|{u^v for u in spaces[cb]} if y else spaces[cb]
                        assert da<=db
                        dn=d+y-x
                        if dn!=d:
                            ranks_delta[d]+=1
                            if dn:
                                ranks_delta[dn]-=1
                            changed.append([t,d,dn])
                        if dn<d:
                            lower_check+=inc[d][0]
                            upper_check+=inc[d][1]
                        elif dn>d:
                            lower_check-=inc[dn][1]
                            upper_check-=inc[dn][0]
                    assert lower_check==lower and lower<=upper_check<=upper
                    witness={'vector':v,'chosen_groups':sorted(chosen),'segments':{g:groups[g] for g in sorted(chosen)},
                             'contacts':{g:uses[g] for g in sorted(chosen)},'changed_rank_edges':changed,
                             'incident_paid_edges':sum(a in chosen or b in chosen for _,a,b,*_ in edges),
                             'old_minus_new_rank_hist':{r:c for r,c in ranks_delta.items() if c},
                             'raw_directed_bounds':[str(17*F(lower,SCALE)),str(17*F(upper_check,SCALE))]}
            results.append(rec)
            if witness:
                break
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    print(dumps({'pins':PINS|{'inputs/inventory.py':sha256((HERE/'inputs/inventory.py').read_bytes()).hexdigest()},
                 'groups':len(groups),'eligible_groups':len(movable),'incident_edges':len(edges),
                 'vectors_checked':len(results),'case_cap':511,'seconds_cap':60,'capped':capped,
                 'scale':SCALE,'rounding_intervals':inc,'results':results,'witness':witness},sort_keys=True,indent=2))
    if capped:
        raise SystemExit(2)


if __name__=='__main__':
    main()
