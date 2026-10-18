from pathlib import Path
import json,subprocess,time
P=Path('/tmp/pr-efficient2600');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a,input=None):return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*a],cwd=R,input=input,stderr=subprocess.STDOUT)
rows=[x for x in json.loads((P/'INTAKE.json').read_text())['pull_requests'] if x['status'] in ('archive_ready','reviewed_ready')];ns=[x['number'] for x in rows];heads={x['number']:x['head'] for x in rows}
def live():
 query='query {repository(owner:"CrocSwap",name:"integer-mult-bounds") {'+' '.join(f'p{n}:pullRequest(number:{n})'+'{number headRefOid state isDraft mergeCommit{oid}}' for n in ns)+'}}'
 return json.loads(subprocess.check_output(['gh','api','graphql','-f','query='+query]))['data']['repository']
ob=live();(P/'premerge.json').write_text(json.dumps(ob,indent=2)+'\n')
for n in ns:assert ob['p'+str(n)]['headRefOid']==heads[n] and ob['p'+str(n)]['state']=='OPEN' and not ob['p'+str(n)]['isDraft']
assert not git('status','--porcelain').strip()
current={}
for rec in git('ls-tree','-r','-z','HEAD').split(b'\0'):
 if rec:
  meta,name=rec.split(b'\t',1);mode,kind,oid=meta.decode().split();current[name.decode()]=(mode,oid)
entries={}
for x in rows:
 pk=json.loads((P/'packets'/f'{x["number"]}.json').read_text());actual=set(git('diff','--name-only','--no-renames','-z',pk['merge_base'],pk['head']).decode().split('\0'))-{''};assert actual=={f['path'] for f in pk['files']}
 if x['archive_mode']=='historical_source_snapshot':continue
 for f in pk['files']:
  s=f['source'];assert s and s['mode'] in ('100644','100755');path=f['path'];entry=(s['mode'],s['oid'])
  if x['status']=='reviewed_ready':
   old=git('ls-tree',pk['merge_base'],'--',path).decode().split();baseline=(old[0],old[2]) if old else None;assert current.get(path)==baseline,('unreviewed concurrent change',x['number'],path)
  else:assert path.startswith('research/') and (path not in current or current[path]==entry)
  resolved=P/'resolutions'/str(x['number'])/path
  if resolved.exists():entry=(s['mode'],git('hash-object','-w','--stdin',input=resolved.read_bytes()).decode().strip())
  assert path not in entries or entries[path]==entry;entries[path]=entry
git('merge','-s','ours','--no-ff','--no-commit',*heads.values());git('update-index','-z','--index-info',input=b''.join((mode+' '+oid+'\t'+path+'\0').encode() for path,(mode,oid) in entries.items()));git('checkout-index','--force','--ignore-skip-worktree-bits','-z','--stdin',input=b''.join((p+'\0').encode() for p in entries))
changed=set(git('diff','--cached','--name-only','-z').decode().split('\0'))-{''};assert changed<=set(entries)
(P/'message.txt').write_text('Integrate replay correctness fixes, navigation and two research archives\n\nPR2958 fixes silently omitted replay inventory entries. PR2928 respects ordered main-branch exclusions. PR2945 updates physical-contract navigation with an explicit current archive-status resolution. PR2961 retains source-only research in the tree; PR2957 remains a historical source snapshot. Scientific claims are not newly validated; selected result unchanged. Scoped evidence and contributor credit are in research/community-efficient2600-audit.\n\nPRs: '+', '.join('#'+str(n) for n in ns)+'\n')
git('commit','-F',str(P/'message.txt'));subprocess.run(['python3',str(P/'verify.py')],check=True);git('fetch','origin','main');git('merge-base','--is-ancestor','origin/main','HEAD');git('push','origin','HEAD:main')
ob=live()
for _ in range(6):
 if all(v['state']=='MERGED' for v in ob.values()):break
 time.sleep(2);ob=live()
assert all(v['state']=='MERGED' and v['headRefOid']==heads[v['number']] for v in ob.values()),ob
(P/'integration-state.json').write_text(json.dumps({str(v['number']):v for v in ob.values()},indent=2)+'\n');print('Published',len(ns),'PRs')
