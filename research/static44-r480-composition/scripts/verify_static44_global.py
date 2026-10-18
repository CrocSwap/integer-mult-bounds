"""Fresh global admission attempt for Dugongue PR541's static44 appendix.
Prepared for Rohan Arun with OpenAI Codex assistance. Inherited auditors are
unchanged PR531/535 code with their original authorship and notices.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,subprocess,sys,shutil,time,hashlib,os
R=Path(__file__).resolve().parent;O=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else R/'static44-global314-retry';assert not O.exists();O.mkdir();(O/'tmp').mkdir();P=R/'source531-review';S=R/'source535-review';L=O/'local';steps=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(O/'tmp'))
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def write(p,x):
 b=json.dumps(x,sort_keys=True,separators=(',',':')).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b+b'\n')
def run(name,script,*args):
 start=time.monotonic();cmd=[sys.executable,'-B',str(P/'code'/script),*map(str,args)]
 with (O/(name+'.log')).open('w')as f:r=subprocess.run(cmd,env=env,cwd=O,stdout=f,stderr=subprocess.STDOUT)
 step=dict(name=name,seconds=time.monotonic()-start,exit=r.returncode);steps.append(step);write(O/'STEPS.json',steps)
 if r.returncode:print((O/(name+'.log')).read_text());raise SystemExit(name+' failed')
 print('PASS',name,step['seconds'],flush=True)
run('scalar-frames','audit_and_transport.py','--raw',R/'static44-local314/FULL-WORD.json.gz','--routing',S/'evidence/local/CANONICAL-WORD.json.gz','--out',L)
run('local-programs','emit_local.py',L)
run('local-scalar','audit_local.py',L)
run('changed-phases','phases_delta.py','--local',L,'--baseline',S/'evidence/local','--compiler',P/'vendor/clifford')
run('residual-adapters','adapters_local.py',L/'CANONICAL-WORD.json.gz',L/'RESIDUAL-ADAPTERS.json',L/'LEMMA-A.json')
# Sort each call's existing slots by width. The new width inventory is
# componentwise no larger. Retain physical families, windows and call order;
# compact each pending interval after changing widths, preserving all roles.
can=read(L/'CANONICAL-WORD.json.gz');widths=[can['h']-len(can['frames'][f])for f in can['start'][2*can['v']:]]
roles=read(S/'inputs/OWNERS.json.gz');plan=read(S/'inputs/OWNER-PLAN.json');oldwidths=plan['baseline_widths'];assert all(a<=b for a,b in zip(sorted(widths),sorted(oldwidths)))
bycall=defaultdict(list)
for z in roles:bycall[z['stage'],z['replica']].append(z)
helpers=sorted(range(len(widths)),key=lambda h:(widths[h],h));changed=0
for zs in bycall.values():
 for h,z in zip(helpers,sorted(zs,key=lambda z:(z['width'],z['helper']))):
  assert widths[h]<=z['width'];changed+=h!=z['helper'] or widths[h]!=z['width'];z['helper']=h;z['width']=widths[h]
bybin=defaultdict(list)
for z in roles:bybin[z['child'],z['copy']].append(z)
for zs in bybin.values():
 offset=0
 for z in sorted(zs,key=lambda z:z['offset']):z['offset']=offset;offset+=z['width']
parent=read(S/'inputs/ROUND20-PARENT-TEMPLATE.json.gz');hist=Counter();checks=read(L/'LOCAL-CHECKS.json')
for c in parent['calls']:hist.update({int(k):v for k,v in checks[c['orientation']]['paid_profile'].items()})
for child in parent['idle_children']:
 for replica in range(8):
  used=sum(z['width']for z in bybin[child['child'],replica*can['v']+child['port']]);left=child['rank']-used;assert left>=0
  if left:hist[left]+=1
assert 73*7168-sum(k*v for k,v in hist.items())==2560
roles.sort(key=lambda z:(z['time'],z['helper']))
plan.update(baseline_widths=widths,profile=dict(sorted(hist.items())),local_word='static44-local314/FULL-WORD.json.gz',status='FROZEN_SLOT_REASSIGNMENT_PENDING_AUDIT');write(O/'OWNERS.json.gz',roles);write(O/'PLAN.json',plan);write(O/'REPACK.json',dict(changed_roles=changed,profile=dict(sorted(hist.items())),width_inventory=dict(Counter(widths)),method='Within each complete call, monotone width matching to old physical roles; compact each actual pending interval without altering owner windows.'))
controller=O/'controller';shutil.copytree(P/'inputs/data-base',controller);shutil.copyfile(S/'inputs/ROUND20-PARENT-TEMPLATE.json.gz',controller/'split-centres/GLOBAL-TEMPLATE.json.gz');shutil.copyfile(P/'evidence/local/CANONICAL-WORD.json.gz',controller/'split-centres/CANONICAL-WORD.json.gz')
run('controller-binding','prepare_supplier_base.py','--data-base',controller,'--local',L,'--out',O/'base')
run('emit-owners','emit_supplier_hosted.py','--base',O/'base','--owners',O/'OWNERS.json.gz','--plan',O/'PLAN.json','--out',O/'hosted')
A=O/'audit';A.mkdir();run('independent-owners','audit_supplier_hosted.py',O/'base',O/'hosted',A/'ASYNC-AUDIT.json','--mutation-controls')
run('fresh-invoice','invoice_final.py','--base',O/'base','--hosted',O/'hosted','--audit',A,'--out',A,'--retained-invoice',P/'evidence/audit/PREFIX-AND-INVOICE.json')
write(O/'RESULT.json',dict(status='PASS_FRESH_STATIC44_GLOBAL_FINITE_ADMISSION_PRICING_PENDING',steps=steps,profile=dict(sorted(hist.items())),scope='Fresh changed complex local frames, scalar, changed phase edges, normalization, whole owners and finite invoice. Pinned unchanged phase/data dependencies reused; all-size assumptions conditional. No new kappa certified in this driver.'))
print('PASS full finite admission; exact combined pricing next',flush=True)
