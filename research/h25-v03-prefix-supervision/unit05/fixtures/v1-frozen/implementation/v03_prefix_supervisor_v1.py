"""One non-minting genuine-Root V03 prefix observation per fresh parent.

Conditional source proposal, Apache-2.0. Derived from the recovered original
parent/domain/closure/copy/supervisor sources. Preserve all original notices.

The enclosing trusted bootstrap must authenticate this source, its imports,
configured selections and native/OS startup before import. C07 ancestor and
immutable-lifetime conditions remain actual external prerequisites.

No epoch is created, reserved, accepted, committed or completed here.
"""
import fcntl
import os
from pathlib import Path
import resource
import signal
import stat
import subprocess
import time

import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import parent_domain_v1 as domain
import parent_closure_v1 as closure
import parent_completion_v1 as parent
import group01_evidence_v1 as group01
import v03_prefix_derivation_v1 as derivation

CONFIGURATION = None
SOURCE_REVIEW = None
STAGE_APPROVAL = None
COMMAND_APPROVAL = None
FUNDING = None
EXECUTION_APPROVAL = None

ROOT_SHA = 'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0'
PROVIDER_SHA = '9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2'
VARIANT_SHA = 'cdb1479253358508088f8aa0e1e92e6c75ffcc127e54552698598a02de061254'
OBSERVER = 'v03_source_refusal_observer_v1'
ENV = {'PATH': '/usr/bin:/bin', 'PYTHONHASHSEED': '0',
       'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC',
       'PYTHONDONTWRITEBYTECODE': '1'}

_PID, _CLOCK, _FLOCK = os.getpid, time.monotonic, fcntl.flock
_PREFIX = [False, None]
_UNKNOWN_OWNER = {
    'quarantine': [False], 'pending': [False],
    'iterator_uncertain': [False], 'primary': [None],
    'native_errors': [None] * 4,
}
_INITIAL = (
    'initial-tcb.raw.json', 'initial-controls.raw.json',
    'initial-restoration.raw.json',
)
_PREFLIGHT = _INITIAL + ('root-before.raw.json', 'preflight-before.raw.json')
_CUSTODY = _PREFLIGHT + ('custody-before.raw.json',)
_RETURNED = _CUSTODY + (
    'v03-root-after.raw.json', 'v03-input-result.raw.json',
)


def _gate_snapshot():
    schema.exact(CONFIGURATION, (
        'plan', 'receiver_policy', 'checker_source', 'original_variant',
    ))
    for pin in CONFIGURATION.values():
        schema.blob(pin, schema.RECORD_BYTES)
    records = (
        (SOURCE_REVIEW, 'review_sha256'),
        (STAGE_APPROVAL, 'stage_review_sha256'),
        (COMMAND_APPROVAL, 'command_review_sha256'),
        (FUNDING, 'reservation_sha256'),
        (EXECUTION_APPROVAL, 'external_launch_policy_sha256'),
    )
    for record, key in records:
        schema.exact(record, (key,))
        schema.digest(record[key])
    copying._gate()
    return schema.plain_copy({
        'configuration': CONFIGURATION,
        'source': SOURCE_REVIEW, 'stage': STAGE_APPROVAL,
        'command': COMMAND_APPROVAL, 'funding': FUNDING,
        'execution': EXECUTION_APPROVAL,
        'copy_configuration': copying.COPY_CONFIGURATION,
        'copy_execution': copying.COPY_EXECUTION_APPROVAL,
        'copy_funding': copying.COPY_FUNDING,
    })


def _state(token):
    schema.need(type(token) is object and _PREFIX[1] is not None and
                _PREFIX[1][0] is token, 'unknown prefix owner')
    return _PREFIX[1][1]


def _clean(owner):
    domain.refresh_unknown_owner(owner)
    schema.need(owner['primary'][0] is None and
                owner['quarantine'][0] is False and
                owner['pending'][0] is False and
                owner['iterator_uncertain'][0] is False,
                'prefix owner requires kernel teardown')


