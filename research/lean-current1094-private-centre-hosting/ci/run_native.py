from pathlib import Path
import os,json,hashlib,subprocess,resource,time,signal,datetime,shutil,re
import sys,fcntl
P=Path(sys.argv[1]).resolve();expected=sys.argv[2]
assert hashlib.sha256(P.read_bytes()).hexdigest()==expected
plan=json.loads(P.read_text());W=Path(plan['owner_worktree']);stage=Path(plan['stage'])
stage.mkdir(exist_ok=False)
limits=plan['limits'];wall=limits['per_command_hard_seconds'];aggregate=limits['aggregate_resource_phase_seconds'];memory=limits['address_space_bytes'];disk=limits['free_disk_floor_bytes']
assert wall>0 and aggregate>0 and memory>0 and disk>0
assert plan['environment']['LEAN_NUM_THREADS']=='1'
lock=Path(plan['compiler_lock']).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
start=time.monotonic();child=None;result=None
receipt={'schema':'native-lean-raw-serial-receipt-v1','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':expected,'status':'RUNNING','roots':[],'scientific_acceptance':'Separate axiom/type/warning/source audit required; raw compiler success alone is not an acceptance seal.'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def pin(p):
 b=Path(p).read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def save():
 temp=stage/'RECEIPT.partial.json';temp.write_text(json.dumps(receipt,indent=2)+'\n');temp.replace(stage/'RECEIPT.json')
def limited():resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
def alarm(sig,frame):
 if child is not None and child.poll() is None:os.killpg(child.pid,signal.SIGKILL)
 raise TimeoutError('aggregate resource-phase deadline')
signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,aggregate)
def guard():
 pins=[plan['runtime']['binary'],plan['runtime']['installed_receipt'],plan['runtime']['import_receipt']]+[r['source'] for r in plan['sources']]
 for x in plan['runtime']['external_direct_roots']+plan.get('retained_roots',[]):pins.extend([x['source'],x['object']])
 pins.extend(plan.get('retained_evidence',[])+plan.get('source_reviews',[]))
 installation=json.loads(Path(plan['runtime']['import_receipt']['path']).read_text());pins.extend(installation['source_config_pins'].values())
 for x in pins:
  a=pin(x['path']);assert (a['bytes'],a['sha256'])==(x['bytes'],x['sha256']),(a,x)
 mathlib=Path(installation['source_config_pins']['lake-manifest.json']['path']).parent
 def git(p,*args):return subprocess.check_output(['git','-C',str(p),*args],text=True,timeout=15).strip()
 assert git(mathlib,'rev-parse','HEAD')==installation['mathlib_head'];assert not git(mathlib,'status','--porcelain')
 for pkg in installation['packages']:
  q=mathlib/'.lake/packages'/pkg['name'];assert git(q,'rev-parse','HEAD')==pkg['commit'];assert not git(q,'status','--porcelain')
 head=git(W,'rev-parse','HEAD');assert head==plan['owner_source_head']
 assert shutil.disk_usage(stage).free>=disk
 return {'utc':utc(),'pins_checked':len(pins),'mathlib_and_eight_package_heads':'PASS','owner_head':head,'owner_status':git(W,'status','--porcelain'),'disk_free_bytes':shutil.disk_usage(stage).free}
