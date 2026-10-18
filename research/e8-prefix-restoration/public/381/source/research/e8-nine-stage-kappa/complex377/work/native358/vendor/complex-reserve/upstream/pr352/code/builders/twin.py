# Twin condensation of M-type plane leftovers on top of a Design-T word.
# For each plane where BH and LO are both M-starters (0->M->P) and LO goes P->FULL after BH += LO:
#   LO (pivot) enters at the common line E = M_bh ∩ M_lo (sigma=1); BH visits E first and absorbs LO there;
#   the absorption is inverted at FULL at the very end. LO's dirt then cancels (it enters BH twice).
import sys, json, collections, pickle, math, os
import numpy as np
from fractions import Fraction
sys.path.insert(0,''+os.environ.get('W3WORK','work')+'/eval'); sys.path.insert(0,''+os.environ.get('W3WORK','work')+'/agentA')
from cost import load_snapshot
from decomp import lab
HH=20
IN=sys.argv[1]; OUT=sys.argv[2]
os.makedirs(OUT,exist_ok=True)
s,fr,dim,rec=load_snapshot(IN)
v=s['v']; n=s['n']; ZERO=s['ZERO']; FULL=s['FULL']
FR=fr['frames']
init={r:s['initial'][str(r)] for r in range(n)}
NR=len(rec)
moves=collections.defaultdict(list)
for k in np.nonzero(rec[:,0]==0)[0]: moves[int(rec[k,1])].append(int(k))
adds_dst=collections.defaultdict(list); adds_src=collections.defaultdict(list)
for k in np.nonzero(rec[:,0]==1)[0]:
    adds_dst[int(rec[k,1])].append(int(k)); adds_src[int(rec[k,2])].append(int(k))
def chain(r): return [init[r]]+[int(rec[k,3]) for k in moves[r]]
chi=np.zeros((v,HH),dtype=np.int64)
for i in range(v):
    for p in lab[i]: chi[i,p]=1
G=None
def gnorm(w):
    s1=sum(x*x for x in w); s2=sum(w)
    return Fraction(s1)-Fraction(s2*s2,9)
def kernel_int(Bm):
    M=[[Fraction(x) for x in b] for b in Bm]; m=len(M); piv=[]; r=0
    for c in range(HH):
        pr=next((i for i in range(r,m) if M[i][c]!=0),None)
        if pr is None: continue
        M[r],M[pr]=M[pr],M[r]; pv=M[r][c]; M[r]=[x/pv for x in M[r]]
        for i in range(m):
            if i!=r and M[i][c]!=0:
                f_=M[i][c]; M[i]=[a-f_*b for a,b in zip(M[i],M[r])]
        piv.append(c); r+=1
        if r==m: break
    out=[]
    for fc in [c for c in range(HH) if c not in piv]:
        x=[Fraction(0)]*HH; x[fc]=Fraction(1)
        for i,pc in enumerate(piv): x[pc]=-M[i][fc]
        den=1
        for q in x: den=den*q.denominator//math.gcd(den,q.denominator)
        out.append([int(q*den) for q in x])
    return out
