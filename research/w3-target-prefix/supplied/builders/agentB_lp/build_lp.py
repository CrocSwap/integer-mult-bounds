# Rebuild the LP-module layer of a word from an abstract all-but-one design (plan).
# Usage: build_lp.py <in_word_dir> <lines.pkl> <design.json> <out_dir> [--lift]
import sys, json, pickle, collections, math, os, argparse
import numpy as np
from fractions import Fraction
sys.path.insert(0,'/home/claude/work/agentB/tools'); sys.path.insert(0,'/home/claude/work/agentB/sat')
from base import *
from plan4 import make_plan
ap=argparse.ArgumentParser()
ap.add_argument('inw'); ap.add_argument('linesp'); ap.add_argument('design'); ap.add_argument('outd')
ap.add_argument('--limit',type=int,default=0)
ap.add_argument('--mode',type=str,default='exch')
a=ap.parse_args()
os.makedirs(a.outd,exist_ok=True)
s=json.load(open(a.inw+'/249-states.json'))
fr=json.load(open(a.inw+'/frames.json')); FR=fr['frames']
rec=np.fromfile(a.inw+'/249-records.bin',dtype='<i4').reshape(-1,6)
v=s['v']; n=s['n']; ZERO=s['ZERO']; FULL=s['FULL']
dim={int(k):len(x['B']) for k,x in FR.items()}
init={r:s['initial'][str(r)] for r in range(n)}
lines=pickle.load(open(a.linesp,'rb'))
P=make_plan(a.design,a.mode); assert P['ok']
NR=len(rec)
print('records',NR,'plan total %.1f'%P['total'],flush=True)
# ---------------- exact frame helpers
def rref_frac(rows):
    M=[[Fraction(x) for x in r] for r in rows]; piv=[]; rr=0
    for c in range(24):
        p=next((i for i in range(rr,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[rr],M[p]=M[p],M[rr]; pv=M[rr][c]; M[rr]=[x/pv for x in M[rr]]
        for i in range(len(M)):
            if i!=rr and M[i][c]!=0:
                f_=M[i][c]; M[i]=[x-f_*y for x,y in zip(M[i],M[rr])]
        piv.append(c); rr+=1
        if rr==len(M): break
    return M[:rr],piv
def canon(rows):
    R,piv=rref_frac(rows)
    return tuple(tuple(x) for x in R)
def kernel_int(B):
    R,piv=rref_frac(B)
    out=[]
    for fc in [c for c in range(24) if c not in piv]:
        x=[Fraction(0)]*24; x[fc]=Fraction(1)
        for i,pc in enumerate(piv): x[pc]=-R[i][fc]
        den=1
        for q in x: den=den*q.denominator//math.gcd(den,q.denominator)
        out.append([int(q*den) for q in x])
    return out
def indep_rows(rows):
    # greedy independent subset (exact)
    sel=[]
    for r in rows:
        if len(rref_frac(sel+[r])[0])>len(sel): sel.append(r)
    return sel
def gram_det_nonzero(B):
    # exact det of B G B^T, G = I - J/9
    d=len(B)
    s_=[sum(r) for r in B]
    M=[[Fraction(sum(x*y for x,y in zip(B[i],B[k])))-Fraction(s_[i]*s_[k],9) for k in range(d)] for i in range(d)]
    # det via elimination
    det=Fraction(1)
    for c in range(d):
        p=next((i for i in range(c,d) if M[i][c]!=0),None)
        if p is None: return False
        if p!=c: M[c],M[p]=M[p],M[c]; det=-det
        det*=M[c][c]
        for i in range(c+1,d):
            if M[i][c]!=0:
                f_=M[i][c]/M[c][c]; M[i]=[x-f_*y for x,y in zip(M[i],M[c])]
    return det!=0
def chi(i):
    w=[0]*24
    for p in lab[i]: w[p]=1
    return w
nextid=max(int(k) for k in FR)+1
newframes={}
canon_index={}
def frame_id_for_rows(rows,hint_ids=()):
    global nextid
    B=indep_rows(rows)
    key=canon(B)
    if key in canon_index: return canon_index[key]
    for h in hint_ids:
        if h is None: continue
        if dim[h]==len(B) and canon(FR[str(h)]['B'])==key:
            canon_index[key]=h; return h
    assert gram_det_nonzero(B), 'degenerate frame'
    fid=nextid; nextid+=1
    newframes[fid]={'B':[list(map(int,r)) for r in B],'A':kernel_int(B),'dim':len(B)}
    dim[fid]=len(B); canon_index[key]=fid
    return fid
# ---------------- records by register
byreg=collections.defaultdict(list)
for k in range(NR):
    o_,a_,b_,c_,f_,z_=rec[k]
    byreg[int(a_)].append(k)
    if o_==1 and b_!=a_: byreg[int(b_)].append(k)
remove=np.zeros(NR,bool)
modify={}            # k -> new record list
insert_fwd=[]        # new forward records (inserted at INS_FWD)
insert_inv=[]        # new inverse records (inserted at INS_INV)
newinit={}
cat_first41=int(np.nonzero((rec[:,0]==1)&(rec[:,5]==41))[0].min())
INS_FWD=879000
print('first cat41 at',cat_first41,flush=True)
keys=sorted(lines)
if a.limit: keys=keys[:a.limit]
stats=collections.Counter()
for key in keys:
    L=lines[key]; blocks=L['blocks']
    planes=L['planes']; outs=L['outs']
    planeR={p['r'] for p in planes.values()}
    others=L['others']
    copies=set(L['copies'])
    modregs=planeR|set(others)
    # reusable fresh ids: sigma0 others
    fresh_pool=[r for r in others if dim[init[r]]==0]
    assert len(fresh_pool)>=10, (key,len(fresh_pool))
    # design register -> actual id
    act={}
    for i in range(10): act[i]=planes[blocks[i]]['r']
    for j,i in enumerate(range(10,20)): act[i]=fresh_pool[j]
    used=set(act.values())
    freed=[r for r in others if r not in used]
    # ---- classify old records of module registers
    old_out={o['old']:Z for Z,o in outs.items()}
    deliv=collections.defaultdict(list)  # Z -> list of record indices (to be renamed)
    for Z,o in outs.items():
        r=o['old']; kc=o['kcopy']
        ks=sorted(k for k in byreg[r] if k>=kc)
        assert ks[0]==kc
        deliv[Z].append(kc)
        mv=[k for k in ks if rec[k][0]==0 and rec[k][1]==r]
        k1=mv[0]; assert dim[int(rec[k1][2])]==21 and dim[int(rec[k1][3])]==22, (key,Z,rec[k1])
        assert int(rec[k1][2])==o['PZ']
        k2=mv[1]; assert dim[int(rec[k1][3])]==22 and int(rec[k2][3])==FULL
        deliv[Z]+= [k1,k2]
        E1=int(rec[k1][3])
        cons=[k for k in ks if k1<k<k2]
        consumers=set()
        for k in cons:
            op,a_,b_,c_,f_,z_=[int(x) for x in rec[k]]
            assert op==1 and b_==r and f_==E1, (key,Z,rec[k])
            consumers.add(a_); deliv[Z].append(k)
        # inverses at FULL: src r, dst in consumers or copy, coeff -1
        for k in ks:
            if k<=k2: continue
            op,a_,b_,c_,f_,z_=[int(x) for x in rec[k]]
            if op==1 and b_==r and (a_ in consumers or a_==o['copy']) and f_==FULL:
                deliv[Z].append(k)
        nd=len(deliv[Z])
        stats['deliv%d'%nd]+=1
    delivset=set(k for ks in deliv.values() for k in ks)
    # remove module records of module registers (except cube-phase of planes, cat41, and deliveries)
    for r in modregs:
        lastcube=None
        if r in planeR:
            lastcube=[p['lastcube'] for p in planes.values() if p['r']==r][0]
        for k in byreg[r]:
            if k in delivset: continue
            op,a_,b_,c_,f_,z_=[int(x) for x in rec[k]]
            if r in planeR:
                if k<=lastcube: continue          # cube phase
                if op==1 and f_==ZERO: continue    # compensation reads handled globally
                if op==1:
                    other=b_ if a_==r else a_
                    if other not in modregs and other not in copies:
                        # cube-layer partner after the plane phase: must be a FULL inverse; keep
                        assert f_==FULL, ('non-FULL cube record after plane',key,r,k,rec[k].tolist())
                        stats['keptcube_'+str(z_)]+=1
                        continue
            # everything else of module registers is module-internal: remove
            if op==1:
                other=b_ if a_==r else a_
                if v<=other<2*v and f_!=ZERO and f_==init[r] and dim[init[r]]>0:
                    stats['rm_sigma_comp']+=1
                elif other not in modregs and other not in copies and not (v<=other<2*v and f_==ZERO):
                    raise Exception(('unexpected partner',key,r,k,rec[k].tolist()))
            remove[k]=True
    for r in freed:
        newinit[r]=FULL
    for r in used:
        if r not in planeR and r not in newinit: newinit[r]=ZERO
    # ---- new forward block
    cur={}   # actual reg -> current catalog frame
    for i in range(10): cur[act[i]]=planes[blocks[i]]['frame']
    def items_of(Kset):
        rows=[]
        for di in Kset:
            X=blocks[di]
            rows+=[chi(it) for it in items(DBM[(key,X)])]
        return rows
    for i in range(10,20):
        inf=P['info'][i]
        if inf['sig']:
            K0=inf['K0']
            fid0=planes[blocks[K0[0]]]['frame'] if len(K0)==1 else frame_id_for_rows(items_of(K0))
            assert dim[fid0]==2*len(K0)+1
            cur[act[i]]=fid0; newinit[act[i]]=fid0; stats['sigF']+=1
        else:
            cur[act[i]]=ZERO
    curdim=lambda r: dim[cur[r]]
    fwd=[]
    def MOVE(r,new):
        old=cur[r]
        if old==new: return
        assert dim[new]>dim[old] or (dim[new]==dim[old] and False), (key,r,old,new)
        fwd.append([0,r,old,new,dim[new]-dim[old],0]); cur[r]=new
    for t,groups in enumerate(P['rounds'],1):
        for gr in groups:
            Kd=gr['K']
            if len(Kd)==1:
                fid=planes[blocks[Kd[0]]]['frame']
            else:
                hints=[cur[act[m]] for m in gr['members']]
                fid=frame_id_for_rows(items_of(Kd),hints)
            assert dim[fid]==2*len(Kd)+1
            for m in gr['members']: MOVE(act[m],fid)
            for (dst,src) in gr['adds']:
                fwd.append([1,act[dst],act[src],1,fid,60])
    # final merges at P{Z}
    for zd in range(10):
        Z=blocks[zd]; o=outs[Z]; PZ=o['PZ']
        Od=[r for r in P['regs'] if P['info'][r]['role']=='O' and P['info'][r]['tgt']==zd][0]
        Md=[r for r in P['regs'] if P['info'][r]['role']=='M' and P['info'][r]['tgt']==zd][0]
        rO,rM=act[Od],act[Md]
        MOVE(rO,PZ); MOVE(rM,PZ)
        fwd.append([1,rO,rM,1,PZ,61])
        # partner retires
        fwd.append([0,rM,PZ,FULL,24-dim[PZ],0]); cur[rM]=FULL
        # rename deliveries: old output -> rO
        oldr=o['old']
        for k in deliv[Z]:
            rr=modify.get(k,rec[k].tolist())
            rr=list(map(int,rr))
            if rr[0]==0:
                assert rr[1]==oldr; rr[1]=rO
            else:
                assert rr[2]==oldr; rr[2]=rO
            modify[k]=rr
    # sanity: every reg either at PZ (outputs, waiting for delivery) or FULL
    insert_fwd.extend(fwd)
    # inverses of new forward ADDs (reverse order), at FULL
    for rr in reversed([x for x in fwd if x[0]==1]):
        insert_inv.append([1,rr[1],rr[2],-1,FULL,62])
    stats['lines']+=1
print(dict(stats),'new frames',len(newframes),flush=True)
# ---- global: remove all frame-0 cat4 compensation reads from sigma0 helpers (regenerated later)
newinit_full=dict(init); newinit_full.update(newinit)
comp=(rec[:,0]==1)&(rec[:,5]==4)&(rec[:,1]>=v)&(rec[:,1]<2*v)
nrm=0
for k in np.nonzero(comp)[0]:
    if dim[int(rec[k,4])]==0 and dim[init[int(rec[k,2])]]==0:
        remove[k]=True; nrm+=1
print('removed comp reads',nrm,flush=True)
# ---- assemble
out=[]
for k in range(NR):
    if k==INS_FWD: out.extend(insert_fwd)
    if k==cat_first41: out.extend(insert_inv)
    if remove[k] and k not in modify: continue
    out.append(modify.get(k,rec[k].tolist()))
out=np.array(out,dtype=np.int32)
print('records',NR,'->',len(out),flush=True)
st=dict(s); ni={str(r):int(newinit_full[r]) for r in range(n)}
st['initial']=ni; st['record_count']=len(out)
json.dump(st,open(a.outd+'/249-states.json','w'))
out.tofile(a.outd+'/249-records.bin')
fr2={'h':fr['h'],'frames':dict(FR)}
for fid,ff in newframes.items(): fr2['frames'][str(fid)]=ff
json.dump(fr2,open(a.outd+'/frames.json','w'))
with open(a.outd+'/frames.txt','w') as fo:
    fo.write('%d\n'%len(fr2['frames']))
    for k_,ff in fr2['frames'].items():
        fo.write('%s %d\n'%(k_,len(ff['B'])))
        for row in ff['B']: fo.write(' '.join(map(str,row))+'\n')
with open(a.outd+'/states.txt','w') as fo:
    fo.write('%d %d %d %d\n'%(n,v,ZERO,FULL))
    for r in range(n): fo.write('%d %d\n'%(int(ni[str(r)]),int(s['final'][str(r)])))
    for t in range(v): fo.write(' '.join(map(str,s['source_covectors'][t]))+'\n')
print('done',flush=True)
