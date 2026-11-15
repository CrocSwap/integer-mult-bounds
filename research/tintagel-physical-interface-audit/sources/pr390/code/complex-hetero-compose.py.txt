"""Literal heterogeneous helper endpoints: exact chronology, dirty words and invoice."""
import sys,os,json,gzip,hashlib,math,importlib.util,time
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;PUB=Path(os.environ.get('COMPLEX_PUBLIC',str(HERE/'public')));BASE=PUB/'381/source/research/e8-nine-stage-kappa/complex377';ROOT=BASE/'work/native358/vendor/complex-reserve/upstream/pr352/code/complex'
CP=Path(os.environ.get('COMPLEX_CERT',str(HERE/'structural-local-prefix18.json')));AP=Path(os.environ.get('COMPLEX_SINK_AUDIT',str(HERE/'structural-sink-prefix18-audit.json')));PP=Path(os.environ.get('COMPLEX_PREWHITE',str(HERE/'structural-prewhite-prefix18.json')));OUT=Path(os.environ.get('COMPLEX_OUTPUT',str(HERE/'complex-hetero-admission')));OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sources={str(p):sha(p) for p in [CP,AP,PP,ROOT/'code/complex_splice.py',ROOT/'code/complex_scalars.py',BASE/'work/odd-stages/clifford_exact.py']}
c=json.loads(gzip.decompress(CP.read_bytes())) if CP.suffix=='.gz' else json.loads(CP.read_text());audit=json.loads(AP.read_text());pre=json.loads(PP.read_text());assert pre['status']=='PASS_EXACT_1023_COLUMN_ABSTRACT_FORWARD_HETEROGENEOUS_DIRTY_DECODER'
sinks={a['sink_helper']:a for a in audit['accepted']};assert set(sinks)=={355,403};bycut={a['cut_group']:a for a in audit['accepted']};frames=c['frames'];final=c['final'][:]
for r,a in sinks.items():final[r]=a['frame'];assert len(frames[final[r]])==8
pin=OUT/'pins.json';pin.write_text(json.dumps({'H':9,'V':120,'R':783}));os.environ['CX_PINS']=str(pin);sys.path.insert(0,str(ROOT/'code'));import complex_splice as S,scatter
local_hist=Counter();newedges=set();words={};events={};physical_checks={};primitive_count={};paid={}
def lift(t,s,a,b,ori):return ('add',('L',t),('L',s),a,b) if ori=='forward' else ('add',('L',s),('L',t),-a,b)
def inverse_transpose(e):
 if e[0]=='add':return ('add',e[2],e[1],-e[3],e[4])
 return e
# Elementary coefficients are actually expanded by literal binary doubling,
# signed ADD, repeated HALVE and DIVIDE3; every coefficient stream is cleared.
def lower_scalar(e):
 if e[0] in ['copy','clear']:return [e]
 assert e[0]=='add';t,src,a,b=e[1:];assert t!=src and t[0]!='W' and src[0]!='W'
 W=('W',0);out=[('clear',W)]
 for bit in bin(abs(a))[2:]:
  out.append(('double',W))
  if bit=='1':out.append(('accumulate',W,src,1))
 for prime,tag in [(2,'halve'),(3,'divide3')]:
  while b%prime==0:b//=prime;out.append((tag,W))
 assert b==1
 return out+[('accumulate',t,W,1 if a>0 else -1),('clear',W)]
def primitive_bound(e):return len(lower_scalar(e))
def check_lowered_coefficient(a,b):
 t,src,W=('L',0),('L',1),('W',0);state={t:[Q(1),Q(0)],src:[Q(0),Q(1)],W:[Q(0),Q(0)]}
 for op in lower_scalar(('add',t,src,a,b)):
  tag,r=op[:2]
  if tag=='clear':state[r]=[Q(0),Q(0)]
  elif tag=='accumulate':state[r]=[x+op[3]*y for x,y in zip(state[r],state[op[2]])]
  else:
   scale={'double':Q(2),'halve':Q(1,2),'divide3':Q(1,3)}[tag];state[r]=[scale*x for x in state[r]]
 assert state[t]==[Q(1),Q(a,b)] and state[src]==[Q(0),Q(1)] and state[W]==[Q(0),Q(0)]
