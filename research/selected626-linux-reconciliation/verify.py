#!/usr/bin/env python3
"""Check preserved PR626 CI evidence; this does not rerun its mathematics.

Josh Snider (jsnider3), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '66849e1475c930fd7732b1a0067ffee7e1e95f60'
CI_HEAD = 'ed49217ad6244f1d3bfe4588f122fa861849739c'
RUN = 38317651752
ARTIFACT = 11784169747
STAGES = ['bit543', 'declarations', 'complex626', 'independent-owner',
          'helper-interface', 'bindings']
MEMBERS = {'STEPS.json', 'RESULT.json', 'complex/ASSEMBLY.json',
           'complex/RECEIPT.json', 'complex/RESULT.json', 'complex/STAGES.json',
           *(name + '.log' for name in STAGES)}
DIFFERING_PATHS = [('template_sha256',), ('input_sha256', 'owner_audit'),
                   ('input_sha256', 'fresh_invoice')]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def source_objects(commit, paths):
    return {path: git('rev-parse', commit + ':' + path).decode().strip()
            for path in paths}


def compare_sources(ci, base, expected):
    require(ci == base == expected, 'Tested source objects differ from base/pins')


def archive_members(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) and set(names) == MEMBERS,
                'Unexpected or missing artifact members')
        return {name: archive.read(name) for name in names}


def check_evidence(run, jobs, artifacts, files, selected, assembly, expected):
    require(run['id'] == RUN and run['head_sha'] == CI_HEAD and run['run_attempt'] == 1,
            'Wrong run, head or attempt')
    require(run['repository']['full_name'] == 'CrocSwap/integer-mult-bounds'
            and run['head_repository']['full_name'] == 'CrocSwap/integer-mult-bounds',
            'Wrong source repository')
    require(run['path'] == '.github/workflows/frontier626.yml'
            and run['event'] == 'push', 'Wrong workflow or event')
    require((run['status'], run['conclusion']) == ('completed', 'success'),
            'Run did not complete successfully')
    require(jobs['total_count'] == len(jobs['jobs']) == 1, 'Unexpected job inventory')
    job = jobs['jobs'][0]
    require(job['run_id'] == RUN and job['head_sha'] == CI_HEAD
            and job['run_attempt'] == 1 and job['name'] == 'replay'
            and job['status'] == 'completed' and job['conclusion'] == 'success',
            'Replay job identity/status mismatch')
    steps = job['steps']
    require(len({s['name'] for s in steps}) == len(steps), 'Duplicate workflow step')
    require(all(s['status'] == 'completed' and s['conclusion'] == 'success' for s in steps),
            'Failed or skipped workflow step')
    require({s['name'] for s in steps} == set(expected['workflow_steps']),
            'Workflow step coverage changed')
    require(artifacts['total_count'] == len(artifacts['artifacts']) == 1,
            'Unexpected artifact inventory')
    artifact = artifacts['artifacts'][0]
    require(artifact['id'] == ARTIFACT and artifact['name'] == 'frontier626-linux-python312'
            and artifact['workflow_run']['id'] == RUN
            and artifact['workflow_run']['head_sha'] == CI_HEAD,
            'Artifact is detached from tested run')
    require(artifact['digest'] == 'sha256:' + expected['evidence_sha256']['artifact.zip'],
            'Artifact archive digest differs from GitHub metadata')
    require(set(files) == MEMBERS, 'Unexpected or missing artifact members')
    replay_steps = json.loads(files['STEPS.json'])
    require([s['name'] for s in replay_steps] == STAGES, 'Replay stage coverage changed')
    for step in replay_steps:
        require(step['exit_code'] == 0, 'Failed replay stage: ' + step['name'])
        require(digest(files[step['name'] + '.log']) == step['log_sha256'],
                'Replay log digest mismatch: ' + step['name'])
    result = json.loads(files['RESULT.json'])
    receipt = json.loads(files['complex/RECEIPT.json'])
    actual = json.loads(files['complex/ASSEMBLY.json'])
    complex_result = json.loads(files['complex/RESULT.json'])
    require(result['status'] == 'PASS_REBUILT_PR543_PR626_COMPOSITION',
            'Composition binding did not pass')
    kappa = Fraction(selected['kappa'])
    require(kappa == Fraction(selected['decimal']) == Fraction(result['kappa'])
            == Fraction(result['decimal']) == Fraction(actual['kappa'])
            == Fraction(complex_result['kappa']), 'Exact selected result mismatch')
    for name, field in [('complex/RECEIPT.json', 'complex_receipt_sha256'),
                        ('complex/ASSEMBLY.json', 'complex_assembly_sha256')]:
        require(digest(files[name]) == result[field], 'Broken composition receipt binding')
    for name in ('RESULT.json', 'ASSEMBLY.json'):
        require(digest(files['complex/' + name]) == receipt['artifacts'][name],
                'Broken complex artifact binding')
    require(receipt['status'] == complex_result['status']
            == 'PASS_COLD14_NATIVE_COMPLEX_AND_CITED_BIT', 'Complex replay did not pass')
    require(complex_result['reused'] == {'baseline': False, 'locals': []},
            'Complex replay reused earlier outputs')
    require(len(receipt['steps']) == len(expected['complex_steps'])
            and sorted(s['name'] for s in receipt['steps']) == expected['complex_steps'],
            'Complex substep coverage changed')
    require(all(s['exit_code'] == 0 for s in receipt['steps']), 'Failed complex substep')
    require(len(actual['outer']) == 47 and all(Fraction(v) > 0 for v in actual['outer'].values()),
            'Strict assembly margins changed')
    require(result['bit_input_sha256'] == actual['input_sha256']['inputs/PR543-EXPECTED.json'],
            'Bit supplier binding changed')
    require(complex_result['global_profile'] == actual['complex_profile'], 'Profile mismatch')
    # Preserve all three differences explicitly; do not erase whole hash maps.
    left, right, differences = deepcopy(actual), deepcopy(assembly), []
    for path in DIFFERING_PATHS:
        a, b = left, right
        for key in path[:-1]:
            a, b = a[key], b[key]
        av, bv = a.pop(path[-1]), b.pop(path[-1])
        differences.append({'path': list(path), 'linux': av, 'committed': bv})
    require(differences == expected['assembly_digest_differences'],
            'Recorded provenance differences changed')
    require(left == right, 'Mathematical assembly fields differ')
    return {'status': 'PASS_PR626_LINUX_RECONCILIATION', 'run': RUN,
            'ci_head': CI_HEAD, 'base': BASE, 'kappa': str(kappa),
            'replay_stages': len(replay_steps), 'complex_substeps': len(receipt['steps']),
            'strict_assembly_margins': len(actual['outer']),
            'assembly_digest_differences': differences}


def negative_controls(args):
    controls = []

    def reject(name, mutate, message):
        changed = deepcopy(args)
        mutate(changed)
        try:
            check_evidence(*changed)
        except ValueError as error:
            require(message in str(error), name + ': wrong rejection: ' + str(error))
            controls.append(name)
        else:
            raise ValueError('Invalid evidence accepted: ' + name)

    def mutate_json(data, member, mutate, rebind=False):
        obj = json.loads(data[3][member])
        mutate(obj)
        data[3][member] = json.dumps(obj).encode()
        if rebind:
            result = json.loads(data[3]['RESULT.json'])
            result['complex_assembly_sha256'] = digest(data[3][member])
            receipt = json.loads(data[3]['complex/RECEIPT.json'])
            receipt['artifacts']['ASSEMBLY.json'] = digest(data[3][member])
            data[3]['complex/RECEIPT.json'] = json.dumps(receipt).encode()
            result['complex_receipt_sha256'] = digest(data[3]['complex/RECEIPT.json'])
            data[3]['RESULT.json'] = json.dumps(result).encode()

    reject('wrong_ci_head', lambda a: a[0].update(head_sha=BASE), 'Wrong run')
    reject('wrong_attempt', lambda a: a[0].update(run_attempt=2), 'Wrong run')
    reject('queued_run', lambda a: a[0].update(status='queued'), 'did not complete')
    reject('skipped_workflow_step', lambda a: a[1]['jobs'][0]['steps'][5].update(conclusion='skipped'), 'Failed or skipped')
    reject('artifact_other_run', lambda a: a[2]['artifacts'][0]['workflow_run'].update(id=RUN + 1), 'detached')
    reject('artifact_bad_digest', lambda a: a[2]['artifacts'][0].update(digest='sha256:' + '0' * 64), 'archive digest')
    reject('missing_helper_log', lambda a: a[3].pop('helper-interface.log'), 'missing artifact')
    reject('corrupt_owner_log', lambda a: a[3].update({'independent-owner.log': b'PASS fake'}), 'log digest')
    reject('missing_helper_stage', lambda a: mutate_json(a, 'STEPS.json', lambda o: o.pop(4)), 'stage coverage')
    reject('failed_bit_stage', lambda a: mutate_json(a, 'STEPS.json', lambda o: o[0].update(exit_code=1)), 'Failed replay')
    reject('wrong_kappa', lambda a: mutate_json(a, 'RESULT.json', lambda o: o.update(kappa='1/100')), 'Exact selected')
    reject('broken_receipt_link', lambda a: mutate_json(a, 'RESULT.json', lambda o: o.update(complex_receipt_sha256='0' * 64)), 'receipt binding')
    reject('changed_positive_margin', lambda a: mutate_json(a, 'complex/ASSEMBLY.json', lambda o: o['outer'].update({next(iter(o['outer'])): '1'}), True), 'Mathematical assembly')
    reject('changed_source_engine_digest', lambda a: mutate_json(a, 'complex/ASSEMBLY.json', lambda o: o['input_sha256'].update({'engines/moment.py': '0' * 64}), True), 'Mathematical assembly')
    reject('changed_recorded_digest_difference', lambda a: mutate_json(a, 'complex/ASSEMBLY.json', lambda o: o.update(template_sha256='0' * 64), True), 'provenance differences')
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='write deterministic report outside evidence inputs')
    options = parser.parse_args()
    expected = read_json(HERE / 'EXPECTED.json')
    for name, pin in expected['evidence_sha256'].items():
        require(digest((HERE / 'evidence' / name).read_bytes()) == pin,
                'Frozen evidence bytes changed: ' + name)
    require(digest(gzip.decompress((HERE / 'evidence/workflow.log.gz').read_bytes()))
            == expected['workflow_log_sha256'], 'Original workflow log bytes changed')
    pins = read_json(HERE / 'SOURCE-PINS.json')
    selected = json.loads(git('show', BASE + ':certificates/selected-result.json'))
    manifest = json.loads(git('show', BASE + ':' + selected['source_manifest']))
    paths = sorted(set(manifest['package_roots'] + list(selected['proof_supplements'])
                       + ['scripts', 'Makefile', '.github/workflows/frontier626.yml',
                          'certificates/selected-result.json', selected['source_manifest'],
                          selected['certificate']]))
    require(sorted(pins) == paths, 'Source comparison coverage changed')
    compare_sources(source_objects(CI_HEAD, paths), source_objects(BASE, paths), pins)
    assembly = json.loads(git('show', BASE + ':' + selected['certificate']))
    files = archive_members((HERE / 'evidence/artifact.zip').read_bytes())
    receipt = json.loads(files['complex/RECEIPT.json'])
    package = 'research/complex-k492-owner-repair/'
    require(receipt['manifest_sha256'] == digest(git('show', BASE + ':' + package + 'MANIFEST.json'))
            and receipt['spec_sha256'] == digest(git('show', BASE + ':' + package + 'data/SPEC.json')),
            'Complex receipt source/spec differs from tested base')
    spec = json.loads(git('show', BASE + ':' + package + 'data/SPEC.json'))
    require(set(receipt['source_manifest_sha256']) == set(spec['build']['sources']),
            'Complex receipt source inventory changed')
    for name, pin in receipt['source_manifest_sha256'].items():
        require(pin == digest(git('show', BASE + ':' + package + 'vendor/' + name + '/MANIFEST.json')),
                'Complex receipt dependency differs from tested base: ' + name)
    args = [read_json(HERE / 'evidence' / (name + '.json')) for name in ('run', 'jobs', 'artifacts')]
    args += [files, selected, assembly, expected]
    report = check_evidence(*args)
    report['source_objects_matched'] = len(paths)
    report['negative_controls'] = negative_controls(args)
    try:
        compare_sources({'source': 'changed'}, {'source': 'base'}, {'source': 'base'})
    except ValueError:
        report['negative_controls'].append('changed_tested_source')
    else:
        raise ValueError('Changed tested source accepted')
    if options.out:
        options.out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], '6 stages, 64 substeps, 47 strict margins,',
          str(len(report['negative_controls'])) + ' rejection controls')


if __name__ == '__main__':
    main()
