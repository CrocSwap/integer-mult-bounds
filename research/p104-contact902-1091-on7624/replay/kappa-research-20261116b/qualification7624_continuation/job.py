"""Resume only the unfinished stages in a separate output; no automatic retry."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'qualification7624'
OLD_FREEZE_SHA = '0ef4032f4c1124de335bad3c1ef94b8a14a7926ec84fa608b0686c0ec8ee13aa'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def check_old(plan):
    freeze = OLD / 'FREEZE.json'
    need(sha(freeze) == OLD_FREEZE_SHA, 'original freeze receipt changed')
    for row in read(freeze)['files']:
        p = Path(row['path'])
        need(p.is_file() and not p.is_symlink() and sha(p) == row['sha256'], 'original frozen file changed: ' + str(p))
    base = OLD / 'run'
    need(base.is_dir() and not base.is_symlink(), 'original run directory missing or symlink')
    actual = {}
    for p in sorted(base.rglob('*')):
        need(not p.is_symlink(), 'symlink in original run: ' + str(p))
        rel = p.relative_to(base).as_posix()
        if p.is_file():
            actual[rel] = sha(p)
        else:
            need(p.is_dir(), 'special file in original run: ' + str(p))
            actual[rel] = None
    need(actual == plan['predecessor_run_snapshot'], 'original run or seed changed')
    control = OLD / 'control'
    need(control.is_dir() and not control.is_symlink(), 'original control directory missing or symlink')
    controls = {}
    for p in sorted(control.rglob('*')):
        need(not p.is_symlink(), 'symlink in original control: ' + str(p))
        rel = p.relative_to(control).as_posix()
        if p.is_file():
            controls[rel] = sha(p)
        else:
            need(p.is_dir(), 'special file in original control: ' + str(p))
            controls[rel] = None
    need(controls == plan['predecessor_control_snapshot'], 'original control tree changed')
    need(not (control / 'RESULT.json').exists(), 'unexpected predecessor controller result')
    recovery = HERE.parent / 'recovery7624'
    inventory = read(recovery / 'INTERRUPTED-RUN-INVENTORY.json')
    entries = inventory['files']
    listed = {row['path']: (row['sha256'], row['bytes']) for row in entries}
    need(len(entries) == len(listed) == inventory['file_count'] == 77, 'interrupted inventory cardinality')
    expected = {('run/' + k): (v, (base / k).stat().st_size) for k, v in actual.items() if v is not None}
    expected.update({('control/' + k): (v, (control / k).stat().st_size) for k, v in controls.items() if v is not None})
    need(listed == expected, 'interrupted inventory disagrees with predecessor trees')
    seed = read(recovery / 'PREPARED-SEED.json')
    seed_rows = seed['files']
    seed_listed = {row['path']: (row['sha256'], row['bytes']) for row in seed_rows}
    seed_expected = {k[len('case/work/'):]: (v, (base / k).stat().st_size)
                     for k, v in actual.items() if k.startswith('case/work/') and v is not None}
    need(len(seed_rows) == len(seed_listed) == 58 and seed_listed == seed_expected, 'prepared seed manifest mismatch')
    need(seed['status'] == 'PREPARED_ONLY_NATIVE_SIGNED_UNEXECUTED' and
         seed['run_id'] == read(base / 'case/work/QUALIFICATION-ID.json')['run_id'], 'seed identity mismatch')
    partial = read(base / 'case/PARTIAL.json')
    rows = partial['stages']
    need(partial['status'] == 'INCOMPLETE' and partial['conditional_application_qualified'] is False and
         [(r['name'], r['exit_code'], r['stage_cap_seconds']) for r in rows] ==
         [('prepare', 0, 60), ('certificates', 0, 180)], 'unexpected completed predecessor stages')
    work = base / 'case/work'
    for rel in ('native.receipt.json', 'signed.receipt.json',
                'producer54/validation_native/NATIVE-RESULT.json', 'producer54/validation_signed/RESULT.json',
                'native.stdout', 'native.stderr', 'signed.stdout', 'signed.stderr'):
        need(not (work / rel).exists(), 'actual stage evidence already exists: ' + rel)
    need(not (base / 'case/certificate-verifier/status.json').exists(), 'certificate verifier already completed')
    prepared = read(work / 'PREPARED.json')
    need(prepared['status'] == 'PREPARED_NOT_EXECUTED' and
         prepared['ledger_sha256'] == sha(work / 'CONTACT7624-ADAPTERS.json'), 'prepared ledger changed')
    cert = read(base / 'case/certificates/status.json')
    need(cert['status'] == 'PREPARED_CERTIFICATES_NOT_REPLAYED_IN_FULL_JOB', 'certificate custody missing')
    for name, pin in cert['hashes'].items():
        need(Path(name).name == name and sha(base / 'case/certificates' / name) == pin, 'certificate custody changed')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    root = a.root.resolve()
    need(root == HERE.parent.resolve(), 'wrong round root')
    out = a.out.resolve()
    need(out == HERE / 'run/case', 'continuation requires fixed case path')
    out.mkdir()
    work = out / 'work'
    gate = root / 'compose7624_completion/run/case'
    plan = read(HERE / 'PLAN.json')
    start = time.monotonic()
    deadline = start + 3290
    rows = []
    report = {'status': 'INCOMPLETE', 'stages': rows, 'conditional_application_qualified': False,
              'supplier_U_implemented': False, 'retained_predecessor_stages': ['prepare', 'certificates'],
              'predecessor_partial_sha256': plan['predecessor_run_snapshot']['case/PARTIAL.json'],
              'scope': 'new execution of remaining stages using retained prepared seed'}
    try:
        need(__debug__ and sys.version_info[:2] == (3, 12), 'normal Python3.12 required')
        check_old(plan)
        shutil.copytree(OLD / 'run/case/work', work)
        shutil.copytree(OLD / 'run/case/certificates', out / 'certificates')
        # Copy verification prevents a changed or partial seed from being adopted.
        for rel, pin in plan['predecessor_run_snapshot'].items():
            for prefix, dest in (('case/work/', work), ('case/certificates/', out / 'certificates')):
                if rel.startswith(prefix):
                    target = dest / rel[len(prefix):]
                    need((target.is_dir() if pin is None else target.is_file() and sha(target) == pin),
                         'copied seed differs: ' + rel)
        check_old(plan)
        app = [str(OLD / 'application.py'), '--root', str(root), '--work', str(work)]
        stages = [
            ('certificate-verifier', 180, [str(OLD / 'certificate_verifier.py'), '--root', str(root), '--gate', str(gate), '--prepared', str(OLD / 'run/case/certificates'), '--out', str(out / 'certificate-verifier')]),
            ('native', 1800, [*app, '--stage', 'native']),
            ('signed', 900, [*app, '--stage', 'signed']),
            ('resources', 20, [str(OLD / 'resources.py'), '--root', str(root), '--work', str(work), '--out', str(out / 'resources')])]
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
             set(signed['stale_native_receipt_bindings_rejected']) == {'run_id', 'native_result_sha256', 'adapter_sha256', 'launcher_sha256'}, 'freshness controls incomplete')
        consumer = signed['native_inventory_consumer_controls']
        need(set(consumer) == {'missing_pair', 'substituted_pair', 'duplicate_pair', 'empty_pairs', 'boolean_pair', 'malformed_row'} and
             all(value is True for value in consumer.values()), 'native inventory consumer controls missing')
        check_old(plan)
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
