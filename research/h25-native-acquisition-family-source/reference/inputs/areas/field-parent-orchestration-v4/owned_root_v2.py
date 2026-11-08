"""Concrete fixed-plan Roots under the original process/domain owner.

This is not another outer runner and accepts no caller command, callback or
completion record. The orchestrator retains all returned opaque tokens. The
actual complete schedule/premises must be independently configured first.
"""
import os
import resource
import signal
import subprocess
import time
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import parent_completion_v1 as parent
import parent_domain_v1 as domain
import group01_evidence_v1 as evidence

CONFIGURATION = None
SOURCE_REVIEW = None
RUNTIME_CONFIGURATION = None
STAGE_APPROVAL = None
COMMAND_APPROVAL = None
FUNDING = None
EXECUTION_APPROVAL = None
_ROOT_PARENTS = []
_TYPE, _LEN = type, len
_OPEN, _CLOSE, _MKDIR, _STAT = os.open, os.close, os.mkdir, os.stat
_POPEN, _CLOCK, _SLEEP = subprocess.Popen, time.monotonic, time.sleep
_SETRLIMIT, _GETRLIMIT = resource.setrlimit, resource.getrlimit
_SETTIMER, _GETTIMER = signal.setitimer, signal.getitimer
_SIGNAL, _GETSIGNAL = signal.signal, signal.getsignal
ENV = parent.ENV


def _gate():
    schema.exact(CONFIGURATION, ('normal', 'optimized'))
    for pin in CONFIGURATION.values():
        schema.blob(pin, schema.RECORD_BYTES)
    for value, name in ((SOURCE_REVIEW, 'SOURCE_REVIEW'), (RUNTIME_CONFIGURATION, 'RUNTIME_CONFIGURATION'),
        (STAGE_APPROVAL, 'STAGE_APPROVAL'), (COMMAND_APPROVAL, 'COMMAND_APPROVAL'),
        (FUNDING, 'FUNDING'), (EXECUTION_APPROVAL, 'EXECUTION_APPROVAL')):
        schema.need(_TYPE(value) is tuple and _LEN(value) == 2 and _TYPE(value[0]) is str and value[0] == name,
                    'fixed Root external gate absent')
        schema.digest(value[1])


def _state(owner):
    schema.need(_TYPE(owner) is object, 'exact live Root parent required')
    for token, state in _ROOT_PARENTS:
        if token is owner:
            return state
    raise schema.EpochStop('unknown fixed Root parent')


def _guard(state):
    _gate()
    parent._guard(state['original'])
    schema.need(state['phase'] != 'STOP' and os.getpid() == state['pid'], 'Root owner stopped or moved process')
    schema.need(CONFIGURATION[state['mode']] == state['plan_pin'], 'fixed Root plan changed')
    copying.verify(state['plan_pin'], schema.RECORD_BYTES, error_owner=state['errors'])
    schema.need(evidence.encode(state['plan']) == state['plan_raw'], 'private Root plan changed')
    schema.need((_OPEN, _CLOSE, _MKDIR, _STAT, _POPEN, _CLOCK, _SLEEP, _SETRLIMIT, _GETRLIMIT,
                 _SETTIMER, _GETTIMER, _SIGNAL, _GETSIGNAL) ==
                (os.open, os.close, os.mkdir, os.stat, subprocess.Popen, time.monotonic, time.sleep,
                 resource.setrlimit, resource.getrlimit, signal.setitimer, signal.getitimer, signal.signal, signal.getsignal),
                 'owned Root primitive binding changed')


def _stop(state, operation, error):
    unknown = state['unknown_owner']
    if unknown['primary'][0] is None:
        unknown['primary'][0] = error
    unknown['quarantine'][0] = True
    if state['primary'][0] is None:
        state['primary'][0] = error
    state['phase'] = 'STOP'


def _alarm(signum, frame):
    raise parent.ParentDeadline('complete fixed Root including spawn deadline')


