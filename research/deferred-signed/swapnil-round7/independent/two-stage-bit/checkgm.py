"""Independent exact check of a global side DAG (no use of the generator's support table):
recompute every active node's support from the inputs, check disjoint operands, topological order,
a common point on every node, every designated output equal to {S : c in S, S cap (T-c) empty},
all 3v (centre, target) outputs present. Prints R = active additions + outputs."""
import sys
from itertools import combinations
import gmside, orders
def check(h, order):
    trip,args,outputs=gmside.build(h,order); v=len(trip)
    assert len(outputs)==3*v and all(c in T for c,T in outputs)
    act=set(); st=list(outputs.values())
    while st:
        n=st.pop()
        if n in act: continue
        act.add(n)
        if args[n]: st.extend(args[n])
    sup={}
    for n in sorted(act):
        if args[n] is None:
            assert 1<=n<=v; sup[n]=1<<(n-1); continue
        x,y=args[n]; assert x<n and y<n and x in sup and y in sup
        assert sup[x]&sup[y]==0, 'overlap'
        sup[n]=sup[x]|sup[y]
    Mp=[sum(1<<i for i,t in enumerate(trip) if p in t) for p in range(h)]
    for n in act:
        assert any(sup[n]&~Mp[p]==0 for p in range(h)), 'no common point'
    for (c,T),n in outputs.items():
        A,B=[p for p in T if p!=c]
        assert sup[n]==Mp[c]&~Mp[A]&~Mp[B], 'wrong output'
    adds=sum(1 for n in act if args[n] is not None)
    return adds+3*v, adds
if __name__=='__main__':
    o=getattr(orders,sys.argv[1])
    for h in map(int,sys.argv[2:]): print(h, *check(h,o), 'OK', flush=True)
