"""Exact source-bound dirty-prefix preimages. Apache-2.0.

Prepared for ywz65 with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import argparse, hashlib, importlib.util, json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok: raise ValueError(message)


def vendor():
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage']!='input': continue
        data=(ROOT/item['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest()==item['sha256'],'source SHA256 mismatch')
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['git_blob'],'source Git blob mismatch')
    path=ROOT/'research/dirty-prefix-precision/vendor/pr628/dirty.py'
    spec=importlib.util.spec_from_file_location('credited_dirty',path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj


def word(n,source=0,target=1,scratch=None,sign=1,factors=None):
    scratch=list(range(2,2+(n-1).bit_length())) if scratch is None else scratch
    factors=list(range(n)) if factors is None else factors
    if len(factors)==1: return [(source,target,factors[0],sign)]
    k=len(factors)//2;z,rest=scratch[0],scratch[1:]
    calls=[(source,z,factors[:k],1),(z,target,factors[k:],1),
           (source,z,factors[:k],-1),(z,target,factors[k:],-1)]
    if sign==-1: calls=[(s,t,f,-a) for s,t,f,a in reversed(calls)]
    return [op for s,t,f,a in calls for op in word(n,s,t,rest,a,f)]


def run(v,arrays,ops,factors,phases,bits,direction):
    for s,t,f,sign in ops:
        v.leaf(arrays[s],arrays[t],factors[f],phases,F(1,2),bits,direction,sign,None)


def reverse(ops): return [(s,t,f,-a) for s,t,f,a in reversed(ops)]


def finite_bank():
    rows=[]
    for modulus,dimensions in product(range(2,7),(2,3)):
        universe=set(product(range(modulus),repeat=dimensions));current=set(universe)
        for cut in range(9):
            dst,src=cut%dimensions,(cut+1)%dimensions;old=current
            def step(state,sign):
                out=list(state);increment=state[src]**2+3*state[src]+cut
                out[dst]=(out[dst]+sign*increment)%modulus
                return tuple(out)
            current={step(state,1) for state in current}
            need(current==universe,'nonlinear bank prefix not onto')
            need({step(state,-1) for state in current}==old,'finite inverse failed')
        rows.append(dict(modulus=modulus,rows=dimensions,states=len(universe),cuts=9))
    return rows


def preimages(v):
    receipt=[];total=0;dirty=0
    for n,length,bits,direction in product((2,3,5),(1,2),(4,7),(-1,1)):
        factors=[(bool(i%2),(F(1,4),F(0)),F(1)) for i in range(n)]
        phases=[v.c.ONE]*length;ops=word(n);count=2+(n-1).bit_length()
        fixed=[(F(1 if j==0 else -1),F(0)) for j in range(length)]
        arrays=[fixed[:]]+[[v.c.ZERO]*length for _ in range(count-1)]
        trace=[];leaf=v.leaf
        def monitor(x,y,factor,ps,beta,w,d,sign,stats):
            trace.append((next(i for i,a in enumerate(arrays) if a is x),
                          next(i for i,a in enumerate(arrays) if a is y),
                          next(i for i,f in enumerate(factors) if f is factor),sign))
            return leaf(x,y,factor,ps,beta,w,d,sign,stats)
        try:
            v.leaf=monitor
            v.compose(arrays[0],arrays[1],factors,arrays[2:],phases,F(1,2),bits,direction)
        finally: v.leaf=leaf
        need(trace==ops,'source-bound leaf chronology disagrees')
        digest=hashlib.sha256()
        for cut in range(len(ops)+1):
            desired=[fixed[:]]+[[(F((row+1)*(j+1)-cut,1<<bits),F(row-j,1<<bits))
                                 for j in range(length)] for row in range(count-1)]
            initial=[a[:] for a in desired]
            run(v,initial,reverse(ops[:cut]),factors,phases,bits,direction)
            need(initial[0]==fixed,'preimage modified fixed original source')
            need(all(v.c.rounded(z,bits)==z for a in initial for z in a),'off-grid preimage')
            replay=[a[:] for a in initial]
            run(v,replay,ops[:cut],factors,phases,bits,direction)
            need(replay==desired,'literal preimage fails at completed leaf cut')
            total+=1;dirty+=int(cut<len(ops) and ops[cut][0]>=2)
            digest.update(json.dumps([initial,desired],default=str,separators=(',',':')).encode())
        receipt.append(dict(factors=n,length=length,bits=bits,direction=direction,
                            leaves=len(ops),prefixes=len(ops)+1,preimage_sha256=digest.hexdigest()))
    return receipt,total,dirty


def exposed_lattice(v):
    factors=[(False,(F(1,4),F(0)),F(1)) for _ in range(2)]
    phases=[v.c.ONE,v.c.ONE];ops=word(2)
    desired=[[v.c.ONE,v.c.ZERO],[v.c.ZERO,v.c.ZERO],[(F(1,16),F(0)),v.c.ZERO]]
    initial=[a[:] for a in desired]
    run(v,initial,reverse(ops[:1]),factors,phases,4,1)
    replay=[a[:] for a in initial];run(v,replay,ops[:1],factors,phases,4,1)
    need(replay==desired and ops[1][0]==2,'witness not at actual dirty-source cut')
    x=sum(z[0] for z in replay[2])/2
    coarse=v.c.rounded((x,F(0)),4)[0];fine=v.c.rounded((x,F(0)),5)[0]
    need((coarse,fine)==(F(1,16),F(1,32)),'precision witness drift')
    return dict(prefix=ops[:1],next_dirty_source=2,initial=initial,desired=desired,
                rounded_linear_coarse=coarse,rounded_linear_fine=fine,
                source_grid_units_sum=1,residual=coarse-fine)


def controls(v):
    need(round(F(1,2))==round(F(-1,2))==0,'ties-even collision missing')
    saturated=lambda y:min(1,max(-1,y+1))
    need(saturated(0)==saturated(1),'saturation collision missing')
    need(0-0==1-1,'target-dependent update collision missing')
    need({y+1 for y in (0,)}=={1} and 0 not in {1},'clean-domain control')
    src=[v.c.ONE];dst=[v.c.ZERO];factor=(False,(F(1,4),F(0)),F(1))
    v.leaf(src,dst,factor,[v.c.ONE],F(1,2),4,1,1,None)
    v.leaf(src,dst,factor,[v.c.ONE],F(1,2),5,1,-1,None)
    need(dst==[(F(1,32),F(0))],'credited mixed-precision control')
    return ['whole_sum_ties_even_collision','saturation_collision','target_dependent_update',
            'clean_initial_domain_not_full','changed_precision_is_not_literal_inverse']


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-receipt',action='store_true');args=parser.parse_args()
    v=vendor();rows,total,dirty=preimages(v)
    result=dict(schema_version=1,finite_nonlinear_banks=finite_bank(),actual_prefixes=rows,
                actual_prefix_count=total,internal_dirty_source_cuts=dirty,
                reachable_parity_counterexample=exposed_lattice(v),controls=controls(v))
    result=json.loads(json.dumps(result,default=str));path=HERE/'RESULT.json'
    if args.write_receipt:
        need(not path.exists(),'refuse receipt overwrite');path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else: need(result==json.loads(path.read_text()),'receipt mismatch')
    print(f'PASS_DIRTY_PREFIX_FULL_GRID actual_prefixes={total} dirty_source_cuts={dirty} controls=5')


if __name__=='__main__':main()
