"""Private operand-set reuse for one authenticated frozen full-caller phase.

The parent owns the new whole-tail execution invariant. This is not inherited
from the native kernel guard and is not a generic alias/security detector.
Standalone, unsupported and unleased calls delegate the literal source.
No scientific module is imported here; the parent supplies an isolated module.
"""
from __future__ import annotations

import _thread
import ast
import builtins
import copy
import fractions
import gc
import hashlib
from pathlib import Path
import signal
import sys
from types import CodeType, FunctionType, GetSetDescriptorType, MemberDescriptorType, ModuleType

SOURCE_SHA256 = "d623617f7c5cb3189580883a8ab30c0bd3832688ae3f1f0c1f881bbbbff8e0c1"
FRACTION_SOURCE_PINS = (
    ("cf33568f7b767f66896995a7a81cc662e8be226f2e58efb61d2028f64eb5d231",
     "recorded-local-cpython-3.12.3"),
    ("d52d1ab9d5be26924e4914a5e40069c992bbfa68f773694c2e5ee8452d0766a0",
     "official-cpython-3.12.15-e848e4b09ca4bc67c0041c9ce7526dae471d4c36"),
)
_TYPE, _OBJECT, _DICT, _LIST, _TUPLE, _INT = type, object, dict, list, tuple, int
_STR = str
_LEN, _SET, _COMPILE = len, set, compile
_GET = dict.get
_OBJGET = object.__getattribute__
_TYPEGET = type.__getattribute__
_CLEAR = list.clear
_BUILTINS = builtins.__dict__
_FRACTION = fractions.Fraction
_BUILTIN_NAMES = ("type", "object", "set", "len", "sum", "enumerate", "dict",
                  "int", "list", "tuple", "all", "range", "hash", "abs", "pow",
                  "isinstance", "super")
_BUILTIN_RECORD = tuple((name, _BUILTINS[name]) for name in _BUILTIN_NAMES)
_SOURCE_LOOKUPS = ("set", "len", "sum", "enumerate", "dict")


def _need(condition, message):
    if not condition:
        raise RuntimeError(message)


def _function_record(function):
    if _TYPE(function) is not FunctionType:
        return None
    closure = function.__closure__
    cells = () if closure is None else _TUPLE((cell, cell.cell_contents) for cell in closure)
    return (function, function.__code__, function.__globals__, function.__builtins__,
            function.__defaults__, function.__kwdefaults__, closure, cells)


def _function_fresh(record):
    function, code, namespace, effective_builtins, defaults, kwdefaults, closure, cells = record
    if not (function.__code__ is code and function.__globals__ is namespace and
            function.__builtins__ is effective_builtins and function.__defaults__ is defaults and
            function.__kwdefaults__ is kwdefaults and function.__closure__ is closure):
        return False
    for cell, value in cells:
        try:
            if cell.cell_contents is not value:
                return False
        except ValueError:
            return False
    return True


def _ordinary_class(cls):
    if _TYPE(cls) is not _TYPE or _TYPEGET(cls, "__mro__") != (cls, _OBJECT):
        return False
    attributes = _TYPEGET(cls, "__dict__")
    if "__getattr__" in attributes or _TYPEGET(cls, "__getattribute__") is not _OBJECT.__getattribute__:
        return False
    if _TYPEGET(cls, "__new__") is not _OBJECT.__new__:
        return False
    for name in ("__dict__", "__weakref__"):
        descriptor = attributes.get(name)
        if _TYPE(descriptor) is not GetSetDescriptorType or descriptor.__objclass__ is not cls:
            return False
    return True


def _ordinary_dict(value, cls):
    if _TYPE(value) is not cls or not _ordinary_class(cls):
        return None
    namespace = _OBJGET(value, "__dict__")
    return namespace if _TYPE(namespace) is _DICT else None


def _triple(value):
    return (_TYPE(value) is _TUPLE and _LEN(value) == 3 and
            _TYPE(value[0]) is _INT and _TYPE(value[1]) is _INT and _TYPE(value[2]) is _INT)


