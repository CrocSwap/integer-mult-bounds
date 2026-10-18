from pathlib import Path
import json,subprocess,time,hashlib
P=Path('/tmp/pr-efficient2300');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a, input=None):return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*a],cwd=R,stderr=subprocess.STDOUT,input=input)
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
 result=subprocess.run(['git','-c','gc.auto=0','merge','-s','ours','--no-ff','--no-commit',*heads],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (P/'merge.log').write_bytes(result.stdout)
 if result.returncode:print(result.stdout.decode()[-3000:]);result.check_returncode()
# Assemble the reviewed tree explicitly: exact research blobs plus the sole
# separately checked additive attributes resolution. Never import hidden changes.
resolution=json.loads((P/'ATTRIBUTE-RESOLUTION.json').read_text())
assert hashlib.sha256(git('show','HEAD:.gitattributes')).hexdigest()==resolution['baseline_sha256']
resolved=(P/'resolved.gitattributes').read_bytes();assert hashlib.sha256(resolved).hexdigest()==resolution['resolved_sha256']
controls=['README.md','scripts/reconcile_pr_queue.py','certificates/selected-result.json']
before_controls=git('check-attr','--cached','-z','text','whitespace','--',*controls)
entries={}
for pk in packets.values():
 for f in pk['files']:
  if f['path']=='.gitattributes':continue
  src=f['source'];assert src and src['mode'] in ('100644','100755') and f['path'].startswith('research/')
  assert f['baseline'] is None or f['baseline']==src, ('non-archival overwrite',f['path'])
  value=(src['mode'],src['oid'])
  assert f['path'] not in entries or entries[f['path']]==value
  entries[f['path']]=value
attrs_oid=git('hash-object','-w','--stdin',input=resolved).decode().strip();entries['.gitattributes']=('100644',attrs_oid)
index_data=b''.join((mode+' '+oid+'\t'+path+'\0').encode() for path,(mode,oid) in sorted(entries.items()))
git('update-index','-z','--index-info',input=index_data)
git('checkout-index','--force','--','.gitattributes')
git('checkout-index','--force','--ignore-skip-worktree-bits','-z','--stdin',input=b''.join((p+'\0').encode() for p in entries if p!='.gitattributes'))
assert before_controls==git('check-attr','--cached','-z','text','whitespace','--',*controls)
for line in resolution['added_rules']:
 fields=line.split();probe=fields[0][:-2]+'__archive_attribute_probe__'
 raw=git('check-attr','--cached','-z','text','whitespace','--',probe).decode().split('\0');values={raw[i+1]:raw[i+2] for i in range(0,len(raw)-1,3)}
 for setting in fields[1:]:
  key,expected=(setting[1:],'unset') if setting.startswith('-') else setting.split('=',1)
  assert values[key]==expected,(line,values)
(P/'attribute-check.json').write_text(json.dumps(dict(status='PASS',resolved_sha256=resolution['resolved_sha256'],controls=controls,rule_probes=len(resolution['added_rules']),scope='Narrow attribute rules take effect; unrelated control paths unchanged. Scientific bytes verified separately.'),indent=2)+'\n')
staged={}
for rec in git('ls-files','--stage','-z').split(b'\0'):
 if rec:
  meta,name=rec.split(b'\t',1);mode,oid,stage=meta.decode().split();assert stage=='0';staged[name.decode()]=(mode,oid)
expected={}
for pk in packets.values():
 for f in pk['files']:
  src=f['source'];wanted=('100644',attrs_oid) if f['path']=='.gitattributes' else (src['mode'],src['oid']);assert staged[f['path']]==wanted
  if f['source']!=f['baseline']:expected[f['path']]=wanted
assert set(git('diff','--cached','--name-only','-z').decode().split('\0'))-{''}==set(expected),'Unexpected merge changes'
selected='certificates/selected-result.json';baseline=json.loads((P/'selection.json').read_text())['baseline'];assert git('show',':'+selected)==git('show',baseline+':'+selected)
msg=P/'message.txt';msg.write_text('Archive '+str(len(ns))+' research contributions with independent review still open\n\nOriginal authors and exact research bytes preserved. The only resolution combines reviewed additive research-package attributes; original attribute files are retained in the audit. Source-only intake and all remaining scientific obligations recorded in research/community-efficient2300-audit. No selected frontier change.\n\nPRs: '+', '.join('#'+str(n) for n in ns)+'\n')
(P/'commit.log').write_bytes(git('commit','-F',str(msg)));git('fetch','origin','main');git('merge-base','--is-ancestor','origin/main','HEAD');(P/'push.log').write_bytes(git('push','origin','HEAD:main'))
ob=live()
for _ in range(6):
 if all(v['state']=='MERGED' for v in ob.values()):break
 time.sleep(2);ob=live()
assert all(v['state']=='MERGED' and v['headRefOid']==packets[v['number']]['head'] for v in ob.values()),ob
(P/'integration-state.json').write_text(json.dumps({str(v['number']):v for v in ob.values()},indent=2)+'\n');print('Published',len(ns),'archive PRs',flush=True)
