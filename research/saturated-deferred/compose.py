#!/usr/bin/env python3
"""Compose PR99 saturation, PR97 signed interfaces, and PR100 transfer.

Physical producers: Swapnil Jain, Zhihao Chen, djsmanchanda and credited
predecessors. Balanced transfer and primary moment refinement: Rohan Arun.
This integration and independent checks: OpenAI Codex assistance. Apache-2.0.
This arithmetic entry point does not replace the complete physical replay.
"""
import sys
if not __debug__:
    raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,math
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVES=ROOT/'references/signed-recursion'
GRID=10**18
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module
def stable(value):
    if isinstance(value,dict):return {k:stable(v)for k,v in value.items()if k!='elapsed'}
    if isinstance(value,list):return [stable(v)for v in value]
    return value
def js(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {str(k):js(v)for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [js(v)for v in value]
    return value
def rational(value):
    if isinstance(value,dict):return {k:rational(v)for k,v in value.items()}
    if isinstance(value,list):return [rational(v)for v in value]
    if isinstance(value,str):
        try:return Q(value)
        except ValueError:return value
    return value
def normalized_hash(value):
    return hashlib.sha256(json.dumps(stable(value),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(path):return json.loads(path.read_text())
def halving(m,r):
    degree=1
    while m**degree<=2*r**degree:degree+=1
    return degree

def inputs(work=None):
    if work is None:
        paths={name:HERE/file for name,file in [('bit','bit-ledger.json'),('complex','complex-ledger.json'),('bridge','bridge.json')]}
    else:
        base=work/'research/deferred-signed'
        paths={name:base/file for name,file in [('bit','round7-literal-ledger/result.json'),('complex','round6-complex-literal-ledger/result.json'),('bridge','round7-balanced-assembly-candidate.json')]}
    return {name:read(path)for name,path in paths.items()}

def physical_profiles(data):
    bit,cx=data['bit'],data['complex']
    assert all(bit[k]for k in ('complete_forward_F2','complete_reflected_F2','reflected_frame_continuity','all_scalar_gates_equal_frame_keys','histogram_matches_external'))
    assert all(cx[k]for k in ('actual_forward_equal_frames','reflected_continuity','actual_geometry_passed','histogram_matches_pinned'))
    profiles={}
    for name,ledger,field in [('bit',bit,'histogram'),('complex',cx,'full_histogram')]:
        h,R=ledger['h'],ledger['roles'];v=math.comb(h,3);N=v*v;m=h*h;W=2*N+2*v*R
        rows={int(t):n for t,n in ledger[field].items()}
        assert all(type(t)is int and type(n)is int and 0<t<m and n>0 for t,n in rows.items())
        rank=sum(t*n for t,n in rows.items());assert rank==ledger['recursive_rank']
        if name=='bit':assert rank==m*W-N+2*v*h*(h-1)
        profiles[name]=dict(h=h,R=R,v=v,N=N,m=m,W=W,s=rank,maxchild=max(rows),child_multiplicities=rows)
    return profiles

def derive_bridge(data,profiles):
    original=rational(data['bridge']);b,c=profiles['bit'],profiles['complex']
    # This is counted by the complete fresh signed frame/event producer.
    updates=data['complex']['literal_scalar_updates_including_copied_scatter']
    G=2*c['v']*updates+4*c['h']*c['v']+4*c['N']
    assert original['literal_word_events']==updates and original['scalar_group_bound']==G
    m,W,s,r=(c[k]for k in ('m','W','s','maxchild'))
    E=64*(W+m+G+1)**3;literal=2*G*W*W+8*s+4*W+4+32*m;B=s+E
    semantic=dict(E=E,literal_charge=literal,strict_literal_gap=E-literal,B=B,C0=32*m*B*B,C1=1)
    assert semantic==original['bridge']['semantic']
    semantic['induction_gap']=2*B*(m-r)-(s+E)
    bridge={}
    for name,p in profiles.items():
        x=dict(m=p['m'],W=p['W'],maxchild=p['maxchild'],halving_degree=halving(p['m'],p['maxchild']))
        if name=='complex':x['s']=p['s']
        assert x==original['bridge'][name]
        x['wire_bits']=p['W'].bit_length()
        if name=='complex':x['scalar_group_upper']=G
        bridge[name]=x
    coefficient=sum(bridge[name]['halving_degree']*bridge[name]['wire_bits']for name in bridge)
    degree=1000*((coefficient*51)//25000+1)
    rows=dict(coefficient=coefficient,degree=degree,degree_gap=Q(degree)-Q(51,25)*coefficient)
    assert rows==original['bridge']['rows']
    rows['suffix_slope']=4*degree
    bridge.update(semantic=semantic,rows=rows)
    return bridge

def sharp_moment(module,p):
    m,W,rows=(p[k]for k in ('m','W','child_multiplicities'))
    lo,hi=0.,.001
    for _ in range(60):
        a=(lo+hi)/2
        if math.fsum(t*n/(m*W)*math.exp(a*math.log(m/t))for t,n in rows.items())<1:lo=a
        else:hi=a
    start=int(lo*GRID);left,right=start-10**6,start+10**6
    assert module.exact_moment(m,W,rows,Q(left,GRID))['upper']<1<module.exact_moment(m,W,rows,Q(right,GRID))['lower']
    while right-left>1:
        mid=(left+right)//2
        if module.exact_moment(m,W,rows,Q(mid,GRID))['upper']<1:left=mid
        else:right=mid
    accepted=module.exact_moment(m,W,rows,Q(left,GRID));rejected=module.exact_moment(m,W,rows,Q(right,GRID))
    assert accepted['upper']<1<rejected['lower'] and right==left+1
    return dict(saving=Q(left,GRID),moment=accepted,next_saving=Q(right,GRID),next_moment=rejected)

def compose(work=None):
    moments=load('saturated_primary_moments',ARCHIVES/'pr100/research/deferred-balanced/moments.py')
    balanced=load('saturated_balanced_assembly',ROOT/'research/copied-fixed/balanced_assembly.py')
    if work is not None:
        selected=work/'research/deferred-signed/swapnil-round7/certificates/round7/deferred_23.json.gz'
        assert selected.read_bytes()==(HERE/'schedule.json.gz').read_bytes(),'Work tree does not contain the selected saturated schedule'
    data=inputs(work);profiles=physical_profiles(data);bridge=derive_bridge(data,profiles)
    balanced.validate_bridge(bridge)
    bit=sharp_moment(moments,profiles['bit'])
    b=Q(36926111,500000000000);p=profiles['complex']
    cxmoment=moments.exact_moment(p['m'],p['W'],p['child_multiplicities'],b)
    assert cxmoment['upper']<1
    a=bit['saving'];h=Q(1,10**12);q=a*(1-2*h);g=(1-h)*q/(1+q)
    k=Q((g*GRID).__floor__(),GRID)
    if k==g:k-=Q(1,GRID)
    result=balanced.assembly(bridge,a,k,beta=Q(1,10),h=h,a_complex=b)
    try:balanced.assembly(bridge,a,k+Q(1,GRID),beta=Q(1,10),h=h,a_complex=b)
    except balanced.InvalidAssembly:pass
    else:raise AssertionError('Adjacent assembly grid accepted')
    return dict(scope='Complete supplied literal profiles with exact moments and balanced assembly; physical replay and inherited analytic/tape hypotheses are separate obligations.',
        bit_saving=a,kappa=k,h=h,bit=dict(**profiles['bit'],**bit),complex=dict(**profiles['complex'],saving=b,moment=cxmoment),
        assembly=result,eventual_bounds=balanced.cutoffs(bridge,result),next_kappa_grid_rejected=True,
        input_normalized_sha256={name:normalized_hash(value)for name,value in data.items()},
        schedule_sha256=hashlib.sha256((HERE/'schedule.json.gz').read_bytes()).hexdigest(),
        previous_pr100_kappa=Q(63978919675787,GRID),improvement_over_pr100=k-Q(63978919675787,GRID))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--work',type=Path);parser.add_argument('--output',type=Path,default=HERE/'certificate.json');args=parser.parse_args()
    result=compose(args.work);args.output.write_text(json.dumps(js(result),indent=2,sort_keys=True)+'\n')
    print('PASS exact saturated composition; bit',result['bit_saving'],'kappa',result['kappa'],'47 inequalities / seven margins / adjacent grids')
if __name__=='__main__':main()
