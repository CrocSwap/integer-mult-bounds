"""Exact pinned source-body copies for isolated deterministic models only.

PROVENANCE: MODEL_SOURCE_BODY_COPY_ONLY. These are not live Root functions,
not the original eleven authenticated code-object exports, and not runtime
ownership/placement/kernel/loader evidence. No Root or driver top level is
imported. Consumers clone these definitions into wholly isolated namespaces.
The driver copy lives separately to preserve its future-annotations flag.
See MODEL-BODY-PROVENANCE-v3.json for source/default/decorator/future semantics.
"""
from driver_model_body_sources_v3 import _initial_native_tcb

def _field_bootstrap_preflight(parsed, runtime_policy, elf_policy, path, expected):
    """Authenticate the ORIGINAL ordinary loader route before any helper call.

    The prospective ordinary_project row is predicted inventory only. A later
    genuine map/symbol snapshot cannot repair failure here. This uses the
    original parent-authenticated OS/interpreter bootstrap, no native hook or
    concurrent load and no bootstrap source/dependency-file replacement premise.
    """
    config = _field_config()
    _check_root()
    _field_admit_history(path)
    _need(_GETDLOPENFLAGS() == 2 and _SYSCONF(30) == 4096 and _GETTRACE() is None and _GETPROFILE() is None and
          tuple(sorted(elf_policy['expected_exports'])) ==
          ('PyInit__h25_dict_probe', 'PyInit__h25_field_service_v1') and
          parsed['sha256'] == expected,
          'Field ordinary loader flags/own initializers/parsed-image binding differs')
    # Fixed metadata and input custody are checked BEFORE ordinary dlopen and
    # before the first maps helper can execute a libc/dlfcn entry or resolver.
    elf_helper, elf_gate, functions = _FIELD_HELPER[0]
    elf_gate()
    import_receipt = functions[4](parsed, runtime_policy)
    _need(import_receipt['schema'] == 'h25-bootstrap-import-profile-v1' and
          import_receipt['ordinary_inventory'] == 'PREDICTED_NOT_OBSERVED',
          'Field ordinary import profile is not a pre-entry proof obligation')
    tcb_helper, tcb_gate, verify = _FIELD_TCB_HELPER[0]
    tcb_gate()
    expected_files = config['preordinary_tcb_files']
    _need(tuple((row[1], row[2], row[3]) for row in config['map_files']) == expected_files,
          'Field literal TCB/file inventory bridge differs')
    # capture_api creates new source-bound closures from the already raw-admitted
    # original Root functions; it does not recapture any current provider values.
    api = capture_api()
    _need(api[0]() == _ROOT_METADATA['source_sha256'], 'Field original API0 identity differs')
    tcb_gate()
    receipt = verify(_ROOT_MODULE, api, expected_files, config['preordinary_hashlib_origin'])
    _need(type(receipt) is dict and receipt.get('schema') == 'h25-initial-native-tcb-v1' and
          receipt.get('status') == 'MATCHED_DECLARED_INITIAL_NATIVE_FILES' and
          receipt.get('declared_file_count') == len(expected_files) and
          receipt.get('probe_private_abi_access') is False and receipt.get('reusable_pass') is False,
          'Field fresh ordinary bootstrap TCB corroboration differs')
    _check_root()
    _field_admit_history(path)
    _need(_GETDLOPENFLAGS() == 2, 'Field ordinary flags changed across bootstrap proof')
    digest, size, _ = _hash_regular(path, _MAX_BINARY, False)
    _need(digest == expected and size == parsed['bytes'], 'Field ordinary ELF changed before load')
    _FIELD_LEDGER['ordinary_bootstrap_receipt'] = receipt
    _FIELD_LEDGER['ordinary_import_receipt'] = import_receipt
    _field_event('ordinary_bootstrap_admitted')


def _register_fields(function_fields, id0, function_type):
    _check_root()
    _field_consistent()
    _need(_FIELD_LEDGER['register_attempts'] == 0 and _FIELD_SLOT[0] == 'UNBOUND',
          'Field primitive registration is once-only')
    _FIELD_LEDGER['register_attempts'] += 1
    try:
        _need(_TYPE(function_fields) is tuple and _LEN(function_fields) == 7 and
              id0 is _ID and function_type is FunctionType, 'Field primitive identity differs')
        getters = []
        for index, pair in enumerate(function_fields):
            _need(_TYPE(pair) is tuple and _LEN(pair) == 2 and
                  _TYPE(pair[0]) is str and pair[0] == _FIELD_NAMES[index],
                  'Field primitive names/order differ')
            getter = pair[1]
            descriptor = FunctionType.__dict__[_FIELD_NAMES[index]]
            # Each descriptor.__get__ lookup creates a fresh method wrapper.
            # Readonly wrapper ownership binds the actual original descriptor.
            original = descriptor.__get__
            _need(_TYPE(getter) is _TYPE(original) and getter.__self__ is descriptor and
                  getter.__name__ == '__get__', 'Field original descriptor getter differs')
            getters.append(getter)
        _need(len(_FIELD_INTEGRATION) == 1, 'Field source registration requires original driver injection')
        _field_install_configuration(_FIELD_INTEGRATION[0])
        _FIELD_LEDGER['primitives'] = (tuple(getters), id0, function_type)
        _field_phase('REGISTERED')
        _field_event('primitives_registered', 7)
    except _BASE_ERROR:
        _field_phase('FAILED')
        raise
    finally:
        function_fields = getters = getter = descriptor = original = None


