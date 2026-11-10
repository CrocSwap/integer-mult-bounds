"""Successor isolated Root models for exact final Root, never runtime coverage.

The original eleven code-object exports remain a separate provenance source.
Additional exact source-body copies have MODEL_SOURCE_BODY_COPY_ONLY provenance.
All kernel, loader, compiler, file, owner and driver-control primitives below are
explicit deterministic models. No live Root state or expected values are recaptured.
"""
from hashlib import sha256
from types import FunctionType, ModuleType, CodeType, SimpleNamespace
from receipt_contract_v1 import need, record, finish, validate
import loader_model_controls_v1 as legacy
from root_model_body_sources_v3 import BODY_PACKET
from restoration_contract_v1 import OLD_FIVE

SCHEMA = 'h25-field-loader-model-control-receipt-v3'
BODY_NAMES = legacy.BODY_NAMES
LEGACY_CASE_IDS = legacy.CASE_IDS
BOOTSTRAP_CASE_IDS = (
 'model-bootstrap-postload-capability-failure', 'model-bootstrap-capture-failure',
 'model-bootstrap-maps-failure', 'model-bootstrap-close-consumed-raises',
 'model-bootstrap-close-secondary-preserves-primary', 'model-bootstrap-success-close-once')
KEY_CASE_IDS = ('model-gate-positive', 'model-gate-root-foreign-samehash-key',
 'model-gate-builtin-foreign-samehash-key', 'model-gate-root-str-subclass', 'model-gate-builtin-str-subclass')
PHASE_CASE_IDS = ('model-phase-production-slot-foreign', 'model-phase-production-publication-foreign',
 'model-phase-production-ledger-foreign', 'model-phase-fixture-positive',
 'model-phase-fixture-slot-foreign', 'model-phase-fixture-publication-foreign')
SETUP_CASE_IDS = ('model-setup-after-original-five-restoration',
 'model-setup-original-five-failure-stops', 'model-setup-restoration-failure-stops')
CASE_IDS = LEGACY_CASE_IDS + BOOTSTRAP_CASE_IDS + KEY_CASE_IDS + PHASE_CASE_IDS + SETUP_CASE_IDS
NORMAL_CASE_COUNT = 53
OPTIMIZED_CASE_COUNT = 53
ORIGINAL_EXPORT_CASE_COUNT = 33
ADDITIONAL_CASE_COUNT = 20
PAYLOAD = b'field-model-payload\n'
FIELDS = ('__code__', '__globals__', '__builtins__', '__defaults__', '__kwdefaults__', '__closure__', '__dict__')

class ModelFault(Exception):
    pass



