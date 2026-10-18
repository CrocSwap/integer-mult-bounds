#!/usr/bin/env python3
"""Relocation, immutability and on-disk failure controls for this package only.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
REL = PACKAGE.relative_to(ROOT)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(root, script='verify.py', expected=None, extra=()):
    result = subprocess.run([sys.executable,'-I','-O','-B',str(root/REL/script),*extra],
                            cwd=root, capture_output=True, text=True, timeout=60)
    if expected is None:
        require(result.returncode==0, result.stdout+result.stderr)
    else:
        require(result.returncode!=0 and expected in result.stderr,
                'failure control did not reject for '+expected+': '+result.stdout+result.stderr)
    return result.stdout


def inventory(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    pins = json.loads((PACKAGE/'SOURCES.json').read_text())
    with tempfile.TemporaryDirectory(prefix='unit-phase-package-') as directory:
        root=Path(directory)
        shutil.copytree(PACKAGE,root/REL)
        for record in pins['files']:
            if record['usage']=='input':
                destination=root/record['path']
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/record['path'],destination)
        initial=inventory(root)
        run(root)
        run(root,'independent.py')
        regenerated=json.loads(run(root,extra=('--emit-certificate',)))
        certificate=root/REL/'CERTIFICATE.json'
        original=certificate.read_bytes()
        require(regenerated==json.loads(original),'relocated regeneration differs')
        require(inventory(root)==initial,'verification modified a file')
        negative=0
        for key,bad in [('minimum_complete_queries',13),('unit_triangle_paths',30239),
                        ('weighted_minimum','2*sum(c_F)+min(c_F)'),('semantic_controls',0)]:
            changed=json.loads(original)
            changed[key]=bad
            certificate.write_text(json.dumps(changed))
            run(root,expected='certificate drift')
            certificate.write_bytes(original)
            negative+=1
        changed=json.loads(original)
        changed['unit_triangle_censuses']['0:1']['row_mask_histogram']['7']=1
        certificate.write_text(json.dumps(changed))
        run(root,'independent.py',expected='unit triangle census mismatch')
        certificate.write_bytes(original)
        negative+=1
        source=root/'research/signed-connector-obstruction/CERTIFICATE.json'
        saved=source.read_bytes()
        source.write_bytes(saved+b' ')
        run(root,expected='source drift')
        source.write_bytes(saved)
        negative+=1
        require(inventory(root)==initial,'controls failed to restore copied inputs')
        all_paths=list(root.rglob('*'))
        try:
            for p in all_paths:
                p.chmod(0o555 if p.is_dir() else 0o444)
            root.chmod(0o555)
            run(root)
            run(root,'independent.py')
            require(inventory(root)==initial,'read-only replay changed contents')
        finally:
            root.chmod(0o755)
            for p in all_paths:
                if p.is_dir():
                    p.chmod(0o755)
        print('PASS_UNIT_PHASE_PACKAGE relocation=1 deterministic_regeneration=1 '
              'read_only=1 disk_rejections='+str(negative))


if __name__=='__main__':
    main()
