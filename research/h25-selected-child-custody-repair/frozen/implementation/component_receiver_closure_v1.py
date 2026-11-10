"""Finite concrete receiver admission inside the original trusted parent.

This verifies pinned source, bytecode derived from those bytes without executing
them, concrete local import edges, and the current captured object graph.  It is
not a new Python sandbox or proof of the initial OS/interpreter/native memory.
The original parent must load these exact modules through its admitted bootstrap
before adverse input.  No user supplied arbitrary checker is accepted.
"""
import ast
import builtins
import __future__
import copy
import dataclasses
import fcntl
import gc
import hashlib
import json
import marshal
import math
import os
import pathlib
import posix
import resource
import signal
import struct
import subprocess
import sys
import time
import types
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying

_TYPE, _LEN, _COMPILE = type, len, compile
_MODULE_DICT = types.ModuleType.__dict__['__dict__'].__get__
_FUNCTION_GETTERS = tuple(types.FunctionType.__dict__[name].__get__ for name in
    ('__code__', '__globals__', '__builtins__', '__defaults__', '__kwdefaults__', '__closure__', '__dict__'))
_CELL_GET = types.CellType.__dict__['cell_contents'].__get__
_CLASS_DICT = type.__dict__['__dict__'].__get__
_STATIC_FUNCTION = staticmethod.__dict__['__func__'].__get__
_CLASS_FUNCTION = classmethod.__dict__['__func__'].__get__
_SOURCE_RECEIVERS = []
_STDLIB_MODULES = {name: module for name, module in tuple(sys.modules.items())
                   if _TYPE(name) is str and _TYPE(module) is types.ModuleType}
MAX_MODULES = 48
MAX_GLOBALS = 512

# These exact registries are intentionally mutated only by their original
# source.  Their object identities are still checked.  Private-state sabotage
# by code already running in this trusted parent remains outside the boundary.
_MUTABLE_NAMES = {
    'epoch_copy_v5': ('_CONTROL',),
    'selected_child_bindings_v1': ('_INSTALLATIONS', '_ENTRY_ATTEMPTS'),
    'h25_parent_supervisor': ('_GUARD_ATTEMPTS', '_PUBLICATION_BINDING', '_SUPERVISION_CURRENT', '_SUPERVISION_HISTORY'),
    'component_control_root_v1': ('_STATE', '_CALLBACKS', '_RETAINED'),
    'component_receiver_closure_v1': ('_SOURCE_RECEIVERS',),
    'persistent_replay_v1': ('_BATCHES',),
    'replay_receiver_closure_v1': ('_SOURCE_RECEIVERS',),
    'epoch_parent_v5': ('_RESERVED_EPOCHS', '_PARENT_OWNERS'),
    'epoch_schema_v5': ('_ERROR_OWNERS',),
    'epoch_stop_v5': ('_SINK_REGISTRY',),
    'parent_domain_v1': ('_DOMAINS',),
    'parent_completion_v1': ('_PARENTS', '_PROCESS'),
    'parent_closure_v1': ('_SOURCE_RECEIVERS',),
    'policy_receiver_closure_v1': ('_SOURCE_RECEIVERS',),
    'policy_parent_domain_v1': ('_OWNERS',),
    'policy_process_domain_v1': ('_DOMAINS',),
}
_GATE_SUFFIXES = ('CONFIGURATION', 'SOURCE_REVIEW', 'EXECUTION_APPROVAL', 'FUNDING',
                  'STAGE_APPROVAL', 'COMMAND_APPROVAL', 'VALIDATION_EXECUTION')
# These five source-None gates have one exact native immutable runtime form.
# Their expected contents come only from the independently pinned parent plan.
_CONFIGURED_GATE_NAMES = ('RUNTIME_PROFILE', 'KERNEL_EXEC_PROFILE',
    'PHASED_FD_CONTRACT', 'TERMINAL_STATUS_CONTRACT', 'REPLAY_BINDING')


