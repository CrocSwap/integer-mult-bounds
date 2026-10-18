"""Unchanged PR628 dirty leaves, with the new subset/prefix error bound.

Source lineage and oracle from PR628; boundary-monitor idea from PR877.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,hashlib,json,time
P=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
core=load('new_core',P/'core.py');v=load('frozen_dirty',P/'vendor/628/dirty.py')

def evaluate(state,L,d,dirt,target=128,full_grid=True):
    r=state['radix'];beta=state['beta'];n=len(state['factors'])
    factors=[(inside,b,F(r if j==0 else 1)) for j,(inside,b) in enumerate(state['factors'])]
    depth,N,C=core.resources(n)
    arrays=[[(F(dirt+3*i-2*j,8),F(2*dirt-i+j,16)) for i in range(L)] for j in range(depth+2)]
    D=max(abs(a)+abs(b) for row in arrays for a,b in row)+1
    units=[v.c.ONE,(F(0),F(1)),(F(3,5),F(4,5)),(F(-5,13),F(12,13))]
    phases=[units[(i*i+i//2+1)%4] for i in range(L)]
    core.need(len({id(a) for a in arrays+[phases]})==len(arrays)+1,'phase and array separation')
    qnorm=sum(abs(a)+abs(b) for a,b in state['q'])
    AQ=F(state['certificate']['inverse_norm_bound'])
    G=max(F(1),r*(1<<n)*qnorm*AQ)
    a=13*(r+1)/beta**3
    bits,budget=core.choose(n,G,a,D,target+1,4,beta)
    if full_grid:
        ulp=F(1,1<<bits)
        arrays[:]=[[(re+ulp,im-ulp) for re,im in row] for row in arrays]
        core.need(all(z.denominator==1<<bits for row in arrays for pair in row for z in pair),'full working-grid input has no reserved low zeros')
    core.need(max(abs(re)+abs(im) for row in arrays for re,im in row)<=D,'initial magnitude')
    original=[row.copy() for row in arrays]
    exact=v.w.solve(v.w.matrix(state['q'],phases,d),original[0])
    perturbation=F(state['certificate']['factorization_inverse_error_bound'])*D
    core.need(perturbation<=F(1,1<<(target+1)),'prepared coefficient budget')
    observed={'boundaries':0,'maximum_squared':max(v.c.norm2(z) for row in arrays for z in row)}
    leaf=v.leaf
    def monitored(x,y,factor,ps,b,w,di,sign,stats):
        before=x.copy();leaf(x,y,factor,ps,b,w,di,sign,stats)
        core.need(x==before,'exact leaf source restoration')
        observed['boundaries']+=1
        observed['maximum_squared']=max(observed['maximum_squared'],max(v.c.norm2(z) for row in arrays for z in row))
    stats={'leaves':0,'scalar_steps':0}
    try:
        v.leaf=monitored
        v.compose(*arrays[:2],factors,arrays[2:],phases,beta,bits,d,stats=stats)
    finally:v.leaf=leaf
    core.need(stats==dict(leaves=N,scalar_steps=3*L*N),'paid work')
    core.need(observed['boundaries']==N,'all leaf boundaries')
    core.need(arrays[0]==original[0] and arrays[2:]==original[2:],'arbitrary dirty restoration')
    core.need(observed['maximum_squared']<=budget['magnitude']**2,'boundary magnitude')
    net=[v.c.sub(a,b) for a,b in zip(arrays[1],original[1])]
    err2=max(v.c.norm2(v.c.sub(a,b)) for a,b in zip(net,exact))
    core.need(err2<=budget['error']**2,'rounded execution error')
    core.need(budget['error']+perturbation<=F(1,1<<target),'true kernel error')
    v.compose(*arrays[:2],factors,arrays[2:],phases,beta,bits,d,-1)
    core.need(arrays==original,'negative whole word exact inverse')
    digest=hashlib.sha256(json.dumps([net,exact,err2,budget,perturbation],default=str,sort_keys=True).encode()).hexdigest()
    return dict(radix=r,embedding=state['embedding'],length=L,direction=d,dirt=dirt,working_bits=bits,
                leaf_calls=N,boundaries=observed['boundaries'],nonzero_rounding=bool(err2),
                error_log2_upper=core.logceil(err2)/2 if err2 else None,proof_sha256=digest,
                source_restored=True,dirty_restored=True,inverse_cancels=True,all_input_low_bits_odd=full_grid)
