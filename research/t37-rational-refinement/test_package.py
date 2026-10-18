#!/usr/bin/env python3
"""Portable source-closure replay and fail-closed evidence controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


with tempfile.TemporaryDirectory(prefix='t37-refinement-package-') as directory:
    root=Path(directory)/'minimal source closure with spaces'
    root.mkdir()
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    inventory=json.loads((ROOT/'research/community-frontier942-audit/SELECTED-SOURCE.json').read_text())['files']
    for name in sorted(set(inventory)|set(manifest['sha256'])):
        destination=root/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,destination)
    package=root/'research/t37-rational-refinement'
    shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
    def replay(*args):
        return subprocess.run([sys.executable,'-I','-B',str(package/'verify.py'),*args],
                              cwd=root,capture_output=True,text=True)
    result=replay()
    need(result.returncode==0 and 'PASS_T37_RATIONAL_REFINEMENT' in result.stdout,
         'relocated full assembly failed: '+result.stderr)
    rejected=[]
    def reject(name,path,data,fragment):
        original=path.read_bytes()
        try:
            if data is None:path.unlink()
            else:path.write_bytes(data)
            result=replay()
            need(result.returncode!=0 and fragment in result.stderr,
                 'corruption accepted or failed unexpectedly: '+name+' '+result.stderr)
            rejected.append(name)
        finally:path.write_bytes(original)
    assembly=package/'ASSEMBLY.json'
    bad=json.loads(assembly.read_text());bad['kappa']=str(0)
    reject('false_bound_receipt',assembly,json.dumps(bad).encode(),'committed certificate mismatch')
    receipt=package/'CERTIFICATE.json'
    bad=json.loads(receipt.read_text());bad['controls_rejected'].pop()
    reject('omitted_control_receipt',receipt,json.dumps(bad).encode(),'committed certificate mismatch')
    reject('missing_certificate',receipt,None,'FileNotFoundError')
    engine=root/'research/e8-bit-carrier-skeleton/code/pricing/outer.py'
    reject('changed_outer_engine',engine,engine.read_bytes()+b'\n# altered\n','source pin')
    inventory_path=root/'research/community-frontier942-audit/SELECTED-SOURCE.json'
    reject('missing_selected_inventory',inventory_path,None,'FileNotFoundError')
    bad=json.loads(assembly.read_text());bad['outer']['compact_phase_layer_above_kappa']='1'
    reject('false_absorption_gap',assembly,json.dumps(bad).encode(),'committed certificate mismatch')
    output=root/'existing output';output.mkdir();sentinel=output/'sentinel';sentinel.write_text('keep\n')
    result=replay('--output',str(output))
    need(result.returncode!=0 and sentinel.read_text()=='keep\n' and
         list(output.iterdir())==[sentinel],'existing output preservation')
    rejected.append('existing_output_preserved')
    result=subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py')],
                          cwd=root,capture_output=True,text=True)
    need(result.returncode!=0 and 'Retained source assertions must stay enabled' in result.stderr,
         'optimized assertion bypass')
    rejected.append('optimized_assertion_bypass')
    print('PASS_T37_REFINEMENT_PACKAGE relocated_full_assembly=PASS controls=8')
