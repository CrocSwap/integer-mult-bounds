from pathlib import Path
from collections import Counter
import json,hashlib,struct
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--labels',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);opts=ap.parse_args();D=opts.base;O=opts.output;O.mkdir(exist_ok=False);read=lambda p:json.loads(Path(p).read_text());write=lambda p,x:Path(p).write_text(json.dumps(x,sort_keys=True)+'\n');sha=lambda b:hashlib.sha256(b).hexdigest();m=read(D/'meta.json');frames=read(D/'frames.json');ini={int(k):f for k,f in read(D/'initial.json').items()};fin={int(k):f for k,f in read(D/'final.json').items()};n=m['n'];v=m['v'];zero=m['ZERO'];full=m['FULL'];r=7790;p=1168;S=list(range(1168,1172));src=4385;q=4341;old=list(struct.iter_unpack('<6i',(D/'records.bin').read_bytes()));entry=max(i for i,e in enumerate(old)if e[0]==3);touch=[(i,e)for i,e in enumerate(old)if e[0]==1 and r in(e[1],e[2])];fwd=[i for i,e in touch if e[1]==r and e[4]!=full];cln=[i for i,e in touch if e[1]==r and e[4]==full];early=[i for i in fwd if i<=entry];later=[i for i in fwd if i>entry];assert len(early)==1 and len(later)==2 and old[early[0]][2]==src and old[early[0]][3]==1
updates=[i for i in range(early[0]+1,entry+1)if old[i][0]==1 and old[i][1]==src];assert len(updates)==1 and old[updates[0]][2:4]==(q,1);assert not any(old[i][0]==1 and old[i][1]==q for i in range(updates[0]+1,entry+1));last=max(later);roots=[i for i,e in touch if e[2]==r and e[4]!=zero];dirty=[i for i,e in touch if e[2]==r and e[4]==zero];assert len(roots)==len(dirty)==4 and {old[i][1]for i in roots}==set(S)=={old[i][1]for i in dirty};assert all(old[i][3]==1 for i in roots)and all(old[i][3]==-1 for i in dirty);root=old[roots[0]][4];assert len({old[i][4]for i in roots})==1 and min(roots)>last and min(cln)>max(roots)
assert not any(e[0]==1 and e[2]in S or e[0]in(2,3)and e[1]in S+[r,src,q] for e in old);assert not any(e[0]==1 and e[1]==p and e[2]!=r for e in old[entry+1:last+1]);state=dict(ini)
for op,a,b,c,f,z in old[:entry+1]:
 if op==0:state[a]=c
recovery=state[src];assert state[q]==recovery and frames[str(recovery)]['dim']==5 and state[r]==old[early[0]][4]and all(state[t]==zero for t in S);firstframe=state[r];fin[r]=recovery
remove=set(cln+roots);raw=[]
for i,e in enumerate(old):
 if e[0]!=0 and i not in remove:raw.append((1,p,e[2],e[3],e[4],96)if i in later else e)
 if i==entry:
  raw.extend([(1,t,p,-1,zero,94)for t in S if t!=p]);raw.extend([(1,p,r,1,firstframe,95),(1,r,src,-1,recovery,97),(1,r,q,1,recovery,98)])
 if i==last:raw.extend((1,t,p,1,root,99)for t in S if t!=p)
subcache={}
def sub(a,b):
 if(a,b)not in subcache:subcache[a,b]=frames[str(a)]['dim']<=frames[str(b)]['dim'] and all(sum(x*y for x,y in zip(xx,yy))==0 for xx in frames[str(a)]['B']for yy in frames[str(b)]['A'])
 return subcache[a,b]
state=dict(ini);out=[];hist=Counter();active=None
def move(a,f):
 if state[a]==f:return
 old=state[a];assert sub(old,f),(a,old,f);gap=frames[str(f)]['dim']-frames[str(old)]['dim'];out.append((0,a,old,f,gap,0));state[a]=f
 if gap:hist[gap]+=1
for e in raw:
 op,a,b,c,f,z=e
 if op==1:
  move(a,f)
  if b!=n:move(b,f)
  else:assert active is not None and f==zero
  assert state[a]==state[b]==f;out.append(e)
 elif op==2:assert active is None;move(a,c);active=a;state[n]=f;hist[z]+=1;out.append(e)
 else:assert op==3 and active==a and state[a]==c and state[n]==f==zero;active=None;del state[n];out.append(e)
for a,f in sorted(fin.items()):move(a,f)
assert state==fin and active is None;raw=b''.join(struct.pack('<6i',*e)for e in out);(O/'records.bin').write_bytes(raw);write(O/'meta.json',dict(m,raw_sha256=sha(raw)));write(O/'frames.json',frames);write(O/'initial.json',ini);write(O/'final.json',fin);(O/'regs.json').write_bytes((D/'regs.json').read_bytes());(O/'labels.json').write_bytes(opts.labels.read_bytes());before=read(D/'physical.json')['paid_histogram'];delta=Counter(hist);delta.subtract({int(k):v for k,v in before.items()});write(O/'physical.json',dict(paid_histogram=dict(hist),paid_rank_mass=sum(k*v for k,v in hist.items()),category_names=[],independent_dirty_registers=n-2*v));rec=dict(status='OWN_LITERAL_DELTA_RECONSTRUCTED_WARM_CACHE_MATERIALIZED',source_sha=m['raw_sha256'],changed_sha=sha(raw),stream=r,pivot=p,targets=S,source=src,correction=q,early_write=early[0],source_update=updates[0],cut_after=entry,recovery_frame=recovery,recovery_rank=5,first_frame=firstframe,first_rank=3,root_frame=root,root_rank=frames[str(root)]['dim'],redirected_writes=later,deleted_cleanup=cln,deleted_deliveries=roots,kept_initial_dirty_reads=dirty,category_names={94:'warm_setup',95:'warm_feed',96:'warm_redirect',97:'warm_restore_current',98:'warm_restore_correction',99:'warm_scatter'},exact_current_minus_correction_equals_historical_source=True,no_kernel_pivot_or_donor_overlap=True,old_mass=sum(int(k)*v for k,v in before.items()),new_mass=sum(k*v for k,v in hist.items()),paid_histogram_delta={k:v for k,v in delta.items()if v},new_ADDs=sum(e[0]==1 for e in out),all_nested_moves=True,scope='Literal paid word/chronology only; complete signed,F2,operand source,bank,finite price require admission.');write(opts.receipt,rec);print(json.dumps(rec))
