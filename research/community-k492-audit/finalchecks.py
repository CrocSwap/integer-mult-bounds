from pathlib import Path
import json,hashlib,subprocess,time,sys
r=Path('/tmp/integer-mult-family588');w=Path('/tmp/im-k492-replay');py='/tmp/integer-mult-review-venv/bin/python';packages=json.load(open('/tmp/im-k492-packages.json'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wait(p):
 end=time.monotonic()+1800
 while not p.exists():
  if time.monotonic()>end:raise RuntimeError('Timeout '+str(p))
  time.sleep(5)
# Unchanged supplier provenance, not a new bit replay.
m=json.load(open(r/'research/community-cold617-audit/SELECTED-SOURCE.json'))
for rel,h in m['files'].items():assert sha(r/rel)==h,rel
old=json.load(open(r/'research/community-hyperplane599-audit/COMPLETED-EVIDENCE.json'))
bit=next(x for x in old if x.get('name')=='fresh-selected-bit')
for rel,h in bit['files'].items():
 p=Path('/tmp/im599-bit543')/Path(rel).relative_to('research/community-hyperplane599-audit/bit543');assert sha(p)==h,rel
(w/'BIT-REUSE.json').write_text(json.dumps(dict(status='PASS_UNCHANGED_BIT_SOURCE_AND_REPLAY_HASHES',source_inventory='research/community-cold617-audit/SELECTED-SOURCE.json',previous_evidence='research/community-hyperplane599-audit/COMPLETED-EVIDENCE.json',files_verified=4,scope='Reuses the preceding checked bit replay; public runner rebuilds it.'),indent=2)+'\n')
wait(w/'pr626/RECEIPT.json')
with (w/'composition626.log').open('w')as f:subprocess.run([py,'-B',str(r/'scripts/verify_frontier626_bindings.py'),'--bit','/tmp/im599-bit543','--complex',str(w/'pr626'),'--out',str(w/'pr626/COMPOSITION.json')],stdout=f,stderr=subprocess.STDOUT,check=True)
verified=[]
for n in [618,619,622,623,624,625,626]:
 d=w/f'pr{n}';wait(d/'RECEIPT.json');rec=json.load(open(d/'RECEIPT.json'));spec=json.load(open(Path(packages[str(n)])/'data/SPEC.json'))
 assert rec['manifest_sha256']==sha(Path(packages[str(n)])/'MANIFEST.json')
 assert rec['spec_sha256']==sha(Path(packages[str(n)])/'data/SPEC.json')
 for st in rec['steps']:assert st['exit_code']==0 and sha(d/(st['name']+'.log'))==st['log_sha256'],(n,st['name'])
 for rel,h in rec['artifacts'].items():assert sha(d/rel)==h,(n,rel)
 z=json.load(open(d/'RESULT.json'));assert z['kappa']==spec['expected']['kappa']
 verified.append(dict(pr=n,status=rec['status'],steps=len(rec['steps']),pinned_artifacts=len(rec['artifacts']),result=z))
(w/'VERIFIED.json').write_text(json.dumps(verified,indent=2)+'\n');print('PASS_ALL_CONSTRUCTION_RECEIPTS',flush=True)
