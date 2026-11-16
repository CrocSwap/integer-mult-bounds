"""Signed/resources completion using retained certificate and native evidence."""
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
OLD = HERE.parent / 'qualification7624_continuation'
ORIGINAL = HERE.parent / 'qualification7624'
AUDIT_SHA = 'ca23807a4b1d9675daf67903608a6d874e37b94c70109a45fa73732ee8123841'
NATIVE_RECEIPT = 'cafc2c05b287d9c4e732fbff0c57a438e6848faecb0c333f78377ce9ab74467e'
NATIVE_RESULT = '2cf79508c3dbffb56a1f0609710ccc921590dd4747850279edefe8f71238b682'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def snapshot(base):
    need(base.is_dir() and not base.is_symlink(), 'predecessor directory missing or symlink')
    result = {}
    for p in sorted(base.rglob('*')):
        need(not p.is_symlink(), 'predecessor symlink')
        if p.is_file():
            result[p.relative_to(base).as_posix()] = sha(p)
        else:
            need(p.is_dir(), 'predecessor special file')
            result[p.relative_to(base).as_posix()] = None
    return result


def check_predecessor(plan):
    need(sha(OLD / 'FREEZE.json') == plan['predecessor_freeze_sha256'] ==
         '4b8ff9e31be998b83515807ac3860d38476df2f1fedd7d6ee91c4b909555d272', 'predecessor freeze changed')
    initial = read(ORIGINAL / 'run/case/PARTIAL.json')
    need(initial['status'] == 'INCOMPLETE' and initial['conditional_application_qualified'] is False and
         [(x['name'], x['exit_code']) for x in initial['stages']] == [('prepare', 0), ('certificates', 0)],
         'original retained stages changed')
    for name in ('run', 'control'):
        need(snapshot(OLD / name) == plan['predecessor_snapshots'][name], 'predecessor tree changed: ' + name)
    partial = read(OLD / 'run/case/PARTIAL.json')
    need(partial['retained_predecessor_stages'] == ['prepare', 'certificates'] and
         partial['predecessor_partial_sha256'] == sha(ORIGINAL / 'run/case/PARTIAL.json'), 'original retained receipt binding')
    need(partial['status'] == 'INCOMPLETE' and partial['conditional_application_qualified'] is False and
         [(x['name'], x['exit_code']) for x in partial['stages']] ==
         [('certificate-verifier', 0), ('native', 0), ('signed', 1)], 'predecessor stages changed')
    ctrl = read(OLD / 'control/RESULT.json')
    need(ctrl['group_empty'] is True and ctrl['differential_case_completed'] is False, 'predecessor controller status')
    cert = read(OLD / 'run/case/certificate-verifier/status.json')
    need(cert['status'] == 'PASS_FRESH_204_CERTIFICATE_REPLAY', 'fresh certificate replay missing')
    work = OLD / 'run/case/work'
    need(sha(work / 'native.receipt.json') == NATIVE_RECEIPT and
         sha(work / 'producer54/validation_native/NATIVE-RESULT.json') == NATIVE_RESULT, 'native bindings changed')
    native = read(work / 'native.receipt.json')
    identity = read(work / 'QUALIFICATION-ID.json')
    ledger = read(work / 'CONTACT7624-ADAPTERS.json')
    need(native['stage'] == 'native' and native['exit'] == 0 and native['run_id'] == identity['run_id'] == ledger['run_id'] and
         native['native_result_sha256'] == NATIVE_RESULT and native['adapter_sha256'] == sha(work / 'CONTACT7624-ADAPTERS.json') and
         native['launcher_sha256'] == sha(ORIGINAL / 'application.py') == sha(work / 'CONTACT7624-LAUNCHER.py'), 'native receipt chain')
    for rel in ('signed.receipt.json', 'signed.stdout', 'signed.stderr', 'producer54/validation_signed/RESULT.json'):
        need(not (work / rel).exists(), 'signed work already exists: ' + rel)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    root, out = a.root.resolve(), a.out.resolve()
    need(root == HERE.parent and out == HERE / 'run/case', 'fixed round and output paths required')
    out.mkdir()
    start = time.monotonic()
    deadline = start + 1190
    rows = []
    report = {'status': 'INCOMPLETE', 'conditional_application_qualified': False, 'supplier_U_implemented': False,
              'retained_predecessor_stages': ['prepare', 'certificates', 'certificate-verifier', 'native'],
              'retained_failed_signed_attempt': True, 'stages': rows}
    try:
        need(__debug__ and sys.version_info[:2] == (3, 12), 'normal Python3.12 required')
        plan = read(HERE / 'PLAN.json')
        check_predecessor(plan)
        work = out / 'work'
        shutil.copytree(OLD / 'run/case/work', work)
        shutil.copytree(OLD / 'run/case/certificates', out / 'certificates')
        for name, destination in (('case/work', work), ('case/certificates', out / 'certificates')):
            prefix = name + '/'
            expected = {k[len(prefix):]: v for k, v in plan['predecessor_snapshots']['run'].items() if k.startswith(prefix)}
            need(snapshot(destination) == expected, 'copied seed differs: ' + name)
        check_predecessor(plan)
        spec = importlib.util.spec_from_file_location('audit_custody', HERE / 'audit_custody.py')
        audit = importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)
        package = root / 'inputs/pr7624/research/p104-w2-primal-dual-bypass'
        need(sha(HERE / 'PREDECESSOR-AUDIT.jsonl') == AUDIT_SHA and
             sha(package / audit.LOG) == AUDIT_SHA, 'predecessor audit bytes changed')
        custody = audit.archive(package, out / 'PREDECESSOR-AUDIT.jsonl', expected_sha=AUDIT_SHA)
        write(out / 'PREDECESSOR-AUDIT-CAPTURE.json', custody)
        stages = [('signed', 900, [str(ORIGINAL / 'application.py'), '--root', str(root), '--work', str(work), '--stage', 'signed']),
                  ('resources', 20, [str(ORIGINAL / 'resources.py'), '--root', str(root), '--work', str(work), '--out', str(out / 'resources')])]
        for name, cap, tail in stages:
            left = deadline - time.monotonic()
            need(left > 0, 'whole completion deadline')
            argv = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + str(out / 'stage-pycache' / name), *tail]
            env = {key: value for key, value in os.environ.items() if not key.startswith('PYTHON')}
            env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
            begin = time.monotonic()
            with (out / (name + '.stdout')).open('x') as stdout, (out / (name + '.stderr')).open('x') as stderr:
                done = subprocess.run(argv, stdout=stdout, stderr=stderr, timeout=min(cap, left), check=False, env=env)
            rows.append({'name': name, 'argv': argv, 'exit_code': done.returncode,
                         'wall_seconds': time.monotonic() - begin, 'stage_cap_seconds': cap})
            write(out / 'PARTIAL.json', report)
            need(done.returncode == 0, 'failed stage ' + name)
        resource = read(out / 'resources/RESOURCE-COMPARISON.json')
        need(resource['status'] == 'PASS_CONDITIONAL_COMMON_U_APPLICATION', 'resource conjunction missing')
        signed = read(work / 'signed.receipt.json')
        need(signed['stale_native_results_rejected'] >= 3 and
             set(signed['stale_native_receipt_bindings_rejected']) == {'run_id', 'native_result_sha256', 'adapter_sha256', 'launcher_sha256'}, 'freshness controls incomplete')
        consumer = signed['native_inventory_consumer_controls']
        need(set(consumer) == {'missing_pair', 'substituted_pair', 'duplicate_pair', 'empty_pairs', 'boolean_pair', 'malformed_row'} and
             all(value is True for value in consumer.values()), 'native inventory consumer controls missing')
        check_predecessor(plan)
        need(time.monotonic() < deadline, 'whole completion deadline after final binding')
        report.update(status='PASS_QUALIFIED_CONDITIONAL_COMMON_U_KAPPA', conditional_application_qualified=True,
                      claim=resource['claim'], claim_decimal=resource['claim_decimal'],
                      resource_comparison_sha256=sha(out / 'resources/RESOURCE-COMPARISON.json'),
                      native_receipt_sha256=sha(work / 'native.receipt.json'), signed_receipt_sha256=sha(work / 'signed.receipt.json'),
                      certificate_verifier_sha256=sha(OLD / 'run/case/certificate-verifier/status.json'),
                      same_original_premise_dominance_established=False, selected_frontier_changed=False,
                      controller_and_audit_completion_required=True)
    except BaseException as error:
        report.update(error_type=type(error).__name__, error=str(error))
    report['wall_seconds'] = time.monotonic() - start
    write(out / 'RESULT.json', report)
    print(json.dumps({'status': report['status'], 'wall_seconds': report['wall_seconds']}, sort_keys=True), flush=True)
    return 0 if report['status'] == 'PASS_QUALIFIED_CONDITIONAL_COMMON_U_KAPPA' else 1


if __name__ == '__main__':
    raise SystemExit(main())
