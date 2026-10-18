# ZPIN: zero-aware pinning model (extra zeros allowed on non-orthogonal pairs). See THEORY.md for the proof of every rule.
# Element e=(kind,u), kind 'r' (row u: alpha_u, x_u) or 'c' (column u: beta_u, y_u). Coordinates i in T(u) (frame F-tetrad).
# alpha_u(i)=M[u,F_i]/M[F_i,F_i], beta_s(i)=M[F_i,s]; M_us = sum_{i in T(u)∩T(s)} alpha_u(i)beta_s(i) + x_u y_s.
# Variables are registered by semantic key, so soundtest.py can evaluate every variable from exact data.
import sys, itertools, os
from blib import *

class Model:
    def __init__(s, Fr, scope='c', mut=(), rules=None):
        s.Fr=tuple(Fr); s.scope=scope; s.mut=set(mut); s.K=None
        if isinstance(scope,str) and scope.startswith('k'): s.K=int(scope[1:]); s.scope='k'; scope='k'
        s.reg={}; s.rev=[]; s.cl=[]; s.nv=0; s.defs={}; s.gsets={}; s.hv=[]
        s.TT=tetrads(s.Fr); s.tets=list(s.TT); s.off=[u for u in range(N) if u not in s.Fr]
        s.Tof={u:T for T in s.tets for u in s.TT[T]}
        s.pairs=[frozenset(p) for p in itertools.combinations(s.Fr,2)]
        s.u0=None
        if scope in ('a','z'):
            f0=s.Fr[0]; s.u0=[u for u in s.off if f0 in s.Tof[u]][0]; s.f0=f0
        elif scope=='b':
            s.u0=s.off[0]
        s.build()
    # ---------- registry
    def v(s,key):
        k=s.reg.get(key)
        if k is None:
            s.nv+=1; k=s.nv; s.reg[key]=k; s.rev.append(key)
        return k
    def add(s,tag,lits): s.cl.append((tag,list(lits)))
    def sg(s,u,a,b): return 1 if dot(E[u],E[a])*dot(E[u],E[b])>0 else -1
    # element accessors
    def NZ(s,e,i): return s.v(('nz',e[0],e[1],i))
    def XS(s,e): return s.v(('x',e[0],e[1]))
    def pk(s,p): return tuple(sorted(p))
    def ZP(s,e,p):
        key=('zp',e[0],e[1],s.pk(p))
        if key not in s.reg:
            z=s.v(key); a,b=s.pk(p); na,nb=s.NZ(e,a),s.NZ(e,b)
            s.add('def',[-z,-na]); s.add('def',[-z,-nb]); s.add('def',[z,na,nb])
        return s.reg[key]
    def NZV(s,e,p):
        key=('nzv',e[0],e[1],s.pk(p))
        if key not in s.reg:
            n=s.v(key); z=s.ZP(e,p); x=s.XS(e)
            s.add('def',[n,z]); s.add('def',[n,-x]); s.add('def',[-n,-z,x])   # n <=> (not zp) or x
        return s.reg[key]
    def EQ(s,p,e1,e2):
        if e1>e2: e1,e2=e2,e1
        return s.reg[('E',s.pk(p),e1,e2)]
    def RQ(s,kind,i,u,w):
        if u>w: u,w=w,u
        return s.reg[('RQ',kind,i,u,w)]
    def build(s):
        Fr,TT,tets,off,Tof=s.Fr,s.TT,s.tets,s.off,s.Tof
        sg=s.sg; add=s.add
        # base nz vars + scope units
        for u in off:
            for kind in 'rc':
                for i in Tof[u]:
                    n=s.NZ((kind,u),i)
                    if s.scope=='n': add('scope',[n])
                    elif s.scope=='z':
                        if (kind=='r' and u==s.u0 and i==s.f0): add('scope',[-n])
                    elif s.scope=='a':
                        add('scope',[-n] if (kind=='r' and u==s.u0 and i==s.f0) else [n])
                    elif s.scope=='b':
                        if not (kind=='r' and u==s.u0): add('scope',[n])
        nonon=lambda u,t: (s.scope in ('a','n')) or (s.scope=='b' and u!=s.u0)
        if 'NONall' in s.mut: nonon=lambda u,t: True
        # ---- E variables per pair, with axioms
        for p in s.pairs:
            a,b=s.pk(p)
            el=[('r',u) for u in off if p<=Tof[u]]+[('c',u) for u in off if p<=Tof[u]]
            V={}
            for e1,e2 in itertools.combinations(el,2):
                V[(e1,e2)]=s.v(('E',(a,b),min(e1,e2),max(e1,e2)))
            for (e1,e2),var in V.items():
                add('E1',[-var,-s.ZP(e1,p)]); add('E1',[-var,-s.ZP(e2,p)])
                if e1[0]==e2[0]:   # same kind: proportional vectors => same zero pattern
                    for i in (a,b):
                        add('E2',[-var,-s.NZ(e1,i),s.NZ(e2,i)]); add('E2',[-var,s.NZ(e1,i),-s.NZ(e2,i)])
                else:              # row/col: point [al_a:al_b] = [be_b:-be_a]
                    r,c=(e1,e2) if e1[0]=='r' else (e2,e1)
                    for i,j in ((a,b),(b,a)):
                        add('E2',[-var,-s.NZ(r,i),s.NZ(c,j)]); add('E2',[-var,s.NZ(r,i),-s.NZ(c,j)])
                # E3: same P0 / P-inf type => equal
                for (i,j) in ((a,b),(b,a)):
                    if e1[0]==e2[0]: l1=[s.NZ(e1,i),-s.NZ(e1,j),s.NZ(e2,i),-s.NZ(e2,j)]
                    else:
                        r,c=(e1,e2) if e1[0]=='r' else (e2,e1)
                        l1=[s.NZ(r,i),-s.NZ(r,j),s.NZ(c,j),-s.NZ(c,i)]
                    # (l1[0] and not l1[1] and l1[2] and not l1[3]) => var
                    L=[-s.NZ(e1,i),s.NZ(e1,j),-s.NZ(e2,i),s.NZ(e2,j),var] if e1[0]==e2[0] else \
                      [-s.NZ(r,i),s.NZ(r,j),-s.NZ(c,j),s.NZ(c,i),var]
                    add('E3',L)
            for e1,e2,e3 in itertools.combinations(el,3):
                a_,b_,c_=V[(e1,e2)],V[(e2,e3)],V[(e1,e3)]
                add('Etr',[-a_,-b_,c_]); add('Etr',[-a_,-c_,b_]); add('Etr',[-b_,-c_,a_])
        # ---- RQ variables (rat_i = x/alpha(i)), transitive, defined only if x!=0 and alpha(i)!=0
        for kind in 'rc':
            for i in Fr:
                el=[u for u in off if i in Tof[u]]; Vr={}
                for u,w in itertools.combinations(el,2):
                    var=s.v(('RQ',kind,i,u,w)); Vr[(u,w)]=Vr[(w,u)]=var
                    for z in (u,w):
                        add('RQd',[-var,s.XS((kind,z))]); add('RQd',[-var,s.NZ((kind,z),i)])
                for u,w,z in itertools.combinations(el,3):
                    a_,b_,c_=Vr[(u,w)],Vr[(w,z)],Vr[(u,z)]
                    add('RQtr',[-a_,-b_,c_]); add('RQtr',[-a_,-c_,b_]); add('RQtr',[-b_,-c_,a_])
        # ---- Schur
        for T in tets:
            Tc=frozenset(Fr)-T
            for u in TT[T]:
                for t in TT[Tc]: add('SCH',[-s.XS(('r',u)),-s.XS(('c',t))])
        # ---- diagonal M_uu != 0
        for u in off:
            terms=[]
            for i in Tof[u]:
                d=s.v(('and2',('nz','r',u,i),('nz','c',u,i)))
                add('def',[-d,s.NZ(('r',u),i)]); add('def',[-d,s.NZ(('c',u),i)]); add('def',[d,-s.NZ(('r',u),i),-s.NZ(('c',u),i)])
                terms.append(d)
            d=s.v(('and2',('x','r',u),('x','c',u)))
            add('def',[-d,s.XS(('r',u))]); add('def',[-d,s.XS(('c',u))]); add('def',[d,-s.XS(('r',u)),-s.XS(('c',u))])
            terms.append(d); add('DIAG',terms)
        # ---- same-tetrad orthogonal pairs: not exactly one nonzero term
        for T in tets:
            for u in TT[T]:
                for t in TT[T]:
                    if u!=t and G[u][t]==0:
                        terms=[]
                        for i in T:
                            d=s.v(('and2',('nz','r',u,i),('nz','c',t,i)))
                            add('def',[-d,s.NZ(('r',u),i)]); add('def',[-d,s.NZ(('c',t),i)]); add('def',[d,-s.NZ(('r',u),i),-s.NZ(('c',t),i)])
                            terms.append(d)
                        d=s.v(('and2',('x','r',u),('x','c',t)))
                        add('def',[-d,s.XS(('r',u))]); add('def',[-d,s.XS(('c',t))]); add('def',[d,-s.XS(('r',u)),-s.XS(('c',t))])
                        terms.append(d)
                        for k in range(len(terms)):
                            add('SAMET',[-terms[k]]+[terms[j] for j in range(len(terms)) if j!=k])
        # ---- per-pair rules
        for p in s.pairs:
            a,b=s.pk(p); ts=[T for T in tets if p<=T]
            for T1 in ts:
                for T2 in ts:
                    if T1==T2: continue
                    for u in TT[T1]:
                        for t in TT[T2]:
                            e=s.EQ(p,('r',u),('c',t)); X=s.XS(('r',u)); Y=s.XS(('c',t)); zu=s.ZP(('r',u),p); zt=s.ZP(('c',t),p)
                            if sg(u,a,b)!=sg(t,a,b):   # orthogonal
                                add('ORTH',[X,zu,zt,e]); add('ORTH',[Y,zu,zt,e])
                                add('ORTH',[-X,-Y,-zu]); add('ORTH',[-X,-Y,-zt]); add('ORTH',[-X,-Y,-e])
                            elif nonon(u,t):
                                for lit in (e,zu,zt):
                                    add('NON',[-lit,X]); add('NON',[-lit,Y])
                            elif s.scope=='k':
                                h=s.v(('h',u,t)); s.hv.append(h)
                                for lit in (e,zu,zt):
                                    add('NON',[h,-lit,X]); add('NON',[h,-lit,Y])
        # K3/D1 duality with dimension variables
        for p in s.pairs:
            a,b=s.pk(p); ts=[T for T in tets if p<=T]
            for eps in (1,-1):
                R={T:[('r',u) for u in TT[T] if sg(u,a,b)==eps] for T in ts}
                C={T:[('c',u) for u in TT[T] if sg(u,a,b)==-eps] for T in ts}
                sets={}
                for i,T in enumerate(ts):
                    Tj,Tk=[x for x in ts if x!=T]
                    sets[('R',i)]=R[T]; sets[('C',i)]=C[T]
                    sets[('Ru',i)]=R[Tj]+R[Tk]; sets[('Cu',i)]=C[Tj]+C[Tk]
                g={k:s.v(('g',(a,b),eps,k)) for k in sets}
                for k in sets: s.gsets[('g',(a,b),eps,k)]=sets[k]
                for i in range(3):
                    for j in range(3):
                        if j!=i:
                            add('Gsub',[-g[('R',j)],g[('Ru',i)]]); add('Gsub',[-g[('C',j)],g[('Cu',i)]])
                    add('Gdual',[-g[('R',i)],-g[('Cu',i)]]); add('Gdual',[-g[('C',i)],-g[('Ru',i)]])
                for k,S in sets.items():
                    gk=g[k]; kind=S[0][0]
                    for e1,e2 in itertools.combinations(S,2):
                        n1,n2=s.NZV(e1,p),s.NZV(e2,p); E_=s.EQ(p,e1,e2)
                        z1,z2=s.ZP(e1,p),s.ZP(e2,p)
                        crd=[(lambda e,a=a: s.NZ(e,a)),(lambda e,b=b: s.NZ(e,b)),(lambda e: s.XS(e))]
                        for f in crd:
                            # non-proportional (pattern differs, both nonzero) => g ; and g false => same pattern
                            add('Kpat',[-n1,-n2,-f(e1),f(e2),gk]); add('Kpat',[-n1,-n2,f(e1),-f(e2),gk])
                        add('Kpat',[z1,z2,E_,gk])
                        # conclusions when g false
                        for f in crd:
                            add('Kcon',[gk,-n1,-n2,-f(e1),f(e2)]); add('Kcon',[gk,-n1,-n2,f(e1),-f(e2)])
                        add('Kcon',[gk,z1,z2,E_])
                        for i in (a,b):
                            add('Kcon',[gk,-s.XS(e1),-s.XS(e2),-s.NZ(e1,i),-s.NZ(e2,i),s.RQ(kind,i,e1[1],e2[1])])
                # ZZ: two x=0 (y=0) vectors of a set, ab nonzero, not proportional => dual set vectors have zero ab-part
                for kS,kD in (('R','Cu'),('Ru','C'),('C','Ru'),('Cu','R')):
                    for i in range(3):
                        S=sets[(kS,i)]; D=sets[(kD,i)]
                        for e1,e2 in itertools.combinations(S,2):
                            E_=s.EQ(p,e1,e2)
                            if 'ZZold' in s.mut: add('ZZ',[s.XS(e1),s.XS(e2),E_])
                            for d in D:
                                add('ZZ',[s.XS(e1),s.XS(e2),s.ZP(e1,p),s.ZP(e2,p),E_,s.ZP(d,p)])
        # ---- Q2 (rat_a, rat_b, E_ab: two => third; all four coordinates nonzero, x nonzero)
        for p in s.pairs:
            a,b=s.pk(p)
            for kind in 'rc':
                el=[u for u in off if p<=Tof[u]]
                for u,w in itertools.combinations(el,2):
                    e1,e2=(kind,u),(kind,w)
                    g_=[-s.XS(e1),-s.XS(e2),-s.NZ(e1,a),-s.NZ(e1,b),-s.NZ(e2,a),-s.NZ(e2,b)]
                    t=[s.RQ(kind,a,u,w),s.RQ(kind,b,u,w),s.EQ(p,e1,e2)]
                    for k in range(3):
                        o=[t[j] for j in range(3) if j!=k]
                        add('Q2',g_+[-o[0],-o[1],t[k]])
        # ---- common partner
        for p in s.pairs:
            a,b=s.pk(p); ts=[T for T in tets if p<=T]
            for eps in (1,-1):
                for kind,okind in (('r','c'),('c','r')):
                    Rs=[(T,[u for u in TT[T] if sg(u,a,b)==eps]) for T in ts]
                    Cs=[(T,[u for u in TT[T] if sg(u,a,b)==-eps]) for T in ts]
                    allR=[(T,u) for T,L in Rs for u in L]
                    for (T1,u),(T2,w) in itertools.combinations(allR,2):
                        E_=s.EQ(p,(kind,u),(kind,w))
                        for T3,L in Cs:
                            if T3==T1 or T3==T2: continue
                            for t in L:
                                Yt=s.XS((okind,t))
                                add('CP',[-Yt,-E_,-s.XS((kind,u)),s.XS((kind,w))]); add('CP',[-Yt,-E_,s.XS((kind,u)),-s.XS((kind,w))])
                                for i in (a,b):
                                    add('CP',[-Yt,-E_,-s.XS((kind,u)),-s.XS((kind,w)),-s.NZ((kind,u),i),s.RQ(kind,i,u,w)])
        # ---- TRI
        for T in tets:
            for tri in itertools.combinations(sorted(T),3):
                for m in tri:
                    x_,y_=[i for i in tri if i!=m]
                    pm=[frozenset((m,x_)),frozenset((m,y_)),frozenset((x_,y_))]
                    for u,w in itertools.combinations(TT[T],2):
                        for kind in 'rc':
                            e1,e2=(kind,u),(kind,w)
                            if 'TRInoguard' in s.mut: add('TRI',[-s.EQ(pm[0],e1,e2),-s.EQ(pm[1],e1,e2),s.EQ(pm[2],e1,e2)])
                            else: add('TRI',[-s.EQ(pm[0],e1,e2),-s.EQ(pm[1],e1,e2),-s.NZ(e1,m),s.EQ(pm[2],e1,e2),s.ZP(e1,pm[2])])
                    for u in TT[T]:
                        for t in TT[T]:
                            def O(q):
                                key=('o',s.pk(q),u,t)
                                if key not in s.reg:
                                    o=s.v(key); e=s.EQ(q,('r',u),('c',t)); z1=s.ZP(('r',u),q); z2=s.ZP(('c',t),q)
                                    add('def',[-e,o]); add('def',[-z1,o]); add('def',[-z2,o]); add('def',[-o,e,z1,z2])
                                return s.reg[key]
                            o1,o2,o3=O(pm[0]),O(pm[1]),O(pm[2])
                            nu,nt=s.NZ(('r',u),m),s.NZ(('c',t),m)
                            add('TRIrc',[-o1,-o2,-nu,-nt,-o3]); add('TRIrc',[-o1,-o2,nu,o3]); add('TRIrc',[-o1,-o2,nt,o3])
        s.finish()
    def finish(s):
        if s.scope!='k': return
        ex=list(s.hv)
        for kind in 'rc':
            for u in s.off:
                for i in s.Tof[u]: ex.append(-s.NZ((kind,u),i))
        K=s.K; n=len(ex)
        # sequential counter: reg[i][j] = at least j+1 of first i+1 literals true
        prev=None
        for i,l in enumerate(ex):
            cur=[s.v(('cnt',i,j)) for j in range(K+1)]
            for j in range(K+1):
                # cur[j] >= prev[j] ; cur[j] >= prev[j-1] & l
                if prev is not None: s.add('CNT',[-prev[j],cur[j]])
                if j==0: s.add('CNT',[-l,cur[0]])
                elif prev is not None: s.add('CNT',[-prev[j-1],-l,cur[j]])
            prev=cur
        s.add('CNT',[-prev[K]])   # not K+1 exceptions
    def add_residue(s):
        Fr=s.Fr
        for t in range(N):
            # (Sigma4) sigma_a empty: D meets O_t, unless beta_t == 0 on T(t) (t off frame)
            Dl=[s.XS(('r',u)) for u in O[t] if u in s.Tof]
            Yl=[s.XS(('c',u)) for u in O[t] if u in s.Tof]
            if t in s.Tof:
                bz=[-s.NZ(('c',t),i) for i in s.Tof[t]]; az=[-s.NZ(('r',t),i) for i in s.Tof[t]]
                bzv=s.v(('allz','c',t)); azv=s.v(('allz','r',t))
                for lit in bz: s.add('def',[-bzv,lit])
                s.add('def',[bzv]+[-l for l in bz])
                for lit in az: s.add('def',[-azv,lit])
                s.add('def',[azv]+[-l for l in az])
                s.add('RES',Dl+[bzv]); s.add('RES',Yl+[azv])
            else:
                s.add('RES',Dl); s.add('RES',Yl)
    def add_notgram(s,which=('r','c')):
        for kind in which:
            opt=[]
            for p in s.pairs:
                a,b=s.pk(p); el=[u for u in s.off if p<=s.Tof[u]]
                for u,w in itertools.combinations(el,2):
                    e=s.EQ(p,(kind,u),(kind,w))
                    opt.append(-e if s.sg(u,a,b)==s.sg(w,a,b) else e)
            for u in s.off:
                for i in s.Tof[u]: opt.append(-s.NZ((kind,u),i))
            s.add('NG'+kind,opt)
    def add_zrig(s):
        # ZRIG: D' (resp. D) is not inside a frame F0 (else P112=E8\F0 has rank<=8 on columns (rows) off F0; Theorem Z => Gram; Lemma E, Thm G => B/A2).
        # every pairwise-orthogonal set extends to a frame, so: D' contains a non-orthogonal pair.
        for kind in 'rc':
            lits=[]
            for u in s.off:
                for t in s.off:
                    if u<t and G[u][t]!=0:
                        d=s.v(('and2',('x',kind,u),('x',kind,t)))
                        s.add('def',[-d,s.XS((kind,u))]); s.add('def',[-d,s.XS((kind,t))]); s.add('def',[d,-s.XS((kind,u)),-s.XS((kind,t))])
                        lits.append(d)
            s.add('ZRIG',lits)
    def add_rank(s):
        s.add('RANK',[s.XS(('r',u)) for u in s.off]); s.add('RANK',[s.XS(('c',u)) for u in s.off])
    def dump(s,fn,tags=None):
        cl=[c for t,c in s.cl if tags is None or t in tags]
        with open(fn,'w') as f:
            f.write(f'p cnf {s.nv} {len(cl)}\n')
            for c in cl: f.write(' '.join(map(str,c))+' 0\n')
        return s.nv,len(cl)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--scope',default='a'); ap.add_argument('--res',type=int,default=1)
    ap.add_argument('--ng',default='rc'); ap.add_argument('--mut',default=''); ap.add_argument('--zrig',type=int,default=0); ap.add_argument('--frame',type=int,default=0)
    A=ap.parse_args()
    m=Model(frames()[A.frame],A.scope,mut=A.mut.split(',') if A.mut else ())
    if A.res: m.add_residue()
    m.add_notgram(tuple(A.ng)); m.add_rank()
    if A.zrig: m.add_zrig()
    print(m.dump(A.out))
