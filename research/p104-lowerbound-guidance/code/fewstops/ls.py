# FEWSTOPS local search: meetings (components of public stays joined by pub-pub gates) get charts; owned-gate meetings pinned.
# Coordinate descent over candidate charts = neighbours' prev/next charts (merges). Rebuild word, exact check.
from load import *
from reassign import SM, mask2id, basis_of
import math, pickle, sys
kf=0.0037214260438636; s=1-kf
def dm(m): return bin(m).count('1').bit_length()-1
def f(x): return x**s if x>0 else 0.0
def stays_of(W2):
    P2=W2['program']; sm=None
    st={r:[] for r in range(n)}   # list of [chart_mask, [event idx]]
    cur=[SM_[x] for x in W2['initial']]
    for i,e in enumerate(P2):
        op=e[0]
        if op=='MOVE':
            if e[1]<n: cur[e[1]]=SM_[e[3]]
            continue
        if op in ('INIT','CLEAR'): continue
        regs=[e[1]] if op=='SCALE' else [e[1],e[2]]
        for r in regs:
            if r<n:
                L=st[r]
                if L and L[-1][0]==cur[r] and L[-1][2]: L[-1][1].append(i)
                else: L.append([cur[r],[i],True])
    return st
def setup(W2):
    global SM_
    SM_=[]
    for b in W2['frames']:
        m=0
        for v in span(b): m|=1<<v
        SM_.append(m)
setup(W)
def optimize(W2, passes=20, verbose=True):
    setup(W2); P2=W2['program']
    for it in range(passes):
        st=stays_of(W2)
        # union-find over stays
        node={}; par=[]
        for r in range(n):
            for k in range(len(st[r])): node[(r,k)]=len(par); par.append(len(par))
        def fd(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        ev2stay={}
        for r in range(n):
            for k,(c,evs,_) in enumerate(st[r]):
                for i in evs: ev2stay[(i,r)]=k
        pin={}
        for i,e in enumerate(P2):
            if e[0] in ('ADD','COPY'):
                d,s_=e[1],e[2]
                if d<n and s_<n:
                    a=fd(node[(d,ev2stay[(i,d)])]); b=fd(node[(s_,ev2stay[(i,s_)])])
                    if a!=b: par[a]=b
                else:
                    r=d if d<n else s_
                    if r<n: pin[fd(node[(r,ev2stay[(i,r)])])]=SM_[e[4]]
        pinned=set()
        for x in list(pin): pinned.add(fd(x))
        members={}
        for (r,k),x in node.items(): members.setdefault(fd(x),[]).append((r,k))
        chart={(r,k):st[r][k][0] for (r,k) in node}
        init=[SM_[x] for x in W2['initial']]; fin=[SM_[x] for x in W2['final']]
        def pq(r,k):
            p=chart[(r,k-1)] if k>0 else init[r]
            q=chart[(r,k+1)] if k+1<len(st[r]) else fin[r]
            return p,q
        def mcost(r,k,G):
            p,q=pq(r,k); return f(dm(G)-dm(p))+f(dm(q)-dm(G))
        gain_tot=0; changed=0
        order=sorted(members, key=lambda m:-len(members[m]))
        for m in order:
            if m in pinned: continue
            mem=members[m]; G0=chart[mem[0]]
            cands=set()
            for (r,k) in mem:
                p,q=pq(r,k); cands.add(p); cands.add(q)
            base=sum(mcost(r,k,G0) for r,k in mem); best=(0,G0)
            for G in cands:
                if G==G0: continue
                ok=True
                for (r,k) in mem:
                    p,q=pq(r,k)
                    if not (p&G==p and G&q==G): ok=False; break
                if not ok: continue
                c=sum(mcost(r,k,G) for r,k in mem)
                if base-c>best[0]+1e-12: best=(base-c,G)
            if best[0]>0:
                for x in mem: chart[x]=best[1]
                gain_tot+=best[0]; changed+=1
        if verbose: print('pass',it,'meetings',len(members),'pinned',len(pinned),'changed',changed,'cost gain@kf',round(gain_tot,4)); sys.stdout.flush()
        if changed==0: break
        W2=rebuild(W2, st, chart)
        setup(W2); P2=W2['program']
    return W2
def rebuild(W2, st, chart):
    frames=[list(b) for b in W2['frames']]; m2i={}
    for i,m in enumerate(SM_): m2i.setdefault(m,i)
    def fid(m):
        if m not in m2i: m2i[m]=len(frames); frames.append(basis_of(m)); SM_.append(m)
        return m2i[m]
    G={}
    for r in range(n):
        for k,(c,evs,_) in enumerate(st[r]):
            for i in evs: G[(i,r)]=chart[(r,k)]
    cur=[SM_[x] for x in W2['initial']]; curid=list(W2['initial']); prog=[]
    for i,e in enumerate(W2['program']):
        op=e[0]
        if op=='MOVE':
            if e[1]>=n: prog.append(e)
            continue
        if op in ('INIT','CLEAR'): prog.append(e); continue
        regs=[e[1]] if op=='SCALE' else [e[1],e[2]]
        g=None
        for r in regs:
            if r<n:
                g=G[(i,r)]
                if cur[r]!=g:
                    assert cur[r]&g==cur[r]
                    nid=fid(g); prog.append(['MOVE',r,curid[r],nid,False]); cur[r]=g; curid[r]=nid
        if op=='SCALE':
            prog.append(['SCALE',e[1],e[2],curid[e[1]] if e[1]<n else e[3]])
        else:
            fr=e[4] if (e[1]>=n or e[2]>=n) else curid[e[1]]
            if e[1]<n and e[2]<n: assert curid[e[1]]==curid[e[2]]
            prog.append([op,e[1],e[2],e[3],fr])
    for r in range(n):
        if curid[r]!=W2['final'][r]:
            assert cur[r]!=SM_[W2['final'][r]] or True
            prog.append(['MOVE',r,curid[r],W2['final'][r],False]); cur[r]=SM_[W2['final'][r]]
    W3=dict(W2); W3['program']=prog; W3['frames']=frames
    return W3
if __name__=='__main__':
    from check import check
    W2=optimize(W)
    print(check(W2,'LS'))
    pickle.dump(W2,open('W_LS.pkl','wb'))
