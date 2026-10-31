"""Source-bound packed GF(2), with a fail-closed stable-runtime boundary.

Supported bindings use the literal frozen source, ordinary built-ins and the
original Label dispatch. Resolved method/helper globals and built-ins, helper
code/defaults/closures and class/native dispatch must remain unchanged after
binding. Calls run serially with no mutation during a call; detected boundary
drift is rejected before arithmetic or fallback. This is not a sandbox
against arbitrary mutation of this backend or native process memory.
"""
from __future__ import annotations

import builtins
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
import sysconfig
from types import BuiltinFunctionType, CodeType, FunctionType, GetSetDescriptorType, ModuleType

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "complex_circuit.py"
SOURCE_SHA256 = "d623617f7c5cb3189580883a8ab30c0bd3832688ae3f1f0c1f881bbbbff8e0c1"
CALLER_SHA256 = "0da395e67ac04fa213494e71012c1b19b544596d34cdce5a3b172b1fb6af5f1b"

# Anchored operations keep drift checks independent of the source's lookup
# environment and avoid executing modified helper functions or descriptors.
_TYPE = type
_LEN = len
_INT = int
_DICT = dict
_LIST = list
_TUPLE = tuple
_OBJECT = object
_RUNTIME_ERROR = RuntimeError
_COMPILE = compile
_DICT_GET = dict.get
_DICT_VALUES = dict.values
_OBJECT_GETATTRIBUTE = object.__getattribute__
_BUILTINS = builtins.__dict__
_BUILTIN_NAMES = ("all", "enumerate", "len", "list", "max", "next", "range",
                  "sorted", "sum", "tuple", "int", "dict", "type", "object")
_CANONICAL_BUILTINS = {name: _BUILTINS[name] for name in _BUILTIN_NAMES}
_HELPER_NAMES = ("echelon", "reduce", "dot", "rank")
_TYPE_BUILTINS = {"list": _LIST, "tuple": _TUPLE, "int": _INT,
                  "dict": _DICT, "type": _TYPE, "object": _OBJECT}
_BIT_DESCRIPTORS = tuple((_INT, name, getattr(_INT, name)) for name in
                        ("bit_count", "bit_length", "__and__", "__xor__", "__lshift__", "__rshift__"))


def require(condition, message):
    if not condition:
        raise _RUNTIME_ERROR(message)


def _check_builtins():
    for name, expected in _CANONICAL_BUILTINS.items():
        require(_DICT_GET(_BUILTINS, name) is expected, "Runtime drift: builtin " + name)
        if name in _TYPE_BUILTINS:
            require(expected is _TYPE_BUILTINS[name], "Unexpected builtin type: " + name)
        elif name in ("enumerate", "range"):
            require(_TYPE(expected) is _TYPE and expected.__name__ == name and
                    expected.__module__ == "builtins" and not (expected.__flags__ & (1 << 9)),
                    "Unexpected builtin class: " + name)
        else:
            require(_TYPE(expected) is BuiltinFunctionType and expected.__name__ == name and
                    expected.__module__ == "builtins", "Unexpected builtin function: " + name)
    for owner, name, descriptor in _BIT_DESCRIPTORS:
        require(_TYPE.__getattribute__(owner, name) is descriptor, "Runtime drift: builtin integer semantics")


def verify_sources():
    raw = SOURCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "Frozen complex source changed")
    caller = (ROOT / "source" / "complex_network.py").read_bytes()
    require(hashlib.sha256(caller).hexdigest() == CALLER_SHA256, "Frozen caller source changed")
    return raw


