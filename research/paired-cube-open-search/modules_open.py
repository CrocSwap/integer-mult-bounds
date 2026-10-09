"""All-but-one module variants in PR161's module format: disjoint additions, roots[i] = sum of all inputs except i.

Copyright 2026 Joel Pulikkan (GamingPuzzled). Apache-2.0. Prepared with Anthropic Claude assistance.
PR161's paired_cube.modules.all_but_one(n) is the balanced-tree variant; cyclic(n) builds every root from
cyclic intervals and shares their prefixes, which reduces the module's node count."""
def _mk(n,build):
    args=[None]*n;support=[1<<i for i in range(n)];by={s:i for i,s in enumerate(support)}
    def add(a,b):
        if a is None:return b
        if b is None:return a
        assert not support[a]&support[b]
        s=support[a]|support[b]
        if s not in by:by[s]=len(args);args.append([a,b]);support.append(s)
        return by[s]
    roots=build(n,add)
    full=(1<<n)-1;assert all(support[r]==full^(1<<i) for i,r in enumerate(roots))
    active=set(range(n));st=list(roots)
    while st:
        x=st.pop()
        if x in active:continue
        active.add(x)
        if args[x] is not None:st.extend(args[x])
    ids=sorted(active);ren={x:i for i,x in enumerate(ids)}
    return dict(kind='all_but_one',n=n,input_count=n,input_labels=list(range(n)),output_labels=list(range(n)),
        args=[None if args[x] is None else [ren[y] for y in args[x]] for x in ids],roots=[ren[x] for x in roots])
def prefix_suffix(n):
    def b(n,add):
        pre=[None];suf=[None]*(n+1)
        for i in range(n):pre.append(add(pre[-1],i))
        for i in range(n-1,-1,-1):suf[i]=add(i,suf[i+1])
        return [add(pre[i],suf[i+1]) for i in range(n)]
    return _mk(n,b)
def cyclic(n):
    def b(n,add):
        iv=lambda a,k:sum(1<<((a+t)%n) for t in range(k))
        node={1<<i:i for i in range(n)}
        def get(a,k):
            key=iv(a,k)
            if key not in node:node[key]=add(get(a,k-1),(a+k-1)%n)
            return node[key]
        return [get((i+1)%n,n-1) for i in range(n)]
    return _mk(n,b)
def tree_split(n,frac):
    def b(n,add):
        def tree(lo,hi):
            if hi-lo==1:return (lo,None,None)
            mid=lo+max(1,min(hi-lo-1,int(round((hi-lo)*frac))));L=tree(lo,mid);R=tree(mid,hi)
            return (add(L[0],R[0]),L,R)
        T=tree(0,n);roots=[None]*n
        def walk(t,out):
            x,L,R=t
            if L is None:roots[x]=out;return
            walk(L,add(out,R[0]));walk(R,add(out,L[0]))
        walk(T,None);return roots
    return _mk(n,b)
