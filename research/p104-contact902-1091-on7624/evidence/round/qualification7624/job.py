"""One fresh complete qualification after the completed fixed-candidate gate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir()
    root, out = a.root.resolve(), a.out.resolve()
    work = out / 'work'
    gate = root / 'compose7624_completion/run/case'
    start = time.monotonic()
    deadline = start + 3290
    rows = []
    report = {'status': 'INCOMPLETE', 'stages': rows, 'conditional_application_qualified': False,
              'supplier_U_implemented': False}
    app = [str(HERE / 'application.py'), '--root', str(root), '--work', str(work)]
    stages = [('prepare', 60, [*app, '--stage', 'prepare']),
              ('certificates', 180, [str(HERE / 'certificates.py'), '--root', str(root), '--gate', str(gate), '--out', str(out / 'certificates')]),
              ('certificate-verifier', 180, [str(HERE / 'certificate_verifier.py'), '--root', str(root), '--gate', str(gate), '--prepared', str(out / 'certificates'), '--out', str(out / 'certificate-verifier')]),
              ('native', 1800, [*app, '--stage', 'native']),
              ('signed', 900, [*app, '--stage', 'signed']),
              ('resources', 20, [str(HERE / 'resources.py'), '--root', str(root), '--work', str(work), '--out', str(out / 'resources')])]
    try:
        need(__debug__ and sys.version_info[:2] == (3, 12), 'normal Python3.12 required')
        for name, cap, tail in stages:
            left = deadline - time.monotonic()
            need(left > 0, 'whole qualification deadline')
            argv = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + str(out / 'stage-pycache' / name), *tail]
            env = {key: value for key, value in os.environ.items() if not key.startswith('PYTHON')}
            env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
            begin = time.monotonic()
            with (out / (name + '.stdout')).open('x') as stdout, (out / (name + '.stderr')).open('x') as stderr:
                done = subprocess.run(argv, stdout=stdout, stderr=stderr, timeout=min(cap, left), check=False, env=env)
            rows.append({'name': name, 'argv': argv, 'exit_code': done.returncode,
                         'wall_seconds': time.monotonic() - begin, 'stage_cap_seconds': cap})
            write(out / 'PARTIAL.json', report)
            print(json.dumps(rows[-1], sort_keys=True), flush=True)
            need(done.returncode == 0, 'failed stage ' + name)
        resource = read(out / 'resources/RESOURCE-COMPARISON.json')
        need(resource['status'] == 'PASS_CONDITIONAL_COMMON_U_APPLICATION', 'resource conjunction missing')
        need(read(out / 'certificate-verifier/status.json')['status'] == 'PASS_FRESH_204_CERTIFICATE_REPLAY', 'certificate replay missing')
        signed = read(work / 'signed.receipt.json')
        need(signed['stale_native_results_rejected'] >= 3 and
             set(signed['stale_native_receipt_bindings_rejected']) == {'run_id', 'native_result_sha256', 'adapter_sha256', 'launcher_sha256'},
             'freshness controls incomplete')
        consumer = signed['native_inventory_consumer_controls']
        need(set(consumer) == {'missing_pair', 'substituted_pair', 'duplicate_pair', 'empty_pairs',
                               'boolean_pair', 'malformed_row'} and
             all(value is True for value in consumer.values()), 'native inventory consumer controls missing')
        need(time.monotonic() < deadline, 'whole qualification deadline after final binding')
        report.update(status='PASS_QUALIFIED_CONDITIONAL_COMMON_U_KAPPA', conditional_application_qualified=True,
                      claim=resource['claim'], claim_decimal=resource['claim_decimal'],
                      resource_comparison_sha256=sha(out / 'resources/RESOURCE-COMPARISON.json'),
                      native_receipt_sha256=sha(work / 'native.receipt.json'), signed_receipt_sha256=sha(work / 'signed.receipt.json'),
                      certificate_verifier_sha256=sha(out / 'certificate-verifier/status.json'),
                      same_original_premise_dominance_established=False, selected_frontier_changed=False)
    except BaseException as error:
        report.update(error_type=type(error).__name__, error=str(error))
    report['wall_seconds'] = time.monotonic() - start
    write(out / 'RESULT.json', report)
    print(json.dumps({'status': report['status'], 'wall_seconds': report['wall_seconds']}, sort_keys=True), flush=True)
    return 0 if report['status'] == 'PASS_QUALIFIED_CONDITIONAL_COMMON_U_KAPPA' else 1


if __name__ == '__main__':
    raise SystemExit(main())
