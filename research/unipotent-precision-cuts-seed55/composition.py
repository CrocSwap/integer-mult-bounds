"""Literal nested composition, with all child work and restoration charged.

This tests the recurrence. Its magnitudes are recomputed globally; the 53-leaf
cap certificate does not transfer to arbitrary recursive callers.
"""
from collections import Counter


def emit(tree, m, old, policies, path=(), source=2, work=None, root=True):
    if work is None:
        work = source+2*m
    if isinstance(tree,dict):
        return old.emit_node(tree,source,work,m,"carry")
    cuts = policies.get(path,list(range(1,len(tree)+1)))
    group, a = [], 0
    for b in cuts:
        for i in range(a,b):
            if i>a:
                group += old.power([(0,1)],1)
            group += emit(tree[i],m,old,policies,path+(i,),work,work+2*m,False)
        group += old.power(old.pairs_at(work,m),a-b)
        group += old.power([(0,1)],1-(b-a))
        a = b
    final_length = cuts[-1]-(cuts[-2] if len(cuts)>1 else 0)
    terminal = old.power([(0,1)],1-final_length)
    group = group[:len(group)-len(terminal)]
    copy = [("ADD",work+j,source+j,1,1) for j in range(2*m)]
    word = copy+group+old.inverse(copy)+old.inverse(group)
    if not root:
        word += old.power(old.pairs_at(source,m),1)
    return word


def invoice(tree,m,old,policies,path=(),root=True):
    if isinstance(tree,dict):
        return old.invoice(tree,m,"carry")
    counts = [invoice(c,m,old,policies,path+(i,),False) for i,c in enumerate(tree)]
    cuts = policies.get(path,list(range(1,len(tree)+1)))
    a, add, scale = 0, 0, 0
    for b in cuts:
        x,y = old.boundary_bill(b-a,m,"carry")
        add += x
        scale += y
        a = b
    last = cuts[-1]-(cuts[-2] if len(cuts)>1 else 0)
    x,y = old.power_bill(last-1)
    add -= x
    scale -= y
    return (2*sum(c[0] for c in counts)+4*m+2*add+(0 if root else m),
            2*sum(c[1] for c in counts)+2*scale)


def check(p,old):
    m=5
    tree=[old.fixture(17,m,seed=53+i) for i in range(3)]
    policies={(i,):[1,17] for i in range(3)}
    word=emit(tree,m,old,policies)
    eager=old.emit_echo(tree,2,12,m,"eager")
    dimension=2+(old.height(tree)+1)*2*m
    target=p.identity(dimension)
    for d,row in enumerate(old.total_reader(tree)):
        for j,value in enumerate(row):
            target[d][2+j]+=value
    results={}
    for label,ops in (("eager",eager),("fused_cuts",word)):
        matrix,fw,_=p.replay(ops,p.identity(dimension))
        inv,iv,_=p.replay(old.inverse(ops),p.identity(dimension))
        negative=p.identity(dimension)
        for d,row in enumerate(old.total_reader(tree)):
            for j,value in enumerate(row):
                negative[d][2+j]-=value
        p.require(matrix==target and inv==negative,"nested full dirty endpoint")
        counts=Counter(op[0] for op in ops)
        expected=invoice(tree,m,old,policies) if label=="fused_cuts" else old.invoice(tree,m,"eager",True)
        p.require((counts["ADD"],counts["SCALE"])==expected,"nested recurrence")
        results[label]={"add":counts["ADD"],"scale":counts["SCALE"],"operations":len(ops),
                        "forward_peak":fw,"inverse_peak":iv,"coordinates":dimension}
    results["scope"]="Composition and complete recurrence only; no inherited root cap or size-contraction claim."
    return results