def _hooks_clear():
    """Known instrumentation denial only; not a generic finalizer theorem."""
    if sys.gettrace() is not None or sys.getprofile() is not None:
        return False
    if _TYPE(gc.callbacks) is not _LIST or _LEN(gc.callbacks) != 0 or _thread._count() != 0:
        return False
    monitoring = getattr(sys, "monitoring", None)
    if monitoring is not None:
        for tool in range(6):
            if monitoring.get_tool(tool) is not None:
                return False
    for number in signal.valid_signals():
        handler = signal.getsignal(number)
        if handler is not signal.SIG_DFL and handler is not signal.SIG_IGN and handler is not signal.default_int_handler:
            return False
    return True


def _code_named(code, name):
    return next(item for item in code.co_consts if _TYPE(item) is CodeType and item.co_name == name)


def _authenticate_function(function, expected, namespace):
    _need(_TYPE(function) is FunctionType and function.__globals__ is namespace and
          function.__builtins__ is _BUILTINS and function.__code__ == expected,
          "Set reuse requires the exact original source function")


class _Token:
    __slots__ = ()


class _LeaseOwner:
    """Parent-private one-call capability; only identity/state, never operand sets."""

    def __init__(self, module, original, source_functions, class_names, receipt):
        self.module = module
        self.namespace = module.__dict__
        self.original = original
        self.circuit_class = self.namespace["ComplexSideCircuit"]
        self.checks_class = self.namespace["Checks"]
        self.class_names = class_names
        self.source_functions = source_functions
        self.receipt = receipt
        self.sealed = False
        self.cli_active = False
        self.used = False
        self.current = None
        self.circuit = self.checks = self.triples = None
        self.class_records = ()
        self.function_records = ()
        self.fraction_globals = _TUPLE(fractions.__dict__.items())
        self.fraction_classes = _TUPLE((cls, _TYPEGET(cls, "__mro__"),
                                       _TUPLE(_TYPEGET(cls, "__dict__").items()))
                                      for cls in _FRACTION.__mro__ if cls is not _OBJECT)
        self.math_gcd = fractions.math.gcd
        self.rational = fractions.numbers.Rational
        self.complex = fractions.numbers.Complex
        self.hash_wrapper = fractions._hash_algorithm
        self.hash_wrapped = fractions._hash_algorithm.__wrapped__
        fraction_functions = []
        for _, _, attributes in self.fraction_classes:
            for _, value in attributes:
                if _TYPE(value) is FunctionType:
                    fraction_functions.append(value)
                elif _TYPE(value) is property:
                    fraction_functions.extend(item for item in (value.fget, value.fset, value.fdel) if item is not None)
        fraction_functions.append(self.hash_wrapped)
        self.fraction_functions = _TUPLE(_function_record(function) for function in fraction_functions)

    def seal(self):
        """Parent calls once after installing all constructor/map phase wrappers."""
        _need(not self.sealed and not self.cli_active, "Set reuse owner already sealed or active")
        classes = (self.circuit_class, self.checks_class)
        records = []
        functions = _LIST(self.source_functions)
        for cls, names in zip(classes, self.class_names):
            _need(_ordinary_class(cls), "Set reuse requires ordinary frozen class dispatch")
            attributes = _TYPEGET(cls, "__dict__")
            _need(_SET(attributes) == names, "Set reuse class member shape changed")
            records.append((cls, _TYPEGET(cls, "__mro__"), _TUPLE(attributes.items())))
            functions.extend(value for value in attributes.values() if _TYPE(value) is FunctionType)
        self.class_records = _TUPLE(records)
        self.function_records = _TUPLE(_function_record(function) for function in functions)
        self.sealed = True

    def arm_cli(self):
        """Parent attests the pinned fresh CLI; do not call for a generic API use."""
        _need(self.sealed and not self.cli_active and self.circuit is None and not self.used,
              "Set reuse allowance cannot be reused")
        self.cli_active = True
        self.receipt["allowances_armed"] += 1

    def capture_c(self, circuit):
        """Called only after the parent-observed original constructor returns."""
        if not self.cli_active or self.circuit is not None or self.used:
            return False
        namespace = _ordinary_dict(circuit, self.circuit_class)
        if namespace is None:
            return False
        triples = _GET(namespace, "triples")
        if _TYPE(triples) is not _LIST:
            return False
        self.circuit, self.triples = circuit, triples
        self.receipt["circuits_captured"] += 1
        return True

    def capture_checks(self, checks):
        """Called only after the parent-observed original Checks init returns."""
        if not self.cli_active or self.circuit is None or self.checks is not None or self.used:
            return False
        namespace = _ordinary_dict(checks, self.checks_class)
        if namespace is None or _GET(namespace, "c") is not self.circuit:
            return False
        self.checks = checks
        self.receipt["checks_captured"] += 1
        return True

    def _fresh(self):
        if (_TYPE(self.module) is not ModuleType or self.module.__dict__ is not self.namespace or
                _GET(self.namespace, "Checks") is not self.checks_class or
                _GET(self.namespace, "ComplexSideCircuit") is not self.circuit_class or
                _GET(self.namespace, "Q") is not _FRACTION or
                _GET(self.namespace, "__builtins__") is not _BUILTINS):
            return False
        for name, expected in _BUILTIN_RECORD:
            if _GET(_BUILTINS, name) is not expected:
                return False
        for name in _SOURCE_LOOKUPS:
            if name in self.namespace:
                return False
        for cls, mro, items in self.class_records + self.fraction_classes:
            if _TYPEGET(cls, "__mro__") is not mro:
                return False
            attributes = _TYPEGET(cls, "__dict__")
            if _LEN(attributes) != _LEN(items):
                return False
            for name, value in items:
                if attributes.get(name) is not value:
                    return False
        for record in self.function_records + self.fraction_functions:
            if not _function_fresh(record):
                return False
        if _LEN(fractions.__dict__) != _LEN(self.fraction_globals):
            return False
        for name, value in self.fraction_globals:
            if _GET(fractions.__dict__, name) is not value:
                return False
        return (fractions.math.gcd is self.math_gcd and
                fractions.numbers.Rational is self.rational and
                fractions.numbers.Complex is self.complex and
                fractions._hash_algorithm is self.hash_wrapper and
                self.hash_wrapper.__wrapped__ is self.hash_wrapped)

    def reserve(self, checks):
        """Consumed before prefix; wrong or unleased objects get literal fallback."""
        self.receipt["entries"] += 1
        if not self.cli_active or self.used or self.current is not None or checks is not self.checks:
            return None
        namespace = _ordinary_dict(checks, self.checks_class)
        if namespace is None or _GET(namespace, "c") is not self.circuit:
            return None
        self.used = True
        if not self._fresh() or not _hooks_clear():
            return None
        token = _Token()
        self.current = token
        self.receipt["reservations"] += 1
        return token

    def admit(self, token, checks, circuit, got):
        """Called after the original prefix, using its actual local got mapping."""
        if (token is None or token is not self.current or not self.cli_active or
                checks is not self.checks or circuit is not self.circuit or
                not self._fresh() or not _hooks_clear()):
            return False
        check_dict = _ordinary_dict(checks, self.checks_class)
        circuit_dict = _ordinary_dict(circuit, self.circuit_class)
        if check_dict is None or circuit_dict is None or _GET(check_dict, "c") is not circuit:
            return False
        triples = _GET(circuit_dict, "triples")
        if triples is not self.triples or _TYPE(triples) is not _LIST:
            return False
        for triple in triples:
            if not _triple(triple):
                return False
        if _TYPE(got) is not _DICT:
            return False
        for key, value in got.items():
            if (_TYPE(key) is not _TUPLE or _LEN(key) != 2 or not _triple(key[0]) or
                    _TYPE(key[1]) is not _FRACTION or _TYPE(value) is not _INT):
                return False
            coefficient = key[1]
            if (_TYPE(_OBJGET(coefficient, "_numerator")) is not _INT or
                    _TYPE(_OBJGET(coefficient, "_denominator")) is not _INT):
                return False
        self.receipt["fast_admissions"] += 1
        return True

    def fallback(self):
        self.receipt["fallback_calls"] += 1

    def constructed(self, count):
        self.receipt["private_operand_sets_constructed"] += count

    def expire(self, token):
        if token is not None and token is self.current:
            self.current = None
            self.receipt["reservations_expired"] += 1

    def disarm_cli(self):
        self.current = None
        self.cli_active = False
        self.circuit = self.checks = self.triples = None


