# R2 PoC: stay drop on #7617 (BIG/TAILS engine) + exact owned-park cleanup of the leftover dirty main rows at their final
# chart G, using rows ever resident at G (forward park: INIT at G, accumulate, deliver after the main's last read, dirty CLEAR).
import os,sys,json,gzip,threading,resource,time,collections as C
from fractions import Fraction as Q
os.environ['SUP_BASE']='inputs/ATTACK/STACK7616/best7616.json.gz'
def _w():
    while True:
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9>3.8: print('RSS bail',flush=True); os._exit(3)
        time.sleep(1)
threading.Thread(target=_w,daemon=True).start()
HERE=os.path.dirname(os.path.abspath(__file__));STAYS=json.loads(sys.argv[1]);outtag=sys.argv[2]
os.chdir('inputs/BIG/TAILS/code');sys.path.insert(0,'.')
from k3 import *
import circ
W8=json.load(gzip.open('inputs/ATTACK/PAIR/code/w7608.json.gz','rt')); nb8=circ.Base(W8)
def mapst(st,old):
    h,F,a,d=st; L=old.stays[h]; i=[x[1] for x in L].index(a)
    pf=L[i-1][0]; nf=L[i+1][0]; N=nb.stays[h]
    c=[j for j,x in enumerate(N) if 0<j<len(N)-1 and x[0]==F and N[j-1][0]==pf and N[j+1][0]==nf]
    if not c: return None
    j=min(c,key=lambda j:abs(N[j][1]-a)); x=N[j]; return (h,x[0],x[1],x[2])
def expected(W):
    n=W['public'];x=set(W['live']);y={r+112 for r in x};h=W['hosted']
    active={W['live'][i] for i in h['Dports']};sp=dict(zip(h['X2'],h['Y2']));al,be=Q(h['alpha']),Q(h['beta'])
    E=[]
    for r in range(n):
        e={r:Q(1)}
        if r in x and r not in active:e[r+112]=al
        if r in y:
            if r-112 in active:e[r-112]=Q(1)
            else:e={r-112:be,r:1+al*be}
        if r in sp:e[sp[r]]=Q(h['alpha2'])
        E.append(e)
    return E
def xreplay(W,charts):
    n=W['public'];N=n+W['owned_fields'];rows=[{r:Q(1)} if r<n else {} for r in range(N)];cur=list(W['initial'])+[None]*W['owned_fields']
    snaps=C.defaultdict(list);lastread={}
    for r in range(n):
        if cur[r] in charts:snaps[cur[r]].append((-1,r,dict(rows[r])))
    for i,e in enumerate(W['program']):
        op,r=e[0],e[1]
        if op=='MOVE':cur[r]=e[3]
        elif op=='INIT':rows[r]={};cur[r]=e[2]
        elif op=='CLEAR':rows[r]={};cur[r]=None;continue
        elif op=='SCALE':q=Q(e[2]);rows[r]={k:v*q for k,v in rows[r].items()}
        else:
            s,q=e[2],Q(e[3]);lastread[s]=i
            if op=='COPY':rows[r]={}
            R=rows[r]
            for k,v in rows[s].items():
                z=R.get(k,0)+q*v
                if z:R[k]=z
                else:R.pop(k,None)
        if cur[r] in charts and rows[r]:snaps[cur[r]].append((i,r,dict(rows[r])))
    return rows,snaps,lastread
def solve(snaps,J):
    "exact: find mu with sum mu_k row_k = J (dict). Gaussian elimination over Q on snapshot rows."
    basis=[]  # (pivot col, row dict, combo dict k->coef)
    def reduce(v,cmb):
        v=dict(v);cmb=dict(cmb)
        for pc,b,bc in basis:
            c=v.get(pc)
            if c:
                for k,x in b.items():
                    z=v.get(k,0)-c*x
                    if z:v[k]=z
                    else:v.pop(k,None)
                for k,x in bc.items():
                    z=cmb.get(k,0)-c*x
                    if z:cmb[k]=z
                    else:cmb.pop(k,None)
        return v,cmb
    for k,(i,r,row) in enumerate(snaps):
        v,cmb=reduce(row,{k:Q(1)})
        if v:
            pc=min(v);c=v[pc];v={a:b/c for a,b in v.items()};cmb={a:b/c for a,b in cmb.items()}
            basis.append((pc,v,cmb))
    v,cmb=reduce(J,{})
    if v:return None,len(basis)
    return {k:-x for k,x in cmb.items()},len(basis)   # sum mu_k row_k = J
