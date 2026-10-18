"""Git-free relocation and real on-disk source/proof/receipt corruption tests."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

P=Path(__file__).resolve().parent


def run(path):
    return subprocess.run([sys.executable,'-I','-O','-B',str(path/'verify.py')],
                          cwd=path,capture_output=True,encoding='utf-8',timeout=45)


with tempfile.TemporaryDirectory(prefix='fintm2-integrity-') as tmp:
    p=Path(tmp)/'package'
    shutil.copytree(P,p,ignore=shutil.ignore_patterns('*.olean','*.ilean','__pycache__'))
    result=run(p)
    if result.returncode:
        raise RuntimeError('relocated positive failed: '+result.stdout+result.stderr)
    cases=[('source/Computable.lean',lambda raw:raw+b'\n'),
           ('Extracted.lean',lambda raw:raw.replace(b'stepAux q (a v) S',b'stepAux q v S')),
           ('Closure.lean',lambda raw:raw.replace(b'1 + depth q',b'0 + depth q')),
           ('RESULT.json',lambda raw:raw.replace(b'1533',b'1534'))]
    rejected=[]
    for name,mutation in cases:
        file=p/name
        original=file.read_bytes();changed=mutation(original)
        if changed==original:
            raise RuntimeError('mutation did not alter '+name)
        file.write_bytes(changed)
        result=run(p)
        if result.returncode==0 or file.read_bytes()!=changed:
            raise RuntimeError('accepted or overwrote corruption: '+name)
        rejected.append(name)
        file.write_bytes(original)
    print(json.dumps({'status':'PASS_GIT_FREE_RELOCATION_AND_REAL_CORRUPTIONS_NOT_KERNEL',
                      'rejected':rejected}))
