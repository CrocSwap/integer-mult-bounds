#!/usr/bin/env python3
"""Portable reproduction and evidence-corruption controls. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(condition,message):
    if not condition: raise ValueError(message)


with tempfile.TemporaryDirectory(prefix='hadamard-package-') as directory:
    root = Path(directory)/'standalone package with spaces'
    shutil.copytree(HERE,root,ignore=shutil.ignore_patterns('__pycache__'))
    def replay(*args):
        return subprocess.run([sys.executable,'-I','-O','-B',str(root/'verify.py'),*args],
                              cwd=directory,capture_output=True,text=True)
    result = replay('--replay-search')
    need(result.returncode==0 and 'PASS_SIGNED_HADAMARD_BATCH' in result.stdout,
         'standalone replay: '+result.stderr)
    rejected=[]
    def reject(name,path,content,fragment):
        original=path.read_bytes()
        try:
            if content is None: path.unlink()
            else: path.write_bytes(content)
            result=replay()
            need(result.returncode!=0 and fragment in result.stderr,
                 'unexpected corruption result: '+name+' '+result.stderr)
            rejected.append(name)
        finally: path.write_bytes(original)
    construction=root/'CONSTRUCTION.json'
    bad=json.loads(construction.read_text());bad['word'][0][2]*=-1
    reject('wrong_readout_sign',construction,json.dumps(bad).encode(),'output dirt cancellation')
    bad=json.loads(construction.read_text());bad['A_lengths'][3]=4
    reject('unpaid_product_length',construction,json.dumps(bad).encode(),'product interface binding')
    bad=json.loads(construction.read_text());bad['query_calls']=21
    reject('false_query_invoice',construction,json.dumps(bad).encode(),'query invoice')
    reject('duplicate_key',construction,
           construction.read_text().replace('{','{"assignment_seed":55,',1).encode(),'duplicate JSON key')
    certificate=root/'CERTIFICATE.json'
    bad=json.loads(certificate.read_text())
    bad['schedules']['candidate']['dense'][0]['tape_travel_word_slots']-=1
    reject('unpaid_head_travel',certificate,json.dumps(bad).encode(),'certificate mismatch')
    reject('missing_certificate',certificate,None,'FileNotFoundError')
    notice=root/'vendor/PR944-NOTICE.md'
    reject('changed_predecessor',notice,notice.read_bytes()+b' ','predecessor pin')
    output=root/'existing output';output.mkdir();sentinel=output/'sentinel';sentinel.write_text('keep\n')
    result=replay('--output',str(output))
    need(result.returncode!=0 and 'output already exists' in result.stderr and
         sentinel.read_text()=='keep\n' and list(output.iterdir())==[sentinel],
         'existing output was not preserved')
    rejected.append('existing_output_preserved')
    print('PASS_SIGNED_HADAMARD_PACKAGE standalone_optimized_replay=PASS controls=8')
