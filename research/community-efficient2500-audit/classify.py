from pathlib import Path
import json,subprocess,collections
P=Path('/tmp/pr-efficient2500');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
head=git('rev-parse','HEAD').decode().strip();tree={}
for rec in git('ls-tree','-r','-z',head).split(b'\0'):
 if rec:
  meta,path=rec.split(b'\t',1);mode,kind,oid=meta.decode().split();tree[path.decode()]=dict(mode=mode,kind=kind,oid=oid)
ledger={x['number']:x for x in json.loads((R/'docs/research/pr-ledger.json').read_text())['pull_requests']};packets={};decisions={}
for b in (1900,2000,2100,2200,2300,2400):
 p=Path(f'/tmp/pr-efficient{b}')
 for f in (p/'packets').glob('*.json'):packets[int(f.stem)]=json.loads(f.read_text())
 if (p/'INTAKE.json').exists():decisions.update({x['number']:x['status'] for x in json.loads((p/'INTAKE.json').read_text())['pull_requests']})
rows=[]
for m in json.loads((P/'live.json').read_text()):
 if m['isDraft']:continue
 n=m['number'];pk=packets.get(n);old=ledger.get(n,{});row=dict(number=n,head=m['headRefOid'],title=m['title'],remaining=old.get('unresolved_question'),prior_intake=decisions.get(n))
 if not pk:row['lane']='new_head'
 elif pk['head']!=m['headRefOid']:row['lane']='changed_head'
 else:
  different=[f for f in pk['files'] if f['source']!=tree.get(f['path'])];row['different_paths']=[f['path'] for f in different];row['source_packet']=next(str(Path(f'/tmp/pr-efficient{b}/packets/{n}.json')) for b in reversed((1900,2000,2100,2200,2300,2400)) if Path(f'/tmp/pr-efficient{b}/packets/{n}.json').exists())
  roots=sorted({f['path'] for f in different if not f['path'].startswith('research/')});row['nonresearch_differences']=roots
  if not different:
   mb=git('merge-base',head,pk['head']).decode().strip();actual=git('diff','--raw','--no-renames','--abbrev=40','-z',mb,pk['head']).split(b'\0');extra=[]
   for i in range(0,len(actual)-1,2):
    info=actual[i].decode().split();name=actual[i+1].decode();s=None if info[1]=='000000' else dict(mode=info[1],kind='blob',oid=info[3])
    if s!=tree.get(name):extra.append(name)
   row['lane']='already_present_exact' if not extra else 'stacked_dependencies';row['unretained_stack_paths']=extra
  elif row['prior_intake'] in ('held_known_correctness','held_intake_errors','held_unmerged_dependencies','held_unreviewed_stack','held_known_correctness_or_integrity'):row['lane']=row['prior_intake']
  elif not roots:row['lane']='research_versions_or_new_files'
  elif roots==['.gitattributes']:row['lane']='research_plus_attributes'
  elif all(x.startswith('.github/workflows/') for x in roots):row['lane']='research_plus_ci'
  else:row['lane']='shared_code_or_docs'
 rows.append(row)
result=dict(baseline=head,counts=dict(collections.Counter(x['lane'] for x in rows)),non_draft=len(rows),pull_requests=rows,scope='Next-action triage from exact current Git source identity and live heads. No mathematical validation or closure authorization inferred from category.')
(P/'QUEUE.json').write_text(json.dumps(result,indent=2)+'\n');print(result['counts'])
for x in rows:
 if x['lane'] in ('already_present_exact','research_plus_attributes','new_head','changed_head'):print(x['number'],x['lane'],x['title'][:80])