def _native_bindings():
    schema.need(
        _PID is os.getpid and _CLOCK is time.monotonic and
        _FLOCK is fcntl.flock and parent.ENV == ENV and
        parent._OPEN is os.open and parent._CLOSE is os.close and
        parent._MKDIR is os.mkdir and parent._STAT is os.stat and
        parent._SCANDIR is os.scandir and
        parent._POPEN is subprocess.Popen and
        parent._CLOCK is time.monotonic and parent._SLEEP is time.sleep and
        parent._SETRLIMIT is resource.setrlimit and
        parent._GETRLIMIT is resource.getrlimit and
        parent._SETTIMER is signal.setitimer and
        parent._GETTIMER is signal.getitimer and
        parent._SIGNAL is signal.signal and
        parent._GETSIGNAL is signal.getsignal,
        'prefix native primitive binding changed',
    )


def _guard(state):
    schema.need(state['phase'] not in ('STOP', 'CLOSED'),
                'prefix owner is terminal')
    schema.need(_PID() == state['pid'], 'prefix owner crossed process')
    _native_bindings()
    _clean(state['unknown_owner'])
    schema.need(_gate_snapshot() == state['admissions'],
                'prefix admission selections changed')
    closure.check_receivers(state['receivers'])
    for pin in state['configuration'].values():
        copying.verify(pin, error_owner=state['errors'])
    schema.need(state['native_keeper'] is not None and
                all(type(fd) is int and fd >= 0 for fd in state['lock_fds']),
                'prefix real keeper or lock ownership missing')
    schema.need(_CLOCK() <= state['shared_deadline'],
                'complete prefix owner deadline exceeded')


def _expected_files(expected):
    schema.exact(expected, (
        'outcome', 'exception_type', 'message', 'terminal_function',
        'v03_discriminator', 'compiler_launches', 'candidate_image_loads',
        'complete_raw_and_owned_terminal_required',
    ))
    schema.boolean(expected['v03_discriminator'])
    schema.need(type(expected['compiler_launches']) is int and
                expected['compiler_launches'] == 0 and
                type(expected['candidate_image_loads']) is int and
                expected['candidate_image_loads'] == 0 and
                expected['complete_raw_and_owned_terminal_required'] is True,
                'prefix expectation scope differs')
    outcome = expected['outcome']
    function, message = expected['terminal_function'], expected['message']
    if outcome == 'PREFIX_RETURN':
        schema.need(function is None and message is None and
                    expected['exception_type'] is None,
                    'positive prefix expectation differs')
        return _RETURNED
    schema.need(outcome == 'EXACT_SOURCE_REFUSAL' and
                expected['exception_type'] == 'RuntimeError',
                'prefix refusal expectation differs')
    if function == '_vcheck_literal_sources':
        schema.need(message in (
            'Variant source role path differs',
            'Variant reviewed source/header differs',
            'Variant role file omitted from closure',
        ), 'prefix literal refusal site differs')
        return _INITIAL
    if function == '_vcheck_custody':
        schema.need(message == 'Variant current source closure differs',
                    'prefix custody refusal site differs')
        return _CUSTODY
    schema.need(function == '_v03_original_input_prefix',
                'prefix refusal function differs')
    if message == 'Variant literal configuration differs':
        return _INITIAL
    schema.need(message == 'Variant original preflight differs' and
                expected['v03_discriminator'] is False,
                'earlier preflight refusal cannot receive V03 credit')
    return _PREFLIGHT


