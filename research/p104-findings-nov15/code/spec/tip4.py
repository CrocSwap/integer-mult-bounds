# R2 class (b): per stay (BIG/TAILS engine on #7617, corrected word W3m, mod P), per dirty public row p (final chart G,
# a = chart at p's last read, hop = p's move after last read):
#  PARK  = span(rows at G, any time) + span(rows at a, before hop)          [owned forward parks: exact, kappa 0]
#  FRESH = PARK + span(rows at charts >= a, after lastread(p))             [superset of the sandwich supply of ANY
#          fresh-public-register network delivering with col_p final: Down(u,td) & Up(u,td), u in {a,G}, td>=lastread]
# J_p in PARK / FRESH?  Stay feasible iff all dirty rows pass (owned/clear dirt reported separately).
import gzip,json,sys,collections as C,numpy as np,time,resource
from fractions import Fraction as Q
from flint import nmod_mat
P=2**31-1
import threading,os
def _wd():
    while True:
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9>3.8:print('RSS>3.8GB bail',flush=True);os._exit(3)
        time.sleep(1)
threading.Thread(target=_wd,daemon=True).start()
B=json.load(gzip.open('../../ATTACK/STACK7616/best7616.json.gz','rt'));dim=[len(b) for b in B['frames']]
def span(b):
    s={0}
    for v in b:s|={x^v for x in s}
    return frozenset(s)
SP=[span(b) for b in B['frames']]
cache={}
def qm(s):
    v=cache.get(s)
    if v is None:q=Q(s);v=cache[s]=q.numerator%P*pow(q.denominator%P,P-2,P)%P
    return v
def rank(rows):
    if not rows:return 0
    A=np.array(rows,dtype=np.int64)%P;A=A[:,A.any(0)]
    return nmod_mat(A.shape[0],A.shape[1],A.ravel().tolist(),P).rank()
def test(W,dirty):
    n=W['public'];NO=W['owned_fields'];N=n+NO;prog=W['program']
    lastread={};mv=C.defaultdict(list)
    for i,e in enumerate(prog):
        if e[0] in('ADD','COPY'):lastread[e[2]]=i
        elif e[0]=='MOVE':mv[e[1]].append((i,e[3]))
    spec={}
    for d in dirty:
        if d['kind']!='pub':continue
        p=d['r'];lr=lastread.get(p,-1);a=W['initial'][p];hop=None
        for i,f in mv[p]:
            if i<lr:a=f
            elif hop is None:hop=i
        spec[p]=(a,d['G'],hop,lr)
    X=np.zeros((N,n),dtype=np.int64);X[np.arange(n),np.arange(n)]=1
    cur=list(W['initial'])+[None]*NO
    arrG=C.defaultdict(lambda:-1)
    for p in spec:
        for i,f_ in mv[p]:
            if f_==spec[p][1]:arrG[p]=i
    # windows per p: u=a (if hop): [lr,hop]; u=G: [max(lr,arrG),end]
    WIN={}
    for p,(a,G,hop,lr) in spec.items():
        L_=[(a,lr,hop)] if hop is not None else []
        WIN[p]=L_
    PK={p:[] for p in spec};DN={(p,k):[] for p in spec for k in range(len(WIN[p]))};UPk={(p,k):[] for p in spec for k in range(len(WIN[p]))}
    dn={};upc={}
    for p in spec:
        for k,(u,tl,th) in enumerate(WIN[p]):
            dn[(p,k)]={c for c in range(len(SP)) if SP[c]<=SP[u]};upc[(p,k)]={u}
    def arrive(i,r):
        c=cur[r]
        if c is None or not X[r].any():return
        v=None
        for p,(a,G,hop,lr) in spec.items():
            if c==G or (c==a and (hop is None or i<hop)):
                v=X[r].astype(np.uint32) if v is None else v;PK[p].append(v)
            for k,(u,tl,th) in enumerate(WIN[p]):
                if i<th and c in dn[(p,k)]:v=X[r].astype(np.uint32) if v is None else v;DN[(p,k)].append(v)
                if i>tl and c in upc[(p,k)]:v=X[r].astype(np.uint32) if v is None else v;UPk[(p,k)].append(v)
    at=C.defaultdict(list)
    for p in spec:
        for k,(u,tl,th) in enumerate(WIN[p]):at[tl].append((p,k))
    def present(i):
        for p,k in at.get(i,()):
            for r in range(N):
                if cur[r] in upc[(p,k)] and X[r].any():UPk[(p,k)].append(X[r].astype(np.uint32))
    for r in range(n):arrive(-1,r)
    present(-1)
    for i,e in enumerate(prog):
        op,r=e[0],e[1]
        if op=='MOVE':cur[r]=e[3];arrive(i,r)
        elif op=='INIT':X[r]=0;cur[r]=e[2]
        elif op=='CLEAR':X[r]=0;cur[r]=None
        elif op=='SCALE':X[r]=X[r]*qm(e[2])%P
        elif op=='COPY':X[r]=qm(e[3])*X[e[2]]%P
        elif op=='ADD':X[r]=(X[r]+qm(e[3])*X[e[2]])%P
        present(i)
    out={}
    for d in dirty:
        if d['kind']!='pub':continue
        p=d['r'];J=np.zeros(n,dtype=np.int64);J[d['cols']]=d['coef']
        pk=list({v.tobytes():v for v in PK[p]}.values())
        inter=[]
        for k in range(len(WIN[p])):
            A=basis(DN[(p,k)]);Bm=basis(UPk[(p,k)])
            inter+=intersect(A,Bm)
        r0=rank(pk);r1=rank(pk+[J]);r2=rank(pk+inter);r3=rank(pk+inter+[J])
        out[p]=dict(park=r1==r0,fresh=r3==r2,rk=(r0,r2,len(inter)),hop=spec[p][2] is not None)
    return out
