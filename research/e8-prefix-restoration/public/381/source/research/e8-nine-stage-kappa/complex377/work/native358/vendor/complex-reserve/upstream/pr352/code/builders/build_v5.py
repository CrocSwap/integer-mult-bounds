# Cube-layer redesign ("Design T") builder.
import json, collections, sys, math, pickle, os
import numpy as np
sys.path.insert(0,''+os.environ.get('W3WORK','work')+'/eval'); sys.path.insert(0,''+os.environ.get('W3WORK','work')+'/agentA')
from cost import load_snapshot
from decomp import lab, idx
OUT=sys.argv[1] if len(sys.argv)>1 else ''+os.environ.get('W3WORK','work')+'/agentA/T/out'
LIMIT=int(sys.argv[2]) if len(sys.argv)>2 else 10**9
os.makedirs(OUT,exist_ok=True)
s,fr,dim,rec=load_snapshot(''+os.environ.get('W3WORK','work')+'/snap')
v=s['v'];n=s['n']; ZERO=s['ZERO']; FULL=s['FULL']
FR=fr['frames']
info=pickle.load(open(''+os.environ.get('W3WORK','work')+'/agentA/T/info.pkl','rb'))
part=pickle.load(open(''+os.environ.get('W3WORK','work')+'/agentA/interface.pkl','rb'))
P=lambda p:p//2
cube_of=[tuple(sorted(P(p) for p in lab[i])) for i in range(v)]
bits=lambda i: tuple(p%2 for p in lab[i])
init={r:s['initial'][str(r)] for r in range(n)}
NR=len(rec)
HH=20
chi=np.zeros((v,HH),dtype=np.int64)
for i in range(v):
    for p in lab[i]: chi[i,p]=1
icache={}
def items_in(fid):
    if fid in icache: return icache[fid]
    if dim[fid]==0 or dim[fid]>3: icache[fid]=None; return None
    A=np.array(FR[str(fid)]['A'],dtype=np.int64)
    I=frozenset(np.nonzero(np.all(chi@A.T==0,axis=1))[0].tolist()); icache[fid]=I if I else None; return icache[fid]
byset={}
for k_ in FR:
    f=int(k_)
    if 1<=dim[f]<=2:
        I=items_in(f)
        if I and len(I)==dim[f]: byset.setdefault(I,f)
newframes={}
nextid=max(int(k) for k in FR)+1
from fractions import Fraction
def kernel_int(B):
    M=[[Fraction(x) for x in b] for b in B]; m=len(M); piv=[]; r=0
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
def frame_for(itemset):
    global nextid
    I=frozenset(itemset)
    if I in byset: return byset[I]
    B=[chi[i].tolist() for i in sorted(I)]
    fid=nextid; nextid+=1
    newframes[fid]={'B':B,'A':kernel_int(B),'dim':len(B)}
    dim[fid]=len(B); byset[I]=fid; icache[fid]=I
    return fid
# ---------------- roles
role={}
for cube,C in info.items():
    for x in C['X']: role[x]=('X',cube)
    for pl,(r,last,e) in C['BH'].items(): role[r]=('BH',cube)
    for r in C['single']: role[r]=('S',cube)
    for r in C['carrier']: role[r]=('C',cube)
    for r in C['death']: role[r]=('D',cube)
    for r in C['upper']: role[r]=('U',cube)
    for r in C['other']: role[r]=('Y' if v<=r<2*v else 'M',cube)
moves=collections.defaultdict(list)
for k in np.nonzero(rec[:,0]==0)[0]: moves[int(rec[k,1])].append(int(k))
# special cubes: Y or X reading BH at planes -> skip
skipc=set(); xplane_keep=set()
for k in np.nonzero(rec[:,0]==1)[0]:
    a,b,f=int(rec[k,1]),int(rec[k,2]),int(rec[k,4])
    if 1<=dim[f]<=3:
        ra=role.get(a,('?',None)); rb=role.get(b,('?',None))
        if rb[0]=='BH' and ra[0]=='X': xplane_keep.add(a)  # v5: keep this X's plane visit
