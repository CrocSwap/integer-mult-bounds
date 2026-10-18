import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'tests'))
import test_research_package_diagnostics as t
x=t.ResearchPackageDiagnosticTests();x.setUp()
try:
 r='docs/research/agent-task-catalog.json';p=x.root/r;c=json.loads(p.read_text());c['tracks'][0]['tasks'][0]['acceptance_gate']='Replacement gate from later head';p.write_text(json.dumps(c));t.package.git(x.root,'add',r);t.package.git(x.root,'-c','gc.auto=0','commit','-qm','later catalogue');head=t.package.git(x.root,'rev-parse','HEAD').decode().strip();sources=x.load('SOURCES.json');row=next(z for z in sources['files'] if z['path']==r);row.update(pin='head:'+head+':'+r,git_blob=t.package.git(x.root,'rev-parse',head+':'+r).decode().strip(),sha256=hashlib.sha256(p.read_bytes()).hexdigest());x.save('SOURCES.json',sources);task=x.load('TASK.json');task['original_card']=c['tracks'][0]['tasks'][0];x.save('TASK.json',task);result=x.run_cli();print(json.dumps(dict(base=x.base,later_head=head,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr)));assert result.returncode==0,'original proposal no longer exhibits catalogue override'
finally:x.doCleanups()
