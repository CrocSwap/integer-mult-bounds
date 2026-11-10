"""Enumerate literal vector sets and GL actions, independently of the formula.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product


def universe(n,q):
    vec=list(product(range(q),repeat=n));ids={x:i for i,x in enumerate(vec)}
    def plus(a,b):
        return a^b if q==4 else (a+b)%q
    def times(a,b):
        if q!=4:
            return a*b%q
        z=0
        while b:
            if b&1:z^=a
            b>>=1;a<<=1
            if a&4:a^=7
        return z
    add=[[ids[tuple(plus(a,b) for a,b in zip(x,y))] for y in vec] for x in vec]
    scale=[[ids[tuple(times(c,a) for a in x)] for x in vec] for c in range(q)]
    zero=ids[(0,)*n];unit=[ids[tuple(int(i==j) for j in range(n))] for i in range(n)]
    def span(basis):
        s={zero}
        for v in basis:
            s={add[x][scale[c][v]] for x in s for c in range(q)}
        return frozenset(s)
    spaces={frozenset([zero]):()};queue=[frozenset([zero])]
    for s in queue:
        for v in range(q**n):
            if v not in s:
                b=spaces[s]+(v,);t=span(b)
                if t not in spaces:spaces[t]=b;queue.append(t)
    sets=sorted(spaces,key=lambda x:(len(x),sorted(x)))
    basis=[spaces[x] for x in sets];index={x:i for i,x in enumerate(sets)}
    masks=[sum(1<<v for v in s) for s in sets];maskid={m:i for i,m in enumerate(masks)}
    dims=[len(b) for b in basis];S=len(sets)
    meet=[[maskid[a&b] for b in masks] for a in masks]
    join=[[index[span(a+b)] for b in basis] for a in basis]
    contain=[[i for i,m in enumerate(masks) if m&x==x] for x in masks]
    def gl(u):
        def rec(cols):
            if len(cols)==n:
                image=[]
                for x in vec:
                    v=zero
                    for c,col in zip(x,cols):v=add[v][scale[c][col]]
                    image.append(v)
                yield [index[frozenset(image[v] for v in s)] for s in sets]
            else:
                used=span(cols)
                for v in range(q**n):
                    if v not in used:yield from rec(cols+(v,))
        yield from rec(tuple(unit[:u]))
    return dict(n=n,q=q,sets=sets,basis=basis,vec=vec,unit=unit,span=span,index=index,masks=masks,
                dims=dims,S=S,meet=meet,join=join,contain=contain,gl=gl)


def counts(space,u):
    S=space['S'];out=[0]*(S**4);matrices=0
    for images in space['gl'](u):
        matrices+=1
        for a in range(S):
            ca=space['contain'][images[a]]
            for b in range(S):
                db=space['contain'][images[b]];base=(a*S+b)*S*S
                for c in ca:
                    for d in db:out[base+c*S+d]+=1
    return out,matrices


def normalized_profile(space,u,a,b,c,d):
    meet,join,dim=space['meet'],space['join'],space['dims']
    U=space['index'][space['span'](space['unit'][:u])]
    ua,ub,u0=meet[U][a],meet[U][b],meet[U][join[a][b]]
    z=join[meet[U][c]][meet[U][d]]
    contained=lambda x,y:meet[x][y]==x
    ok=contained(ua,c) and contained(ub,d) and contained(u0,join[c][d])
    values=[space['n'],u,dim[a]-dim[ua],dim[b]-dim[ub],dim[join[a][b]]-dim[u0],
            dim[c]-dim[meet[U][c]],dim[d]-dim[meet[U][d]],dim[join[c][d]]-dim[meet[U][join[c][d]]],
            dim[meet[a][b]]+dim[meet[u0][z]]-dim[ua]-dim[ub],
            dim[meet[c][d]]-dim[meet[U][meet[c][d]]],
            dim[meet[U][c]],dim[meet[U][d]],dim[meet[U][meet[c][d]]]]
    return values,ok
