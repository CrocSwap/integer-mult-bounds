"""Exact literature-transfer tests. Python standard library; no downloaded code."""
from collections import deque, Counter
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path


def need(ok, msg):
    if not ok: raise ValueError(msg)


def gf2rank(vs):
    piv={}
    for v in vs:
        while v:
            i=v.bit_length()-1
            if i in piv:v^=piv[i]
            else:piv[i]=v;break
    return len(piv)


def image(cols,x):
    y=0
    for j,c in enumerate(cols):
        if x>>j&1:y^=c
    return y


def compose(a,b):return tuple(image(a,c) for c in b)


def hadamard_test():
    # Coordinates are (x0,x1,z0,z1); columns describe Pauli conjugation.
    n=2;identity=tuple(1<<j for j in range(2*n));gens=[]
    for j in range(n):
        cols=list(identity);cols[j],cols[n+j]=cols[n+j],cols[j]
        gens.append((tuple(cols),1))
        cols=list(identity);cols[j]^=1<<(n+j)
        gens.append((tuple(cols),0))
    for c,t in [(0,1),(1,0)]:
        cols=list(identity);cols[c]^=1<<t;cols[n+t]^=1<<(n+c)
        gens.append((tuple(cols),0))
    dist={identity:0};q=deque([identity])
    while q:
        m=q.popleft();d=dist[m]
        for g,w in gens:
            h=compose(g,m);nd=d+w
            if nd<dist.get(h,999):
                dist[h]=nd
                if w:q.append(h)
                else:q.appendleft(h)
    need(len(dist)==720,'symplectic census')
    histogram=Counter()
    for m,d in dist.items():
        r=gf2rank([m[n+j]&3 for j in range(n)])
        need(d==r,'Hadamard Bruhat rank disagrees with exact shortest synthesis')
        histogram[d]+=1
    return {'symplectic_classes':len(dist),'minimum_H_distribution':{str(k):v for k,v in sorted(histogram.items())},'scope':'two-qubit symplectic quotient only; phases tested separately'}


def pauli_test():
    # i^k X^a Z^b, with the absolute central phase retained.
    def act(a,b,k,x):return x^a,(k+2*((b&x).bit_count()&1))%4
    checked=0
    for a,b,k,c,d,l in product(range(4),range(4),range(4),range(4),range(4),range(4)):
        aa,bb,kk=a^c,b^d,(k+l+2*((b&c).bit_count()&1))%4
        for x in range(4):
            y,p=act(c,d,l,x);z,q=act(a,b,k,y)
            target,r=act(aa,bb,kk,x)
            need((z,(p+q)%4)==(target,r),'phase cocycle')
            checked+=1
    need(act(0,0,0,0)!=act(0,0,2,0),'absolute central phase must not be merged')
    # The parity phase S(x xor y) = S(x) S(y) CZ(x,y).
    parity=0
    for x,y in product(range(2),repeat=2):
        need((x^y)%4==(x+y-2*x*y)%4,'quadratic parity phase')
        parity+=1
    affine_checks=0
    affine=[(a,b,t) for a,b in product(range(1,4),repeat=2) if gf2rank([a,b])==2 for t in range(4)]
    for c,l0,l1,b in product(range(4),range(4),range(4),range(2)):
        def value(x):return (c+l0*(x&1)+l1*((x>>1)&1)+2*b*(x&1)*((x>>1)&1))%4
        for a0,a1,t in affine:
            vals=[value(image((a0,a1),x)^t) for x in range(4)]
            cc=vals[0];ll0=(vals[1]-cc)%4;ll1=(vals[2]-cc)%4
            cross=(vals[3]-vals[1]-vals[2]+cc)%4
            need(cross in (0,2),'quadratic phase refinement not closed')
            for x in range(4):
                got=(cc+ll0*(x&1)+ll1*((x>>1)&1)+cross*(x&1)*((x>>1)&1))%4
                need(got==vals[x],'affine phase reconstruction')
            affine_checks+=1
    return {'phase_sensitive_basis_checks':checked,'affine_quadratic_compositions':affine_checks,'quadratic_parity_cases':parity,'projective_merge_rejected':True}


def z(a=0,b=0):return F(a),F(b)
ZERO=z();ONE=z(1)
def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def neg(a):return -a[0],-a[1]
def cscale(c,a):return tuple(tuple(mul(c,x) for x in r) for r in a)
def mm(a,b):return tuple(tuple(sumz(mul(a[r][k],b[k][c]) for k in range(len(a))) for c in range(len(a))) for r in range(len(a)))
def sumz(xs):
    a=ZERO
    for x in xs:a=add(a,x)
    return a

def mv(a,x):return [sumz(mul(v,t) for v,t in zip(row,x)) for row in a]
def adj(a):return tuple(tuple((a[c][r][0],-a[c][r][1]) for c in range(len(a))) for r in range(len(a)))
def ident(n):return tuple(tuple(ONE if r==c else ZERO for c in range(n)) for r in range(n))
def madd(a,b):return tuple(tuple(add(x,y) for x,y in zip(ar,br)) for ar,br in zip(a,b))
def vp(x,y,s=1):return [add(a,mul(z(s),b)) for a,b in zip(x,y)]


