"""Cold-build the signed #8073 six-column successor and run selected source scopes."""
from argparse import ArgumentParser
from hashlib import sha256
from datetime import datetime,timezone
from pathlib import Path
from shutil import copyfile,copytree
from subprocess import run
from tempfile import TemporaryDirectory
import json,sys

root=Path(__file__).resolve().parent
cli=ArgumentParser()
cli.add_argument('--output',type=Path,required=True)
cli.add_argument('--scope',nargs='+',help='Run only these scopes; the default is every registered local scope.')
a=cli.parse_args()
out=a.output.resolve()
out.mkdir(exist_ok=False,parents=True)
inputs=json.loads((root/'BUNDLE-INPUTS.json').read_bytes())
start=datetime.now(timezone.utc).isoformat()
with TemporaryDirectory(prefix='six-column-source-') as temp:
    tree=Path(temp)
    for name,pin in inputs.items():
        src=root/name;dest=tree/name
        assert src.is_file() and sha256(src.read_bytes()).hexdigest()==pin
        dest.parent.mkdir(exist_ok=True,parents=True);copyfile(src,dest)
    run([sys.executable,'-IB',str(tree/'compose8073.py')],check=True)
    candidate=tree/'combined'
    call=run([sys.executable,'-IB',str(candidate/'run_successor.py'),*(a.scope or [])])
    logs=candidate/'successor/logs';copytree(logs,out/'logs')
    copyfile(candidate/'successor/delta-pins.json',out/'delta-pins.json')
    checks={p.stem:json.loads(p.read_bytes()) for p in sorted(logs.glob('*.json'))}
    valid=call.returncode==0 and bool(checks) and all(r['code']==0 for r in checks.values())
    (out/'cold-result.json').write_text(json.dumps({'source_head':'cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e',
        'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'python':sys.version,
        'verified_inputs':len(inputs),'scopes':checks,'pass':valid},indent=2)+'\n')
    if not valid: raise SystemExit('Some verified source scopes failed. See the retained per-scope evidence.')
