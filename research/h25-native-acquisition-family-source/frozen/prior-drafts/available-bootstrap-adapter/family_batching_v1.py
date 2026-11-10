"""Source-owned family judgment and immutable scheduling envelopes.

The authenticated actual original outer parent must bind/configure these exact
sources before import, under the inherited trusted startup/no-mutator premise.
No input dictionary creates authority. No dispatcher runs at import. The actual
stage/command/source closure/funding/resource grants are intentionally absent.
"""
import hashlib
import builtins
import json
import os
import resource
import signal
import sys
import time
from pathlib import Path
import types
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import parent_completion_v1 as parent
import parent_domain_v1 as original_domain
import parent_orchestration_v2 as orchestration
import persistent_replay_v1 as replay
import bootstrap_bindings_v2 as bindings
import component_control_validation_v1 as component_wire
import h25_parent_supervisor as supervisor
import h25_original_queue_v4 as original_queue
import h25_queue4_wrapper as queue_wrapper
import requirement_anchor_v1 as anchor
import configured_inverse_v2 as configured
import offline_replay_v2 as offline

CONFIGURATION = None
SOURCE_REVIEW = None
SCENARIO_REVIEW = None
SOURCE_BINDING_REVIEW = None
RESOURCE_FIT_REVIEW = None
FUNDING = None
EXECUTION_APPROVAL = None
_OWNERS = []
_SOURCE_BINDINGS = [None]
LAUNCH_FLAGS = original_queue.LAUNCH_FLAGS
_BORROWED_BUILTINS = (builtins.abs, builtins.sum)
_CLOCK = time.monotonic
_TYPE = type
_MAX_ENVELOPES = 256
_MAX_CHILDREN_PER_ENVELOPE = 2
_MAX_CASES = 512
_MAX_CHAIN_RECORDS = 4096
_MAX_CHAIN_BYTES = 4 * 1024 * 1024
_MAX_RAW_BYTES_PER_CASE = 256 * schema.FILE_BYTES + 2 * schema.LOG_BYTES
_MAX_PROGRAM_TESTS = 256
_MAX_CASES_PER_FAMILY = 512
_ALIASES = (queue_wrapper.RootProxy, original_queue.require_trusted_launch,
            original_queue.digest, original_queue.record_time, supervisor.run_root,
            component_wire.validate_protocol, copying.write_once, copying.read_verified_complete_v3)


def _source_default(node, namespace, definitions, active=()):
    """Evaluate the finite literal/default grammar, never arbitrary Python."""
    ast = bindings.ast
    if type(node) is ast.Name:
        schema.need(node.id in definitions and node.id not in active and len(active) < 32,
                    'default does not name a finite source constant')
        value = _source_default(definitions[node.id], namespace, definitions, active + (node.id,))
        schema.need(bindings._data(namespace[node.id]) == bindings._data(value),
                    'source constant used by a default changed')
        return value
    if type(node) is ast.BinOp:
        left = _source_default(node.left, namespace, definitions, active)
        right = _source_default(node.right, namespace, definitions, active)
        schema.need(type(left) is int and type(right) is int,
                    'default arithmetic must use exact source integers')
        if type(node.op) is ast.Add:
            value = left + right
        elif type(node.op) is ast.Sub:
            value = left - right
        elif type(node.op) is ast.Mult:
            value = left * right
        elif type(node.op) is ast.LShift:
            schema.need(0 <= right <= 127, 'source default shift bound')
            value = left << right
        else:
            raise schema.EpochStop('unsupported source default expression')
        schema.need(value.bit_length() <= 128, 'source default integer bound')
        return value
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        raise schema.EpochStop('nonliteral default requires another independently reviewed provider')
    bindings._data(value)
    return value


def _source_objects(module, pin, raw, exact_modules):
    """Use the inspected original bootstrap verifier, with explicit imports.

    The predecessor's source_bindings_v3 body is not substituted by a guessed
    API. This reached adapter uses the actual available three-result provider.
    Both import forms retain the exact source module and imported object.
    """
    tree, functions, classes = bindings._source_objects(module, pin, raw, exact_modules)
    namespace = bindings._namespace(module)
    if namespace['__name__'] in ('family_batching_v1', 'requirement_anchor_v1',
                                'offline_replay_v2', 'bootstrap_bindings_v2'):
        definitions = {node.targets[0].id: node.value for node in tree.body
            if type(node) is bindings.ast.Assign and len(node.targets) == 1 and
                type(node.targets[0]) is bindings.ast.Name}
        for node in tree.body:
            if type(node) is bindings.ast.FunctionDef:
                function = namespace[node.name]
                defaults = tuple(_source_default(v, namespace, definitions) for v in node.args.defaults) or None
                keywords = {arg.arg: _source_default(value, namespace, definitions)
                    for arg, value in zip(node.args.kwonlyargs, node.args.kw_defaults) if value is not None} or None
                schema.need(bindings._data(function.__defaults__) == bindings._data(defaults) and
                    bindings._data(function.__kwdefaults__) == bindings._data(keywords),
                    'actual new-source defaults do not derive from the selected source')
    imports = []
    for node in tree.body:
        if type(node) not in (bindings.ast.Import, bindings.ast.ImportFrom):
            continue
        if type(node) is bindings.ast.ImportFrom:
            schema.need(node.level == 0, 'relative source import is not admitted')
        for alias in node.names:
            schema.need(alias.name != '*', 'star source import is not admitted')
            source_name = alias.name if type(node) is bindings.ast.Import else node.module
            source_module = exact_modules.get(source_name)
            schema.need(type(source_module) is types.ModuleType, 'actual source import owner absent')
            if type(node) is bindings.ast.Import:
                local_name = alias.asname or alias.name.split('.')[0]
                if alias.asname is None and '.' in alias.name:
                    source_module = exact_modules.get(alias.name.split('.')[0])
                expected = source_module
                member = None
            else:
                local_name = alias.asname or alias.name
                member = alias.name
                expected = bindings._namespace(source_module).get(member)
            schema.need(expected is not None and namespace.get(local_name) is expected,
                        'actual source import identity differs')
            imports.append((namespace, local_name, source_module, member, expected))
    return tree, functions, classes, tuple(imports)


def _imports_unchanged(imports):
    for namespace, local_name, source_module, member, expected in imports:
        schema.need(namespace.get(local_name) is expected and
            (source_module is expected if member is None else
             bindings._namespace(source_module).get(member) is expected),
            'source import owner or imported object changed')


def _gate(original=None):
    schema.need(_SOURCE_BINDINGS[0] is not None, 'actual independently authenticated new-source seal required')
    _check_source_bindings(original)
    schema.exact(CONFIGURATION, ('normal', 'optimized'))
    for pin in CONFIGURATION.values():
        schema.blob(pin, schema.RECORD_BYTES)
    for value, label in ((SOURCE_REVIEW, 'SOURCE_REVIEW'), (SCENARIO_REVIEW, 'SCENARIO_REVIEW'),
        (SOURCE_BINDING_REVIEW, 'SOURCE_BINDING_REVIEW'), (RESOURCE_FIT_REVIEW, 'RESOURCE_FIT_REVIEW'),
        (FUNDING, 'FUNDING'), (EXECUTION_APPROVAL, 'EXECUTION_APPROVAL')):
        schema.need(type(value) is tuple and len(value) == 2 and type(value[0]) is str and value[0] == label,
                    'batch/family external source and actual execution gate absent')
        schema.digest(value[1])
    actual = (queue_wrapper.RootProxy, original_queue.require_trusted_launch,
              original_queue.digest, original_queue.record_time, supervisor.run_root,
              component_wire.validate_protocol, copying.write_once, copying.read_verified_complete_v3)
    schema.need(all(a is b for a, b in zip(actual, _ALIASES)), 'source-fixed operational function binding changed')
    schema.need(_CLOCK is time.monotonic and _TYPE is type, 'batch primitive identity changed')
    _borrowed_bindings_unchanged()


