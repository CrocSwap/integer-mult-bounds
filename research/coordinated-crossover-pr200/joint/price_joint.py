from pathlib import Path
from fractions import Fraction as Q
import json,sys,importlib.util
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
D=Path(__file__).resolve().parent;PACKAGE=D.parent;ROOT=PACKAGE.parents[1];P=ROOT/'research/paired-cube-diagonal-bit-168'
sys.path.insert(0,str(P/'bit'));sys.path.insert(0,str(P/'arithmetic'))
from prove import certify
record=json.loads((PACKAGE/'newg/profile.json').read_text());banks=json.loads((D/'joint-banks.json').read_text());r=record['profile'];H={int(k):n for k,n in r['child_histogram'].items()};assert H.pop(60)==2200 and H.pop(54)==13 and H.pop(57,0)==0 and H.pop(36)==18 and H.pop(39)==48
H={t:24*n for t,n in H.items()};mass=sum(t*n for t,n in H.items());assert 72*banks['W']-mass==banks['deficit']
row=dict(m=72,W_per_vertex=banks['W'],child_histogram=H,rank_per_vertex=mass,deficit_per_vertex=banks['deficit'],maxchild=max(H));coarse=certify(row)
spec=importlib.util.spec_from_file_location('base_two_moment',ROOT/'research/coordinated-crossover-pr200/geometry/base_two_moment.py');alt=importlib.util.module_from_spec(spec);spec.loader.exec_module(alt)
a=coarse['coarse_saving'];fb=32*72**2*sum(H.values());_,upper=alt.moment(72,banks['W'],list(H.items()),a);_,bad=alt.moment(72,banks['W'],[(1,fb)],a);assert upper+Q(1,10**16)*bad<1
lower,_=alt.moment(72,banks['W'],list(H.items()),a+Q(1,10**18));badlower,_=alt.moment(72,banks['W'],[(1,fb)],a+Q(1,10**18));assert lower+Q(1,10**16)*badlower>1
def enc(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):enc(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [enc(v)for v in x]
 return x
(D/'joint-paid.json').write_text(json.dumps(enc(dict(profile=row,coarse=coarse,independent_base2_pass=True)),indent=2)+'\n')
import subprocess
subprocess.run([sys.executable,'-B',str(D/'arithmetic.py')],check=True)
