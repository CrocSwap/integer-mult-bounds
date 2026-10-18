import json,subprocess,pathlib,hashlib
R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015');P=pathlib.Path('/tmp/pr-efficient1300')
receipt=json.load(open(P/'sources/2046/research/merge5112-retention-receipt/RECEIPT.json'))
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
base,merge=receipt['base_commit'],receipt['merge_commit']
review={str(r['number']):r for r in json.loads(git('show',merge+':research/community-efficient800-audit/DISPOSITIONS.json'))['pull_requests']}
credits=git('show',merge+':CONTRIBUTORS.md').decode()
rows=[];total=0
for n,r in receipt['pull_requests'].items():
 q=review[n];assert r['head']==r['reviewed_head_recorded']==q['reviewed_head']==q['metadata']['headRefOid'];assert r['author']==q['metadata']['author']['login'];assert r['author'] in credits
 assert r['integration_location_recorded']==q['integration_location']
 changed=git('diff','--no-renames','--name-status',base+'...'+r['head']).decode().splitlines();assert all(l.startswith('A\t') for l in changed)
 paths=[l.split('\t')[1] for l in changed];assert paths==[x['path'] for x in r['changed_paths']]
 for path in paths:
  assert any(path.startswith(p+'/') for p in q['integration_location'])
  assert git('ls-tree',r['head'],'--',path)==git('ls-tree',merge,'--',path)
 total+=len(paths);rows.append({'number':int(n),'head':r['head'],'author':r['author'],'files':len(paths),'mode_and_blob':'identical'})
assert total==77 and len(rows)==9 and receipt['totals']['prs']==9 and receipt['totals']['changed_heads_vs_reviewed']==0
assert hashlib.sha256(git('show',merge+':certificates/selected-result.json')).hexdigest()==receipt['selected_record_sha256']
print(json.dumps({'status':'PASS','scope':'Independent supplemental historical review-head, author, path inventory, Git mode/blob and selected-hash verification; no scientific replay or fresh GitHub observation.', 'merge':merge,'prs':rows,'changed_files':total},indent=2))