def seal_source_bindings(original_parent, original_orchestrator, externally_authenticated_manifest_pin):
    """Same inherited before-use outer authentication premise as bootstrap V2.

    The caller must authenticate this manifest and these exact immutable sources
    BEFORE import/entry. Hashes supplied by an untrusted caller grant nothing.
    Installation is consumed before acquisition and can never be retried.
    """
    original = parent._state(original_parent)
    parent._guard(original)
    orchestration._guard(orchestration._state(original_orchestrator))
    schema.need(_SOURCE_BINDINGS[0] is None, 'new-source binding attempt already consumed')
    state = {'original': original, 'phase': 'PREPARING', 'rows': [], 'manifest': externally_authenticated_manifest_pin}
    _SOURCE_BINDINGS[0] = state
    try:
        schema.blob(externally_authenticated_manifest_pin, schema.RECORD_BYTES)
        schema.need(not externally_authenticated_manifest_pin['identity']['mode'] & 0o222, 'immutable externally authenticated new-source manifest required')
        raw = copying.read_verified_complete_v3(externally_authenticated_manifest_pin, schema.RECORD_BYTES,
                                               error_owner=original['errors'])
        manifest = bindings._document(raw)
        schema.exact(manifest, ('schema', 'modules', 'source_review_sha256'))
        schema.need(manifest['schema'] == 'h25-family-new-source-manifest-v1' and
                    manifest['source_review_sha256'] == SOURCE_REVIEW[1], 'new source review/manifest differs')
        schema.exact(manifest['modules'], ('family_batching_v1', 'requirement_anchor_v1', 'offline_replay_v2', 'bootstrap_bindings_v2'))
        module_map = {name: module for name,module in tuple(sys.modules.items())
                      if type(name) is str and type(module) is types.ModuleType}
        for name in ('family_batching_v1', 'requirement_anchor_v1', 'offline_replay_v2', 'bootstrap_bindings_v2'):
            module = sys.modules[name]; item = manifest['modules'][name]
            schema.exact(item, ('source', 'inverse'))
            pin, inverse = item['source'], item['inverse']
            schema.blob(pin)
            schema.need(not pin['identity']['mode'] & 0o222, 'immutable new-source image required')
            if name == 'offline_replay_v2':
                schema.need(inverse['template_sha256'] == '533afcfed5e31d127383b1d53098446d8e2a0ced1ade3f91e722d9be17b2c9a0',
                            'exact reviewed V4 offline data helper required')
            schema.need(inverse['module'] == name and inverse['configured_sha256'] == pin['sha256'],
                        'exact new configured source binding differs')
            source = copying.read_verified_complete_v3(pin, 8388608, error_owner=original['errors'])
            configured.verify_configured_source(source, inverse)
            tree, functions, classes, imports = _source_objects(module, pin, source, module_map)
            namespace = bindings._namespace(module)
            literals = []
            for node in tree.body:
                if type(node) is bindings.ast.Assign and len(node.targets) == 1 and type(node.targets[0]) is bindings.ast.Name:
                    key = node.targets[0].id
                    if name == 'family_batching_v1' and key in ('_OWNERS', '_SOURCE_BINDINGS'):
                        continue  # exact source-owned registries; identities still captured
                    if name == 'bootstrap_bindings_v2' and key == '_INSTALLATIONS':
                        continue  # genuine before-capture installation registry
                    try:
                        value = bindings.ast.literal_eval(node.value)
                    except (ValueError, TypeError, SyntaxError):
                        continue
                    schema.need(bindings._data(namespace[key]) == bindings._data(value), 'literal source binding differs')
                    literals.append((key, bindings._data(value)))
            state['rows'].append((module, pin, namespace, tuple(namespace.items()), functions, classes, imports, tuple(literals)))
        state['phase'] = 'SEALED'
        _check_source_bindings()
        return None
    except BaseException as error:
        state['phase'] = 'STOP'
        if original['unknown_owner']['primary'][0] is None:
            original['unknown_owner']['primary'][0] = error
        original['unknown_owner']['quarantine'][0] = True
        raise


def _check_source_bindings(current_original=None):
    state = _SOURCE_BINDINGS[0]
    schema.need(state is not None and state['phase'] == 'SEALED', 'new-source seal is absent/stopped')
    original = state['original'] if current_original is None else current_original
    parent._guard(original)
    schema.need(original['unknown_owner'] is state['original']['unknown_owner'], 'source seal shared owner differs')
    copying.verify(state['manifest'], error_owner=original['errors'])
    for module,pin,namespace,items,functions,classes,imports,literals in state['rows']:
        schema.need(bindings._namespace(module) is namespace and len(namespace) == len(items), 'new-source namespace changed')
        for key,value in items:
            schema.need(namespace.get(key) is value, 'new-source global identity changed')
        for record in functions:
            bindings._function_check(record)
        bindings._classes_unchanged(classes)
        _imports_unchanged(imports)
        for key,snapshot in literals:
            schema.need(bindings._data(namespace[key]) == snapshot, 'new-source literal content changed')
        copying.verify(pin, error_owner=original['errors'])
    return None


def _entry(owner):
    schema.need(type(owner) is object, 'exact live family owner required')
    for token, state in _OWNERS:
        if token is owner:
            return state
    raise schema.EpochStop('unregistered family owner; records cannot restore authority')


def _stop(state, error):
    if state['original']['unknown_owner']['primary'][0] is None:
        state['original']['unknown_owner']['primary'][0] = error
    state['original']['unknown_owner']['quarantine'][0] = True
    if state['primary'][0] is None:
        state['primary'][0] = error
    state['phase'] = 'STOP'


def _fresh(state):
    _gate(state['original'])
    parent._guard(state['original'])
    orchestration._guard(orchestration._state(state['orchestrator']))
    schema.need(state['pid'] == os.getpid() and state['phase'] != 'STOP', 'family owner moved or stopped')
    schema.need(state['original']['unknown_owner'] is parent._UNKNOWN_OWNER and
                state['original']['unknown_owner']['primary'][0] is None and
                state['original']['unknown_owner']['quarantine'][0] is False,
                'actual original shared owner requires teardown')
    schema.need(_CLOCK() <= state['original']['shared_deadline'], 'original complete parent deadline exhausted')
    schema.need(_canonical(state['plan']) == state['plan_raw'], 'private batch/family plan changed')
    if state['source_binding'] is not None:
        for module, pin, namespace, items, functions, classes, imports, literals in state['source_binding']:
            schema.need(bindings._namespace(module) is namespace and len(namespace) == len(items),
                        'operational source namespace census changed')
            for key, value in items:
                schema.need(namespace.get(key) is value, 'operational source binding changed')
            for record in functions:
                bindings._function_check(record)
            bindings._classes_unchanged(classes)
            _imports_unchanged(imports)
            for key,snapshot in literals:
                schema.need(bindings._data(namespace[key]) == snapshot, 'operational source literal dependency changed')
            copying.verify(pin, error_owner=state['original']['errors'])


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii') + b'\n'


def _read(state, pin, limit=_MAX_CHAIN_BYTES):
    _fresh(state)
    raw = copying.read_verified_complete_v3(pin, limit, error_owner=state['original']['errors'])
    _fresh(state)
    return raw


def _append(state, kind, identity, payload):
    """Same externally anchored registry; no deletion/rotation or saved PASS."""
    _fresh(state)
    replay._guard(replay._entry(state['replay']))
    schema.need(len(state['records']) < _MAX_CHAIN_RECORDS, 'batch durable chain capacity exhausted')
    for pin in state['records']:
        _read(state, pin)
    sequence = state['sequence']
    state['sequence'] += 1  # burn before serialization/acquisition, never restored
    key = hashlib.sha256(_canonical({'mode': state['mode'], 'identity': identity, 'kind': kind})).hexdigest()
    path = state['registry'] + '/family-batch-' + key + '.json'
    value = {'schema': 'h25-family-batch-chain-v1', 'plan_sha256': state['plan_pin']['sha256'],
             'mode': state['mode'], 'kind': kind, 'identity': identity, 'sequence': sequence,
             'previous': state['head'], 'payload': payload, 'runtime_authority': False, 'saved_PASS': False}
    raw = _canonical(value)
    schema.need(len(raw) <= _MAX_CHAIN_BYTES, 'complete batch record exceeds reviewed4MiB writer domain')
    pin = copying.write_observation_once_v3(path, raw, error_owner=state['original']['errors'])
    schema.need(_read(state, pin) == raw, 'complete durable batch readback differs')
    state['records'].append(pin)
    state['head'] = pin
    return pin


def _plain(value, depth=0):
    """Closed native data, including exact typed protocol projections only."""
    schema.need(depth <= 64, 'oracle traversal depth exceeded')
    kind = type(value)
    if value is None or kind is str or kind is bytes or kind is int or kind is bool:
        return
    schema.need(kind is tuple or kind is list or kind is dict, 'foreign oracle input rejected')
    schema.need(len(value) <= 8192, 'oracle collection bound exceeded')
    if kind is dict:
        for key in value:
            schema.need(type(key) is str, 'foreign oracle key')
        schema.need('opaque_observation_tag' not in value, 'opaque runtime identity has no independent parent oracle')
    for item in value.values() if kind is dict else value:
        _plain(item, depth + 1)


def _path(value, path):
    schema.need(type(path) is list and len(path) <= 64, 'fixed oracle path bound')
    for key in path:
        if type(value) is dict:
            schema.need(type(key) is str and all(type(k) is str for k in value) and key in value,
                        'required raw oracle field absent')
        else:
            schema.need((type(value) is list or type(value) is tuple) and type(key) is int and
                        0 <= key < len(value), 'required raw oracle index absent')
        value = value[key]
    _plain(value)
    return value


def _equal(actual, expected):
    _plain(actual); _plain(expected)
    if type(actual) is not type(expected):
        return False
    if type(actual) is dict:
        return set(actual) == set(expected) and all(_equal(actual[k], expected[k]) for k in actual)
    if type(actual) is tuple or type(actual) is list:
        return len(actual) == len(expected) and all(_equal(a, b) for a, b in zip(actual, expected))
    return actual == expected


def _expected_literal(node, count, depth=0):
    # JSON catalog budget327693 counts >=2 nodes per typed native node.
    count[0] += 1
    schema.need(count[0] <= 163846 and depth <= 32 and type(node) is list and
                len(node) in (1, 2), 'bounded exact typed expected literal required')
    tag = node[0]
    schema.need(type(tag) is str, 'expected exact tag string required')
    if tag == 'none':
        schema.need(len(node) == 1, 'expected none arity')
        return None
    schema.need(len(node) == 2 and type(tag) is str, 'expected typed literal shape')
    value = node[1]
    if tag == 'bool':
        schema.need(type(value) is bool, 'expected bool type'); return value
    if tag == 'int':
        schema.need(type(value) is int and value.bit_length() <= 128, 'expected int type'); return value
    if tag == 'str':
        schema.need(type(value) is str and len(value) <= 2097152, 'expected string bound'); return value
    if tag == 'bytes':
        schema.need(type(value) is str and len(value) <= 2097152 and len(value) % 2 == 0 and
            all(c in '0123456789abcdef' for c in value), 'expected bytes encoding'); return bytes.fromhex(value)
    schema.need(type(value) is list and len(value) <= 8192, 'expected literal collection bound')
    if tag == 'tuple' or tag == 'list':
        result = [_expected_literal(x, count, depth+1) for x in value]
        return tuple(result) if tag == 'tuple' else result
    schema.need(tag == 'dict', 'expected literal tag unsupported')
    result = {}
    for pair in value:
        schema.need(type(pair) is list and len(pair) == 2 and type(pair[0]) is str and pair[0] not in result,
                    'expected literal exact key shape')
        result[pair[0]] = _expected_literal(pair[1], count, depth+1)
    return result


