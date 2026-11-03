"""P2: candidate-only live guard with identity dedup and failure-only raises.

The caller installs the returned class into an isolated candidate backend before
binding. Original source admission, wrappers, arithmetic, observers and baseline
modules are not changed here. The original serial stable-runtime policy applies.
"""


def make_runtime_guard(backend):
    """Return a class compatible with backend.bind and object.__new__.

    Parent integration must finalize every helper/trace binding and wrapper cell
    before constructing this guard. Subclasses adding owner checks must initialize
    their own state before this constructor calls self.check().
    """
    _TYPE = backend._TYPE
    _LEN = backend._LEN
    _LIST = backend._LIST
    _TUPLE = backend._TUPLE
    _RUNTIME_ERROR = backend._RUNTIME_ERROR
    _DICT_GET = backend._DICT_GET
    _BUILTINS = backend._BUILTINS
    _CANONICAL_BUILTINS = backend._CANONICAL_BUILTINS
    _HELPER_NAMES = backend._HELPER_NAMES
    FunctionType = backend.FunctionType
    ModuleType = backend.ModuleType
    BuiltinFunctionType = backend.BuiltinFunctionType
    require = backend.require

    class RuntimeGuard:
        """Run every distinct freshness check at each original boundary."""

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
            # Identity only: no hashing, user equality or saved PASS. Keep first
            # occurrence order and retain distinct functions sharing code.
            unique_functions = []
            for function in functions:
                for previous in unique_functions:
                    if function is previous:
                        break
                else:
                    unique_functions.append(function)
            self.functions = _TUPLE((function, function.__code__, function.__globals__, function.__builtins__,
                                     function.__defaults__, function.__kwdefaults__, function.__closure__,
                                     () if function.__closure__ is None else
                                     _TUPLE((cell, cell.cell_contents) for cell in function.__closure__))
                                    for function in unique_functions)
            self.native = native
            require(_TYPE(native) is ModuleType, "Unexpected native module type")
            self.native_items = _TUPLE((name, native.__dict__[name]) for name in ("gram_rank", "complement"))
            for name, function in self.native_items:
                require(_TYPE(function) is BuiltinFunctionType and function.__self__ is native,
                        "Changed native entry point: " + name)
            self.check()

        def check(self):
            # Predicates and their short-circuit order match PR5995. Attribute
            # failures, including an empty cell's ValueError, propagate directly.
            if not (_TYPE(self.module) is ModuleType and self.module.__dict__ is self.namespace):
                raise _RUNTIME_ERROR("Runtime drift: source module dispatch")
            if not (_TYPE(self.label) is _TYPE and self.label.__mro__ is self.mro):
                raise _RUNTIME_ERROR("Runtime drift: Label class dispatch")
            for name, value in self.global_items:
                if not (_DICT_GET(self.namespace, name) is value):
                    raise _RUNTIME_ERROR("Runtime drift: source helper " + name)
            for name, expected in _CANONICAL_BUILTINS.items():
                if not (name not in self.namespace and _DICT_GET(_BUILTINS, name) is expected):
                    raise _RUNTIME_ERROR("Runtime drift: builtin lookup " + name)
            attributes = self.label.__dict__
            if not (_LEN(attributes) == _LEN(self.class_items)):
                raise _RUNTIME_ERROR("Runtime drift: Label descriptors")
            for name, value in self.class_items:
                if not (attributes.get(name) is value):
                    raise _RUNTIME_ERROR("Runtime drift: Label member " + name)
            for function, code, namespace, effective_builtins, defaults, kwdefaults, closure, cells in self.functions:
                if not (function.__code__ is code and function.__globals__ is namespace and
                        function.__builtins__ is effective_builtins and function.__defaults__ is defaults and
                        function.__kwdefaults__ is kwdefaults and function.__closure__ is closure):
                    raise _RUNTIME_ERROR("Runtime drift: function code or calling environment")
                for cell, value in cells:
                    if not (cell.cell_contents is value):
                        raise _RUNTIME_ERROR("Runtime drift: wrapper closure")
            if not (_TYPE(self.native) is ModuleType):
                raise _RUNTIME_ERROR("Runtime drift: native module dispatch")
            for name, function in self.native_items:
                if not (_DICT_GET(self.native.__dict__, name) is function):
                    raise _RUNTIME_ERROR("Runtime drift: native entry point " + name)

    return RuntimeGuard
