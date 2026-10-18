#!/usr/bin/env python3
"""Actual entry-point defect controls and Git-free read-only replay.
Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import gzip
import json
from pathlib import Path
import shutil
import runpy
import struct
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def invoke(path,script='verify.py',expected=None,extra=()):
    r=subprocess.run([sys.executable,'-I','-O','-B',str(path/script),*extra],cwd='/',capture_output=True,text=True,timeout=180)
    combined=r.stdout+r.stderr
    if expected is None:
        need(r.returncode==0,combined)
    else:
        need(r.returncode!=0 and expected in combined,'wrong control outcome: '+combined)
    return combined


def hashes(path):
    return {str(f.relative_to(path)):hashlib.sha256(f.read_bytes()).hexdigest() for f in path.rglob('*') if f.is_file()}


def main():
    controls=[]
    with tempfile.TemporaryDirectory(prefix='r439-sprint-package-') as tmp:
        root=Path(tmp)/'export';p=root/'research'/HERE.name
        shutil.copytree(HERE,p)
        source_paths=[pin['path'] for pin in json.loads((HERE/'SOURCES.json').read_text())['files'] if pin['usage']=='input']
        for rel in source_paths:
            dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
        before=hashes(root)
        directories=[root,*[x for x in root.rglob('*') if x.is_dir()]]
        try:
            for f in root.rglob('*'):
                if f.is_file():f.chmod(0o444)
            for d in reversed(directories):d.chmod(0o555)
            records_path=Path(tmp)/'candidate-records'
            invoke(p,extra=('--output',str(records_path)));invoke(p,'independent.py')
            oracle=runpy.run_path(str(p/'independent.py'))
            source_word=json.loads(gzip.decompress((root/'research/r439-bsection-stars-seed01/candidate.json.gz').read_bytes()))
            fixed_witness=json.loads((p/'WITNESS.json').read_text())
            events,_=oracle['make_stream'](source_word,fixed_witness)
            independent_records=oracle['native_records'](events)
            primary_records=list(struct.iter_unpack('<6i',(records_path/'records.bin').read_bytes()))
            need(independent_records==primary_records,'complete independent literal record mismatch')
            controls.append('all13990 literal records match independent reconstruction exactly')
            need(hashes(root)==before,'read-only relocation changed evidence')
        finally:
            for d in directories:d.chmod(0o755)
            for f in root.rglob('*'):
                if f.is_file():f.chmod(0o644)
        controls.append('both optimized engines pass read-only Git-free relocation; all file hashes unchanged')
        def edit_file(path,raw,expected,script='verify.py'):
            old=path.read_bytes()
            try:
                path.write_bytes(raw);invoke(p,script,expected)
            finally:path.write_bytes(old)
        word=root/'research/r439-bsection-stars-seed01/candidate.json.gz'
        edit_file(word,word.read_bytes()+b'\0','source SHA256')
        controls.append('changed immutable word bytes reject at primary source pin')
        cert=p/'WITNESS.json';x=json.loads(cert.read_text());x['taps'][-1][0]=0
        edit_file(cert,(json.dumps(x)+'\n').encode(),'tap response')
        controls.append('wrong cut in consumed witness rejects')
        x=json.loads(cert.read_text());x['expected_scatter_adds']=87
        edit_file(cert,(json.dumps(x)+'\n').encode(),'claimed scatter ADDs')
        controls.append('false stronger scatter claim rejects')
        result=p/'RESULT.json';x=json.loads(result.read_text());x['schedules']['interleaved88']['B']-=1
        edit_file(result,(json.dumps(x)+'\n').encode(),'fixed result receipt mismatch')
        controls.append('underreported reverse envelope rejects')
        for filename in ('WITNESS.json','RESULT.json'):
            path=p/filename;raw=path.read_bytes();path.unlink()
            try:invoke(p,expected='FileNotFoundError')
            finally:path.write_bytes(raw)
            controls.append('missing '+filename+' rejects')
        script=p/'verify.py';raw=script.read_bytes()
        guard=b"require(actual==wanted, 'tap response differs from required column')"
        need(raw.count(guard)==1,'guard-removal target not unique')
        edit_file(script,raw.replace(guard,b'pass  # deliberate omitted tap guard'), 'control accepted: omitted tap')
        controls.append('actual tap-guard deletion makes named rejection control fail')
        need(hashes(root)==before,'controls did not restore exported evidence')
    print('PASS_R439_INTERLEAVING_PACKAGE_CONTROLS groups='+str(len(controls)))
    print(json.dumps(controls,indent=2))


if __name__=='__main__':main()
