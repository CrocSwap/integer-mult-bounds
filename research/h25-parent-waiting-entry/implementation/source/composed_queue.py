# Modified 2026-11-07: Clear1nsight, with OpenAI Codex and ChatGPT Pro assistance. See NOTICE.md.
"""Parent-owned serial queue derivative for the fresh composed route.

Actual runner receipts and retained logs are checked before the next case.
The explicit trusted transport retains native process authority. Nested metrics
are diagnostics inside one enclosing body, never additive ledger records.
No scientific module is imported here. No automatic retry.
"""
import hashlib
import json
import os
import resource
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028')


STAGE_BASE = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/caller-proof-completion-20261107T0155Z/implementation/bindings/stages')
CONFIG_BASE = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/caller-proof-completion-20261107T0155Z/implementation/bindings/control')
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



_COMPLETED = None
_FULL_RECEIVER = None


def bind_full_receiver(module):
    global _FULL_RECEIVER
    need(_FULL_RECEIVER is None and module is not None, 'one authenticated actual full receiver')
    _FULL_RECEIVER = module
    return True


def configure_completed_source(layout, registry, guardian):
    global _COMPLETED
    need(_COMPLETED is None and registry.layout is layout and guardian is not None,
         'one actual complete-source binding before producers')
    _COMPLETED = (layout, registry, guardian)
    return True

def completed_source():
    need(_COMPLETED is not None, 'actual complete-source binding required')
    return _COMPLETED

def digest(path):
    h = hashlib.sha256()
    count = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            h.update(block)
            count += len(block)
    return h.hexdigest(), count


def _write_admin(path,value,registry):
    raw=(json.dumps(value,indent=2,sort_keys=True)+'\n').encode('ascii')
    if len(raw)>4194304:
        raise ValueError('bounded queue admin metadata')
    fd,primary,secondary,traceback=None,None,None,None
    try:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        position=0
        while position<len(raw):
            count=os.write(fd,raw[position:position+65536])
            need(type(count) is int and count>0,'queue admin complete write')
            position+=count
        os.fsync(fd)
    except BaseException as error:
        primary=error
        traceback=BaseException.__dict__['__traceback__'].__get__(error,BaseException)
        registry.remember(error)
    finally:
        if fd is not None:
            closing_fd,fd=fd,None
            try:
                os.close(closing_fd)
            except BaseException as error:
                secondary=error
                registry.quarantine(error)
    if primary is not None:
        raise BaseException.with_traceback(primary,traceback)
    if secondary is not None:
        raise secondary


def record_time(path):
    row = json.loads(path.read_bytes())
    return row.get('runner_wall_seconds', row['wall_seconds'])


