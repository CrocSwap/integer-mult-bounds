"""Global-matching side circuit ("gm"): Paureel's paired exclusion circuit on h-1 points (sidegen.Excl),
lifted to every centre c with the point order of orders.gm, sharing every node whose exact global support
(set of triples) is already built. Emits the global DAG: inputs 1..v (triples), args[k]=(x,y), outputs."""
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from itertools import combinations
import sidegen, orders
def build(h, order=orders.gm):
    loc=sidegen.Excl(h-1)
    trip=list(combinations(range(h),3)); idx={t:i+1 for i,t in enumerate(trip)}; v=len(trip)
    sup=[0]+[1<<i for i in range(v)]; args=[None]*(v+1); look={}; outputs={}
    for c in range(h):
        pts=order(h,c); mp={}
        for nd in sorted(loc.active):
            if loc.args[nd] is None:
                a,b=loc.inputs[nd-1]; mp[nd]=idx[tuple(sorted((c,pts[a],pts[b])))]; continue
            x,y=(mp[z] for z in loc.args[nd]); s=sup[x]|sup[y]; k=look.get(s)
            if k is None: k=len(sup); sup.append(s); args.append((x,y)); look[s]=k
            mp[nd]=k
        for (a,b),nd in loc.outputs.items(): outputs[c,tuple(sorted((c,pts[a],pts[b])))]=mp[nd]
    return trip, args, outputs

def roles(h, order=orders.gm):
    # side roles per invocation: active additions (reachable from an output) plus outputs
    trip, args, outputs = build(h, order)
    act = set(); st = list(outputs.values())
    while st:
        n = st.pop()
        if n in act: continue
        act.add(n)
        if args[n]: st.extend(args[n])
    adds = sum(args[n] is not None for n in act)
    return adds + len(outputs), adds, len(outputs)
