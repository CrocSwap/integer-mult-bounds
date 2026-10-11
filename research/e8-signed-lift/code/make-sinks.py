from pathlib import Path
from array import array
from collections import Counter
import json,hashlib,struct
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);opts=ap.parse_args();D=opts.base;O=opts.output;O.mkdir(exist_ok=False)
read=lambda p:json.loads(Path(p).read_text());write=lambda p,x:Path(p).write_text(json.dumps(x,sort_keys=True)+'\n');sha=lambda b:hashlib.sha256(b).hexdigest()
m=read(D/'meta.json');n=m['n'];v=m['v'];zero=m['ZERO'];full=m['FULL'];frames=read(D/'frames.json');ini={int(k):f for k,f in read(D/'initial.json').items()};fin={int(k):f for k,f in read(D/'final.json').items()};regs=read(D/'regs.json');old=list(struct.iter_unpack('<6i',(D/'records.bin').read_bytes()));selection=read(opts.selection)['candidates'];entry=selection[0]['entry'];S=set();remove=set();redirect={};after={entry:[]};deleted=set();logs=[]
for row in selection:
 r=row['stream'];p=row['pivot'];targets=row['targets'];assert not S&set(targets);S.update(targets);deleted.add(r)
 for k,e in enumerate(old):
  op,a,b,c,f,z=e
  if op==1 and b==r:remove.add(k)
 for k in row['cleanups']:remove.add(k)
 for k in row['writes']:
  op,a,b,c,f,z=old[k];assert a==r;redirect[k]=(op,p,b,c,f,z)
 after[entry]+=[(1,t,p,-1,zero,90)for t in targets if t!=p]
 after.setdefault(row['last'],[]).extend((1,t,p,1,row['root_frame'],91)for t in targets if t!=p)
 logs.append(dict(stream=r,pivot=p,deleted_reads_and_deliveries=sum(1 for e in old if e[0]==1 and e[2]==r),deleted_cleanups=len(row['cleanups']),redirected_writes=len(row['writes']),setup_restore_ADDs=2*(len(targets)-1)))
raw=[]
for k,e in enumerate(old):
 if e[0]!=0 and k not in remove:raw.append(redirect.get(k,e))
 raw.extend(after.get(k,[]))
assert all(a not in deleted and (op==0 or b not in deleted)for op,a,b,c,f,z in raw)
surv=[a for a in range(n)if a not in deleted];mp={a:j for j,a in enumerate(surv)};mp[n]=len(surv);ns=len(surv);ini={mp[a]:f for a,f in ini.items()if a not in deleted};fin={mp[a]:f for a,f in fin.items()if a not in deleted};raw=[(op,mp[a],b if op==0 else mp[b],c,f,z)for op,a,b,c,f,z in raw]
state=dict(ini);out=[];hist=Counter();subcache={};active=None
# Matrix nesting is exact integer annihilator dot, no float/rank relaxation.
def sub(a,b):
 if (a,b)not in subcache:subcache[a,b]=frames[str(a)]['dim']<=frames[str(b)]['dim'] and all(sum(x*y for x,y in zip(xx,yy))==0 for xx in frames[str(a)]['B']for yy in frames[str(b)]['A'])
 return subcache[a,b]
def move(a,f):
 if state[a]==f:return
 old=state[a];assert sub(old,f),(a,old,f);gap=frames[str(f)]['dim']-frames[str(old)]['dim'];out.append((0,a,old,f,gap,0));state[a]=f
 if gap:hist[gap]+=1
for e in raw:
 op,a,b,c,f,z=e
 if op==1:
  move(a,f)
  if b!=ns:move(b,f)
  else:assert active is not None and f==zero
  assert state[a]==state[b]==f;out.append(e)
 elif op==2:
  assert active is None;move(a,c);state[ns]=f;active=a;hist[z]+=1;out.append(e)
 elif op==3:assert active==a and state[a]==c and state[ns]==f==zero;active=None;out.append(e);del state[ns]
 else:raise AssertionError(op)
for a,f in sorted(fin.items()):move(a,f)
assert active is None and state==fin
rbytes=b''.join(struct.pack('<6i',*e)for e in out);(O/'records.bin').write_bytes(rbytes);write(O/'frames.json',frames);write(O/'initial.json',ini);write(O/'final.json',fin);write(O/'regs.json',[regs[a-2*v]for a in surv if a>=2*v]);meta=dict(m,n=ns,R=ns-2*v,raw_sha256=sha(rbytes));write(O/'meta.json',meta);before=read(D/'physical.json')['paid_histogram'];delta=Counter(hist);delta.subtract({int(k):v for k,v in before.items()});write(O/'physical.json',dict(paid_histogram=dict(hist),paid_rank_mass=sum(k*v for k,v in hist.items()),category_names=[],independent_dirty_registers=ns-2*v));receipt=dict(status='OWN_LITERAL_SINKS351_MATERIALIZED_NESTED_FRAMES',selected=len(selection),removed_roles=sorted(deleted),survivor_role_map=mp,unchanged_data_endpoints=True,all_MOVEs_nested_exact=True,source_raw_sha256=m['raw_sha256'],output_raw_sha256=sha(rbytes),records=len(out),ADDs=sum(e[0]==1 for e in out),old_R=m['R'],new_R=ns-2*v,old_mass=sum(int(k)*v for k,v in before.items()),new_mass=sum(k*v for k,v in hist.items()),paid_histogram_delta={k:v for k,v in delta.items()if v},changes=logs,scope='Literal own edits and exact rebuilt frame chronology, all-column and bank/finite invoice pending');write(opts.receipt,receipt);print(json.dumps({k:v for k,v in receipt.items()if k not in ['survivor_role_map','changes']}))
