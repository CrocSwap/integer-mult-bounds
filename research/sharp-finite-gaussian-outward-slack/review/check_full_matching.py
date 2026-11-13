"""Independent full-vertex matching and alternating Hall cut; no orbit optimizer."""
from collections import Counter, deque
from itertools import product, permutations
from math import isqrt, prod
import json, sys

H = ((1,1,1,1),(1,-1,1,-1),(1,1,-1,-1),(1,-1,-1,1))
Q = 1 << 128
def need(ok, why):
    if not ok: raise ValueError(why)
def n2(v): return sum(t*t for t in v)
def root_interval(n):
    a=isqrt(n*Q*Q)
    return a,a+int(a*a!=n*Q*Q)
def gap_interval(a,b):
    la,ua=root_interval(a);lb,ub=root_interval(b)
    return la-ub,ua-lb
BLO,BHI=gap_interval(21,19)
def strict(a,b):
    if a<=b:return True
    if (a,b)==(21,19):return False
    lo,hi=gap_interval(a,b)
    if hi<BLO:return True
    if lo>BHI:return False
    raise ValueError(('unseparated exact radical gaps',a,b))
def candidates(x):
    hx=tuple(sum(a*b for a,b in zip(row,x)) for row in H)
    need(len({z%2 for z in hx})==1,'common Hadamard parity')
    if hx[0]%2:
        for bits in product((0,1),repeat=4):
            yield tuple(z//2+t for z,t in zip(hx,bits))
    else:
        c=tuple(z//2 for z in hx);yield c
        for i in range(4):
            for sign in (-1,1):
                y=list(c);y[i]+=sign;yield tuple(y)
def maximum_matching(adj):
    left=[None]*len(adj);right={};rounds=0
    while True:
        dist=[-1]*len(adj);todo=deque()
        for x,y in enumerate(left):
            if y is None:dist[x]=0;todo.append(x)
        end=False
        while todo:
            x=todo.popleft()
            for y in adj[x]:
                z=right.get(y)
                if z is None:end=True
                elif dist[z]<0:dist[z]=dist[x]+1;todo.append(z)
        if not end:break
        def augment(x):
            for y in adj[x]:
                z=right.get(y)
                if z is None or (dist[z]==dist[x]+1 and augment(z)):
                    left[x]=y;right[y]=x;return True
            dist[x]=-1;return False
        gained=sum(augment(x) for x,y in enumerate(left) if y is None)
        need(gained>0,'augmenting BFS progress');rounds+=1
    need(len(right)==sum(y is not None for y in left),'matching cardinality')
    need(all(left[x]==y and y in adj[x] for y,x in right.items()),'matching edges')
    lseen={x for x,y in enumerate(left) if y is None};rseen=set();todo=deque(lseen)
    while todo:
        x=todo.popleft()
        for y in adj[x]:
            if y in rseen:continue
            rseen.add(y);need(y in right,'augmenting path remains')
            z=right[y]
            if z not in lseen:lseen.add(z);todo.append(z)
    need(rseen=={y for x in lseen for y in adj[x]},'complete Hall neighborhood')
    need(len(lseen)-len(rseen)==len(adj)-len(right),'maximal Hall deficiency')
    return left,lseen,rseen,rounds
def dtype(x):
    return tuple(sorted(map(abs,x))), (0 if 0 in x else int(prod(x)<0))
def main():
    pairs=[(a,b) for a in range(-5,6) for b in range(-5,6) if a*a+b*b<=25]
    xs=sorted((a,b,c,d) for a,b in pairs for c,d in pairs if a*a+b*b+c*c+d*d<=25)
    need(len(xs)==3121,'complete ball count')
    all_edges=[tuple(candidates(x)) for x in xs]
    need(sum(map(len,all_edges))==39681,'complete error-one edge count')
    for x,ys in zip(xs,all_edges):
        hx=[sum(a*b for a,b in zip(row,x)) for row in H]
        need(all(sum((2*a-b)**2 for a,b in zip(y,hx))<=4 for y in ys),'exact edge error')
    adj=[tuple(y for y in ys if strict(n2(y),n2(x))) for x,ys in zip(xs,all_edges)]
    matching,ls,ns,rounds=maximum_matching(adj);ts={xs[i] for i in ls}
    group=[]
    for perm in permutations(range(4)):
        for signs in product((-1,1),repeat=4):
            A=[[signs[i]*int(j==perm[i]) for j in range(4)] for i in range(4)]
            num=[[sum(H[i][a]*A[a][b]*H[j][b] for a in range(4) for b in range(4)) for j in range(4)] for i in range(4)]
            if any(z%4 for row in num for z in row):continue
            B=[[z//4 for z in row] for row in num]
            if not (all(sum(map(abs,row))==1 for row in B) and all(sum(abs(B[i][j]) for i in range(4))==1 for j in range(4))):continue
            group.append((perm,signs,B))
            need({tuple(signs[i]*x[perm[i]] for i in range(4)) for x in ts}==ts,'input cut symmetry')
            need({tuple(sum(B[i][j]*y[j] for j in range(4)) for i in range(4)) for y in ns}==ns,'output cut symmetry')
    need(len(group)==192,'paired graph group count')
    need(all(prod(s)==1 for _,s,_ in group),'group is even sign changes')
    counts=Counter(dtype(x) for x in xs);tc=Counter(dtype(x) for x in ts)
    need(all(v==counts[k] for k,v in tc.items()),'complete W(D4) input orbits')
    output_universe={y for ys in all_edges for y in ys};oc=Counter(dtype(y) for y in output_universe);nc=Counter(dtype(y) for y in ns)
    need(all(v==oc[k] for k,v in nc.items()),'complete W(D4) output orbits')
    n1={x for x in xs if n2(x)<=19 and tuple(sorted(map(abs,x))) not in ((0,0,3,3),(0,1,3,3))}
    extra={x for x in xs if tuple(sorted(map(abs,x)))==(2,2,2,3) and prod(x)>0}
    t1=n1|extra
    actual={y for x in t1 for y in candidates(x) if strict(n2(y),n2(x))}
    need(len(n1)==1777 and len(extra)==32 and len(t1)==1809 and actual==n1,'independent closed witness equality')
    wrong_ties={y for x in t1 for y in candidates(x) if strict(n2(y),n2(x)) or (n2(y),n2(x))==(21,19)}
    need(wrong_ties-n1,'wrong inclusive tie breaks compact output container')
    inclusive=[tuple(y for y in ys if strict(n2(y),n2(x)) or (n2(y),n2(x))==(21,19)) for x,ys in zip(xs,all_edges)]
    im,il,ir,_=maximum_matching(inclusive)
    need(all(y is not None for y in im) and not il and not ir,'inclusive threshold permits full matching')
    out={'marker':'PASS_FULL_GRAPH_ALTERNATING_HALL_CUT','inputs':len(xs),'error_one_edges':sum(map(len,all_edges)),
         'strict_edges':sum(map(len,adj)),'strict_maximum_matching':sum(y is not None for y in matching),
         'strict_cut_inputs':len(ts),'strict_cut_outputs':len(ns),'strict_cut_deficiency':len(ts)-len(ns),
         'closed_witness':{'inputs':len(t1),'complete_neighbors':len(actual),'deficiency':len(t1)-len(actual),'wrong_tie_extra_outputs':len(wrong_ties-n1)},
         'matching_rounds':rounds,'group_order':len(group),'group':'all coordinate permutations with an even number of sign changes',
         'input_orbits':[{'absolute_coordinates':k[0],'negative_product':k[1],'size':v} for k,v in sorted(tc.items())],
         'output_orbits':[{'absolute_coordinates':k[0],'negative_product':k[1],'size':v} for k,v in sorted(nc.items())],
         'strict_cut_input_points':sorted(ts),'strict_cut_output_points':sorted(ns),
         'negative_control':'including the 19-to-21 beta edges restores a complete matching',
         'method':'full vertex Hopcroft-Karp and alternating reachability; independent of compressed orbit min-cut'}
    if "--full-points" not in sys.argv:
        out={k:v for k,v in out.items() if not k.endswith("_points")}
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
