"""SOURCE ONLY: direct Group05 owned launch and typed outcome receiver.

Uses the genuine registered parent owner and shared UNKNOWN_OWNER. No process,
Popen callback, PID-only completion or child PASS report is accepted. The thirteen
native negative source ports are separately constructed; this API does not claim
that Group05 completes them or the full24 union. No gates are installed.
"""
import ast
import os
import signal
import subprocess
import resource
import time
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import group01_evidence_v1 as evidence
import parent_completion_v1 as parent
import parent_closure_v1 as original_closure
import negative_receiver_closure_v2 as closure
import negative_process_domain_v2 as domain
import typed_codec_v2 as codec
import epoch_parent_v5 as epoch
import negative_observation_v2 as observation
import fixture_parent_v2 as fixtures

CONFIGURATION = None
SOURCE_REVIEW = None
RUNTIME_CONFIGURATION = None
KERNEL_CONFIGURATION = None
REPLAY_CONFIGURATION = None
STAGE_APPROVAL = None
COMMAND_APPROVAL = None
FUNDING = None
EXECUTION_APPROVAL = None
_OWNERS = []
ROOT_SHA256 = 'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0'
NATIVE_GROUPS = ('02','03','04','07','08','09','10','11','12','13','14','15','16')
ALL_GROUPS = ('02','03','04','05','07','08','09','10','11','12','13','14','15','16')
REQUIRED_MODULES = parent.REQUIRED_MODULES + ('negative_parent_v2', 'negative_receiver_closure_v2',
                                            'negative_process_domain_v2', 'typed_codec_v2',
    'negative_observation_v2','negative_wide_codec_v2','run_controls_v1','inert_byte_v2','fixture_parent_v2','owned_root_v2')
GATES = ('SOURCE_REVIEW','RUNTIME_CONFIGURATION','KERNEL_CONFIGURATION','REPLAY_CONFIGURATION',
         'STAGE_APPROVAL','COMMAND_APPROVAL','FUNDING','EXECUTION_APPROVAL')
_OPEN, _CLOSE, _MKDIR, _STAT, _FSYNC = os.open, os.close, os.mkdir, os.stat, os.fsync
_POPEN, _CLOCK, _SLEEP = subprocess.Popen, time.monotonic, time.sleep
_GETRLIMIT, _SETRLIMIT = resource.getrlimit, resource.setrlimit
_GETTIMER, _SETTIMER, _GETSIGNAL, _SIGNAL = signal.getitimer, signal.setitimer, signal.getsignal, signal.signal
MAX_RAW = 2 * 1024 * 1024


def _gate():
    schema.exact(CONFIGURATION, ('normal', 'optimized', 'receiver_policy'))
    for pin in CONFIGURATION.values():
        schema.blob(pin, schema.RECORD_BYTES)
    values = (SOURCE_REVIEW, RUNTIME_CONFIGURATION, KERNEL_CONFIGURATION, REPLAY_CONFIGURATION,
              STAGE_APPROVAL, COMMAND_APPROVAL, FUNDING, EXECUTION_APPROVAL)
    for key, value in zip(GATES, values):
        schema.exact(value, ('admission_sha256',))
        schema.digest(value['admission_sha256'])
    return {key: value['admission_sha256'] for key, value in zip(GATES, values)}


def _owner(token):
    schema.need(type(token) is object, 'exact negative parent capability required')
    for registered, state in _OWNERS:
        if token is registered:
            return state
    raise schema.EpochStop('unregistered negative parent capability')


def _unknown(state):
    unknown = state['parent']['unknown_owner']
    domain.refresh_unknown_owner(unknown)
    schema.need(unknown['quarantine'][0] is False and unknown['pending'][0] is False and
                unknown['iterator_uncertain'][0] is False and unknown['primary'][0] is None,
                'negative parent shared ownership requires teardown')
    return unknown


def _guard(state):
    gates = _gate()
    parent._guard(state['parent'])
    _unknown(state)
    closure.check_receivers(state['receivers'])
    schema.need(gates == state['plan']['gate_digests'], 'negative gates differ from independently pinned plan')
    schema.need(state['phase'] != 'STOP' and state['parent']['phase'] == 'EXPORTED',
                'negative children require original committed parent exports')
    schema.need(CONFIGURATION[state['mode']] == state['plan_pin'] and
                CONFIGURATION['receiver_policy'] == state['receiver_pin'], 'negative configured pins drifted')
    schema.need(schema.canonical(state['plan']) == state['plan_raw'], 'negative private plan drifted')
    schema.need((_OPEN, _CLOSE, _MKDIR, _STAT, _FSYNC, _POPEN, _CLOCK, _SLEEP, _GETRLIMIT, _SETRLIMIT,
                 _GETTIMER, _SETTIMER, _GETSIGNAL, _SIGNAL) ==
                (os.open, os.close, os.mkdir, os.stat, os.fsync, subprocess.Popen, time.monotonic, time.sleep,
                 resource.getrlimit, resource.setrlimit, signal.getitimer, signal.setitimer,
                 signal.getsignal, signal.signal), 'negative actual native primitive binding changed')
    copying.verify(state['plan_pin'], schema.RECORD_BYTES, error_owner=state['parent']['errors'])
    copying.verify(state['receiver_pin'], schema.RECORD_BYTES, error_owner=state['parent']['errors'])


def _fail(state, operation, error):
    unknown = state['parent']['unknown_owner']
    if unknown['primary'][0] is None:
        unknown['primary'][0] = error
    if state['primary'][0] is None:
        state['primary'][0] = unknown['primary'][0]
    state['phase'] = 'STOP'
    # The original parent retains known errors/earlier raw files. Its own stop
    # writer refuses new acquisition once shared quarantine is present.
    parent._stop(state['parent'], operation, state['primary'][0])


