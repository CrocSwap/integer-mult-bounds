"""Prepared stage-only completion; requires fresh user authorization to launch."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
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


def retain(out):
    record = read(HERE / 'RETAINED.json')
    old = Path(record['original_compose'])
    freeze = old / 'FREEZE.json'
    need(sha(freeze) == record['first_freeze_sha256'], 'original freeze identity')
    for row in read(freeze)['files']:
        path = Path(row['path'])
        need(path.is_file() and not path.is_symlink() and sha(path) == row['sha256'], 'original frozen source changed')
    for row in record['evidence']:
        path = Path(row['path'])
        need(path.is_file() and not path.is_symlink() and sha(path) == row['sha256'], 'retained evidence changed')
        if row.get('destination'):
            target = out / row['destination']
            need(target.resolve().is_relative_to(out.resolve()) and not target.exists(), 'retained output path')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            need(sha(target) == row['sha256'], 'retained copy mismatch')
    controller = read(old / 'control/RESULT.json')
    need(controller['differential_case_completed'] is False and controller['group_empty'] is True and
         controller['returncode'] == 1, 'original failed attempt not preserved/closed')
    result = read(old / 'run/case/RESULT.json')
    need(result['status'] == 'INCOMPLETE' and result['error'] == 'failed stage certificates', 'unexpected original failure')
    stages = result['stages']
    need([row['name'] for row in stages] == ['controls', 'built', 'exact', 'proof', 'certificates'] and
         all(row['exit_code'] == 0 for row in stages[:4]) and stages[-1]['exit_code'] != 0,
         'retained stage outcomes')
    need(read(old / 'run/case/certificates/status.json')['error'] == 'rank/metadata mismatch', 'different certificate failure')
    need(read(out / 'exact/status.json')['status'] == 'U_CONDITIONAL_LITERAL_EXACT_ONLY' and
         read(out / 'proof/status.json')['status'] == 'ZERO_NORMALIZED_STREAM_ONLY_UNQUALIFIED', 'retained proof not passed')
    write(out / 'RETAINED-PASSED.json', record)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir()
    start = time.monotonic()
    deadline = start + 580
    rows = []
    report = {'status': 'INCOMPLETE', 'stages': rows, 'qualified_kappa': False,
              'scope': 'Stage-only completion, retaining passed fixed-candidate controls/build/exact/zero proof and original metadata failure; no complete native/signed qualification.'}
    try:
        need(__debug__ and sys.version_info[:2] == (3, 12), 'normal Python3.12 required')
        record = retain(args.out)
        rows.append({'name': 'retain_passed', 'exit_code': 0, 'wall_seconds': time.monotonic() - start})
        stages = [('controls', 'controls.py', 30, []),
                  ('certificates', 'certificates.py', 210, ['--built', str(args.out / 'built')]),
                  ('physical', 'physical.py', 75, ['--built', str(args.out / 'built'), '--exact', str(args.out / 'exact')]),
                  ('price', 'price.py', 70, ['--built', str(args.out / 'built'), '--exact', str(args.out / 'exact')])]
        for name, script, cap, extra in stages:
            left = deadline - time.monotonic()
            need(left > 0, 'completion whole 580-second deadline')
            argv = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + str(args.out / 'stage-pycache' / name), str(HERE / script)]
            if name == 'controls':
                argv += ['--out', str(args.out / 'CONTROLS.json')]
            else:
                argv += ['--root', str(args.root), '--out', str(args.out / name), *extra]
            begin = time.monotonic()
            with (args.out / (name + '.stdout')).open('x') as stdout, (args.out / (name + '.stderr')).open('x') as stderr:
                done = subprocess.run(argv, stdout=stdout, stderr=stderr, check=False,
                                      timeout=min(cap, left), env=dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'))
            rows.append({'name': name, 'argv': argv, 'exit_code': done.returncode,
                         'wall_seconds': time.monotonic() - begin, 'stage_cap_seconds': cap})
            write(args.out / 'PARTIAL.json', report)
            need(done.returncode == 0, 'failed completion stage ' + name)
        original_job = Path(record['original_compose']) / 'job.py'
        need(sha(original_job) == record['original_job_sha256'], 'original binding implementation drift')
        spec = importlib.util.spec_from_file_location('retained_receipt_binding', original_job)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        report['receipt_hashes'] = mod.bindings(args.out)
        report['receipt_hashes']['RETAINED-PASSED.json'] = sha(args.out / 'RETAINED-PASSED.json')
        need(time.monotonic() < deadline, 'completion deadline after binding')
        report.update(status='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U',
                      original_failed_controller_sha256=record['original_failed_controller_sha256'],
                      corrected_certificate_code_sha256=sha(HERE / 'certificates.py'))
    except BaseException as error:
        report.update(error_type=type(error).__name__, error=str(error))
    report['wall_seconds'] = time.monotonic() - start
    write(args.out / 'RESULT.json', report)
    print(json.dumps({'status': report['status'], 'wall_seconds': report['wall_seconds']}, sort_keys=True), flush=True)
    return 0 if report['status'] == 'PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U' else 1


if __name__ == '__main__':
    raise SystemExit(main())