def _contract_shape(contract, mode, scenario_review):
    schema.exact(contract, ('unit_id', 'body_source', 'body_sha256', 'original_requirement_sha256',
        'scenario_id', 'occurrence', 'role', 'mode', 'event_contract', 'tests', 'reach',
        'requires_opaque_identity', 'scenario_review_sha256', 'delivery_kind'))
    schema.need(contract['mode'] == mode and contract['scenario_review_sha256'] == scenario_review,
                'case mode and independently admitted raw program differ')
    schema.need(contract['requires_opaque_identity'] is False and
        contract['delivery_kind'] != 'NATIVE_OR_OPAQUE_REQUIRED',
        'unsupported runtime identity/native delivery requires genuine new witness and source review')
    schema.need(type(contract['tests']) is list and 1 <= len(contract['tests']) <= _MAX_PROGRAM_TESTS,
                'independent raw predicate program absent')
    for test in contract['tests']:
        schema.exact(test, ('source', 'raw_ordinal', 'path', 'operation', 'expected'))
        schema.choice(test['source'], ('RAW', 'OWNED'))
        schema.choice(test['operation'], ('EXACT_EQUAL', 'EXACT_TYPE', 'EXACT_BYTES_SOURCE'))
        schema.need(type(test['path']) is list and len(test['path']) <= 64, 'case predicate path exceeds source domain')
        if test['operation'] == 'EXACT_EQUAL':
            _expected_literal(test['expected'], [0])
        elif test['operation'] == 'EXACT_BYTES_SOURCE':
            schema.need(test['source'] == 'RAW', 'original native bytes comparison requires RAW')
            schema.blob(test['expected'])
            schema.need(not test['expected']['identity']['mode'] & 0o222, 'independent expected bytes source must be immutable')
        else:
            schema.need(type(test['expected']) is str, 'exact expected type label required')
    return None


def _raw_node(event, path):
    schema.need(type(path) is list and 1 <= len(path) <= 64, 'typed raw path required')
    first = path[0]
    if event['kind'] == 'RAW_RAISE' and first == 'exception_type':
        schema.need(len(path) == 1, 'exception class string path is atomic')
        return ['str', event['payload']['exception_type']]
    schema.need(type(first) is str and first in event['payload'], 'actual typed raw root missing')
    node = event['payload'][first]
    for key in path[1:]:
        schema.need(type(node) is list and len(node) == 2 and type(node[0]) is str, 'typed raw descendant missing')
        if node[0] == 'dict':
            schema.need(type(key) is str, 'typed dict path key type')
            matches = [p[1] for p in node[1] if p[0] == key]
            schema.need(len(matches) == 1, 'typed raw dictionary key missing/repeated')
            node = matches[0]
        else:
            schema.need(node[0] in ('list','tuple') and type(key) is int and 0 <= key < len(node[1]),
                        'typed raw sequence index invalid')
            node = node[1][key]
    schema.need(type(node) is list and type(node[0]) is str, 'selected native raw tag missing')
    return node


def _match_raw(node, expected, state, artifacts, depth=0):
    schema.need(depth <= 32 and type(node) is list and type(expected) is list and
        type(node[0]) is str and type(expected[0]) is str, 'exact native raw/expected tag required')
    tag = node[0]
    schema.need(tag not in ('opaque-process-local-object-not-authority',
        'original-registered-ParentEpoch-not-serializable','original-ErrorOwner-not-serializable'),
        'opaque original runtime identity cannot be independently reconstructed')
    if tag != expected[0]:
        return False
    if tag == 'none':
        return len(node) == len(expected) == 1
    if tag == 'bytes':
        wanted = _expected_literal(expected, [0])
        matches = [p for p in artifacts if p['bytes'] == node[1] and p['sha256'] == node[2]]
        schema.need(matches, 'actual full native bytes not retained separately')
        return _read(state, matches[0], schema.FILE_BYTES) == wanted
    if tag == 'dict':
        actual_keys = [p[0] for p in node[1]]; expected_keys = [p[0] for p in expected[1]]
        if set(actual_keys) != set(expected_keys):
            return False
        expected_map = dict(expected[1])
        return all(_match_raw(value, expected_map[key], state, artifacts, depth+1) for key,value in node[1])
    if tag == 'tuple' or tag == 'list':
        return len(node[1]) == len(expected[1]) and all(_match_raw(a,z,state,artifacts,depth+1)
            for a,z in zip(node[1],expected[1]))
    return _equal(component_wire._typed(node), _expected_literal(expected,[0]))


def _judge(protocol, contract, owned_facts, state, artifacts):
    """Recompute predicates from RAW and actual parent ownership, never ORACLE truth."""
    schema.exact(contract, ('unit_id', 'body_source', 'body_sha256', 'original_requirement_sha256',
        'scenario_id', 'occurrence', 'role', 'mode', 'event_contract', 'tests', 'reach',
        'requires_opaque_identity', 'scenario_review_sha256', 'delivery_kind'))
    schema.choice(contract['delivery_kind'], ('ORIGINAL_PYTHON_BEHAVIOR', 'FIXED_PYTHON_PORT', 'NATIVE_OR_OPAQUE_REQUIRED'))
    schema.need(contract['delivery_kind'] != 'NATIVE_OR_OPAQUE_REQUIRED',
                'actual native/opaque delivery witness unavailable; Python port cannot substitute')
    schema.need(contract['requires_opaque_identity'] is False,
                'independent runtime identity witness/judge not implemented; family remains blocked')
    schema.digest(contract['scenario_review_sha256'])
    schema.need(protocol['unit_id'] == contract['unit_id'] and protocol['mode'] == contract['mode'] and
                protocol['protocol_is_case_PASS'] is False and protocol['family_completion'] is False,
                'unit protocol scope cannot become family authority')
    actual_contract = [{'ordinal': e['ordinal'], 'kind': e['kind'], 'target': e['target'],
        'raw_ordinal': e['payload']['raw_ordinal'] if e['kind'] == 'ORACLE' else None} for e in protocol['events']]
    schema.need(_equal(actual_contract, contract['event_contract']), 'raw/oracle target/order/occurrence differs')
    reach = contract['reach']
    schema.exact(reach, ('raw_ordinal', 'target', 'site_path', 'site', 'occurrence_path', 'occurrence', 'role_path'))
    schema.integer(reach['raw_ordinal'], 1, 8190)
    event = protocol['events'][reach['raw_ordinal']]
    schema.need(event['kind'] in ('RAW_RETURN', 'RAW_RAISE') and event['target'] == reach['target'],
                'required actual target was not reached')
    schema.need(_equal(_path(event['decoded'], reach['site_path']), reach['site']) and
                _equal(_path(event['decoded'], reach['occurrence_path']), reach['occurrence']),
                'earlier rejection cannot stand in for a later selected fault occurrence')
    if reach['role_path'] is None:
        schema.need(contract['role'] == 'NO_ROLE', 'role-specific scenario has no raw role witness')
    else:
        schema.need(_equal(_path(event['decoded'], reach['role_path']), contract['role']), 'actual raw role differs')
    tests = contract['tests']
    schema.need(type(tests) is list and 1 <= len(tests) <= _MAX_PROGRAM_TESTS,
                'complete source-reviewed independent raw predicates absent')
    for test in tests:
        schema.exact(test, ('source', 'raw_ordinal', 'path', 'operation', 'expected'))
        schema.choice(test['source'], ('RAW', 'OWNED'))
        if test['source'] == 'RAW':
            schema.integer(test['raw_ordinal'], 1, 8190)
            raw = protocol['events'][test['raw_ordinal']]
            schema.need(raw['kind'] in ('RAW_RETURN', 'RAW_RAISE'), 'oracle cannot read child ORACLE/terminal flags')
            selected_node = _raw_node(raw, test['path'])
            if test['operation'] == 'EXACT_BYTES_SOURCE':
                schema.need(selected_node[0] == 'bytes' and any(_equal(p, test['expected']) for p in owned_facts['source']),
                            'independent expected byte source absent or native return is not bytes')
                matches = [p for p in artifacts if p['bytes'] == selected_node[1] and p['sha256'] == selected_node[2]]
                schema.need(matches and _read(state,matches[0],schema.FILE_BYTES) ==
                    _read(state,test['expected'],schema.FILE_BYTES), 'complete original byte value differs')
                continue
            if test['operation'] == 'EXACT_EQUAL':
                schema.need(_match_raw(selected_node, test['expected'], state, artifacts),
                            'independent exact native raw predicate failed')
                continue
            labels = {'NoneType':'none','bool':'bool','int':'int','str':'str','bytes':'bytes',
                      'tuple':'tuple','list':'list','dict':'dict'}
            schema.need(type(test['expected']) is str and test['expected'] in labels and
                selected_node[0] == labels[test['expected']], 'independent original native type differs')
            continue
        else:
            schema.need(test['raw_ordinal'] is None, 'ownership predicate cannot supply a child raw ordinal')
            actual = _path(owned_facts, test['path'])
        schema.choice(test['operation'], ('EXACT_EQUAL', 'EXACT_TYPE', 'EXACT_BYTES_SOURCE'))
        if test['operation'] == 'EXACT_TYPE':
            allowed = {'NoneType': type(None), 'bool': bool, 'int': int, 'str': str, 'bytes': bytes,
                       'tuple': tuple, 'list': list, 'dict': dict}
            schema.need(type(test['expected']) is str and test['expected'] in allowed and
                        type(actual) is allowed[test['expected']], 'independent exact raw type predicate failed')
        else:
            schema.need(_equal(actual, _expected_literal(test['expected'], [0])), 'independent original raw predicate failed')
    return None


