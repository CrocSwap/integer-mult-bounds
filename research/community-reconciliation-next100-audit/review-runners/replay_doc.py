from pathlib import Path
import subprocess,time,json,hashlib
P=Path('/tmp/reconciliation-next100-20261013');row=next(r for r in json.load(open(P/'snapshot.json'))['pull_requests'] if r['number']==278);work=P/'doc278';pkg=work/'docs/multicut-delayed-inverse-checkpoint';cmd=[str(P/'doc-venv/bin/python'),'-B',str(pkg/'joint259_system_docs_incremental_test.py'),'--source',str(work/'research/multicut-delayed-inverse-checkpoint'),'--raster-dpi','40'];log=P/'pr278-doc.txt';start=time.monotonic()
with log.open('w') as f:ret=subprocess.run(cmd,cwd=pkg,stdout=f,stderr=subprocess.STDOUT).returncode
x=dict(number=278,head=row['headRefOid'],command=cmd,exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest());(P/'doc-execution.json').write_text(json.dumps([x],indent=2)+'\n');print(ret,x['seconds'])
