"""Independent exact price-half review of90 enlarged-mask site duals."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json,hashlib,sys
HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent.parent/'accounting/verify.py'
if hashlib.sha256(AUDIT.read_bytes()).hexdigest()!='116ed12d5aaeef8a5fb084c95db50febb50a9df04825a3506eab633e4abffa3f':raise ValueError('Reviewed interval/accounting source changed')
spec=importlib.util.spec_from_file_location('iv',AUDIT);iv=importlib.util.module_from_spec(spec);spec.loader.exec_module(iv)
SCALE=10**18;K=Q('.00337180');native_t,native_p=iv.source_census()
DUALS=HERE.parent/'DUALS.json'
certificate=json.loads(DUALS.read_text())
iv.need(certificate['scale']==SCALE and certificate['kappa']=='0.00337180' and certificate['pivot']==8,'fixed dual parameters')
records=certificate['cases']
iv.need(len(records)==90 and{(r['kl'],r['kr'])for r in records}=={(a,b)for a in range(9)for b in range(10)},'exact90shape coverage')
cost={m:(iv.power_bounds(8*m,K)[0]*SCALE).__floor__()for m in range(1,19)}
def masks(a,b):
 return [{0,*range(1,j+2),*range(9,9+b)}for j in range(8)]+[set(range(18))]+[{0,*range(j,18),*range(9-a,9)}for j in range(9,18)]
results=[]
for record in records:
 a,b=record['kl'],record['kr'];ms=masks(a,b);d=[len(s)-2 for s in ms]
 T=Counter(8*sum(i in s for s in ms)+1 for i in range(18))
 formula=Counter({145:1})
 formula.update(8*(9-i+9*(i>=8-a))+1 for i in range(8))
 formula.update(8*(j-7+8*(j<=8+b))+1 for j in range(9,18))
 iv.need(T==formula,'independent closed-form target histogram')
 iv.need(len(ms)==18 and sum(T.values())==18 and sum(d)==80+9*a+8*b,'site/target census')
 iv.need(sum(r*n for r,n in T.items())-1-8*sum(d)==305,'exact root mass305')
 weights=record['weights'];iv.need(len(weights)==18 and all(type(v)is int and v>=0 for v in weights),'18nonnegative exact rational dual weights')
 objective=sum(x*y for x,y in zip(d,weights));iv.need(objective==record['paid_lower_units'],'dual objective arithmetic')
 signed=Counter({r:18*n for r,n in native_t.items()});signed.subtract({r:18*n for r,n in native_p.items()})
 signed.update({r:104*n for r,n in T.items()});signed[1]-=104
 upper=iv.moment(signed,K)[1]-104*Q(objective,SCALE)
 ceil=(upper*SCALE).__ceil__();iv.need(ceil==record['margin_upper_units']<0,'certified rounded complete negative margin')
 # Geometry reviewer independently excludes every price-violating support.
 sums=[0]*(1<<18);violations=0;by_size=Counter()
 for bits in range(1,1<<18):
  last=bits&-bits;sums[bits]=sums[bits^last]+weights[last.bit_length()-1]
  size=bits.bit_count()
  if sums[bits]>cost[size]:violations+=1;by_size[size]+=1
 results.append({'kl':a,'kr':b,'targets':dict(sorted(T.items())),'demands':d,'paid_lower_units':objective,'margin_upper_units':ceil,'violating_supports':violations,'violating_support_sizes':dict(sorted(by_size.items()))})
result={'status':'PASS_ENLARGEMENT_PRICE_HALF','dual_sha256':hashlib.sha256(DUALS.read_bytes()).hexdigest(),'benchmark':str(K),'scale':SCALE,'records':results,'cost_floor_units':cost,'worst_margin_upper_units':max(r['margin_upper_units']for r in results),'total_price_violations':sum(r['violating_supports']for r in results),'limits':'Price inequalities alone do not certify dual feasibility. Requires geometry proof that every price-violating support has zero carrier capacity; no attained idle cover or new kappa.'}
encoded=json.dumps(result,indent=2)+'\n'
if '--emit' in sys.argv:(HERE/'PRICE-RESULT.json').write_text(encoded)
else:iv.need((HERE/'PRICE-RESULT.json').read_text()==encoded,'exact independent price receipt')
print({k:v for k,v in result.items()if k not in('records','cost_floor_units')})