def _distinct_science_lock(operational_root):
    # Never release or replace either owner's locks. A nested fixture directory
    # is legal when its actual science lock is a distinct file.
    descriptor = parent._PROCESS[0]['locks'][1]
    actual = os.fstat(descriptor)
    try:
        operational = os.stat(operational_root / 'runtime/science.lock', follow_symlinks=False)
    except FileNotFoundError:
        return None  # metadata-only absence, under the original single-writer premise
    schema.need((actual.st_dev, actual.st_ino) != (operational.st_dev, operational.st_ino),
                'operational runner would contend on its own genuine parent science lock')
    return None


def _validate_operational_binding(state):
    policy = offline.decode(_read(state, state['plan']['source_policy']))
    schema.exact(policy, ('schema', 'sources', 'bootstrap_review_sha256'))
    schema.need(policy['schema'] == 'h25-family-operational-source-map-v1' and
        policy['bootstrap_review_sha256'] == SOURCE_BINDING_REVIEW[1], 'actual operational binding review differs')
    schema.exact(policy['sources'], ('queue', 'wrapper', 'supervisor', 'runner', 'envelope', 'validator'))
    modules = {'queue': original_queue, 'wrapper': queue_wrapper, 'supervisor': supervisor, 'validator': component_wire}
    expected_modules = {name: module for name, module in tuple(sys.modules.items())
                        if type(name) is str and type(module) is types.ModuleType}
    records = []
    for name, pin in policy['sources'].items():
        schema.blob(pin)
        schema.need(pin['sha256'] == anchor.OPERATIONAL_SOURCE_PINS[name],
                    'source-authenticated operational queue member differs')
        raw = _read(state, pin)
        if name in modules:
            module = modules[name]
            tree, functions, classes, imports = _source_objects(module, pin, raw, expected_modules)
            namespace = bindings._namespace(module)
            literals = []
            for node in tree.body:
                if type(node) is bindings.ast.Assign and len(node.targets) == 1 and type(node.targets[0]) is bindings.ast.Name:
                    key = node.targets[0].id
                    if module is supervisor and key in ('_GUARD_ATTEMPTS','_PUBLICATION_BINDING'):
                        continue  # fixed new one-shot live registry; identity remains captured
                    try:
                        value = bindings.ast.literal_eval(node.value)
                    except (ValueError,TypeError,SyntaxError):
                        continue
                    schema.need(bindings._data(namespace[key]) == bindings._data(value), 'operational literal source dependency differs')
                    literals.append((key,bindings._data(value)))
            records.append((module, pin, namespace, tuple(namespace.items()), functions, classes, imports, tuple(literals)))
    publication=supervisor._publication_binding()
    schema.need(publication['admission']['source_review_sha256']==SOURCE_REVIEW[1],
        'publication before-capture source admission differs')
    state['source_binding'] = tuple(records)


def _validate_catalog(state, requirements, catalog):
    """Closed original requirement identities and explicit full scenario expansion."""
    schema.need(len(requirements['families']) == 212 and len(requirements['units']) == 86,
                'source-fixed original212/current86 requirement universe differs')
    schema.exact(catalog, ('schema', 'requirements_sha256', 'scenario_review_sha256', 'families'))
    schema.need(catalog['schema'] == 'h25-complete-family-scenario-catalog-v1' and
                catalog['requirements_sha256'] == anchor.REQUIREMENTS_SHA256, 'exact full recipe catalog differs')
    schema.digest(catalog['scenario_review_sha256'])
    schema.need(catalog['scenario_review_sha256'] == SCENARIO_REVIEW[1], 'complete independent scenario review differs')
    expected = {r['identity']: r for r in requirements['families']}
    schema.exact(catalog['families'], tuple(expected))
    units = {u['unit_id']: u for u in requirements['units']}
    cases, family_order, unresolved = {}, [], []
    for requirement in requirements['families']:
        identity = requirement['identity']; item = catalog['families'][identity]
        schema.exact(item, ('original_requirement_sha256', 'expansion_review_sha256', 'required_cases'))
        schema.need(item['original_requirement_sha256'] == requirement['original_requirement_sha256'],
                    'original scenario/recipe identity changed')
        family_order.append(identity)
        if item['required_cases'] is None or item['expansion_review_sha256'] is None:
            unresolved.append(identity)
        if item['required_cases'] is None:
            continue
        if item['expansion_review_sha256'] is not None:
            schema.digest(item['expansion_review_sha256'])
        schema.need(type(item['required_cases']) is list and
                    1 <= len(item['required_cases']) <= _MAX_CASES_PER_FAMILY, 'full ordered scenario expansion missing')
        for case in item['required_cases']:
            schema.exact(case, ('case_id', 'unit_id', 'contract', 'source'))
            schema.text(case['case_id'], 256); schema.text(case['unit_id'], 128)
            schema.need(case['case_id'] not in cases and case['unit_id'] in units,
                        'missing body, duplicate or substituted unit; source successor required')
            unit = units[case['unit_id']]
            schema.need(unit['case_identity'] == identity and case['contract']['unit_id'] == case['unit_id'] and
                case['contract']['original_requirement_sha256'] == requirement['original_requirement_sha256'] and
                case['contract']['body_sha256'] == unit['body_sha256'] and
                case['contract']['body_source']['sha256'] == anchor.COMPONENT_ROOT_SHA256,
                'exact original/current body and scenario linkage differs')
            _contract_shape(case['contract'], state['mode'], catalog['scenario_review_sha256'])
            cases[case['case_id']] = dict(case, family=identity)
    state['requirements'], state['catalog'] = requirements, catalog
    state['cases'], state['family_order'], state['unresolved'] = cases, family_order, tuple(unresolved)
    state['required_case_order'] = list(cases)


def make_family_owner(original_parent, replay_owner, original_orchestrator):
    """Only the original authenticated outer calls this with actual live owners."""
    original = parent._state(original_parent)
    state = None
    try:
        _gate(original); parent._guard(original)
        orchestrator_state = orchestration._state(original_orchestrator)
        orchestration._guard(orchestrator_state)
        mode = original['plan']['mode']
        schema.need(mode in orchestrator_state['mode_states'] and
            orchestrator_state['mode_states'][mode]['parent'] is original_parent and
            orchestrator_state['phase'] == mode, 'actual complete outer mode/parent authority required')
        schema.need(mode != 'optimized' or orchestrator_state['optimized_consumed'] is True,
            'optimized constructor requires consumed live actual normal finite authority')
        schema.need(len(_OWNERS) < 2 and not any(s['mode'] == mode for _, s in _OWNERS), 'family mode replay')
        replay_state = replay._entry(replay_owner); replay._guard(replay_state)
        schema.need(replay_owner is orchestrator_state['replay'],
                    'family replay owner is not the actual enclosing reservation')
        pin = CONFIGURATION[mode]
        raw = copying.read_verified_complete_v3(pin, schema.RECORD_BYTES, error_owner=original['errors'])
        plan = offline.decode(raw)
        schema.exact(plan, ('schema', 'mode', 'requirements', 'catalog', 'registry_directory', 'envelopes',
            'root', 'source_policy', 'supervisor_policy', 'fit', 'evidence_directory'))
        schema.need(plan['schema'] == 'h25-family-batch-plan-v1' and plan['mode'] == mode and
            plan['registry_directory'] == replay_state['configuration']['registry_directory'],
            'actual anchored replay/parent mode differs')
        operational_root = Path(plan['root']).resolve()
        schema.need(operational_root == original_queue.ROOT, 'immutable original queue root differs')
        fixture_root = Path(original['plan']['round_root']).resolve()
        schema.need(operational_root != fixture_root,
            'operational runner and genuine fixture parent science locks must be distinct predeclared roots')
        _distinct_science_lock(operational_root)
        state = {'pid': os.getpid(), 'mode': mode, 'original': original,
            'original_parent': original_parent, 'replay': replay_owner,
            'orchestrator': original_orchestrator, 'phase': 'PREPARING', 'plan_pin': pin, 'plan': plan, 'plan_raw': _canonical(plan),
            'registry': plan['registry_directory'], 'records': [], 'head': None, 'sequence': 0,
            'began': _CLOCK(), 'usage_start': (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)),
            'initial_costs': None, 'accounted': False,
            'checkpoint': 'CONSTRUCTING', 'source_binding': None, 'primary': [None], 'next_envelope': 0, 'attempted': set(), 'captured': {}, 'families': {},
            'seen_generations': set(), 'pending': [None], 'raw_native': [], 'errors': [], 'next_case': 0,
            'mode_token': None, 'mode_completion_pin': None, 'consumed_by': None}
        owner = object(); _OWNERS.append((owner, state))
        requirements_raw = _read(state, plan['requirements'], 1048576)
        schema.need(hashlib.sha256(requirements_raw).hexdigest() == anchor.REQUIREMENTS_SHA256,
                    'original complete recipe universe changed')
        requirements = json.loads(requirements_raw)
        offline._bounded(requirements, [0])
        catalog = offline.decode_wire_v4(_read(state, plan['catalog']))
        _validate_operational_binding(state)
        cap, initial_costs = supervisor.budget(operational_root)
        schema.need(cap == 2400, 'actual approved aggregate cap must remain2400')
        state['initial_costs'] = initial_costs
        schema.need(plan['fit']['complete_parent_milliseconds'] <=
            int((cap - sum(initial_costs.values())) * 1000), 'declared complete allocation exceeds actual remaining charged budget')
        _validate_catalog(state, requirements, catalog)
        _validate_envelopes(state)
        # Every envelope and semantic child generation reserved before dispatch.
        _append(state, 'BATCH_PLAN_RESERVED', original['plan']['epoch_id'], {'cases': state['ordered_cases'],
            'envelopes': [e['envelope_id'] for e in plan['envelopes']], 'restorable': False})
        for envelope in plan['envelopes']:
            for child in envelope['children']:
                _append(state, 'CHILD_RESERVED', child['generation'], {'case_id': child['case_id'],
                    'label': child['queue_case']['label'], 'envelope_id': envelope['envelope_id']})
        state['phase'] = 'READY'
        state['checkpoint'] = 'READY'
        return owner
    except BaseException as error:
        if state is not None:
            _stop(state, error)
        else:
            if original['unknown_owner']['primary'][0] is None:
                original['unknown_owner']['primary'][0] = error
            original['unknown_owner']['quarantine'][0] = True
        raise


