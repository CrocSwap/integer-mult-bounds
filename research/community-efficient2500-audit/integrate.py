from pathlib import Path
import json,subprocess,time
P=Path('/tmp/pr-efficient2500');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a,input=None):return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*a],cwd=R,input=input,stderr=subprocess.STDOUT)
rows=[x for x in json.loads((P/'INTAKE.json').read_text())['pull_requests'] if x['status']=='archive_ready'];ns=[x['number'] for x in rows];heads=[x['head'] for x in rows]
def live():
 out={}
 for i in range(0,len(ns),12):
  query='query {repository(owner:"CrocSwap",name:"integer-mult-bounds") {'+' '.join(f'p{n}:pullRequest(number:{n})'+'{number headRefOid state isDraft mergeCommit{oid}}' for n in ns[i:i+12])+'}}'
  out.update(json.loads(subprocess.check_output(['gh','api','graphql','-f','query='+query]))['data']['repository'])
 return out
ob=live();(P/'premerge.json').write_text(json.dumps(ob,indent=2)+'\n')
for x in rows:assert ob['p'+str(x['number'])]['headRefOid']==x['head'] and ob['p'+str(x['number'])]['state']=='OPEN' and not ob['p'+str(x['number'])]['isDraft']
assert not git('status','--porcelain').strip()
# Explicit historical archive merge: preserve every author commit as a parent,
# but do not replace default-tree versions or activate historical attributes.
git('merge','-s','ours','--no-ff','--no-commit',*heads)
entries={}
current={}
for rec in git('ls-tree','-r','-z','HEAD').split(b'\0'):
 if rec:
  meta,name=rec.split(b'\t',1);mode,kind,oid=meta.decode().split();current[name.decode()]=(mode,oid)
for x in rows:
 if x['archive_mode'] not in ('default_tree_archive','workflow_resolution'):continue
 pk=json.loads((P/'packets'/f'{x["number"]}.json').read_text())
 for f in pk['files']:
  s=f['source'];assert s and (f['path'].startswith('research/') or f['path'].startswith('.github/workflows/')) and s['mode'] in ('100644','100755')
  if f['path'].startswith('.github/workflows/'):
   assert f['path'] not in current
   content=(P/'resolved-workflows'/Path(f['path']).name).read_bytes();s=dict(s,oid=git('hash-object','-w','--stdin',input=content).decode().strip())
  entry=(s['mode'],s['oid']);assert f['path'] not in entries or entries[f['path']]==entry;entries[f['path']]=entry
  assert f['path'] not in current or current[f['path']]==entry,f['path']
git('update-index','-z','--index-info',input=b''.join((mode+' '+oid+'\t'+path+'\0').encode() for path,(mode,oid) in entries.items()))
git('checkout-index','--force','--ignore-skip-worktree-bits','-z','--stdin',input=b''.join((p+'\0').encode() for p in entries))
changed=set(git('diff','--cached','--name-only','-z').decode().split('\0'))-{''};assert changed<=set(entries)
(P/'message.txt').write_text('Archive research contributions with reviewed manual replay configurations\n\nResearch sources enter the default tree unchanged. Workflows are resolved to manual-only triggers, read-only permissions, immutable action refs and bounded concurrency. Original author workflows remain in the audit. No frozen package or selected result is replaced, and no replay is launched. Exact sources, contributor credit, archival mode and remaining scientific obligations are indexed in research/community-efficient2500-audit.\n\nPRs: '+', '.join('#'+str(n) for n in ns)+'\n')
git('commit','-F',str(P/'message.txt'));subprocess.run(['python3',str(P/'verify.py')],check=True)
git('fetch','origin','main');git('merge-base','--is-ancestor','origin/main','HEAD');git('push','origin','HEAD:main')
ob=live()
for _ in range(6):
 if all(v['state']=='MERGED' for v in ob.values()):break
 time.sleep(2);ob=live()
assert all(v['state']=='MERGED' and v['headRefOid'] in heads for v in ob.values()),ob
(P/'integration-state.json').write_text(json.dumps({str(v['number']):v for v in ob.values()},indent=2)+'\n');print('Published',len(ns),'archive PRs')
