"""Public CLI relocation and source/receipt failure controls."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok, why):
    if not ok:raise ValueError(why)


def inventory(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='connector-tariff-') as temp:
        root=Path(temp);package=root/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']!='input':continue
            dest=root/row['path'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/row['path'],dest)
        elsewhere=root/'elsewhere';elsewhere.mkdir()
        def run(*extra):
            return subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py'),*extra],
                                  cwd=elsewhere,capture_output=True,text=True,timeout=120)
        before=inventory(root);result=run()
        need(result.returncode==0 and 'PASS_CONNECTOR_READ_TRANSFER_TARIFF' in result.stdout,'relocated CLI '+result.stderr)
        need(inventory(root)==before,'replay is read-only')
        source=package/'predecessor/PR2538-synth.py';original=source.read_bytes()
        source.write_bytes(original+b'\nraise RuntimeError("UNAUTHENTICATED_CODE_RAN")\n')
        result=run()
        need(result.returncode!=0 and 'source SHA256 predecessor/PR2538-synth.py' in result.stderr
             and 'UNAUTHENTICATED_CODE_RAN' not in result.stderr,'reject changed source before executing it')
        source.write_bytes(original)
        receipt=package/'RESULT.json';original=receipt.read_bytes();value=json.loads(original)
        value['complete_states']='830';receipt.write_text(json.dumps(value),encoding='utf-8')
        result=run();need(result.returncode!=0 and 'complete typed receipt mismatch' in result.stderr,'typed receipt failure')
        receipt.write_bytes(original)
        result=run('--write',str(receipt))
        need(result.returncode!=0 and 'FileExistsError' in result.stderr and receipt.read_bytes()==original,'exclusive output')
        need(inventory(root)==before,'integrity export restored')
    print('PASS_CONNECTOR_TARIFF_INTEGRITY relocated_readonly source_before_execution typed_receipt exclusive_output')


if __name__=='__main__':main()
