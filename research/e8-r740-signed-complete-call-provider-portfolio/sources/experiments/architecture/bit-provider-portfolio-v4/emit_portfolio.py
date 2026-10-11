"""Whole signed complete-call providers; exact record streams are authoritative."""
from pathlib import Path
import json,gzip,hashlib,struct,copy,shutil
from collections import Counter
P=Path(__file__).resolve().parent;ROOT=P.parents[2];BASE=ROOT/'experiments/architecture/whole-owner-pooling-v4/bit60';OUT=P/'global';OUT.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n')
for name in ['GEOMETRY.json','ISOMETRIES.json','bank_routes.py','hosting_core.py','row_bound.py','moment.py','target_address.py']:
 shutil.copy2(BASE/name,OUT/name)
providers={};streams={};checks={};initials={}
for pid,source in [('base',BASE/'local'),('lazy',P/'drop970-948-lazy')]:
 fs=read(source/'records/frames.json')['frames'];dims={int(k):v['dim']for k,v in fs.items()};st=read(source/'records/249-states.json');initial=[st['initial'][str(i)]for i in range(980)];final=[st['final'][str(i)]for i in range(980)];initials[pid]=initial
 raw=source/'records/249-records.bin';rec=list(struct.iter_unpack('<6i',raw.read_bytes()));srec=list(struct.iter_unpack('<6i',(source/'signed-records.bin').read_bytes()))
 providers[pid]={'directory':str(source),'native_record_sha256':sha(raw),'signed_record_sha256':sha(source/'signed-records.bin'),'states_sha256':sha(source/'records/249-states.json'),'word_sha256':sha(source/'word.json'),'initial_frames':initial,'final_frames':final,'widths':[8-dims[f]for f in initial[240:]]}
 for rev in [False,True]:
  ori='reverse'if rev else'forward';key=pid+'_'+ori;cur=(final if rev else initial)[:]+[-1];val=[1<<i for i in range(980)]+[0];norm=[1]*980+[0];events=[];H=Counter();center=None;adds=0;dim=lambda f:8-dims[f]if rev else dims[f]
  for op,x,y,c,f,z in reversed(rec)if rev else rec:
   if op==0:
    a,b=(c,y)if rev else(y,c);assert cur[x]==a and dim(b)-dim(a)==f;cur[x]=b;H[f]+=bool(f);events.append([0,x,a,b,f,int(rev)])
   elif op==1:
    assert cur[x]==cur[y]==f;val[x]^=val[y];norm[x]+=abs(c)*norm[y];adds+=1;events.append([1,x,y,-c if rev else c,f,int(rev)])
   elif op==(3 if rev else 2):
    assert center is None and val[980]==0;center=x;cur[980]=f;val[980]=val[x];norm[980]=norm[x];H[8]+=1;events.append([2,x,980,c,f,8,int(rev)])
   else:
    assert center==x and val[980]==val[x];center=None;cur[980]=-1;val[980]=norm[980]=0;events.append([3,x,980,c,f,z,int(rev)])
  assert cur[:980]==(initial if rev else final)and center is None
  assert val==[(1<<i)^((1<<(i-120))if 120<=i<240 else 0)for i in range(980)]+[0]
  # Cancellation-free SIGNED prefix, not the native parity stream.
  nn=[1]*980+[0];peak=1
  for op,x,y,c,f,z in reversed(srec)if rev else srec:
   if op==1:nn[x]+=abs(c)*nn[y];peak=max(peak,nn[x])
   elif op==(3 if rev else 2):nn[980]=nn[x]
   elif op in [2,3]:nn[980]=0
  H.pop(0,None);streams[key]=events;checks[key]={'sha256':hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest(),'profile':dict(sorted(H.items())),'native_additions':adds,'signed_units':sum(abs(z[3])for z in srec if z[0]==1),'signed_prefix':peak,'records':len(events)}
 registry=providers[pid];registry['program_keys']=[pid+'_forward',pid+'_reverse']
t=json.loads(gzip.decompress((BASE/'GLOBAL-TEMPLATE.json.gz').read_bytes()));nom=read(P/'POOL-NOMINATION-count8.json');slots=nom['slots'];idle=[e for e in t['schedule']if e['kind']=='idle'];hosted={(s,h):(i,cp,off,w)for i,cp,off,w,s,h in slots};H=Counter();digest=hashlib.sha256();events=0
for call in t['calls']:
 s,rep=call['stage'],call['replica'];pid='lazy'if s==5 else'base';key=pid+'_'+call['orientation'];owners=call['owners'][:240]
 for h in range(740):
  i,cp,off,w=hosted[s,rep*740+h];ownerrep,sp=divmod(cp,240);side,port=divmod(sp,120);family=ownerrep*1200+(2*idle[i]['pair']+side)*120+port;owners.append([family,['hosted',i,off,w]])
 call.update(provider=pid,program_key=key,source_record_sha256=providers[pid]['native_record_sha256'],signed_record_sha256=providers[pid]['signed_record_sha256'],local_hash=checks[key]['sha256'],owners=owners,helper_owner_replicas=[f//1200 for f,r in owners[240:]])
 H.update({int(k):v for k,v in checks[key]['profile'].items()})
 for z in streams[key]:
  op=z[0];mapped=[op,owners[z[1]],*z[2:]]if op==0 else[op,owners[z[1]],owners[z[2]]if z[2]<980 else[9600,['private',0]],*z[3:]];digest.update((json.dumps(mapped,separators=(',',':'))+'\n').encode());events+=1
rem=Counter(nom['remainder_profile']);H.update({int(r):n for r,n in rem.items()if int(r)});assert dict(sorted(H.items()))=={int(k):v for k,v in nom['profile'].items()}
t['local_programs']=streams;t['provider_registry']=providers;t['version']='signed-whole-call-provider-portfolio-stage5-eight-v1';t['source_record_sha256']=providers['base']['native_record_sha256'];t['hosting']['slots']=slots
# Reconstruct exact per-idle remainder owner table.
remainders={}
for i,e in enumerate(idle):
 widths=[e['rank']]*1920
 for ii,cp,off,w,s,h in slots:
  if ii==i:widths[cp]-=w
 assert min(widths)>=0;remainders[str(i)]={str(r):n for r,n in sorted(Counter(widths).items())}
t['hosting']['remainders']=remainders
blob=json.dumps(t,separators=(',',':'),sort_keys=True).encode();(OUT/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0));g=read(BASE/'GLOBAL.json');g.update(template_sha256=hashlib.sha256(blob).hexdigest(),profile=dict(sorted(H.items())),maxchild=max(H),emitted_program_sha256=digest.hexdigest(),emitted_events=events,local_checks=checks,provider_registry=providers,status='PASS_ACTUAL_SIGNED_WHOLE_CALL_PROVIDER_PORTFOLIO_TEMPLATE')
prefix=(1<<24)
for s in range(11):prefix*=checks[('lazy'if s==5 else'base')+('_reverse'if s%2 else'_forward')]['signed_prefix']
assert prefix<1<<192;g.update(global_prefix_bound=str(prefix),global_prefix_bits=prefix.bit_length(),selected_provider_calls=8)
write(OUT/'GLOBAL.json',g);write(OUT/'PROVIDERS.json',providers);write(OUT/'LOCAL-SUMMARY.json',read(BASE/'LOCAL-SUMMARY.json'));write(OUT/'NOMINATION.json',nom);shutil.copy2(P/'POOL-SELECTION-count8.json',OUT/'HOSTING-SELECTION.json')
print(g['status'],g['template_sha256'],g['global_prefix_bits'],checks)