def _namespace(bundle, scenario):
    need(type(bundle) is tuple and len(bundle) == 4 and bundle[0] == 'h25-root-loader-model-sources-v1', 'model source packet')
    _, bodies, types0, constants0 = bundle
    need(type(bodies) is tuple and tuple(row[0] for row in bodies) == BODY_NAMES, 'model exact original body inventory')
    need(type(types0) is tuple and len(types0) == 2 and all(type(x) is type for x in types0), 'model original record types')
    need(type(constants0) is tuple and all(type(row) is tuple and len(row) == 2 for row in constants0), 'model constants')
    namespace = {'__builtins__': __builtins__, '_TYPE': type, '_LEN': len,
                 '_BASE_ERROR': BaseException, '_SHA256': sha256, '_need': need,
                 'ModuleType': ModuleType, 'FunctionType': FunctionType,
                 '_FieldSpec': types0[0], '_SealedImage': types0[1]}
    namespace.update(dict(constants0))
    for name, code, defaults in bodies:
        need(type(code) is CodeType and code.co_freevars == () and (defaults is None or type(defaults) is tuple and all(value is None or type(value) in (int, str, bool) for value in defaults)),
             'model original body exact closure/defaults')
        namespace[name] = FunctionType(code, namespace, name, defaults)
    for name, code, defaults in BODY_PACKET:
        need(type(code) is CodeType and code.co_freevars == () and defaults is None, 'copied model body shape')
        namespace[name] = FunctionType(code, namespace, name, defaults)
    ledger = {'phase': 'REGISTERED', 'register_attempts': 1, 'bind_attempts': 0,
              'image_attempts': 0, 'load_attempts': 0, 'close_calls': 0,
              'cleanup_failures': [], 'events': [], 'primitives': ((), object(), FunctionType),
              'token': object(), 'image': None, 'image_identity': None, 'native': None,
              'entries': None, 'bootstrap_binding': None, 'elf': None,
              'copy_write_calls': 0, 'copy_bytes': 0, 'preload_cleanup_fds': []}
    namespace.update(_FIELD_LEDGER=ledger, _FIELD_SLOT=['REGISTERED', None],
                     _FIELD_PUBLICATION=['REGISTERED', None], _FIELD_IMAGES=[],
                     _FIELD_IMPORT_HISTORY=[], _FIELD_LOAD_HISTORY=[], _ROOT_MODULES={})
    config = {'elf_policy': {}, 'initial_native_origins': (),
              'native_import_history_before_bind': (), 'native_origins_before_bind': (),
              'source_closure': (('/model/header.h', '1' * 64, 17),),
              'compiler_dependencies': {'/model/header.h': {'sha256': '1' * 64, 'bytes': 17}},
              'build_commands': {'production': ('model-compiler-not-invoked',)},
              'map_files': (('model-map', '/model/system.so', '2' * 64, 23),),
              'preordinary_tcb_files': (('/model/system.so', '2' * 64, 23),),
              'preordinary_hashlib_origin': '/model/hashlib.so'}
    for key, value in (('source_closure_sha256', config['source_closure']),
                       ('compiler_closure_sha256', config['compiler_dependencies']),
                       ('link_profile_sha256', config['build_commands'])):
        config['elf_policy'][key] = sha256(repr(namespace['_field_freeze'](value)).encode('utf-8')).hexdigest()
    config['elf_policy']['expected_exports'] = ('PyInit__h25_dict_probe', 'PyInit__h25_field_service_v1')
    trace, files, open_fds = [], {10: bytearray(PAYLOAD), 20: bytearray()}, set()
    state = {'read_offset': 0, 'source_stats': 0, 'seals': 0, 'loader_calls': 0,
             'reused': False, 'model_native_close_calls': 0, 'model_native_bind_calls': 0,
             'bootstrap_load_calls': 0, 'bootstrap_close_calls': 0, 'bootstrap_active': False,
             'capability_calls': 0, 'preordinary_tcb_calls': 0}
    def opened(path, flags):
        trace.append('open-source' if path == '/fixture/production.so' else 'open-alias')
        fd = 10 if path == '/fixture/production.so' else 30
        need(path in ('/fixture/production.so', '/proc/self/fd/20'), 'model unexpected open')
        open_fds.add(fd)
        return fd
    def memfd(name, flags):
        trace.append('memfd')
        if scenario == 'model-memfd-unsupported': raise OSError('unsupported-memfd-policy')
        open_fds.add(20)
        return 20
    def fstat(fd):
        source = fd == 10
        if source: state['source_stats'] += 1
        inode = 101 if source else 202
        if fd == 30 and scenario == 'model-alias-inode-mismatch': inode = 303
        if state['reused'] and fd == 20: inode = 404
        mtime = 2 if source and scenario == 'model-copy-source-drift' and state['source_stats'] > 1 else 1
        return SimpleNamespace(st_dev=7, st_ino=inode, st_size=len(files[10 if source else 20]),
             st_mode=0o100711, st_mtime_ns=mtime, st_ctime_ns=1)
    def read(fd, count):
        need(fd == 10, 'model unexpected read FD')
        if scenario == 'model-copy-early-eof': return b''
        if scenario == 'model-copy-short-reads': count = min(count, 2)
        offset = state['read_offset']
        block = bytes(files[10][offset:offset + count]); state['read_offset'] += len(block)
        return block
    def write(fd, block):
        need(fd == 20, 'model unexpected write FD')
        if scenario in ('model-copy-zero-write', 'model-cleanup-error-preserves-primary'): return 0
        if scenario == 'model-copy-bool-write': return True
        if scenario == 'model-copy-excess-write': return len(block) + 1
        count = min(2, len(block)) if scenario == 'model-copy-short-writes' else len(block)
        files[20].extend(block[:count]); return count
    def pread(fd, count, offset):
        need(fd == 20, 'model unexpected pread FD')
        data = bytes(files[20])
        if scenario == 'model-seal-readback-mismatch': data = b'X' + data[1:]
        return data[offset:offset + count]
    def fcntl(fd, command, *args):
        need(fd in (20, 30), 'model unexpected seal FD')
        if command == 1033:
            trace.append('seal')
            if scenario == 'model-writable-map-conflict': raise BlockingIOError('writable-map-conflict')
            state['seals'] = 15 if scenario == 'model-seal-missing' else 63
            return 0
        need(command == 1034, 'model unexpected fcntl command')
        return state['seals']
    def close(fd):
        trace.append('close-' + str(fd))
        if scenario == 'model-cleanup-error-preserves-primary': raise OSError('cleanup-stop')
        open_fds.discard(fd)
    class ModelEntry:
        def __init__(self, owner, name):
            self.__self__, self.__name__ = owner, name
        def __call__(self, *args):
            name = self.__name__
            if name == '_field_abi': return (1, 7, 0x030C03F0, 8, 2)
            if name == '_field_status': return (1, 4 if scenario == 'model-status-failure-retains' else 1, 0, 1, 0)
            if name == '_bind_fields':
                state['model_native_bind_calls'] += 1
                if scenario in ('model-partial-bind-failure-retains', 'model-partial-bind-cleanup-failure-retains'):
                    raise ModelFault('bind-stop')
            if name == '_close_fields':
                state['model_native_close_calls'] += 1
                if scenario == 'model-partial-bind-cleanup-failure-retains': raise ModelFault('cleanup-bind-stop')
            return None
    def create(spec):
        trace.append('create-dynamic-model'); state['loader_calls'] += 1
        if scenario == 'model-load-failure-retains': raise ModelFault('create-stop')
        if scenario == 'model-loader-return-wrong-type-retains': return object()
        module = ModuleType('_h25_field_service_v1')
        for name in ('field_id', '_bind_fields', '_close_fields', '_field_status', '_field_abi', '_new_field_context'):
            module.__dict__[name] = ModelEntry(module, name)
        return module
    def execute(module):
        trace.append('exec-dynamic-model')
        if scenario == 'model-module-exec-failure-retains': raise ModelFault('exec-stop')
    def mark(name, result):
        def operation(*args): trace.append(name); return result
        return operation
    binding_owner = object()
    def bootstrap_load(*args):
        trace.append('ordinary-load-model')
        need(not state['bootstrap_active'], 'model bootstrap owner duplicate load')
        state['bootstrap_load_calls'] += 1
        state['bootstrap_active'] = True
        return binding_owner
    def bootstrap_close(binding):
        trace.append('bootstrap-close')
        state['bootstrap_close_calls'] += 1
        need(binding is binding_owner and state['bootstrap_active'], 'model bootstrap close duplicate/wrong owner')
        state['bootstrap_active'] = False  # genuine-provider-shaped consume before raised error
        if scenario in ('model-bootstrap-close-consumed-raises', 'model-bootstrap-close-secondary-preserves-primary'):
            raise ModelFault('bootstrap-close-stop')
    class Binding:
        close = staticmethod(bootstrap_close)
    def maps():
        trace.append('maps')
        if scenario == 'model-bootstrap-maps-failure': raise ModelFault('maps-stop')
        return {}
    def capture(binding):
        trace.append('bootstrap-capture')
        need(binding is binding_owner and state['bootstrap_active'], 'model capture active owner')
        if scenario in ('model-bootstrap-capture-failure', 'model-bootstrap-close-secondary-preserves-primary'):
            raise ModelFault('capture-stop')
        return object(), maps, mark('symbol-snapshot', {})
    provider = SimpleNamespace(ProbeBinding=Binding, capture_field_loader=capture)
    provider_state = (None, provider, None, None, None, None,
                      {'_FIELD_SYSTEM_HEADER_FILES': config['source_closure']})
    def capability_state(cap):
        state['capability_calls'] += 1
        trace.append('capability-' + str(state['capability_calls']))
        if scenario == 'model-bootstrap-postload-capability-failure' and state['capability_calls'] == 3:
            raise ModelFault('postload-capability-stop')
        return provider_state
    def tcb_verify(root, api, files, origin):
        trace.append('preordinary-tcb-model')
        state['preordinary_tcb_calls'] += 1
        need(files == config['preordinary_tcb_files'] and origin == config['preordinary_hashlib_origin'],
             'model literal preordinary TCB inventory')
        return {'schema': 'h25-initial-native-tcb-v1', 'status': 'MATCHED_DECLARED_INITIAL_NATIVE_FILES',
                'declared_file_count': 1, 'probe_private_abi_access': False, 'reusable_pass': False}
    parsed = {'sha256': sha256(PAYLOAD).hexdigest(), 'bytes': len(PAYLOAD)}
    namespace.update(_OPEN=opened, _MEMFD=memfd, _FSTAT=fstat, _READ=read, _WRITE=write,
       _PREAD=pread, _FCNTL=fcntl, _CLOSE=close, _CREATE_DYNAMIC=create, _EXEC_DYNAMIC=execute,
       BuiltinFunctionType=ModelEntry, _GETDLOPENFLAGS=lambda: 2, _GETTRACE=lambda: None,
       _GETPROFILE=lambda: None, _SYSCONF=lambda name: 4096 if name == 30 else None,
       _check_root=mark('check-root-model', None), _capability_state=capability_state,
       _field_config=lambda: config, _field_native_origins=lambda: config['native_origins_before_bind'],
       _field_admit_builds=lambda path, expected, receipt: len(PAYLOAD),
       _hash_regular=lambda path, limit, materialize: (sha256(PAYLOAD).hexdigest(), len(PAYLOAD), PAYLOAD if materialize else None),
       _field_runtime_policy=lambda *args: {}, _field_map_custody=lambda *args: None,
       load_probe=bootstrap_load, _ROOT_MODULE=ModuleType('_model_root_only'),
       _ROOT_METADATA={'source_sha256': '3' * 64},
       capture_api=lambda: (mark('preordinary-api0-model', '3' * 64),),
       _FIELD_TCB_HELPER=[(object(), mark('tcb-gate-model', None), tcb_verify)],
       _FIELD_HELPER=[(object(), lambda: None, (mark('static-admit-model', parsed),
          mark('map-admit-model', {}), mark('requests-model', ()), mark('provider-admit-model', {}),
          mark('preordinary-import-model', {'schema': 'h25-bootstrap-import-profile-v1',
               'ordinary_inventory': 'PREDICTED_NOT_OBSERVED'})))])
    return namespace, config, state, trace, open_fds



