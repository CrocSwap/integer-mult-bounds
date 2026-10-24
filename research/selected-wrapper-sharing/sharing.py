"""Opt-in normalization of already compiled, closed residual segments.

The caller must keep definition fields deeply unchanged during execution and
use only field-based callbacks/observers. Compilation and its guards still run.
"""
from dataclasses import fields, is_dataclass, replace


def need(ok, message):
    if not ok:
        raise ValueError(message)


def snapshot(value):
    if value is None or type(value) in (int, bool, str):
        return (type(value).__name__, value)
    if type(value) is tuple:
        return ('tuple', tuple(snapshot(item) for item in value))
    if type(value) is dict:
        return ('dict', tuple(sorted(((snapshot(k), snapshot(v)) for k, v in value.items()), key=repr)))
    if is_dataclass(value) and value.__dataclass_params__.frozen:
        return ('dataclass', type(value).__module__+'.'+type(value).__qualname__,
                tuple((f.name, snapshot(getattr(value, f.name))) for f in fields(value)))
    raise ValueError('unsupported mutable definition field')


def share_codes(programs):
    """Share equal definitions within a mode; retain every operation and guard.

    shortcut: this is a post-compilation pass, so it does not reduce setup peak
    memory; a streaming compiler needs a separate emission/refinement proof.
    """
    result, counts = [], []
    for mode, code in enumerate(programs):
        cache, signatures, operations = {}, {}, []
        active = chosen = role = None
        original_ids, shared_ids = set(), set()
        for operation in code.operations:
            kind = operation[0]
            if kind == 'residual_begin':
                need(active is None and len(operation) == 3, 'closed nonoverlapping segment')
                _, role, active = operation
                need(is_dataclass(active) and active.__dataclass_params__.frozen, 'frozen residual wrapper')
                key = (mode, active.identifier, active.common, active.low)
                signature = snapshot(active)
                if key in cache:
                    need(signature == signatures[key], 'equal key has changed definition fields')
                else:
                    cache[key], signatures[key] = active, signature
                chosen = cache[key]
                original_ids.add(id(active)); shared_ids.add(id(chosen))
                operations.append((kind, role, chosen))
            elif kind == 'block':
                need(active is not None and operation[1] is active, 'block identity belongs to active segment')
                operations.append((kind, chosen, *operation[2:]))
            elif kind == 'residual_end':
                need(active is not None and operation[1] == role and operation[2] is active,
                     'end identity and role belong to active segment')
                operations.append((kind, role, chosen))
                active = chosen = role = None
            else:
                need(active is None, 'unrecognized operation inside residual segment')
                operations.append(operation)
        need(active is None, 'unterminated residual segment')
        result.append(replace(code, operations=tuple(operations)))
        counts.append({'mode': mode, 'original_wrappers': len(original_ids),
                       'shared_wrappers': len(shared_ids), 'operations': len(operations)})
    return tuple(result), counts
