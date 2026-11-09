"""Chain-nested root caller, exact construction (Python 3.12, standard library).

Root fields A, f_0..f_{gL-1}, h_0..h_{gR-1}, plus one empty field when the field count is odd (n even).
Left site i: x = A + f_i + 2 sum_{j<i} f_j, y = A* - f_i*.  Right site m: x = -A + h_m + 2 sum_{l>m} h_l, y = A* + h_m*.
Each inner field carries one merged idle over the consecutive sites that do not touch it.
build(sL, sR) takes child sizes in time order; with dyadic=False (default) every pivot is +-1, so all ADD
coefficients are integers and all SCALE factors are +-1 (integral transfer); dyadic=True restores the
power-of-two pivots, which produce 1/2 and 2 factors (used only as a negative control).
"""
import sys,json
from fractions import Fraction as Q
from copy import deepcopy

def need(ok,message):
    if not ok:raise ValueError(message)
def eye(n):return [[Q(int(i==j)) for j in range(n)] for i in range(n)]
def inverse(a):
    n=len(a);rows=[[Q(x) for x in row]+idr for row,idr in zip(a,eye(n))]
    for j in range(n):
        k=next((k for k in range(j,n) if rows[k][j]),None);need(k is not None,'Nonsingular rational matrix')
        rows[j],rows[k]=rows[k],rows[j];v=rows[j][j];rows[j]=[x/v for x in rows[j]]
        for k in range(n):
            if k!=j:
                v=rows[k][j];rows[k]=[x-v*y for x,y in zip(rows[k],rows[j])]
    return [row[n:] for row in rows]
DYADIC=False
def unit(q):
    q=Q(q)
    if not DYADIC:return q in (1,-1)
    return q and abs(q.numerator)&(abs(q.numerator)-1)==0 and q.denominator&(q.denominator-1)==0
def thin_vectors(gL,gR,n,fL,fR,A,E):
    sL,sR=gL%2,gR%2
    def vec(a,u,p=0,q=0):
        x=[Q(0)]*n;y=[Q(0)]*n
        x[A]=Q(a);y[A]=Q(u)
        for i,f in enumerate(fL): x[f]=Q(a+1);y[f]=Q((1-u)*(-1)**i)
        for r,h in enumerate(reversed(fR)): x[h]=Q(1-a);y[h]=Q((u-1)*(-1)**r)
        if E is not None: x[E]=Q(q);y[E]=Q(p)
        return x,y
    if sL==sR==1:   # g=a'(2-u)+pq'
        return [vec(0,1,0,1),vec(-1,2,1,0),vec(-1,3,1,-1)]
    if sL==sR==0:   # g=u a'+pq'
        return [vec(0,1,0,1),vec(-1,0,1,0),vec(-1,-1,1,-1)]
    if sL==1:  # g=a'+1-u
        return [vec(0,1),vec(-1,0)]
    return [vec(0,1),vec(1,2)] # g=u-1+a'
def complete(x,y,n):
    a=next(f for f in range(n) if y[f] and unit(y[f]) and True)
    for a in [f for f in range(n) if y[f] and unit(y[f])]:
        for b in [f for f in range(n) if x[f] and unit(x[f]) and f!=a]:
            w=[Q(0)]*n;w[a]=1/y[a]
            z=[Q(0)]*n;z[b]=1/x[b]
            # need z x=1,z w=0,y w=1,y x=0
            cols={0:x,1:w};rows={0:z,1:y}
            oth=[f for f in range(n) if f not in(a,b)]
            c=[[Q(0)]*n for _ in range(n)]
            for i in range(n): c[i][0]=x[i];c[i][1]=w[i]
            for k,f in enumerate(oth):
                v=[Q(int(i==f)) for i in range(n)]
                v=[v[i]-y[f]*w[i]-z[f]*x[i] for i in range(n)]
                for i in range(n): c[i][k+2]=v[i]
            return c
    raise ValueError('no unit completion')