def _validate_plan(plan, original):
    schema.exact(plan, ('schema','mode','parent_epoch_id','parent_plan_sha256','gate_digests',
        'source_files','stage_directory','stage_manifest','stage_directories','group05','native_groups','native','soname'))
    schema.need(plan['schema'] == 'h25-negative-parent-plan-v1' and plan['mode'] == original['plan']['mode'] and
                plan['parent_epoch_id'] == original['plan']['epoch_id'] and
                plan['parent_plan_sha256'] == original['configuration']['plan']['sha256'],
                'negative independent original parent/mode binding differs')
    schema.exact(plan['gate_digests'], GATES)
    for value in plan['gate_digests'].values():
        schema.digest(value)
    schema.need(plan['gate_digests'] == _gate(), 'negative external gate/profile not independently bound')
    schema.need(plan['native_groups'] == list(NATIVE_GROUPS), 'thirteen native obligations cannot be removed')
    schema.path(plan['stage_directory'])
    schema.blob(plan['stage_manifest'], schema.RECORD_BYTES)
    row = plan['group05']
    schema.exact(row, ('generation','launch_nonce','command','cwd','evidence_directory','child_configuration',
        'root_seconds','address_space_bytes','rss_bytes','expected_error','expected_trace_source_sha256',
        'child_source','original_root','typed_codec','error_trace','scratch_source','launch_binding','launch_artifacts'))
    schema.label(row['generation'])
    schema.digest(row['launch_nonce'])
    schema.launch(row['launch_binding'])
    schema.path(row['cwd'])
    schema.path(row['evidence_directory'])
    schema.need(row['evidence_directory'] == original['plan']['session_directory'] + '/negative-05',
                'Group05 original private session origin differs')
    schema.integer(row['root_seconds'], 1, 180)
    schema.integer(row['address_space_bytes'], 1, 1024 ** 3)
    schema.integer(row['rss_bytes'], 1, 1024 ** 3)
    for key in ('child_configuration','child_source','original_root','typed_codec','error_trace','scratch_source'):
        schema.blob(row[key], schema.RECORD_BYTES)
    schema.need(row['original_root']['sha256'] == ROOT_SHA256 and
                row['launch_binding']['root_sha256'] == ROOT_SHA256 and
                row['launch_binding']['configuration_sha256'] == row['child_configuration']['sha256'] and
                row['launch_binding']['stage_sha256'] == plan['stage_manifest']['sha256'],
                'Group05 original Root/child configuration/stage differs')
    schema.need(row['expected_trace_source_sha256'] == row['scratch_source']['sha256'],
                'Group05 error trace source is not the actual scratch source')
    expected_command = ['/usr/bin/python3.12', '-S', '-s', '-P', '-B'] + (
        ['-O'] if plan['mode'] == 'optimized' else []) + [row['child_source']['path'],
        '--configuration', row['child_configuration']['path'], row['child_configuration']['sha256']]
    schema.need(row['command'] == expected_command and
                schema.sha(schema.canonical({'argv': expected_command})) == row['launch_binding']['command_sha256'],
                'Group05 exact source-fixed command differs')
    source_by_path = {pin['path']: pin for pin in plan['source_files']}
    for key in ('child_configuration','child_source','original_root','typed_codec','error_trace','scratch_source'):
        pin = row[key]
        schema.need(pin['path'] in source_by_path and source_by_path[pin['path']]['sha256'] == pin['sha256'] and
                    source_by_path[pin['path']]['bytes'] == pin['bytes'], 'Group05 source omitted from full custody')
    schema.exact(row['launch_artifacts'], ('startup_tcb_sha256','expected_history_sha256'))
    for key,pin in row['launch_artifacts'].items():
        schema.blob(pin,schema.RECORD_BYTES)
        schema.need(pin['sha256']==row['launch_binding'][key] and pin['path'] in source_by_path and
                    source_by_path[pin['path']]['sha256']==pin['sha256'],
                    'Group05 actual startup/history launch artifact unbound')
    child_raw = copying.read_verified(row['child_configuration'],65536,error_owner=original['errors'])
    child = evidence.decode(child_raw)
    schema.exact(child, ('schema','epoch_id','mode','generation','launch_nonce','original_root',
        'typed_codec_v2','error_trace_v2','group05_scratch_v1','runtime_profile_sha256','kernel_profile_sha256'))
    schema.need(child['schema']=='h25-group05-child-config-v1' and child['epoch_id']==plan['parent_epoch_id'] and
                child['mode']==plan['mode'] and child['generation']==row['generation'] and
                child['launch_nonce']==row['launch_nonce'] and
                child['runtime_profile_sha256']==plan['gate_digests']['RUNTIME_CONFIGURATION'] and
                child['kernel_profile_sha256']==plan['gate_digests']['KERNEL_CONFIGURATION'],
                'Group05 actual child configuration is not bound to independent parent plan')
    for child_name,parent_name in (('original_root','original_root'),('typed_codec_v2','typed_codec'),
        ('error_trace_v2','error_trace'),('group05_scratch_v1','scratch_source')):
        pin = row[parent_name]
        schema.need(child[child_name]==[pin['path'],pin['sha256'],pin['bytes']],
                    'Group05 concrete child source image differs from parent source closure')
    child_source = copying.read_verified(row['child_source'],schema.RECORD_BYTES,error_owner=original['errors'])
    assignments = {node.targets[0].id:ast.literal_eval(node.value) for node in ast.parse(child_source).body
        if type(node) is ast.Assign and len(node.targets)==1 and type(node.targets[0]) is ast.Name and
        node.targets[0].id.startswith('CHILD_')}
    for child_gate,parent_gate in (('CHILD_SOURCE_REVIEW','SOURCE_REVIEW'),
        ('CHILD_RUNTIME_CONFIGURATION','RUNTIME_CONFIGURATION'),('CHILD_KERNEL_CONFIGURATION','KERNEL_CONFIGURATION'),
        ('CHILD_STAGE_APPROVAL','STAGE_APPROVAL'),('CHILD_COMMAND_APPROVAL','COMMAND_APPROVAL'),
        ('CHILD_FUNDING','FUNDING'),('CHILD_EXECUTION_APPROVAL','EXECUTION_APPROVAL')):
        schema.need(assignments.get(child_gate)==plan['gate_digests'][parent_gate],
                    'Group05 configured child source gate differs from independent parent admission')
    # Only immutable exact tuple semantics are accepted after typed decoding.
    expected = row['expected_error']
    schema.exact(expected, ('errno','message','filename','filename2'))
    schema.integer(expected['errno'], 16, 16)
    schema.text(expected['message'], 4096)
    schema.need(bool(expected['message']) and expected['filename'] is None and expected['filename2'] is None,
                'Group05 independent EBUSY errno/message oracle absent')


