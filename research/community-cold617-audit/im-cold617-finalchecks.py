from pathlib import Path
import json,hashlib,subprocess,time,sys
r=Path('/tmp/integer-mult-family588');w=Path('/tmp/im-cold617-replay');py='/tmp/integer-mult-review-venv/bin/python'
prs=[600,601,603,604,607,608,609,610,614,615,616,617]
def wait(p):
 deadline=time.time()+7200
 while not p.exists():
  if time.time()>deadline:raise RuntimeError('Timeout '+str(p))
  time.sleep(4)
def run(label,args):
 print('RUN',label,flush=True)
 with (w/(label+'.log')).open('w')as f:subprocess.run([py,'-B',*map(str,args)],cwd=r,stdout=f,stderr=subprocess.STDOUT,check=True)
 print('PASS',label,flush=True)
for n,e,c in [(604,46,14),(615,48,14),(617,48,28)]:
 d=w/f'pr{n}';wait(d/'RECEIPT.json');spec=json.load(open(Path(json.load(open('/tmp/im-cold617-packages.json'))[str(n)])/'data/SPEC.json'))
 run(f'interface{n}',[r/'scripts/verify_cold617_interface.py',*[d/(x+'-local')for x in spec['build']['providers']],'--entering',e,'--cold',c,'--out',d/'INTERFACE.json'])
wait(w/'pr616/RECEIPT.json')
run('owner616',[r/'research/complex-cold-owner-repair/code/check_owner_map.py','--work',w/'pr616','--provider','atm3='+str(w/'pr604/atm3-local'),'--provider','jp8='+str(w/'pr604/jp8-local'),'--out',w/'pr616/INDEPENDENT-OWNER.json'])
# Verify exactly the retained source inventory and retained bit execution artifacts.
manifest=json.load(open(r/'research/community-hyperplane599-audit/SELECTED-SOURCE.json'))
for rel,h in manifest['files'].items():assert hashlib.sha256((r/rel).read_bytes()).hexdigest()==h,rel
old=json.load(open(r/'research/community-hyperplane599-audit/COMPLETED-EVIDENCE.json'))
bit=[x for x in old if x.get('name')=='fresh-selected-bit'];assert len(bit)==1
for rel,h in bit[0]['files'].items():
 q=Path('/tmp/im599-bit543')/str(Path(rel).relative_to('research/community-hyperplane599-audit/bit543'))
 assert hashlib.sha256(q.read_bytes()).hexdigest()==h,rel
(w/'BIT-REUSE.json').write_text(json.dumps({'status':'PASS_UNCHANGED_BIT_SOURCE_AND_REPLAY_HASHES','previous_evidence':'research/community-hyperplane599-audit/COMPLETED-EVIDENCE.json','files_verified':len(bit[0]['files']),'note':'This round reuses the preceding unchanged bit replay; public cold runner rebuilds it.'},indent=2)+'\n')
run('composition617',[r/'scripts/verify_frontier617_bindings.py','--bit','/tmp/im599-bit543','--complex',w/'pr617','--out',w/'pr617/COMPOSITION.json'])
verified=[]
for n in prs:
 d=w/f'pr{n}';wait(d/'RECEIPT.json');rec=json.load(open(d/'RECEIPT.json'))
 for st in rec['steps']:
  assert st['exit_code']==0,(n,st)
  assert hashlib.sha256((d/(st['name']+'.log')).read_bytes()).hexdigest()==st['log_sha256'],(n,st['name'])
 for rel,h in rec['artifacts'].items():assert hashlib.sha256((d/rel).read_bytes()).hexdigest()==h,(n,rel)
 verified.append({'pr':n,'status':rec['status'],'steps':len(rec['steps']),'pinned_artifacts':len(rec['artifacts']),'result':json.load(open(d/'RESULT.json'))})
(w/'VERIFIED.json').write_text(json.dumps(verified,indent=2)+'\n');print('PASS_ALL_CONSTRUCTION_RECEIPTS',flush=True)
