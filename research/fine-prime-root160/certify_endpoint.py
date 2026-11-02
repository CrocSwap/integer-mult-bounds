"""Exact outward-rounded moment bracket using two retained algorithms.
The proposed endpoint is data. No floating point or root finder runs here.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
import json,sys,hashlib,importlib.util,copy
P=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Assertions required')
def read(n):return json.loads((P/n).read_text())
def load(name):
 s=importlib.util.spec_from_file_location(name,P/'reference'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
param=read('PARAMETERS.json');ep=read('ENDPOINT.json');source=read('inputs/SOURCE-SPEC.json');derived=read('inputs/SPEC.json');expected=copy.deepcopy(source);expected['expected']['complex_lower']=ep['lower'];assert derived==expected
H={int(k):int(v)for k,v in source['expected']['global_profile'].items()};m=source['geometry']['dimension'];W=source['expected']['live'];lo,hi=Q(ep['lower']),Q(ep['upper'])
assert ep['profile']=={str(k):v for k,v in H.items()}and ep['m']==m and ep['live']==W
assert 0<Q(source['expected']['complex_lower'])<lo<hi and hi-lo==Q(1,10**param['root_digits'])
A=load('fine_mercator');B=load('fine_moment');A.DYAD=1<<param['mercator_bits'];A.LOGN=param['mercator_log_terms']+1;A.EXPN=param['exp_terms'];B.GRID=10**param['moment_grid_digits'];B.LOG_TERMS=param['log_terms'];B.EXP_TERMS=param['exp_terms'];B.log_bounds=lru_cache(None)(B.log_bounds)
assert (A.LOGN-1)%2==0
rows={}
for name,fn in [('alternating_mercator',lambda x:A.moment(H,m,W,x)),('base_two_atanh',lambda x:B.moment(m,W,list(H.items()),x))]:
 l,u=fn(lo);rl,ru=fn(hi);assert 0<l<=u<1<rl<=ru
 rows[name]=dict(lower_endpoint_interval=[str(l),str(u)],upper_endpoint_interval=[str(rl),str(ru)],acceptance_margin=str(1-u),upper_rejection_margin=str(rl-1))
leader=read('inputs/LEADER1839.json');assert Q(leader['kappa_rational'])<lo
result=dict(status='PASS_TWO_ENGINE_ENDPOINT_BRACKET',lower=str(lo),upper=str(hi),engines=rows,profile=H,m=m,live=W,monotonicity='Every positive child term (n*r/(m*W))*(m/r)^b is strictly increasing in b because 0<r<m. The accepted lower and rejected upper therefore enclose the same unique positive moment root.',scope='Exact finite moment recertification of the unchanged supplier profile; full native admission and all inherited theorem hypotheses are separate.',source_hashes={f:hashlib.sha256((P/f).read_bytes()).hexdigest()for f in ['inputs/SOURCE-SPEC.json','inputs/SPEC.json','PARAMETERS.json','ENDPOINT.json','reference/fine_mercator.py','reference/fine_moment.py']})
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
