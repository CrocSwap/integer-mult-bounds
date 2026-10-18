"""Read-only relocated replay and effective source/receipt/tree corruptions."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:
        raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    base=Path(tempfile.gettempdir()).resolve()
    with tempfile.TemporaryDirectory(prefix='adaptive-affine-',dir=base) as name:
        temp=Path(name).resolve()
        need(temp!=base and temp.is_relative_to(base),'bounded temporary export')
        root=temp/'export';package=root/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
        for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if r['usage']=='input':
                target=root/r['path'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(HERE.parents[1]/r['path'],target)
        other=temp/'elsewhere';other.mkdir()
        def run(script='verify.py',*args):
            return subprocess.run([sys.executable,'-I','-O','-B',str(package/script),*args],
                                  cwd=other,capture_output=True,text=True,timeout=120)
        def rejects(result,message):
            need(result.returncode!=0 and message in result.stderr,'expected '+message+': '+result.stderr)
        before=inventory(temp)
        result=run();need(result.returncode==0 and 'PASS_EISENSTEIN_ADAPTIVE_AFFINE_FLOOR' in result.stdout,'relocated primary '+result.stderr)
        result=run('independent.py');need(result.returncode==0 and 'PASS_INDEPENDENT_ADAPTIVE_AFFINE' in result.stdout,'relocated independent '+result.stderr)
        need(inventory(temp)==before,'default replay modified export')
        receipt=package/'RESULT.json';raw=receipt.read_bytes();data=json.loads(raw)
        data['global_mixed_derivative']=True;receipt.write_text(json.dumps(data),encoding='utf-8')
        rejects(run(),'typed receipt mismatch');receipt.write_bytes(raw)
        rejects(run('verify.py','--output',str(receipt)),'output already exists')
        need(receipt.read_bytes()==raw,'exclusive output replaced receipt')
        rejects(run('verify.py','--unknown'),'unknown arguments')
        for source_name in ('research/eisenstein-reduction-copy-floor/verify.py',
                            'research/eisenstein-clique-copy-bound/geometry.py'):
            source=root/source_name;old=source.read_bytes()
            source.write_bytes(old+b'\nraise RuntimeError("UNAUTHENTICATED_CODE_EXECUTED")\n')
            result=run();rejects(result,'source SHA')
            need('UNAUTHENTICATED_CODE_EXECUTED' not in result.stderr,'unauthenticated source ran')
            source.write_bytes(old)
        source=root/'research/eisenstein-reduction-copy-floor/README.md';old=source.read_bytes()
        source.unlink();rejects(run(),'FileNotFoundError');source.write_bytes(old)
        tree=package/'SMALL-TREES.json';old=tree.read_bytes();data=json.loads(old)
        data['small_adaptive']['nodes'][0]['rows']=[0]
        tree.write_text(json.dumps(data),encoding='utf-8')
        rejects(run(),'literal small-tree binding')
        rejects(run('independent.py'),'receiver-conflict witness')
        tree.write_bytes(old)
        need(inventory(temp)==before,'export controls not restored')
    print('PASS_ADAPTIVE_AFFINE_INTEGRITY relocated=2 corruption_cli_controls=8')


if __name__=='__main__':
    main()