def _namespace(module):
    schema.need(_TYPE(module) is types.ModuleType, 'exact original module required')
    namespace = _MODULE_DICT(module, types.ModuleType)
    schema.need(_TYPE(namespace) is dict and _LEN(namespace) <= MAX_GLOBALS,
                'original module namespace bound differs')
    for key in namespace:
        schema.text(key, 256)
    return namespace


def _function_record(function):
    schema.need(_TYPE(function) is types.FunctionType, 'exact source function required')
    values = tuple(getter(function, types.FunctionType) for getter in _FUNCTION_GETTERS)
    closure = values[5]
    cells = () if closure is None else tuple((cell, _CELL_GET(cell, types.CellType)) for cell in closure)
    schema.need(_LEN(cells) <= 64, 'source function closure bound exceeded')
    return function, values, cells


def _function_check(record):
    function, values, cells = record
    schema.need(_TYPE(function) is types.FunctionType, 'source function identity changed')
    for getter, expected in zip(_FUNCTION_GETTERS, values):
        schema.need(getter(function, types.FunctionType) is expected,
                    'source function code/globals/builtins/defaults/closure/dict changed')
    for cell, expected in cells:
        schema.need(_CELL_GET(cell, types.CellType) is expected, 'source function closure contents changed')


def _codes(code, result):
    result.setdefault(code.co_qualname, []).append(code)
    for child in code.co_consts:
        if _TYPE(child) is types.CodeType:
            _codes(child, result)


def _data(value, depth=0):
    """Snapshot literal data only; no foreign repr/hash/eq/iteration protocols."""
    schema.need(depth <= 32, 'literal snapshot depth exceeded')
    kind = _TYPE(value)
    if value is None or kind in (str, int, bool, bytes, float):
        return (kind, value)
    if kind in (list, tuple):
        schema.need(_LEN(value) <= 65536, 'literal sequence bound exceeded')
        return (kind, tuple(_data(item, depth + 1) for item in value))
    if kind is dict:
        schema.need(_LEN(value) <= 8192, 'literal mapping bound exceeded')
        for key in value:
            schema.need(_TYPE(key) in (str, int), 'nonliteral mapping key')
        return (kind, tuple((_data(key, depth + 1), _data(item, depth + 1))
                            for key, item in value.items()))
    if kind in (set, frozenset):
        schema.need(_LEN(value) <= 8192 and all(_TYPE(item) in (str, int) for item in value),
                    'nonliteral set value')
        return (kind, frozenset(value))
    raise schema.EpochStop('not literal data')


def _validate_code(function, compiled_codes, namespace):
    values = tuple(getter(function, types.FunctionType) for getter in _FUNCTION_GETTERS)
    code = values[0]
    schema.need(values[1] is namespace and values[2] is builtins.__dict__,
                'source function original namespace/builtins differs')
    candidates = compiled_codes.get(code.co_qualname, ())
    encoded = marshal.dumps(code)
    schema.need(any(marshal.dumps(expected) == encoded for expected in candidates),
                'receiving function bytecode differs from pinned source')


def _configuration_profile(profile):
    """Validate only bounded native data; this is no callable/PASS authority."""
    schema.exact(profile, ('schema', 'gate_digests'))
    schema.text(profile['schema'], 64)
    schema.need(profile['schema'] == 'h25-policy-parent-gate-profile-v2',
                'configured receiver profile schema differs')
    digests = profile['gate_digests']
    schema.exact(digests, _CONFIGURED_GATE_NAMES)
    for key in _CONFIGURED_GATE_NAMES:
        schema.digest(digests[key])
    return tuple((key, digests[key]) for key in _CONFIGURED_GATE_NAMES)


def _configured_gate(value, key, expected_digest):
    """Type-check before equality/iteration; retain only exact tuple/str data."""
    schema.need(_TYPE(value) is tuple and _LEN(value) == 2,
                'configured receiver gate tuple shape differs')
    schema.text(value[0], 64)
    schema.need(value[0] == key, 'configured receiver gate label differs')
    schema.digest(value[1])
    schema.need(value[1] == expected_digest, 'configured receiver gate admission differs')
    return (value[0], value[1])


