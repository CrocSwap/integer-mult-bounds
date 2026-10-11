"""Frame retiming of the complex word: coordinate descent over gate frames (existing family), objective J=sum r*ln(73/r) over climbs."""
from cxlab import *
import math,random,sys
def spanmask(F):
    s={0}
    for b in F:s|={x^b for x in s}
    m=0
    for x in s:m|=1<<x
    return m
def perp(x):return basis([z for z in range(1,512) if not (x&z).bit_count()%2])
FULL=tuple(1<<i for i in range(8,-1,-1))
class Word:
    def __init__(self,w,start=None,m=73):
        self.w=w;self.P=w['ports'];R=w['R'] if 'R' in w else w['report']['R'];self.n=240+R;n=self.n
        self.ops=[e for e in w['A']]+[e for e in w['B']];self.na=len(w['A'])
        self.regs=[[e[1]]+([e[2]] if e[0]=='add' else []) for e in self.ops]
        self.F=[tuple(e[-1]) for e in self.ops]    # frame basis tuples
        self.start={};self.final={}
        for r in range(n):
            if r<v:self.start[r]=(self.P[r],)
            elif r<2*v:self.start[r]=()
            else:self.start[r]=basis(list((start or {}).get(r,())))
            self.final[r]=FULL if (r<v or r>=2*v) else perp(self.P[r-v])
        self.pos=defaultdict(list)
        for i,rs in enumerate(self.regs):
            for r in rs:self.pos[r].append(i)
        self.mk={}
        self.m=m
        self.centers_pin={}
        # pinned: centre registers final frame within A (last A gate)
        for r,f in zip(w['centers'],w['center_frames']):
            for i in reversed(self.pos[r]):
                if i<self.na:self.centers_pin[i]=True;break
    def sm(self,F):
        F=tuple(F)
        if F not in self.mk:self.mk[F]=spanmask(F)
        return self.mk[F]
    def phi(self,d):return d*math.log(self.m/d) if d>0 else 0.0
    def chain_cost(self,r,F=None):
        """cost of register r's chain with current frames (F: optional override list)"""
        F=F or self.F
        cur=self.start[r];c=0.0;cnt=Counter()
        for i in self.pos[r]:
            f=F[i]
            if f!=cur:
                d=len(f)-len(cur);c+=self.phi(d);cnt[d]+=1;cur=f
        f=self.final[r]
        if f!=cur:
            d=len(f)-len(cur);c+=self.phi(d);cnt[d]+=1
        return c,cnt
    def total(self):
        c=0.;cnt=Counter()
        for r in range(self.n):
            a,b=self.chain_cost(r);c+=a;cnt+=b
        return c,cnt
    def legal(self):
        for r in range(self.n):
            cur=self.sm(self.start[r])
            for i in self.pos[r]:
                f=self.sm(self.F[i])
                if cur&~f:return False,(r,i)
                cur=f
            if cur&~self.sm(self.final[r]):return False,(r,'final')
        return True,None

def family(W):
    fam={}
    for F in W.F:fam[W.sm(F)]=tuple(F)
    for r in range(W.n):
        for F in (W.start[r],W.final[r]):fam[W.sm(F)]=tuple(F)
    return fam
def bounds(W,i):
    rs=W.regs[i];L=0;U=None
    for r in rs:
        ps=W.pos[r];k=ps.index(i)
        prev=W.F[ps[k-1]] if k>0 else W.start[r]
        L|=0
        nxt=W.F[ps[k+1]] if k+1<len(ps) else W.final[r]
        Um=W.sm(nxt)
        U=Um if U is None else (U&Um)
    # L = join of prev frames
    Lb=[]
    for r in rs:
        ps=W.pos[r];k=ps.index(i)
        Lb+=list(W.F[ps[k-1]] if k>0 else W.start[r])
    Lb=basis(Lb)
    return Lb,U
def local_cost(W,i,F,rs=None):
    rs=rs or W.regs[i];old=W.F[i];W.F[i]=F
    c=sum(W.chain_cost(r)[0] for r in rs);W.F[i]=old;return c
def descent(W,fam,seed=0,passes=10,verbose=True):
    rnd=random.Random(seed);gates=[i for i in range(len(W.ops)) if i not in W.centers_pin]
    famitems=list(fam.items())
    for p in range(passes):
        rnd.shuffle(gates);moved=0
        for i in gates:
            Lb,U=bounds(W,i);Lm=W.sm(Lb)
            cur=W.F[i];best=cur;bc=local_cost(W,i,cur)
            for m_,F in famitems:
                if m_==W.sm(cur):continue
                if Lm&~m_ or m_&~U:continue
                c=local_cost(W,i,F)
                if c<bc-1e-9:bc=c;best=F
            if best!=cur:W.F[i]=best;moved+=1
        c,cnt=W.total()
        if verbose:print('pass',p,'moved',moved,'J',round(c,2),sorted(cnt.items()),flush=True)
        if not moved:break
    return W

