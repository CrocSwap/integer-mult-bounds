#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fast, source-bound local verification for Yiyang (@Lyy-iiis).

Prepared with substantial OpenAI Codex assistance. This wrapper authenticates
all LOCAL-PINS.json fixtures, imports only the pinned pure producer, and runs
the separate independent checker. It does not establish owner, native-phase,
packing, outer-moment, or full inherited-source-release admission.
"""
import sys
if not __debug__:
    raise SystemExit('Refusing Python -O/-OO: fast verification requires active assertions in its independent checker.')
sys.dont_write_bytecode = True
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else sha_bytes(stream.read())


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON key: ' + str(key))
        out[key] = value
    return out


def checked_fixture(package, relative, expected):
    require(isinstance(relative, str) and isinstance(expected, str), 'invalid pin entry types')
    name = Path(relative)
    require(not name.is_absolute() and '..' not in name.parts, 'unsafe fixture path: ' + relative)
    path = (package / name).resolve()
    require(package in path.parents and path.is_file(), 'fixture missing or outside package: ' + relative)
    require(len(expected) == 64 and all(c in '0123456789abcdef' for c in expected), 'invalid SHA256 pin: ' + relative)
    actual = sha_file(path)
    require(actual == expected, 'fixture SHA256 mismatch: ' + relative)
    return actual


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def run_checker(checker, source, candidate, directory, expected_failure=None):
    directory.mkdir()
    receipt = directory / 'CHECK.json'
    command = [sys.executable, '-I', '-B', str(checker), '--source-word', str(source),
               '--candidate-word', str(candidate), '--out', str(receipt)]
    process = subprocess.run(command, cwd=directory, capture_output=True, text=True,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    (directory / 'stdout.txt').write_text(process.stdout)
    (directory / 'stderr.txt').write_text(process.stderr)
    result = dict(command=command, returncode=process.returncode,
                  source_sha256=sha_file(source), candidate_sha256=sha_file(candidate))
    if expected_failure is None:
        require(process.returncode == 0 and receipt.is_file(), 'independent checker failed: ' + str(directory))
        data = json.loads(receipt.read_text())
        require(data.get('status') == 'PASS_INDEPENDENT_FOUR_GROUP_LOCAL_DIFFERENTIAL_AUDIT',
                'unexpected independent checker status')
        result.update(status='PASS', receipt=str(receipt))
    else:
        lines = [line.strip() for line in process.stderr.splitlines() if line.strip()]
        expected_last = 'AssertionError: ' + expected_failure
        require(process.returncode != 0 and lines and lines[-1] == expected_last,
                'fault rejected for unexpected reason: ' + str(directory))
        require(not receipt.exists(), 'fault checker wrote a success receipt')
        result.update(status='EXPECTED_REJECTION', failure=expected_failure,
                      scope='The independent checker rejects the altered literal structure; endpoint controls are retained separately.')
    dump(directory / 'RUN.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--work', type=Path, help='fresh directory outside the package for all receipts')
    args = parser.parse_args()
    package = args.package.resolve()
    manifest = package / 'LOCAL-PINS.json'
    manifest_bytes = manifest.read_bytes()
    pins = json.loads(manifest_bytes, object_pairs_hook=unique_object)
    require(isinstance(pins, dict) and pins, 'LOCAL-PINS.json must be a nonempty object')
    # Every listed fixture is checked with explicit conditions, before imports or writes.
    before = {name: checked_fixture(package, name, expected) for name, expected in sorted(pins.items())}
    required = ['shared_kernel.py', 'check_four_kernels.py']
    for variant in ('base', 'extra'):
        required += [f'sources/PR2833-WORD-{variant}.json.gz', f'words/WORD-{variant}.json.gz']
    require(all(name in pins for name in required), 'missing required producer/checker/word pins')
    if args.work is None:
        temporary_root = Path(tempfile.gettempdir()).resolve()
        require(temporary_root != package and package not in temporary_root.parents,
                'temporary root is inside package; pass --work outside package')
        work = Path(tempfile.mkdtemp(prefix='shared-kernel-fast-', dir=temporary_root)).resolve()
    else:
        work = args.work.resolve()
        require(work != package and package not in work.parents, 'work directory must be outside package')
        require(not work.exists(), 'work directory must be fresh')
        work.mkdir(parents=True)
    spec = importlib.util.spec_from_file_location('_pinned_shared_kernel_fast_verify', package / 'shared_kernel.py')
    require(spec is not None and spec.loader is not None, 'cannot load pinned producer')
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    checker = package / 'check_four_kernels.py'
    positives = []
    source_controls = []
    sources = {}
    candidates = {}
    ledgers = {}
    for variant in ('base', 'extra'):
        source_path = package / f'sources/PR2833-WORD-{variant}.json.gz'
        candidate_path = package / f'words/WORD-{variant}.json.gz'
        source = json.loads(gzip.decompress(source_path.read_bytes()))
        candidate = json.loads(gzip.decompress(candidate_path.read_bytes()))
        original = copy.deepcopy(source)
        changed, ledger = producer.apply(source)
        require(source == original, 'pure producer mutated decoded source: ' + variant)
        require(changed == candidate, 'derived word differs from pinned candidate: ' + variant)
        sources[variant], candidates[variant], ledgers[variant] = source, candidate, ledger
        derived_path = work / f'DERIVED-{variant}.json.gz'
        derived_path.write_bytes(gzip.compress(json.dumps(changed, separators=(',', ':')).encode(), mtime=0))
        dump(work / f'PRODUCER-{variant}.json', dict(ledger=ledger, decoded_equal=True,
             source_unchanged=True, source_sha256=sha_file(source_path),
             pinned_candidate_sha256=sha_file(candidate_path), derived_sha256=sha_file(derived_path)))
        positives.append(run_checker(checker, source_path, derived_path, work / f'positive-{variant}'))
        bad_source = copy.deepcopy(source)
        bad_source['report']['R'] += 1
        try:
            producer.apply(bad_source)
        except ValueError as error:
            require(str(error) == 'unauthorized decoded source SHA256', 'unexpected bad-source producer failure')
        else:
            raise RuntimeError('producer accepted an unauthorized decoded source: ' + variant)
        source_controls.append(dict(variant=variant, control='producer_bad_source',
                                    rejected=True, reason='unauthorized decoded source SHA256'))
        require(source == original, 'bad-source control mutated original decoded source')
    # Three targeted faults in actual candidate words, without rerunning the larger native suite.
    mutants = []
    missing = copy.deepcopy(candidates['base'])
    bridge = ['add', 490, 478, -1, 1, [25]]
    require(missing['A'].count(bridge) == 1, 'new A bridge is not unique')
    missing['A'].remove(bridge)
    mutants.append(('missing_new_A', 'base', missing, 'exact_twenty_insertions_no_hidden_scalar_changes'))
    wrong_comp = copy.deepcopy(candidates['extra'])
    require(wrong_comp['compensation'][-1][0] == 'add', 'last compensation gate shape')
    wrong_comp['compensation'][-1][3] *= -1
    mutants.append(('wrong_compensation', 'extra', wrong_comp, 'exact_compensation_column_replacements'))
    stale = copy.deepcopy(candidates['base'])
    inverse_bridge = ['add', 490, 478, 1, 1, [256,128,64,32,16,8,4,2,1]]
    require(stale['cleanup'].count(inverse_bridge) == 1, 'new cleanup inverse is not unique')
    stale['cleanup'].remove(inverse_bridge)
    mutants.append(('stale_cleanup_missing_new_inverse', 'base', stale,
                    'exact_inverse_reverse_cleanup_excludes_prelude_targets_and_uses_private_buffers'))
    negatives = []
    for name, variant, mutant, failure in mutants:
        path = work / (name + '.json.gz')
        path.write_bytes(gzip.compress(json.dumps(mutant, separators=(',', ':')).encode(), mtime=0))
        negatives.append(run_checker(checker, package / f'sources/PR2833-WORD-{variant}.json.gz',
                                     path, work / name, expected_failure=failure))
    # Explicit SHA failure and optimization-rejection controls also work under normal Python.
    try:
        checked_fixture(package, 'shared_kernel.py', '0' * 64)
    except RuntimeError as error:
        require(str(error) == 'fixture SHA256 mismatch: shared_kernel.py', 'unexpected pin failure')
    else:
        raise RuntimeError('wrong producer SHA pin accepted')
    optimized_work = work / 'optimized-must-not-exist'
    optimized = subprocess.run([sys.executable, '-O', '-B', str(Path(__file__).resolve()),
                               '--package', str(package), '--work', str(optimized_work)],
                              cwd=work, capture_output=True, text=True,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    require(optimized.returncode != 0 and 'Refusing Python -O/-OO:' in optimized.stderr
            and not optimized_work.exists(), 'optimized invocation was not rejected before output')
    dump(work / 'OPTIMIZATION-REJECTION.json', dict(returncode=optimized.returncode,
         stdout=optimized.stdout, stderr=optimized.stderr, output_created=False))
    after = {name: checked_fixture(package, name, expected) for name, expected in sorted(pins.items())}
    require(before == after and manifest.read_bytes() == manifest_bytes, 'pinned package inputs changed during verification')
    result = dict(status='PASS_FAST_SHARED_KERNEL_LOCAL_VERIFY', package=str(package),
                  manifest_sha256=sha_bytes(manifest_bytes), authenticated_fixture_count=len(pins),
                  imported_package_modules=['shared_kernel.py'], positives=positives,
                  word_faults=negatives, source_controls=source_controls,
                  incorrect_fixture_pin_rejected=True, optimized_mode_rejected_before_write=True,
                  all_pinned_inputs_unchanged=True, before=before, after=after,
                  remaining_admission=['constructive owner/layout verification', 'complete native phase/Gaussian and inherited-source release',
                                       'all returned-idle costs and exact full outer moment', 'selected-parent admission'],
                  scope='Fast local reproducibility and differential checks only; this wrapper does not certify the bound.')
    dump(work / 'FAST-VERIFY.json', result)
    print(json.dumps(dict(status=result['status'], fixtures=len(pins), positive_words=2,
                         actual_word_faults=3, receipt=str(work / 'FAST-VERIFY.json')), sort_keys=True))


if __name__ == '__main__':
    main()