for ori in ['forward','backward']:
 ev=[];sch=[];cur=c['start'][:];hist=Counter();reg={('L',i):{i:Q(1)}for i in range(1023)};initialized=set();centers=set()
 def scalar(phase,e,f):
  t=e[1];src=e[2] if e[0] in ['add','copy'] else None
  for x in [t]+([src] if src else []):
   if x[0]=='L':
    assert 0<=x[1]<1023
    if phase=='main':assert cur[x[1]]==f
    elif phase=='cleanup':assert cur[x[1]]==1 and (x[1]<120 or x[1]>=240)
    else:assert phase=='old_response' and x[1]>=120 and f=='old0'
   else:assert x[0]=='C'
  if src and src[0]=='C':assert src in initialized
  if e[0]=='clear':reg[t]={};initialized.add(t);centers.discard(t)
  elif e[0]=='copy':reg[t]=dict(reg.get(src,{}));initialized.add(t);centers.add(t) if t[0]=='C' else None
  else:
   assert e[0]=='add';d=reg.setdefault(t,{});q=Q(e[3],e[4]);ss=dict(reg.get(src,{}))
   for j,z in ss.items():
    nz=d.get(j,Q(0))+q*z
    if nz:d[j]=nz
    else:d.pop(j,None)
   initialized.add(t);centers.add(t) if t[0]=='C' else None
  ev.append(('scalar',phase,e,f));sch.append((phase,e))
 def climb(r,f,phase):
  old=cur[r]
  if old==f:return
  assert not centers and len(frames[old])<len(frames[f]) and S.contains(frames[old],frames[f]),('bad frame',r,old,f)
  rank=len(frames[f])-len(frames[old]);hist[rank]+=1;newedges.add((old,f));cur[r]=f;ev.append(('climb',phase,r,old,f,rank))
 # Dirty target precancellation MUST precede helper prewhitening: its
 # coefficients are expressed in the ORIGINAL initial-helper basis.
 ev.append(('phase','old_response'))
 for key in ['pre_target_dirty_cancellation_gates','pre_helper_inverse_gates']:
  for t,s,a,b in pre[key]:scalar('old_response',lift(t,s,a,b,ori),'old0')
 ev.append(('phase','ad0'))
 for r,f in enumerate(c['start']):ev.append(('adapter','old_to_new',r,f))
 gi=0
 for phase in ['A','centers','B']:
  ev.append(('phase',phase))
  if phase=='centers':
   table=scatter.table(c)
   for k,r,f in c['ret']:
    temp=('C',k);scalar('main',('clear',temp),f if ori=='forward' else 0)
    if ori=='forward':scalar('main',('add',temp,('L',r),1,1),f)
    else:
     for t in range(120):
      if k in table[t]:q=table[t][k];scalar('main',('add',temp,('L',120+t),q.numerator,q.denominator),0)
    hist[len(frames[f])]+=1;ev.append(('center',k,f if ori=='forward' else 0,0 if ori=='forward' else f,len(frames[f])))
    if ori=='forward':
     for t in range(120):
      if k in table[t]:q=table[t][k];scalar('main',('add',('L',120+t),temp,q.numerator,q.denominator),0)
    else:scalar('main',('add',('L',r),temp,-1,1),f)
    scalar('main',('clear',temp),0 if ori=='forward' else f)
   continue
  for g in c[phase]:
   f=g[1]
   for r in [g[2]]+[t for t,a,b in g[3]]+(g[4] if g[0]=='out' else []):climb(r,f,phase)
   for r,a,b in g[3]:
    t,s=(r,g[2]) if g[0]=='out' else (g[2],r);scalar('main',lift(t,s,a,b,ori),f)
   if gi in bycut:
    aa=bycut[gi];f=aa['frame'];r=aa['sink_helper']
    for q in [r]+[q for q,a,b in aa['uncompute']]:climb(q,f,phase)
    for q,a,b in aa['uncompute']:scalar('main',lift(r,q,a,b,ori),f)
   gi+=1
 ev.append(('phase','final'))
 for r,f in enumerate(final):climb(r,f,'final')
 ev.append(('phase','adF'))
 for r,f in enumerate(final):ev.append(('adapter','canonical_to_bank_residual' if r in sinks else 'new_to_old',r,f))
 ev.append(('phase','cleanup'))
 for key in ['post_source_inverse_gates','post_full_helper_clean_repair_gates']:
  for t,s,a,b in pre[key]:assert t not in sinks and s not in sinks;scalar('cleanup',lift(t,s,a,b,ori),'old1')
 ev.append(('phase','done'))
 expected={('L',i):{i:Q(1)}for i in range(1023)}
 for t in range(120):
  if ori=='forward':expected[('L',120+t)][t]=Q(1)
  else:expected[('L',t)][120+t]=Q(-1)
 assert all(reg[r]==e for r,e in expected.items()),ori+' all independent live columns'
 assert all(not z for r,z in reg.items() if r[0]!='L') and not centers
 for a,b in {(e[3],e[4]) for p,e in sch if e[0]=='add'}:check_lowered_coefficient(a,b)
 primitive_count[ori]=2*sum(primitive_bound(e) for p,e in sch);paid[ori]=hist;events[ori]=ev;words[ori]=sch
 physical_checks[ori]=dict(independent_live_columns=1023,helper_columns=783,all_private_restored_zero=True,common_frame_gate_incidences=True,scalar_macros=len(sch),real_component_primitive_upper=primitive_count[ori],events=len(ev))
 print('PASS heterogeneous literal dirty word + common frames',ori,flush=True)
