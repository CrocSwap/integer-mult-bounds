"""Finite concrete receiver admission inside the original trusted parent.

This verifies pinned source, bytecode derived from those bytes without executing
them, concrete local import edges, and the current captured object graph.  It is
not a new Python sandbox or proof of the initial OS/interpreter/native memory.
The original parent must load these exact modules through its admitted bootstrap
before adverse input.  No user supplied arbitrary checker is accepted.
"""
import ast
import argparse
import importlib.util as _importlib_util
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
import configured_inverse_v2 as configured_inverse
import bootstrap_bindings_v2 as binding_installer

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
MAX_MODULES = 63
MAX_GLOBALS = 512

# These exact registries are intentionally mutated only by their original
# source.  Their object identities are still checked.  Private-state sabotage
# by code already running in this trusted parent remains outside the boundary.
_MUTABLE_NAMES = {
    # Source-owned publication, guard, and terminal-custody registries retain
    # exact object identity; only the authenticated supervisor mutates them.
    'h25_parent_supervisor': ('_GUARD_ATTEMPTS', '_PUBLICATION_BINDING',
                              '_SUPERVISION_CURRENT', '_SUPERVISION_HISTORY'),
    'epoch_parent_v5': ('_RESERVED_EPOCHS', '_PARENT_OWNERS'),
    'epoch_schema_v5': ('_ERROR_OWNERS',),
    'epoch_stop_v5': ('_SINK_REGISTRY',),
    'parent_domain_v1': ('_DOMAINS',),
    'parent_completion_v1': ('_PARENTS', '_PROCESS'),
    'parent_closure_v1': ('_SOURCE_RECEIVERS',),
    'policy_receiver_closure_v1': ('_SOURCE_RECEIVERS',),
    'policy_parent_domain_v1': ('_OWNERS',),
    'policy_process_domain_v1': ('_DOMAINS',),
    'persistent_replay_v1': ('_BATCHES',),
    'replay_receiver_closure_v1': ('_SOURCE_RECEIVERS',),
    'negative_parent_v2': ('_OWNERS',),
    'negative_receiver_closure_v2': ('_SOURCE_RECEIVERS',),
    'negative_process_domain_v2': ('_DOMAINS',),
    'parent_orchestration_v2': ('_ORCHESTRATORS',),
    'family_batching_v1': ('_OWNERS', '_SOURCE_BINDINGS'),
    'owned_root_v2': ('_ROOT_PARENTS',),
    'fixture_parent_v2': ('_FIXTURE_PARENTS',),
    'orchestration_closure_v2': ('_SOURCE_RECEIVERS',),
    'bootstrap_bindings_v2': ('_INSTALLATIONS',),
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


def bind_receivers(modules, source_policy, error_owner, configuration_profile, configured_sources):
    """Only the source-fixed original parent calls this before child launch.

    source_policy is a separately pinned, prelaunch source inventory, never a
    report supplied by a child. configuration_profile is exact native data
    decoded from the independently admitted CONFIGURATION[mode] plan pin.
    Live gate values cannot supply their own expected digests.
    The two producer-specific validators have fixed
    names; unsupported or absent variant source cannot be substituted by a
    callable argument.  Every received module must be listed in the policy.
    """
    schema.owner_state(error_owner)
    schema.need(_TYPE(modules) is dict and 1 <= _LEN(modules) <= MAX_MODULES and
                _TYPE(source_policy) is dict, 'finite receiver module map required')
    for name in modules:
        schema.text(name, 128)
    for name in source_policy:
        schema.text(name, 128)
    schema.need(set(modules) == set(source_policy), 'exact receiver closure differs')
    expected_gates = dict(_configuration_profile(configuration_profile))
    schema.exact(configured_sources, tuple(modules))
    schema.need('policy_parent_domain_v1' in modules, 'configured policy receiver absent')
    records = []
    for name in sorted(modules):
        module = modules[name]
        namespace = _namespace(module)
        pin = source_policy[name]
        schema.blob(pin)
        raw = copying.read_verified_complete_v3(pin, schema.FILE_BYTES, error_owner=error_owner)
        schema.need(namespace.get('__name__') == name and namespace.get('__file__') == pin['path'],
                    'original receiving module origin differs')
        inverse_record = configured_sources[name]
        schema.need(inverse_record['module'] == name and inverse_record['configured_sha256'] == pin['sha256'],
                    'configured closure source pin differs')
        configured_literals = configured_inverse.verify_configured_source(raw, inverse_record)
        tree = ast.parse(raw, filename=pin['path'])
        compiled = _COMPILE(raw, pin['path'], 'exec', dont_inherit=True, optimize=sys.flags.optimize)
        compiled_codes = {}
        _codes(compiled, compiled_codes)
        functions, classes, literals, imports = [], [], [], []
        configured = []
        for node in tree.body:
            if _TYPE(node) is ast.FunctionDef:
                function = namespace[node.name]
                _validate_code(function, compiled_codes, namespace)
                functions.append(_function_record(function))
            elif _TYPE(node) is ast.ClassDef:
                cls = namespace[node.name]
                schema.need(_TYPE(cls) is type, 'source class type differs')
                class_namespace = _CLASS_DICT(cls, type)
                for item in node.body:
                    if _TYPE(item) is ast.FunctionDef:
                        method = class_namespace[item.name]
                        # The currently selected explicit methods have no
                        # property/classmethod/staticmethod decorators.
                        schema.need(not item.decorator_list, 'unreviewed decorated receiver method')
                        # Python implicitly wraps __new__ and two class hooks.
                        # No arbitrary descriptor protocol is invoked.
                        if item.name == '__new__' and _TYPE(method) is staticmethod:
                            method = _STATIC_FUNCTION(method, staticmethod)
                        elif item.name in ('__init_subclass__', '__class_getitem__') and _TYPE(method) is classmethod:
                            method = _CLASS_FUNCTION(method, classmethod)
                        _validate_code(method, compiled_codes, namespace)
                        functions.append(_function_record(method))
                # Dataclass-generated methods are part of the inherited
                # dataclasses/initial-parent trust, not compiled from this
                # class body.  Their actual original code/environment remains
                # captured and checked; they cannot be changed after capture.
                for method in class_namespace.values():
                    if _TYPE(method) is types.FunctionType and not any(method is r[0] for r in functions):
                        functions.append(_function_record(method))
                classes.append((cls, tuple(class_namespace.items())))
            elif _TYPE(node) in (ast.Import, ast.ImportFrom):
                for alias in node.names:
                    schema.need(alias.name != '*', 'star receiver import unsupported')
                    if _TYPE(node) is ast.Import:
                        source_name = alias.name
                        local_name = alias.asname or source_name.split('.')[0]
                        expected = modules.get(source_name, _STDLIB_MODULES.get(source_name))
                    else:
                        source_name = node.module
                        schema.need(node.level == 0, 'relative receiver import unsupported')
                        local_name = alias.asname or alias.name
                        source_module = modules.get(source_name, _STDLIB_MODULES.get(source_name))
                        schema.need(source_module is not None, 'receiver import dependency absent')
                        expected = _namespace(source_module).get(alias.name)
                    schema.need(expected is not None and namespace.get(local_name) is expected,
                                'concrete receiving import identity differs')
                    imports.append((local_name, expected))
            elif _TYPE(node) is ast.Assign:
                if _LEN(node.targets) != 1 or _TYPE(node.targets[0]) is not ast.Name:
                    continue
                key = node.targets[0].id
                if name == 'policy_parent_domain_v1' and key in _CONFIGURED_GATE_NAMES:
                    value = namespace[key]
                    snapshot = _configured_gate(value, key, expected_gates[key])
                    if key in configured_literals:
                        literal_snapshot = _configured_gate(configured_literals[key], key, expected_gates[key])
                        schema.need(snapshot == literal_snapshot,
                                    'configured source literal and runtime gate differ')
                    else:
                        schema.need(_TYPE(node.value) is ast.Constant and node.value.value is None,
                                    'installed gate no longer has its verified template None')
                        binding_installer.require_installed_gate(module, key, value)
                    configured.append((key, value, snapshot))
                    continue
                if key in _MUTABLE_NAMES.get(name, ()) or key.endswith(_GATE_SUFFIXES):
                    continue
                try:
                    literal = ast.literal_eval(node.value)
                except (ValueError, TypeError, SyntaxError):
                    continue
                schema.need(_data(namespace[key]) == _data(literal), 'receiver literal differs from source')
                literals.append((key, _data(literal)))
        if name == 'policy_parent_domain_v1':
            schema.need(tuple(row[0] for row in configured) == _CONFIGURED_GATE_NAMES,
                        'configured receiver gate source census differs')
        for function in namespace.values():
            if _TYPE(function) is types.FunctionType and not any(function is r[0] for r in functions):
                functions.append(_function_record(function))
        records.append((name, module, namespace, pin, tuple(namespace.items()),
                        tuple(functions), tuple(classes), tuple(literals), tuple(imports), tuple(configured)))
    capability = object()
    packet = (capability, tuple(records), error_owner)
    schema.need(_LEN(_SOURCE_RECEIVERS) < 1, 'receiver closure finite parent bound exceeded')
    _SOURCE_RECEIVERS.append(packet)
    check_receivers(capability)
    return capability


def _packet(capability):
    schema.need(_TYPE(capability) is object, 'exact receiver capability required')
    for packet in _SOURCE_RECEIVERS:
        if packet[0] is capability:
            return packet
    raise schema.EpochStop('unknown original receiver closure')


def check_receivers(capability):
    packet = _packet(capability)
    for name, module, namespace, pin, original_items, functions, classes, literals, imports, configured in packet[1]:
        schema.need(_namespace(module) is namespace and _LEN(namespace) == _LEN(original_items),
                    'receiver namespace identity/census changed')
        for key, expected in original_items:
            schema.need(namespace.get(key) is expected, 'receiver namespace binding changed')
        for key, original, snapshot in configured:
            schema.need(namespace[key] is original, 'configured receiver gate identity changed')
            schema.need(_configured_gate(namespace[key], key, snapshot[1]) == snapshot,
                        'configured receiver gate immutable contents changed')
        for record in functions:
            _function_check(record)
        for cls, items in classes:
            current = _CLASS_DICT(cls, type)
            schema.need(_LEN(current) == _LEN(items), 'receiver class census changed')
            for key, expected in items:
                schema.need(current.get(key) is expected, 'receiver class binding changed')
        for key, expected in literals:
            schema.need(_data(namespace[key]) == expected, 'receiver literal data changed')
        copying.verify(pin, error_owner=packet[2])
    return None


def receiver(capability, module_name, name):
    """Return only a specifically named original from the registered closure."""
    schema.text(module_name, 128)
    schema.text(name, 128)
    for row in _packet(capability)[1]:
        if row[0] == module_name:
            schema.need(name in row[2], 'fixed receiving entry missing')
            return row[2][name]
    raise schema.EpochStop('fixed receiving module missing')