def make_negative_parent(original_parent, original_receivers):
    _gate()
    original = parent._state(original_parent)
    parent._guard(original)
    schema.need(len(_OWNERS) < 2 and not any(s['mode'] == original['plan']['mode'] for _, s in _OWNERS),
                'negative owner is once per mode')
    token = object()
    state = {'parent': original, 'parent_token':original_parent, 'mode': original['plan']['mode'], 'phase': 'CONSTRUCTING',
             'primary': [None], 'receivers': None, 'plan_pin': None, 'receiver_pin': None,
             'plan': None, 'plan_raw': None, 'run': None, 'observation': None,'runs':{},'native_next':0,'fixture_owner':None,'soname':None}
    _OWNERS.append((token, state))
    try:
        _unknown(state)
        errors = original['errors']
        state['plan_pin'] = schema.plain_copy(CONFIGURATION[state['mode']])
        state['receiver_pin'] = schema.plain_copy(CONFIGURATION['receiver_policy'])
        state['plan'] = evidence.decode(copying.read_verified(state['plan_pin'], schema.RECORD_BYTES, error_owner=errors))
        _validate_plan(state['plan'], original)
        _validate_native_plan(state['plan'],original)
        state['plan_raw'] = schema.canonical(state['plan'])
        policy = evidence.decode(copying.read_verified(state['receiver_pin'], schema.RECORD_BYTES, error_owner=errors))
        old_policy = evidence.decode(copying.read_verified(original['configuration']['receiver_policy'],
            schema.RECORD_BYTES, error_owner=errors))
        schema.need(type(original_receivers) is dict and set(policy) == set(REQUIRED_MODULES) == set(original_receivers),
                    'negative exact concrete receiving source inventory differs')
        for record in original_closure._packet(original['receivers'])[1]:
            name, module = record[0], record[1]
            schema.need(original_receivers[name] is module and policy[name] == old_policy[name],
                        'negative receiver must preserve every original module/object/pin')
        state['receivers'] = closure.bind_receivers(original_receivers, policy, errors)
        schema.need(closure.receiver(state['receivers'], 'negative_parent_v2', 'run_group05') is run_group05 and
                    closure.receiver(state['receivers'], 'negative_process_domain_v2', 'create_domain') is domain.create_domain,
                    'negative actual receiving functions differ')
        state['phase'] = 'READY'
        _guard(state)
        return token
    except BaseException as error:
        _fail(state, 'negative_parent_construct', error)
        raise


