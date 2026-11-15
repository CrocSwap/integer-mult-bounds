def clean(chs):
    o=[chs[0]]
    for c in chs[1:]:
        if c!=o[-1]: o.append(c)
    return o
def okpath(M,o): return all(M.sp[a]&~M.sp[b]==0 and M.sp[a]!=M.sp[b] for a,b in zip(o,o[1:]))
def newpath(M,r,k,e,F):
    nd=M.nodes[r]; chs=[x['c'] for x in nd]; ops=nd[k]['ops']; L=len(chs)
    if len(ops)==1:
        if k==0: out=chs[:1]+[F]+chs[1:]
        elif k==L-1: out=chs[:-1]+[F]+chs[-1:]
        else: out=chs[:k]+[F]+chs[k+1:]
    elif ops[0]==e: out=chs[:k]+[F]+chs[k:]
    elif ops[-1]==e: out=chs[:k+1]+[F]+chs[k+1:]
    else: return None
    out=clean(out)
    return out if okpath(M,out) else None
