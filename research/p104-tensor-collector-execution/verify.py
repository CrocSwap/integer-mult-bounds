"""Read-only source-bound replay; timing fields are not acceptance criteria."""
import argparse
import json
from pathlib import Path
import sys
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter
from lanes import need
import run


TRANSIENT = {'execution_seconds', 'oracle_check_seconds', 'peak_rss_kib', 'python', 'mode'}


def stable(result):
    return {k: v for k, v in result.items() if k not in TRANSIENT}


def equal(actual, expected, message):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def check_small():
    result = {}
    for fixture in ['promoted', 'rounding', 'cancellation', 'zero']:
        old = run.run('original', 1, fixture)
        new = run.run('packed', 1, fixture)
        equal(stable(old), stable(new), 'complete original/packed receipt: ' + fixture)
        result[fixture] = stable(new)
    # A source change must fail before the modified bytes are executed.
    read = Path.read_bytes
    for suffix in ['research/dense-paired-collector/model.py',
                   'research/dense-paired-collector/inputs/pr3109.tar',
                   'research/p104-tensor-collector-execution/vendor/oracle.py']:
        def altered(path, target=suffix):
            data = read(path)
            return data + b'\nchanged' if str(path).endswith(target) else data
        with mock.patch.object(Path, 'read_bytes', altered), mock.patch.object(run.importlib.util, 'module_from_spec', side_effect=AssertionError('vendor executed before authentication')) as loader:
            try:
                run.vendor()
            except ValueError as exc:
                need('authenticated input:' in str(exc), 'source rejection reason')
                need(not loader.called, 'reject before vendor execution')
            else:
                raise ValueError('source corruption was accepted: ' + suffix)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--suite', choices=['small', 'tensor'], required=True)
    p.add_argument('--emit', action='store_true', help='Print a candidate receipt; do not rewrite expected files')
    args = p.parse_args()
    actual = check_small() if args.suite == 'small' else stable(run.run('packed', 2))
    if args.emit:
        print(json.dumps(actual, sort_keys=True, indent=2))
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text())[args.suite]
        equal(actual, expected, 'complete typed expected receipt')
        print('PASS_P104_PACKED_' + args.suite.upper() + ' exact_arrays_and_retained_cleanup no_new_kappa')


if __name__ == '__main__':
    main()
