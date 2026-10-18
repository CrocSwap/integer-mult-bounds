"""Reconcile one authenticated GitHub metadata snapshot with the current ledger; no closure inference from titles."""
from pathlib import Path
import json,hashlib,collections
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015')
f=P/'live-after-twentynine.json';g=R/'docs/research/pr-ledger.json'
live=json.loads(f.read_text());ledger=json.loads(g.read_text());by={x['number']:x for x in ledger['pull_requests']};buckets=collections.defaultdict(list)
for row in live:
 n=row['number'];old=by.get(n)
 if row['isDraft']:key='draft'
 elif old is None:key='not_yet_in_ledger'
 elif old.get('reviewed_head')!=row['headRefOid']:key='head_differs_from_recorded_review'
 else:key=old['disposition']
 buckets[key].append(n)
assert sum(map(len,buckets.values()))==len(live)==len({x['number']for x in live})
out=dict(scope='Snapshot-only triage, not completion or authorization to close any PR. Includes the then-open PR801, integrated after this snapshot. Pending review obligations remain unchanged.',snapshot=f.name,snapshot_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),ledger_sha256=hashlib.sha256(g.read_bytes()).hexdigest(),open_count=len(live),non_draft_count=sum(not r['isDraft']for r in live),buckets={k:dict(count=len(v),prs=sorted(v))for k,v in sorted(buckets.items())})
(P/'finding-live-queue-coverage.json').write_text(json.dumps(out,indent=2)+'\n');print({k:len(v)for k,v in buckets.items()})
