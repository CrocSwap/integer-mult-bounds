"""Portable producer/specification -> final raw6 word replay, with frozen pins.
Fresh outputs only. No discovery pin recording is permitted. OpenAI Codex.
"""
import sys,os,json,hashlib,subprocess,shutil,time
from pathlib import Path
assert __debug__;sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 pins=json.loads((HERE/'MANIFEST.json').read_text());actual={p.relative_to(HERE).as_posix():sha(p)for p in HERE.rglob('*')if p.is_file()and p!=HERE/'MANIFEST.json'}
 assert all(not p.is_symlink()for p in HERE.rglob('*'));assert pins['files']==actual,'source package manifest mismatch';return sha(HERE/'MANIFEST.json')

def verify(output,include_admission=True):
 output=Path(output).resolve();assert not output.exists()and not output.is_relative_to(HERE);output.mkdir(parents=True);before=integrity();start=time.monotonic();steps=[];pkg=output/'pkg';shutil.copytree(HERE/'pkg',pkg)
 expected=json.loads((HERE/'EXPECTED.json').read_text())
 def step(name,script,args=(),extra=None):
  log=output/(name+'.log');cmd=[sys.executable,'-B',str(script)]+list(map(str,args));t=time.monotonic()
  with log.open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1',**(extra or{})})
  row=dict(stage=name,actual_exit=r.returncode,seconds=time.monotonic()-t,command=cmd);steps.append(row);(output/'STAGES.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,r.returncode,round(row['seconds'],2),flush=True);assert r.returncode==0,(name,r.returncode)
 def check(prefix,p):
  for n in ('249-records.bin','249-states.json','frames.json'):assert sha(p/n)==expected[prefix+'/'+n],(prefix,n,sha(p/n),expected[prefix+'/'+n])
 if include_admission:step('newbase-source-admission',HERE/'source_admission.py',['--output',output/'newbase-source-admission'])
 step('producer-regeneration',pkg/'bitword/producer/regenerate.py',['--work',output/'producer-regeneration'])
 step('base-export',HERE/'code/export_p10.py',[pkg,output/'base']);check('base',output/'base')
 step('descent-selection',pkg/'discovery/descent_search.py',[pkg,pkg/'descent-selection.json'])
 step('target-selection',pkg/'discovery/target_search.py',[pkg,pkg/'descent-selection.json',pkg/'target-selection.json'])
 step('restore-selection',pkg/'discovery/build_restore_selection.py')
 step('sink-selection',pkg/'discovery/build_sink_selection.py')
 for n in ('descent','target','restore','sink'):assert sha(pkg/(n+'-selection.json'))==expected['selection/'+n+'-selection.json'],n
 step('stages-export',HERE/'code/export_stages.py',[pkg,output/'stages']);check('staged',output/'stages/04-sink')
 step('design-t',HERE/'code/dt.py',[output/'stages/04-sink',output/'design-t'])
 step('completion',HERE/'code/comp.py',[output/'design-t'])
 step('twins-471',HERE/'code/twin.py',[output/'design-t',output/'candidate'],{'TWIN_CAP':'471'})
 p=output/'candidate/249-states.json';st=json.loads(p.read_text());st['record_sha256']=sha(output/'candidate/249-records.bin');st['record_count']=(output/'candidate/249-records.bin').stat().st_size//24;p.write_text(json.dumps(st,sort_keys=True)+'\n');check('candidate',output/'candidate')
 sys.path.insert(0,str(HERE/'code'));from f2 import replay
 rr,resid=replay(str(output/'candidate'));assert not resid and all(rr[k]==0 for k in ('violations','final_mismatch','X_not_restored','H_not_restored','resid_sigma0','resid_other'))and rr['copies']==20
 step('new-frame-geometry',HERE/'code/nondeg.py',[output/'candidate',output/'base'])
 step('exact-residual-tiling',HERE/'code/tile.py',[output/'candidate','300'])
 assert integrity()==before
 report=dict(status='PASS_STRICT_SOURCE353354_REGENERATION',twin_cap=471,local_residual_bank_replicas=300,producer_word_regenerated=True,all_four_selections_regenerated=True,base_matches_pinned353=True,final_word_sha256=sha(output/'candidate/249-records.bin'),full_newbase_admission=include_admission,final_F2=rr,steps=steps,source_manifest_sha256=before,source_files_unchanged=True,seconds=time.monotonic()-start,scope='Source regeneration and local finite checks including residual census/zero-padding tiling at 300 replicas; downstream native charts/primes/banks/invoice/assembly are separate obligations.')
 (output/'VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['final_word_sha256'],flush=True);return report

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--without-duplicate-source-admission',action='store_true');a=ap.parse_args();verify(a.output,not a.without_duplicate_source_admission)
