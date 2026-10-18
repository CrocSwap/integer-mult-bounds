"""Source-bound public replay and corruption controls in a Git-free export."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='retired-lenders-') as temp:
        root=Path(temp);p=root/'export'/'research'/HERE.name
        shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__'))
        elsewhere=root/'elsewhere';elsewhere.mkdir()
        def run(*args):
            return subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py'),*args],
                cwd=elsewhere,text=True,capture_output=True,timeout=120)
        before=inventory(root);r=run()
        need(r.returncode==0 and 'PASS_RETIRED_LENDER_EXHAUSTION' in r.stdout,'relocated CLI '+r.stderr)
        need(inventory(root)==before,'read-only public replay')
        source=p/'predecessor/PR2526-base.json.gz';raw=source.read_bytes()
        source.write_bytes(raw+b'changed')
        r=run();need(r.returncode!=0 and 'source SHA256 predecessor/PR2526-base.json.gz' in r.stderr,'changed word source')
        source.write_bytes(raw)
        receipt=p/'RESULT.json';raw=receipt.read_bytes();data=json.loads(raw)
        data['words']['base']['maximum_matching_size']='2';receipt.write_text(json.dumps(data))
        r=run();need(r.returncode!=0 and 'typed receipt mismatch' in r.stderr,'typed receipt control')
        receipt.write_bytes(raw)
        r=run('--write');need(r.returncode!=0 and 'FileExistsError' in r.stderr and receipt.read_bytes()==raw,'exclusive receipt output')
        need(inventory(root)==before,'restored export')
    print('PASS_RETIRED_LENDER_INTEGRITY readonly_export source typed_receipt exclusive_output')


if __name__=='__main__':main()
