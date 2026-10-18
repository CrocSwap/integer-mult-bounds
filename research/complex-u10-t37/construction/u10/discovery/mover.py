import json,gzip,copy,collections
V=112
def L(p): return json.loads(gzip.decompress(open(p,'rb').read()))
def istgt(r): return V<=r<2*V
def regs(e): return [e[1]]+([e[2]] if e[0]=='add' else [])
def candidates(w):
    B=w['B']; hf=set(map(int,w['helper_final']))
    writes=collections.defaultdict(list); readsH=collections.defaultdict(list)
    for i,g in enumerate(B):
        writes[g[1]].append(i)
        if g[0]=='add': readsH[g[2]].append(i)
    tr=collections.defaultdict(list)
    for i,g in enumerate(B):
        if g[0]=='add' and istgt(g[1]) and not istgt(g[2]): tr[g[1]].append(i)
    out=[]
    for t,l in tr.items():
        for iV in l:
            for iH in l:
                if iV==iH: continue
                gV,gH=B[iV],B[iH]
                if (gV[3],gV[4])!=(gH[3],gH[4]): continue
                Vr,H=gV[2],gH[2]
                if Vr==H: continue
                lo,hi=min(iV,iH),max(iV,iH)
                if any(lo<j<hi for j in writes[Vr]): continue      # V constant between reads
                # H not read by anyone else after iH in B (else they'd see V) -- reads of H at j>iH by others
                if any(j>iH and j!=iH for j in readsH[H] if not (B[j][1]==t)): continue
                if any(j>iH for j in writes[H]): continue
                out.append((t,iV,iH,Vr,H))
    return out
FULLF=[256,128,64,32,16,8,4,2,1]
def basis(vs):
    b={}
    for x in vs:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))
def contained(a,b): return basis(list(a)+list(b))==basis(b)
def apply_move(w,mv,restore,pos='late'):
    t,iV,iH,Vr,H=mv
    w=copy.deepcopy(w);B=w['B']
    gV=B[iV]
    don=['add',H,Vr,1,1,[]]
    if pos=='late': p=iH
    else:
        lw=[j for j,g in enumerate(B) if j<iH and g[1] in (H,Vr)]
        p=(max(lw)+1) if lw else 0
    nb=[]
    for i,g in enumerate(B):
        if i==p: nb.append(don)
        if i==iV: continue
        nb.append(g)
    if restore=='B':
        k=nb.index(B[iH]) if False else None
        # insert right after the H read (which is now at shifted index)
        pos=[j for j,g in enumerate(nb) if g is B[iH]][0]
        nb.insert(pos+1,['add',H,Vr,-1,1,[]])
    w['B']=nb
    hf=set(map(int,w['helper_final']))
    if restore=='C':
        if H in hf or Vr in hf:
            w['cleanup'].append(['add',H,Vr,-1,1,FULLF])
            w['early_cleanup'].insert(0,[len(w['cleanup'])-1,[]])
        else:
            w['cleanup'].insert(0,['add',H,Vr,-1,1,FULLF])
            w['early_cleanup']=[[i+1,U] for i,U in w['early_cleanup']]
    return w
def fix_frames(w):
    v=112;R=w['report']['R'];n=2*v+R
    full=basis(FULLF)
    end=[full]*v+[basis([x for x in range(1,512) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
    for q,U in w['helper_final'].items(): end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(v+R)
    for q,U in w['start_extra'].items(): start[int(q)]=basis(U)
    cur=list(start)
    for e in w['A']:
        for q in regs(e): cur[q]=basis(e[-1])
    lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
    for q,U in zip(w['centers'],w['center_frames']): cur[q]=basis(U)
    for e in w['B']:
        U=basis(list(e[-1])+[x for q in regs(e) for x in cur[q]])
        e[-1]=list(U)
        for q in regs(e): cur[q]=U
    for j,(i,U) in enumerate(w['early_cleanup']):
        e=w['cleanup'][i]
        U=basis(list(U)+[x for q in regs(e) for x in cur[q]])
        w['early_cleanup'][j]=[i,list(U)]
        for q in regs(e): cur[q]=U
    ok=all(contained(cur[q],end[q]) for q in range(n))
    return ok
def profile(w):
    v=112;R=w['report']['R'];n=2*v+R
    full=basis(FULLF)
    end=[full]*v+[basis([x for x in range(1,512) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
    for q,U in w['helper_final'].items(): end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(v+R)
    for q,U in w['start_extra'].items(): start[int(q)]=basis(U)
    cur=list(start);paid=collections.Counter()
    def climb(q,U):
        U=basis(U)
        if not contained(cur[q],U): raise ValueError('nonmono')
        d=len(U)-len(cur[q])
        if d: paid[d]+=1
        cur[q]=U
    for e in w['A']:
        for q in regs(e): climb(q,e[-1])
    lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
    for q,U in zip(w['centers'],w['center_frames']):
        U=basis(U); served={lev.get(e[1]-v,()) for e in w['cut'] if e[2]==q}
        for T in sorted(served,key=lambda x:-len(x)):
            if T!=U: paid[len(U)-len(T)]+=1
            U=T
    for e in w['B']:
        for q in regs(e): climb(q,e[-1])
    early=w['early_cleanup']
    for i,U in early:
        for q in regs(w['cleanup'][i]): climb(q,U)
    for q in range(n): climb(q,end[q])
    return dict(sorted(paid.items()))
def least_frames(w):
    v=112;R=w['report']['R'];n=2*v+R
    start=[(p,) for p in w['ports']]+[()]*(v+R)
    for q,U in w['start_extra'].items(): start[int(q)]=basis(U)
    cur=list(start)
    for e in w['A']:
        U=basis([x for q in regs(e) for x in cur[q]]); e[-1]=list(U)
        for q in regs(e): cur[q]=U
    for q,U in zip(w['centers'],w['center_frames']): cur[q]=basis(U)
    lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
    for t in range(v):
        if not contained(cur[v+t],lev.get(t,())): return False
        cur[v+t]=lev.get(t,())
    for e in w['B']:
        U=basis([x for q in regs(e) for x in cur[q]]); e[-1]=list(U)
        for q in regs(e): cur[q]=U
    for j,(i,U) in enumerate(w['early_cleanup']):
        e=w['cleanup'][i]
        U=basis([x for q in regs(e) for x in cur[q]])
        w['early_cleanup'][j]=[i,list(U)]
        for q in regs(e): cur[q]=U
    return True
