"""Source-owned one-shot PRE-CAPTURE binding under an authenticated outer parent.

The outer caller must authenticate this immutable source and the supplied
manifest BEFORE import/entry (inherited C04); no hash supplied here grants that
trust. This module has no loader, exec, callback, source mutation, Root API write,
stage write or target launch. It verifies exact already imported source objects,
then installs only a fixed enum of literal gate bindings once, before capture.
"""
import ast
import argparse
import importlib.util as _importlib_util
import builtins
import hashlib
import json
import os
import stat
import sys
import types
import marshal
import parent_completion_v1 as parent
import parent_closure_v1 as original_closure
import configured_inverse_v2 as inverse

_INSTALLATIONS = []
_TYPE, _LEN = type, len
_OPEN, _READ, _CLOSE, _FSTAT, _GETPID = os.open, os.read, os.close, os.fstat, os.getpid
_MODULE_DICT = types.ModuleType.__dict__['__dict__'].__get__
_FUNCTION_GETTERS = tuple(types.FunctionType.__dict__[name].__get__ for name in
    ('__code__', '__globals__', '__builtins__', '__defaults__', '__kwdefaults__', '__closure__', '__dict__'))
_CELL_GET = types.CellType.__dict__['cell_contents'].__get__
_CLASS_DICT = type.__dict__['__dict__'].__get__
_STATIC_FUNCTION = staticmethod.__dict__['__func__'].__get__
_CLASS_FUNCTION = classmethod.__dict__['__func__'].__get__
# Captured only at the inherited independently admitted no-mutator startup.
_STARTUP_MODULES = {name: module for name, module in tuple(sys.modules.items())
                    if type(name) is str and type(module) is types.ModuleType}
_STARTUP_HELPERS = tuple((module, tuple(_MODULE_DICT(module, types.ModuleType).items()))
                         for module in (parent, original_closure, inverse))
_MAX_GLOBALS = 512
MAX_MODULES = 63
MAX_IMAGE = 8 * 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024


class BindingStop(RuntimeError):
    pass


def _need(value, message):
    if not value:
        raise BindingStop(message)


def _exact(value, keys):
    _need(_TYPE(value) is dict and all(_TYPE(k) is str for k in value) and set(value) == set(keys), 'binding exact keys differ')


def _identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode, 'links': info.st_nlink,
            'uid': info.st_uid, 'gid': info.st_gid, 'size': info.st_size,
            'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


def _entry(context):
    _need(_TYPE(context) is object, 'exact original installation context required')
    for token, state in _INSTALLATIONS:
        if token is context:
            return state
    raise BindingStop('unregistered pre-capture installation context')


def _primitive_bindings_match_v3(values):
    _need(_TYPE(values) is tuple and _LEN(values) == 5, 'exact primitive binding tuple required')
    return all(actual is expected for actual, expected in zip(values, (os.open, os.read, os.close, os.fstat, os.getpid)))


def _fresh(state):
    owner = state['owner']
    _need(parent._UNKNOWN_OWNER is owner and _GETPID() == state['pid'] and state['phase'] != 'STOP' and
          owner['primary'][0] is None and owner['quarantine'][0] is False and
          owner['pending'][0] is False and owner['iterator_uncertain'][0] is False,
          'original installation owner requires teardown')
    _need(_primitive_bindings_match_v3((_OPEN, _READ, _CLOSE, _FSTAT, _GETPID)) and
          _TYPE is builtins.type and _LEN is builtins.len,
          'original installation primitive binding changed')