def load_source(name):
    verify_sources()
    spec = importlib.util.spec_from_file_location(name, SOURCE)
    require(spec is not None and spec.loader is not None, "Missing frozen module loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _code_shape(code):
    """Compare source code using only exact immutable values, never user equality."""
    require(_TYPE(code) is CodeType, "Unexpected function code type")
    def constant(value):
        kind = _TYPE(value)
        if value is None or value is Ellipsis:
            return ("singleton", value is Ellipsis)
        if kind is _INT or kind is bool or kind is str or kind is bytes:
            return (kind.__name__, value)
        if kind is _TUPLE:
            return ("tuple", _TUPLE(constant(item) for item in value))
        if kind is CodeType:
            return ("code", _code_shape(value))
        raise _RUNTIME_ERROR("Unexpected mutable or custom constant in frozen function")
    fields = (code.co_argcount, code.co_posonlyargcount, code.co_kwonlyargcount,
              code.co_nlocals, code.co_stacksize, code.co_flags, code.co_code,
              code.co_names, code.co_varnames, code.co_freevars, code.co_cellvars,
              code.co_exceptiontable, code.co_linetable, code.co_firstlineno,
              code.co_filename, code.co_name, code.co_qualname, code.co_consts)
    return _TUPLE(constant(value) for value in fields)


def guard_module(module):
    """Validate code AND every resolved builtin/helper/Label dispatch owner."""
    _check_builtins()
    raw = verify_sources()
    require(_TYPE(module) is ModuleType, "Unexpected source module type")
    namespace = module.__dict__
    require(_TYPE(_DICT_GET(namespace, "__file__")) is str and _TYPE(_DICT_GET(namespace, "__name__")) is str, "Unexpected source module metadata types")
    require(Path(namespace["__file__"]).resolve() == SOURCE.resolve(), "Unexpected source module path")
    require(_DICT_GET(namespace, "__builtins__") is _BUILTINS, "Changed source builtins owner")
    for name in _BUILTIN_NAMES:
        require(name not in namespace, "Source builtin shadow: " + name)
    expected = _COMPILE(raw, str(SOURCE), "exec", dont_inherit=True, optimize=sys.flags.optimize)
    codes = {code.co_name: code for code in expected.co_consts if _TYPE(code) is CodeType}

    def check(function, expected_code, name):
        require(_TYPE(function) is FunctionType, "Non-function replacement: " + name)
        require(function.__globals__ is namespace, "Changed function globals: " + name)
        # A function captures its own builtins pointer when created; checking
        # only the module's current __builtins__ slot would miss a forged one.
        require(function.__builtins__ is _BUILTINS, "Changed effective function builtins: " + name)
        require(function.__closure__ is None and function.__defaults__ is None and
                function.__kwdefaults__ is None, "Changed function calling contract: " + name)
        require(_code_shape(function.__code__) == _code_shape(expected_code),
                "Changed frozen function code: " + name)

    for name in _HELPER_NAMES:
        check(_DICT_GET(namespace, name), codes[name], name)
    label = _DICT_GET(namespace, "Label")
    require(_TYPE(label) is _TYPE and label.__mro__ == (label, _OBJECT), "Changed Label class shape")
    require(_TYPE(label.__module__) is str and label.__module__ == module.__name__, "Changed Label module ownership")
    methods = {code.co_name: code for code in codes["Label"].co_consts if _TYPE(code) is CodeType}
    attributes = label.__dict__
    require(_LEN(attributes) == 4 + _LEN(methods), "Changed Label class attributes")
    for name in ("__module__", "__doc__", "__dict__", "__weakref__"):
        require(name in attributes, "Missing original Label descriptor")
    for name in ("__dict__", "__weakref__"):
        descriptor = attributes[name]
        require(_TYPE(descriptor) is GetSetDescriptorType and descriptor.__objclass__ is label,
                "Custom Label descriptor: " + name)
    for name, code in methods.items():
        check(attributes.get(name), code, "Label." + name)
    require(label.__getattribute__ is _OBJECT.__getattribute__ and label.__new__ is _OBJECT.__new__,
            "Custom Label attribute or construction dispatch")
    return label


class RuntimeGuard:
    """Identity-only freshness checks; no modified callable is invoked."""
    def __init__(self, module, label, native, original_functions):
        self.module = module
        self.namespace = module.__dict__
        self.label = label
        self.mro = label.__mro__
        self.class_items = _TUPLE(label.__dict__.items())
        self.global_items = _TUPLE((name, self.namespace[name]) for name in _HELPER_NAMES + ("Label", "__builtins__"))
        functions = _LIST(original_functions)
        functions.extend(value for _, value in self.class_items if _TYPE(value) is FunctionType)
        functions.append(self.namespace["rank"])
        self.functions = _TUPLE((function, function.__code__, function.__globals__, function.__builtins__,
                                 function.__defaults__, function.__kwdefaults__, function.__closure__,
                                 () if function.__closure__ is None else
                                 _TUPLE((cell, cell.cell_contents) for cell in function.__closure__))
                                for function in functions)
        self.native = native
        require(_TYPE(native) is ModuleType, "Unexpected native module type")
        self.native_items = _TUPLE((name, native.__dict__[name]) for name in ("gram_rank", "complement"))
        for name, function in self.native_items:
            require(_TYPE(function) is BuiltinFunctionType and function.__self__ is native,
                    "Changed native entry point: " + name)
        self.check()

    def check(self):
        # The source globals and Label remain a normal module and exact class;
        # lookups below therefore do not invoke user-defined descriptors.
        require(_TYPE(self.module) is ModuleType and self.module.__dict__ is self.namespace,
                "Runtime drift: source module dispatch")
        require(_TYPE(self.label) is _TYPE and self.label.__mro__ is self.mro,
                "Runtime drift: Label class dispatch")
        for name, value in self.global_items:
            require(_DICT_GET(self.namespace, name) is value, "Runtime drift: source helper " + name)
        for name, expected in _CANONICAL_BUILTINS.items():
            require(name not in self.namespace and _DICT_GET(_BUILTINS, name) is expected,
                    "Runtime drift: builtin lookup " + name)
        attributes = self.label.__dict__
        require(_LEN(attributes) == _LEN(self.class_items), "Runtime drift: Label descriptors")
        for name, value in self.class_items:
            require(attributes.get(name) is value, "Runtime drift: Label member " + name)
        for function, code, namespace, effective_builtins, defaults, kwdefaults, closure, cells in self.functions:
            require(function.__code__ is code and function.__globals__ is namespace and
                    function.__builtins__ is effective_builtins and function.__defaults__ is defaults and
                    function.__kwdefaults__ is kwdefaults and function.__closure__ is closure,
                    "Runtime drift: function code or calling environment")
            for cell, value in cells:
                require(cell.cell_contents is value, "Runtime drift: wrapper closure")
        require(_TYPE(self.native) is ModuleType, "Runtime drift: native module dispatch")
        for name, function in self.native_items:
            require(_DICT_GET(self.native.__dict__, name) is function, "Runtime drift: native entry point " + name)


class ComplementTrace:
    """Stream every ordered complement input and typed output, without retention.

    Snapshotting is confined to the exact Label/exact dict/int domain of the
    complete H25 workload. Finite fallback tests leave this observer disabled.
    """
    def __init__(self, label):
        self.label = label
        self.count = 0
        self.bytes = 0
        self.hasher = hashlib.sha256()

    def before(self, small, big):
        require(_TYPE(small) is self.label and _TYPE(big) is self.label, "Trace requires exact frozen Label objects")
        big_dict = _OBJECT_GETATTRIBUTE(big, "__dict__")
        small_dict = _OBJECT_GETATTRIBUTE(small, "__dict__")
        require(_TYPE(big_dict) is _DICT and _TYPE(small_dict) is _DICT, "Trace requires ordinary instance dictionaries")
        vs_basis = _DICT_GET(big_dict, "basis")
        us_basis = _DICT_GET(small_dict, "basis")
        require(_TYPE(vs_basis) is _DICT and _TYPE(us_basis) is _DICT, "Trace requires exact basis dictionaries")
        vs = _TUPLE(_DICT_VALUES(vs_basis))
        us = _TUPLE(_DICT_VALUES(us_basis))
        require(all(_TYPE(value) is _INT for value in us + vs), "Trace requires exact integer vectors")
        return us, vs

    def after(self, inputs, output):
        us, vs = inputs
        if output is None:
            result = {"type": "None"}
        else:
            require(_TYPE(output) is _LIST and all(_TYPE(value) is _INT for value in output),
                    "Trace requires an exact integer list or None result")
            result = {"type": "list", "values": output}
        record = {"call": self.count, "us": us, "vs": vs, "result": result}
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"
        self.hasher.update(encoded)
        self.bytes += _LEN(encoded)
        self.count += 1

    def receipt(self):
        return {"calls": self.count, "canonical_stream_bytes": self.bytes,
                "sha256": self.hasher.hexdigest(),
                "schema": "v2-jsonl:call,us,vs,result(type=list+values or type=None); ordered exact integer vectors"}


def build_native(directory):
    """Always cold compile/link/load once. The parent supplies the outer guard."""
    require(sys.implementation.name == "cpython" and sys.version_info[:2] == (3, 12),
            "This qualification is frozen to CPython 3.12")
    require(sys.platform.startswith("linux"), "This qualification is frozen to Linux")
    directory = Path(directory)
    require(not directory.exists(), "Refusing to reuse a native build directory")
    directory.mkdir(parents=True)
    source = ROOT / "native_gf2.c"
    source_before = source.read_bytes()
    source_hash = hashlib.sha256(source_before).hexdigest()
    suffix = sysconfig.get_config_var("EXT_SUFFIX")
    require(_TYPE(suffix) is str and suffix.endswith(".so"), "Unexpected extension suffix")
    target = directory / ("_packed_gf2" + suffix)
    compiler = shlex.split(sysconfig.get_config_var("CC") or "cc")
    require(compiler, "Missing configured C compiler")
    command = compiler + ["-shared", "-fPIC", "-O3", "-std=c11", "-Wall", "-Wextra", "-Werror",
                          "-I" + sysconfig.get_paths()["include"], str(source), "-o", str(target)]
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, timeout=90, check=False)
    manifest = {"command": command, "returncode": completed.returncode,
                "stdout": completed.stdout, "stderr": completed.stderr,
                "c_source_sha256": source_hash, "python": sys.version,
                "no_cached_binary": True}
    (directory / "build.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    require(completed.returncode == 0, "Native compilation failed; see build.json (no retry)")
    require(source.read_bytes() == source_before, "Native source changed during compilation")
    manifest["extension_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location("_packed_gf2", target)
    require(spec is not None and spec.loader is not None, "Missing extension loader")
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    (directory / "build.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return native, manifest


def attach_trace(module, rank_calls, complement_trace=None):
    """Baseline observers; original arithmetic and return objects stay intact."""
    original_rank = module.rank
    original_complement = module.Label.complement_in

    def traced_rank(rows):
        frozen_rows = _TUPLE(rows)
        answer = original_rank(frozen_rows)
        require(_TYPE(answer) is _INT, "Rank output type changed")
        rank_calls.append((frozen_rows, answer))
        return answer

    def traced_complement(self, other):
        inputs = complement_trace.before(self, other)
        answer = original_complement(self, other)
        complement_trace.after(inputs, answer)
        return answer

    module.rank = traced_rank
    if complement_trace is not None:
        module.Label.complement_in = traced_complement
    return original_rank


def bind(module, native, rank_calls=None, complement_trace=None):
    """Replace two methods only; any detected runtime drift is a hard failure."""
    require(_TYPE(native) is ModuleType, "Unexpected native module type")
    native_complement = _DICT_GET(native.__dict__, "complement")
    native_gram = _DICT_GET(native.__dict__, "gram_rank")
    require(_TYPE(native_complement) is BuiltinFunctionType and native_complement.__self__ is native and
            _TYPE(native_gram) is BuiltinFunctionType and native_gram.__self__ is native,
            "Missing or replaced native entry points")
    label = guard_module(module)
    original_functions = [module.__dict__[name] for name in _HELPER_NAMES]
    original_functions.extend(value for value in label.__dict__.values() if _TYPE(value) is FunctionType)
    original_complement = label.complement_in
    original_nondegenerate = label.nondegenerate
    original_dot = module.dot
    original_rank = module.rank
    if rank_calls is not None:
        attach_trace(module, rank_calls)
    counters = {"complement_native": 0, "complement_fallback": 0,
                "gram_native": 0, "gram_fallback": 0}
    runtime = None

    def complement_in(self, other):
        runtime.check()
        inputs = None if complement_trace is None else complement_trace.before(self, other)
        if _TYPE(self) is label and _TYPE(other) is label:
            big_dict = _OBJECT_GETATTRIBUTE(other, "__dict__")
            small_dict = _OBJECT_GETATTRIBUTE(self, "__dict__")
            if _TYPE(big_dict) is _DICT and _TYPE(small_dict) is _DICT:
                big = _DICT_GET(big_dict, "basis")
                small = _DICT_GET(small_dict, "basis")
                if _TYPE(big) is _DICT and _TYPE(small) is _DICT:
                    result = native_complement(small, big)
                    if result is not NotImplemented:
                        counters["complement_native"] += 1
                        if complement_trace is not None:
                            complement_trace.after(inputs, result)
                        return result
        counters["complement_fallback"] += 1
        result = original_complement(self, other)
        if complement_trace is not None:
            complement_trace.after(inputs, result)
        return result

    def nondegenerate(self):
        runtime.check()
        if _TYPE(self) is label:
            instance = _OBJECT_GETATTRIBUTE(self, "__dict__")
            if _TYPE(instance) is _DICT:
                basis = _DICT_GET(instance, "basis")
                if _TYPE(basis) is _DICT:
                    answer = native_gram(basis)
                    if answer is not NotImplemented:
                        rows, rank = answer
                        if rank_calls is not None:
                            require(_TYPE(rank) is _INT, "Native rank output type changed")
                            rank_calls.append((rows, rank))
                        counters["gram_native"] += 1
                        return rank == _LEN(rows)
        counters["gram_fallback"] += 1
        return original_nondegenerate(self)

    label.complement_in = complement_in
    label.nondegenerate = nondegenerate
    # Set the closure before capturing it, then initialize the guard in place.
    # Thus every captured cell identity is its final stable value.
    runtime = _OBJECT.__new__(RuntimeGuard)
    RuntimeGuard.__init__(runtime, module, label, native, original_functions)
    return {"counters": counters, "original_complement": original_complement,
            "original_nondegenerate": original_nondegenerate, "original_dot": original_dot,
            "original_rank": original_rank, "label": label, "runtime_guard": runtime}
