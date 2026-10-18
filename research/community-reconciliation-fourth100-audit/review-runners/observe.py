import json,subprocess,datetime,sys
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');rows=json.load(open(P/'snapshot.json'))['pull_requests'];out=[]
for off in range(0,100,25):
 fields=' '.join('p%d: pullRequest(number:%d) {number state isDraft headRefOid closedAt mergedAt url}'%(r['number'],r['number']) for r in rows[off:off+25]);q='query {repository(owner:"CrocSwap",name:"integer-mult-bounds") {'+fields+'}}';data=json.loads(subprocess.check_output(['gh','api','graphql','-f','query='+q],text=True));assert not data.get('errors');out.extend(data['data']['repository'].values())
(P/(sys.argv[1] if len(sys.argv)>1 else 'before-closure.json')).write_text(json.dumps(dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),pull_requests=out),indent=2)+'\n');by={r['number']:r for r in rows};print('observed',len(out),'changed',[(r['number'],r['headRefOid'])for r in out if r['headRefOid']!=by[r['number']]['headRefOid']],'already resolved',[r['number']for r in out if r['state']!='OPEN'])
