"""Read-only Git-free replay, source/evidence rejection and exclusive output."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def require(ok,why):
    if not ok:
        raise ValueError(why)


def snapshot(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='chart-rank-export-') as tmp:
        root=Path(tmp)/'checkout'
        pkg=root/'research'/HERE.name
        shutil.copytree(HERE,pkg,ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('research/dirty-connector-chart-transport/README.md','research/universal-connector-boundary/README.md'):
            target=root/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/name).read_bytes())
        def run(*extra,ok=True,needle=None):
            result=subprocess.run([sys.executable,'-I','-O','-B',str(pkg/'verify.py'),*map(str,extra)],
                                  cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=120)
            require((result.returncode==0)==ok,result.stdout+result.stderr)
            if needle:
                require(needle in result.stdout+result.stderr,'wrong result: '+result.stdout+result.stderr)
        before=snapshot(root)
        run(needle='PASS_CONNECTOR_CHART_RANK_REPAIR')
        require(snapshot(root)==before,'replay wrote files')
        path=root/'research/dirty-connector-chart-transport/README.md'
        raw=path.read_bytes()
        path.write_bytes(raw+b'\n')
        run(ok=False,needle='source binding')
        path.write_bytes(raw)
        result=pkg/'RESULT.json'
        raw=result.read_bytes()
        data=json.loads(raw)
        data['pilot']['minimum_rank']=True
        result.write_text(json.dumps(data),encoding='utf-8')
        run(ok=False,needle='typed exact receipt mismatch')
        result.write_text('{"schema_version":1,"schema_version":1}',encoding='utf-8')
        run(ok=False,needle='duplicate JSON key')
        result.write_bytes(raw)
        new=Path(tmp)/'new-result.json'
        run('--write-result',new)
        require(json.loads(new.read_text())==json.loads(raw),'regeneration mismatch')
        fresh=new.read_bytes()
        run('--write-result',new,ok=False,needle='output already exists')
        require(new.read_bytes()==fresh,'existing output changed')
        require(snapshot(root)==before,'export changed')
    print('PASS_CONNECTOR_CHART_RANK_EXPORT groups=4')


if __name__=='__main__':
    main()
