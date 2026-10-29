# build mapped mask tables for all 120 roots and all 1080 D7 vectors (images of h0 under W(E8)) ; binary u64 pairs
import numpy as np, struct
L=[tuple(map(int,l.split()[1:])) for l in open('lines.txt')]
pos={}
for t,v in enumerate(L): pos[v]=t; pos[tuple(-x for x in v)]=t
def refl(v,w):  # reflect vector w in line v
    d=sum(a*b for a,b in zip(w,v))//4
    return tuple(a-d*b for a,b in zip(w,v))
def lperm(v): return [pos[refl(v,L[t])] for t in range(120)]
gens=[lperm(L[v]) for v in range(120)]
gv=[L[v] for v in range(120)]
def orbit(h0):
    # returns dict canon(vector up to sign) -> perm sending h0 to it
    ident=list(range(120)); key=lambda x: max(x,tuple(-a for a in x))
    seen={key(h0):(h0,ident)}; fr=[(h0,ident)]
    while fr:
        nf=[]
        for h,p in fr:
            for v in gv:
                h2=refl(v,h); k=key(h2)
                if k in seen: continue
                g=lperm(v); p2=[g[p[t]] for t in range(120)]   # new perm = reflect after p
                seen[k]=(h2,p2); nf.append((h2,p2))
        fr=nf
    return seen
roots=orbit(L[0]); print(len(roots))
s=[t for t in range(1,120) if sum(a*b for a,b in zip(L[0],L[t]))==0][0]
h0=tuple(a+b for a,b in zip(L[0],L[s]))
d7=orbit(h0); print(len(d7))
def readmasks(fn):
    out=[]
    for l in open(fn):
        x=list(map(int,l.split())); out.append(x[1:])
    return out
rb=readmasks('A_root16.txt'); db=readmasks('A_d7_22.txt')
def dump(name,orb,base):
    with open(name,'wb') as f:
        for k,(h,p) in orb.items():
            # sanity: perm maps base target line set; check inner product invariance not needed
            for m in base:
                lo=hi=0
                for t in m:
                    u=p[t]
                    if u<64: lo|=1<<u
                    else: hi|=1<<(u-64)
                f.write(struct.pack('<QQBH',lo,hi,len(m),0) if False else struct.pack('<QQ',lo,hi))
    print(name)
dump('roots.bin',roots,rb); dump('d7.bin',d7,db)
open('counts.txt','w').write('%d %d %d %d\n'%(len(roots),len(rb),len(d7),len(db)))
# root index per orbit element (for 'r in E'): order of dict = order of dump
open('rootidx.txt','w').write(' '.join(str(pos[h]) for h,_ in roots.values()))
