#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the fixed R480 T37 owner construction and its full finite invoice."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    need(not sys.flags.optimize, 'Retained checks require assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', type=Path, default=ROOT)
    parser.add_argument('--local', type=Path, default=HERE / 'inputs/local')
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--discover', action='store_true')
    args = parser.parse_args()
    main, local, work = args.main.resolve(), args.local.resolve(), args.work.resolve()
    need(not work.exists(), 'Choose a new replay directory')
    for relative, expected in read(HERE / 'SOURCE-FREEZE.json')['files'].items():
        need(sha(HERE / relative) == expected, 'Package source changed: ' + relative)
    upstream = main / 'research/complex-k492-owner-repair/vendor/multicold'
    baseline = main / 'research/community-k492-audit/pr622/replay/baseline558'
    source1074 = HERE / 'vendor/pr1074'
    for relative, expected in read(source1074 / 'UPSTREAM-PINS.json').items():
        need(sha(main / relative) == expected, 'Upstream dependency changed: ' + relative)
    need(local.is_dir(), 'Native local directory is missing')
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MULTICOLD_SOURCE=str(upstream), GAIN_PR564_SOURCE=str(upstream))
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(key, None)
    stages = []

    def run(name, script, *arguments, spec=None, discover=False):
        started = time.monotonic()
        command = [sys.executable, '-B', str(upstream / 'code/run_portable.py'),
                   str(script), *map(str, arguments)]
        childenv = dict(env)
        if spec:
            childenv['WITNESS_SPEC'] = str(spec)
        if discover:
            childenv.update(WITNESS_DISCOVER='1', WITNESS_RECORD=str(work / 'WITNESS-RECORD.jsonl'))
        log = work / (name + '.log')
        with log.open('w') as output:
            result = subprocess.run(command, env=childenv, stdout=output, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, seconds=round(time.monotonic()-started, 3),
                           exit_code=result.returncode, log_sha256=sha(log)))
        (work / 'STAGES.json').write_text(json.dumps(stages, indent=2)+'\n')
        need(result.returncode == 0, name + ' failed:\n' + log.read_text()[-6000:])
        print('PASS', name, stages[-1]['seconds'], flush=True)

    spec8 = source1074 / 'data/SPEC-T8.json'
    run('restore-parent', source1074 / 'code/restore_parent.py', '--source', upstream,
        '--baseline', baseline, '--out', work / 'parent558')
    run('bind8', source1074 / 'code/bind_providers_portable.py', '--baseline', work / 'parent558',
        '--provider', 'gauge44='+str(local), '--plan', source1074 / 'T8/PLAN.json',
        '--out', work / 'global8', spec=spec8)
    run('lift', HERE / 'lift.py', '--base', work / 'global8/base', '--out', work / 'lift')
    plan = work / 'lift/PLAN.json'
    if not args.discover:
        need(read(plan) == read(HERE / 'data/PLAN.json'), 'Frozen T37 plan differs')
    runtime = work / 'runtime'
    (runtime / 'data').mkdir(parents=True)
    shutil.copytree(source1074 / 'construction', runtime / 'construction')
    specpath = runtime / 'data/SPEC.json'
    if args.discover:
        spec = read(spec8)
        spec['name'] = 'r480-k8-x54-t37-owner-optimum'
        spec['call_order'] = read(HERE / 'ORDER.json')
        spec['dispatch'] = [[s, r, 'gauge44'] for s, r in spec['call_order']]
        spec['providers'] = {}
        spec['expected'] = {'gain_baseline_kappa': spec['expected']['gain_baseline_kappa']}
        spec['data'] = dict(plan_sha256=sha(plan), owners_sha256=sha(HERE / 'OWNERS.json.gz'))
        specpath.write_text(json.dumps(spec, indent=2)+'\n')
    else:
        shutil.copyfile(HERE / 'data/SPEC.json', specpath)
    parent = work / 'parent37'
    shutil.copytree(work / 'parent558', parent)
    shutil.copyfile(work / 'lift/GLOBAL-TEMPLATE.json.gz',
                    parent / 'complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
    code, global_ = HERE / 'code', work / 'global'
    def stage(name, script, *arguments):
        run(name, code / script, *arguments, spec=specpath, discover=args.discover)
    stage('bind', 'bind_providers_portable.py', '--baseline', parent, '--provider',
          'gauge44='+str(local), '--plan', plan, '--out', global_)
    stage('emit', 'emit_allcold.py', '--base', global_ / 'base', '--owners', HERE / 'OWNERS.json.gz',
          '--plan', global_ / 'PLAN.json', '--out', global_ / 'hosted')
    stage('audit', 'audit_allcold.py', global_ / 'base', global_ / 'hosted',
          global_ / 'audit/ASYNC-AUDIT.json', '--mutation-controls')
    retained = upstream / 'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json'
    stage('invoice', 'invoice_allcold.py', '--base', global_ / 'base', '--hosted', global_ / 'hosted',
          '--audit', global_ / 'audit', '--out', global_ / 'audit', '--retained-invoice', retained)
    stage('assembly', 'assemble.py', upstream, global_, work / 'ASSEMBLY.json')
    if args.discover:
        run('freeze', code / 'freeze_spec.py', '--spec', specpath, '--discovery', work)
    else:
        for name, script, filename in [('admission-controls', 'assembly_controls.py', 'ADMISSION-CONTROLS.json'),
                                        ('bit-controls', 'bit_supplier_controls.py', 'BIT-CONTROLS.json')]:
            stage(name, script, '--source-package', upstream, '--owner', global_ / 'audit/OWNERS-AND-PROFILE.json',
                  '--invoice', global_ / 'audit/PREFIX-AND-INVOICE.json', '--out', work / filename)
    run('independent-owner', HERE / 'independent_owner.py', '--baseline-parent',
        work / 'global8/base/split-centres/GLOBAL-TEMPLATE.json.gz', '--owners', HERE / 'OWNERS.json.gz',
        '--word', local / 'CANONICAL-WORD.json.gz', '--out', work / 'INDEPENDENT-OWNER.json',
        '--replicas', 37, '--expected-idle', '{"1":5622,"48":11302}')
    assembly = read(work / 'ASSEMBLY.json')
    owner = read(work / 'INDEPENDENT-OWNER.json')
    invoice = read(global_ / 'audit/PREFIX-AND-INVOICE.json')
    need(owner['profile'] == assembly['complex_profile'], 'Independent complete profile')
    need(owner['prefix_bits'] == invoice['global_prefix_bits'] < 1024, 'Independent prefix bound')
    need(owner['physical_row_coefficient'] == invoice['finite']['physical_row_coefficient'] < 20161,
         'Independent physical row bound')
    need(owner['roles'] == 159840 and owner['calls'] == 333 and owner['deficit'] == 11840,
         'Complete fixed construction')
    need(assembly['kappa_decimal'] == '0.001674137810105185', 'Attained bound')
    if not args.discover:
        admission, bit = read(work / 'ADMISSION-CONTROLS.json'), read(work / 'BIT-CONTROLS.json')
        need(len(admission['rejected_controls']) == 69 and not admission['discovery_accepted_controls'],
             'Complete strict admission controls')
        need(len(bit['rejected_controls']) == 12, 'Complete bit controls')
    receipt = dict(status='DISCOVERY_R480_T37' if args.discover else 'PASS_R480_T37_STRICT_FINITE_CONSTRUCTION',
                   kappa=assembly['kappa'], kappa_decimal=assembly['kappa_decimal'],
                   roles=159840, calls=333, prefix_bits=owner['prefix_bits'], charged_prefix_bits=1024,
                   physical_row_coefficient=owner['physical_row_coefficient'],
                   stages=stages, local_input_sha256={p.name: sha(p) for p in local.iterdir() if p.is_file()},
                   scope='Finite owner, controller, chart, invoice and assembly replay. Local scalar and phase replay and inherited all-size obligations are recorded separately.')
    (work / 'RESULT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(receipt['status'], receipt['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