def _error(operation):
    try:
        operation()
    except BaseException as exc:
        return [type(exc).__name__, str(exc)]
    return None


def _key_case(env, name):
    counters = {'equal_calls': 0, 'target_calls': 0}
    root_namespace = {'sentinel_root': object()}
    builtin_model = SimpleNamespace(sentinel_builtin=object())
    def target():
        counters['target_calls'] += 1
    env.update(_FIELD_NAMES=FIELDS, _ROOT_NAMESPACE=root_namespace, builtins=builtin_model,
               _ROOT_CELL=(), BootstrapCapability=type('ModelBootstrapCapability', (), {}),
               _NativeSpec=type('ModelNativeSpec', (), {}))
    gate = env['_field_source_gate'](target)
    same_hash = None
    if name != 'model-gate-positive':
        owner = root_namespace if '-root-' in name else builtin_model.__dict__
        key = 'sentinel_root' if '-root-' in name else 'sentinel_builtin'
        key_hash = hash(key)
        class ForeignKey:
            def __hash__(self): return key_hash
            def __eq__(self, other):
                counters['equal_calls'] += 1
                raise ModelFault('foreign-key-equality-executed')
        class ForeignStr(str):
            __hash__ = str.__hash__
            def __eq__(self, other):
                counters['equal_calls'] += 1
                raise ModelFault('foreign-key-equality-executed')
        foreign = ForeignStr(key) if name.endswith('-str-subclass') else ForeignKey()
        original = owner.pop(key)
        need(not owner, 'model foreign insertion must not compare with another key')
        owner[foreign] = original
        same_hash = hash(foreign) == key_hash
        need(counters['equal_calls'] == 0 and same_hash is True and len(owner) == 1,
             'model same-size same-hash precondition')
    error = _error(gate)
    return {'error': error, 'foreign_equality_calls': counters['equal_calls'],
            'target_calls': counters['target_calls'], 'same_hash_precondition': same_hash,
            'real_syscalls': 0, 'real_native_calls': 0}, {
            'modeled_root_key_count': len(root_namespace), 'modeled_builtin_key_count': len(builtin_model.__dict__),
            'proof_class': 'MODEL_SOURCE_BODY_COPY_ONLY', 'live_root_or_builtins_mutated': False}


