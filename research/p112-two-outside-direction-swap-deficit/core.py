"""Exact separator/list partition. JoyboyBrian; OpenAI Codex assistance."""
from collections import deque

def require(ok, message):
    if not ok:
        raise ValueError(message)

def partition(points, edges, separators, prime=None):
    n=len(points)
    require(len(separators)==n, 'separator coverage')
    mod=lambda x: x if prime is None else x%prime
    dot=lambda x,y: mod(sum(a*b for a,b in zip(x,y)))
    adj=[set() for _ in points]
    for x in points:
        require(len(x)==2 and any(mod(z)!=0 for z in x), 'nonzero point')
    require(len(edges)==len(set(edges)), 'duplicate edges')
    for a,b in edges:
        require(0<=a<b<n, 'simple ordered edge')
        adj[a].add(b);adj[b].add(a)
    for i,f in enumerate(separators):
        require(len(f)==2 and dot(f,points[i])!=0, 'own separator')
        require(all(dot(f,points[j])==0 for j in adj[i]), 'neighbor separator')
    colors=[None]*n
    for start in range(n):
        if colors[start] is not None: continue
        sides={start:0};q=deque([start])
        while q:
            i=q.popleft()
            for j in adj[i]:
                if j not in sides:
                    sides[j]=1-sides[i];q.append(j)
                require(sides[j]!=sides[i], 'odd cycle')
        flips=[f for f in (0,1) if all(mod(points[i][s^f])!=0 for i,s in sides.items())]
        require(flips, 'membership lists')
        for i,s in sides.items(): colors[i]=s^flips[0]
    require(all(colors[a]!=colors[b] for a,b in edges), 'color edge')
    require(all(mod(points[i][c])!=0 for i,c in enumerate(colors)), 'color membership')
    return colors

def binary_rank(rows):
    piv={}
    for x in rows:
        while x:
            b=x.bit_length()-1
            if b in piv:x^=piv[b]
            else:piv[b]=x;break
    return len(piv)
