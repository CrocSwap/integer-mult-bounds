"""Original Root code clones with isolated deterministic primitive models.

MODEL_BRANCH_ONLY. These controls do not perform kernel calls, seal real bytes,
load any image, establish original primitive provenance, or qualify a runtime.
Fake native entries are explicitly a model class; their admission is NOT C ABI
validation. The separate real native and required kernel controls remain due.
"""
from hashlib import sha256
from types import FunctionType, ModuleType, CodeType, SimpleNamespace
from receipt_contract_v1 import need, record, finish, validate

SCHEMA = 'h25-field-loader-model-control-receipt-v1'
BODY_NAMES = ('_field_new_image', '_field_hash_fd', '_field_check_image', '_field_event',
 '_field_phase', '_field_admit_history', '_bind_field_service', '_close_field_service',
 '_field_freeze', '_fingerprint', '_field_consistent')
CASE_IDS = ('model-copy-valid', 'model-copy-short-reads', 'model-copy-short-writes',
 'model-copy-zero-write', 'model-copy-bool-write', 'model-copy-excess-write',
 'model-copy-early-eof', 'model-copy-hash-mismatch', 'model-copy-source-drift',
 'model-seal-missing', 'model-memfd-unsupported', 'model-writable-map-conflict',
 'model-seal-readback-mismatch', 'model-alias-inode-mismatch',
 'model-fd-reuse-detected', 'model-owner-mismatch', 'model-serial-mismatch',
 'model-spec-mismatch', 'model-duplicate-image', 'model-cleanup-error-preserves-primary',
 'model-history-valid', 'model-history-prior-procfd', 'model-history-reserved-name',
 'model-history-retained-cache-no-sysmodules', 'model-history-import-drift',
 'model-load-failure-retains', 'model-module-exec-failure-retains',
 'model-loader-return-wrong-type-retains', 'model-partial-bind-failure-retains',
 'model-partial-bind-cleanup-failure-retains', 'model-status-failure-retains',
 'model-success-close-retains', 'model-duplicate-bind')
NORMAL_CASE_COUNT = 33
OPTIMIZED_CASE_COUNT = 33
PAYLOAD = b'field-model-payload\n'


class ModelFault(Exception):
    pass


def expectations():
    # Exact independent outcome projection; detailed observed call trace and
    # original error text are retained separately in the hashed receipt.
    expected = {}
    errors = {
      'model-copy-zero-write': ['RuntimeError', 'Field copy write failed or exceeded requested bytes'],
      'model-copy-bool-write': ['RuntimeError', 'Field copy write failed or exceeded requested bytes'],
      'model-copy-excess-write': ['RuntimeError', 'Field copy write failed or exceeded requested bytes'],
      'model-copy-early-eof': ['RuntimeError', 'Field source copy ended early'],
      'model-copy-hash-mismatch': ['RuntimeError', 'Field source changed during bounded copy'],
      'model-copy-source-drift': ['RuntimeError', 'Field source changed during bounded copy'],
      'model-seal-missing': ['RuntimeError', 'Field mandatory WRITE/GROW/SHRINK/SEAL/EXEC seals unavailable'],
      'model-memfd-unsupported': ['OSError', 'unsupported-memfd-policy'],
      'model-writable-map-conflict': ['BlockingIOError', 'writable-map-conflict'],
      'model-seal-readback-mismatch': ['RuntimeError', 'Field sealed byte readback differs'],
      'model-alias-inode-mismatch': ['RuntimeError', 'Field private procfd alias differs from retained sealed inode'],
      'model-fd-reuse-detected': ['RuntimeError', 'Field retained image bytes/inode/seals differ'],
      'model-owner-mismatch': ['RuntimeError', 'Field sealed image ownership differs'],
      'model-serial-mismatch': ['RuntimeError', 'Field sealed image ownership differs'],
      'model-spec-mismatch': ['RuntimeError', 'Field original FD slot/spec/source identity changed'],
      'model-duplicate-image': ['RuntimeError', 'No second field image is permitted'],
      'model-cleanup-error-preserves-primary': ['RuntimeError', 'Field copy write failed or exceeded requested bytes'],
      'model-history-prior-procfd': ['RuntimeError', 'Field reserved name/procfd/legacy-cache history collision'],
      'model-history-reserved-name': ['RuntimeError', 'Field reserved name/procfd/legacy-cache history collision'],
      'model-history-retained-cache-no-sysmodules': ['RuntimeError', 'Field prior explicit Root native load exists'],
      'model-history-import-drift': ['RuntimeError', 'Field complete source-controlled native import history differs'],
      'model-load-failure-retains': ['ModelFault', 'create-stop'],
      'model-module-exec-failure-retains': ['ModelFault', 'exec-stop'],
      'model-loader-return-wrong-type-retains': ['RuntimeError', 'Field loader returned non-module'],
      'model-partial-bind-failure-retains': ['ModelFault', 'bind-stop'],
      'model-partial-bind-cleanup-failure-retains': ['ModelFault', 'bind-stop'],
      'model-status-failure-retains': ['RuntimeError', 'Field service did not bind original primitives'],
      'model-duplicate-bind': ['RuntimeError', 'Field binding requires fixed primitives and one attempt']}
    retained_names = set(CASE_IDS[25:])
    for name in CASE_IDS:
        retained = name in retained_names
        expected[name] = {'error': errors.get(name), 'loader_calls': 1 if retained else 0,
                          'retained_image': retained, 'real_syscalls': 0, 'real_native_calls': 0}
    need(len(expected) == 33, 'model literal inventory')
    return expected


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
              'native_import_history_before_bind': (), 'native_origins_before_bind': ()}
    trace, files, open_fds = [], {10: bytearray(PAYLOAD), 20: bytearray()}, set()
    state = {'read_offset': 0, 'source_stats': 0, 'seals': 0, 'loader_calls': 0,
             'reused': False, 'model_native_close_calls': 0, 'model_native_bind_calls': 0}
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
             st_mode=0o100700, st_mtime_ns=mtime, st_ctime_ns=1)
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
    class Binding:
        close = staticmethod(mark('bootstrap-close', None))
    provider = SimpleNamespace(ProbeBinding=Binding,
        capture_field_loader=lambda binding: (object(), mark('maps', {}), mark('symbol-snapshot', {})))
    namespace.update(_OPEN=opened, _MEMFD=memfd, _FSTAT=fstat, _READ=read, _WRITE=write,
       _PREAD=pread, _FCNTL=fcntl, _CLOSE=close, _CREATE_DYNAMIC=create, _EXEC_DYNAMIC=execute,
       BuiltinFunctionType=ModelEntry, _GETDLOPENFLAGS=lambda: 2, _GETTRACE=lambda: None,
       _GETPROFILE=lambda: None, _check_root=lambda: None, _capability_state=lambda cap: (None, provider),
       _field_config=lambda: config, _field_native_origins=lambda: config['native_origins_before_bind'],
       _field_admit_builds=lambda path, expected, receipt: len(PAYLOAD),
       _hash_regular=lambda path, limit, materialize: (sha256(PAYLOAD).hexdigest(), len(PAYLOAD), PAYLOAD if materialize else None),
       _field_runtime_policy=lambda *args: {}, _field_map_custody=lambda *args: None,
       load_probe=lambda *args: object(),
       _FIELD_HELPER=[(object(), lambda: None, (mark('static-admit-model', {}),
          mark('map-admit-model', {}), mark('requests-model', ()), mark('provider-admit-model', {})))])
    return namespace, config, state, trace, open_fds


