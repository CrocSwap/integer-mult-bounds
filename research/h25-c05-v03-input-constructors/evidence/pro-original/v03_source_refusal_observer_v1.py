"""Pure source-location corroboration for parent-retained V03 stderr.

This does not establish ownership, currentness, admission, or even that a child
ran. The genuine parent must supply its complete retained raw stderr after
actual owned termination, with independently authenticated driver/stage pins.
No result of this function by itself is a V03 PASS or a ParentCompletion.
"""
import ast
import json

COMPONENT_LOG_BYTES = 2 * 1024 * 1024
COMPONENT_RECORD_BYTES = 1048576
ROOT_COUNTERS = ('load_calls', 'native_creations', 'native_execs',
                 'activation_attempts', 'successful_bindings',
                 'deactivation_attempts', 'cleanup_failures',
                 'control_module_creations')

MESSAGES = {
    '_vcheck_literal_sources': (
        'Variant source role path differs',
        'Variant reviewed source/header differs',
        'Variant role file omitted from closure'),
    '_vcheck_custody': ('Variant current source closure differs',),
    '_v03_original_input_prefix': (
        'Variant literal configuration differs',
        'Variant original preflight differs'),
}


def source_site(driver_bytes, function, message):
    """Derive the unique original logical-raise line without running code."""
    if (type(driver_bytes) is not bytes or not 0 < len(driver_bytes) <= 262144 or
            type(function) is not str or type(message) is not str or
            function not in MESSAGES or message not in MESSAGES[function]):
        raise ValueError('bounded source and literal V03 refusal required')
    tree = ast.parse(driver_bytes, feature_version=(3, 12))
    candidates = [node for node in tree.body
                  if isinstance(node, ast.FunctionDef) and node.name == function]
    if len(candidates) != 1:
        raise ValueError('unique actual control function required')
    sites = []
    for node in ast.walk(candidates[0]):
        if not isinstance(node, ast.Raise):
            continue
        value = node.exc
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and
                value.func.id == 'RuntimeError' and len(value.args) == 1 and
                not value.keywords and isinstance(value.args[0], ast.Constant) and
                type(value.args[0].value) is str and value.args[0].value == message):
            sites.append(node.lineno)
    if len(sites) != 1:
        raise ValueError('unique actual literal raise required')
    return sites[0]


def corroborate_raw_refusal(driver_bytes, driver_path, stderr_raw,
                            function, message, original_log_bound):
    """Recognize only the expected terminal logical source refusal.

    All exceptions from this checker mean incomplete verification. A False
    return means different or insufficient raw evidence; never generic success.
    The bound is the existing parent's independently fixed log limit, not a
    newly increased allowance. This parser intentionally refuses chained,
    grouped, truncated and nonstandard tracebacks; those require review.
    """
    if (type(driver_path) is not str or not 1 < len(driver_path) <= 4096 or
            not driver_path.startswith('/') or
            any(not 32 <= ord(c) < 127 for c in driver_path) or
            type(original_log_bound) is not int or original_log_bound <= 0):
        raise ValueError('actual source path and existing parent log limit required')
    if (type(stderr_raw) is not bytes or
            len(stderr_raw) > min(original_log_bound, COMPONENT_LOG_BYTES)):
        return False
    line_number = source_site(driver_bytes, function, message)
    header = ('  File "' + driver_path + '", line ' + str(line_number) +
              ', in ' + function).encode('ascii')
    ending = ('RuntimeError: ' + message + '\n').encode('ascii')
    start = b'Traceback (most recent call last):\n'
    if (not stderr_raw.startswith(start) or not stderr_raw.endswith(ending) or
            stderr_raw.count(start) != 1 or
            b'During handling of the above exception' in stderr_raw or
            b'The above exception was the direct cause' in stderr_raw):
        return False
    frames = [line for line in stderr_raw.splitlines() if line.startswith(b'  File "')]
    return bool(frames) and frames[-1] == header


def _no_noninteger(token):
    raise ValueError('noninteger JSON number or constant')


