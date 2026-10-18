import json
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');groups=['local','local-repair','native','native-repair','inherited-ci','cold-retry','cold-parallel','gauge','quick','quick-retry','extra','report','serialization','post'];passed=set()
for group in groups:
 p=P/(group+'-execution.json')
 if p.exists():passed.update(x['number']for x in json.load(open(p))if x['exit_code']==0)
ci=set(map(int,json.load(open(P/'ci-selection.json'))));blocked={455,461,465,485,499};alln={r['number']for r in json.load(open(P/'snapshot.json'))['pull_requests']};ready=(passed|ci)-blocked;receipts=json.load(open(P/'closure-receipts.json'))if(P/'closure-receipts.json').exists()else[]
print(json.dumps(dict(completed_scoped_reviews=len(ready),closed=sum(x['status']=='closed_after_published_review'for x in receipts),remaining_executions=sorted(alln-ready-blocked),explicit_blockers=sorted(blocked)),indent=2))
for group in ['local-repair','inherited-ci','cold-retry','cold-parallel','gauge','extra']:
 p=P/(group+'-runner.log');print(group, p.read_text().splitlines()[-1] if p.exists()else 'not started')