def run_loader_model_controls(bundle, mode):
    expected, rows = expectations(), []
    for name in CASE_IDS:
        env, config, state, trace, open_fds = _namespace(bundle, name)
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
            elif name in CASE_IDS[25:]:
                env['_bind_field_service'](object(), '/fixture/production.so', sha256(PAYLOAD).hexdigest(), {})
                if name == 'model-success-close-retains':
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
                    # Capability absence is a source contract of this model.
                    'real_syscalls': 0, 'real_native_calls': 0}
        if state['loader_calls']:
            need(trace.index('maps') < trace.index('map-admit-model') < trace.index('requests-model') <
                 trace.index('symbol-snapshot') < trace.index('provider-admit-model') < trace.index('create-dynamic-model'),
                 'model two-phase/pre-loader ordering')
        if name == 'model-cleanup-error-preserves-primary':
            need(env['_FIELD_LEDGER']['cleanup_failures'] == [('copy_close', 'OSError'), ('copy_close', 'OSError')], 'model copy cleanup evidence')
        if name == 'model-partial-bind-cleanup-failure-retains':
            need(env['_FIELD_LEDGER']['cleanup_failures'] == [('partial_native_close', 'ModelFault')], 'model bind cleanup evidence')
        if name == 'model-success-close-retains':
            need(state['model_native_close_calls'] == 1 and env['_FIELD_SLOT'][0] == 'CLOSED' and
                 images[0].module is env['_FIELD_LEDGER']['native'], 'model idempotent logical close retention')
        rows.append(record(name, observed, expected[name], {'model_call_trace': trace,
          'open_model_descriptors': sorted(open_fds), 'cleanup_failures': env['_FIELD_LEDGER']['cleanup_failures'],
          'events': env['_FIELD_LEDGER']['events'], 'phase': env['_FIELD_SLOT'][0]}))
    inner = finish(rows, CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT, expected, mode)
    return {'schema': SCHEMA, 'proof_class': 'MODEL_BRANCH_ONLY', 'runtime_qualified': False, 'observations': inner}


def validate_model_receipt(receipt, mode):
    need(type(receipt) is dict and set(receipt) == {'schema', 'proof_class', 'runtime_qualified', 'observations'} and
         receipt['schema'] == SCHEMA and receipt['proof_class'] == 'MODEL_BRANCH_ONLY' and
         receipt['runtime_qualified'] is False, 'model receipt cannot claim kernel/native qualification')
    validate(receipt['observations'], CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT, expectations(), mode)
    return receipt
