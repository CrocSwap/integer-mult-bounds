"""Bit-side tuners for bitE8/1+mut words on the flat elementary-op form (one source per gate): single-op transport with
reframing (the mechanism of PR #541's preload60 and PR #548's trace20), Steinberg 3 -> 2 cancellation (PR #548),
frame-only reassignment, observable pruning (PR #542 / #548) and the least-frame assignment (PR #542).  D, B's
scatter, start and final are never changed; C is rebuilt as the literal reverse of the z-destination gates of A then B.
Frames are never changed for a retained total's last A gate (the COPY rank, hence the decoder constant, is fixed).
Used by apply.py --discover to rediscover the moves of moves.json from the base word.
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0."""
import bisect,copy,math,sys,json
from collections import Counter
import numpy as np
import wlib

PR=2147483647

def rank_mod(rows):
    rows=[[x%PR for x in r] for r in rows]
    rk=0;ncol=len(rows[0]) if rows else 0
    for c in range(ncol):
        p=next((i for i in range(rk,len(rows)) if rows[i][c]),None)
        if p is None: continue
        rows[rk],rows[p]=rows[p],rows[rk]
        inv=pow(rows[rk][c],PR-2,PR)
        rows[rk]=[x*inv%PR for x in rows[rk]]
        for i in range(len(rows)):
            if i!=rk and rows[i][c]:
                f=rows[i][c];rows[i]=[(a-f*b)%PR for a,b in zip(rows[i],rows[rk])]
        rk+=1
    return rk,rows[:rk]

class Cat:
    """frame catalogue; frames are root-closed sets of live lines (python int masks)"""
    def __init__(self,w):
        self.w=w;self.lines=w['lines'];self.nl=len(self.lines)
        self.masks=[sum(1<<i for i in f) for f in w['frames']]
        self.dim=[rank_mod([self.lines[i] for i in f])[0] if f else 0 for f in w['frames']]
        self.idx={m:i for i,m in enumerate(self.masks)}
        self.clcache={}
        self.new=[]   # ids of frames created by closure
        self._arr()
    def _arr(self):
        self.lo=np.array([m&0xFFFFFFFFFFFFFFFF for m in self.masks],dtype=np.uint64)
        self.hi=np.array([m>>64 for m in self.masks],dtype=np.uint64)
        self.dimarr=np.array(self.dim,dtype=np.int64)
    def closure(self,mask):
        """id of the least catalogue frame containing mask, created if needed (None if mask empty -> zero frame)"""
        if mask in self.clcache: return self.clcache[mask]
        sel=[self.lines[i] for i in range(self.nl) if mask>>i&1]
        rk,bas=rank_mod(sel) if sel else (0,[])
        cl=0
        for i in range(self.nl):
            if mask>>i&1: cl|=1<<i
            elif sel and rank_mod(bas+[self.lines[i]])[0]==rk: cl|=1<<i
        if cl not in self.idx:
            self.idx[cl]=len(self.masks);self.masks.append(cl);self.dim.append(rk);self.new.append(len(self.masks)-1);self._arr()
        r=self.idx[cl];self.clcache[mask]=r;return r
    def feasible(self,low,high):
        lo=np.uint64(low&0xFFFFFFFFFFFFFFFF);hi=np.uint64(low>>64)
        hl=np.uint64(high&0xFFFFFFFFFFFFFFFF);hh=np.uint64(high>>64)
        ok=((self.lo&lo)==lo)&((self.hi&hi)==hi)&((self.lo&~hl)==0)&((self.hi&~hh)==0)
        return np.nonzero(ok)[0]
    def le(self,a,b): return self.masks[a]&self.masks[b]==self.masks[a]
    def export(self,w):
        w['frames']=[[i for i in range(self.nl) if m>>i&1] for m in self.masks]

def fee_table(a,top=9):
    return np.array([0.0]+[k*math.expm1(a*math.log(64/k)) for k in range(1,top+8)])

