from pathlib import Path
import json,subprocess,time,hashlib
P=Path('/tmp/pr-efficient2100');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a):return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*a],cwd=R,stderr=subprocess.STDOUT)
rows=[x for x in json.loads((P/'INTAKE.json').read_text())['pull_requests'] if x['status']=='archive_ready'];ns=[x['number'] for x in rows];packets={n:json.loads((P/'packets'/f'{n}.json').read_text()) for n in ns};heads=[packets[n]['head'] for n in ns]
def live():
 result={}
 for i in range(0,len(ns),12):
  query='query {repository(owner:"CrocSwap",name:"integer-mult-bounds") {'+' '.join(f'p{n}:pullRequest(number:{n})'+'{number headRefOid state isDraft mergedAt mergeCommit{oid}}' for n in ns[i:i+12])+'}}'
  result.update(json.loads(subprocess.check_output(['gh','api','graphql','-f','query='+query]))['data']['repository'])
 return result
ob=live();(P/'premerge.json').write_text(json.dumps(ob,indent=2)+'\n')
for n in ns:assert ob['p'+str(n)]['state']=='OPEN' and not ob['p'+str(n)]['isDraft'] and ob['p'+str(n)]['headRefOid']==packets[n]['head']
allowed={f['path'] for pk in packets.values() for f in pk['files']}
for pk in packets.values():
 mb=git('merge-base','HEAD',pk['head']).decode().strip()
 actual=set(git('diff','--name-only','-z',mb,pk['head']).decode().split('\0'))-{''}
 assert actual<=allowed, ('unreviewed stacked dependencies',pk['number'],sorted(actual-allowed))
start=git('rev-parse','HEAD').decode().strip();mergehead=R/git('rev-parse','--git-path','MERGE_HEAD').decode().strip()
if mergehead.exists():assert set(mergehead.read_text().splitlines())==set(heads)
else:
 assert not git('status','--porcelain').strip()
 result=subprocess.run(['git','-c','gc.auto=0','merge','--no-ff','--no-commit',*heads],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (P/'merge.log').write_bytes(result.stdout)
 if result.returncode:print(result.stdout.decode()[-3000:]);result.check_returncode()
staged={}
for rec in git('ls-files','--stage','-z').split(b'\0'):
 if rec:
  meta,name=rec.split(b'\t',1);mode,oid,stage=meta.decode().split();assert stage=='0';staged[name.decode()]=(mode,oid)
expected={}
for pk in packets.values():
 for f in pk['files']:
  src=f['source'];assert staged[f['path']]==(src['mode'],src['oid']);expected[f['path']]=(src['mode'],src['oid'])
assert set(git('diff','--cached','--name-only','-z').decode().split('\0'))-{''}==set(expected),'Unexpected merge changes'
selected='certificates/selected-result.json';baseline=json.loads((P/'selection.json').read_text())['baseline'];assert git('show',':'+selected)==git('show',baseline+':'+selected)
msg=P/'message.txt';msg.write_text('Archive '+str(len(ns))+' research contributions with independent review still open\n\nOriginal authors and exact source bytes preserved. Source-only intake and all remaining scientific obligations recorded in research/community-efficient2100-audit. No selected frontier change.\n\nPRs: '+', '.join('#'+str(n) for n in ns)+'\n')
(P/'commit.log').write_bytes(git('commit','-F',str(msg)));git('fetch','origin','main');git('merge-base','--is-ancestor','origin/main','HEAD');(P/'push.log').write_bytes(git('push','origin','HEAD:main'))
ob=live()
for _ in range(6):
 if all(v['state']=='MERGED' for v in ob.values()):break
 time.sleep(2);ob=live()
assert all(v['state']=='MERGED' and v['headRefOid']==packets[v['number']]['head'] for v in ob.values()),ob
(P/'integration-state.json').write_text(json.dumps({str(v['number']):v for v in ob.values()},indent=2)+'\n');print('Published',len(ns),'archive PRs',flush=True)
