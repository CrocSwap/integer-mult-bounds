"""Independent dual audit using eigenspace capacities and prior author-independent arithmetic.
Uses arithmetic retained from the reviewer's earlier no-idle verifier, never
the carrier author's code. Relative paths/report handling adapted for this
package; the independent matrix and pricing algorithms are unchanged.
Jerry Chen / @CubeJerry, substantial OpenAI GPT-6 Astra Pro assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import ast,json
import arithmetic as v
from pathlib import Path
H=Path(__file__).resolve().parent
A=H.parent
r=json.loads((H/'EXPECTED-GEOMETRY.json').read_text())
d=json.loads((A/'dual-certificate.json').read_text())
scale=d['scale'];C=Q(d['verification_kappa'])
intervals=[(a,b) for a in range(18) for b in range(a,18)]
capdata={(z['a'],z['b']):z['caps'] for z in r['capacities']}
v.need(len(d['cases'])==81 and {(z['a'],z['b']) for z in d['cases']}==set(capdata),'complete unique eighty-one-case dual domain')
values={}
for node in ast.parse((A/'retained/pricing.py').read_text()).body:
 if isinstance(node,ast.Assign):
  for target in node.targets:
   if isinstance(target,ast.Name) and target.id in ('HELPERS','LOCAL_PAID'):
    values[target.id]=ast.literal_eval(node.value)
v.need(set(values)=={'HELPERS','LOCAL_PAID'},'both source profile tables')
native={k:values['HELPERS'].get(k,0)-values['LOCAL_PAID'].get(k,0) for k in set(values['HELPERS'])|set(values['LOCAL_PAID'])}
v.need(native=={1:-2220,2:-446,3:-485,4:-1,5:-135,6:-4,7:1,8:39,9:359},'independently recounted native profile')
N=v.interval_sum({k:18*x for k,x in native.items()},C)
out=[];failing=[]
for case in d['cases']:
 a,b=case['a'],case['b'];alpha,beta=case['alpha'],case['beta']
 v.need(len(alpha)==171 and len(beta)==18 and all(x<=0 for x in alpha),'dual dimensions and signs')
 masks=[]
 for k in range(18):
  mask={0,*range(1,k+2)} if k<9 else {0,*range(k+1,19)}
  if a<=k<=b:mask=set(range(19))
  masks.append(mask)
 demands=[len(mask)-2 for mask in masks]
 targets={}
 for c in range(20):
  rank=1+8*sum(c in mask for mask in masks);targets[rank]=targets.get(rank,0)+1
 for j,(l,u) in enumerate(intervals):
  lhs=sum(alpha[i] for i,(c,e) in enumerate(intervals) if l<=c<=e<=u)+sum(beta[l:u+1])
  cost=v.power_bounds(8*(u-l+1),C)[0]
  v.need(Q(lhs,scale)<=cost,'independent dual inequality '+str((a,b,l,u)))
 objective=Q(sum(x*y for x,y in zip(alpha,capdata[(a,b)]))+sum(x*y for x,y in zip(beta,demands)),scale)
 target=v.interval_sum(targets,C)
 margin=N[1]+104*(target[1]-3-objective)
 v.need(margin<0,'complete favorable invoice loses '+str((a,b)))
 out.append({'a':a,'b':b,'upper_margin':v.enclosure((margin,margin))})
worst=max(out,key=lambda x:Q(x['upper_margin'][1]))
result={'verdict':'PASS_INDEPENDENT_81_DUAL_COMPLETE_PRICES','verification_kappa':str(C),
        'dual_constraints_checked':81*171,'cases':81,'worst_certified_case':worst,'results':out}
v.need(result==json.loads((H/'EXPECTED-PRICES.json').read_text()),'independent price expected report')
print(json.dumps({k:x for k,x in result.items() if k!='results'},indent=2))