class View:
    """one section (A or B) of the tuner, seen as a flat elementary-op list with pre/post frame bounds per register"""
    def __init__(self,T,sec):
        self.T=T;self.sec=sec;self.cat=T.cat;self.fee=T.fee;self.N=T.N
        self.ops=T.secs[sec]
        self.ret=T.ret if sec=='A' else set()
        self.cp=T.cp
        self.refresh()
    def reindex(self):
        self.touch=[[] for _ in range(self.N)]
        for i,(f,t,s) in enumerate(self.ops):
            self.touch[t].append(i);self.touch[s].append(i)
    def refresh(self):
        T=self.T;N=self.N
        A=T.secs['A'];B=T.secs['B']
        lastA=list(T.w['start'])
        for f,t,s in A: lastA[t]=f;lastA[s]=f
        firstB=list(T.w['final']);seen=set()
        for f,t,s in B:
            for r in (t,s):
                if r not in seen: firstB[r]=f;seen.add(r)
        if self.sec=='A': self.pre=list(T.w['start']);self.post=firstB
        else: self.pre=lastA;self.post=list(T.w['final'])
        self.reindex()

class Tuner:
    def __init__(self,w,a=0.001733):
        self.w=copy.deepcopy(w);self.V=w['v'];self.N=2*self.V+w['R']
        self.cat=Cat(self.w);self.fee=fee_table(a)
        self.ret=set(w['ret'])
        self.secs={sec:[[f,t,s] for f,t,ss in w[sec] for s in ss] for sec in 'AB'}
        self.cp={}
        for r in self.ret:
            lf=None
            for f,t,s in self.secs['A']:
                if r in (t,s): lf=f
            self.cp[r]=lf if lf is not None else w['start'][r]
        self.views={sec:View(self,sec) for sec in 'AB'}
    def view(self,sec):
        v=self.views[sec];v.refresh();return v
    def word(self):
        w=copy.deepcopy(self.w);self.cat.export(w)
        for sec in 'AB': w[sec]=[[f,t,[s]] for f,t,s in self.secs[sec]]
        w['C']=wlib.rebuild_C(w)
        # keep the original catalogue ids; keep only those new closure frames that are used, renumbered after them
        n0=len(self.w['frames'])
        used=set(w['start'])|set(w['final'])
        for sec in 'DABC':
            for f,t,ss in w[sec]: used.add(f)
        newused=sorted(f for f in used if f>=n0)
        remap={f:n0+i for i,f in enumerate(newused)}
        if any(k!=v for k,v in remap.items()):
            w['start']=[remap.get(f,f) for f in w['start']];w['final']=[remap.get(f,f) for f in w['final']]
            for sec in 'DABC':
                for g in w[sec]: g[0]=remap.get(g[0],g[0])
        w['frames']=w['frames'][:n0]+[w['frames'][f] for f in newused]
        return w
    def paid(self):
        w=self.word();return wlib.paid(w),w

# ---------------------------------------------------------------- transports
def commute(a,b):
    """elementary additions [f,t,s] a and b commute algebraically: dst(a)!=src(b) and dst(b)!=src(a)"""
    return a[1]!=b[2] and b[1]!=a[2]

def _slotcost(T,fr_idx,dt,pt,nt,ds,ps,ns,Fs):
    fee=T.fee;dm=T.cat.dimarr
    dF=dm[Fs]
    c=fee[dF-pt]+fee[nt-dF]-fee[nt-pt]+fee[dF-ps]+fee[ns-dF]-fee[ns-ps]
    return c

