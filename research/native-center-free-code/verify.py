"""Portable release/source authentication and exact coded-offer replay."""
from pathlib import Path
from hashlib import sha256
import json,importlib.util,io,contextlib
HERE=Path(__file__).resolve().parent

def need(c,m):
    if not c: raise ValueError(m)

def main():
    pins=json.loads((HERE/'CONTENT-HASHES.json').read_text(encoding='utf-8'))
    actual={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
    need(actual==set(pins)|{'CONTENT-HASHES.json'},'Exact package file inventory')
    for name,h in pins.items():
        need(sha256((HERE/name).read_bytes()).hexdigest()==h,'Package byte drift: '+name)
    origins=json.loads((HERE/'ORIGINS.json').read_text(encoding='utf-8'))
    for row in origins['origins']:
        need(sha256((HERE/row['local']).read_bytes()).hexdigest()==row['sha256'],'Upstream byte pin')
    spec=importlib.util.spec_from_file_location('coded_offer',HERE/'coded_verify.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    output=io.StringIO()
    with contextlib.redirect_stdout(output): module.main()
    receipt=json.loads(output.getvalue())
    need(receipt==json.loads((HERE/'EXPECTED.json').read_text(encoding='utf-8')),'Frozen mathematical receipt')
    print(json.dumps(receipt,sort_keys=True))
    print('PASS_SOURCE_BOUND_CENTER_FREE_CODE no_new_kappa')
if __name__=='__main__':main()
