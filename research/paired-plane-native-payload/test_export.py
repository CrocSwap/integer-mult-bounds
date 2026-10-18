"""Source-only replay and rejection at actual input/receipt/output boundaries."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]

def need(ok,why):
    if not ok:raise ValueError(why)

def main():
    sources=json.loads((PACKAGE/'SOURCES.json').read_text())['files']
    with tempfile.TemporaryDirectory(prefix='plane-native-export-') as temp:
        root=Path(temp);pkg=root/'research'/PACKAGE.name
        shutil.copytree(PACKAGE,pkg)
        for row in sources:
            if row['usage']=='input':
                path=root/row['path'];path.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],path)
        snapshot={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in root.rglob('*') if p.is_file()}
        def run(*args,ok=True,needle='PASS_PAIRED_PLANE_NATIVE_PAYLOAD'):
            result=subprocess.run([sys.executable,'-I','-O','-B',str(pkg/'verify.py'),*args],
                                  cwd=root,capture_output=True,text=True,timeout=90)
            need((result.returncode==0)==ok,'export exit status: '+result.stderr[-300:])
            need(needle in result.stdout+result.stderr,'export expected outcome: '+result.stderr[-300:])
        for p in root.rglob('*'):
            if p.is_file():p.chmod(0o444)
        run()
        after={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in root.rglob('*') if p.is_file()}
        need(snapshot==after,'read-only source export changed')
        receipt=root/'receipt.json';run('--output',str(receipt))
        before=receipt.read_bytes()
        run('--output',str(receipt),ok=False,needle='FileExistsError')
        need(receipt.read_bytes()==before,'existing output was changed')
        expected=pkg/'EXPECTED.json';original=expected.read_bytes();expected.chmod(0o644)
        data=json.loads(original);data['copy_mass']=112;expected.write_text(json.dumps(data))
        run(ok=False,needle='complete recomputed receipt');expected.write_bytes(original)
        row=next(x for x in sources if x['usage']=='input' and x['path'].endswith('clifford_exact.py'))
        path=root/row['path'];original=path.read_bytes();path.chmod(0o644);path.write_bytes(original+b'\n# mutation\n')
        run(ok=False,needle='changed source:');path.write_bytes(original)
        run()
    print('PASS_PAIRED_PLANE_EXPORT_CONTROLS source_only read_only receipt source output restored')

if __name__=='__main__':main()
