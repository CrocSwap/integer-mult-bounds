#!/usr/bin/env python3
"""Offline relocation and proof-relevant mutation controls; no repository writes."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
FILES=['program.py','verify.py','independent.py','full_census.py','CERTIFICATE.json','SOURCES.json']


def require(ok,message):
    if not ok:
        raise ValueError(message)


def snapshot(directory):
    return {str(p.relative_to(directory)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def copy_package(destination):
    destination.mkdir()
    for name in FILES:
        shutil.copyfile(ROOT/name,destination/name)
    shutil.copytree(ROOT/'references',destination/'references')


def run(directory,optimized=True):
    command=[sys.executable,'-I','-B']+(['-O'] if optimized else [])+[str(directory/'verify.py')]
    return subprocess.run(command,cwd=directory.parent,text=True,capture_output=True,timeout=30)


def change_json(directory,name,mutation):
    file=directory/name
    data=json.loads(file.read_text())
    mutation(data)
    file.write_text(json.dumps(data))


def change_code(directory,name,old,new):
    file=directory/name
    text=file.read_text()
    require(text.count(old)==1,'ambiguous mutation anchor')
    file.write_text(text.replace(old,new))


def main():
    mutations={
        'receipt_dropped_restore':lambda d:change_json(d,'CERTIFICATE.json',
            lambda j:j['seed_fixture']['schedules']['borrowed']['word'].pop()),
        'receipt_underpriced_read':lambda d:change_json(d,'CERTIFICATE.json',
            lambda j:j['seed_fixture']['schedules']['borrowed']['invoice_L3'].__setitem__('source_reads',0)),
        'receipt_census':lambda d:change_json(d,'CERTIFICATE.json',
            lambda j:j['minimum_word_census'].__setitem__('two_source_minimum_words',76033)),
        'source_pin':lambda d:change_json(d,'SOURCES.json',
            lambda j:j['references'][0].__setitem__('sha256','0'*64)),
        'source_commit_metadata':lambda d:change_json(d,'SOURCES.json',
            lambda j:j['references'][0].__setitem__('commit','0'*40)),
        'source_bytes':lambda d:(d/'references'/'PR982-PROOF.md').write_text('corrupt reference\n'),
        'missing_final_cleanup':lambda d:change_code(d,'program.py',
            'return word + before + load + inverse(before) + inverse(load)',
            'return word + before + load + inverse(before)'),
        'unpaid_head_return':lambda d:change_code(d,'program.py','travel += cursor','travel += 0'),
        'wrong_leaf_recurrence':lambda d:change_code(d,'program.py',
            'return 2 * leaf_count(n // 2) + 2 * leaf_count(n - n // 2)',
            'return 2 * leaf_count(n // 2) + leaf_count(n - n // 2)'),
        'full_census_wrong_source':lambda d:change_code(d,'full_census.py',
            "(1, 'D', 1, 2), (-1, 'D', 1, 2)",
            "(1, 'D', 0, 2), (-1, 'D', 0, 2)"),
    }
    with tempfile.TemporaryDirectory(prefix='rectangular-batch-') as td:
        temp=Path(td)
        clean=temp/'clean'
        copy_package(clean)
        before=snapshot(clean)
        normal=run(clean,False)
        optimized=run(clean,True)
        require(normal.returncode==0,normal.stderr)
        require(optimized.returncode==0,optimized.stderr)
        require(normal.stdout==optimized.stdout,'normal/optimized output differs')
        require(before==snapshot(clean),'read-only replay changed package files')
        for name,mutate in mutations.items():
            destination=temp/name
            copy_package(destination)
            mutate(destination)
            completed=run(destination)
            require(completed.returncode!=0,'accepted corruption '+name)
            require('ValueError' in completed.stderr,'unexpected failure '+name+': '+completed.stderr)
    print('PASS_RECTANGULAR_PACKAGE offline_relocation=PASS normal_optimized=PASS mutations=10')


if __name__=='__main__':
    main()
