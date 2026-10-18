"""Rebuild and admit the rank-seven end pair using pinned predecessor checkers."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import time


PACKAGE = Path(__file__).resolve().parent


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_sha(path):
    return hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def extract_package(archive, destination, prefix):
    with tarfile.open(archive) as source:
        for member in source.getmembers():
            relative = PurePosixPath(member.name)
            need(not relative.is_absolute() and '..' not in relative.parts, 'Unsafe archive member')
            if relative == PurePosixPath(prefix) or PurePosixPath(prefix) in relative.parents:
                target = destination.joinpath(*relative.parts)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    need(member.isfile(), 'Dependency archive must contain regular files')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with source.extractfile(member) as incoming, target.open('wb') as outgoing:
                        shutil.copyfileobj(incoming, outgoing)
            else:
                need(member.isdir() and relative in PurePosixPath(prefix).parents,
                     'Unexpected file outside the pinned package')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True, help='New output directory outside this package')
    parser.add_argument('--git-repository', type=Path,
                        help='Read pinned commits from an existing local repository instead of fetching')
    args = parser.parse_args()
    need(__debug__ and sys.version_info >= (3, 11), 'Python 3.11+ with assertions enabled is required')
    work = args.work.resolve()
    need(not work.exists() and not work.is_relative_to(PACKAGE), 'Use a new external output directory')
    work.mkdir(parents=True)
    pins, expected = read(PACKAGE / 'SOURCES.json'), read(PACKAGE / 'data/EXPECTED.json')
    comparison = PACKAGE / pins['comparison_snapshot']['artifact']
    need(payload_sha(comparison) == pins['comparison_snapshot']['source_content_sha256'],
         'Pinned selected-result comparison snapshot')
    need(read(comparison)['kappa'] == expected['baseline_kappa'], 'Selected comparison value')
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    for name in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD',
                 'MULTICOLD_SOURCE', 'GAIN_PR564_SOURCE', 'SW4_PIN', 'PR635_CODE',
                 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET'):
        environment.pop(name, None)
    stages = []
    started = time.monotonic()

    def run(name, command, binary_output=None):
        print('RUN', name, flush=True)
        begin = time.monotonic()
        log = work / (name + '.log')
        with log.open('wb') as stream:
            if binary_output is None:
                result = subprocess.run(list(map(str, command)), stdout=stream, stderr=subprocess.STDOUT,
                                        env=environment)
            else:
                with binary_output.open('wb') as output:
                    result = subprocess.run(list(map(str, command)), stdout=output, stderr=stream,
                                            env=environment)
        stages.append(dict(name=name, exit_code=result.returncode, seconds=time.monotonic()-begin,
                           log_sha256=sha(log)))
        dump(work / 'STAGES.json', stages)
        if result.returncode:
            raise RuntimeError(name + ' failed:\n' + log.read_text(errors='replace')[-6000:])
        print('PASS', name, flush=True)
        return log.read_text(errors='replace')

    def python(name, script, *arguments):
        return run(name, [sys.executable, '-B', script, *arguments])

    repository = args.git_repository.resolve() if args.git_repository else work / 'source.git'
    if args.git_repository is None:
        run('initialize-source-cache', ['git', 'init', '--bare', repository])
    sources = {}
    for row in pins['sources']:
        number, commit, relative = row['pr'], row['commit'], row['path']
        if args.git_repository is None:
            run(f'fetch-{number}', ['git', '-C', repository, 'fetch', '--no-tags', '--depth=1',
                                   row['repository'], commit])
        run(f'check-commit-{number}', ['git', '-C', repository, 'cat-file', '-e', commit + '^{commit}'])
        archive = work / f'source-{number}.tar'
        run(f'archive-{number}', ['git', '-C', repository, 'archive', '--format=tar', commit, relative],
            binary_output=archive)
        destination = work / f'source-{number}'
        extract_package(archive, destination, relative)
        package = destination / relative
        need(sha(package / 'MANIFEST.json') == row['manifest_sha256'], 'Pinned source manifest')
        actual = {path.relative_to(package).as_posix(): sha(path) for path in package.rglob('*')
                  if path.is_file() and path != package / 'MANIFEST.json' and '__pycache__' not in path.parts}
        manifest = read(package / 'MANIFEST.json')
        need(actual == manifest, f'All source files match PR{number}')
        sources[number] = package
    ancestor, dependency, checker = [sources[number] for number in (741, 799, 777)]
    root = ancestor / 'vendor/main'
    native_source = root / 'research/complex-k492-owner-repair/vendor/multicold'
    routing = native_source / 'vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    pr635 = ancestor / 'vendor/pr635/research/complex-571-cold14-st2'
    baseline = work / 'baseline741'
    python('complete-ancestor-replay', ancestor / 'verify.py', '--work', baseline)

    construction = work / 'baseline799-construction'
    construction.mkdir()
    base_word = construction / 'FULL-WORD.json.gz'
    recipe = dependency / 'construction/jx/RECIPE-X4.json'
    builder = dependency / 'construction/jx/build_jx.py'
    python('rebuild-x4-word', builder, '--input', baseline / 'sw4/FULL-WORD.json.gz',
           '--recipe', recipe, '--out', base_word)
    x4 = read(recipe)
    need(payload_sha(base_word) == x4['expected']['output_content_sha256'] == expected['baseline_word_sha256'],
         'Rebuilt X4 source word')
    control_results = {}
    for name, control in sorted(x4['controls'].items()):
        log = python('x4-control-' + name, builder, '--input', baseline / 'sw4/FULL-WORD.json.gz',
                     '--recipe', recipe, '--control', name)
        if 'rejection_expected' in control:
            need('CONTROL PINNED' in log, 'Expected X4 construction rejection')
            control_results[name] = {'rejected': control['rejection_expected']}
        else:
            need('OK ' + control['expected_sha'] in log, 'Expected X4 construction output')
            control_results[name] = {'content_sha256': control['expected_sha']}
    need(len(control_results) == 7, 'Complete predecessor construction control census')
    dump(construction / 'CONTROLS.json', control_results)

    u8_source = sources[869]
    u8_construction = work / 'baseline869-construction'
    u8_construction.mkdir()
    u8_word = u8_construction / 'FULL-WORD.json.gz'
    u8_recipe = u8_source / 'construction/barch/RECIPE-U8.json'
    python('build-u8-word', u8_source / 'construction/barch/build_tri.py',
           base_word, u8_recipe, u8_word)
    need(payload_sha(u8_word) == read(u8_recipe)['expect_sha256'] == expected['u8_word_sha256'],
         'Rebuilt U8 source word')
    need(sha(u8_source / 'independent/audit_local.py') == sha(dependency / 'independent/audit_local.py'),
         'Unchanged independent U8 auditor')
    python('u8-construction-controls', u8_source / 'construction/barch/run_controls.py',
           base_word, u8_recipe, u8_source / 'independent/audit_local.py', u8_construction / 'controls')
    u8_controls = read(u8_construction / 'controls/controls.json')
    need(len(u8_controls) == 38 and all(row['ok'] is True for row in u8_controls.values()),
         'Complete U8 construction control census')

    word = work / 'FULL-WORD.json.gz'
    python('build-end-pair', PACKAGE / 'build_word.py', '--input', u8_word, '--output', word)
    need(payload_sha(word) == expected['word_sha256'], 'Minimal candidate word')
    python('independent-point-audit', PACKAGE / 'audit_points.py', '--baseline', u8_word,
           '--word', word, '--output', work / 'POINT-AUDIT.json')
    python('end-pair-controls', PACKAGE / 'end_controls.py', '--word', word,
           '--independent-auditor', dependency / 'independent/audit_local.py',
           '--native-auditor', pr635 / 'code/hpe_audit_and_transport.py',
           '--portable-runner', native_source / 'code/run_portable.py',
           '--routing', routing, '--main', root, '--output', work / 'end-controls')
    owners = work / 'owners'
    python('rebuild-owners', PACKAGE / 'build_owners.py', '--word', word,
           '--plan', dependency / 'data/PLAN.json', '--out', owners)
    need(payload_sha(owners / 'OWNERS.json.gz') == expected['owners_sha256'], 'Exact literal owner assignment')
    native = work / 'native'
    python('complete-native-replay', PACKAGE / 'code/replay_native.py', '--ancestor-package', ancestor,
           '--dependency', dependency, '--raw', word, '--out', native)
    native_result = read(native / 'RESULT.json')
    need(native_result['pins'] == expected['native_pins'], 'Every proof-relevant native output')
    admission = work / 'admission'
    python('complete-global-admission', PACKAGE / 'code/admit_candidate.py', '--ancestor-package', ancestor,
           '--ancestor-replay', baseline, '--dependency', dependency, '--checker-package', checker,
           '--native', native, '--owners', owners / 'OWNERS.json.gz',
           '--comparison-record', comparison, '--out', admission)
    admitted = read(admission / 'RESULT.json')
    for field in ('kappa', 'kappa_decimal', 'complex_lower', 'bit_lower', 'global_profile', 'gain'):
        need(admitted[field] == expected[field], 'Frozen admitted result: ' + field)
    result = dict(status='PASS_COLD_RANK7_END_PAIR_COMPLETE_ADMISSION',
                  kappa=admitted['kappa'], kappa_decimal=admitted['kappa_decimal'], gain=admitted['gain'],
                  baseline_kappa=admitted['baseline_kappa'], global_profile=admitted['global_profile'],
                  sources=pins, word_sha256=payload_sha(word), owners_sha256=payload_sha(owners / 'OWNERS.json.gz'),
                  native_pins=native_result['pins'], seconds=time.monotonic()-started, stages=stages,
                  scope='Fresh pinned ancestor, X4 and U8 constructions, minimal end recipe, independent point audit, '
                        'targeted controls, exact owner reconstruction, complete native and strict global admission. '
                        'The cited PR589 bit circuit is repriced. Inherited uniform and analytic assumptions remain.')
    dump(work / 'RESULT.json', result)
    outputs = ['RESULT.json', 'STAGES.json', 'POINT-AUDIT.json', 'FULL-WORD.json.gz',
               'baseline741/RESULT.json', 'baseline741/RECEIPT.json', 'baseline741/ANCESTRAL-LINK.json',
               'baseline799-construction/CONTROLS.json', 'owners/OWNERS.json.gz',
               'baseline869-construction/FULL-WORD.json.gz', 'baseline869-construction/controls/controls.json',
               'native/RESULT.json', 'native/RECEIPT.json', 'admission/RESULT.json', 'admission/RECEIPT.json']
    dump(work / 'RECEIPT.json', dict(status=result['status'],
         artifacts={name: sha(work / name) for name in outputs},
         package_inputs={str(path.relative_to(PACKAGE)): sha(path) for path in PACKAGE.rglob('*')
                         if path.is_file() and '__pycache__' not in path.parts}))
    print(result['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
