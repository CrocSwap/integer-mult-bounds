#!/usr/bin/env python3
"""Fresh incremental verification from the pinned, previously rebuilt PR699 word.

Rebuilds the frame edits, native programs, scalar/frame/phase/wrapper controls,
physical hosting, invoices, independent owner moments and both outer prices.
The ancestral PR699 construction and cited bit circuit are inherited inputs;
this command does not claim to rebuild either. Prepared for tekuuu with
substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_sha(path):
    return hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('main', 'pr635', 'dependency', 'work'):
        ap.add_argument('--' + name, type=Path, required=True)
    args = ap.parse_args()
    need(__debug__, 'Inherited verification requires assertions; do not use -O')
    main, pr635, dep, work = [getattr(args, name).resolve()
                             for name in ('main', 'pr635', 'dependency', 'work')]
    need(not work.exists(), 'Use a new output directory')
    need(not any(work.is_relative_to(root) for root in (PACKAGE, main, pr635, dep)),
         'Output must be outside all input packages')
    own_manifest = read(PACKAGE / 'MANIFEST.json')
    actual = {p.relative_to(PACKAGE).as_posix(): sha(p) for p in PACKAGE.rglob('*')
              if p.is_file() and p != PACKAGE / 'MANIFEST.json' and '__pycache__' not in p.parts}
    need(actual == own_manifest, 'Exact submitted package manifest')
    sources = read(PACKAGE / 'SOURCES.json')
    need(sha(dep / 'MANIFEST.json') == sources['pr699_manifest_sha256'], 'PR699 dependency manifest pin')
    for name, key in (('PLAN.json', 'pr699_plan_sha256'), ('OWNERS.json.gz', 'pr699_owners_sha256')):
        need(sha(dep / 'data' / name) == sources[key], 'PR699 source pin: ' + name)
    need(sha(PACKAGE / 'data/OWNERS.json.gz') == sources['pr699_owners_sha256'], 'Unchanged literal PR699 owners')
    input_word = PACKAGE / 'inputs/PR699-WORD.json.gz'
    need(content_sha(input_word) == sources['input_word_content_sha256'], 'Pinned raw PR699 input word')
    need(sha(PACKAGE / 'exact_intervals.py') == sources['exact_intervals_sha256'], 'Independent interval helper pin')
    recipe = read(PACKAGE / 'construction/FRAME-RAISES.json')
    need(recipe['input_sha256'] == sources['input_word_content_sha256'], 'Recipe/source input binding')
    plan, spec = read(PACKAGE / 'data/PLAN.json'), read(PACKAGE / 'data/SPEC.json')
    for key in ('order', 'windows', 'pairs', 'sides'):
        need(plan[key] == read(dep / 'data/PLAN.json')[key], 'Inherited physical geometry: ' + key)
    need(set(spec['providers']) == {'gauge44'}, 'Single unchanged-width supplier dispatch')
    work.mkdir(parents=True)
    started = time.monotonic()
    stages = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    for key in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(key, None)

    def run(name, script, *arguments):
        start = time.monotonic()
        log = work / (name + '.log')
        print('RUN', name, flush=True)
        with log.open('w') as stream:
            result = subprocess.run([sys.executable, '-B', str(script), *map(str, arguments)],
                                    env=env, stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=result.returncode,
                           seconds=round(time.monotonic() - start, 3), log_sha256=sha(log)))
        dump(work / 'STAGES.json', stages)
        if result.returncode:
            raise RuntimeError(name + ' failed:\n' + log.read_text()[-8000:])
        print('PASS', name, flush=True)

    run('dependency-manifest', dep / 'verify_manifest.py')
    native = work / 'native'
    run('fresh-native-and-controls', PACKAGE / 'construction/reproduce_native.py',
        '--main', main, '--pr635', pr635, '--dependency699', dep, '--out', native,
        '--input', input_word)
    native_stages = read(native / 'STEPS.json')
    required_native = ['dependency-manifest', 'frame-construction', 'independent-audit',
                       'native', 'ledgers', 'local-replay', 'wrappers', 'frame-controls',
                       'layer-end-controls', 'phases']
    need([s['step'] for s in native_stages] == required_native
         and all(s['exit_code'] == 0 for s in native_stages), 'Complete fresh native stage sequence')
    word, local = native / 'word/FULL-WORD.json.gz', native / 'local'
    need(content_sha(word) == recipe['output_sha256'], 'Constructed raw word payload')
    need(read(native / 'NATIVE-PINS.json') == read(PACKAGE / 'construction/LOCAL-PINS.json'), 'Frozen native semantic pins')
    raw_audit = read(native / 'INDEPENDENT-AUDIT.json')
    need(raw_audit['status'] == 'PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES'
         and raw_audit['checked_columns'] == 728 and raw_audit['content_sha256'] == recipe['output_sha256'],
         'Independent complete-column raw audit')
    need(raw_audit['local_profile'] == recipe['profile'], 'Independent native paid profile')
    local_audit = read(local / 'INDEPENDENT-LOCAL-REPLAY.json')
    need(local_audit['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'Native scalar/frame replay')
    need(len(local_audit['negative_controls_rejected']) == spec['providers']['gauge44']['native_negative_controls'],
         'Complete independent native negative controls')
    for orientation in ('forward', 'backward'):
        record = local_audit['local'][orientation]
        need(record['all_exact_columns'] == 728 and record['private_work_erased'], 'All native columns/private restoration')
        need(local_audit['paid_profiles'][orientation] == recipe['profile'], 'Native orientation profile')
    need(read(local / 'WRAPPER-CHECKS.json')['status'] == 'PASS_RESIDUAL_WRAPPERS_ARE_EXACT', 'Exact normalized residual wrappers')
    phases = read(local / 'CLIFFORD-REVIEW.json')
    need(phases['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES'
         and phases['all_child_equalities_include_global_phase'] is True
         and phases['directed_edges'] == spec['providers']['gauge44']['phase_edges'], 'All exact native phase edges')
    frame_controls = read(native / 'FRAME-CONTROLS.json')
    need(frame_controls['status'] == 'PASS_FRAME_RETIMING_35_NEGATIVE_CONTROLS'
         and frame_controls['honest'] == 'PASS'
         and len(frame_controls['rejected']) == 4 * len(recipe['changes']) + 3, 'Complete targeted frame controls')
    end_controls = read(native / 'controls/COLD-END-CONTROLS.json')
    need(end_controls['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS'
         and len(end_controls['rejected']) == 95, 'All inherited cold-end controls')
    run('independent-pointset-frames', PACKAGE / 'independent_frames.py', '--before', input_word,
        '--after', word, '--out', work / 'INDEPENDENT-FRAMES.json')
    frame_audit = read(work / 'INDEPENDENT-FRAMES.json')
    need(frame_audit['status'] == 'PASS_EXPLICIT_512_POINT_FRAME_RECOUNT'
         and frame_audit['local_profile'] == recipe['profile']
         and frame_audit['helper_footprints_unchanged'] and frame_audit['scalar_gates_unchanged'],
         'Independent point-set frame obligations')
    need(len(frame_audit['negative_controls']) == 12
         and all(c['rejected'] for c in frame_audit['negative_controls']), 'Independent frame mutations')
    global_run = work / 'global-replay'
    run('strict-global-admission', PACKAGE / 'verify_global.py', '--main', main, '--dependency', dep,
        '--plan', PACKAGE / 'data/PLAN.json', '--owners', PACKAGE / 'data/OWNERS.json.gz',
        '--spec', PACKAGE / 'data/SPEC.json', '--provider', 'gauge44=' + str(local), '--work', global_run)
    run('independent-owners-and-moments', PACKAGE / 'audit_owners.py', '--dependency', dep,
        '--plan', PACKAGE / 'data/PLAN.json', '--owners', PACKAGE / 'data/OWNERS.json.gz',
        '--spec', PACKAGE / 'data/SPEC.json', '--provider', 'gauge44=' + str(local),
        '--output', work / 'INDEPENDENT-OWNERS.json')
    run('independent-two-engine-outer47', dep / 'independent/price_profile.py', '--main', main,
        '--profile', PACKAGE / 'data/PLAN.json', '--output', work / 'INDEPENDENT-PRICE.json')
    assembly = read(global_run / 'ASSEMBLY.json')
    owner_audit = read(work / 'INDEPENDENT-OWNERS.json')
    price = read(work / 'INDEPENDENT-PRICE.json')
    kappa = spec['expected']['kappa']
    need(kappa == assembly['kappa'] == owner_audit['kappa']
         == price['prices']['native']['outer_with_bit']['kappa'], 'All exact kappa witnesses agree')
    need(Fraction(kappa) > Fraction(read(dep / 'data/SPEC.json')['expected']['kappa']), 'Strict improvement over PR699')
    need(assembly['complex_profile'] == spec['expected']['global_profile'], 'Frozen final global profile')
    need(len(owner_audit['negative_controls']) == 7 and owner_audit['roles'] == 36288, 'Independent full owner census and controls')
    for mode in ('native', 'conservative'):
        need(price['prices'][mode]['outer_with_bit']['strict_constraints_passed'] == 47, 'All outer constraints')
    admission = read(global_run / 'ADMISSION-CONTROLS.json')
    need(len(admission['rejected_controls']) == spec['expected']['assembly_controls_rejected']
         and not admission['discovery_accepted_controls'], 'Strict admission mutation census')
    need(len(read(global_run / 'BIT-SUPPLIER-CONTROLS.json')['rejected_controls']) == 12, 'Cited bit-supplier controls')
    result = dict(status='PASS_PINNED_INPUT_FRAME_RETIMING_COMPLETE_REPLAY',
                  kappa=kappa, kappa_decimal=assembly['kappa_decimal'], complex_lower=assembly['complex_lower'],
                  bit_lower=assembly['bit_lower'], global_profile=assembly['complex_profile'],
                  seconds=round(time.monotonic() - started, 3), stages=stages,
                  package_manifest_sha256=sha(PACKAGE / 'MANIFEST.json'),
                  source_pins=sources, native_pins=read(native / 'NATIVE-PINS.json'),
                  controls=dict(frame=len(frame_controls['rejected']), cold_end=95, independent_frames=12,
                                native=len(local_audit['negative_controls_rejected']), owner=7,
                                admission=len(admission['rejected_controls']), bit_supplier=12),
                  scope='Fresh incremental replay from the pinned PR699 raw word: frame construction, both complete native orientations, exact wrappers/phases, physical controller and full coefficient invoice, independent owners, rational moments and 47 outer inequalities. The PR699 ancestral construction and cited PR589 bit circuit are inherited, not rebuilt by this command. All-size/compiler, hosting, precision/tape and analytic-transfer assumptions remain conditional. This corroborates concurrent PR741; no mathematical priority claim.')
    dump(work / 'RESULT.json', result)
    retained = ['RESULT.json', 'STAGES.json', 'INDEPENDENT-FRAMES.json', 'INDEPENDENT-OWNERS.json', 'INDEPENDENT-PRICE.json',
                'native/STEPS.json', 'native/NATIVE-PINS.json', 'native/INDEPENDENT-AUDIT.json',
                'native/FRAME-CONTROLS.json', 'native/controls/COLD-END-CONTROLS.json',
                'native/word/FULL-WORD.json.gz', 'native/word/FRAME-CHECKS.json',
                'global-replay/ASSEMBLY.json', 'global-replay/REPLAY.json', 'global-replay/STAGES.json',
                'global-replay/ADMISSION-CONTROLS.json', 'global-replay/BIT-SUPPLIER-CONTROLS.json']
    retained += ['native/local/' + p.name for p in local.iterdir() if p.is_file()]
    dump(work / 'RECEIPT.json', dict(status=result['status'], kappa=kappa,
                                    artifacts={name: sha(work / name) for name in retained},
                                    package_manifest_sha256=result['package_manifest_sha256']))
    print(result['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