def _phase_case(env, name):
    equality = [0]
    class ForeignPhase:
        def __eq__(self, other):
            equality[0] += 1
            raise ModelFault('foreign-phase-equality-executed')
    if '-production-' in name:
        if '-slot-' in name: env['_FIELD_SLOT'][0] = ForeignPhase()
        elif '-publication-' in name: env['_FIELD_PUBLICATION'][0] = ForeignPhase()
        else: env['_FIELD_LEDGER']['phase'] = ForeignPhase()
        operation = env['_field_consistent']
        provenance = 'ORIGINAL_CODE_OBJECT_EXPORT_MODEL_ONLY'
    else:
        env.update(_ID=id, _FIELD_NAMES=FIELDS,
                   _new_field_fixture=lambda: (object(), (None,) * 5),
                   _field_source_gate=lambda function: function,
                   _field_admission_record=lambda function: (function, (), ()))
        transport = env['_new_field_fixture_transport']()
        if '-slot-' in name: transport[0][0] = ForeignPhase()
        elif '-publication-' in name: transport[-1][0] = ForeignPhase()
        operation = transport[4]  # actual copied nested receipt/consistent code
        provenance = 'MODEL_SOURCE_BODY_COPY_ONLY'
    error = _error(operation)
    return {'error': error, 'foreign_equality_calls': equality[0],
            'real_syscalls': 0, 'real_native_calls': 0}, {
            'proof_class': provenance, 'fixture_admission_and_native_entries_are_models': True,
            'production_state_mutated': False}


