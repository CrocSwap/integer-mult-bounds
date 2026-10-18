from pathlib import Path
import json,hashlib,shutil,sys
src=Path(sys.argv[1]);dst=Path(sys.argv[2]);meta=Path(sys.argv[3]);dst.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());files=set();records=[]
for sub in ('','ancestral558'):
 root=src/sub;receipt=read(root/'RECEIPT.json');st=read(root/'STAGES.json');assert receipt.get('stages',receipt.get('steps'))==st
 for s in st:
  log=root/(s['name']+'.log');assert s['exit_code']==0 and sha(log)==s['log_sha256'];files.add(log.relative_to(src).as_posix())
 for rel,h in receipt['artifacts'].items():
  p=root/rel;assert sha(p)==h,rel;files.add(p.relative_to(src).as_posix())
 for name in ('RECEIPT.json','STAGES.json'):files.add((root/name).relative_to(src).as_posix())
 records.append(dict(directory=sub,stages=len(st),artifacts=len(receipt['artifacts']),receipt_sha256=sha(root/'RECEIPT.json')))
for sub,table,label in [('global-replay','STAGES.json','name'),('gauge44','STEPS.json','step'),('layered66','STEPS.json','step'),('notri56','STEPS.json','step'),('notri-control','STEPS.json','step')]:
 root=src/sub
 for s in read(root/table):
  log=root/(s[label]+'.log');assert s['exit_code']==0
  if 'log_sha256'in s:assert sha(log)==s['log_sha256']
  files.add(log.relative_to(src).as_posix())
 files.add((root/table).relative_to(src).as_posix())
for rel in files:
 p=dst/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/rel,p)
for rel in ('PROCESS.json','TERMINAL.json','PLATFORM.json'):
 if(meta/rel).is_file():shutil.copy2(meta/rel,dst/rel)
assert read(dst/'TERMINAL.json')['exit_code']==0
result=dict(status='PASS_TOP_LEVEL_ANCESTRAL_GLOBAL_AND_CONSTRUCTION_RECEIPT_HASHES',records=records,terminal=read(dst/'TERMINAL.json'),files={rel:sha(dst/rel)for rel in sorted(files)})
(dst/'RECEIPT-CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(records,len(files))
