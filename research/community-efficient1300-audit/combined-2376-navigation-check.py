import pathlib,subprocess,json,re,posixpath,hashlib,time,platform
P=pathlib.Path('/tmp/pr-efficient1300');R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015'); n=2376
head=json.load(open(P/f'{n}.json'))['headRefOid']
def blob(ref):return subprocess.check_output(['git','show',ref],cwd=R)
paths=[f['path'] for f in json.load(open(P/'packets'/f'{n}.json'))['files']]
checked=[]
for path in paths:
 s=blob(head+':'+path).decode()
 for target in re.findall(r'\]\(([^)]+)\)|^\[[^]]+\]: (\S+)',s,re.M):
  url=next(x for x in target if x)
  if url.startswith(('http:', 'https:', '#')):continue
  rel=posixpath.normpath(posixpath.join(posixpath.dirname(path),url.split('#')[0]));blob(head+':'+rel);checked.append(rel)
s=blob(head+':docs/research/qq16-controller-scope-map.md').decode()
immutable=re.findall(r'https://github.com/[^/]+/integer-mult-bounds/blob/([0-9a-f]{40})/([^\s)]+)',s)
for h,path in immutable:blob(h+':'+path)
ledger=json.load(open(R/'docs/research/pr-ledger.json'))
# Record contemporaneous scientific dispositions without relabelling the author's dated source checkpoint.
rows=ledger.get('pull_requests',ledger.get('prs',[]))
if isinstance(rows,dict):rows=list(rows.values())
statuses={}
for n in [1969,2079,2093,2174,2346]:
 r=next((x for x in rows if x.get('number')==n),None)
 if r:statuses[str(n)]=r.get('disposition')
result={'status':'PASS','head':head,'local_links':checked,'immutable_sources':[{'head':h,'path':p}for h,p in immutable], 'current_ledger_statuses':statuses,'scope':'Navigation/source-link check and written claim-scope review. Historical pending labels refer to the explicitly dated author checkpoint; numbered packages have since been retained by maintainer rounds. Author predecessor-replay claims are not new maintainer executions. No supplier admission or kappa change.'}
(P/'combined-2376-navigation-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
