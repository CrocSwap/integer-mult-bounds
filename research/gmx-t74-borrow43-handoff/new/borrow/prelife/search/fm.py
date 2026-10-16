"""Frame model of a BORROW-WORD (replicates audit_local.run_borrow section 4) + forward-lift raise moves."""
import json,gzip,heapq,bisect,math
from collections import Counter,defaultdict
def basis(vs):
    piv={}
    for a in vs:
        while a:
            bit=a.bit_length()-1
            if bit in piv:a^=piv[bit]
            else:piv[bit]=a;break
    for k in sorted(piv):
        for j in piv:
            if j>k and piv[j]>>k&1:piv[j]^=piv[k]
    return tuple(piv[k] for k in sorted(piv,reverse=True))
def contained(a,b):return basis(list(a)+list(b))==b
def join(a,b):return basis(list(a)+list(b))
def regs_of(e):return tuple(e[1:3]) if e[0]=='add' else (e[1],)
def load(p):return json.loads(gzip.decompress(open(p,'rb').read()))
A_=0.0017037
def phi(d):return (d/73)**(1-A_)
class FM:
    def __init__(s,w):
        s.w=w;v,h,R=w['report']['v'],w['report']['h'],w['report']['R'];s.v=v;n=2*v+R;s.n=n
        full=basis([1<<i for i in range(h)]);s.full=full
        s.removed=set(w['removed']);s.live=[r for r in range(n) if r not in s.removed]
        end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
        for q,U in w['helper_final'].items():end[int(q)]=basis(U)
        start=[(p,) for p in w['ports']]+[()]*(v+R)
        for q,U in w['start_extra'].items():start[int(q)]=basis(U)
        s.end,s.start=end,start
        ev=[];npre=w.get('prelude_events',0)
        # ev: [kind, regs, frame(s), ref]; kind gate|warp
        for i,e in enumerate(w['A']):
            if e[0]=='warp':ev.append(['warp',(e[1],),(basis(e[3]),basis(e[4])),('A',i)])
            else:ev.append(['gate',regs_of(e),basis(e[-1]),('A',i)])
        s.kA=len(ev)  # events < kA are in A
        byp=defaultdict(list)
        for op,rec in enumerate(w['warps'],1):byp[rec[0]].append(op)
        B=w['B']
        for p in range(len(B)+1):
            for op in byp.get(p,[]):
                rec=w['warps'][op-1];ev.append(['warp',(rec[1],),(basis(rec[3]),basis(rec[4])),('W',op-1)])
            if p<len(B):ev.append(['gate',regs_of(B[p]),basis(B[p][-1]),('B',p)])
        for i,e in enumerate(w['restore']):ev.append(['gate',regs_of(e),basis(e[-1]),('restore',i)])
        s.ev=ev;s.byreg=defaultdict(list)
        for k,e in enumerate(ev):
            for r in e[1]:s.byreg[r].append(k)
        lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
        s.Aend={}
        for t in range(v):s.Aend[v+t]=lev.get(t,())
        for q,U in zip(w['centers'],w['center_frames']):s.Aend[q]=basis(U)
        # center path pieces (fixed)
        s.cpieces=Counter()
        for q,U in zip(w['centers'],w['center_frames']):
            U=basis(U);served={lev.get(e[1]-v,()) for e in w['cut'] if e[2]==q}
            for T in sorted(served,key=lambda x:-len(x)):
                if T!=U:s.cpieces[len(U)-len(T)]+=1
                U=T
    def frame_after(s,k,r,F=None):
        e=s.ev[k];f=(F or {}).get(k,e[2])
        return f[1] if e[0]=='warp' else f
    def frame_before(s,k,r,F=None):
        e=s.ev[k];f=(F or {}).get(k,e[2])
        return f[0] if e[0]=='warp' else f
    def climbs(s,r,F=None):
        cur=s.start[r];c=[]
        for k in s.byreg[r]:
            e=s.ev[k]
            if e[0]=='warp':
                U,E=(F or {}).get(k,e[2]);assert cur==U,(r,k);cur=E;continue
            f=(F or {}).get(k,e[2]);assert contained(cur,f),(r,k,cur,f)
            if len(f)>len(cur):c.append(len(f)-len(cur))
            cur=f
        assert contained(cur,s.end[r]);
        if len(s.end[r])>len(cur):c.append(len(s.end[r])-len(cur))
        return c
    def profile(s,F=None):
        p=Counter(s.cpieces)
        for r in s.live:
            for d in s.climbs(r,F):p[d]+=1
        return p
    def check_Aend(s,r,F):
        ks=[k for k in s.byreg[r] if k<s.kA]
        if r in s.Aend:
            f=s.frame_after(ks[-1],r,F) if ks else s.start[r]
            return f==s.Aend[r]
        return True
    def lift(s,k0,Fnew):
        """raise gate k0 to Fnew (must contain current); forward propagate. returns (F dict, touched regs) or None"""
        F={k0:Fnew};heap=[k0];seen=set();touched=set()
        while heap:
            k=heapq.heappop(heap)
            if k in seen:continue
            seen.add(k);e=s.ev[k];f=F[k]
            for r in e[1]:
                touched.add(r);ks=s.byreg[r];i=bisect.bisect_right(ks,k)
                if i<len(ks):
                    k2=ks[i];e2=s.ev[k2]
                    if e2[0]=='warp':
                        if F.get(k2,e2[2])[0]!=f:return None
                        continue
                    f2=F.get(k2,e2[2])
                    if not contained(f,f2):
                        if k2 in seen:return None
                        F[k2]=join(f2,f);heapq.heappush(heap,k2)
                else:
                    if not contained(f,s.end[r]):return None
        for r in touched:
            if r in s.Aend and not s.check_Aend(r,F):return None
        return F,touched
def cost(cl):return sum(phi(d) for d in cl)
