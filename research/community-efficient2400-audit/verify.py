from pathlib import Path
import json,subprocess,hashlib
P=Path('/tmp/pr-efficient2400');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def tree(head):
 out={}
 for rec in git('ls-tree','-r','-z',head).split(b'\0'):
  if rec:
   meta,name=rec.split(b'\t',1);mode,kind,oid=meta.decode().split();out[name.decode()]=dict(mode=mode,kind=kind,oid=oid)
 return out
base=json.loads((P/'selection.json').read_text())['baseline'];current=tree('HEAD');rows=[x for x in json.loads((P/'INTAKE.json').read_text())['pull_requests'] if x['status']=='archive_ready'];count=0
for x in rows:
 git('merge-base','--is-ancestor',x['head'],'HEAD');pk=json.loads((P/'packets'/f'{x["number"]}.json').read_text());t=tree(x['head']) if x['archive_mode']=='historical_source_snapshot' else current
 for f in pk['files']:assert f['source']==t.get(f['path']),(x['number'],f['path']);count+=1
for p in ('certificates/selected-result.json','.gitattributes'):assert git('show',base+':'+p)==git('show','HEAD:'+p)
# Prior scientific packages and workflows must be unchanged by this round.
changed=set(git('diff','--name-only','--no-renames','-z',base,'HEAD').decode().split('\0'))-{''}
allowed={'CONTRIBUTORS.md','scripts/reconcile_pr_queue.py','scripts/verify_pr_reconciliation.py','docs/research/research-archive-intake.md','docs/research/pr-ledger.json','docs/research/pr-ledger.md','docs/research/pr-queue-next-actions.md'}
allowed|={f'research/community-efficient{b}-audit/INTEGRATION-RESOLUTIONS.json' for b in (1600,1700,1800,1900)}
for x in rows:
 if x['archive_mode']=='default_tree_archive':allowed|={f['path'] for f in json.loads((P/'packets'/f'{x["number"]}.json').read_text())['files']}
assert all(p in allowed or p.startswith('research/community-efficient2400-audit/') for p in changed),sorted(p for p in changed if p not in allowed and not p.startswith('research/community-efficient2400-audit/'))
res=dict(status='PASS',head=git('rev-parse','HEAD').decode().strip(),archives=len(rows),original_file_entries=count,historical=sum(x['archive_mode']=='historical_source_snapshot' for x in rows),scope='Exact source trees and ancestry, original blobs/modes, bounded active-tree changes, unchanged selected result and active attributes. No scientific replay.')
(P/'source-retention.json').write_text(json.dumps(res,indent=2)+'\n');print(res)