# single -> target (delivery ADD)
sdeliv={}
for k in np.nonzero(rec[:,0]==1)[0]:
    a,b=int(rec[k,1]),int(rec[k,2])
    if v<=a<2*v and role.get(b,('?',))[0]=='S' and dim[int(rec[k,4])]==HH-1: sdeliv[b]=a-v
# X-X forward mix ADDs
xx={}
for k in np.nonzero(rec[:,0]==1)[0]:
    a,b=int(rec[k,1]),int(rec[k,2])
    if a<v and b<v and dim[int(rec[k,4])]<HH:
        assert frozenset((a,b)) not in xx; xx[frozenset((a,b))]=int(k)
cubelist=sorted(info.keys())
todo=[c for c in cubelist if c not in skipc][:LIMIT]
print('cubes',len(cubelist),'skip(special)',len(skipc),'transform',len(todo))
# ---------------- outputs
remove=np.zeros(NR,bool)
modify={}                 # k -> new record (replace in place)
insert_before=collections.defaultdict(list)   # k -> records to emit before k
newblock=[]
fwd=[]                    # new forward gates for inversion (a,b,f)
unused=set()
def MOVE(r,old,new):
    assert dim[new]>=dim[old], (r,old,new)
    return [0,r,old,new,dim[new]-dim[old],0]
def ADD(a,b,f,c=1,z=40): return [1,a,b,c,f,z]
def xor(a,b): return tuple(p^q for p,q in zip(a,b))
allb=[(i,j,k) for i in (0,1) for j in (0,1) for k in (0,1)]
cubeframes_of={}
def is_cubeframe(fid,cube):
    I=items_in(fid)
    return bool(I) and all(cube_of[i]==cube for i in I)
stats=collections.Counter()
GPOOL=[]
for cube in todo: GPOOL.extend(sorted(info[cube]['death']))
GPOOL_SET=set(GPOOL)
used_ids=set()
def take_id(own):
    while own:
        r=own.pop()
        if r not in used_ids: used_ids.add(r); return r
    while GPOOL:
        r=GPOOL.pop()
        if r not in used_ids: used_ids.add(r); return r
    raise Exception('global pool empty')
