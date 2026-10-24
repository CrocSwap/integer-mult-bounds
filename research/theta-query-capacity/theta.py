"""Exact finite theta capacity constructor. JoyboyBrian; Apache-2.0."""
NAMES=('u','v','a','b','c','d','e')
EDGES=((0,2),(1,2),(0,3),(3,4),(1,4),(0,5),(5,6),(1,6))
NEIGHBORS=tuple(tuple(j for j in range(7) if tuple(sorted((i,j))) in {tuple(sorted(e)) for e in EDGES}) for i in range(7))
def need(ok,message):
    if not ok:raise ValueError(message)
def widths(d):
    need(type(d) in (list,tuple) and len(d)==7,'seven widths')
    need(all(type(x) is int and x>=0 for x in d),'nonnegative integer widths')
    return tuple(d)
def options(w):
    i=next(i for i,x in enumerate(w) if x)
    a=list(w);a[i]-=1
    out=[(tuple(a),None)]
    for j in NEIGHBORS[i]:
        if w[j]:
            b=a.copy();b[j]-=1;out.append((tuple(b),tuple(sorted((i,j)))))
    return out

def construct(d):
    d=widths(d);zero=(0,)*7;memo={zero:(0,None)};stack=[d]
    while stack:
        w=stack[-1]
        if w in memo:stack.pop();continue
        choices=options(w)
        missing=next((child for child,e in choices if child not in memo),None)
        if missing is not None:stack.append(missing);continue
        scored=[(memo[child][0]+int(e is not None),child,e)for child,e in choices]
        best=max(scored,key=lambda x:x[0]);memo[w]=(best[0],(best[1],best[2]));stack.pop()
    counts={tuple(sorted(e)):0 for e in EDGES};private=[0]*7;w=d
    while any(w):
        child,e=memo[w][1]
        if e is None:private[next(i for i in range(7)if w[i]!=child[i])]+=1
        else:counts[e]+=1
        w=child
    result={'widths':list(d),'edges':[counts[tuple(sorted(e))]for e in EDGES],
            'private':private,'rank':sum(d)-memo[d][0]}
    validate(result)
    return result

def validate(recipe):
    d=widths(recipe['widths']);x=recipe['edges'];p=recipe['private']
    need(type(x) is list and len(x)==8 and type(p) is list and len(p)==7,'recipe sizes')
    need(all(type(v) is int and v>=0 for v in x+p),'integer channel counts')
    used=p.copy()
    for (i,j),v in zip(EDGES,x):used[i]+=v;used[j]+=v
    need(tuple(used)==d,'whole payload coverage')
    need(type(recipe['rank']) is int and recipe['rank']==sum(x)+sum(p),'whole channel invoice')

def matrix(recipe):
    validate(recipe);d=recipe['widths'];S=sum(d);M=[[0]*S for _ in range(S)]
    off=[sum(d[:i])for i in range(7)];cursor=off.copy()
    for (i,j),x in zip(EDGES,recipe['edges']):
        for _ in range(x):
            a,b=cursor[i],cursor[j];cursor[i]+=1;cursor[j]+=1
            for r in (a,b):
                for c in (a,b):M[r][c]=1
    for i,p in enumerate(recipe['private']):
        for _ in range(p):a=cursor[i];cursor[i]+=1;M[a][a]=1
    return M
