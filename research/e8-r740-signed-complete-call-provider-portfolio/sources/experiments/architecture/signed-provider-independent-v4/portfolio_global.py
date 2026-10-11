"""Independent reconstruction of heterogeneous controller streams and ownership."""
import json,gzip,hashlib,struct
from pathlib import Path
from collections import Counter,defaultdict
P=Path(__file__).resolve().parent;A=P.parent/'bit-provider-portfolio-v4/global'
r=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
b=gzip.decompress((A/'GLOBAL-TEMPLATE.json.gz').read_bytes());t=json.loads(b);g=r(A/'GLOBAL.json');reg=r(A/'PROVIDERS.json');assert t['provider_registry']==reg and sha(b)==g['template_sha256']
streams={};profiles={};prefixes={}
for pid,z in reg.items():
 s=Path(z['directory']);fs=r(s/'records/frames.json')['frames'];st=r(s/'records/249-states.json');ini=[st['initial'][str(i)]for i in range(980)];fin=[st['final'][str(i)]for i in range(980)];assert ini==z['initial_frames']and fin==z['final_frames'];assert z['widths']==[8-fs[str(f)]['dim']for f in ini[240:]]
 raw=(s/'records/249-records.bin').read_bytes();signed=(s/'signed-records.bin').read_bytes();assert sha(raw)==z['native_record_sha256']and sha(signed)==z['signed_record_sha256']
 for rev in [0,1]:
  key=pid+('_reverse'if rev else'_forward');cur=(fin if rev else ini)[:]+[-1];out=[];H=Counter();norm=[1]*981;peak=1;open_copy=False
  for op,x,y,c,f,last in list(struct.iter_unpack('<6i',raw))[::(-1 if rev else 1)]:
   if op==0:
    a,bb=(c,y)if rev else(y,c);assert cur[x]==a;rank=abs(fs[str(bb)]['dim']-fs[str(a)]['dim']);assert rank==f;cur[x]=bb;H[f]+=bool(f);out.append([0,x,a,bb,f,rev])
   elif op==1:assert cur[x]==cur[y]==f;out.append([1,x,y,-c if rev else c,f,rev])
   elif op==(3 if rev else 2):assert not open_copy;open_copy=True;cur[980]=f;H[8]+=1;out.append([2,x,980,c,f,8,rev])
   else:assert open_copy;open_copy=False;cur[980]=-1;out.append([3,x,980,c,f,last,rev])
  assert not open_copy and cur[:980]==(ini if rev else fin);assert out==t['local_programs'][key];H.pop(0,None);profiles[key]=H;streams[key]=out
  for op,x,y,c,f,last in list(struct.iter_unpack('<6i',signed))[::(-1 if rev else 1)]:
   if op==1:norm[x]+=abs(c)*norm[y];peak=max(peak,norm[x])
   elif op==(3 if rev else 2):norm[980]=norm[x]
   elif op in(2,3):norm[980]=0
  prefixes[key]=peak
idle=[x for x in t['schedule']if x['kind']=='idle'];slots=t['hosting']['slots'];lookup={};occupied=defaultdict(set);used=Counter();H=Counter();digest=hashlib.sha256();events=0
calls={(c['stage'],c['replica']):c for c in t['calls']};assert len(calls)==88
for i,cp,off,w,s,gh in slots:
 rep,h=divmod(gh,740);call=calls[s,rep];assert (s,gh)not in lookup;lookup[s,gh]=(i,cp,off,w)
 assert w==reg[call['provider']]['widths'][h];e=idle[i];assert e['rank']>=off+w
 assert not occupied[i,cp].intersection(range(off,off+w));occupied[i,cp].update(range(off,off+w));used[i,cp]+=w
 # The pending child must be idle throughout the helper invocation.
 at=[j for j,x in enumerate(t['schedule'])if x['kind']=='local_cover_sweep'and x['stage']==s];assert len(at)==1
 for x in t['schedule'][min(at[0],t['schedule'].index(e)):max(at[0],t['schedule'].index(e))+1]:
  if x['kind']=='local_cover_sweep':assert x['pair']!=e['pair']
  if x['kind']=='bridge':assert e['pair']not in(x['src'],x['dst'])
assert len(lookup)==65120
for (s,rep),c in calls.items():
 pid='lazy'if s==5 else'base';assert c['provider']==pid;key=pid+'_'+c['orientation'];assert c['program_key']==key
 assert c['source_record_sha256']==reg[pid]['native_record_sha256']and c['signed_record_sha256']==reg[pid]['signed_record_sha256'];assert c['local_hash']==sha(json.dumps(streams[key],separators=(',',':')).encode())
 owners=[]
 for x in range(240):
  side,port=divmod(x,120);side=1-side if c['orientation']=='reverse'else side;owners.append([rep*1200+(2*c['pair']+side)*120+port,['data',s,port]])
 for h in range(740):
  i,cp,off,w=lookup[s,rep*740+h];orep,sp=divmod(cp,240);side,port=divmod(sp,120);owners.append([orep*1200+(2*idle[i]['pair']+side)*120+port,['hosted',i,off,w]])
 assert owners==c['owners'];H.update(profiles[key])
 for z in streams[key]:
  op=z[0];mapped=[op,owners[z[1]],*z[2:]]if op==0 else[op,owners[z[1]],owners[z[2]]if z[2]<980 else[9600,['private',0]],*z[3:]];digest.update((json.dumps(mapped,separators=(',',':'))+'\n').encode());events+=1
remainders={}
for i,e in enumerate(idle):
 rr=Counter(e['rank']-used[i,cp]for cp in range(1920));assert min(rr)>=0;remainders[str(i)]={str(k):v for k,v in sorted(rr.items())};H.update({k:v for k,v in rr.items()if k})
assert remainders==t['hosting']['remainders'];assert dict(H)=={int(k):v for k,v in g['profile'].items()};assert 9600*78-sum(k*v for k,v in H.items())==3264
assert digest.hexdigest()==g['emitted_program_sha256']and events==g['emitted_events'];prefix=2**24
for s in range(11):prefix*=prefixes[('lazy'if s==5 else'base')+('_reverse'if s%2 else'_forward')]
assert prefix==int(g['global_prefix_bound'])and prefix<2**192
out={'status':'PASS','template_sha256':sha(b),'calls':88,'alternate_calls':8,'slots':len(slots),'profile':dict(sorted(H.items())),'deficit':3264,'mapped_event_sha256':digest.hexdigest(),'events':events,'prefix_bits':prefix.bit_length(),'scope':'Exact registry streams, native frame controller, literal owner injection and disjoint no-touch windows; local signed980/arbitrarydirt gates separately bound. Correlated-bank and all-size compiler premise retained.'}
(P/'PORTFOLIO-GLOBAL.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
