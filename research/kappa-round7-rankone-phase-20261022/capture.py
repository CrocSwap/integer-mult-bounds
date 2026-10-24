"""Pin actual native bytes and attributed geometry/form source implementations."""
from pathlib import Path
from hashlib import sha256
import json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
FILES={
 'mixed_gauge.py':'research/kappa-round7-4610-coupled-recursion-20261022/mixed_gauge.py',
 'phase_equations.py':'research/kappa-round7-4610-scalar-contract-20261022/sources/PR4665-verify.py',
 'native-word.json.gz':'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
 'PHASE-FORM-GRAMMAR.md':'research/kappa-round7-4610-scalar-contract-20261022/sources/PHASE-FORM-GRAMMAR.md',
 'PHASE-CUT.md':'research/kappa-round7-4610-scalar-contract-20261022/sources/PHASE-CUT.md',
}
def main():
    out=[];(HERE/'sources').mkdir(exist_ok=True)
    for name,path in FILES.items():
        data=(ROOT/path).read_bytes();target=HERE/'sources'/name
        if target.exists() and target.read_bytes()!=data:raise ValueError('Captured source changed '+name)
        target.write_bytes(data);out.append(dict(copy=name,path=path,sha256=sha256(data).hexdigest()))
    result=dict(files=out,native_commit='1eb8da6cfb35512c0cc2533413e5ca42f48e13c6',
        native_canonical_sha256='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd',
        credits='Geometry contact loader: Cao Yifan parallel research; forms/equality verifier: Cinna Davis PR4665; phase grammar/cut: Dugongue PR4654; native word/controller/source lineage as retained.')
    (HERE/'SOURCES.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print('PINNED_PHASE_SEARCH_SOURCES',len(out))
if __name__=='__main__':main()