def _validate_envelopes(state):
    plan = state['plan']; rows = plan['envelopes']
    schema.need(type(rows) is list and 1 <= len(rows) <= _MAX_ENVELOPES, 'more than256 scheduling envelopes')
    ids, generations, labels, contexts, ordered = set(), set(), set(), set(), []
    private_paths = set()
    total_seconds = 0
    schema.exact(plan['fit'], ('review_sha256', 'complete_parent_milliseconds', 'retained_bytes',
        'per_case_object_bound_review_sha256', 'continuous_outer_guard_sha256'))
    for key in ('review_sha256', 'per_case_object_bound_review_sha256', 'continuous_outer_guard_sha256'):
        schema.digest(plan['fit'][key])
    schema.need(plan['fit']['review_sha256'] == RESOURCE_FIT_REVIEW[1], 'independently reviewed exact resource proof differs')
    schema.integer(plan['fit']['complete_parent_milliseconds'], 1, 2400000)
    schema.integer(plan['fit']['retained_bytes'], 1, 1024 ** 3)
    for envelope in rows:
        schema.exact(envelope, ('envelope_id', 'children', 'milliseconds', 'overhead_milliseconds', 'memory_bytes'))
        schema.label(envelope['envelope_id'])
        schema.need(envelope['envelope_id'] not in ids, 'envelope reused')
        ids.add(envelope['envelope_id'])
        schema.need(type(envelope['children']) is list and 1 <= len(envelope['children']) <= 2,
                    'immutable scheduling envelope child bound exceeded')
        schema.integer(envelope['milliseconds'], 1, 180000)
        schema.integer(envelope['overhead_milliseconds'], 1, 180000)
        schema.integer(envelope['memory_bytes'], 1, 1024 ** 3)
        schema.need(plan['fit']['retained_bytes'] + plan['supervisor_policy']['root_rss_sum_bytes'] <=
            envelope['memory_bytes'], 'combined retained parent plus all child RSS exceeds1GiB envelope')
        charge = envelope['overhead_milliseconds']
        for child in envelope['children']:
            schema.exact(child, ('case_id', 'generation', 'queue_case', 'context_id', 'context_source',
                'root_milliseconds', 'raw_artifacts', 'expected_context', 'source_pins', 'command_sha256', 'context_inverse',
                'entry_source', 'entry_inverse', 'start_marker', 'requirement_source', 'context_configuration', 'guard'))
            schema.text(child['case_id'], 256); schema.label(child['generation']); schema.label(child['context_id'])
            schema.need(child['case_id'] in state['cases'] and child['case_id'] not in ordered and
                child['generation'] not in generations and child['context_id'] not in contexts,
                'missing/duplicate/replayed case, cold context or generation')
            case = child['queue_case']
            schema.need(type(case) is dict and all(type(k) is str for k in case) and
                all(type(case[k]) is str for k in ('stage', 'job', 'label', 'stage_sha256')),
                'exact original queue stage case required')
            schema.need(case['label'] not in labels, 'actual output/receipt label reused')
            schema.integer(child['root_milliseconds'], 1, 180000)
            schema.digest(child['command_sha256'])
            schema.need(type(child['source_pins']) is list and 1 <= len(child['source_pins']) <= 8192,
                        'complete original source inventory exceeds original8192-file bound')
            for pin in child['source_pins']:
                schema.blob(pin)
            requirement = next(r for r in state['requirements']['families'] if r['identity'] == state['cases'][child['case_id']]['family'])
            schema.blob(child['requirement_source'])
            schema.need(child['requirement_source']['sha256'] == requirement['source_sha256'] and
                any(p['path'] == child['requirement_source']['path'] and p['sha256'] == child['requirement_source']['sha256']
                    for p in child['source_pins']), 'original recipe current source missing from full source graph')
            schema.blob(child['context_source']);
            schema.need(child['context_inverse']['module'] == 'component_control_root_v1' and
                child['context_inverse']['template_sha256'] == anchor.COMPONENT_ROOT_SHA256 and
                child['context_inverse']['configured_sha256'] == child['context_source']['sha256'],
                'fixed V4 component context inverse identity differs')
            context_values = configured.verify_configured_source(_read(state, child['context_source'], 8388608), child['context_inverse'])
            context = child['context_configuration']
            if 'CONTEXT_CONFIGURATION' in context_values:
                schema.need(_equal(context_values['CONTEXT_CONFIGURATION'], context), 'source literal and admitted full context differ')
            # Empty None-only inverse is supported for an independently admitted
            # before-capture installer; live marker/context protocol must match.
            schema.exact(context, ('schema','unit_id','mode','receiver_policy','fixture_directory',
                'epoch_export_directory','raw_fixture','parent_plan'))
            schema.need(context['unit_id'] == state['cases'][child['case_id']]['unit_id'] and
                context['mode'] == state['mode'] and context['raw_fixture'] == child['expected_context']['input_raw'] and
                context['receiver_policy'] == child['expected_context']['receiver_policy'],
                'actual configured cold context differs from independently required unit/mode/input/source')
            for key in ('fixture_directory', 'epoch_export_directory'):
                schema.path(context[key])
                schema.need(context[key] not in private_paths, 'actual original cold fixture/export directory reused')
                private_paths.add(context[key])
            schema.blob(context['parent_plan'], schema.RECORD_BYTES)
            schema.need(context['parent_plan']['path'] not in private_paths, 'cold parent configuration path reused')
            private_paths.add(context['parent_plan']['path'])
            guard = child['guard']
            schema.need(type(guard) is dict and _equal(case.get('family_guard'), guard) and
                case.get('family_action_id') == envelope['envelope_id'] and case.get('family_generation') == child['generation'],
                'actual proxy case lacks complete fixed parent guard binding')
            supervisor._guard_binding(guard)
            actual_parent = supervisor.proc(os.getpid())
            schema.need(actual_parent is not None and _equal(guard['parent_generation'],
                {'pid':actual_parent['pid'],'start_ticks':actual_parent['start_ticks']}), 'guard live parent identity differs')
            schema.need(all(guard[k] == value for k,value in (
                ('case_id',child['case_id']),('context_id',child['context_id']),
                ('unit_id',state['cases'][child['case_id']]['unit_id']),('mode',state['mode']),
                ('action_id',envelope['envelope_id']),('generation',child['generation']),
                ('marker_path',child['start_marker']),('context_sha256',hashlib.sha256(_canonical(context)).hexdigest()))) and
                _equal(guard['component_source'],{k:child['context_source'][k] for k in ('path','sha256','bytes')}) and
                _equal(guard['entry_source'],{k:child['entry_source'][k] for k in ('path','sha256','bytes')}) and
                guard['supervisor_source']['sha256'] == anchor.OPERATIONAL_SOURCE_PINS['supervisor'] and
                guard['timeout_milliseconds'] <= child['root_milliseconds'], 'guard exact source/context/action/physical bound differs')
            for name in ('request_path','ack_path','consume_path'):
                for path in (guard[name],guard[name]+'.pending'):
                    schema.need(path not in private_paths, 'one-shot guard publication path reused')
                    private_paths.add(path)
            schema.path(child['start_marker'])
            schema.need(child['start_marker'] not in private_paths, 'pre-target identity artifact path reused')
            private_paths.add(child['start_marker'])
            schema.need(type(child['raw_artifacts']) is list and
                len(child['raw_artifacts']) <= 256, 'complete per-case raw artifact declarations missing')
            raw_max = 2 * schema.LOG_BYTES
            for artifact in child['raw_artifacts']:
                schema.exact(artifact, ('path', 'maximum_bytes', 'role'))
                schema.path(artifact['path']); schema.integer(artifact['maximum_bytes'], 0, schema.FILE_BYTES)
                schema.choice(artifact['role'], ('INPUT_SOURCE', 'OWNED_OUTPUT'))
                if artifact['role'] == 'INPUT_SOURCE':
                    schema.need(artifact['path'] == context['raw_fixture']['path'] or
                        any(p['path'] == artifact['path'] for p in child['source_pins']),
                        'input bytes are not independently pinned current source')
                else:
                    roots = (context['fixture_directory'], context['epoch_export_directory'],
                             plan['root'] + '/runtime/runs/' + case['label'] + '/science')
                    schema.need(any(artifact['path'].startswith(path + '/') for path in roots) and
                        artifact['path'] not in private_paths, 'unit output bytes not separately owned/reused')
                    private_paths.add(artifact['path'])
                raw_max += artifact['maximum_bytes']
            schema.need(raw_max <= _MAX_RAW_BYTES_PER_CASE, 'complete raw/object fit unavailable; do not omit artifacts')
            # Complete record bound, not a shortened pin/path or omitted tail.
            paths = [a['path'] for a in child['raw_artifacts']] + [guard[k] for k in ('request_path','ack_path','consume_path')] + [child['start_marker'],
                plan['root'] + '/runtime/runs/' + case['label'] + '/stdout.txt',
                plan['evidence_directory'] + '/' + case['label'] + '/SUPERVISION.json']
            record_bound = len(_canonical(child['source_pins'])) + sum(12*len(path)+2048 for path in paths) + 262144 + 8192
            schema.need(record_bound <= _MAX_CHAIN_BYTES, 'full child source/raw/owned record does not fit4MiB; no truncation')
            charge += child['root_milliseconds']
            generations.add(child['generation']); contexts.add(child['context_id']); labels.add(case['label'])
            ordered.append(child['case_id'])
        schema.need(charge <= envelope['milliseconds'], 'two full child allocations plus paid overhead do not fit180')
        total_seconds += envelope['milliseconds']
    schema.need(len(ordered) <= _MAX_CASES and ordered == state['required_case_order'], 'case order/tail omitted/substituted')
    outer = orchestration._state(state['orchestrator'])
    actual_actions = [a for a in outer['schedule']['modes'][state['mode']]['actions']
        if a['phase'] == 'finite' and a['kind'] == 'component-envelope']
    schema.need([a['action_id'] for a in actual_actions] == [e['envelope_id'] for e in rows] and
        all(a['role'] == a['source_role'] == a['action_id'] and
            a['receiver_module'] == 'family_batching_v1' and
            a['receiver_function'] == 'run_next_envelope' for a in actual_actions),
        'complete family envelope order differs from the enclosing reserved schedule')
    schema.need(total_seconds <= plan['fit']['complete_parent_milliseconds'] and
        _CLOCK() + plan['fit']['complete_parent_milliseconds'] / 1000 <= state['original']['shared_deadline'],
        'complete schedule exceeds proved original parent/global allocation')
    state['ordered_cases'] = ordered


