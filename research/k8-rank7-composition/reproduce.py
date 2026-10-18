# SPDX-License-Identifier: Apache-2.0
# Prepared for 1337isnot1337 with substantial OpenAI Codex assistance.
"""Replay the smaller-end construction and complete conditional admission.

The frozen, freshly checked k8 ancestry is explicitly reused. The new native
word, both orientations, wrappers, exact phases, controller, invoice, moments,
outer constraints and mutation controls are recomputed. No solver is required.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,tarfile,time
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def require(ok,message):
 if not ok:raise RuntimeError(message)
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sources(root=ROOT):
 require(__debug__,'Assertions required; do not use -O')
 manifest=read(HERE/'MANIFEST.json')
 for rel,expected in manifest.items():require((HERE/rel).is_file() and sha(HERE/rel)==expected,'package manifest: '+rel)
 spec=read(HERE/'SOURCES.json')
 for rel,expected in spec['main_files'].items():require((root/rel).is_file() and sha(root/rel)==expected,'main source pin: '+rel)
 for rel,expected in spec['source_archives'].items():require((HERE/rel).is_file() and sha(HERE/rel)==expected,'source archive pin: '+rel)
 return spec

def unpack(path,out):
 with tarfile.open(path) as t:
  for m in t.getmembers():
   rel=PurePosixPath(m.name)
   require(not rel.is_absolute() and '..' not in rel.parts and (m.isfile() or m.isdir()),'unsafe source archive member')
  t.extractall(out,filter='data')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path);ap.add_argument('--check-pins-only',action='store_true');a=ap.parse_args()
 pins=sources()
 if a.check_pins_only:print('PASS_K8_RANK7_SOURCE_PINS',len(pins['main_files']));return
 require(a.work is not None,'--work required');work=a.work.resolve();require(not work.exists(),'output already exists');work.mkdir(parents=True)
 src=ROOT/'research/complex-k492-owner-repair/vendor/multicold';b=src/'vendor/pr558';parent=b/'vendor/pr552';up=ROOT/'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2'
 predecessor=work/'sources';predecessor.mkdir();unpack(HERE/'sources/PR1031.tar.gz',predecessor);old=predecessor/'gauge44-slots-t16'
 unpack(HERE/'sources/SLOT-NATIVE.tar.gz',work/'old-native')
 ancestry=read(HERE/'evidence/ANCESTRY.json');expected_steps=['pivot-swap','cold44-exact','lec-p6n','promotion','promo-controls','lec-promo','jx','jx-control-C0_identity','jx-control-C1_741_only','jx-control-N3_plain_join_moved_reads','lec-jx','hybrids','hybrid-controls','lec-hyb','frames','lec-frames','native','ledgers','local-replay','wrappers','phases']
 require([x['step'] for x in ancestry['completed_steps']]==expected_steps and all(x['exit_code']==0 for x in ancestry['completed_steps']),'complete ancestor receipt')
 require(len(ancestry['slot_controls'])==34 and all(x['ok'] for x in ancestry['slot_controls'].values()),'slot mutation receipt')
 require(sha(HERE/'sources/K8-SLOT-WORD.json.gz')==pins['source_archives']['sources/K8-SLOT-WORD.json.gz'],'frozen slot word')
 old_plan=read(old/'data/PLAN.json');sys.path.insert(0,str(old/'code'));from generated_identity import artifact_identities
 require(artifact_identities(work/'old-native/local')==old_plan['provider_registry']['gauge44']['artifact_semantic_sha256'],'frozen baseline native identities')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',GAIN_PR564_SOURCE=str(src),MULTICOLD_SOURCE=str(src))
 for k in ('PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD'):env.pop(k,None)
 steps=[]
 def run(nm,script,args,portable=False):
  log=work/(nm+'.log');begin=time.monotonic();cmd=[sys.executable,'-B']+([str(src/'code/run_portable.py')] if portable else [])+[str(script),*map(str,args)]
  with log.open('w') as f:rc=subprocess.run(cmd,env=env,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
  steps.append(dict(name=nm,exit_code=rc,seconds=round(time.monotonic()-begin,3),script_sha256=sha(script),log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(steps,indent=2)+'\n')
  require(rc==0,nm+' failed:\n'+log.read_text()[-4000:]);print('PASS',nm,flush=True)
 run('predecessor-manifest',old/'verify_manifest.py',[])
 raw=work/'NEW-WORD.json.gz'
 run('construction',HERE/'construct.py',['--input',HERE/'sources/K8-SLOT-WORD.json.gz','--promotion',old/'construction/promo/build_promotion.py','--output',raw])
 run('point-accounting',HERE/'point_audit.py',[raw])
 run('independent-local',old/'independent/audit_local.py',['--word',raw,'--out',work/'INDEPENDENT-LOCAL.json','--main',ROOT])
 local=work/'new-local'
 run('native',up/'code/hpe_audit_and_transport.py',['--raw',raw,'--routing',parent/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local],True)
 run('ledgers',up/'code/hpe_emit_local.py',[local],True)
 run('local-replay',up/'code/hpe_audit_local.py',[local],True)
 run('wrappers',up/'code/hpe_adapters_local.py',[local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json'],True)
 run('phases',b/'code/phases_full.py',[local,parent/'complex-global/vendor531/vendor/clifford'],True)
 run('baseline-t16',old/'verify_t16.py',['--main',ROOT,'--local',work/'old-native/local','--work',work/'baseline'])
 run('complete-new-admission',HERE/'admit.py',['--owners',HERE/'data/OWNERS.json.gz','--out',work/'admission','--root',ROOT,'--predecessor',old,'--local',local,'--baseline',work/'baseline'])
 actual=read(work/'admission/strict-ASSEMBLY.json');expected=read(HERE/'evidence/ASSEMBLY.json')
 for field in ('kappa','complex_lower','complex_profile','conservative_complex_lower','conservative_kappa','outer','conservative_outer','bootstrap','conservative_bootstrap'):
  require(actual[field]==expected[field],'certificate field: '+field)
 require(actual['kappa_decimal']=='0.001672404744903063','final kappa')
 result=dict(status='PASS_K8_RANK7_COMPLETE_REPRODUCTION',kappa=actual['kappa'],kappa_decimal=actual['kappa_decimal'],steps=steps,ancestry_reuse=True,main_source_pins=len(pins['main_files']))
 (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],actual['kappa_decimal'],flush=True)

if __name__=='__main__':main()