def basis(rows):
    if not rows:return np.zeros((0,1),dtype=np.int64)
    A=np.array(list({v.tobytes():v for v in rows}.values()),dtype=np.int64)%P
    M=nmod_mat(A.shape[0],A.shape[1],A.ravel().tolist(),P).rref()[0]
    rk=0
    R=[]
    for i in range(M.nrows()):
        row=[int(M[i,j]) for j in range(M.ncols())]
        if not any(row):break
        R.append(row)
    return np.array(R,dtype=np.int64).reshape(len(R),A.shape[1])
def intersect(A,Bm):
    if not len(A) or not len(Bm):return []
    M=np.vstack([A,(-Bm)%P])  # rows; find (alpha,beta) with alpha A - beta B... left nullspace
    T=M.T.copy()
    X_,nul=nmod_mat(T.shape[0],T.shape[1],T.ravel().tolist(),P).nullspace()
    out=[]
    for j in range(nul):
        al=np.array([int(X_[i,j]) for i in range(len(A))],dtype=np.int64)
        v=np.zeros(A.shape[1],dtype=np.int64)
        for i in np.nonzero(al)[0]:v=(v+int(al[i])*A[i])%P
        if v.any():out.append(v.astype(np.uint32))
    return out
L=[json.loads(l) for l in open(sys.argv[1]) if l.count('"kind": "pub"')<=6];lim=int(sys.argv[3]) if len(sys.argv)>3 else 10**9
done=set()
try:
    for l in open(sys.argv[2]):done.add(json.loads(l)['tag'])
except FileNotFoundError:pass
for x in [x for x in L if sum(d["kind"]=="pub" for d in x["dirty"])<=6][:lim]:
    if x['tag'] in done:continue
    t0=time.time()
    W=json.load(gzip.open('outall/w3m_%s.json.gz'%x['tag'],'rt'))
    o=test(W,x['dirty'])
    kinds=C.Counter(d['kind'] for d in x['dirty'])
    rec=dict(tag=x['tag'],st=x['st'],sv=x['sv'],kinds=dict(kinds),npub=len(o),park=all(v['park'] for v in o.values()),
             fresh=all(v['fresh'] for v in o.values()),npark=sum(v['park'] for v in o.values()),nfresh=sum(v['fresh'] for v in o.values()),
             detail={str(k):v for k,v in list(o.items())[:6]},sec=round(time.time()-t0,1),gb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9)
    open(sys.argv[2],'a').write(json.dumps(rec)+'\n')
    print(rec['tag'],rec['kinds'],'park',rec['npark'],'fresh',rec['nfresh'],'/',rec['npub'],rec['sec'],'s',round(rec['gb'],2),'GB',flush=True)
