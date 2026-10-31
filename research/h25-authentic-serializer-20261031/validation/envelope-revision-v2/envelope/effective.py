"""Source-derived callable/class/default/global binding fingerprints.

Only ordinary interpreter metadata is inspected; descriptors and target functions
are never invoked. Mutable cache contents are not frozen. Binding identities,
Python code/defaults/closures, builtin authority and all class methods are.
"""
import builtins
import hashlib
import json
import marshal
from pathlib import Path
import types
from custody import need


def value(obj, depth=0):
    if type(obj) in (str, int, bool, float, bytes, type(None)):
        return [type(obj).__name__, repr(obj)]
    if depth < 8 and type(obj) in (tuple, list):
        return [type(obj).__name__, [value(x, depth + 1) for x in obj]]
    if depth < 8 and type(obj) is dict:
        return ['dict', sorted((repr(k), value(v, depth + 1)) for k, v in obj.items())]
    return ['identity', type(obj).__module__, type(obj).__qualname__, id(obj)]


def fingerprint(module):
    seen, rows = set(), []
    def visit(label, obj, depth=0):
        if id(obj) in seen or depth > 16:
            return
        seen.add(id(obj))
        if type(obj) is types.FunctionType:
            code = obj.__code__
            names = set(code.co_names)
            global_bindings = []
            for name in sorted(names):
                if name in obj.__globals__:
                    bound = obj.__globals__[name]
                    global_bindings.append((name, id(bound), type(bound).__module__, type(bound).__qualname__))
                    if isinstance(bound, (types.FunctionType, type)):
                        visit(label + '.global.' + name, bound, depth + 1)
                elif hasattr(builtins, name):
                    bound = vars(builtins)[name]
                    global_bindings.append(('builtins.' + name, id(bound), type(bound).__name__))
            rows.append((label, 'function', id(obj), hashlib.sha256(marshal.dumps(code)).hexdigest(),
                         value(obj.__defaults__), value(obj.__kwdefaults__),
                         [value(cell.cell_contents) for cell in (obj.__closure__ or ())], global_bindings,
                         id(obj.__builtins__)))
            wrapped = vars(obj).get('__wrapped__')
            if wrapped is not None:
                visit(label + '.__wrapped__', wrapped, depth + 1)
        elif isinstance(obj, type):
            rows.append((label, 'class', id(obj), [(b.__module__, b.__qualname__, id(b)) for b in obj.__bases__]))
            for name, bound in sorted(vars(obj).items()):
                if isinstance(bound, (staticmethod, classmethod)):
                    bound = bound.__func__
                if isinstance(bound, property):
                    for suffix in ('fget', 'fset', 'fdel'):
                        function = getattr(bound, suffix)
                        if function is not None:
                            visit(label + '.' + name + '.' + suffix, function, depth + 1)
                elif isinstance(bound, (types.FunctionType, type, types.BuiltinFunctionType,
                                        types.MethodDescriptorType, types.WrapperDescriptorType)):
                    visit(label + '.' + name, bound, depth + 1)
        elif isinstance(obj, (types.BuiltinFunctionType, types.MethodDescriptorType, types.WrapperDescriptorType)):
            rows.append((label, 'native', id(obj), getattr(obj, '__module__', None), getattr(obj, '__qualname__', None)))
    for name, obj in sorted(vars(module).items()):
        if isinstance(obj, (types.FunctionType, type, types.BuiltinFunctionType)):
            visit(name, obj)
        elif name.isupper() and type(obj) in (tuple, str, int, bool, dict, list):
            rows.append((name, 'constant', value(obj)))
    raw = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'binding_rows': len(rows)}


def capture(modules):
    result = {}
    for name, module in sorted(modules.items()):
        if module is not None and getattr(module, '__file__', None):
            result[name] = fingerprint(module)
    return result


def unchanged(before, after):
    for name, expected in before.items():
        need(after.get(name) == expected, 'effective callable/class/default/global binding drift: ' + name)