def validate(case, nested_root, runner_path):
    stage = STAGE_BASE / case['stage']
    stage_hash, _ = digest(stage / 'STAGE.json')
    need(stage_hash == case['stage_sha256'], 'Reviewed stage changed')
    declared = json.loads((stage / 'STAGE.json').read_bytes())
    layout,registry,guardian = completed_source()
    attempt = registry.attempt(case['label'])
    registry.assert_open(attempt)
    folder = attempt.layout.runner_root
    receipt = json.loads((folder / 'receipt.json').read_bytes())
    common='integration/candidate_entry.py' in declared['files']
    need(not common or case['job']=='normal','positive queue validator cannot accept optimized STOP')
    start = json.loads((folder / 'START.json').read_bytes())
    for key, value in start.items():
        need(receipt.get(key) == value, 'START differs from receipt: ' + key)
    need(receipt['stage_sha256'] == stage_hash, 'Receipt stage differs')
    need(receipt['runner_sha256'] == declared['runner_sha256'] == digest(runner_path)[0], 'Runner identity differs')
    need(receipt['parent_launch'] == require_trusted_launch(), 'Parent launch provenance differs')
    if not common:
        need(receipt['funding_intent_sha256'] == digest(attempt.layout.intent_path)[0] and
             receipt['outer_label'] == nested_root.name and receipt['nested_is_not_registry_charge'] is True,
             'Exact enclosing ACTIVE intent DATA provenance differs')
        need(_FULL_RECEIVER is not None and receipt['command'] ==
             _FULL_RECEIVER.command_for(stage,declared,case['job'],_FULL_RECEIVER.job_for(case['job']),attempt.layout.science_root),
             'Exact adopted full Root/provider/scientific command differs')
    else:
        entry=json.loads((folder/'ENTRY.json').read_bytes())
        need(entry['inner_command']==_FULL_RECEIVER.command_for(stage,declared,case['job'],
             _FULL_RECEIVER.job_for(case['job']),attempt.layout.science_root),
             'common entry retains the exact original inner scientific command')
    need(receipt['fractions_sha256'] == digest(Path('/usr/lib/python3.12/fractions.py'))[0], 'Actual Fraction source differs')
    need(receipt['label'] == case['label'] and receipt['job'] == case['job'], 'Receipt case differs')
    need(receipt['status'] == 'PASS' and receipt['exit'] == (1 if case['job'] == 'optimized' else 0) and
         receipt['termination'] is None, 'Actual runner terminal disposition differs')
    need(receipt['source_bytes_and_modes_unchanged'] is True and receipt['retained_log_bytes_stable'] is True, 'Custody or logs changed')
    need(receipt['log_read_chunk_bytes'] == 65536, 'Bounded log reader differs')
    for stream in ('stdout', 'stderr'):
        observed, count = digest(folder / (stream + '.txt'))
        need(observed == receipt[stream + '_sha256'], 'Raw log digest differs')
        need(count == receipt[stream + '_bytes'] == receipt[stream + '_final_bytes'], 'Raw log byte count differs')
        need(count <= 2097152, 'Ordinary raw log cap exceeded')
    need((receipt['stderr_bytes'] == 0) if case['job'] == 'normal' else
         (receipt['stderr_bytes'] > 0), 'Original full/refusal stderr disposition differs')
    need(receipt['runner_wall_seconds'] >= receipt['wall_seconds'] >= 0, 'Runner time scope differs')
    usage = receipt['usage']
    usage_fields_available = (type(usage) is dict and
        all(key in usage and type(usage[key]) in (int,float)
            for key in ('user_seconds','system_seconds','kernel_max_rss_kib')))
    science_status = ('FULL_NETWORK_COMPLETE_PASS' if case['job'] == 'normal' else
                      'ORIGINAL_OPTIMIZED_FULL_ENTRY_REFUSAL_OBSERVED')
    return {'label': case['label'], 'job': case['job'], 'stage': case['stage'],
            'gate': 'PASS_RETAINED_RECEIPT', 'science_status': science_status,
            'runner_wall_seconds': receipt['runner_wall_seconds'], 'child_wall_seconds': receipt['wall_seconds'],
            'cpu_seconds': (usage['user_seconds'] + usage['system_seconds']) if usage_fields_available else None,
            'usage_fields_available': usage_fields_available,
            'runner_cpu_seconds_before_own_receipt': receipt['runner_user_seconds'] + receipt['runner_system_seconds'],
            'kernel_max_rss_kib': usage['kernel_max_rss_kib'] if usage_fields_available else None,
            'sampled_process_group_rss_bytes': receipt['sampled_process_group_rss_bytes']}


