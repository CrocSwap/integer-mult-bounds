from pathlib import Path
from collections import Counter
import json,sys
import hosting_core as HC
P=Path(__file__).resolve().parent;ROOT=P.parents[3];S=P/'local'
st=json.loads((S/'records/249-states.json').read_text());fs=json.loads((S/'records/frames.json').read_text())['frames']
width=[8-fs[str(st['initial'][str(h)])]['dim']for h in range(240,980)]
schedule=[dict(kind='local',stage=0,pair=0)];idx=0
for j in range(5):
 s=2*j+1;schedule.append(dict(kind='local',stage=s,pair=j))
 if j<4:
  schedule.append(dict(kind='idle',idx=idx,pair=j+1,rank=14*(j+1),source_level=-1,target_level=s));idx+=1
  schedule.append(dict(kind='bridge',dst=j,src=j+1))
 s+=1;schedule.append(dict(kind='local',stage=s,pair=j))
 if j<4:
  schedule.append(dict(kind='idle',idx=idx,pair=j+1,rank=7,source_level=s-1,target_level=s));idx+=1
  schedule.append(dict(kind='bridge',dst=j,src=j+1))
 else:
  for p in range(5):
   schedule.append(dict(kind='idle',idx=idx,pair=p,rank=7*(10-(2*p+2)),source_level=2*p+2,target_level=10));idx+=1
for j in reversed(range(4)):schedule.append(dict(kind='bridge',dst=j+1,src=j))
schedule.append(dict(kind='exchange'))
win={i:w for i,w in HC.windows(schedule).items()if w[1]and w[2]}
avail=Counter((s,w)for s in range(11)for w in width*8)
if '--replay'not in sys.argv:
 ys,zs,val=HC.solve(win,1920,dict(avail),78,group={w:10000 for w in set(width)})
 HC.save_selection(P/'HOSTING-SELECTION.json','bit',ys,zs,val)
ys,zs,val=HC.load_selection(P/'HOSTING-SELECTION.json','bit');slots,rem=HC.expand(win,ys,zs,{s:list(enumerate(width*8))for s in range(11)},1920)
assert len(slots)==65120 and len({(s,h)for i,c,o,w,s,h in slots})==65120
base=json.loads((P/'LOCAL-SUMMARY.json').read_text())['local_profile'];base={int(k):v for k,v in base.items()};paid=Counter({r:n*88 for r,n in base.items()})
for r in rem.values():
 if r:paid[r]+=1
mass=sum(r*n for r,n in paid.items());assert 78*9600-mass==3264
report=dict(status='OWN_SIGNED60_WHOLE_OWNER_POOL_ELEVEN_STAGE_PROFILE_NOMINATION',width_inventory=dict(Counter(width)),m=78,L=11,K=5,T=8,live=9600,physical=9609,hosted_residuals=65120,bank_assignments=0,profile=dict(sorted(paid.items())),rankmass=mass,deficit=3264,maxchild=max(paid),local_invocations=88,schedule=schedule,windows={str(i):[p,r,sorted(ss)]for i,(p,r,ss)in win.items()},slots=slots,explicit_slot_format="idle, physical_cp=ownerrep*240+sideport, offset,width,stage, logicalhelper=invocationrep*740+helper",remainder_profile=dict(Counter(rem.values())),scope='Exact assignment/count/profile screen only. Requires emitted template, actual sigma/operator, signed dirt/inverse/global prefix and full invoice gates.')
(P/'NOMINATION.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items()if k not in('slots','schedule','windows')})
