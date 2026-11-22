"""Independent source-driven versus rectangle-driven ragged halo gather."""
from itertools import product
from collections import defaultdict
from pathlib import Path
import json,math
HERE=Path(__file__).resolve().parent
def points(ranges):return product(*(range(a,b) for a,b in ranges))
def rectangles(S,N,L):
    Q=[(s+N-1)//N for s in S];g=len(S)
    for tile in product(*(range(q) for q in Q)):
        sizes=[min(N,s-t*N) for s,t in zip(S,tile)]
        if min(sizes)<N:
            yield ('ragged',tile),[(-L,r+L) for r in sizes],[(0,r) for r in sizes]
        else:
            for j in range(g):
                for side in (0,1):
                    source=[(0,N) if i<j else ((-L,2*L) if side==0 else (N-2*L,N+L)) if i==j else (-L,N+L) for i in range(g)]
                    target=[(L,N-L) if i<j else ((0,L) if side==0 else (N-L,N)) if i==j else (0,N) for i in range(g)]
                    yield ('face',tile,j,side),source,target
def check(S,N,L):
    g=len(S);Q=[(s+N-1)//N for s in S]
    data={x:1+sum((i+1)*(a+1)**2 for i,a in enumerate(x)) for x in points([(0,s) for s in S])}
    expected={};rects=list(rectangles(S,N,L));bytile=defaultdict(list)
    for tag,src,dst in rects:
        tile=tag[1];bytile[tile].append((tag,src,dst))
        for y in points(src):
            x=tuple((t*N+a)%s for t,a,s in zip(tile,y,S));expected[tag,y]=data[x]
    actual={};candidate_pairs=0
    for x,value in data.items():
        options=[]
        for i,a in enumerate(x):
            opts=[]
            for t in range(Q[i]):
                r=min(N,S[i]-t*N)
                for shift in (-S[i],0,S[i]):
                    y=a-t*N+shift
                    if -L<=y<r+L:opts.append((t,y))
            assert len(opts)<=3
            options.append(opts)
        for choice in product(*options):
            candidate_pairs+=1;tile=tuple(t for t,y in choice);y=tuple(y for t,y in choice)
            for tag,src,dst in bytile[tile]:
                if all(a<=z<b for z,(a,b) in zip(y,src)):
                    assert (tag,y) not in actual;actual[tag,y]=value
    assert actual==expected
    kernels=[[2+i,-1,3+i] for i in range(g)]
    offsets=list(product(range(-L,L+1),repeat=g));assert L==1
    weights={z:math.prod(kernels[i][a+L] for i,a in enumerate(z)) for z in offsets}
    direct={x:sum(w*data[tuple((a-b)%s for a,b,s in zip(x,z,S))] for z,w in weights.items()) for x in data}
    corrected={}
    for tag,src,dst in rects:
        tile=tag[1]
        for y in points(dst):
            x=tuple(t*N+a for t,a in zip(tile,y))
            val=sum(w*actual[tag,tuple(a-b for a,b in zip(y,z))] for z,w in weights.items())
            assert val==direct[x] and x not in corrected;corrected[x]=val
    # The remaining coordinates are interiors of complete regular tiles.
    for x in data:
        tile=tuple(a//N for a in x);y=tuple(a%N for a in x)
        regular=all(min(N,s-t*N)==N for s,t in zip(S,tile))
        if regular and all(L<=a<N-L for a in y):assert x not in corrected
        else:assert x in corrected
    return dict(S=S,N=N,L=L,g=g,input_records=len(data),halo_records=len(actual),
        full_halo_candidate_pairs=candidate_pairs,corrected_outputs=len(corrected),
        source_and_rectangle_gathers_identical=True,true_period_tensor_convolution_checked=True)
def main():
    out=dict(status='PASS_RAGGED_TRUE_PERIOD_SPARSE_HALO',cases=[check([19,22],8,1),check([17,18,20],8,1)])
    (HERE/'RAGGED-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
