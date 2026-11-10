"""Independent full-invoice no-reentry bound for all 90 enlarged masks."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json,hashlib,sys
from functools import lru_cache
HERE=Path(__file__).resolve().parent
A=HERE.parent.parent/'accounting/verify.py'
if hashlib.sha256(A.read_bytes()).hexdigest()!='116ed12d5aaeef8a5fb084c95db50febb50a9df04825a3506eab633e4abffa3f':raise ValueError('Reviewed interval/accounting source changed')
spec=importlib.util.spec_from_file_location('intervals',A);iv=importlib.util.module_from_spec(spec);spec.loader.exec_module(iv)
K=Q(0);CAP=Q('.01');SCALE=10**18
nt,np=iv.source_census()

def masks(kl,kr):
 return [set([0,*range(1,i+2),*range(9,9+kr)])for i in range(8)]+[set(range(18))]+[set([0,*range(i,18),*range(9-kl,9)])for i in range(9,18)]

@lru_cache(None)
def lo(r):
 lower,upper=iv.log_bounds(r)
 return r*iv.exp_negative(CAP*upper)[0]*lower
@lru_cache(None)
def hi(r):return iv.power_bounds(r,K)[1]*iv.log_bounds(r)[1]
iv.need(1-CAP*(2+iv.log_bounds(144)[1])>0,'convex rank-log moment through rank144')
iv.need(1-CAP*iv.log_bounds(8)[1]>0,'convex extension from zero')
rows=[]
for kl in range(9):
 for kr in range(10):
  ms=masks(kl,kr);d=[len(s)-2 for s in ms]
  iv.need(d==list(range(kr,kr+8))+[16]+list(reversed(range(kl,kl+9))),'independent site dimensions')
  targets=Counter(8*sum(c in s for s in ms)+1 for c in range(18))
  iv.need(sum(r*n for r,n in targets.items())-(1+8*sum(d))==305,'root rank-mass305')
  ferrers=[sum(x>=level for x in d)for level in range(1,max(d)+1)]
  iv.need(sum(ferrers)==sum(d),'idle incidence conservation')
  bound=18*sum(n*hi(r)for r,n in np.items())-18*sum(n*lo(r)for r,n in nt.items())
  bound+=104*(sum(hi(8*m)for m in ferrers)-sum(n*lo(r)for r,n in targets.items()))
  iv.need(bound<0,'uniform no-reentry derivative for enlarged mask')
  rows.append({'kl':kl,'kr':kr,'demands':d,'targets':dict(sorted(targets.items())),'Ferrers_lengths':ferrers,'derivative_upper_units':(bound*SCALE).__ceil__()})
result={'status':'PASS_ENLARGED_PIVOT_NO_REENTRY','interval':['0','0.01'],'scale':SCALE,'records':rows,'maximum_derivative_upper_units':max(r['derivative_upper_units']for r in rows)}
encoded=json.dumps(result,indent=2)+'\n'
if '--emit' in sys.argv:(HERE/'DERIVATIVE-RESULT.json').write_text(encoded)
else:iv.need((HERE/'DERIVATIVE-RESULT.json').read_text()==encoded,'exact independent derivative receipt')
print({k:v for k,v in result.items()if k!='records'})
