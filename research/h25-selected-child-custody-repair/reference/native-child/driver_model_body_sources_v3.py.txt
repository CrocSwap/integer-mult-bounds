"""Exact driver body copy; MODEL_SOURCE_BODY_COPY_ONLY, no driver top-level execution.

The original driver has future annotations enabled. This separate module keeps
that compiler semantic while Root copies retain the absence of future imports.
"""
from __future__ import annotations

def _initial_native_tcb():
    root, api = _CAPTURED_BOOTSTRAP_ROOT, _CAPTURED_BOOTSTRAP_API
    if (type(NATIVE_TCB_CANDIDATE_PROFILE_ADMISSION_SHA256) is not str or
            len(NATIVE_TCB_CANDIDATE_PROFILE_ADMISSION_SHA256) != 64 or
            any(character not in '0123456789abcdef' for character in NATIVE_TCB_CANDIDATE_PROFILE_ADMISSION_SHA256)):
        raise RuntimeError('Candidate initial native TCB profile has not been independently admitted')
    if (type(EXPECTED_BOOTSTRAP_ROOT_SHA256) is not str or
            _INITIAL_ROOT_IDENTITY != EXPECTED_BOOTSTRAP_ROOT_SHA256 or
            type(NATIVE_TCB_HELPER_SHA256) is not str or len(NATIVE_TCB_HELPER_SHA256) != 64 or
            type(NATIVE_TCB_EXPECTED_FILES) is not tuple or
            type(NATIVE_TCB_EXPECTED_HASHLIB_ORIGIN) is not str):
        raise RuntimeError('Initial native TCB source and expected dependency tuple are not configured')
    helper_path = __file__.rsplit('/', 2)[0] + '/areas/cache-validity/probe-native/native_tcb_v1.py'
    api[0]()
    digest, _, source = root._hash_regular(helper_path, 262144, True)
    if digest != NATIVE_TCB_HELPER_SHA256:
        raise RuntimeError('Initial native TCB helper source differs')
    helper = root.ModuleType('_h25_initial_native_tcb')
    namespace = helper.__dict__
    namespace.update({'__file__': helper_path, '__builtins__': root.builtins.__dict__})
    api[0]()
    code = root._COMPILE(source, helper_path, 'exec', dont_inherit=True, optimize=root._OPTIMIZE)
    api[0]()
    root._EXEC(code, namespace)
    api[0]()
    receipt = namespace['verify_native_tcb'](root, api, NATIVE_TCB_EXPECTED_FILES,
                                               NATIVE_TCB_EXPECTED_HASHLIB_ORIGIN)
    if type(NATIVE_TCB_CONTROLS_SHA256) is not str or len(NATIVE_TCB_CONTROLS_SHA256) != 64:
        raise RuntimeError('Initial native TCB control source pin is not configured')
    control_path = __file__.rsplit('/', 2)[0] + '/areas/cache-validity/probe-native/native_tcb_controls_v1.py'
    api[0]()
    digest, _, control_source = root._hash_regular(control_path, 262144, True)
    if digest != NATIVE_TCB_CONTROLS_SHA256:
        raise RuntimeError('Initial native TCB controls source differs')
    control_namespace = {'__name__': '_h25_initial_native_tcb_controls', '__file__': control_path,
                         '__builtins__': root.builtins.__dict__}
    api[0]()
    control_code = root._COMPILE(control_source, control_path, 'exec', dont_inherit=True, optimize=root._OPTIMIZE)
    api[0]()
    root._EXEC(control_code, control_namespace)
    argv = root.sys.argv
    if (type(argv) is not list or any(type(arg) is not str for arg in argv) or
            argv.count('--output') != 1 or argv.index('--output') + 1 >= len(argv)):
        raise RuntimeError('Early TCB controls require the unique parent --output argument')
    output = argv[argv.index('--output') + 1]
    stage_root = __file__.rsplit('/', 2)[0]
    if (not output.startswith('/') or output.endswith('/') or
            any(part in ('', '.', '..') for part in output.split('/')[1:]) or
            output == stage_root or output.startswith(stage_root + '/')):
        raise RuntimeError('Early TCB controls require a canonical absolute output outside the stage')
    # Parent owns an existing nonsymlink output parent. mkdir is exclusive:
    # a preexisting output, file, or symlink is rejected before any fixture write.
    api[0]()
    root.posix.mkdir(output, 0o700)
    control_directory = output + '/initial-tcb-controls'
    root.posix.mkdir(control_directory, 0o700)
    api[0]()
    controls = control_namespace['run_controls'](
        helper, root, api, NATIVE_TCB_EXPECTED_FILES, NATIVE_TCB_EXPECTED_HASHLIB_ORIGIN, control_directory)
    if (controls.get('schema') != 'h25-native-tcb-controls-v1' or
            controls.get('expected_records') != 5 or len(controls.get('records', [])) != 5 or
            controls.get('scientific_calls') != 0 or controls.get('probe_native_imports') != 0):
        raise RuntimeError('Initial native TCB control census differs')
    controls['status'] = 'NATIVE_INITIAL_TCB_CONTROLS_PASS'
    # Exact source-reviewed exception: preserve the original five controls and
    # repeat the positive check before cold authority or field-service setup.
    # Expected rows remain the literal candidate profile above, never recaptured.
    api[0]()
    restoration = namespace['verify_native_tcb'](
        root, api, NATIVE_TCB_EXPECTED_FILES, NATIVE_TCB_EXPECTED_HASHLIB_ORIGIN)
    if (type(restoration) is not dict or
            restoration.get('status') != 'MATCHED_DECLARED_INITIAL_NATIVE_FILES' or
            restoration.get('declared_file_count') != len(NATIVE_TCB_EXPECTED_FILES) or
            restoration.get('probe_private_abi_access') is not False):
        raise RuntimeError('Initial native TCB restoration corroboration differs')
    return receipt, controls, output, restoration

