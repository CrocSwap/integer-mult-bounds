def natural(h,c): return [j for j in range(h) if j!=c]
def gmatch_end(h,c):
    # global pairs (0,1),(2,3)..; h odd -> last point z=h-1 singleton. centre's partner moved next to z at end
    z=h-1
    if c==z: return list(range(h-1))
    cs=c^1
    return [j for j in range(h-1) if j not in (c,cs)]+[z,cs]
def gmatch_front(h,c):
    z=h-1
    if c==z: return list(range(h-1))
    cs=c^1
    return [z,cs]+[j for j in range(h-1) if j not in (c,cs)]
def gmatch_mid(h,c):
    z=h-1
    if c==z: return list(range(h-1))
    cs=c^1; r=[j for j in range(h-1) if j not in (c,cs)]; m=(len(r)//4)*2
    return r[:m]+[z,cs]+r[m:]
def rot(h,c): return [(c+k)%h for k in range(1,h)]
def gm(h,c):
    # global matching (0,1),(2,3),...; odd h: z=h-1 joins the centre's partner at the end; even h: partner alone at end
    if h%2:
        z=h-1
        if c==z: return list(range(h-1))
        cs=c^1; return [j for j in range(h-1) if j not in (c,cs)]+[z,cs]
    cs=c^1; return [j for j in range(h) if j not in (c,cs)]+[cs]
def gmf(h,c):
    if h%2:
        z=h-1
        if c==z: return list(range(h-1))
        cs=c^1; return [z,cs]+[j for j in range(h-1) if j not in (c,cs)]
    cs=c^1; return [cs]+[j for j in range(h) if j not in (c,cs)]
def gmm(h,c):
    r=gm(h,c); 
    if h%2 and c==h-1: return r
    k=2 if h%2 else 1; sp=r[-k:]; r=r[:-k]; m=(len(r)//4)*2
    return r[:m]+sp+r[m:]
def gmrev(h,c):
    # global matching but pairs listed in reverse order (tests order dependence)
    r=gm(h,c); k=2 if h%2 else 1
    if h%2 and c==h-1: return r[::-1]
    body=r[:-k]; pairs=[body[i:i+2] for i in range(0,len(body),2)][::-1]
    return [x for p in pairs for x in p]+r[-k:]
