"""Exercise complete cached-baseline coverage without rerunning its circuits."""
import argparse
import copy
import gzip
import json
import shutil
from pathlib import Path

from baseline_cache import covered_files, read, validate_baseline


def corrupt_phase(data):
    document = json.loads(data)
    def change(value):
        if isinstance(value,dict):
            if type(value.get('phase')) is int:
                value['phase'] = (value['phase']+1)%4
                return True
            return any(change(child) for child in value.values())
        if isinstance(value,list):
            return any(change(child) for child in value)
        return False
    if not change(document):
        raise ValueError('No phase field in retained recipe fixture')
    return json.dumps(document).encode()


def main():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled for cache controls')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--source-package', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    baseline, package = args.baseline.resolve(), args.source_package.resolve()
    receipt = read(baseline/'PORTABLE-RESULT.json')
    honest = validate_baseline(baseline, package, receipt)
    fixture = work/'baseline'
    fixture.mkdir()
    for relative, path in covered_files(baseline).items():
        target = fixture/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    validate_baseline(fixture, package, receipt)
    checks = []

    def reject(name, operation, undo, altered_receipt=receipt):
        operation()
        try:
            validate_baseline(fixture, package, altered_receipt)
        except (AssertionError, KeyError, ValueError) as error:
            checks.append({'name': name, 'rejected': True,
                           'reason': str(error)})
        else:
            raise RuntimeError('Accepted changed cached baseline: '+name)
        finally:
            undo()

    def altered_file(name, relative, replacement):
        path = fixture/relative
        original = path.read_bytes()
        reject(name, lambda: path.write_bytes(replacement(original)),
               lambda: path.write_bytes(original))

    word = fixture/'native-new-base/local/FULL-WORD.json.gz'
    original = word.read_bytes()
    word.write_bytes(gzip.compress(gzip.decompress(original), mtime=1))
    validate_baseline(fixture, package, receipt)
    checks.append({'name': 'gzip-container-header-only', 'accepted': True})
    word.write_bytes(original)
    altered_file('previously-unselected-source',
                 'parent/layout/packing74/replay.py', lambda data: data+b'\n# changed\n')
    altered_file('retained-native-phase-recipe',
                 'parent/native-base/local/CLIFFORD-RECIPES.json',
                 corrupt_phase)
    altered_file('changed-native-phase-status',
                 'native-new-extra/local/CLIFFORD-REVIEW.json',
                 lambda data: json.dumps(dict(json.loads(data),
                    all_child_equalities_include_global_phase=False)).encode())
    altered_file('stale-native-word', 'native-new-base/local/FULL-WORD.json.gz',
                 lambda data: gzip.compress(json.dumps(dict(
                    json.loads(gzip.decompress(data)), R=-1)).encode(),mtime=0))
    missing = fixture/'native-new-base/local/WRAPPER-CHECKS.json'
    stash = work/'stashed-wrapper.json'
    reject('missing-proof-artifact', lambda: missing.rename(stash),
           lambda: stash.rename(missing))
    extra = fixture/'UNBOUND.json'
    reject('unexpected-proof-artifact', lambda: extra.write_text('{}\n'), extra.unlink)
    incomplete = copy.deepcopy(receipt)
    incomplete['bindings'].pop('parent/layout/packing74/replay.py')
    reject('incomplete-bindings-receipt', lambda: None, lambda: None, incomplete)
    chain = copy.deepcopy(receipt)
    chain['native_chains']['retained-base']['steps'][4]['exit_code'] = 1
    reject('stale-retained-chain', lambda: None, lambda: None, chain)
    result = {'status': 'PASS_COMPLETE_BASELINE_CACHE_CONTROLS',
              'native_pipeline_rerun': False, 'honest': honest, 'checks': checks,
              'positive_controls': sum(c.get('accepted',False) for c in checks),
              'negative_controls': sum(c.get('rejected',False) for c in checks)}
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
