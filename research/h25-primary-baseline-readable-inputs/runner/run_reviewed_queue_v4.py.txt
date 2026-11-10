"""Parent-owned serial queue of frozen, independently admitted stages.

Each actual-runner receipt and retained log is independently checked before the
next case. Every enclosing cost beyond nested runner time is charged once as a
new ledger record. No scientific module is imported here. No automatic retry.
"""
import hashlib
import json
import os
import resource
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent

# This is a trusted parent launch contract, not Python self-authentication or -I.
# -P suppresses unsafe path insertion; -S/-s prevent site and user-site loading.
# Unlike -I, this preserves the explicitly whitelisted fixed hash seed.
LAUNCH_FLAGS = ('-S', '-s', '-P', '-B')
LAUNCH_ENV = {'PATH': '/usr/bin:/bin', 'PYTHONHASHSEED': '0',
              'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC',
              'PYTHONDONTWRITEBYTECODE': '1'}


def require_trusted_launch():
    if not (sys.flags.no_site == 1 and sys.flags.no_user_site == 1 and
            sys.flags.safe_path and sys.flags.dont_write_bytecode == 1 and
            sys.flags.ignore_environment == 0 and sys.flags.isolated == 0 and
            sys.flags.hash_randomization == 0):
        raise ValueError('Explicit no-site/safe-path parent launch required')
    if dict(os.environ) != LAUNCH_ENV:
        raise ValueError('Exact clean parent environment required')
    if sys.executable != '/usr/bin/python3.12':
        raise ValueError('Absolute admitted interpreter required')
    if tuple(sys.path) != ('/usr/lib/python312.zip', '/usr/lib/python3.12',
                           '/usr/lib/python3.12/lib-dynload'):
        raise ValueError('Unadmitted ordered initial Python search path')
    return {'contract': 'trusted-clean-nosite-safe-path-fixedseed-v1',
            'no_site': sys.flags.no_site, 'no_user_site': sys.flags.no_user_site,
            'safe_path': bool(sys.flags.safe_path),
            'ignore_environment': sys.flags.ignore_environment,
            'isolated': sys.flags.isolated, 'hash_seed_environment': '0',
            'hash_randomization': sys.flags.hash_randomization,
            'initial_sys_path': list(sys.path), 'environment': dict(os.environ),
            'trust_boundary': 'Authenticated parent launcher, OS, interpreter and system stdlib before this module; no Python self-authentication claim'}


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    count = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            h.update(block)
            count += len(block)
    return h.hexdigest(), count


def record_time(path):
    row = json.loads(path.read_bytes())
    return row.get('runner_wall_seconds', row['wall_seconds'])


def validate(case):
    stage = ROOT / 'stages' / case['stage']
    stage_hash, _ = digest(stage / 'STAGE.json')
    need(stage_hash == case['stage_sha256'], 'Reviewed stage changed')
    declared = json.loads((stage / 'STAGE.json').read_bytes())
    folder = ROOT / 'runtime/runs' / case['label']
    receipt = json.loads((folder / 'receipt.json').read_bytes())
    start = json.loads((folder / 'START.json').read_bytes())
    for key, value in start.items():
        need(receipt.get(key) == value, 'START differs from receipt: ' + key)
    need(receipt['stage_sha256'] == stage_hash, 'Receipt stage differs')
    need(receipt['runner_sha256'] == declared['runner_sha256'] == digest(ROOT / 'run_guarded_v3.py')[0], 'Runner identity differs')
    need(receipt['budget_phase_sha256'] == digest(ROOT / 'control/EXECUTION-PHASE.json')[0], 'Budget identity differs')
    need(receipt['parent_launch'] == require_trusted_launch(), 'Parent launch provenance differs')
    need(receipt['command'][:5] == ['/usr/bin/python3.12', *LAUNCH_FLAGS], 'Child launch flags differ')
    need(receipt['fractions_sha256'] == digest(Path('/usr/lib/python3.12/fractions.py'))[0], 'Actual Fraction source differs')
    need(receipt['label'] == case['label'] and receipt['job'] == case['job'], 'Receipt case differs')
    need(receipt['status'] == 'PASS' and receipt['exit'] == 0 and receipt['termination'] is None, 'Actual runner rejected case')
    need(receipt['source_bytes_and_modes_unchanged'] is True and receipt['retained_log_bytes_stable'] is True, 'Custody or logs changed')
    need(receipt['log_read_chunk_bytes'] == 65536, 'Bounded log reader differs')
    for stream in ('stdout', 'stderr'):
        observed, count = digest(folder / (stream + '.txt'))
        need(observed == receipt[stream + '_sha256'], 'Raw log digest differs')
        need(count == receipt[stream + '_bytes'] == receipt[stream + '_final_bytes'], 'Raw log byte count differs')
        need(count <= 2097152, 'Ordinary raw log cap exceeded')
    need(receipt['stderr_bytes'] == 0, 'Unexpected actual child stderr')
    need(receipt['runner_wall_seconds'] >= receipt['wall_seconds'] >= 0, 'Runner time scope differs')
    prior = [p for p in (ROOT / 'runtime/runs').glob('*/receipt.json') if p.parent != folder]
    need(abs(sum(record_time(p) for p in prior) - receipt['spent_before_seconds']) < 1e-7, 'Aggregate ledger differs')
    science_path = folder / 'science/receipt.json'
    need(science_path.stat().st_size <= 4 * 1024 * 1024, 'Scientific receipt cap exceeded')
    science = json.loads(science_path.read_bytes())
    need(science['status'] == case['science_status'], 'Scientific/control status differs')
    for key, expected in case.get('science_fields', {}).items():
        need(science.get(key) == expected, 'Scientific/control field differs: ' + key)
    return {'label': case['label'], 'job': case['job'], 'stage': case['stage'],
            'gate': 'PASS_RETAINED_RECEIPT', 'science_status': science['status'],
            'runner_wall_seconds': receipt['runner_wall_seconds'], 'child_wall_seconds': receipt['wall_seconds'],
            'cpu_seconds': receipt['usage']['user_seconds'] + receipt['usage']['system_seconds'],
            'runner_cpu_seconds_before_own_receipt': receipt['runner_user_seconds'] + receipt['runner_system_seconds'],
            'kernel_max_rss_kib': receipt['usage']['kernel_max_rss_kib'],
            'sampled_process_group_rss_bytes': receipt['sampled_process_group_rss_bytes']}


