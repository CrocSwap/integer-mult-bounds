"""Source-bound component replay; finite evidence, not universal theorem acceptance."""
from pathlib import Path
import hashlib,json,io,contextlib
HERE=Path(__file__).resolve().parent

def require(ok,why):
    if not ok:raise ValueError(why)

def load(name):
    p=HERE/(name+'.py'); ns={'__name__':'authenticated_component','__file__':str(p)}
    exec(compile(p.read_bytes(),str(p),'exec'),ns);return ns

def main():
    pins=json.loads((HERE/'CONTENT-HASHES.json').read_text(encoding='utf-8'))
    actual={p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.rglob('*') if p.is_file() and p.name!='CONTENT-HASHES.json'}
    require(actual==pins,'package inventory or source hash mismatch')
    source_map=json.loads((HERE/'MODERN-SOURCE-MAP.json').read_text())
    for row in source_map['sources']:
        require(pins[row['local_file']]==row['sha256'],'frozen analytic source pin')
    for row in json.loads((HERE/'CODE-SOURCE-PINS.json').read_text()):
        require(pins[row['local_file']]==row['sha256'],'frozen code/source pin')
    out={}
    for name in ('critical_check','native_metadata','batched_band','record_product','sparse_membership','limb_setup'):
        out[name]=load(name)['check']()
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):load('native_ledger')['main']()
    out['native_ledger']=json.loads(capture.getvalue())
    require(out['native_ledger']['kappa']=='6040331/2000000000','target drift')
    print(json.dumps({'status':'PASS_NATIVE_ASSEMBLY_COMPONENTS','authenticated_files':len(pins),'results':out,'scope':'Finite components and exact arithmetic only; retained universal source proofs are not mechanically certified.'},indent=2))
if __name__=='__main__':main()
