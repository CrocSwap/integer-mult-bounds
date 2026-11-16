"""Retain six unchanged passed suites and run the corrected certificate suites."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(obj):
    value = obj.get('rejected', obj.get('controls'))
    if isinstance(value, dict):
        value = value.get('rejected')
    need(isinstance(value, list) and all(type(x) is str for x in value), 'control name types')
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads((HERE / 'RETAINED.json').read_bytes())
    old = Path(spec['original_compose'])
    need(sha(old / 'controls.py') == spec['original_controls_code_sha256'], 'retained controls code drift')
    module_spec = importlib.util.spec_from_file_location('retained_control_inventory', old / 'controls.py')
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    original = old / 'run/case/CONTROLS.json'
    need(sha(original) == spec['original_controls_receipt_sha256'], 'retained control receipt drift')
    prior = json.loads(original.read_bytes())
    need(prior['status'] == 'PASS_SOURCE_FREE_CONTROLS', 'original controls did not pass')
    runs = []
    seen = set()
    for row in prior['runs']:
        if row['module'] == 'certificates.py':
            continue
        key = (row['module'], row['optimized'])
        need(type(row['optimized']) is bool and key not in seen and row['exit_code'] == 0,
             'retained control identity')
        values = names(row['result'])
        need(len(values) == len(set(values)) == len(module.EXPECTED[row['module']]) and
             set(values) == module.EXPECTED[row['module']], 'retained control population')
        if row['module'] == 'exact.py':
            need(row['result']['positive'] == ['dirty_init_zero', 'clean_copy_assignment', 'clear',
                                              'changed_public_operator'], 'retained positive controls')
        seen.add(key)
        runs.append(dict(row, retained=True, original_receipt_sha256=sha(original)))
    need(seen == {(name, mode) for name in ('build.py', 'exact.py', 'proof.py') for mode in (False, True)},
         'retained suite population')
    expected = module.EXPECTED['certificates.py'] | {'other_live_include_zero',
               'other_live_omit_nonzero', 'zero_provider'}
    need(len(expected) == 24, 'corrected certificate control denominator')
    for optimize in (False, True):
        argv = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + str(args.out.parent / ('cert-control-cache-' + str(optimize)))]
        if optimize:
            argv.append('-O')
        argv += [str(HERE / 'certificates.py'), '--controls-only']
        done = subprocess.run(argv, capture_output=True, text=True, timeout=20, check=False)
        need(done.returncode == 0 and not done.stderr, 'corrected certificate control process')
        obj = json.loads(done.stdout)
        values = names(obj)
        need(obj['status'] == 'PASS_CONTROLS_ONLY' and len(values) == len(set(values)) == 24 and
             set(values) == expected, 'corrected certificate controls incomplete')
        need(obj['controls']['public_rank_counterexample'] ==
             'accepted remaining-live rank 2, public rank 1 at cut; final rank 2', 'rank positive witness')
        runs.append({'module': 'certificates.py', 'optimized': optimize, 'retained': False,
                     'exit_code': 0, 'argv': argv, 'control_count': len(values), 'result': obj,
                     'code_sha256': sha(HERE / 'certificates.py')})
    need(len(runs) == 8, 'current control suite count')
    report = {'status': 'PASS_SOURCE_FREE_CONTROLS', 'runs': runs,
              'scope': 'Six unchanged passed source-free suites retained; corrected certificate suite freshly run normally and optimized. Original failed certificate attempt preserved.'}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'runs': len(runs)}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
