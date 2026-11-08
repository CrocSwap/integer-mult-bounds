"""Same-process subreaper wrapper around byte-unchanged reviewed queue v4.

The actual consumer is this wrapper plus its explicitly narrow subprocess alias
proxy and supervisor. The queue's calling environment is deliberately extended;
its original bytes and real root status/stdout/stderr remain independently pinned.
"""
import argparse
import hashlib
import importlib.util as _importlib_util
import json
from pathlib import Path
import subprocess
import sys
import time

def source_packet(expected):
    here = Path(__file__).resolve().parent
    manifest_path = here / 'SOURCE-READINESS.json'
    if manifest_path.is_symlink() or manifest_path.stat().st_mode & 0o222:
        raise RuntimeError('Concrete source manifest must be readonly')
    with manifest_path.open('rb') as stream:
        raw = stream.read(262145)
    if len(raw) > 262144 or hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError('Parent-reviewed source manifest differs')
    manifest = json.loads(raw)
    blobs = {}
    for name, row in manifest['files'].items():
        if Path(name).name != name or name == 'SOURCE-READINESS.json':
            raise RuntimeError('Unsafe source packet member')
        path = here / name
        if path.is_symlink() or path.stat().st_mode & 0o222:
            raise RuntimeError('Parent must freeze the concrete source packet readonly')
        with path.open('rb') as stream:
            data = stream.read(262145)
        if len(data) > 262144 or len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise RuntimeError('Source packet member differs: ' + name)
        blobs[name] = data
    if blobs[Path(__file__).name] != Path(__file__).read_bytes():
        raise RuntimeError('Actual queue entry differs from frozen source packet')
    path = here / 'supervisor.py'
    spec = _importlib_util.spec_from_file_location('h25_parent_supervisor', path)
    module = _importlib_util.module_from_spec(spec)
    exec(compile(blobs['supervisor.py'], str(path), 'exec'), module.__dict__)
    return module, manifest



class RootProxy:
    def __init__(self, supervisor, root, cases, evidence, policy, deadline):
        self.s, self.root, self.cases = supervisor, root, cases
        self.evidence, self.policy, self.deadline = evidence, policy, deadline
        self.next = 0
        self.records = []

    def run(self, command, **kwargs):
        s = self.s
        s.need(self.next < len(self.cases), 'Unregistered extra queue root command')
        case = self.cases[self.next]
        expected = ['/usr/bin/python3.12', *s.FLAGS, str(self.root / 'run_guarded_v3.py'),
                    case['stage'], case['job'], case['label']]
        s.need(command == expected and set(kwargs) == {'cwd', 'env', 'capture_output', 'timeout'} and
               kwargs['cwd'] == self.root and kwargs['env'] == s.ENV and
               kwargs['capture_output'] is True and kwargs['timeout'] == 190,
               'Queue subprocess alias call exceeded its exact reviewed interface')
        folder = self.evidence / case['label']
        result = s.run_root(self.root, case, folder, self.policy['root_seconds'], self.deadline,
                            self.policy['root_address_space_bytes'], self.policy['root_rss_sum_bytes'])
        original_rc = result['returncode']
        receipt_path = self.root / 'runtime/runs' / case['label'] / 'receipt.json'
        if receipt_path.exists():
            root_receipt, root_pin = s.read_json(receipt_path, 4 * 1024 * 1024)
        else:
            root_receipt, root_pin = {'status': 'ABSENT_UNCLOSED_ROOT'}, None
        failure = result['failure']
        if original_rc == 0 and (result['cleanup']['observed_after_root_exit'] or
                                 result['cleanup']['reaped_adopted']):
            failure = failure or {'type': 'OrphanAfterApparentPass',
                                  'message': 'Original root exit 0 retained; supervisor admission STOP'}
        if not result['cleanup']['complete']:
            failure = failure or {'type': 'CleanupIncomplete', 'message': 'Owned process groups not empty'}
        originals = {'root_returncode': original_rc, 'root_status': root_receipt['status'],
                     'root_receipt_pin': root_pin, 'root_stdout': result['outer_logs']['root.stdout.raw'],
                     'root_stderr': result['outer_logs']['root.stderr.raw']}
        row = {'label': case['label'], 'actual_consumer': 'wrapper+module-alias-proxy+supervisor+queue-v4',
               'original': originals, 'effective_admission': 'STOP' if failure else 'DEFER_TO_QUEUE_V4',
               'supervision_failure': failure, 'original_root_receipt_unchanged': True,
               'cleanup_before_queue_validation': True}
        s.write_new(folder / 'PROXY.json', row)
        self.records.append(row)
        if failure:
            s.stop_supplement(self.root, case['label'], failure)
            raise RuntimeError('Root supervision rejected case; original status retained: ' + case['label'])
        stdout_record, stdout = s.stable_file(folder / 'root.stdout.raw', s.LOG_CAP, True)
        stderr_record, stderr = s.stable_file(folder / 'root.stderr.raw', s.LOG_CAP, True)
        s.need(stdout_record == originals['root_stdout'] and stderr_record == originals['root_stderr'],
               'Original root command streams changed before queue consumption')
        self.next += 1
        return subprocess.CompletedProcess(command, original_rc, stdout, stderr)


