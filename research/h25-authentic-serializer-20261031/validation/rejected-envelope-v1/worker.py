"""Single fixed-operation coordinator inside inclusive observer; no target imports."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from custody import check_snapshot, need, pin, read_json, safe, same, stage, write_json


def subst(value, bindings):
    for key, replacement in bindings.items():
        value = value.replace('{' + key + '}', replacement)
    need('{' not in value and '}' not in value, 'unresolved command binding')
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--admission', required=True)
    parser.add_argument('--admission-sha256', required=True)
    args = parser.parse_args()
    admission = read_json(Path(args.admission), args.admission_sha256)
    operation = admission['operation']
    root = safe(Path(admission['operation_root']))
    job = admission['job']
    need(job['id'] == operation, 'operation/job mismatch')
    state = {'schema': 'o03-worker-receipt-v1', 'operation': operation, 'status': 'STARTED', 'errors': []}
    package_custody, input_custody = None, None
    try:
        # Fresh separately owned copies are made under the already live outer observation.
        package_custody = stage(root / 'package', admission['package_sources'])
        state['package_before'] = package_custody
        runtime = read_json(Path(admission['runtime_manifest']), admission['runtime_sha256'])
        for filename, expected in runtime['files'].items():
            same(Path(filename), expected)
        from bootstrap import closure
        from effective import capture, unchanged
        import importlib
        for name in runtime['preload_modules']:
            importlib.import_module(name)
        state['worker_runtime_before'], worker_objects = closure(runtime, Path(__file__).resolve().parent.parent,
            Path(__file__).resolve(), main_path=Path(__file__).resolve())
        effective_before = capture(dict(sys.modules))
        state['effective_before'] = effective_before
        bindings = {'package': str(root / 'package'), 'operation_root': str(root),
                    'output_root': str(root / 'outputs'), 'receipt': str(root / 'target-receipt.json'),
                    'runtime_manifest': admission['runtime_manifest'], 'runtime_sha256': admission['runtime_sha256']}
        if job['needs_authentic_inputs']:
            input_custody = stage(root / 'inputs', admission['input_sources'])
            # Loader schema exact: no wrapper/metadata extra file enters the input root.
            write_json(root / 'input-custody.json', input_custody)
            state['input_before'] = input_custody
            bindings.update(input_root=str(root / 'inputs'), custody_json=str(root / 'input-custody.json'))
        for key, spec in admission.get('dependency_receipts', {}).items():
            path = safe(Path(spec['path']))
            same(path, spec['pin'])
            bindings[key] = str(path)
        for key, directory in admission.get('dependency_output_roots', {}).items():
            bindings[key] = str(safe(Path(directory)))
        argv = [subst(value, bindings) for value in job['argv']]
        request = {'package_custody': package_custody, 'entry': job['entry'], 'argv': argv,
                   'runtime_manifest': admission['runtime_manifest'], 'runtime_sha256': admission['runtime_sha256'],
                   'runtime_report': str(root / 'effective-runtime.json')}
        write_json(root / 'bootstrap-request.json', request)
        request_sha = pin(root / 'bootstrap-request.json')['sha256']
        bootstrap = root / 'package/envelope/bootstrap.py'
        need('envelope/bootstrap.py' in package_custody['files'], 'bootstrap absent')
        command = [admission['interpreter'], '-B', '-I', '-S']
        if job['optimization'] == 1:
            command.append('-O')
        else:
            need(job['optimization'] == 0, 'invalid optimization')
        command += [str(bootstrap), str(root / 'bootstrap-request.json'), request_sha]
        state['command'] = command
        # The outer observer owns the only real180s/1GiB/aggregate guard and logs.
        completed = subprocess.run(command, cwd=root, stdin=subprocess.DEVNULL, check=False)
        state['target_exit'] = completed.returncode
        need(completed.returncode == 0, 'bootstrap/target failed')
        effective = read_json(root / 'effective-runtime.json')
        need(effective['status'] == 'PASS', 'runtime before/after failed')
        receipt = read_json(root / 'target-receipt.json')
        for key, expected in job['receipt_predicates'].items():
            need(receipt.get(key) == expected, 'target receipt predicate failed: ' + key)
        state['target_receipt'] = pin(root / 'target-receipt.json')
        # Receipt and runtime closure readbacks, source checks and genuine-input cleanup
        # checks remain substantive measured work before worker exits.
        state['runtime_report'] = pin(root / 'effective-runtime.json')
        for filename, expected in runtime['files'].items():
            same(Path(filename), expected)
        state['worker_runtime_after'], after_objects = closure(runtime, Path(__file__).resolve().parent.parent,
            Path(__file__).resolve(), main_path=Path(__file__).resolve())
        need(all(after_objects[k] is v for k, v in worker_objects.items()), 'worker callable drift')
        state['effective_after'] = capture(dict(sys.modules))
        unchanged(effective_before, state['effective_after'])
        for key, spec in admission.get('dependency_receipts', {}).items():
            same(Path(spec['path']), spec['pin'])
        for relative in job['must_be_absent_after']:
            path = root / relative
            need(not path.exists() and not path.is_symlink(), 'cleanup failed: ' + relative)
    except BaseException as error:
        state['errors'].append({'type': type(error).__name__, 'message': str(error)})
    finally:
        for name, custody in (('package_after', package_custody), ('input_after', input_custody)):
            if custody is not None:
                try:
                    state[name] = check_snapshot(custody)
                except BaseException as error:
                    state['errors'].append({'check': name, 'type': type(error).__name__, 'message': str(error)})
        state['retention'] = 'immutable staged inputs/sources and complete first-attempt evidence intentionally retained; candidate private staging absence checked by target validator; no silently deleted failures'
        state['status'] = 'PASS' if not state['errors'] else 'STOP'
        write_json(root / 'worker-receipt.json', state)
    if state['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
