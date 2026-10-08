#!/usr/bin/env python3
"""Hash-validated rectangular certificate; inherited proofs are retained verbatim."""
from hashlib import sha256
from pathlib import Path
import argparse,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj
arithmetic=module('rectangular_semantic_arithmetic',HERE/'semantic_arithmetic.py')
saved=sys.modules.get('semantic_arithmetic');sys.modules['semantic_arithmetic']=arithmetic
try:record=module('rectangular_record',HERE/'record.py')
finally:
    if saved is None:sys.modules.pop('semantic_arithmetic',None)
    else:sys.modules['semantic_arithmetic']=saved
controls=module('rectangular_exact_controls',HERE/'controls.py')
base=module('rectangular_inherited_PR23',ROOT/'research/semantic-bulk/verify.py')

def pinned_inputs():
    base.pinned_inputs()
    inherited=json.loads((ROOT/'research/a5-semantic/certificate.json').read_text())
    pinned={**inherited['source_sha256'],**inherited['inherited_PR23_input_sha256']}
    for name,digest in pinned.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    inputs=json.loads((HERE/'inputs.json').read_text());checked={};replay={}
    for alias,digest in inputs['source_sha256'].items():
        if alias=='PR21/partial-swap-input.json':path=ROOT/'certificates/partial-swap-input.json'
        elif alias.startswith(('PR21/scripts/','PR25/scripts/')):path=ROOT/alias.split('/',1)[1]
        elif alias=='PR25/fresh-producer-report.json':path=HERE/'evidence/fresh-producer-report.json'
        elif alias.startswith('fresh-local/') and alias.endswith('.json'):path=HERE/'evidence'/alias.split('/',1)[1]
        elif alias.startswith('fresh-local/'):
            replay[alias]=digest;continue
        else:raise AssertionError('Unresolved source alias: '+alias)
        assert sha256(path.read_bytes()).hexdigest()==digest,alias
        checked[str(path.relative_to(ROOT))]=digest
    for h in (27,28):
        archived=json.loads((HERE/f'evidence/producer-{h}.json').read_text())
        assert archived['record']==inputs['producers'][str(h)]['record']
        for key in ('scalar','original','labels','positive'):
            assert archived[key]==inputs['producers'][str(h)][key],key
    fresh=json.loads((HERE/'evidence/fresh-producer-report.json').read_text())
    h57=fresh['producers']['57'];expected=inputs['producers']['57']['record']
    assert fresh['regenerated_from_source'] and h57['certificate_equal']
    assert expected==dict(v=h57['v'],roles=h57['R'],additions=h57['c'],outputs=h57['q'],matches=h57['matched'],loss=h57['loss'],histogram=h57['histogram'])
    for key in ('complex','semantic'):
        assert inputs['semantic_PR23']['finite_bridge'][key]==inherited['finite_bridge'][key],key
    return dict(live_pinned_sha256=pinned,validated_archival_sha256=checked,
                deterministic_replay_expected_sha256=replay,
                replay_scope='Archival receipt hashes validated here; producer.py independently regenerates new h27/h28 DAGs, matching, labels and deterministic bytes.')

def run():
    pin=pinned_inputs();result=record.run();result['fresh_exact_controls']=controls.run(result['prescribed_basis'])
    result['pin_validation']=pin
    result['status']='CONDITIONAL RECTANGULAR SAVING 12260937/10^12; NOT FORMAL VERIFICATION'
    result['proof_status']='Written general A1/A3/A5 compatibility arguments, independent audits and exact finite controls. Inherited PR18/21 physical and PR23 semantic/tape hypotheses remain. Full rerun status is recorded separately in validation.json. No global optimality claim.'
    files=list(HERE.glob('*.py'))+list(HERE.glob('*.txt'))+[HERE/'inputs.json',HERE/'SOURCE.json',HERE/'README.md',ROOT/'notes/rectangular-semantic-note.tex',ROOT/'tests/test_rectangular_semantic.py']
    result['package_source_sha256']={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'certificate.json');args=p.parse_args()
    result=run();args.output.write_text(json.dumps(arithmetic.js(result),indent=2,sort_keys=True)+'\n')
    print('PASS rectangular kappa='+str(result['assembly']['parameters']['kappa'])+'; 47 strict constraints; 7 margins; row degree 96000')