def echo_and_invoice_test():
    alpha=z(F(1,2),F(1,2));beta=z(F(1,2),F(-1,2))
    C=((alpha,beta),(beta,alpha));S=((ONE,ZERO),(ZERO,z(0,1)))
    G=mm(mm(S,C),adj(S));Gi=adj(G);Ci=adj(C)
    need(mv(S,[ONE,ZERO])==[ONE,ZERO] and mv(S,[ZERO,ONE])!=[ZERO,ONE],'state equality does not prove arbitrary-input operator equality')
    need(mm(C,Ci)==ident(2) and mm(G,Gi)==ident(2),'paid primitive inverse')
    need(madd(ident(2),C)!=madd(ident(2),cscale(z(-1),C)),'projective replacement inside a sum must be rejected')
    need(mm(C,G)!=mm(G,C),'echo must cover noncommuting primitives')
    cases=64;calls=0
    for seed in range(cases):
        original={k:[z((seed*(j+3)+t)%11-5,(seed*(j+1)+2*t)%13-6) for j in range(2)] for k,t in [('x',1),('y',4),('d',7)]}
        regs={k:v[:] for k,v in original.items()}
        def inject(dst,src,M,Mi,sign):
            nonlocal calls
            need(src!=dst,'aliasing dirty source and destination')
            old=regs[src][:];regs[src]=mv(M,regs[src]);calls+=1
            regs[dst]=vp(regs[dst],regs[src],sign)
            regs[src]=mv(Mi,regs[src]);calls+=1
            need(regs[src]==old,'injection changed independent source')
        inject('d','x',C,Ci,1);inject('y','d',G,Gi,1)
        inject('d','x',C,Ci,-1);inject('y','d',G,Gi,-1)
        need(regs['x']==original['x'] and regs['d']==original['d'],'dirty restoration')
        need(regs['y']==vp(original['y'],mv(G,mv(C,original['x']))),'dirty echo target')
    need(calls==8*cases,'compute/restore paid invoice')
    # Actual paid C = H S H also has a one-H representative, including phase.
    H0=((ONE,ONE),(ONE,z(-1)))
    need(C==cscale(alpha,mm(mm(adj(S),H0),adj(S))),'phase-correct one-H representative')
    ledger=[{'width':f,'naive_H_count':2*f,'optimized_H_count':f,'paid_Gaussian_calls_before':1,'paid_Gaussian_calls_after':1} for f in range(1,6)]
    for r in ledger:
        need(r['optimized_H_count']<r['naive_H_count'] and r['paid_Gaussian_calls_after']==r['paid_Gaussian_calls_before'],'H count is not supplier invoice')
    # A nonzero additive two-bank shear is not a unitary quantum circuit.
    L=madd(ident(2),cscale(z(2),S));Fblock=mm(mm(C,L),C)
    U=tuple(tuple(C[r][c] if r<2 and c<2 else ZERO if r<2 else Fblock[r-2][c] if c<2 else C[r-2][c-2] for c in range(4)) for r in range(4))
    need(mm(adj(U),U)!=ident(4),'nonunitary block cannot be fed to a unitary Clifford compiler')
    # Even FLO preserves fermion parity. This project primitive does not in the standard encoding.
    parity=((ONE,ZERO),(ZERO,z(-1)))
    need(mm(C,parity)!=mm(parity,C),'standard even-FLO mismatch control')
    return {'arbitrary_dirty_echo_cases':cases,'paid_primitive_invocations':calls,'calls_per_echo':8,'hadamard_vs_paid_ledger':ledger,'nonunitary_shear_rejected':True,'even_FLO_encoding_rejected':True,'relative_phase_merge_rejected':True,'state_only_operator_certificate_rejected':True,'scope':'exact all-input linear echo, with explicit compute/restore overhead; no supplier saving'}


def ownership_test():
    # Positive owner discipline: symbolic register identity precedes any role number.
    class Arena:
        def __init__(self):self.cells={'helper631':[3,-2]};self.owned=set();self.stores=0
        def allocate(self,name,size):
            need(name not in self.cells,'owned allocation aliases existing independent input')
            self.cells[name]=[0]*size;self.owned.add(name);self.stores+=size
        def clear(self,name):
            if name not in self.owned:raise ValueError('CLEAR requires owned field')
            self.stores+=len(self.cells[name]);self.cells[name]=[0]*len(self.cells[name])
    arena=Arena();old=arena.cells['helper631'][:]
    arena.allocate('fresh-center',2);arena.cells['fresh-center']=[7,9];arena.clear('fresh-center')
    need(arena.cells['helper631']==old and arena.cells['fresh-center']==[0,0],'positive owned clear')
    rejected=0
    for bad in ['helper631','unallocated-center']:
        try:arena.clear(bad)
        except ValueError:rejected+=1
    try:arena.allocate('helper631',2)
    except ValueError:rejected+=1
    # This is the rejected historical parser pattern: center=-1; helper=632+center.
    aliased='helper'+str(632+(-1))
    try:arena.clear(aliased)
    except ValueError:rejected+=1
    need(rejected==4 and arena.cells['helper631']==old,'owned-CLEAR alias regression')
    return {'valid_owned_initialization_and_clear':True,'owned_stores_charged':arena.stores,'invalid_clear_or_alias_rejections':rejected,'borrowed_input_preserved':True}

def main():
    got={'status':'PASS_PHASE_AWARE_LITERATURE_TRANSFER','hadamard':hadamard_test(),'phase':pauli_test(),'dirty_and_model':echo_and_invoice_test(),'ownership':ownership_test(),'new_kappa':None}
    expected=Path(__file__).resolve().with_name('EXPECTED.json')
    need(expected.is_file(),'missing deterministic receipt')
    need(got==json.loads(expected.read_text(encoding='utf8')),'changed deterministic receipt')
    print(json.dumps(got,sort_keys=True))

if __name__=='__main__':main()