def _validate_unit_stage(case):
    """Borrowed original queue validation below; scientific branch replaced only."""
    return _validate_original_queue_unit(case)


def _validate_case_source(state, child):
    case = child['queue_case']; root = Path(state['plan']['root'])
    stage = root / 'stages' / case['stage']
    stage_pin = copying.inspect(str(stage / 'STAGE.json'), schema.RECORD_BYTES,
                               error_owner=state['original']['errors'])
    schema.need(stage_pin['sha256'] == case['stage_sha256'], 'exact child immutable stage changed')
    stage_doc = json.loads(_read(state, stage_pin))
    jobs_pin = copying.inspect(str(stage / 'JOBS.json'), schema.RECORD_BYTES, error_owner=state['original']['errors'])
    schema.need(jobs_pin['sha256'] == stage_doc['files']['JOBS.json']['sha256'], 'complete declared jobs source differs')
    job = json.loads(_read(state, jobs_pin))[case['job']]
    schema.need(job.get('entry', 'integration/full_driver.py') == 'integration/full_driver.py' and
        stage_doc['files']['integration/full_driver.py']['sha256'] ==
        'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0',
        'each child must invoke the genuine unchanged Root')
    driver = job['bootstrap']['driver']
    schema.need(stage_doc['files'][driver]['sha256'] == child['entry_source']['sha256'] and
        child['entry_source']['path'] == str(stage / driver) and
        child['entry_inverse']['template_sha256'] == anchor.STAGE_ENTRY_SHA256 and
        job.get('optimized', False) is (state['mode'] == 'optimized'),
        'fixed canonical unit main adapter or actual mode differs')
    entry_values = configured.verify_configured_source(_read(state, child['entry_source']), child['entry_inverse'])
    expected_entry = {'marker_path': child['start_marker'],
        'case_id': child['case_id'], 'context_id': child['context_id'],
        'unit_id': state['cases'][child['case_id']]['unit_id'], 'mode': state['mode'], 'guard':child['guard']}
    if 'START_CONFIGURATION' in entry_values:
        schema.need(_equal(entry_values['START_CONFIGURATION'], expected_entry),
            'fixed pre-target stage entry context/identity binding differs')
    schema.need(child['context_source']['path'].startswith(str(stage) + '/') and
        any(p['path'] == child['context_source']['path'] and p['sha256'] == child['context_source']['sha256']
            for p in child['source_pins']), 'configured canonical unit source absent from whole stage/source custody')
    return None


def _case_observation(state, child, proxy):
    case = child['queue_case']; root = Path(state['plan']['root'])
    folder = root / 'runtime/runs' / case['label']
    raw_path = folder / 'stdout.txt'
    pin = copying.inspect(str(raw_path), schema.LOG_BYTES, error_owner=state['original']['errors'])
    raw = _read(state, pin, schema.LOG_BYTES)
    protocol = component_wire.validate_protocol(raw, state['cases'][child['case_id']]['unit_id'], state['mode'])
    schema.need(_equal(protocol['events'][0]['decoded'], child['expected_context']), 'actual fresh context differs')
    artifacts = []
    for declaration in child['raw_artifacts']:
        artifact = copying.inspect(declaration['path'], declaration['maximum_bytes'], error_owner=state['original']['errors'])
        # Retain/hash every original byte before the parent oracle, even if the
        # wire references only its digest. Bounded scratch is disposed after read.
        _read(state, artifact, declaration['maximum_bytes'] or 1)
        artifacts.append(artifact)
    byte_images = {(p['bytes'], p['sha256']) for p in artifacts}
    _require_full_bytes(protocol['events'], byte_images)
    record = proxy.records[-1]
    schema.need(record['effective_admission'] == 'DEFER_TO_QUEUE_V4' and record['supervision_failure'] is None,
                'actual owned queue child was not admitted after cleanup')
    supervision_path = Path(proxy.evidence) / case['label'] / 'SUPERVISION.json'
    supervision_pin = copying.inspect(str(supervision_path), schema.RECORD_BYTES, error_owner=state['original']['errors'])
    supervision = json.loads(_read(state, supervision_pin))
    live_guard = supervision['before_target_guard']
    schema.need(live_guard['schema'] == 'h25-family-live-parent-guard-v2' and
        live_guard['phase'] == 'CONSUMED_RELEASE' and live_guard['actual_error_retained'] is False and
        live_guard['no_post_exit_substitute'] is True and live_guard['no_retry'] is True and
        _equal(live_guard['parent_generation'],child['guard']['parent_generation']),
        'actual parent did not release observed live source-bound generation before target')
    for name in ('request','ack','consume'):
        guard_pin = copying.inspect(live_guard[name]['path'],supervisor.GUARD_CAP,error_owner=state['original']['errors'])
        schema.need(guard_pin['sha256'] == live_guard[name]['sha256'] and guard_pin['bytes'] == live_guard[name]['bytes'],
                    'complete retained before-target guard packet differs')
        _read(state,guard_pin,supervisor.GUARD_CAP); artifacts.append(guard_pin)
    cleanup = supervision['cleanup']
    for key in ('returncode',):
        schema.integer(supervision[key], 0, 0)
    schema.need(supervision['returncode'] == 0 and supervision['spawn_returned'] is True and
        cleanup['complete'] is True and cleanup['group_empty_proved'] is True and
        cleanup['remaining'] == [] and cleanup['observed_after_root_exit'] == [] and
        cleanup['reaped_adopted'] == [], 'real Root/group cleanup was not complete')
    captured = supervision['captured_root']
    schema.need(type(captured['pid']) is int and type(captured['start_ticks']) is int and
        type(captured['pgid']) is int and type(captured['sid']) is int and
        captured['pgid'] == captured['sid'] == captured['pid'], 'actual owned Root identity differs')
    marker_pin = copying.inspect(child['start_marker'], schema.RECORD_BYTES, error_owner=state['original']['errors'])
    marker = offline.decode(_read(state, marker_pin))
    schema.need(marker['schema'] == 'h25-component-pretarget-identity-v1' and
        marker['case_id'] == child['case_id'] and marker['context_id'] == child['context_id'] and
        marker['unit_id'] == state['cases'][child['case_id']]['unit_id'] and marker['mode'] == state['mode'] and
        marker['component_source_path'] == child['context_source']['path'] and
        _equal(marker['actual_context'], child['context_configuration']), 'actual unit pre-target source/context differs')
    leaf = marker['process']
    schema.need(any(all(row[k] == leaf[k] and type(row[k]) is int and type(leaf[k]) is int
        for k in ('pid', 'ppid', 'pgid', 'sid', 'start_ticks')) for row in cleanup['owned_generations']),
        'self-reported unit PID/start/session absent from actual outer generation-owned kernel history')
    schema.need(all(type(live_guard['live_generation_before_release'][k]) is int and
        live_guard['live_generation_before_release'][k] == leaf[k] for k in ('pid','ppid','pgid','sid','start_ticks')),
        'before-target parent-observed generation differs from final owned unit')
    key = leaf['pid'], leaf['start_ticks']
    schema.need(key not in state['seen_generations'], 'actual owned unit generation reused across cases')
    state['seen_generations'].add(key)
    artifacts.append(marker_pin)
    owned = {'root': captured, 'unit_root': leaf, 'cleanup': cleanup, 'source': child['source_pins'],
             'context_id': child['context_id'], 'command_sha256': child['command_sha256']}
    state['pending'][0]['native'] = (protocol, supervision, marker, tuple(artifacts))
    state['checkpoint'] = 'INDEPENDENT_ORACLE'
    _judge(protocol, state['cases'][child['case_id']]['contract'], owned, state, artifacts)
    for p in [pin, supervision_pin, *artifacts]:
        copying.verify(p, error_owner=state['original']['errors'])
    return {'case_id': child['case_id'], 'generation': child['generation'], 'owned': owned,
        'raw_pins': (pin, supervision_pin, *artifacts), 'protocol_sha256': pin['sha256'],
        'protocol_scope': False, 'family_completion': False, 'complete_finite_union': False}