def objects(module):return [str(Path(p)/(module+'.olean')) for p in plan['environment']['LEAN_PATH'].split(':') if (Path(p)/(module+'.olean')).exists()]
try:
 active=[]
 for q in Path('/proc').iterdir():
  if q.name.isdigit():
   try:
    args=(q/'cmdline').read_bytes().split(b'\0');ex=os.path.basename(args[0].decode()) if args else ''
    if ex in ['lean','lake','leantar']:active.append({'pid':q.name,'executable':ex})
   except (FileNotFoundError,PermissionError):pass
 assert not active,active
 receipt['pre_guard']=guard();save()
 for kept in plan.get('retained_roots',[]):
  assert objects(kept['module'])==[kept['object']['path']]
  assert pin(kept['object']['path'])==kept['object']
 for i,root in enumerate(plan['sources']):
  assert root['command'][0]==plan['runtime']['binary']['path']
  assert Path(root['output']).parent.resolve()==stage.resolve()
  assert not Path(root['output']).exists();assert not objects(root['module'])
  inherited=[]
  for dependency in root['direct_imports']:
   local=[x for x in plan['sources'] if x['module']==dependency]
   if local:
    previous=[x for x in receipt['roots'] if x['module']==dependency];assert len(previous)==1 and previous[0]['status']=='COMPILER_EXIT_ZERO_OBJECT_PRESENT'
    pp=pin(previous[0]['object']['path']);assert pp==previous[0]['object'];assert objects(dependency)==[pp['path']];inherited.append(pp)
   elif any(x['module']==dependency for x in plan.get('retained_roots',[])):
    kept=next(x for x in plan.get('retained_roots',[]) if x['module']==dependency);pp=pin(kept['object']['path']);assert pp==kept['object'];assert objects(dependency)==[pp['path']];inherited.append(pp)
   else:
    expected=next(x['object'] for x in plan['runtime']['external_direct_roots'] if x['module']==dependency)
    matches=[str(Path(p)/Path(*dependency.split('.')).with_suffix('.olean')) for p in plan['environment']['LEAN_PATH'].split(':') if (Path(p)/Path(*dependency.split('.')).with_suffix('.olean')).exists()]
    assert matches and matches[0]==expected['path']
  out=stage/(root['module']+'.stdout');err=stage/(root['module']+'.stderr');env=os.environ.copy();env.update(plan['environment']);env.pop('LEAN_OPTS',None)
  result={'module':root['module'],'source':root['source'],'command':root['command'],'cwd':root['cwd'],'inherited_objects':inherited,'started_utc':utc(),'status':'RUNNING'};receipt['roots'].append(result);save();t=time.monotonic();rss=vm=0;reason=None
  with out.open('wb') as so,err.open('wb') as se:
   child=subprocess.Popen(root['command'],cwd=root['cwd'],env=env,stdout=so,stderr=se,start_new_session=True,preexec_fn=limited)
   while child.poll() is None:
    try:
     fields={x.split(':',1)[0]:x.split(':',1)[1].strip() for x in Path(f'/proc/{child.pid}/status').read_text().splitlines() if ':' in x}
     rss=max(rss,int(fields.get('VmRSS','0 kB').split()[0])*1024);vm=max(vm,int(fields.get('VmSize','0 kB').split()[0])*1024)
    except FileNotFoundError:pass
    if time.monotonic()-t>wall or shutil.disk_usage(stage).free<disk:
     reason='per_command_wall_or_disk_limit';os.killpg(child.pid,signal.SIGKILL);break
    time.sleep(.01)
   code=child.wait();child=None
  good=code==0 and reason is None and Path(root['output']).is_file()
  result.update({'status':'COMPILER_EXIT_ZERO_OBJECT_PRESENT' if good else 'FAIL_PRESERVED','exit_code':code,'limit_failure':reason,'finished_utc':utc(),'elapsed_seconds':time.monotonic()-t,'sampled_peak_rss_bytes':rss,'sampled_peak_vm_bytes':vm,'stdout':pin(out),'stderr':pin(err),'object':pin(root['output']) if Path(root['output']).exists() else None});save()
  (stage/(root['module']+'.receipt.json')).write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps(result),flush=True)
  if not good:break
 receipt['post_guard']=guard();receipt['status']='RAW_COMPILERS_COMPLETE' if len(receipt['roots'])==len(plan['sources']) and all(x['status']=='COMPILER_EXIT_ZERO_OBJECT_PRESENT' for x in receipt['roots']) else 'FAIL_PRESERVED'
except BaseException as exc:
 receipt['status']='FAIL_PRESERVED';receipt['failure']=repr(exc)
 if child is not None:
  if child.poll() is None:os.killpg(child.pid,signal.SIGKILL)
  code=child.wait()
  if result is not None and result['status']=='RUNNING':
   result.update({'status':'INTERRUPTED_PRESERVED','exit_code':code,'finished_utc':utc(),'stdout':pin(out) if out.exists() else None,'stderr':pin(err) if err.exists() else None,'object':pin(root['output']) if Path(root['output']).exists() else None})
   (stage/(root['module']+'.receipt.json')).write_text(json.dumps(result,indent=2)+'\n')
   save();print(json.dumps(result),flush=True)
finally:
 receipt['finished_utc']=utc();receipt['resource_phase_seconds']=time.monotonic()-start;signal.setitimer(signal.ITIMER_REAL,0);save()
print(json.dumps({'status':receipt['status'],'receipt':pin(stage/'RECEIPT.json')}),flush=True)
