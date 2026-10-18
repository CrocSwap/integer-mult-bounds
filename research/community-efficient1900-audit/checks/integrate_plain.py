import pathlib,json,subprocess,time,sys,hashlib
P=pathlib.Path('/tmp/pr-efficient1900');R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015')
def git(*args,check=True):return subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0',*args],cwd=R,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check)
def live(ns):
 q='query {repository(owner:"CrocSwap",name:"integer-mult-bounds") {'+' '.join(f'p{n}:pullRequest(number:{n})'+'{number headRefOid state isDraft mergedAt mergeCommit{oid}}'for n in ns)+'}}'
 return json.loads(subprocess.check_output(['gh','api','graphql','-f','query='+q],text=True))['data']['repository']
states=json.load(open(P/'integration-state.json'))if(P/'integration-state.json').exists()else{}
ready=json.load(open(P/'ready.json')); ns=[]
for n in ready:
 if str(n)in states:continue
 pk=json.load(open(P/'packets'/f'{n}.json'))
 if all(f['path'].startswith('research/')for f in pk['files']) or (n==2903 and all(f['path'].startswith('research/qq16-numerical-contract-navigation/') or f['path'] in ['docs/research/bottleneck-brief.md','docs/research/qq16-controller-scope-map.md','docs/research/qq16-numerical-contract-map.md'] for f in pk['files'])) or (n==2760 and all(f['path'].startswith('docs/research/') for f in pk['files'])) or (n==1075 and all(f['path'].startswith('research/cube-xor-replay/') or f['path']=='.github/workflows/cube-xor-replay.yml' for f in pk['files'])) or (n==1007 and all(f['path'].startswith('research/pr116-evidence-reconciliation/') or f['path'] in ['scripts/reconcile_pr_queue.py','docs/research/pr-ledger.json','docs/research/pr-ledger.md','tests/test_pr116_ledger_evidence.py'] for f in pk['files'])) or (n==1830 and all(f['path'].startswith(('research/h6-compensation-network/','research/h6-independent-audit/','research/h6-banked-breakeven/')) or f['path']=='.github/workflows/h6-compensation-network.yml' for f in pk['files'])):ns.append(n)
ns=ns[:40]
if not ns:sys.exit('No plain ready group')
obs=live(ns);label=f'{ns[0]}-{ns[-1]}';(P/f'premerge-{label}.json').write_text(json.dumps(obs,indent=2))
for n in ns:
 m=json.load(open(P/f'{n}.json'));v=obs['p'+str(n)];assert v['state']=='OPEN' and not v['isDraft'] and v['headRefOid']==m['headRefOid'],v
heads=[json.load(open(P/f'{n}.json'))['headRefOid']for n in ns]
mergehead=R/git('rev-parse','--git-path','MERGE_HEAD').stdout.strip()
if mergehead.exists():
 assert set(mergehead.read_text().splitlines())==set(heads)
else:
 assert not git('status','--porcelain').stdout, 'Commit reviewed audit changes before starting integration'
 a=git('merge','--no-ff','--no-commit',*heads,check=False);(P/f'merge-{label}.log').write_text(a.stdout+a.stderr);assert a.returncode==0,a.stdout+a.stderr
staged={}
for record in git('ls-files','--stage','-z').stdout.split('\0'):
 if record:
  meta,path=record.split('\t',1);fields=meta.split();assert fields[2]=='0', ('unmerged index',path);staged[path]=fields
for n in ns:
 for f in json.load(open(P/'packets'/f'{n}.json'))['files']:
  got=staged.get(f['path'],[]);v=f['source']
  resolution=next((r for r in json.load(open(P/'resolution-plan.json')) if r['number']==n and r['path']==f['path']),None)
  resolved=resolution is not None and got and hashlib.sha256(subprocess.check_output(['git','show',':'+f['path']],cwd=R)).hexdigest()==resolution['resolved_sha256']
  assert resolved or (not got if v is None else len(got)>=3 and got[0]==v['mode'] and got[1]==v['oid']),(n,f['path'],got,v)
# Apply only separately reviewed, tested integration resolutions.
import shutil
for resolution in json.load(open(P/'resolution-plan.json')):
 if resolution['number'] not in ns:continue
 rel=resolution['path'];src=P/'resolutions'/str(resolution['number'])/rel
 assert hashlib.sha256(src.read_bytes()).hexdigest()==resolution['resolved_sha256']
 dst=R/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 git('add','--sparse','--',rel)
 assert hashlib.sha256(subprocess.check_output(['git','show',':'+rel],cwd=R)).hexdigest()==resolution['resolved_sha256']
(R/'research/community-efficient1900-audit').mkdir(parents=True,exist_ok=True)
shutil.copy2(P/'resolution-plan.json',R/'research/community-efficient1900-audit/INTEGRATION-RESOLUTIONS.json')
git('add','--sparse','research/community-efficient1900-audit/INTEGRATION-RESOLUTIONS.json')
assert git('show',':certificates/selected-result.json').stdout==git('show','a7482490b4ca256db67d767a33fa6f7553060807:certificates/selected-result.json').stdout
whitespace_excludes=[':(exclude)research/a2-family-b-locus/checks/relax.py'] if 2830 in ns else []
if 2464 in ns:whitespace_excludes.append(':(exclude)research/z4-typed-echo-supplier-instance/TASK.json')
archives=json.load(open(P/'archive-intake.json')) if (P/'archive-intake.json').exists() else {}
for n in ns:
 if str(n) in archives:
  whitespace_excludes.extend(':(exclude)'+p+'/**' for p in archives[str(n)]['paths'])
# These author-original whitespace bytes are preserved; exact blobs/modes were verified above.
whitespace=git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':(exclude)research/community-efficient1900-audit/**',*whitespace_excludes,check=False)
assert whitespace.returncode==0, whitespace.stdout+whitespace.stderr
msg=P/f'message-{label}.txt';msg.write_text('Integrate research contributions '+', '.join('#'+str(n)for n in ns)+'\n\nOriginal authors and predecessor credit retained. Exact-head review tiers, source-only archival admissions, finite checks where performed, and open obligations are recorded in research/community-efficient1900-audit. No selected frontier change.\n')
a=git('commit','-F',str(msg));(P/f'commit-{label}.log').write_text(a.stdout)
git('fetch','origin','main');assert git('merge-base','--is-ancestor','origin/main','HEAD',check=False).returncode==0,'origin advanced; reconcile before push'
a=git('push','origin','HEAD:main');(P/f'push-{label}.log').write_text(a.stdout)
obs=live(ns)
for _ in range(12):
 if all(v['state']=='MERGED'for v in obs.values()):break
 time.sleep(2);obs=live(ns)
for n in ns:
 v=obs['p'+str(n)];assert v['state']=='MERGED',v;states[str(n)]=v
(P/'integration-state.json').write_text(json.dumps(states,indent=2)+'\n');print('Published',ns,'total',len(states),flush=True)
