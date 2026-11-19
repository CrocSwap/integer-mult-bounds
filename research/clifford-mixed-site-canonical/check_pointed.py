"""Verify the 12+1 orbital solve, raw phase identities and projection masses."""
from collections import Counter
from fractions import Fraction
from math import lcm
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pointed as P
from canonical import coefficient as repeated_coefficient
from compile_row import apply, span, UPPER, shear
from bell_reads import transvection


def flag_orbits():
    spaces,elems,counts,reps=P.geometry()
    by_space={L:k for k,L in enumerate(spaces)}
    # These symplectic generators all fix the base flag. A connected orbit
    # per signature certifies sufficiency of the displayed invariants.
    generators=[shear(1<<k) for k in range(len(UPPER))]
    for i in range(1,4):
        for j in range(4):
            if i!=j:
                S=list(P.IDENTITY)
                S[i]^=1<<j
                S[4+j]^=1<<(4+i)
                generators.append(tuple(S))
    actions=[]
    for S in generators:
        P.require(P.is_symplectic(S) and S[0]==1 and P.point_set(S[:4])==P.BASE,"base-flag generator")
        g=[apply(S,v) for v in range(256)]
        images=[by_space[sum(1<<g[v] for v in vs)] for vs in elems]
        actions.append((g,images))
    for key,(L,v) in reps.items():
        first=(by_space[L],v)
        orbit=[first]
        seen={first}
        for i,v in orbit:
            for action,images in actions:
                other=images[i],action[v]
                if other not in seen:
                    seen.add(other)
                    orbit.append(other)
        P.require(len(orbit)==counts[key] and all(P.relation(P.BASE,1,spaces[i],v)==key for i,v in orbit),
                  "signature is not one orbit")
    P.require(len(counts)==20,"expected orbit rank")


def verify_inverse():
    spaces,elems,_,reps=P.geometry()
    labels=[(Y,v,P.relation(P.BASE,1,Y,v)) for Y,vs in zip(spaces,elems,strict=True) for v in vs if v]
    G,H=P.orbital_kernels()
    for key,(X,x) in reps.items():
        pairs=Counter((i,P.relation(Y,v,X,x)) for Y,v,i in labels)
        result=sum(n*G[i]*H[j] for (i,j),n in pairs.items())
        P.require(result==int(key==P.relation(P.BASE,1,P.BASE,1)),"orbital inverse identity")
    print("PASS all 20 orbital coefficients of Gram times its pushed-forward inverse.")


def canonical_census():
    # At a fixed Lagrangian distance average independently over labels of the
    # two Fourier characters. Their zero/nonzero pattern is the only input invariant.
    bases,_,rings=P.quotient()
    wt=P.weights()
    source=(P.ORDER//2295)
    totals=Counter()
    gram_norm=Counter()
    all_weights=set()
    for j in range(5):
        B=bases[rings.index(j)]
        weights=P.site_weights(B,0,0,*wt)
        P.require(len(set(weights))==(4,7,8,7,4)[j] and all(weights),"distinct nonzero shell weights")
        all_weights.update(weights)
        pts=span(B)
        fibres=rings.count(j)*source
        for key in [(0,0),(1,0),(0,1),(1,1)]:
            allowed=[(a,b) for a in range(16) for b in range(16) if (bool(a),bool(b))==key]
            mass=Fraction(fibres,len(allowed))
            for a,b in allowed:
                w=weights[a+(b<<4)]
                if w:
                    totals[key] += mass*(16<<j)
                compatible=all(((a & t).bit_count()+(b & v).bit_count())%2==0
                               for v,t in enumerate(pts) if t<16)
                if compatible:
                    gram_norm[key] += mass*16*Fraction(-1,64)**j * w / 4**13
    P.require(all(v.denominator==1 for v in totals.values()) and
              all(0<v<1 for v in gram_norm.values()),"projection mass / support")
    h=lcm(*(v.denominator for v in all_weights))
    expected=(Fraction(478566778595,5856573836677349376),
              Fraction(34240796149757,767064758258815834521600),
              Fraction(319403078159153570779,55516311878981796023500800000))
    P.require(len(set(expected))==3 and all(gram_norm[k]==expected[sum(k)] for k in totals),
              "three principal-angle masses")
    P.require(set(totals.values())=={8338459852800},"sharp canonical support census")
    P.require(len(all_weights)==30 and h==2**17*5878456335448005684375,"weight denominator")
    print("12+1 same-basis coordinate controls (different row, different column):",
          sorted((k,int(totals[k]),str(m)) for k,m in gram_norm.items()))
    return gram_norm, totals


def literal():
    ident=P.IDENTITY
    def sym(axes):
        S=ident
        for axis in axes:
            S=tuple(transvection(axis,v) for v in S)
        return S
    bases=[ident,sym([17,34,68,136]),sym([17,131,51]),sym([35,16,49,201,6,8,141])]
    raw_ring=tuple(P.rhs(i) for i in range(5))
    _,_,counts,_=P.geometry()
    raw_point={k:(P.rhs(k[0]) if k[1] else 0) for k in counts}
    singulars=probes=0
    for i,S in enumerate(bases):
        for left,right in [(ident,ident),(bases[2],bases[1])]:
            r,c=(i+2)%16,(i+1)%16
            rel=P.transformed_inputs(S,left,right)
            W=P.site_weights(rel,r,c,raw_ring,raw_point)
            for p in (0,2,17,49,69,130,255):
                tau=P.conjugate(P.transition(S,p,r,c,left,right))
                power=P.Q.multiply
                repeated=(1,0)
                for _ in range(12):
                    repeated=power(repeated,tau)
                for a,b in [(r,c),(1,2),(r^1,c),(r,c^4),(r^2,c^4)]:
                    singleton=P.conjugate(P.transition(S,p,a,b,left,right))
                    direct=power(repeated,singleton)
                    h=W[a | (b<<4)]
                    P.require(tuple(Fraction(t,4**13) for t in direct)==tuple(h*t for t in singleton),
                              "raw singleton phase and compatibility")
                    probes+=1
                    singulars+=any(t!=0 for t in direct)
                once=P.coefficient(S,p,r,c,[(r,c,(1,0))],left,right)
                P.require(once==repeated_coefficient(S,p,r,c,left,right),"repeated-site specialization")
    P.require(singulars>0 and singulars<probes,"degenerate literal controls")
    print("PASS",probes,"literal mixed tensor entries, including",singulars,"nonzeros.")


if __name__=='__main__':
    flag_orbits()
    verify_inverse()
    literal()
    canonical_census()