for cube in todo:
    C=info[cube]; byb=C['byb']; Xb=lambda b: byb[b]
    cubeset=set(C['items'])
    regs=set(C['X'])|{r for pl,(r,l,e) in C['BH'].items()}|set(C['single'])|set(C['carrier'])|set(C['death'])
    # ---- mix pairs
    mixpairs=[]
    for b in allb:
        if b[1]==0:
            A_,B_=Xb(b),Xb(xor(b,(0,1,1)))
            k=xx[frozenset((A_,B_))]
            car=int(rec[k,1]); pas=int(rec[k,2])
            early=dim[int(rec[k,4])]==2
            Mf=int(rec[k,4]) if early else frame_for((A_,B_))
            mixpairs.append(dict(A=car,B=pas,k=k,early=early,M=Mf,bA=bits(car),bB=bits(pas)))
    mixof={}
    for mp in mixpairs: mixof[frozenset((mp['A'],mp['B']))]=mp
    # ---- planes and BHs
    planes=[]
    for pl,(r,last,e) in C['BH'].items():
        fl=part[r]['frames']; pids=[f for f in fl if dim[f]==3]
        bs=[bits(i) for i in pl]
        if len({b[0] for b in bs})==1 or len({b[1]^b[2] for b in bs})==1: dirn=(0,1,1)
        elif len({b[1] for b in bs})==1 or len({b[0]^b[2] for b in bs})==1: dirn=(1,0,1)
        else: dirn=(1,1,0)
        # split into 2 edges along dirn
        its=sorted(pl); e1=None
        edges=[]
        rest=set(its)
        while rest:
            a=min(rest); bb=[i for i in rest if xor(bits(a),bits(i))==dirn][0]
            edges.append(frozenset((a,bb))); rest-={a,bb}
        planes.append(dict(items=pl,BH=r,pids=pids,first=pids[0],dirn=dirn,edges=edges))
    # ---- tetra edges (non-mix): each in 2 planes
    tedges={}
    for p in planes:
        if p['dirn']!=(0,1,1):
            for e in p['edges']: tedges.setdefault(e,[]).append(p)
    assert len(tedges)==8 and all(len(x)==2 for x in tedges.values()), (cube,len(tedges))
    medges={}
    for p in planes:
        if p['dirn']==(0,1,1):
            for e in p['edges']: medges.setdefault(e,[]).append(p)
    assert len(medges)==4 and all(len(x)==2 for x in medges.values())
    # ---- singles matching: single for target t holds item s=t^011; edge {s, t^101} or {s, t^110}
    singles=[]
    for r,d in C['single'].items():
        t=sdeliv[r]; c=d['exit_content']; assert len(c)==1
        sitem=c[0]; tb=bits(t); assert xor(tb,(0,1,1))==bits(sitem), (r,t,sitem)
        cands=[frozenset((sitem,byb[xor(tb,(1,0,1))])),frozenset((sitem,byb[xor(tb,(1,1,0))]))]
        singles.append((r,t,sitem,cands))
    # bipartite matching singles <-> tedges
    match={}
    def try_assign(i,used):
        r,t,si,cands=singles[i]
        for e in cands:
            if e in used: continue
            used.add(e)
            if e not in match or try_assign(match[e],used): match[e]=i; return True
        return False
    for i in range(len(singles)): assert try_assign(i,set()), 'no matching'
    # ---- carriers
    carriers=[]
    for r in C['carrier']:
        d=part[r]; c=d['exit_content']
        if len(c)==1: carriers.append((r,'line',c[0]))
        elif len(c)==2:
            e=frozenset(c); diff=xor(bits(c[0]),bits(c[1]))
            if diff==(0,1,1): carriers.append((r,'M',e))
            else:
                assert e in tedges, ('carrier pair not a T edge',cube,c)
                carriers.append((r,'T',e))
        elif len(c)==3: carriers.append((r,'drop',None))   # p10 port: dead 3-item chain partial, register continues as a gauge
        else: raise Exception(('carrier content',len(c)))
    # ---- id pool for leftovers
    pool=list(C['death'])
    # ---- assign pair-holders
    # tetra edges: L_a, L_b ; send L for item min->face plane? choose: arrival to plane p from edge e
    arrivals=collections.defaultdict(list)   # plane index -> list of (regid placeholder, source kind, edge, item)
    T_regs={}
    for e,pls in tedges.items():
        a,b=sorted(e)
        # pls: two planes; L_a -> pls[0], L_b -> pls[1]
        T_regs[e]=dict(La=a,Lb=b,pa=pls[0],pb=pls[1])
    plane_index={id(p):i for i,p in enumerate(planes)}
    for e,tr in T_regs.items():
        arrivals[plane_index[id(tr['pa'])]].append(('L',e,tr['La']))
        arrivals[plane_index[id(tr['pb'])]].append(('L',e,tr['Lb']))
    for e,pls in medges.items():
        for p in pls: arrivals[plane_index[id(p)]].append(('M',e,None))
    # decide BH vs LO per plane, assign ids
    regid={}   # (kind,e,item/planeidx) -> role id
    recyc={}   # plane index -> carrier id
    pair_carriers=[(r,kind,c) for (r,kind,c) in carriers if kind in ('M','T')]
    for (r,kind,c) in pair_carriers:
        last=part[r]['frames'][-1]
        for pi,p in enumerate(planes):
            if last in p['pids'] and c in p['edges'] and pi not in recyc:
                recyc[pi]=(r,kind,c); break
    recycled_carriers={x[0] for x in recyc.values()}
    carriers=[x for x in carriers if x[0] not in recycled_carriers]
    for pi,p in enumerate(planes):
        arr=arrivals[pi]; assert len(arr)==2
        bh,lo=arr[0],arr[1]
        if pi in recyc:
            ce=recyc[pi][2]
            if bh[1]==ce: bh,lo=lo,bh
            assert lo[1]==ce
        key_bh=(bh[0],bh[1],bh[2] if bh[0]=='L' else pi); key_lo=(lo[0],lo[1],lo[2] if lo[0]=='L' else pi)
        regid[key_bh]=p['BH']
        if pi in recyc: regid[key_lo]=recyc[pi][0]; p['lo_carrier']=recyc[pi][0]
        else: regid[key_lo]=take_id(pool)
        p['bh_key']=key_bh; p['lo_key']=key_lo
    # ---- remove old records of cube-layer regs within the cube layer
    # deaths: all records removed (MOVEs, ADDs) -> handled via role-level removal below
    # BH: MOVEs into cube frames up to and including first plane id
    for p in planes:
        r=p['BH']
        for k in moves[r]:
            nf=int(rec[k,3])
            if is_cubeframe(nf,cube):
                remove[k]=True
                if nf==p['first']: break
    # singles: remove MOVEs into cube frames; modify exit MOVE
    for r,t,si,c in singles:
        ex=part[r]['exit']; k=ex[2]
        for kk in moves[r]:
            if kk<k: remove[kk]=True
    # carriers: remove MOVEs before exit
    for r,kind,c in carriers:
        ex=part[r]['exit']; k=ex[2]
        for kk in moves[r]:
            if kk<k: remove[kk]=True
    # X: remove MOVEs into cube frames (other than line which is initial);
    # keep rank-0 alias MOVEs out of M (the official checker compares frame ids, not subspaces)
    Mof={}
    for mp in mixpairs:
        for x in (mp['A'],mp['B']): Mof[x]=mp['M']
    xalias={}
    for x in C['X']:
        ex=part[x]['exit']; k=ex[2]
        cur={Mof[x]}; last=Mof[x]
        for kk in moves[x]:
            if kk<k:
                o_,nw=int(rec[kk,2]),int(rec[kk,3])
                if o_ in cur and o_!=nw and dim[nw]==dim[o_]:
                    cur.add(nw); last=nw; stats['xalias']+=1; continue
                if x in xplane_keep and o_ in cur and dim[nw]==3 and is_cubeframe(nw,cube):
                    cur={nw}; last=nw; stats['xplane']+=1; continue
                remove[kk]=True
        xalias[x]=last
    # ---- new block
    blk=[]
    # line registers
    linefr={i:init[i] for i in C['items']}
    for e,tr in T_regs.items():
        for item in (tr['La'],tr['Lb']):
            r=regid[('L',e,item)]
            blk.append(MOVE(r,ZERO,linefr[item])); g=ADD(r,item,linefr[item]); blk.append(g); fwd.append(g)
    for r,kind,c in carriers:
        if kind=='line':
            blk.append(MOVE(r,ZERO,linefr[c])); g=ADD(r,c,linefr[c]); blk.append(g); fwd.append(g)
    # X to M
    for mp in mixpairs:
        for x in (mp['A'],mp['B']): blk.append(MOVE(x,linefr[x],mp['M']))
    # M starters
    for e,pls in medges.items():
        mp=mixof[e]
        for p in pls:
            pi=plane_index[id(p)]; r=regid[('M',e,pi)]
            blk.append(MOVE(r,ZERO,mp['M']))
            for x in (mp['A'],mp['B']): g=ADD(r,x,mp['M']); blk.append(g); fwd.append(g)
    for r,kind,c in carriers:
        if kind=='M':
            mp=mixof[c]; blk.append(MOVE(r,ZERO,mp['M']))
            for x in (mp['A'],mp['B']): g=ADD(r,x,mp['M']); blk.append(g); fwd.append(g)
    # tetra frames
    Tframe={}
    for e,tr in T_regs.items():
        Tf=frame_for(e); Tframe[e]=Tf
        La=regid[('L',e,tr['La'])]; Lb=regid[('L',e,tr['Lb'])]
        blk.append(MOVE(La,linefr[tr['La']],Tf)); blk.append(MOVE(Lb,linefr[tr['Lb']],Tf))
        si=match.get(e)
        if si is not None:
            sr,t,sitem,_=singles[si]
            blk.append(MOVE(sr,ZERO,Tf))
            a_=La if sitem==tr['La'] else Lb; b_=Lb if a_==La else La
            for g in (ADD(sr,a_,Tf),ADD(a_,b_,Tf),ADD(b_,sr,Tf)): blk.append(g); fwd.append(g)
        else:
            raise Exception('tetra edge without single')
        for r,kind,c in carriers:
            if kind=='T' and c==e:
                blk.append(MOVE(r,ZERO,Tf)); g=ADD(r,La,Tf); blk.append(g); fwd.append(g)
    # planes
    for pi,p in enumerate(planes):
        bk=p['bh_key']; lk=p['lo_key']
        def srcframe(key):
            return Tframe[key[1]] if key[0]=='L' else mixof[key[1]]['M']
        rb=regid[bk]; rl=regid[lk]
        blk.append(MOVE(rb,srcframe(bk),p['first'])); blk.append(MOVE(rl,srcframe(lk),p['first']))
        g=ADD(rb,rl,p['first']); blk.append(g); fwd.append(g)
        if 'lo_carrier' in p:
            k=part[rl]['exit'][2]; rr=rec[k].tolist(); rr[2]=p['first']; rr[4]=dim[rr[3]]-dim[rr[2]]; modify[k]=rr
            for kk in moves[rl]:
                if kk<k: remove[kk]=True
        else:
            blk.append(MOVE(rl,p['first'],FULL))
    newblock.extend(blk)
    # ---- exit MOVE modifications
    for r,t,si,c in singles:
        k=part[r]['exit'][2]; e_=[e for e,i in match.items() if singles[i][0]==r][0]
        rr=rec[k].tolist(); rr[2]=Tframe[e_]; rr[4]=dim[rr[3]]-dim[rr[2]]; modify[k]=rr
    for r,kind,c in carriers:
        k=part[r]['exit'][2]
        src=ZERO if kind=='drop' else (linefr[c] if kind=='line' else (mixof[c]['M'] if kind=='M' else Tframe[c]))
        rr=rec[k].tolist(); rr[2]=src; rr[4]=dim[rr[3]]-dim[rr[2]]; modify[k]=rr
    for mp in mixpairs:
        A_,B_=mp['A'],mp['B']
        if mp['early']:
            for x in (A_,B_):
                k=part[x]['exit'][2]; rr=rec[k].tolist()
                if dim[rr[3]]==3:   # should not happen: exit is beyond cube frames
                    raise Exception('X exit into plane')
                rr[2]=xalias[x]; rr[4]=dim[rr[3]]-dim[rr[2]]; modify[k]=rr
        else:
            assert xalias[A_]==mp['M'] and xalias[B_]==mp['M']
            # retimed: old: A: line->E (k_A), B: line->E (k_B), mix at E (mp['k'])
            kA=part[A_]['exit'][2]; kB=part[B_]['exit'][2]
            E=int(rec[kA,3]); assert int(rec[mp['k'],4])==E
            # carrier: emit mix at M then MOVE M->E in place of kA
            mixrec=rec[mp['k']].tolist(); mixrec[4]=mp['M']
            insert_before[kA].append(mixrec)
            rr=rec[kA].tolist(); rr[2]=mp['M']; rr[4]=dim[rr[3]]-dim[rr[2]]; modify[kA]=rr
            remove[mp['k']]=True
            # passive: remove its MOVE to E; its next MOVE (from E) gets source M
            remove[kB]=True
            nxt=[kk for kk in moves[B_] if kk>kB]
            assert nxt, 'passive no next move'
            k2=nxt[0]; rr=rec[k2].tolist(); assert rr[2]==int(rec[kB,3]), ('passive next move',rr)
            # any ADDs of passive at E between? check later in verification
            rr[2]=mp['M']; rr[4]=dim[rr[3]]-dim[rr[2]]; modify[k2]=rr
    # ---- deaths & cube-internal ADD removal
    for r in C['death']:
        for kk in moves[r]: remove[kk]=True
    stats['cubes']+=1
