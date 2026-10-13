#!/usr/bin/env python3
"""Rebuild and admit the composed-prefix witness using complete prior replays.

No baseline is rerun and no optimizer is required. PR564 sources, the prior
six-provider replay and PR569 global replay are verified before reuse. Only
new files in --work are written; the source and prior replays remain intact.
"""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parents[1]
PRIOR=RESEARCH/'larger-gain'
SOURCE_MANIFEST='dd602912d0e60c9bb2befba446629ae531ea42a9d4fecda922f98aac40762c41'
STATUS='PASS_FRESH_COMPOSED_PREFIX_MULTICOLD_REPLAY'


def require(condition,message):
    if not condition:raise ValueError(message)
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

def verify_prior_global(directory,baseline,providers):
    result,receipt=read(directory/'RESULT.json'),read(directory/'RECEIPT.json')
    require(result['status']==receipt['status']=='PASS_PORTABLE_WIDTH7_GLOBAL_REPLAY','Wrong prior global replay')
    require(Fraction(result['kappa'])==Fraction('0.001600067494703216'),'Wrong prior bound')
    require(receipt['source_manifest_sha256']==SOURCE_MANIFEST,'Wrong prior source')
    require(receipt['baseline_receipt_sha256']==sha(baseline/'RECEIPT.json') and receipt['provider_receipt_sha256']==sha(providers/'RECEIPT.json'),'Prior replay dependency mismatch')
    stages=['bind-providers','emit-owners','independent-owners','fresh-invoice','exact-assembly','admission-controls','phase-timing-controls']
    actual=[s['name']for s in receipt['steps']]
    require(actual in(stages,['six-provider-replay']+stages,['baseline564','six-provider-replay']+stages),'Incomplete prior global stages')
    require(read(directory/'STAGES.json')==receipt['steps'],'Prior global stage mismatch')
    for step in receipt['steps']:
        require(step['exit_code']==0 and sha(directory/'logs'/(step['name']+'.log'))==step['log_sha256'],'Changed prior global stage/log')
    inventory={p.relative_to(directory).as_posix():sha(p)for p in directory.rglob('*')if p.is_file()and p!=directory/'RECEIPT.json'and not p.is_relative_to(baseline)and not p.is_relative_to(providers)}
    require(receipt['artifacts']==inventory,'Prior global artifact inventory differs')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('source','baseline','prior-providers','prior-global','work'):parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args();require(__debug__,'Assertions required')
    source,baseline,providers,prior_global,work=[getattr(a,n).resolve()for n in('source','baseline','prior_providers','prior_global','work')]
    require(not work.exists() and not work.is_relative_to(source)and not work.is_relative_to(PRIOR),'Use a fresh work directory outside immutable inputs')
    pins=read(HERE/'REPRODUCTION-PINS.json')
    require(pins['source_manifest_sha256']==SOURCE_MANIFEST and pins['status']=='FROZEN_COMPOSED_PREFIX_INPUTS','Wrong input pins')
    expected_owned={'compose_prefix.py','relabel_owners.py','prefix-input/FULL-WORD.json.gz','upstream568/code/build_multicut_kernels.py','upstream568/code/audit_multicold_controls.py','upstream568/data/EIGHT-MULTICOLD.json','combined-prefix-word/ALL-KERNEL-OMISSIONS.json','combined-prefix-word/FULL-WORD.json.gz'}
    expected_owned.update('global-code/'+n for n in('bind_providers_portable.py','emit_allcold.py','audit_allcold.py','invoice_allcold.py','assemble.py','assembly_controls.py','phase_timing_controls.py'))
    expected_owned.update('combined-prefix-local/'+n for n in('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','WRAPPER-CHECKS.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json'))
    require(set(pins['owned'])==expected_owned,'Incomplete reproduction input inventory')
    expected_prior={'providers/reproduce.py','global/reproduce.py','providers/build_entrance_promotions.py','providers/width7/eight/FULL-WORD.json.gz','providers/width7/eight/RECIPES.json','global/width7/PLAN.json','global/width7/OWNERS.json.gz'}
    require(set(pins['prior'])==expected_prior,'Incomplete prior source inventory')
    for root,inventory in((HERE,pins['owned']),(PRIOR,pins['prior'])):
        for name,digest in inventory.items():require(sha(root/name)==digest,'Changed frozen input: '+name)
    local_driver=module('prior_local_reproduction',PRIOR/'providers/reproduce.py')
    global_driver=module('prior_global_reproduction',PRIOR/'global/reproduce.py')
    local_driver.verify_source(source);local_driver.verify_baseline(source,baseline)
    global_driver.verify_providers(providers,baseline)
    verify_prior_global(prior_global,baseline,providers)
    work.mkdir(parents=True);(work/'logs').mkdir();steps=[];started=time.monotonic()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
    def run(name,script,*args):
        command=[sys.executable,'-B',str(source/'code/run_portable.py'),str(script)]+list(map(str,args))
        log=work/'logs'/(name+'.log');t=time.monotonic();print('RUN',name,flush=True)
        with log.open('w')as stream:process=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env=env)
        steps.append(dict(name=name,script_sha256=sha(script),command=command,exit_code=process.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)))
        dump(work/'STAGES.json',steps)
        if process.returncode:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
        print('PASS',name,flush=True)
    b=source/'vendor/pr558';f=b/'vendor/pr552';v=f/'complex-global/vendor531';gk=f/'complex-local/static44/gk'
    run('construct-multicold',HERE/'upstream568/code/build_multicut_kernels.py','--input',baseline/'eight-cold-word/FULL-WORD.json.gz','--recipe',HERE/'upstream568/data/EIGHT-MULTICOLD.json','--gk-dir',gk,'--out',work/'multicold-word')
    run('construct-width7',PRIOR/'providers/build_entrance_promotions.py','--word',work/'multicold-word/FULL-WORD.json.gz','--gk-dir',gk,'--recipes',PRIOR/'providers/width7/eight/RECIPES.json','--out',work/'width7-word')
    word=work/'composed-word';local=work/'local'
    run('compose-prefix',HERE/'compose_prefix.py','--base',PRIOR/'providers/width7/eight/FULL-WORD.json.gz','--prefix',HERE/'prefix-input/FULL-WORD.json.gz','--combined',work/'width7-word/FULL-WORD.json.gz','--gk-dir',gk,'--out',word)
    require(sha(word/'FULL-WORD.json.gz')==sha(HERE/'combined-prefix-word/FULL-WORD.json.gz'),'Rebuilt literal word differs')
    run('all-columns-native',v/'code/audit_and_transport.py','--raw',word/'FULL-WORD.json.gz','--routing',f/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local)
    run('reflected-ledgers',v/'code/emit_local.py',local)
    run('independent-local',v/'code/audit_local.py',local)
    run('normalized-wrappers',v/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
    run('all-phase-edges',b/'code/phases_full.py',local,v/'vendor/clifford')
    run('all-kernel-omissions',HERE/'upstream568/code/audit_multicold_controls.py','--word',word/'FULL-WORD.json.gz','--recipe',HERE/'combined-prefix-word/ALL-KERNEL-OMISSIONS.json','--out',word/'ALL-KERNEL-CONTROLS.json')
    shutil.copyfile(baseline/'eight-cold-word/PROMOTION.json',word/'PROMOTION.json')
    run('rank5-omissions',b/'code/audit_promoted_scalar.py',word/'FULL-WORD.json.gz',baseline/'baseline558/reconstruction/static44/SELECTION.json',word/'RANK5-OMISSION-CONTROLS.json')
    for name in('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','WRAPPER-CHECKS.json','CLIFFORD-RECIPES.json'):
        require(sha(local/name)==sha(HERE/'combined-prefix-local'/name),'Fresh deterministic local artifact differs: '+name)
    phase=read(local/'CLIFFORD-REVIEW.json');reference=read(HERE/'combined-prefix-local/CLIFFORD-REVIEW.json')
    require({k:v for k,v in phase.items()if k!='seconds'}=={k:v for k,v in reference.items()if k!='seconds'},'Fresh phase semantics differ')
    require(phase['directed_edges']==3004 and phase['endpoint_adapters']==224 and phase['all_child_equalities_include_global_phase']is True,'Incomplete phases')
    require(len(read(local/'INDEPENDENT-LOCAL-REPLAY.json')['negative_controls_rejected'])==11,'Missing native controls')
    require(len(read(word/'ALL-KERNEL-CONTROLS.json')['controls'])==135 and len(read(word/'RANK5-OMISSION-CONTROLS.json')['controls'])==8,'Missing omission controls')
    nomination=work/'nomination';glob=work/'global';code=HERE/'global-code'
    run('relabel-owners',HERE/'relabel_owners.py','--plan',PRIOR/'global/width7/PLAN.json','--owners',PRIOR/'global/width7/OWNERS.json.gz','--local',local,'--out',nomination)
    run('bind-providers',code/'bind_providers_portable.py','--baseline',baseline/'baseline558','--plain',providers/'fourcold-eight/local','--width7',local,'--plan',nomination/'PLAN.json','--out',glob)
    run('emit-owners',code/'emit_allcold.py','--base',glob/'base','--owners',nomination/'OWNERS.json.gz','--plan',glob/'PLAN.json','--out',glob/'hosted')
    run('independent-owners',code/'audit_allcold.py',glob/'base',glob/'hosted',glob/'audit/ASYNC-AUDIT.json','--mutation-controls')
    run('fresh-invoice',code/'invoice_allcold.py','--base',glob/'base','--hosted',glob/'hosted','--audit',glob/'audit','--out',glob/'audit','--retained-invoice',v/'evidence/audit/PREFIX-AND-INVOICE.json')
    run('exact-assembly',code/'assemble.py',source,glob,glob/'ASSEMBLY.json')
    run('admission-controls',code/'assembly_controls.py','--source-package',source,'--owner',glob/'audit/OWNERS-AND-PROFILE.json','--invoice',glob/'audit/PREFIX-AND-INVOICE.json','--out',glob/'ASSEMBLY-CONTROLS.json')
    run('phase-timing-controls',code/'phase_timing_controls.py',source,glob/'base',glob/'audit',glob/'PHASE-TIMING-CONTROLS.json')
    assembly=read(glob/'ASSEMBLY.json');require(Fraction(assembly['kappa'])==Fraction('0.001600682403612293'),'Unexpected bound')
    require(assembly['conservative_kappa_decimal']=='0.001600682400830496','Unexpected conservative bound')
    require(len(read(glob/'audit/ASYNC-AUDIT.json')['mutations_rejected'])==16 and len(read(glob/'ASSEMBLY-CONTROLS.json')['rejected_controls'])==93,'Missing global controls')
    result=dict(status=STATUS,kappa=assembly['kappa'],kappa_decimal=assembly['kappa_decimal'],conservative_kappa_decimal=assembly['conservative_kappa_decimal'],gain_over_pinned569_percent=assembly['gain_over_pinned569_percent'],profile=assembly['complex_profile'],source_manifest_sha256=SOURCE_MANIFEST,prior_provider_receipt_sha256=sha(providers/'RECEIPT.json'),prior_global_receipt_sha256=sha(prior_global/'RECEIPT.json'),baseline_receipt_sha256=sha(baseline/'RECEIPT.json'),seconds=time.monotonic()-started,scope=assembly['scope'])
    dump(work/'RESULT.json',result)
    inventory={p.relative_to(work).as_posix():sha(p)for p in work.rglob('*')if p.is_file()}
    dump(work/'RECEIPT.json',dict(status=STATUS,driver_sha256=sha(Path(__file__)),pins_sha256=sha(HERE/'REPRODUCTION-PINS.json'),steps=steps,artifacts=inventory,prior_global_receipt_sha256=sha(prior_global/'RECEIPT.json'),prior_provider_receipt_sha256=sha(providers/'RECEIPT.json'),baseline_receipt_sha256=sha(baseline/'RECEIPT.json')))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