def make_root_parent(original_parent):
    original = parent._state(original_parent)
    state = None
    try:
        _gate()
        parent._guard(original)
        mode = original['plan']['mode']
        schema.need(_LEN(_ROOT_PARENTS) < 2 and not any(s['mode'] == mode for _, s in _ROOT_PARENTS),
                    'fixed Root parent mode replay')
        pin = CONFIGURATION[mode]
        raw = copying.read_verified_complete_v3(pin, schema.RECORD_BYTES, error_owner=original['errors'])
        plan = evidence.decode(raw)
        schema.exact(plan, ('schema', 'mode', 'parent_plan_sha256', 'source_closure_admission_sha256',
                           'source_files', 'actions'))
        schema.need(plan['schema'] == 'h25-owned-fixed-root-plan-v2' and plan['mode'] == mode and
                    plan['parent_plan_sha256'] == original['configuration']['plan']['sha256'],
                    'actual original parent source plan differs')
        schema.digest(plan['source_closure_admission_sha256'])
        schema.need(_TYPE(plan['actions']) is list and 1 <= _LEN(plan['actions']) <= 256, 'Root action plan missing')
        ids, paths = set(), set()
        for row in plan['actions']:
            schema.exact(row, ('action_id', 'generation', 'source_role', 'binding_sha256', 'phase',
                'command', 'cwd', 'output', 'evidence_directory', 'stage_directory', 'stage_manifest',
                'stage_directories', 'launch_binding', 'launch_artifacts', 'root_seconds', 'address_space_bytes',
                'rss_bytes', 'evidence_plan', 'driver_sha256', 'driver_path'))
            for key in ('action_id', 'generation', 'source_role'):
                schema.label(row[key])
            schema.digest(row['binding_sha256']); schema.digest(row['driver_sha256']); schema.path(row['driver_path'])
            schema.choice(row['phase'], ('finite', 'full'))
            schema.need(row['source_role'] != 'baseline-full',
                        'primary predecessor requires a separately sourced compatibility-only owner; candidate Root route is prohibited')
            schema.need(row['action_id'] not in ids, 'duplicate owned action')
            ids.add(row['action_id'])
            for key in ('cwd', 'output', 'evidence_directory', 'stage_directory'):
                schema.path(row[key])
            schema.need(row['output'] not in paths and row['evidence_directory'] not in paths and
                        row['output'] != row['evidence_directory'], 'owned output path reused')
            paths.update((row['output'], row['evidence_directory']))
            schema.need(row['evidence_directory'].startswith(original['plan']['session_directory'] + '/') and
                        row['output'].startswith(original['plan']['session_directory'] + '/'), 'owned Root outside parent session')
            schema.blob(row['stage_manifest'], schema.RECORD_BYTES)
            schema.launch(row['launch_binding'])
            schema.need(_TYPE(row['command']) is list and 6 <= _LEN(row['command']) <= 96 and
                        all(_TYPE(s) is str for s in row['command']), 'fixed exact command absent')
            prefix = ['/usr/bin/python3.12', *parent.FLAGS] + (
                ['-O'] if row['phase'] == 'finite' and mode == 'optimized' else [])
            schema.need(row['command'][:len(prefix)] == prefix and len(row['command']) > len(prefix),
                        'exact clean interpreter path/flags/mode differs')
            entry = row['command'][len(prefix)]
            schema.path(entry)
            schema.need(entry.startswith(row['stage_directory'] + '/'), 'owned entry outside exact stage')
            by_path = {item['path']: item for item in plan['source_files']}
            schema.need(len(by_path) == len(plan['source_files']) and entry in by_path,
                        'actual entry lacks independent complete source pin')
            command = row['command']
            schema.need(command.count('--driver') <= 1 and ('--driver' not in command or
                command.index('--driver') + 2 < len(command)), 'actual driver selector is truncated/repeated')
            driver = command[command.index('--driver') + 1] if command.count('--driver') == 1 else entry
            schema.need(driver == row['driver_path'], 'actual selected driver path differs from fixed row')
            schema.need(command.count('--driver') <= 1 and driver in by_path and
                        by_path[driver]['sha256'] == row['driver_sha256'], 'actual driver source binding differs')
            if '--driver' in command:
                schema.need(command[command.index('--driver') + 2] == row['driver_sha256'],
                            'genuine bootstrap driver digest differs')
            schema.need(command.count('--output') == 1 and
                        command[command.index('--output') + 1] == row['output'], 'fixed output argument differs')
            schema.need(schema.sha(schema.canonical({'argv': command})) == row['launch_binding']['command_sha256'] and
                        row['stage_manifest']['sha256'] == row['launch_binding']['stage_sha256'],
                        'actual command or complete stage launch binding differs')
            schema.need(row['launch_binding']['root_sha256'] ==
                        'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0' and
                        any(item['sha256'] == row['launch_binding']['root_sha256'] for item in plan['source_files']),
                        'unchanged genuine Root source omitted')
            schema.need(not any(x in ('-c', '-m', '-OO', '-I') for x in row['command']), 'alternate entry route forbidden')
            if row['phase'] == 'full':
                schema.need('-O' not in row['command'] and '--finite-only' not in row['command'],
                            'every scientific arm requires assertions and original full caller')
            else:
                schema.need(('-O' in row['command']) is (mode == 'optimized'), 'finite command mode differs')
            for key in ('root_seconds', 'rss_bytes', 'address_space_bytes'):
                schema.integer(row[key], 1, 180 if key == 'root_seconds' else 1024 ** 3)
            schema.exact(row['launch_artifacts'], ('configuration_sha256', 'startup_tcb_sha256', 'expected_history_sha256'))
            for key, artifact in row['launch_artifacts'].items():
                schema.blob(artifact, schema.RECORD_BYTES)
                schema.need(artifact['sha256'] == row['launch_binding'][key] and artifact['path'] in by_path and
                            by_path[artifact['path']]['sha256'] == artifact['sha256'] and
                            by_path[artifact['path']]['bytes'] == artifact['bytes'],
                            'actual launch artifact lacks exact source inventory binding')
        state = {'original': original, 'mode': mode, 'plan': plan, 'plan_pin': schema.plain_copy(pin),
            'plan_raw': evidence.encode(plan), 'pid': original['pid'], 'phase': 'READY', 'next': 0,
            'runs': {}, 'errors': original['errors'], 'unknown_owner': original['unknown_owner'],
            'io_quarantine': original['unknown_owner']['quarantine'], 'shared_deadline': original['shared_deadline'],
            'primary': [None], 'fallback': [None] * 4}
        token = object()
        _ROOT_PARENTS.append((token, state))
        _guard(state)
        return token
    except BaseException as error:
        if original['unknown_owner']['primary'][0] is None:
            original['unknown_owner']['primary'][0] = error
        original['unknown_owner']['quarantine'][0] = True
        if state is not None:
            state['phase'] = 'STOP'
            state['primary'][0] = error
        raise


