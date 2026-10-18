#!/usr/bin/env python3
"""Git-free, optimized and failure-path public CLI controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent


def require(x,message):
    if not x:raise ValueError(message)


def snapshot(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run(package,*extra):
    return subprocess.run([sys.executable,'-I','-B','-O',str(package/'verify.py'),*extra],
                          cwd=package.parent,capture_output=True,text=True,timeout=300)


def main():
    with tempfile.TemporaryDirectory(prefix='dn-unrestricted-export-') as tmp:
        root=Path(tmp)
        package=root/'research'/HERE.name
        shutil.copytree(HERE,package)
        before=snapshot(root)
        result=run(package)
        require(result.returncode==0 and 'PASS_DN_UNRESTRICTED_ROOT_CODE_FLOOR' in result.stdout,'optimized Git-free replay: '+result.stderr)
        require(snapshot(root)==before,'read-only export')
        result=run(package,'--output',str(package/'RESULT.json'))
        require(result.returncode!=0 and 'output already exists' in result.stderr,'overwrite rejection')
        source=package/'references/PR2518-search.py'
        saved=source.read_bytes();source.write_bytes(saved+b'\nraise RuntimeError("must not execute")\n')
        result=run(package)
        require(result.returncode!=0 and 'source SHA256:' in result.stderr and 'must not execute' not in result.stderr,'source fails before extraction')
        source.write_bytes(saved)
        receipt=package/'RESULT.json';saved=receipt.read_bytes();bad=json.loads(saved)
        bad['binary_code_checks'][0]['binary_rank']=float(bad['binary_code_checks'][0]['binary_rank'])
        receipt.write_text(json.dumps(bad),encoding='utf-8')
        result=run(package)
        require(result.returncode!=0 and 'typed receipt mismatch' in result.stderr,'typed receipt rejection')
        receipt.write_bytes(saved)
        require(snapshot(root)==before,'mutants restored')
    print('PASS_DN_GITFREE_EXPORT: optimized read-only; source, typed receipt and overwrite controls')


if __name__=='__main__':main()
