"""transform.py CAND_DIR PLAN_JSON OUT_DIR
Kernel condensation on the w3 word (#310). For every family (pivot p, donors d_i, integer coefficients a_i with
C_p + sum a_i C_{d_i} = 0 over Z, E = nondegenerate subspace contained in the first positive frames of p and all d_i):
  - remove p's initial target-correction reads (cat 4 at ZERO, all before CUT);
  - after CUT (last initial read): families in increasing dim(E): MOVE d_i -> E, ADD d_i += a_i * p at E (cat 28);
  - p enters at E (initial frame), its first MOVE ZERO->F_p becomes E->F_p (deleted if E == F_p);
    d_i's first MOVE ZERO->F_d starts from d_i's last entrance frame instead;
  - at the very end (all helpers at FULL): ADD d_i -= a_i * p at FULL (cat 29).
Zero-response singles (C_p = 0, no reads): p enters at its first frame F_p, first MOVE deleted.
Writes COHORT249-RECORDS.bin (+249-records.bin copy), COHORT249-INITIAL.json, COHORT249-FRAMES.json (#310's + new),
COHORT249-SELECTION.json, COHORT249-FINAL.json, 249-states.json (initial, record_count, record_sha256), frames.json (merged)."""
import sys,json,hashlib,shutil,os
import numpy as np
from fractions import Fraction as Fr
from math import lcm,gcd
C,PLAN,OUT=sys.argv[1],sys.argv[2],sys.argv[3]
os.makedirs(OUT,exist_ok=True)
st=json.load(open(C+'/249-states.json')); n,v,ZERO,FULL=st['n'],st['v'],st['ZERO'],st['FULL']; H0=2*v
frames=json.load(open(C+'/frames.json'))
FR=frames['frames']
newfr_310=json.load(open(C+'/COHORT249-FRAMES.json'))
plan=json.load(open(PLAN))
rec=np.fromfile(C+'/COHORT249-RECORDS.bin',dtype='<i4').reshape(-1,6).tolist()
ini={int(k):x for k,x in json.load(open(C+'/COHORT249-INITIAL.json')).items()}
CUT=plan['cut']
assert all(r[0]==1 and r[5]==4 and r[4]==ZERO for r in rec[:CUT+1])
assert not any(r[0]==1 and r[5]==4 and r[4]==ZERO for r in rec[CUT+1:])
owners=set(st['source_owned_roles']); donorkeys=set(json.load(open(sys.argv[4] if len(sys.argv)>4 else C+'/../base-verify/export/249-DONOR-OWNERSHIP.json'))['donor_keys'])
dim=lambda f: FR[str(f)]['dim']
def rref(rows):
    m=[[Fr(x) for x in r] for r in rows]; piv=[]; rr=0
    for c in range(24):
        p=next((i for i in range(rr,len(m)) if m[i][c]!=0),None)
        if p is None: continue
        m[rr],m[p]=m[p],m[rr]; pv=m[rr][c]; m[rr]=[x/pv for x in m[rr]]
        for i in range(len(m)):
            if i!=rr and m[i][c]!=0:
                q=m[i][c]; m[i]=[a-q*b for a,b in zip(m[i],m[rr])]
        piv.append(c); rr+=1
    return tuple(tuple(r) for r in m[:rr]),piv