def _snapshot_sources(plan, errors):
    return parent._snapshot_sources(plan, errors)


def _stage(plan, errors, state):
    return parent._stage(plan, errors, state)


def _source_custody_bytes(state, files, stage):
    return parent._source_custody_bytes(state, files, stage)


def _close_logs(run, primary):
    return parent._close_logs(run, primary)


def run_owned_root(owner_capability, action_id):
    state = _state(owner_capability)
    try:
        _guard(state)
        schema.label(action_id)
        schema.need(state['phase'] == 'READY' and state['next'] < len(state['plan']['actions']) and
                    action_id == state['plan']['actions'][state['next']]['action_id'] and action_id not in state['runs'],
                    'fixed Root order, replay or prior completion differs')
    except BaseException as primary:
        _stop(state, 'run_producer_entry', primary)
        raise
    row = state['plan']['actions'][state['next']]
    producer_role = row['source_role']
    # Consume the declared fixed Root before any later preparation or launch.
    try:
        # The caller has durably burned this exact declared action before entry.
        # This private Root owner adds a second source-owned one-shot reservation.
        run_token = object()
        run = {'token': run_token, 'role': producer_role, 'phase': 'RESERVED',
           'unknown_owner': state['unknown_owner'],
           'plan': row, 'domain': None, 'process': None, 'root': None, 'terminal': None,
           'log_fds': [None, None], 'log_close_attempted': [False, False],
           'log_close_confirmed': [False, False], 'errors': [None] * 8,
           'primary': [None], 'acquisition_in_flight': False, 'spawn_entered': False,
           'spawn_returned': False, 'source_before': None, 'stage_before': None,
               'began': _CLOCK(), 'peak_rss': 0, 'file_limits': tuple(_GETRLIMIT(resource.RLIMIT_FSIZE))}
        state['runs'][action_id] = run
        state['phase'] = 'PRODUCER_IN_FLIGHT'
    except BaseException as primary:
        _stop(state, 'run_producer_reservation', primary)
        raise
    primary = None
    old_handler = None
    alarm_installed = False
    try:
        _guard(state)
        _MKDIR(row['evidence_directory'], 0o700)
        # output remains absent; the genuine original Root creates it exclusively.
        try:
            _STAT(row['output'], follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise schema.EpochStop('producer output already exists')
        if row['source_role'] == 'elf41':
            # The exact accepted standalone adapter requires caller-owned0700 output.
            _MKDIR(row['output'], 0o700)
        local_plan = dict(state['plan'], **row)
        run['source_before'] = _snapshot_sources(state['plan'], state['errors'])
        run['stage_before'] = _stage(local_plan, state['errors'], state)
        # Reject oversized complete-custody records BEFORE any child launch.
        run['source_bytes_before'] = _source_custody_bytes(state, run['source_before'], run['stage_before'])
        for pin in row['launch_artifacts'].values():
            copying.verify(pin, schema.RECORD_BYTES, error_owner=state['errors'])
        run['domain'] = domain.create_domain(state['unknown_owner'])
        launch = {'schema': 'h25-owned-fixed-root-launch-v2', 'epoch_id': state['original']['plan']['epoch_id'],
            'mode': state['plan']['mode'], 'role': producer_role,
            'generation': row['generation'], 'action_id': action_id,
            'parent_pid': state['pid'], 'command': row['command'], 'environment': ENV, 'cwd': row['cwd'],
            'launch_binding': row['launch_binding'], 'parent_file_limits': list(run['file_limits']),
            'new_session': True, 'close_fds': True, 'pass_fds': [],
            'root_seconds': row['root_seconds'], 'rss_bytes': row['rss_bytes'],
            'address_space_bytes': row['address_space_bytes']}
        run['launch'] = copying.write_once(row['evidence_directory'] + '/LAUNCH.json',
            schema.canonical(launch), error_owner=state['errors'])
        for index, name in enumerate(('stdout.raw', 'stderr.raw')):
            schema.need(state['io_quarantine'][0] is False and state['unknown_owner']['pending'][0] is False and
                        state['unknown_owner']['iterator_uncertain'][0] is False,
                        'raw stream cannot acquire after uncertain ownership')
            run['acquisition_in_flight'] = True
            state['unknown_owner']['pending'][0] = True
            run['log_fds'][index] = _OPEN(row['evidence_directory'] + '/' + name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
            run['acquisition_in_flight'] = False
            state['unknown_owner']['pending'][0] = False
        setter, kind, limits = _SETRLIMIT, resource.RLIMIT_AS, (row['address_space_bytes'], row['address_space_bytes'])
        def child_limit():
            setter(kind, limits)
        schema.need(_GETTIMER(signal.ITIMER_REAL) == (0.0, 0.0), 'existing parent timer cannot be replaced')
        old_handler = _GETSIGNAL(signal.SIGALRM)
        _SIGNAL(signal.SIGALRM, _alarm)
        alarm_installed = True
        deadline = min(run['began'] + row['root_seconds'], state['shared_deadline'] - domain.CLEANUP_SECONDS)
        schema.need(_CLOCK() < deadline, 'no funded root/cleanup interval remains')
        _SETTIMER(signal.ITIMER_REAL, max(0.000001, deadline - _CLOCK()))
        run['spawn_entered'] = True
        run['process'] = _POPEN(row['command'], cwd=row['cwd'], env=dict(ENV),
            stdout=run['log_fds'][0], stderr=run['log_fds'][1], stdin=subprocess.DEVNULL,
            close_fds=True, pass_fds=(), start_new_session=True, preexec_fn=child_limit)
        run['spawn_returned'] = True
        run['root'] = domain.adopt_popen(run['domain'], run['process'])
        while True:
            unused, current = domain.observe(run['domain'])
            run['peak_rss'] = max(run['peak_rss'], sum(item[6] for item in current))
            schema.need(run['peak_rss'] <= row['rss_bytes'], 'owned process RSS sum exceeded')
            schema.need(max(_STAT(row['evidence_directory'] + '/' + name, follow_symlinks=False).st_size
                        for name in ('stdout.raw', 'stderr.raw')) <= schema.LOG_BYTES, 'root output bound exceeded')
            if domain.poll_owned(run['domain']) is not None:
                break
            _SLEEP(0.01)
    except BaseException as error:
        if state['unknown_owner']['primary'][0] is None:
            state['unknown_owner']['primary'][0] = error
        primary = state['unknown_owner']['primary'][0]
        run['primary'][0] = primary
        if primary is not error:
            run['errors'][4] = error
        if (run['acquisition_in_flight'] or state['unknown_owner']['pending'][0] or
                state['unknown_owner']['iterator_uncertain'][0] or _TYPE(error) is MemoryError):
            state['io_quarantine'][0] = True
        raise primary
    finally:
        # Preserve the first locally delivered primary through all cleanup.
        first_cleanup = None
        if alarm_installed:
            try:
                _SETTIMER(signal.ITIMER_REAL, 0)
                _SIGNAL(signal.SIGALRM, old_handler)
            except BaseException as error:
                run['errors'][2] = error
                first_cleanup = error
        if run['domain'] is not None:
            try:
                domain.finish_domain(run['domain'])
            except BaseException as error:
                run['errors'][3] = error
                state['io_quarantine'][0] = True
                if first_cleanup is None:
                    first_cleanup = error
        try:
            _close_logs(run, primary if primary is not None else first_cleanup)
        except BaseException as error:
            if first_cleanup is None:
                first_cleanup = error
        for index in range(2):
            if run['log_close_attempted'][index] and not run['log_close_confirmed'][index]:
                state['io_quarantine'][0] = True
        if primary is not None:
            _stop(state, 'run_producer', primary)
        elif first_cleanup is not None:
            _stop(state, 'run_producer_cleanup', first_cleanup)
            raise first_cleanup
    try:
        schema.need(run['spawn_entered'] is True and run['spawn_returned'] is True and
                    run['acquisition_in_flight'] is False and all(run['log_close_confirmed']),
                    'root spawn or raw stream ownership incomplete')
        run['terminal'] = domain.terminal_facts(run['domain'])
        schema.need(tuple(_GETRLIMIT(resource.RLIMIT_FSIZE)) == run['file_limits'], 'parent file limit drift')
        run['phase'] = 'JOINED'
        state['phase'] = 'PRODUCER_JOINED'
        _guard(state)
        return run_token
    except BaseException as primary:
        _stop(state, 'postcleanup_terminal', primary)
        raise



def _joined(owner, joined):
    state = _state(owner)
    _guard(state)
    schema.need(_TYPE(joined) is object and state['phase'] == 'PRODUCER_JOINED', 'owned joined Root required')
    matches = [r for r in state['runs'].values() if r['token'] is joined]
    schema.need(len(matches) == 1 and matches[0]['phase'] == 'JOINED', 'owned Root token replay')
    run = matches[0]
    run['phase'] = 'RECEIVER_CONSUMED'
    return state, run


def _accepted(state, run):
    _guard(state)
    schema.need(domain.terminal_facts(run['domain']) == run['terminal'], 'late owned cleanup changed')
    schema.need(_snapshot_sources(state['plan'], state['errors']) == run['source_before'], 'final sources changed')
    schema.need(_stage(dict(state['plan'], **run['plan']), state['errors'], state) == run['stage_before'], 'final stage changed')
    schema.need(_CLOCK() <= run['began'] + run['plan']['root_seconds'], 'complete receiver tail exceeds Root bound')
    run['phase'] = 'ACCEPTED'
    state['next'] += 1
    state['phase'] = 'READY' if state['next'] < len(state['plan']['actions']) else 'COMPLETE'


def stop_evidence(owner):
    state = _state(owner)
    return state['primary'], state['fallback'], tuple((r['primary'], r['errors']) for r in state['runs'].values())
