# Common loader + combinatorics for agent B analyses (read-only on inputs).
import json, collections, math, itertools, sys
import numpy as np
G='/home/claude/scratch_rar/source_inputs/base_bit/research/paired-cube-diagonal-bit-168/selected/bit/graph_p12.json'
lab=[tuple(sorted(l)) for l in json.load(open(G))['labels']]
v=1760
idx={l:i for i,l in enumerate(lab)}
P=lambda p:p//2
cube_of=[tuple(sorted(P(p) for p in lab[i])) for i in range(v)]
g=lambda r: r*math.log(120/r) if r>0 else 0.0
def mask(its):
    m=0
    for i in its: m|=1<<i
    return m
def items(m):
    out=[]
    while m:
        b=m&-m; out.append(b.bit_length()-1); m^=b
    return out
def popc(m): return bin(m).count('1')
# atoms
def face_mask(c,D,E):
    """items {c,a,b} with P(a),P(b) not in {P(c),D,E}"""
    return mask(i for i in range(v) if c in lab[i] and not ({P(q) for q in lab[i]} & {D,E}))
def linekey(x,y):
    if P(x)>P(y): x,y=y,x
    if x%2==1: x,y=x^1,y^1
    return (x,y)
LINEMASK={}
for i in range(v):
    a,b,c=lab[i]
    for (x,y) in ((a,b),(a,c),(b,c)):
        LINEMASK.setdefault(linekey(x,y),0)
for key in list(LINEMASK):
    x,y=key
    LINEMASK[key]=mask(i for i in range(v) if (x in lab[i] and y in lab[i]) or ((x^1) in lab[i] and (y^1) in lab[i]))
LINEKEYS=sorted(LINEMASK)
def third(i,key):
    x,y=key
    return [P(q) for q in lab[i] if P(q) not in (P(x),P(y))][0]
DBM={}
for key,m in LINEMASK.items():
    for X in range(12):
        if X in (P(key[0]),P(key[1])): continue
        DBM[(key,X)]=mask(i for i in items(m) if third(i,key)==X)
def lp_mask(key,Z):
    return LINEMASK[key]&~DBM[(key,Z)]
def target_parts(t):
    c,d,e=lab[t]
    F={p:face_mask(p,*[P(q) for q in lab[t] if q!=p]) for p in (c,d,e)}
    L={}
    for (a,b) in ((c,d),(c,e),(d,e)):
        z=[P(q) for q in lab[t] if q not in (a,b)][0]
        key=linekey(a,b^1)
        L[(a,b)]=(key,z,lp_mask(key,z))
    K=[idx[tuple(sorted(s))] for s in ((c,d^1,e^1),(c^1,d,e^1),(c^1,d^1,e))]
    return F,L,K
def N_of(t):
    F,L,K=target_parts(t)
    m=0
    for x in F.values(): m^=x
    for x in L.values(): m^=x[2]
    for k in K: m^=1<<k
    return m

class Word:
    def __init__(self,d):
        self.d=d
        s=json.load(open(d+'/249-states.json'))
        self.s=s
        self.n=s['n']; self.ZERO=s['ZERO']; self.FULL=s['FULL']
        self.init={r:s['initial'][str(r)] for r in range(self.n)}
        self.fin={r:s['final'][str(r)] for r in range(self.n)}
        self.rec=np.fromfile(d+'/249-records.bin',dtype='<i4').reshape(-1,6)
        # dims from frames.txt (faster than json)
        self.dim={}
        with open(d+'/frames.txt') as f:
            nf=int(f.readline())
            for _ in range(nf):
                fid,dd=map(int,f.readline().split())
                self.dim[fid]=dd
                for __ in range(dd): f.readline()
    def frames_json(self):
        return json.load(open(self.d+'/frames.json'))['frames']
