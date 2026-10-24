#!/usr/bin/env python3
"""Small exact four-bit support discriminator, not an all-width proof."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
N=16
ZERO=(F(0),F(0));ONE=(F(1),F(0));I=(F(0),F(1))
Q,U1,U2,W=1,2,4,8

def need(ok,why):
    if not ok:raise RuntimeError(why)

def add(a,b):return(a[0]+b[0],a[1]+b[1])
def mul(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def conj(a):return(a[0],-a[1])
def reciprocal(a):
    d=a[0]*a[0]+a[1]*a[1];need(d!=0,'nonzero monomial weight')
    return(a[0]/d,-a[1]/d)
def fresh():return[[ZERO for _ in range(N)]for _ in range(N)]
def identity():return monomial(list(range(N)),[ONE]*N)
def monomial(perm,weights):
    need(sorted(perm)==list(range(N)) and all(w!=ZERO for w in weights),'invertible weighted permutation')
    a=fresh()
    for j,(i,w)in enumerate(zip(perm,weights)):a[i][j]=w
    return a
def product(a,b):
    out=fresh()
    for i in range(N):
        for k in range(N):
            if a[i][k]==ZERO:continue
            for j in range(N):
                if b[k][j]!=ZERO:out[i][j]=add(out[i][j],mul(a[i][k],b[k][j]))
    return out
def adjoint(a):return[[conj(a[j][i])for j in range(N)]for i in range(N)]
def chain(*matrices):
    out=matrices[0]
    for a in matrices[1:]:out=product(out,a)
    return out
def permutation(a):
    cols=[[i for i in range(N)if a[i][j]!=ZERO]for j in range(N)]
    if any(len(c)!=1 for c in cols):return None
    p=[c[0]for c in cols]
    return p if sorted(p)==list(range(N))else None
def inverse_monomial(a):
    p=permutation(a);need(p is not None,'monomial inversion')
    b=fresh()
    for j,i in enumerate(p):b[j][i]=reciprocal(a[i][j])
    return b
def enc(z):return[str(z[0]),str(z[1])]
def sparse(a):return[[i,j,*enc(a[i][j])]for i in range(N)for j in range(N)if a[i][j]!=ZERO]
def digest(a):return sha256(json.dumps(sparse(a),separators=(',',':')).encode()).hexdigest()
def support(a):
    return dict(row_counts=[sum(z!=ZERO for z in row)for row in a],
                column_counts=[sum(a[i][j]!=ZERO for i in range(N))for j in range(N)])
def first_branch(a):
    for j in range(N):
        entries=[[i,*enc(a[i][j])]for i in range(N)if a[i][j]!=ZERO]
        if len(entries)>1:return dict(column=j,entries=entries)
    return None
def gaussian(v):
    need(0<v<N,'nonzero translation direction')
    a,b=(F(1,2),F(1,2)),(F(1,2),F(-1,2));out=fresh()
    for j in range(N):out[j][j]=a;out[j^v][j]=b
    return out
def cosets(v):return sorted({tuple(sorted((j,j^v)))for j in range(N)})
def maps_partition(p,active):
    blocks={tuple(j for j in range(N)if j&~active==base)for base in range(N)if base&active==0}
    return all(tuple(sorted(p[j]for j in b))in blocks for b in blocks)
def maps_direction(p,v,w):return all(p[j]^p[j^v]==w for j in range(N))
def nonaffine_witness(p):
    # Every affine Boolean map has zero second difference on this face.
    return p[0]^p[U1]^p[U2]^p[U1^U2]

def main():
    source_paths=['outputs/nonlinear-monomial-control-ceiling-20261023/PROOF.md',
      'outputs/released-operator-intersection-20261023/PROOF.md',
      'outputs/released-operator-intersection-20261023/SOURCES.json',
      'outputs/released-operator-intersection-20261023/frozen/PHYSICAL.md']
    before={n:sha256((ROOT/n).read_bytes()).hexdigest()for n in source_paths}
    ident=identity();cq=gaussian(Q);d=gaussian(W)
    need(product(adjoint(cq),cq)==ident and product(cq,adjoint(cq))==ident,'Q inverse is actual adjoint')
    need(product(adjoint(d),d)==ident and product(d,adjoint(d))==ident,'D inverse is actual adjoint')
    need(product(cq,cq)==monomial([j^Q for j in range(N)],[ONE]*N),'actual C squared is X, not identity')
    need(adjoint(cq)!=cq,'C is not self-adjoint')
    examples={}
    for label,target in [('weighted_Toffoli_q',Q),('weighted_Toffoli_w',W)]:
        controls=[int(bool(j&U1)and bool(j&U2))for j in range(N)]
        p=[j^(target if controls[j]else 0)for j in range(N)]
        h=monomial(p,[(F(2**controls[j]),F(0))for j in range(N)])
        need(nonaffine_witness(p)==target,'genuinely nonlinear permutation')
        examples[label]=h
    ccz=monomial(list(range(N)),[(F(-1 if(j&Q and j&W and j&U1)else 1),F(0))for j in range(N)])
    examples['CCZ_q_w_u1']=ccz
    validated={};result_examples={};matrices={'Q':sparse(cq),'D':sparse(d)}
    for label,h in examples.items():
        h_inv=inverse_monomial(h);need(chain(h,h_inv)==ident and chain(h_inv,h)==ident,'exact h invertible')
        q_conjugate=chain(adjoint(cq),h,cq)
        k=chain(d,h,adjoint(d));k_inv=chain(d,h_inv,adjoint(d))
        need(permutation(q_conjugate)is not None and permutation(k)is not None,'actual two conjugate monomial conditions')
        need(chain(h,cq)==chain(cq,q_conjugate) and chain(d,h)==chain(k,d),'exact intertwiner orientations')
        if label.startswith('weighted_Toffoli'):
            need(q_conjugate==h and k==h,'nonlinear weighted positive examples commute with actual Q and D')
        need(chain(k,k_inv)==ident and chain(k_inv,k)==ident,'transported k invertible')
        ph,pk=permutation(h),permutation(k)
        need(maps_partition(ph,Q)and maps_partition(ph,W)and maps_partition(ph,Q|W),'h preserves both partitions and join')
        need(maps_partition(pk,W)and maps_partition(pk,Q|W),'transported k preserves W partition and join')
        validated[label]=k
        result_examples[label]=dict(h_sha256=digest(h),Q_inverse_h_Q_sha256=digest(q_conjugate),
          D_h_D_inverse_sha256=digest(k),h_permutation=ph,k_permutation=pk,
          h_q_partition=True,h_W_partition=True,h_join_partition=True,
          k_W_partition=True,k_join_partition=True,k_q_partition=maps_partition(pk,Q),
          nonaffine_second_difference=nonaffine_witness(ph),
          h_weights=[enc(h[ph[j]][j])for j in range(N)])
        matrices[label+'_h']=sparse(h);matrices[label+'_Qinverse_h_Q']=sparse(q_conjugate);matrices[label+'_k']=sparse(k)
    k=validated['CCZ_q_w_u1'];pk=permutation(k)
    need(not maps_partition(pk,Q),'transported CCZ must reject central-coset preservation')
    x=U1;edge=[pk[x],pk[x^Q]]
    need(edge==[U1,U1^Q^W] and edge[0]^edge[1]==Q^W,'actual transported q-edge shifts w')
    need(permutation(chain(adjoint(cq),k,cq))is None,'transported k need not satisfy original Q condition')
    wrong=chain(adjoint(d),ccz,d)
    need(wrong!=k and permutation(wrong)is not None,'D order sign discriminator')
    need(chain(d,ccz,d)!=k,'missing inverse on D is detected')
    matrices['CCZ_wrong_Dinverse_h_D']=sparse(wrong)
    terminal=[]
    for label,k in validated.items():
        pk=permutation(k)
        for v in (2,3,4,5,6,7):
            for w in (1,8,9):
                need(not maps_direction(pk,v,w),'different join blocks cannot become a w-coset')
                for right_inverse in (False,True):
                    qv=gaussian(v);qw=gaussian(w)
                    terminal_matrix=chain(adjoint(qw),k,adjoint(qv)if right_inverse else qv)
                    need(permutation(terminal_matrix)is None,'nonzero-U terminal must be nonmonomial')
                    branch=first_branch(terminal_matrix);need(branch is not None,'explicit support branching')
                    terminal.append(dict(example=label,v=v,w=w,right_inverse=right_inverse,
                      matrix_sha256=digest(terminal_matrix),support=support(terminal_matrix),branch=branch))
    # Remove the join-preservation hypothesis: a literal swap can intertwine
    # the two Gaussian directions and make the very same terminal monomial.
    swap_perm=[(j&~(U1|W))|((j&U1)<<2)|((j&W)>>2)for j in range(N)]
    swap=monomial(swap_perm,[ONE]*N)
    need(chain(adjoint(cq),swap,cq)==swap,'swap still satisfies central Q condition')
    bad_d=chain(d,swap,adjoint(d))
    need(permutation(bad_d)is None and not maps_partition(swap_perm,W)and not maps_partition(swap_perm,Q|W),'swap fails D-conjugate/partition hypothesis')
    swap_terminal=chain(adjoint(gaussian(W)),swap,gaussian(U1))
    need(swap_terminal==swap and permutation(swap_terminal)is not None,'omitted join hypothesis genuinely changes answer')
    no_U_terminal=chain(adjoint(cq),validated['weighted_Toffoli_q'],cq)
    need(permutation(no_U_terminal)is not None,'nonzero U hypothesis is necessary')
    controls=dict(swap_Q_condition=True,swap_D_conjugate_monomial=False,
      swap_breaks_W_and_join=True,swap_terminal_is_exactly_swap=True,
      swap_nonmonomial_D_conjugate_branch=first_branch(bad_d),
      zero_U_terminal_monomial=True,CCZ_transported_q_edge_input=[x,x^Q],
      CCZ_transported_q_edge_output=edge,CCZ_transported_q_edge_difference=Q^W,
      CCZ_transported_Q_conjugate_nonmonomial=True,
      reversed_D_conjugation_differs=True,missing_D_inverse_differs=True,
      CCZ_k_at_q_u1_w0=enc(validated['CCZ_q_w_u1'][permutation(validated['CCZ_q_w_u1'])[Q|U1]][Q|U1]))
    matrices['swap']=sparse(swap);matrices['swap_Dconjugate']=sparse(bad_d);matrices['swap_terminal']=sparse(swap_terminal)
    need(before=={n:sha256((ROOT/n).read_bytes()).hexdigest()for n in source_paths},'read-only source hashes unchanged')
    results=dict(status='PASS_EXACT_FOUR_BIT_SUPPORT_DISCRIMINATOR',
      basis_bits=dict(q=Q,u1=U1,u2=U2,w=W),matrix_convention='M[row][column]; column inputs; rightmost applies first',
      scalars='exact pairs of Fraction(real),Fraction(imaginary); no floating membership',
      gaussian='C_v=((1+i)I+(1-i)X_v)/2; inverse=adjoint; C_v^2=X_v',
      source_sha256=before,examples=result_examples,terminal_tests=terminal,terminal_nonmonomial_count=len(terminal),
      direction_pairs_per_example=18,conjugation_orders_tested=['Qw^-1 k Qv','Qw^-1 k Qv^-1'],
      controls=controls,all_source_hashes_unchanged=True,
      scope='finite 16x16 four-bit exact support calibration only; no17-axis/all-width theorem or rank lower bound',
      native_solver_compiler_executed=False)
    (HERE/'RESULT.json').write_text(json.dumps(results,sort_keys=True,indent=2)+'\n')
    (HERE/'MATRICES.json').write_text(json.dumps(matrices,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(status=results['status'],positive_examples=len(validated),terminal_nonmonomial_tests=len(terminal),controls=controls),sort_keys=True))

if __name__=='__main__':main()
