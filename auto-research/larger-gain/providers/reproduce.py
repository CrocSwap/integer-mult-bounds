#!/usr/bin/env python3
"""Reconstruct and fully replay the six retained local providers.

Prepared with OpenAI Codex assistance. Apache-2.0. This admits local words;
physical hosting, the global invoice and recurrence remain separate.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
SOURCE_HEAD = 'c18417b02b80594b2ca1c8c21185d28befafc935'
SOURCE_MANIFEST = 'dd602912d0e60c9bb2befba446629ae531ea42a9d4fecda922f98aac40762c41'
BASELINE_STATUS = 'PASS_THREE_PROVIDER_048_ALLCOLD_NATIVE_COMPLEX_AND_CITED_BIT'
NAMES = ('zero', 'four', 'eight')
CORE_FILES = ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz',
              'RESIDUAL-ADAPTERS.json', 'WRAPPER-CHECKS.json',
              'INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-RECIPES.json')


def baseline_inventory():
    stages = ['frozen558-full-replay', 'construct-four-pivots', 'four-promoted-scalar-omissions']
    artifacts = {'PHASE-TIMING-CONTROLS.json', 'mixed-global/audit/IDLE-REMAINDER-FRAMES.json',
                 'RESULT.json', 'ASSEMBLY.json', 'ASSEMBLY-CONTROLS.json', 'FOUR-SCALAR-CONTROLS.json',
                 'four-word/CONSTRUCTION.json', 'mixed-global/BINDING.json',
                 'mixed-global/audit/ASYNC-AUDIT.json', 'mixed-global/audit/OWNERS-AND-PROFILE.json',
                 'mixed-global/audit/PREFIX-AND-INVOICE.json'}
    for name in NAMES:
        stages += [name + '-' + s for s in
                   ('cold-construction', 'cold-kernel-omissions', 'inherited-44-omissions')]
        if name != 'zero':
            stages.append(name + '-promoted-omissions')
        stages += [name + '-' + s for s in ('all-columns-native-frames', 'both-reflected-ledgers',
                                            'independent-local-controls', 'normalized-wrappers')]
        artifacts.update(name + '-cold-word/' + filename for filename in
                         ('KERNEL-CONSTRUCTION.json', 'KERNEL-OMISSION-CONTROLS.json',
                          'STATIC44-SCALAR-AUDIT.json'))
        artifacts.update(name + '-cold-local/' + filename for filename in
                         ('INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-REVIEW.json', 'WRAPPER-CHECKS.json'))
    stages += [name + '-all-phase-edges' for name in NAMES]
    stages += ['bind-three-providers', 'emit-three-provider-controller',
               'independent-controller-and-controls', 'fresh-three-provider-invoice',
               'conservative-and-native-exact-assembly', 'fifty-four-admission-controls',
               'phase-timing-portability-controls']
    return stages, artifacts


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_sha(path):
    raw = path.read_bytes()
    return hashlib.sha256(gzip.decompress(raw) if path.suffix == '.gz' else raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def verify_source(source):
    require(sha(source / 'MANIFEST.json') == SOURCE_MANIFEST, 'Wrong PR564 manifest')
    inventory = {p.relative_to(source).as_posix(): sha(p) for p in source.rglob('*')
                 if p.is_file() and p != source / 'MANIFEST.json' and '__pycache__' not in p.parts}
    require(inventory == read(source / 'MANIFEST.json'), 'PR564 source inventory differs')


def verify_baseline(source, baseline):
    receipt = read(baseline / 'RECEIPT.json')
    require(receipt['status'] == BASELINE_STATUS and receipt['manifest_sha256'] == SOURCE_MANIFEST,
            'Baseline is not the pinned PR564 replay')
    stages, artifacts = baseline_inventory()
    require([s['name'] for s in receipt['steps']] == stages and
            all(s['exit_code'] == 0 for s in receipt['steps']), 'Incomplete baseline replay')
    require(set(receipt['artifacts']) == artifacts, 'Incomplete baseline artifact inventory')
    require(read(baseline / 'STAGES.json') == receipt['steps'], 'Baseline stage receipt differs')
    for stage in receipt['steps']:
        require(sha(baseline / (stage['name'] + '.log')) == stage['log_sha256'],
                'Baseline stage log differs: ' + stage['name'])
    for name, expected in receipt['artifacts'].items():
        path = (baseline / name).resolve()
        require(path.is_relative_to(baseline), 'Baseline artifact escaped its directory')
        require(sha(path) == expected, 'Baseline artifact mismatch: ' + name)
    result = read(baseline / 'RESULT.json')
    require(result['status'] == BASELINE_STATUS and
            Fraction(result['kappa_decimal']) == Fraction('0.001593134158181640'),
            'Wrong baseline result')
    # The source recipes bind the actual raw words, not just copied receipts.
    for name in NAMES:
        recipe = read(source / 'data' / (name.upper() + '-COLD.json'))
        require(content_sha(baseline / (name + '-cold-word/FULL-WORD.json.gz')) ==
                recipe['output_content_sha256'], 'Wrong baseline raw provider: ' + name)
    selection = baseline / 'baseline558/reconstruction/static44/SELECTION.json'
    expected = read(HERE / 'fourcold-eight/controls/STATIC44-SCALAR-AUDIT.json')['selection_sha256']
    require(sha(selection) == expected, 'Wrong static44 selection')
    for name in ('four', 'eight'):
        expected_promotion = HERE / ('fourcold-' + name) / 'word/PROMOTION.json'
        require(sha(baseline / (name + '-cold-word/PROMOTION.json')) == sha(expected_promotion),
                'Wrong promotion recipe: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Pinned PR564 complex-allcold package')
    parser.add_argument('--work', type=Path, required=True, help='Fresh output directory')
    parser.add_argument('--baseline', type=Path, help='Reuse a complete source-bound PR564 replay')
    args = parser.parse_args()
    require(__debug__, 'Assertions must remain enabled in inherited verifiers')
    source, work = args.source.resolve(), args.work.resolve()
    require(not work.exists() and not work.is_relative_to(source) and not work.is_relative_to(HERE),
            'Output must be fresh and outside source/provider packages')
    verify_source(source)
    work.mkdir(parents=True)
    (work / 'logs').mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    env.pop('PYTHONOPTIMIZE', None)
    steps = []
    started = time.monotonic()

    def execute(name, script, *arguments, optimized=False):
        command = [sys.executable, '-B']
        if optimized:
            command += ['-O', str(script)]
        else:
            command += [str(source / 'code/run_portable.py'), str(script)]
        command += list(map(str, arguments))
        log = work / 'logs' / (name + '.log')
        start = time.monotonic()
        print('RUN', name, flush=True)
        with log.open('w', encoding='utf-8') as stream:
            result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, env=env)
        record = dict(name=name, command=command, script_sha256=sha(script),
                      exit_code=result.returncode, seconds=time.monotonic() - start,
                      log_sha256=sha(log))
        if result.returncode:
            raise RuntimeError(name + ' failed\n' + log.read_text()[-6000:])
        print('PASS', name, flush=True)
        return record

    def run(*arguments, **keywords):
        steps.append(execute(*arguments, **keywords))
        dump(work / 'STAGES.json', steps)

    baseline = args.baseline.resolve() if args.baseline else work / 'baseline564'
    if not args.baseline:
        run('baseline564', source / 'verify.py', '--work', baseline)
    verify_baseline(source, baseline)
    b = source / 'vendor/pr558'
    f = b / 'vendor/pr552'
    v = f / 'complex-global/vendor531'
    gk = f / 'complex-local/static44/gk'
    routing = f / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    selection = baseline / 'baseline558/reconstruction/static44/SELECTION.json'
    providers = {}
    for name in NAMES:
        original = baseline / (name + '-cold-word/FULL-WORD.json.gz')
        retained = HERE / ('fourcold-' + name)
        recipes = [retained / 'recipes' / ('candidate-%03d.json' % i) for i in range(3)]
        recipe_arguments = [x for recipe in recipes for x in ('--recipe', recipe)]
        four_word = work / ('fourcold-' + name) / 'word'
        run(name + '-construct-fourcold', HERE / 'build_suffix_kernels.py',
            '--word', original, '--gk-dir', gk, *recipe_arguments, '--out', four_word)
        run(name + '-independent-composition', HERE / 'audit_suffix_composition.py',
            '--source', original, '--word', four_word / 'FULL-WORD.json.gz',
            *recipe_arguments, '--out', four_word / 'INDEPENDENT-COMPOSITION.json', optimized=True)
        composition = read(four_word / 'INDEPENDENT-COMPOSITION.json')
        require(len(composition['negative_controls_rejected']) == 3, 'Missing composition controls')
        seven_word = work / ('width7-' + name) / 'word'
        run(name + '-construct-width7', HERE / 'build_entrance_promotions.py',
            '--word', four_word / 'FULL-WORD.json.gz', '--gk-dir', gk,
            '--recipes', HERE / 'width7' / name / 'RECIPES.json', '--out', seven_word)
        for kind, word in (('fourcold', four_word), ('width7', seven_word)):
            key = kind + '-' + name
            local, controls = word.parent / 'local', word.parent / 'controls'
            controls.mkdir()
            expected = retained / 'local' if kind == 'fourcold' else HERE / 'width7' / name
            require(content_sha(word / 'FULL-WORD.json.gz') == content_sha(expected / 'FULL-WORD.json.gz'),
                    'Constructed word differs from retained provider: ' + key)
            if name != 'zero':
                shutil.copyfile(baseline / (name + '-cold-word/PROMOTION.json'), word / 'PROMOTION.json')
            for pivot in ('extra-506', 'extra-518', 'extra-530', 'inherited-494'):
                output = controls / (pivot + '-omissions.json')
                run(key + '-' + pivot, source / 'code/audit_kernel_controls.py',
                    '--word', word / 'FULL-WORD.json.gz', '--recipe',
                    retained / 'controls' / (pivot + '-recipe.json'), '--out', output)
                require(len(read(output)['controls']) == 6, 'Missing kernel omission controls')
            if kind == 'fourcold':
                run(key + '-static44', f / 'complex-local/static44/audit_scalar.py',
                    word / 'FULL-WORD.json.gz', selection, controls / 'STATIC44-SCALAR-AUDIT.json')
                require(len(read(controls / 'STATIC44-SCALAR-AUDIT.json')['controls']) == 44,
                        'Missing static44 omission controls')
            else:
                output = controls / 'INDEPENDENT-SCALAR-TRANSFER.json'
                run(key + '-scalar-omission-transfer', HERE / 'audit_frame_promotions.py',
                    '--source', four_word / 'FULL-WORD.json.gz', '--word', word / 'FULL-WORD.json.gz',
                    '--recipes', HERE / 'width7' / name / 'RECIPES.json',
                    '--controls', four_word.parent / 'controls',
                    '--promotions', {'zero': 0, 'four': 4, 'eight': 8}[name], '--out', output,
                    optimized=True)
                require(len(read(output)['negative_controls_rejected']) == 3,
                        'Missing independent scalar-transfer controls')
            if kind == 'fourcold' and name != 'zero':
                output = controls / 'PROMOTED-SCALAR-AUDIT.json'
                run(key + '-rank5-omissions', b / 'code/audit_promoted_scalar.py',
                    word / 'FULL-WORD.json.gz', selection, output)
                require(len(read(output)['controls']) == {'four': 4, 'eight': 8}[name],
                        'Missing rank-five omission controls')
            run(key + '-native', v / 'code/audit_and_transport.py', '--raw', word / 'FULL-WORD.json.gz',
                '--routing', routing, '--out', local)
            run(key + '-ledgers', v / 'code/emit_local.py', local)
            run(key + '-independent-replay', v / 'code/audit_local.py', local)
            run(key + '-wrappers', v / 'code/adapters_local.py', local / 'CANONICAL-WORD.json.gz',
                local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
            providers[key] = (local, expected, 2929 if kind == 'fourcold' else 3005)

    # Phase jobs are independent; every one is awaited and checked.
    with ThreadPoolExecutor(max_workers=3) as executor:
        jobs = [executor.submit(execute, key + '-phases', b / 'code/phases_full.py',
                                local, v / 'vendor/clifford')
                for key, (local, _, _) in providers.items()]
        for job in jobs:
            steps.append(job.result())
            dump(work / 'STAGES.json', steps)
    summary = {}
    for key, (local, expected, edge_count) in providers.items():
        for filename in CORE_FILES:
            require(sha(local / filename) == sha(expected / filename),
                    'Deterministic replay differs: ' + key + '/' + filename)
        native = read(local / 'SCALAR-FRAME-AUDIT.json')
        reference_native = read(expected / 'SCALAR-FRAME-AUDIT.json')
        for field in set(native) | set(reference_native):
            if field != 'seconds':
                require(native.get(field) == reference_native.get(field), 'Native result differs: ' + key)
        replay = read(local / 'INDEPENDENT-LOCAL-REPLAY.json')
        require(len(replay['negative_controls_rejected']) == 11 and
                replay['paid_profiles']['forward'] == replay['paid_profiles']['backward'],
                'Incomplete independent local replay: ' + key)
        phase = read(local / 'CLIFFORD-REVIEW.json')
        require(phase['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES' and
                phase['all_child_equalities_include_global_phase'] is True and
                phase['directed_edges'] == edge_count and phase['endpoint_adapters'] == 224,
                'Incomplete exact phase replay: ' + key)
        summary[key] = dict(local=str(local.relative_to(work)), profile=native['local_profile'],
                            widths=native['widths'], directed_edges=edge_count,
                            canonical_word_sha256=sha(local / 'CANONICAL-WORD.json.gz'),
                            programs_sha256=sha(local / 'LOCAL-PROGRAMS.json.gz'))
    result = dict(status='PASS_SIX_PROVIDERS_FULL_LOCAL_REPLAY', providers=summary,
                  source_head=SOURCE_HEAD, seconds=time.monotonic() - started,
                  scope='Exact local scalar/frame, omission, wrapper and complete phase replay only. '
                        'Global hosting, invoice and recurrence admission are separate.')
    dump(work / 'RESULT.json', result)
    artifacts = {p.relative_to(work).as_posix(): sha(p) for p in work.rglob('*')
                 if p.is_file() and not p.is_relative_to(baseline)}
    inputs = {p.relative_to(HERE).as_posix(): sha(p) for p in HERE.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts}
    dump(work / 'RECEIPT.json', dict(status=result['status'], source_manifest_sha256=SOURCE_MANIFEST,
         baseline_receipt_sha256=sha(baseline / 'RECEIPT.json'), steps=steps, artifacts=artifacts,
         provider_inputs=inputs))
    print(json.dumps(dict(status=result['status'], providers=list(summary), work=str(work)), indent=2))


if __name__ == '__main__':
    main()