def _validate_plan(plan):
    schema.exact(plan, (
        'schema', 'mode', 'round_root', 'session_directory',
        'session_seconds', 'source_closure_admission_sha256',
        'source_files', 'case',
    ))
    schema.need(plan['schema'] == 'h25-v03-prefix-parent-plan-v1',
                'prefix plan schema differs')
    schema.choice(plan['mode'], ('normal', 'optimized'))
    for key in ('round_root', 'session_directory'):
        schema.path(plan[key])
    schema.integer(plan['session_seconds'], 1, 600)
    schema.digest(plan['source_closure_admission_sha256'])
    schema.need(type(plan['source_files']) is list and
                1 <= len(plan['source_files']) <= parent.MAX_SOURCE_FILES,
                'prefix parent source inventory bound differs')
    case = plan['case']
    schema.exact(case, (
        'id', 'generation', 'launch_nonce', 'stage_directory',
        'stage_manifest', 'stage_directories', 'output', 'command',
        'root_seconds', 'address_space_bytes', 'rss_bytes',
        'root_source', 'driver_source', 'gate_values', 'expectation',
    ))
    schema.label(case['id'])
    schema.label(case['generation'])
    schema.digest(case['launch_nonce'])
    schema.path(case['stage_directory'])
    schema.path(case['output'])
    schema.need(
        case['output'] == plan['session_directory'] + '/producer-output' and
        case['output'] != case['stage_directory'] and
        not case['output'].startswith(case['stage_directory'] + '/'),
        'prefix source/output origins differ',
    )
    schema.integer(case['root_seconds'], 1, 180)
    schema.integer(case['address_space_bytes'], 1, 1024 ** 3)
    schema.integer(case['rss_bytes'], 1, 1024 ** 3)
    for key in ('stage_manifest', 'root_source', 'driver_source', 'gate_values'):
        schema.blob(case[key], schema.RECORD_BYTES)
    schema.need(type(case['stage_directories']) is list and
                len(case['stage_directories']) <= parent.MAX_STAGE_ENTRIES,
                'prefix stage directory declaration differs')
    integration = case['stage_directory'] + '/integration'
    schema.need(
        case['root_source']['path'] == integration + '/full_driver.py' and
        case['root_source']['sha256'] == ROOT_SHA and
        case['root_source']['bytes'] == 38851 and
        case['driver_source']['path'] ==
            integration + '/v03_control_driver_v1.py' and
        0 < case['driver_source']['bytes'] <= 262144,
        'prefix genuine Root/selected driver source differs',
    )
    command = ['/usr/bin/python3.12', '-S', '-s', '-P', '-B']
    if plan['mode'] == 'optimized':
        command.append('-O')
    command += [
        integration + '/full_driver.py', '--root-sha256', ROOT_SHA,
        '--provider', integration + '/probe_binding_v3.py', PROVIDER_SHA,
        '--driver', case['driver_source']['path'],
        case['driver_source']['sha256'], '--integration', integration, '--',
        '--output', case['output'], '--generation', case['generation'],
        '--launch-nonce', case['launch_nonce'],
    ]
    schema.need(type(case['command']) is list and
                all(type(arg) is str for arg in case['command']) and
                case['command'] == command,
                'prefix exact original Root command differs')
    _expected_files(case['expectation'])


def _record_bytes(value):
    raw = group01.encode(value)
    schema.need(len(raw) <= schema.RECORD_BYTES,
                'prefix parent record exceeds original writer bound')
    return raw


def _source_snapshot(state):
    plan = state['plan']
    files = parent._snapshot_sources(plan, state['errors'])
    stage = parent._stage(dict(plan, **plan['case']), state['errors'], state)
    raw = _record_bytes({
        'schema': 'h25-prefix-source-custody-v1',
        'files': files, 'stage': stage,
        'source_closure_admission_sha256':
            plan['source_closure_admission_sha256'],
        'interval_proved_by_endpoint_equality': False,
    })
    return files, stage, raw


