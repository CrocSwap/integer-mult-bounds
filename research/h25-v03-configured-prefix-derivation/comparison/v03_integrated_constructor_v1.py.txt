"""Pure authoring support for the proposed genuine-Root V03 prefix route.

No original module is imported or executed.  Output is a source draft with
all eight original admission/configuration literals still None.  The selected
prefix requires independent review as V03 source-gate coverage, and is not V01.
"""
import ast
import hashlib

ROOT_SHA = 'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0'
PROVIDER_SHA = '9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2'
VARIANT_SHA = 'cdb1479253358508088f8aa0e1e92e6c75ffcc127e54552698598a02de061254'
NATIVE_ENV = {
    b'PATH': b'/usr/bin:/bin', b'PYTHONHASHSEED': b'0',
    b'LANG': b'C.UTF-8', b'LC_ALL': b'C.UTF-8', b'TZ': b'UTC',
    b'PYTHONDONTWRITEBYTECODE': b'1',
}
GATES = ('VARIANT_CONFIGURATION', 'VARIANT_SOURCE_REVIEW',
         'VARIANT_STAGE_ADMISSION', 'VARIANT_NATIVE_PROFILE',
         'VARIANT_HEADER_ADMISSION', 'VARIANT_COMMAND_ADMISSION',
         'VARIANT_FUNDING', 'VARIANT_EXECUTION')
TAIL = b'''try:
    _variant_main()
except BaseException as _variant_error:
    _VARIANT_TERMINAL_ERROR[0] = _variant_error
    raise
'''
CONTROL_TAIL = b'''_V03_RESULT = [None]
try:
    _V03_RESULT[0] = _v03_original_input_prefix()
    _vroot(_INITIAL_OUTPUT + '/v03-root-after.raw.json')
    _vraw(_INITIAL_OUTPUT + '/v03-input-result.raw.json', {
        'schema': 'h25-v03-input-prefix-result-v1',
        'status': 'ORIGINAL_INPUT_PREFIX_RETURNED',
        'binding': _V03_RESULT[0],
        'whole_variant_producer_completed': False,
        'runtime_qualified': False})
except BaseException as _v03_error:
    _VARIANT_TERMINAL_ERROR[0] = _v03_error
    # No diagnostic allocation or I/O after an inherited failure. The genuine
    # parent retains its raw stderr stream and owned terminal facts; absent or
    # incomplete evidence is STOP, never a successful negative control.
    raise
'''


def need(condition, message):
    if not condition:
        raise ValueError(message)


def absolute(path):
    need(type(path) is str and 1 < len(path) <= 4096 and
         path.startswith('/') and all(32 <= ord(c) < 127 for c in path) and
         all(part not in ('', '.', '..') for part in path.split('/')[1:]),
         'canonical bounded absolute ASCII path required')
    return path


def build_control_driver(original):
    """Construct an unconfigured driver by a checked source transformation."""
    need(type(original) is bytes and len(original) == 41337 and
         hashlib.sha256(original).hexdigest() == VARIANT_SHA,
         'exact original variant source required')
    tree = ast.parse(original, feature_version=(3, 12))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == '_variant_main']
    need(len(functions) == 1, 'unique original main required')
    function = functions[0]
    lines = original.splitlines(keepends=True)
    body = b''.join(lines[function.lineno - 1:function.end_lineno])
    cut = b'    builds = []\n'
    need(body.count(cut) == 1 and body.startswith(b'def _variant_main():\n'),
         'original prebuild boundary differs')
    prefix = body.split(cut, 1)[0]
    prefix = prefix.replace(b'def _variant_main():\n',
                            b'def _v03_original_input_prefix():\n', 1)
    prefix += b'    return binding\n\n\n'
    need(original.endswith(TAIL) and original.count(TAIL) == 1,
         'original terminal entry differs')
    result = original[:-len(TAIL)] + prefix + CONTROL_TAIL
    need(len(result) <= 262144, 'genuine Root driver limit exceeded')
    result_tree = ast.parse(result, feature_version=(3, 12))
    found = {}
    for node in result_tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in GATES:
                need(isinstance(node.value, ast.Constant) and
                     node.value.value is None, 'original gate was configured')
                found[target.id] = None
    need(set(found) == set(GATES), 'original gate census differs')
    return result


def genuine_launch(stage, output, generation, nonce, mode, driver_bytes):
    """Return launch DATA only. It is not stage/source/funding admission.

    CWD=stage is an explicit choice of this launch instance, allowed by the
    original Root. It becomes part of Gamma and must enter C05 rule derivation.
    The future parent must authenticate and own that exact stage and output
    ancestor before actually passing these values to its genuine Popen route.
    """
    absolute(stage)
    absolute(output)
    need(output != stage and not output.startswith(stage + '/'),
         'output must be outside the immutable stage')
    need(type(generation) is str and 1 <= len(generation) <= 96 and
         all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in generation),
         'generation differs')
    need(type(nonce) is str and len(nonce) == 64 and
         all(c in '0123456789abcdef' for c in nonce), 'nonce differs')
    need(type(mode) is str and mode in ('normal', 'optimized'), 'mode differs')
    need(type(driver_bytes) is bytes and 0 < len(driver_bytes) <= 262144,
         'bounded reviewed driver bytes required')
    integration = stage + '/integration'
    command = ['/usr/bin/python3.12', '-S', '-s', '-P', '-B']
    if mode == 'optimized':
        command.append('-O')
    command += [integration + '/full_driver.py',
                '--root-sha256', ROOT_SHA,
                '--provider', integration + '/probe_binding_v3.py', PROVIDER_SHA,
                '--driver', integration + '/v03_control_driver_v1.py',
                hashlib.sha256(driver_bytes).hexdigest(),
                '--integration', integration, '--',
                '--output', output, '--generation', generation,
                '--launch-nonce', nonce]
    return {'command': command, 'env': dict(NATIVE_ENV), 'cwd': stage,
            'mode': mode, 'generation': generation, 'launch_nonce': nonce,
            'source_admitted': False, 'execution_admitted': False}
