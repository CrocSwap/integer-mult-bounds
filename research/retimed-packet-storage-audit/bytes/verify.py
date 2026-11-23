"""Reproduce the pinned local byte proofs' exact finite evidence."""
from hashlib import sha256
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import ast
import inspect
import json
import subprocess
import sys
from textwrap import dedent
import time


def need(ok, why):
    if not ok: raise AssertionError(why)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime',type=Path,required=True)
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    root = Path(__file__).resolve().parent
    evidence = root/'evidence'; evidence.mkdir(exist_ok=True)
    sys.path.insert(0,str(runtime))
    from upstream import install
    install()
    pins = json.loads((root/'SOURCE-BINDINGS.json').read_text())
    for name,pin in pins['resolved_modules'].items():
        actual = Path(import_module(name).__file__).read_bytes()
        need(sha256(actual).hexdigest() == pin['sha256'], 'resolved source changed: '+name)
        need(actual == (root/'sources'/pin['file']).read_bytes(), 'stable source changed: '+name)
    for name,digest in pins['retained_files'].items():
        need(sha256((root/'sources'/name).read_bytes()).hexdigest() == digest,
             'retained source file changed: '+name)
    spec = spec_from_file_location('retained_stage_inventory',root/'sources/check_stage_inventory.py')
    check_stage_inventory = module_from_spec(spec)
    spec.loader.exec_module(check_stage_inventory)
    check_stage_inventory.inventory()
    work, pages = [], {}
    for module,names in check_stage_inventory.BODIES.items():
        for name in names.split():
            body = import_module(module)
            for part in name.split('.'): body = getattr(body,part)
            nodes = ast.walk(ast.parse(dedent(inspect.getsource(body))))
            for node in nodes:
                if not isinstance(node,ast.Call): continue
                function = ast.unparse(node.func).rsplit('.',1)[-1]
                if function == 'work_tapes':
                    work.append({'module':module,'body':name,'local_line':node.lineno,
                                 'slots':ast.literal_eval(node.args[0])})
                if function == 'pipe': pages[ast.literal_eval(node.args[1])] = 2
                if function == 'frames' and isinstance(node.args[0],ast.Constant):
                    pages[ast.literal_eval(node.args[0])] = ast.literal_eval(node.args[1])
    inventory = {'page_arities':dict(sorted(pages.items())), 'named_heads':sum(pages.values())+2,
                 'work_sites':work, 'work_head_slots':sum(row['slots'] for row in work)}
    need(inventory == json.loads((root/'ROLE-INVENTORY.json').read_text()),
         'extracted installed role inventory changed')
    started = time.monotonic()
    outputs = []
    jobs = [('audit_bytes.py','bytes.json',['--full-high']),
            ('audit_repair.py','repair.json',[]),
            ('audit_headers.py','headers.json',[])]
    jobs += [('audit_bytes.py','control-'+name+'.json',['--mutation',name])
             for name in ('bucket-erase','odd-collision','dirty-truncate')]
    for script,output,options in jobs:
        command = [sys.executable,'-IB',str(root/script),'--runtime',str(runtime),
                   '--output',str(evidence/output),*options]
        result = subprocess.run(command,check=True,capture_output=True,text=True)
        print(result.stdout,end='',flush=True)
        (evidence/(output+'.log')).write_text(result.stdout+result.stderr)
        record = json.loads((evidence/output).read_text())
        outputs.append({'file':output,'status':record['status'],
                        'sha256':sha256((evidence/output).read_bytes()).hexdigest()})
    artifacts = {}
    for path in sorted(root.rglob('*')):
        if path.is_file() and path.suffix in ('.py','.md','.json') and evidence not in path.parents:
            artifacts[str(path.relative_to(root))] = sha256(path.read_bytes()).hexdigest()
    report = {'status':'PASS_RETIMED_LOCAL_BYTE_CENSUS','commit':pins['commit'],
              'python':sys.version,'resolved_source_modules':len(pins['resolved_modules']),
              'named_heads':inventory['named_heads'],'work_heads':inventory['work_head_slots'],
              'seconds':time.monotonic()-started,'outputs':outputs,'artifact_sha256':artifacts,
              'scope':'source-local historical byte covers; mass, movement, remaining census and full threshold are not re-certified'}
    (evidence/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'])


if __name__ == '__main__': main()
