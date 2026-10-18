"""Reconstruct the fixed supplier, every local phase, and the whole-owner witness.
No optimizer or network. The pinned unchanged data-controller and bit supplier
remain explicit dependencies; inherited all-size/analytic contracts remain.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,os,subprocess,sys,time
if not __debug__:raise RuntimeError('Assertions must remain enabled; do not use -O')
ROOT=Path(__file__).resolve().parent;P=ROOT/'vendor/pr531'
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('out',type=Path);a=ap.parse_args();OUT=a.out.resolve()
assert not OUT.exists()and not OUT.is_relative_to(ROOT),'Use a fresh directory outside the package'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 actual={str(p.relative_to(ROOT)):sha(p)for p in ROOT.rglob('*')if p.is_file()and p!=ROOT/'MANIFEST.json'and '__pycache__'not in p.parts}
 assert actual==read(ROOT/'MANIFEST.json'),'complete package manifest'
 for rel,h in read(P/'MANIFEST.json')['sha256'].items():assert sha(P/rel)==h,rel
 for rel,h in read(ROOT/'SOURCES.json')['inherited_files'].items():assert sha(ROOT/rel)==h,rel
integrity();OUT.mkdir();steps=[];started=time.monotonic();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
def run(name,script,*args):
 t=time.monotonic();log=OUT/(name+'.log');print('RUN',name,flush=True)
 with log.open('w')as f:r=subprocess.run([sys.executable,'-B',str(ROOT/'code/run.py'),str(script),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,seconds=time.monotonic()-t,exit_code=r.returncode,log_sha256=sha(log)));(OUT/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
 assert r.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
try:
 local=OUT/'local';base=OUT/'base';host=OUT/'hosted';audit=OUT/'audit';audit.mkdir()
 run('rebuild-factory-and-selection',ROOT/'code/construct.py',OUT/'construction')
 run('independent-92-kernel-controls',ROOT/'code/audit_kernel_scalar.py',OUT/'construction/SELECTED.json.gz',ROOT/'data/SELECTION.json',OUT/'KERNEL-SCALAR.json')
 kernel=read(OUT/'KERNEL-SCALAR.json');assert kernel['kernel_pivots']==92 and kernel['columns_each_orientation']==728
 run('same-partition-frontier',P/'code/audit_same_partition_frontier.py','--packets',P/'inputs/hamming','--out',OUT/'SOURCE-FRONTIER.json')
 run('scalar-and-frame-transport',P/'code/audit_and_transport.py','--raw',OUT/'construction/coalesced/FULL-WORD.json.gz','--routing',P/'inputs/data-base/split-centres/CANONICAL-WORD.json.gz','--out',local)
 run('emit-local',P/'code/emit_local.py',local)
 run('independent-local',P/'code/audit_local.py',local)
 run('normalized-wrappers',P/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'LEMMA-A.json')
 run('every-local-phase-and-endpoint',ROOT/'code/phases_full.py',local,P/'vendor/clifford')
 run('bind-unchanged-data-controller',P/'code/prepare_supplier_base.py','--data-base',P/'inputs/data-base','--local',local,'--out',base)
 run('emit-whole-owner-program',P/'code/emit_supplier_hosted.py','--base',base,'--owners',ROOT/'data/OWNERS.json.gz','--plan',ROOT/'data/PLAN.json','--out',host)
 run('independent-owner-controller-and-mutations',P/'code/audit_supplier_hosted.py',base,host,audit/'ASYNC-AUDIT.json','--mutation-controls')
 run('fresh-finite-invoice',P/'code/invoice_final.py','--base',base,'--hosted',host,'--audit',audit,'--out',audit,'--retained-invoice',P/'inputs/PR523-PREFIX-AND-INVOICE.json')
 run('two-moment-engines-and-outer',P/'code/assemble.py',audit,base,host,P/'inputs/PR493-EXPECTED.json')
 assembly=read(audit/'EXACT-ASSEMBLY.json');owners=read(audit/'OWNERS-AND-PROFILE.json');inv=read(audit/'PREFIX-AND-INVOICE.json');ph=read(local/'CLIFFORD-REVIEW.json');controls=read(audit/'ASYNC-AUDIT.json');expected=read(ROOT/'EXPECTED.json')
 result={k:assembly[k]for k in ('kappa','kappa_decimal','complex_lower','next_b_rejected','bit_lower','binding_component')}
 result.update(status='PASS_DIRECT504_KERNEL92_FINITE_WITNESS',global_profile=owners['paid_profile'],live=owners['live'],physical=owners['physical'],deficit=owners['deficit'],helper_roles=owners['hosted_residuals'],idle_remainders=owners['explicit_idle_remainder_children'],local_profile=read(local/'CANONICAL-WORD.json.gz')['local_profile'],canonical_word_sha256=sha(local/'CANONICAL-WORD.json.gz'),local_program_sha256=sha(local/'LOCAL-PROGRAMS.json.gz'),local_phase_recipe_sha256=sha(local/'CLIFFORD-RECIPES.json'),global_prefix_bits=inv['global_prefix_bits'],charged_prefix_bits=inv['charged_prefix_bits'],kernel_omission_controls=len(kernel['controls']),phase_edges=ph['directed_edges'],endpoint_adapters=ph['endpoint_adapters'])
 for k,v in expected.items():assert result[k]==v,(k,result.get(k),v)
 assert len(assembly['strict_outer_constraints'])==47 and all(s['exit_code']==0 for s in steps)
 assert ph['all_child_equalities_include_global_phase']and controls['mutation_controls_run']and len(controls['mutations_rejected'])==7
 integrity();result.update(seconds=time.monotonic()-started,python=sys.version,manifest_sha256=sha(ROOT/'MANIFEST.json'),scope='Fresh supplier construction, both arbitrary-input scalar orientations, all local phases/endpoints, residual wrappers, actual whole owners, finite invoice and exact outer composition. Pinned unchanged data controller/data phases and PR493 bit operator retained; inherited all-size and analytic interfaces remain conditional.')
 (OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 files=['RESULT.json','KERNEL-SCALAR.json','SOURCE-FRONTIER.json','local/SCALAR-FRAME-AUDIT.json','local/INDEPENDENT-LOCAL-REPLAY.json','local/CLIFFORD-REVIEW.json','local/LEMMA-A.json','audit/ASYNC-AUDIT.json','audit/OWNERS-AND-PROFILE.json','audit/IDLE-REMAINDER-FRAMES.json','audit/GLOBAL-PREFIX.json','audit/PREFIX-AND-INVOICE.json','audit/EXACT-ASSEMBLY.json']
 (OUT/'RECEIPT.json').write_text(json.dumps(dict(status=result['status'],steps=steps,artifacts={f:sha(OUT/f)for f in files},manifest_sha256=sha(ROOT/'MANIFEST.json')),indent=2)+'\n');print(result['status'],result['kappa_decimal'],flush=True)
except BaseException as e:
 (OUT/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