def _field_source_gate(target):
    """Lifecycle-only, direct native caller gate before any mutable validator.

    The source-authenticated raw caller first admits this returned closure using
    its own original descriptors. This gate then admits the complete original
    Root Python validator graph before target can call _check_root or helpers.
    It has no effective global loads and is never used for individual fields.
    """
    type0, len0, id0, error = type, len, id, RuntimeError
    function_type = FunctionType
    cell_type = type((lambda value: lambda: value)(None).__closure__[0])
    getters = tuple(FunctionType.__dict__[name].__get__ for name in _FIELD_NAMES)
    cell_get = cell_type.__dict__['cell_contents'].__get__
    dict_len, dict_get, dict_iter = dict.__len__, dict.get, dict.__iter__
    next0, str0 = next, str
    missing = object()
    namespace, builtin_namespace = _ROOT_NAMESPACE, builtins.__dict__
    namespace_items, builtin_items = tuple(namespace.items()), tuple(builtin_namespace.items())
    pending = [value for _, value in namespace_items if type0(value) is function_type]
    pending.extend(value for value in _ROOT_CELL if type0(value) is function_type)
    for cls in (BootstrapCapability, _NativeSpec, _FieldSpec, _SealedImage):
        for value in cls.__dict__.values():
            if type0(value) in (staticmethod, classmethod):
                value = value.__func__
            if type0(value) is function_type:
                pending.append(value)
    pending.append(target)
    functions, records = [], []
    while pending:
        function = pending.pop()
        if any(function is prior for prior in functions):
            continue
        _need(len(functions) < 512, 'Root caller admission graph exceeds bound')
        functions.append(function)
        values = tuple(getter(function, function_type) for getter in getters)
        cells = () if values[5] is None else tuple((cell, cell_get(cell, cell_type)) for cell in values[5])
        records.append((function, values, cells))
        for cell, value in cells:
            if type0(value) is function_type:
                pending.append(value)
    records = tuple(records)
    def admitted(*args):
        # All operations until target() below use captured native descriptors and
        # builtin identities. In particular no Python self-validator runs first.
        if dict_len(namespace) != len0(namespace_items) or dict_len(builtin_namespace) != len0(builtin_items):
            raise error('Field caller Root namespace size changed')
        iterator = key = None
        try:
            for owner in (namespace, builtin_namespace):
                iterator = dict_iter(owner)
                while True:
                    key = next0(iterator, missing)
                    if key is missing:
                        break
                    if type0(key) is not str0:
                        key = iterator = None
                        raise error('Field caller namespace contains a foreign key')
                    key = None
                iterator = None
        finally:
            key = iterator = owner = None
        for key, expected in namespace_items:
            if dict_get(namespace, key, missing) is not expected:
                raise error('Field caller Root namespace member changed')
        for key, expected in builtin_items:
            if dict_get(builtin_namespace, key, missing) is not expected:
                raise error('Field caller builtin changed')
        for function, values, cells in records:
            if type0(function) is not function_type:
                raise error('Field caller original function type differs')
            for index, getter in enumerate0(getters):
                if getter(function, function_type) is not values[index]:
                    raise error('Field caller Root function descriptor changed')
            for cell, expected in cells:
                if cell_get(cell, cell_type) is not expected:
                    raise error('Field caller Root function closure changed')
        return target(*args)
    # Bind enumerate locally before record creation; source gate has no global
    # enumerate lookup when the gate is invoked after an adverse control.
    enumerate0 = enumerate
    return admitted


