"""Independent column-span audit of the proof's actual intermediate inequalities.

JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0.
"""
def need(ok,message):
    if not ok:raise ValueError(message)
def dimension(columns,q):
    basis={}
    for column in columns:
        v=[x%q for x in column]
        for i in range(len(v)):
            if not v[i]:continue
            if i in basis:
                factor=v[i];v=[(x-factor*y)%q for x,y in zip(v,basis[i])]
            else:
                scale=pow(v[i],-1,q);basis[i]=[x*scale%q for x in v];break
    return len(basis)
def audit(a,d,q):
    n=len(d);k=(n-1)//2;s=sum(d);offset=[sum(d[:i])for i in range(n)]
    columns=[list(column)for column in zip(*a)]
    def chosen(vertices):
        return [columns[c]for i in vertices for c in range(offset[i],offset[i]+d[i])]
    r=dimension(columns,q)
    need(all(dimension(chosen([i]),q)==d[i]for i in range(n)),'injective payload column images')
    intersections=[d[i]+d[(i+1)%n]-dimension(chosen([i,(i+1)%n]),q)for i in range(n)]
    need(all(intersections[i-1]+intersections[i]<=d[i]for i in range(n)),'two incident intersections are disjoint')
    cuts=[]
    for i in range(n):
        vertices=[i,(i+1)%n]+[(i+j)%n for j in range(3,2*k,2)]
        rhs=sum(d[j]for j in vertices)-intersections[i]
        need(dimension(chosen(vertices),q)==rhs and rhs<=r,'actual one-edge-plus-isolates dimension')
        cuts.append(rhs)
    need(n*r>=(k+1)*s-sum(intersections) and 2*sum(intersections)<=s,
         'summed rotated rank inequality')
    return dict(length=n,field=q,total=s,rank=r,intersections=intersections,cuts=cuts)