def best_move(T,i,eps=1e-12,allow_move=True,thr=None,all_=False):
    """best (delta, q, F) for the op at index i of T.ops, or None.  q is the insertion index in the list with op i removed."""
    cat=T.cat;ops=T.ops;n=len(ops);op=ops[i];f0,t,s=op
    lo=i
    while allow_move and lo>0 and commute(op,ops[lo-1]): lo-=1
    hi=i
    while allow_move and hi<n-1 and commute(op,ops[hi+1]): hi+=1
    # touch lists in removed-list index space
    def tl(r): return [j if j<i else j-1 for j in T.touch[r] if j!=i]
    tt,ts=tl(t),tl(s)
    def frame_of(e): return ops[e if e<i else e+1][0]
    starts=sorted({lo}|{e+1 for e in tt+ts if lo<=e+1<=hi}|({i} if lo<=i<=hi else set()))
    # slot ranges
    best=None
    old=None
    res=[]
    for k,st in enumerate(starts):
        en=(starts[k+1]-1) if k+1<len(starts) else hi
        q=min(max(i,st),en)
        def ctx(lst,r):
            kk=bisect.bisect_left(lst,q)
            p=frame_of(lst[kk-1]) if kk>0 else T.pre[r]
            nx=frame_of(lst[kk]) if kk<len(lst) else T.post[r]
            return p,nx,kk
        pt,nt,kt=ctx(tt,t);ps,ns,ks=ctx(ts,s)
        low=cat.masks[pt]|cat.masks[ps];high=cat.masks[nt]&cat.masks[ns]
        if low&~high: continue
        Fs=cat.feasible(low,high)
        F0=cat.closure(low)
        if cat.masks[F0]&~high==0 and F0 not in Fs: Fs=np.append(Fs,F0)
        if len(Fs)==0: continue
        dm=cat.dim
        c=_slotcost(T,None,None,dm[pt],dm[nt],None,dm[ps],dm[ns],np.array(Fs)) if False else None
        fee=T.fee;dF=cat.dimarr[Fs]
        c=fee[dF-dm[pt]]+fee[dm[nt]-dF]-fee[dm[nt]-dm[pt]]+fee[dF-dm[ps]]+fee[dm[ns]-dF]-fee[dm[ns]-dm[ps]]
        # ret registers: last A frame must stay
        for r,lst,nx,Fvec in ((t,tt,kt,None),(s,ts,ks,None)):
            pass
        if t in T.ret or s in T.ret:
            ok=np.ones(len(Fs),bool)
            for r,lst,kk in ((t,tt,kt),(s,ts,ks)):
                if r in T.ret and kk==len(lst):   # op is last on r in this slot
                    ok&=np.array([Fs[x]==T.cp[r] for x in range(len(Fs))])
            if not ok.any(): continue
            c=np.where(ok,c,np.inf)
        jmin=int(np.argmin(c))
        entry=(float(c[jmin]),q,int(Fs[jmin]),st<=i<=en)
        if st<=i<=en:
            # cost with the old frame
            jold=np.nonzero(Fs==f0)[0]
            old=float(c[jold[0]]) if len(jold) else None
        res.append(entry)
    if old is None: return None
    # ret last-frame condition for removal: if op was last on a ret register and new slot makes another op last
    cand=[]
    lim=-eps if thr is None else thr
    for c,q,F,isold in res:
        d=c-old
        if (not isold or F!=f0) and d<lim:
            # ret check: after removal+insertion, last frame of each ret register must equal cp
            okr=True
            for r in (t,s):
                if r in T.ret:
                    lst=tt if r==t else ts
                    kk=bisect.bisect_left(lst,q)
                    last=F if kk==len(lst) else frame_of(lst[-1])
                    if last!=T.cp[r]: okr=False
            if okr: cand.append((d,q,F))
    if not cand: return [] if all_ else None
    return sorted(cand) if all_ else min(cand)

def apply_move(T,i,q,F):
    op=T.ops.pop(i);op[0]=F;T.ops.insert(q,op);T.reindex()

def transport_sweep(T,eps=1e-12,allow_move=True,verbose=True,maxmoves=10**9):
    """greedy: nominate every op's best move, apply best-first with re-evaluation.  returns list of applied moves"""
    for k,op in enumerate(T.ops): pass
    ids={id(op):op for op in T.ops}
    nom=[]
    for i in range(len(T.ops)):
        m=best_move(T,i,eps,allow_move)
        if m: nom.append((m[0],id(T.ops[i])))
    nom.sort()
    applied=[]
    for d0,oid in nom:
        if len(applied)>=maxmoves: break
        i=next(j for j,op in enumerate(T.ops) if id(op)==oid)
        m=best_move(T,i,eps,allow_move)
        if not m: continue
        d,q,F=m
        old=(T.ops[i][0],i)
        apply_move(T,i,q,F);applied.append(dict(id=oid,delta=d,old_index=i,new_index=q,old_frame=old[0],new_frame=F))
    if verbose: print('sweep: nominated',len(nom),'applied',len(applied),'sum delta %.6f'%sum(a['delta'] for a in applied),flush=True)
    return applied

# ---------------------------------------------------------------- Steinberg 3 -> 2
def chain_cost_list(T,r,ops):
    cat=T.cat;cur=T.pre[r];c=0.0
    for f,t,s in ops:
        if t==r or s==r:
            assert cat.le(cur,f),(r,cur,f);c+=T.fee[cat.dim[f]-cat.dim[cur]];cur=f
    assert cat.le(cur,T.post[r]);c+=T.fee[cat.dim[T.post[r]]-cat.dim[cur]]
    return c

