#!/usr/bin/env python3
"""Bind the X4 replay to the rebuilt PR589/741 ancestry. Finite, conditional checks."""
import argparse
from fractions import Fraction
import gzip
import json
from pathlib import Path
import sys
from verify_frontier741_bindings import check as check_ancestry, digest, read, require

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/gauge44-frames-x'
KAPPA = '1661634653669567/1000000000000000000'


def check(ancestor, native, global_dir, independent, price):
    parent = check_ancestry(ancestor / 'bit', ancestor / 'complex')
    require((PACKAGE/'inputs/PR589-EXPECTED.json').read_bytes() ==
            (ROOT/'research/e8-bit-p111-tuned/tune/EXPECTED.json').read_bytes(), 'Bit source differs')
    manifest = read(PACKAGE/'MANIFEST.json')
    # The submitted manifest covers every package file except itself.
    actual = {p.relative_to(PACKAGE).as_posix(): digest(p) for p in PACKAGE.rglob('*')
              if p.is_file() and p != PACKAGE/'MANIFEST.json' and '__pycache__' not in p.parts}
    require(actual == manifest, 'X4 package manifest')
    recipe = read(PACKAGE/'construction/jx/RECIPE-X4.json')
    pins = read(PACKAGE/'construction/jx/LOCAL-PINS-jx-X4.json')
    from hashlib import sha256
    def payload(path):
        return sha256(gzip.decompress(path.read_bytes())).hexdigest()
    require(payload(ancestor/'complex/sw4/FULL-WORD.json.gz') == recipe['input_content_sha256'], 'SW4 ancestor')
    require(payload(native/'jx/FULL-WORD.json.gz') == recipe['expected']['output_content_sha256'], 'X4 raw word')
    local = native/'local'
    require(payload(local/'CANONICAL-WORD.json.gz') == pins['canonical_sha256'], 'X4 canonical word')
    checks = read(local/'LOCAL-CHECKS.json')
    require({o:checks[o]['sha256'] for o in ('forward','backward')} == pins['program_sha256'], 'X4 program pins')
    require(digest(local/'CLIFFORD-RECIPES.json') == pins['clifford_recipes_sha256'], 'X4 phase recipe')
    expected_steps = ['jx'] + ['jx-control-'+name for name in sorted(recipe['controls'])] + [
        'layer-end-controls','native','ledgers','local-replay','wrappers','phases']
    steps = read(native/'STEPS.json')
    require([s['step'] for s in steps] == expected_steps and all(s['exit_code']==0 for s in steps), 'Complete X4 native stages')
    require(len(read(native/'JX-CONTROLS.json')['controls']) == pins['jx_controls'], 'X4 controls')
    require(len(read(native/'controls/COLD-END-CONTROLS.json')['rejected']) == 95, 'Endpoint controls')
    replay = read(local/'INDEPENDENT-LOCAL-REPLAY.json')
    require(replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'Native replay status')
    for orientation in ('forward','backward'):
        row = replay['local'][orientation]
        require(row['all_exact_columns']==728 and row['private_work_erased'], 'Native all-column restoration')
        require(replay['paid_profiles'][orientation] == recipe['expected']['local_profile'], 'Native paid profile')
    phase = read(local/'CLIFFORD-REVIEW.json')
    spec = read(PACKAGE/'data/SPEC.json')
    require(phase['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES' and
            phase['all_child_equalities_include_global_phase'] is True and
            phase['directed_edges']==spec['providers']['gauge44']['phase_edges'], 'Complete phase check')
    require(read(local/'WRAPPER-CHECKS.json')['status']=='PASS_RESIDUAL_WRAPPERS_ARE_EXACT', 'Wrapper restoration')
    raw = read(independent)
    require(raw['status']=='PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES' and
            raw['checked_columns']==728 and raw['content_sha256']==recipe['expected']['output_content_sha256'], 'Independent raw audit')
    global_steps = read(global_dir/'STAGES.json')
    require([s['name'] for s in global_steps] == ['restore-parent','bind','emit','audit','invoice','assembly','admission-controls','bit-supplier-controls'] and
            all(s['exit_code']==0 for s in global_steps), 'Complete global stages')
    for step in global_steps:
        require(digest(global_dir/(step['name']+'.log'))==step['log_sha256'], 'Global log binding')
    report = read(global_dir/'REPLAY.json')
    require(report['spec_sha256']==digest(PACKAGE/'data/SPEC.json'), 'X4 spec binding')
    admission = read(global_dir/'ADMISSION-CONTROLS.json')
    require(not admission['discovery_accepted_controls'] and len(admission['rejected_controls'])==spec['expected']['assembly_controls_rejected'], 'Admission controls')
    require(len(read(global_dir/'BIT-SUPPLIER-CONTROLS.json')['rejected_controls'])==12, 'Bit controls')
    assembly = read(global_dir/'ASSEMBLY.json')
    require(assembly['kappa']==report['kappa']==KAPPA, 'Selected X4 kappa')
    require(assembly['bit_lower']==read(ancestor/'bit/RESULT9.json')['bit_lower'], 'Rebuilt bit endpoint')
    require(assembly['complex_profile']==spec['expected']['global_profile'], 'Global profile')
    require(len(assembly['outer'])==47 and all(Fraction(v)>0 for v in assembly['outer'].values()), 'Strict outer constraints')
    require(assembly['surcharge_model']=={'complex':False,'bit':True}, 'Surcharge model')
    arithmetic = read(price)
    require(arithmetic['status']=='PASS_FROZEN_PROFILE_TWO_EXACT_ENGINE_AND_OUTER47_CROSSCHECK' and
            arithmetic['global_profile']==assembly['complex_profile'] and
            arithmetic['prices']['native']['outer_with_bit']['kappa']==KAPPA, 'Independent price')
    return dict(status='PASS_REBUILT_PR589_PR799_COMPOSITION', kappa=KAPPA,
                decimal=assembly['kappa_decimal'], ancestry=parent,
                package_manifest_sha256=digest(PACKAGE/'MANIFEST.json'),
                assembly_sha256=digest(global_dir/'ASSEMBLY.json'),
                independent_sha256=digest(independent), price_sha256=digest(price),
                scope='Exact finite X4 scalar/frame/phase/owner/invoice/assembly checks, bound to rebuilt PR589 and SW4 ancestry. Inherited all-size/compiler, common-label/mutable-source, whole-call hosting, precision/tape and analytic assumptions remain; not a full Lean theorem.')


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('ancestor','native','global','independent','price','out'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    result=check(a.ancestor,a.native,getattr(a,'global'),a.independent,a.price)
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],result['decimal'])

if __name__=='__main__': main()
