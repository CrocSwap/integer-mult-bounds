from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
import json,gzip,hashlib
import argparse
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);args=ap.parse_args()
HERE=Path(__file__).resolve().parent;ROOT=args.output.resolve();assert not ROOT.exists();ROOT.mkdir(parents=True)
src=HERE.parent/'data/far783.json.gz';c=json.loads(gzip.decompress(src.read_bytes()));choice=json.loads((HERE/'SOURCE-DUAL-CANDIDATES.json').read_text())['candidates'][0]
x,y=choice['x'],choice['y'];q=Q(choice['q_num'],choice['q_den']);n=2*c['v']+c['R'];phases=[];reads=[0]*n;groups={}
for phase,name in enumerate(('A','B')):
 es=[]
 for gi,g in enumerate(c[name]):
  for term in g[3]:
   r,a,b=term;t,s=(r,g[2]) if g[0]=='out' else (g[2],r);f=g[1];tok=(t,reads[t],f,phase);ei=len(es);es.append((t,s,Q(a,b),f))
   if s in (x,y):
    z=groups.setdefault(tok,dict(value=Q(0),last=ei,phase=phase,frame=f,target=t));z['value']+=Q(a,b)*(1 if s==x else q);z['last']=ei
   reads[s]+=1
 phases.append(es)
new=[]
for phase,es in enumerate(phases):
 at=defaultdict(list)
 for z in groups.values():
  if z['phase']==phase and z['value']:at[z['last']].append((z['target'],x,z['value'],z['frame']))
 z=[]
 for ei,e in enumerate(es):
  if e[1]!=x:z.append(e)
  z.extend(at[ei])
 new.append(z)

def replay(gs,wrap=False,omit_setup=False,omit_restore=False):
 rows=[{i:Q(1)} for i in range(n)]
 def axpy(t,s,q):
  for i,v in list(rows[s].items()):
   z=rows[t].get(i,Q(0))+q*v
   if z:rows[t][i]=z
   else:rows[t].pop(i,None)
 if wrap and not omit_setup:axpy(y,x,-q)
 for t,s,a,f in gs[0]:axpy(t,s,a)
 totals=[dict(rows[r])for k,r,f in c['ret']]
 for target,es in enumerate(c['scat']['table']):
  for k,a,b in es:
   for i,v in totals[k].items():
    z=rows[c['v']+target].get(i,Q(0))+Q(a,b)*v
    if z:rows[c['v']+target][i]=z
    else:rows[c['v']+target].pop(i,None)
 for t,s,a,f in gs[1]:axpy(t,s,a)
 if wrap and not omit_restore:axpy(y,x,q)
 return rows,totals
old=replay(phases);actual=replay(new,True);assert actual==old
assert replay(new,False)!=old
assert replay(new,True,omit_setup=True)!=old
assert replay(new,True,omit_restore=True)!=old
primitive_cost=lambda es:sum(abs(a.numerator)for ph in es for t,s,a,f in ph)
assert primitive_cost(phases)-primitive_cost(new)-2==choice['net_primitive_gain_after_two_wrappers']
result=dict(status='PASS_EXACT_SOURCE_DUAL_ALL_LIVE_COLUMNS_AND_RETAINED_TOTALS',input_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),candidate=choice,all_live_columns=n,retained_totals=len(c['ret']),net_unit_numerator_primitive_gain=primitive_cost(phases)-primitive_cost(new)-2,source_setup=dict(target=y,source=x,coefficient=str(-q)),source_restore=dict(target=y,source=x,coefficient=str(q)),negative_controls_rejected=['omit_source_wrappers','omit_setup','omit_restore'],scope='Universal source-dual algebra on arbitrary initial source/helper/target values; same read-epoch grouping proof. Not a physical gcert admission: source wrappers need common-frame lifts, changed source cleanup/K and complete paid ledger; no kappa improvement claimed from primitive savings.')
(ROOT/'SOURCE-DUAL-EXACT-v2.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'SOURCE-DUAL-SCALAR-RECIPE-v2.json').write_text(json.dumps(dict(choice=choice,setup=[y,x,str(-q)],A=[[t,s,str(a),f]for t,s,a,f in new[0]],B=[[t,s,str(a),f]for t,s,a,f in new[1]],restore=[y,x,str(q)]),indent=2)+'\n')
print(result['status'],choice)
