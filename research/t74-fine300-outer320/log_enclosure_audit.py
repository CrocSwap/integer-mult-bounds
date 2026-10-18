"""Independent exact atanh oracle for the fine Mercator parity repair.
Credit Philippe Van Velzen, PR1519, for finding and counterexamples.
No predecessor audit implementation is imported.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import importlib.util,json,argparse
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('fine_mercator',P/'code/fine_mercator.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
@lru_cache(None)
def unit_log(x):
 z=(x-1)/(x+1);assert 0<=z<=Q(1,3)
 t=z;v=Q(0);n=0
 while True:
  v+=2*t/(2*n+1);t*=z*z;n+=1
  tail=2*t/((2*n+1)*(1-z*z))
  if tail<Q(1,2**1800):return v,v+tail
@lru_cache(None)
def oracle(x):
 k=0
 while x>=2:x/=2;k+=1
 a,b=unit_log(x);c,d=unit_log(Q(2));return a+k*c,b+k*d

def run():
 xs=sorted(set([Q(73,r)for r in range(1,73)]+[Q(73),Q(43),Q(189),Q(352),Q(1)]))
 margins=[]
 for x in xs:
  a,b=M.logarithm(x);l,u=oracle(x);assert a<=l<=u<=b,(x,'enclosure');margins.append(l-a)
 # Reproduce the old false lower bound without changing the fixed module.
 namespace={};text=(P/'evidence/pr1479-source/code/fine_mercator.py').read_text();assert 'LOGN = 800' in text
 exec(compile(text,'<pinned-old-parity-control>','exec'),namespace)
 rejected=[]
 for x in [Q(43),Q(189),Q(352)]:
  a,b=namespace['logarithm'](x);l,u=oracle(x);assert a>u;rejected.append(str(x))
 assert M.LOGN-1>0 and (M.LOGN-1)%2==0
 return dict(status='PASS_FINE_MERCATOR_PARITY_REPAIR_INDEPENDENT_ATANH',inputs=len(xs),actual_moment_log_inputs=73,terms=M.LOGN-1,old_false_lower_controls=rejected,oracle_tail_target='2^-1800',scope='Exact checks on current moment inputs and reported counterexamples; even-term alternating series gives the general enclosure argument. No full theorem or fresh native replay.')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);a=ap.parse_args();r=run()
 if a.out:a.out.write_text(json.dumps(r,indent=2)+'\n')
 print(r['status'],r['inputs'],flush=True)