def main():
    began = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    s, source_manifest = source_packet(args.source_sha256)
    s.launch_contract()
    root = args.root.resolve()
    config_path, policy_path = args.config.resolve(), args.policy.resolve()
    s.need(config_path.is_relative_to(root / 'control') and policy_path.is_relative_to(root / 'control'),
           'Config and policy must be frozen round controls')
    config, config_pin = s.read_json(config_path)
    policy, policy_pin = s.read_json(policy_path)
    s.need(set(policy) == {'queue', 'shared_seconds', 'root_seconds', 'root_address_space_bytes', 'root_rss_sum_bytes'},
           'Exact supervisor policy shape required')
    name = config['queue']
    s.need(type(name) is str and name.isalnum() and policy['queue'] == name, 'Queue policy identity differs')
    s.need(type(policy['shared_seconds']) in (int, float) and 0 < policy['shared_seconds'] <= 600 and
           type(policy['root_seconds']) in (int, float) and 0 < policy['root_seconds'] <= 190 and
           type(policy['root_address_space_bytes']) is int and 0 < policy['root_address_space_bytes'] <= 1024 ** 3 and
           type(policy['root_rss_sum_bytes']) is int and 0 < policy['root_rss_sum_bytes'] <= 1024 ** 3,
           'Unadmitted generic supervisor limits')
    evidence = root / 'validation/attempts' / (name + '-supervision')
    evidence.mkdir()
    lock = s.parent_lock(root)
    cap, initial = s.budget(root)
    deadline = min(began + policy['shared_seconds'], began + cap - sum(initial.values()))
    failure, proxy, keeper = None, None, None
    old_argv = sys.argv
    try:
        subreaper, keeper = s.install_subreaper(root)
        s.write_new(evidence / 'PARENT-SUBREAPER.json', subreaper)
        path = root / 'integration/run_reviewed_queue_v4.py'
        queue_pin, raw = s.stable_file(path, s.META_CAP, True)
        s.need(queue_pin['sha256'] == s.QUEUE_SHA, 'Original reviewed queue-v4 bytes changed')
        spec = _importlib_util.spec_from_file_location('h25_original_queue_v4', path)
        queue = _importlib_util.module_from_spec(spec)
        exec(compile(raw, str(path), 'exec'), queue.__dict__)
        s.need(queue.ROOT == root and queue.subprocess is subprocess, 'Unexpected queue module binding')
        proxy = RootProxy(s, root, config['cases'], evidence, policy, deadline)
        # Only this authenticated module's alias changes. The stdlib module is intact.
        queue.subprocess = proxy
        sys.argv = [str(path), str(config_path)]
        queue.main()
        s.need(proxy.next == len(config['cases']), 'Queue omitted a registered root call')
        s.need(not s.children_now(), 'Wrapper finished with children still present')
        s.need(s.stable_file(config_path, s.META_CAP)['sha256'] == config_pin['sha256'] and
               s.stable_file(policy_path, s.META_CAP)['sha256'] == policy_pin['sha256'], 'Control policy changed')
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)[:2048]}
        raise
    finally:
        sys.argv = old_argv
        try:
            s.packet_unchanged(Path(__file__).resolve().parent, source_manifest)
        except BaseException as error:
            failure = failure or {'type': type(error).__name__, 'message': str(error)[:2048]}
        elapsed = time.monotonic() - began
        current = s.ledger(root, allow_unclosed=True)
        s.need(all(current.get(k) == v for k, v in initial.items()), 'Prior cost records changed')
        nested = sum(v for k, v in current.items() if k not in initial)
        residual = max(0.0, elapsed - nested)
        if time.monotonic() > deadline:
            failure = failure or {'type': 'SupervisorBudget', 'message': 'Full wrapper bound crossed; cleanup remains charged'}
        result = {'schema': 'h25-queue-v4-supervisor-envelope-v1', 'queue': name,
                  'status': 'STOP' if failure else 'SUPERVISED_QUEUE_V4_COMPLETE', 'failure': failure,
                  'actual_consumer': 'wrapper+module-alias-proxy+supervisor+queue-v4',
                  'original_queue_sha256': s.QUEUE_SHA, 'original_root_sha256': s.RUNNER_SHA,
                  'source_manifest_sha256': args.source_sha256, 'config_pin': config_pin, 'policy_pin': policy_pin,
                  'controls': [] if proxy is None else proxy.records,
                  'complete_wrapper_seconds_before_own_receipt': elapsed,
                  'nested_queue_and_root_seconds': nested, 'wrapper_residual_seconds': residual,
                  'outer_GNU_time_final_tail_reconciliation_required': True,
                  'subreaper_is_same_queue_process': True, 'original_root_receipts_preserved': True}
        folder = root / 'runtime/runs' / (name + '-supervisor-overhead')
        folder.mkdir()
        s.write_new(folder / 'START.json', {'kind': 'parent_cost_only'})
        s.write_new(folder / 'receipt.json', dict(result, label=folder.name, kind='parent_cost_only',
                    wall_seconds=residual, runner_wall_seconds=residual))
        s.write_new(evidence / 'WRAPPER.json', result)
        lock.close()
    if failure:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
