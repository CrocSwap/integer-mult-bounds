import importlib.util,pathlib,json,hashlib,subprocess
P=pathlib.Path('/tmp/pr-efficient1300');R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015')
root=P/'sources/2263'; f=root/'research/r420-rref-production/verify.py'
s=importlib.util.spec_from_file_location('check2263',f);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
v.run_xcheck=lambda script:b'identical successful receipt'
result=v.check_temp_corruption_rejection()
if not result.get('rejected'):raise RuntimeError('Expected false-positive control not reproduced')
findings=[{'pr':2263,'finding':'False-positive negative control: successful identical checker output is caught as subprocess failure','returned':result}]
for n in [2263,2276]:
 root=P/'sources'/str(n);head=json.load(open(P/f'{n}.json'))['headRefOid']
 paths=['research/r420-rref-performance/SOURCES.json','research/r420-rref-performance/adapter.py']
 manifest=json.loads(subprocess.check_output(['git','show',head+':'+paths[0]],cwd=R))
 mismatches=[]
 for row in manifest['files']:
  if row['path']not in ['research/e8-bit-r420/code/xcheck.py','research/e8-bit-r420/code/mutants.py']:continue
  actual=hashlib.sha256(subprocess.check_output(['git','show',head+':'+row['path']],cwd=R)).hexdigest()
  if actual!=row['sha256']:mismatches.append({'path':row['path'],'expected':row['sha256'],'actual':actual})
 if not mismatches:raise RuntimeError('Expected executable pin mismatch absent')
 findings.append({'pr':n,'head':head,'finding':'Historical registered RREF adapter bind_sources rejects updated production source before execution','mismatches':mismatches})
(P/'combined-r420-regression.json').write_text(json.dumps(findings,indent=2)+'\n');print(json.dumps(findings,indent=2))
