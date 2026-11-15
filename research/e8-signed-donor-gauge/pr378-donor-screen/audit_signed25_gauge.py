from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,hashlib,sys,copy
P=Path('pr378-donor-screen');c=json.load(gzip.open(P/'signed25-donor-candidate.json.gz'));source=json.load(gzip.open('pr378-complex-screen/package/data/gcert1-e8-r783-far.json.gz'));raw=gzip.decompress((P/'signed25-gauge-template.json.gz').read_bytes());ir=json.loads(raw);report=json.load(open(P/'signed25-gauge-emission.json'));assert hashlib.sha256(raw).hexdigest()==report['template_sha256'];bank=json.load(gzip.open(P/'best-bank-owners.json.gz'));lookup={(a['replica'],a['helper']):a for a in bank};ext=dict(c['ext']);v=c['v'];n=2*v+c['R']
# Independently read actual emitted local state walks/scalar operands.
def check_local(events,ori):
 cur=c['start'][:];hist=Counter();entry={};exit=set();scalar=[];phases=[]
 for ev in events:
  if ev[0]=='phase':phases.append(ev[1]);continue
  if ev[0]=='climb':
   _,ph,r,a,b,d=ev;assert cur[r]==a and d==len(c['frames'][b])-len(c['frames'][a])>0
   for x in c['frames'][a]:
    for y in c['frames'][b]:
     if x>>(y.bit_length()-1)&1:x^=y
    assert x==0
   cur[r]=b;hist[d]+=1
  elif ev[0]=='center':hist[ev[-1]]+=1
  elif ev[0]=='scalar':
   _,ph,e,f=ev;scalar.append((ph,e))
   if ph=='main':
    for k,r in [e[1]]+([e[2]] if e[0] in ('copy','add') else []):
     if k=='L':assert cur[r]==f
  elif ev[0]=='adapter':
   if ev[1]=='initial_chart_to_canonical':
    r,f,chart=ev[2:];entry[r]=chart
    if r in ext:assert f==ext[r] and chart==['Cq',c['frames'][f][0]]
    else:assert chart==['retained',r]
   if ev[1]=='inverse_residual_phase':exit.add(ev[2]);assert ev[3]['rank']==0
  else:raise AssertionError(ev[0])
 assert len(entry)==n and exit==set(ext) and cur==c['final']
 assert phases==['old_response','entrance_adapters','A','centers','B','final','exit_adapters','cleanup','bank_residual_adapters','done']
 return hist

def audit(obj):
 H=Counter();locals={o:check_local(e,o) for o,e in obj['local_programs'].items()};pairs={e['stage']:e for e in obj['recipe'] if e['kind']=='local'};seen=set()
 for call in obj['calls']:
  s,r=call['stage'],call['replica'];assert (s,r) not in seen;seen.add((s,r));assert call['orientation']==('backward' if pairs[s]['reverse'] else 'forward')
  for helper in range(2*v,n):
   b=lookup[r,helper];assert call['owners'][helper]==[7680+s*782+b['bank'],['orthogonal_inverse_route',r,helper]]
  assert len({json.dumps(owner) for owner in call['owners']})==n
  H.update(locals[call['orientation']])
 for x in obj['idle_children']:H[x['rank']]+=x['replicas']
 for pad in obj['bank_padding']:assert pad['rank']==len(pad['axes'])>0;H[pad['rank']]+=1
 assert dict(H)=={int(r):q for r,q in report['paid_profile'].items()}
 assert obj['cover_final_correction']['families']==[0,obj['live']] and obj['live']*obj['m']-sum(r*q for r,q in H.items())==2496
 return H
H=audit(ir);controls=[]
for name,mut in [('zero_gauge_entrance',lambda x:next(e for e in x['local_programs']['forward'] if e[0]=='adapter' and e[1]=='initial_chart_to_canonical' and e[2] in ext).__setitem__(4,['retained',850])),('omit_residual_adapter',lambda x:x['local_programs']['forward'].pop(next(i for i,e in enumerate(x['local_programs']['forward']) if e[0]=='adapter' and e[1]=='inverse_residual_phase'))),('alias_owner',lambda x:x['calls'][0]['owners'].__setitem__(241,x['calls'][0]['owners'][240])),('omit_padding',lambda x:x['bank_padding'].pop()),('omit_final_cover_family',lambda x:x['cover_final_correction']['families'].__setitem__(1,x['live']-1))]:
 bad=copy.deepcopy(ir);mut(bad)
 try:audit(bad)
 except AssertionError:controls.append(name)
 else:raise AssertionError('accepted '+name)
# Changed actual prefix/donor Clifford edges only. Source receipt reused
# only for exact frame-basis pairs that were already checked there.
sys.path.insert(0,'pr378-complex-screen/compressed/work/odd-stages');import clifford_exact as X
oldrecipes=json.load(open('pr378-complex-screen/compressed/work/complex-nine-native/CLIFFORD-RECIPES.json'))['children'];checkedpairs={(tuple(source['frames'][a['old']]),tuple(source['frames'][a['new']])) for a in oldrecipes}
newpairs=set()
for ori,events in ir['local_programs'].items():
 for e in events:
  if e[0]=='climb':a,b=e[3:5]
  elif e[0]=='center':a,b=e[2:4]
  else:continue
  pair=tuple(c['frames'][a]),tuple(c['frames'][b])
  if pair not in checkedpairs:newpairs.add(pair)
newpairs |= {(b,a) for a,b in newpairs};recipes=[]
for a,b in sorted(newpairs):
 op=X.canonical_frame(c['h'],a).adjoint().then(X.canonical_frame(c['h'],b));rec,compiled=X.lower_child(op);assert rec['rank']==abs(len(a)-len(b));assert compiled.tab==op.tab and compiled.zero_state()==op.zero_state();recipes.append(dict(old_basis=a,new_basis=b,**rec))
(P/'signed25-gauge-new-phase-recipes.json').write_text(json.dumps(recipes))
result=dict(status='PASS_SCOPED_EMITTED_TEMPLATE_READBACK_AND_NEW_LOCAL_PHASES',template_sha256=hashlib.sha256(raw).hexdigest(),new_and_reflected_phase_pairs=len(recipes),structural_mutants_rejected=controls,reused_exact_old_phase_pairs=len(checkedpairs),paid_profile=dict(sorted(H.items())),scope='Independent local state/gauge adapter and global owner/profile readback plus newly used Clifford edges. Retains prior bank-route geometry and data phases. Does not yet independently verify complete ambient gauge/cover splice, whole execution schedule, or provide package/assembly admission. No new kappa.')
(P/'signed25-gauge-readback.json').write_text(json.dumps(result,indent=2));print(result)
