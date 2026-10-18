#!/usr/bin/env python3
"""Cold replay of the pinned PR2288 supplier and its retained outer proof.

This wrapper preserves the predecessor's programs and proof checks. On POSIX
it accepts only the known four generated-JSON newline differences, restores
their committed encoding, and executes the original remaining checks.
Predecessor credit: PR2288 and its retained notices. Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from fractions import Fraction as Q
from pathlib import Path
from baseline_cache import seal_completed_baseline, validate_baseline

HEAD = '614c74a63b0f6d4a24c7740d7ddb90d37861b3c7'
PACKAGE_PATH = 'research/gmx-t74-borrow43-refit'
MANIFEST_SHA256 = '557d8d6cfe0768c427e564beed37fbdfe3f65d10367f4c3a3dc36359c89cc62b'
STABLE = ('LOCAL-CHECKS.json', 'CLIFFORD-RECIPES.json', 'RESIDUAL-ADAPTERS.json')
NATIVE_STEPS = ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
MUTABLE_RECEIPTS = (
    'new/borrow/receipts/AUDIT-43base-prerefit.json',
    'new/borrow/receipts/AUDIT-43base.json',
    'new/borrow/receipts/CONTROLS-43base.json',
    'new/borrow/receipts/AUDIT-43extra.json',
    'new/borrow/receipts/CONTROLS-43extra.json',
)
EXPECTED_STOP = ('regenerated PLAN differs from new/PLAN.json beyond '
                 'bind-rebound receipt hashes')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def lf(data):
    return data.replace(b'\r\n', b'\n')


def bind_view(plan):
    result = copy.deepcopy(plan)
    for desc in result['provider_registry'].values():
        desc['artifact_sha256'] = {
            name: digest for name, digest in desc['artifact_sha256'].items()
            if name in STABLE
        }
    return result


def differences(left, right, prefix=()):
    if isinstance(left, dict) and isinstance(right, dict):
        out = []
        for key in sorted(set(left) | set(right)):
            if key not in left or key not in right:
                out.append(prefix + (key,))
            else:
                out.extend(differences(left[key], right[key], prefix + (key,)))
        return out
    return [] if left == right else [prefix]


def check_manifest(package):
    require(sha(package / 'MANIFEST.json') == MANIFEST_SHA256,
            'The upstream package manifest is not the pinned PR2288 manifest')
    expected = read(package / 'MANIFEST.json')
    actual = {p.relative_to(package).as_posix(): sha(p)
              for p in package.rglob('*') if p.is_file()
              and p != package / 'MANIFEST.json' and '__pycache__' not in p.parts}
    require(actual == expected, 'Upstream package inventory or file hashes differ')
    return expected


class Runner:
    def __init__(self, root):
        self.root = root
        self.stages = []
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                        PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
                        OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                        FINE_ENGINE_CACHE=str(root / 'verify/fine-cache'),
                        TMPDIR=str(root / 'tmp'))
        for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD',
                    'WITNESS_SPEC', 'GAIN_PR564_SOURCE', 'MULTICOLD_SOURCE'):
            self.env.pop(key, None)

    def run(self, name, script, *args, allow_failure=False):
        command = [sys.executable, '-B', str(script), *map(str, args)]
        log = self.root / (name + '.log')
        started = time.monotonic()
        with log.open('wb') as output:
            result = subprocess.run(command, cwd=self.root, env=self.env,
                                    stdin=subprocess.DEVNULL, stdout=output,
                                    stderr=subprocess.STDOUT)
        stage = dict(name=name, command=command, cwd=str(self.root),
                     returncode=result.returncode,
                     seconds=round(time.monotonic() - started, 3),
                     log=log.relative_to(self.root).as_posix(),
                     log_sha256=sha(log))
        self.stages.append(stage)
        write(self.root / 'STAGES.json', self.stages)
        if not allow_failure:
            require(result.returncode == 0,
                    name + ' failed: ' + log.read_text(errors='replace')[-2500:])
            print('PASS', name, flush=True)
        return stage


def check_stage_receipt(path):
    rows = read(path)
    require(rows and all(row['exit_code'] == 0 for row in rows),
            'An upstream stage did not pass: ' + str(path))
    for row in rows:
        if 'log_sha256' in row:
            log = path.parent / (row['name'] + '.log')
            require(log.is_file() and sha(log) == row['log_sha256'],
                    'Upstream stage log binding differs: ' + str(log))
    return rows


def check_cold_inputs(package, verify):
    parent = read(verify / 'parent/RESULT.json')
    require(parent['status'] ==
            'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION',
            'The retained parent admission did not pass')
    require(parent['base_native_reuse'] is False and
            parent['extra_native_reuse'] is False,
            'The cold replay unexpectedly reused retained natives')
    upstream = check_stage_receipt(verify / 'STAGES.json')
    expected_stages = {'fine-engine-oracle', 'retained-provider-and-parent-admission',
        'native-new-base', 'native-new-extra', 'reconstruct-owners', 'lift-parent',
        'rebuild-words-566', 'rebuild-borrow-words', 'audit-local-566-base',
        'audit-local-566-extra', 'rebind-566', 'lemmag-labels'}
    require(expected_stages <= {row['name'] for row in upstream},
            'The original verifier did not complete all required preceding stages')
    check_stage_receipt(verify / 'parent/STAGES.json')
    for kind in ('base', 'extra'):
        for retained in (False, True):
            directory = verify / (('parent/native-' if retained else 'native-new-') + kind)
            steps = read(directory / 'STEPS.json')
            require([x['step'] for x in steps] == NATIVE_STEPS and
                    all(x['exit_code'] == 0 for x in steps),
                    'A complete five-stage native chain is missing: ' + str(directory))
            word = package / ('vendor/pr1297/' +
                ('gauge44-word.json.gz' if kind == 'base' else 'extra-word.json.gz')
                if retained else
                'new/borrow/words/BORROW-WORD-43' + kind + '.json.gz')
            require(gzip.decompress((directory / 'local/FULL-WORD.json.gz').read_bytes())
                    == gzip.decompress(word.read_bytes()),
                    'A cold native chain is not bound to its shipped word')
    labels = read(verify / 'LEMMAG-LABELS.json')
    for kind in ('base', 'extra'):
        key = str(verify / ('native-new-' + kind))
        require(key in labels, 'Missing changed-provider Lemma G evidence')
        row = labels[key]
        require(set(row['honest']) == {'forward', 'backward'} and
                all(value == 0 for result in row['honest'].values()
                    for value in result.values()), 'Lemma G honest checks failed')
        require(set(row['mutants']) == {'X', 'Y', 'Z'} and
                all(x['rejected'] is True for x in row['mutants'].values()) and
                row.get('borrow_mutants') and all(row['borrow_mutants'].values()),
                'Lemma G rejecting controls did not pass')


def finish_posix(package, verify, runner):
    require(os.name == 'posix', 'Only the known POSIX newline stop can be resumed')
    original = read(package / 'new/PLAN.json')
    before_plan = read(verify / 'data-rebound/PLAN.json')
    expected = {('provider_registry', provider, 'artifact_sha256', name)
                for provider in ('gauge44', 'extra')
                for name in ('LOCAL-CHECKS.json', 'RESIDUAL-ADAPTERS.json')}
    require(set(differences(bind_view(original), bind_view(before_plan))) == expected,
            'The original verifier stopped on more than the four known newline hashes')
    normalization = []
    for provider, kind in (('gauge44', 'base'), ('extra', 'extra')):
        for name in ('LOCAL-CHECKS.json', 'RESIDUAL-ADAPTERS.json'):
            path = verify / ('native-new-' + kind) / 'local' / name
            before = path.read_bytes()
            after = lf(before).replace(b'\n', b'\r\n')
            wanted = original['provider_registry'][provider]['artifact_sha256'][name]
            require(before != after and json.loads(before) == json.loads(after) and
                    hashlib.sha256(after).hexdigest() == wanted,
                    'Generated JSON differs by more than its committed newline encoding')
            saved = verify / 'pre-normalization' / provider / name
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(before)
            path.write_bytes(after)
            normalization.append(dict(provider=provider, artifact=name,
                original_generated_sha256=sha(saved), normalized_sha256=sha(path),
                immutable_pin=wanted, parsed_json_unchanged=True))
    write(verify / 'NATIVE-CRLF-NORMALIZATION.json', normalization)
    rebound = verify / 'portable-rebound'
    runner.run('portable-rebind', package / 'new/rebind.py', package,
               verify / 'native-new-base/local', verify / 'native-new-extra/local', rebound)
    require(bind_view(read(rebound / 'PLAN.json')) == bind_view(original),
            'Normalized native rebound PLAN differs from the immutable PLAN')
    require(read(rebound / 'PROFILE.json') == read(package / 'new/PROFILE.json'),
            'Normalized rebound profile differs')
    layout = verify / 'parent/layout'
    runtime = layout / 'packing74'
    runtime.mkdir()
    data = runtime / 'candidate'
    data.mkdir()
    for name in ('replay.py', 'freeze_spec.py', 'audit_mixed.py', 'independent_core.py',
                 'geometry_controls.py', 'audit_fast.py'):
        shutil.copy2(package / name, runtime / name)
    for name in ('code', 'construction'):
        shutil.copytree(package / name, runtime / name)
    (runtime / 'inputs').mkdir()
    shutil.copy2(package / 'inputs/PR589-EXPECTED.json', runtime / 'inputs/PR589-EXPECTED.json')
    for name in ('PLAN.json', 'SPEC.json', 'PROFILE.json', 'OWNERS.json.gz',
                 'DISPATCH.json', 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz'):
        source = package / ('new' if name in ('PLAN.json', 'SPEC.json', 'PROFILE.json') else '') / name
        shutil.copy2(source, data / name)
    shutil.copytree(verify / 'native-new-extra', runtime / 'native-extra')
    runner.run('portable-strict-t74', runtime / 'replay.py', '--data', data,
               '--work', verify / 'strict', '--local', verify / 'native-new-base/local')
    runner.run('portable-geometry-controls', runtime / 'geometry_controls.py',
               '--source', layout / 'joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold',
               '--strict', verify / 'strict', '--out', verify / 'GEOMETRY-CONTROLS.json')
    return normalization


def replay_outer(package, root, runner):
    temporary = root / 'outer-tmp'
    (temporary / 'new').mkdir(parents=True)
    shutil.copytree(package / 'outer', temporary / 'outer')
    shutil.copy2(package / 'new/SPEC.json', temporary / 'new/SPEC.json')
    shutil.copy2(package / 'CLAIM.json', temporary / 'CLAIM.json')
    for artifact in ('LEDGER.json', 'INDEPENDENT.json'):
        (temporary / 'outer' / artifact).unlink()
    for name in ('check_ledger.py', 'independent_check.py'):
        runner.run('outer-' + name[:-3], temporary / 'outer' / name)
    comparisons = []
    for name in ('LEDGER.json', 'INDEPENDENT.json'):
        fresh, committed = temporary / 'outer' / name, package / 'outer' / name
        require(read(fresh) == read(committed) and lf(fresh.read_bytes()) == lf(committed.read_bytes()),
                'Regenerated outer artifact differs after newline normalization: ' + name)
        comparisons.append(dict(artifact=name, generated_sha256=sha(fresh),
                                committed_sha256=sha(committed), parsed_json_equal=True,
                                normalized_bytes_equal=True))
    for name in ('sched_test.py', 'sched_review.py', 'struct_check.py',
                 'check_gaugefree.py', 'check_fine_padding.py', 'replay_evidence.py'):
        args = ('--out', root / 'fine-padding.json') if name == 'check_fine_padding.py' else ()
        runner.run('outer-' + name[:-3], package / 'outer' / name, *args)
    write(root / 'OUTER-ARTIFACT-COMPARISON.json', comparisons)
    return read(temporary / 'outer/LEDGER.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Run this wrapper with assertions enabled')
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    provided_package = args.source_root.resolve() / PACKAGE_PATH
    root = args.work.resolve()
    require(not root.exists() and not root.is_relative_to(provided_package),
            'Work must be a new directory outside the upstream package')
    manifest = check_manifest(provided_package)
    root.mkdir(parents=True)
    (root / 'tmp').mkdir()
    # The predecessor rebuild regenerates diagnostic files in its own package.
    # Stage identical mathematical inputs so a read-only or reused source root
    # remains untouched and incidental bytecode caches cannot enter its audit.
    package = root / 'source' / PACKAGE_PATH
    shutil.copytree(provided_package, package,
                    ignore=shutil.ignore_patterns('__pycache__'))
    check_manifest(package)
    originals = root / 'source-receipts-original'
    for relative in MUTABLE_RECEIPTS:
        target = originals / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(package / relative, target)
        require(sha(target) == manifest[relative], 'Source receipt backup differs')
    runner = Runner(root)
    verify = root / 'verify'
    restored = []
    try:
        cold = runner.run('original-cold-verify', package / 'verify.py', '--work', verify,
                          allow_failure=True)
        check_cold_inputs(package, verify)
        normalization = []
        if cold['returncode']:
            log = (root / cold['log']).read_text(errors='replace').strip()
            require(log.splitlines()[-1] == 'AssertionError: ' + EXPECTED_STOP,
                    'The original cold verifier failed outside the known newline stop')
            require(not (verify / 'strict').exists() and
                    not (verify / 'parent/layout/packing74').exists(),
                    'Unexpected partial strict replay at the portability stop')
            cold['accepted_portability_stop'] = EXPECTED_STOP
            normalization = finish_posix(package, verify, runner)
        else:
            require(read(verify / 'RESULT.json')['status'] ==
                    'PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION',
                    'Original verifier returned without complete admission')
        strict, assembly = read(verify / 'strict/RESULT.json'), read(verify / 'strict/ASSEMBLY.json')
        require(strict['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL' and
                assembly['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' and
                len(assembly['outer']) == 47 and
                Q(strict['kappa']) == Q(assembly['kappa']) == Q(read(package / 'CLAIM.json')['kappa']),
                'Strict supplier result does not match the immutable claim')
        require(len(read(verify / 'GEOMETRY-CONTROLS.json')['rejected']) == 6,
                'Missing geometry rejecting controls')
        check_stage_receipt(verify / 'strict/STAGES.json')
        ledger = replay_outer(package, root, runner)
        spec, bj = read(package / 'new/SPEC.json'), read(package / 'outer/B.json')
        require(Q(assembly['complex_lower']) == Q(spec['expected']['complex_lower']) and
                Q(bj['b']) < Q(assembly['complex_lower']) < Q(bj['b_above_endpoint']),
                'Actual supplier endpoint does not bracket the outer input')
        require({int(k): v for k, v in assembly['complex_profile'].items()} ==
                {int(k): v for k, v in bj['profile'].items()} ==
                {int(k): v for k, v in spec['expected']['global_profile'].items()} and
                Q(assembly['bit_lower']) == Q('.001733427039589844234749'),
                'Actual supplier profile or bit endpoint differs from the ledger')
        final = ledger['rows']['struct_boundary_radix_union']['kappa']
        claim = read(package / 'outer/OUTER-CLAIM.json')
        require(Q(final['rational']) == Q(final['decimal']) == Q(claim['kappa']) ==
                Q(assembly['complex_lower']) - Q(1, 10**3046) - Q(1, 10**3022),
                'Outer kappa differs from its exact fixed-grid identity')
    finally:
        for relative in MUTABLE_RECEIPTS:
            current, original = package / relative, originals / relative
            require(original.is_file() and sha(original) == manifest[relative],
                    'Immutable source receipt backup is unavailable')
            saved = root / 'fresh-rebuilt-source-receipts' / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            if current.is_file():
                shutil.copy2(current, saved)
            fresh_sha256 = sha(saved) if saved.is_file() else None
            shutil.copy2(original, current)
            restored.append(dict(path=relative, fresh_sha256=fresh_sha256,
                changed_by_rebuild=fresh_sha256 != manifest[relative],
                immutable_sha256=manifest[relative]))
        write(root / 'SOURCE-RECEIPT-RESTORATION.json', restored)
        check_manifest(package)
    runner.run('final-unchanged-source-manifest', package / 'verify_manifest.py')
    bindings = {}
    required = ('strict/RESULT.json', 'strict/ASSEMBLY.json', 'strict/INDEPENDENT.json',
        'strict/global/audit/OWNERS-AND-PROFILE.json',
        'strict/global/audit/PREFIX-AND-INVOICE.json',
        'LEMMAG-LABELS.json', 'GEOMETRY-CONTROLS.json', 'STAGES.json', 'parent/RESULT.json')
    for relative in required:
        bindings[relative] = sha(verify / relative)
    chains = {}
    for kind in ('base', 'extra'):
        directory = verify / ('native-new-' + kind)
        chains[kind] = dict(directory=directory.relative_to(verify).as_posix(),
                            steps_sha256=sha(directory / 'STEPS.json'),
                            steps=read(directory / 'STEPS.json'))
        for item in directory.rglob('*'):
            if item.is_file():
                bindings[item.relative_to(verify).as_posix()] = sha(item)
    result = dict(status='PASS_PORTABLE_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION',
        head=HEAD, manifest_sha256=MANIFEST_SHA256, source_package=PACKAGE_PATH,
        source_final_manifest_matches=True, cold_native_reuse=False,
        strict_kappa=assembly['kappa'], complex_lower=assembly['complex_lower'],
        bit_lower=assembly['bit_lower'], profile=assembly['complex_profile'],
        final_upstream_kappa=final['rational'], bindings=bindings,
        native_chains=chains, normalization=normalization,
        stages=runner.stages, original_cold_verifier=cold,
        upstream_stages=read(verify / 'STAGES.json'),
        parent_stages=read(verify / 'parent/STAGES.json'),
        strict_stages=read(verify / 'strict/STAGES.json'),
        outer_bindings={name: sha(root / 'outer-tmp/outer' / name)
                        for name in ('LEDGER.json', 'INDEPENDENT.json')},
        wrapper_sha256=sha(Path(__file__)),
        portability='Only the four generated JSON newline encodings and the '
            'five regenerated source diagnostic receipts are normalized or restored; '
            'all predecessor mathematical checks and exact source pins are retained.',
        scope=read(package / 'CLAIM.json')['scope'])
    result = seal_completed_baseline(verify, package, result)
    result['cache_validation'] = validate_baseline(verify, package, result)
    write(verify / 'PORTABLE-RESULT.json', result)
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
