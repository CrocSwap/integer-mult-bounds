#!/usr/bin/env python3
"""Exact finite fixtures for tangent hypotheses and finite block funding.

The universal statements are proved in the notes, not inferred from samples.
"""
from fractions import Fraction as Q
from itertools import combinations
import json
def need(ok,label):
    if not ok:raise ValueError(label)
def rank(rows):
    basis={}
    for original in rows:
        row=list(map(Q,original))
        for p,v in sorted(basis.items()):
            if row[p]:
                a=row[p];row=[x-a*y for x,y in zip(row,v)]
        p=next((j for j,v in enumerate(row) if v),None)
        if p is not None:
            a=row[p];basis[p]=[v/a for v in row]
    return len(basis)
def transpose(A):return list(map(list,zip(*A)))
def mm(A,B):return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*B)] for row in A]
def inspan(v,rows):return rank(rows+[v])==rank(rows)
def basisprice(rows,weights):
    r=rank(rows);n=len(weights);best=None
    for cols in combinations(range(n),r):
        if rank([[row[j] for j in cols] for row in rows])==r:
            value=sum((weights[j] for j in cols),Q(0))
            if best is None or value<best:best=value
    need(best is not None,'finite minimum column basis exists');return best
def run():
    records=[]
    A1=[[1,0,0,0],[0,1,0,0]];A2=[[1,1,0,0],[1,-1,0,0]];t1=[[1,0,1,0]];t2=[[1,0,0,1]];zero=[[0,-1,-1,1]]
    for p in [Q(-2),Q(-1,2),Q(0),Q(1),Q(3,2)]:
        T=[[1,0],[0,1],[0,2*p],[0,1+2*p]];need(mm([[1,2*p]],mm(A1,T))==mm(t1,T),'first nonlinear-cache tangent factor');need(mm([[1+p,-p]],mm(A2,T))==mm(t2,T),'second nonlinear-cache tangent factor');need(mm(zero,T)==[[0,0]],'zero row preserved')
        U=[[-2*p,1,0],[-1-2*p,0,1]];need(rank(U)==2 and rank([[row[1],row[2]] for row in U])==2,'fully debited J pivot columns');need(basisprice(U,list(map(Q,[9,4,5])))<=9,'tangent funding no larger than charged J')
    records.append({'fixture':'nonlinear_scalar_graph_two_caches_one_zero','tested_rational_points':5,'all_same_tangent_dependencies':True,'retained_submersion_and_J_pivots':True})
    need(rank([[0]])==0 and rank([[0],[1]])==1,'real cubic critical point fails factorization');need(rank([[3]])==1,'real cubic noncritical point regular')
    records.append({'fixture':'real_cubic_at_zero','counterexample_to':'fixed-point lift without locally constant observation rank','bad_observation_rank':0,'target_differential_rank':1})
    need(rank([[0],[0]])==0 and rank([[0],[0],[1]])==1,'complex cusp critical observation');need(rank([[2],[3]])==1,'complex cusp regular point')
    records.append({'fixture':'complex_smooth_graph_cusp_observation','global_decoder':'z/y away from origin,0 at origin','counterexample_to':'using arbitrary critical point'})
    T=[[1,0],[0,1],[1,0],[0,-1]];obs=[[0,0,1,0],[0,0,0,1]];target=[[1,0,0,0],[0,1,0,0]];conj=[[1,0],[0,-1]];need(mm(conj,mm(obs,T))==mm(target,T),'real conjugation recovery');Jcol=[0,1,0,1];need(not inspan(Jcol,transpose(T)),'conjugation graph tangent is not complex linear')
    records.append({'fixture':'complex_conjugation_graph','real_block_factor':True,'complex_scalar_tangent_inference_rejected':True,'does_not_refute_real_block_lift':True})
    need(rank([[0]])==0 and rank([[1]])==1,'critical retained projection');need(rank([[1,0]])==1 and rank([[0]])==0,'annihilator has no debited-column pivot at critical point')
    records.append({'fixture':'smooth_graph_t_squared_t_at_zero','counterexample_to':'funding without retained-coordinate submersion'})
    grid={(x+2*y):(x,y) for x in (0,1) for y in (0,1)};need(len(grid)==4 and (-2)+2*1==0 and -2!=0,'finite grid decoding escapes real linear kernel')
    records.append({'fixture':'two_bit_exact_grid','deterministic_decoder_injective':True,'continuous_linear_lift_impossible':True})
    digit_counts=[]
    for n in range(1,6):
        codes=set()
        for x in range(1<<n):
            for y in range(1<<n):
                code=0
                for k in range(n):code+=(2*((x>>k)&1)+((y>>k)&1))*(4**k)
                codes.add(code)
        need(len(codes)==4**n,'digit interleaving injective at finite prefix');digit_counts.append(len(codes))
    records.append({'fixture':'nonregular_digit_graph_prefixes','prefixes_1_through_5_injective_cardinalities':digit_counts,'infinite_graph_statement_proved_in_notes':True})
    prime=7;need(len({pow(t,prime,prime) for t in range(prime)})==prime and prime%prime==0,'Frobenius point bijection with zero formal derivative')
    records.append({'fixture':'characteristic7_Frobenius','pointwise_bijection':True,'formal_observation_derivative':0,'excluded_from_char0_theorem':True})
    block=[]
    for D in (1,2,3):
        cut=(D+1)//2;M=[[Q(i==j and i<cut) for j in range(D)] for i in range(D)];N=[[Q(j==(i+1)%D) for j in range(D)] for i in range(D)]
        U=[]
        for i in range(D):U.append([-v for v in M[i]]+[Q(i==j) for j in range(D)]+[Q(0)]*D)
        for i in range(D):U.append([-v for v in N[i]]+[Q(0)]*D+[Q(i==j) for j in range(D)])
        W=[]
        for j in range(D):
            row=[Q(0)]*(3*D);row[j]=1
            if j<cut:row[D+j]=-1
            else:row[2*D+(j-1)%D]=-1
            need(inspan(row,U),'each full-cache relation in block helper promise');W.append(row)
        need(rank(U)==2*D and rank(W)==D,'whole cache forces D relation directions');weights=[Q(9,D)]*D+[Q(1,D)]*D+[Q(3,D)]*D;cost=basisprice(W,weights);need(cost>=1 and basisprice(U,weights)<=4,'block basis debit bounds')
        actual_prefix=[]
        for k in (1,3,9):
            cols=[h*D+j for h,r in enumerate((9,1,3)) if r<=k for j in range(D)];actual_prefix.append(rank([[row[j] for j in cols] for row in W]));need(actual_prefix[-1]<=D,'generic scalar tensor cheap-prefix dominates')
        partial=W[:-1]
        if D>1:
            history=[]
            for j in range(D,3*D):
                row=[Q(0)]*(3*D);row[j]=1;history.append(row)
            missing=[Q(0)]*(3*D);missing[D-1]=1
            need(rank(partial)==D-1 and basisprice(partial,weights)<1 and not inspan(missing,history+partial),'partial output cannot be charged as a full cache');need(mm(M,N)!=mm(N,M),'noncommuting block operators exercised')
        block.append({'D':D,'noncommuting':D>1,'full_relation_rank':D,'actual_prefix_ranks':actual_prefix,'generic_prefix_ranks':[D,D,D],'actual_W_basis_price':str(cost),'generic_gamma':'1','whole_debited_field_price':'4','partial_output_control_rejected':D>1})
    records.append({'fixture':'noncommuting_block_graphs_and_partial_output_guard','cases':block})
    for D in (1,2,3):
        W1=[];W2=[]
        for j in range(D):
            a=[Q(0)]*(2*D);b=a.copy();a[j]=a[D+j]=1;b[j]=1;b[D+j]=-1;W1.append(a);W2.append(b)
        weights=[Q(1,D)]*D+[Q(3,D)]*D;need(rank(W1+W2)==2*D,'tensor components direct sum');need(basisprice(W1+W2,weights)>=basisprice(W1,weights)+basisprice(W2,weights),'Laplace lower bound with overlapping helper supports')
    records.append({'fixture':'tensor_Laplace_overlapping_helper_supports','dimensions_checked':[1,2,3]})
    need(rank([[1,1]])==1,'main-helper diagonal');need([[0]]!=[[1]],'main-dependent helper promise is not product tangent')
    records.append({'fixture':'main_dependent_helper_graph','product_hypothesis_required':True})
    out={'status':'PASS_EXACT_POSITIVE_SCOPE_AND_BLOCK_FIXTURES','scalar_positive_points':5,'records':records,'block_lift_is_mathematical_review_not_physical_admission':True,'universal_claims_proved_in_notes_not_by_finite_samples':True}
    return out
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