def main():
    require_trusted_launch()
    begin = time.monotonic()
    usage_start = (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN))
    initial = set((ROOT / 'runtime/runs').glob('*/receipt.json'))
    own_raw = Path(__file__).read_bytes()
    name = 'unadmitted' + str(time.time_ns())
    raw = None
    rows, failure = [], None
    try:
        need(len(sys.argv) == 2, 'Exactly one frozen queue config required')
        config_path = Path(sys.argv[1]).resolve()
        need(config_path.is_relative_to(ROOT / 'control'), 'Queue config must be new-round control source')
        raw = config_path.read_bytes()
        spec = json.loads(raw)
        proposed = spec['queue']
        need(type(proposed) is str and proposed.isalnum(), 'Simple unique queue identity required')
        evidence = ROOT / 'validation/attempts' / proposed
        need(not evidence.exists(), 'Queue already attempted; no automatic retry')
        need(not (ROOT / 'runtime/runs' / (proposed + '-parent-overhead')).exists(), 'Queue ledger already exists')
        name = proposed
        evidence.mkdir(parents=True)
        for case in spec['cases']:
            for key in ('stage', 'job', 'label'):
                need(type(case[key]) is str and case[key] and all(c.isalnum() or c in '-_' for c in case[key]), 'Unsafe queue case identity')
            need(not (ROOT / 'runtime/runs' / case['label']).exists(), 'Case already attempted')
            need(digest(ROOT / 'stages' / case['stage'] / 'STAGE.json')[0] == case['stage_sha256'], 'Admitted stage differs before queue')
        for case in spec['cases']:
            command = ['/usr/bin/python3.12', *LAUNCH_FLAGS, str(ROOT / 'run_guarded_v3.py'), case['stage'], case['job'], case['label']]
            case_begin = time.monotonic()
            case_usage = (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN))
            result = subprocess.run(command, cwd=ROOT, env=dict(LAUNCH_ENV), capture_output=True, timeout=190)
            (evidence / (case['label'] + '.stdout')).write_bytes(result.stdout)
            (evidence / (case['label'] + '.stderr')).write_bytes(result.stderr)
            need(result.returncode == 0 and not result.stderr, 'Unexpected runner exit: ' + case['label'])
            row = validate(case)
            case_end_usage = (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN))
            row['parent_command_wall_seconds_through_validation'] = time.monotonic() - case_begin
            row['parent_command_cpu_seconds_with_runner_children_validation'] = sum((b.ru_utime + b.ru_stime) - (a.ru_utime + a.ru_stime) for a, b in zip(case_usage, case_end_usage))
            rows.append(row)
            (evidence / (case['label'] + '.gate.json')).write_text(json.dumps(row, indent=2, sort_keys=True) + '\n')
            print(json.dumps(row, sort_keys=True), flush=True)
        need(config_path.read_bytes() == raw and Path(__file__).read_bytes() == own_raw, 'Queue config or consumer changed')
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        usage_end = (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN))
        elapsed = time.monotonic() - begin
        current = set((ROOT / 'runtime/runs').glob('*/receipt.json')) - initial
        nested = sum(record_time(p) for p in current)
        overhead = max(0.0, elapsed - nested)
        folder = ROOT / 'runtime/runs' / (name + '-parent-overhead')
        folder.mkdir(parents=True)
        result = {'status': 'STOP' if failure else 'PASS_REVIEWED_QUEUE', 'queue': name, 'controls': rows,
                  'failure': failure, 'nested_runner_seconds': nested, 'parent_overhead_seconds': overhead,
                  'complete_queue_seconds_before_own_receipt': elapsed,
                  'parent_self_cpu_seconds_before_own_receipt': (usage_end[0].ru_utime + usage_end[0].ru_stime) - (usage_start[0].ru_utime + usage_start[0].ru_stime),
                  'all_child_cpu_seconds_before_own_receipt': (usage_end[1].ru_utime + usage_end[1].ru_stime) - (usage_start[1].ru_utime + usage_start[1].ru_stime),
                  'complete_cpu_seconds_before_own_receipt': sum((b.ru_utime + b.ru_stime) - (a.ru_utime + a.ru_stime) for a, b in zip(usage_start, usage_end)),
                  'queue_own_receipt_tail_excluded': True, 'all_raw_outputs_retained': True,
                  'config_sha256': None if raw is None else hashlib.sha256(raw).hexdigest(),
                  'consumer_sha256': hashlib.sha256(own_raw).hexdigest()}
        meta = dict(result, label=folder.name, job='parent-envelope-overhead', kind='parent_cost_only',
                    wall_seconds=overhead, runner_wall_seconds=overhead)
        (folder / 'START.json').write_text(json.dumps({'kind': 'parent_cost_only'}) + '\n')
        (folder / 'receipt.json').write_text(json.dumps(meta, indent=2, sort_keys=True) + '\n')
        (ROOT / 'validation' / (name + '-QUEUE.json')).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