def _new_field_fixture_transport():
    """One isolated authority/control owner; no production slot reset or load."""
    owner, entries = _new_field_fixture()
    slot, publication = ['UNBOUND', None], ['UNBOUND', None]
    original_fields = tuple((name, FunctionType.__dict__[name].__get__) for name in _FIELD_NAMES)
    function_type, id0, type0, tuple0, len0 = FunctionType, _ID, _TYPE, tuple, len
    token, error, base_error = object(), RuntimeError, BaseException
    private = {'attempted': False, 'bound': False, 'primitives': None, 'close_calls': 0}
    def consistent():
        if (type0(slot) is not list or len0(slot) != 2 or type0(publication) is not list or len0(publication) != 2 or
                type0(slot[0]) is not str or type0(publication[0]) is not str or
                slot[0] != publication[0] or slot[1] is not publication[1]):
            raise error('Fixture slot/publication custody differs')
    def register(fields, original_id, original_type):
        consistent()
        if slot[0] != 'UNBOUND' or private['attempted']:
            raise error('Fixture primitive registration is once-only')
        private['attempted'] = True
        try:
            if type0(fields) is not tuple0 or len0(fields) != 7 or original_id is not id0 or original_type is not function_type:
                raise error('Fixture original primitive identity differs')
            getters = []
            for index, pair in enumerate(fields):
                name, original = original_fields[index]
                if (type0(pair) is not tuple0 or len0(pair) != 2 or type0(pair[0]) is not str or pair[0] != name or
                        type0(pair[1]) is not type0(original) or pair[1].__self__ is not original.__self__ or
                        pair[1].__name__ != '__get__'):
                    raise error('Fixture getter identity differs')
                getters.append(pair[1])
            private['primitives'] = (tuple0(getters), original_id, original_type)
            publication[0] = slot[0] = 'REGISTERED'
        except base_error:
            publication[0] = slot[0] = 'FAILED'
            raise
    def bind():
        consistent()
        if slot[0] != 'REGISTERED' or private['bound']:
            raise error('Fixture primitive binding is once-only')
        private['bound'] = True
        publication[0] = slot[0] = 'BINDING'
        try:
            primitive = private['primitives']
            entries[1](primitive[0], primitive[1], primitive[2], token)
            payload = (entries[0], owner, 'h25-indexed-field-v1', type0(owner))
            publication[1] = slot[1] = payload
            publication[0] = slot[0] = 'ACTIVE'
        except base_error:
            publication[0] = slot[0] = 'FAILED'
            raise
    def close():
        consistent()
        private['close_calls'] += 1
        if slot[0] in ('CLOSING', 'CLOSED'):
            return None
        if slot[0] not in ('UNBOUND', 'REGISTERED', 'ACTIVE'):
            raise error('Fixture failed owner cannot close as fallback')
        publication[0] = slot[0] = 'CLOSING'
        try:
            if private['bound']:
                entries[2](token)
            private['primitives'] = None
            publication[0] = slot[0] = 'CLOSED'
        except base_error:
            publication[0] = slot[0] = 'FAILED'
            raise
    def receipt():
        consistent()
        return {'schema': 'h25-field-fixture-lifecycle-v1', 'phase': publication[0],
                'bound': private['bound'], 'close_calls': private['close_calls']}
    functions = tuple(_field_source_gate(function) for function in (register, bind, close, receipt))
    records = tuple(_field_admission_record(function) for function in functions)
    return (slot,) + functions + (records, publication)


def _entry():
    args = sys.argv[1:]
    _need(len(args) >= 11 and args[0] == '--root-sha256' and args[2] == '--provider' and
          args[5] == '--driver' and args[8] == '--integration' and args[10] == '--',
          'Bootstrap launch argument schema differs')
    initialize(args[1])
    provider_path, provider_sha = args[3], args[4]
    driver_path, driver_sha, integration = args[6], args[7], args[9]
    _need(type(integration) is str and integration.startswith('/') and
          provider_path.rsplit('/', 1)[0] == integration and
          driver_path.rsplit('/', 1)[0] == integration,
          'Bootstrap integration/source directory differs')
    _FIELD_INTEGRATION.append(integration)  # reservation only; setup follows original TCB controls
    capability = admit_provider(provider_path, provider_sha)
    api = capture_api()
    preflight(capability)  # reject unsupported profile before any driver/build work
    _check_root()
    digest, _, driver_source = _hash_regular(driver_path, _MAX_SOURCE, True)
    _need(digest == driver_sha, 'Bootstrap scientific driver source differs')
    _need(tuple(sys.path) == _INITIAL_PATH, 'Bootstrap initial search path changed before stage installation')
    sys.path.insert(0, integration)
    driver = ModuleType('__main__')
    driver_namespace = driver.__dict__
    driver_namespace.update({'__file__': driver_path, '__builtins__': builtins.__dict__,
                             'bootstrap_root': _ROOT_MODULE,
                             'bootstrap_capability': capability, 'bootstrap_api': api,
                             'field_transport': _FIELD_TRANSPORT_CELL[0],
                             'field_control_transport': _FIELD_CONTROL_CELL[0]})
    code = _COMPILE(driver_source, driver_path, 'exec', dont_inherit=True, optimize=_OPTIMIZE)
    _check_root()
    sys.argv = [driver_path] + args[11:]
    sys.modules['__main__'] = driver
    _EXEC(code, driver_namespace)


BODY_NAMES = ('_field_bootstrap_preflight', '_register_fields', '_field_source_gate', '_new_field_fixture_transport', '_entry', '_initial_native_tcb')
BODY_PACKET = tuple((name, globals()[name].__code__, globals()[name].__defaults__) for name in BODY_NAMES)
