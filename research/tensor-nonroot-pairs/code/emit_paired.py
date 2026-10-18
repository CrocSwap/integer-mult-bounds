"""Emit the complete paired-rational whole-owner cover; source-bound literal rows."""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,struct,hashlib,sys
read=lambda p:json.loads(Path(p).read_text())
canon=lambda z:json.dumps(z,sort_keys=True,separators=(',',':')).encode()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def local_streams(local):
 rec=list(struct.iter_unpack('<6i',(local/'records/249-records.bin').read_bytes()));state=read(local/'records/249-states.json');fs=read(local/'records/frames.json')['frames'];dims={int(f):z['dim']for f,z in fs.items()}
 initial=[state['initial'][str(i)]for i in range(955)];final=[state['final'][str(i)]for i in range(955)];streams={};checks={}
 for reverse in (False,True):
  cur=(final if reverse else initial)[:]+[-1];val=[1<<i for i in range(955)]+[0];norm=[1]*955+[0];maxnorm=1;center=None;hist=Counter();events=[];copies=adds=0
  dim=lambda f:8-dims[f]if reverse else dims[f]
  for op,x,y,c,f,z in (reversed(rec)if reverse else rec):
   if op==0:
    oldf,newf=(c,y)if reverse else(y,c);assert cur[x]==oldf and dim(newf)-dim(oldf)==f>=0;cur[x]=newf
    if f:hist[f]+=1
    events.append([0,x,oldf,newf,f,int(reverse)])
   elif op==1:
    assert cur[x]==cur[y]==f and x!=y and x<955
    if center is not None:assert x!=center
    if y==955:assert center is not None
    if c&1:val[x]^=val[y]
    norm[x]+=abs(c)*norm[y];maxnorm=max(maxnorm,norm[x]);adds+=1;events.append([1,x,y,-c if reverse else c,f,int(reverse)])
   elif op==(3 if reverse else 2):
    assert center is None and y==955 and cur[x]==c and val[955]==0;rank=abs(dim(c)-dim(f));assert rank==8 and z==(0 if reverse else rank)
    center=x;cur[955]=f;val[955]=val[x];norm[955]=norm[x];hist[rank]+=1;copies+=1;events.append([2,x,955,c,f,rank,int(reverse)])
   else:
    assert op==(2 if reverse else 3) and center==x and y==955 and cur[x]==c and cur[955]==f and val[955]==val[x]
    val[955]=norm[955]=0;cur[955]=-1;center=None;events.append([3,x,955,c,f,z,int(reverse)])
  assert center is None and copies==9 and cur[:955]==(initial if reverse else final)and val[955]==0
  for i in range(955):assert val[i]==((1<<i)^((1<<(i-120))if 120<=i<240 else 0))
  key='reverse'if reverse else'forward';streams[key]=events;checks[key]=dict(copies=copies,adds=adds,records=len(events),all_columns=955,cancellation_free_row_l1=maxnorm,profile=dict(hist),sha256=hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest())
 assert checks['forward']['profile']==checks['reverse']['profile']
 return streams,checks,initial