def build(sL,sR,dyadic=False):
    global DYADIC
    DYADIC=dyadic
    gL,gR=len(sL),len(sR);nf=1+gL+gR;e=nf%2;n=nf+e
    A=0;fL=list(range(1,1+gL));fR=list(range(1+gL,1+gL+gR));E=nf if e else None
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
            need(unit(a[j][j]),'Exact dyadic unit pivot')
            q=1/a[j][j]
            if q!=1:a[j]=[q*x for x in a[j]];ops.append(['SCALE',j,str(q)])
            for k in range(j):
                if a[k][j]:
                    q=-a[k][j];a[k]=[x+q*y for x,y in zip(a[k],a[j])];ops.append(['ADD',k,j,str(q)])
        need(a==eye(n),'basis')
        for x in reversed(ops):
            if x[0]=='ADD':x[-1]=str(-Q(x[-1]))
            elif x[0]=='SCALE':x[-1]=str(1/Q(x[-1]))
            emit(*x)
    def label(t):
        nonlocal stage
        if t==1:stage+=1;return {'stage':stage,'stages':[stage]}
        a,b=map(label,t);return {'left':a,'right':b,'stages':a['stages']+b['stages']}
    def shape(m): return 1 if m==1 else [shape(m//2),shape(m-m//2)]
    def query(x,y): emit('LAMBDA',x,-1);emit('QUERY',x,y,-1);emit('LAMBDA',x,1)
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
    def basis(colsx,w,lines,rest):
        # columns: x,w,phi...,rest unit vectors. returns matrix c
        cols=[colsx,w]+lines+rest
        return [[cols[j][i] for j in range(n)] for i in range(n)]
    def ev(idx,v=1):
        r=[Q(0)]*n;r[idx]=Q(v);return r
    def add(*pairs):
        r=[Q(0)]*n
        for i,v in pairs:r[i]+=Q(v)
        return r
    fieldstages={}
    for i in range(gL):
        x=add((A,1),(fL[i],1),*[(fL[j],2) for j in range(i)])
        w=add((A,1),*[(fL[j],2) for j in range(i)])
        phis=[ev(fL[j]) for j in range(i)]
        used={A,fL[i]}|{fL[j] for j in range(i)}
        rest=[ev(f) for f in range(n) if f not in used]
        c=basis(x,w,phis,rest);mix(inverse(c))
        supplier(treesL[i],0,1);emit('ADD',0,1,'-1')
        if i>=1:
            # line j=i: phi=f_{i-1} is at register 2+i-1
            st=[t for tr in treesL[i:] for t in tr['stages']]
            emit('IDLE_ONE',2+i-1,st)
        mix(c)
    for x,y in thin_vectors(gL,gR,n,fL,fR,A,E):
        c=complete(x,y,n);mix(inverse(c));query(0,1);emit('ADD',0,1,'-1');mix(c)
    for m in range(gR):
        x=add((A,-1),(fR[m],1),*[(fR[l],2) for l in range(m+1,gR)])
        w=add((A,1),*[(fR[l],-2) for l in range(m+1,gR)])
        lines=[ev(fR[l]) for l in range(m+1,gR)]
        used={A,fR[m]}|{fR[l] for l in range(m+1,gR)}
        rest=[ev(f) for f in range(n) if f not in used]
        c=basis(x,w,lines,rest);mix(inverse(c))
        supplier(treesR[m],0,1);emit('ADD',0,1,'-1')
        if m==0:
            for j in range(gR-1):
                st=[t for tr in treesR[:j+1] for t in tr['stages']]
                emit('IDLE_ONE',2+j,st)
        mix(c)
    allst=[t for tr in treesL+treesR for t in tr['stages']]
    targets[A]=[-1,allst]
    for i,f in enumerate(fL): targets[f]=[-1,[t for tr in treesL[i:] for t in tr['stages']]]
    for m,h in enumerate(fR): targets[h]=[-1,[t for tr in treesR[:m+1] for t in tr['stages']]]
    if E is not None: targets[E]=[-1,[]]
    for r in range(next_role):emit('LAMBDA',r,-1)
    diagonal=[[targets[r][0],0]+[int(j in targets[r][1]) for j in range(1,stage+1)] for r in range(next_role)]
    return {'schema':'chain-nested-root/1','roles':next_role,'stages':stage,'ambient_rank':9+8*stage,'events':events,'diagonal':diagonal,'nodes':nodes,'n':n,'sL':sL,'sR':sR}