def dyadic(q):return q.denominator&(q.denominator-1)==0 and abs(q)+1<2**16
for st in STAYS:
    t0=time.time();m=mapst(tuple(st[0]),nb8);mode=st[1]
    r=test([m],frames_mode=mode,K=300 if mode=='all' else 4000,owned=False,want=True)
    ed,W2,org,seeds,sv=make([m])
    evs=[]
    bad=False
    for (a,b,pos,F),v in zip(r.get('cands',[]),r.get('x',[])):
        if v:
            q=ratrec(v)
            if q is None:bad=True;break
            evs.append((pos,['ADD',a,b,str(q),F]))
    if bad:print(st,'ratrec fail');continue
    W3=insert(W2,evs);n3=W3['public'];E=expected(B0)
    rows,_,_=xreplay(W3,set())
    dirty=[p for p in range(n3) if rows[p]!=E[p]]
    G={p:W3['final'][p] for p in dirty}
    _,_,lr0=xreplay(W3,set())
    A={}
    for p in dirty:
        c=W3['initial'][p];hop=None
        for i,x in enumerate(W3['program']):
            if x[0]=='MOVE' and x[1]==p:
                if i<lr0.get(p,-1):c=x[3]
                elif hop is None:hop=i
        A[p]=(c,hop)
    rows,snaps,lastread=xreplay(W3,set(G.values())|{c for c,h in A.values()})
    print(st,m,'sv',round(sv,3),'dirty',[(p,G[p]) for p in dirty],flush=True)
    # owned rows / clear contents vs base are checked by accxfast later
    plan=[];ok=True
    for p in dirty:
        J={k:E[p].get(k,0)-rows[p].get(k,0) for k in set(E[p])|set(rows[p])};J={k:v for k,v in J.items() if v}
        mv=[x for x in W3['program'] if x[0]=='MOVE' and x[1]==p]
        moves_after=[i for i,x in enumerate(W3['program']) if x[0]=='MOVE' and x[1]==p and i>lastread.get(p,-1)]
        a,hop=A[p]
        S=[s for s in snaps[G[p]] if s[1]!=p]
        if hop is not None:S=S+[s for s in snaps[a] if s[1]!=p and s[0]<hop]
        if len(sys.argv)>3:S=S+[s for s in snaps[a] if s[1]!=p]  # diagnostic: time-ignored
        print('  p',p,'a',a,'hop',hop,'lastread',lastread.get(p))
        mu,rk=solve(S,J)
        if mu is None:print('  p',p,'NOT in span; rank',rk,'support',len(J));ok=False;break
        nd=[x for x in mu.values() if not dyadic(x)]
        print('  p',p,'G',G[p],'|J|',len(J),'rank',rk,'uses',len(mu),'snapshots; non-dyadic',len(nd),'moves after last read',len(moves_after))
        plan.append((p,G[p],[(S[k][0],S[k][1],x) for k,x in mu.items()]))
    if not ok:continue
    # build: owned park per dirty main; label free over [first use, end]
    prog=W3['program'];L=len(prog);n=W3['public'];NO=W3['owned_fields']
    busy=C.defaultdict(list);open_={}
    for i,e in enumerate(prog):
        if e[0]=='INIT':open_[e[1]]=i
        elif e[0]=='CLEAR':busy[e[1]].append((open_.pop(e[1]),i))
    ins=C.defaultdict(list);tail=[];used=[]
    for p,Gp,uses in plan:
        t0_=min(i for i,_,_ in uses)
        lab=next((o for o in range(n,n+NO) if o not in used and all(b<t0_ for a,b in busy[o])),None)
        if lab is None:print('  no free owned label from',t0_);ok=False;break
        used.append(lab)
        ins[t0_].append(['INIT',lab,Gp])
        for i,s,x in sorted(uses):ins[i].append(['ADD',lab,s,str(x),Gp])
        tail+=[['ADD',p,lab,'1',Gp],['CLEAR',lab,Gp]]
    if not ok:continue
    newp=[]
    for i in range(-1,L):
        if i>=0:newp.append(prog[i])
        newp.extend(ins.get(i,[]))
    W5=dict(W3);W5['program']=newp+tail
    rows5,_,_=xreplay(W5,set())
    bad5=[p for p in range(n) if rows5[p]!=E[p]]
    print('  parks',len(plan),'labels',used,'added events',len(newp)+len(tail)-L,'rows differing after parks',bad5,round(time.time()-t0,1),flush=True)
    if not bad5:
        fn=os.path.join(HERE,'hit_%s_%s.json.gz'%(outtag,'_'.join(map(str,m))))
        with gzip.GzipFile(fn,'wb',mtime=0) as f:f.write(json.dumps(W5,separators=(',',':')).encode())
        print('  SAVED',fn,flush=True)