def _integer(token):
    if len(token) > 21:
        raise ValueError('JSON integer length bound')
    value = int(token)
    if not -(1 << 64) <= value < (1 << 64):
        raise ValueError('JSON integer domain')
    return value


def _pairs(pairs):
    if len(pairs) > 1024:
        raise ValueError('JSON mapping bound')
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def _tree(value, depth, budget):
    budget[0] += 1
    if depth > 24 or budget[0] > 65536:
        raise ValueError('JSON tree bound')
    kind = type(value)
    if value is None or kind is bool or kind is int:
        return
    if kind is str:
        budget[1] += len(value)
        if len(value) > 8192 or budget[1] > 524288:
            raise ValueError('JSON text bound')
        return
    if kind is list:
        if len(value) > 1024:
            raise ValueError('JSON sequence bound')
        for item in value:
            _tree(item, depth + 1, budget)
        return
    if kind is dict:
        for key in value:
            _tree(key, depth + 1, budget)
            _tree(value[key], depth + 1, budget)
        return
    raise ValueError('foreign JSON value')


def _decode(raw, original_record_bound):
    if (type(original_record_bound) is not int or original_record_bound <= 0 or
            type(raw) is not bytes or
            not 0 < len(raw) <= min(original_record_bound, COMPONENT_RECORD_BYTES)):
        raise ValueError('existing parent/raw component byte bound')
    value = json.loads(raw.decode('ascii'), object_pairs_hook=_pairs,
                       parse_int=_integer, parse_float=_no_noninteger,
                       parse_constant=_no_noninteger)
    _tree(value, 0, [0, 0])
    return value


def corroborate_positive(result_raw, root_after_raw, preflight_raw,
                         parent_binding, original_record_bound):
    """Corroborate three complete raw records against independent launch data.

    A True result is ONLY these three checks. Original initial TCB/five-control/
    restoration records, custody-before, independent dependencies, parent source
    continuity, domain ownership and terminal capture remain required elsewhere.
    Limits here are additional component ceilings, never increased parent caps.
    Decode resource/MemoryError failures propagate for parent first-error capture.
    """
    if (type(parent_binding) is not dict or
            any(type(k) is not str for k in parent_binding) or set(parent_binding) != {
            'mode', 'generation', 'launch_nonce'} or
            any(type(v) is not str for v in parent_binding.values()) or
            parent_binding['mode'] not in ('normal', 'optimized') or
            not 1 <= len(parent_binding['generation']) <= 96 or
            any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-'
                for c in parent_binding['generation']) or
            len(parent_binding['launch_nonce']) != 64 or
            any(c not in '0123456789abcdef' for c in parent_binding['launch_nonce'])):
        raise ValueError('independent actual parent launch binding required')
    result = _decode(result_raw, original_record_bound)
    counters = _decode(root_after_raw, original_record_bound)
    preflight = _decode(preflight_raw, original_record_bound)
    if (type(result) is not dict or set(result) != {
            'schema', 'status', 'binding', 'whole_variant_producer_completed',
            'runtime_qualified'} or
            type(result['schema']) is not str or
            result['schema'] != 'h25-v03-input-prefix-result-v1' or
            type(result['status']) is not str or
            result['status'] != 'ORIGINAL_INPUT_PREFIX_RETURNED' or
            result['whole_variant_producer_completed'] is not False or
            result['runtime_qualified'] is not False or
            type(result['binding']) is not dict or
            set(result['binding']) != set(parent_binding) or
            any(type(result['binding'][k]) is not str or
                result['binding'][k] != parent_binding[k] for k in parent_binding)):
        return False
    if (type(counters) is not dict or set(counters) != set(ROOT_COUNTERS) or
            any(type(counters[k]) is not int or counters[k] != 0 for k in ROOT_COUNTERS)):
        return False
    return (type(preflight) is dict and set(preflight) == {
        'schema', 'authenticated_files', 'native_private_access', 'cached_admission'} and
        type(preflight['schema']) is str and
        preflight['schema'] == 'h25-public-runtime-preflight-v2' and
        type(preflight['authenticated_files']) is int and
        preflight['authenticated_files'] == 217 and
        preflight['native_private_access'] is False and
        preflight['cached_admission'] is False)
