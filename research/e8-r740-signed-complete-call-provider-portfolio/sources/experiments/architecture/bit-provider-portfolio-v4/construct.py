"""Complete signed zero-entrance provider variants, freshly dirt-compensated."""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import json,struct,gzip,copy
P=Path(__file__).resolve().parent;ROOT=P.parents[2];BASE=ROOT/'experiments/architecture/whole-owner-pooling-v4/bit60/local';read=lambda q:json.loads(q.read_bytes());word=read(BASE/'word.json');sel=read(BASE/'SELECTION.json');state=read(BASE/'records/249-states.json');frames=read(BASE/'records/frames.json');F={int(k):v for k,v in frames['frames'].items()};records=list(struct.iter_unpack('<6i',(BASE/'signed-records.bin').read_bytes()));n=980
add=lambda a,b,c:{k:v for k,v in {k:a.get(k,0)+c*b.get(k,0)for k in a.keys()|b.keys()}.items()if v}
def run(es):
 rows=[{i:1}for i in range(n)]+[{}];opened=None
 for op,a,b,c,f,z in es:
  if op==0:continue
  if op==1:rows[a]=add(rows[a],rows[b],c)
  elif op==2:assert opened is None and not rows[n];rows[n]=dict(rows[a]);opened=a
  else:assert op==3 and opened==a and rows[n]==rows[a];rows[n]={};opened=None
 assert opened is None and not rows[n];return rows[:n]
I=[{i:1}for i in range(n)];expected=run(records)
for dropped in [(970,),(948,),(970,948)]:
 out=P/('drop'+'-'.join(map(str,dropped))+'-lazy');out.mkdir(exist_ok=True);(out/'records').mkdir(exist_ok=True);chosen=[e for e in sel['entries']if e['pivot']in dropped];assert len(chosen)==len(dropped)
 remove=[]
 for e in chosen:
  for donor,q in e['donor_coefficients']:
   pre=(1,donor,e['pivot'],-q,e['frame'],2);post=(1,donor,e['pivot'],q,1,5)
   assert records.count(pre)==records.count(post)==1;remove.extend([pre,post])
 es=[x for x in records if x not in remove];s=copy.deepcopy(state);w=copy.deepcopy(word)
 for p in dropped:
  old=int(s['initial'][str(p)]);assert old==w['start'][p] and F[old]['dim']==1;s['initial'][str(p)]=0;w['start'][p]=0
  k=next(i for i,x in enumerate(es)if x[0]==0 and x[1]==p);op,a,b,c,f,z=es[k];assert b==old;es[k]=(op,a,0,c,f+1,z)
 # The raw changed main operator is evaluated on every integer column.
 changed=run(es);assert all(changed[i]==I[i]for i in list(range(120))+list(range(240,n)))
 assert all({k:v for k,v in changed[t].items()if k not in dropped}==expected[t]for t in range(120,240))
 compensation=[(1,t,p,-changed[t].get(p,0),0,1)for t in range(120,240)for p in dropped if changed[t].get(p,0)]
 es=compensation+es;assert run(es)==expected
 # Recompile every actual frame transition at its first surviving use.
 # Removing a kernel shear can retire a donor entrance climb entirely.
 oldes=es;es=[];labels={int(r):f for r,f in s['initial'].items()};labels[n]=-1
 def reach(r,f):
  old=labels[r]
  if old==f:return
  assert r<n and F[f]['dim']>F[old]['dim'] and all(sum(x*y for x,y in zip(u,v))==0 for u in F[old]['B'] for v in F[f]['A'])
  es.append((0,r,old,f,F[f]['dim']-F[old]['dim'],0));labels[r]=f
 for op,a,b,c,f,z in oldes:
  if op==0:continue
  if op==1:
   reach(a,f)
   if b==n:assert labels[b]==f
   else:reach(b,f)
  elif op==2:reach(a,c);assert labels[n]==-1;labels[n]=f
  else:assert op==3 and labels[a]==c and labels[n]==f;labels[n]=-1
  es.append((op,a,b,c,f,z))
 for r in range(n):reach(r,s['final'][str(r)])
 assert run(es)==expected
 inverse=[(op,a,b,-c,f,z)if op==1 else(3 if op==2 else 2,a,b,c,f,z)if op in(2,3)else x for x in reversed(es)for op,a,b,c,f,z in[x]]
 # Literal inverse on arbitrary target/helper dirt, rather than a native parity check.
 rows=run(inverse);wanted=[dict(x)for x in I]
 for t in range(120,240):wanted[t]=add(wanted[t],{k:v for k,v in expected[t].items()if k<120},-1)
 assert rows==wanted
 cur={int(r):f for r,f in s['initial'].items()};cur[n]=-1;H=Counter();opened=None;units=0;norm=[1]*n+[0];peak=1
 for op,a,b,c,f,z in es:
  if op==0:
   assert cur[a]==b;assert F[c]['dim']-F[b]['dim']==f;cur[a]=c;H[f]+=1
  elif op==1:
   assert cur[a]==cur[b]==f and a!=opened;norm[a]+=abs(c)*norm[b];peak=max(peak,norm[a]);units+=abs(c)
  elif op==2:
   assert opened is None and cur[a]==c;cur[n]=f;opened=a;norm[n]=norm[a];H[8]+=1
  else:assert opened==a and cur[a]==c and cur[n]==f;cur[n]=-1;opened=None;norm[n]=0
 assert opened is None and all(cur[r]==s['final'][str(r)]for r in range(n))
 native=[(op,a,b,1,f,z)if op==1 else x for x in es for op,a,b,c,f,z in[x]if op!=1 or c&1]
 (out/'signed-records.bin').write_bytes(b''.join(struct.pack('<6i',*x)for x in es));(out/'records/249-records.bin').write_bytes(b''.join(struct.pack('<6i',*x)for x in native));(out/'records/249-states.json').write_text(json.dumps(s,indent=2)+'\n');(out/'records/frames.json').write_bytes((BASE/'records/frames.json').read_bytes())
 w={k:v for k,v in w.items()if k not in ['A','B','C','D']};w['program_model']='authoritative integer record stream; no grouped-word regeneration';w['native_record_sha256']=sha256((out/'records/249-records.bin').read_bytes()).hexdigest();w['signed_record_sha256']=sha256((out/'signed-records.bin').read_bytes()).hexdigest()
 (out/'word.json').write_text(json.dumps(w,sort_keys=True,separators=(',',':')));(out/'word.json.gz').write_bytes(gzip.compress((out/'word.json').read_bytes(),mtime=0));(out/'decoder-and-dirt.json').write_bytes((BASE/'decoder-and-dirt.json').read_bytes())
 report=dict(status='PASS_COMPLETE_SIGNED_PROVIDER_ALL980_DIRT_LITERAL_INVERSE_FRAMES',dropped=list(dropped),removed_shears=remove,new_zero_compensation=compensation,local_profile=dict(H),rankmass=sum(r*k for r,k in H.items()),signed_units=units,forward_prefix=peak,width_inventory=dict(Counter(8-F[s['initial'][str(h)]]['dim']for h in range(240,980))),source={str(q):sha256(q.read_bytes()).hexdigest()for q in [BASE/'signed-records.bin',BASE/'SELECTION.json',BASE/'word.json',BASE/'records/249-states.json']},scope='Actual signed provider, freshly dirt corrected; native word grouped phases have not been recompiled, only canonical integer record stream is authoritative. Full supplier allocation/sigma/prefix/invoice remain separate.')
 (out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(out.name,{k:v for k,v in report.items()if k not in['source','removed_shears','new_zero_compensation','scope']})
