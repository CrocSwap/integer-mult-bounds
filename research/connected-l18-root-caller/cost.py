"""Actual emitted census and conditional native gates, never a kappa certificate."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,getcontext
from collections import Counter
import json,math
if not __debug__:raise RuntimeError('Cost check requires assertions')
HERE=Path(__file__).resolve().parent;getcontext().prec=60

def value(h,k):return sum(D(c)*D(r)**(1-k)for r,c in h.items())
def census(g):
 C=json.loads((HERE/f'caller_L{g}.json').read_text());counts=Counter(e[0]for e in C['events']);n=C['roles'];T=Counter(1+8*m.bit_count()for m in C['masks']);P={8:counts['IDLE_ONE'],1:counts['QUERY']};sc=[F(e[-1])for e in C['events']if e[0]in['ADD','SCALE']]
 assert counts['HOST']==g and counts['QUERY']==3 and counts['LAMBDA']==2*g+6+n
 assert all(m>0 for m in C['masks'])
 if g==18:assert counts==Counter({'ADD':1041,'SCALE':189,'SWAP':858,'LAMBDA':80,'QUERY':3,'HOST':18,'IDLE_ONE':181})
 gates={}
 for label,k in [('selected_complex',D('.003125804')),('pending_complex_6936',D('.00362701882')),('ordinary_BIT_6726',D('.00376669'))]:
  gate=(value(T,k)-value(P,k))/g
  baseline={8:P[8]+2*g,1:3+2*g}
  gates[label]={'comparison_kappa':str(k),'max_native_signed_cost_per_port_per_call_before_ordinary_outer':str(gate),'allowance_above_two_H8':str(gate-2*D(8)**(1-k)),'direct_baseline_signed_moment':str(value(T,k)-value(baseline,k))}
  assert value(T,k)-value(baseline,k)<0
 source=json.loads((HERE/'inputs/base_invoice.json').read_text());fp={int(r):c for r,c in source['local_paid'].items()};ft={int(r):c for r,c in source['helpers'].items()}
 if g==18:
  for label,z in gates.items():
   k=D(z['comparison_kappa']);fprice=(value(fp,k)-value(ft,k))/104+1
   z['retained_F_plus_H1_cost_per_port']=str(fprice)
   z['retained_F_plus_H1_excess']=str(fprice-D(z['max_native_signed_cost_per_port_per_call_before_ordinary_outer']))
   assert fprice>D(z['max_native_signed_cost_per_port_per_call_before_ordinary_outer'])
 return {'roles':n,'stages':g,'events':len(C['events']),'event_counts':dict(counts),'ordinary_events':sum(counts[x]for x in['ADD','SCALE','SWAP','LAMBDA']),'target_histogram':dict(sorted(T.items())),'target_rank_mass':sum(r*c for r,c in T.items()),'paid_outside_native':P,'paid_outside_native_mass':sum(r*c for r,c in P.items()),'ordinary_scalar_denominator_lcm':str(math.lcm(*(x.denominator for x in sc))),'max_abs_ordinary_scalar':str(max(map(abs,sc))),'native_gates':gates}
if __name__=='__main__':
 out={str(g):census(g)for g in[3,9,18]};out=json.loads(json.dumps(out))
 p=HERE/'COST.json'
 if p.exists():assert out==json.loads(p.read_text())
 print(json.dumps(out,indent=2));print('PASS_EMITTED_CENSUS')
