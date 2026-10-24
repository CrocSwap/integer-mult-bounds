"""Source-bound exact controls; universal result is the written proof.
JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib,importlib.util,json
from pathlib import Path
from model import need,inverse_checks,geometry_checks,operator_controls,remainder_checks
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def run():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source hash: '+row['path'])
    spec=importlib.util.spec_from_file_location('retained_geometry',ROOT/'research/broad-phase-cell-inverse-bound/verify.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    setup,expr=mod.source_expression()
    return {'exact':inverse_checks(),'geometry':geometry_checks(setup,expr),'operators':operator_controls(),'remainders':remainder_checks(),'claim':'finite corroboration of written fixed-alpha operator-norm theorem; no physical caller or growing-alpha claim'}
def main():
    expected=json.loads((HERE/'RESULT.json').read_text())
    actual=run();need(canonical(actual)==canonical(expected),'complete typed receipt mismatch')
    print(canonical(actual));print('PASS_GAUSSIAN_HALF_LINE_OPERATOR_LIMIT')
if __name__=='__main__':main()
