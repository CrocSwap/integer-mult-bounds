#!/usr/bin/env python3
"""Fresh finite admission of concentrated source partners plus pre-life hosting.

No cached native or parent stages are accepted. All original acceptance checks remain; four exact candidate-specific
pins/control adaptations follow PR2696 and are explicitly hash-bound.
The 24-digit complex bracket suffices only if its complete modern outer claim
strictly exceeds the entire published PR2733 claim.

Apache-2.0. Marius-Paul Dumitrean with substantial OpenAI Codex assistance.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as Q
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import combined_adapt
import generate as refit_generate

sys.set_int_max_str_digits(0)
SOURCE_HEAD = '2e2cf56521df8a2b816b2689144765ee00b69a24'
MANIFEST_SHA = 'db498ed7998397ef00501e037f10678e89ee113d57af4667c5c6978fc42e83ba'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--fill', type=Path, required=True)
    parser.add_argument('--source2696', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--order', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    need(__debug__, 'Assertions must be enabled')
    need(args.jobs == 1, 'Use one controller-audit shard: inherited parallel temporary path is shared')
    candidate, reference = args.candidate.resolve(), args.source2696.resolve()
    combined_adapt.authenticate(candidate, reference)
    adapter_hash = sha(Path(combined_adapt.__file__))
    source, fill, order, work = (p.resolve() for p in
                                 (args.source, args.fill, args.order, args.work))
    need(not work.exists() and not work.is_relative_to(source), 'Fresh external output required')
    need(sha(source/'MANIFEST.json') == MANIFEST_SHA, 'Exact PR2679 manifest')
    pins = read(source/'MANIFEST.json')
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*')
              if p.is_file() and p != source/'MANIFEST.json'}
    need(actual == set(pins), 'Exact predecessor file set')
    for name, digest in pins.items():
        need(sha(source/name) == digest, 'Predecessor source pin: '+name)
    fill_hash, order_hash = sha(fill), sha(order)
    refit_generate.authenticate()
    original = read(refit_generate.PARENT/'CLAIM.json')
    need(sha(fill) == sha(candidate/'FILL.json.gz') and sha(order) == sha(candidate/'ORDER.json'),
         'Frozen combined fill and order')
    work.mkdir(parents=True)
    package = work/'derivative'
    shutil.copytree(source, package)
    adaptations = combined_adapt.install(package, candidate)
    write(work/'CHECKER-ADAPTATIONS.json', adaptations)
    (work/'tmp').mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1',
               AUDIT_FAST_SHARDS=str(args.jobs), TMPDIR=str(work/'tmp'),
               FINE_ENGINE_CACHE=str(work/'fine-cache'),
               BORROW_RECEIPTS=str(work/'borrow-receipts'))
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(key, None)
    stages = []
    lock = threading.Lock()
    started = time.monotonic()

    def run(name, script, *arguments):
        command = [sys.executable, '-B', str(script), *map(str, arguments)]
        begin = time.monotonic()
        log = work/(name+'.log')
        with log.open('w') as stream:
            result = subprocess.run(command, cwd=work, env=env,
                                    stdin=subprocess.DEVNULL, stdout=stream,
                                    stderr=subprocess.STDOUT)
        with lock:
            stages.append(dict(name=name, command=command, exit_code=result.returncode,
                               seconds=time.monotonic()-begin,
                               script_sha256=sha(script), log_sha256=sha(log)))
            write(work/'STAGES.json', stages)
        need(result.returncode == 0, 'Failed '+name+'; inspect '+str(log))
        print('PASS', name, flush=True)

    run('fine-engine-oracle', package/'code/oracle_check.py')
    def rebuild_sources():
        # These original scripts only read the frozen words and put receipts in
        # BORROW_RECEIPTS. They have no dependency on the native output trees.
        run('rebuild-words-566', package/'new/rebuild_chain.py')
        run('rebuild-borrow-words', package/'new/rebuild_borrow.py')

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(run, 'retained-parent', package/'vendor/pr1297/verify.py',
                               '--work', work/'parent')]
        for tag in ('base', 'extra'):
            futures.append(pool.submit(run, 'native-'+tag, package/'new/run_native_borrow.py',
                                       package/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz',
                                       work/('native-'+tag)))
        futures.append(pool.submit(rebuild_sources))
        for future in futures:
            future.result()
    parent = read(work/'parent/RESULT.json')
    need(parent['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
         and Q(parent['kappa']) == Q(read(source/'vendor/pr1297/CLAIM.json')['kappa']),
         'Exact retained-parent claim and admission status')
    need(parent['base_native_reuse'] is False and parent['extra_native_reuse'] is False,
         'Fresh retained-parent native chains')
    need(len(parent['stages']) == 18 and all(type(x['exit_code']) is int and
         x['exit_code'] == 0 for x in parent['stages']), 'Complete retained-parent admission')
    for tag in ('base', 'extra'):
        need(read(work/f'native-{tag}/local/FULL-WORD.json.gz') ==
             read(candidate/f'words/{tag}.json.gz'), 'Native word binding '+tag)
        steps = read(work/f'native-{tag}/STEPS.json')
        need([x['step'] for x in steps] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
             and all(type(x['exit_code']) is int and x['exit_code'] == 0 for x in steps),
             'Complete fresh native chain '+tag)
    upstream = work/'parent/layout/joint1148-round45/source'
    for tag, word in (('base', 'gauge44-word-566.json.gz'), ('extra', 'extra-word-566.json.gz')):
        run('audit-local-566-'+tag, upstream/'research/gauge44-slots/independent/audit_local.py',
            '--word', package/'new'/word, '--main', upstream,
            '--output', work/('AUDIT-LOCAL-566-'+tag+'.json'))
    run('lemmag-labels', package/'code/lemmag_stage.py', work/'LEMMAG-LABELS.json',
        work/'native-base', work/'native-extra')

    shutil.copy2(fill, package/'new/borrow-fill/FILL.json.gz')
    shutil.copy2(order, package/'new/borrow-fill/ORDER.json')
    run('candidate-owner-reconstruction', package/'reconstruct.py', '--out', work/'owners')
    run('candidate-parent-lift', package/'lift_parent.py', '--owners', work/'owners',
        '--out', work/'lifted')
    for name in ('PLAN.json', 'OWNERS.json.gz', 'DISPATCH.json', 'PROFILE.json',
                 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz', 'SPEC.json'):
        shutil.copy2(work/'lifted'/name, package/name)
    for name in ('PLAN.json', 'PROFILE.json', 'SPEC.json'):
        shutil.copy2(work/'lifted'/name, package/'new'/name)
    latest_spec = read(source/'new/SPEC.json')
    for name in ('SPEC.json', 'new/SPEC.json'):
        spec = read(package/name)
        spec['width_spot_helpers'] = latest_spec['width_spot_helpers']
        spec['outer_refinement'] = dict(endpoint_digits=24, grid_digits=18,
                                         margin_digits=28, bootstrap_steps=12)
        spec['expected']['live'] = 66304
        write(package/name, spec)
    profile = read(package/'PROFILE.json')
    need(sum(int(r)*n for r, n in profile.items()) == 4816512, 'Complete paid rank mass')
    run('rebind', package/'new/rebind.py', package, work/'native-base/local',
        work/'native-extra/local', work/'rebound')
    # Original rebind.py omits private zero buffers in its provisional SPEC.
    # Original verify.py uses the correctly frozen source SPEC instead. Derive
    # the same complete stock from actual fresh native words before discovery.
    native_words = [read(work/f'native-{tag}/local/CANONICAL-WORD.json.gz')
                    for tag in ('base', 'extra')]
    need(all(word['R'] == 415 and len(word['zero_buffers']) == 72
             for word in native_words), 'Actual native helper and private-buffer inventory')
    physical = 66304 + 415 + 8 + 2 + max(len(word['zero_buffers']) for word in native_words)
    need(physical == latest_spec['expected']['physical'] == 66801,
         'Native physical stock agrees with the frozen source contract')
    rebound_spec = read(work/'rebound/SPEC.json')
    provisional_physical = rebound_spec['expected']['physical']
    rebound_spec['expected']['physical'] = physical
    write(work/'rebound/SPEC.json', rebound_spec)
    write(work/'PRIVATE-STOCK-BINDING.json', dict(
        status='BOUND_ACTUAL_NATIVE_PRIVATE_STOCK', provisional=provisional_physical,
        helpers=415, private_buffers=72, actual_physical=physical,
        source_physical=latest_spec['expected']['physical'],
        canonical_sha256={tag:sha(work/f'native-{tag}/local/CANONICAL-WORD.json.gz')
                          for tag in ('base', 'extra')}))
    runtime = work/'parent/layout/prelife_order_composition'
    runtime.mkdir()
    for name in ('replay.py', 'freeze_spec.py', 'audit_mixed.py', 'independent_core.py',
                 'geometry_controls.py', 'audit_fast.py'):
        shutil.copy2(package/name, runtime/name)
    for name in ('code', 'construction', 'inputs'):
        shutil.copytree(package/name, runtime/name)
    shutil.copytree(work/'rebound', runtime/'candidate')
    shutil.copytree(work/'native-extra', runtime/'native-extra')
    data = runtime/'candidate'
    run('discover', runtime/'replay.py', '--data', data, '--work', work/'discovery',
        '--local', work/'native-base/local', '--discover')
    run('strict', runtime/'replay.py', '--data', data, '--work', work/'strict',
        '--local', work/'native-base/local')
    run('geometry-controls', runtime/'geometry_controls.py', '--source',
        upstream/'research/complex-k492-owner-repair/vendor/multicold',
        '--strict', work/'strict', '--out', work/'GEOMETRY-CONTROLS.json')
    strict = read(work/'strict/RESULT.json')
    need(strict['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL', 'Strict candidate admission')
    need(len(read(work/'GEOMETRY-CONTROLS.json')['rejected']) == 6, 'Six geometry controls')
    need(len(read(work/'strict/ADMISSION-CONTROLS.json')['rejected_controls']) == 114,
         '114 admission controls')
    need(len(read(work/'strict/BIT-CONTROLS.json')['rejected_controls']) == 12,
         '12 bit controls')
    need(strict['independent']['roles'] == 276390 and
         len(strict['independent']['controls_rejected']) == 8, 'All owner roles and eight controls')
    for name in ('PLAN.json', 'PROFILE.json', 'SPEC.json'):
        shutil.copy2(data/name, package/'new'/name)
    spec = read(data/'SPEC.json')
    C = Q(spec['expected']['complex_lower'])
    write(package/'CLAIM.json', dict(kappa=strict['kappa'], kappa_decimal=strict['kappa_decimal'],
                                    scope='Conditional finite construction; inherited assumptions remain.'))
    write(package/'outer/B.json', dict(b=str(C-Q(1, 10**104)),
                                      b_above_endpoint=str(C+Q(1, 10**24)), profile=profile, live=66304))
    for name in ('check_ledger.py', 'independent_check.py'):
        run('outer-'+name, package/'outer'/name)
    run('outer-evidence', package/'outer/run_outer.py', work/'outer-replay')
    ledger = read(package/'outer/LEDGER.json')
    k = Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational'])
    need(k > Q(original['kappa']), 'Full exact claim must beat the entire PR2733 claim')
    assembly = read(work/'strict/ASSEMBLY.json')
    boundary = read(package/'outer/B.json')
    need(assembly['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' and
         len(assembly['outer']) == 47, 'Full supplier assembly and 47 inequalities')
    need(Q(assembly['complex_lower']) == C and
         Q(boundary['b']) < C < Q(boundary['b_above_endpoint']), 'Certified supplier endpoint binding')
    need(Q(assembly['bit_lower']) == Q('0.001733427039589844234749'), 'Exact bit endpoint binding')
    need(ledger['profile'] == profile == assembly['complex_profile'],
         'Outer, supplier and literal profile binding')
    need(len(ledger['rows']['struct_boundary_radix_union']['strict_checks']) == 63 and
         len(ledger['rejecting_controls']['struct_boundary_radix_union']) == 17, 'Outer coverage')
    need(sha(fill) == fill_hash and sha(order) == order_hash, 'Candidate unchanged during replay')
    for name, digest in pins.items():
        need(sha(source/name) == digest, 'Frozen predecessor unchanged: '+name)
        if name.endswith('.py'):
            expected_hash = adaptations[name]['adapted_sha256'] if name in adaptations else digest
            need(sha(package/name) == expected_hash, 'Declared proof/checker source: '+name)
    combined_adapt.authenticate(candidate, reference)
    refit_generate.authenticate()
    need(sha(Path(combined_adapt.__file__)) == adapter_hash, 'Adapter unchanged during replay')
    result = dict(status='PASS_CONCENTRATED_PRELIFE_REFIT_COMPLETE_FRESH_FINITE_ADMISSION_AND_OUTER',
                  driver_sha256=sha(Path(__file__)), adapter_sha256=adapter_hash,
                  candidate_manifest_sha256=combined_adapt.CANDIDATE_MANIFEST,
                  concentrated_source_head=combined_adapt.REFERENCE_HEAD,
                  exact_reference_kappa=original['kappa'],
                  comparison_pr2733_head='2761b52b17590b8cf94f2e410004a8252d5592dc',
                  comparison_pr2733_manifest_sha256=sha(refit_generate.PARENT/'ARTIFACTS.json'),
                  construction_script_sha256=sha(Path(refit_generate.__file__)),
                  checker_adaptations=adaptations,
                  source_head=SOURCE_HEAD, source_manifest_sha256=MANIFEST_SHA,
                  candidate_fill_sha256=fill_hash, candidate_order_sha256=order_hash,
                  kappa=str(k), kappa_decimal=ledger['rows']['struct_boundary_radix_union']['kappa']['decimal'],
                  complex_lower=str(C), global_profile=profile,
                  gain_over_pr2733=str(k-Q(original['kappa'])), stages=stages,
                  native_and_parent_reuse=False, seconds=time.monotonic()-started,
                  inherited_parent_geometry_reuse=parent.get('parent_geometry_reuse'),
                  scope='Finite conditional construction and exact outer inequalities; inherited all-size, machine, analytic and bit assumptions remain.')
    write(work/'RESULT.json', result)
    print(result['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