def run_group05(owner):
    state = _owner(owner)
    try:
        _guard(state)
        schema.need(state['phase'] == 'READY' and state['run'] is None, 'Group05 attempt already consumed')
        row = state['plan']['group05']
        joined = object()
        run = {'token': joined, 'unknown_owner': state['parent']['unknown_owner'], 'domain': None, 'process': None,
            'log_fds': [None,None], 'log_close_attempted': [False,False], 'log_close_confirmed': [False,False],
            'errors': [None] * 8, 'primary': [None], 'spawn_entered': False, 'spawn_returned': False,
            'began': _CLOCK(), 'peak_rss': 0, 'source_before': None, 'source_after': None,
            'stage_before': None, 'stage_after': None, 'terminal': None, 'raw_pins': None, 'raw': None}
        state['run'] = run
        state['phase'] = 'ATTEMPT_CONSUMED'
    except BaseException as error:
        _fail(state, 'group05_reserve', error)
        raise
    unknown, errors = run['unknown_owner'], state['parent']['errors']
    primary = None
    installed = False
    prior_handler = None
    try:
        _guard(state)
        _MKDIR(row['evidence_directory'], 0o700)
        run['source_before'] = parent._snapshot_sources(state['plan'], errors)
        run['stage_before'] = parent._stage(state['plan'], errors, state['parent'])
        custody_size = len(evidence.encode({'source_before':run['source_before'],'source_after':run['source_before'],
            'stage_before':run['stage_before'],'stage_after':run['stage_before']}))
        schema.need(custody_size + 131072 <= schema.RECORD_BYTES, 'Group05 complete custody exceeds reserved record bound before launch')
        copying.write_once(row['evidence_directory'] + '/LAUNCH.json', schema.canonical({
            'schema':'h25-group05-parent-launch-v1','parent_epoch_id':state['plan']['parent_epoch_id'],
            'mode':state['mode'],'generation':row['generation'],'launch_nonce':row['launch_nonce'],
            'command':row['command'],'cwd':row['cwd'],'environment':parent.ENV,
            'launch_binding':row['launch_binding'],'new_session':True,'close_fds':True,'pass_fds':[]}),
            error_owner=errors)
        run['domain'] = domain.create_domain(unknown)
        for index, filename in enumerate(('stdout.raw','stderr.raw')):
            _unknown(state)
            unknown['pending'][0] = True
            run['log_fds'][index] = _OPEN(row['evidence_directory'] + '/' + filename,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
            unknown['pending'][0] = False
        setter, kind, limits = _SETRLIMIT, resource.RLIMIT_AS, (row['address_space_bytes'], row['address_space_bytes'])
        def child_limit():
            setter(kind, limits)
        schema.need(_GETTIMER(signal.ITIMER_REAL) == (0.0,0.0), 'Group05 cannot replace active parent timer')
        prior_handler = _GETSIGNAL(signal.SIGALRM)
        _SIGNAL(signal.SIGALRM, parent._alarm)
        installed = True
        deadline = min(run['began'] + row['root_seconds'], state['parent']['shared_deadline'] - domain.CLEANUP_SECONDS)
        schema.need(_CLOCK() < deadline, 'Group05 no funded child and cleanup interval')
        _SETTIMER(signal.ITIMER_REAL, max(0.000001, deadline - _CLOCK()))
        run['spawn_entered'] = True
        unknown['pending'][0] = True
        run['process'] = _POPEN(row['command'], cwd=row['cwd'], env=dict(parent.ENV),
            stdin=subprocess.DEVNULL, stdout=run['log_fds'][0], stderr=run['log_fds'][1],
            close_fds=True, pass_fds=(), start_new_session=True, preexec_fn=child_limit)
        unknown['pending'][0] = False
        run['spawn_returned'] = True
        domain.adopt_popen(run['domain'], run['process'])
        while True:
            unused, current = domain.observe(run['domain'])
            run['peak_rss'] = max(run['peak_rss'], sum(item[6] for item in current))
            schema.need(run['peak_rss'] <= row['rss_bytes'], 'Group05 actual owned RSS exceeded')
            schema.need(max(_STAT(row['evidence_directory'] + '/' + name, follow_symlinks=False).st_size
                        for name in ('stdout.raw','stderr.raw')) <= MAX_RAW, 'Group05 ordinary stream bound exceeded')
            if domain.poll_owned(run['domain']) is not None:
                break
            _SLEEP(0.01)
    except BaseException as error:
        if unknown['primary'][0] is None:
            unknown['primary'][0] = error
        primary = unknown['primary'][0]
        run['primary'][0] = primary
        if unknown['pending'][0] or unknown['iterator_uncertain'][0] or type(error) is MemoryError:
            unknown['quarantine'][0] = True
        raise primary
    finally:
        first_cleanup = None
        if installed:
            try:
                _SETTIMER(signal.ITIMER_REAL, 0)
                _SIGNAL(signal.SIGALRM, prior_handler)
            except BaseException as error:
                if unknown['primary'][0] is None:
                    unknown['primary'][0] = error
                run['errors'][2] = error
                first_cleanup = error
        if run['domain'] is not None:
            try:
                domain.finish_domain(run['domain'])
            except BaseException as error:
                if unknown['primary'][0] is None:
                    unknown['primary'][0] = error
                unknown['quarantine'][0] = True
                run['errors'][3] = error
                if first_cleanup is None:
                    first_cleanup = error
        if primary is None and first_cleanup is None and unknown['quarantine'][0] is False:
            for index in range(2):
                if run['log_fds'][index] is not None:
                    try:
                        _FSYNC(run['log_fds'][index])
                    except BaseException as error:
                        if unknown['primary'][0] is None:
                            unknown['primary'][0] = error
                        run['errors'][4 + index] = error
                        if first_cleanup is None:
                            first_cleanup = error
        try:
            parent._close_logs(run, primary if primary is not None else first_cleanup)
        except BaseException as error:
            if first_cleanup is None:
                first_cleanup = error
        if primary is not None:
            _fail(state, 'group05_owned_run', primary)
        elif first_cleanup is not None:
            _fail(state, 'group05_owned_cleanup', first_cleanup)
            raise first_cleanup
    try:
        _unknown(state)
        schema.need(run['spawn_entered'] is True and run['spawn_returned'] is True and
                    all(run['log_close_confirmed']), 'Group05 parent-owned launch/streams incomplete')
        run['terminal'] = domain.terminal_facts(run['domain'])
        run['source_after'] = parent._snapshot_sources(state['plan'], errors)
        run['stage_after'] = parent._stage(state['plan'], errors, state['parent'])
        schema.need(run['source_after'] == run['source_before'] and run['stage_after'] == run['stage_before'],
                    'Group05 complete source/stage custody drift')
        run['raw_pins'] = tuple(copying.inspect(row['evidence_directory'] + '/' + name, MAX_RAW, error_owner=errors)
                                for name in ('stdout.raw','stderr.raw'))
        # Durable complete streams were parent-opened and closed before parsing.
        run['raw'] = tuple(copying.read_verified(pin, MAX_RAW, error_owner=errors) for pin in run['raw_pins'])
        custody = {'schema':'h25-group05-parent-custody-v1','source_before':run['source_before'],
            'source_after':run['source_after'],'stage_before':run['stage_before'],'stage_after':run['stage_after'],
            'terminal':run['terminal'],'raw_streams':list(run['raw_pins']), 'peak_owned_rss':run['peak_rss']}
        run['custody'] = copying.write_once(row['evidence_directory'] + '/CUSTODY.json',
            schema.canonical(custody), error_owner=errors)
        state['phase'] = 'JOINED'
        _guard(state)
        return joined
    except BaseException as error:
        _fail(state, 'group05_postjoin', error)
        raise


def _frames(raw):
    schema.need(type(raw) is bytes and 0 < len(raw) <= MAX_RAW, 'Group05 exact bounded raw bytes absent')
    cursor, result = 0, []
    while cursor < len(raw):
        schema.need(len(result) < 4 and cursor + 8 <= len(raw), 'Group05 extra or truncated raw frame')
        count = int.from_bytes(raw[cursor:cursor + 8], 'big')
        cursor += 8
        schema.need(0 < count <= 1024 * 1024 and cursor + count <= len(raw), 'Group05 typed frame bound/truncation')
        payload = raw[cursor:cursor + count]
        cursor += count
        value = codec.decode(payload)
        schema.need(codec.encode(value) == payload, 'Group05 canonical typed frame differs')
        schema.need(type(value) is tuple and len(value) == 2 and type(value[0]) is str,
                    'Group05 exact typed frame tuple required')
        result.append(value)
    schema.need(tuple(row[0] for row in result) == ('START','TARGET_RAW','CLEANUP_RAW','END'),
                'Group05 exact raw frame order/count differs')
    return tuple(row[1] for row in result)


def take_group05_observation(owner, joined):
    state = _owner(owner)
    try:
        _guard(state)
        run = state['run']
        schema.need(type(joined) is object and run is not None and joined is run['token'] and
                    state['phase'] == 'JOINED', 'Group05 requires its actual unconsumed joined owner result')
        state['phase'] = 'RECEIVER_CONSUMED'
        schema.need(run['raw'][1] == b'', 'Group05 stderr is not empty')
        start, target, cleanup, end = _frames(run['raw'][0])
        row = state['plan']['group05']
        binding = ('h25-group05-child-v1',state['plan']['parent_epoch_id'],state['mode'],row['generation'],row['launch_nonce'])
        pid = run['terminal']['root'][0]
        schema.need(codec.equal(start, ('h25-group05-start-v1',binding,pid,ROOT_SHA256,19,4096,1,3,47)),
                    'Group05 exact parent launch/start/mapping flags differ')
        schema.need(type(target) is tuple and len(target) == 10 and target[0] == 'h25-group05-target-v1',
                    'Group05 actual target envelope differs')
        unused, returned, error, identity, flags, mapping, sealing, calls, imports, maps = target
        schema.need(returned is None and type(error) is tuple and len(error) == 6 and error[0] is True,
                    'Group05 target did not return original exact OSError')
        expected = row['expected_error']
        schema.need(codec.equal(error[1:5], ((16,expected['message']),16,None,None)),
                    'Group05 original exact error args/errno/filenames differ')
        schema.need(type(identity) is tuple and len(identity) == 4 and all(type(x) is int for x in identity) and
                    identity[1] > 0 and identity[2] & 0o170000 == 0o100000 and identity[3] == 4096,
                    'Group05 actual bounded memfd identity differs')
        schema.need(codec.equal((flags,mapping,sealing,calls,imports),(19,(4096,1,3,0),(1033,47),1,())),
                    'Group05 real operation parameters/sole seal/no import interval differ')
        schema.need(type(maps) is tuple and len(maps) == 1 and type(maps[0]) is tuple and len(maps[0]) == 4 and
                    all(type(x) is int for x in maps[0]) and maps[0][0] >= 0 and maps[0][1:] == (4096,0,0),
                    'Group05 genuine single mmap audit event differs')
        trace = error[5]
        schema.need(type(trace) is dict and trace.get('complete') is True and trace.get('foreign_formatting') is False and
                    type(trace.get('objects')) is tuple and len(trace['objects']) == 1,
                    'Group05 complete original error trace absent')
        error_object = trace['objects'][0]
        schema.need(codec.equal(error_object['args'], (16,expected['message'])) and
                    error_object['cause_id'] is None and error_object['context_id'] is None and
                    type(error_object['frames']) is tuple and len(error_object['frames']) == 1,
                    'Group05 original native error chain/frame census differs')
        frame = error_object['frames'][0]
        schema.need(frame['filename'] == row['scratch_source']['path'] and frame['name'] == 'run_group05' and
                    frame['qualname'] == 'run_group05', 'Group05 original real seal callsite differs')
        # Source/hash bound above establishes the only fcntl site in this exact
        # function. A concrete parent recipe must bind its line too; included
        # below by independently deriving it from the pinned source AST.
        source = copying.read_verified(row['scratch_source'], schema.RECORD_BYTES, error_owner=state['parent']['errors'])
        tree = ast.parse(source, filename=row['scratch_source']['path'])
        sites = [node.lineno for node in ast.walk(tree) if type(node) is ast.Call and
                 type(node.func) is ast.Name and node.func.id == '_FCNTL']
        schema.need(len(sites) == 1 and type(frame['lineno']) is int and frame['lineno'] == sites[0],
                    'Group05 error did not originate at the actual sole seal callsite')
        schema.need(codec.equal(cleanup, ('h25-group05-cleanup-v1',True,True,True,True,False,False,False)),
                    'Group05 exact confirmed cleanup/uncertainty differs')
        schema.need(codec.equal(end, ('h25-group05-end-v1',binding,pid,ROOT_SHA256,1,(),maps,'RAW_COMPLETE_NO_CHILD_ORACLE')),
                    'Group05 terminal typed binding differs')
        _guard(state)
        observation = ('h25-owned-group05-observation-v1',state['plan']['parent_epoch_id'],state['mode'],
            row['generation'],row['launch_nonce'],codec.encode(tuple(run['raw_pins'])),
            run['custody']['sha256'], 'ONE_GROUP_EXPECTED_NATIVE_CONFLICT', 'FULL_NATIVE_UNION_NOT_ADMITTED')
        # Process-local observation capability retains full exact data separately.
        observation_token = object()
        state['observation'] = (observation_token, observation, codec.encode((start,target,cleanup,end)))
        state['phase'] = 'READY'
        return (observation, state['observation'][2])
    except BaseException as error:
        _fail(state, 'group05_outcome_receiver', error)
        raise


def stop_evidence(owner):
    state = _owner(owner)
    run = state['run']
    return state['primary'], None if run is None else run['primary'], None if run is None else run['errors']


NATIVE_MAX_RAW = 64 * 1024 * 1024
_EPOCH_CLAIM = epoch.ParentEpoch.claim_child

def _run_native_owned(state,group,row,run):
    joined = run['token']
    unknown, errors = run['unknown_owner'], state['parent']['errors']
    primary = None
    installed = False
    prior_handler = None
    try:
        _guard(state)
        run['source_before'] = parent._snapshot_sources(state['plan'], errors)
        run['stage_before'] = parent._stage(state['plan'], errors, state['parent'])
        custody_size = len(evidence.encode({'source_before':run['source_before'],'source_after':run['source_before'],
            'stage_before':run['stage_before'],'stage_after':run['stage_before']}))
        schema.need(custody_size + 131072 <= schema.RECORD_BYTES, 'Negative child complete custody exceeds reserved record bound before launch')
        copying.write_once(row['evidence_directory'] + '/LAUNCH.json', schema.canonical({
            'schema':'h25-negative_child-parent-launch-v1','parent_epoch_id':state['plan']['parent_epoch_id'],
            'mode':state['mode'],'generation':row['generation'],'launch_nonce':row['launch_nonce'],
            'command':row['command'],'cwd':row['cwd'],'environment':parent.ENV,
            'launch_binding':row['launch_binding'],'new_session':True,'close_fds':True,'pass_fds':[]}),
            error_owner=errors)
        run['domain'] = domain.create_domain(unknown)
        for index, filename in enumerate(('stdout.raw','stderr.raw')):
            _unknown(state)
            unknown['pending'][0] = True
            run['log_fds'][index] = _OPEN(row['evidence_directory'] + '/' + filename,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
            unknown['pending'][0] = False
        setter, kind, limits = _SETRLIMIT, resource.RLIMIT_AS, (row['address_space_bytes'], row['address_space_bytes'])
        def child_limit():
            setter(kind, limits)
        schema.need(_GETTIMER(signal.ITIMER_REAL) == (0.0,0.0), 'Negative child cannot replace active parent timer')
        prior_handler = _GETSIGNAL(signal.SIGALRM)
        _SIGNAL(signal.SIGALRM, parent._alarm)
        installed = True
        deadline = min(run['began'] + row['root_seconds'], state['parent']['shared_deadline'] - domain.CLEANUP_SECONDS)
        schema.need(_CLOCK() < deadline, 'Negative child no funded child and cleanup interval')
        _SETTIMER(signal.ITIMER_REAL, max(0.000001, deadline - _CLOCK()))
        run['spawn_entered'] = True
        unknown['pending'][0] = True
        run['process'] = _POPEN(row['command'], cwd=row['cwd'], env=dict(parent.ENV),
            stdin=subprocess.DEVNULL, stdout=run['log_fds'][0], stderr=run['log_fds'][1],
            close_fds=True, pass_fds=(), start_new_session=True, preexec_fn=child_limit)
        unknown['pending'][0] = False
        run['spawn_returned'] = True
        domain.adopt_popen(run['domain'], run['process'])
        while True:
            unused, current = domain.observe(run['domain'])
            run['peak_rss'] = max(run['peak_rss'], sum(item[6] for item in current))
            schema.need(run['peak_rss'] <= row['rss_bytes'], 'Negative child actual owned RSS exceeded')
            schema.need(max(_STAT(row['evidence_directory'] + '/' + name, follow_symlinks=False).st_size
                        for name in ('stdout.raw','stderr.raw')) <= NATIVE_MAX_RAW, 'Negative child ordinary stream bound exceeded')
            if domain.poll_owned(run['domain']) is not None:
                break
            _SLEEP(0.01)
    except BaseException as error:
        if unknown['primary'][0] is None:
            unknown['primary'][0] = error
        primary = unknown['primary'][0]
        run['primary'][0] = primary
        if unknown['pending'][0] or unknown['iterator_uncertain'][0] or type(error) is MemoryError:
            unknown['quarantine'][0] = True
        raise primary
    finally:
        first_cleanup = None
        if installed:
            try:
                _SETTIMER(signal.ITIMER_REAL, 0)
                _SIGNAL(signal.SIGALRM, prior_handler)
            except BaseException as error:
                if unknown['primary'][0] is None:
                    unknown['primary'][0] = error
                run['errors'][2] = error
                first_cleanup = error
        if run['domain'] is not None:
            try:
                domain.finish_domain(run['domain'])
            except BaseException as error:
                if unknown['primary'][0] is None:
                    unknown['primary'][0] = error
                unknown['quarantine'][0] = True
                run['errors'][3] = error
                if first_cleanup is None:
                    first_cleanup = error
        if primary is None and first_cleanup is None and unknown['quarantine'][0] is False:
            for index in range(2):
                if run['log_fds'][index] is not None:
                    try:
                        _FSYNC(run['log_fds'][index])
                    except BaseException as error:
                        if unknown['primary'][0] is None:
                            unknown['primary'][0] = error
                        run['errors'][4 + index] = error
                        if first_cleanup is None:
                            first_cleanup = error
        try:
            parent._close_logs(run, primary if primary is not None else first_cleanup)
        except BaseException as error:
            if first_cleanup is None:
                first_cleanup = error
        if primary is not None:
            _fail(state, 'negative_child_owned_run', primary)
        elif first_cleanup is not None:
            _fail(state, 'negative_child_owned_cleanup', first_cleanup)
            raise first_cleanup
    try:
        _unknown(state)
        schema.need(run['spawn_entered'] is True and run['spawn_returned'] is True and
                    all(run['log_close_confirmed']), 'Negative child parent-owned launch/streams incomplete')
        run['terminal'] = domain.terminal_facts(run['domain'])
        run['source_after'] = parent._snapshot_sources(state['plan'], errors)
        run['stage_after'] = parent._stage(state['plan'], errors, state['parent'])
        schema.need(run['source_after'] == run['source_before'] and run['stage_after'] == run['stage_before'],
                    'Negative child complete source/stage custody drift')
        run['raw_pins'] = tuple(copying.inspect(row['evidence_directory'] + '/' + name, NATIVE_MAX_RAW, error_owner=errors)
                                for name in ('stdout.raw','stderr.raw'))
        # Durable complete streams were parent-opened and closed before parsing.
        run['raw'] = tuple(copying.read_verified(pin, NATIVE_MAX_RAW, error_owner=errors) for pin in run['raw_pins'])
        custody = {'schema':'h25-negative_child-parent-custody-v1','source_before':run['source_before'],
            'source_after':run['source_after'],'stage_before':run['stage_before'],'stage_after':run['stage_after'],
            'terminal':run['terminal'],'raw_streams':list(run['raw_pins']), 'peak_owned_rss':run['peak_rss']}
        run['custody'] = copying.write_once(row['evidence_directory'] + '/CUSTODY.json',
            schema.canonical(custody), error_owner=errors)
        run['phase'] = 'JOINED'
        state['phase'] = 'NATIVE_JOINED'
        _guard(state)
        return joined
    except BaseException as error:
        _fail(state, 'negative_child_postjoin', error)
        raise



def _validate_native_row(plan,original,key,row):
    schema.exact(row,('generation','launch_nonce','command','cwd','evidence_directory','private_directory',
        'root_seconds','address_space_bytes','rss_bytes','child_source','runtime_source','control_port_source',
        'history_source','source_configuration_sha256','original_root','launch_binding','launch_artifacts','expected_subcase'))
    schema.label(row['generation']);schema.digest(row['launch_nonce'])
    schema.launch(row['launch_binding'])
    schema.integer(row['root_seconds'],1,180)
    schema.integer(row['address_space_bytes'],1,1024**3);schema.integer(row['rss_bytes'],1,1024**3)
    for name in ('cwd','evidence_directory','private_directory'):
        schema.path(row[name])
    schema.need(row['evidence_directory'] == original['plan']['session_directory']+'/negative-'+key and
                row['private_directory'] == row['evidence_directory']+'/private','negative exact private owned directories')
    source_by_path = {pin['path']:pin for pin in plan['source_files']}
    for name in ('child_source','runtime_source','control_port_source','history_source','original_root'):
        schema.blob(row[name],schema.RECORD_BYTES)
        pin = row[name]
        schema.need(pin['path'] in source_by_path and source_by_path[pin['path']] == pin,
                    'negative exact runtime/helper source omitted from prelaunch custody')
    schema.need(row['original_root']['sha256'] == ROOT_SHA256 and row['launch_binding']['root_sha256'] == ROOT_SHA256 and
                row['launch_binding']['configuration_sha256'] == row['source_configuration_sha256'] and
                row['launch_binding']['stage_sha256'] == plan['stage_manifest']['sha256'],
                'negative actual original Root/configuration/stage binding')
    command = ['/usr/bin/python3.12','-S','-s','-P','-B']+(['-O'] if plan['mode'] == 'optimized' else [])+[
        row['child_source']['path'],'--launch-context',row['evidence_directory']+'/LAUNCH-CONTEXT.json']
    schema.need(row['command'] == command and schema.sha(schema.canonical({'argv':command})) ==
                row['launch_binding']['command_sha256'],'negative fixed owned child command')
    schema.exact(row['launch_artifacts'],('startup_tcb_sha256','expected_history_sha256'))
    for name,pin in row['launch_artifacts'].items():
        schema.blob(pin,schema.RECORD_BYTES)
        schema.need(pin['sha256'] == row['launch_binding'][name] and source_by_path.get(pin['path']) == pin,
                    'negative startup/history artifact absent from original source custody')
    raw = copying.read_verified(row['child_source'],schema.RECORD_BYTES,error_owner=original['errors'])
    child = {node.targets[0].id:ast.literal_eval(node.value) for node in ast.parse(raw).body
             if type(node) is ast.Assign and len(node.targets) == 1 and type(node.targets[0]) is ast.Name and
             node.targets[0].id.startswith('CHILD_')}
    config = child['CHILD_CONFIGURATION']
    schema.need(type(config) is dict and config['schema'] == 'h25-negative-child-configuration-v2' and
                config['group'] == ('09' if key == '09-soname' else key) and config['mode'] == plan['mode'] and
                config['generation'] == row['generation'] and config['launch_nonce'] == row['launch_nonce'] and
                config['launch_context_path'] == row['evidence_directory']+'/LAUNCH-CONTEXT.json' and
                config['output_directory'] == row['evidence_directory']+'/child-output' and
                config['original_root'] == row['original_root'],'negative actual child literal data binding')
    unsigned = {name:value for name,value in config.items() if name != 'configuration_sha256'}
    schema.need(schema.sha(codec.encode(unsigned)) == config['configuration_sha256'] == row['source_configuration_sha256'],
                'negative actual source configuration is not independently bound')
    for child_name,parent_name in (('CHILD_SOURCE_REVIEW','SOURCE_REVIEW'),('CHILD_RUNTIME_CONFIGURATION','RUNTIME_CONFIGURATION'),
        ('CHILD_STAGE_APPROVAL','STAGE_APPROVAL'),('CHILD_COMMAND_APPROVAL','COMMAND_APPROVAL'),
        ('CHILD_FUNDING','FUNDING'),('CHILD_EXECUTION_APPROVAL','EXECUTION_APPROVAL')):
        schema.need(child.get(child_name) == plan['gate_digests'][parent_name],'negative child source gate binding')
    for child_name in ('CHILD_HEADER_CONFIGURATION','CHILD_NATIVE_CONFIGURATION'):
        schema.digest(child.get(child_name))
    for pin in config['sources'].values():
        schema.need(source_by_path.get(pin['path']) == pin,'negative child helper omitted from full source custody')
    schema.need(source_by_path.get(config['provider']['path']) == config['provider'],
                'negative original provider absent from full source custody')


def _validate_native_plan(plan,original):
    schema.exact(plan['native'],NATIVE_GROUPS)
    generations = set()
    for group in NATIVE_GROUPS:
        row = plan['native'][group]
        _validate_native_row(plan,original,group,row)
        schema.need(row['generation'] not in generations,'negative group generation repeated')
        generations.add(row['generation'])
    _validate_native_row(plan,original,'09-soname',plan['soname'])
    schema.need(plan['soname']['generation'] not in generations and plan['soname']['expected_subcase'] == 'soname-name',
                'negative genuine SONAME requires separate fresh child generation')


def register_fixture_claims(owner,fixture_owner):
    state = _owner(owner)
    _guard(state)
    schema.need(state['fixture_owner'] is None and not state['runs'],'fixture owner must bind before negative child attempts')
    # Registry lookup is through the source-fixed fixture module, never a caller
    # function or receipt boolean. Its claim API verifies the original parent.
    fixture_state = fixtures._state(fixture_owner)
    schema.need(fixture_state['parent'] is state['parent'],'negative fixture owner belongs to another original parent')
    state['fixture_owner'] = fixture_owner
    return None


def _new_native_run(state,group):
    joined = object()
    run = {'token':joined,'unknown_owner':state['parent']['unknown_owner'],'domain':None,'process':None,
        'log_fds':[None,None],'log_close_attempted':[False,False],'log_close_confirmed':[False,False],
        'errors':[None]*8,'primary':[None],'spawn_entered':False,'spawn_returned':False,
        'began':_CLOCK(),'peak_rss':0,'source_before':None,'source_after':None,
        'stage_before':None,'stage_after':None,'terminal':None,'raw_pins':None,'raw':None,
        'phase':'RESERVED','group':group,'claim':None,'claim_pin':None,'launch_context':None,'launch_pin':None,
        'fixture_claim':None,'observation':None}
    return run


def _issue_launch(state,group,row,run,soname=False):
    errors = state['parent']['errors']
    _unknown(state)
    _MKDIR(row['evidence_directory'],0o700)
    _MKDIR(row['private_directory'],0o700)
    if soname:
        schema.need(state['fixture_owner'] is not None,'additive SONAME requires actual owned fixture producer')
        additive = fixtures.claim_for_soname(state['fixture_owner'],state['parent_token'],row['private_directory'])
        run['claim'],run['claim_pin'] = additive['claim'],additive['claim_pin']
        run['fixture_claim'] = additive['fixture_claim']
        manifest_pin = additive['manifest']
    else:
        schema.need(epoch.ParentEpoch.claim_child is _EPOCH_CLAIM,'original epoch claim source changed')
        original = state['parent']
        epoch_state = epoch._entry_state(original['epoch'],original['authority'])
        manifest_pin = epoch_state['_manifest_file']
        run['claim'],run['claim_pin'] = _EPOCH_CLAIM(original['epoch'],original['authority'],group,row['generation'],
                                                   row['launch_binding'],row['private_directory'])
        if group in ('09','10','11'):
            schema.need(state['fixture_owner'] is not None,'negative history needs actual owned fixture producer')
            history_directory = row['evidence_directory']+'/history'
            _MKDIR(history_directory,0o700)
            run['fixture_claim'] = fixtures.claim_for_negative(state['fixture_owner'],group,history_directory)
    launch = {'schema':'h25-negative-launch-context-v2','group':'09' if soname else group,'mode':state['mode'],
        'generation':row['generation'],'launch_nonce':row['launch_nonce'],'launch_binding':row['launch_binding'],
        'manifest':manifest_pin,'claim':run['claim_pin'],'private_directory':row['private_directory'],
        'child_source':row['child_source'],'fixture_claim':run['fixture_claim'],
        'soname_claim':run['claim'] if soname else None}
    run['launch_context'] = launch
    run['launch_pin'] = copying.write_once(row['evidence_directory']+'/LAUNCH-CONTEXT.json',
        schema.canonical(launch),error_owner=errors)
    copying.verify(run['launch_pin'],schema.RECORD_BYTES,error_owner=errors)
    return None


def run_negative(owner,group):
    state = _owner(owner)
    try:
        _guard(state)
        schema.choice(group,NATIVE_GROUPS)
        schema.need(state['phase'] == 'READY' and state['native_next'] < len(NATIVE_GROUPS) and
                    group == NATIVE_GROUPS[state['native_next']] and group not in state['runs'],
                    'negative literal full thirteen order or replay')
        run = _new_native_run(state,group)
        state['runs'][group] = run
        state['native_next'] += 1
        state['phase'] = 'NATIVE_ATTEMPT_CONSUMED'
        row = state['plan']['native'][group]
        _issue_launch(state,group,row,run)
        return _run_native_owned(state,group,row,run)
    except BaseException as error:
        _fail(state,'negative_owned_child',error)
        raise


def run_soname(owner):
    state = _owner(owner)
    try:
        _guard(state)
        schema.need(state['phase'] == 'READY' and state['native_next'] == len(NATIVE_GROUPS) and state['soname'] is None,
                    'additive SONAME Root requires all original13 and one independent attempt')
        state['soname'] = _new_native_run(state,'09-soname')
        state['phase'] = 'SONAME_ATTEMPT_CONSUMED'
        _issue_launch(state,'09-soname',state['plan']['soname'],state['soname'],True)
        return _run_native_owned(state,'09-soname',state['plan']['soname'],state['soname'])
    except BaseException as error:
        _fail(state,'negative_additive_soname_child',error)
        raise


def _take_native(state,joined,soname):
    _guard(state)
    candidates = (state['soname'],) if soname else tuple(state['runs'].values())
    matches = tuple(run for run in candidates if run is not None and joined is run['token'])
    schema.need(type(joined) is object and len(matches) == 1,'negative actual owner-private joined token required')
    run = matches[0]
    schema.need(run['phase'] == 'JOINED' and state['phase'] == 'NATIVE_JOINED','negative observation replay/order')
    run['phase'] = 'RECEIVER_CONSUMED'
    row = state['plan']['soname'] if soname else state['plan']['native'][run['group']]
    copying.verify(run['launch_pin'],schema.RECORD_BYTES,error_owner=state['parent']['errors'])
    schema.need(run['raw'][1] == b'','negative raw stderr must be retained empty for acceptance')
    parsed = observation.validate_owned_negative(run['raw'][0],run['launch_context'],row,
        run['terminal'],state['receivers'],state['parent']['errors'])
    native = ('h25-owned-negative-observation-v2',state['plan']['parent_epoch_id'],state['mode'],run['group'],
        row['generation'],row['launch_nonce'],tuple(run['raw_pins']),run['launch_pin'],run['custody'],
        run['terminal'],parsed,'ONE_CHILD_EXPECTED_SOURCE_BOUND_OBSERVATION','FULL24_UNION_NOT_ADMITTED')
    encoded = codec.encode(native,NATIVE_MAX_RAW)
    run['observation'] = (native,encoded)
    run['phase'] = 'OBSERVED'
    state['phase'] = 'READY'
    _guard(state)
    return native,encoded


def take_negative_observation(owner,joined):
    state = _owner(owner)
    try:
        return _take_native(state,joined,False)
    except BaseException as error:
        _fail(state,'negative_child_observation',error)
        raise


def take_soname_observation(owner,joined):
    state = _owner(owner)
    try:
        return _take_native(state,joined,True)
    except BaseException as error:
        _fail(state,'negative_soname_observation',error)
        raise


def planned_action(owner,role):
    state = _owner(owner)
    _guard(state)
    schema.need(type(role) is str,'negative planned action exact string')
    row = state['plan']['group05'] if role == '05' else (state['plan']['soname'] if role == '09-soname' else
          state['plan']['native'].get(role))
    schema.need(type(row) is dict,'negative unknown planned action')
    return schema.plain_copy(row)


def verify_all_terminal(owner):
    state = _owner(owner)
    try:
        _guard(state)
        schema.need(state['native_next'] == 13 and tuple(state['runs']) == NATIVE_GROUPS and
                    all(run['phase'] == 'OBSERVED' for run in state['runs'].values()) and
                    state['soname'] is not None and state['soname']['phase'] == 'OBSERVED' and
                    state['run'] is not None and state['observation'] is not None,
                    'all13 native, separate05, and independent SONAME observations remain mandatory')
        errors = state['parent']['errors']
        sources = parent._snapshot_sources(state['plan'],errors)
        stage = parent._stage(state['plan'],errors,state['parent'])
        rows = []
        for run in tuple(state['runs'].values())+(state['soname'],state['run']):
            actual = domain.terminal_facts(run['domain'])
            schema.need(actual == run['terminal'] and sources == run['source_after'] and stage == run['stage_after'],
                        'negative final actual domain/current source custody differs')
            for pin in run['raw_pins']:
                copying.verify(pin,NATIVE_MAX_RAW,error_owner=errors)
            copying.verify(run['custody'],schema.RECORD_BYTES,error_owner=errors)
            if 'launch_pin' in run:
                copying.verify(run['launch_pin'],schema.RECORD_BYTES,error_owner=errors)
                copying.verify(run['claim_pin'],schema.RECORD_BYTES,error_owner=errors)
            rows.append((run.get('group','05'),run['custody']['sha256'],tuple(pin['sha256'] for pin in run['raw_pins'])))
        _guard(state)
        return ('h25-negative-all-current-terminal-v2',state['plan']['parent_epoch_id'],state['mode'],tuple(rows),
                '13_EPOCH_CHILDREN_41_PRIVATE_COPIES_PLUS_SEPARATE05_AND_SONAME',
                'FULL24_AND_FULLCALLER_REMAIN_ORCHESTRATOR_OBLIGATIONS')
    except BaseException as error:
        _fail(state,'negative_all_terminal_freshness',error)
        raise