def _fraction_source_profile(digest):
    """Exact reviewed source allowlist; no version-only or shape-only admission."""
    if _TYPE(digest) is _STR:
        for expected, profile in FRACTION_SOURCE_PINS:
            if digest == expected:
                return profile
    raise RuntimeError("Set reuse Fraction source differs")


def _fraction_source_check():
    raw = Path(fractions.__file__).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    profile = _fraction_source_profile(digest)
    compiled = _COMPILE(raw, fractions.__file__, "exec", dont_inherit=True, optimize=sys.flags.optimize)
    fraction_code = _code_named(compiled, "Fraction")
    _need(_TYPEGET(_FRACTION, "__getattribute__") is _OBJECT.__getattribute__,
          "Set reuse Fraction attribute dispatch differs")
    for name in ("_numerator", "_denominator"):
        descriptor = _TYPEGET(_FRACTION, name)
        _need(_TYPE(descriptor) is MemberDescriptorType and descriptor.__objclass__ is _FRACTION,
              "Set reuse Fraction slot descriptor differs")
    _need(fractions.numbers.Rational is _FRACTION.__mro__[1] and
          fractions.numbers.Complex in _FRACTION.__mro__,
          "Set reuse Fraction number-class resolution differs")
    for name in ("__new__", "__hash__", "__eq__"):
        _authenticate_function(_TYPEGET(_FRACTION, name), _code_named(fraction_code, name), fractions.__dict__)
    for name in ("numerator", "denominator"):
        _authenticate_function(_TYPEGET(_FRACTION, name).fget, _code_named(fraction_code, name), fractions.__dict__)
    _authenticate_function(fractions._hash_algorithm.__wrapped__, _code_named(compiled, "_hash_algorithm"), fractions.__dict__)
    return digest, profile


