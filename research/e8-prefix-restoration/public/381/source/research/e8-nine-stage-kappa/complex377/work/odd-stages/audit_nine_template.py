"""Read back the emitted IR, verify independent scalar composition and owners,
derive its histogram, reject structural mutations, and price that actual IR.
"""
import json,gzip,hashlib,copy,importlib.util,math
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
OUT=Path('work/complex-nine-native');raw=gzip.decompress((OUT/'GLOBAL-TEMPLATE.json.gz').read_bytes());ir=json.loads(raw);report=json.loads((OUT/'GLOBAL-REVIEW.json').read_text());assert hashlib.sha256(raw).hexdigest()==report['template_sha256']
c=json.load(gzip.open('work/pr361/complex/gcert1-e8-r783.json.gz'))
def scalar(recipe,omit=None):
 A=[[int(i==j) for j in range(8)] for i in range(8)]
 def add(t,s,q):A[t]=[x+q*y for x,y in zip(A[t],A[s])]
 for z,e in enumerate(recipe):
  if z==omit:continue
  kind=e['kind']
  if kind=='local':
   x=2*e['pair'];y=x+1;add(x,y,-1) if e['reverse'] else add(y,x,1)
  elif kind=='bridge':
   i,j,q=e['dst'],e['src'],e['coefficient'];add(2*i,2*j,q);add(2*j+1,2*i+1,-q)
  elif kind=='terminal':
   B=copy.deepcopy(A)
   for j in range(4):A[2*j]=B[2*j+1];A[2*j+1]=[-x for x in B[2*j]]
  else:raise AssertionError(kind)
 return A
I=[[int(i==j) for j in range(8)] for i in range(8)]
def audit(t):
 assert scalar(t['recipe'])==I
 assert [(x['stage'],x['replica']) for x in t['calls']]==[(s,r) for s in range(9) for r in range(8)]
 levels=[-1]*4;stages=[]
 for event in t['execution_schedule']:
  if event['kind']=='local_cover_sweep':
   s=event['stage'];pair=next(e['pair'] for e in t['recipe'] if e['kind']=='local' and e['stage']==s);assert levels[pair]==s-1;levels[pair]=s;stages.append(s)
  elif event['kind']=='idle_cover_sweep':
   p=event['pair'];assert levels[p]==event['from_level']<=event['to_level'];levels[p]=event['to_level']
  elif event['kind']=='bridge':assert levels[event['src']]==levels[event['dst']]
  elif event['kind']=='terminal':assert levels==[8]*4
 assert stages==list(range(9)) and t['execution_schedule'][-1]['kind']=='translate_every_live_family'
 assert t['cover_final_correction']==dict(kind='translate_every_live_family',formula='delta_i=(weight(row_i(g))-1)/2 mod 2',families=[0,14727],must_follow_bank_padding_and_data_signed_exchange=True,charged_calls_per_cover=14727)
 H=Counter();stagepairs={e['stage']:e for e in t['recipe'] if e['kind']=='local'};seen=set()
 for call in t['calls']:
  s,r,p=call['stage'],call['replica'],call['pair'];assert p==stagepairs[s]['pair'];assert call['orientation']==('backward' if stagepairs[s]['reverse'] else 'forward');assert (s,r) not in seen;seen.add((s,r))
  own=call['owners'];assert len(own)==1023 and len({(f,tuple(route)) for f,route in own})==1023
  for z,(fam,route) in enumerate(own):
   if z<240:assert fam==r*960+(2*p+z//120)*120+z%120 and route==[1,s,z%120]
   else:
    k=r*783+z-240;assert fam==7680+s*783+k//8 and route==[2,k%8]
  for event in t['local_programs'][call['orientation']]:
   if event[0]=='climb':H[event[5]]+=1
   elif event[0]=='center':H[event[4]]+=1
 assert seen=={(s,r) for s in range(9) for r in range(8)}
 for child in t['idle_children']:H[child['rank']]+=child['replicas']
 padding=t['bank_padding'];assert padding==dict(families=list(range(7680,14727)),axis=72,child_rank=1);H[1]+=len(padding['families'])
 assert t['live']==14727 and t['physical']==15520 and 73*t['live']-sum(r*n for r,n in H.items())==2496
 return H
H=audit(ir);assert dict(H)=={int(r):n for r,n in report['profile'].items()}
controls=[]
for name,mut in [
 ('missing_cover_phase',lambda t:t.pop('cover_final_correction')),
 ('aliased_helper_route',lambda t:t['calls'][0]['owners'][241].__setitem__(1,[2,0])),
 ('missing_padding',lambda t:t['bank_padding']['families'].pop()),
 ('wrong_reverse_local',lambda t:t['calls'][8].__setitem__('orientation','forward')),
 ('omitted_terminal_exchange',lambda t:t['recipe'].pop())]:
 bad=copy.deepcopy(ir);mut(bad)
 try:audit(bad)
 except (AssertionError,KeyError):controls.append(name)
 else:raise AssertionError('accepted mutation '+name)
for i,e in enumerate(ir['recipe']):
 if e['kind']=='bridge':assert scalar(ir['recipe'],omit=i)!=I
def engine(name):
 s=importlib.util.spec_from_file_location('cx9audit_'+name,Path('work/pr361/code/engines')/(name+'.py'));e=importlib.util.module_from_spec(s);s.loader.exec_module(e);return e
M=engine('moment');B=engine('base_two_moment');r=M.certify(H,73,14727,True);b=Q(int(Q(r['lower'])*10**18),10**18);grid=Q(1,10**18);fb=32*73**2*sum(H.values())
lo,up=M.moment(H,73,14727,b,True);nl,nu=M.moment(H,73,14727,b+grid,True);assert up<1<nl
_,u=B.moment(73,14727,list(H.items()),b);_,bu=B.moment(73,14727,[(1,fb)],b);l,_=B.moment(73,14727,list(H.items()),b+grid);bl,_=B.moment(73,14727,[(1,fb)],b+grid);assert u+Q(1,10**16)*bu<1<l+Q(1,10**16)*bl
assert b==Q(999240641319551,10**18)
result=dict(status='PASS_INDEPENDENT_EMITTED_TEMPLATE_AUDIT_AND_TWO_MOMENTS',template_sha256=hashlib.sha256(raw).hexdigest(),coarse_complex=str(b),next_grid_rejected=True,all_eight_signed_data_columns=True,bridge_omission_controls=9,structural_controls_rejected=controls,paid_profile=dict(sorted(H.items())),fixed_baseline_kappa='804849251275843/1000000000000000000',final_kappa_improvement_claim=False,scope='Finite complex component with explicit PROOF.txt retaining the analytic interfaces. No Lean rebuild and no improved bit-side or multiplication certificate.')
(OUT/'INDEPENDENT-TEMPLATE-AUDIT.json').write_text(json.dumps(result,indent=2));print(result)
