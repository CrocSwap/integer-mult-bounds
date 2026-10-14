"""Strict additive finite release on frozen PR1800, with exact unchanged-profile binding.

Complete independently reviewed source/execution-bound reuse is optional; default is fresh. Parent source bytes, inherited credits, and notices
remain unchanged. The new endpoint is a rational nomination, independently
enclosed on the actually admitted profile; its600printed digits are not evidence.
Substantial OpenAI Codex assistance; inherited all-size assumptions remain open.
"""
import argparse,hashlib,json,os,pathlib,shutil,signal,subprocess,sys,time
from fractions import Fraction as Q
from reuse.bound_parent_reuse import verified_original_run
from portable_parent import prepare_parent,verify_parent,same_artifact_bytes
P=pathlib.Path(__file__).resolve().parent
def fail(message):raise RuntimeError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rd(path):return json.loads(path.read_bytes())
def check_manifest(root,name='MANIFEST.json'):
 pins=rd(root/name);have={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p!=root/name}
 if have!=set(pins):fail('source file set mismatch: '+str(root))
 for rel,digest in pins.items():
  if sha(root/rel)!=digest:fail('source digest mismatch: '+rel)
 return sha(root/name)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=pathlib.Path,required=True);ap.add_argument('--main',type=pathlib.Path,required=True);ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--timeout-seconds',type=int,default=1800)
 ap.add_argument('--reuse-baseline-run',type=pathlib.Path);ap.add_argument('--reuse-baseline-source',type=pathlib.Path)
 a=ap.parse_args()
 if not __debug__ or sys.flags.optimize:fail('Assertions must remain enabled for inherited admission')
 if not 1<=a.jobs<=2 or not 1<=a.timeout_seconds<=3600:fail('Bounded jobs1..2 and timeout1..3600 required')
 work=a.work.resolve()
 if work.exists() or work.is_relative_to(P):fail('work must be absent and outside package')
 msha=check_manifest(P); parent=P/'parent';psha=check_manifest(parent)
 if psha!='b8dba5524f8603e1848c73a8dd675404a0d3d9eed3b0285e9f0cfccde38fd15f':fail('wrong immutable parent')
 provenance=rd(P/'PROVENANCE.json')
 if sha(P/'refinement/new/SPEC.json')!=provenance['endpoint_source']['sha256']:fail('wrong600digit operand source')
 work.mkdir();deadline=time.monotonic()+a.timeout_seconds;stages=[]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for key in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(key,None)
 def run(name,*args):
  start=time.monotonic();log=work/(name+'.log');remaining=deadline-start
  if remaining<=0:fail('overall replay time budget exhausted')
  with log.open('w',encoding='utf-8') as out:
   opts={'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP} if os.name=='nt' else {'start_new_session':True}
   child=subprocess.Popen([sys.executable,'-B',*map(str,args)],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,env=env,**opts)
   try:rc=child.wait(timeout=remaining)
   except subprocess.TimeoutExpired:
    if os.name=='nt':subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],capture_output=True)
    else:os.killpg(child.pid,signal.SIGKILL)
    fail('replay time budget exhausted during '+name)
  stages.append({'stage':name,'returncode':rc,'seconds':time.monotonic()-start,'log_sha256':sha(log)})
  (work/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
  if rc:fail(name+' failed; inspect '+str(log))
 # Run original full release, including original outer evidence, with NO reuse flags.
 reuse_mode=a.reuse_baseline_run is not None
 if reuse_mode != (a.reuse_baseline_source is not None):fail('both reuse source and run flags are required together')
 original=work/'original';reuse_receipt=None;portability_receipt=None;portability_before=None;portability_after=None;execution_parent=parent
 if reuse_mode:
  original,reuse_receipt=verified_original_run(a.reuse_baseline_run,a.reuse_baseline_source,parent,P/'reuse/FULL-REUSE-SEAL.json')
  (work/'BASELINE-REUSE.json').write_text(json.dumps(reuse_receipt,indent=2)+'\n')
 else:
  execution_parent,portability_receipt=prepare_parent(parent,work/'portable-parent')
  portability_before=verify_parent(parent,execution_parent,portability_receipt)
  (work/'PARENT-PORTABILITY.json').write_text(json.dumps(portability_receipt,indent=2)+'\n')
  run('original-full-release',execution_parent/'verify_release.py','--main',a.main.resolve(),'--work',original,'--jobs',a.jobs)
  portability_after=verify_parent(parent,execution_parent,portability_receipt)
 base=rd(original/'verify/strict/ASSEMBLY.json')
 if base['status']!='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' or len(base['outer'])!=47:fail('parent native assembly incomplete')
 profile={int(k):v for k,v in base['complex_profile'].items()}
 if not all(type(v) is int and v>=0 for v in profile.values()):fail('profile integer types corrupted')
 actualowner=original/'verify/strict/global/audit/OWNERS-AND-PROFILE.json'
 owner=rd(actualowner)
 if sha(actualowner)!=base['input_sha256']['owner_audit']:fail('actual owner receipt not bound by assembly')
 if owner['status']!='PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE' or owner['live']!=66304 or {int(k):v for k,v in owner['paid_profile'].items()}!=profile:fail('actual owner live/profile differs')
 spec=rd(P/'refinement/new/SPEC.json');bj=rd(P/'refinement/outer/B.json')
 if profile!={int(k):int(v) for k,v in bj['profile'].items()} or profile!={int(k):int(v) for k,v in spec['expected']['global_profile'].items()}:fail('actual admitted profile differs from nominee profile')
 if spec['geometry']['dimension']!=73 or spec['expected']['live']!=66304:fail('actual supplier dimensions differ')
 if Q(base['bit_lower'])!=Q('0.001733427039589844234749'):fail('actual bit endpoint differs')
 originalspec=rd(parent/'new/SPEC.json')
 if Q(base['complex_lower'])!=Q(originalspec['expected']['complex_lower']):fail('parent native endpoint differs')
 target=work/'refinement';shutil.copytree(P/'refinement',target)
 for art in ('LEDGER.json','INDEPENDENT.json'):(target/'outer'/art).unlink()
 for script in ('check_ledger.py','independent_check.py'):run('new-'+script.removesuffix('.py'),target/'outer'/script)
 for art in ('LEDGER.json','INDEPENDENT.json'):
  if not same_artifact_bytes((target/'outer'/art).read_bytes(),(P/'refinement/outer'/art).read_bytes()):fail('refined arithmetic artifact differs beyond CRLF/LF '+art)
 ledger=rd(target/'outer/LEDGER.json');row=ledger['rows']['struct_boundary_radix_union'];claim=rd(P/'refinement/outer/OUTER-CLAIM.json')
 k=Q(row['kappa']['rational'])
 if k!=Q(row['kappa']['decimal']) or k!=Q(claim['rational']) or k!=Q(claim['kappa']):fail('candidate exact rational/decimal mismatch')
 if len(row['strict_checks'])!=57 or not all(Q(v['rational'])>0 for v in row['strict_checks'].values()):fail('missing or failed outer inequalities')
 if len(ledger['rejecting_controls']['struct_boundary_radix_union'])!=17:fail('missing rejecting outer controls')
 if not Q(ledger['native_moment'][1]['rational'])<1:fail('new nominee endpoint not enclosed')
 old=Q(rd(parent/'outer/OUTER-CLAIM.json')['kappa'])
 if not k>old:fail('candidate does not improve exact parent')
 # Independent enclosure is implemented separately and consumes the ACTUAL full-parent assembly.
 run('independent-profile-enclosure',P/'independent/check.py','--assembly',original/'verify/strict/ASSEMBLY.json','--package',P,'--out',work/'INDEPENDENT-PROFILE.json')
 independent=rd(work/'INDEPENDENT-PROFILE.json')
 if independent['status']!='PASS_INDEPENDENT_ACTUAL_PROFILE_ENCLOSURE' or Q(independent['kappa'])!=k:fail('independent actual-profile check did not bind candidate')
 run('independent-broad-shift',P/'independent/check_broad_shift.py')
 broad=rd(work/'independent-broad-shift.log')
 if broad['status']!='PASS_EXACT_BROAD_SHIFT_CORRECTION' or len(broad['controls'])!=4:fail('broad shift exact corrected identity failed')
 if reuse_mode:
  again,_=verified_original_run(a.reuse_baseline_run,a.reuse_baseline_source,parent,P/'reuse/FULL-REUSE-SEAL.json')
  if again!=original:fail('parent reuse location changed')
 if portability_receipt is not None:
  portability_after=verify_parent(parent,execution_parent,portability_receipt)
  (work/'PARENT-PORTABILITY-AFTER.json').write_text(json.dumps(portability_after,indent=2)+'\n')
 if check_manifest(parent)!=psha or check_manifest(P)!=msha:fail('source changed during replay')
 result={'status':'PASS_ADDITIVE_FINITE_REFINEMENT_FULL_NATIVE','manifest_sha256':msha,'parent_manifest_sha256':psha,'parent_full_replay':True,'native_reuse':reuse_mode,'parent_verification_mode':'complete reviewed bound reuse' if reuse_mode else 'fresh native replay','parent_reuse_receipt':reuse_receipt,'parent_portability_receipt':portability_receipt,'parent_portability_before':portability_before,'parent_portability_after':portability_after,'parent_execution_manifest_sha256':portability_receipt['execution_manifest_sha256'] if portability_receipt else psha,'kappa':str(k),'kappa_decimal':claim['kappa'],'exact_gain':str(k-old),'actual_profile':profile,'independent_profile_receipt_sha256':sha(work/'INDEPENDENT-PROFILE.json'),'stages':stages,'all_size_proved':False,'current_record_claim':False,'scope':'Actual parent finite native supplier (fresh by default, or complete reviewed source/execution-bound reuse) plus two separate exact enclosures and57conditional outer inequalities. Inherited fine-prime padding, gauge-free accretive circuit, union schedule, compiler/tape/precision/recovery and analytic assumptions remain mathematical inputs.'}
 (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal'])
if __name__=='__main__':main()
