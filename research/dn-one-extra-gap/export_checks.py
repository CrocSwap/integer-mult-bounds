# SPDX-License-Identifier: Apache-2.0
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent


def need(ok,message):
    if not ok:
        raise ValueError(message)


def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run(package,extra=()):
    return subprocess.run([sys.executable,'-I','-O','-B',str(package/'check.py'),*map(str,extra)],
                          cwd=package,capture_output=True,text=True,timeout=180)


def main():
    with tempfile.TemporaryDirectory(prefix='dn-extra-export-') as td:
        root=Path(td);p=root/'research'/HERE.name
        shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            dest=root/row['path'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/row['path'],dest)
        before=hashes(root)
        need(run(p).returncode == 0,'Git-free optimized replay')
        need(hashes(root) == before,'read-only replay')
        result=p/'RESULT.json';raw=result.read_bytes();receipt=json.loads(raw)
        receipt['supplier_admitted']=0;result.write_text(json.dumps(receipt))
        attempt=run(p)
        need(attempt.returncode != 0 and 'typed receipt mismatch' in attempt.stderr,'typed receipt control')
        result.write_bytes(raw)
        source=p/'references/PR2518-search.py';original=source.read_bytes()
        source.write_text('raise RuntimeError("EXECUTED_UNAUTHENTICATED")\n')
        attempt=run(p)
        need(attempt.returncode != 0 and 'source SHA256 mismatch' in attempt.stderr and 'EXECUTED_UNAUTHENTICATED' not in attempt.stderr,'source before AST')
        source.write_bytes(original)
        attempt=run(p,['--emit',result])
        need(attempt.returncode != 0 and result.read_bytes() == raw,'overwrite refusal')
        need(hashes(root) == before,'control restoration')
    print('PASS_DN_ONE_EXTRA_EXPORT: Git-free optimized, read-only, typed receipt, source-before-AST, overwrite')


if __name__ == '__main__':
    main()
