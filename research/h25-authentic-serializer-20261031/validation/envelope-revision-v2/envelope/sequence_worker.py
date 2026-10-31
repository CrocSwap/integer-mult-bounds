"""Fixed eight-operation serial coordinator inside one inclusive180s command.

One outer observer receipt and one parent readback close this finite operation.
No intermediate parent process/action, retries, rerolls or fresh admission from
candidate observations. Every child is reaped before the next child starts.
"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from custody import need, pin, read_json, write_json

ORDER = ('observer-controls', 'loader-controls-normal', 'consumer-controls-normal',
         'loader-controls-O', 'consumer-controls-O', 'baseline-first', 'candidate-first', 'independent-validation')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--admission', required=True)
    parser.add_argument('--admission-sha256', required=True)
    args = parser.parse_args()
    admission = read_json(Path(args.admission), args.admission_sha256)
    need(admission['operation'] == 'complete-fixed-o03', 'fixed operation required')
    need(tuple(job['id'] for job in admission['sequence']) == ORDER, 'fixed serial order differs')
    root = Path(admission['operation_root'])
    steps = root / 'steps'
    steps.mkdir(mode=0o700)
    state = {'schema': 'o03-fixed-sequence-v1', 'status': 'STARTED', 'ordered_operations': list(ORDER), 'steps': [], 'errors': []}
    try:
        from custody import same
        from bootstrap import closure
        from effective import capture, unchanged
        import importlib
        runtime = read_json(Path(admission['runtime_manifest']), admission['runtime_sha256'])
        for filename, expected in runtime['files'].items():
            same(Path(filename), expected)
        for name in runtime['preload_modules']:
            importlib.import_module(name)
        state['runtime_before'], objects = closure(runtime, Path(__file__).resolve().parent.parent,
            Path(__file__).resolve(), main_path=Path(__file__).resolve())
        effective_before = capture(dict(sys.modules))
        for job in admission['sequence']:
            step_root = steps / job['id']
            step_root.mkdir(mode=0o700)
            child = dict(admission, operation=job['id'], operation_root=str(step_root), job=job)
            child.pop('sequence')
            child['dependency_receipts'] = {}
            child['dependency_output_roots'] = {}
            if job['id'] == 'independent-validation':
                for arm, label in (('baseline', 'baseline-first'), ('candidate', 'candidate-first')):
                    prior_root = steps / label
                    child['dependency_receipts'][arm + '_receipt'] = {
                        'path': str(prior_root / 'target-receipt.json'), 'pin': pin(prior_root / 'target-receipt.json')}
                    child['dependency_output_roots'][arm + '_root'] = str(prior_root / 'outputs')
            path = root / (job['id'] + '-request.json')
            write_json(path, child)
            sha = pin(path)['sha256']
            command = [admission['interpreter'], '-B', '-I', '-S', str(Path(__file__).resolve().with_name('worker.py')),
                       '--admission', str(path), '--admission-sha256', sha]
            completed = subprocess.run(command, cwd=root, stdin=subprocess.DEVNULL, check=False)
            row = {'id': job['id'], 'exit': completed.returncode, 'request': pin(path)}
            state['steps'].append(row)
            need(completed.returncode == 0, 'fixed operation failed: ' + job['id'])
            receipt = read_json(step_root / 'worker-receipt.json')
            need(receipt['status'] == 'PASS', 'worker receipt failed')
            row['worker_receipt'] = pin(step_root / 'worker-receipt.json')
        # Full independent validator already performed byte/receipt/cleanup checks;
        # all step receipts are reread here inside observation, never outside tail.
        for row in state['steps']:
            expected = row['worker_receipt']
            need(pin(steps / row['id'] / 'worker-receipt.json') == expected, 'step receipt drift')
        state['runtime_after'], actual = closure(runtime, Path(__file__).resolve().parent.parent,
            Path(__file__).resolve(), main_path=Path(__file__).resolve())
        need(all(actual[k] is v for k, v in objects.items()), 'sequence callable drift')
        unchanged(effective_before, capture(dict(sys.modules)))
    except BaseException as error:
        state['errors'].append({'type': type(error).__name__, 'message': str(error)})
    state['status'] = 'PASS' if not state['errors'] else 'STOP'
    write_json(root / 'worker-receipt.json', state)
    if state['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