assert paid['forward']==paid['backward'];H0=Counter()
for b in c['blocks'].values():
 for r,n in b.items():H0[int(r)]+=n
assert dict(paid['forward']-H0)=={1:2,3:4} and dict(H0-paid['forward'])=={4:4}
# Audit every additional canonical transition, including scalar phase.
sys.path.insert(0,str(BASE/'work/odd-stages'));from clifford_exact import *
oldedges=set();cur=c['start'][:]
for ph in ['A','B']:
 for g in c[ph]:
  for r in [g[2]]+[t for t,a,b in g[3]]+(g[4] if g[0]=='out' else []):
   if cur[r]!=g[1]:oldedges.add((cur[r],g[1]));cur[r]=g[1]
for r,f in enumerate(c['final']):
 if cur[r]!=f:oldedges.add((cur[r],f));cur[r]=f
phase_recipes=[]
for a,b in sorted(newedges-oldedges):
 op=canonical_frame(9,frames[a]).adjoint().then(canonical_frame(9,frames[b]));rec,compiled=lower_child(op);assert rec['rank']==len(frames[b])-len(frames[a]);phase_recipes.append(dict(old=a,new=b,**rec))
H=Counter({r:288*n for r,n in paid['forward'].items()})
for r in [16,8,32,8,48,8,48,32,16]:H[r]+=7680
H[1]+=9*3123
m,live,physical=73,58899,58899+783+9+1;mass=sum(r*n for r,n in H.items());assert m*live-mass==9984
compiler=64*74**3;macros=max(len(words[o]) for o in words);lc=sum(paid['forward'].values());adapters=16*(macros+lc+1023+9)+64*73
local_bound=max(primitive_count.values())+adapters*compiler;scalar_total=160*primitive_count['forward']+128*primitive_count['backward'];bridge_adds=18*120*32;terminal_shifts=4*120*32;terminal_moves=2*4*120*32;cover_corrections=live
# At least eight compiler groups per actual nonlocal item, including two
# new rank8 bank endpoint adapters per replica/invocation and all slot routes.
nonlocal_items=4*120*32*9+2*120*32*9+2*9*32*783+2160*32+9*3131+bridge_adds+terminal_shifts+terminal_moves+cover_corrections+physical+2*9*32
outside=8*nonlocal_items+64*73;pervertex=scalar_total+bridge_adds+terminal_shifts+terminal_moves+cover_corrections+(288*adapters+outside)*compiler+64*physical
r=36;group=2**1296*math.prod(2**(2*i)-1 for i in range(1,37));stock=group*physical;s=group*mass;logical=group*pervertex+64;router=compiler*(logical+1)*(stock+1)**2;E=1<<100000;B=s+E;literal=2*(1<<30000)*stock**2+8*s+4*stock+4+32*73
assert local_bound<1<<48 and logical<1<<6050 and router<1<<30000 and literal<E and 32*73*B*B<1<<210000 and 73**2>2*48**2
row=2*stock.bit_length()+9909+252;assert row<20161
invoice=dict(local_primitive_bound=local_bound,pervertex=pervertex,physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),required_C0_bits=(32*73*B*B).bit_length(),physical_row_coefficient=row,halving_degree=2,induction_gap_multiple_B=49)
def load(name):
 path=BASE/'work/pr361/code/engines'/(name+'.py');spec=importlib.util.spec_from_file_location('hetero_'+name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
M=load('moment');BM=load('base_two_moment');rr=M.certify(H,73,live,True);b=Q(int(Q(rr['lower'])*10**18),10**18);step=Q(1,10**18);assert M.moment(H,73,live,b,True)[1]<1<M.moment(H,73,live,b+step,True)[0]
fb=32*73**2*sum(H.values());_,hi=BM.moment(73,live,list(H.items()),b);_,bh=BM.moment(73,live,[(1,fb)],b);lo,_=BM.moment(73,live,list(H.items()),b+step);bl,_=BM.moment(73,live,[(1,fb)],b+step);assert hi+Q(1,10**16)*bh<1<lo+Q(1,10**16)*bl
assert sources=={p:sha(p) for p in sources}
raw=json.dumps(dict(local_programs=events,endpoint_frames=final,bank_endpoint_phase_receipt='BANK-ENDPOINT-PHASE.json',new_phase_recipes=phase_recipes,local_scalar_programs=words,lowered_scalar_programs={o:[(p,op) for p,e in words[o] for op in lower_scalar(e)] for o in words}),sort_keys=True,separators=(',',':')).encode();(OUT/'HETEROGENEOUS-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0))
result=dict(status='PASS_HETEROGENEOUS_LOCAL_BOTH_DIRTY_ORIENTATIONS_FRAME_LEGALITY_NEW_PHASES_FINITE_INVOICE_AND_PRICE',coarse=str(b),coarse_float=float(b),profile=dict(sorted(H.items())),local_profile=dict(sorted(paid['forward'].items())),live=live,physical=physical,m=73,rank_mass=mass,deficit=9984,paid_calls=sum(H.values()),new_canonical_phase_edges=len(phase_recipes),physical_checks=physical_checks,literal_coefficient_expansion='Binary doubling and accumulate, repeated halve and divide3; every distinct coefficient independently checked on symbolic source/target columns, work zero after every macro',invoice=invoice,source_hashes=sources,template_sha256=hashlib.sha256(raw).hexdigest(),bank_geometry='Root HETEROBANKS.json must be pinned; endpoint BANK-ENDPOINT-PHASE.json must be emitted and charged',scope='Finite changed local words, all-column audits and conservative global invoice. Global heterogeneous owners/orthogonal routes and endpoint adapters are separately audited; inherited all-size interfaces remain conditional.')
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2));print('PASS heterogeneous exact coarse',b,float(b),flush=True)
