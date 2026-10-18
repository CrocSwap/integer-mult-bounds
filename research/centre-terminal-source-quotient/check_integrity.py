"""Git-free public replay plus real source and typed-receipt rejection."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def main():
    with tempfile.TemporaryDirectory(prefix='centre-terminal-integrity-') as temp:
        root=Path(temp);package=root/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']=='input':
                target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],target)
        def run(success,marker):
            cp=subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py')],cwd=root,
                              text=True,capture_output=True,timeout=120)
            if (cp.returncode==0)!=success or marker not in cp.stdout+cp.stderr:
                raise ValueError(repr((cp.returncode,cp.stdout,cp.stderr)))
        run(True,'PASS_CENTRE_TERMINAL_SOURCE_QUOTIENT')
        archive=root/'research/community-frontier1094-audit/selected-replay.tar.gz'
        original=archive.read_bytes()
        archive.write_bytes(bytes([original[0]^1])+original[1:])
        run(False,'source hash mismatch')
        archive.write_bytes(original)
        receipt=package/'RESULT.json';original_receipt=receipt.read_bytes()
        changed=json.loads(original_receipt);changed['no_native_lift_or_physical_saving_claim']=1
        receipt.write_text(json.dumps(changed),encoding='utf-8')
        run(False,'typed receipt mismatch')
        receipt.write_bytes(original_receipt)
        if archive.read_bytes()!=original or receipt.read_bytes()!=original_receipt:
            raise ValueError('export restoration mismatch')
    print('PASS_CENTRE_TERMINAL_INTEGRITY git_free=1 source_rejections=1 receipt_rejections=1')

if __name__=='__main__':main()
