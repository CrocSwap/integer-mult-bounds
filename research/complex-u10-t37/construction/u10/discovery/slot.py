import sys,itertools,copy,collections
sys.path.insert(0,'/tmp/don')
from mover import *
from frameopt import optimise
from fractions import Fraction as Fr
V=112
def slot_info(w,ci):
    B=w['B'];g=B[ci];E,X=g[1],g[2]
    reads=[(i,B[i][1],B[i][2],Fr(B[i][3],B[i][4])) for i in range(ci+1,len(B)) if B[i][0]=='add' and istgt(B[i][1]) and B[i][2] in (E,X)]
    pre=[(i,B[i][1],Fr(B[i][3],B[i][4])) for i in range(ci) if B[i][0]=='add' and istgt(B[i][1]) and B[i][2]==E]
    return E,X,reads,pre
def build(w,ci,assign,dons,restore='C'):
    """assign: dict read_index->src (E or X); dons: list of (read_index, H, iH) meaning read is delivered via H += src before H's read."""
    B=w['B'];E,X,reads,pre=slot_info(w,ci)
    hf=set(map(int,w['helper_final']))
    clean=(str(E) in w['start_extra']) and not any(j<ci and B[j][1]==E for j in range(len(B)))
    priorY=any(j<ci and B[j][1]==E for j in range(len(B)))
    ecoef=collections.Counter()
    for (i,t,s,c) in reads:
        if assign[i]==E: ecoef[t]+=c
    if clean:
        pos0=pre[0][0] if pre else ci
        newpre=[['add',t,E,(-c).numerator,(-c).denominator,[]] for t,c in sorted(ecoef.items()) if c!=0]
        oldpre={p[0] for p in pre}
    else:
        pos0=ci; oldpre=set()
        if str(E) in w['start_extra'] or priorY:
            e0=collections.Counter()
            for (i,t,s,c) in reads:
                if s==E: e0[t]+=c
            dl={t:ecoef[t]-e0[t] for t in set(ecoef)|set(e0)}
            newpre=[['add',t,E,(-c).numerator,(-c).denominator,[]] for t,c in sorted(dl.items()) if c!=0]
        else: newpre=[]
    if any(x[4]&(x[4]-1) for x in newpre): return None
    ins=collections.defaultdict(list)
    ins[pos0]+=newpre
    dset={d[0]:d for d in dons}
    for (i,H,iH) in dons:
        src=assign[i]
        lw=[j for j,g in enumerate(B) if j<iH and g[1] in (H,src)]
        p=max(max(lw)+1 if lw else 0,ci+1)
        r=Fr(B[i][3],B[i][4])/Fr(B[iH][3],B[iH][4])
        ins[p].append(['add',H,src,r.numerator,r.denominator,[]])
    nb=[]
    for j,g in enumerate(B):
        nb.extend(copy.deepcopy(ins.get(j,[])))
        if j in oldpre: continue
        if j in dset: continue
        g=list(g)
        if j in assign: g=g[:2]+[assign[j]]+g[3:]
        nb.append(g)
    w=copy.deepcopy(w);w['B']=nb
    for (i,H,iH) in dons:
        src=assign[i]
        r=Fr(B[i][3],B[i][4])/Fr(B[iH][3],B[iH][4])
        if H in hf or src in hf:
            w['cleanup'].append(['add',H,src,-r.numerator,r.denominator,FULLF])
            w['early_cleanup'].insert(0,[len(w['cleanup'])-1,[]])
        else:
            w['cleanup'].insert(0,['add',H,src,-r.numerator,r.denominator,FULLF])
            w['early_cleanup']=[[k+1,U] for k,U in w['early_cleanup']]
    return w
def holders(w,ci,i,src_set):
    """holder reads by same target t with same coefficient, H not read by others after, not written after."""
    B=w['B'];t=B[i][1];c=(B[i][3],B[i][4])
    out=[]
    for j,g in enumerate(B):
        if j<=ci or g[0]!='add' or g[1]!=t or istgt(g[2]) or g[2] in src_set: continue
        r=Fr(c[0],c[1])/Fr(g[3],g[4])
        if r.denominator&(r.denominator-1) or abs(r.numerator)>2: continue
        H=g[2]
        if any(k>j and B[k][0]=='add' and B[k][2]==H for k in range(len(B))): continue
        if any(k>j and B[k][1]==H for k in range(len(B))): continue
        out.append((H,j))
    return out
