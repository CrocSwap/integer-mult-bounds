"""Reconstruct and verify both actual providers and every mixed physical call.
Prepared with OpenAI Codex assistance. Apache-2.0; see NOTICE.md.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
assert __debug__, 'Assertions must remain enabled'
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();O=a.work.resolve();assert not O.exists() and not O.is_relative_to(P)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
actual={q.relative_to(P).as_posix():sha(q)for q in P.rglob('*')if q.is_file()and q!=P/'MANIFEST.json'and'__pycache__'not in q.parts};assert actual==read(P/'MANIFEST.json'),'package manifest'
O.mkdir(parents=True);steps=[];start=time.monotonic();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONUTF8='1');env.pop('PYTHONOPTIMIZE',None)
def run(name,script,*args):
 t=time.monotonic();log=O/(name+'.log');print('RUN',name,flush=True)
 with log.open('w')as f:r=subprocess.run([sys.executable,'-B',str(P/'code/run_portable.py'),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=env)
 steps.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));dump(O/'STAGES.json',steps)
 if r.returncode:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
 print('PASS',name,flush=True)
B=P/'vendor/pr558';F=B/'vendor/pr552';V=F/'complex-global/vendor531';baseline=O/'baseline558';cold=O/'cold-local';G=O/'mixed-global'
run('frozen-pr558-full-replay',B/'verify.py','--work',baseline)
run('construct-cold-kernel',P/'code/build_cold_kernel.py','--input',baseline/'reconstruction/promoted/FULL-WORD.json.gz','--recipe',P/'data/FROZEN-KERNEL-RECIPE.json','--gk-dir',F/'complex-local/static44/gk','--out',O/'cold-word')
run('new-kernel-omission-controls',P/'code/audit_kernel_controls.py','--word',O/'cold-word/FULL-WORD.json.gz','--recipe',P/'data/FROZEN-KERNEL-RECIPE.json','--out',O/'KERNEL-OMISSION-CONTROLS.json')
run('cold-all-columns-native-frames',V/'code/audit_and_transport.py','--raw',O/'cold-word/FULL-WORD.json.gz','--routing',F/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',cold)
run('cold-both-reflected-ledgers',V/'code/emit_local.py',cold)
run('cold-independent-local-and-controls',V/'code/audit_local.py',cold)
run('cold-normalized-wrappers',V/'code/adapters_local.py',cold/'CANONICAL-WORD.json.gz',cold/'RESIDUAL-ADAPTERS.json',cold/'WRAPPER-CHECKS.json')
run('cold-every-phase-edge',B/'code/phases_full.py',cold,V/'vendor/clifford')
run('bind-fresh-provider-dispatch',P/'code/prepare_mixed_base.py','--baseline',baseline,'--cold',cold,'--plan',P/'data/PLAN.json','--out',G)
run('emit-mixed-global',P/'code/emit_mixed.py','--base',G/'base','--owners',P/'data/OWNERS.json.gz','--plan',G/'PLAN.json','--out',G/'hosted')
(G/'audit').mkdir()
run('independent-mixed-owners',P/'code/audit_mixed.py',G/'base',G/'hosted',G/'audit/ASYNC-AUDIT.json','--mutation-controls')
run('fresh-mixed-invoice',P/'code/invoice_mixed.py','--base',G/'base','--hosted',G/'hosted','--audit',G/'audit','--out',G/'audit','--retained-invoice',V/'evidence/audit/PREFIX-AND-INVOICE.json')
run('mixed-two-engine-exact-assembly',P/'code/assemble.py',P,G,O/'ASSEMBLY.json')
run('mixed-assembly-admission-controls',P/'code/assembly_controls.py','--owner',G/'audit/OWNERS-AND-PROFILE.json','--invoice',G/'audit/PREFIX-AND-INVOICE.json','--out',O/'ASSEMBLY-CONTROLS.json')
assembly=read(O/'ASSEMBLY.json');native=read(cold/'INDEPENDENT-LOCAL-REPLAY.json');phase=read(cold/'CLIFFORD-REVIEW.json');owners=read(G/'audit/OWNERS-AND-PROFILE.json');invoice=read(G/'audit/PREFIX-AND-INVOICE.json');control=read(G/'audit/ASYNC-AUDIT.json')
assert phase['all_child_equalities_include_global_phase'] and phase['endpoint_adapters']==224 and phase['directed_edges']==2929
assert native['paid_profiles']['forward']==native['paid_profiles']['backward'] and len(native['negative_controls_rejected'])==11
assert len(read(O/'KERNEL-OMISSION-CONTROLS.json')['controls'])==6
assert len(control['mutations_rejected'])==14
assert len(read(O/'ASSEMBLY-CONTROLS.json')['rejected_controls'])==40
assert all(invoice['strict_checks'].values()) and invoice['provider_counts']=={'rank5_eight':71,'coldkernel000':1}
assert assembly['kappa_decimal']=='0.001592518729588709'
result=dict(status='PASS_MIXED_COLDKERNEL_COMPLEX_AND_CITED_BIT',kappa=assembly['kappa'],kappa_decimal=assembly['kappa_decimal'],complex_lower=assembly['complex_lower'],bit_lower=assembly['bit_lower'],word_sha256=sha(O/'cold-word/FULL-WORD.json.gz'),cold_local_profile=native['paid_profiles']['forward'],global_profile=owners['paid_profile'],provider_counts=invoice['provider_counts'],seconds=time.monotonic()-start,scope=assembly['scope'])
dump(O/'RESULT.json',result)
paths=['RESULT.json','ASSEMBLY.json','ASSEMBLY-CONTROLS.json','KERNEL-OMISSION-CONTROLS.json','cold-word/KERNEL-CONSTRUCTION.json','cold-local/INDEPENDENT-LOCAL-REPLAY.json','cold-local/CLIFFORD-REVIEW.json','mixed-global/BINDING.json','mixed-global/audit/ASYNC-AUDIT.json','mixed-global/audit/OWNERS-AND-PROFILE.json','mixed-global/audit/PREFIX-AND-INVOICE.json']
dump(O/'RECEIPT.json',dict(status=result['status'],steps=steps,artifacts={name:sha(O/name)for name in paths},manifest_sha256=sha(P/'MANIFEST.json')))
print(json.dumps(result,indent=2))
