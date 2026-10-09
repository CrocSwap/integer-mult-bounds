"""Exact terminal-target compiler on the served physical bit word.

Fork of PR200's bit/terminal.py (Chafik Boukhalfa, Apache-2.0; James Chang's PR166 substitution) with served
operations: a served gate adds the passive source data register into its destination, and a served pair's
partner XOR runs right after the injections. Every check of the original is kept.

James Chang's PR166 terminal substitution, specialized and independently
verified by Chafik Boukhalfa with OpenAI Codex assistance. All inherited
word, frame, gauge, reuse and partner-pair credits remain in the adapter.
No source producer is executed. The original adjoint includes deleted roots.
"""
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import sha256
import argparse,importlib.util,json,time,math,sys,gc,resource,signal

def need(x,msg):
 if not x:raise AssertionError(msg)
def compact(c):return {str(k):v for k,v in sorted(c.items()) if v}

def prove(word,selection):
 t0=time.monotonic();C=word.C;h,v,R=word.h,word.v,word.R;ops=word.ops
 baseline=word.row();phase=set(word.phase1);order=word.phase1+word.rest;position={i:j for j,i in enumerate(word.rest)}
 sources=set(word.source.values());aliasroles=set(word.donor)|set(word.donor.values());writes=defaultdict(list);uses=defaultdict(list);rootids=defaultdict(list)
 for i,(a,b,n) in enumerate(ops):
  writes[a].append(i)
  if b>=0:uses[b].append(i)
 for j,s in enumerate(word.w['rootroles']):rootids[s].append(j)
 at=defaultdict(list)
 for s in word.order:at[word.readtime[s]].append(s)
 first=[len(word.rest)+1]*v
 for s in word.order:
  for target in word.gauge[s]['targets']:first[target]=min(first[target],word.readtime[s])
 chosen=[];seen=set();targets=set()
 for entry in selection:
  j,pivot=entry['root'],entry['pivot'];need(type(j) is int and 0<=j<len(word.g['roots']),'root index')
  r=word.g['roots'][j];s=word.w['rootroles'][j];U=word.w['root_frame'][j]
  need(j not in seen and r['kind']=='side','distinct side roots');seen.add(j)
  need(s not in sources|aliasroles|set(word.gauge),'zero-gauge independent scratch root')
  need(rootids[s]==[j] and not uses[s] and writes[s],'one terminal root with writes and no retained consumers')
  need(all(i not in phase for i in writes[s]),'root untouched in center phase')
  need(all(C.sub(word.opframe[i],U) for i in writes[s]),'all writes within root cap')
  need(type(pivot) is int and pivot in r['targets'],'pivot target')
  need(first[pivot]>max(position[i] for i in writes[s]),'pivot untouched by compensation before post')
  need(not targets.intersection(r['targets']),'simultaneous disjoint target groups');targets.update(r['targets'])
  path=[word.opframe[i] for i in writes[s]]+[U,word.w['full_frame']];prev=None;prefix=[]
  for f in path:
   need(prev is None or C.sub(prev,f),'deleted root trajectory nested')
   d=C.dimf[f]-(0 if prev is None else C.dimf[prev])
   if d:prefix.append(d)
   prev=f
  need(sum(prefix)==h,'complete deleted root path')
  chosen.append(dict(root=j,role=s,targets=r['targets'],pivot=pivot,root_frame=U,root_rank=C.dimf[U],writes=writes[s],deleted_path=prefix))
 removed={e['role'] for e in chosen};deletedroots={e['root'] for e in chosen};bywrite={i:e for e in chosen for i in e['writes']};after={e['writes'][-1]:e for e in chosen}
 need(all(a not in removed and b not in removed for i,(a,b,n) in enumerate(ops) if i not in bywrite),'removed roles only occur in their own writes')
 # Complete modified target chronology, including every retained partner delivery.
 Y=Counter();current=[None]*v;events=0
 def move(t,f):
  nonlocal events
  prev=current[t];need(prev is None or C.sub(prev,f),'new target chain nesting')
  need(all(word.module.dot(C.cov[t],b)==0 for b in C.B[f]),'target movement stays inside cap')
  d=C.dimf[f]-(0 if prev is None else C.dimf[prev]);need(d>=0,'target rank monotonicity')
  if d:Y[d]+=1
  current[t]=f;events+=1
 for j,i in enumerate(word.rest):
  for s in at[j]:
   for t in word.gauge[s]['targets']:move(t,word.gauge[s]['frame'])
  if i in bywrite:move(bywrite[i]['pivot'],word.opframe[i])
  if i in after:
   for t in after[i]['targets']:move(t,after[i]['root_frame'])
 for s in at[len(word.rest)]:
  for t in word.gauge[s]['targets']:move(t,word.gauge[s]['frame'])
 deliveries=defaultdict(list)
 for e in word.k['entries']:deliveries[e['deliver_after_root']].append(e)
 for j,r in enumerate(word.g['roots']):
  if r['kind']=='side' and j not in deletedroots:
   for t in r['targets']:move(t,word.w['root_frame'][j])
  for e in deliveries[j]:
   for t in e['receivers']:move(t,e['deliver_frame'])
 for t,f in enumerate(current):
  need(f is not None and C.dimf[f]<=h-1,'final target cap')
  gap=h-1-C.dimf[f]
  if gap:Y[gap]+=1
 need(sum(r*n for r,n in Y.items())==v*(h-1),'full target rank mass')
 local=Counter({int(r):n for r,n in baseline['physical_internal_histogram'].items()})
 for e in chosen:local.subtract(e['deleted_path'])
 need(all(n>=0 for n in local.values()),'positive remaining local ledger')
 _,_,source,_=word.C.chains();child=Counter()
 for part in (local,Y,source):
  for r,n in part.items():
   if r and n:child[r]+=3*n
 for s,z in word.gauge.items():
  if s not in word.donor:child[3*z['dim']]+=1
 child[2]+=2*v;physical_R=baseline['R']-len(chosen);W=2*v+physical_R;rank=sum(r*n for r,n in child.items())
 need(W*3*h-rank==baseline['deficit_per_vertex'],'terminal rank deficit unchanged')
 delta=Counter(child);delta.subtract({int(r):n for r,n in baseline['child_histogram'].items()});expected=Counter()
 for e in chosen:expected[e['root_rank']]-=3;expected[h-e['root_rank']]-=3
 need(compact(delta)==compact(expected),'independent complete ledger agrees with exact terminal cancellation')
 # Literal local sandwich, with arbitrary target values and non-pivot corrections.
 for e in chosen:
  ts=e['targets'];p=ts.index(e['pivot']);n=len(ts);k=len(e['writes']);N=2*n+k
  initial=[[int(a==b) for b in range(N)] for a in range(n)];state=[r[:] for r in initial];program=[]
  def apply(event,direction=1):
   kind,a,b,c=event;c*=direction
   if kind=='shear':state[a]=[x+c*y for x,y in zip(state[a],state[b])]
   else:state[a][b]+=c
  for a in range(n):
   if a!=p:program.append(('shear',a,p,-1))
  program.extend(('basis',p,n+j,1) for j in range(k))
  program.extend(('basis',a,n+k+a,1) for a in range(n) if a!=p)
  for a in range(n):
   if a!=p:program.append(('shear',a,p,1))
  for event in program:apply(event)
  for a in range(n):
   want=initial[a][:]
   for j in range(k):want[n+j]+=1
   if a!=p:want[n+k+a]+=1
   need(state[a]==want,'integer arbitrary-target sandwich')
  for event in reversed(program):apply(event,-1)
  need(state==initial,'literal inverse of integer sandwich')
 # Full original integer adjoint, including the removed root responses.
 adj=word.adjoint()
 def without_deleted():
  out=[{} for _ in range(R)]
  for j,(r,s) in enumerate(zip(word.g['roots'],word.w['rootroles'])):
   if j not in deletedroots:
    for t in r['targets']:out[s][t]=out[s].get(t,0)+1
  for a,b,n in reversed(ops):
   if b<0:continue
   for t,c in out[a].items():out[b][t]=out[b].get(t,0)+c
  return out
 badadj=None;live=sorted(set(word.phys.values())-removed);index={r:2*v+i for i,r in enumerate(live)};columns=2*v+len(live)
 need(len(live)==physical_R,'terminal physical inventory')
 def execute(mode,direction=1,bits=None,mutation=None):
  nonlocal badadj
  major=mode=='bound';binary=mode=='F2'
  unit=(lambda i:1) if major else (lambda i:1<<i) if binary else (lambda i:1<<(bits*i))
  def add(x,c,y):return x+abs(c)*y if major else x^y if binary and c&1 else x if binary else x+c*y
  X0=[unit(i) for i in range(v)];Y0=[unit(v+i) for i in range(v)];Z0={r:unit(index[r]) for r in live}
  x=X0[:];y=Y0[:];z=Z0.copy();done=[];top=1
  def track(value):
   nonlocal top
   if major:top=max(top,value)
   return value
  responses=adj
  if mutation=='omit-ancestor-response':
   if badadj is None:badadj=without_deleted()
   responses=badadj
  def read(s):
   value=z[word.phys[s]]
   for t,c in responses[s].items():y[t]=track(add(y[t],-direction*c,value))
  def gate(i,sign):
   a,b,n=ops[i]
   if i in word.served:z[word.phys[a]]=track(add(z[word.phys[a]],sign,x[word.served[i][0]]));return
   a,b=word.phys[a],word.phys[b];z[a]=track(add(z[a],sign,z[b]))
  for s in range(R):
   if s not in word.gauge and s not in removed:read(s)
  for n,s in word.source.items():z[word.phys[s]]=track(add(z[word.phys[s]],1,x[n]))
  for e in word.k['entries']:
   if e.get('early'):x[e['carrier']]=track(add(x[e['carrier']],1,x[e['passive']]))
  for i in word.phase1:gate(i,1);done.append(i)
  for r,s in zip(word.g['roots'],word.w['rootroles']):
   if r['kind']=='center':
    for t in r['targets']:y[t]=track(add(y[t],direction,z[word.phys[s]]))
  for e in chosen:
   if mutation=='omit-pre-target' and e is chosen[0]:continue
   for t in e['targets']:
    if t!=e['pivot']:y[t]=track(add(y[t],-1,y[e['pivot']]))
  omitted=False
  for j,i in enumerate(word.rest):
   for s in at[j]:read(s)
   if i in bywrite:
    e=bywrite[i];a,b,n=ops[i]
    if mutation=='omit-write' and not omitted:omitted=True
    else:y[e['pivot']]=track(add(y[e['pivot']],direction,z[word.phys[b]]))
   else:gate(i,1);done.append(i)
   if i in after:
    e=after[i]
    for t in e['targets']:
     if t!=e['pivot']:y[t]=track(add(y[t],1,y[e['pivot']]))
  for s in at[len(word.rest)]:read(s)
  for j,(r,s) in enumerate(zip(word.g['roots'],word.w['rootroles'])):
   if r['kind']=='side' and j not in deletedroots:
    for t in r['targets']:y[t]=track(add(y[t],direction,z[word.phys[s]]))
   for e in deliveries[j]:
    a,b=e['carrier'],e['passive']
    if not e.get('early'):x[a]=track(add(x[a],1,x[b]))
    for t in e['receivers']:y[t]=track(add(y[t],direction,x[a]))
  for e in word.k['entries']:
   a,b=e['carrier'],e['passive'];x[a]=track(add(x[a],-1,x[b]))
  need(done==[i for i in order if i not in bywrite],'exact retained forward operation list')
  for i in reversed(done):gate(i,-1)
  for n,s in word.source.items():z[word.phys[s]]=track(add(z[word.phys[s]],-1,x[n]))
  if binary:want=[Y0[t]^X0[t] for t in range(v)]
  else:
   # Independent defining integer decoder from source-disjoint graph supports.
   # It includes all original roots and every original partner delivery.
   want=Y0[:];cache={}
   for r in word.g['roots']:
    n=r['node']
    if n not in cache:
     mask=C.sup[n];value=0
     while mask:
      bit=mask&-mask;mask-=bit;value=add(value,1,X0[bit.bit_length()-1])
     cache[n]=value
    for t in r['targets']:want[t]=add(want[t],direction,cache[n])
   for e in word.k['entries']:
    value=add(X0[e['carrier']],1,X0[e['passive']])
    for t in e['receivers']:want[t]=add(want[t],direction,value)
  if major:return max(top,max(a+b for a,b in zip(y,want)),max(z[r]+Z0[r] for r in live),max(a+b for a,b in zip(x,X0)))
  need(y==want,'all output columns equal the independent defining decoder')
  need(z==Z0 and x==X0,'all dirty and source columns restored')
  return dict(mode=mode,direction=direction,formal_columns=columns,source_columns=v,target_columns=v,dirty_columns=len(live),all_outputs=True,all_sources_and_dirty_restored=True,partner_mix_unmix_at_original_anchors=True,retained_cleanup_literal_reverse=True)
 bound=execute('bound');bits=8*((bound.bit_length()+2+7)//8);need((1<<bits)>2*bound,'injective integer residual digit bound')
 print('bound',bound,'bits',bits,'columns',columns,flush=True)
 formal=[execute('F2')];gc.collect();formal.append(execute('Z',1,bits));gc.collect();formal.append(execute('Z',-1,bits));gc.collect()
 controls={}
 for mutation in ['omit-ancestor-response','omit-pre-target','omit-write']:
  try:execute('F2',mutation=mutation)
  except AssertionError:controls[mutation]='REJECTED'
  else:raise AssertionError('accepted mutation '+mutation)
 original_hist={int(r):n for r,n in baseline['child_histogram'].items()}
 profile=dict(baseline,R=physical_R,terminal_sinks=len(chosen),active_virtual_R=R-len(chosen),scalar_role_reserve=R,W_per_vertex=W,rank_per_vertex=rank,child_histogram=compact(child),physical_internal_histogram=compact(local),physical_target_histogram=compact(Y))
 return dict(status='PASS complete terminal bit word, exact geometry/ledger/F2/integer columns',profile=profile,baseline_profile=baseline,selected=chosen,target_events=events,child_delta=compact(delta),formal=formal,integer_residual_bound=bound,packed_digit_bits=bits,base_exceeds_twice_bound=True,controls=controls,literal_sandwich_inverse=True,all_original_adjoint_responses_retained=True,original_partner_delivery_anchors_retained=True,new_frames_added=0,scalar_addition_delta=-sum(len(e['writes'])+2 for e in chosen),scalar_bill='Retain the original conservative full-word scalar inventory: removed old root reads/old root corrections and deleted inverse gates dominate the new pre/post target shears.',foreign_producer_replays=0,seconds=time.monotonic()-t0,maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

if __name__=='__main__':
 if sys.flags.optimize:raise SystemExit('run without -O')
 p=argparse.ArgumentParser();p.add_argument('--adapter',type=Path,required=True);p.add_argument('--selection',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 resource.setrlimit(resource.RLIMIT_CPU,(180,180));signal.alarm(180)
 spec=importlib.util.spec_from_file_location('checked_bit_adapter',a.adapter);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);w=m.Candidate();w.exact_frames()
 pins={str(p):sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),a.adapter,a.adapter.with_name('base_word.py'),Path(w.module.__file__),a.selection,*w.input_paths]}
 a.out.with_suffix('.inputs.json').write_text(json.dumps(pins,sort_keys=True,indent=2)+'\n')
 data=json.loads(a.selection.read_text());selected=data['selected'] if isinstance(data,dict) else data
 result=prove(w,selected)
 for path,digest in pins.items():need(sha256(Path(path).read_bytes()).hexdigest()==digest,'source changed during proof: '+path)
 result['input_pins']=pins;a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','seconds','integer_residual_bound','packed_digit_bits','controls','maxrss']}),flush=True)
