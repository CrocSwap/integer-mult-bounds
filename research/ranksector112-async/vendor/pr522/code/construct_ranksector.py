# Adapted by OpenAI Codex for isolated structural research.
# Modified from PR425 by icekylinx with Codex assistance.
"""Full discovery word for Hamming packets with borrowed X and Y registers.

This changes the scalar architecture. It is not accepted by the old restricted
gx interface: source bases may change until full-frame cleanup, and targets use
an explicitly inverted output basis. No supplier admission is asserted.
"""
import copy,gzip,json,math,time
import itertools as it
from collections import Counter,defaultdict
from fractions import Fraction as Q
from pathlib import Path

import sys
INPUT=Path(sys.argv[1]);OUT=Path(sys.argv[2]);OUT.mkdir(parents=True,exist_ok=False);D=json.loads((INPUT/'PROTOTYPE.json').read_text())
P=D['binary_ports'];R=D['root_lines'];v=120;h=9
modules=json.load(gzip.open(INPUT/'PACKET-PROGRAMS.json.gz'))

def basis(vectors):
    b={}
    for x in vectors:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))
def inside(a,b):return basis(a+b)==b
def hyper(p):return basis([x for x in range(1,512) if (x&p).bit_count()%2==0])
FULL=basis([1<<i for i in range(9)])
G=[[sum(x*y for x,y in zip(a,b))//2 for b in R] for a in R]
blocks={tuple(z['receipt']['block']):z for z in modules}
frame={next(i for i,x in enumerate(r) if x):s for s,r in enumerate(R) if sum(x!=0 for x in r)==1}
cur=[(p,) for p in P]+[()]*v;rows=[{r:Q(1)} if r<v else {} for r in range(2*v)]
A=[];B=[];H=Counter();by={k:Counter() for k in 'xysc'};phase=A

def alloc():
    n=len(cur);cur.append(());rows.append({});return n
def climb(r,F):
    assert inside(cur[r],F),('frame violation',r,cur[r],F)
    dr=len(F)-len(cur[r])
    if dr:H[dr]+=1;by['x' if r<v else 'y' if r<2*v else 's'][dr]+=1
    cur[r]=F
def add(t,s,q,F):
    assert t!=s;q=Q(q)
    if not q:return
    climb(t,F);climb(s,F);phase.append(['add',t,s,q.numerator,q.denominator,list(F)])
    for j,x in list(rows[s].items()):
        z=rows[t].get(j,Q(0))+q*x
        if z:rows[t][j]=z
        else:rows[t].pop(j,None)
def scale(t,q,F):
    q=Q(q);assert q
    if q==1:return
    climb(t,F);phase.append(['scale',t,q.numerator,q.denominator,list(F)])
    rows[t]={j:q*x for j,x in rows[t].items()}
def swap(a,b,F):
    if a==b:return
    add(a,b,1,F);add(b,a,-1,F);add(a,b,1,F);scale(b,-1,F)
def linear(regs,M,F):
    """Apply an invertible rational square matrix by elementary operations."""
    n=len(regs);a=[list(map(Q,row)) for row in M];undo=[]
    for col in range(n):
        k=next(i for i in range(col,n) if a[i][col])
        if k!=col:a[k],a[col]=a[col],a[k];undo.append(('swap',k,col))
        q=a[col][col]
        if q!=1:a[col]=[x/q for x in a[col]];undo.append(('scale',col,1/q))
        for i in range(n):
            if i==col or not a[i][col]:continue
            q=-a[i][col];a[i]=[x+q*y for x,y in zip(a[i],a[col])];undo.append(('add',i,col,q))
    assert a==[[Q(i==j) for j in range(n)] for i in range(n)]
    old=[dict(rows[r]) for r in regs]
    for op in reversed(undo):
        if op[0]=='swap':swap(regs[op[1]],regs[op[2]],F)
        elif op[0]=='scale':scale(regs[op[1]],1/op[2],F)
        else:add(regs[op[1]],regs[op[2]],-op[3],F)
    for i,r in enumerate(regs):
        expected=defaultdict(Q)
        for j,q in enumerate(M[i]):
            for k,x in old[j].items():expected[k]+=q*x
        assert rows[r]=={k:x for k,x in expected.items() if x}

# All original-source loads precede source borrowing.
own={};fl={}
for c,z in sorted(blocks.items()):
    ids=z['receipt']['source_lines']
    for s in ids:
        own[s]=alloc()

packets={};retired={}
for c,z in sorted(blocks.items()):
    ids=z['receipt']['source_lines'];mp={i:s for i,s in enumerate(ids)}
    mp.update({i:alloc() for i in range(8,24)})
    for event_index,(e,F) in enumerate(zip(z['events'],z['event_frames'])):
        t,s,a,b=e;add(mp[t],mp[s],Q(a,b),tuple(F))
        # 16 source copies and 24 two-shear operations precede face assembly.
        if event_index==39:
            for parity in (0,1):
                tet=sorted(s for s in ids if sum(R[s][i]<0 for i in c)%2==parity)
                matching=[[(tet[0],tet[1]),(tet[2],tet[3])],[(tet[0],tet[2]),(tet[1],tet[3])],[(tet[0],tet[3]),(tet[1],tet[2])]][((json.loads(Path(sys.argv[3]).read_text())[','.join(map(str,c))][parity]) if len(sys.argv)==4 else tuple(map(int,sys.argv[3:5]))[parity])]
                for pair in matching:
                    rs=sorted(r for r in mp.values() if set(rows[r])==set(pair))
                    assert len(rs)==2,(pair,rs)
                    for s,r in zip(pair,rs):
                        assert len(cur[r])==2
                        add(own[s],r,1,cur[r])
    keys=[(p,epsilon) for p in it.combinations(c,2) for epsilon in (-1,1)]
    for key,(reg,alpha) in zip(keys,z['outputs']):
        a=mp[reg];alpha=Q(alpha);F=cur[a]
        b=alloc();add(b,a,1,F)
        consumers=sorted(d for d in blocks if d!=c and set(key[0])<=set(d))
        assert len(consumers)==2
        for target,rr in zip(consumers,(a,b)):packets[c,key[0],key[1],target]=(rr,alpha)
    retired[c]=[mp[r] for r in z['dead_registers']]

# Four coordinate sums per code block, reconstructed in the retired register
# stock at its legal rank-four frame. The remaining eight rows retain a basis.
block_totals={}
def rowrank(a):
    a=[list(map(Q,r))for r in a];i=0
    for j in range(len(a[0])if a else 0):
        k=next((k for k in range(i,len(a))if a[k][j]),None)
        if k is None:continue
        a[i],a[k]=a[k],a[i];q=a[i][j];a[i]=[x/q for x in a[i]]
        for k in range(i+1,len(a)):
            q=a[k][j]
            if q:a[k]=[x-q*y for x,y in zip(a[k],a[i])]
        i+=1
    return i
def invmat(T):
    n=len(T);a=[list(map(Q,r))+[Q(i==j)for j in range(n)]for i,r in enumerate(T)]
    for col in range(n):
        k=next(i for i in range(col,n)if a[i][col]);a[k],a[col]=a[col],a[k];q=a[col][col];a[col]=[x/q for x in a[col]]
        for i in range(n):
            if i!=col:
                q=a[i][col];a[i]=[x-q*y for x,y in zip(a[i],a[col])]
    return[r[n:]for r in a]
for c,z in sorted(blocks.items()):
    ids=z['receipt']['source_lines'];regs=retired[c];F=basis([P[s]for s in ids]);chosen=[];T=[]
    for r in regs:
        t=[rows[r].get(x,Q(0))for x in ids]
        if rowrank(T+[t])>len(T):chosen.append(r);T.append(t)
    assert len(chosen)==8
    U=[[Q(R[s][i])for s in ids]for i in c];assert rowrank(U)==4
    for j in range(8):
        t=[Q(k==j)for k in range(8)]
        if rowrank(U+[t])>len(U):U.append(t)
    assert len(U)==8
    V=invmat(T);M=[[sum(U[i][k]*V[k][j]for k in range(8))for j in range(8)]for i in range(8)]
    linear(chosen,M,F)
    for i,r in zip(c,chosen[:4]):
        assert rows[r]=={s:Q(R[s][i])for s in ids};block_totals[c,i]=r

# Eight global coordinate sums, with a single copy each for the centers. The
# other copy is exactly the correction needed by the eight frame-line targets.
global_totals={};centers=[]
for i in range(8):
    regs=[block_totals[c,i] for c in sorted(blocks) if i in c]
    F=hyper(P[frame[i]]);a=regs[0]
    for b in regs[1:]:add(a,b,1,F)
    global_totals[i]=a
    centers.append(a)
centers += [frame[i] for i in range(8)]
center_frames=[cur[r] for r in centers]
assert list(map(len,center_frames))==[8]*8+[1]*8

# Own-block and coordinate-frame corrections, one stream per code target.
own_out={};tetrads={}
for c,z in sorted(blocks.items()):
    ids=z['receipt']['source_lines']
    tet=[sorted(s for s in ids if sum(R[s][i]<0 for i in c)%2==parity) for parity in (0,1)]
    tetrads[c]=tet
    for parity,targets in enumerate(tet):
        sources=tet[1-parity];xs=[own[s] for s in sources]
        F=basis([P[s] for s in sources])
        # Current own registers are an invertible pair-partial basis T*x.
        T=[[rows[x].get(s,Q(0)) for s in sources] for x in xs]
        n=len(T);aug=[r+[Q(i==j) for j in range(n)] for i,r in enumerate(T)]
        for col in range(n):
            k=next(i for i in range(col,n) if aug[i][col]);aug[k],aug[col]=aug[col],aug[k]
            q=aug[col][col];aug[col]=[x/q for x in aug[col]]
            for i in range(n):
                if i!=col:
                    q=aug[i][col];aug[i]=[a-q*b for a,b in zip(aug[i],aug[col])]
        inv=[r[n:] for r in aug]
        M=[[sum(Q(G[t][s])*inv[k][j] for k,s in enumerate(sources)) for j in range(n)] for t in targets]
        assert all(q.denominator&(q.denominator-1)==0 for row in M for q in row)
        linear(xs,M,F)
        for t,x in zip(targets,xs):own_out[t]=x

# Cross-block M packets, shared by four targets, then two-output pair transforms.
Ms={};consumers=defaultdict(list);pairs=[]
for c in sorted(blocks):
    for p in it.combinations(c,2):
        ds=sorted(d for d in blocks if d!=c and set(p)<=set(d))
        for epsilon in (-1,1):
            (a,alpha),(b,beta)=[packets[d,p,epsilon,c] for d in ds]
            F=basis(cur[a]+cur[b]);add(a,b,beta/alpha,F)
            Ms[c,p,epsilon]=(a,alpha)
    i,j,k,l=c;partitions=[((i,j),(k,l)),((i,k),(j,l)),((i,l),(j,k))]
    for parity,tet in enumerate(tetrads[c]):
        for pi,(p,q) in enumerate(partitions):
            groups=defaultdict(list)
            for t in tet:groups[R[t][p[0]]*R[t][p[1]]].append(t)
            for eps,ts in sorted(groups.items()):
                assert len(ts)==2;a,b=sorted(ts)
                e2=R[a][q[0]]*R[a][q[1]]
                assert e2==R[b][q[0]]*R[b][q[1]]
                keys=[(c,p,eps),(c,q,e2)];pid=len(pairs)
                selected=(pi==parity)  # different first partitions in the two tetrads
                pairs.append({'targets':(a,b),'keys':keys,'selected':selected,
                              'matrix':[[R[t][p[0]],R[t][q[0]]] for t in (a,b)]})
                for key in keys:consumers[key].append(pid)
slots={}
for key,uses in sorted(consumers.items()):
    assert len(uses)==2
    a,alpha=Ms[key];ordinary=[i for i in uses if not pairs[i]['selected']]
    for j,pid in enumerate(ordinary):
        if j==0:r=a
        else:r=alloc();add(r,a,1,cur[a])
        slots[pid,key]=(r,alpha)

assert len(cur)-240==560,(len(cur)-240)

# The selected target pairs borrow Y as the first packet destination. Their
# two-shear output basis is compensated at frame zero and in the scatter table.
phase=B;selected=[];output_basis=[]
for pid,pair in enumerate(pairs):
    if not pair['selected']:continue
    (t,u),(key1,key2),mat=pair['targets'],pair['keys'],pair['matrix']
    (a,alpha),(b,beta)=Ms[key1],Ms[key2]
    add(v+t,a,-Q(mat[0][0],2)*alpha,cur[a])
    add(v+u,b,-Q(mat[0][1],2)*beta,cur[b])
    selected.append((pid,t,u,mat))
for pid,t,u,mat in selected:
    F=basis(cur[v+t]+cur[v+u]);assert all((P[s]&p).bit_count()%2==0 for s in (t,u) for p in F)
    add(v+t,v+u,1,F);add(v+u,v+t,-Q(1,2),F)
    z=-Q(2*mat[1][0],mat[0][0]);scale(v+u,z,F)
    output_basis.append((t,u,z))

for pid,pair in enumerate(pairs):
    if pair['selected']:continue
    (t,u),(key1,key2),mat=pair['targets'],pair['keys'],pair['matrix']
    (a,alpha),(b,beta)=slots[pid,key1],slots[pid,key2]
    F=basis(cur[a]+cur[b]);aa,ab=Q(mat[0][0])*alpha,Q(mat[0][1])*beta
    ba,bb=Q(mat[1][0])*alpha,Q(mat[1][1])*beta
    add(a,b,ab/aa,F);q=ba/(bb-ba*ab/aa);add(b,a,q,F)
    add(v+t,a,-aa/2,hyper(P[t]));add(v+u,b,-(bb-ba*ab/aa)/2,hyper(P[u]))
for t,r in own_out.items():add(v+t,r,-Q(1,2),hyper(P[t]))

side=[dict(rows[v+t]) for t in range(v)]
for t in range(v):
    expected={s:-Q(G[t][s],2) for s in range(v) if s!=t and G[t][s] and s not in frame.values()} if t not in frame.values() else {}
    assert side[t]==expected,('side identity',t)

# Correct the eight-center scatter through the inverse two-output basis.
scatter=[[Q(r[i],4) if t not in frame.values() else Q(0) for i in range(8)]+[Q(t==frame[i]) for i in range(8)] for t,r in enumerate(R)]
precondition=[]
for t,u,z in output_basis:
    a,b=scatter[t].copy(),scatter[u].copy()
    scatter[t]=[x/2-y/z for x,y in zip(a,b)]
    scatter[u]=[x/2+y/z for x,y in zip(a,b)]
    precondition.extend([['scale',v+u,(1/z).numerator,(1/z).denominator,[]],
                         ['add',v+u,v+t,1,2,[]],['add',v+t,v+u,-1,1,[]]])

for r in range(len(cur)):climb(r,hyper(P[r-v]) if v<=r<2*v else FULL)
H[8]+=8;H[1]+=8;by['c'][8]+=8;by['c'][1]+=8
n=len(cur);Rcount=n-240
assert sum(r*z for r,z in H.items())==9*Rcount+240*8+72

def apply(event,matrix):
    if event[0]=='add':
        _,t,s,a,b,*_=event;q=Q(a,b)
        for j,x in list(matrix[s].items()):
            z=matrix[t].get(j,Q(0))+q*x
            if z:matrix[t][j]=z
            else:matrix[t].pop(j,None)
    else:
        _,t,a,b,*_=event;q=Q(a,b);matrix[t]={j:q*x for j,x in matrix[t].items()}
def inverse(e,F=None):
    e=copy.deepcopy(e)
    if e[0]=='add':e[3]*=-1
    else:e[2],e[3]=e[3],e[2]
    if F is not None:e[-1]=list(F)
    return e
cut=[]
for t,rr in enumerate(scatter):
    for i,q in enumerate(rr):
        if q:cut.append(['add',v+t,centers[i],q.numerator,q.denominator,None])
cleanup=[inverse(e,FULL) for e in reversed(A+B) if not v<=e[1]<2*v]

# Exact clean replay checks the changed decoder and restored source basis.
matrix=[{r:Q(1)} if r<v else {} for r in range(n)]
for e in A+cut+B+cleanup:apply(e,matrix)
assert all(matrix[r]==({r:Q(1)} if r<v else {r-v:Q(1)} if r<2*v else {}) for r in range(n))

m=73;T=8;L=9;W=7680+L*Rcount;globalH=Counter({r:z*L*T for r,z in H.items()})
for r in (16,8,32,8,48,8,48,32,16):globalH[r]+=240*T
globalH[1]+=L*Rcount
assert m*W-sum(r*z for r,z in globalH.items())==2496
# Discovery-only approximate display annotations use explicit left-to-right
# accumulation for stable results across Python sum() implementations. These
# floats are not acceptance inputs; complete profiles receive exact pricing.
low,high=0.,.003
for _ in range(60):
    q=(low+high)/2
    moment=0.0
    for r,z in globalH.items():moment+=r*z/(m*W)*(m/r)**q
    moment+=32*m*sum(globalH.values())/(10**16*W)*m**q
    if moment<1:low=q
    else:high=q
report={'status':'EXACT_CLEAN_FULL_WORD_DISCOVERY_NOT_ADMITTED',
        'h':9,'v':120,'R':Rcount,'cst':72,'local_profile':dict(sorted(H.items())),
        'global_profile':dict(sorted(globalH.items())),'m':m,'W':W,
        'complex_coarse_float':(low+high)/2,'baseline_b':0.000999388595603943,
        'gain_percent_float':100*((low+high)/2/0.000999388595603943-1),
        'scalar_operations_A':len(A),'scalar_operations_B':len(B),
        'borrowed_output_pairs':len(output_basis),'centre_ranks':list(map(len,center_frames)),'source_columns_exact':120,
        'source_and_helper_cleanup_exact_on_clean_columns':True,
        'retained_center_rows_exact':True,
        'remaining':['full arbitrary-dirt program and independent replay','exact complex phases and global template','finite invoice and coefficient lowering','two rational prices and outer assembly']}
full={'report':report,'ports':P,'root_lines':R,'A':A,'B':B,'centers':centers,'scatter':[[str(x) for x in r] for r in scatter],
      'cut':cut,'cleanup':cleanup,'precondition':precondition,'center_frames':center_frames}
(OUT/'FULL-WORD.json.gz').write_bytes(gzip.compress(json.dumps(full,sort_keys=True,separators=(',',':')).encode(),mtime=0))
(OUT/'FULL-DISCOVERY.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
