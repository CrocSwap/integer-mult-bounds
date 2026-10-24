"""New parametric local/global emission with explicit nonzero entrance charts."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,hashlib,sys,os,math
P=Path('pr378-donor-screen');c=json.load(gzip.open(P/'signed25-donor-candidate.json.gz'));old=json.load(gzip.open(P/'best-candidate.json.gz'));ga=json.load(open(P/'signed25-gauge-lift-audit.json'));pa=json.load(open(P/'signed25-donor-screen.json'));bank=json.load(gzip.open(P/'best-bank-owners.json.gz'));geo=json.load(open(P/'best-bank-geometry.json'));root=Path('pr378-complex-screen/candidate-guard').resolve();os.environ['CX_PINS']=str(root/'pins-e8.json');sys.path.insert(0,str(root/'code'));import complex_scalars as S,scatter
v,R,h=c['v'],c['R'],c['h'];n=2*v+R;ext=dict(c['ext']);A0=S.flat(old['A']);B0=S.flat(old['B']);K=list(S.old_positive(A0,B0,old));programs={};bills={};checked={}
def flat(gs):
 for g in gs:
  for r,a,b in g[3]:yield (r,g[2],Q(a,b)) if g[0]=='out' else (g[2],r,Q(a,b))
for ori in ['forward','backward']:
 events=[];schedule=[];cur=c['start'][:];H=Counter();centers=set();edges=set();inc=0
 def scalar(phase,e,frame):
  nonlocal_dummy=None
  op=e[0];regs=[e[1]]+([e[2]] if op in ('add','copy') else [])
  for kind,r in regs:
   if kind=='L':
    assert 0<=r<n
    if phase=='main':assert cur[r]==frame
    elif phase=='cleanup':assert cur[r]==1 and (r<v or r>=2*v)
    else:assert phase=='old_response' and r>=v and frame=='old0'
  if op=='clear' and e[1][0]=='C':centers.discard(e[1][1])
  elif e[1][0]=='C':centers.add(e[1][1])
  events.append(['scalar',phase,e,frame]);schedule.append((phase,e))
 def climb(r,f,phase):
  before=cur[r]
  if before==f:return
  assert not centers
  fromframe,toframe=c['frames'][before],c['frames'][f]
  assert len(fromframe)<len(toframe)
  def reduce(x):
   for b in toframe:
    if x>>(b.bit_length()-1)&1:x^=b
   return x
  assert all(reduce(x)==0 for x in fromframe)
  d=len(toframe)-len(fromframe);H[d]+=1;edges.add((before,f));events.append(['climb',phase,r,before,f,d]);cur[r]=f
 events.append(['phase','old_response'])
 for e in S.old_word(ori,K):scalar('old_response',e,'old0')
 events.append(['phase','entrance_adapters'])
 for r,f in enumerate(c['start']):events.append(['adapter','initial_chart_to_canonical',r,f,('Cq',c['frames'][f][0]) if r in ext else ('retained',r)])
 for phase in ['A','centers','B']:
  events.append(['phase',phase])
  if phase=='centers':
   table=scatter.table(c);ranks=scatter.centre_ranks(c)
   for k,r,f in c['ret']:
    srcframe=f if ori=='forward' else 0;dstframe=0 if ori=='forward' else f
    scalar('main',S.clear(S.center(k)),srcframe)
    if ori=='forward':scalar('main',S.add(S.center(k),S.live(r),Q(1)),f)
    else:
     for t in range(v):
      if k in table[t]:scalar('main',S.add(S.center(k),S.live(v+t),table[t][k]),0)
    assert centers=={k};events.append(['center',k,srcframe,dstframe,ranks[k]]);H[ranks[k]]+=1;schedule.append(('main',('recursive_center',k,ranks[k])))
    if ori=='forward':
     for t in range(v):
      if k in table[t]:scalar('main',S.add(S.live(v+t),S.center(k),table[t][k]),0)
    else:scalar('main',S.add(S.live(r),S.center(k),Q(-1)),f)
    scalar('main',S.clear(S.center(k)),dstframe)
   continue
  for g in c[phase]:
   for r in [g[2]]+[a[0] for a in g[3]]+(g[4] if g[0]=='out' else []):climb(r,g[1],phase)
   for t,s,q in flat([g]):
    scalar('main',S.add(S.live(t),S.live(s),q) if ori=='forward' else S.add(S.live(s),S.live(t),-q),g[1]);inc+=2
 events.append(['phase','final'])
 for r,f in enumerate(c['final']):climb(r,f,'final')
 assert cur==c['final']
 events.append(['phase','exit_adapters'])
 for r,f in enumerate(c['final']):events.append(['adapter','canonical_to_retained',r,f])
 events.append(['phase','cleanup'])
 for e in S.cleanup(ori,A0+B0):scalar('cleanup',e,'old1')
 events.append(['phase','bank_residual_adapters'])
 for r in ext:events.append(['adapter','inverse_residual_phase',r,geo['residual_phase_adapter']])
 events.append(['phase','done']);S.lifecycle(schedule,c);bills[ori]=S.bill(schedule)
 assert bills[ori]==ga['bills'][ori]
 local=Counter()
 for block in c['blocks'].values():local.update({int(r):n for r,n in block.items()})
 assert H==local
 programs[ori]=events;checked[ori]=dict(events=len(events),paid_histogram=dict(H),common_frame_incidences=inc,nested_edges=len(edges),centers=len(c['ret']),clean_temporary_lifetimes=True,entrance_adapters=len(ext),residual_phase_adapters=len(ext),scalar_word_sha256=bills[ori]['schedule_sha256'])
 print('local',ori,checked[ori],flush=True)
# Reuse only unchanged data/idle chronology, binding the actual old template.
base=Path('pr378-complex-screen/compressed/work/complex-nine-native');priorraw=gzip.decompress((base/'GLOBAL-TEMPLATE.json.gz').read_bytes());prior=json.loads(priorraw);sourcecert=json.load(gzip.open('pr378-complex-screen/package/data/gcert1-e8-r783-far.json.gz'));assert c['ports']==sourcecert['ports'] and c['start'][:2*v]==sourcecert['start'][:2*v] and c['final']==sourcecert['final']
m=prior['m'];T=1+max(x['replica'] for x in bank);banks=1+max(x['bank'] for x in bank);stages=sorted({call['stage'] for call in prior['calls']});datafamilies=min(f for f,r in prior['calls'][0]['owners'][2*v:]);live=datafamilies+len(stages)*banks;physical=live+R+h+1;assert live==pa['live'];lookup={(x['replica'],x['helper']):x for x in bank};calls=[];H=Counter();primitives=0
for call in prior['calls']:
 call=json.loads(json.dumps(call));s,r=call['stage'],call['replica'];owners=call['owners'][:2*v]
 for helper in range(2*v,n):
  b=lookup[r,helper];owners.append([datafamilies+s*banks+b['bank'],['orthogonal_inverse_route',r,helper]])
 assert len(owners)==n and len({json.dumps(o) for o in owners})==n
 call['owners']=owners;call['local_program_sha256']=hashlib.sha256(json.dumps(programs[call['orientation']],separators=(',',':')).encode()).hexdigest();calls.append(call)
 H.update({int(k):q for k,q in checked[call['orientation']]['paid_histogram'].items()});primitives+=bills[call['orientation']]['totals']['real_component_primitive_steps']
for ch in prior['idle_children']:H[ch['rank']]+=ch['replicas']
padding=[]
for s in stages:
 for b in range(banks):
  used={x for owner in bank if owner['bank']==b for x in owner['residual_axes']};missing=sorted(set(range(m))-used)
  if missing:padding.append(dict(family=datafamilies+s*banks+b,axes=missing,rank=len(missing)));H[len(missing)]+=1
assert dict(H)=={int(k):q for k,q in pa['profile'].items()};mass=sum(k*q for k,q in H.items());assert m*live-mass==2496
# Finite invoice counted from new scalar emission. Same published explicit
# quadratic Clifford compiler and conservative multiplier, newly counted items.
compiler=64*(m+1)**3;macros=max(bills[o]['totals']['scalar_macros'] for o in bills);lc=sum(checked['forward']['paid_histogram'].values());adapters=16*(macros+lc+n+h)+64*m+4*len(ext);localbound=max(bills[o]['totals']['real_component_primitive_steps'] for o in bills)+adapters*compiler
bridges=sum(e['kind']=='bridge' for e in prior['recipe']);pairs=len({e['pair'] for e in prior['recipe'] if e['kind']=='local'});bridge_adds=2*v*T*bridges;terminal_shifts=pairs*v*T;terminal_moves=datafamilies
nonlocal_items=6*v*T*len(stages)+2*len(stages)*T*R+len(prior['idle_children'])*T+len(padding)+bridge_adds+terminal_shifts+terminal_moves+live+physical+2*len(calls)*len(ext)
outside=8*nonlocal_items+64*m;pervertex=primitives+bridge_adds+terminal_shifts+terminal_moves+live+(len(calls)*adapters+outside)*compiler+64*physical
rr=m//2;group=2**(rr*rr)*math.prod(2**(2*i)-1 for i in range(1,rr+1));stock=group*physical;smass=group*mass;logical=group*pervertex+64;router=compiler*(logical+1)*(stock+1)**2;G=1<<30000;E=1<<100000;B=smass+E;literal=2*G*stock**2+8*smass+4*stock+4+32*m
assert localbound<1<<48 and logical<1<<6050 and router<G and literal<E and 32*m*B*B<1<<210000 and m*m>2*max(H)**2
row=2*stock.bit_length()+9909+252;assert row<20161
invoice=dict(local_bound=localbound,real_primitives_all_calls=primitives,adapter_groups=adapters,outside_groups=outside,pervertex=pervertex,physical=physical,group_bits=group.bit_length(),physical_stock_bits=stock.bit_length(),logical_bits=logical.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),row=row,retained_row=20161)
ir=dict(version='prefix-donor-gauge-candidate-v1',candidate_sha256=pa['candidate_sha256'],m=m,live=live,physical=physical,local_programs=programs,calls=calls,helper_route_source='best-bank-owners.json.gz; complete columns extended by increasing unused coordinate axes; owner right factor is TRANSPOSE, not assumed symmetric',bank_geometry_sha256=hashlib.sha256((P/'best-bank-geometry.json').read_bytes()).hexdigest(),recipe=prior['recipe'],idle_children=prior['idle_children'],bank_padding=padding,cover_final_correction=dict(kind='translate_every_live_family',families=[0,live],formula=prior['cover_final_correction']['formula']),scope='Candidate emitted symbolic cover template. Needs independent readback and ambient gauge/route phase integration audit before supplier admission.')
raw=json.dumps(ir,sort_keys=True,separators=(',',':')).encode();(P/'signed25-gauge-template.json.gz').write_bytes(gzip.compress(raw,mtime=0));result=dict(status='CANDIDATE_EMITTED_LOCAL_FRAME_WORDS_GLOBAL_OWNERS_AND_FINITE_INVOICE',template_sha256=hashlib.sha256(raw).hexdigest(),local_checks=checked,global_calls=len(calls),live=live,physical=physical,paid_profile=dict(sorted(H.items())),rankmass=mass,deficit=2496,padding_calls=len(padding),invoice=invoice,reused_prior_template_sha256=hashlib.sha256(priorraw).hexdigest(),scope=ir['scope']);(P/'signed25-gauge-emission.json').write_text(json.dumps(result,indent=2));print(result)