def emit(parent,local,word,allocation,out):
 out.mkdir(exist_ok=False);t=json.loads(gzip.decompress((parent/'GLOBAL-TEMPLATE.json.gz').read_bytes()));g=read(parent/'GLOBAL.json');w=read(word);a=read(allocation)
 assert a['source_word_sha256']==sha(word);streams,checks,initial=local_streams(local);assert initial==w['start'];t['local_programs']=streams
 L,T,M,R=11,8,78,715;DATA=9600;pcs={(s,rep,h):z for s,rep,h,z in a['owners']};paid=Counter();callmap={}
 for c in t['calls']:
  s,rep=c['stage'],c['replica'];ori='reverse'if c['orientation'].endswith('reverse')else'forward';c['orientation']=ori;c['local_hash']=checks[ori]['sha256'];own=c['owners'][:240]
  for h in range(240,955):
   z=pcs[s,rep,h]
   route=['paired-rational',z['pair'],z['copy']]if z['kind']=='paired-rational-whole'else['coordinate-whole',z['window'],z['offset'],z['width']]
   own.append([z['family'],route])
  c['owners']=own;callmap[s,rep]=c
  for z in streams[ori]:
   if z[0]==0 and z[4]:paid[z[4]]+=1
   if z[0]==2:paid[z[5]]+=1
 used=Counter()
 for z in pcs.values():
  if z['kind']=='coordinate-whole':used[z['window'],z['family']]+=z['width']
 for p in a['pairs']:used[p['window'],p['family']]+=14
 remainder=Counter()
 for key,(pair,rank,stages)in a['windows'].items():
  i=int(key)
  for rep in range(T):
   for cp in range(240):
    family=rep*1200+pair*240+cp;r=rank-used[i,family];assert r>=0
    if r:paid[r]+=1;remainder[r]+=1
 assert dict(paid)=={int(r):n for r,n in a['profile'].items()}
 # Complete chronological scalar replay on all independent stage-helper columns.
 n=1200+L*R;vals=[1<<i for i in range(n)]+[0];stages=[]
 for e in t['schedule']:
  if e['kind']=='local_cover_sweep':
   s,p,rev=e['stage'],e['pair'],e['reverse'];before=vals[:];temp=n;opened=False
   def mapper(i):
    if i==955:return temp
    if i<240:return (2*p+((1-i//120)if rev else i//120))*120+i%120
    return 1200+s*R+i-240
   for z in streams['reverse'if rev else'forward']:
    if z[0]==0:continue
    x,y=mapper(z[1]),mapper(z[2])
    if z[0]==1:
     if z[3]&1:vals[x]^=vals[y]
    elif z[0]==2:assert not opened;vals[temp]=vals[x];opened=True
    else:assert opened and vals[temp]==vals[x];vals[temp]=0;opened=False
   assert not opened
   dst=(2*p+(0 if rev else 1))*120;src=(2*p+(1 if rev else 0))*120
   for k in range(120):before[dst+k]^=before[src+k]
   assert vals==before;stages.append(dict(stage=s,all_columns=n,helper_columns=L*R,reverse=rev))
  elif e['kind']=='bridge':
   d,s=e['dst'],e['src']
   for k in range(120):vals[2*d*120+k]^=vals[2*s*120+k];vals[(2*s+1)*120+k]^=vals[(2*d+1)*120+k]
 # Physical family alias-sensitive integer l1 invoice on EVERY emitted row.
 norms=[1]*DATA+[0];pref=1;dg=hashlib.sha256();count=0
 for e in t['schedule']:
  if e['kind']=='local_cover_sweep':
   for rep in range(T):
    c=callmap[e['stage'],rep];own=c['owners']
    for z in streams[c['orientation']]:
     op=z[0];mapped=[op,own[z[1]]]
     if op==0:mapped.extend(z[2:])
     else:
      mapped.extend([own[z[2]]if z[2]<955 else[DATA,['private',0]],*z[3:]])
      x=own[z[1]][0];y=own[z[2]][0]if z[2]<955 else DATA
      if op==1:norms[x]+=abs(z[3])*norms[y]
      elif op==2:norms[DATA]=norms[x]
      else:assert op==3;norms[DATA]=0
      pref=max(pref,norms[x],norms[DATA])
     dg.update(json.dumps(mapped,separators=(',',':')).encode()+b'\n');count+=1
  elif e['kind']=='bridge':
   d,s=e['dst'],e['src']
   for rep in range(T):
    for k in range(120):
     for x,y in [(rep*1200+2*d*120+k,rep*1200+2*s*120+k),(rep*1200+(2*s+1)*120+k,rep*1200+(2*d+1)*120+k)]:norms[x]+=norms[y];pref=max(pref,norms[x]);dg.update(json.dumps(['bridge-add',x,y],separators=(',',':')).encode()+b'\n');count+=1
 assert norms[DATA]==0
 t.pop('hosting',None);t.pop('program_registry',None)
 dims={int(f):z['dim']for f,z in read(local/'records/frames.json')['frames'].items()}
 iso=[]
 pairedframes={int(x)for x in a['registry']}
 for f in sorted(set(initial[240:])-pairedframes):
  ent=sorted({i for li in w['frames'][f]for i,x in enumerate(w['lines'][li])if x and sum(bool(y)for y in w['lines'][li])==1});res=[i for i in range(8)if i not in ent]
  assert len(ent)==dims[f] and all(all(i in ent for i,x in enumerate(w['lines'][li])if x)for li in w['frames'][f])
  iso.append(dict(frame=f,entrance_rank=len(ent),denominator=2,entrance_basis=ent,residual_basis=res,orthogonal_rows_numerator=[[2*int(i==j)for j in range(8)]for i in ent+res]))
 t.update(residual_isometries=iso,entrance_rank_total=sum(dims[f]for f in initial[240:]),source_word_sha256=sha(word),frame_geometry=dict(lines=w['lines'],frames=w['frames'],initial=initial,final=[read(local/'records/249-states.json')['final'][str(i)]for i in range(955)]))
 t.update(version='nonroot-paired-whole-owner-v1',cover='GL',residual_isometries_scope='Fresh source-bound coordinate entrance maps plus complete paired rational registry for every new non-root pivot',paired_rational_hosting=a,source_record_sha256=sha(local/'records/249-records.bin'))
 blob=canon(t);(out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0))
 dims={int(f):z['dim']for f,z in read(local/'records/frames.json')['frames'].items()}
 g.update(local_additions=max(v['adds']for v in checks.values()),entrance_rank_total=sum(dims[f]for f in initial[240:]),hosted_coordinates=sum(z['width']for z in pcs.values()),local_invocations=len(t['calls']))
 (out/'GEOMETRY.json').write_bytes((parent/'GEOMETRY.json').read_bytes())
 g.update(status='PASS_COMPLETE_PAIRED_WHOLE_OWNER_SCALAR_EMISSION',word_sha256=sha(word),source_records_sha256=sha(local/'records/249-records.bin'),local_checks=checks,scalar_stages=stages,template_sha256=hashlib.sha256(blob).hexdigest(),emitted_program_sha256=dg.hexdigest(),emitted_events=count,profile=dict(sorted(paid.items())),rank_mass=sum(r*n for r,n in paid.items()),deficit=3264,maxchild=max(paid),global_prefix_bound=str(pref),global_prefix_bits=pref.bit_length(),charged_prefix_bits=64*((pref.bit_length()+63)//64),paired_allocation_sha256=sha(allocation),paired_residuals=1936,whole_residuals=L*T*R,cross_family_splits=0,route_extra_required=5,residual_isometry_factor_allowance=512,cover='GL',row_coefficient=28416,routing_allowance='Same fixed-dyadic ordered-affine weighted GL contract B_GL as PR490',provider_initial_frames=initial)
 (out/'GLOBAL.json').write_text(json.dumps(g,indent=2)+'\n');print(json.dumps({k:g[k]for k in ['status','profile','global_prefix_bits','charged_prefix_bits','row_coefficient','emitted_events']},indent=2))
if __name__=='__main__':emit(*map(Path,sys.argv[1:]))