def _require_full_bytes(value, images, depth=0):
    schema.need(depth <= 64, 'full-byte dependency depth exceeded')
    if type(value) is dict:
        if value.get('full_bytes_required_separately') is True:
            schema.need((value['byte_observation_length'], value['byte_observation_sha256']) in images,
                        'complete original native byte artifact missing')
        for item in value.values():
            _require_full_bytes(item, images, depth + 1)
    elif type(value) is tuple or type(value) is list:
        for item in value:
            _require_full_bytes(item, images, depth + 1)


def run_next_envelope(owner):
    state = _entry(owner)
    try:
        _fresh(state)
        schema.need(state['phase'] == 'READY' and state['next_envelope'] < len(state['plan']['envelopes']),
                    'batch order/replay/phase differs')
        envelope = state['plan']['envelopes'][state['next_envelope']]
        outer = orchestration._state(state['orchestrator'])
        key = (state['mode'], envelope['envelope_id'])
        schema.need(outer['next'] < len(outer['order']) and outer['order'][outer['next']] == key,
                    'actual whole original schedule order differs')
        action = outer['actions'][key]
        own_pin = next(row[1] for row in _SOURCE_BINDINGS[0]['rows']
                       if row[0] is sys.modules[__name__])
        schema.need(action['receiver_module'] == 'family_batching_v1' and
            action['receiver_function'] == 'run_next_envelope' and action['receiver_sha256'] == own_pin['sha256'],
            'actual source-sealed batch receiver differs from fixed complete schedule')
        binding = {'mode': state['mode'], 'epoch_id': state['original']['plan']['epoch_id'],
            'parent_plan_sha256': state['original']['configuration']['plan']['sha256'],
            'source_role': action['source_role'], 'action_id': envelope['envelope_id'],
            'generation': action['generation'], 'receiver_module': 'family_batching_v1',
            'receiver_function': 'run_next_envelope', 'receiver_sha256': own_pin['sha256'],
            'actual': {'family_plan': state['plan_pin'], 'envelope': envelope}}
        schema.need(hashlib.sha256(_canonical(binding)).hexdigest() == action['binding_sha256'],
                    'complete actual source/configuration/envelope binding differs')
        replay.burn_action(state['replay'], state['mode'], envelope['envelope_id'])
        state['next_envelope'] += 1  # consume envelope before fallible work
        _append(state, 'ENVELOPE_CONSUMED', envelope['envelope_id'], {'children': [c['generation'] for c in envelope['children']]})
        deadline = min(_CLOCK() + envelope['milliseconds'] / 1000, state['original']['shared_deadline'])
        root = Path(state['plan']['root'])
        for child in envelope['children']:
            _fresh(state)
            schema.need(child['case_id'] == state['ordered_cases'][state['next_case']] and
                child['case_id'] not in state['attempted'], 'exact global child order differs')
            state['attempted'].add(child['case_id'])
            _append(state, 'CHILD_CONSUMED', child['generation'], {'case_id': child['case_id']})
            for pin in child['source_pins']:
                copying.verify(pin, error_owner=state['original']['errors'])
            copying.verify(child['context_source'], error_owner=state['original']['errors'])
            _distinct_science_lock(root)
            _validate_case_source(state, child)
            policy = dict(state['plan']['supervisor_policy'], root_seconds=child['root_milliseconds'] / 1000)
            schema.need(policy['root_seconds'] <= 180 and policy['root_address_space_bytes'] <= 1024 ** 3 and
                        policy['root_rss_sum_bytes'] <= 1024 ** 3, 'original root resource cap increased')
            proxy = queue_wrapper.RootProxy(supervisor, root, [child['queue_case']],
                Path(state['plan']['evidence_directory']), policy, deadline)
            case = child['queue_case']
            command = ['/usr/bin/python3.12', *supervisor.FLAGS, str(root / 'run_guarded_v3.py'),
                       case['stage'], case['job'], case['label']]
            schema.need(hashlib.sha256(_canonical({'argv': command})).hexdigest() == child['command_sha256'],
                        'actual canonical queue command differs')
            state['pending'][0] = {'proxy': proxy, 'child': child, 'command': command, 'result': None}
            state['checkpoint'] = 'ORIGINAL_ROOT'
            result = proxy.run(command, cwd=root, env=dict(supervisor.ENV), capture_output=True, timeout=190)
            state['pending'][0]['result'] = result
            schema.need(result.returncode == 0 and result.stderr == b'' and proxy.next == 1,
                        'actual source-owned Root proxy rejected child')
            state['checkpoint'] = 'UNIT_RAW_VALIDATION'
            _validate_unit_stage(case)
            observed = _case_observation(state, child, proxy)
            state['checkpoint'] = 'DURABLE_JUDGMENT'
            pin = _append(state, 'CHILD_JUDGED', child['generation'], dict(observed,
                raw_pins=list(observed['raw_pins'])))
            state['captured'][child['case_id']] = {'observed': observed, 'judgment': pin}
            state['pending'][0] = None
            state['next_case'] += 1
            schema.need(_CLOCK() <= deadline, 'complete parent child receiver exceeds envelope180 allocation')
        _append(state, 'ENVELOPE_COMPLETE', envelope['envelope_id'], {'children': len(envelope['children']),
            'whole_family_or_union': False})
        return {'schema': 'h25-scheduling-envelope-observation-v1', 'envelope_id': envelope['envelope_id'],
            'child_judgments': [state['captured'][c['case_id']]['judgment'] for c in envelope['children']],
            'raw_pins': tuple(state['captured'][c['case_id']]['judgment'] for c in envelope['children']),
            'family_completion': False, 'complete_finite_union': False, 'runtime_authority': False}
    except BaseException as error:
        _stop(state, error)
        raise


def seal_family(owner, identity):
    state = _entry(owner)
    try:
        _fresh(state)
        schema.need(type(identity) is str and identity in state['catalog']['families'] and
            identity not in state['families'], 'missing or repeated exact family identity')
        state['checkpoint'] = 'FAMILY_SEAL'
        item = state['catalog']['families'][identity]
        schema.need(identity == state['family_order'][len(state['families'])], 'original full family order differs')
        schema.need(identity not in state['unresolved'] and item['required_cases'] is not None,
                    'missing original scenarios/body/oracle expansion; no unit-to-family promotion')
        required = [c['case_id'] for c in item['required_cases']]
        schema.need(required and all(c in state['captured'] for c in required), 'complete ordered family cases missing')
        for case_id in required:
            record = state['captured'][case_id]
            _read(state, record['judgment'])
            for pin in record['observed']['raw_pins']:
                _read(state, pin, schema.FILE_BYTES)
            for pin in record['observed']['owned']['source']:
                copying.verify(pin, error_owner=state['original']['errors'])
        raw = _append(state, 'FAMILY_COMPLETE', identity, {'original_requirement_sha256': item['original_requirement_sha256'],
            'cases': required, 'judgment_sha256s': [state['captured'][c]['judgment']['sha256'] for c in required],
            'complete_preceding_chain_head': state['head'],
            'saved_PASS': False, 'restorable': False})
        token = object()
        state['families'][identity] = (token, raw)
        return token
    except BaseException as error:
        _stop(state, error)
        raise


def finish_mode(owner):
    state = _entry(owner)
    try:
        _fresh(state)
        schema.need(not state['unresolved'] and len(state['families']) == 212 and
            list(state['families']) == state['family_order'] and
            state['next_envelope'] == len(state['plan']['envelopes']) and
            state['next_case'] == len(state['ordered_cases']) and state['mode_token'] is None,
            'all212 genuine family completions and complete physical schedule required')
        for identity, (token, pin) in state['families'].items():
            _read(state, pin)
        pin = _append(state, 'COMPONENT_UNION_COMPLETE', state['original']['plan']['epoch_id'],
            {'families': state['family_order'], 'full_six_area_finite': False, 'restorable': False})
        state['mode_completion_pin'] = pin
        state['mode_token'] = object(); state['phase'] = 'COMPONENT_COMPLETE'
        return state['mode_token']
    except BaseException as error:
        _stop(state, error)
        raise


def consume_component_union(owner, token):
    state = _entry(owner)
    try:
        _fresh(state)
        schema.need(state['phase'] == 'COMPONENT_COMPLETE' and token is state['mode_token'],
                    'exact live current component union required; no saved receipt authority')
        state['mode_token'] = None; state['phase'] = 'UNION_CONSUMED'
        state['consumed_by'] = state['orchestrator']
        return None
    except BaseException as error:
        _stop(state, error)
        raise


def complete_for_parent(owner, original_parent, original_orchestrator, replay_owner, mode):
    """Seal and consume the original full-family token in the real caller.

    Unit and scheduling-envelope scopes remain false. Every family is sealed
    in its original order; a failed partial seal cannot be retried or restored.
    """
    state = _entry(owner)
    try:
        _fresh(state)
        schema.need(state['original_parent'] is original_parent and
            state['original'] is parent._state(original_parent) and
            state['orchestrator'] is original_orchestrator and
            state['replay'] is replay_owner and state['mode'] == mode and
            state['phase'] == 'READY' and state['consumed_by'] is None and
            not state['families'], 'actual family consumer identity or one-use state differs')
        outer = orchestration._state(original_orchestrator)
        schema.need(outer['mode_states'][mode]['parent'] is original_parent and
            outer['replay'] is replay_owner and outer['phase'] == mode,
            'family consumer is not the actual reached mode owner')
        for identity in state['family_order']:
            seal_family(owner, identity)
        token = finish_mode(owner)
        consume_component_union(owner, token)
        return verify_consumed_union(owner, original_parent, original_orchestrator, replay_owner, mode)
    except BaseException as error:
        _stop(state, error)
        raise