def main(config_path, nested_root, runner_path, transport, *, layout=None, registry=None, guardian=None):
    if _COMPLETED is None:
        configure_completed_source(layout,registry,guardian)
    layout,registry,guardian = completed_source()
    require_trusted_launch()
    begin = time.monotonic()
    usage_start = (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN))
    own_raw = Path(__file__).read_bytes()
    name = 'unadmitted'
    raw = None
    rows, failure = [], None
    first_error = None
    actual_attempt = None
    try:
        need(type(config_path) is type(ROOT) and type(nested_root) is type(ROOT) and
             type(runner_path) is type(ROOT), 'Exact concrete queue paths required')
        need(config_path.resolve(strict=True) == config_path, 'Canonical frozen queue config required')
        need(config_path.is_relative_to(CONFIG_BASE), 'Queue config must be new-round control source')
        raw = config_path.read_bytes()
        spec = json.loads(raw)
        proposed = spec['queue']
        need(type(proposed) is str and proposed.isalnum(), 'Simple unique queue identity required')
        evidence = layout.admin_role('queue') / proposed
        need(not evidence.exists(), 'Queue already attempted; no automatic retry')
        need(not (layout.admin_role('queue') / (proposed+'-QUEUE.json')).exists(), 'Queue observation already exists')
        name = proposed
        layout.admin_role('queue').mkdir(mode=0o700,exist_ok=True)
        evidence.mkdir(mode=0o700)
        for case in spec['cases']:
            actual_attempt = registry.reserve_actual_attempt(case['label'])
            for key in ('stage','job','label'):
                need(type(case[key]) is str and case[key] and
                     all(c.isalnum() or c in '-_' for c in case[key]), 'Unsafe queue case identity')
            need(digest(STAGE_BASE / case['stage'] / 'STAGE.json')[0] == case['stage_sha256'],
                 'Admitted stage differs before queue')
            command = ['/usr/bin/python3.12', *LAUNCH_FLAGS, str(runner_path), case['stage'], case['job'], case['label']]
            case_begin = time.monotonic()
            case_usage = (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN))
            result = transport.run(command, cwd=ROOT, env=dict(LAUNCH_ENV), capture_output=True, timeout=190)
            registry.write_bytes(actual_attempt,'queue-stdout',actual_attempt.layout.queue_root / (case['label'] + '.stdout'),result.stdout)
            registry.write_bytes(actual_attempt,'queue-stderr',actual_attempt.layout.queue_root / (case['label'] + '.stderr'),result.stderr)
            need(result.returncode == (1 if case['job']=='optimized' else 0) and not result.stderr,
                 'actual common runner terminal code differs: '+case['label'])
            row = transport.validate(case)
            row.update(transport.primary(case))
            rows.append(row)
            registry.write_json(actual_attempt,'queue-gate',actual_attempt.layout.queue_root / (case['label'] + '.gate.json'),row)
            registry.required_writer_closed(actual_attempt,'queue')
            actual_attempt = None
            print(json.dumps(row, sort_keys=True), flush=True)
        need(config_path.read_bytes() == raw and Path(__file__).read_bytes() == own_raw, 'Queue config or consumer changed')
    except BaseException as error:
        first_error = error  # Direct actual object before helper or projection.
        try:
            registry.remember(error)
        except BaseException:
            pass
        failure = {'type':'opaque-caught-exception','message':'projection_unavailable'}
    finally:
        finalizer_errors = [None] * 8
        if actual_attempt is not None and actual_attempt.status is None:
            try:
                registry.write_json(actual_attempt,'queue-terminal',actual_attempt.layout.queue_root / 'QUEUE-STOP.json',
                    {'schema':'h25-actual-queue-case-stop-v1','status':'INTERRUPTED' if type(first_error) in (KeyboardInterrupt,SystemExit) else 'STOP',
                     'error_type':None if first_error is None else 'opaque-caught-exception',
                     'canonical_runner_receipt_created':False})
                registry.required_writer_closed(actual_attempt,'queue')
            except BaseException as error:
                finalizer_errors[0] = error
        usage_end, elapsed = None,None
        try:
            usage_end = (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN))
        except BaseException as error:
            finalizer_errors[1] = error
        try:
            elapsed = time.monotonic() - begin
        except BaseException as error:
            finalizer_errors[2] = error
        for error in finalizer_errors:
            if error is not None:
                if first_error is None:
                    first_error = error
                try:
                    registry.remember(error)
                except BaseException:
                    pass
        try:
            result = {'status':'STOP' if first_error is not None else 'PASS_REVIEWED_QUEUE',
                'queue':name,'controls':rows,'failure':failure,
                'nested_metrics_not_additive_charges':True,'financial_receipt_created':False,
                'complete_queue_seconds_before_own_receipt':elapsed,
                'parent_self_cpu_seconds_before_own_receipt':None if usage_end is None else (usage_end[0].ru_utime+usage_end[0].ru_stime)-(usage_start[0].ru_utime+usage_start[0].ru_stime),
                'all_child_cpu_seconds_before_own_receipt':None if usage_end is None else (usage_end[1].ru_utime+usage_end[1].ru_stime)-(usage_start[1].ru_utime+usage_start[1].ru_stime),
                'complete_cpu_seconds_before_own_receipt':None if usage_end is None else sum((b.ru_utime+b.ru_stime)-(a.ru_utime+a.ru_stime) for a,b in zip(usage_start,usage_end)),
                'queue_own_receipt_tail_excluded':True,'all_raw_outputs_retained':first_error is None,
                'config_sha256':None if raw is None else hashlib.sha256(raw).hexdigest(),
                'consumer_sha256':hashlib.sha256(own_raw).hexdigest()}
            destination = layout.admin_role('queue') / (name+'-QUEUE.json')
            _write_admin(destination,result,registry)
        except BaseException as error:
            finalizer_errors[3] = error
            if first_error is None:
                first_error = error
            try:
                registry.remember(error)
            except BaseException:
                pass
    if first_error is not None:
        raise first_error


def finalize_completed_source(error=None):
    layout,registry,guardian = completed_source()
    for item in registry.snapshot()['attempts']:
        attempt = registry.attempt(item['label'])
        if attempt.status is not None or attempt.required['queue'] is True:
            continue
        registry.prepare_finalizer_dirs(attempt)
        if error is not None:
            registry.capture_error(attempt,error)
        registry.write_json(attempt,'queue-finalizer',attempt.layout.queue_root/'QUEUE-FINALIZER.json',{
            'schema':'h25-queue-finalizer-stop-v1','label':attempt.label,'status':'STOP',
            'canonical_runner_receipt_created':False,'raw_original_error_held':attempt.error is not None})
        registry.required_writer_closed(attempt,'queue')