def _read_pin(state, pin, limit=MAX_IMAGE):
    """Nofollow component descent; known tokens close once, uncertainty latches."""
    _fresh(state)
    _exact(pin, ('path', 'sha256', 'bytes', 'identity'))
    path = pin['path']
    _need(_TYPE(path) is str and path.startswith('/') and len(path) <= 4096 and
          all(c not in ('', '.', '..') for c in path.split('/')[1:]), 'binding pin path differs')
    _digest(pin['sha256'])
    _need(_TYPE(pin['bytes']) is int and 0 <= pin['bytes'] <= limit, 'binding pin byte bound')
    _exact(pin['identity'], ('device', 'inode', 'mode', 'links', 'uid', 'gid', 'size', 'mtime_ns', 'ctime_ns'))
    _need(all(_TYPE(x) is int and x >= 0 for x in pin['identity'].values()) and
          pin['identity']['links'] == 1 and pin['identity']['size'] == pin['bytes'] and
          stat.S_ISREG(pin['identity']['mode']) and not pin['identity']['mode'] & 0o222,
          'immutable binding source pin required')
    primary = None
    state['fds'] = [None, None]
    try:
        state['owner']['pending'][0] = True
        state['fds'][0] = _OPEN('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
        state['owner']['pending'][0] = False
        parts = path.split('/')[1:]
        for component in parts[:-1]:
            state['owner']['pending'][0] = True
            state['fds'][1] = _OPEN(component, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                                   dir_fd=state['fds'][0])
            state['owner']['pending'][0] = False
            old = state['fds'][0]; state['fds'][0] = None
            _CLOSE(old)
            state['fds'][0], state['fds'][1] = state['fds'][1], None
        state['owner']['pending'][0] = True
        state['fds'][1] = _OPEN(parts[-1], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=state['fds'][0])
        state['owner']['pending'][0] = False
        _need(_identity(_FSTAT(state['fds'][1])) == pin['identity'], 'actual binding file identity differs')
        chunks, count = [], 0
        while True:
            raw = _READ(state['fds'][1], min(65536, pin['bytes'] + 1 - count))
            _need(_TYPE(raw) is bytes, 'native binding read type differs')
            if not raw:
                break
            count += len(raw); _need(count <= pin['bytes'], 'binding source grew')
            chunks.append(raw)
        raw = b''.join(chunks)
        _need(len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'] and
              _identity(_FSTAT(state['fds'][1])) == pin['identity'], 'binding source custody changed')
        return raw
    except BaseException as error:
        primary = error
        if state['owner']['primary'][0] is None:
            state['owner']['primary'][0] = error
        state['owner']['quarantine'][0] = True
        state['phase'] = 'STOP'
        raise
    finally:
        close_primary = None
        for index in (1, 0):
            descriptor = state['fds'][index]
            state['fds'][index] = None
            if descriptor is not None:
                try:
                    _CLOSE(descriptor)
                except BaseException as error:
                    if state['owner']['primary'][0] is None:
                        state['owner']['primary'][0] = error
                    state['owner']['quarantine'][0] = True
                    state['phase'] = 'STOP'
                    state['close_errors'].append(error)
                    if close_primary is None:
                        close_primary = error
        if primary is None and close_primary is not None:
            raise close_primary


def _pairs(items):
    _need(len(items) <= 8192, 'binding mapping bound')
    result = {}
    for key, value in items:
        _need(_TYPE(key) is str and len(key) <= 1048576 and key not in result, 'binding duplicate/foreign key')
        result[key] = value
    return result


def _reject(value):
    raise BindingStop('binding noninteger/nonfinite literal rejected')


def _document(raw):
    value = json.loads(raw.decode('ascii'), object_pairs_hook=_pairs, parse_float=_reject, parse_constant=_reject)
    _literal(value, [0])
    _need(_TYPE(value) is dict, 'binding top-level document differs')
    return value


def _namespace(module):
    _need(_TYPE(module) is types.ModuleType, 'exact installed module type required')
    namespace = _MODULE_DICT(module, types.ModuleType)
    _need(_TYPE(namespace) is dict and _LEN(namespace) <= _MAX_GLOBALS, 'bounded exact installed namespace required')
    # Complete key walk BEFORE any membership, lookup, set, hash or equality.
    for key in namespace:
        _need(_TYPE(key) is str and _LEN(key) <= 256, 'foreign installed namespace key')
    for key in ('__name__', '__file__'):
        _need(key in namespace and _TYPE(namespace[key]) is str and 0 < _LEN(namespace[key]) <= 4096,
              'exact installed module metadata required')
    return namespace


def _startup_helpers_unchanged():
    for module, items in _STARTUP_HELPERS:
        namespace = _namespace(module)
        _need(_LEN(namespace) == _LEN(items), 'startup helper namespace census changed')
        for key, expected in items:
            _need(_TYPE(key) is str and namespace.get(key) is expected, 'startup helper binding identity changed')



def _function_record(function):
    _need(_TYPE(function) is types.FunctionType, 'exact source function required')
    values = tuple(getter(function, types.FunctionType) for getter in _FUNCTION_GETTERS)
    closure = values[5]
    cells = () if closure is None else tuple((cell, _CELL_GET(cell, types.CellType)) for cell in closure)
    _need(_LEN(cells) <= 64, 'source function closure bound exceeded')
    return function, values, cells


def _function_check(record):
    function, values, cells = record
    _need(_TYPE(function) is types.FunctionType, 'source function identity changed')
    for getter, expected in zip(_FUNCTION_GETTERS, values):
        _need(getter(function, types.FunctionType) is expected,
                    'source function code/globals/builtins/defaults/closure/dict changed')
    for cell, expected in cells:
        _need(_CELL_GET(cell, types.CellType) is expected, 'source function closure contents changed')


def _codes(code, result):
    result.setdefault(code.co_qualname, []).append(code)
    for child in code.co_consts:
        if _TYPE(child) is types.CodeType:
            _codes(child, result)


def _data(value, depth=0):
    """Snapshot literal data only; no foreign repr/hash/eq/iteration protocols."""
    _need(depth <= 32, 'literal snapshot depth exceeded')
    kind = _TYPE(value)
    if value is None or (kind is str or kind is int or kind is bool or kind is bytes or kind is float):
        return (kind, value)
    if (kind is list or kind is tuple):
        _need(_LEN(value) <= 65536, 'literal sequence bound exceeded')
        return (kind, tuple(_data(item, depth + 1) for item in value))
    if kind is dict:
        _need(_LEN(value) <= 8192, 'literal mapping bound exceeded')
        for key in value:
            _need((_TYPE(key) is str or _TYPE(key) is int), 'nonliteral mapping key')
        return (kind, tuple((_data(key, depth + 1), _data(item, depth + 1))
                            for key, item in value.items()))
    if (kind is set or kind is frozenset):
        _need(_LEN(value) <= 8192 and all((_TYPE(item) is str or _TYPE(item) is int) for item in value),
                    'nonliteral set value')
        return (kind, frozenset(value))
    raise BindingStop('not literal data')


def _validate_code(function, compiled_codes, namespace):
    _need(_TYPE(function) is types.FunctionType, 'exact installed source function required')
    values = tuple(getter(function, types.FunctionType) for getter in _FUNCTION_GETTERS)
    code = values[0]
    _need(values[1] is namespace and values[2] is builtins.__dict__,
                'source function original namespace/builtins differs')
    candidates = compiled_codes.get(code.co_qualname, ())
    encoded = marshal.dumps(code)
    _need(any(marshal.dumps(expected) == encoded for expected in candidates),
                'receiving function bytecode differs from pinned source')


def _digest(value):
    _need(type(value) is str and len(value) == 64 and all(x in '0123456789abcdef' for x in value),
          'exact configuration digest required')


def _literal(value, budget, depth=0):
    budget[0] += 1
    _need(budget[0] <= 200000 and depth <= 32, 'finite configured literal tree bound')
    kind = type(value)
    if value is None or kind is bool:
        return
    if kind is int:
        _need(value.bit_length() <= 127, 'configuration integer bound')
        return
    if kind is str or kind is bytes:
        _need(len(value) <= 1048576, 'configuration atom bound')
        return
    _need((kind is tuple or kind is list or kind is dict) and len(value) <= 8192, 'configuration exact literal type')
    if kind is dict:
        for key in value:
            _need(type(key) is str, 'configuration dictionary key type')
    for item in (value.values() if kind is dict else value):
        _literal(item, budget, depth + 1)



def _source_objects(module, source_pin, raw, exact_modules):
    namespace = _namespace(module)
    _need(namespace.get('__file__') == source_pin['path'], 'installed module source origin differs')
    tree = ast.parse(raw, filename=source_pin['path'])
    code = compile(raw, source_pin['path'], 'exec', dont_inherit=True, optimize=sys.flags.optimize)
    codes = {}; _codes(code, codes)
    records, classes = [], []
    for node in tree.body:
        if _TYPE(node) is ast.FunctionDef:
            function = namespace[node.name]
            _validate_code(function, codes, namespace)
            values = tuple(getter(function, types.FunctionType) for getter in _FUNCTION_GETTERS)
            _need(values[5] is None and not node.decorator_list, 'top-level installed closure/decorator differs')
            if module is inverse:
                expected_defaults = tuple(ast.literal_eval(x) for x in node.args.defaults) or None
                _need(_data(values[3]) == _data(expected_defaults), 'installed source defaults differ')
                expected_kwdefaults = {arg.arg: ast.literal_eval(value) for arg, value in
                    zip(node.args.kwonlyargs, node.args.kw_defaults) if value is not None} or None
                _need(_data(values[4]) == _data(expected_kwdefaults), 'installed source keyword defaults differ')
            records.append(_function_record(function))
        elif _TYPE(node) is ast.ClassDef:
            cls = namespace[node.name]
            _need(_TYPE(cls) is type, 'installed source class type differs')
            class_namespace = _CLASS_DICT(cls, type)
            for item in node.body:
                if _TYPE(item) is ast.FunctionDef:
                    _need(not item.decorator_list, 'unreviewed decorated installation method')
                    method = class_namespace[item.name]
                    if item.name == '__new__' and _TYPE(method) is staticmethod:
                        method = _STATIC_FUNCTION(method, staticmethod)
                    elif item.name in ('__init_subclass__', '__class_getitem__') and _TYPE(method) is classmethod:
                        method = _CLASS_FUNCTION(method, classmethod)
                    _validate_code(method, codes, namespace)
                    records.append(_function_record(method))
            for method in class_namespace.values():
                # Dataclass-generated methods retain the admitted original
                # interpreter/dataclasses premise and their actual identity.
                if _TYPE(method) is types.FunctionType and not any(method is row[0] for row in records):
                    records.append(_function_record(method))
            classes.append((cls, tuple(class_namespace.items())))
    for node in tree.body:
        if _TYPE(node) is ast.Import:
            for alias in node.names:
                name = alias.name
                expected = exact_modules.get(name, _STARTUP_MODULES.get(name))
                _need(expected is not None and namespace.get(alias.asname or name.split('.')[0]) is expected,
                      'installed source import binding changed')
    return tree, tuple(records), tuple(classes)


def _classes_unchanged(classes):
    for cls, items in classes:
        namespace = _CLASS_DICT(cls, type)
        _need(len(namespace) == len(items), 'installed class namespace census changed')
        for key, prior in items:
            _need(namespace.get(key) is prior, 'installed class attribute binding changed')



def prepare_binding_context(original_parent, original_unknown_owner, exact_modules, outer_manifest_pin):
    """Called only by independently authenticated actual original outer parent.

    outer_manifest_pin is externally authenticated command/manifest input, not
    a trust decision made by this source. It binds data without reciprocal
    source hashes: source images -> plans -> schedule -> bindings -> outer pin.
    """
    state = None
    try:
        _startup_helpers_unchanged()
        _need(original_parent is parent and original_unknown_owner is parent._UNKNOWN_OWNER and
              not _INSTALLATIONS and not parent._PARENTS and parent._PROCESS[0] is None,
              'actual pristine original parent/private owner required before capture')
        _need(_TYPE(exact_modules) is dict and 1 <= len(exact_modules) <= MAX_MODULES and
              all(_TYPE(name) is str and name.isidentifier() for name in exact_modules), 'exact finite source modules required')
        state = {'owner': original_unknown_owner, 'pid': _GETPID(), 'phase': 'PREPARING', 'consumed': False,
                 'modules': exact_modules, 'fds': [None, None], 'close_errors': [], 'records': [],
                 'sources': {}, 'bindings': {}, 'installed': {}, 'primary': [None], 'outer_pin': outer_manifest_pin}
        token = object(); _INSTALLATIONS.append((token, state))
        outer = _document(_read_pin(state, outer_manifest_pin))
        _exact(outer, ('schema', 'source_manifest', 'binding_plan', 'source_review_sha256', 'bootstrap_review_sha256',
                      'command_review_sha256', 'root_source_sha256', 'runtime_premise_sha256'))
        _need(outer['schema'] == 'h25-authenticated-pre-capture-context-v2' and
              outer['root_source_sha256'] == 'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0',
              'original Root and external context differ')
        for key in ('source_review_sha256', 'bootstrap_review_sha256', 'command_review_sha256', 'runtime_premise_sha256'):
            _digest(outer[key])
        manifest = _document(_read_pin(state, outer['source_manifest']))
        plan = _document(_read_pin(state, outer['binding_plan']))
        _exact(manifest, ('schema', 'modules'))
        _exact(plan, ('schema', 'bindings'))
        _exact(manifest['modules'], tuple(exact_modules))
        _need(_TYPE(plan['bindings']) is dict and _LEN(plan['bindings']) <= MAX_MODULES and
              all(_TYPE(key) is str for key in plan['bindings']), 'exact bounded gate module keys required')
        _need(manifest['schema'] == 'h25-bootstrap-module-manifest-v2' and plan['schema'] == 'h25-pre-capture-bindings-v2' and
              set(manifest['modules']) == set(exact_modules), 'complete bootstrap source inventory differs')
        _need(set(plan['bindings']) <= set(ALLOWED_GATES) and set(plan['bindings']) <= set(exact_modules),
              'binding contains module outside fixed source enum')
        total = 0
        for name, module in exact_modules.items():
            _need(_namespace(module).get('__name__') == name, 'bootstrap module name differs')
            record = manifest['modules'][name]
            _exact(record, ('source', 'template_inverse'))
            source_pin = record['source']
            raw = _read_pin(state, source_pin)
            total += len(raw); _need(total <= MAX_TOTAL, 'whole bootstrap source byte bound')
            _need(record['template_inverse']['configured_sha256'] == source_pin['sha256'] and
                  record['template_inverse']['module'] == name, 'bootstrap configured source binding differs')
            state.setdefault('inverse_work', []).append((raw, record['template_inverse']))
            tree, functions, classes = _source_objects(module, source_pin, raw, exact_modules)
            names = {node.targets[0].id: node.value for node in tree.body if _TYPE(node) is ast.Assign and
                     len(node.targets) == 1 and _TYPE(node.targets[0]) is ast.Name}
            namespace = _namespace(module)
            selected = plan['bindings'].get(name, {})
            _need(_TYPE(selected) is dict and set(selected) <= set(ALLOWED_GATES.get(name, ())), 'unknown gate assignment')
            needed = tuple(key for key in ALLOWED_GATES.get(name, ()) if key in namespace)
            _need(set(selected) == set(needed), 'complete fixed gate binding set omitted')
            bound = {}
            for gate, literal in selected.items():
                _need(gate in names and type(names[gate]) is ast.Constant and names[gate].value is None and
                      namespace[gate] is None and type(literal) is str and literal.isascii() and '\n' not in literal,
                      'gate was previously configured, captured, or is not an explicit None template')
                value = ast.literal_eval(literal); _literal(value, [0])
                _need(value is not None, 'installation cannot leave required gate unset')
                bound[gate] = value
            state['sources'][name] = source_pin
            state['bindings'][name] = bound
            state['records'].append((name, module, namespace, tuple(namespace.items()), functions, classes))
        # Every supplied helper/function/class and its namespace is authenticated
        # from outer-pinned source BEFORE the first inverse helper invocation.
        _need(exact_modules.get('configured_inverse_v2') is inverse and
              exact_modules.get('parent_completion_v1') is parent and
              exact_modules.get('parent_closure_v1') is original_closure,
              'complete original helper source inventory required')
        _startup_helpers_unchanged()
        for raw, inverse_record in state['inverse_work']:
            inverse.verify_configured_source(raw, inverse_record)
        state['outer'] = outer
        state['phase'] = 'PREPARED'
        return token
    except BaseException as error:
        if parent._UNKNOWN_OWNER['primary'][0] is None:
            parent._UNKNOWN_OWNER['primary'][0] = error
        parent._UNKNOWN_OWNER['quarantine'][0] = True
        if state is not None:
            state['primary'][0] = error; state['phase'] = 'STOP'
        raise


def install_before_capture(context):
    state = _entry(context)
    try:
        _fresh(state)
        _need(state['phase'] == 'PREPARED' and not state['consumed'] and not parent._PARENTS and
              parent._PROCESS[0] is None, 'binding installation is one-shot before original capture')
        state['consumed'] = True
        state['phase'] = 'INSTALLING'
        for name, module, namespace, original, functions, classes in state['records']:
            _need(_namespace(module) is namespace and len(namespace) == len(original), 'pre-capture namespace changed')
            for key, value in original:
                _need(namespace.get(key) is value, 'pre-capture source object changed')
            for function in functions:
                _function_check(function)
            _classes_unchanged(classes)
            _read_pin(state, state['sources'][name])
        for name, module, namespace, original, functions, classes in state['records']:
            for key, value in state['bindings'][name].items():
                namespace[key] = value
                state['installed'][(name, key)] = (module, value, _data(value))
        state['phase'] = 'SEALED'
        verify_bindings(context)
        return None
    except BaseException as error:
        if state['owner']['primary'][0] is None:
            state['owner']['primary'][0] = error
        state['owner']['quarantine'][0] = True
        state['primary'][0] = error; state['phase'] = 'STOP'
        raise


def verify_bindings(context):
    state = _entry(context)
    _fresh(state)
    _need(state['phase'] == 'SEALED' and state['consumed'], 'final source capture requires sealed bindings')
    _read_pin(state, state['outer_pin'])
    for pin in (state['outer']['source_manifest'], state['outer']['binding_plan']):
        _read_pin(state, pin)
    for name, module, namespace, original, functions, classes in state['records']:
        _need(_namespace(module) is namespace and len(namespace) == len(original), 'installed namespace census changed')
        for key, prior in original:
            expected = state['bindings'][name].get(key, prior)
            _need(namespace.get(key) is expected, 'installed source binding identity changed')
        for record in functions:
            _function_check(record)
        _classes_unchanged(classes)
        _read_pin(state, state['sources'][name])
    for (name, key), (module, value, snapshot) in state['installed'].items():
        _need(_namespace(module)[key] is value and _data(value) == snapshot,
              'installed gate identity/content changed')
    return None


def require_installed_gate(module, name, value):
    """Read-only link from a receiver closure to its sealed original context."""
    _need(_TYPE(name) is str and _TYPE(module) is types.ModuleType, 'exact installed gate lookup')
    matches = []
    for token, state in _INSTALLATIONS:
        if state['phase'] == 'SEALED':
            for (module_name, gate), row in state['installed'].items():
                if row[0] is module and gate == name:
                    matches.append((token, row))
    _need(len(matches) == 1 and matches[0][1][1] is value, 'gate not installed by the original sealed context')
    verify_bindings(matches[0][0])
    return None


def stop_evidence(context):
    state = _entry(context)
    return state['primary'], tuple(state['close_errors']), tuple(state['fds'])


# Exact finite gate enum, source-reviewed; no wildcard or arbitrary namespace writes.
ALLOWED_GATES = {'component_control_root_v1': ('CONTEXT_CONFIGURATION', 'CONTEXT_SOURCE_REVIEW', 'CONTEXT_EXECUTION_APPROVAL', 'CONTEXT_FUNDING'), 'epoch_copy_v5': ('COMPLETE_IO_CONFIGURATION', 'COPY_CONFIGURATION', 'COPY_EXECUTION_APPROVAL', 'COPY_FUNDING', 'CONTROL_CONFIGURATION', 'CONTROL_SOURCE_REVIEW', 'CONTROL_EXECUTION_APPROVAL', 'CONTROL_FUNDING'), 'epoch_parent_v5': ('CONFIGURATION', 'SOURCE_REVIEW', 'EXECUTION_APPROVAL', 'FUNDING'), 'epoch_stop_v5': ('STOP_CONFIGURATION', 'STOP_EXECUTION_APPROVAL', 'STOP_FUNDING'), 'fixture_parent_v2': ('CONFIGURATION', 'SOURCE_REVIEW', 'FIXTURE_PROFILE_CONFIGURATION', 'SONAME_CONSUMER_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'negative_parent_v2': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_CONFIGURATION', 'KERNEL_CONFIGURATION', 'REPLAY_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'original_build_provenance_v5': ('PARSER_CONFIGURATION', 'PARSER_EXECUTION_APPROVAL', 'PARSER_FUNDING'), 'owned_root_v2': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'parent_completion_v1': ('CONFIGURATION', 'SOURCE_REVIEW', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'parent_orchestration_v2': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_CONFIGURATION', 'NATIVE_PROFILE_CONFIGURATION', 'FULL_UNION_CONFIGURATION', 'FULL_CALLER_CONFIGURATION', 'BOOTSTRAP_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'persistent_replay_v1': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_CONFIGURATION', 'PERSISTENCE_CONFIGURATION', 'FULL_ORCHESTRATOR_CONFIGURATION', 'NATIVE_PROFILE_CONFIGURATION', 'SOURCE_CLOSURE_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'policy_parent_domain_v1': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_PROFILE', 'KERNEL_EXEC_PROFILE', 'PHASED_FD_CONTRACT', 'TERMINAL_STATUS_CONTRACT', 'REPLAY_BINDING', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'supplemental_receivers_v2': ('CONTROL_EXECUTORS_CONFIGURATION',), 'variant_validation_v1': ('VALIDATION_CONFIGURATION', 'VALIDATION_SOURCE_REVIEW', 'VALIDATION_EXECUTION', 'VALIDATION_FUNDING')}
