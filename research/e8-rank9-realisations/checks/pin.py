# KSTAR round 2: P^1-valued pinning abstraction (sound) in pivot coordinates w.r.t. a frame F of E8.
# Per pair p={a,b} of F: every row u with p ⊆ T(u) has ratio rho_p(u)=alpha_u(b)/alpha_u(a) in K*, every column s has
# tau_p(s)=-beta_s(a)/beta_s(b) in K*, so that alpha_u|p . beta_s|p = alpha_u(a) beta_s(b) (rho - tau).
# Boolean: x[u] (x_u != 0), y[s]; E[p][(e,e')] equality of values (transitive).
# Rules (each proven in THEORY §6): ORTH, NON, TRI (row-row / col-col / row-col), K3 (local lemma), ZZ, Schur.
import sys, itertools, os
import os as _o; sys.path.insert(0,_o.path.dirname(_o.path.abspath(__file__)))
from e8lib import *
cl=[]; nv=[0]
def new(): nv[0]+=1; return nv[0]
def build(Fr, opts):
    Fr=tuple(Fr); TT=tetrads(Fr); tets=list(TT); off=[u for u in range(N) if u not in Fr]
    Tof={u:T for T in tets for u in TT[T]}
    X={u:new() for u in off}; Y={u:new() for u in off}
    sg=lambda u,a,b: 1 if dot(E[u],E[a])*dot(E[u],E[b])>0 else -1
    pairs=[frozenset(p) for p in itertools.combinations(Fr,2)]
    EQ={}
    for p in pairs:
        el=[('r',u) for u in off if p<=Tof[u]]+[('c',u) for u in off if p<=Tof[u]]
        V={}
        for e1,e2 in itertools.combinations(el,2): V[(e1,e2)]=V[(e2,e1)]=new()
        for e1,e2,e3 in itertools.combinations(el,3):
            a_,b_,c_=V[(e1,e2)],V[(e2,e3)],V[(e1,e3)]
            cl.extend([[-a_,-b_,c_],[-a_,-c_,b_],[-b_,-c_,a_]])
        EQ[p]=V
    # Schur
    for T in tets:
        Tc=frozenset(Fr)-T
        for u in TT[T]:
            for s in TT[Tc]: cl.append([-X[u],-Y[s]])
    for p in pairs:
        a,b=sorted(p); V=EQ[p]; ts=[T for T in tets if p<=T]
        # ORTH / NON between different tetrads through p
        for T1 in ts:
            for T2 in ts:
                if T1==T2: continue
                for u in TT[T1]:
                    for s in TT[T2]:
                        e=V[(('r',u),('c',s))]
                        if sg(u,a,b)!=sg(s,a,b):   # orthogonal
                            cl.append([X[u],e]); cl.append([Y[s],e]); cl.append([-X[u],-Y[s],-e])
                        else:
                            cl.append([X[u],-e]); cl.append([Y[s],-e])
        # K3 local lemma + ZZ
        for eps in (1,-1):
            for i,Ti in enumerate(ts):
                R=[u for u in TT[Ti] if sg(u,a,b)==eps]
                C=[s for T2 in ts if T2!=Ti for s in TT[T2] if sg(s,a,b)==-eps]
                Rr=[u for T2 in ts if T2!=Ti for u in TT[T2] if sg(u,a,b)==eps]
                Cc=[s for s in TT[Ti] if sg(s,a,b)==-eps]
                # rows R in T_i vs columns C: dim U_i>=2 => all C equal value and equal y-status
                for u,w in itertools.combinations(R,2):
                    e=V[(('r',u),('r',w))]
                    for s,t in itertools.combinations(C,2):
                        f=V[(('c',s),('c',t))]
                        for cond in ([e],[-e,-X[u],X[w]],[-e,X[u],-X[w]]):
                            cl.append(cond+[f]); cl.append(cond+[-Y[s],Y[t]]); cl.append(cond+[Y[s],-Y[t]])
                    cl.append([X[u],X[w],e])   # ZZ
                # transposed: columns of T_i ((-eps) class) vs rows of other tetrads (eps class)
                for s,t in itertools.combinations(Cc,2):
                    f=V[(('c',s),('c',t))]
                    for u,w in itertools.combinations(Rr,2):
                        e=V[(('r',u),('r',w))]
                        for cond in ([f],[-f,-Y[s],Y[t]],[-f,Y[s],-Y[t]]):
                            cl.append(cond+[e]); cl.append(cond+[-X[u],X[w]]); cl.append(cond+[X[u],-X[w]])
                    cl.append([Y[s],Y[t],f])
    # TRI: triples inside a tetrad
    for T in tets:
        for tri in itertools.combinations(sorted(T),3):
            a,b,c=tri; P3=[frozenset((a,b)),frozenset((b,c)),frozenset((a,c))]
            el=[('r',u) for u in TT[T]]+[('c',u) for u in TT[T]]
            for e1,e2 in itertools.combinations(el,2):
                vs=[EQ[q][(e1,e2)] for q in P3]
                same=(e1[0]==e2[0])
                for k in range(3):
                    o=[vs[j] for j in range(3) if j!=k]
                    if same: cl.append([-o[0],-o[1],vs[k]])
                    else: cl.append([-o[0],-o[1],-vs[k]])

    # TW (twist rule): dim U_i = 1 at (p,eps) whenever the (-eps) columns of the other two tetrads span >= 2 dims
    # (two columns with different psi, or a Z' and a D' column). Then x_u = t*alpha_u(a) on the class.
    # Two disjoint pairs p, p' with p ∪ p' = T: rows u,w in a common 1-dim class at p and at p', x_u,x_w != 0
    # => alpha(c)/alpha(a) equal => EQ_{ac}(u,w).  Transposed for columns.
    if opts.get('tw',1):
        D1={}; globals()['D1_']=D1
        for p in pairs:
            a,b=sorted(p); V=EQ[p]; ts=[T for T in tets if p<=T]
            for eps in (1,-1):
                for Ti in ts:
                    for kind,P_,Q_ in (('r',X,Y),('c',Y,X)):
                        okind='c' if kind=='r' else 'r'
                        C=[s for T2 in ts if T2!=Ti for s in TT[T2] if sg(s,a,b)==-eps]
                        d=new(); D1[(kind,p,eps,Ti)]=d
                        for s,t in itertools.combinations(C,2):
                            cl.append([V[((okind,s),(okind,t))],d])      # different psi => d
                            cl.append([-Q_[s],Q_[t],d]); cl.append([Q_[s],-Q_[t],d])   # Z'/D' mix => d
        for T in tets:
            Ts=sorted(T)
            for a,b in itertools.combinations(Ts,2):
                c,dd=[i for i in Ts if i not in (a,b)]
                p=frozenset((a,b)); q=frozenset((c,dd))
                for kind,P_ in (('r',X),('c',Y)):
                    for u,w in itertools.combinations(TT[T],2):
                        if sg(u,a,b)!=sg(w,a,b) or sg(u,c,dd)!=sg(w,c,dd): continue
                        e1=D1[(kind,p,sg(u,a,b),T)]; e2=D1[(kind,q,sg(u,c,dd),T)]
                        tgt=EQ[frozenset((a,c))][((kind,u),(kind,w))]
                        cl.append([-e1,-e2,-P_[u],-P_[w],tgt])

    # RATIO rules: rat_i(u) := x_u/alpha_u(i) (rows with x_u != 0, i in T(u)); columns likewise with y.
    if opts.get('ratio',1):
        RQ={}; globals()['RQ_']=RQ
        for kind,P_ in (('r',X),('c',Y)):
            for i in Fr:
                el=[u for u in off if i in Tof[u]]; Vr={}
                for u,w in itertools.combinations(el,2): Vr[(u,w)]=Vr[(w,u)]=new()
                for u,w,z in itertools.combinations(el,3):
                    a_,b_,c_=Vr[(u,w)],Vr[(w,z)],Vr[(u,z)]
                    cl.extend([[-a_,-b_,c_],[-a_,-c_,b_],[-b_,-c_,a_]])
                RQ[(kind,i)]=Vr
        for p in pairs:
            a,b=sorted(p); V=EQ[p]; ts=[T for T in tets if p<=T]
            for kind,P_,Q_ in (('r',X,Y),('c',Y,X)):
                okind='c' if kind=='r' else 'r'
                el=[u for u in off if p<=Tof[u]]
                # Q2: two of {rat_a, rat_b, eq_ab} => third (x != 0 on both)
                for u,w in itertools.combinations(el,2):
                    t=[RQ[(kind,a)][(u,w)],RQ[(kind,b)][(u,w)],V[((kind,u),(kind,w))]]
                    for k in range(3):
                        o=[t[j] for j in range(3) if j!=k]
                        cl.append([-P_[u],-P_[w],-o[0],-o[1],t[k]])
                for eps in (1,-1):
                    for Ti in ts:
                        Rcl=[u for u in TT[Ti] if sg(u,a,b)==eps]
                        d=D1[(kind,p,eps,Ti)]
                        for u,w in itertools.combinations(Rcl,2):
                            cl.append([-d,V[((kind,u),(kind,w))]])
                            cl.append([-d,-P_[u],P_[w]]); cl.append([-d,P_[u],-P_[w]])
                            for i in (a,b): cl.append([-d,-P_[u],-P_[w],RQ[(kind,i)][(u,w)]])
                    # common D' (resp. D) partner: u in T_i, w in T_k (eps), s in T_j (-eps), j != i,k
                    for Ti,Tk in itertools.permutations(ts,2):
                        if Ti>Tk: continue
                        Tj=[T for T in ts if T not in (Ti,Tk)][0]
                        Rs=[u for u in TT[Ti] if sg(u,a,b)==eps]; Rk=[u for u in TT[Tk] if sg(u,a,b)==eps]
                        Cs=[s_ for s_ in TT[Tj] if sg(s_,a,b)==-eps]
                        for u in Rs:
                            for w in Rk:
                                for s_ in Cs:
                                    for i in (a,b): cl.append([-P_[u],-P_[w],-Q_[s_],-V[((kind,u),(kind,w))],RQ[(kind,i)][(u,w)]])
    # residue hypotheses
    if opts.get('residue',1):
        for s in range(N):
            cl.append([X[u] for u in O[s] if u in X]); cl.append([Y[u] for u in O[s] if u in Y])
    # not row-Gram-shaped and not column-Gram-shaped
    for kind,Z in (('r',X),('c',Y)):
        if not opts.get('notgram',1): break
        opt=[]
        for p in pairs:
            a,b=sorted(p); V=EQ[p]; el=[u for u in off if p<=Tof[u]]
            for u,w in itertools.combinations(el,2):
                e=V[((kind,u),(kind,w))]
                if sg(u,a,b)==sg(w,a,b): opt.append(-e)
                else: opt.append(e)
        cl.append(opt)
    cl.append([X[u] for u in off]); cl.append([Y[u] for u in off])
    return X,Y,EQ
if __name__=='__main__':
    opts={k:int(v) for k,v in (a.split('=') for a in sys.argv[2:])}
    build(frames()[0],opts)
    with open(sys.argv[1],'w') as f:
        f.write(f'p cnf {nv[0]} {len(cl)}\n')
        for c in cl: f.write(' '.join(map(str,c))+' 0\n')
    print(nv[0],len(cl))
