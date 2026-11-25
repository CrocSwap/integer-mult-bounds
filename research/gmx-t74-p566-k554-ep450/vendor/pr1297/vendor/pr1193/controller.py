"""Run the retained emitted-controller checks and bind their final receipts."""
from fractions import Fraction
import os,subprocess,sys,time
from common import P,ROOT,read,dump,sha

def replay(work,providers,discovery=False):
    source=ROOT/'research/complex-k492-owner-repair/vendor/multicold'
    code=work/'runtime/code';spec=work/'runtime/data/SPEC.json'
    mode='discovery'if discovery else'strict';out=work/mode;out.mkdir();g=out/'global'
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',
      MULTICOLD_SOURCE=str(source),GAIN_PR564_SOURCE=str(source),WITNESS_SPEC=str(spec))
    for k in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD'):env.pop(k,None)
    if discovery:env.update(WITNESS_DISCOVER='1',WITNESS_RECORD=str(out/'WITNESS-RECORD.jsonl'))
    stages=[]
    def run(name,script,*args):
        start=time.monotonic();log=out/(name+'.log')
        with log.open('w')as f:r=subprocess.run([sys.executable,'-B',str(source/'code/run_portable.py'),str(code/script),*map(str,args)],env=env,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,exit_code=r.returncode,seconds=round(time.monotonic()-start,3),log_sha256=sha(log)))
        dump(out/'STAGES.json',stages)
        if r.returncode:raise RuntimeError(name+'\n'+log.read_text()[-6000:])
        print('PASS',mode,name,flush=True)
    provider_args=[arg for pid,local in sorted(providers.items()) for arg in ('--provider',pid+'='+str(local))]
    run('bind','bind_providers_portable.py','--baseline',work/'parent',*provider_args,'--plan',work/'lift/PLAN.json','--out',g)
    run('emit','emit_allcold.py','--base',g/'base','--owners',P/'data/OWNERS.json.gz','--plan',g/'PLAN.json','--out',g/'hosted')
    run('audit','audit_allcold.py',g/'base',g/'hosted',g/'audit/ASYNC-AUDIT.json','--mutation-controls')
    run('invoice','invoice_allcold.py','--base',g/'base','--hosted',g/'hosted','--audit',g/'audit','--out',g/'audit','--retained-invoice',source/'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json')
    run('assembly','assemble.py',source,g,out/'ASSEMBLY.json')
    if discovery:
        run('freeze','freeze_spec.py','--spec',spec,'--discovery',out)
        return read(out/'ASSEMBLY.json')
    for name,script,target in [('admission-controls','assembly_controls.py','ADMISSION-CONTROLS.json'),('bit-controls','bit_supplier_controls.py','BIT-CONTROLS.json')]:
        run(name,script,'--source-package',source,'--owner',g/'audit/OWNERS-AND-PROFILE.json','--invoice',g/'audit/PREFIX-AND-INVOICE.json','--out',out/target)
    asm=read(out/'ASSEMBLY.json');owner=read(g/'audit/OWNERS-AND-PROFILE.json')
    invoice=read(g/'audit/PREFIX-AND-INVOICE.json');audit=read(g/'audit/ASYNC-AUDIT.json')
    ac=read(out/'ADMISSION-CONTROLS.json');bc=read(out/'BIT-CONTROLS.json');claim=read(P/'CLAIM.json')
    for k in ('kappa','kappa_decimal','complex_lower','bit_lower','complex_profile'):assert asm[k]==claim[k],k
    for k in ('live','physical','rank_mass','deficit'):assert owner[k]==claim[k],k
    assert owner['hosted_residuals']==audit['complex_hosted_residuals']==claim['roles']==159840
    assert audit['complete_invocations']==invoice['complete_invocation_sweeps']==333
    assert invoice['global_prefix_bits']==775 and invoice['charged_prefix_bits']==1024
    assert invoice['finite']['physical_row_coefficient']==17495<invoice['finite']['retained_row_coefficient']==20161
    assert invoice['strict_checks'] and all(invoice['strict_checks'].values())
    assert len(asm['outer'])==47 and all(Fraction(v)>0 for v in asm['outer'].values())
    assert not ac['discovery_accepted_controls'] and len(ac['rejected_controls'])==114
    assert len(bc['rejected_controls'])==12 and bc['derived_deficit']==10272
    assert audit['mutation_controls_run'] and len(audit['mutations_rejected'])==23
    assert asm['template_sha256']==owner['template_sha256']==invoice['template_sha256']
    assert invoice['owner_audit_sha256']==sha(g/'audit/OWNERS-AND-PROFILE.json')
    assert invoice['controller_audit_sha256']==sha(g/'audit/ASYNC-AUDIT.json')
    for pid,local in providers.items():
        for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json'):
            assert read(g/'base/providers'/pid/name)==read(local/name),'Fresh provider binding: '+pid+'/'+name
    return dict(status='PASS_MIXED_DEMOTIONS_T37_STRICT_CONTROLLER',kappa=asm['kappa'],kappa_decimal=asm['kappa_decimal'],
      complex_profile=asm['complex_profile'],roles=159840,calls=333,prefix_bits=775,row_coefficient=17495,
      controls=dict(admission=114,bit_supplier=12,controller=23),scope=claim['scope'],stages=stages)