def _setup_case(env, name):
    """Copied entry + copied driver TCB + copied registration; primitive stubs.

    The modeled original-five callback is not an execution of the original
    five controls. This tests the copied orchestration's fail-closed order and
    does not prove actual driver top-level placement or original-five behavior.
    """
    trace, counters = [], {'positive_calls': 0, 'setup_calls': 0, 'cold_calls': 0,
                            'old_calls': [], 'restored': False}
    root_digest, driver_digest = '3' * 64, '4' * 64
    helper_digest, controls_digest = '5' * 64, '6' * 64
    expected_files = (('/model/system.so', '7' * 64, 19),)
    sys_model = SimpleNamespace(argv=['model-python', '--root-sha256', root_digest,
        '--provider', '/model/integration/provider.py', '8' * 64,
        '--driver', '/model/integration/driver.py', driver_digest,
        '--integration', '/model/integration', '--', '--output', '/model-output'],
        path=['/model/start'], modules={})
    def api0():
        trace.append('original-api0-model')
        return root_digest
    api = (api0,)
    def verify(root, supplied_api, files, origin):
        need(supplied_api is api and files is expected_files and origin == '/model/hashlib.so',
             'model initial literal expected values not recaptured')
        counters['positive_calls'] += 1
        if counters['positive_calls'] == 1:
            trace.append('initial-positive-model')
        else:
            trace.append('post-five-restoration-model')
            need(counters['old_calls'] == list(OLD_FIVE), 'model restoration must follow five controls')
            if name == 'model-setup-restoration-failure-stops':
                raise ModelFault('restoration-stop')
            counters['restored'] = True
        return {'schema': 'h25-initial-native-tcb-v1', 'status': 'MATCHED_DECLARED_INITIAL_NATIVE_FILES',
                'declared_file_count': 1, 'probe_private_abi_access': False}
    def old_controls(helper, root, supplied_api, files, origin, directory):
        need(supplied_api is api and files is expected_files and origin == '/model/hashlib.so',
             'model original controls literal input identity')
        for case in OLD_FIVE:
            counters['old_calls'].append(case)
            trace.append('old-control-model:' + case)
            if name == 'model-setup-original-five-failure-stops' and len(counters['old_calls']) == 3:
                raise ModelFault('original-control-stop')
        return {'schema': 'h25-native-tcb-controls-v1', 'expected_records': 5,
                'records': [{'case': case} for case in OLD_FIVE],
                'scientific_calls': 0, 'probe_native_imports': 0}
    def model_hash(path, limit, materialize):
        if path.endswith('/native_tcb_v1.py'): return helper_digest, 12, b'helper-model'
        if path.endswith('/native_tcb_controls_v1.py'): return controls_digest, 14, b'controls-model'
        need(path == '/model/integration/driver.py', 'model setup unknown input')
        return driver_digest, 12, b'driver-model'
    def model_compile(source, filename, mode, **kwargs):
        need(mode == 'exec' and kwargs.get('dont_inherit') is True, 'model compile invocation shape')
        return source  # no compilation; fixed token dispatch only
    def support_exec(token, namespace):
        if token == b'helper-model': namespace['verify_native_tcb'] = verify
        elif token == b'controls-model': namespace['run_controls'] = old_controls
        else: raise ModelFault('unknown-model-support-token')
    root_model = SimpleNamespace(ModuleType=ModuleType,
        builtins=SimpleNamespace(__dict__=__builtins__), _hash_regular=model_hash,
        _COMPILE=model_compile, _EXEC=support_exec, _OPTIMIZE=0, sys=sys_model,
        posix=SimpleNamespace(mkdir=lambda path, flags: trace.append('mkdir-model:' + path)))
    driver_namespace = {'__builtins__': __builtins__, '__file__': '/model/integration/driver.py',
        '_CAPTURED_BOOTSTRAP_ROOT': root_model, '_CAPTURED_BOOTSTRAP_API': api,
        'NATIVE_TCB_CANDIDATE_PROFILE_ADMISSION_SHA256': '9' * 64,
        'EXPECTED_BOOTSTRAP_ROOT_SHA256': root_digest, '_INITIAL_ROOT_IDENTITY': root_digest,
        'NATIVE_TCB_HELPER_SHA256': helper_digest, 'NATIVE_TCB_CONTROLS_SHA256': controls_digest,
        'NATIVE_TCB_EXPECTED_FILES': expected_files, 'NATIVE_TCB_EXPECTED_HASHLIB_ORIGIN': '/model/hashlib.so'}
    initial_body = next(code for body_name, code, defaults in BODY_PACKET if body_name == '_initial_native_tcb')
    initial = FunctionType(initial_body, driver_namespace, '_initial_native_tcb')
    def install(integration):
        counters['setup_calls'] += 1
        trace.append('field-configuration-model')
        need(counters['restored'] is True and counters['old_calls'] == list(OLD_FIVE),
             'model setup attempted before original five/restoration')
    def execute_driver(token, namespace):
        need(token == b'driver-model' and counters['setup_calls'] == 0,
             'model entry performed field setup before driver initial controls')
        initial()
        counters['cold_calls'] += 1
        trace.append('cold-capture-model')
        fields = tuple((field, FunctionType.__dict__[field].__get__) for field in FIELDS)
        env['_register_fields'](fields, id, FunctionType)
    env['_FIELD_LEDGER']['register_attempts'] = 0
    env['_field_phase']('UNBOUND')
    env.update(sys=sys_model, builtins=SimpleNamespace(__dict__=__builtins__),
        _FIELD_INTEGRATION=[], _FIELD_TRANSPORT_CELL=[object()], _FIELD_CONTROL_CELL=[object()],
        _ID=id, _FIELD_NAMES=FIELDS, _ROOT_MODULE=root_model, _INITIAL_PATH=tuple(sys_model.path),
        _MAX_SOURCE=262144, _OPTIMIZE=0, _hash_regular=model_hash, _COMPILE=model_compile,
        _EXEC=execute_driver, initialize=lambda digest: trace.append('initialize-model'),
        admit_provider=lambda path, digest: object(), capture_api=lambda: api,
        preflight=lambda cap: trace.append('ordinary-preflight-model'),
        _check_root=lambda: trace.append('check-root-model'), _field_install_configuration=install)
    error = _error(env['_entry'])
    if counters['setup_calls']:
        need(trace.index('post-five-restoration-model') < trace.index('cold-capture-model') <
             trace.index('field-configuration-model'), 'model post-five setup sequence')
    observed = {'error': error, 'modeled_original_control_ids': list(counters['old_calls']),
                'restored': counters['restored'], 'cold_capture_calls': counters['cold_calls'],
                'field_setup_calls': counters['setup_calls'], 'real_syscalls': 0, 'real_native_calls': 0}
    details = {'proof_class': 'MODEL_SOURCE_BODY_COPY_ONLY', 'model_call_trace': trace,
               'original_five_controls_actually_executed': False, 'actual_driver_placement_proven': False,
               'literal_expected_tuple_identity_checked': True, 'support_compiler_invoked': False}
    return observed, details