def _generate(module, method_ast, owner, original):
    """Only original prefix/tail AST plus declared private bookkeeping changes."""
    _need(_LEN(method_ast.body) == 7 and _TYPE(method_ast.body[3]) is ast.For and
          _TYPE(method_ast.body[4]) is ast.Assign and _TYPE(method_ast.body[5]) is ast.For,
          "Unexpected pinned verify_map AST layout")
    prefix = copy.deepcopy(method_ast.body[:4])
    fallback_tail = copy.deepcopy(method_ast.body[4:])
    template = ast.parse('''
def _h25_sr_factory(_h25_sr_enter, _h25_sr_admit, _h25_sr_expire, _h25_sr_original,
                    _h25_sr_fallback, _h25_sr_constructed, _h25_sr_clear):
    def verify_map(self):
        _h25_sr_token = _h25_sr_enter(self)
        _h25_sr_sets = None
        _h25_sr_left = None
        try:
            if _h25_sr_token is None:
                _h25_sr_fallback()
                return _h25_sr_original(self)
            _H25_PREFIX
            if not _h25_sr_admit(_h25_sr_token, self, c, got):
                _h25_sr_fallback()
                _H25_FALLBACK
            _h25_sr_sets = [set(T) for T in c.triples]
            _h25_sr_constructed(len(_h25_sr_sets))
            nonzero = 0
            for _h25_sr_position, S in enumerate(c.triples):
                _h25_sr_left = _h25_sr_sets[_h25_sr_position]
                zero = sum(1 << i for i, T in enumerate(c.triples)
                           if not _h25_sr_left & _h25_sr_sets[i])
                two = sum(1 << i for i, T in enumerate(c.triples)
                          if len(_h25_sr_left & _h25_sr_sets[i]) == 2)
                assert got.get((S, Q(1, 2)), 0) == zero and got.get((S, Q(-1, 2)), 0) == two
                nonzero += zero.bit_count()+two.bit_count()
            return dict(targets=len(c.triples), nonzero_coefficients=nonzero,
                        side_map_exact=True, coefficients='+1/2 disjoint, -1/2 intersection two')
        finally:
            if _h25_sr_sets is not None:
                _h25_sr_clear(_h25_sr_sets)
            _h25_sr_left = None
            _h25_sr_sets = None
            _h25_sr_expire(_h25_sr_token)
    return verify_map
''')
    method = template.body[0].body[0]
    guarded = method.body[3]
    _need(_TYPE(guarded) is ast.Try, "Internal set adapter AST layout changed")
    replaced = []
    for statement in guarded.body:
        if _TYPE(statement) is ast.Expr and _TYPE(statement.value) is ast.Name and statement.value.id == "_H25_PREFIX":
            replaced.extend(prefix)
        elif _TYPE(statement) is ast.If and statement.body and any(
                _TYPE(item) is ast.Expr and _TYPE(item.value) is ast.Name and item.value.id == "_H25_FALLBACK"
                for item in statement.body):
            statement.body = statement.body[:1] + fallback_tail
            replaced.append(statement)
        else:
            replaced.append(statement)
    guarded.body = replaced
    ast.fix_missing_locations(template)
    namespace = module.__dict__
    name = "_h25_sr_factory"
    _need(name not in namespace, "Set reuse helper name collision")
    try:
        exec(_COMPILE(template, "<h25-private-set-reuse>", "exec", dont_inherit=True,
                      optimize=sys.flags.optimize), namespace)
        factory = namespace[name]
        function = factory(owner.reserve, owner.admit, owner.expire, original,
                           owner.fallback, owner.constructed, _CLEAR)
    finally:
        namespace.pop(name, None)
    return function


