"""Export a bitE8/1 word to the PR249 record format read by PR #266's official cohort checkers and PR #315's engines.
usage: python3 export_records.py word.json[.gz] OUTDIR   ->  OUTDIR/{249-records.bin,249-states.json,frames.json}
Records are int32 six-tuples: MOVE(0,role,old,new,rank,0), ADD(1,dst,src,1,frame,phase), COPY(2,centre,temp,frame,ZERO,rank),
ERASE(3,centre,temp,frame,ZERO,0).  A multi-source gate becomes one ADD per source, preceded by the MOVEs of every
register of the gate to the gate frame.  Frames: integer basis rows B (label vectors of the frame's root lines in the
word's coordinates, a rational basis) and integer annihilator rows A (standard dot product), as PR #266 expects.
Dylan Crow, with Anthropic Claude assistance; Apache-2.0."""
import sys, json, gzip, struct, os
from fractions import Fraction as Fr
from math import gcd
def load(p):
    with (gzip.open(p,'rt') if p.endswith('.gz') else open(p)) as f: return json.load(f)
c=load(sys.argv[1]); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
v,R,h=c['v'],c['R'],c['h']; n=2*v+R; lines=c['lines']
def basis(idx):
    rows=[]; piv=[]; B=[]
    for i in idx:
        x=[Fr(a) for a in lines[i]]
        for p,r in zip(piv,rows):
            if x[p]: f=x[p]/r[p]; x=[a-f*b for a,b in zip(x,r)]
        nz=[k for k in range(h) if x[k]]
        if nz: rows.append(x); piv.append(nz[0]); B.append(list(lines[i]))
    return B,rows,piv
def annihilator(rows,piv):
    # rows in echelon (pivot columns piv); free columns give the null space of the row space under the dot product
    # reduce to RREF
    R_=[r[:] for r in rows]
    for i,(p,r) in enumerate(zip(piv,R_)):
        R_[i]=[a/r[p] for a in r]
    for i,p in enumerate(piv):
        for j in range(len(R_)):
            if j!=i and R_[j][p]: f=R_[j][p]; R_[j]=[a-f*b for a,b in zip(R_[j],R_[i])]
    free=[k for k in range(h) if k not in piv]; A=[]
    for f in free:
        a=[Fr(0)]*h; a[f]=Fr(1)
        for i,p in enumerate(piv): a[p]=-R_[i][f]
        L=1
        for x in a: L=L*x.denominator//gcd(L,x.denominator)
        ai=[int(x*L) for x in a]; g=0
        for x in ai: g=gcd(g,abs(x))
        A.append([x//g for x in ai])
    return A
frames={}
for k,idx in enumerate(c['frames']):
    B,rows,piv=basis(idx); A=annihilator(rows,piv) if B else [[int(i==j) for j in range(h)] for i in range(h)]
    assert all(sum(a*b for a,b in zip(x,y))==0 for x in A for y in B) and len(A)+len(B)==h
    frames[str(k)]=dict(dim=len(B),B=B,A=A)
dim=[frames[str(k)]['dim'] for k in range(len(c['frames']))]
ZERO=[k for k in range(len(dim)) if dim[k]==0]; assert len(ZERO)==1; ZERO=ZERO[0]
cur=list(c['start']); rec=[]
def move(r,f):
    if cur[r]!=f: rec.append((0,r,cur[r],f,dim[f]-dim[cur[r]],0)); cur[r]=f
def run(gates,ph):
    for f,d,srcs in gates:
        for r in [d]+srcs: move(r,f)
        for s in srcs: rec.append((1,d,s,1,f,ph))
run(c['D'],1); run(c['A'],2)
temp=n
for k,q in enumerate(c['ret']):
    fq=cur[q]; rec.append((2,q,temp,fq,ZERO,dim[fq]))
    for t,row in enumerate(c['scatter']):
        if k in row: rec.append((1,v+t,temp,1,ZERO,3))
    rec.append((3,q,temp,fq,ZERO,0))
run(c['B'],4); run(c['C'],5)
for r in range(n): move(r,c['final'][r])
with open(out+'/249-records.bin','wb') as f:
    for e in rec: f.write(struct.pack('<6i',*e))
st=dict(n=n,v=v,h=h,R=R,ZERO=ZERO,initial={str(r):c['start'][r] for r in range(n)},final={str(r):c['final'][r] for r in range(n)},
        retained_totals=c['ret'],source_owned_roles=[],regs=[])
json.dump(st,open(out+'/249-states.json','w'),sort_keys=True,separators=(',',':'))
json.dump(dict(frames=frames),open(out+'/frames.json','w'),sort_keys=True,separators=(',',':'))
print('exported',len(rec),'records,',len(frames),'frames, n',n,'ZERO',ZERO)
