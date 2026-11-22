"""Reprice the literal nine-contact native graph and its 36-call placement."""
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


def counts(g):
    d={int(c):f['dim'] for c,f in g['frames'].items()};u=Counter();v=Counter()
    for r in g['program']:
        if r[0]=='MOVE':
            s,t=r[2:];z=d[t]-d[s];assert z;(u if z>0 else v)[abs(z)]+=1
    return u,v


def run(reference_dir,new_path):
    root=Path(reference_dir);code=root/'price_audit.py';assert sha256(code.read_bytes()).hexdigest()=='ca650d573f605bf51a8806a772903b6775cd036dfbfe7f043eccd3e51bc9977b'
    spec=importlib.util.spec_from_file_location('p104_pinned_integer_root_price',code);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    targets,paid=m.load_inputs();old=json.loads(gzip.decompress((root/'strong-bit.json.gz').read_bytes()));raw=gzip.decompress(Path(new_path).read_bytes());assert sha256(raw).hexdigest()=='8808114e43456fa966b63a6645808c8fdb32a589dff6270ad5407e0f7c85d52d';new=json.loads(raw)
    up,down=counts(old);updated,newdown=counts(new);assert updated==up and down==Counter({1:17,2:1,4:1,5:8}) and newdown==Counter({8:9}) and old['start']==new['start'] and old['final']==new['final']
    q=m.K;c=Fraction(70084296829703,2**54);assert q==Fraction(194523,50_000_000)
    def format_interval(bounds,places=18):return m.enclosing_text(*bounds,places)
    def price(hist):return format_interval(m.raw_difference(hist,{},q))
    whole={}
    for n in (0,1,36):
        changed=paid.copy()
        for r,v in down.items():changed[r]-=n*v
        for r,v in newdown.items():changed[r]+=n*v
        assert all(v>=0 for v in changed.values());assert sum(changed.values())==104904-18*n and sum(k*v for k,v in changed.items())==285600+9*n
        sd=m.raw_difference(targets,changed,q);ps=m.powered_surplus(targets,changed,c,268,m.Z,m.W,m.WEIGHT,15);assert sd[1]<0 and ps[1]<0
        # Same signed-count monotonicity test as #8027, with a changed rank-eight constant.
        signed={r:targets.get(r,0)-changed.get(r,0) for r in set(targets)|set(changed)};assert all(signed[r]<=0 for r in range(1,8));assert all(signed[r]==-444 and signed[r+1]==444 for r in (14,21,28,35,42,49,56));assert {r for r in signed if r>8}-{14,15,21,22,28,29,35,36,42,43,49,50,56,57}=={64,127} and signed[64]>0 and signed[127]>0
        grid=10**17;lo,hi=0,grid//200;assert m.raw_difference(targets,changed,Fraction(lo,grid))[0]>0 and m.raw_difference(targets,changed,Fraction(hi,grid))[1]<0
        while hi-lo>1:
            mid=(hi+lo)//2;z=m.raw_difference(targets,changed,Fraction(mid,grid));assert z[0]>0 or z[1]<0
            if z[0]>0:lo=mid
            else:hi=mid
        whole[n]={'paid_positions':sum(changed.values()),'total_rank':sum(r*v for r,v in changed.items()),'raw_target_minus_paid_at_trial':format_interval(sd),'268_factor_relative_surplus_at_supplier_margin':format_interval(ps),'directed_raw_crossing':format_interval((Fraction(lo,grid),Fraction(hi,grid)),17)}
    return {'trial_kappa':str(q),'powered_bit_saving':str(c),'unchanged_local_upward_price':price(up),'native_local_downward_price':price(down),'nine_local_downward_price':price(newdown),'native_complete_local_price':price(up+down),'nine_complete_local_price':price(up+newdown),'literal_local_price_increase':format_interval(m.raw_difference(newdown,down,q)),'caller_rewritten_local_occurrences':whole,'unchanged_productive_interfaces':sum(targets.values()),'conditional_inherited_analytical_lower_bound':'0.0038901152865907 using the native 27-contact word (#8035)'}

if __name__=='__main__':print(json.dumps(run(sys.argv[1],sys.argv[2]),indent=2,sort_keys=True))