def basis_of_mask(m):
    vs=[x for x in range(512) if m>>x&1]
    return basis(vs)
def descent2(W,seed=0,passes=10,verbose=True,allow_new=True):
    rnd=random.Random(seed);gates=[i for i in range(len(W.ops)) if i not in W.centers_pin]
    for p in range(passes):
        rnd.shuffle(gates);moved=0
        for i in gates:
            Lb,U=bounds(W,i)
            cur=W.F[i];best=cur;bc=local_cost(W,i,cur)
            cands=[Lb,basis_of_mask(U)]
            for F in cands:
                if W.sm(F)==W.sm(cur):continue
                c=local_cost(W,i,F)
                if c<bc-1e-9:bc=c;best=F
            if best!=cur:W.F[i]=best;moved+=1
        c,cnt=W.total()
        if verbose:print('pass',p,'moved',moved,'J',round(c,2),sorted(cnt.items()),flush=True)
        if not moved:break
    return W

def join(a,b):return basis(list(a)+list(b))
def meetmask(W,a,b):return W.sm(a)&W.sm(b)
def raise_closure(W,i,Fnew,maxn=60):
    """set F[i]=Fnew (superframe) and cascade raises on successors. returns dict gate->frame or None if illegal."""
    ch={i:Fnew};queue=[i]
    while queue:
        g=queue.pop();Fg=ch[g]
        for r in W.regs[g]:
            ps=W.pos[r];k=ps.index(g)
            if k+1<len(ps):
                h=ps[k+1];Fh=ch.get(h,W.F[h])
                if W.sm(Fg)&~W.sm(Fh):
                    if h in W.centers_pin:return None
                    nf=join(Fh,Fg);ch[h]=nf;queue.append(h)
                    if len(ch)>maxn:return None
            else:
                if W.sm(Fg)&~W.sm(W.final[r]):return None
    return ch
def lower_closure(W,i,Fnew,maxn=60):
    """set F[i]=Fnew (subframe of F[i]) and cascade lowering on predecessors whose frame must sit inside Fnew."""
    ch={i:Fnew};queue=[i]
    while queue:
        g=queue.pop();Fg=ch[g]
        if g in W.centers_pin and g!=i:return None
        for r in W.regs[g]:
            ps=W.pos[r];k=ps.index(g)
            if k>0:
                h=ps[k-1];Fh=ch.get(h,W.F[h])
                if W.sm(Fh)&~W.sm(Fg):
                    if h in W.centers_pin:return None
                    nf=basis_of_mask(W.sm(Fh)&W.sm(Fg));ch[h]=nf;queue.append(h)
                    if len(ch)>maxn:return None
            else:
                if W.sm(W.start[r])&~W.sm(Fg):return None
    return ch
def apply_ch(W,ch):
    old={g:W.F[g] for g in ch}
    for g,f in ch.items():W.F[g]=f
    return old
def delta(W,ch):
    regs=set()
    for g in ch:regs|=set(W.regs[g])
    before=sum(W.chain_cost(r)[0] for r in regs)
    old=apply_ch(W,ch);after=sum(W.chain_cost(r)[0] for r in regs)
    for g,f in old.items():W.F[g]=f
    return after-before
def closure_descent(W,seed=0,passes=6,verbose=True,maxn=60):
    rnd=random.Random(seed);gates=[i for i in range(len(W.ops)) if i not in W.centers_pin]
    for p in range(passes):
        rnd.shuffle(gates);moved=0
        for i in gates:
            best=None;bd=-1e-9
            cands=[]
            for r in W.regs[i]:
                ps=W.pos[r];k=ps.index(i)
                if k+1<len(ps):cands.append(('r',W.F[ps[k+1]]))
                if k>0:cands.append(('l',W.F[ps[k-1]]))
                cands.append(('rf',W.final[r])) if k+1==len(ps) else None
            for kind,F in cands:
                if W.sm(F)==W.sm(W.F[i]):continue
                if kind in('r','rf') and not (W.sm(W.F[i])&~W.sm(F)):
                    ch=raise_closure(W,i,F,maxn)
                elif kind=='l' and not (W.sm(F)&~W.sm(W.F[i])):
                    ch=lower_closure(W,i,F,maxn)
                else:continue
                if ch is None:continue
                d=delta(W,ch)
                if d<bd:bd=d;best=ch
            if best:apply_ch(W,best);moved+=1
        c,cnt=W.total()
        if verbose:print('pass',p,'moved',moved,'J',round(c,2),sorted(cnt.items()),flush=True)
        if not moved:break
    return W