def bind_verify_map(module):
    """Return verify_map/owner/receipt; parent installs, wraps, seals, then arms.

    This factory must receive an isolated candidate module. Keep the unchanged
    baseline/reference in another module/process; existing globals are never
    copied or rebound, so ordinary fallback retains live source resolution.
    """
    _need(_TYPE(module) is ModuleType, "Set reuse needs an exact source module")
    namespace = module.__dict__
    path = Path(namespace["__file__"])
    raw = path.read_bytes()
    _need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "Set reuse scientific source differs")
    _need(_GET(namespace, "__builtins__") is _BUILTINS and _GET(namespace, "Q") is _FRACTION,
          "Set reuse source calling environment differs")
    for name, value in _BUILTIN_RECORD:
        _need(_GET(_BUILTINS, name) is value, "Set reuse builtin identity differs")
    for name in _SOURCE_LOOKUPS:
        _need(name not in namespace, "Set reuse source shadows a builtin")
    compiled = _COMPILE(raw, str(path), "exec", dont_inherit=True, optimize=sys.flags.optimize)
    source_functions = []
    class_names = []
    for name in ("ComplexSideCircuit", "Checks"):
        cls = namespace[name]
        _need(_ordinary_class(cls), "Set reuse source class dispatch differs")
        class_code = _code_named(compiled, name)
        attributes = _TYPEGET(cls, "__dict__")
        expected_names = {"__module__", "__doc__", "__dict__", "__weakref__"}
        for code in class_code.co_consts:
            if _TYPE(code) is CodeType:
                expected_names.add(code.co_name)
                function = attributes.get(code.co_name)
                _authenticate_function(function, code, namespace)
                source_functions.append(function)
        _need(_SET(attributes) == expected_names, "Set reuse source class members differ")
        class_names.append(expected_names)
    fraction_digest, fraction_profile = _fraction_source_check()
    original = namespace["Checks"].verify_map
    parsed = ast.parse(raw, filename=str(path))
    checks_ast = next(item for item in parsed.body if _TYPE(item) is ast.ClassDef and item.name == "Checks")
    method_ast = next(item for item in checks_ast.body if _TYPE(item) is ast.FunctionDef and item.name == "verify_map")
    receipt = {"schema": "h25-private-set-reuse-v1", "source_sha256": SOURCE_SHA256,
               "fraction_sha256": fraction_digest, "fraction_source_profile": fraction_profile,
               "allowances_armed": 0, "circuits_captured": 0,
               "checks_captured": 0, "entries": 0, "reservations": 0, "fast_admissions": 0,
               "fallback_calls": 0, "private_operand_sets_constructed": 0, "reservations_expired": 0}
    owner = _LeaseOwner(module, original, _TUPLE(source_functions), _TUPLE(class_names), receipt)
    candidate = _generate(module, method_ast, owner, original)
    return {"verify_map": candidate, "owner": owner, "receipt": receipt, "original": original}
