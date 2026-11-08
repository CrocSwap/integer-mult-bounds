"""Source-owned one-shot PRE-CAPTURE binding under an authenticated outer parent.

The outer caller must authenticate this immutable source and the supplied
manifest BEFORE import/entry (inherited C04); no hash supplied here grants that
trust. This module has no loader, exec, callback, source mutation, Root API write,
stage write or target launch. It verifies exact already imported source objects,
then installs only a fixed enum of literal gate bindings once, before capture.
"""
import ast
import builtins
import hashlib
import json
import os
import stat
import sys
import types
import marshal
import dataclasses
import parent_completion_v1 as parent
import parent_closure_v1 as original_closure
import configured_inverse_v2 as inverse

_INSTALLATIONS = []
_ENTRY_ATTEMPTS = []
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
MAX_MODULES = 57
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
    primary = close_primary = None
    parts = path.split('/')[1:]
    _need(len(parts) <= 2048, 'source path component bound')
    record = {'fds': [None, None], 'close_fds': [None, None],
              'close_entered': [False, False], 'close_errors': [None, None],
              'walk_fds': [None] * len(parts), 'walk_entered': [False] * len(parts),
              'walk_errors': [None] * len(parts), 'primary': [None]}
    # Record allocation/retention precedes every acquisition owned by this read.
    state['read_records'].append(record)
    state['fds'] = record['fds']
    try:
        state['owner']['pending'][0] = True
        state['fds'][0] = _OPEN('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW)
        state['owner']['pending'][0] = False
        for walk_index, component in enumerate(parts[:-1]):
            state['owner']['pending'][0] = True
            state['fds'][1] = _OPEN(component, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                                   dir_fd=state['fds'][0])
            state['owner']['pending'][0] = False
            old = state['fds'][0]
            record['walk_fds'][walk_index] = old
            record['walk_entered'][walk_index] = True
            state['fds'][0] = None
            try:
                _CLOSE(old)
            except BaseException as error:
                record['walk_errors'][walk_index] = error
                raise
            state['fds'][0] = state['fds'][1]
            state['fds'][1] = None
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
        record['primary'][0] = error
        if state['owner']['primary'][0] is None:
            state['owner']['primary'][0] = error
        state['owner']['quarantine'][0] = True
        state['phase'] = 'STOP'
        raise
    finally:
        descriptor = state['fds'][1]
        record['close_fds'][1] = descriptor
        if descriptor is not None:
            record['close_entered'][1] = True
            state['fds'][1] = None
            try:
                _CLOSE(descriptor)
            except BaseException as error:
                record['close_errors'][1] = error
                if close_primary is None:
                    close_primary = error
                if state['owner']['primary'][0] is None:
                    state['owner']['primary'][0] = error
                state['owner']['quarantine'][0] = True
                state['phase'] = 'STOP'
        descriptor = state['fds'][0]
        record['close_fds'][0] = descriptor
        if descriptor is not None:
            record['close_entered'][0] = True
            state['fds'][0] = None
            try:
                _CLOSE(descriptor)
            except BaseException as error:
                record['close_errors'][0] = error
                if close_primary is None:
                    close_primary = error
                if state['owner']['primary'][0] is None:
                    state['owner']['primary'][0] = error
                state['owner']['quarantine'][0] = True
                state['phase'] = 'STOP'
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



def _source_value(node, namespace, definitions, active=()):
    """Finite source expression interpreter; never eval or candidate callbacks."""
    if type(node) is ast.Name:
        _need(node.id in definitions and node.id not in active and len(active) < 32,
              'source default name is not a finite constant')
        value = _source_value(definitions[node.id], namespace, definitions, active + (node.id,))
        _need(_data(namespace[node.id]) == _data(value), 'source default constant changed')
        return value
    if type(node) is ast.Attribute and type(node.value) is ast.Name:
        module = namespace[node.value.id]
        _need(type(module) is types.ModuleType, 'source default owner is not a module')
        value = _MODULE_DICT(module, types.ModuleType)[node.attr]
        _data(value)
        return value
    if type(node) is ast.BinOp:
        left = _source_value(node.left, namespace, definitions, active)
        right = _source_value(node.right, namespace, definitions, active)
        _need(type(left) is int and type(right) is int, 'exact source integer default required')
        if type(node.op) is ast.Add: value = left + right
        elif type(node.op) is ast.Sub: value = left - right
        elif type(node.op) is ast.Mult: value = left * right
        elif type(node.op) is ast.LShift:
            _need(0 <= right <= 127, 'source default shift bound')
            value = left << right
        elif type(node.op) is ast.Pow:
            _need(0 <= right <= 127 and left.bit_length() * right <= 128, 'source default power bound')
            value = left ** right
        else: raise BindingStop('unsupported source default arithmetic')
        _need(value.bit_length() <= 128, 'source default integer bound')
        return value
    value = ast.literal_eval(node)
    _data(value)
    return value


def _defined_function(function, node, codes, namespace, definitions, cls=None):
    _validate_code(function, codes, namespace)
    values = tuple(getter(function, types.FunctionType) for getter in _FUNCTION_GETTERS)
    expected = tuple(_source_value(v, namespace, definitions) for v in node.args.defaults) or None
    keywords = {a.arg: _source_value(v, namespace, definitions)
        for a, v in zip(node.args.kwonlyargs, node.args.kw_defaults) if v is not None} or None
    _need(_data(values[3]) == _data(expected) and _data(values[4]) == _data(keywords),
          'initial function defaults differ from actual selected source')
    if cls is None or not function.__code__.co_freevars:
        _need(values[5] is None, 'unexpected source function closure')
    else:
        _need(function.__code__.co_freevars == ('__class__',) and len(values[5]) == 1 and
              _CELL_GET(values[5][0], types.CellType) is cls, 'class closure does not own actual class')
    return _function_record(function)


def _source_objects(module, source_pin, raw, exact_modules):
    namespace = _namespace(module)
    _need(namespace.get('__file__') == source_pin['path'] and
          sys.modules.get(namespace['__name__']) is module, 'installed actual source module differs')
    tree = ast.parse(raw, filename=source_pin['path'])
    code = compile(raw, source_pin['path'], 'exec', dont_inherit=True, optimize=sys.flags.optimize)
    codes = {}; _codes(code, codes)
    definitions = {n.targets[0].id: n.value for n in tree.body
        if type(n) is ast.Assign and len(n.targets) == 1 and type(n.targets[0]) is ast.Name}
    records, classes = [], []
    for node in tree.body:
        if type(node) is ast.FunctionDef:
            _need(not node.decorator_list, 'top-level decorated selected function unsupported')
            records.append(_defined_function(namespace[node.name], node, codes, namespace, definitions))
        elif type(node) is ast.ClassDef:
            cls = namespace[node.name]
            _need(type(cls) is type and not node.keywords and
                  cls.__module__ == namespace['__name__'] and cls.__name__ == node.name and
                  cls.__qualname__ == node.name, 'source class/metaclass/name owner differs')
            bases = []
            for base in node.bases:
                _need(type(base) is ast.Name, 'unreviewed computed class base')
                bases.append(namespace.get(base.id, builtins.__dict__.get(base.id)))
            _need(cls.__bases__ == tuple(bases or [object]), 'actual source class bases differ')
            dataclass_owned = False
            if node.decorator_list:
                _need(len(node.decorator_list) == 1, 'unreviewed source class decorator composition')
                decorator = node.decorator_list[0]
                _need(type(decorator) is ast.Call and type(decorator.func) is ast.Name and
                      namespace.get(decorator.func.id) is dataclasses.dataclass and not decorator.args,
                      'only actual original dataclass factory admitted')
                options = {kw.arg: ast.literal_eval(kw.value) for kw in decorator.keywords}
                _need(options == {'frozen': True, 'slots': True} and cls.__dataclass_params__.frozen is True,
                      'original dataclass constructor options differ')
                fields = tuple(n.target.id for n in node.body
                    if type(n) is ast.AnnAssign and type(n.target) is ast.Name)
                _need(tuple(cls.__dataclass_fields__) == fields and tuple(cls.__slots__) == fields,
                      'actual generated dataclass fields/slots differ')
                dataclass_owned = True
            own = _CLASS_DICT(cls, type)
            declared = set()
            for item in node.body:
                if type(item) is ast.FunctionDef:
                    method = own[item.name]; declared.add(item.name)
                    decorators = tuple(d.id if type(d) is ast.Name else None for d in item.decorator_list)
                    if decorators:
                        _need(decorators in (('staticmethod',), ('classmethod',)),
                              'unreviewed explicit method decorator')
                        descriptor = staticmethod if decorators == ('staticmethod',) else classmethod
                        _need(namespace.get(decorators[0], builtins.__dict__[decorators[0]]) is descriptor and
                              type(method) is descriptor, 'actual method wrapper owner differs')
                        method = (_STATIC_FUNCTION(method, staticmethod) if descriptor is staticmethod
                                  else _CLASS_FUNCTION(method, classmethod))
                    elif item.name == '__new__' and type(method) is staticmethod:
                        method = _STATIC_FUNCTION(method, staticmethod)
                    elif item.name in ('__init_subclass__', '__class_getitem__') and type(method) is classmethod:
                        method = _CLASS_FUNCTION(method, classmethod)
                    records.append(_defined_function(method, item, codes, namespace, definitions, cls))
            for name, method in own.items():
                if type(method) is types.FunctionType and name not in declared:
                    _need(dataclass_owned and name in ('__init__', '__repr__', '__eq__', '__hash__',
                        '__setattr__', '__delattr__', '__getstate__', '__setstate__'),
                        'extra generated source method lacks the original fixed factory')
                    records.append(_function_record(method))
            classes.append((cls, tuple(own.items())))
    return tree, tuple(records), tuple(classes), _import_bindings(tree, namespace, exact_modules)


def _import_namespace(module):
    _need(_TYPE(module) is types.ModuleType, 'exact imported module required')
    namespace = _MODULE_DICT(module, types.ModuleType)
    _need(_TYPE(namespace) is dict and _LEN(namespace) <= _MAX_GLOBALS,
          'bounded imported namespace required')
    for key in namespace:
        _need(_TYPE(key) is str and _LEN(key) <= 256, 'foreign import namespace key')
    _need(_TYPE(namespace.get('__name__')) is str, 'import module metadata differs')
    return namespace


def _import_bindings(tree, namespace, exact_modules):
    """Exact Python import semantics, no import hook or dynamic attribute lookup.

    The caller authenticates source modules before this function is invoked.
    Stdlib modules are the admitted startup objects; every selected object is
    also the actual sys.modules object. Parent package edges are checked and
    retained, rather than treating an import alias as a name-map convention.
    """
    _need(_TYPE(exact_modules) is dict and _LEN(exact_modules) <= 4096,
          'bounded exact module inventory required')
    for key, value in exact_modules.items():
        _need(_TYPE(key) is str and _TYPE(value) is types.ModuleType and
              sys.modules.get(key) is value, 'invented/substituted module inventory')
    records, seen = [], set()
    def selected(name):
        _need(_TYPE(name) is str and 0 < _LEN(name) <= 256 and
              all(part.isidentifier() for part in name.split('.')), 'exact absolute import name')
        parts = name.split('.')
        _need(_LEN(parts) <= 32, 'import package depth exceeded')
        prior = None
        for index in range(1, _LEN(parts) + 1):
            full = '.'.join(parts[:index])
            expected = exact_modules.get(full, _STARTUP_MODULES.get(full))
            _need(expected is not None and _TYPE(expected) is types.ModuleType and
                  sys.modules.get(full) is expected, 'import module missing/substituted')
            startup = _STARTUP_MODULES.get(full)
            _need(startup is None or startup is expected, 'admitted startup import identity changed')
            own = _import_namespace(expected)
            _need(own['__name__'] == full or
                  (_STARTUP_MODULES.get(own['__name__']) is expected and
                   sys.modules.get(own['__name__']) is expected), 'import module canonical/real alias identity differs')
            if prior is not None:
                _need(prior.get(parts[index - 1]) is expected, 'package submodule edge changed')
            if full not in seen:
                seen.add(full)
                records.append((full, expected, own, tuple(own.items())))
            prior = own
        return expected
    for node in tree.body:
        if _TYPE(node) is ast.Import:
            for alias in node.names:
                submodule = selected(alias.name)
                if alias.asname is None:
                    bound_name = alias.name.split('.')[0]
                    expected = selected(bound_name)
                else:
                    bound_name, expected = alias.asname, submodule
                _need(namespace.get(bound_name) is expected, 'installed exact import alias differs')
        elif _TYPE(node) is ast.ImportFrom:
            _need(node.level == 0 and _TYPE(node.module) is str,
                  'relative import requires separately reviewed package context')
            module = selected(node.module)
            imported = _import_namespace(module)
            for alias in node.names:
                _need(alias.name != '*' and alias.name.isidentifier(), 'explicit imported symbol required')
                _need(alias.name in imported, 'imported symbol absent from real namespace')
                expected = imported[alias.name]
                if _TYPE(expected) is types.ModuleType:
                    _need(selected(node.module + '.' + alias.name) is expected,
                          'from-import submodule identity differs')
                _need(namespace.get(alias.asname or alias.name) is expected,
                      'installed from-import symbol/alias differs')
    return tuple(records)


def _imports_unchanged(records, installed=None):
    for name, module, namespace, items in records:
        _need(sys.modules.get(name) is module and _import_namespace(module) is namespace and
              _LEN(namespace) == _LEN(items), 'import namespace identity/census changed')
        for key, value in items:
            expected = value if installed is None else installed.get((name, key), value)
            _need(namespace.get(key) is expected, 'import package/submodule/symbol binding changed')



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
                 'modules': exact_modules, 'fds': [None, None], 'close_errors': [], 'read_records': [], 'records': [],
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
            tree, functions, classes, imports = _source_objects(module, source_pin, raw, exact_modules)
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
            state['records'].append((name, module, namespace, tuple(namespace.items()), functions, classes, imports))
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
        for name, module, namespace, original, functions, classes, imports in state['records']:
            _need(_namespace(module) is namespace and len(namespace) == len(original), 'pre-capture namespace changed')
            for key, value in original:
                _need(namespace.get(key) is value, 'pre-capture source object changed')
            for function in functions:
                _function_check(function)
            _classes_unchanged(classes)
            _imports_unchanged(imports)
            _read_pin(state, state['sources'][name])
        for name, module, namespace, original, functions, classes, imports in state['records']:
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
    for name, module, namespace, original, functions, classes, imports in state['records']:
        _need(_namespace(module) is namespace and len(namespace) == len(original), 'installed namespace census changed')
        for key, prior in original:
            expected = state['bindings'][name].get(key, prior)
            _need(namespace.get(key) is expected, 'installed source binding identity changed')
        for record in functions:
            _function_check(record)
        _classes_unchanged(classes)
        _imports_unchanged(imports, {(module_name, key): value for module_name, values in state['bindings'].items() for key, value in values.items()})
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
    return state['primary'], tuple(state['read_records']), tuple(state['fds'])


# Exact finite gate enum, source-reviewed; no wildcard or arbitrary namespace writes.
ALLOWED_GATES = {'component_control_root_v1': ('CONTEXT_CONFIGURATION', 'CONTEXT_SOURCE_REVIEW', 'CONTEXT_EXECUTION_APPROVAL', 'CONTEXT_FUNDING'), 'epoch_copy_v5': ('COMPLETE_IO_CONFIGURATION', 'COPY_CONFIGURATION', 'COPY_EXECUTION_APPROVAL', 'COPY_FUNDING', 'CONTROL_CONFIGURATION', 'CONTROL_SOURCE_REVIEW', 'CONTROL_EXECUTION_APPROVAL', 'CONTROL_FUNDING'), 'epoch_parent_v5': ('CONFIGURATION', 'SOURCE_REVIEW', 'EXECUTION_APPROVAL', 'FUNDING'), 'epoch_stop_v5': ('STOP_CONFIGURATION', 'STOP_EXECUTION_APPROVAL', 'STOP_FUNDING'), 'fixture_parent_v2': ('CONFIGURATION', 'SOURCE_REVIEW', 'FIXTURE_PROFILE_CONFIGURATION', 'SONAME_CONSUMER_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'negative_parent_v2': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_CONFIGURATION', 'KERNEL_CONFIGURATION', 'REPLAY_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'original_build_provenance_v5': ('PARSER_CONFIGURATION', 'PARSER_EXECUTION_APPROVAL', 'PARSER_FUNDING'), 'owned_root_v2': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'parent_completion_v1': ('CONFIGURATION', 'SOURCE_REVIEW', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'parent_orchestration_v2': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_CONFIGURATION', 'NATIVE_PROFILE_CONFIGURATION', 'FULL_UNION_CONFIGURATION', 'FULL_CALLER_CONFIGURATION', 'BOOTSTRAP_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'persistent_replay_v1': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_CONFIGURATION', 'PERSISTENCE_CONFIGURATION', 'FULL_ORCHESTRATOR_CONFIGURATION', 'NATIVE_PROFILE_CONFIGURATION', 'SOURCE_CLOSURE_CONFIGURATION', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'policy_parent_domain_v1': ('CONFIGURATION', 'SOURCE_REVIEW', 'RUNTIME_PROFILE', 'KERNEL_EXEC_PROFILE', 'PHASED_FD_CONTRACT', 'TERMINAL_STATUS_CONTRACT', 'REPLAY_BINDING', 'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'), 'supplemental_receivers_v2': ('CONTROL_EXECUTORS_CONFIGURATION',), 'variant_validation_v1': ('VALIDATION_CONFIGURATION', 'VALIDATION_SOURCE_REVIEW', 'VALIDATION_EXECUTION', 'VALIDATION_FUNDING')}


_NATIVE_UNITS = ('epoch-v4/C03/native-enoent', 'epoch-v4/C03/native-eexist', 'epoch-v4/C03/native-eloop')
_NATIVE_COPY = 'b8303732ede41dd48aa767f2c40cbbff249f34e2621f532b5484d38a218a0f69'
_PORT_COPY = 'bcc465a7c61261b58e92c06f1cf7937b134256243f1a0ff84ad859965ad0134d'
_SCHEMA = 'b89a789654be87bde40a47300f4d9702dce2b90e6ab3be9a2025f6d8041b3e9a'


def prepare_selected_child(lane_text, exact_modules):
    """Actual Root driver dispatch, using its authenticated unchanged argv tail.

    The original source-owned parent binds these lane bytes in immutable JOBS
    and the exact whole command. This function proves checks/use, not that an
    arbitrary string caller is that parent. The unchanged original fresh-Root
    premise supplies that factual source/input provenance.
    """
    _need(not _ENTRY_ATTEMPTS and type(lane_text) is str and len(lane_text) <= 16384,
          'selected child pre-capture entry is one-shot')
    state = {'owner': parent._UNKNOWN_OWNER, 'pid': _GETPID(), 'phase': 'READING',
             'fds': [None, None], 'close_errors': [], 'read_records': [], 'primary': [None]}
    _ENTRY_ATTEMPTS.append(state)  # Before the first acquisition.
    try:
        transport = _document(lane_text.encode('ascii'))
        _exact(transport, ('schema', 'plan'))
        _need(transport['schema'] == 'h25-selected-child-argv-v1' and
              json.dumps(transport, sort_keys=True, separators=(',', ':')) == lane_text,
              'exact canonical original-owner lane transport required')
        plan = _document(_read_pin(state, transport['plan']))
        _exact(plan, ('schema', 'outer_context', 'entry_configuration', 'selection'))
        _need(plan['schema'] == 'h25-selected-child-preparation-v1', 'selected preparation schema differs')
        selection = plan['selection']
        _exact(selection, ('unit_id', 'mode', 'kind'))
        _need(selection['mode'] == ('normal' if sys.flags.optimize == 0 else 'optimized') and
              sys.flags.optimize in (0, 1), 'actual selected child mode differs')
        kind = 'NATIVE_PRODUCTION' if selection['unit_id'] in _NATIVE_UNITS else 'HISTORICAL_PORT'
        _need(selection['kind'] == kind, 'source-owned native/port choice differs')
        token = prepare_binding_context(parent, parent._UNKNOWN_OWNER, exact_modules, plan['outer_context'])
        installed = _entry(token)
        context = installed['bindings']['component_control_root_v1']['CONTEXT_CONFIGURATION']
        _need(context['unit_id'] == selection['unit_id'] and context['mode'] == selection['mode'],
              'installed actual context differs from selection')
        source_manifest = _document(_read_pin(installed, installed['outer']['source_manifest']))
        modules = source_manifest['modules']
        _need(modules['epoch_copy_v5']['template_inverse']['template_sha256'] ==
              (_NATIVE_COPY if kind == 'NATIVE_PRODUCTION' else _PORT_COPY) and
              modules['epoch_schema_v5']['template_inverse']['template_sha256'] == _SCHEMA,
              'actual selected production/port source differs')
        _need(modules['component_control_root_v1']['template_inverse']['assignments'] == {},
              'context must be installed before capture, never a cyclic configured source')
        install_before_capture(token)
        state['token'], state['plan'], state['transport'] = token, plan, transport
        state['phase'] = 'SEALED'
        return plan['entry_configuration']
    except BaseException as error:
        if state['primary'][0] is None: state['primary'][0] = error
        if state['owner']['primary'][0] is None: state['owner']['primary'][0] = error
        state['owner']['quarantine'][0] = True
        state['phase'] = 'STOP'
        raise


def require_selected_child(modules, source_policy, unit, mode):
    _need(len(_ENTRY_ATTEMPTS) == 1 and _ENTRY_ATTEMPTS[0]['phase'] == 'SEALED',
          'actual selected child constructor was not reached')
    state = _ENTRY_ATTEMPTS[0]; installed = _entry(state['token'])
    _need(installed['modules'] is modules or all(installed['modules'].get(k) is v for k,v in modules.items()),
          'actual selected module objects differ')
    _need(set(installed['sources']) == set(source_policy) and all(
          _data(installed['sources'][name]) == _data(source_policy[name]) for name in source_policy),
          'receiver policy differs from actual authenticated source manifest')
    selection = state['plan']['selection']
    _need(selection['unit_id'] == unit and selection['mode'] == mode, 'actual selection context differs')
    verify_bindings(state['token'])
    return state['token']
