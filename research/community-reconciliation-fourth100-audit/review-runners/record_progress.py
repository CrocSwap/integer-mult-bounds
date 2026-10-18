import json,datetime
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');A=R/'research/community-reconciliation-fourth100-audit';rec=json.load(open(P/'closure-receipts.json'));d=json.load(open(A/'DISPOSITIONS.json'));by={r['number']:r for r in d['pull_requests']}
for r in rec:
 row=by[r['number']];o=r['observed'];assert o['headRefOid']==row['reviewed_head'];row['current_head']=o['headRefOid'];row['github_state']=o['state']
 if r['status']=='closed_after_published_review':
  assert o['state']=='CLOSED' and row['disposition']=='incorporated';row['closure']={**o,'comment_url':r['comment']['url'],'integration_commit':r['publication_commit']}
 elif r['status']=='retained_open':row['blocker_comment']=r['comment']['url']
(A/'DISPOSITIONS.json').write_text(json.dumps(d,indent=2)+'\n');(A/'PROGRESS-CLOSURES.json').write_text(json.dumps(dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Completed subset of the frozen 100; remaining reviews continue.',receipts=rec),indent=2)+'\n');print('Recorded',len(rec),'GitHub outcomes')
