"""Full cold replay: PR575 joint prefixes, PR576 added kernels, and new owners.
Prepared with OpenAI Codex assistance; Apache-2.0. Standard library only.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,os,subprocess,sys,time
if not __debug__:raise RuntimeError('Assertions required; optimized verification is disabled')
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
dump=lambda p,x:p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
def inventory():return{p.relative_to(P).as_posix():sha(p)for p in P.rglob('*')if p.is_file()and p!=P/'MANIFEST.json'and '__pycache__'not in p.parts}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();w=a.work.resolve()
 assert not w.exists()and not w.is_relative_to(P),'Use an absent external output directory'
 initial=inventory();assert initial==read(P/'MANIFEST.json')
 for vendor,record in read(P/'SOURCE-PINS.json').items():
  for name,pin in record['files'].items():
   raw=(P/'vendor'/vendor/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin['sha256'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob']
 s=P/'vendor/pr575';b=s/'vendor/pr558';f=b/'vendor/pr552';v=f/'complex-global/vendor531';gk=f/'complex-local/static44/gk';code=P/'code';spec=read(P/'data/WITNESS-SPEC.json')
 assert read(P/'data/P571K-MULTICOLD.json')['kernels']==read(P/'vendor/pr576/data/P571K-MULTICOLD.json')['kernels']
 w.mkdir();(w/'logs').mkdir();steps=[];started=time.monotonic()
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None);env.pop('WITNESS_DISCOVER',None)
 def run(name,script,*args,portable=True):
  cmd=[sys.executable,'-B']+([str(s/'code/run_portable.py')]if portable else[])+[str(script),*map(str,args)];log=w/'logs'/(name+'.log');t=time.monotonic();print('RUN',name,flush=True)
  with log.open('w',encoding='utf-8',newline='\n')as out:r=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,env=env)
  steps.append(dict(name=name,command=cmd,seconds=time.monotonic()-t,exit_code=r.returncode,script_sha256=sha(script),log_sha256=sha(log)));dump(w/'STAGES.json',steps)
  if r.returncode:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
  print('PASS',name,flush=True)
 parent=w/'parent575';word=w/'prefixk-word';local=w/'prefixk-local'
 run('full-pinned575-cold-replay',s/'verify.py','--work',parent,portable=False)
 assert read(parent/'RESULT.json')['kappa_decimal']=='0.001600770286423653'
 run('twelve-added-kernel-construction',code/'build_multicut_kernels.py','--input',parent/'width7-joint-word/FULL-WORD.json.gz','--recipe',P/'data/P571K-MULTICOLD.json','--gk-dir',gk,'--out',word)
 raw=json.loads(gzip.decompress((word/'FULL-WORD.json.gz').read_bytes()));assert raw['report']['local_rank_mass']==sum(int(r)*n for r,n in raw['report']['local_profile'].items())
 assert raw['report']['width_inventory']==spec['providers']['prefixk_eight']['inventory']
 run('all-twelve-kernel-omissions',s/'code/audit_multicold_controls.py','--word',word/'FULL-WORD.json.gz','--recipe',P/'data/P571K-MULTICOLD.json','--out',word/'MULTICOLD-OMISSION-CONTROLS.json')
 assert len(read(word/'MULTICOLD-OMISSION-CONTROLS.json')['controls'])==48
 run('all-columns-and-native-frames',v/'code/audit_and_transport.py','--raw',word/'FULL-WORD.json.gz','--routing',f/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local)
 run('both-reflected-programs',v/'code/emit_local.py',local)
 run('independent-local-replay',v/'code/audit_local.py',local)
 assert len(read(local/'INDEPENDENT-LOCAL-REPLAY.json')['negative_controls_rejected'])==11
 run('normalized-wrappers',v/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
 run('all-phase-edges-and-endpoints',b/'code/phases_full.py',local,v/'vendor/clifford')
 phase=read(local/'CLIFFORD-REVIEW.json');assert phase['directed_edges']==spec['providers']['prefixk_eight']['phase_edges']and phase['endpoint_adapters']==224 and phase['all_child_equalities_include_global_phase']is True
 run('complete-physical-invoice-and-admission',code/'replay_global.py','--parent',parent,'--prefixk',local,'--work',w/'admission',portable=False)
 assert inventory()==initial,'Source changed during verification'
 result=read(w/'admission/RESULT.json');result['status']='PASS_FULL_COLD_JOINT_PREFIX_KERNEL_PACKING';dump(w/'RESULT.json',result)
 files=['RESULT.json','prefixk-word/KERNEL-CONSTRUCTION.json','prefixk-word/MULTICOLD-OMISSION-CONTROLS.json','prefixk-local/INDEPENDENT-LOCAL-REPLAY.json','prefixk-local/CLIFFORD-REVIEW.json','prefixk-local/WRAPPER-CHECKS.json','admission/RESULT.json','admission/RECEIPT.json']
 dump(w/'RECEIPT.json',dict(status=result['status'],source_manifest_sha256=sha(P/'MANIFEST.json'),parent_receipt_sha256=sha(parent/'RECEIPT.json'),seconds=time.monotonic()-started,steps=steps,artifacts={n:sha(w/n)for n in files}));print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