unused=GPOOL_SET-used_ids
print('new frames',len(newframes),'unused ids',len(unused), dict(stats))
# ---------------- ADD removal (forward cube-layer gates) for transformed cubes
tset=set(todo)
cl_regs=set()
for cube in todo:
    C=info[cube]
    cl_regs|=set(C['X'])|{r for pl,(r,l,e) in C['BH'].items()}|set(C['single'])|set(C['carrier'])|set(C['death'])
deaths=set(); 
for cube in todo: deaths|=set(info[cube]['death'])
fwd_removed=np.zeros(NR,bool)
for k in np.nonzero(rec[:,0]==1)[0]:
    a,b,f=int(rec[k,1]),int(rec[k,2]),int(rec[k,4])
    if dim[f]==HH: continue
    if a in deaths or b in deaths:
        if v<=a<2*v and dim[f]==0 and int(rec[k,5])==4: continue  # comp read handled separately
        fwd_removed[k]=True; continue
    if 1<=dim[f]<=3:
        ra=role.get(a,('?',None)); rb=role.get(b,('?',None))
        if ra[1] in tset or rb[1] in tset:
            # keep interface ADDs
            if ra[0] in ('U','Y','M'): continue
            if ra[0]=='X' and rb[0]=='X': continue      # mix handled separately
            if ra[0]=='X' and a in xplane_keep and rb[0]=='BH': continue   # v5: special X reads its plane block
            fwd_removed[k]=True
