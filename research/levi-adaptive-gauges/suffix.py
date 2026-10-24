"""Exact suffix response to additive logical defects. Apache-2.0.
Dugongue with substantial OpenAI assistance; no new kappa.
"""
from fractions import Fraction as Q
from collections import defaultdict

def need(ok,msg):
 if not ok:raise ValueError(msg)
def add(a,b,q):
 for key,value in tuple(b.items()):
  value=a.get(key,Q(0))+q*value
  if value:a[key]=value
  else:a.pop(key,None)
def warp_right(row,operator,backward):
 symbol=(1 if operator>0 else -1)*(abs(operator)+(10**6 if backward else 0))
 out={}
 for (output,word),q in row.items():
  moved=word[:-1] if word and word[-1]==-symbol else word+(symbol,)
  key=(output,moved);out[key]=out.get(key,Q(0))+q
 return {k:q for k,q in out.items() if q}
def suffix(program,backward=False,roles=None,samples=()):
 roles=roles if roles is not None else [('L',i) for i in range(632)]+[('C',0)]
 saved={};columns={r:{(r,()):Q(1)} for r in roles};bounds=defaultdict(lambda:defaultdict(Q));counts=defaultdict(int);max_column=Q(0)
 for index in range(len(program)-1,-1,-1):
  e=program[index];kind=e[0];target=None;category=None
  if kind=='scalar':target=tuple(e[1][1]);category=e[1][0]
  elif kind=='warp':target=tuple(e[1]);category='warp'
  elif kind=='climb':target=('L',e[2]);category='rank-'+str(e[5])
  elif kind=='center':target=('C',e[1]);category='rank-'+str(e[4])
  if target is not None:
   need(target in columns,'Known target role')
   if index in samples:saved[index]=dict(columns[target])
   counts[category]+=1
   for (output,word),q in columns[target].items():bounds[category][output]+=abs(q)
   max_column=max(max_column,sum(map(abs,columns[target].values()),Q(0)))
  if kind=='scalar':
   op=e[1]
   if op[0]=='add':add(columns[tuple(op[2])],columns[target],Q(op[3],op[4]))
   elif op[0]=='scale':columns[target]={key:Q(op[2],op[3])*q for key,q in columns[target].items()}
   elif op[0]=='clear':columns[target]={}
   elif op[0]=='copy':
    need(target!=tuple(op[2]),'Distinct COPY roles');add(columns[tuple(op[2])],columns[target],Q(1));columns[target]={}
   else:raise ValueError('Scalar opcode')
  elif kind=='warp':columns[target]=warp_right(columns[target],e[2],backward)
  else:need(kind in ('phase','adapter','residual_adapter','climb','center'),'Known native event')
 return columns,bounds,counts,max_column,saved

def summarize(program,backward=False):
 columns,bounds,counts,mx,samples=suffix(program,backward)
 roles=[('L',i) for i in range(632)];categories=sorted(counts)
 rows=[{'role':list(r),'weights':{cat:str(bounds[cat][r]) for cat in categories}} for r in roles]
 joint=max(sum((bounds[cat][r] for cat in ('add','scale')),Q(0)) for r in roles)
 bits=0
 while Q(2)**bits<joint:bits+=1
 return {'categories':categories,'events_per_class':dict(sorted(counts.items())),'persistent_output_rows':rows,'class_maxima':{cat:str(max(bounds[cat][r] for r in roles)) for cat in categories},'uniform_add_scale_bound':str(joint),'sufficient_extra_logical_defect_bits':bits,'max_single_injection_total_output_l1':str(mx)}

def bound_from_rows(receipt,defects):
 need(set(defects)==set(receipt['categories']),'Provide an explicit nonnegative defect for EVERY event class; unknown is not zero')
 defects={k:Q(v) for k,v in defects.items()};need(all(v>=0 for v in defects.values()),'Nonnegative defects')
 return max(sum((Q(row['weights'][cat])*defects[cat] for cat in receipt['categories']),Q(0)) for row in receipt['persistent_output_rows'])
