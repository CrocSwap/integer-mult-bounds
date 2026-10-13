# Frame-chain local search over monotone frame lifts of the PR531 504-helper word.
# Prepared by rohanarun with Claude Opus 5.5 (Anthropic). Apache-2.0.
# usage: frame_chain_search.py COALESCED_WORD SEED SECONDS OUTPREFIX B TEMP SELECTED_WORD
# Every node frame G satisfies F_constructor <= G and per-register chain monotonicity; barriers, starts,
# target levels, final frames and all scalar operations are fixed. Objective: sum_r H_r * r((73/r)^B - 1).
import json,gzip,math,random,sys,time,copy
from collections import Counter
WORD=sys.argv[1];SEED=int(sys.argv[2]);SECS=float(sys.argv[3]);OUT=sys.argv[4]
B=float(sys.argv[5]) if len(sys.argv)>5 else 0.00152
TEMP0=float(sys.argv[6]) if len(sys.argv)>6 else 0.3
random.seed(SEED)
w=json.loads(gzip.decompress(open(WORD,'rb').read()))
orig=json.loads(gzip.decompress(open(sys.argv[7],'rb').read()))  # pre-coalescing frames = minimal legal
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
def span(F):
    s={0}
    for y in F: s|={x^y for x in s}
    return frozenset(s)
SP={}
def sp(F):
    if F not in SP: SP[F]=span(F)
    return SP[F]
def join(F,G): return basis(list(F)+list(G))
def meet(F,G): return basis(sorted(sp(F)&sp(G)))
def le(F,G): return sp(F)<=sp(G)
V,R,h=len(w['ports']),w['report']['R'],9;m=73;n=2*V+R
FULL=basis([1<<i for i in range(h)])
hyper=lambda p: basis([x for x in range(1,1<<h) if not (x&p).bit_count()%2])
starts=[(p,) for p in w['ports']]+[()]*(V+R)
for r,F in w.get('start_extra',{}).items(): starts[int(r)]=basis(F)
levels={int(t):basis(F) for t,F in w.get('target_levels',{}).items()}
nodes=[];chains=[[] for _ in range(n)]
def node(regs,F,mut,lo=None,sec=None,idx=None):
    k=len(nodes);nodes.append(dict(regs=list(regs),F=basis(F),mut=mut,lo=basis(lo) if lo is not None else basis(F),sec=sec,idx=idx))
    for r in regs: chains[r].append(k)
    return k
for r,F in enumerate(starts): node([r],F,False)
mutable=[]
for section in ('A','B'):
    if section=='B':
        for r,F in zip(w['centers'],w['center_frames']): node([r],F,False)
        for t in range(V): node([V+t],levels.get(t,()),False)
    for i,e in enumerate(w[section]):
        regs=e[1:3] if e[0]=='add' else e[1:2]
        assert [x for x in orig[section][i][:-1]]==e[:-1]
        mutable.append(node(regs,e[-1],True,lo=orig[section][i][-1],sec=section,idx=i))
for r in range(n): node([r],hyper(w['ports'][r-V]) if V<=r<2*V else FULL,False)
prv={};nxt={}
for r,ch in enumerate(chains):
    for x,y in zip(ch,ch[1:]): nxt[x,r]=y;prv[y,r]=x
f=lambda r: r*((m/r)**B-1) if r>0 else 0.0
def chainprof():
    H=Counter()
    for r,ch in enumerate(chains):
        for x,y in zip(ch,ch[1:]):
            d=len(nodes[y]['F'])-len(nodes[x]['F']);assert d>=0 and le(nodes[x]['F'],nodes[y]['F'])
            if d:H[d]+=1
    return H
