"""Chain-nested shortest root and its literal caller; deterministic, no search at replay.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
The binary query supplier and the ordinary-basis elimination follow the retained
caller by Cinna Davis, Ali Romman, thu-nmrc and zxv (retained/caller/caller.py);
whole common idles follow thu-nmrc (#6716).

Shape: child sizes sL (outer to centre) and sR (centre to outer).  Fields are A,
f_0..f_{gL-1}, h_0..h_{gR-1} and, when the count is odd, one empty field E.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from algebra import add,eye,inverse,multiply,need

SHAPE=([1]*9,[1]*9)
GATE=([4,4,1],[1,4,4])

def unit(q):
    # Integral form: pivots are +-1 only, so the ordinary caller has integer scalars.
    return Q(q) in (1,-1)

def fields(sL,sR):
    gL,gR=len(sL),len(sR)
    nf=1+gL+gR;e=nf%2
    return {'n':nf+e,'A':0,'f':list(range(1,1+gL)),'h':list(range(1+gL,1+gL+gR)),'E':nf if e else None}

def vector(n,*pairs):
    v=[Q(0)]*n
    for i,c in pairs:v[i]+=Q(c)
    return v

def thin_vectors(sL,sR):
    """Closed-form thin queries, ordered; see PROOF.md section 2."""
    F=fields(sL,sR);n,A,f,h,E=F['n'],F['A'],F['f'],F['h'],F['E']
    def vec(a,u,p=0,q=0):
        x=[Q(0)]*n;y=[Q(0)]*n
        x[A]=Q(a);y[A]=Q(u)
        for i,j in enumerate(f):x[j]=Q(a+1);y[j]=Q((1-u)*(-1)**i)
        for r,j in enumerate(reversed(h)):x[j]=Q(1-a);y[j]=Q((u-1)*(-1)**r)
        if E is not None:x[E]=Q(q);y[E]=Q(p)
        return x,y
    a,b=len(f)%2,len(h)%2
    if a and b:return [vec(0,1,0,1),vec(-1,2,1,0),vec(-1,3,1,-1)]
    if not a and not b:return [vec(0,1,0,1),vec(-1,0,1,0),vec(-1,-1,1,-1)]
    if a:return [vec(0,1),vec(-1,0)]
    return [vec(0,1),vec(1,2)]

def sites(sL,sR):
    """Ordered root: (x,y,mask or None,kind,index)."""
    F=fields(sL,sR);n,A,f,h=F['n'],F['A'],F['f'],F['h']
    out=[]
    for i in range(len(f)):
        x=vector(n,(A,1),(f[i],1),*[(f[j],2) for j in range(i)])
        y=vector(n,(A,1),(f[i],-1))
        out.append((x,y,{A,*f[:i+1]},'L',i))
    for j,(x,y) in enumerate(thin_vectors(sL,sR)):out.append((x,y,None,'Q',j))
    for m in range(len(h)):
        x=vector(n,(A,-1),(h[m],1),*[(h[l],2) for l in range(m+1,len(h))])
        y=vector(n,(A,1),(h[m],1))
        out.append((x,y,{A,*h[m:]},'R',m))
    return out

def lines(sL,sR):
    """Idle lines: (phi,gamma,sites-of-group covered,side)."""
    F=fields(sL,sR);n,A,f,h=F['n'],F['A'],F['f'],F['h']
    out=[]
    for j in range(1,len(f)):
        out.append((vector(n,(f[j-1],1)),vector(n,(f[j-1],1),(A,-2)),list(range(j,len(f))),'L'))
    for j in range(len(h)-1):
        out.append((vector(n,(h[j+1],1)),vector(n,(h[j+1],1),(A,2)),list(range(0,j+1)),'R'))
    return out

def dot(a,b):return sum(u*v for u,v in zip(a,b))

def verify_root(sL,sR):
    """Exact algebra of the root: sign Gram, alternating sum, endpoint, commutants, chain merge."""
    F=fields(sL,sR);n=F['n'];S=sites(sL,sR);I=eye(n)
    need(n%2==0 and len(S)==n+1,'Shortest root: n even and n+1 queries')
    for i,(xi,yi,*_) in enumerate(S):
        for j,(xj,*_) in enumerate(S):
            need(dot(yi,xj)==(i>j)-(i<j),'Sign Gram matrix')
    need(all(sum((-1)**k*s[0][i] for k,s in enumerate(S))==0 for i in range(n)),'Alternating sum of the x vectors vanishes')
    K=[r[:] for r in I];prefix=[]
    for x,y,*_ in S:
        R=[[u*v for v in y] for u in x]
        need(any(any(r) for r in R) and multiply(R,R)==[[Q(0)]*n for _ in range(n)],'Nonzero square-zero query')
        K=multiply(add(I,R,-2),K);prefix.append(K)
    need(K==add([[Q(0)]*n for _ in range(n)],I,-1),'Complete shortest-root endpoint -I')
    fulls=0
    for k,(x,y,mask,kind,idx) in enumerate(S):
        if mask is None:continue
        P=[[Q(int(a==b and a in mask)) for b in range(n)] for a in range(n)]
        R=[[u*v for v in y] for u in x]
        need(multiply(P,R)==R and multiply(R,P)==R,'Query inside its stage support')
        need(multiply(P,prefix[k])==multiply(prefix[k],P),'Stage support commutes with its query prefix')
        fulls+=1
    need(fulls==len(sL)+len(sR),'One full site per child')
    # Chain merge: each line is dual, inside the supports it covers, and killed by the sites it crosses.
    group={'L':[s for s in S if s[3]=='L'],'R':[s for s in S if s[3]=='R']}
    L=lines(sL,sR)
    for a,(phi,gamma,cover,side) in enumerate(L):
        need(dot(gamma,phi)==1,'Unit dual idle line')
        for b,(phib,gammab,_,sideb) in enumerate(L):
            if a!=b:need(dot(gamma,phib)==0,'Distinct lines are dual-orthogonal')
        for i in cover:
            x,y,mask,_,_=group[side][i]
            need(dot(y,phi)==0 and dot(gamma,x)==0,'Line killed by every site it crosses')
            need(all(not v or c in mask for c,v in enumerate(phi)) and all(not v or c in mask for c,v in enumerate(gamma)),'Line inside each support it crosses')
    # Exact decomposition of each stage projector into its active plane and its idle lines.
    for side,g in group.items():
        for i,(x,y,mask,_,_) in enumerate(g):
            P=[[Q(int(a==b and a in mask)) for b in range(n)] for a in range(n)]
            active=add(P,[[Q(0)]*n for _ in range(n)])
            count=0
            for phi,gamma,cover,sd in L:
                if sd==side and i in cover:
                    active=add(active,[[u*v for v in gamma] for u in phi],-1);count+=1
            need(count==len(mask)-2,'Idle lines fill the support outside the active plane')
            need(multiply(active,active)==active and multiply(active,[[u] for u in x])==[[u] for u in x],'Active projector fixes x')
            need(multiply([y],active)==[y],'Active projector fixes y')
            need(sum(active[c][c] for c in range(n))==2,'Rank-two active plane')
    return {'fields':n,'queries':len(S),'full_sites':fulls,'thin_queries':len(S)-fulls,'idle_lines':len(L),
            'stage_supports':[len(s[2]) for s in S if s[2]],'sign_gram_entries':len(S)**2}

def complete(x,y,n):
    for a in [f for f in range(n) if y[f] and unit(y[f])]:
        for b in [f for f in range(n) if x[f] and unit(x[f]) and f!=a]:
            w=[Q(0)]*n;w[a]=1/y[a]
            z=[Q(0)]*n;z[b]=1/x[b]
            oth=[f for f in range(n) if f not in(a,b)]
            c=[[Q(0)]*n for _ in range(n)]
            for i in range(n):c[i][0]=x[i];c[i][1]=w[i]
            for k,f in enumerate(oth):
                v=[Q(int(i==f)) for i in range(n)]
                v=[v[i]-y[f]*w[i]-z[f]*x[i] for i in range(n)]
                for i in range(n):c[i][k+2]=v[i]
            return c
    raise ValueError('No unit completion of a thin query')

def build(sL,sR):
    F=fields(sL,sR);n,A,fL,fR,E=F['n'],F['A'],F['f'],F['h'],F['E'];gL,gR=len(fL),len(fR)
    events=[];nodes=[];stage=0;next_role=n;targets={}
    def emit(op,*a):events.append([op,*a])
    def mix(rows):
        a=deepcopy(rows);ops=[]
        for j in range(n):
            while True:
                k=next(k for k in range(j,n) if a[k][j])
                if k!=j:a[j],a[k]=a[k],a[j];ops.append(['SWAP',j,k])
                k=next((k for k in range(j+1,n) if a[k][j]),None)
                if k is None:break
                q=a[k][j]//a[j][j]
                if q:a[k]=[x-q*y for x,y in zip(a[k],a[j])];ops.append(['ADD',k,j,str(-q)])
                if a[k][j]:a[j],a[k]=a[k],a[j];ops.append(['SWAP',j,k])
            need(unit(a[j][j]),'Exact integral unit pivot')
            q=1/a[j][j]
            if q!=1:a[j]=[q*x for x in a[j]];ops.append(['SCALE',j,str(q)])
            for k in range(j):
                if a[k][j]:
                    q=-a[k][j];a[k]=[x+q*y for x,y in zip(a[k],a[j])];ops.append(['ADD',k,j,str(q)])
        need(a==eye(n),'Complete exact integral basis elimination')
        for x in reversed(ops):
            if x[0]=='ADD':x[-1]=str(-Q(x[-1]))
            elif x[0]=='SCALE':x[-1]=str(1/Q(x[-1]))
            emit(*x)
    def label(t):
        nonlocal stage
        if t==1:stage+=1;return {'stage':stage,'stages':[stage]}
        a,b=map(label,t);return {'left':a,'right':b,'stages':a['stages']+b['stages']}
    def shape(m):return 1 if m==1 else [shape(m//2),shape(m-m//2)]
    def query(x,y):emit('LAMBDA',x,-1);emit('QUERY',x,y,-1);emit('LAMBDA',x,1)
    def supplier(t,x,y):
        nonlocal next_role
        if 'stage'in t:
            emit('LAMBDA',x,-1);emit('LOCAL',t['stage'],y,x);emit('LAMBDA',x,1);return
        a,b=next_role,next_role+1;next_role+=2;st=t['stages'];nodes.append({'roles':[a,b],'stages':st})
        emit('SWAP',x,b);emit('SWAP',y,a);emit('SWAP',a,b)
        emit('ADD',x,a,'1');emit('ADD',b,y,'-1');query(a,b)
        emit('ADD',b,y,'1');emit('ADD',x,a,'-1');emit('IDLE',a,b,st)
        emit('SCALE',y,'-1');supplier(t['left'],y,x);emit('SCALE',y,'-1');supplier(t['right'],x,y)
        emit('ADD',x,a,'1');emit('SCALE',a,'-1');emit('ADD',a,x,'1');emit('SWAP',y,b);emit('SCALE',b,'-1');emit('ADD',b,y,'1')
        targets[a],targets[b]=[-1,st],[-1,st]
    treesL=[label(shape(s)) for s in sL];treesR=[label(shape(s)) for s in sR]
    def basis(colsx,w,cols,rest):
        full=[colsx,w]+cols+rest
        return [[full[j][i] for j in range(n)] for i in range(n)]
    def ev(i):return vector(n,(i,1))
    for i in range(gL):
        x=vector(n,(A,1),(fL[i],1),*[(fL[j],2) for j in range(i)])
        w=vector(n,(A,1),*[(fL[j],2) for j in range(i)])
        used={A,fL[i]}|set(fL[:i])
        c=basis(x,w,[ev(fL[j]) for j in range(i)],[ev(f) for f in range(n) if f not in used]);mix(inverse(c))
        supplier(treesL[i],0,1);emit('ADD',0,1,'-1')
        if i>=1:
            emit('IDLE_ONE',2+i-1,[t for tr in treesL[i:] for t in tr['stages']])
        mix(c)
    for x,y in thin_vectors(sL,sR):
        c=complete(x,y,n);mix(inverse(c));query(0,1);emit('ADD',0,1,'-1');mix(c)
    for m in range(gR):
        x=vector(n,(A,-1),(fR[m],1),*[(fR[l],2) for l in range(m+1,gR)])
        w=vector(n,(A,1),*[(fR[l],-2) for l in range(m+1,gR)])
        used={A,fR[m]}|set(fR[m+1:])
        c=basis(x,w,[ev(fR[l]) for l in range(m+1,gR)],[ev(f) for f in range(n) if f not in used]);mix(inverse(c))
        supplier(treesR[m],0,1);emit('ADD',0,1,'-1')
        if m==0:
            for j in range(gR-1):
                emit('IDLE_ONE',2+j,[t for tr in treesR[:j+1] for t in tr['stages']])
        mix(c)
    targets[A]=[-1,[t for tr in treesL+treesR for t in tr['stages']]]
    for i,f in enumerate(fL):targets[f]=[-1,[t for tr in treesL[i:] for t in tr['stages']]]
    for m,h in enumerate(fR):targets[h]=[-1,[t for tr in treesR[:m+1] for t in tr['stages']]]
    if E is not None:targets[E]=[-1,[]]
    for r in range(next_role):emit('LAMBDA',r,-1)
    diagonal=[[targets[r][0],0]+[int(j in targets[r][1]) for j in range(1,stage+1)] for r in range(next_role)]
    return {'schema':'chain-nested-root/1','roles':next_role,'stages':stage,'ambient_rank':9+8*stage,
            'events':events,'diagonal':diagonal,'nodes':nodes,'n':n,'sL':list(sL),'sR':list(sR)}

def outer_formula(sL,sR):
    """Per-port outer histograms from the shape alone; compared with the literal word by pricing.py."""
    T,P=Counter(),Counter()
    def nodes(m):
        if m==1:return
        T[8*m+1]+=2;P[8*m]+=2
        nodes(m//2);nodes(m-m//2)
    for m in list(sL)+list(sR):nodes(m)
    N=sum(sL)+sum(sR)
    T[8*N+1]+=1
    for i in range(len(sL)):
        T[8*sum(sL[i:])+1]+=1
        if i>=1:P[8*sum(sL[i:])]+=1
    for m in range(len(sR)):
        T[8*sum(sR[:m+1])+1]+=1
        if m<len(sR)-1:P[8*sum(sR[:m+1])]+=1
    F=fields(sL,sR)
    if F['E'] is not None:T[1]+=1
    internal=sum(m-1 for m in list(sL)+list(sR))
    P[1]+=len(thin_vectors(sL,sR))+internal
    return T,P
