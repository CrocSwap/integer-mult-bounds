from pathlib import Path
import json,subprocess
P=Path('/tmp/pr-efficient2300');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
observed=json.loads((P/'other-departures.json').read_text())['data']['repository'];records={}
for v in observed.values():
 n=v['number'];pk=json.loads((P/'packets'/f'{n}.json').read_text());assert v['state']=='MERGED' and v['headRefOid']==pk['head'];git('merge-base','--is-ancestor',pk['head'],'HEAD');tree={}
 for rec in git('ls-tree','-r','-z',pk['head']).split(b'\0'):
  if rec:
   meta,path=rec.split(b'\t',1);mode,kind,oid=meta.decode().split();tree[path.decode()]=dict(mode=mode,kind=kind,oid=oid)
 for f in pk['files']:assert tree.get(f['path'])==f['source']
 records[str(n)]=dict(observation=v,source_commit=pk['head'],changed_files=len(pk['files']),source_tree_url='https://github.com/CrocSwap/integer-mult-bounds/tree/'+pk['head'],scope='Historical ancestor archive only: exact source commit is reachable from main; default checkout is NOT claimed to equal this historical version. No mathematical or execution approval.')
(P/'ancestry-archives.json').write_text(json.dumps(records,indent=2)+'\n');print('PASS4ancestor source archives',sum(x['changed_files'] for x in records.values()),'fileentries')
p=P/'report.py';s=p.read_text();anchor="for name in ['selection.json'";assert anchor in s
block="""ancestors=json.loads((P/'ancestry-archives.json').read_text()) if (P/'ancestry-archives.json').exists() else {}
for row in rows:
 anc=ancestors.get(str(row['number']))
 if anc:
  row['github_state']='MERGED';row['integration_location']=[anc['source_tree_url']]
  row['closure']=dict(kind='merged_as_historical_ancestor',url='https://github.com/CrocSwap/integer-mult-bounds/pull/'+str(row['number']),merge_commit=anc['observation']['mergeCommit']['oid'])
  row['scope']=anc['scope'];row['review_completion']=dict(changed_file_coverage=True,scoped_mechanism_review=False,required_execution_complete=False,published=True)
  row['verification_evidence'].append('research/community-efficient2300-audit/ancestry-archives.json')
"""
s=s.replace(anchor,block+anchor,1).replace("'attribute-check.json']", "'attribute-check.json','ancestry-archives.json','other-departures.json','record_ancestors.py']")
s=s.replace('merged_for_archive=len(states)','merged_for_archive=len(states)+len(ancestors),historical_ancestors=len(ancestors)').replace('remaining_open=len(selection["prs"])-len(states)','remaining_open=len(selection["prs"])-len(states)-len(ancestors)').replace("str(len(states))","str(len(states)+len(ancestors))").replace("str(len(selection['prs'])-len(states))","str(len(selection['prs'])-len(states)-len(ancestors))")
s=s.replace("stage='Archived, not independently validated' if row['github_state']=='MERGED' else status[n]['status']", "stage=('Historical source commit only' if str(n) in ancestors else 'Archived, not independently validated') if row['github_state']=='MERGED' else status[n]['status']")
p.write_text(s);compile(s,str(p),'exec')
f=R/'CONTRIBUTORS.md';s=f.read_text();s+='\nHistorical predecessor versions automatically included through the above merge ancestry are retained at their immutable commits, with independent review still open:\n\n'
for n,a in records.items():
 m=json.loads((P/f'{n}.json').read_text());s+=f'- **{m["author"]["login"]}** — [#{n}]({m["url"]}), [exact historical sources]({a["source_tree_url"]}): {m["title"]}.\n'
f.write_text(s)