def intersect_line(a1,a2,b1,b2):
    # solve al*chi[a1]+be*chi[a2]-ga*chi[b1]-de*chi[b2]=0
    Mx=np.stack([chi[a1],chi[a2],-chi[b1],-chi[b2]],axis=1).astype(object)
    # nullspace over Q
    M=[[Fraction(int(x)) for x in row] for row in Mx]
    rows=len(M); cols=4; piv=[]; r=0
    for c in range(cols):
        pr=next((i for i in range(r,rows) if M[i][c]!=0),None)
        if pr is None: continue
        M[r],M[pr]=M[pr],M[r]; pv=M[r][c]; M[r]=[x/pv for x in M[r]]
        for i in range(rows):
            if i!=r and M[i][c]!=0:
                f_=M[i][c]; M[i]=[a-f_*b for a,b in zip(M[i],M[r])]
        piv.append(c); r+=1
    free=[c for c in range(cols) if c not in piv]
    if len(free)!=1: return None
    fc=free[0]; x=[Fraction(0)]*cols; x[fc]=Fraction(1)
    for i,pc in enumerate(piv): x[pc]=-M[i][fc]
    w=[x[0]*int(chi[a1,j])+x[1]*int(chi[a2,j]) for j in range(HH)]
    den=1
    for q in w: den=den*q.denominator//math.gcd(den,q.denominator)
    wi=[int(q*den) for q in w]
    gg=0
    for q in wi: gg=math.gcd(gg,abs(q))
    wi=[q//gg for q in wi]
    return wi
# detect eligible planes
elig=[]
for k in np.nonzero((rec[:,0]==1)&(rec[:,5]==40))[0]:
    a,b,f=int(rec[k,1]),int(rec[k,2]),int(rec[k,4])
    if dim[f]!=3 or a<2*v or b<2*v or a>=n or b>=n: continue
    ca,cb=chain(a),chain(b)
    if len(ca)<3 or len(cb)!=4: continue
    if not (ca[0]==ZERO and dim[ca[1]]==2 and ca[2]==f): continue
    if not (cb[0]==ZERO and dim[cb[1]]==2 and cb[2]==f and cb[3]==FULL): continue
    if ca[1]==cb[1]: continue
    xa=[int(rec[kk,2]) for kk in adds_dst[a] if int(rec[kk,4])==ca[1]]
    xb=[int(rec[kk,2]) for kk in adds_dst[b] if int(rec[kk,4])==cb[1]]
    if len(xa)!=2 or len(xb)!=2 or max(xa+xb)>=v: continue
    # LO consumers: only BH at P (forward); BH must not be read before this merge
    lo_src=[kk for kk in adds_src[b] if 0<dim[int(rec[kk,4])]<HH]
    if lo_src!=[int(k)]: continue
    bh_src_before=[kk for kk in adds_src[a] if kk<k and 0<dim[int(rec[kk,4])]<HH]
    if bh_src_before: continue
    # LO forward reads: only the two X reads at M
    lo_dst=[kk for kk in adds_dst[b] if 0<dim[int(rec[kk,4])]<HH]
    if len(lo_dst)!=2: continue
    elig.append((int(k),a,b,f,ca[1],cb[1],xa,xb))
print('eligible planes',len(elig))
# frames for lines
nextid=max(int(x) for x in FR)+1
newframes={}; linekey={}
remove=set(); modify={}; insert_before=collections.defaultdict(list); appendix=[]
initmod={}
bad=0
for (k,bh,lo,P_,Mbh,Mlo,xa,xb) in elig:
    w=intersect_line(xa[0],xa[1],xb[0],xb[1])
    if w is None or gnorm(w)==0: bad+=1; continue
    # canonical sign
    for q in w:
        if q!=0:
            if q<0: w=[-x for x in w]
            break
    key=tuple(w)
    if key not in linekey:
        fid=nextid; nextid+=1
        newframes[fid]={'B':[list(key)],'A':kernel_int([list(key)]),'dim':1}
        dim[fid]=1; linekey[key]=fid
    E=linekey[key]
    kb=moves[bh][0]; kl=moves[lo][0]
    assert int(rec[kb,2])==ZERO and int(rec[kb,3])==Mbh and int(rec[kl,2])==ZERO and int(rec[kl,3])==Mlo
    k1=min(kb,kl)
    insert_before[k1].append([0,bh,ZERO,E,1,0])
    insert_before[k1].append([1,bh,lo,1,E,42])
    modify[kb]=[0,bh,E,Mbh,1,0]
    modify[kl]=[0,lo,E,Mlo,1,0]
    initmod[lo]=E
    appendix.append([1,bh,lo,-1,FULL,43])
print('applied',len(appendix),'bad',bad,'new line frames',len(newframes))
# remove frame-0 ADDs involving pivots (comp reads) -- regenerated later
piv=set(initmod)
for k in np.nonzero(rec[:,0]==1)[0]:
    a,b,f=int(rec[k,1]),int(rec[k,2]),int(rec[k,4])
    if dim[f]==0 and (a in piv or b in piv): remove.add(int(k))
print('removed frame-0 reads of pivots',len(remove))
out=[]
for k in range(NR):
    if k in insert_before: out.extend(insert_before[k])
    if k in remove: continue
    out.append(modify.get(k,rec[k].tolist()))
out.extend(reversed(appendix))
out=np.array(out,dtype=np.int32)
st=dict(s); newinit=dict(s['initial'])
for r,E in initmod.items(): newinit[str(r)]=E
st['initial']=newinit; st['record_count']=len(out)
json.dump(st,open(OUT+'/249-states.json','w'))
out.tofile(OUT+'/249-records.bin')
fr2={'h':fr['h'],'frames':dict(FR)}
for fid,ff in newframes.items(): fr2['frames'][str(fid)]=ff
json.dump(fr2,open(OUT+'/frames.json','w'))
with open(OUT+'/frames.txt','w') as fo:
    fo.write('%d\n'%len(fr2['frames']))
    for k_,ff in fr2['frames'].items():
        fo.write('%s %d\n'%(k_,len(ff['B'])))
        for row in ff['B']: fo.write(' '.join(map(str,row))+'\n')
with open(OUT+'/states.txt','w') as fo:
    fo.write('%d %d %d %d\n'%(n,v,ZERO,FULL))
    for r in range(n): fo.write('%d %d\n'%(int(newinit[str(r)]),int(s['final'][str(r)])))
    for t in range(v): fo.write(' '.join(map(str,s['source_covectors'][t]))+'\n')
print('records',NR,'->',len(out))