def find_triples(T):
    ops=T.ops
    from collections import defaultdict
    pair=defaultdict(list);bysrc=defaultdict(list);bydst=defaultdict(list)
    for i,(f,t,s) in enumerate(ops): pair[(t,s)].append(i);bysrc[s].append(i);bydst[t].append(i)
    out=[]
    for pl,(fb,bt,bs) in enumerate(ops):
        cands=[]
        for pk in bysrc[bt]:
            if pk>pl: cands.append((1,pk,(ops[pk][1],bs)))
        for pk in bydst[bs]:
            if pk>pl: cands.append((2,pk,(bt,ops[pk][2])))
        for case,pk,cp in cands:
            for pq in pair.get(cp,[]):
                if len({pl,pk,pq})<3: continue
                if not all(commute(ops[pk],ops[j]) for j in range(pl+1,pk)): continue
                if not all(commute(ops[pq],ops[j]) for j in range(min(pl,pq),max(pl,pq)+1) if j not in (pk,pl,pq)): continue
                out.append((case,pl,pk,pq))
    return out

def eval_steinberg(T,pl,pk,pq):
    """best (delta,Fe,Fb,q) for replacing b=ops[pl], e=ops[pk], c=ops[pq] by [e',b'] at b's place"""
    cat=T.cat;ops=T.ops;dm=cat.dim
    b,e,c=ops[pl],ops[pk],ops[pq]
    rest=[op for j,op in enumerate(ops) if j not in (pk,pl,pq)]
    q=pl-(1 if pq<pl else 0)
    regs=sorted({e[1],e[2],b[1],b[2]})
    assert {c[1],c[2]}<=set(regs)
    # prev/next per register at slot q of rest
    ctxp={};ctxn={};last_in_rest={}
    base={};old={}
    for r in regs:
        idx=[j for j,op in enumerate(rest) if op[1]==r or op[2]==r]
        kk=bisect.bisect_left(idx,q)
        ctxp[r]=rest[idx[kk-1]][0] if kk>0 else T.pre[r]
        ctxn[r]=rest[idx[kk]][0] if kk<len(idx) else T.post[r]
        last_in_rest[r]=(kk==len(idx))
        base[r]=chain_cost_list(T,r,rest)-T.fee[dm[ctxn[r]]-dm[ctxp[r]]]
        old[r]=chain_cost_list(T,r,ops)
    er=[e[1],e[2]];br=[b[1],b[2]]
    lowe=0;highe=-1
    for r in er: lowe|=cat.masks[ctxp[r]];highe&=cat.masks[ctxn[r]]
    if lowe&~highe: return None
    Se=list(cat.feasible(lowe,highe))
    F0=cat.closure(lowe)
    if cat.masks[F0]&~highe==0 and F0 not in Se: Se.append(F0)
    fee=T.fee;best=None
    shared=set(er)&set(br)
    for Fe in Se:
        lowb=0;highb=-1
        for r in br:
            lowb|=cat.masks[Fe] if r in shared else cat.masks[ctxp[r]]
            highb&=cat.masks[ctxn[r]]
        if lowb&~highb: continue
        Sb=list(cat.feasible(lowb,highb))
        Fb0=cat.closure(lowb)
        if cat.masks[Fb0]&~highb==0 and Fb0 not in Sb: Sb.append(Fb0)
        Sb=np.array(Sb)
        dFe=dm[Fe];dFb=cat.dimarr[Sb]
        tot=np.zeros(len(Sb))
        ok=np.ones(len(Sb),bool)
        for r in regs:
            dp,dn=dm[ctxp[r]],dm[ctxn[r]]
            ine=r in er;inb=r in br
            if ine and inb:
                part=fee[dFe-dp]+fee[dFb-dFe]+fee[dn-dFb]
                lastF=Sb
            elif ine:
                part=np.full(len(Sb),fee[dFe-dp]+fee[dn-dFe]);lastF=np.full(len(Sb),Fe)
            else:
                part=fee[dFb-dp]+fee[dn-dFb];lastF=Sb
            tot+=base[r]+part-old[r]
            if r in T.ret and last_in_rest[r]:
                ok&=(lastF==T.cp[r])
        tot=np.where(ok,tot,np.inf)
        j=int(np.argmin(tot))
        if best is None or tot[j]<best[0]: best=(float(tot[j]),int(Fe),int(Sb[j]),q)
    return best

