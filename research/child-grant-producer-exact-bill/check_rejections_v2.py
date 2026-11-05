from pathlib import Path
import json,hashlib,shutil,subprocess,datetime,time
S=Path('/private/tmp/contribution-batch-b11-20261104T1654Z/session-08');P=S/'BUILD';M=S/'MUTANT-v2';M.mkdir();PY='/Users/evaayala/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';cut=datetime.datetime.fromisoformat(json.loads((S/'CHECKPOINT.json').read_text())['science_cutoff']);original={f.relative_to(P).as_posix():f.read_bytes() for f in P.rglob('*') if f.is_file()};plans=[('drift_cases','CASES.json'),('drift_schema','SCHEMA.json'),('drift_pins','SOURCE-PINS.json'),('drift_source','source/producer.py'),('missing_source','source/inputs/PR6719/machine.py'),('manifest_omission','FILES.json'),('missing_certificate',None),('duplicate_key',None),('float_token',None),('nonfinite_token',None),('boolean_version',None),('boolean_row',None),('missing_case_row',None),('wrong_steps',None),('coherent_wrong_table',None),('false_control',None),('wrong_bound',None),('extra_field',None),('wrong_source_head',None),('wrong_small_witness',None)]
pre={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':[x[0] for x in plans],'first_suite':True,'actual_cli_rejections_expected':40,'complete_actual_certificates_under_test':True};(S/'REJECTION-v2-PRESEAL.json').write_text(json.dumps(pre,indent=2)+'\n');rows=[]
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode('ascii')
def restore():
 for name,data in original.items():
  f=M/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)

def expected(case,engine):
 if case.startswith('drift_'):return ['drift']
 if case in ('missing_source','missing_certificate'):return ['No such file']
 if case=='manifest_omission':return ['FILES']
 if case=='coherent_wrong_table':return ['one success HALT','certificate differs','single HALT','one halt','one success halt']
 if case=='duplicate_key':return ['duplicate JSON']
 if case in ('float_token','nonfinite_token'):return ['float or nonfinite']
 if case in ('boolean_version','boolean_row'):return ['proof integer']
 if case=='missing_case_row':return ['261 cases','all actual case rows']
 if case=='wrong_small_witness':return ['small witness values','certificate differs']
 if case=='wrong_bound':return ['bound coefficients','certificate differs']
 if case=='wrong_source_head':return ['certificate source','certificate differs']
 if case=='extra_field':return ['certificate exact keys']
 if case=='false_control':return ['Boolean']
 return ['certificate differs']
for case,target in plans:
 for engine,base in [('primary','CERTIFICATE.json'),('oracle','ORACLE.json')]:
  restore();artifact=M/'UNDER-TEST.json';raw=original[base];obj=json.loads(raw);artifact.write_bytes(raw)
  if case.startswith('drift_'):(M/target).write_bytes(original[target]+b'\n')
  elif case=='missing_source':(M/target).unlink()
  elif case=='manifest_omission':
   v=json.loads(original[target]);v['files'].pop();(M/target).write_text(json.dumps(v))
  elif case=='missing_certificate':artifact.unlink()
  elif case=='duplicate_key':artifact.write_bytes(b'{"schema_version":1,'+raw[1:])
  else:
   if case=='float_token':obj['schema_version']=1.0
   elif case=='nonfinite_token':obj['schema_version']=float('nan')
   elif case=='boolean_version':obj['schema_version']=True
   elif case=='boolean_row':obj['case_rows'][0]['steps']=True
   elif case=='missing_case_row':obj['case_rows'].pop()
   elif case=='wrong_steps':obj['case_rows'][0]['steps']+=1
   elif case=='coherent_wrong_table':
    table=obj['tables'][0];next(row for row in table['instructions'] if row[0]=='halt')[:]=['reject','external coherent table mutant'];obj['tables_sha256']=hashlib.sha256(canon(obj['tables'])).hexdigest()
   elif case=='false_control':obj['controls']['quotient_write_mutant']=False
   elif case=='wrong_bound':obj['bounds']['steps_per_S_plus_K']=1
   elif case=='extra_field':obj['unbound_extra']=0
   elif case=='wrong_source_head':obj['source_head']='0'*40
   elif case=='wrong_small_witness':obj['small_witness']['steps']-=1
   artifact.write_text(json.dumps(obj,sort_keys=True)+'\n')
  folder=S/'REJECTION-v2-INPUTS'/case/engine;folder.mkdir(parents=True)
  if artifact.exists():shutil.copyfile(artifact,folder/'UNDER-TEST.json')
  if target and (M/target).exists():shutil.copyfile(M/target,folder/Path(target).name)
  now=datetime.datetime.now(datetime.timezone.utc);remaining=(cut-now).total_seconds()
  if remaining<=0:raise SystemExit('Science cutoff reached; incomplete suite preserved')
  argv=[PY,'-I','-B',str(M/(engine+'.py')),'--certificate',str(artifact)];start=time.monotonic();q=subprocess.run(argv,cwd=M,capture_output=True,timeout=min(60,remaining));(folder/'stdout').write_bytes(q.stdout);(folder/'stderr').write_bytes(q.stderr);diag=q.stderr.decode(errors='replace');tokens=expected(case,engine);matched=any(t in diag for t in tokens);row={'case':case,'engine':engine,'argv':argv,'at':now.isoformat(),'exit':q.returncode,'wall_seconds':time.monotonic()-start,'expected_diagnostic':tokens,'diagnostic_matched':matched,'stdout_sha256':hashlib.sha256(q.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(q.stderr).hexdigest()};rows.append(row);(S/'REJECTION-v2-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n')
  if q.returncode==0 or not matched:
   (S/'REJECTION-v2-FIRST-FAILURE.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row));print(diag);raise SystemExit('Unexpected rejection result; first failure retained')
restore();assert all((P/n).read_bytes()==v for n,v in original.items());result={'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':20,'actual_cli_rejections':len(rows),'all_intended':True,'first_suite':True,'script_sha256':pre['script_sha256'],'checks':rows};(S/'REJECTION-v2-CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
