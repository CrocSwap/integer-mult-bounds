"""Exact whole-controller moment gate for emitted phase rank witnesses.

This checks invoice arithmetic, conditional on the rank witness. It does not
substitute for arbitrary-column native/phase lowering or helper normalization.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
import owned_phase_probe as P

def main():
    path=ROOT/'research/kappa-rebuild/transfer-audit/outer_transfer_audit.py'
    spec=importlib.util.spec_from_file_location('phase_invoice_intervals',path)
    X=importlib.util.module_from_spec(spec);spec.loader.exec_module(X)
    @lru_cache(None)
    def log(n):return X.log_integer(n)
    def exp(x):
        if x<0:
            a,b=exp(-x);return X.down(1/b),X.up(1/a)
        shifts=0
        while x>=F(1,10):x/=2;shifts+=1
        a,b=X.exp_small(x)
        for _ in range(shifts):a,b=X.down(a*a),X.up(b*b)
        return a,b
    t=F(99697822419,100000000000)
    @lru_cache(None)
    def power(n):
        if not n:return F(0),F(0)
        a,b=log(n);return exp(t*a)[0],exp(t*b)[1]
    def moment(profile):
        a=b=F(0)
        for rank,n in profile.items():
            lo,hi=power(rank)
            if n>=0:a+=n*lo;b+=n*hi
            else:a+=n*hi;b+=n*lo
        return a,b
    baseline=ROOT/'research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json'
    source=json.loads(baseline.read_text(encoding='utf-8'))
    localT=Counter({4:28,7:7,8:47,9:326});localP=Counter({1:2201,2:412,3:510,4:127,5:40,8:8})
    globalT=Counter({int(k):v for k,v in source['targets'].items()})
    globalP=Counter({int(k):v for k,v in source['paid'].items()})
    witnesses=json.loads((HERE/'ONE-DEFECT-WITNESSES.json').read_text(encoding='utf-8'));results=[]
    for w in witnesses:
        v=w['result'];d=v['added_paid_rank'];r=v['old_paid_rank'];assert d>0
        paidDelta=Counter();paidDelta[r+d]+=1
        if r:paidDelta[r]-=1
        targetDelta=Counter();roles=set()
        for g in v['helper_gains']:
            assert g['role'] not in roles;roles.add(g['role'])
            old,new=g['old_rank'],g['old_rank']+g['added_rank']
            assert 0<old<new<=9
            targetDelta[old]-=1;targetDelta[new]+=1
        T=Counter(localT);T.update(targetDelta);T+=Counter()
        Q=Counter(localP);Q.update(paidDelta);Q+=Counter()
        assert all(localP[k]+paidDelta[k]>=0 for k in paidDelta)
        assert all(localT[k]+targetDelta[k]>=0 for k in targetDelta)
        reward,cost=moment(targetDelta),moment(paidDelta)
        surplus=(18*(reward[0]-cost[1]),18*(reward[1]-cost[0]))
        GT=Counter(globalT);GT.update({k:18*n for k,n in targetDelta.items()});GT+=Counter()
        GP=Counter(globalP);GP.update({k:18*n for k,n in paidDelta.items()});GP+=Counter()
        all_t_loss=r==0 and d==1 and len(v['helper_gains'])==1 and v['helper_gains'][0]['added_rank']==1
        if all_t_loss:assert surplus[1]<0
        results.append(dict(edge=w['edge'],local_helpers=dict(T),local_paid=dict(Q),
            whole_targets=dict(GT),whole_paid=dict(GP),whole_moment_surplus_delta=list(map(str,surplus)),
            strictly_negative_for_every_0_lt_t_lt_1_by_subadditivity=all_t_loss,
            positive_moment_gain_certified=surplus[0]>0))
    result=dict(status='PASS_EXACT_WHOLE_PHASE_INVOICE_ARITHMETIC',exponent=str(t),
        script_sha256=P.digest(__file__),witnesses_sha256=P.digest(HERE/'ONE-DEFECT-WITNESSES.json'),
        independent_interval_engine_sha256=P.digest(path),baseline_whole_arithmetic_sha256=P.digest(baseline),
        witness_count=len(results),positive_witnesses=sum(x['positive_moment_gain_certified'] for x in results),
        all_t_negative_witnesses=sum(x['strictly_negative_for_every_0_lt_t_lt_1_by_subadditivity'] for x in results),
        results=results,scope='Conditional on emitted exact form ranks. Full controller multiplicity18 and every unchanged charge retained. No native lowering, absolute phase, helper normalizer, compiler or kappa claim.')
    (HERE/'INVOICE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print('WHOLE_PHASE_INVOICE',len(results),'witnesses',result['positive_witnesses'],'positive')
if __name__=='__main__':main()
