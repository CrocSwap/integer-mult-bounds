"""checks.py CAND_DIR OUT_DIR OUT_JSON : exact independent checks of a kernel candidate built by transform.py.
 - every frame added to COHORT249-FRAMES.json beyond #310's: B full rank, A full rank 24-d, A.B=0, Gram under 9I-J nonsingular (exact)
 - every selection family: F2 kernel identity on the ORIGINAL word's prefix responses (C_p + sum C_d = 0 mod 2, odd coefficients),
   E contained in the actual first positive frame of every member, members are ZERO-initial FULL-final helpers, not source owners/donor keys
 - zero-response singles: no prefix reads in the original word; initial frame = their first MOVE destination
 - entrance rank total divisible by 3; 249-states.json record_sha256 matches the records"""
import sys,json,hashlib,collections
import numpy as np
from sympy import Matrix
C,O,OUTJ=sys.argv[1:4]
st=json.load(open(C+'/249-states.json')); n,v,ZERO,FULL=st['n'],st['v'],st['ZERO'],st['FULL']; H0=2*v
fr=json.load(open(O+'/frames.json'))['frames']
old_nf=json.load(open(C+'/COHORT249-FRAMES.json')); nf=json.load(open(O+'/COHORT249-FRAMES.json'))
added={k:x for k,x in nf.items() if k not in old_nf}
G=Matrix(24,24,lambda i,j:(9 if i==j else 0)-1)
for k,f in added.items():
    B=Matrix(f['B']); A=Matrix(f['A']); d=f['dim']
    assert B.rows==d and B.rank()==d and A.rows==24-d and A.rank()==24-d and (A*B.T).is_zero_matrix, k
    assert (B*G*B.T).det()!=0, ('degenerate',k)
    assert fr[k]==f
rec=np.fromfile(C+'/COHORT249-RECORDS.bin',dtype='<i4').reshape(-1,6)
isread=(rec[:,0]==1)&(rec[:,5]==4)&(rec[:,4]==ZERO); CUT=int(np.nonzero(isread)[0][-1]); assert isread[:CUT+1].all()
resp=collections.defaultdict(collections.Counter)
for _,a,b,c,f,z in rec[:CUT+1].tolist(): resp[b][a]+=c
first={}
for i in range(CUT+1,len(rec)):
    k,a,b,c,f,z=rec[i].tolist()
    for s in ((a,) if k==0 else (a,b)):
        if H0<=s<n and s not in first: first[s]=(k,c if k==0 else None,b if k==0 else None)
own=set(st['source_owned_roles']); dk=set(json.load(open(sys.argv[4] if len(sys.argv)>4 else C+'/../base-verify/export/249-DONOR-OWNERSHIP.json'))['donor_keys'])
ini={int(k):x for k,x in st['initial'].items()}
nini={int(k):x for k,x in json.load(open(O+'/COHORT249-INITIAL.json')).items()}
def contained(Bk,Fk):
    return (Matrix(fr[str(Fk)]['A'])*Matrix(fr[str(Bk)]['B']).T).is_zero_matrix if fr[str(Fk)]['A'] else True
sel=json.load(open(O+'/COHORT249-SELECTION.json'))
er=0; piv=set(); par=set(); nf_=ns=0
for s in sel:
    p=s['a']; ms=[p]+s['partners']; E=s['new_frame_id']; er+=s['E_dimension']; assert fr[str(E)]['dim']==s['E_dimension']
    assert p not in piv; piv.add(p); par.update(s['partners'])
    for h in ms:
        assert H0<=h<n and ini[h]==ZERO and st['final'][str(h)]==FULL and st['regs'][h-H0] not in own and st['regs'][h-H0] not in dk
        assert first[h][0]==0 and first[h][2]==ZERO and contained(E,first[h][1]),h
    assert nini[p]==E
    acc=collections.Counter(resp[p])
    for d,c in zip(s['partners'],s['coefficients']):
        assert c%2
        for t,x in resp[d].items(): acc[t]+=c*x
    assert all(x%2==0 for x in acc.values()),p
    if s['partners']: nf_+=1
    else: ns+=1; assert not resp[p] and E==first[p][1]
assert not piv&par and er%3==0
raw=open(O+'/COHORT249-RECORDS.bin','rb').read(); ost=json.load(open(O+'/249-states.json'))
assert ost['record_sha256']==hashlib.sha256(raw).hexdigest() and ost['record_count']==len(raw)//24
assert {int(k):x for k,x in ost['initial'].items()}==nini
r=dict(status='PASS_EXACT_KERNEL_CANDIDATE_CHECKS',added_frames=len(added),families=nf_,singles=ns,entrance_rank=er,record_sha256=ost['record_sha256'])
json.dump(r,open(OUTJ,'w'),indent=1); print(r)
