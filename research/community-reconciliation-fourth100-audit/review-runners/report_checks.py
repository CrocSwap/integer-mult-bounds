import json,subprocess,hashlib,time,gzip
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']};receipts=[];evidence=[]
for n,root,extra in [(594,'certificates/pr591-independent-replay',['certificates/frontier-20261012-591.json']),(611,'certificates/pr604-independent-replay',[])]:
 head=rows[n]['headRefOid'];paths=subprocess.check_output(['git','ls-tree','-r','--name-only',head,'--',root,*extra],cwd=R).decode().splitlines();files={}
 for path in paths:
  b=subprocess.check_output(['git','show',head+':'+path],cwd=R);assert b==(R/path).read_bytes(),path;files[path]=hashlib.sha256(b).hexdigest()
 details={'number':n,'head':head,'identical_already_integrated_files':files,'scope':'Fresh identity and internal consistency check of previously incorporated contributor report, not rerunning the reported original construction.'}
 if n==611:
  d=R/root;rec=json.load(open(d/'RECEIPT.json'));audit=json.load(open(d/'pr604-independent-audit.json'));result=json.load(open(d/'RESULT.json'))
  for name,key in [('RECEIPT.json','receipt_sha256'),('RESULT.json','result_sha256'),('ASSEMBLY.json','assembly_sha256')]:assert hashlib.sha256((d/name).read_bytes()).hexdigest()==audit[key]
  assert len(rec['steps'])==audit['top_level_stages']==55 and all(s['exit_code']==0 for s in rec['steps']);assert len(rec['artifacts'])==audit['receipt_artifacts']==54
  assert audit['result_status']==result['status'];details['internal_receipt_check']='55 successful recorded steps, 54 recorded artifact entries; actual shipped receipt/result/assembly hashes match. Full original logs are not shipped and are not claimed independently rehashed here.'
 else:
  obj=json.load(open(R/extra[0]));assert obj['pr']==591 and obj['replay']['top_level_stages']==49;assert obj['scope'] and obj['provenance'];details['internal_receipt_check']='Reported 49-stage fresh replay remains an attributed report; no full work tree is bundled. Previous maintainer review and retained independent audit remain the source of construction acceptance.'
 raw=(json.dumps(details,indent=2)+'\n').encode();log=P/f'pr{n}-report.txt';log.write_bytes(raw);receipts.append(dict(number=n,head=head,command=['python3',str(P/'report_checks.py')],exit_code=0,log=log.name,sha256=hashlib.sha256(raw).hexdigest(),scope=details['scope']));evidence.append(details)
(P/'report-execution.json').write_text(json.dumps(receipts,indent=2)+'\n');(P/'report-identity.json').write_text(json.dumps(evidence,indent=2)+'\n');print('PASS report identity and explicitly limited receipt consistency for 594,611')
