"""Exact monomial-orbit graph of ternary pencils, including zero-u coordinates."""
from collections import Counter, deque
from hashlib import sha256
from itertools import combinations_with_replacement, product
from math import factorial, prod
from pathlib import Path
import json,sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from algorithms import scalar_small_field
from settlement import Field, ternary_extra


def normalize(f, v):
    u,b,w=v
    if u:
        return (1,f.mul[u][b],f.mul[u][w])
    pivot=b or w
    if not pivot:
        return (0,0,0)
    inv=f.inv[pivot]
    return (0,f.mul[inv][b],f.mul[inv][w])


def packet_table(f):
    types=sorted({normalize(f,v) for v in product(range(f.q),repeat=3)})
    labels={v:i for i,v in enumerate(types)}
    changes={}
    for i,(ui,bi,wi) in enumerate(types):
        for j,(uj,bj,wj) in enumerate(types):
            targets=set()
            for a in range(1,f.q):
                neg=f.neg[a]
                vi=(f.add[ui][f.mul[a][uj]],bi,wi)
                vj=(uj,f.add[bj][f.mul[neg][bi]],f.add[wj][f.mul[neg][wi]])
                targets.add(tuple(sorted((labels[normalize(f,vi)],labels[normalize(f,vj)]))))
            changes[i,j]=targets
    return types,changes


def candidates(m,types):
    for word in combinations_with_replacement(range(len(types)),m):
        packets=[types[j] for j in word]
        if not any(w for _,_,w in packets):
            continue
        x=tuple(u*b % 3 for u,b,_ in packets)
        y=tuple(u*w % 3 for u,_,w in packets)
        if sum(x)%3==1 and sum(y)%3==0:
            yield word,x,y


def successors(word,changes):
    freq=Counter(word)
    for i in freq:
        for j in freq:
            if i==j and freq[i]<2:
                continue
            rest=list(word)
            rest.remove(i)
            rest.remove(j)
            for pair in changes[i,j]:
                yield tuple(sorted((*rest,*pair)))


def orbit_weight(word, m):
    # The all-zero packet has label 0. All other local scaling orbits have size 2.
    counts=Counter(word)
    return factorial(m)*2**(m-counts[0])//prod(factorial(n) for n in counts.values())


def census(m):
    f=Field(3)
    types,changes=packet_table(f)
    info={}
    seeds=[]
    for word,x,y in candidates(m,types):
        info[word]=(x,y)
        if not any(y) and x.count(1)-x.count(2) in (1,-2):
            seeds.append(word)
    dist=dict.fromkeys(seeds,0)
    queue=deque(seeds)
    while queue:
        word=queue.popleft()
        for nxt in successors(word,changes):
            if nxt not in dist:
                dist[nxt]=dist[word]+1
                queue.append(nxt)
    if info.keys()!=dist.keys():
        raise ValueError("monomial quotient coverage")
    hist, gap_hist = Counter(),Counter()
    digest=sha256()
    example=None
    key_prior={}
    hidden=None
    first_dimension_gaps=[]
    for word in sorted(dist):
        x,y=info[word]
        lower=sum(v!=0 for v in y)-scalar_small_field(f,y)
        gap=dist[word]-max(lower,ternary_extra(x))
        if gap<0 or dist[word]>2*lower+ternary_extra(x):
            raise ValueError("sharp ternary price envelope")
        wt=orbit_weight(word,m)
        hist[dist[word]]+=wt
        gap_hist[gap]+=wt
        if gap and (not example or gap>example["gap"]):
            example=dict(packets=[types[i] for i in word],gap=gap,true_distance=dist[word],
                         separation=lower,scalar=ternary_extra(x))
        if m==5 and gap:
            first_dimension_gaps.append(dict(packets=[types[i] for i in word],weight=wt,
                                             cost=dist[word],separation=lower,scalar=ternary_extra(x)))
        key=tuple(sorted(zip(x,y)))
        if key not in key_prior:
            key_prior[key]=(word,dist[word])
        elif hidden is None and key_prior[key][1]!=dist[word]:
            prior,val=key_prior[key]
            hidden=dict(first=[types[i] for i in prior],second=[types[i] for i in word],
                        distances=[val,dist[word]])
        digest.update(bytes((*word,dist[word])))
    total=sum(hist.values())
    if total!=(3**m-1)*3**(m-1)*(3**(m-1)-1):
        raise ValueError("monomial orbit multiplicities")
    return dict(m=m,orbits=len(dist),raw_states=total,weighted_costs=dict(sorted(hist.items())),
                weighted_bound_gap=dict(sorted(gap_hist.items())),gap_example=example,
                equal_charge_example=hidden,first_dimension_gaps=first_dimension_gaps,
                orbit_cost_sha256=digest.hexdigest())


def collect():
    return [census(m) for m in range(2,9)]


if __name__=="__main__":
    extended=sys.argv[1:]==["--extended"]
    if sys.argv[1:] not in ([],["--extended"]):
        raise ValueError("unknown orbit domain")
    rows=[census(m) for m in range(9,13)] if extended else collect()
    fixture="LARGE-ORBITS.json" if extended else "TERNARY-ORBITS.json"
    if json.loads(json.dumps(rows))!=json.loads((HERE/fixture).read_text(encoding="utf8")):
        raise ValueError("frozen ternary orbit census")
    print(json.dumps(dict(status="PASS_SETTLEMENT_TERNARY_ORBITS",fixture=fixture,
                          orbits=sum(x["orbits"] for x in rows),largest_raw=rows[-1]["raw_states"])))