def make_prefix_owner(original_receivers):
    schema.need(_PREFIX[0] is False, 'one prefix owner per fresh process')
    _PREFIX[0] = True
    began = _CLOCK()
    state = None
    try:
        admissions = _gate_snapshot()
        _native_bindings()
        _clean(_UNKNOWN_OWNER)
        errors = schema.make_error_owner()
        _UNKNOWN_OWNER['native_errors'][0] = schema.owner_state(errors)
        configuration = schema.plain_copy(CONFIGURATION)
        plan = group01.decode(copying.read_verified(
            configuration['plan'], schema.RECORD_BYTES, error_owner=errors))
        _validate_plan(plan)
        policy = group01.decode(copying.read_verified(
            configuration['receiver_policy'], schema.RECORD_BYTES,
            error_owner=errors))
        schema.need(type(policy) is dict and
                    policy.get('v03_prefix_supervisor_v1') ==
                    configuration['checker_source'],
                    'prefix checker absent from independent source policy')
        receivers = closure.bind_receivers(original_receivers, policy, errors)
        schema.need(
            closure.receiver(receivers, 'v03_prefix_supervisor_v1',
                             'make_prefix_owner') is make_prefix_owner and
            closure.receiver(receivers, 'epoch_schema_v5',
                             'make_error_owner') is schema.make_error_owner and
            closure.receiver(receivers, 'epoch_copy_v5',
                             'inspect') is copying.inspect and
            closure.receiver(receivers, 'parent_domain_v1',
                             'create_domain') is domain.create_domain and
            closure.receiver(receivers, 'parent_completion_v1',
                             '_snapshot_sources') is parent._snapshot_sources and
            closure.receiver(receivers, 'v03_prefix_derivation_v1',
                             'verify_configured_prefix') is
                             derivation.verify_configured_prefix,
            'prefix actual receiver identities differ',
        )
        schema.need(parent._PARENTS == [] and parent._PROCESS[0] is None and
                    domain._DOMAINS == [],
                    'prefix requires a fresh parent/domain lifetime')
        _clean(parent._UNKNOWN_OWNER)
        launch_contract = closure.receiver(
            receivers, 'h25_parent_supervisor', 'launch_contract')
        installer = closure.receiver(
            receivers, 'h25_parent_supervisor', 'install_subreaper')
        launch_contract()
        closure.check_receivers(receivers)

        case = plan['case']
        state = {
            'pid': _PID(), 'phase': 'CONSTRUCTING', 'errors': errors,
            'plan': plan, 'configuration': configuration,
            'admissions': admissions, 'receivers': receivers,
            'unknown_owner': _UNKNOWN_OWNER,
            'io_quarantine': _UNKNOWN_OWNER['quarantine'],
            'fallback': [None] * 8,
            'began': began,
            'shared_deadline': began + plan['session_seconds'],
            'lock_fds': [None, None],
            'native_keeper': None, 'subreaper': None,
            'initial_sources': None, 'run': None,
        }
        # Retain construction resources even if no capability is returned.
        _PREFIX[1] = (None, state)

        parent._MKDIR(plan['session_directory'], 0o700)
        parent._MKDIR(plan['session_directory'] + '/retained', 0o700)
        for index, name in enumerate(('parent-queue.lock', 'science.lock')):
            _clean(_UNKNOWN_OWNER)
            _UNKNOWN_OWNER['pending'][0] = True
            state['lock_fds'][index] = parent._OPEN(
                plan['round_root'] + '/runtime/' + name,
                os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
            _UNKNOWN_OWNER['pending'][0] = False
            _FLOCK(state['lock_fds'][index], fcntl.LOCK_EX | fcntl.LOCK_NB)

        _UNKNOWN_OWNER['pending'][0] = True
        installed = installer(Path(plan['round_root']))
        state['subreaper'], state['native_keeper'] = installed
        _UNKNOWN_OWNER['pending'][0] = False
        closure.check_receivers(receivers)
        _clean(_UNKNOWN_OWNER)

        state['initial_sources'] = _source_snapshot(state)
        by_path = {row['path']: row for row in plan['source_files']}
        pins = tuple(configuration.values()) + (
            case['root_source'], case['driver_source'], case['gate_values'],
        )
        for pin in pins:
            schema.need(pin['path'] in by_path and
                        by_path[pin['path']]['sha256'] == pin['sha256'] and
                        by_path[pin['path']]['bytes'] == pin['bytes'] and
                        by_path[pin['path']]['mode'] ==
                            pin['identity']['mode'] & 0o7777,
                        'prefix input absent from parent source custody')
        state['root_bytes'] = copying.read_verified(
            case['root_source'], 262144, error_owner=errors)
        state['driver_bytes'] = copying.read_verified(
            case['driver_source'], 262144, error_owner=errors)
        original = copying.read_verified(
            configuration['original_variant'], 262144, error_owner=errors)
        schema.need(configuration['original_variant']['sha256'] == VARIANT_SHA,
                    'original variant source pin differs')
        gate_raw = copying.read_verified(
            case['gate_values'], schema.RECORD_BYTES, error_owner=errors)
        decode = closure.receiver(receivers, OBSERVER, '_decode')
        values = decode(gate_raw, schema.RECORD_BYTES)
        derivation.verify_configured_prefix(
            original, state['driver_bytes'], values)
        schema.need(all(value is not None for value in values.values()),
                    'prefix remains unconfigured; launch withheld')
        # The check above does not approve these values. Their genuine
        # admission must already be established by the authenticated bootstrap.
        state['before_pin'] = copying.write_once(
            plan['session_directory'] + '/SOURCE-BEFORE.json',
            state['initial_sources'][2], error_owner=errors)
        state['phase'] = 'READY'
        _guard(state)
        token = object()
        _PREFIX[1] = (token, state)
        return token
    except BaseException as error:
        if _UNKNOWN_OWNER['primary'][0] is None:
            _UNKNOWN_OWNER['primary'][0] = error
        _UNKNOWN_OWNER['quarantine'][0] = True
        if state is not None:
            state['phase'] = 'STOP'
        primary = _UNKNOWN_OWNER['primary'][0]
        if primary is error:
            raise
        raise primary


def _terminal(state, run):
    _guard(state)
    schema.need(run['primary'][0] is None,
                'earlier run error forbids terminal observation')
    if run['expectation']['outcome'] == 'PREFIX_RETURN':
        return domain.terminal_facts(run['domain'])
    return domain.prefix_exit1_terminal_facts(run['domain'])


def _supervise(state):
    owner, plan = state['unknown_owner'], state['plan']
    case = plan['case']
    run = None
    primary = first_cleanup = None
    old_handler = None
    alarm_installed = False
    try:
        _guard(state)
        schema.need(state['phase'] == 'READY' and state['run'] is None,
                    'prefix control already consumed')
        state['phase'] = 'CONTROL_CONSUMED'
        run = {
            'plan': case, 'unknown_owner': owner,
            'domain': None, 'process': None, 'root': None, 'terminal': None,
            'log_fds': [None, None],
            'log_close_attempted': [False, False],
            'log_close_confirmed': [False, False],
            'errors': [None] * 8, 'primary': [None],
            'acquisition_in_flight': False,
            'spawn_entered': False, 'spawn_returned': False,
            'finish_attempted': False,
            'began': _CLOCK(), 'peak_rss': 0, 'file_limits': None,
            'retained': {}, 'expectation': case['expectation'],
        }
        state['run'] = run
        before = _source_snapshot(state)
        schema.need(before == state['initial_sources'],
                    'prefix source/stage changed before launch')
        try:
            parent._STAT(case['output'], follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise schema.EpochStop('prefix output already exists')

        run['file_limits'] = tuple(parent._GETRLIMIT(resource.RLIMIT_FSIZE))
        run['domain'] = domain.create_domain(owner)
        run['launch'] = copying.write_once(
            plan['session_directory'] + '/LAUNCH.json',
            _record_bytes({
                'schema': 'h25-prefix-control-launch-v1',
                'case': case['id'], 'mode': plan['mode'],
                'generation': case['generation'],
                'launch_nonce': case['launch_nonce'],
                'parent_pid': state['pid'], 'command': case['command'],
                'cwd': case['stage_directory'], 'environment': ENV,
                'parent_file_limits': list(run['file_limits']),
                'root_seconds': case['root_seconds'],
                'address_space_bytes': case['address_space_bytes'],
                'rss_bytes': case['rss_bytes'],
                'new_session': True, 'close_fds': True, 'pass_fds': [],
                'production_completion': False,
            }), error_owner=state['errors'])

        for index, name in enumerate(('stdout.raw', 'stderr.raw')):
            _clean(owner)
            run['acquisition_in_flight'] = True
            owner['pending'][0] = True
            run['log_fds'][index] = parent._OPEN(
                plan['session_directory'] + '/' + name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
            run['acquisition_in_flight'] = False
            owner['pending'][0] = False

        setter, kind = parent._SETRLIMIT, resource.RLIMIT_AS
        limits = (case['address_space_bytes'], case['address_space_bytes'])

        def child_limit():
            setter(kind, limits)

        schema.need(parent._GETTIMER(signal.ITIMER_REAL) == (0.0, 0.0),
                    'existing timer cannot be replaced')
        old_handler = parent._GETSIGNAL(signal.SIGALRM)
        parent._SIGNAL(signal.SIGALRM, parent._alarm)
        alarm_installed = True
        deadline = min(run['began'] + case['root_seconds'],
                       state['shared_deadline'] - domain.CLEANUP_SECONDS)
        schema.need(_CLOCK() < deadline, 'no funded root/cleanup interval')
        parent._SETTIMER(signal.ITIMER_REAL,
                         max(0.000001, deadline - _CLOCK()))
        _guard(state)
        run['spawn_entered'] = True
        run['process'] = parent._POPEN(
            case['command'], cwd=case['stage_directory'], env=dict(ENV),
            stdout=run['log_fds'][0], stderr=run['log_fds'][1],
            stdin=subprocess.DEVNULL, close_fds=True, pass_fds=(),
            start_new_session=True, preexec_fn=child_limit)
        run['spawn_returned'] = True
        run['root'] = domain.adopt_popen(run['domain'], run['process'])
        while True:
            unused, current = domain.observe(run['domain'])
            run['peak_rss'] = max(run['peak_rss'],
                                  sum(row[6] for row in current))
            schema.need(run['peak_rss'] <= case['rss_bytes'],
                        'owned prefix RSS sum exceeded')
            schema.need(max(parent._STAT(
                plan['session_directory'] + '/' + name,
                follow_symlinks=False).st_size
                for name in ('stdout.raw', 'stderr.raw')) <= schema.LOG_BYTES,
                'prefix raw log bound exceeded')
            if domain.poll_owned(run['domain']) is not None:
                break
            parent._SLEEP(0.01)
    except BaseException as error:
        if owner['primary'][0] is None:
            owner['primary'][0] = error
        primary = owner['primary'][0]
        if run is not None:
            run['primary'][0] = primary
            if error is not primary:
                run['errors'][4] = error
        if (owner['pending'][0] or owner['iterator_uncertain'][0] or
                (run is not None and run['acquisition_in_flight']) or
                type(error) is MemoryError):
            owner['quarantine'][0] = True
    finally:
        if alarm_installed:
            try:
                parent._SETTIMER(signal.ITIMER_REAL, 0)
                parent._SIGNAL(signal.SIGALRM, old_handler)
            except BaseException as error:
                if owner['primary'][0] is None:
                    owner['primary'][0] = error
                if run is not None:
                    run['errors'][2] = error
                first_cleanup = error
        if run is not None and run['domain'] is not None:
            run['finish_attempted'] = True
            try:
                domain.finish_domain(run['domain'])
            except BaseException as error:
                if owner['primary'][0] is None:
                    owner['primary'][0] = error
                owner['quarantine'][0] = True
                run['errors'][3] = error
                if first_cleanup is None:
                    first_cleanup = error
        if run is not None:
            try:
                parent._close_logs(
                    run, primary if primary is not None else first_cleanup)
            except BaseException as error:
                if owner['primary'][0] is None:
                    owner['primary'][0] = error
                if first_cleanup is None:
                    first_cleanup = error
            for index in range(2):
                if (run['log_close_attempted'][index] and
                        not run['log_close_confirmed'][index]):
                    owner['quarantine'][0] = True

    if owner['primary'][0] is not None:
        state['phase'] = 'STOP'
        raise owner['primary'][0]
    schema.need(run is not None and run['spawn_entered'] is True and
                run['spawn_returned'] is True and
                run['finish_attempted'] is True and
                run['acquisition_in_flight'] is False and
                all(run['log_close_confirmed']),
                'prefix spawn/stream ownership incomplete')
    schema.need(tuple(parent._GETRLIMIT(resource.RLIMIT_FSIZE)) ==
                run['file_limits'], 'parent file limit drift')
    run['terminal'] = _terminal(state, run)
    state['phase'] = 'CONTROL_JOINED'
    return run


def _directory_identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_gid, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _census_output(state, directory, files, directories):
    """Original path-census ownership pattern; C07 remains a prerequisite."""
    _clean(state['unknown_owner'])
    schema.path(directory)
    schema.need(len(files) + len(directories) <= 9,
                'prefix output declaration bound')
    before = parent._STAT(directory, follow_symlinks=False)
    schema.need(stat.S_ISDIR(before.st_mode), 'prefix directory kind differs')
    owner = state['unknown_owner']
    iterator = None
    primary = None
    found_files, found_directories = [], []
    owner['pending'][0] = True
    try:
        iterator = parent._SCANDIR(directory)
        owner['pending'][0] = False
        for entry in iterator:
            schema.need(type(entry) is os.DirEntry,
                        'prefix native directory entry differs')
            name = entry.name
            schema.need(type(name) is str and 0 < len(name) <= 256 and
                        '/' not in name and name not in ('.', '..'),
                        'prefix directory entry name differs')
            schema.need(len(found_files) + len(found_directories) < 9,
                        'prefix output entry bound exceeded')
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISREG(info.st_mode):
                found_files.append(name)
            elif stat.S_ISDIR(info.st_mode):
                found_directories.append(name)
            else:
                raise schema.EpochStop('prefix symlink/special output refused')
    except BaseException as error:
        if owner['primary'][0] is None:
            owner['primary'][0] = error
        primary = owner['primary'][0]
        owner['quarantine'][0] = True
        owner['iterator_uncertain'][0] = True
        if primary is error:
            raise
        raise primary
    finally:
        if iterator is not None:
            owned = iterator
            iterator = None
            try:
                owned.close()
            except BaseException as error:
                if owner['primary'][0] is None:
                    owner['primary'][0] = error
                owner['quarantine'][0] = True
                owner['iterator_uncertain'][0] = True
                if state['fallback'][3] is None:
                    state['fallback'][3] = error
                if primary is None:
                    raise owner['primary'][0]
    after = parent._STAT(directory, follow_symlinks=False)
    schema.need(_directory_identity(before) == _directory_identity(after),
                'prefix directory changed during census')
    schema.need(sorted(found_files) == sorted(files) and
                sorted(found_directories) == sorted(directories),
                'prefix exact output census differs')
    return _directory_identity(after)


def _capture(state, run):
    plan, case = state['plan'], state['plan']['case']
    names = _expected_files(case['expectation'])
    occupied, raw, pins = (), {}, {}
    sources = (
        ('stdout.raw', plan['session_directory'] + '/stdout.raw',
         schema.LOG_BYTES),
        ('stderr.raw', plan['session_directory'] + '/stderr.raw',
         schema.LOG_BYTES),
    ) + tuple((name, case['output'] + '/' + name, schema.RECORD_BYTES)
              for name in names)

    # Complete exclusive copies precede semantic interpretation.
    for name, path, bound in sources:
        _guard(state)
        source = copying.inspect(path, bound, error_owner=state['errors'])
        run['retained'][name] = {'source': source}
        pair = schema.inode(source)
        schema.need(pair not in occupied, 'prefix raw occurrences alias')
        occupied += (pair,)
        copied = copying.copy_once(
            source, plan['session_directory'] + '/retained/' + name,
            occupied, error_owner=state['errors'])
        run['retained'][name]['copy'] = copied
        occupied += (schema.inode(copied),)
        raw[name] = copying.read_verified(
            copied, bound, error_owner=state['errors'])
        pins[name] = (source, copied, bound)

    output_identity = _census_output(
        state, case['output'], names, ('initial-tcb-controls',))
    scratch_identity = _census_output(
        state, case['output'] + '/initial-tcb-controls', (), ())
    decode = closure.receiver(state['receivers'], OBSERVER, '_decode')
    values = {name: decode(raw[name], schema.RECORD_BYTES) for name in names}
    closure.check_receivers(state['receivers'])
    schema.need(raw['stdout.raw'] == b'', 'prefix stdout is not empty')
    for name in ('initial-tcb.raw.json', 'initial-restoration.raw.json'):
        receipt = values[name]
        schema.need(type(receipt) is dict and
                    type(receipt.get('pid')) is int and
                    receipt['pid'] == run['root'][0],
                    'prefix initial/restoration PID differs')

    expected = case['expectation']
    binding = {'mode': plan['mode'], 'generation': case['generation'],
               'launch_nonce': case['launch_nonce']}
    if expected['outcome'] == 'PREFIX_RETURN':
        schema.need(raw['stderr.raw'] == b'',
                    'positive prefix stderr is not empty')
        check = closure.receiver(
            state['receivers'], OBSERVER, 'corroborate_positive')
        ok = check(raw['v03-input-result.raw.json'],
                   raw['v03-root-after.raw.json'],
                   raw['preflight-before.raw.json'],
                   binding, schema.RECORD_BYTES)
    else:
        check = closure.receiver(
            state['receivers'], OBSERVER, 'corroborate_complete_refusal')
        ok = check(state['driver_bytes'], state['root_bytes'],
                   case['driver_source']['path'], case['root_source']['path'],
                   raw['stderr.raw'], expected['terminal_function'],
                   expected['message'], schema.LOG_BYTES)
    schema.need(ok is True, 'complete prefix data corroboration differs')
    closure.check_receivers(state['receivers'])
    for source, copied, bound in pins.values():
        _clean(state['unknown_owner'])
        copying.verify(source, bound, error_owner=state['errors'])
        copying.verify(copied, bound, error_owner=state['errors'])
    schema.need(
        _census_output(state, case['output'], names,
                       ('initial-tcb-controls',)) == output_identity and
        _census_output(state, case['output'] + '/initial-tcb-controls',
                       (), ()) == scratch_identity,
        'prefix output changed after capture',
    )


def run_prefix(token):
    state = _state(token)
    owner = state['unknown_owner']
    try:
        run = _supervise(state)
        _capture(state, run)
        after = _source_snapshot(state)
        schema.need(after == state['initial_sources'],
                    'complete prefix source/stage custody changed')
        schema.need(_terminal(state, run) == run['terminal'],
                    'prefix owned terminal facts changed')
        case = state['plan']['case']
        schema.need(_CLOCK() - run['began'] <= case['root_seconds'],
                    'complete prefix root/capture tail exceeded bound')
        _guard(state)
        record = {
            'schema': 'h25-owned-v03-prefix-observation-v1',
            'case': case['id'], 'mode': state['plan']['mode'],
            'generation': case['generation'],
            'launch_nonce': case['launch_nonce'],
            'launch': run['launch'], 'terminal': run['terminal'],
            'source_before': state['before_pin'],
            'source_after_equals_before': True,
            'raw': run['retained'],
            'data_corroboration': 'COMPLETE_PREFIX_DATA_ONLY',
            'independent_native_receipt_replay_performed': False,
            'interval_proved_by_endpoint_equality': False,
            'parent_exit_observed_here': False,
            'enclosing_guard_must_observe_parent_exit': True,
            'production_completion': False,
            'full_c05': False, 'full_v03': False,
            'runtime_qualified': False,
        }
        result = copying.write_once(
            state['plan']['session_directory'] + '/PREFIX-OBSERVATION.json',
            _record_bytes(record), error_owner=state['errors'])
        _guard(state)
        schema.need(_CLOCK() - run['began'] <= case['root_seconds'],
                    'complete prefix result-writing tail exceeded bound')
        state['phase'] = 'CLOSED'
        # Plain file pin DATA only. No owner/domain/Popen/epoch token escapes.
        return schema.plain_copy(result)
    except BaseException as error:
        if owner['primary'][0] is None:
            owner['primary'][0] = error
        state['phase'] = 'STOP'
        if owner['pending'][0] or owner['iterator_uncertain'][0]:
            owner['quarantine'][0] = True
        primary = owner['primary'][0]
        if primary is error:
            raise
        raise primary


def stop_evidence(token):
    state = _state(token)
    run = state['run']
    summary = None if run is None else {
        'spawn_entered': run['spawn_entered'],
        'spawn_returned': run['spawn_returned'],
        'finish_attempted': run['finish_attempted'],
        'log_close_attempted': list(run['log_close_attempted']),
        'log_close_confirmed': list(run['log_close_confirmed']),
    }
    return (state['unknown_owner']['primary'], state['errors'],
            state['fallback'], summary)