def expectations():
    expected = legacy.expectations()
    errors = {
      'model-bootstrap-postload-capability-failure': ['ModelFault', 'postload-capability-stop'],
      'model-bootstrap-capture-failure': ['ModelFault', 'capture-stop'],
      'model-bootstrap-maps-failure': ['ModelFault', 'maps-stop'],
      'model-bootstrap-close-consumed-raises': ['ModelFault', 'bootstrap-close-stop'],
      'model-bootstrap-close-secondary-preserves-primary': ['ModelFault', 'capture-stop']}
    for name in BOOTSTRAP_CASE_IDS:
        positive = name == 'model-bootstrap-success-close-once'
        expected[name] = {'error': errors.get(name), 'bootstrap_load_calls': 1, 'bootstrap_close_calls': 1,
            'bootstrap_owner_active': False, 'bootstrap_ledger_owner_cleared': True,
            'loader_calls': 1 if positive else 0, 'retained_image': positive,
            'cleanup_failures': [['bootstrap_provider_close', 'ModelFault']] if
                name == 'model-bootstrap-close-secondary-preserves-primary' else [],
            'real_syscalls': 0, 'real_native_calls': 0}
    for name in KEY_CASE_IDS:
        positive = name == 'model-gate-positive'
        expected[name] = {'error': None if positive else ['RuntimeError', 'Field caller namespace contains a foreign key'],
            'foreign_equality_calls': 0, 'target_calls': 1 if positive else 0,
            'same_hash_precondition': None if positive else True, 'real_syscalls': 0, 'real_native_calls': 0}
    for name in PHASE_CASE_IDS:
        expected[name] = {'error': None if name == 'model-phase-fixture-positive' else
            ['RuntimeError', 'Field slot phase/ledger differs' if '-production-' in name else
             'Fixture slot/publication custody differs'], 'foreign_equality_calls': 0,
            'real_syscalls': 0, 'real_native_calls': 0}
    for name in SETUP_CASE_IDS:
        positive = name == 'model-setup-after-original-five-restoration'
        early = name == 'model-setup-original-five-failure-stops'
        expected[name] = {'error': None if positive else ['ModelFault',
            'original-control-stop' if early else 'restoration-stop'],
            'modeled_original_control_ids': list(OLD_FIVE[:3] if early else OLD_FIVE),
            'restored': positive, 'cold_capture_calls': 1 if positive else 0,
            'field_setup_calls': 1 if positive else 0, 'real_syscalls': 0, 'real_native_calls': 0}
    need(tuple(expected) == CASE_IDS and len(expected) == 53, 'model v3 literal ordered inventory')
    return expected


