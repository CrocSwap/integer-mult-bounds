"""Independent exact vector replay at widths 1 and 2; no tensor-of-sum shortcut."""
from pathlib import Path
import hashlib, importlib.util, json, sys

base=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent/'word'
p=base/'pr4710'/'verify_residual.py'
if hashlib.sha256(p.read_bytes()).hexdigest()!='0d277854396e4ceda1e0f26916bd576b6decb474c0692b6671ebf2595283ddb9':
    raise ValueError('source drift')
spec=importlib.util.spec_from_file_location('exact_source',p);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
C=[v.c_letter(j) for j in range(3)];S=v.s_letter(7)
U=v.monomial([0,5,2,7,4,1,6,3]);V=v.monomial([0,2,1,3,4,6,5,7])
P=v.word(S,U,S);Q=v.word(S,V,S);A=C[0]
J=v.word(v.pauli(0,2),V,C[2]);W=v.pauli(0,5)
M=v.monomial([2,0,3,1,4,6,5,7],[0,0,2,2,1,3,3,1]);K=v.word(*C);a=v.pauli(1,3)
T=v.monomial([((x&1)<<2)|(x&2)|((x&4)>>2) for x in range(8)])
correction=v.word(K,a,v.adjoint(K))

def req(b,s):
    if not b: raise ValueError(s)
def plus(x,y,c=1):return [v.add(a,v.mul(v.q(c),b)) for a,b in zip(x,y)]
def scaled(x,c):return [v.mul(v.q(c),a) for a in x]
def tensor_apply(G,x,f):
    out=x[:]
    for axis in range(f):
        stride=8**axis;nxt=out[:]
        for start in range(0,len(x),8*stride):
            for off in range(stride):
                for r in range(8):
                    z=v.ZERO
                    for c in range(8):z=v.add(z,v.mul(G[r][c],out[start+off+c*stride]))
                    nxt[start+off+r*stride]=z
        out=nxt
    return out

R=v.word(v.adjoint(P),Q)
R2=v.word(R,R);R3=v.word(R2,R)
req(v.word(R3,R)==v.ident(),'actual phase-bearing coupling order four')
poly=v.plus(v.plus(v.ident(),v.scale(v.q(-2),R)),v.plus(v.scale(v.q(4),R2),v.scale(v.q(-8),R3)))
Li=v.scale(v.q(v.F(-1,15)),v.word(poly,v.adjoint(P)))
L=v.plus(P,v.scale(v.q(2),Q))
req(v.word(L,Li)==v.ident(),'left coupling inverse')
req(v.word(Li,L)==v.ident(),'right coupling inverse')
tests=0;controls=0
for f in (1,2):
    apply=lambda G,x:tensor_apply(G,x,f)
    for seed in range(6):
        x=[v.q((13*j+seed)%11-5,(7*j+3*seed)%9-4) for j in range(8**f)]
        y=[v.q((5*j+seed)%7-3,(11*j+seed)%13-6) for j in range(8**f)]
        t=apply(A,x)
        mixed=plus(plus(y,apply(P,t)),apply(Q,t),2)
        s=apply(A,mixed)
        req(s==plus(apply(A,y),apply(A,plus(apply(P,t),apply(Q,t),2))),'dirty two-call')
        recovered=plus(plus(apply(v.adjoint(A),s),apply(P,t),-1),apply(Q,t),-2)
        req(recovered==y and apply(v.adjoint(A),t)==x,'two-call inverse')
        u=apply(J,apply(W,s))
        rhs=plus(plus(apply(J,apply(W,apply(A,y))),apply(M,apply(C[2],x))),apply(K,apply(a,x)),2)
        req(u==rhs,'three-call dirty block')
        req(apply(J,apply(W,apply(A,y)))!=[v.ZERO]*len(y),'dirty baseline retained');controls+=1
        for sign in (1,-1):
            sector=scaled(plus(x,apply(T,x),sign),v.F(1,2))
            t0=apply(A,sector)
            s0=apply(A,plus(apply(P,t0),apply(Q,t0),2))
            u0=apply(J,apply(W,s0))
            clean=scaled(plus(u0,apply(M,apply(T,t0)),-sign),v.F(1,2))
            clean=apply(v.adjoint(correction),clean)
            req(clean==apply(K,sector),'sector canonical target including phase')
            tests+=1
        tests+=3
print(json.dumps({'status':'PASS_INDEPENDENT_WORD_REVIEW','widths':[1,2],'exact_vector_identities':tests,'dirty_baseline_controls':controls,'exact_coupling_inverse_checks':3,'all_width_basis':'separate tensorized word products; proof in WORD-REVIEW.md','new_kappa':False},sort_keys=True))
