"""Reconstruct all three eight-cold complex providers and admit the complete mixed witness.
Prepared with OpenAI Codex assistance. Apache-2.0; see NOTICE.md.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time,shutil
from pathlib import Path
from fractions import Fraction as Q
assert __debug__, 'Assertions required'
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();O=a.work.resolve();assert not O.exists()and not O.is_relative_to(P)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
actual={f.relative_to(P).as_posix():sha(f)for f in P.rglob('*')if f.is_file()and f!=P/'MANIFEST.json'and'__pycache__'not in f.parts};assert actual==read(P/'MANIFEST.json')
O.mkdir(parents=True);steps=[];start=time.monotonic();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
def begin(name,script,*args):
 log=O/(name+'.log');f=log.open('w');t=time.monotonic();print('RUN',name,flush=True)
 proc=subprocess.Popen([sys.executable,'-B',str(P/'code/run_portable.py'),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=env)
 return name,log,f,t,proc
def finish(job):
 name,log,f,t,proc=job;code=proc.wait();f.close();steps.append(dict(name=name,exit_code=code,seconds=time.monotonic()-t,log_sha256=sha(log)));dump(O/'STAGES.json',steps)
 if code:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
 print('PASS',name,flush=True)
def run(name,script,*args):finish(begin(name,script,*args))
B=P/'vendor/pr558';F=B/'vendor/pr552';V=F/'complex-global/vendor531';baseline=O/'baseline558';zero=O/'zero-local';four=O/'four-local';G=O/'mixed-global'
run('frozen558-full-replay',B/'verify.py','--work',baseline)
run('construct-four-pivots',P/'code/build_four_portable.py','--input',baseline/'reconstruction/weighted/FULL-WORD.json.gz','--recipe',P/'data/FROZEN-FOUR-PROMOTION.json','--gk-dir',F/'complex-local/static44/gk','--out',O/'four-word')
run('four-promoted-scalar-omissions',B/'code/audit_promoted_scalar.py',O/'four-word/FULL-WORD.json.gz',baseline/'reconstruction/static44/SELECTION.json',O/'FOUR-SCALAR-CONTROLS.json')
providers={}
for name,raw in [('zero',baseline/'reconstruction/weighted/FULL-WORD.json.gz'),('four',O/'four-word/FULL-WORD.json.gz'),('eight',baseline/'reconstruction/promoted/FULL-WORD.json.gz')]:
 local=O/(name+'-cold-local');cold=O/(name+'-cold-word');word=O/(name+'-multicold-word');recipe=P/'data'/(name.upper()+'-COLD.json');multi=P/'data'/(name.upper()+'-MULTICOLD.json');providers[name]=local
 run(name+'-cold-construction',P/'code/build_cold_kernel.py','--input',raw,'--recipe',recipe,'--gk-dir',F/'complex-local/static44/gk','--out',cold)
 run(name+'-cold-kernel-omissions',P/'code/audit_kernel_controls.py','--word',cold/'FULL-WORD.json.gz','--recipe',recipe,'--out',cold/'KERNEL-OMISSION-CONTROLS.json')
 run(name+'-multicold-construction',P/'code/build_multicut_kernels.py','--input',cold/'FULL-WORD.json.gz','--recipe',multi,'--gk-dir',F/'complex-local/static44/gk','--out',word)
 run(name+'-multicold-kernel-omissions',P/'code/audit_multicold_controls.py','--word',word/'FULL-WORD.json.gz','--recipe',multi,'--out',word/'MULTICOLD-OMISSION-CONTROLS.json')
 run(name+'-inherited-44-omissions',F/'complex-local/static44/audit_scalar.py',word/'FULL-WORD.json.gz',baseline/'reconstruction/static44/SELECTION.json',word/'STATIC44-SCALAR-AUDIT.json')
 if name!='zero':
  shutil.copyfile(raw.parent/'PROMOTION.json',word/'PROMOTION.json')
  run(name+'-promoted-omissions',B/'code/audit_promoted_scalar.py',word/'FULL-WORD.json.gz',baseline/'reconstruction/static44/SELECTION.json',word/'PROMOTED-SCALAR-AUDIT.json')
 run(name+'-all-columns-native-frames',V/'code/audit_and_transport.py','--raw',word/'FULL-WORD.json.gz','--routing',F/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local)
 run(name+'-both-reflected-ledgers',V/'code/emit_local.py',local)
 run(name+'-independent-local-controls',V/'code/audit_local.py',local)
 run(name+'-normalized-wrappers',V/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
phase_jobs=[begin(name+'-all-phase-edges',B/'code/phases_full.py',local,V/'vendor/clifford')for name,local in providers.items()]
for job in phase_jobs:finish(job)
zero,four,eight=[providers[k]for k in ('zero','four','eight')]
run('bind-three-providers',P/'code/bind_providers_portable.py','--baseline',baseline,'--zero',zero,'--four',four,'--eight',eight,'--plan',P/'data/PLAN.json','--out',G)
run('emit-three-provider-controller',P/'code/emit_allcold.py','--base',G/'base','--owners',P/'data/OWNERS.json.gz','--plan',G/'PLAN.json','--out',G/'hosted')
(G/'audit').mkdir()
run('independent-controller-and-controls',P/'code/audit_allcold.py',G/'base',G/'hosted',G/'audit/ASYNC-AUDIT.json','--mutation-controls')
run('fresh-three-provider-invoice',P/'code/invoice_allcold.py','--base',G/'base','--hosted',G/'hosted','--audit',G/'audit','--out',G/'audit','--retained-invoice',V/'evidence/audit/PREFIX-AND-INVOICE.json')
run('conservative-and-native-exact-assembly',P/'code/assemble.py',P,G,O/'ASSEMBLY.json')
run('fifty-four-admission-controls',P/'code/assembly_controls.py','--owner',G/'audit/OWNERS-AND-PROFILE.json','--invoice',G/'audit/PREFIX-AND-INVOICE.json','--out',O/'ASSEMBLY-CONTROLS.json')
run('phase-timing-portability-controls',P/'code/phase_timing_controls.py',G/'base',G/'audit',O/'PHASE-TIMING-CONTROLS.json')
for local in [zero,four,eight]:
 r=read(local/'INDEPENDENT-LOCAL-REPLAY.json');ph=read(local/'CLIFFORD-REVIEW.json')
 assert len(r['negative_controls_rejected'])==11 and r['paid_profiles']['forward']==r['paid_profiles']['backward']
 assert ph['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES' and ph['all_child_equalities_include_global_phase']is True and ph['directed_edges']==2929 and ph['endpoint_adapters']==224
assert len(read(O/'FOUR-SCALAR-CONTROLS.json')['controls'])==4
assert len(read(G/'audit/ASYNC-AUDIT.json')['mutations_rejected'])==16
assert len(read(O/'ASSEMBLY-CONTROLS.json')['rejected_controls'])==54
z=read(O/'ASSEMBLY.json');assert Q(z['kappa_decimal'])==Q('0.001596133352130093') and Q(z['conservative_kappa_decimal'])==Q('0.001596133349380077')
r=dict(status='PASS_THREE_PROVIDER_048_MULTICOLD_NATIVE_COMPLEX_AND_CITED_BIT',kappa=z['kappa'],kappa_decimal=z['kappa_decimal'],complex_lower=z['complex_lower'],bit_lower=z['bit_lower'],conservative_kappa_decimal=z['conservative_kappa_decimal'],conservative_complex_lower=z['conservative_complex_lower'],global_profile=z['complex_profile'],provider_counts=z['provider_counts'],surcharge_model=z['surcharge_model'],four_word_sha256=sha(O/'four-word/FULL-WORD.json.gz'),seconds=time.monotonic()-start,scope=z['scope']);dump(O/'RESULT.json',r)
paths=['PHASE-TIMING-CONTROLS.json','mixed-global/audit/IDLE-REMAINDER-FRAMES.json','RESULT.json','ASSEMBLY.json','ASSEMBLY-CONTROLS.json','FOUR-SCALAR-CONTROLS.json','four-word/CONSTRUCTION.json','mixed-global/BINDING.json','mixed-global/audit/ASYNC-AUDIT.json','mixed-global/audit/OWNERS-AND-PROFILE.json','mixed-global/audit/PREFIX-AND-INVOICE.json']
for name in ('zero','four','eight'):
 for fn in ('KERNEL-CONSTRUCTION.json','KERNEL-OMISSION-CONTROLS.json'):paths.append(name+'-cold-word/'+fn)
 for fn in ('KERNEL-CONSTRUCTION.json','MULTICOLD-OMISSION-CONTROLS.json','STATIC44-SCALAR-AUDIT.json'):paths.append(name+'-multicold-word/'+fn)
 for fn in ('INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json','WRAPPER-CHECKS.json'):paths.append(name+'-cold-local/'+fn)
 assert len(read(O/(name+'-cold-word/KERNEL-OMISSION-CONTROLS.json'))['controls'])==6
 assert len(read(O/(name+'-multicold-word/MULTICOLD-OMISSION-CONTROLS.json'))['controls'])==32
dump(O/'RECEIPT.json',dict(status=r['status'],steps=steps,artifacts={name:sha(O/name)for name in paths},manifest_sha256=sha(P/'MANIFEST.json')))
print(json.dumps(r,indent=2))
