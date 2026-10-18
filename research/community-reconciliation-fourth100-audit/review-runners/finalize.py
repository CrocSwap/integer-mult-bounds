import json,subprocess,datetime,shutil,collections
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');A=R/'research/community-reconciliation-fourth100-audit';receipts=json.load(open(P/'closure-receipts.json'));assert len(receipts)==100
subprocess.run(['python3',str(P/'observe.py'),'ending-live.json'],check=True);observations=json.load(open(P/'ending-live.json'))['pull_requests'];obs={r['number']:r for r in observations};raw=json.load(open(A/'DISPOSITIONS.json'));by={r['number']:r for r in receipts}
for row in raw['pull_requests']:
 n=row['number'];r=by[n];o=obs[n];assert o['headRefOid']==r['observed']['headRefOid'];row['github_state']=o['state'];row['current_head']=o['headRefOid']
 if r['status']=='closed_after_published_review':
  assert o['state']=='CLOSED' and row['reviewed_head']==o['headRefOid'];row['closure']={**o,'comment_url':r['comment']['url'],'integration_commit':r['publication_commit']}
 elif r['status']=='retained_open':row['blocker_comment']=r['comment']['url'];assert o['state']=='OPEN' and row['closure']is None and row['disposition']=='partially_reviewed'
 elif r['status']=='changed_or_draft_keep_open':
  row['disposition']='changed_since_review';row['review_completion']['required_execution_complete']=False;row['unresolved_question']='Live head or draft state changed after the frozen review; reassess the new delta before closure.'
(A/'DISPOSITIONS.json').write_text(json.dumps(raw,indent=2)+'\n');shutil.copyfile(P/'closure-receipts.json',A/'CLOSURE-RECEIPTS.json')
counts=dict(collections.Counter(r['state']for r in observations));closed=sum(r['status']=='closed_after_published_review'for r in receipts);opens=[r['number']for r in observations if r['state']=='OPEN'];ending=dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='The frozen next100 only; not a live count of the entire PR queue.',counts=counts,closed_in_this_round=closed,open_remaining=opens,pull_requests=observations);(A/'ENDING-SNAPSHOT.json').write_text(json.dumps(ending,indent=2)+'\n')
shutil.copyfile(P/'ledger-check.txt',A/'LOCAL-VALIDATION.txt')
f=R/'docs/research/community-reconciliation-fourth100-review.md';s=f.read_text();marker='This round covers **100 non-draft PRs by 26 contributors**.';summary=f'\nThe final live check records **{closed} PRs closed in this round**, with **{len(opens)} retained open**: '+', '.join('#'+str(n)for n in opens)+'.\nSee the [closure receipts](../../research/community-reconciliation-fourth100-audit/CLOSURE-RECEIPTS.json) and [ending snapshot](../../research/community-reconciliation-fourth100-audit/ENDING-SNAPSHOT.json).\n';assert marker in s;s=s.replace(marker,marker+summary);f.write_text(s);print(ending['counts'],closed,opens)