# LIFO matching of inverses
stack=collections.defaultdict(list); inv_of={}
for k in range(NR):
    if rec[k,0]!=1: continue
    a,b,f=int(rec[k,1]),int(rec[k,2]),int(rec[k,4])
    if v<=a<2*v: continue
    if dim[f]!=HH: stack[(a,b)].append(k)
    else:
        if stack[(a,b)]: inv_of[stack[(a,b)].pop()]=k
nomatch=sum(1 for k in np.nonzero(fwd_removed)[0] if k not in inv_of)
print('removed forward ADDs',int(fwd_removed.sum()),'without inverse',nomatch)
for k in np.nonzero(fwd_removed)[0]:
    remove[k]=True
    if k in inv_of: remove[inv_of[k]]=True
# deaths: also remove any FULL ADDs involving them that remain
for k in np.nonzero(rec[:,0]==1)[0]:
    a,b,f=int(rec[k,1]),int(rec[k,2]),int(rec[k,4])
    if (a in deaths or b in deaths) and dim[f]==HH: remove[k]=True
# comp reads: remove all frame-0 cat4 reads from sigma0 helpers (regenerated later)
comp=(rec[:,0]==1)&(rec[:,5]==4)&(rec[:,1]>=v)&(rec[:,1]<2*v)
for k in np.nonzero(comp)[0]:
    if dim[int(rec[k,4])]==0 and dim[init[int(rec[k,2])]]==0: remove[k]=True
# ---------------- assemble
out=[]
out.extend(newblock)
for k in range(NR):
    if k in insert_before: out.extend(insert_before[k])
    if remove[k] and k not in modify: continue
    out.append(modify.get(k, rec[k].tolist()))
# inverses of new forward gates, appended at the end
for (o,a,b,c,f,z) in reversed(fwd):
    out.append([1,a,b,-c,FULL,41])
out=np.array(out,dtype=np.int32)
print('records',NR,'->',len(out))
# states
newinit=dict(s['initial']); 
for r in unused: newinit[str(r)]=FULL
st=dict(s); st['initial']=newinit; st['record_count']=len(out)
json.dump(st,open(OUT+'/249-states.json','w'))
out.tofile(OUT+'/249-records.bin')
# frames
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
pickle.dump(dict(todo=todo,unused=sorted(unused),newframes=list(newframes)),open(OUT+'/plan.pkl','wb'))
print('done')
