import pathlib,json,subprocess,hashlib,re,posixpath,time,platform,sys
P=pathlib.Path('/tmp/pr-efficient1600');R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015');F=P/'navigation-fixture';info=json.load(open(P/'navigation-fixture.json'));base=info['base'];results=[];started=time.time()
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def blob(commit,path):return git('show',commit+':'+path)
def sha(data):return hashlib.sha256(data).hexdigest()
def checkpin(x,commit):
 data=blob(commit,x['path']);assert sha(data)==x['sha256'],x
 if 'git_blob' in x:assert git('rev-parse',commit+':'+x['path']).decode().strip()==x['git_blob'],x
 return dict(commit=commit,path=x['path'],sha256=sha(data))
log=P/'combined-navigation-check.log'
with log.open('w') as out:
 for pat in ['test_research_overlap*.py','test_research_onboarding.py']:
  cmd=['/tmp/pr-efficient200-venv/bin/python','-I','-B','-m','unittest','discover','-s','tests','-p',pat]
  out.write(repr(cmd)+'\n');out.flush();t=time.time();v=subprocess.run(cmd,cwd=F,stdout=out,stderr=subprocess.STDOUT,timeout=60);results.append(dict(command=cmd,exit_code=v.returncode,seconds=round(time.time()-t,3)));assert v.returncode==0
 pins=[]
 x=json.load(open(F/'docs/research/pr1048-correction-map.json'))
 for row in x['main_sources']+x['external_sources']:pins.append(checkpin(row,row['commit']))
 y=json.load(open(F/'docs/research/five-source-connector-scope-map.json'))
 assert sha(blob(y['base_commit'],'certificates/selected-result.json'))==y['selected_record_sha256']
 assert sha(blob(y['base_commit'],y['ledger']['path']))==y['ledger']['sha256']
 for row in y['sources']:pins.append(checkpin(row,y['base_commit']))
 ledger={r['number']:r for r in json.loads(blob(base,'docs/research/pr-ledger.json'))['pull_requests']}
 for row in y['sources']:
  actual=ledger[row['number']];assert actual['reviewed_head']==row['reviewed_head'] and actual['disposition']==row['disposition'],row
 for row in x['retained_dispositions']:
  actual=ledger[row['pr']];assert actual['reviewed_head']==row['reviewed_head'] and actual['disposition']==row['disposition'],row
 assert ledger[2562]['disposition']=='incorporated'
 links=[];p104=[]
 for rel in ['docs/research/p104-helper-lifetime-scope-map.md','docs/research/pr1048-correction-map.md','docs/research/five-source-connector-scope-map.md']:
  text=(F/rel).read_text()
  for ref in re.findall(r'\]\(([^\s)]+)\)',text):
   if re.match(r'^[a-z]+://',ref) or ref.startswith('#'):continue
   target=posixpath.normpath(posixpath.join(posixpath.dirname(rel),ref.split('#')[0]));assert (F/target).exists() or subprocess.run(['git','cat-file','-e',base+':'+target],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0,(rel,target)
   links.append(dict(source=rel,target=target))
  for commit,path in re.findall(r'https://github.com/CrocSwap/integer-mult-bounds/blob/([0-9a-f]{40})/([^\s)#]+)',text):
   data=blob(commit,path);pins.append(dict(commit=commit,path=path,sha256=sha(data)))
  if 'helper-lifetime' in rel:
   for n,head,pkg in re.findall(r'\| (\d+) \| `([0-9a-f]{40})` \| `([^`]+)` \|',text):
    actual=ledger[int(n)];assert actual['reviewed_head']==head
    p104.append(dict(number=int(n),head=head,disposition=actual['disposition'],package=pkg))
 out.write(json.dumps(dict(source_pins=pins,relative_links=links,p104_status=p104),indent=2)+'\n')
res=dict(status='PASS',base=base,heads={str(n):json.load(open(P/f'{n}.json'))['headRefOid']for n in info['prs']},commands=results,source_pin_checks=len(pins),local_link_checks=len(links),p104_status=p104,seconds=round(time.time()-started,3),environment=platform.platform(),fixture_sha256=info['files'],log_sha256=sha(log.read_bytes()),scope='Source/navigation review and combined opt-in closed-PR search regression tests. Historical source receipts retained; no historical scientific suite, full census, Lean kernel or selected supplier replay claimed.')
(P/'combined-navigation-check.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({k:res[k]for k in ['status','source_pin_checks','local_link_checks','seconds']}))