def run_loader_model_controls(bundle, mode):
    expected, rows = expectations(), []
    for name in CASE_IDS:
        env, config, state, trace, open_fds = _namespace(bundle, name)
        if name in KEY_CASE_IDS:
            observed, details = _key_case(env, name)
        elif name in PHASE_CASE_IDS:
            observed, details = _phase_case(env, name)
        elif name in SETUP_CASE_IDS:
            observed, details = _setup_case(env, name)
        else:
            error = None
            try:
                if name.startswith('model-history-'):
                    if name == 'model-history-prior-procfd':
                        config['native_import_history_before_bind'] = (('old', '/proc/self/fd/20'),)
                        env['_FIELD_IMPORT_HISTORY'][:] = config['native_import_history_before_bind']
                    elif name == 'model-history-reserved-name':
                        config['initial_native_origins'] = (('_h25_field_service_v1', '/fixture/old.so'),)
                    elif name == 'model-history-retained-cache-no-sysmodules':
                        env['_FIELD_LOAD_HISTORY'].append(('_h25_field_service_v1', '/proc/self/fd/20'))
                    elif name == 'model-history-import-drift':
                        env['_FIELD_IMPORT_HISTORY'].append(('unexpected', '/fixture/x.so'))
                    env['_field_admit_history']('/fixture/production.so')
                elif name in LEGACY_CASE_IDS[25:] or name in BOOTSTRAP_CASE_IDS:
                    env['_bind_field_service'](object(), '/fixture/production.so', sha256(PAYLOAD).hexdigest(), {})
                    if name in ('model-success-close-retains', 'model-bootstrap-success-close-once'):
                        env['_close_field_service'](); env['_close_field_service']()
                    elif name == 'model-duplicate-bind':
                        env['_bind_field_service'](object(), '/fixture/production.so', sha256(PAYLOAD).hexdigest(), {})
                else:
                    digest = '0' * 64 if name == 'model-copy-hash-mismatch' else sha256(PAYLOAD).hexdigest()
                    image = env['_field_new_image']('/fixture/production.so', digest, len(PAYLOAD))
                    if name == 'model-fd-reuse-detected': state['reused'] = True
                    elif name == 'model-owner-mismatch': image.owner = object()
                    elif name == 'model-serial-mismatch': image.serial = 2
                    elif name == 'model-spec-mismatch': image.spec = env['_FieldSpec'](('_h25_field_service_v1', '/proc/self/fd/20'))
                    elif name == 'model-duplicate-image': env['_field_new_image']('/fixture/production.so', digest, len(PAYLOAD))
                    env['_field_check_image'](image)
            except BaseException as exc:
                error = [type(exc).__name__, str(exc)]
            images = env['_FIELD_IMAGES']
            retained = bool(images) and images[0].retain is True and 20 in open_fds
            observed = {'error': error, 'loader_calls': state['loader_calls'], 'retained_image': retained,
                        'real_syscalls': 0, 'real_native_calls': 0}
            if name in BOOTSTRAP_CASE_IDS:
                observed.update(bootstrap_load_calls=state['bootstrap_load_calls'],
                    bootstrap_close_calls=state['bootstrap_close_calls'],
                    bootstrap_owner_active=state['bootstrap_active'],
                    bootstrap_ledger_owner_cleared=env['_FIELD_LEDGER']['bootstrap_binding'] is None,
                    cleanup_failures=[list(row) for row in env['_FIELD_LEDGER']['cleanup_failures']])
            if state['bootstrap_load_calls']:
                need(trace.index('preordinary-import-model') < trace.index('preordinary-api0-model') <
                     trace.index('preordinary-tcb-model') < trace.index('ordinary-load-model'),
                     'model copied preordinary TCB proof precedes ordinary load')
                need(state['bootstrap_close_calls'] == 1 and not state['bootstrap_active'] and
                     env['_FIELD_LEDGER']['bootstrap_binding'] is None,
                     'model bootstrap returned owner consumed exactly once without leak')
            if state['loader_calls']:
                need(trace.index('maps') < trace.index('map-admit-model') < trace.index('requests-model') <
                     trace.index('symbol-snapshot') < trace.index('provider-admit-model') <
                     trace.index('bootstrap-close') < trace.index('memfd') < trace.index('create-dynamic-model'),
                     'model two-phase/pre-loader ordering')
            if name == 'model-cleanup-error-preserves-primary':
                need(env['_FIELD_LEDGER']['cleanup_failures'] == [('copy_close', 'OSError'), ('copy_close', 'OSError')],
                     'model copy cleanup evidence')
            if name == 'model-partial-bind-cleanup-failure-retains':
                need(env['_FIELD_LEDGER']['cleanup_failures'] == [('partial_native_close', 'ModelFault')],
                     'model bind cleanup evidence')
            if name in ('model-success-close-retains', 'model-bootstrap-success-close-once'):
                need(state['model_native_close_calls'] == 1 and env['_FIELD_SLOT'][0] == 'CLOSED' and
                     images[0].module is env['_FIELD_LEDGER']['native'], 'model idempotent logical close retention')
            details = {'model_call_trace': trace, 'open_model_descriptors': sorted(open_fds),
                'cleanup_failures': env['_FIELD_LEDGER']['cleanup_failures'],
                'events': env['_FIELD_LEDGER']['events'], 'phase': env['_FIELD_SLOT'][0],
                'proof_class': 'ORIGINAL_CODE_OBJECT_EXPORT_WITH_SOURCE_COPY_DEPENDENCY_MODEL_ONLY',
                'preordinary_dependency_provenance': 'MODEL_SOURCE_BODY_COPY_ONLY',
                'bootstrap_load_calls': state['bootstrap_load_calls'],
                'bootstrap_close_calls': state['bootstrap_close_calls'], 'bootstrap_owner_active': state['bootstrap_active']}
        rows.append(record(name, observed, expected[name], details))
    inner = finish(rows, CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT, expected, mode)
    result = {'schema': SCHEMA, 'proof_class': 'MODEL_BRANCH_ONLY', 'runtime_qualified': False,
        'original_export_body_count': 11, 'copied_body_count': 6,
        'copied_body_provenance': 'MODEL_SOURCE_BODY_COPY_ONLY',
        'legacy_model_case_count': 33, 'additional_model_case_count': 20,
        'original_case_order_and_expectation_projection_preserved': True,
        'actual_original_five_or_driver_placement_qualified': False,
        'actual_kernel_or_loader_cases_qualified': False, 'observations': inner}
    return validate_model_receipt(result, mode)