def verify_consumed_union(owner, original_parent, original_orchestrator, replay_owner, mode):
    """Currentness of a consumed live capability; this never restores one."""
    state = _entry(owner)
    try:
        _fresh(state)
        schema.need(state['original_parent'] is original_parent and
            state['original'] is parent._state(original_parent) and
            state['orchestrator'] is original_orchestrator and
            state['consumed_by'] is original_orchestrator and
            state['replay'] is replay_owner and state['mode'] == mode and
            state['phase'] == 'UNION_CONSUMED' and state['mode_token'] is None and
            not state['unresolved'] and len(state['families']) == 212 and
            list(state['families']) == state['family_order'] and
            state['next_envelope'] == len(state['plan']['envelopes']) and
            state['next_case'] == len(state['ordered_cases']) and
            tuple(state['captured']) == tuple(state['ordered_cases']) and
            state['pending'][0] is None and state['mode_completion_pin'] is not None,
            'no complete same-operation consumed family union')
        for pin in state['records']:
            _read(state, pin)
        for identity in state['family_order']:
            _read(state, state['families'][identity][1])
        for case_id in state['ordered_cases']:
            captured = state['captured'][case_id]
            _read(state, captured['judgment'])
            for pin in captured['observed']['raw_pins']:
                _read(state, pin, schema.FILE_BYTES)
            for pin in captured['observed']['owned']['source']:
                copying.verify(pin, error_owner=state['original']['errors'])
        _read(state, state['mode_completion_pin'])
        # The returned immutable pin is evidence, never the consumed live token.
        return state['mode_completion_pin']
    except BaseException as error:
        _stop(state, error)
        raise


def stop_evidence(owner):
    state = _entry(owner)
    return state['primary'], state['pending'], tuple(state['errors']), tuple(state['records'])


# Byte-borrowed queue verification helpers; immutable source binding required.
ROOT = original_queue.ROOT
need = original_queue.need
digest = original_queue.digest
record_time = original_queue.record_time
require_trusted_launch = original_queue.require_trusted_launch

def _borrowed_bindings_unchanged():
    # Complete free-global audit of the byte-borrowed validator, including
    # nested comprehension code. No hidden configuration/builtin injection.
    schema.need(ROOT is original_queue.ROOT and need is original_queue.need and
        digest is original_queue.digest and record_time is original_queue.record_time and
        require_trusted_launch is original_queue.require_trusted_launch and
        json is original_queue.json and Path is original_queue.Path and
        LAUNCH_FLAGS is original_queue.LAUNCH_FLAGS, 'borrowed validator global identity changed')
    schema.need(type(LAUNCH_FLAGS) is tuple and len(LAUNCH_FLAGS) == 4 and
        all(type(v) is str for v in LAUNCH_FLAGS) and LAUNCH_FLAGS == ('-S','-s','-P','-B'),
        'borrowed validator exact authenticated launch flags differ')
    schema.need(builtins.abs is _BORROWED_BUILTINS[0] and builtins.sum is _BORROWED_BUILTINS[1],
        'borrowed validator builtin identity changed')


def _validate_original_queue_unit(case):
    _borrowed_bindings_unchanged()
    stage = ROOT / 'stages' / case['stage']
    stage_hash, _ = digest(stage / 'STAGE.json')
    need(stage_hash == case['stage_sha256'], 'Reviewed stage changed')
    declared = json.loads((stage / 'STAGE.json').read_bytes())
    folder = ROOT / 'runtime/runs' / case['label']
    receipt = json.loads((folder / 'receipt.json').read_bytes())
    start = json.loads((folder / 'START.json').read_bytes())
    for key, value in start.items():
        need(receipt.get(key) == value, 'START differs from receipt: ' + key)
    need(receipt['stage_sha256'] == stage_hash, 'Receipt stage differs')
    need(receipt['runner_sha256'] == declared['runner_sha256'] == digest(ROOT / 'run_guarded_v3.py')[0], 'Runner identity differs')
    need(receipt['budget_phase_sha256'] == digest(ROOT / 'control/EXECUTION-PHASE.json')[0], 'Budget identity differs')
    need(receipt['parent_launch'] == require_trusted_launch(), 'Parent launch provenance differs')
    need(receipt['command'][:5] == ['/usr/bin/python3.12', *LAUNCH_FLAGS], 'Child launch flags differ')
    need(receipt['fractions_sha256'] == digest(Path('/usr/lib/python3.12/fractions.py'))[0], 'Actual Fraction source differs')
    need(receipt['label'] == case['label'] and receipt['job'] == case['job'], 'Receipt case differs')
    need(receipt['status'] == 'PASS' and receipt['exit'] == 0 and receipt['termination'] is None, 'Actual runner rejected case')
    need(receipt['source_bytes_and_modes_unchanged'] is True and receipt['retained_log_bytes_stable'] is True, 'Custody or logs changed')
    need(receipt['log_read_chunk_bytes'] == 65536, 'Bounded log reader differs')
    for stream in ('stdout', 'stderr'):
        observed, count = digest(folder / (stream + '.txt'))
        need(observed == receipt[stream + '_sha256'], 'Raw log digest differs')
        need(count == receipt[stream + '_bytes'] == receipt[stream + '_final_bytes'], 'Raw log byte count differs')
        need(count <= 2097152, 'Ordinary raw log cap exceeded')
    need(receipt['stderr_bytes'] == 0, 'Unexpected actual child stderr')
    need(receipt['runner_wall_seconds'] >= receipt['wall_seconds'] >= 0, 'Runner time scope differs')
    prior = [p for p in (ROOT / 'runtime/runs').glob('*/receipt.json') if p.parent != folder]
    need(abs(sum(record_time(p) for p in prior) - receipt['spent_before_seconds']) < 1e-7, 'Aggregate ledger differs')
    need(case.get('kind') == 'component-unit' and case['science_status'] == 'IMPLEMENTED_UNIT_PASS' and
         case.get('science_fields', {}) == {}, 'Original scientific field checks cannot be omitted via unit adapter')
    # Full original unit protocol + independently fixed parent case oracle follows.
    # No synthetic scientific receipt or component/family PASS is emitted here.
    science = {'status': 'UNIT_RAW_WIRE_PENDING_INDEPENDENT_PARENT_JUDGMENT'}
    return {'label': case['label'], 'job': case['job'], 'stage': case['stage'],
            'gate': 'PASS_RETAINED_RECEIPT', 'science_status': science['status'],
            'runner_wall_seconds': receipt['runner_wall_seconds'], 'child_wall_seconds': receipt['wall_seconds'],
            'cpu_seconds': receipt['usage']['user_seconds'] + receipt['usage']['system_seconds'],
            'runner_cpu_seconds_before_own_receipt': receipt['runner_user_seconds'] + receipt['runner_system_seconds'],
            'kernel_max_rss_kib': receipt['usage']['kernel_max_rss_kib'],
            'sampled_process_group_rss_bytes': receipt['sampled_process_group_rss_bytes']}



def _reconcile_parent_cost(owner, *, outer_reconciler_source_sha256):
    """Once-only enclosing cost, including failures; outer final tail still due.

    This is a required actual-parent finalization API, never automatically run
    during source work. The enclosing source_packet/GNU-time owner reconciles
    its own final tail exactly once after this receipt as the original policy.
    """
    state = _entry(owner)
    schema.need(state['phase'] != 'STOP' and state['original']['unknown_owner']['quarantine'][0] is False,
                'quarantined parent must exit; external original cost reconciler owns failure accounting')
    schema.need(state['accounted'] is False, 'parent cost already reconciled')
    state['accounted'] = True
    schema.digest(outer_reconciler_source_sha256)
    root = Path(state['plan']['root'])
    now = _CLOCK()
    current = supervisor.ledger(root, allow_unclosed=True)
    schema.need(all(current.get(k) == v for k, v in state['initial_costs'].items()), 'prior guarded cost changed')
    nested = sum(v for k, v in current.items() if k not in state['initial_costs'])
    elapsed = now - state['began']
    residual = max(0.0, elapsed - nested)
    usage = (resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN))
    label = state['original']['plan']['epoch_id'] + '-family-batch-parent-cost'
    folder = root / 'runtime/runs' / label
    folder.mkdir()
    supervisor.write_new(folder / 'START.json', {'kind': 'parent_cost_only'})
    supervisor.write_new(folder / 'receipt.json', {'schema': 'h25-family-batch-parent-cost-v1',
        'kind': 'parent_cost_only', 'label': label, 'mode': state['mode'],
        'status': 'STOP' if state['primary'][0] is not None else 'PARENT_ACCOUNTED_NOT_FAMILY_PASS',
        'nested_runner_seconds': nested, 'complete_elapsed_before_own_receipt': elapsed,
        'wall_seconds': residual, 'runner_wall_seconds': residual,
        'complete_cpu_seconds_before_own_receipt': sum((z.ru_utime+z.ru_stime)-(a.ru_utime+a.ru_stime)
            for a,z in zip(state['usage_start'],usage)), 'outer_reconciler_source_sha256': outer_reconciler_source_sha256,
        'outer_final_tail_not_included_here': True, 'full_science': False, 'gain': False})
    return None


def reconcile_parent_cost(owner, *, outer_reconciler_source_sha256):
    state = _entry(owner)
    try:
        return _reconcile_parent_cost(owner, outer_reconciler_source_sha256=outer_reconciler_source_sha256)
    except BaseException as error:
        _stop(state, error)
        raise