def prim(vec):
    L=1
    for x in vec: L=lcm(L,Fr(x).denominator)
    iv=[int(Fr(x)*L) for x in vec]; g=0
    for x in iv: g=gcd(g,abs(x))
    return [x//g for x in iv]
def annih(B):
    R,piv=rref(B); A=[]
    for fc in range(24):
        if fc in piv: continue
        vec=[Fr(0)]*24; vec[fc]=Fr(1)
        for i,pc in enumerate(piv): vec[pc]=-R[i][fc]
        A.append(prim(vec))
    return A
def contained(B,f):  # rows of B inside frame f
    A=FR[str(f)]['A']
    return all(sum(x*y for x,y in zip(b,a))==0 for b in B for a in A)
# first-use MOVE index per helper after CUT
firstmove={}
for i in range(CUT+1,len(rec)):
    k,a,b,c,f,z=rec[i]
    if k==0 and a>=H0 and a not in firstmove: firstmove[a]=i
    elif k in (1,2,3):
        for s in (a,b):
            if s>=H0 and s<n and s not in firstmove: firstmove[s]=('nonmove',i)
nextid=max(int(k) for k in FR)+1
canon={}; added={}
def frame_for(B,cands):
    key=rref(B)[0]
    for f in cands:  # reuse an existing frame equal to E
        if dim(f)==len(B) and contained(B,f): return f
    if key in canon: return canon[key]
    global nextid
    fid=nextid; nextid+=1
    A=annih(B); assert len(A)==24-len(B)
    FR[str(fid)]={'dim':len(B),'B':[list(map(int,b)) for b in B],'A':A}; added[str(fid)]=FR[str(fid)]
    canon[key]=fid; return fid
def check_role(h):
    assert H0<=h<n and st['regs'][h-H0] not in owners and st['regs'][h-H0] not in donorkeys and ini[h]==ZERO and st['final'][str(h)]==FULL,h
    assert isinstance(firstmove.get(h),int) and rec[firstmove[h]][2]==ZERO,h
pivots=set(); donors=set()
sel=[]
fams=[]
for fam in plan['families']:
    p=fam['p']; check_role(p); assert p not in pivots; pivots.add(p)
    for d in fam['ds']: check_role(d); donors.add(d)
    Fp=rec[firstmove[p]][3]; Fds=[rec[firstmove[d]][3] for d in fam['ds']]
    B=fam['basis']; assert contained(B,Fp) and all(contained(B,f) for f in Fds)
    E=frame_for(B,[Fp]+Fds)
    fams.append((dim(E),p,fam['ds'],fam['cs'],E))
assert not (pivots&donors)
for h in plan['singles']:
    check_role(h); assert h not in pivots and h not in donors
# --- build new word
delete=set(); mod={}
remove_reads=[i for i in range(CUT+1) if rec[i][2] in pivots]
delete.update(remove_reads)
fams.sort(key=lambda x:(x[0],x[1]))
state={}
gates=[]
for e,p,ds,cs,E in fams:
    for d,c in zip(ds,cs):
        cur=state.get(d,ZERO)
        if cur!=E:
            assert contained(FR[str(cur)]['B'],E) if cur!=ZERO else True
            gates.append([0,d,cur,E,dim(E)-dim(cur),0]); state[d]=E
        gates.append([1,d,p,c,E,28])
    ini[p]=E
    i=firstmove[p]; _,a,b,c,f,z=rec[i]
    if c==E: delete.add(i)
    else: mod[i]=[0,a,E,c,dim(c)-dim(E),z]
for d,cur in state.items():
    i=firstmove[d]; _,a,b,c,f,z=rec[i]
    if c==cur: delete.add(i)
    else:
        assert contained(FR[str(cur)]['B'],c)
        mod[i]=[0,a,cur,c,dim(c)-dim(cur),z]
for h in plan['singles']:
    i=firstmove[h]; ini[h]=rec[i][3]; delete.add(i)
out=[]
for i,r in enumerate(rec):
    if i in delete: pass
    else: out.append(mod.get(i,r))
    if i==CUT: out.extend(gates)
for e,p,ds,cs,E in fams:
    for d,c in zip(ds,cs): out.append([1,d,p,-c,FULL,29])
arr=np.array(out,dtype='<i4'); raw=arr.tobytes()
open(OUT+'/COHORT249-RECORDS.bin','wb').write(raw); open(OUT+'/249-records.bin','wb').write(raw)
sha=hashlib.sha256(raw).hexdigest()
for s in range(n): st['initial'][str(s)]=ini[s]
st['record_count']=len(out); st['record_sha256']=sha
json.dump(st,open(OUT+'/249-states.json','w'))
json.dump({str(s):ini[s] for s in range(n)},open(OUT+'/COHORT249-INITIAL.json','w'))
nf=dict(newfr_310); nf.update(added); json.dump(nf,open(OUT+'/COHORT249-FRAMES.json','w'))
json.dump(frames,open(OUT+'/frames.json','w'))
shutil.copy(C+'/COHORT249-FINAL.json',OUT+'/COHORT249-FINAL.json')
selection=[dict(a=p,partners=list(ds),coefficients=list(cs),new_frame_id=E,E_dimension=dim(E),kind='kernel_family') for e,p,ds,cs,E in fams]
selection+=[dict(a=h,partners=[],coefficients=[],new_frame_id=ini[h],E_dimension=dim(ini[h]),kind='zero_response_single') for h in plan['singles']]
json.dump(selection,open(OUT+'/COHORT249-SELECTION.json','w'),indent=0)
H={}
for r in out:
    if r[0]==0 and r[4]: H[r[4]]=H.get(r[4],0)+1
    elif r[0]==2: H[r[5]]=H.get(r[5],0)+1
oldH={}
for r in rec:
    if r[0]==0 and r[4]: oldH[r[4]]=oldH.get(r[4],0)+1
    elif r[0]==2: oldH[r[5]]=oldH.get(r[5],0)+1
mass=sum(k*c for k,c in H.items()); oldmass=sum(k*c for k,c in oldH.items())
er=sum(dim(ini[h]) for h in plan['singles'])+sum(dim(E) for e,p,ds,cs,E in fams)
receipt=dict(records=len(out),old_records=len(rec),sha256=sha,families=len(fams),singles=len(plan['singles']),new_frames=len(added),
    removed_initial_reads=len(remove_reads),gates_Q=sum(1 for g in gates if g[0]==1),moves_inserted=sum(1 for g in gates if g[0]==0),
    entrance_rank=er,old_rank_mass=oldmass,new_rank_mass=mass,mass_drop=oldmass-mass,
    delta={k:H.get(k,0)-oldH.get(k,0) for k in sorted(set(H)|set(oldH)) if H.get(k,0)!=oldH.get(k,0)})
assert oldmass-mass==er,(oldmass-mass,er)
json.dump(receipt,open(OUT+'/TRANSFORM-RECEIPT.json','w'),indent=1)
print(json.dumps(receipt))