def validate_model_receipt(receipt, mode):
    need(type(receipt) is dict and set(receipt) == {'schema', 'proof_class', 'runtime_qualified',
        'original_export_body_count', 'copied_body_count', 'copied_body_provenance',
        'legacy_model_case_count', 'additional_model_case_count',
        'original_case_order_and_expectation_projection_preserved',
        'actual_original_five_or_driver_placement_qualified', 'actual_kernel_or_loader_cases_qualified', 'observations'},
        'model v3 exact receipt keys')
    need(receipt['schema'] == SCHEMA and receipt['proof_class'] == 'MODEL_BRANCH_ONLY' and
         receipt['copied_body_provenance'] == 'MODEL_SOURCE_BODY_COPY_ONLY', 'model v3 provenance')
    for key, value in (('original_export_body_count', 11), ('copied_body_count', 6),
                       ('legacy_model_case_count', 33), ('additional_model_case_count', 20)):
        need(type(receipt[key]) is int and receipt[key] == value, 'model v3 independent count')
    need(receipt['original_case_order_and_expectation_projection_preserved'] is True and
         receipt['runtime_qualified'] is False and receipt['actual_original_five_or_driver_placement_qualified'] is False and
         receipt['actual_kernel_or_loader_cases_qualified'] is False, 'model v3 scope cannot upgrade to runtime')
    validate(receipt['observations'], CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT,
             expectations(), mode)
    # A second independent projection preserves all 33 old expected outcomes.
    original_expected = legacy.expectations()
    original_records = receipt['observations']['records'][:33]
    need(tuple(row['case_id'] for row in original_records) == LEGACY_CASE_IDS and
         all(row['observed'] == original_expected[row['case_id']] and
             row['expected'] == original_expected[row['case_id']] for row in original_records),
         'model v3 changed an original expected result/order')
    return receipt
