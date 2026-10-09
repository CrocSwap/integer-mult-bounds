"""Mixed-gap all-but-one module for the p = 12 bit word.

Copyright 2026 Joel Pulikkan (GamingPuzzled). Apache-2.0. Prepared with Anthropic Claude assistance.
eumemic's PR168 nested prefix builds prefixes p_{k+1} = p_k + x_k and suffixes s_k = x_k + s_{k+1}, and every middle
output y_j (all inputs except x_j) in the left-gap form L: p_{j-1} + (x_{j-1} + s_{j+1}).  The right-gap form
R: (p_j + x_{j+1}) + s_{j+2} is the mirror image.  PATTERN chooses the form for j = 1..n-2; all L is PR168's module.
Unused prefix/suffix nodes are pruned, and the all-but-one contract is checked on disjoint supports.
"""
PATTERN = 'RLLLRRRL'


def lr_module(n, forms):
    """All-but-one with nested prefix p and suffix s; middle output j uses form L: p_{j-1}+(x_{j-1}+s_{j+1})
    or R: (p_j+x_{j+1})+s_{j+2}.  forms[j-1] for j=1..n-2.  Dead nodes pruned; contract-checked."""
    args=[None]*n
    def add(a,b): args.append([a,b]); return len(args)-1
    pre={1:0}
    for k in range(1,n-1): pre[k+1]=add(pre[k],k)
    suf={n-1:n-1}
    for k in range(n-2,0,-1): suf[k]=add(k,suf[k+1])
    roots=[None]*n; roots[0],roots[n-1]=suf[1],pre[n-1]
    for j in range(1,n-1):
        f=forms[j-1]
        if f=='L': roots[j]=add(0,suf[2]) if j==1 else add(pre[j-1],add(j-1,suf[j+1]))
        else: roots[j]=add(pre[j],n-1) if j==n-2 else add(add(pre[j],j+1),suf[j+2])
    support=[]
    for x,a in enumerate(args):
        support.append(1<<x if a is None else support[a[0]]|support[a[1]])
        if a is not None: assert not support[a[0]]&support[a[1]]
    live=set(range(n)); st=list(roots)
    while st:
        x=st.pop()
        if x in live: continue
        live.add(x)
        if args[x] is not None: st.extend(args[x])
    ids=sorted(live); ren={x:i for i,x in enumerate(ids)}
    args=[None if args[x] is None else [ren[y] for y in args[x]] for x in ids]; roots=[ren[r] for r in roots]
    full=(1<<n)-1; sup=[]
    for a in args: sup.append(None)
    for x,a in enumerate(args): sup[x]=1<<x if a is None else sup[a[0]]|sup[a[1]]
    assert all(sup[r]==full^(1<<i) for i,r in enumerate(roots))
    return dict(input_count=n,args=args,roots=roots)


def module(n):
    assert len(PATTERN) == n - 2
    return lr_module(n, PATTERN)