H=chainprof();H0=Counter(H)
fee=lambda H: sum(f(r)*z for r,z in H.items())
cur=fee(H);best=cur;bestF=[z['F'] for z in nodes]
print('start',dict(sorted(H.items())),cur,flush=True)
def try_move(k,G):
    """set node k to G, propagate closure; return (changes dict, dh) or None"""
    ch={k:G};queue=[k]
    while queue:
        j=queue.pop();Fj=ch[j]
        for r in nodes[j]['regs']:
            q=nxt[j,r];Fq=ch.get(q,nodes[q]['F'])
            if not le(Fj,Fq):
                if not nodes[q]['mut']: return None
                ch[q]=join(Fq,Fj);queue.append(q)
            p=prv[j,r];Fp=ch.get(p,nodes[p]['F'])
            if not le(Fp,Fj):
                if not nodes[p]['mut']: return None
                Np=meet(Fp,Fj)
                if not le(nodes[p]['lo'],Np): return None
                ch[p]=Np;queue.append(p)
        if len(ch)>60: return None
    edges=set()
    for j in ch:
        for r in nodes[j]['regs']:
            edges.add((prv[j,r],j,r));edges.add((j,nxt[j,r],r))
    dh=Counter()
    for p,q,r in edges:
        o=len(nodes[q]['F'])-len(nodes[p]['F']);nw=len(ch.get(q,nodes[q]['F']))-len(ch.get(p,nodes[p]['F']))
        if o:dh[o]-=1
        if nw:dh[nw]+=1
    return ch,dh
t0=time.time();it=0;acc=0
while time.time()-t0<SECS:
    it+=1
    T=TEMP0*(1-(time.time()-t0)/SECS)+1e-6
    k=random.choice(mutable);z=nodes[k];F=z['F']
    u=random.random()
    if u<0.5:
        # raise by one vector from meet of successors or random
        Gm=FULL
        for r in z['regs']: Gm=meet(Gm,nodes[nxt[k,r]]['F'])
        cand=[x for x in range(1,512) if x not in sp(F)] if random.random()<0.3 else [x for x in sp(Gm) if x not in sp(F)]
        if not cand: continue
        G=join(F,(random.choice(cand),))
    else:
        # lower: remove one dimension while keeping lo and prev joins
        if len(F)==len(z['lo']): continue
        lo=z['lo']
        # pick a hyperplane of F containing lo
        Fs=sorted(sp(F)-{0});x=random.choice(Fs)
        Hs=[y for y in sp(F) if not (bin(y&x).count('1')%2)] if False else None
        # random codim-1 subspace of F containing lo: choose random linear functional on F vanishing on lo
        Fb=list(F);
        coeffs=[random.randint(0,1) for _ in Fb]
        if not any(coeffs): continue
        keep=[v for v in sp(F) if sum(c for c,b in zip(coeffs,Fb) if False)==0]
        # build subspace via functional: express vectors in F coordinates
        vecs=[]
        for mask in range(1<<len(Fb)):
            v=0;par=0
            for i,b in enumerate(Fb):
                if mask>>i&1: v^=b;par^=coeffs[i]
            if par==0: vecs.append(v)
        G=basis(vecs)
        if not le(lo,G): continue
    res=try_move(k,G)
    if res is None: continue
    ch,dh=res;d=fee(dh)
    if d<-1e-12 or (T>0 and random.random()<math.exp(-d/T)):
        for j,Gj in ch.items(): nodes[j]['F']=Gj
        H.update(dh);H=Counter({a:b for a,b in H.items() if b});cur+=d;acc+=1
        if cur<best-1e-12: best=cur;bestF=[z['F'] for z in nodes]
for j,F in enumerate(bestF): nodes[j]['F']=F
Hb=chainprof()
print('iters',it,'acc',acc,'best',best,'start',fee(H0),dict(sorted(Hb.items())),flush=True)
out=copy.deepcopy(w)
for k in mutable:
    z=nodes[k];out[z['sec']][z['idx']][-1]=list(z['F'])
json.dump(dict(best=best,start=fee(H0),chain_profile=dict(sorted(Hb.items())),start_chain_profile=dict(sorted(H0.items()))),open(OUT+'.json','w'))
open(OUT+'.gz','wb').write(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0))
