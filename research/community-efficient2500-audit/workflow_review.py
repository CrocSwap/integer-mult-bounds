from pathlib import Path
import json,subprocess,re,hashlib,copy
P=Path('/tmp/pr-efficient2500');rows=json.loads((P/'workflows.json').read_text());pins=json.loads((P/'action-pins.json').read_text());ready={x['number'] for x in json.loads((P/'INTAKE.json').read_text())['pull_requests'] if x['status']=='archive_ready'}
rows=[x for x in rows if x['number'] in ready]
def parse(raws):
 return json.loads(subprocess.check_output(['ruby','-r','yaml','-r','json','-e','puts JSON.generate(JSON.parse(STDIN.read).map { |x| YAML.safe_load(x) })'],input=json.dumps(raws).encode()))
original=parse([x['source'] for x in rows]);out=[];resolved=[]
(P/'original-workflows').mkdir(exist_ok=True);(P/'resolved-workflows').mkdir(exist_ok=True)
for x,obj in zip(rows,original):
 assert obj['permissions']=={'contents':'read'} and 'concurrency' not in obj and 'env' not in obj
 assert set(obj.get('true',{}))<= {'workflow_dispatch','push','pull_request'}
 assert 'secrets.' not in x['source'] and 'pull_request_target' not in x['source'] and 'workflow_run' not in x['source']
 text=x['source'];text,n=re.subn(r'(?ms)^on:\s*\n.*?(?=^[A-Za-z][A-Za-z0-9_-]*:)','on:\n  workflow_dispatch:\n\n',text,count=1);assert n==1
 text=text.replace('jobs:\n','concurrency:\n  group: research-archive-replay\n  cancel-in-progress: false\n\njobs:\n',1)
 for old,pin in pins.items():text=text.replace(old,pin['resolved'])
 for jobid,job in obj['jobs'].items():
  assert job['runs-on'] in ('ubuntu-latest','ubuntu-24.04') and 'permissions' not in job and 'container' not in job and 'services' not in job
  if 'timeout-minutes' not in job:
   needle='  '+jobid+':\n';assert text.count(needle)==1;text=text.replace(needle,needle+'    timeout-minutes: 30\n')
  else:assert 1<=job['timeout-minutes']<=120
  if 'strategy' in job:
   assert set(job['strategy'])<={'matrix','fail-fast'}
 text=text.replace('    strategy:\n','    strategy:\n      max-parallel: 1\n')
 text=re.sub(r'(?m)^(      - uses: actions/checkout@[^\n]+\n)(?!        with:)',r'\1        with:\n          persist-credentials: false\n',text)
 text='# Manual research replay; archival intake is not scientific validation.\n# See docs/research/research-archive-intake.md before dispatching.\n'+text
 name=Path(x['path']).name;(P/'original-workflows'/name).write_text(x['source']);(P/'resolved-workflows'/name).write_text(text);resolved.append(text)
 out.append(dict(number=x['number'],head=x['head'],path=x['path'],original_sha256=x['sha256'],resolved_sha256=hashlib.sha256(text.encode()).hexdigest(),scope='Manual-only trigger, read-only token, no persisted checkout credentials, immutable action refs, global replay concurrency and serial matrix legs; existing commands preserved. No job executed.'))
parsed=parse(resolved);shell_checks=0
for old,new,x in zip(original,parsed,out):
 assert set(new['true'])=={'workflow_dispatch'} and new['permissions']=={'contents':'read'} and new['concurrency']=={'group':'research-archive-replay','cancel-in-progress':False}
 expected=copy.deepcopy(old['jobs'])
 for job in expected.values():
  job.setdefault('timeout-minutes',30)
  if 'strategy' in job:job['strategy']['max-parallel']=1
  for step in job['steps']:
   if 'uses' in step:
    step['uses']=pins.get(step['uses'],{}).get('resolved',step['uses'])
    assert re.fullmatch(r'actions/(checkout|setup-python|upload-artifact)@[a-f0-9]{40}',step['uses'])
    if step['uses'].startswith('actions/checkout@'):step.setdefault('with',{})['persist-credentials']=False
   if 'run' in step:
    shell=re.sub(r'\$\{\{.*?\}\}','REVIEW_VALUE',step['run']);subprocess.run(['bash','-n'],input=shell.encode(),check=True,capture_output=True);shell_checks+=1
 assert expected==new['jobs'],x['number']
(P/'WORKFLOW-RESOLUTIONS.json').write_text(json.dumps(dict(status='PASS',workflows=out,shell_blocks_syntax_checked=shell_checks,scope='Configuration and shell syntax only, exact job-body equivalence modulo documented controls. Does not verify dependency availability or scientific execution. Shared concurrency permits one active and one pending run; later pending dispatches can replace earlier ones. Dispatch deliberately, one at a time.'),indent=2)+'\n')
print('Reviewed',len(out),'manual-only workflows;',shell_checks,'shell blocks parsed without execution.')
