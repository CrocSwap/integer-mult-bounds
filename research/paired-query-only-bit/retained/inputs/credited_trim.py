#!/usr/bin/env python3
"""Exact finite target-restriction strictification; Python standard library.

Source interval implementation is unchanged and authenticated; see INPUTS.json.
New theorem and construction: PROOF.md. An invoice is not a native admission.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('credited_exact_intervals',HERE/'inputs/exact_arithmetic.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)

def require(ok,message):
    if not ok: raise ValueError(message)

def load_hist(h):
    q={int(k):int(n) for k,n in h.items()}
    require(all(k>0 and n>0 for k,n in q.items()),'positive integer inventories')
    return q

def rational_up(x,digits=15):
    scale=10**digits
    return Q(-((-x*scale).__floor__()),scale)

def display_point(x):
    return E.display((x,x))

def certificate(T,P,C,v,c,b,u,w,uniform_gap=None,label='source',source_status='unadmitted'):
    T,P=load_hist(T),load_hist(P)
    C,u,w=Q(C),Q(u),Q(w);t=1-C
    require(0<C<1 and u>=C and w>0,'valid moment exponents')
    require(isinstance(v,int) and v>=1,'positive integer power')
    m=max(T)
    require(1<c<b<m and isinstance(c,int) and isinstance(b,int),'strict integer rank bases')
    require(max(P)<m,'raw maximum paid rank is below ambient')
    Tt,Pt=E.moment(T,t),E.moment(P,t)
    alpha=E.divide(Pt,Tt)
    gamma=E.divide(E.moment(P,t+u),E.mul(E.power(c,u),Tt))
    lam=E.divide(E.mul(E.power(b,w),E.moment(T,t-w)),Tt)
    bounds=[rational_up(x[1]) for x in (alpha,gamma,lam)]
    require(all(0<a<1 for a in bounds),'all three finite tail bounds below one')
    a,g,l=bounds
    # (1-s)^v <= 1/(1+v*s), all exact rational arithmetic.
    norm=1/(1+v*(1-a))+2*g**v+l**v
    require(norm<1,'strict paid plus discarded moment below original productive moment')
    p1=sum(k*n for k,n in P.items());b0=sum(T.values());p0=sum(P.values())
    result={
      'label':label,'source_status':source_status,
      'targets':{str(k):n for k,n in sorted(T.items())},
      'paid':{str(k):n for k,n in sorted(P.items())},
      'tested_saving':str(C),'tensor_power':v,'cutoff_base':c,'floor_base':b,
      'paid_tail_offset':str(u),'target_tail_offset':str(w),
      'alpha':E.display(alpha),'gamma':E.display(gamma),'lambda':E.display(lam),
      'rational_upper_limits':list(map(str,bounds)),
      'normalized_paid_plus_lost_target_upper':display_point(norm),
      'strict_normalized_gap':display_point(1-norm),
      'ambient':f'{m}^{v}','maximum_paid':f'{c}^{v}',
      'minimum_retained_target':f'{b}^{v}',
      'source_public_fields':b0,'source_paid_calls':p0,'source_paid_rank_mass':p1,
      'retained_productive_fields':f'W = sum over target tuples with product >= {b}^{v} of their multiplicities',
      'specialized_owned_fields':f'D = {b0}^{v} - W',
      'specialized_initial_and_final':0,
      'owned_allocation_records_bound':f'2*{b0}^{v}',
      'product_raw_invocation_count':f'sum(i=0..{v-1}, {b0}^({v-1}-i)*{p0}^i)',
      'split_paid_calls_upper':f'{p1}^{v}',
      'product_or_uniform_word_materialized':False,
      'rank_mass_surplus':'positive by separated t-moment advantage; no discarded target mass retained as credit',
      'construction':'chronological product; specialize low complete targets to owned zero; retain all original paid calls; split paid calls on disjoint axes',
    }
    if uniform_gap is not None:
      result['uniform_compiler']=uniform_certificate(C,v,c,b,m,Q(uniform_gap))
    return result

def uniform_certificate(C,v,c,b,m,gap):
    C,gap=Q(C),Q(gap);t=1-C
    require(0<gap<C and gap.numerator==1,'positive unit-fraction uniform gap')
    den=2
    while not c**den < b**(den-1): den+=1
    theta=Q(den-1,den)
    require(2*(c**v)**den <= (m**v)**(den-1),'shifted logarithm condition')
    eta=E.scale(E.power(m,-v*C),t)
    base=E.power(m,v*C)
    p=1
    while not theta**p<eta[0] or not base[1]<2**p:p+=1
    previous_p_fails=(theta**(p-1)>=eta[1] or base[0]>=2**(p-1))
    step=gap.denominator
    def passes(j): return (step*j+1)**p < 2**j
    lo,hi=1,2
    while not passes(hi):lo,hi=hi,hi*2
    while hi-lo>1:
      mid=(lo+hi)//2
      if passes(mid):hi=mid
      else:lo=mid
    require(passes(hi) and not passes(hi-1),'integer uniform threshold and preceding grid point')
    H=step*hi
    return {'uniform_saving':str(C-gap),'gap':str(gap),'theta':str(theta),
      'logarithm_power':p,'eta':E.display(eta),'ordinary_base_bound':E.display(base),
      'previous_logarithm_power_fails':previous_p_fails,'H':H,'N':f'2^{H}',
      'integer_test_exponent':hi,'preceding_integer_grid_fails':True,
      'proof':'retained separated finite compiler and logarithmic majorant, with all new owned fields charged'}

def product_hist(hist,v):
    out=Counter({1:1})
    for _ in range(v):
      nxt=Counter()
      for a,n in out.items():
        for b,k in hist.items():nxt[a*b]+=n*k
      out=nxt
    return out

def split_hist(hist,J):
    out=Counter()
    for r,n in hist.items():
      q,s=divmod(r,J)
      if q:out[J]+=n*q
      if s:out[s]+=n
    return out

def exact_small_inventory():
    # A rank-inventory check only: no physical source is claimed for this toy.
    T={2:2,5:1};P={1:3,3:1};v=3;c=2;b=3
    TT=product_hist(T,v);PP=product_hist(P,v)
    keep={k:n for k,n in TT.items() if k>=b**v}
    drop={k:n for k,n in TT.items() if k<b**v}
    paid=split_hist(PP,c**v)
    require(sum(TT.values())==sum(T.values())**v,'exact integer product count')
    require(sum(k*n for k,n in paid.items())==sum(k*n for k,n in PP.items()),'paid split preserves mass')
    require(max(paid)<min(keep),'small finite separated rule')
    original_mass=sum(k*n for k,n in TT.items())-sum(k*n for k,n in PP.items())
    final_mass=sum(k*n for k,n in keep.items())-sum(k*n for k,n in paid.items())
    require(original_mass-final_mass==sum(k*n for k,n in drop.items()),'every removed target rank is debited')
    require(final_mass>0,'small example positive mass')
    return {'scope':'rank-inventory mechanism; no physical source claimed','original_targets':dict(TT),
      'retained_targets':keep,'specialized_zero_targets':drop,'all_paid_after_split':dict(paid),
      'before_surplus':original_mass,'after_surplus':final_mass,'no_hidden_completion_calls':True}

def restriction_probe():
    # Exact 2-register, 2-coordinate example. Both registers receive H2.
    # The second register starts at zero but is nonzero in the middle.
    H=lambda a:[a[0]+a[1],a[0]-a[1]]
    for a in ([1,0],[0,1],[5,-2]):
      x=list(a);z=[0,0]
      z=[v+u for v,u in zip(z,x)]
      require(z!=[0,0],'discarded owner can be polluted')
      x=H(x);z=H(z)
      z=[v-u for v,u in zip(z,x)]
      require(x==H(a) and z==[0,0],'independent complete endpoint specialization')
    x=[1,0];z=x.copy();x=H(x)
    z=[v-u for v,u in zip(z,x)] # illegally omit query on zero-at-entrance owner
    require(z!=[0,0],'omitting intermediate paid call is rejected')
    return {'arithmetic':'integers','retained_columns':2,'intermediate_zero_assumption_rejected':True,
      'complete_endpoint_verified':True,'source_paid_calls_retained':2,
      'scope':'restriction lemma toy; not a native supplier improvement'}

def authenticate():
    rows=json.loads((HERE/'INPUTS.json').read_text())
    for row in rows:
      require(sha256((HERE/row['path']).read_bytes()).hexdigest()==row['sha256'],'input hash '+row['path'])
    return rows

def main():
    inputs=authenticate()
    old=json.loads((HERE/'inputs/selected-p104-result.json').read_text())['complete_cost']
    pending=json.loads((HERE/'inputs/pending-pr5827-result.json').read_text())['complete_cost']
    cases=[]
    cases.append(certificate(old['targets'],old['paid'],'0.0031004505',256,19,20,'1/5','1/5',
      uniform_gap=Q(1,14000000000),label='selected_p104_unchanged',source_status='selected conditional physical source; no new kappa'))
    cases.append(certificate(pending['targets'],pending['paid'],'0.003124766805',384,19,20,'1/5','1/5',
      uniform_gap=Q(1,1400000000000),label='pending_pr5827',source_status='pending predecessor physical source; local independent admission handled separately'))
    reduced=json.loads((HERE/'inputs/integrated-owned-reduction.json').read_text())
    require(reduced['word_sha256']=='81e996a7452d9eee04e2641ce2b2db06464145607792d476d59ab55f91852d7c'
      and len(reduced['selected_helpers'])==23,'frozen V1 integrated complex word, not interim 37-helper screen')
    cases.append(certificate(reduced['complete_targets'],reduced['complete_paid'],'0.003124766805',384,19,20,'1/5','1/5',
      uniform_gap=Q(1,1400000000000),label='integrated_neutral_reduced_complex',source_status='actual kappa010 finite source; complete source admission in complex/review'))
    cases[-1]['source_word_sha256']=reduced['word_sha256']
    cases[-1]['owned_helper_specializations']=len(reduced['selected_helpers'])
    bit=json.loads((HERE/'inputs/integrated-bit-construction.json').read_text())
    cases.append(certificate(bit['targets'],bit['paid'],'0.0034754',192,19,20,'3/10','1/2',
      uniform_gap=Q(1,10000000),label='integrated_compact436_BIT',source_status='actual kappa010 complete BIT caller; admission and delayed cover in bit/review'))
    T=load_hist(old['targets']);T[3]=T.get(3,0)+3*T.pop(9)
    cases.append(certificate(T,old['paid'],'0.0041',256,15,16,'1/10','1/20',
      uniform_gap=Q(1,100000),label='all_H9_ternary_relaxation',source_status='ACCOUNTING RELAXATION ONLY; physical helper cuts not supplied'))
    controls={}
    try:certificate(old['targets'],old['paid'],'0.0041',256,19,20,'1/5','1/5')
    except ValueError as e:controls['unfunded_current_0041']=str(e)
    else:raise ValueError('unfunded current 0.0041 accepted')
    try:certificate(old['targets'],old['paid'],'0.0031004505',256,19,20,'1/10000','1/5')
    except ValueError as e:controls['illegal_paid_tail_exponent']=str(e)
    else:raise ValueError('sublinear paid tail accepted')
    result={'schema':'kappa010-target-restriction-compiler/1','status':'PASS','inputs':inputs,
      'cases':cases,'small_inventory':exact_small_inventory(),'restriction_probe':restriction_probe(),
      'negative_controls':controls,'limits':['No source tensor product or uniform word materialized.',
      'All-column native implementation, owned erasure, original compiler semantics, precision/tape and analytic recovery remain conditional.',
      'An arithmetic certificate on a hypothetical histogram does not establish its physical construction.']}
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','cases':[{'label':r['label'],'v':r['tensor_power'],'gap':r['strict_normalized_gap'],'compiler':r.get('uniform_compiler')} for r in cases]},indent=2))

if __name__=='__main__':main()