def bind_receivers(modules, source_policy, error_owner, configuration_profile):
    """Bind actual selected modules after the reached before-capture installer."""
    schema.owner_state(error_owner)
    schema.need(type(modules) is dict and 1 <= len(modules) <= MAX_MODULES and
                type(source_policy) is dict and set(modules) == set(source_policy),
                'exact finite actual selected module closure required')
    binding = modules['selected_child_bindings_v1']
    schema.need(binding is sys.modules['selected_child_bindings_v1'], 'actual selected source constructor absent')
    component = modules['component_control_root_v1']
    context = _namespace(component)['CONTEXT_CONFIGURATION']
    token = binding.require_selected_child(modules, source_policy, context['unit_id'], context['mode'])
    installed = binding._entry(token)
    expected_gates = dict(_configuration_profile(configuration_profile))
    records = []
    for name in sorted(modules):
        module = modules[name]; namespace = _namespace(module); pin = source_policy[name]
        schema.need(sys.modules.get(name) is module and namespace['__name__'] == name and
                    namespace['__file__'] == pin['path'], 'actual selected module/name/path differs')
        raw = copying.read_verified(pin, schema.FILE_BYTES, error_owner=error_owner)
        tree, functions, classes, imports = binding._source_objects(module, pin, raw, modules)
        literals, configured = [], []
        for node in tree.body:
            if type(node) is not ast.Assign or len(node.targets) != 1 or type(node.targets[0]) is not ast.Name:
                continue
            key = node.targets[0].id
            if key in installed['bindings'][name]:
                value = installed['bindings'][name][key]
                schema.need(namespace[key] is value and type(node.value) is ast.Constant and
                            node.value.value is None, 'gate was not installed into its exact source None slot')
                configured.append((key, value, binding._data(value)))
                if name == 'policy_parent_domain_v1' and key in _CONFIGURED_GATE_NAMES:
                    _configured_gate(value, key, expected_gates[key])
                continue
            if key in _MUTABLE_NAMES.get(name, ()):
                continue
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError):
                continue
            schema.need(_data(namespace[key]) == _data(value), 'actual selected source literal changed')
            literals.append((key, _data(value)))
        records.append((name, module, namespace, pin, tuple(namespace.items()),
                        functions, classes, tuple(literals), imports, tuple(configured)))
    schema.need(len(_SOURCE_RECEIVERS) < 2, 'receiver registration bound exceeded')
    authority = object()
    _SOURCE_RECEIVERS.append((authority, tuple(records), error_owner, binding, token))
    check_receivers(authority)
    return authority


def _packet(authority):
    schema.need(type(authority) is object, 'exact original receiver authority required')
    for packet in _SOURCE_RECEIVERS:
        if packet[0] is authority:
            return packet
    raise schema.EpochStop('unregistered actual receiver authority')


def check_receivers(authority):
    unused, records, error_owner, binding, token = _packet(authority)
    schema.need(sys.modules.get('selected_child_bindings_v1') is binding,
                'actual selected source constructor changed')
    for name, module, namespace, pin, original, functions, classes, literals, imports, configured in records:
        schema.need(sys.modules.get(name) is module and _namespace(module) is namespace and
                    len(namespace) == len(original), 'actual selected module namespace changed')
        for key, value in original:
            schema.need(namespace.get(key) is value, 'actual selected global object changed')
        for record in functions:
            binding._function_check(record)
        binding._classes_unchanged(classes)
        binding._imports_unchanged(imports)
        for key, expected in literals:
            schema.need(_data(namespace[key]) == expected, 'source literal contents changed')
        for key, value, expected in configured:
            schema.need(namespace[key] is value and binding._data(value) == expected,
                        'actual installed gate identity/contents changed')
        copying.verify(pin, schema.FILE_BYTES, error_owner=error_owner)
    return None


def receiver(authority, module_name, function_name):
    check_receivers(authority)
    unused, records, error_owner, binding, token = _packet(authority)
    for name, module, namespace, pin, original, functions, classes, literals, imports, configured in records:
        if name == module_name:
            value = namespace[function_name]
            schema.need(type(value) is types.FunctionType, 'fixed actual receiving function required')
            return value
    raise schema.EpochStop('fixed actual receiving module absent')
