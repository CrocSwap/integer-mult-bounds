#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Bind a completed strict candidate admission to the pinned PR2374 outer.

The global supplier must already have passed. No discovery receipt is accepted.
Uses original PR1297 parent admission and fresh candidate admission; it does
not assume that the failed PR2269 aggregate completed.
"""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from fractions import Fraction as Q
from pathlib import Path
from check_endpoints import CASE,RESEARCH,NATIVE,CONSERVATIVE,PROFILE_PIN

HERE=Path(__file__).resolve().parent
PARENT=RESEARCH/'anticipatory-stage-evidence/parent'
PINNED={
 'check_ledger.py':(CASE.parent/'PR2374-check_ledger.py','9e12909c73d3b3a31a45d801ae76c034510d6306400412e474df79bc4f1dc67e'),
 'independent_check.py':(CASE.parent/'global-admission/outer-screen/PR2374-independent_check.py','a5a0361539ec7cae9eb6c0371f857919335a1720040f22af291aa3e34fc864c7'),
 'check_gaugefree.py':(CASE.parent/'global-admission/outer-screen/PR2374-check_gaugefree.py','2957d2aafc56e3b757c5734bb29c3258cdf0ab167bd06ee0daf95281b5207e10'),
 'struct_check.py':(CASE.parent/'global-admission/outer-screen/PR2374-struct_check.py','f1df92bb6247034a22e141dcb39c1e8b6b9df6eb9791493be25a3911f7add8d4'),
}

def rd(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,indent=2)+'\n')
def validate_stages(work,result,key):
 stages=rd(work/'STAGES.json')
 assert result[key]==stages and stages
 for stage in stages:
  assert stage['exit_code']==0
  assert sha(work/(stage['name']+'.log'))==stage['log_sha256'],stage['name']
 return stages


def main():
 if not __debug__:raise RuntimeError('Assertions required')
 sys.set_int_max_str_digits(0)
 ap=argparse.ArgumentParser();ap.add_argument('--strict',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
 ap.add_argument('--parent-admission',type=Path,default=CASE.parent/'global-admission/retained-pr1297')
 a=ap.parse_args();strict=a.strict.resolve();out=a.out.resolve();prior=a.parent_admission.resolve()
 assert not out.exists(),'fresh output directory required'
 # Verify original immutable supplier source tree, not a repaired output tree.
 old=PARENT/'vendor/pr1297';manifest=rd(old/'MANIFEST.json')
 actual={p.relative_to(old).as_posix() for p in old.rglob('*') if p.is_file() and p!=old/'MANIFEST.json' and '__pycache__' not in p.parts}
 assert actual==set(manifest)
 for name,h in manifest.items():assert sha(old/name)==h,name
 pr=rd(prior/'RESULT.json')
 assert pr['status']=='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
 assert pr['kappa']==rd(old/'CLAIM.json')['kappa']
 assert (pr['admission_controls'],pr['bit_controls'],pr['controller_controls'],pr['independent_owner_controls'],pr['outer_inequalities'])==(114,12,15,8,47)
 prior_stages=validate_stages(prior,pr,'stages')
 result=rd(strict/'RESULT.json');assembly=rd(strict/'ASSEMBLY.json')
 assert result['status']=='PASS_STRICT_COMPOSED_FOUR428_GLOBAL_AND_OUTER_ADMISSION','discovery is not admission'
 strict_stages=validate_stages(strict,result,'steps')
 assert [x['name'] for x in strict_stages]==['bind','emit','audit','invoice','assembly','admission','bit','independent']
 assert len(rd(strict/'ADMISSION-CONTROLS.json')['rejected_controls'])==114
 assert len(rd(strict/'BIT-CONTROLS.json')['rejected_controls'])==12
 assert len(rd(strict/'INDEPENDENT.json')['controls_rejected'])==8
 controller=rd(strict/'global/audit/ASYNC-AUDIT.json')
 assert len(controller['mutations_rejected'])==21 and len(controller['buffer_controls_rejected'])==6
 assert len(rd(strict.parent/'GEOMETRY-CONTROLS.json')['rejected'])==6
 invoice=rd(strict/'global/audit/PREFIX-AND-INVOICE.json');owner=rd(strict/'global/audit/OWNERS-AND-PROFILE.json')
 assert invoice['status']=='PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE'
 assert invoice['private_zero_buffers']==76 and invoice['physical']==66818
 assert all(invoice['strict_checks'].values()) and len(invoice['strict_checks'])==9
 assert invoice['buffer_binding_sha256']==owner['buffer_binding_sha256'] and len(owner['buffer_controls_rejected'])==6
 assert assembly['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY'
 assert len(assembly['outer'])==47 and all(Q(v)>0 for v in assembly['outer'].values())
 assert Q(assembly['complex_lower'])==NATIVE and Q(assembly['conservative_complex_lower'])==CONSERVATIVE
 assert Q(assembly['bit_lower'])==Q('0.001733427039589844234749')
 assert assembly['kappa']==result['kappa']
 spec=rd(strict/'runtime/data/SPEC.json')
 assert Q(spec['expected']['complex_lower'])==NATIVE
 assert Q(spec['expected']['kappa'])==Q(assembly['kappa'])
 H=rd(CASE/'budget/RESTRICTED-PROFILE.json')
 assert sha(CASE/'budget/RESTRICTED-PROFILE.json')==PROFILE_PIN
 assert H==assembly['complex_profile']==spec['expected']['global_profile']==owner['paid_profile']
 assert invoice['owner_audit_sha256']==sha(strict/'global/audit/OWNERS-AND-PROFILE.json')
 assert assembly['input_sha256']['owner_audit']==sha(strict/'global/audit/OWNERS-AND-PROFILE.json')
 assert assembly['input_sha256']['fresh_invoice']==sha(strict/'global/audit/PREFIX-AND-INVOICE.json')
 # Each inherited outer file is bound to the original package manifest.
 source_manifest=rd(PARENT/'MANIFEST.json');sources={}
 for p in (PARENT/'outer').iterdir():
  if p.is_file():assert sha(p)==source_manifest['outer/'+p.name],p
 for name,(path,digest) in PINNED.items():assert sha(path)==digest,name
 out.mkdir(parents=True);(out/'new').mkdir()
 shutil.copytree(PARENT/'outer',out/'outer')
 (out/'vendor').symlink_to((PARENT/'vendor').resolve(),target_is_directory=True)
 for name,(path,digest) in PINNED.items():shutil.copyfile(path,out/'outer'/name)
 for name in ('LEDGER.json','INDEPENDENT.json','OUTER-CLAIM.json'):(out/'outer'/name).unlink()
 dump(out/'new/SPEC.json',spec)
 dump(out/'CLAIM.json',{'status':'STRICT_SUPPLIER_INPUT_TO_OUTER','kappa':assembly['kappa'],'kappa_decimal':assembly['kappa_decimal'],'strict_result_sha256':sha(strict/'RESULT.json')})
 D=spec['outer_refinement']['endpoint_digits'];assert D==24
 C=Q(assembly['complex_lower']);R=Q(1,10**(D+80))
 dump(out/'outer/B.json',{'b':str(C-R),'b_above_endpoint':str(C+Q(1,10**D)),'profile':H,'live':66304})
 steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None)
 def run(name,script,*args):
  t=time.monotonic()
  with (out/(name+'.log')).open('w') as log:
   p=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],env=env,stdout=log,stderr=subprocess.STDOUT)
  steps.append({'name':name,'exit_code':p.returncode,'seconds':time.monotonic()-t,'log_sha256':sha(out/(name+'.log'))})
  dump(out/'STAGES.json',steps)
  assert p.returncode==0,(name,(out/(name+'.log')).read_text()[-4000:])
  print('PASS',name,flush=True)
 run('ledger',out/'outer/check_ledger.py')
 run('independent-balance',out/'outer/independent_check.py')
 run('outer-fresh-regeneration-and-evidence',out/'outer/run_outer.py',out/'replay')
 ledger=rd(out/'outer/LEDGER.json');ind=rd(out/'outer/INDEPENDENT.json')
 row=ledger['rows']['struct_boundary_radix_union'];K=Q(row['kappa']['rational'])
 assert K==C-Q(1,10**(D+46))-Q(1,10**(D+22))
 assert K==Q(row['kappa']['decimal'])==Q(ind['rows']['struct_boundary_radix_union']['kappa'])
 assert len(row['strict_checks'])==63 and len(ledger['rejecting_controls']['struct_boundary_radix_union'])==17
 comparison=rd(CASE/'vendor/outer/OUTER-CLAIM.json');oldK=Q(comparison['kappa']);assert K>oldK
 inputs={str(p):sha(p) for p in [strict/'RESULT.json',strict/'ASSEMBLY.json',strict/'runtime/data/SPEC.json',prior/'RESULT.json',prior/'STAGES.json',old/'MANIFEST.json']}
 source_pins={name:digest for name,(_,digest) in PINNED.items()}
 receipt={'status':'PASS_STRICT_CANDIDATE_FINITE_AND_OUTER_ARITHMETIC_CONDITIONAL_BOUND',
 'kappa':str(K),'kappa_decimal':row['kappa']['decimal'],'gain_over_pinned_pr2435':str(K-oldK),
 'comparison_head':'324d7d3590dc21003940a44cb0cbdc32b3620f25','strict_supplier':str(strict),'original_parent_admission':str(prior),
 'original_parent_stages_checked':len(prior_stages),'strict_supplier_stages_checked':len(strict_stages),
 'input_sha256':inputs,'outer_source_commit':'5449da65da12bdfd94675dccc38731eaa91e93b6','outer_source_sha256':source_pins,
 'outer_inequalities':63,'outer_mutants_rejected':17,'supplier_independent_evidence_replays':19,
 'stages':steps,'scope':'Conditional bound from fresh strict supplier admission plus exact outer ledger and retained evidence. All-size compiler, mutable-source/common-label realization, whole-call hosting, precision/tape, exact recovery, PR559 correction, PR589 bit H1-H5, prime theorem, and written gauge-free/locality/outer-transfer assumptions remain inherited. No unconditional theorem or machine formalization is claimed. PR2269 aggregate failure is not represented as a pass.'}
 dump(out/'OUTER-ADMISSION.json',receipt)
 dump(out/'outer/OUTER-CLAIM.json',{'status':receipt['status'],'kappa':receipt['kappa_decimal'],'kappa_rational':str(K),'admission_receipt_sha256':sha(out/'OUTER-ADMISSION.json')})
 print(receipt['status']);print(receipt['kappa_decimal'])

if __name__=='__main__':main()