def steinberg_sweep(T,eps=1e-12,verbose=True,maxmoves=10**9):
    tr=find_triples(T)
    nom=[]
    for case,pl,pk,pq in tr:
        r=eval_steinberg(T,pl,pk,pq)
        if r and r[0]<-eps: nom.append((r[0],id(T.ops[pl]),id(T.ops[pk]),id(T.ops[pq])))
    nom.sort()
    applied=[]
    for d0,ib,ie,ic in nom:
        if len(applied)>=maxmoves: break
        pos={id(op):j for j,op in enumerate(T.ops)}
        if ib not in pos or ie not in pos or ic not in pos: continue
        pl,pk,pq=pos[ib],pos[ie],pos[ic]
        b,e,c=T.ops[pl],T.ops[pk],T.ops[pq]
        # re-verify the structure (indices may have shifted)
        ok=pl<pk and ((b[1]==e[2] and (c[1],c[2])==(e[1],b[2])) or (b[2]==e[1] and (c[1],c[2])==(b[1],e[2])))
        ok=ok and all(commute(e,T.ops[j]) for j in range(pl+1,pk)) and all(commute(c,T.ops[j]) for j in range(min(pl,pq),max(pl,pq)+1) if j not in (pk,pl,pq))
        if not ok: continue
        r=eval_steinberg(T,pl,pk,pq)
        if not r or r[0]>=-eps: continue
        d,Fe,Fb,q=r
        rest=[op for j,op in enumerate(T.ops) if j not in (pk,pl,pq)]
        e2=[Fe,e[1],e[2]];b2=[Fb,b[1],b[2]]
        T.ops[:]=rest[:q]+[e2,b2]+rest[q:];T.reindex()
        applied.append(dict(delta=d,b=b,e=e,c=c,Fe=Fe,Fb=Fb))
    if verbose: print('steinberg: triples',len(tr),'nominated',len(nom),'applied',len(applied),'sum delta %.6f'%sum(a['delta'] for a in applied),flush=True)
    return applied

# ---------------------------------------------------------------- observable pruning
def prune_dead(Tn):
    """delete A summands whose destination has zero response on the target outputs (exact backward propagation)"""
    w=Tn.w;V=Tn.V;N=Tn.N
    H=[0]*N
    for i in range(V):H[V+i]=1<<i
    for f,t,s in reversed(Tn.secs['B']):H[s]^=H[t]
    for t,S in enumerate(w['scatter']):
        for k in S:H[w['ret'][k]]^=H[V+t]
    A=Tn.secs['A'];dead=[]
    for i in range(len(A)-1,-1,-1):
        f,t,s=A[i]
        if H[t]==0:dead.append(i)
        H[s]^=H[t]
    ds=set(dead);A[:]=[op for i,op in enumerate(A) if i not in ds]
    return len(dead)

# ---------------------------------------------------------------- PR542 mechanism: least feasible frames
def least_frames(w,cat=None,secs=('A','B'),keep_ret=True):
    """chronological least-span frame assignment of every gate of the given sections (PR542 minimum.py).
    Returns (new word dict, list of changed gates).  Frames of the last A gate on a retained-total register are kept."""
    w=copy.deepcopy(w);cat=cat or Cat(w)
    V=w['v'];N=2*V+w['R']
    ret=set(w['ret'])
    lastA={}
    for i,(f,t,ss) in enumerate(w['A']):
        for r in [t,*ss]: lastA[r]=i
    cur=list(w['start']);moves=[]
    def run(sec):
        for i,(f,t,ss) in enumerate(w[sec]):
            regs=[t,*ss]
            if sec in secs and not (keep_ret and sec=='A' and any(r in ret and lastA[r]==i for r in regs)):
                m=0
                for r in regs: m|=cat.masks[cur[r]]
                F=cat.closure(m)
                assert cat.masks[F]&~cat.masks[f]==0,'least frame not below old'
                if F!=f: moves.append((sec,i,f,F));w[sec][i][0]=F;f=F
            for r in regs:
                assert cat.masks[cur[r]]&~cat.masks[f]==0
                cur[r]=f
    run('D');run('A');run('B')
    cat.export(w)
    return w,moves
